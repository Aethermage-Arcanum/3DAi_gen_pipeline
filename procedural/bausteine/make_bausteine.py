"""Baustein-Bibliothek (Varianten-Baukasten, Spec 3.4) – headless, reproduzierbar.

Erzeugt pro Typ 2–3 Low-Poly-Formen im facettierten Stil (Artist B) und schreibt:
  procedural/bausteine/<typ>.fbx   alle Formen des Typs als einzelne Objekte (für Blender/Menschen, Standard-Format)
  procedural/bausteine/<typ>.glb   dasselbe als glTF
  procedural/bausteine/<typ>.json  Werte jeder Form + die Meshes selbst (achsen-eindeutig, liest der Unity-Baukasten)

Koordinaten aller Formen: X = vorn/Länge, Y = links/Breite, Z = oben/Höhe (wie die Kreaturen in Blender),
Ursprung = Mitte der Unterseite (z = 0 sitzt auf der Haut), größte Ausdehnung = 1.0.
Die Variante skaliert das Teil mit `groesse` (Anteil Kreaturgröße) und `streckung` [Länge, Breite, Höhe].

Aufruf:
  & "D:\\Blender\\blender.exe" -b --factory-startup -P procedural/bausteine/make_bausteine.py
  optional:  -- --typ basaltbrocken     (nur einen Typ bauen)
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

VERSION = "0.1.0"
OUT = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------------------------- Formen (Werte)
# Pro Typ die Formen mit ihren Werkbank-Werten (Spec 3.4: Form-Regler). Seed = Reproduzierbarkeit.
TYPEN = {
    "basaltbrocken": {
        "basalt_a": {"ecken": 6, "blockig": 0.7, "dicke": 0.62, "streckung": [1.0, 0.85], "seed": 11},
        "basalt_b": {"ecken": 5, "blockig": 0.5, "dicke": 0.72, "streckung": [1.0, 0.75], "seed": 23},
        "basalt_c": {"ecken": 7, "blockig": 0.85, "dicke": 0.48, "streckung": [1.0, 0.95], "seed": 37},
    },
    "steinplatte": {
        "stein_a": {"ecken": 6, "dicke": 0.26, "woelbung": 0.12, "kantenfase": 0.10, "seed": 5},
        "stein_b": {"ecken": 5, "dicke": 0.30, "woelbung": 0.15, "kantenfase": 0.14, "seed": 17},
        "stein_c": {"ecken": 7, "dicke": 0.22, "woelbung": 0.08, "kantenfase": 0.08, "seed": 29},
    },
    "felszacke": {
        "zacke_a": {"kanten": 4, "schlankheit": 0.42, "bruchkante": 0.25, "spitze_versatz": 0.12, "seed": 3},
        "zacke_b": {"kanten": 5, "schlankheit": 0.50, "bruchkante": 0.35, "spitze_versatz": 0.20, "seed": 13},
        "zacke_c": {"kanten": 4, "schlankheit": 0.34, "bruchkante": 0.15, "spitze_versatz": 0.06, "seed": 41},
    },
}


def ring(n, rnd, jitter_r=0.18, jitter_a=0.35, sx=1.0, sy=1.0, z=0.0, phase=None):
    """Unregelmäßiges n-Eck (Radius ~0.5) in der Höhe z."""
    phase = rnd.uniform(0, math.tau) if phase is None else phase
    pts = []
    for i in range(n):
        a = phase + (i + rnd.uniform(-jitter_a, jitter_a) * 0.5) * math.tau / n
        r = 0.5 * (1.0 + rnd.uniform(-jitter_r, jitter_r))
        pts.append(Vector((math.cos(a) * r * sx, math.sin(a) * r * sy, z)))
    return pts


def build_basalt(bm, w, rnd):
    """Blockiger Basaltbrocken: konvexe Hülle aus Unter-/Ober-Ring + Gipfelpunkten. `blockig` hoch = flache Oberseite."""
    n, h = w["ecken"], w["dicke"]
    sx, sy = w["streckung"]
    pts = ring(n, rnd, 0.15, 0.4, sx, sy, 0.0)
    top_scale = 0.55 + 0.35 * w["blockig"]
    pts += [Vector((p.x * top_scale + rnd.uniform(-0.05, 0.05), p.y * top_scale + rnd.uniform(-0.05, 0.05),
                    h * (0.75 + 0.2 * w["blockig"]) + rnd.uniform(-0.06, 0.06))) for p in ring(n, rnd, 0.2, 0.5, sx, sy)]
    for _ in range(2):   # 1–2 Gipfelpunkte (Bruchkanten oben)
        pts.append(Vector((rnd.uniform(-0.15, 0.15) * sx, rnd.uniform(-0.15, 0.15) * sy, h * rnd.uniform(0.95, 1.05))))
    # mittlere Ausbuchtung (wirkt nicht wie ein Prisma)
    pts += [Vector((p.x * 1.08, p.y * 1.08, h * 0.4)) for p in ring(max(4, n - 2), rnd, 0.2, 0.5, sx, sy)]
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])


def build_platte(bm, w, rnd):
    """Steinplatte: unregelmäßiges n-Eck, Dicke, Fase an der Oberkante, gewölbte Oberseite (Mittelpunkt erhöht)."""
    n, d, f = w["ecken"], w["dicke"], w["kantenfase"]
    base = ring(n, rnd, 0.16, 0.45, 1.0, 0.85, 0.0)
    vb = [bm.verts.new(p) for p in base]
    vm = [bm.verts.new(Vector((p.x, p.y, d * 0.55))) for p in base]                       # Seitenwand
    vt = [bm.verts.new(Vector((p.x * (1 - f * 1.6), p.y * (1 - f * 1.6), d + rnd.uniform(-0.02, 0.02)))) for p in base]
    c = bm.verts.new(Vector((rnd.uniform(-0.06, 0.06), rnd.uniform(-0.06, 0.06), d + w["woelbung"])))
    bm.faces.new(list(reversed(vb)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([vb[i], vb[j], vm[j], vm[i]])
        bm.faces.new([vm[i], vm[j], vt[j], vt[i]])
        bm.faces.new([vt[i], vt[j], c])


def build_zacke(bm, w, rnd):
    """Felszacke: n-kantiger Sockel, Bruchkante auf halber Höhe (versetzter Ring), schräge Spitze."""
    n, s = w["kanten"], w["schlankheit"]
    base = ring(n, rnd, 0.12, 0.3, 1.0, 0.9, 0.0)
    vb = [bm.verts.new(Vector((p.x * s * 1.15, p.y * s * 1.15, 0.0))) for p in base]
    zm = 0.45 + rnd.uniform(-0.05, 0.05)
    br = w["bruchkante"]
    vm = []
    for p in base:
        k = 0.62 + rnd.uniform(-br, br) * 0.4
        vm.append(bm.verts.new(Vector((p.x * s * 1.15 * k + w["spitze_versatz"] * 0.4, p.y * s * 1.15 * k, zm + rnd.uniform(-br, br) * 0.12))))
    tip = bm.verts.new(Vector((w["spitze_versatz"], rnd.uniform(-0.04, 0.04), 1.0)))
    bm.faces.new(list(reversed(vb)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([vb[i], vb[j], vm[j], vm[i]])
        bm.faces.new([vm[i], vm[j], tip])


BUILDERS = {"basaltbrocken": build_basalt, "steinplatte": build_platte, "felszacke": build_zacke}


def normalize(bm):
    """Ursprung = Mitte der Unterseite, größte Ausdehnung = 1."""
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    cx, cy, z0 = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
    ext = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    for v in bm.verts:
        v.co = Vector(((v.co.x - cx) / ext, (v.co.y - cy) / ext, (v.co.z - z0) / ext))


def make_type(typ, formen):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    data = {"format": "baustein_bibliothek", "version": VERSION, "typ": typ,
            "koordinaten": "X vorn/Laenge, Y links/Breite, Z oben/Hoehe; Ursprung Mitte Unterseite; groesste Ausdehnung 1.0",
            "formen": {}}
    mat = bpy.data.materials.new(f"{typ}_mat")
    for name, w in formen.items():
        rnd = random.Random(w["seed"])
        bm = bmesh.new()
        BUILDERS[typ](bm, w, rnd)
        normalize(bm)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        # Box-Projektion als UV (Teile brauchen UVs für Tangenten/spätere Atlas-Kachel)
        uv = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            n = poly.normal
            ax = max(range(3), key=lambda k: abs(n[k]))
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                u, v = [(co.y, co.z), (co.x, co.z), (co.x, co.y)][ax]
                uv.data[li].uv = (u * 0.5 + 0.5, v * 0.5 + 0.5)
        for p in me.polygons:
            p.use_smooth = False
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        dims = [max(v.co[k] for v in me.vertices) - min(v.co[k] for v in me.vertices) for k in range(3)]
        data["formen"][name] = {
            "werte": w,
            "tris": len(me.polygons),
            "masse": [round(d, 3) for d in dims],
            "vertices": [[round(c, 5) for c in v.co] for v in me.vertices],
            "dreiecke": [list(p.vertices) for p in me.polygons],
        }
        print(f"[bausteine] {typ}/{name}: {len(me.polygons)} Tris, Maße {['%.2f' % d for d in dims]}")
    # nebeneinander aufstellen (nur für die FBX-Ansicht; die JSON-Meshes bleiben im Ursprung)
    for i, ob in enumerate(bpy.context.scene.collection.objects):
        ob.location.x = i * 1.5
    fbx = os.path.join(OUT, f"{typ}.fbx")
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, apply_unit_scale=True, bake_space_transform=False,
                             object_types={"MESH"}, mesh_smooth_type="FACE", add_leaf_bones=False)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, f"{typ}.glb"), export_format="GLB")
    for ob in bpy.context.scene.collection.objects:
        ob.location.x = 0.0
    with open(os.path.join(OUT, f"{typ}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return data


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = argv[argv.index("--typ") + 1] if "--typ" in argv else None
    for typ, formen in TYPEN.items():
        if only and typ != only:
            continue
        make_type(typ, formen)
    print("[bausteine] fertig")


main()
