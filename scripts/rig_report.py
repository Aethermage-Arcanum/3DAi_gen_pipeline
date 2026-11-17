"""Analysiert ein Tripo-Rig: Knochen-Hierarchie, Ketten (Beine/Wirbelsäule) und deren Lage.

Aufruf: & "D:\\Blender\\blender.exe" -b --factory-startup -P scripts/rig_report.py -- <rig.glb> [<ausgabe.json>]
"""
import json
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])

arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("OBJECTS", [(o.name, o.type, len(o.data.vertices) if o.type == "MESH" else "") for o in bpy.data.objects])

# Gewichtsanteil pro Knochen (wie viele Vertices hängen hauptsächlich daran)
main_bone = {}
for o in meshes:
    names = {g.index: g.name for g in o.vertex_groups}
    for v in o.data.vertices:
        if v.groups:
            g = max(v.groups, key=lambda g: g.weight)
            main_bone[names[g.group]] = main_bone.get(names[g.group], 0) + 1

M = arm.matrix_world
bones = []
for b in arm.data.bones:
    h, t = M @ b.head_local, M @ b.tail_local
    bones.append({"name": b.name, "parent": b.parent.name if b.parent else None,
                  "children": [c.name for c in b.children],
                  "head": [round(x, 3) for x in h], "tail": [round(x, 3) for x in t],
                  "verts": main_bone.get(b.name, 0)})


# Ketten: von jedem Knochen mit !=1 Kindern bzw. Wurzel aus, linear nach unten folgen
def chain_from(name):
    out = [name]
    b = arm.data.bones[name]
    while len(b.children) == 1:
        b = b.children[0]
        out.append(b.name)
    return out


chains = []
for b in arm.data.bones:
    if b.parent is None or len(b.parent.children) > 1:
        chains.append(chain_from(b.name))
info = {"armature": arm.name, "bones": bones, "chains": chains}
for c in chains:
    start = M @ arm.data.bones[c[0]].head_local
    end = M @ arm.data.bones[c[-1]].tail_local
    print("CHAIN", len(c), c[0], "->", c[-1], "start", [round(x, 2) for x in start], "end", [round(x, 2) for x in end],
          "verts", sum(main_bone.get(n, 0) for n in c))
if len(args) > 1:
    open(args[1], "w", encoding="utf-8").write(json.dumps(info, indent=1, ensure_ascii=False))
