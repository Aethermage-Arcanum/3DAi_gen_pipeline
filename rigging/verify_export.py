"""Gegentest: exportierte FBX/GLB frisch importieren und Kennzahlen prüfen.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/verify_export.py -- <datei.fbx|glb> [<report.json>]
"""
import json
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
path = a[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
if path.lower().endswith(".fbx"):
    bpy.ops.import_scene.fbx(filepath=path)
else:
    bpy.ops.import_scene.gltf(filepath=path)
arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
# Nur echte Modell-Meshes (am Rig hängend). Der glTF-Import erzeugt zusätzlich eine "Icosphere"
# als Knochen-Anzeigeform – die steckt nicht in der Datei und wird ignoriert.
meshes = [o for o in bpy.data.objects if o.type == "MESH"
          and (o.parent in arms or any(m.type == "ARMATURE" for m in o.modifiers))]
dg = bpy.context.evaluated_depsgraph_get()
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
bones = [b.name for a_ in arms for b in a_.data.bones]
# Standard-Skelette: Pflichtknochen, Rumpfknochen (für Blickrichtung), Fuß zum Bewegungstest
QL = [f"Leg_{n}_{k}" for n in ("FL", "FR", "BL", "BR") for k in range(1, 5)]
SKELETONS = {
    "crawler": {"marker": "Thorax", "body": "Thorax", "foot": "Leg_L3_Tarsus",
                "std": {"Root", "Thorax", "Abdomen_1", "Abdomen_2", "Head"} |
                {f"Leg_{s}{k}_{p}" for s in "LR" for k in range(1, 5) for p in ("Coxa", "Femur", "Tibia", "Tarsus")}},
    "quadruped": {"marker": "Leg_FL_1", "body": "Chest", "foot": "Leg_FL_4",
                  "std": {"Root", "Hips", "Spine_1", "Chest", "Neck_1", "Neck_2", "Head", "Jaw",
                          "Tail_1", "Tail_2", "Tail_3", "Tail_4", "Shoulder_FL", "Shoulder_FR"} | set(QL)},
    "legless": {"marker": "Spine_01", "body": "Spine_01", "foot": None,
                "std": {"Root", "Spine_01", "Head", "Jaw"}},
}
SK_NAME = next((k for k, v in SKELETONS.items() if v["marker"] in bones), None)
SK = SKELETONS.get(SK_NAME, {"std": set(), "body": None, "foot": None})
std = SK["std"]
missing = sorted(std - set(bones))
unweighted = 0
maxinf = 0
for o in meshes:
    for v in o.data.vertices:
        n = sum(1 for g in v.groups if g.weight > 1e-4)
        maxinf = max(maxinf, n)
        unweighted += n == 0
# Blickrichtung: Kopfknochen relativ zum Thorax
facing = None
if arms and "Head" in arms[0].data.bones and SK["body"]:
    h = arms[0].matrix_world @ arms[0].data.bones["Head"].tail_local
    t = arms[0].matrix_world @ arms[0].data.bones[SK["body"]].head_local
    d = (h - t).normalized()
    facing = [round(c, 2) for c in d]
# Animation abspielen: bewegen sich die Füße?
moved = None
if arms and bpy.data.actions and SK["foot"]:
    arm = arms[0]
    # Fußbewegung am Lauf-Clip prüfen (in Stand-Clips wie Attack stehen die Füße absichtlich still)
    act = next((x for x in bpy.data.actions if "Walk" in x.name), bpy.data.actions[0])
    arm.animation_data_create()
    arm.animation_data.action = act
    f0, f1 = (int(x) for x in act.frame_range)
    tip = lambda: (arm.matrix_world @ arm.pose.bones[SK["foot"]].tail).copy()
    bpy.context.scene.frame_set(f0)
    p0 = tip()
    bpy.context.scene.frame_set((f0 + f1) // 2)
    moved = round((tip() - p0).length, 4)
dims = None
if meshes:
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    dims = [round(max(p[i] for p in pts) - min(p[i] for p in pts), 3) for i in range(3)]
r = {"skeleton": SK_NAME, "file": path.split("\\")[-1].split("/")[-1], "meshes": len(meshes), "triangles": tris, "bones": len(bones),
     "missing_standard_bones": missing, "unweighted_vertices": unweighted, "max_influences": maxinf,
     "materials": sorted({s.material.name for o in meshes for s in o.material_slots if s.material}),
     "textures": [[i.name, list(i.size)] for i in bpy.data.images if i.size[0]],
     "actions": [[x.name, [int(v) for v in x.frame_range]] for x in bpy.data.actions],
     "head_direction_blender": facing, "foot_moves_m": moved, "dimensions_m": dims}
r["ok"] = (not missing and unweighted == 0 and bool(r["actions"]) and (moved is None and SK_NAME == "legless" or (moved or 0) > 0.001))
print("VERIFY", json.dumps(r, ensure_ascii=False))
if len(a) > 1:
    open(a[1], "w", encoding="utf-8").write(json.dumps(r, indent=2, ensure_ascii=False))
