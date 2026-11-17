"""Exportiert ein gerigtes + animiertes Krabbler-Blend für Unity (FBX) und Web/Blender (GLB).

& "D:\\Blender\\blender.exe" -b <crawler_walk.blend> -P rigging/export_unity.py -- <ausgabeordner> <name> [<creature.toml>]

- dreht das Modell so, dass es in Unity nach +Z schaut (Blender: Kopf −Y)
- verkleinert Texturen auf [export] texture_size
- FBX: Flat Shading, keine Leaf-Bones, nur deformierende Knochen, Animation gebacken
"""
import json
import math
import pathlib
import sys

import bpy

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from crawler_rig import load_cfg  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
OUT, NAME = pathlib.Path(a[0]).resolve(), a[1]
cfg = load_cfg(a[2] if len(a) > 2 else None)
E = cfg.get("export", {})
OUT.mkdir(parents=True, exist_ok=True)

arm = bpy.data.objects["Crawler_Rig"]
body = bpy.data.objects["Body_Mesh"]

# Hilfsobjekte aus Prüf-Renders entfernen
for o in list(bpy.data.objects):
    if o not in (arm, body):
        bpy.data.objects.remove(o)

# Ausrichtung: Kopf +X → −Y (Unity-Konvention über FBX: −Y vorne in Blender = +Z in Unity)
for o in bpy.data.objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.rotation_euler = (0, 0, math.radians(-90))
body.parent = arm
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False, properties=False)
arm.name = NAME
arm.data.name = NAME + "_Rig"
body.name = NAME + "_Mesh"

# Texturen verkleinern
size = E.get("texture_size", 1024)
resized = []
for img in bpy.data.images:
    if img.size[0] > size:
        img.scale(size, size)
        resized.append(img.name)
    img.pack()

action = arm.animation_data.action if arm.animation_data else None
if action and action.name == "Walk":          # alter Einzel-Clip ohne Muster-Präfix
    action.name = E.get("clip_name", "Walk")
for act in bpy.data.actions:
    act.use_fake_user = True

bpy.ops.export_scene.fbx(
    filepath=str(OUT / f"{NAME}.fbx"), use_selection=False, object_types={"ARMATURE", "MESH"},
    apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
    mesh_smooth_type="FACE", add_leaf_bones=False, use_armature_deform_only=False,
    primary_bone_axis="Y", secondary_bone_axis="X",
    bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
    path_mode="COPY", embed_textures=True,
)
bpy.ops.export_scene.gltf(filepath=str(OUT / f"{NAME}.glb"), export_format="GLB", export_animations=True,
                          export_apply=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{NAME}.blend"))
info = {"name": NAME, "texture_size": size, "resized": resized,
        "clips": {a_.name: [int(v) for v in a_.frame_range] for a_ in bpy.data.actions}}
print("EXPORT_OK", json.dumps(info, ensure_ascii=False))
