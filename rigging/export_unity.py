"""Exportiert ein gerigtes + animiertes Blend (jedes Skelett) für Unity (FBX) und Web/Blender (GLB).

& "D:\\Blender\\blender.exe" -b <clips.blend> -P rigging/export_unity.py -- <ausgabeordner> <name> [<creature.toml>]

- dreht das Modell so, dass es in Unity nach +Z schaut (Blender: Kopf −Y)
- verkleinert Texturen auf [export] texture_size
- FBX: Flat Shading, keine Leaf-Bones, nur deformierende Knochen, Animation gebacken
- frei hängende Teile (nur wenn rigging/dangling.py das Mesh markiert hat, Attribut "_DANGLING"):
  FBX → Vertex-Farbe (linear, unverändert), GLB → eigenes Attribut "_DANGLING" (kein COLOR_0, sonst färben
  glTF-Programme das Modell ein), dazu <name>_dangling.json mit den Shader-Startwerten für Unity.
  Kreaturen ohne Markierung werden exakt wie bisher exportiert.
"""
import json
import math
import pathlib
import sys

import bpy

import tomllib

HERE = pathlib.Path(__file__).resolve().parent
a = sys.argv[sys.argv.index("--") + 1:]
OUT, NAME = pathlib.Path(a[0]).resolve(), a[1]
E = {"texture_size": 1024}
if len(a) > 2:                                       # creature.toml: [export] oder (alt) [crawler.export]
    ct = tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8"))
    E.update(ct.get("crawler", {}).get("export", {}))
    E.update(ct.get("export", {}))
OUT.mkdir(parents=True, exist_ok=True)

arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
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

# Frei hängende Teile: nur bei markiertem Mesh andere Export-Optionen + Startwerte für den Unity-Shader
dangle = body.data.color_attributes.get("_DANGLING")
fbx_extra, gltf_extra = {}, {}
dangle_json = OUT / f"{NAME}_dangling.json"
if dangle:
    fbx_extra = {"colors_type": "LINEAR"}                   # Werte 1:1 (Gewicht/Phase), keine sRGB-Umrechnung
    gltf_extra = {"export_vertex_color": "NONE", "export_attributes": True}
    dcfg = tomllib.loads((HERE / "dangling_defaults.toml").read_text(encoding="utf-8"))
    if len(a) > 2:
        dcfg.update(ct.get("dangling", {}))
    co = [body.matrix_world @ v.co for v in body.data.vertices]
    msize = max(max(c[i] for c in co) - min(c[i] for c in co) for i in range(3))
    wts = [d.color[0] for d in dangle.data]
    dangle_json.write_text(json.dumps({
        "attribute": "_DANGLING", "channels": "R = Gewicht (0 starr … 1 frei), G = Phase je Teil",
        "amplitude_m": round(dcfg["amplitude"] * msize, 4), "frequency_hz": dcfg["frequency"],
        "lag_rad": dcfg["lag"], "vertical": dcfg["vertical"],
        "dangling_vertices": sum(w > 1e-3 for w in wts), "vertices": len(wts)}, indent=2, ensure_ascii=False),
        encoding="utf-8")
elif dangle_json.exists():
    dangle_json.unlink()                                     # Markierung entfernt → alte Startwerte weg

bpy.ops.export_scene.fbx(
    filepath=str(OUT / f"{NAME}.fbx"), use_selection=False, object_types={"ARMATURE", "MESH"},
    apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
    mesh_smooth_type="FACE", add_leaf_bones=False, use_armature_deform_only=False,
    primary_bone_axis="Y", secondary_bone_axis="X",
    bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
    path_mode="COPY", embed_textures=True, **fbx_extra,
)
bpy.ops.export_scene.gltf(filepath=str(OUT / f"{NAME}.glb"), export_format="GLB", export_animations=True,
                          export_apply=False, **gltf_extra)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{NAME}.blend"))
info = {"name": NAME, "texture_size": size, "resized": resized,
        "clips": {a_.name: [int(v) for v in a_.frame_range] for a_ in bpy.data.actions}}
if dangle:
    info["dangling"] = dangle_json.name
print("EXPORT_OK", json.dumps(info, ensure_ascii=False))
