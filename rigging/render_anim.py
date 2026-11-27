"""Rendert die aktive Animation eines Rigs als Einzelbilder aus mehreren Blickwinkeln.
Danach mit make_gif.py zu GIFs zusammensetzen.

& "D:\\Blender\\blender.exe" -b <blend> -P rigging/render_anim.py -- <ausgabeordner> [res]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
OUT = pathlib.Path(a[0]).resolve()
RES = int(a[1]) if len(a) > 1 else 360
CLIP = a[2] if len(a) > 2 else None          # Action-Name; ohne Angabe die aktive Action
VIEWS = a[3].split(",") if len(a) > 3 else ["side", "top", "arpg"]
OUT.mkdir(parents=True, exist_ok=True)
sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
if CLIP:
    arm.animation_data.action = bpy.data.actions[CLIP]
act = arm.animation_data.action
sc.frame_start, sc.frame_end = (int(v) for v in act.frame_range)
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = RES
w = bpy.data.worlds.new("w")
sc.world = w
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.32, 0.33, 0.35, 1)
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (0.6, 0.2, 0.5)
sc.collection.objects.link(sun)
# Boden als Kontaktreferenz (Füße müssen ihn berühren)
body = bpy.data.objects["Body_Mesh"]
zmin = min((body.matrix_world @ Vector(c)).z for c in body.bound_box)
if "ground_z" in sc:                          # opt-in (z. B. legless_kit [meta] render_ground = "rest"): Abtauchen sichtbar
    zmin = float(sc["ground_z"])
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, zmin - 0.002))
g = bpy.context.active_object
gm = bpy.data.materials.new("g")
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.18, 0.18, 0.19, 1)
g.data.materials.append(gm)
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = 1.4
sc.collection.objects.link(cam)
sc.camera = cam
views = {"side": (-90, 4), "top": (0, 89.9), "arpg": (-55, 50)}
for name, (az, el) in ((k, v) for k, v in views.items() if k in VIEWS):
    az, el = math.radians(az), math.radians(el)
    cam.location = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))) * 5
    cam.rotation_euler = (-cam.location).to_track_quat("-Z", "Y").to_euler()
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        sc.render.filepath = str(OUT / f"{name}_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
print("ANIM_RENDER_OK")
