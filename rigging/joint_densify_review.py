"""Prüfwerkzeug zur Gelenk-Verdichtung (rigging/joint_densify.py): Dehnung vorher/nachher fair messen + Nahaufnahmen.

Dehnung je Clip (alle Frames mit Schritt <every>):
  & "D:\\Blender\\blender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- stretch <aus.json> [<ring.json>] [every]
    "kit"   = wie die Baukästen messen: größte Kantendehnung (Länge/Ruhelänge) aller Kanten des AKTUELLEN Mesh
              (Kanten unter 0,4 % der Länge ignoriert). Achtung: nach dem Verdichten sind die Kanten kürzer → nicht
              direkt mit vorher vergleichbar.
    "orig"  = fair: die Kanten des Mesh VOR dem Verdichten. Ist eine Kante geteilt worden, zählt die Länge der Kette
              über die neuen Vertices (= Haut entlang der alten Kante). Ohne <rig>/joint_densify.json = Mesh-Kanten.
    "ring"  = wie "orig", aber nur Kanten im Gelenk-Ring (Ringe aus <ring.json> = joint_densify.json des verdichteten
              Baus, damit vorher und nachher dieselben Stellen gemessen werden).
    Je Wert: max, p99 (99 % der Kanten darunter), Anzahl Kanten > 1,5 und > 2,0, schlimmste Stelle.

Nahaufnahme eines Gelenks im verformten Zustand (3 Felder: Render | Drahtgitter | Dehnung je Dreieck):
  & "D:\\Blender\\blender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- shot <aus.png> <Action> <frames> <Knochen> <radius_m>
    frames = "12" oder "0,3,6,…" (mehrere → <aus>_000.png, _001 … für ein GIF). Kamera schaut senkrecht auf die
    Beugeebene (Eltern-Knochen × Knochen), von außen. Ausschnitt = 2,6 × Radius.
    Dehnung je Dreieck = größte Kantendehnung seiner Kanten (grau ≤ 1,1, gelb 1,5, rot ≥ 2,0).

Dehnung auf den aus der SPIELKAMERA sichtbaren Flächen (C15, schräg von oben wie die ARPG-Vorschau):
  & "D:\\Blender\\blender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- visible <aus.json> [every]
    Sichtbar = Vertex in Ruhe aus mindestens 2 von 8 Richtungen (alle 45° rundum, 50° Höhe) nicht verdeckt
    (Strahl Richtung Kamera trifft nichts). Unterseiten/Innenseiten der Beine fallen damit weg.
    Bereich = nächster Knochen in Ruhe (geometrisch, unabhängig von den Gewichten → vorher/nachher fair) + Normale:
      Rücken (Rumpf, Normale nach oben) · Flanke oben · Bauchlinie (Rumpf unter der Wirbelsäulen-Mitte) ·
      Hals/Nacken · Kopf · Schwanz · Schulter/Oberschenkel (Leg_*_1, Shoulder_*) · Unterbein
      Beinlos (legless): Spine_01…/Ring_01… wie Rumpf. Achtbeiner (octopod): Thorax wie Rumpf, Abdomen_* → Hinterleib_oben (Normale nach oben) / Hinterleib,
      Leg_*_Coxa/_Femur → Schulter/Oberschenkel
    Dehnung = Kantenlänge/Ruhelänge wie "orig" (verdichtete Kanten als Kette gemessen). Je Clip und Bereich:
    max, p99, Kanten > 1,5 / > 2,0, Frame; dazu die 40 schlimmsten sichtbaren Kanten aller Clips mit Gewichten
    beider Enden (für die Ursache).

Dehnung in der ARPG-Ansicht (wie rig/anim/*.gif: orthografisch, 50° von oben, Azimut −55°):
  & "D:\\Blender\\blender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- arpg <aus.png> <Action> <frames> [az] [scale]
    3 Felder wie "shot" (Render | Drahtgitter | Dehnung je Dreieck); mehrere Frames → <aus>_000.png … (für ein GIF).

Vorher/Nachher-Bogen (normales Python mit PIL, ohne Blender):
  python rigging/joint_densify_review.py sheet <aus.png> "<Titel 1>" <bild1.png> "<Titel 2>" <bild2.png> …
GIF aus Bildreihen nebeneinander (z. B. vorher | nachher):
  python rigging/joint_densify_review.py gif <aus.gif> <fps> "<Titel 1>" "<muster1_*.png>" "<Titel 2>" "<muster2_*.png>" …
"""
import json
import pathlib
import sys

if len(sys.argv) > 2 and sys.argv[1] == "sheet":           # ohne Blender: python rigging/joint_densify_review.py sheet …
    from PIL import Image, ImageDraw, ImageFont
    out, rows = pathlib.Path(sys.argv[2]), list(zip(sys.argv[3::2], sys.argv[4::2]))
    ims = [Image.open(p).convert("RGB") for _, p in rows]
    W, LH = max(i.width for i in ims), 34
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    sheet = Image.new("RGB", (W, sum(i.height + LH for i in ims) + LH), (40, 41, 44))
    d = ImageDraw.Draw(sheet)
    pw = ims[0].width // 3
    for k, t in enumerate(("Render", "Drahtgitter", "Dehnung: grau ≤ 1,1 · gelb 1,5 · rot ≥ 2,0")):
        d.text((k * pw + 10, 6), t, fill=(230, 230, 230), font=font)
    y = LH
    for (label, _), im in zip(rows, ims):
        d.text((10, y + 4), label, fill=(255, 210, 80), font=font)
        sheet.paste(im, (0, y + LH))
        y += im.height + LH
    sheet.save(out)
    print("JD_SHEET", out)
    sys.exit(0)

if len(sys.argv) > 2 and sys.argv[1] == "gif":             # ohne Blender: Bildreihen nebeneinander als GIF
    import glob
    from PIL import Image, ImageDraw, ImageFont
    out, fps = pathlib.Path(sys.argv[2]), int(sys.argv[3])
    cols = [(t, sorted(glob.glob(p))) for t, p in zip(sys.argv[4::2], sys.argv[5::2])]
    n = min(len(f) for _, f in cols)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    frames = []
    for i in range(n):
        ims = [Image.open(f[i]).convert("RGB") for _, f in cols]
        ims = [im.resize((1040, round(im.height * 1040 / im.width))) if im.width > 1040 else im for im in ims]
        w, h = ims[0].size
        fr = Image.new("RGB", (w, sum(im.height for im in ims) + 30 * len(ims)), (40, 41, 44))
        d = ImageDraw.Draw(fr)
        y = 0
        for (t, _), im in zip(cols, ims):
            d.text((8, y + 5), t, fill=(255, 210, 80), font=font)
            fr.paste(im, (0, y + 30))
            y += im.height + 30
        frames.append(fr.quantize(colors=200, method=Image.Quantize.MEDIANCUT))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)
    print("JD_GIF", out, n, "Frames")
    sys.exit(0)

import bpy
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
MODE, OUT = a[0], pathlib.Path(a[1]).resolve()
OUT.parent.mkdir(parents=True, exist_ok=True)
sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = bpy.data.objects.get("Body_Mesh")
BLEND = pathlib.Path(bpy.data.filepath)


def set_action(name):
    act = bpy.data.actions[name]
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and act.slots:
        arm.animation_data.action_slot = act.slots[0]
    return act


def deformed():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    m = ev.to_mesh()
    P = np.empty(len(m.vertices) * 3)
    m.vertices.foreach_get("co", P)
    ev.to_mesh_clear()
    return P.reshape(-1, 3)


def stats(r):
    if not len(r):
        return {"max": 1.0, "p99": 1.0, "n_gt_1_5": 0, "n_gt_2": 0}
    return {"max": round(float(r.max()), 2), "p99": round(float(np.percentile(r, 99)), 2),
            "n_gt_1_5": int((r > 1.5).sum()), "n_gt_2": int((r > 2.0).sum())}


if MODE == "stretch":
    ring_json = pathlib.Path(a[2]) if len(a) > 2 and a[2].endswith(".json") else None
    every = int(a[-1]) if len(a) > 2 and a[-1].isdigit() else 2
    me = body.data
    V0 = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", V0)
    V0 = V0.reshape(-1, 3)
    SIZE = float(np.ptp(V0[:, 0]))
    min_edge = 0.004 * SIZE
    E = np.array([e.vertices[:] for e in me.edges])
    l0 = np.linalg.norm(V0[E[:, 0]] - V0[E[:, 1]], axis=1)
    kit_ok = l0 > min_edge
    # Ketten der alten Kanten
    jd = BLEND.parent / "joint_densify.json"
    if jd.exists():
        J = json.loads(jd.read_text(encoding="utf-8"))
        E0 = np.array(J["base_edges"])
        chains = {int(k): v for k, v in J["chains"].items()}
    else:
        E0, chains = E, {}
    seg_a, seg_b, seg_e = [], [], []                     # Kanten-Segmente je alter Kante
    for ei, (u, w) in enumerate(E0):
        ch = chains.get(ei, [u, w])
        for x, y in zip(ch[:-1], ch[1:]):
            seg_a.append(x)
            seg_b.append(y)
            seg_e.append(ei)
    seg_a, seg_b, seg_e = map(np.array, (seg_a, seg_b, seg_e))
    L0 = np.linalg.norm(V0[E0[:, 0]] - V0[E0[:, 1]], axis=1)
    orig_ok = L0 > min_edge
    # Ring-Kanten (aus dem verdichteten Bau, Gelenkpunkte = Ruhe-Kopf der Knochen dieses Rigs)
    in_ring = np.zeros(len(E0), bool)
    rings = []
    if ring_json:
        RJ = json.loads(ring_json.read_text(encoding="utf-8"))["report"]
        r_m = RJ["radius_m"]
        for n in RJ["joints"]:
            b = arm.data.bones[n]
            rings.append((n, np.array((arm.matrix_world @ b.head_local)[:])))
        mid = (V0[E0[:, 0]] + V0[E0[:, 1]]) / 2
        for n, p in rings:
            in_ring |= np.linalg.norm(mid - p, axis=1) < max(r_m)
    gname = {g.index: g.name for g in body.vertex_groups}

    def dominant(i):
        gs = me.vertices[int(i)].groups
        return gname[max(gs, key=lambda g: g.weight).group] if len(gs) else "?"

    res = {"blend": str(BLEND), "verts": len(V0), "edges": len(E), "base_edges": len(E0),
           "ring_edges": int((in_ring & orig_ok).sum()), "clips": {}}
    for act in sorted(bpy.data.actions, key=lambda x: x.name):
        set_action(act.name)
        f0, f1 = (int(v) for v in act.frame_range)
        best = {"kit": np.ones(len(E)), "orig": np.ones(len(E0))}
        where = {}
        for f in sorted(set(range(f0, f1 + 1, every)) | {f1}):
            sc.frame_set(f)
            P = deformed()
            rk = np.where(kit_ok, np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1) / np.maximum(l0, 1e-12), 1.0)
            sl = np.linalg.norm(P[seg_a] - P[seg_b], axis=1)
            L1 = np.zeros(len(E0))
            np.add.at(L1, seg_e, sl)
            ro = np.where(orig_ok, L1 / np.maximum(L0, 1e-12), 1.0)
            for k, r in (("kit", rk), ("orig", ro)):
                if r.max() > best[k].max():
                    i = int(r.argmax())
                    where[k] = f"{dominant(E[i, 0] if k == 'kit' else E0[i, 0])} @ Frame {f}"
                best[k] = np.maximum(best[k], r)
            if ring_json and (in_ring & orig_ok).any():
                rr = np.where(in_ring & orig_ok, ro, 0)
                if rr.max() > where.get("_ring_v", 0):
                    where["_ring_v"] = float(rr.max())
                    where["ring"] = f"{dominant(E0[int(rr.argmax()), 0])} @ Frame {f}"
        c = {"kit": stats(best["kit"][kit_ok]), "orig": stats(best["orig"][orig_ok])}
        if ring_json:
            c["ring"] = stats(best["orig"][in_ring & orig_ok])
        for k in c:
            c[k]["at"] = where.get(k, "")
        res["clips"][act.name] = c
        print("JD_STRETCH", act.name, json.dumps(c, ensure_ascii=False))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")

elif MODE == "visible":
    import math
    import re
    from mathutils.bvhtree import BVHTree
    every = int(a[2]) if len(a) > 2 else 1
    me = body.data
    mwb = np.array(body.matrix_world)
    V0 = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", V0)
    V0 = V0.reshape(-1, 3) @ mwb[:3, :3].T + mwb[:3, 3]
    NV = len(V0)
    SIZE = float(np.ptp(V0[:, 0]))
    jd = BLEND.parent / "joint_densify.json"
    if jd.exists():
        J = json.loads(jd.read_text(encoding="utf-8"))
        E0, chains, NB = np.array(J["base_edges"]), {int(k): v for k, v in J["chains"].items()}, J["base_verts"]
    else:
        E0, chains, NB = np.array([e.vertices[:] for e in me.edges]), {}, NV
    seg_a, seg_b, seg_e = [], [], []
    for ei, (u, w) in enumerate(E0):
        ch = chains.get(ei, [u, w])
        for x, y in zip(ch[:-1], ch[1:]):
            seg_a.append(x)
            seg_b.append(y)
            seg_e.append(ei)
    seg_a, seg_b, seg_e = map(np.array, (seg_a, seg_b, seg_e))
    L0 = np.linalg.norm(V0[E0[:, 0]] - V0[E0[:, 1]], axis=1)
    ok = L0 > 0.004 * SIZE
    # Sichtbarkeit je Vertex (Ruhe): 8 Richtungen rundum, 50° Höhe, Strahl Richtung Kamera darf nichts treffen
    tris = [tuple(p.vertices) for p in me.polygons]
    bvh = BVHTree.FromPolygons([Vector(v) for v in V0], tris)
    nrm = np.array([(body.matrix_world.to_3x3() @ v.normal).normalized()[:] for v in me.vertices])
    vis_n = np.zeros(NV, int)
    for k in range(8):
        az, el = math.radians(45 * k), math.radians(50)
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        dn = np.array(d[:])
        for i in range(NV):
            if nrm[i] @ dn < 0.05:
                continue
            hit = bvh.ray_cast(Vector(V0[i]) + d * (0.002 * SIZE), d)
            if hit[0] is None:
                vis_n[i] += 1
    vis = vis_n >= 2
    # Bereich je alter Kante: nächster Knochen in Ruhe (geometrisch) + Normale
    mwa = np.array(arm.matrix_world)
    bl = [b for b in arm.data.bones if b.name != "Root"]
    BH = np.array([mwa[:3, :3] @ np.array(b.head_local) + mwa[:3, 3] for b in bl])
    BT = np.array([mwa[:3, :3] @ np.array(b.tail_local) + mwa[:3, 3] for b in bl])
    mid = (V0[E0[:, 0]] + V0[E0[:, 1]]) / 2
    en = nrm[E0[:, 0]] + nrm[E0[:, 1]]
    en /= np.maximum(np.linalg.norm(en, axis=1, keepdims=True), 1e-9)
    Dm = []
    for h, t in zip(BH, BT):
        ab = t - h
        tt = np.clip(((mid - h) @ ab) / max(1e-12, ab @ ab), 0, 1)
        Dm.append(np.linalg.norm(mid - (h + tt[:, None] * ab), axis=1))
    nb = np.argmin(np.stack(Dm, 1), 1)
    bname = np.array([b.name for b in bl])[nb]
    spine_z = np.array([(BH[j, 2] + BT[j, 2]) / 2 for j in nb])

    def region(i):
        n = bname[i]
        if n in ("Hips", "Spine_1", "Chest", "Thorax") or re.fullmatch(r"(Spine|Ring)_\d\d", n):
            # Thorax = Achtbeiner (octopod, seit 2026-11-21); Spine_01…/Ring_01… = Beinlos-Rumpf (legless, 2026-11-27)
            if en[i, 2] > 0.55:
                return "Ruecken"
            return "Bauchlinie" if mid[i, 2] < spine_z[i] else "Flanke"
        if n.startswith("Abdomen_"):                            # octopod: Hinterleib (Spinne: samt Eierhaufen)
            return "Hinterleib_oben" if en[i, 2] > 0.3 else "Hinterleib"
        if n.startswith("Neck"):
            return "Hals"
        if n in ("Head", "Jaw"):
            return "Kopf"
        if n.startswith("Tail"):
            return "Schwanz"
        if n.startswith("Shoulder_") or n.endswith(("_1", "_Coxa", "_Femur")):
            return "Schulter_Oberschenkel"
        return "Unterbein"
    reg = np.array([region(i) for i in range(len(E0))])
    evis = vis[E0[:, 0]] & vis[E0[:, 1]] & ok
    REG = ["Ruecken", "Flanke", "Bauchlinie", "Hals", "Kopf", "Schwanz", "Schulter_Oberschenkel", "Unterbein",
           "Hinterleib_oben", "Hinterleib"]
    gname = {g.index: g.name for g in body.vertex_groups}

    def wstr(i):
        gs = sorted(me.vertices[int(i)].groups, key=lambda g: -g.weight)
        return {gname[g.group]: round(g.weight, 2) for g in gs if g.weight > 0.01}

    res = {"blend": str(BLEND), "verts": NV, "visible_verts": int(vis.sum()), "edges": len(E0),
           "visible_edges": {r: int((evis & (reg == r)).sum()) for r in REG}, "clips": {}}
    worst_all = []
    buf = np.empty(NV * 3)
    for act in sorted(bpy.data.actions, key=lambda x: x.name):
        set_action(act.name)
        f0, f1 = (int(v) for v in act.frame_range)
        best, bf = np.ones(len(E0)), np.full(len(E0), f0)
        for f in sorted(set(range(f0, f1 + 1, every)) | {f1}):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            ev = body.evaluated_get(dg)
            m = ev.to_mesh()
            m.vertices.foreach_get("co", buf)
            ev.to_mesh_clear()
            P = buf.reshape(-1, 3)
            L1 = np.zeros(len(E0))
            np.add.at(L1, seg_e, np.linalg.norm(P[seg_a] - P[seg_b], axis=1))
            r = np.where(ok, L1 / np.maximum(L0, 1e-12), 1.0)
            up = r > best
            best[up], bf[up] = r[up], f
        c = {}
        for rg in REG:
            sel = evis & (reg == rg)
            if not sel.any():
                continue
            v = best[sel]
            i = np.where(sel)[0][int(v.argmax())]
            c[rg] = {"max": round(float(v.max()), 2), "p99": round(float(np.percentile(v, 99)), 2),
                     "n_gt_1_5": int((v > 1.5).sum()), "n_gt_2": int((v > 2.0).sum()), "frame": int(bf[i]),
                     "edge": int(i)}
        res["clips"][act.name] = c
        print("JD_VISIBLE", act.name, json.dumps({k: [x["max"], x["n_gt_1_5"], x["frame"]] for k, x in c.items()}))
        for i in np.where(evis & (best > 1.5))[0]:
            worst_all.append((float(best[i]), act.name, int(bf[i]), int(i)))
    worst_all.sort(reverse=True)
    seen, top = set(), []
    for s, clip, f, i in worst_all:
        if i in seen:
            continue
        seen.add(i)
        u, w = E0[i]
        top.append({"stretch": round(s, 2), "clip": clip, "frame": f, "edge": i, "region": reg[i], "near_bone": bname[i],
                    "rest_len_cm": round(float(L0[i]) * 100, 2), "mid": np.round(mid[i], 3).tolist(),
                    "verts": [int(u), int(w)], "w_a": wstr(u), "w_b": wstr(w)})
        if len(top) >= 40:
            break
    res["worst"] = top
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print("JD_VISIBLE_OK", OUT)

elif MODE in ("shot", "arpg"):
    from mathutils import Matrix
    if MODE == "shot":
        action, frames, bone, radius = a[2], [int(x) for x in a[3].split(",")], a[4], float(a[5])
    else:                                                  # ARPG-Ansicht wie render_anim.py (Kamera aufs Origin)
        action, frames, bone = a[2], [int(x) for x in a[3].split(",")], None
        AZ = float(a[4]) if len(a) > 4 else -55.0
        radius = (float(a[5]) if len(a) > 5 else 1.4) / 2.6
    set_action(action)
    sc.render.engine = "BLENDER_EEVEE"
    PX = 520
    sc.render.resolution_x = sc.render.resolution_y = PX
    sc.view_settings.view_transform = "Standard"           # Farben der Dehnungs-Ansicht unverfälscht
    w = bpy.data.worlds.new("jd")
    sc.world = w
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.31, 0.33, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    sun = bpy.data.objects.new("jd_sun", bpy.data.lights.new("jd_sun", "SUN"))
    sun.data.energy = 3.0
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("jd_cam", bpy.data.cameras.new("jd_cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.6 * radius
    cam.data.clip_end = 20
    sc.collection.objects.link(cam)
    sc.camera = cam

    def emit_mat(name, color=None, attr=None):
        mt = bpy.data.materials.new(name)
        nt = mt.node_tree
        bs = nt.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
        bs.inputs["Emission Strength"].default_value = 1.0
        if attr:                                           # reine Farbe ohne Licht/Glanz (Dehnungs-Ansicht)
            an = nt.nodes.new("ShaderNodeAttribute")
            an.attribute_name = attr
            em = nt.nodes.new("ShaderNodeEmission")
            nt.links.new(an.outputs["Color"], em.inputs["Color"])
            nt.links.new(em.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
        else:
            bs.inputs["Emission Color"].default_value = (*color, 1)
        return mt
    wire_mat = emit_mat("jd_wire", (1.0, 0.85, 0.1))
    heat_mat = emit_mat("jd_heatm", attr="jd_heat")
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = True
    rest = np.array([v.co[:] for v in body.data.vertices])
    E = np.array([e.vertices[:] for e in body.data.edges])
    l0 = np.linalg.norm(rest[E[:, 0]] - rest[E[:, 1]], axis=1)
    if MODE == "arpg":                                     # winzige Kanten wie die Baukästen ignorieren (Rauschen)
        l0 = np.where(l0 > 0.004 * float(np.ptp(rest[:, 0])), l0, 0.0)
    CENTER = body.matrix_world @ Vector(rest.mean(0))

    def heat(r):                                           # grau ≤ 1,1 · gelb 1,5 · rot ≥ 2,0
        t1 = np.clip((r - 1.1) / 0.4, 0, 1)
        t2 = np.clip((r - 1.5) / 0.5, 0, 1)
        g = np.array([0.35, 0.35, 0.37])
        y = np.array([1.0, 0.85, 0.1])
        rd = np.array([0.9, 0.05, 0.05])
        c = g + (y - g) * t1[:, None]
        return c + (rd - c) * t2[:, None]

    def save_pixels(img_list, out):
        tiles = []
        for f in img_list:
            im = bpy.data.images.load(str(f))
            px = np.empty(im.size[0] * im.size[1] * 4, np.float32)
            im.pixels.foreach_get(px)
            tiles.append(px.reshape(im.size[1], im.size[0], 4))
            bpy.data.images.remove(im)
            pathlib.Path(f).unlink()
        big = np.concatenate(tiles, 1)
        img = bpy.data.images.new("jd_out", big.shape[1], big.shape[0], alpha=True)
        img.pixels.foreach_set(big.ravel())
        img.filepath_raw = str(out)
        img.file_format = "PNG"
        img.save()
        bpy.data.images.remove(img)

    out_files, info = [], []
    for fi, f in enumerate(frames):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        for n in ("jd_snap", "jd_wire", "jd_heat"):
            if n in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[n])
        dg = bpy.context.evaluated_depsgraph_get()
        m = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
        P = np.array([v.co[:] for v in m.vertices])
        r = np.where(l0 > 1e-9, np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1) / np.maximum(l0, 1e-9), 1.0)
        fr = np.ones(len(m.polygons))                      # Fläche = größte Dehnung ihrer Kanten
        ek = {tuple(sorted(e)): i for i, e in enumerate(E.tolist())}
        for pi, poly in enumerate(m.polygons):
            fr[pi] = max(r[ek[tuple(sorted(k))]] for k in poly.edge_keys)
        snap = bpy.data.objects.new("jd_snap", m)
        wire = bpy.data.objects.new("jd_wire", m.copy())
        hm = m.copy()
        hm.materials.clear()
        hm.materials.append(heat_mat)
        at = hm.attributes.new("jd_heat", "FLOAT_COLOR", "FACE")
        col = np.concatenate([heat(fr), np.ones((len(fr), 1))], 1).astype(np.float32)
        at.data.foreach_set("color", col.ravel())
        hobj = bpy.data.objects.new("jd_heat", hm)
        for o in (snap, wire, hobj):
            o.matrix_world = body.matrix_world
            sc.collection.objects.link(o)
        wm = wire.modifiers.new("w", "WIREFRAME")
        wm.thickness = 0.01 * radius
        wm.use_replace = True
        wm.use_even_offset = False                         # sonst Stachel-Artefakte an spitzen Ecken
        wire.data.materials.clear()
        wire.data.materials.append(wire_mat)
        if MODE == "arpg":
            import math
            az, el = math.radians(AZ), math.radians(50)
            cam.location = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))) * 5
            cam.rotation_euler = (-cam.location).to_track_quat("-Z", "Y").to_euler()
            sun.rotation_euler = (0.6, 0.2, 0.5)
        else:
            pb = arm.pose.bones[bone]
            p = arm.matrix_world @ pb.head
            d_child = (arm.matrix_world @ pb.tail - p).normalized()
            d_par = (p - arm.matrix_world @ pb.parent.head).normalized() if pb.parent else Vector((0, 0, 1))
            nrm = d_par.cross(d_child)
            if nrm.length < 0.2:                               # fast gestreckt → seitlich schauen
                nrm = Vector((0, 1, 0))
            nrm.normalize()
            if nrm.dot(p - CENTER) < 0:                        # von außen auf das Gelenk schauen
                nrm = -nrm
            zc = nrm                                           # Kamera: Z zur Kamera, Y = Welt-Senkrechte projiziert
            yc = Vector((0, 0, 1)) - zc * zc.z
            if yc.length < 1e-3:
                yc = Vector((1, 0, 0)) - zc * zc.x
            yc.normalize()
            xc = yc.cross(zc).normalized()
            cam.location = p + zc * 5.0
            cam.rotation_euler = Matrix((xc, yc, zc)).transposed().to_euler()
            sun.rotation_euler = (-(nrm + Vector((0, 0, 1.2))).normalized()).to_track_quat("-Z", "Y").to_euler()
        fp = OUT if len(frames) == 1 else OUT.parent / f"{OUT.stem}_{fi:03d}.png"
        tiles = []
        for k, show in enumerate(((snap,), (snap, wire), (hobj,))):    # Render | Drahtgitter | Dehnung
            for o in (snap, wire, hobj):
                o.hide_render = o not in show
            sc.render.filepath = str(OUT.parent / f"_jd_tile{k}.png")
            bpy.ops.render.render(write_still=True)
            tiles.append(sc.render.filepath)
        save_pixels(tiles, fp)
        out_files.append(str(fp))
        info.append({"frame": f, "max_edge_stretch": round(float(r.max()), 2)})
    print("JD_SHOT", json.dumps({"files": out_files, "bone": bone, "action": action, "frames": info}))
