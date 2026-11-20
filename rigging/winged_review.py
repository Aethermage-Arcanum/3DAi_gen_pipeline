"""Prüfbilder für das Skelett `winged` (Wyvern, Geier): Skelett-Overlay, Gewichte, Einzelbild-Streifen.
Eigene Kopie von rigging/upright_review.py (Kapselung: kein Skelett hängt an Dateien eines anderen), Farben für winged.

  Skelett + Gewichte (Ruhepose, vorn + seitlich):
    & "D:\\Blender\\blender.exe" -b <winged_rigged.blend|clips.blend> -P rigging/winged_review.py -- rig <ausgabe.png>
  Einzelbilder eines Clips als Streifen (Zeilen = Ansichten):
    & "D:\\Blender\\blender.exe" -b <clips.blend> -P rigging/winged_review.py -- strip <ausgabe.png> <Action> <f1,f2,…> [arpg,side,front] [weights|weights+bones]

Ansichten: front (von vorn), side (von links), back, arpg (Spielkamera schräg von oben). Der Bildausschnitt umfasst alle
gezeigten Frames (nichts wird abgeschnitten, alle Bilder im gleichen Maßstab). Boden = Ruhe-Tiefpunkt (graue Linie/Ebene).
"""
import colorsys
import math
import pathlib
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
MODE, OUT = a[0], pathlib.Path(a[1]).resolve()
OUT.parent.mkdir(parents=True, exist_ok=True)
sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = bpy.data.objects["Body_Mesh"]
RES = 420
PALETTE = {"Root": (0.5, 0.5, 0.5), "Pelvis": (0.1, 0.45, 0.2), "Spine_1": (0.15, 0.65, 0.3), "Spine_2": (0.2, 0.8, 0.6),
           "Chest": (0.9, 0.15, 0.15), "Neck_1": (0.95, 0.95, 0.95), "Neck_2": (0.7, 0.7, 0.75), "Neck_3": (0.95, 0.8, 0.8),
           "Head": (1, 0.6, 0.8), "Jaw": (0.9, 0.0, 0.5), "Tail_1": (0.2, 0.2, 0.6), "Tail_2": (0.3, 0.3, 0.9),
           "Tail_3": (0.2, 0.5, 1.0), "Tail_4": (0.4, 0.7, 1.0), "Tail_5": (0.6, 0.85, 1.0), "Tail_6": (0.85, 0.95, 1.0),
           "Clavicle": (1.0, 0.5, 0.0), "UpperArm": (1.0, 0.85, 0.1), "Forearm": (0.6, 1.0, 0.2),
           "Hand": (0.1, 0.95, 0.95), "Finger_1": (0.15, 0.3, 1.0), "Finger_2": (0.6, 0.2, 0.95),
           "Thigh": (0.55, 0.3, 0.9), "Shin": (0.65, 0.4, 0.2), "Foot": (0.95, 0.95, 0.85), "Toe": (0.25, 0.2, 0.15)}


def bone_color(name):
    return next((c for k, c in PALETTE.items() if name.startswith(k)), (0.5, 0.5, 0.5))


def setup():
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = RES
    w = bpy.data.worlds.new("rev")
    sc.world = w
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.31, 0.33, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    sun = bpy.data.objects.new("rev_sun", bpy.data.lights.new("rev_sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (0.6, 0.2, 0.5)
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("rev_cam", bpy.data.cameras.new("rev_cam"))
    cam.data.type = "ORTHO"
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def mesh_pts():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    m = ev.to_mesh()
    P = np.array([(body.matrix_world @ v.co)[:] for v in m.vertices])
    ev.to_mesh_clear()
    return P


def ground_plane(z):
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, z - 0.002))
    g = bpy.context.active_object
    gm = bpy.data.materials.new("rev_ground")
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.16, 0.16, 0.17, 1)
    g.data.materials.append(gm)
    return g


def bone_overlay():
    if "rev_bones" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["rev_bones"])
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new("rev_bones")
    bm = bmesh.new()
    mats = {}
    for pb in arm.pose.bones:
        h, t = arm.matrix_world @ pb.head, arm.matrix_world @ pb.tail
        d = t - h
        L = d.length
        if L < 1e-6:
            continue
        r = max(0.01, 0.12 * L)
        ax = d.normalized()
        u = ax.orthogonal().normalized()
        v = ax.cross(u)
        mid = h + d * 0.25
        ring = [bm.verts.new(mid + (u * math.cos(k * math.pi / 2) + v * math.sin(k * math.pi / 2)) * r) for k in range(4)]
        a_, b_ = bm.verts.new(h), bm.verts.new(t)
        key = pb.name
        if key not in mats:
            m = bpy.data.materials.new(f"rev_b_{key}")
            m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*bone_color(key), 1)
            m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*bone_color(key), 1)
            m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.6
            mats[key] = len(mats)
            me.materials.append(m)
        for k in range(4):
            for f in (bm.faces.new((a_, ring[k], ring[(k + 1) % 4])), bm.faces.new((ring[(k + 1) % 4], ring[k], b_))):
                f.material_index = mats[key]
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("rev_bones", me)
    sc.collection.objects.link(o)
    o.show_in_front = True
    return o


def ghost(on, alpha=0.35):
    if on:
        m = bpy.data.materials.get("rev_ghost") or bpy.data.materials.new("rev_ghost")
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = (0.75, 0.72, 0.68, 1)
        bs.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
        body["_saved"] = [s.material.name if s.material else "" for s in body.material_slots]
        for s in body.material_slots:
            s.material = m
    else:
        for s, n in zip(body.material_slots, body.get("_saved", [])):
            s.material = bpy.data.materials.get(n)


def dominant_colors():
    """Material: jede Ecke in der Farbe ihres stärksten Knochens (zeigt, welcher Teil woran hängt)."""
    me = body.data
    gname = {g.index: g.name for g in body.vertex_groups}
    cols = np.zeros((len(me.vertices), 4), np.float32)
    for v in me.vertices:
        gs = [(g.weight, gname[g.group]) for g in v.groups if g.weight > 0]
        if gs:
            gs.sort(reverse=True)
            c = np.array(bone_color(gs[0][1]))
            if len(gs) > 1 and gs[1][0] > 0.2:      # Übergang: mit der zweiten Farbe mischen
                c = c * (1 - gs[1][0]) + np.array(bone_color(gs[1][1])) * gs[1][0]
            cols[v.index] = (*c, 1)
    at = me.color_attributes.get("rev_dom") or me.color_attributes.new("rev_dom", "FLOAT_COLOR", "POINT")
    at.data.foreach_set("color", cols.ravel())
    m = bpy.data.materials.new("rev_dom")
    nt = m.node_tree
    an = nt.nodes.new("ShaderNodeAttribute")
    an.attribute_name = "rev_dom"
    nt.links.new(an.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    body["_saved"] = [s.material.name if s.material else "" for s in body.material_slots]
    for s in body.material_slots:
        s.material = m


VIEWS = {"front": Vector((1, 0, 0.08)), "side": Vector((0, 1, 0.05)), "back": Vector((-1, 0, 0.08)),
         "arpg": Vector((0.55, 0.45, 1.0)), "top": Vector((0.001, 0, 1))}


def fit(view, P):
    """Bildmitte + Maßstab so, dass alle Punkte P in dieser Ansicht ins Bild passen (Projektion auf die Bildachsen)."""
    d = VIEWS[view].normalized()
    q = (-d).to_track_quat("-Z", "Y")
    rx, uy = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0))
    a, b = P @ np.array(rx[:]), P @ np.array(uy[:])
    c = Vector(((P.max(0) + P.min(0)) / 2).tolist())
    c += rx * float((a.max() + a.min()) / 2 - np.array(rx[:]) @ np.array(c[:]))         + uy * float((b.max() + b.min()) / 2 - np.array(uy[:]) @ np.array(c[:]))
    return c, max(float(np.ptp(a)), float(np.ptp(b))) * 1.08


def shoot(cam, view, ctr, scale, path, P=None):
    d = VIEWS[view].normalized()
    if P is not None:
        ctr, scale = fit(view, P)
    cam.location = ctr + d * 6
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = scale
    cam.data.clip_end = 20
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(str(path))
    px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
    bpy.data.images.remove(img)
    path.unlink()
    return px


def save(rows, path):
    sheet = np.concatenate([np.concatenate(r, axis=1) for r in rows][::-1], axis=0)   # Blender-Bilder: unten zuerst
    out = bpy.data.images.new("rev_sheet", sheet.shape[1], sheet.shape[0], alpha=True)
    out.pixels.foreach_set(sheet.ravel())
    out.filepath_raw = str(path)
    out.file_format = "PNG"
    out.save()
    print("REVIEW_OK", path)


cam = setup()
tmp = OUT.with_name("_rev_tmp.png")
if MODE == "rig":
    if arm.animation_data:
        arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.matrix_basis.identity()
    bpy.context.view_layer.update()
    P = mesh_pts()
    ground_plane(P[:, 2].min())
    ctr = Vector(((P.max(0) + P.min(0)) / 2).tolist())
    scale = float((P.max(0) - P.min(0)).max()) * 1.12
    bone_overlay()
    row1 = []
    ghost(True)
    for v in ("front", "side", "top"):
        row1.append(shoot(cam, v, ctr, scale, tmp))
    ghost(False)
    bpy.data.objects["rev_bones"].hide_render = True
    dominant_colors()
    row2 = []
    for v in ("front", "side", "top"):
        row2.append(shoot(cam, v, ctr, scale, tmp))
    save([row1, row2], OUT)
else:
    act, frames = a[2], [int(x) for x in a[3].split(",")]
    views = a[4].split(",") if len(a) > 4 else ["arpg", "side"]
    arm.animation_data.action = bpy.data.actions[act]
    pts = []
    for f in frames:
        sc.frame_set(f)
        pts.append(mesh_pts())
    for pb in arm.pose.bones:
        pass
    allp = np.vstack(pts)
    sc.frame_set(0)
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.matrix_basis.identity()
    bpy.context.view_layer.update()
    rest_low = mesh_pts()[:, 2].min()
    arm.animation_data.action = bpy.data.actions[act]
    ground_plane(rest_low)
    ctr = Vector(((allp.max(0) + allp.min(0)) / 2).tolist())
    scale = float((allp.max(0) - allp.min(0)).max()) * 1.08
    rows = []
    with_weights = len(a) > 5 and "weights" in a[5]
    with_bones = len(a) > 5 and "bones" in a[5]
    for v in views:
        row = []
        for f in frames:
            sc.frame_set(f)
            row.append(shoot(cam, v, ctr, scale, tmp, allp))
        rows.append(row)
    if with_weights:                                    # gleiche Ansichten in Gewichts-Farben (+ Skelett): Risse/Dehnung
        dominant_colors()
        for v in views:
            row = []
            for f in frames:
                sc.frame_set(f)
                if with_bones:
                    bone_overlay()
                row.append(shoot(cam, v, ctr, scale, tmp, allp))
            rows.append(row)
    save(rows, OUT)
