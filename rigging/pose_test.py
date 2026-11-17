"""Selbstprüfung des Rigs: Skelett-Overlay + Testpose (Beine heben, Kopf drehen) aus mehreren Blickwinkeln.

& "D:\\Blender\\blender.exe" -b <hexapod_rigged.blend> -P rigging/pose_test.py -- <ausgabeordner>
"""
import colorsys
import math
import pathlib
import sys

import bmesh
import bpy
from mathutils import Euler, Vector

OUT = pathlib.Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
arm = bpy.data.objects["Hexapod_Rig"]
body = bpy.data.objects["Body_Mesh"]
sc = bpy.context.scene


def bone_overlay():
    """Knochen als farbige Prismen (folgt der aktuellen Pose)."""
    if "BoneViz" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["BoneViz"])
    bm = bmesh.new()
    me = bpy.data.meshes.new("BoneViz")
    chains = sorted({b.name.rsplit("_", 1)[0] for b in arm.pose.bones})
    for i, c in enumerate(chains):
        m = bpy.data.materials.new(f"bv{i}")
        rgb = colorsys.hsv_to_rgb((i * 0.618) % 1, 0.8, 1)
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = (*rgb, 1)
        bs.inputs["Emission Color"].default_value = (*rgb, 1)
        bs.inputs["Emission Strength"].default_value = 4
        me.materials.append(m)
    r = 0.006
    for pb in arm.pose.bones:
        h, t = arm.matrix_world @ pb.head, arm.matrix_world @ pb.tail
        dv = t - h
        if dv.length < 1e-5:
            continue
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=r * 1.8, radius2=r * 0.5, depth=dv.length)
        rot = dv.to_track_quat("Z", "Y").to_matrix().to_4x4()
        idx = chains.index(pb.name.rsplit("_", 1)[0])
        for v in res["verts"]:
            v.co = rot @ (v.co + Vector((0, 0, dv.length / 2))) + h
            for f in v.link_faces:
                f.material_index = idx
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("BoneViz", me)
    ob.show_in_front = True
    sc.collection.objects.link(ob)


def setup():
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = 700
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.31, 0.33, 1)
    sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (0.6, 0.2, 0.5)
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.35
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def shoot(cam, name, az, el):
    az, el = math.radians(az), math.radians(el)
    cam.location = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))) * 5
    cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)


cam = setup()
body.data.materials[0].surface_render_method = "BLENDED" if False else body.data.materials[0].surface_render_method

# --- Ruhepose mit Skelett ---
bone_overlay()
shoot(cam, "rest_top", 0, 89.9)
shoot(cam, "rest_side", -90, 5)

# --- Testpose: Dreifuß-Gruppe A heben, Gruppe B nach hinten, Kopf + Hinterleib drehen ---
group_a = ["L1", "R2", "L3", "R4"]
for pb in arm.pose.bones:
    pb.rotation_mode = "XYZ"
for leg in ["L1", "L2", "L3", "L4", "R1", "R2", "R3", "R4"]:
    fem = arm.pose.bones[f"Leg_{leg}_Femur"]
    cox = arm.pose.bones[f"Leg_{leg}_Coxa"]
    if leg in group_a:
        fem.rotation_euler = Euler((math.radians(-35), 0, 0))   # anheben
    else:
        cox.rotation_euler = Euler((0, 0, math.radians(20 if leg[0] == "L" else -20)))  # nach hinten schwingen
arm.pose.bones["Head"].rotation_euler = Euler((0, 0, math.radians(25)))
arm.pose.bones["Abdomen_1"].rotation_euler = Euler((math.radians(15), 0, 0))
bpy.context.view_layer.update()
bone_overlay()
shoot(cam, "pose_top", 0, 89.9)
shoot(cam, "pose_side", -90, 5)
shoot(cam, "pose_arpg", -60, 50)
bpy.data.objects["BoneViz"].hide_render = True
shoot(cam, "pose_arpg_clean", -60, 50)
print("POSE_TEST_OK")
