"""Einseitige Flächen (z. B. Tripo-Insektenflügel = dünne offene Platten) doppelseitig machen.

Problem: Tripo baut Flügel als EINE Lage Dreiecke ohne Rückseite. Jede Engine zeichnet Standard-Materialien nur von
vorn (Backface Culling) → von der Rückseite aus ist der Flügel unsichtbar, sein Schatten aber da.
Lösung (engine-unabhängig, 1 Material, Standard-Shader): die betroffenen Flächen mit umgedrehter Richtung kopieren.

Erkennung (ohne Namen/Knochen, nur Geometrie): von jeder Fläche einen Strahl nach HINTEN schießen.
  - geschlossener Körper: der Strahl trifft die Innenseite des Körpers (Treffer-Normale zeigt vom Strahl weg)
  - einseitige Platte: der Strahl trifft nichts oder etwas von außen → Rückseite liegt frei
Treffer werden über gemeinsame Kanten (UV-Naht-Duplikate zusammengefasst) zu Bereichen verbunden; Bereiche unter
`min_area` (Anteil Größe²) bleiben unverändert (Splitter in Körperfalten).

Kopie: neue Vertices mit denselben Gewichten + UVs (bmesh kopiert alle Vertex-/Ecken-Daten), Richtung umgedreht,
um `offset` (Anteil Größe) nach hinten versetzt – sonst flimmern Vorder- und Rückseite in Programmen ohne Culling
(Blender-Vorschau, glTF-Viewer). Alle Kopien an derselben Position bekommen denselben Versatz (keine Risse an UV-Nähten).

  report = double_sided.apply(obj, size, cfg)      # nach dem Gewichten, vor dem Speichern
"""
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def detect(bm, size):
    """→ bool-Array je Fläche: Rückseite liegt frei."""
    tree = BVHTree.FromBMesh(bm)
    eps = 1e-4 * size
    out = np.zeros(len(bm.faces), bool)
    for f in bm.faces:
        n = f.normal
        if n.length < 1e-9:
            continue
        hit = tree.ray_cast(f.calc_center_median() - n * eps, -n, 2 * size)
        out[f.index] = hit[0] is None or hit[1].dot(-n) < 0
    return out


def apply(obj, size, cfg):
    min_area = cfg.get("min_area", 0.002) * size * size
    offset = cfg.get("offset", 0.001) * size
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    open_back = detect(bm, size)

    # Bereiche: offene Flächen über gemeinsame (geschweißte) Kanten verbinden
    key = {}
    wid = np.array([key.setdefault(tuple(np.round(v.co[:], 5)), len(key)) for v in bm.verts])
    edge_faces = {}
    for f in bm.faces:
        if open_back[f.index]:
            for e in f.edges:
                k = tuple(sorted((wid[e.verts[0].index], wid[e.verts[1].index])))
                edge_faces.setdefault(k, []).append(f.index)
    parent = {i: i for i in np.where(open_back)[0]}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for fs in edge_faces.values():
        for x in fs[1:]:
            parent[find(x)] = find(fs[0])
    regions = {}
    for i in parent:
        regions.setdefault(find(i), []).append(i)
    keep, areas = [], []
    for fs in regions.values():
        area = sum(bm.faces[i].calc_area() for i in fs)
        if area >= min_area:
            keep += fs
            areas.append(area)
    faces = [bm.faces[i] for i in sorted(keep)]

    if faces:
        # gemeinsamer Versatz je Position: gemittelte Normale der betroffenen Flächen
        acc = {}
        for f in faces:
            for v in f.verts:
                acc[wid[v.index]] = acc.get(wid[v.index], Vector()) + f.normal * f.calc_area()
        ret = bmesh.ops.duplicate(bm, geom=faces)
        new_faces = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
        bmesh.ops.reverse_faces(bm, faces=new_faces, flip_multires=False)
        new_verts = {g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)}
        for old, new in ret["vert_map"].items():
            if old not in new_verts:
                n = acc[wid[old.index]]
                if n.length > 1e-12:
                    new.co = old.co - n.normalized() * offset
        bm.to_mesh(obj.data)
        obj.data.update()
    bm.free()
    report = {"faces_checked": int(len(open_back)), "open_back_faces": int(open_back.sum()),
              "regions": len(areas), "region_areas_m2": sorted((round(a, 4) for a in areas), reverse=True),
              "faces_added": len(faces), "verts_total": len(obj.data.vertices), "faces_total": len(obj.data.polygons)}
    print("RIG_DOUBLE_SIDED", report)
    return report
