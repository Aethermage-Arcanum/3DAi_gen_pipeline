"""Rendert das Skelett eines Rigs als farbige Linien über das (halbtransparente) Modell.

Aufruf: & "D:\\Blender\\blender.exe" -b --factory-startup -P scripts/render_rig.py -- <rig.glb> <ausgabe.png>
"""
import colorsys
import math
import sys

import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
meshes = [o for o in bpy.data.objects if o.type == "MESH"]

ghost = bpy.data.materials.new("ghost")
ghost.use_nodes = True
bsdf = ghost.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1)
bsdf.inputs["Alpha"].default_value = 0.25
ghost.surface_render_method = "BLENDED"
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append(ghost)

# Knochen als dünne Prismen, jede Kette eigene Farbe
M = arm.matrix_world
bm = bmesh.new()
mats = []
roots = [b for b in arm.data.bones if b.parent is None or len(b.parent.children) > 1]
color_of = {}
for i, r in enumerate(roots):
    stack = [r]
    while stack:
        b = stack.pop()
        color_of[b.name] = i
        if len(b.children) == 1:
            stack.append(b.children[0])
for i in range(len(roots)):
    m = bpy.data.materials.new(f"c{i}")
    m.use_nodes = True
    rgb = colorsys.hsv_to_rgb((i * 0.618) % 1, 0.85, 1)
    em = m.node_tree.nodes["Principled BSDF"]
    em.inputs["Emission Color"].default_value = (*rgb, 1)
    em.inputs["Emission Strength"].default_value = 3
    em.inputs["Base Color"].default_value = (*rgb, 1)
    mats.append(m)

bone_me = bpy.data.meshes.new("bones")
bone_ob = bpy.data.objects.new("bones", bone_me)
bpy.context.scene.collection.objects.link(bone_ob)
for m in mats:
    bone_me.materials.append(m)
for b in arm.data.bones:
    h, t = M @ b.head_local, M @ b.tail_local
    d = t - h
    if d.length < 1e-5:
        continue
    r = 0.008
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=r * 1.6, radius2=r * 0.6, depth=d.length)
    rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    for v in res["verts"]:
        v.co = rot @ (v.co + Vector((0, 0, d.length / 2))) + h
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = color_of.get(b.name, 0)
    ball = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r * 2.2)
    for v in ball["verts"]:
        v.co += h
        for f in v.link_faces:
            f.material_index = color_of.get(b.name, 0)
bm.to_mesh(bone_me)
bm.free()

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 900
w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.05, 0.06, 1)
pts = [o.matrix_world @ Vector(c) for o in meshes if len(o.data.vertices) > 100 for c in o.bound_box]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(mx - mn) * 1.15
cam.location = ((mn + mx) / 2) + Vector((0, 0, 5))
sc.collection.objects.link(cam)
sc.camera = cam
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN"))
sc.collection.objects.link(sun)
sc.render.filepath = args[1]
bpy.ops.render.render(write_still=True)
print("RIG_RENDER_OK", len(roots), "Ketten")
