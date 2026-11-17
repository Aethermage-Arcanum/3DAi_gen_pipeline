"""Visualisiert die Anatomie-Erkennung: Inseln nach Gruppe eingefärbt + Gelenkpunkte.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/debug_detect.py -- <mesh.glb> <ausgabeordner>
"""
import colorsys
import pathlib
import sys
import tomllib

import bmesh
import bpy
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from crawler_detect import detect  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = pathlib.Path(args[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
cfg = tomllib.loads((HERE / "crawler_defaults.toml").read_text(encoding="utf-8"))["detect"]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
obj = next(o for o in bpy.data.objects if o.type == "MESH")
d = detect(obj, cfg)

print("DETECT legs", len(d["legs"]), "body islands", len(d["body"]), "antennae", len(d["antennae"]),
      "mandibles", len(d["mandibles"]), "others", len(d["others"]), "total", len(d["islands"]))
for line in d["debug"]:
    print("  DBG", line)
for l in d["legs"]:
    print(f"  LEG {l['side']}{l.get('slot')} islands={len(l['islands'])} joints={len(l['joints'])} "
          f"root={tuple(round(x, 2) for x in l['joints'][0])} tip={tuple(round(x, 2) for x in l['joints'][-1])}")


def mat(name, rgb, emit=0.0):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Emission Color"].default_value = (*rgb, 1)
    b.inputs["Emission Strength"].default_value = emit
    return m


me = obj.data
me.materials.clear()
groups = {"body": mat("body", (0.35, 0.35, 0.38)), "ant": mat("ant", (1, 0.9, 0.1)),
          "man": mat("man", (0.7, 0.2, 1)), "oth": mat("oth", (1, 1, 1), 0.5)}
for m in groups.values():
    me.materials.append(m)
leg_mat_index = {}
for n, l in enumerate(d["legs"]):
    rgb = colorsys.hsv_to_rgb((n * 0.13) % 1, 0.9, 1)
    me.materials.append(mat(f"leg{n}", rgb))
    leg_mat_index[n] = len(me.materials) - 1
vert_group = {}
for i in d["body"]:
    for v in d["islands"][i]["verts"]:
        vert_group[v] = 0
for i in d["antennae"]:
    for v in d["islands"][i]["verts"]:
        vert_group[v] = 1
for i in d["mandibles"]:
    for v in d["islands"][i]["verts"]:
        vert_group[v] = 2
for i in d["others"]:
    for v in d["islands"][i]["verts"]:
        vert_group[v] = 3
for n, l in enumerate(d["legs"]):
    for i in l["islands"]:
        for v in d["islands"][i]["verts"]:
            vert_group[v] = leg_mat_index[n]
for p in me.polygons:
    p.material_index = vert_group.get(p.vertices[0], 3)
    p.use_smooth = False

# Gelenkpunkte als kleine Kugeln + Verbindungslinien
bm = bmesh.new()
r = d["size"] * 0.012
for l in d["legs"]:
    for a, b in zip(l["joints"], l["joints"][1:]):
        dvec = b - a
        if dvec.length < 1e-6:
            continue
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=r * 0.6, radius2=r * 0.6, depth=dvec.length)
        rot = dvec.to_track_quat("Z", "Y").to_matrix().to_4x4()
        for v in res["verts"]:
            v.co = rot @ (v.co + Vector((0, 0, dvec.length / 2))) + a
    for j in l["joints"]:
        s = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in s["verts"]:
            v.co += j
jm = bpy.data.meshes.new("joints")
bm.to_mesh(jm)
bm.free()
jo = bpy.data.objects.new("joints", jm)
jm.materials.append(mat("j", (1, 0.15, 0.1), 2))
bpy.context.scene.collection.objects.link(jo)

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 800
w = bpy.data.worlds.new("w")
sc.world = w
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.08, 0.08, 0.09, 1)
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN"))
sun.data.energy = 3
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = d["size"] * 1.2
sc.collection.objects.link(cam)
sc.camera = cam
for name, loc, rot in (("top", (0, 0, 5), (0, 0, 0)), ("side", (0, -5, 0), (1.5708, 0, 0)),
                       ("front", (5, 0, 0), (1.5708, 0, 1.5708))):
    cam.location, cam.rotation_euler = loc, rot
    sc.render.filepath = str(OUT / f"detect_{name}.png")
    bpy.ops.render.render(write_still=True)
print("DEBUG_OK")
