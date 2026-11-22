"""Basis-Kreatur in Blender: laden (Rig + Mesh + Clips aus creatures/<NN>/output/<Name>.blend), Analyse im Mesh-Raum,
Andock-Zonen und Statur.

Gleiche Rechnung wie Unity (`VkBase.cs`, `VkZones`, `VkBuilder.ApplyShape`, `ConfigureStatur`), damit Masken und Statur
in beiden Programmen gleich aussehen:
- Körperachsen: oben = Objekt-Z, vorn = Hüfte → Kopf, links = Seite von Leg_FL_1.
- Kreaturgröße L = längste Kante des Begrenzungsrahmens entlang der Körperachsen.
- Knochen-Enden wie in Unity (Kettenkind, sonst Ausdehnung der Haut am Knochen).
- Zonen aus rigging/<skelett>_zonen.json als weiche Masken pro Vertex.
- Statur S (Formziele) als ein Shape Key „VK_Statur“ nach den Formeln aus Unity; Statur K/G als Pose-Skalierung
  (Kinder erben keine Skalierung) + Versatz über Copy-Location-Constraints (Spurbreite) + Anheben des Rigs (Bodenhöhe).
"""
import math
import os
import re

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import vk_json

BINS = 48
SPINE = ["Hips", "Spine_1", "Chest", "Neck_1", "Neck_2", "Head"]
COLL_NAME = "VK_Basis"


# ------------------------------------------------------------------------------------------------ Basen finden
def list_bases():
    root = os.path.join(vk_json.pipeline_root(), "creatures")
    res = []
    if not os.path.isdir(root):
        return res
    for d in sorted(os.listdir(root)):
        cd = os.path.join(root, d)
        toml = os.path.join(cd, "creature.toml")
        out = os.path.join(cd, "output")
        if not os.path.isfile(toml) or not os.path.isdir(out):
            continue
        txt = open(toml, encoding="utf-8").read()
        m = re.search(r'^name\s*=\s*"([^"]+)"', txt, re.M)
        p = re.search(r'^bodyplan\s*=\s*"([^"]+)"', txt, re.M)
        blends = [f for f in os.listdir(out) if f.endswith(".blend")]
        fbx = [f for f in os.listdir(out) if f.endswith(".fbx")]
        if not m or not p or p.group(1) != "quadruped" or not blends or not fbx:
            continue
        name = os.path.splitext(fbx[0])[0]
        blend = name + ".blend" if name + ".blend" in blends else blends[0]
        res.append({"id": m.group(1), "name": name, "dir": cd, "blend": os.path.join(out, blend), "fbx": os.path.join(out, fbx[0])})
    return res


def find_base(base_id):
    for b in list_bases():
        if b["id"] == base_id:
            return b
    raise RuntimeError(f"Basis-Kreatur '{base_id}' nicht gefunden (creatures/*/creature.toml name, bodyplan quadruped, output/*.blend + *.fbx)")


def creature_dir_of_variant(path):
    # creatures/<NN>/varianten/<id>.variant.json
    return os.path.dirname(os.path.dirname(os.path.abspath(path)))


# ------------------------------------------------------------------------------------------------ Laden
def load_into_scene(info):
    """Rig + Mesh + Clips der Basis in die aktuelle Szene holen (angehängt, die Basis-Datei bleibt unberührt)."""
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is not None:
        for ob in list(coll.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
    else:
        coll = bpy.data.collections.new(COLL_NAME)
        bpy.context.scene.collection.children.link(coll)
    with bpy.data.libraries.load(info["blend"], link=False) as (src, dst):
        dst.objects = list(src.objects)
        dst.actions = list(src.actions)
    arm = mesh = None
    for ob in dst.objects:
        if ob is None:
            continue
        if ob.type in ("ARMATURE", "MESH"):
            coll.objects.link(ob)
            if ob.type == "ARMATURE" and arm is None:
                arm = ob
            if ob.type == "MESH" and mesh is None and len(ob.data.polygons) > 100:
                mesh = ob
        else:
            bpy.data.objects.remove(ob, do_unlink=True)
    if arm is None or mesh is None:
        raise RuntimeError(f"{info['blend']}: kein Rig/Mesh gefunden")
    for a in bpy.data.actions:
        a.use_fake_user = True
    arm["vk_basis"] = info["id"]
    mesh["vk_basis"] = info["id"]
    return arm, mesh


def find_in_scene():
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is None:
        return None, None
    arm = next((o for o in coll.objects if o.type == "ARMATURE"), None)
    mesh = next((o for o in coll.objects if o.type == "MESH" and "vk_basis" in o), None)
    return arm, mesh


def clips(arm):
    names = sorted(a.name for a in bpy.data.actions if a.name.startswith("Quadruped_") or "_" in a.name)
    return names


# ------------------------------------------------------------------------------------------------ Analyse
def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _band(lo, hi, x, soft):
    return _smooth(lo - soft, lo + soft, x) * (1 - _smooth(hi - soft, hi + soft, x))


class Analysis:
    """Analyse der Basis im Mesh-Raum (Ruhepose, ohne Shape Keys)."""

    def __init__(self, arm, mesh_ob):
        self.arm, self.ob = arm, mesh_ob
        me = mesh_ob.data
        n = len(me.vertices)
        co = np.empty(n * 3, np.float32)
        me.vertices.foreach_get("co", co)
        self.verts = co.reshape(n, 3).astype(np.float64)
        nr = np.empty(n * 3, np.float32)
        me.vertex_normals.foreach_get("vector", nr)
        self.normals = nr.reshape(n, 3).astype(np.float64)
        me.calc_loop_triangles()
        tri = np.empty(len(me.loop_triangles) * 3, np.int32)
        me.loop_triangles.foreach_get("vertices", tri)
        self.tris = tri.reshape(-1, 3)
        # Gewichte: Matrix n × Knochen (nur Deform-Knochen mit Vertex-Gruppe)
        self.bone_names = [b.name for b in arm.data.bones]
        self.bone_index = {b: i for i, b in enumerate(self.bone_names)}
        vg_to_bone = {g.index: self.bone_index[g.name] for g in mesh_ob.vertex_groups if g.name in self.bone_index}
        W = np.zeros((n, len(self.bone_names)), np.float64)
        for v in me.vertices:
            for g in v.groups:
                bi = vg_to_bone.get(g.group)
                if bi is not None:
                    W[v.index, bi] += g.weight
        # wie Unity: höchstens 4 Einflüsse, normiert
        if W.shape[1] > 4:
            idx = np.argsort(-W, axis=1)[:, 4:]
            np.put_along_axis(W, idx, 0.0, axis=1)
        s = W.sum(1, keepdims=True)
        s[s == 0] = 1
        self.W = W / s
        to_mesh = mesh_ob.matrix_world.inverted() @ arm.matrix_world
        self.bone_head = np.array([list(to_mesh @ b.head_local) for b in arm.data.bones], np.float64)
        up = mesh_ob.matrix_world.inverted().to_3x3() @ Vector((0, 0, 1))
        self.up = np.array(up.normalized())
        f = self.head("Head") - self.head("Hips")
        f = f - np.dot(f, self.up) * self.up
        self.fwd = f / np.linalg.norm(f)
        left = np.cross(self.up, self.fwd)
        left /= np.linalg.norm(left)
        if self.bone("Leg_FL_1") >= 0 and np.dot(self.head("Leg_FL_1") - self.head("Hips"), left) < 0:
            left = -left
        self.left = left
        mn, mx = self.verts.min(0), self.verts.max(0)
        self.origin = (mn + mx) * 0.5
        ex = [np.ptp(self.verts @ a) for a in (self.fwd, self.up, self.left)]
        self.L = float(max(ex))
        self.body = self.to_body(self.verts)
        self.ground = float(self.body[:, 1].min())
        self._tails()
        self._torso()
        self.zones = Zones(self)

    # ---- Helfer
    def bone(self, name):
        return self.bone_index.get(name, -1)

    def head(self, name):
        return self.bone_head[self.bone_index[name]]

    def to_body(self, p):
        d = np.asarray(p, np.float64) - self.origin
        return np.stack([d @ self.fwd, d @ self.up, d @ self.left], axis=-1)

    def from_body(self, b):
        b = np.asarray(b, np.float64)
        return self.origin + b[..., 0:1] * self.fwd + b[..., 1:2] * self.up + b[..., 2:3] * self.left

    def body_dir(self, d):
        d = np.asarray(d, np.float64)
        return np.stack([d @ self.fwd, d @ self.up, d @ self.left], axis=-1)

    def wsum(self, names):
        idx = [self.bone(n) for n in names if self.bone(n) >= 0]
        return self.W[:, idx].sum(1) if idx else np.zeros(len(self.verts))

    @staticmethod
    def chain_child(b):
        m = {"Hips": "Spine_1", "Spine_1": "Chest", "Chest": "Neck_1", "Neck_1": "Neck_2", "Neck_2": "Head", "Root": "Hips"}
        if b in m:
            return m[b]
        r = re.match(r"^(Leg_[FB][LR]|Tail)_(\d+)$", b)
        if r:
            return f"{r.group(1)}_{int(r.group(2)) + 1}"
        r = re.match(r"^Shoulder_(F[LR])$", b)
        if r:
            return f"Leg_{r.group(1)}_1"
        return None

    def _tails(self):
        nb = len(self.bone_names)
        self.bone_tail = np.zeros((nb, 3))
        for i, name in enumerate(self.bone_names):
            c = self.chain_child(name)
            ci = self.bone(c) if c else -1
            if ci >= 0:
                self.bone_tail[i] = self.bone_head[ci]
                continue
            own = self.verts[self.W[:, i] > 0.5]
            if len(own) == 0:
                self.bone_tail[i] = self.bone_head[i] + self.fwd * self.L * 0.02
                continue
            cen = own.mean(0)
            d = cen - self.bone_head[i]
            d /= max(np.linalg.norm(d), 1e-9)
            if name in ("Head", "Jaw"):
                d = d + self.fwd
                d /= np.linalg.norm(d)
            ext = float(((own - self.bone_head[i]) @ d).max())
            self.bone_tail[i] = self.bone_head[i] + d * max(ext, self.L * 0.02)

    def along(self, p, bi):
        a = self.bone_head[bi]
        d = self.bone_tail[bi] - a
        return ((np.asarray(p) - a) @ d) / max(1e-12, float(d @ d))

    def bone_u(self, spec):
        parts = spec.split(":")
        bi = self.bone(parts[0])
        if bi < 0:
            return 0.0
        t = float(parts[1]) if len(parts) > 1 else 0.0
        p = self.bone_head[bi] + (self.bone_tail[bi] - self.bone_head[bi]) * t
        return float(self.to_body(p)[0])

    def _torso(self):
        spine = SPINE + [n for n in self.bone_names if n.startswith("Tail")]
        ws = self.wsum(spine)
        self.u_min, self.u_max = float(self.body[:, 0].min()), float(self.body[:, 0].max())
        top = np.full(BINS, -np.inf)
        bot = np.full(BINS, np.inf)
        k = self.ubin(self.body[:, 0])
        for v in np.nonzero(ws >= 0.5)[0]:
            top[k[v]] = max(top[k[v]], self.body[v, 1])
            bot[k[v]] = min(bot[k[v]], self.body[v, 1])
        self.torso_top = self._fill(top)
        self.torso_bot = self._fill(bot)

    @staticmethod
    def _fill(a):
        a = a.copy()
        bad = lambda x: not np.isfinite(x)
        for _ in range(BINS):
            for i in range(BINS):
                if bad(a[i]):
                    if i > 0 and not bad(a[i - 1]):
                        a[i] = a[i - 1]
                    elif i < BINS - 1 and not bad(a[i + 1]):
                        a[i] = a[i + 1]
        c = a.copy()
        for i in range(BINS):
            a[i] = (c[max(0, i - 1)] + c[i] * 2 + c[min(BINS - 1, i + 1)]) / 4
        return a

    def ubin(self, u):
        return np.clip(((np.asarray(u) - self.u_min) / (self.u_max - self.u_min + 1e-6) * BINS).astype(int), 0, BINS - 1)

    # ---- Statur S (Formziele), Formeln wie Unity VkBuilder.ApplyShape
    def apply_shape(self, st):
        g = lambda k: float(st.get(k, 1.0))
        rh, rd, bu, gd, kb, sl = g("rumpf_hoehe"), g("rumpf_dicke"), g("buckel"), g("glied_dicke"), g("kopf_breite"), g("schnauze_laenge")
        dv = self.verts.copy()
        if all(abs(x - 1) < 1e-6 for x in (rh, rd, bu, gd, kb, sl)):
            return dv
        bp = self.body
        d = np.zeros_like(bp)
        wt = _smooth(0.3, 0.85, self.wsum(["Hips", "Spine_1", "Chest", "Neck_1"]))
        k = self.ubin(bp[:, 0])
        cy = (self.torso_top[k] + self.torso_bot[k]) * 0.5
        d[:, 1] += (rh - 1) * (bp[:, 1] - cy) * wt
        d[:, 1] += (rd - 1) * (bp[:, 1] - cy) * wt * 0.6
        d[:, 2] += (rd - 1) * bp[:, 2] * wt
        d[:, 1] += (bu - 1) * 0.07 * self.L * self.zones.mask("buckel")
        if abs(gd - 1) > 1e-6:
            legs = [i for i, n in enumerate(self.bone_names) if re.match(r"^Leg_[FB][LR]_[123]$", n)]
            Wl = self.W[:, legs]
            wl = Wl.sum(1)
            best = np.array(legs)[np.argmax(Wl, axis=1)]
            has = (Wl.max(1) > 0) & (wl > 0)
            for v in np.nonzero(has)[0]:
                b = best[v]
                t = min(max(float(self.along(self.verts[v], b)), 0.0), 1.0)
                axis_p = self.bone_head[b] + (self.bone_tail[b] - self.bone_head[b]) * t
                off = self.body_dir(self.verts[v] - axis_p)
                dr = self.body_dir(self.bone_tail[b] - self.bone_head[b])
                dr /= max(np.linalg.norm(dr), 1e-12)
                off = off - np.dot(off, dr) * dr
                d[v] += (gd - 1) * off * _smooth(0.2, 0.8, wl[v])
        hi, ji = self.bone("Head"), self.bone("Jaw")
        if hi >= 0:
            wh = self.W[:, hi] + (self.W[:, ji] if ji >= 0 else 0)
            hb = self.to_body(self.bone_head[hi])
            head_len = float(np.linalg.norm(self.bone_tail[hi] - self.bone_head[hi]))
            t = self.along(self.verts, hi)
            m = wh > 0
            d[m, 2] += (kb - 1) * bp[m, 2] * wh[m]
            d[m, 1] -= (kb - 1) * 0.3 * (bp[m, 1] - hb[1]) * wh[m]
            d[m, 0] += (sl - 1) * np.maximum(0, t[m] - 0.6) * head_len * wh[m]
        dv = self.verts + d[:, 0:1] * self.fwd + d[:, 1:2] * self.up + d[:, 2:3] * self.left
        return dv

    # ---- Strich-Richtung (Fell „knochen“): Knochenrichtung, vorn zeigende Knochen umgedreht, nach Gewicht gemischt
    def strich(self):
        dirs = self.bone_tail - self.bone_head
        dirs /= np.maximum(np.linalg.norm(dirs, axis=1, keepdims=True), 1e-9)
        flip = (dirs @ self.fwd) > 0.3
        dirs[flip] *= -1
        s = self.W @ dirs
        s -= (s * self.normals).sum(1, keepdims=True) * self.normals
        ln = np.linalg.norm(s, axis=1, keepdims=True)
        fb = -self.fwd - (self.normals @ -self.fwd)[:, None] * self.normals
        s = np.where(ln > 1e-6, s / np.maximum(ln, 1e-9), fb)
        return s


class Zones:
    """Andock-Zonen (rigging/<skelett>_zonen.json) als weiche Masken pro Vertex – wie Unity VkZones."""

    def __init__(self, a, skelett="quadruped"):
        self.a = a
        j = vk_json.read_file(os.path.join(vk_json.pipeline_root(), "rigging", f"{skelett}_zonen.json"))
        self.defs = j.get("zonen", {})
        self.sammel = j.get("sammel", {})
        self.rueckenlinie = j.get("rueckenlinie", {})
        self.cache = {}

    @property
    def names(self):
        return list(self.defs.keys())

    @property
    def sammel_names(self):
        return list(self.sammel.keys())

    def mask(self, name):
        if name in self.cache:
            return self.cache[name]
        n = len(self.a.verts)
        if name == "ganzer_koerper":
            m = np.ones(n)
        elif name in self.sammel:
            m = np.zeros(n)
            for s in self.sammel[name]:
                m = np.maximum(m, self.mask(s))
        elif name in self.defs:
            m = self._compute(self.defs[name])
        elif name == "rueckenlinie":
            m = np.maximum(self.mask("ruecken_gesamt"), self.mask("nacken"))
        else:
            m = np.zeros(n)
        self.cache[name] = m
        return m

    def combined(self, zonen, ohne=None):
        n = len(self.a.verts)
        m = np.zeros(n)
        for z in zonen or ["ganzer_koerper"]:
            m = np.maximum(m, self.mask(z))
        for z in ohne or []:
            m = m * (1 - self.mask(z))
        return m

    def _compute(self, z):
        a = self.a
        n = len(a.verts)
        r = np.ones(n)
        bones = [b for b in z.get("knochen", []) if a.bone(b) >= 0]
        wmin = float(z.get("gewicht_min", 0.35))
        if bones:
            r *= _smooth(wmin - 0.15, wmin + 0.15, a.wsum(bones))
        ab_name = z.get("abschnitt_knochen") or (bones[0] if bones else None)
        ab_b = a.bone(ab_name) if ab_name else -1
        if "abschnitt" in z and ab_b >= 0:
            lo, hi = z["abschnitt"]
            r *= _band(lo, hi, a.along(a.verts, ab_b), 0.06)
        bp = a.body
        soft = a.L * 0.025
        ax = z.get("achse", [])
        if len(ax) == 2:
            a0, a1 = sorted([a.bone_u(ax[0]), a.bone_u(ax[1])])
            r *= _band(a0, a1, bp[:, 0], soft)
        if "hoehe" in z:
            lo, hi = z["hoehe"]
            k = a.ubin(bp[:, 0])
            top, bot = a.torso_top[k], a.torso_bot[k]
            r *= _band(lo, hi, (bp[:, 1] - bot) / np.maximum(1e-6, top - bot), 0.06)
        if "nicht_knochen" in z:
            nw = float(z.get("nicht_gewicht", 0.5))
            r *= 1 - _smooth(nw - 0.15, nw + 0.15, a.wsum(z["nicht_knochen"]))
        if "ueber" in z:
            parts = z["ueber"].split(":")
            bi = a.bone(parts[0])
            if bi >= 0:
                tt = float(parts[1]) if len(parts) > 1 else 0.0
                yb = float(a.to_body(a.bone_head[bi] + (a.bone_tail[bi] - a.bone_head[bi]) * tt)[1])
                r *= _smooth(yb - soft, yb + soft, bp[:, 1])
        seite = z.get("seite")
        if seite:
            nb = a.body_dir(a.normals)
            side = np.where(bp[:, 2] >= 0, 1.0, -1.0)
            dirs = {"oben": (0, 1, 0), "unten": (0, -1, 0), "vorn": (1, 0, 0), "hinten": (-1, 0, 0), "links": (0, 0, 1),
                    "rechts": (0, 0, -1), "oben_vorn": (0.7071, 0.7071, 0)}
            if seite == "aussen":
                dot = nb[:, 2] * side
            elif seite == "aussen_vorn":
                dot = (nb[:, 0] + nb[:, 2] * side) * 0.7071
            else:
                dot = nb @ np.array(dirs.get(seite, (0, 1, 0)), np.float64)
            sw = float(z.get("schwelle", 0.0))
            r *= _smooth(sw - 0.15, sw + 0.15, dot)
            if seite == "links":
                r *= _smooth(-soft, soft, bp[:, 2])
            if seite == "rechts":
                r *= _smooth(-soft, soft, -bp[:, 2])
        return r


# ------------------------------------------------------------------------------------------------ Statur in Blender
SHAPE_KEY = "VK_Statur"


def apply_statur(an, arm, mesh_ob, st):
    """Statur live: Formziele als Shape Key, Knochenlängen als Pose-Skalierung (wie Unity ConfigureStatur)."""
    me = mesh_ob.data
    if me.shape_keys is None:
        mesh_ob.shape_key_add(name="Basis", from_mix=False)
    kb = me.shape_keys.key_blocks.get(SHAPE_KEY) or mesh_ob.shape_key_add(name=SHAPE_KEY, from_mix=False)
    dv = an.apply_shape(st).astype(np.float32)
    kb.data.foreach_set("co", dv.ravel())
    kb.value = 1.0
    me.update()
    _apply_bones(an, arm, st)


def _apply_bones(an, arm, st):
    g = lambda k: float(st.get(k, 1.0))
    g0, bv, bh, pv, ph = g("groesse"), g("bein_laenge_vorn"), g("bein_laenge_hinten"), g("pranken_vorn"), g("pranken_hinten")
    kg, sl, sd, kl, hl, sp = g("kopf_groesse"), g("schwanz_laenge"), g("schwanz_dicke"), g("koerper_laenge"), g("hals_laenge"), g("spur_breite")
    own = {}
    for side in ("FL", "FR"):
        for k in (1, 2, 3):
            own[f"Leg_{side}_{k}"] = bv
        own[f"Leg_{side}_4"] = pv
    for side in ("BL", "BR"):
        for k in (1, 2, 3):
            own[f"Leg_{side}_{k}"] = bh
        own[f"Leg_{side}_4"] = ph
    own["Head"] = kg
    own["Jaw"] = kg
    for k in range(1, 5):
        own[f"Tail_{k}"] = sl
    stretch = {"Spine_1": kl, "Chest": kl, "Neck_1": hl, "Neck_2": hl}
    for b in arm.data.bones:
        b.inherit_scale = "NONE" if b.name != "Root" else "FULL"
    for pb in arm.pose.bones:
        n = pb.name
        if n == "Root":
            pb.scale = (g0, g0, g0)
            continue
        f = own.get(n, 1.0)
        # Ohne geerbte Skalierung: jeder Knochen bekommt seinen eigenen Gesamtfaktor (× Gesamtgröße)
        sx = sz = f * g0
        sy = f * g0 * stretch.get(n, 1.0)
        if n == "Tail_1" or n.startswith("Tail_"):
            sx *= sd
            sz *= sd
        pb.scale = (sx, sy, sz)
    # Spurbreite: Schultern/Hüftbeine seitlich (Copy-Location-Constraint mit Versatz-Empty, wirkt nach dem Clip)
    for bone, sign in (("Shoulder_FL", 1), ("Shoulder_FR", -1), ("Leg_BL_1", 1), ("Leg_BR_1", -1)):
        pb = arm.pose.bones.get(bone)
        if pb is None:
            continue
        half = abs(float(an.to_body(an.head(bone))[2]))
        off_mesh = Vector(an.left * sign * (sp - 1) * half * g0)
        _offset_constraint(arm, pb, off_mesh)
    # Bodenhöhe: Rig anheben (mittlerer Beinfaktor, wie Unity)
    def H(bone):
        bi = an.bone(bone)
        return 0.0 if bi < 0 else float(an.to_body(an.bone_head[bi])[1] - an.ground)
    lift = 0.5 * ((bv - 1) * H("Leg_FL_1") + (pv - 1) * H("Leg_FL_4") * 0.6 + (bh - 1) * H("Leg_BL_1") + (ph - 1) * H("Leg_BL_4") * 0.6) * g0
    base_z = arm.get("vk_z0")
    if base_z is None:
        arm["vk_z0"] = arm.location.z
        base_z = arm.location.z
    arm.location.z = base_z + lift + (g0 - 1) * (-an.ground)


def _offset_constraint(arm, pb, off_mesh):
    name = "VK_Spur"
    emp_name = f"VK_Versatz_{pb.name}"
    emp = bpy.data.objects.get(emp_name)
    if emp is None:
        emp = bpy.data.objects.new(emp_name, None)
        emp.hide_viewport = True
        emp.hide_render = True
        coll = bpy.data.collections.get(COLL_NAME)
        (coll or bpy.context.scene.collection).objects.link(emp)
    # Versatz im lokalen Raum des Knochens (Ruhe-Orientierung)
    rest = pb.bone.matrix_local.to_3x3()
    emp.location = rest.inverted() @ off_mesh
    c = pb.constraints.get(name)
    if c is None:
        c = pb.constraints.new("COPY_LOCATION")
        c.name = name
        c.target = emp
        c.use_offset = True
        c.target_space = "LOCAL"
        c.owner_space = "LOCAL"
    c.influence = 1.0 if off_mesh.length > 1e-7 else 0.0
