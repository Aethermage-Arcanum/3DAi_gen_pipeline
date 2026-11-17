"""Blender-Teil der Modellprüfung (scripts/model_check.py). Nicht direkt aufrufen – der Python-Aufrufer macht das.

AUTOMATISCHE MESSUNG = NUR FRÜHWARNSYSTEM. Eine individuelle Sichtprüfung des Modells (Bilder ansehen, gegen Concept
und Referenzbilder vergleichen) durch den Agenten ist IMMER zusätzlich notwendig.

Zwei Modi (beide laden das rohe Tripo-Modell gleich: zusammenführen, Transformationen anwenden, vorn = +X drehen):

  export  <model.glb> <out.npz> <facing>
          Geometrie für die Messung in Python: Vertices, Dreiecke, Kanten, Teil je Vertex, Anzahl Mesh-Objekte,
          und je Fläche "Rückseite liegt frei" (Strahl nach hinten trifft nichts → einseitige/offene Fläche).
          Die Erkennung kommt unverändert aus rigging/double_sided.py (detect); zusätzlich je offener Fläche der
          Abstand bis zur nächsten Oberfläche dahinter (aufliegend = verdeckt, frei = von hinten sichtbar).
  render  <model.glb> <outdir> <facing> <marks.json>
          Vier orthografische Ansichten (vorn, Seite, oben, unten); Flächen aus marks.json werden rot
          (Auffälligkeit) bzw. orange (per creature.toml mit Begründung freigegeben) eingefärbt.
          Schreibt view_<name>.png + views.json (Kamera je Ansicht, damit Python Markierungen einzeichnen kann).

Koordinaten wie überall hier: Z oben, Kopf nach +X, Boden = tiefster Punkt (nicht verschoben, damit die Messung
„steht auf dem Boden“ ehrlich bleibt).
"""
import json
import math
import pathlib
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import double_sided  # noqa: E402
import rig_common as RC  # noqa: E402

ANGLE = {"+x": 0, "-y": 90, "-x": 180, "+y": -90}


def load(src, facing):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(src))
    n_objects = sum(1 for o in bpy.data.objects if o.type == "MESH")
    obj = RC.load_mesh(src)[0]        # setzt die Szene zurück, importiert neu, führt zusammen, wendet Transformationen an
    ang = ANGLE[facing]
    if ang:
        obj.rotation_euler = (0, 0, math.radians(ang))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return obj, n_objects


def do_export(src, out, facing):
    obj, n_objects = load(src, facing)
    V, part, _main = RC.arrays(obj)
    size = float(np.max(V.max(0) - V.min(0)))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    open_back = double_sided.detect(bm, size)
    # Zusatz für die Bewertung: wie weit hinter einer offenen Fläche liegt die nächste Oberfläche?
    # Nah (z. B. aufliegende Panzerplatte) = Rückseite vom Körper verdeckt, unsichtbar; nichts/fern (Flügel) = sichtbar.
    tree = BVHTree.FromBMesh(bm)
    eps = 1e-4 * size
    back_dist = np.full(len(bm.faces), np.inf)
    for i in np.where(open_back)[0]:
        f = bm.faces[int(i)]
        n = f.normal
        hit = tree.ray_cast(f.calc_center_median() - n * eps, -n, 2 * size)
        if hit[0] is not None:
            back_dist[i] = hit[3] / size
    bm.free()
    me = obj.data
    me.calc_loop_triangles()
    tris = np.array([t.vertices[:] for t in me.loop_triangles], dtype=np.int32).reshape(-1, 3)
    tri_poly = np.array([t.polygon_index for t in me.loop_triangles], dtype=np.int32)
    edges = np.array([e.vertices[:] for e in me.edges], dtype=np.int32).reshape(-1, 2)
    np.savez_compressed(out, V=V, tris=tris, tri_poly=tri_poly, edges=edges, part=part,
                        poly_open=open_back, back_dist=back_dist, n_polys=len(me.polygons), n_objects=n_objects,
                        n_materials=len([s for s in obj.material_slots if s.material]))
    print("MODELCHECK_EXPORT_OK", len(V), len(tris))


def do_render(src, outdir, facing, marks_path):
    outdir.mkdir(parents=True, exist_ok=True)
    marks = json.loads(pathlib.Path(marks_path).read_text(encoding="utf-8"))
    obj, _ = load(src, facing)
    me = obj.data
    # Markierungsfarben als zusätzliche Materialien (nur fürs Bild, das Modell wird nicht gespeichert)
    slot_of = {}
    for name, rgb in (("rot", (1.0, 0.02, 0.02)), ("orange", (1.0, 0.45, 0.0))):
        polys = marks.get(name, [])
        if not polys:
            continue
        m = bpy.data.materials.new(f"MC_{name}")
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = 0.8
        obj.data.materials.append(m)
        slot_of[name] = len(obj.data.materials) - 1
        idx = np.zeros(len(me.polygons), np.int32)
        me.polygons.foreach_get("material_index", idx)
        idx[np.asarray(polys, dtype=np.int64)] = slot_of[name]
        me.polygons.foreach_set("material_index", idx)
    me.update()

    V = np.array([v.co[:] for v in me.vertices])
    mn, mx = V.min(0), V.max(0)
    center = (mn + mx) / 2
    ext = mx - mn
    res = int(marks.get("res", 560))

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 8         # Prüfbild, kein Schönbild – schnell
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("W")
    sc.world = world
    if not world.node_tree:                  # Blender 5: Node-Baum ist Standard, use_nodes veraltet
        world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.42, 0.43, 0.45, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.1
    for rot, energy in (((math.radians(40), 0, math.radians(30)), 2.5), ((math.radians(160), 0, math.radians(-40)), 0.8)):
        sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
        sun.data.energy = energy
        sun.rotation_euler = rot
        sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    sc.collection.objects.link(cam)
    sc.camera = cam

    # Ansicht: Name → (Bildrechts, Bildoben); Blickrichtung = oben × rechts
    views = {
        "vorn": ((0, 1, 0), (0, 0, 1)),     # Kamera vor dem Kopf, blickt nach −X
        "seite": ((1, 0, 0), (0, 0, 1)),    # Kamera rechts (−Y), Kopf zeigt im Bild nach rechts
        "oben": ((1, 0, 0), (0, 1, 0)),     # von oben, Kopf rechts
        "unten": ((1, 0, 0), (0, -1, 0)),   # von unten, Kopf rechts
    }
    info = {}
    for name, (r, u) in views.items():
        r, u = Vector(r), Vector(u)
        back = r.cross(u)                    # Kamera blickt entlang −back
        # Bildausschnitt: Ausdehnung in Bild-Richtungen
        w = abs(r.x) * ext[0] + abs(r.y) * ext[1] + abs(r.z) * ext[2]
        h = abs(u.x) * ext[0] + abs(u.y) * ext[1] + abs(u.z) * ext[2]
        scale = max(w, h) * 1.12
        cam.data.ortho_scale = scale
        dist = float(np.max(ext)) * 3
        c = Vector(center.tolist())
        cam.location = c + back * dist
        cam.data.clip_end = dist * 3
        rot = Matrix((r, u, back)).transposed()
        cam.rotation_euler = rot.to_euler()
        sc.render.filepath = str(outdir / f"view_{name}.png")
        bpy.ops.render.render(write_still=True)
        info[name] = {"center": center.tolist(), "right": list(r), "up": list(u), "ortho_scale": scale, "res": res}
    (outdir / "views.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print("MODELCHECK_RENDER_OK")


if __name__ == "__main__":
    a = sys.argv[sys.argv.index("--") + 1:]
    mode = a[0]
    if mode == "export":
        do_export(pathlib.Path(a[1]).resolve(), pathlib.Path(a[2]).resolve(), a[3])
    elif mode == "render":
        do_render(pathlib.Path(a[1]).resolve(), pathlib.Path(a[2]).resolve(), a[3], a[4])
    else:
        raise SystemExit(f"Unbekannter Modus {mode}")
