"""Achtbeiner-Rig (Spinnen, Krabben …): 4 Beinpaar-Plätze, vorderes Paar ggf. Scheren.
Entstanden 2026-11-17 als Kopie des Krabbler-Rigs (heute hexapod_rig.py) – ab jetzt eigenständig.
Erkennt die Anatomie, baut das Standard-Skelett, setzt Gewichte.

Aufruf:
  & "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/octopod_rig.py -- <mesh.glb> <ausgabeordner> [<creature.toml>]
Ergebnis: <ausgabe>/octopod_rigged.blend, rig_report.json

Standard-Skelett (immer vollständig, auch wenn ein Teil fehlt – dann ohne Gewichte):
  Root
  └ Thorax
    ├ Abdomen_1 └ Abdomen_2
    ├ Head ├ Antenna_L_1 └ Antenna_L_2 · Antenna_R_1 └ Antenna_R_2 · Mandible_L · Mandible_R
    └ Leg_{L|R}{1..4}_Coxa └ _Femur └ _Tibia └ _Tarsus      (1 = vorne … 4 = hinten)
Konvention: Kopf +X, oben +Z, links = +Y.
"""
import json
import math
import pathlib
import sys
import tomllib

import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from octopod_detect import detect  # noqa: E402

LEG_PARTS = ("Coxa", "Femur", "Tibia", "Tarsus")
SIDES = ("L", "R")
SLOTS = (1, 2, 3, 4)


def load_cfg(creature_toml=None):
    cfg = tomllib.loads((HERE / "octopod_defaults.toml").read_text(encoding="utf-8"))
    if creature_toml:
        over = tomllib.loads(pathlib.Path(creature_toml).read_text(encoding="utf-8")).get("octopod", {})
        for sec, vals in over.items():
            cfg.setdefault(sec, {}).update(vals)
    return cfg


def seg_dist(p, a, b):
    t = intersect_point_line(p, a, b)[1]
    t = max(0.0, min(1.0, t))
    return (p - (a + (b - a) * t)).length


def polyline_point(pts, frac):
    """Punkt bei Anteil frac (0..1) der Gesamtlänge einer Polylinie."""
    lens = [(b - a).length for a, b in zip(pts, pts[1:])]
    total = sum(lens) or 1e-9
    target = total * frac
    for (a, b), l in zip(zip(pts, pts[1:]), lens):
        if target <= l and l > 0:
            return a + (b - a) * (target / l)
        target -= l
    return pts[-1].copy()


def leg_points(joints, cfg):
    """Variable Gelenkkette → 5 Standardpunkte: Wurzel, Coxa-Ende, Knie, Knöchel, Spitze.
    Bevorzugt ECHTE Segment-Übergänge (Kontaktpunkte), damit jedes Chitin-Segment
    genau an einem Gelenk knickt. Nur wenn keiner passt, wird ein Punkt interpoliert."""
    root, tip = joints[0], joints[-1]
    inner = joints[1:-1]
    if not inner:
        return [root, polyline_point(joints, 0.15), polyline_point(joints, 0.4),
                polyline_point(joints, 0.75), tip]
    # Knie = höchster Übergang, aber nur in plausiblem Bereich der Beinlänge (sonst entartete Glieder:
    # beim Chitin Crawler lag das Knie von L2 bei 6 % → Oberschenkel fast null → IK unbrauchbar)
    seg = [(b - a).length for a, b in zip(joints, joints[1:])]
    total = sum(seg) or 1e-9
    pos = [sum(seg[:i]) / total for i in range(len(joints))]
    lo, hi = cfg["knee_min_fraction"], cfg["knee_max_fraction"]
    cand = [i for i in range(1, len(joints) - 1) if lo <= pos[i] <= hi]
    if cand:
        k = max(cand, key=lambda i: joints[i].z)
    else:   # kein echter Übergang im Bereich → Knie-Punkt in die Kette einfügen
        knee_pt = polyline_point(joints, (lo + hi) / 2)
        i_ins = next(i for i in range(1, len(joints)) if pos[i] > (lo + hi) / 2)
        joints = joints[:i_ins] + [knee_pt] + joints[i_ins:]
        k = i_ins
    knee = joints[k]

    def pick(cands, target):
        return min(cands, key=lambda p: abs((p - root).length - target)) if cands else None

    before = joints[1:k]
    after = joints[k + 1:-1]
    coxa_end = pick(before, (knee - root).length * cfg["coxa_fraction"]) \
        or polyline_point(joints[:k + 1], cfg["coxa_fraction"])
    ankle = None
    if after:
        tgt = (knee - root).length + (tip - knee).length * cfg["ankle_fraction"]
        ankle = min(after, key=lambda p: abs((p - root).length - tgt))
    ankle = ankle or polyline_point(joints[k:], cfg["ankle_fraction"])
    # Fuß (Tarsus) nicht übermäßig lang: sonst Knöchel auf max. Anteil zur Spitze hin verschieben
    leg_len = sum((b - a).length for a, b in zip(joints, joints[1:]))
    if (tip - ankle).length > cfg["tarsus_max_fraction"] * leg_len:
        ankle = tip + (ankle - tip).normalized() * cfg["tarsus_max_fraction"] * leg_len
    return [root, coxa_end, knee, ankle, tip]


def body_profile(obj, d, cfg):
    """Breite des Rumpfs entlang X → Einschnürungen (Petiolus, Hals) finden.
    Misst über gleichmäßig verteilte Oberflächenpunkte (Low-Poly hat zu wenige Vertices)."""
    import random
    co = d["coords"]
    isl = set(d["body_core"]) | set(d["others"])   # Mittelteile + Panzerplatten, ohne Gelenkringe
    vown = {v: i for i in isl for v in d["islands"][i]["verts"]}
    rnd = random.Random(1)
    tris = []
    for p in obj.data.polygons:
        if p.vertices[0] in vown:
            vs = [co[v] for v in p.vertices]
            for k in range(1, len(vs) - 1):
                a, b, c = vs[0], vs[k], vs[k + 1]
                tris.append((a, b, c, (b - a).cross(c - a).length / 2))
    total = sum(t[3] for t in tris) or 1
    pts = []
    for a, b, c, area in tris:
        for _ in range(max(1, int(cfg["profile_samples"] * area / total))):
            r1, r2 = rnd.random(), rnd.random()
            if r1 + r2 > 1:
                r1, r2 = 1 - r1, 1 - r2
            pts.append(a + (b - a) * r1 + (c - a) * r2)
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    n = cfg["profile_bins"]
    ys, zs = [[] for _ in range(n)], [[] for _ in range(n)]
    for p in pts:
        b = min(n - 1, int((p.x - x0) / (x1 - x0) * n))
        ys[b].append(abs(p.y))
        zs[b].append(p.z)

    def pct(vals, q):
        if not vals:
            return 0.0
        s = sorted(vals)
        return s[min(len(s) - 1, int(q * len(s)))]

    width = [pct(v, 0.9) for v in ys]
    zmid = [(min(v) + max(v)) / 2 if v else None for v in zs]
    xs = [x0 + (i + 0.5) / n * (x1 - x0) for i in range(n)]
    return xs, width, zmid, x0, x1


def build(mesh_path, out_dir, creature_toml=None):
    cfg = load_cfg(creature_toml)
    out = pathlib.Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(mesh_path))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in bpy.data.objects:
        o.select_set(o in meshes)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "Body_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Low-Poly-Look: Flat Shading
    for p in obj.data.polygons:
        p.use_smooth = False

    d = detect(obj, cfg["detect"])
    rc = cfg["rig"]
    report = {"warnings": [], "legs_found": len(d["legs"])}

    # ---------- Wirbelsäule ----------
    xs, width, zmid, x0, x1 = body_profile(obj, d, rc)
    L = x1 - x0
    report["profile"] = [[round(x, 3), round(w, 3)] for x, w in zip(xs, width)]
    roots = [l["joints"][0] for l in d["legs"]]
    leg_x_min = min(r.x for r in roots) if roots else x0 + 0.4 * L
    leg_x_max = max(r.x for r in roots) if roots else x0 + 0.7 * L

    def narrowest(lo, hi, fallback):
        cand = [(width[i], xs[i]) for i in range(len(xs)) if lo <= xs[i] <= hi and zmid[i] is not None]
        return min(cand)[1] if cand else fallback

    # Petiolus: engste Stelle zwischen Hinterleib-Mitte und knapp vor den hintersten Beinwurzeln
    petiole_x = narrowest(x0 + 0.25 * L, leg_x_min + rc["petiole_search_ahead"] * L, leg_x_min)
    neck_x = narrowest(leg_x_max, x1 - 0.05 * L, leg_x_max)

    def z_at(x):
        i = min(range(len(xs)), key=lambda k: abs(xs[k] - x) if zmid[k] is not None else 1e9)
        return zmid[i]

    P = {
        "tail": Vector((x0, 0, z_at(x0 + 0.02 * (x1 - x0)))),
        "abd_mid": Vector(((x0 + petiole_x) / 2, 0, z_at((x0 + petiole_x) / 2))),
        "petiole": Vector((petiole_x, 0, z_at(petiole_x))),
        "neck": Vector((neck_x, 0, z_at(neck_x))),
        "head_tip": Vector((x1, 0, z_at(x1 - 0.02 * (x1 - x0)))),
    }
    # Ein-Mesh-Spinne (detect_single, seit 2026-11-21): Der Hinterleib samt Eierhaufen ragt über den Vorderkörper,
    # eine Einschnürung gibt es von außen nicht. → Trennebene zwischen Vorderkörper (Mitte der Beinwurzeln) und
    # Hinterleib (Schwerpunkt hinter den hintersten Beinwurzeln); dahinter hängt alles STARR an Abdomen_1.
    # Mehrteilige Meshes (Crab/Crawler) laufen unverändert über die Einschnürungen.
    abd_plane = None
    if d.get("single_mesh") and roots:
        pro_c = sum(roots, Vector()) / len(roots)
        bpts = [d["coords"][v] for v in d["islands"][0]["verts"]]
        back = [p for p in bpts if p.x < min(r.x for r in roots)] or bpts
        abd_c = sum(back, Vector()) / len(back)
        n_ = pro_c - abd_c
        n_.y = 0.0
        n_.normalize()
        p0 = pro_c.lerp(abd_c, rc["sm_abdomen_split"])
        p0.y = 0.0
        abd_plane = (p0, n_)
        ax = Vector((abd_c.x, 0, abd_c.z)) - p0
        reach = max((p - p0).dot(ax.normalized()) for p in bpts)
        P["petiole"], P["abd_mid"] = p0, p0 + ax
        P["tail"] = p0 + ax.normalized() * max(reach, ax.length * 1.2)
        report["abdomen_plane"] = {"point": [round(c, 3) for c in p0], "normal": [round(c, 3) for c in n_]}
    report["spine"] = {k: [round(c, 3) for c in v] for k, v in P.items()}

    # ---------- Armature ----------
    arm_data = bpy.data.armatures.new("Octopod_Rig")
    arm = bpy.data.objects.new("Octopod_Rig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.data.objects:
        o.select_set(o is arm)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones
    up = Vector((0, 0, 1))

    def bone(name, head, tail, parent=None, connect=False):
        b = eb.new(name)
        b.head, b.tail = head, tail
        if (b.tail - b.head).length < 1e-4:
            b.tail = b.head + Vector((0, 0, 0.01))
        b.align_roll(up)
        if parent:
            b.parent = eb[parent]
            b.use_connect = connect
        return b

    ground = d["ground_z"]
    thorax_mid = (P["petiole"] + P["neck"]) / 2
    bone("Root", Vector((thorax_mid.x, 0, ground)), Vector((thorax_mid.x + 0.1 * d["size"], 0, ground)))
    bone("Thorax", P["petiole"], P["neck"], "Root")
    bone("Abdomen_1", P["petiole"], P["abd_mid"], "Thorax")
    bone("Abdomen_2", P["abd_mid"], P["tail"], "Abdomen_1", True)
    bone("Head", P["neck"], P["head_tip"], "Thorax")

    # Fühler: Inseln nach Seite trennen, Basis = nächster Punkt zum Kopf, Spitze = weitester
    co = d["coords"]
    antenna_pts = {}
    for side, sign in (("L", 1), ("R", -1)):
        pts = [co[v] for i in d["antennae"] if d["islands"][i]["center"].y * sign > 0 for v in d["islands"][i]["verts"]]
        if pts:
            base = min(pts, key=lambda p: (p - P["neck"]).length + 0.0 * p.z)
            base = min(pts, key=lambda p: (p - (P["neck"] + P["head_tip"]) / 2).length)
            tip = max(pts, key=lambda p: (p - base).length)
            mid = (base + tip) / 2 + Vector((0, 0, 0.0))
            mid = max(pts, key=lambda p: p.z) if rc["antenna_mid_highest"] else mid
            antenna_pts[side] = (base, mid, tip)
        else:
            hb = P["head_tip"] + Vector((-0.05, sign * 0.03, 0.05)) * d["size"]
            antenna_pts[side] = (hb, hb + Vector((0.05, sign * 0.02, 0.05)) * d["size"],
                                 hb + Vector((0.1, sign * 0.04, 0.06)) * d["size"])
            report["warnings"].append(f"Fühler {side} nicht gefunden – Platzhalter-Knochen ohne Gewichte")
        b, m, t = antenna_pts[side]
        bone(f"Antenna_{side}_1", b, m, "Head")
        bone(f"Antenna_{side}_2", m, t, f"Antenna_{side}_1", True)
    for side, sign in (("L", 1), ("R", -1)):
        mb = P["head_tip"] + Vector((-0.02, sign * 0.02, -0.03)) * d["size"]
        bone(f"Mandible_{side}", mb, mb + Vector((0.05, -sign * 0.01, -0.01)) * d["size"], "Head")

    # Beine: erkannte Beine in Slots, fehlende Slots als eingeklappte Platzhalter
    leg_by_slot = {(l["side"], l["slot"]): l for l in d["legs"] if l.get("slot", 9) <= 4}
    leg_pts = {}
    for side in SIDES:
        sign = 1 if side == "L" else -1
        for slot in SLOTS:
            l = leg_by_slot.get((side, slot))
            if l:
                pts = leg_points(l["joints"], rc)
            else:
                # Platzhalter: kurz, unter dem Thorax eingeklappt – unsichtbar, ohne Gewichte
                r0 = Vector((P["petiole"].x - 0.02 * slot * d["size"], sign * 0.03 * d["size"], P["petiole"].z))
                pts = [r0 + Vector((0, sign * f * 0.02, -f * 0.01)) * d["size"] for f in range(5)]
                report["warnings"].append(f"Bein {side}{slot} nicht vorhanden – Platzhalter ohne Gewichte (Fake it)")
            leg_pts[(side, slot)] = pts
            names = [f"Leg_{side}{slot}_{p}" for p in LEG_PARTS]
            for k, nm in enumerate(names):
                bone(nm, pts[k], pts[k + 1], "Thorax" if k == 0 else names[k - 1], k > 0)
    bpy.ops.object.mode_set(mode="OBJECT")

    # ---------- Gewichte ----------
    for vg in list(obj.vertex_groups):
        obj.vertex_groups.remove(vg)
    groups = {b.name: obj.vertex_groups.new(name=b.name) for b in arm_data.bones}
    bones_ws = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_data.bones}

    def nearest(p, names):
        return min(names, key=lambda n: seg_dist(p, *bones_ws[n]))

    assigned = {}

    def blended(p, names, blend_dist):
        ds = sorted((seg_dist(p, *bones_ws[n]), n) for n in names)
        (d1, n1), (d2, n2) = ds[0], ds[1]
        if d2 - d1 < blend_dist:
            w2 = 0.5 * (1 - (d2 - d1) / blend_dist)
            return [(n1, 1 - w2), (n2, w2)]
        return [(n1, 1.0)]

    # 1) Bein-Gewichte.
    #    "positional": nach Lage entlang der Beinkette; in einer Zone um jedes Gelenk (inkl. Beinansatz
    #                  am Thorax) weich zwischen beiden Knochen überblendet → keine Lücken beim Knicken.
    #    "island":     jedes Chitin-Segment starr an einem Knochen (alt, klafft an Gelenken auf).
    leg_blend = rc["leg_blend"] * d["size"]
    joint_r = rc["joint_blend"] * d["size"]

    def smooth(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3 - 2 * x)

    def leg_weights(p, side, slot):
        pts = leg_pts[(side, slot)]
        names = ["Thorax"] + [f"Leg_{side}{slot}_{q}" for q in LEG_PARTS]
        seg_len = [(b - a).length for a, b in zip(pts, pts[1:])]
        cum = [0.0]
        for L_ in seg_len:
            cum.append(cum[-1] + L_)
        best = None
        for k_, (a, b) in enumerate(zip(pts, pts[1:])):
            t = max(0.0, min(1.0, intersect_point_line(p, a, b)[1]))
            dd = (p - (a + (b - a) * t)).length
            if best is None or dd < best[0]:
                best = (dd, k_, cum[k_] + t * seg_len[k_])
        _, k_, s = best
        w = {names[k_ + 1]: 1.0}
        for m in range(4):  # Gelenke: 0 = Thorax/Coxa, 1 = Coxa/Femur, 2 = Femur/Tibia, 3 = Tibia/Tarsus
            r_ = min(joint_r, 0.4 * seg_len[m], 0.4 * seg_len[m - 1] if m > 0 else joint_r)
            if abs(s - cum[m]) < r_ and r_ > 1e-6:
                wc = smooth((s - cum[m] + r_) / (2 * r_))
                w = {names[m]: 1 - wc, names[m + 1]: wc}
                break
        return [(n, x) for n, x in w.items() if x > 1e-3]

    for l in d["legs"]:
        if l.get("slot", 9) > 4:
            continue
        names = [f"Leg_{l['side']}{l['slot']}_{p}" for p in LEG_PARTS]
        if rc["leg_weight_mode"] == "positional":
            for i in l["islands"]:
                for v in d["islands"][i]["verts"]:
                    assigned[v] = leg_weights(co[v], l["side"], l["slot"])
            continue
        for i in l["islands"]:
            isl = d["islands"][i]
            pts = [co[v] for v in isl["verts"]]
            # Welche Knochen berührt die Insel? (nächster Knochen pro Vertex)
            hit = {nearest(p, names) for p in pts}
            if len(hit) <= 2 or not rc["split_long_leg_islands"]:
                n = nearest(isl["center"], names)
                for v in isl["verts"]:
                    assigned[v] = [(n, 1.0)]
            else:
                for v in isl["verts"]:
                    assigned[v] = blended(co[v], names, leg_blend)
    # 2) Fühler-Inseln starr
    for i in d["antennae"]:
        isl = d["islands"][i]
        side = "L" if isl["center"].y > 0 else "R"
        n = nearest(isl["center"], [f"Antenna_{side}_1", f"Antenna_{side}_2"])
        for v in isl["verts"]:
            assigned[v] = [(n, 1.0)]
    # 3) Rumpf + Rest: pro Vertex, weiche Übergänge zwischen den 2 nächsten Rumpfknochen
    spine = ["Thorax", "Abdomen_1", "Abdomen_2", "Head"]
    blend = rc["spine_blend"] * d["size"]
    rest_islands = set(d["body"]) | set(d["others"]) | set(d["mandibles"])
    all_leg_bones = [f"Leg_{s}{k}_{p}" for (s, k) in leg_by_slot for p in LEG_PARTS]
    others = set(d["others"])
    moved_to_leg = 0
    for i in rest_islands:
        isl = d["islands"][i]
        if i in others and all_leg_bones:
            # Loses Teil, das eigentlich zu einem Bein gehört (liegt parallel zur Beinkette)?
            nl = nearest(isl["center"], all_leg_bones)
            ns = nearest(isl["center"], spine)
            if seg_dist(isl["center"], *bones_ws[nl]) < rc["leg_capture_ratio"] * seg_dist(isl["center"], *bones_ws[ns]):
                side, slot = nl[4], int(nl[5])
                for v in isl["verts"]:
                    assigned[v] = (leg_weights(co[v], side, slot) if rc["leg_weight_mode"] == "positional"
                                   else [(nl, 1.0)])
                moved_to_leg += 1
                continue
        if len(isl["verts"]) < rc["rigid_island_max_verts"]:
            # kleine Rumpfteile (Panzerplatten, Gelenkringe) starr am nächsten RUMPF-Knochen,
            # sonst reißen beim Biegen Löcher in den Panzer
            n = nearest(isl["center"], spine)
            for v in isl["verts"]:
                assigned[v] = [(n, 1.0)]
            continue
        if abd_plane:                   # Ein-Mesh-Spinne: Hinterleib starr, schmale Überblendung an der Trennebene
            band = rc["sm_abdomen_band"] * d["size"]
            for v in isl["verts"]:
                s_ = (co[v] - abd_plane[0]).dot(abd_plane[1])
                front = blended(co[v], ["Thorax", "Head"], blend)
                k_ = smooth((s_ + band) / (2 * band))
                mix = {"Abdomen_1": 1 - k_}
                for n_, x_ in front:
                    mix[n_] = mix.get(n_, 0) + x_ * k_
                assigned[v] = [(n_, x_) for n_, x_ in mix.items() if x_ > 1e-3]
            continue
        for v in isl["verts"]:
            assigned[v] = blended(co[v], spine, blend)

    # 4) Rumpf-Vertices direkt am Beinansatz (Gelenkringe) teilweise mit der Coxa mitnehmen,
    #    sonst klafft zwischen Ring und Bein eine Lücke, wenn das Bein schwenkt.
    if rc["leg_weight_mode"] == "positional":
        from mathutils.kdtree import KDTree
        leg_vs = [v for v, ws in assigned.items() if any(n.startswith("Leg_") for n, _ in ws)]
        leg_set = set(leg_vs)
        if abd_plane:
            # Ein-Mesh-Spinne: Rumpf nur am echten Beinansatz (Coxa) mitnehmen – nicht dort, wo ein Bein weiter außen
            # nah am Kopf/Rumpf vorbeiläuft (sonst zieht das Knie die Kopf-Haut mit)
            leg_vs = [v for v in leg_vs if any(n.endswith("_Coxa") for n, _ in assigned[v])]
        kd = KDTree(len(leg_vs))
        for idx, v in enumerate(leg_vs):
            kd.insert(co[v], idx)
        kd.balance()
        root_r = rc["root_blend"] * d["size"]
        for v, ws in list(assigned.items()):
            if v in leg_set:
                continue
            if abd_plane and dict(ws).get("Abdomen_1", 0.0) > 0.5:
                continue                # Ein-Mesh-Spinne: Hinterleib/Eierhaufen über den Beinwurzeln bleibt starr
            near = [(p_, idx, dist) for (p_, idx, dist) in kd.find_range(co[v], root_r)]
            if near:
                # Gewichte der nahen Bein-Vertices (auch verschiedener Beine) anteilig übernehmen,
                # gewichtet nach Nähe → Rumpf "klebt" an allen Beinen, die er berührt
                dist = min(x[2] for x in near)
                wc = rc["root_blend_max"] * (1 - dist / root_r)
                mix = {}
                for n, x in ws:
                    mix[n] = mix.get(n, 0) + x * (1 - wc)
                inv = [(1 - dd / root_r) ** 2 for _, _, dd in near]
                tot_inv = sum(inv) or 1
                for (_, idx, _), f_ in zip(near, inv):
                    for n, x in assigned[leg_vs[idx]]:
                        mix[n] = mix.get(n, 0) + x * wc * f_ / tot_inv
                # max. 4 Einflüsse (Unity-Standard), normalisiert
                top = sorted(mix.items(), key=lambda kv: -kv[1])[:4]
                tot = sum(x for _, x in top)
                assigned[v] = [(n, x / tot) for n, x in top if x / tot > 1e-3]
    for v, ws in assigned.items():
        for n, w in ws:
            groups[n].add([v], w, "REPLACE")

    report["loose_parts_to_legs"] = moved_to_leg
    if d.get("fused_faces_cut"):
        report["fused_faces_cut"] = d["fused_faces_cut"]
    unweighted = len(obj.data.vertices) - len(assigned)
    if unweighted:
        report["warnings"].append(f"{unweighted} Vertices ohne Gewicht")
    obj.parent = arm
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm

    used_bones = sorted({n for ws in assigned.values() for n, _ in ws})
    report.update({
        "bones": len(arm_data.bones),
        "bones_with_weights": len(used_bones),
        "bones_without_weights": sorted(set(b.name for b in arm_data.bones) - set(used_bones)),
        "vertices": len(obj.data.vertices),
        "unweighted_vertices": unweighted,
        "max_influences": max((len(ws) for ws in assigned.values()), default=0),
        "legs": {f"{s}{k}": [[round(c, 3) for c in p] for p in leg_pts[(s, k)]] for s in SIDES for k in SLOTS},
        "detect_debug": d["debug"],
    })
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "octopod_rigged.blend"))
    (out / "rig_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("RIG_REPORT", json.dumps({k: v for k, v in report.items() if k not in ("legs", "detect_debug")}, ensure_ascii=False))
    return obj, arm, report


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    build(a[0], a[1], a[2] if len(a) > 2 else None)
    print("RIG_OK")
