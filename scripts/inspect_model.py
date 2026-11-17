"""Prüft ein GLB/FBX in Blender: Kennzahlen + Vorschau-Renders (Ansichten + Animations-Frames).

Aufruf:
  & "D:\\Blender\\blender.exe" -b --factory-startup -P scripts/inspect_model.py -- <modell.glb> <ausgabeordner>
Ergebnis: <ausgabeordner>/stats.json, view_*.png, anim_*.png
"""
import json
import math
import pathlib
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(args[0]).resolve(), pathlib.Path(args[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
if SRC.suffix.lower() == ".fbx":
    bpy.ops.import_scene.fbx(filepath=str(SRC))
else:
    bpy.ops.import_scene.gltf(filepath=str(SRC))

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]

dg = bpy.context.evaluated_depsgraph_get()
tris = verts = 0
for o in meshes:
    me = o.evaluated_get(dg).to_mesh()
    tris += sum(len(p.vertices) - 2 for p in me.polygons)
    verts += len(me.vertices)
    o.evaluated_get(dg).to_mesh_clear()

stats = {
    "datei": SRC.name,
    "meshes": len(meshes),
    "dreiecke": tris,
    "vertices": verts,
    "materialien": sorted({s.material.name for o in meshes for s in o.material_slots if s.material}),
    "texturen": [{"name": i.name, "größe": list(i.size)} for i in bpy.data.images if i.size[0]],
    "uv_maps": sorted({uv.name for o in meshes for uv in o.data.uv_layers}),
    "knochen": sum(len(a.data.bones) for a in arms),
    "knochen_namen": [b.name for a in arms for b in a.data.bones],
    "max_gewichte_pro_vertex": max((sum(1 for g in v.groups if g.weight > 0.001)
                                    for o in meshes for v in o.data.vertices), default=0),
    "animationen": [{"name": a.name, "frames": [int(a.frame_range[0]), int(a.frame_range[1])]}
                    for a in bpy.data.actions],
}

# Bounding Box über alle Meshes (Weltkoordinaten)
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
size = mx - mn
stats["maße_m"] = [round(size.x, 3), round(size.y, 3), round(size.z, 3)]
(OUT / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
print("STATS", json.dumps({k: v for k, v in stats.items() if k != "knochen_namen"}, ensure_ascii=False))

# ---------- Szene ----------
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 640
sc.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("W")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.36, 0.38, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sun.data.energy = 2.5
sun.rotation_euler = (math.radians(40), 0, math.radians(30))
sc.collection.objects.link(sun)

center = (mn + mx) / 2
radius = max(size) * 1.25
target = bpy.data.objects.new("T", None)
target.location = center
sc.collection.objects.link(target)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(size) * 1.3
cam.constraints.new("TRACK_TO").target = target
sc.collection.objects.link(cam)
sc.camera = cam


def shoot(name, azimuth_deg, elevation_deg, frame=None):
    if frame is not None:
        sc.frame_set(frame)
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    cam.location = center + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * radius * 3
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)


start = int(min((a.frame_range[0] for a in bpy.data.actions), default=1))
shoot("view_1_arpg", 35, 50, start)       # typischer ARPG-Blick
shoot("view_2_side", 90, 5, start)
shoot("view_3_front", 0, 10, start)
shoot("view_4_top", 0, 89, start)
if bpy.data.actions:
    a0, a1 = (int(v) for v in bpy.data.actions[0].frame_range)
    for i in range(6):
        f = a0 + round((a1 - a0) * i / 6)
        shoot(f"anim_{i}", 90, 5, f)
print("INSPECT_OK")
