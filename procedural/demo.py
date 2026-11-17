"""Demo: Test-Grundkörper + "Monster Anbauteile" → Varianten rendern.

Aufruf (headless):
  & "D:\\Blender\\blender.exe" -b --factory-startup -P procedural/demo.py -- <ausgabeordner>
Ergebnis: <ausgabeordner>/variant_N.png, stats.json, procedural_parts.blend (zum Selbst-Ausprobieren)
"""
import json
import math
import pathlib
import random
import sys
import tomllib

import bmesh
import bpy
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from addon_nodes import apply_settings, build_addon_group  # noqa: E402

OUT = pathlib.Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)


def make_material(name, color, emission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.65
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = emission
    return m


def build_test_body():
    """Einfacher Low-Poly-Vierbeiner als Platzhalter (später: echter Tripo-Grundkörper)."""
    rnd = random.Random(3)
    parts = []

    def add(op, **kw):
        op(**kw)
        parts.append(bpy.context.active_object)
        return parts[-1]

    t = add(bpy.ops.mesh.primitive_ico_sphere_add, subdivisions=2, radius=1, location=(0, 0, 0.95))
    t.scale = (0.75, 1.45, 0.62)
    h = add(bpy.ops.mesh.primitive_ico_sphere_add, subdivisions=2, radius=1, location=(0, -1.55, 1.05))
    h.scale = (0.42, 0.55, 0.38)
    for sx in (-1, 1):
        for y in (-0.75, 0.8):
            leg = add(bpy.ops.mesh.primitive_cone_add, vertices=5, radius1=0.17, radius2=0.08, depth=1.0,
                      location=(sx * 0.62, y, 0.48), rotation=(0, sx * math.radians(-18), 0))
    tail = add(bpy.ops.mesh.primitive_cone_add, vertices=5, radius1=0.2, radius2=0.02, depth=1.1,
               location=(0, 1.75, 0.95), rotation=(math.radians(-70), 0, 0))

    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    body = bpy.context.active_object
    body.name = "Testkoerper"
    # leichte Unregelmäßigkeit für organischen Low-Poly-Look
    bm = bmesh.new()
    bm.from_mesh(body.data)
    for v in bm.verts:
        v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.035
    bm.to_mesh(body.data)
    bm.free()
    return body


def setup_scene():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 800, 600
    sc.view_settings.view_transform = "AgX"
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.06, 0.08, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.2

    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.data.materials.append(make_material("Boden", (0.07, 0.07, 0.075)))

    sun = bpy.data.objects.new("Sonne", bpy.data.lights.new("Sonne", "SUN"))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(30))
    sc.collection.objects.link(sun)

    target = bpy.data.objects.new("Ziel", None)
    target.location = (0, 0, 0.7)
    sc.collection.objects.link(target)
    cam = bpy.data.objects.new("Kamera", bpy.data.cameras.new("Kamera"))
    cam.data.lens = 45
    # ARPG-typischer Blickwinkel: schräg von oben (~50°), leicht seitlich
    cam.location = (4.6, -5.4, 6.2)
    c = cam.constraints.new("TRACK_TO")
    c.target = target
    sc.collection.objects.link(cam)
    sc.camera = cam


def tri_count(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    ev.to_mesh_clear()
    return n


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_scene()
    body = build_test_body()
    ng = build_addon_group()
    mod = body.modifiers.new("Monster Anbauteile", "NODES")
    mod.node_group = ng

    variants = tomllib.loads((HERE / "demo_variants.toml").read_text(encoding="utf-8"))["variant"]
    # Standardwerte aus der Node-Gruppe, damit jede Variante bei null anfängt
    from addon_nodes import socket_ids
    defaults = {it.name: it.default_value for it in ng.interface.items_tree
                if getattr(it, "item_type", "") == "SOCKET" and it.in_out == "INPUT"
                and it.socket_type in ("NodeSocketFloat", "NodeSocketInt", "NodeSocketBool")}

    stats = []
    for i, v in enumerate(variants, 1):
        mats = {
            "Körper Material": make_material(f"Koerper_{i}", tuple(v["body_color"])),
            "Stachel Material": make_material(f"Stachel_{i}", tuple(v.get("spike_color", [0.8, 0.75, 0.65])),
                                              v.get("spike_emission", 0.0)),
            "Platten Material": make_material(f"Platten_{i}", tuple(v.get("plate_color", [0.4, 0.4, 0.4]))),
        }
        settings = dict(defaults)
        settings.update(v.get("settings", {}))
        settings.update(mats)
        apply_settings(body, mod, settings)
        bpy.context.view_layer.update()
        tris = tri_count(body)
        bpy.context.scene.render.filepath = str(OUT / f"variant_{i}.png")
        bpy.ops.render.render(write_still=True)
        stats.append({"index": i, "label": v["label"], "tris": tris})
        print(f"VARIANT {i}: {v['label']} – {tris} Dreiecke", flush=True)

    (OUT / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "procedural_parts.blend"))
    print("DEMO_OK")


main()
