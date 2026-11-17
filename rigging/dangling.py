"""Standard-Baustein „frei hängende Teile“: markiert Bereiche im Mesh, die in Unity per Shader frei schwingen – OHNE Knochen.

& "D:\\Blender\\blender.exe" -b <rig>/<skelett>_rigged.blend -P rigging/dangling.py -- <creature.toml> <rig-ordner> [render]

Wird von scripts/creature_pipeline.py direkt nach dem Rig aufgerufen – nur wenn die creature.toml einen Abschnitt
[dangling] hat. Speichert das Rig-Blend mit der Markierung neu, schreibt <rig-ordner>/dangling_report.json und (mit
"render") ein Prüfbild <rig-ordner>/dangling_preview.png (blau = starr, rot = schwingt frei).

Ergebnis im Mesh: Farb-Attribut "_DANGLING" (pro Vertex, linear)
  R = Gewicht 0 … 1   0 = starr (folgt nur dem Rig), 1 = schwingt voll; steigt vom Ansatz zur Spitze
  G = Phase 0 … 1     pro Teil (Lappen, Fühler) eine eigene, damit nicht alle im Gleichtakt schwingen
  B = 0 (frei für später), A = 1
FBX: als Vertex-Farbe (Unity: mesh.colors). GLB: als eigenes Attribut "_DANGLING" (nicht COLOR_0, sonst färben
glTF-Programme das Modell ein). Beides stellt rigging/export_unity.py ein.

Welche Vertices schwingen (alles in der Ruhepose):
  1. Bereich: [[dangling.region]] – Vertices, die hauptsächlich an einem der `bones` hängen (Rig-Gewichte, Namen mit *
     erlaubt), optional nur unterhalb (`below`) bzw. oberhalb (`above`) der Knochenlinie (Welt-Höhe, Anteil Größe).
  2. Dünn: Dicke (Strahl von der Oberfläche nach innen bis zur Gegenseite) < thin_max · Größe. Der Rumpf ist dick und
     schwingt deshalb nie mit, auch wenn er im Bereich liegt – nur Lappen, Fühler, Hautfahnen.
  3. Verlauf: Abstand über die Mesh-Kanten vom Ansatz (erster starrer Nachbar) → je Teil auf 0 … 1, hoch `exponent`,
     mal Reichweite: Teile kürzer als min_length bleiben starr (Zähne, Noppen, kurze Zacken), ab full_length voll.
     Am Ansatz ≈ 0 → nichts reißt ab.
Vertices an derselben Position (Tripo trennt an UV-Nähten) bekommen exakt dieselben Werte → keine Risse im Shader.
"""
import fnmatch
import heapq
import json
import math
import pathlib
import sys
import tomllib

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = pathlib.Path(__file__).resolve().parent
ATTR = "_DANGLING"


def load_cfg(toml_path):
    cfg = tomllib.loads((HERE / "dangling_defaults.toml").read_text(encoding="utf-8"))
    cfg.update(tomllib.loads(pathlib.Path(toml_path).read_text(encoding="utf-8")).get("dangling", {}))
    return cfg


def weld_ids(V):
    key = {}
    return np.array([key.setdefault(tuple(c), len(key)) for c in np.round(V, 5)]), len(key)


def thickness(obj, size):
    """Dicke je Vertex: kürzester Strahl nach innen (entlang −Vertex-Normale und −Normalen der angrenzenden Flächen)
    bis zur Gegenseite. An dünnen Spitzen liegt die Vertex-Normale fast tangential und verfehlt die Gegenseite –
    deshalb mehrere Richtungen. Ganz ohne Treffer = inf (wird danach aus den Nachbarn aufgefüllt)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.normal_update()
    bm.verts.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    th = np.full(len(bm.verts), np.inf)
    eps = 1e-4 * size
    for v in bm.verts:
        own = {f.index for f in v.link_faces}
        for n in [v.normal] + [f.normal for f in v.link_faces]:
            if n.length < 1e-9:
                continue
            hit = tree.ray_cast(v.co - n * eps, -n, 2 * size)
            if hit[0] is not None and hit[2] not in own and hit[3] < th[v.index]:
                th[v.index] = hit[3]
    bm.free()
    return th


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    cfg = load_cfg(a[0])
    out = pathlib.Path(a[1]).resolve()
    render = len(a) > 2 and a[2] == "render"
    regions = cfg.get("region", [])
    if not regions:
        raise SystemExit("[dangling] ohne [[dangling.region]] – nichts zu markieren")

    obj = bpy.data.objects["Body_Mesh"]
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    me = obj.data
    mw = obj.matrix_world
    V = np.array([(mw @ v.co)[:] for v in me.vertices])
    N = len(V)
    size = float((V.max(0) - V.min(0)).max())
    wid, NW = weld_ids(V)
    # Kanten-Graph über Positionen
    VW = np.zeros((NW, 3))
    VW[wid] = V
    adj = [[] for _ in range(NW)]
    for e in me.edges:
        p, q = wid[e.vertices[0]], wid[e.vertices[1]]
        if p != q:
            l = float(np.linalg.norm(VW[p] - VW[q]))
            adj[p].append((q, l))
            adj[q].append((p, l))

    # Hauptknochen je Vertex (stärkste Rig-Gewichtung)
    gname = {g.index: g.name for g in obj.vertex_groups}
    main_bone = []
    for v in me.vertices:
        gs = [(g.weight, gname[g.group]) for g in v.groups if g.group in gname]
        main_bone.append(max(gs)[1] if gs else "")
    bones = {b.name: (np.array((arm.matrix_world @ b.head_local)[:]), np.array((arm.matrix_world @ b.tail_local)[:]))
             for b in arm.data.bones}

    def line_height(i, bname):
        """Höhe des Vertex über der Knochenlinie (am nächsten Punkt der Knochenstrecke)."""
        h, t = bones[bname]
        ab = t - h
        s = np.clip((V[i] - h) @ ab / max(1e-12, ab @ ab), 0, 1)
        return V[i, 2] - (h + s * ab)[2]

    th = thickness(obj, size)
    # Dicke je Position mitteln (Kopien an UV-Nähten haben verschiedene Normalen)
    thw = np.full(NW, np.inf)
    fin = np.isfinite(th)
    acc, cnt = np.zeros(NW), np.zeros(NW)
    np.add.at(acc, wid[fin], th[fin])
    np.add.at(cnt, wid[fin], 1)
    thw[cnt > 0] = acc[cnt > 0] / cnt[cnt > 0]
    for _ in range(8):                              # Positionen ohne Treffer: Mittel der Nachbarn
        miss = np.where(~np.isfinite(thw))[0]
        if not len(miss):
            break
        fill = thw.copy()
        for p in miss:
            nb = [thw[q] for q, _ in adj[p] if np.isfinite(thw[q])]
            if nb:
                fill[p] = float(np.mean(nb))
        thw = fill

    def close_thin(thin):
        """Einzelne „dicke“ Ausreißer mitten in dünnen Teilen schließen (Strahl lief z. B. längs durch den Fühler):
        Position mit ≥ 60 % dünnen Nachbarn gilt als dünn. Sonst zerfiele ein Fühler in kurze Stücke."""
        for _ in range(3):
            frac = np.array([np.mean([thin[q] for q, _ in adj[p]]) if adj[p] else 0.0 for p in range(NW)])
            thin = thin | (frac >= 0.6)
        return thin

    in_region = np.zeros(NW, bool)
    region_counts = []
    for r in regions:
        pats = r.get("bones", ["*"])
        thin = close_thin(thw < r.get("thin_max", cfg["thin_max"]) * size)
        ok = np.zeros(NW, bool)
        for i in range(N):
            b = main_bone[i]
            if not b or not any(fnmatch.fnmatchcase(b, p) for p in pats):
                continue
            if "below" in r or "above" in r:
                hgt = line_height(i, b)
                if "below" in r and hgt > r["below"] * size:
                    continue
                if "above" in r and hgt < r["above"] * size:
                    continue
            ok[wid[i]] = True
        hit = ok & thin
        region_counts.append(int(hit.sum()))
        in_region |= hit
    D = in_region                                   # je Position: schwingt

    # Abstand vom Ansatz (Dijkstra, Start = starre Positionen direkt neben schwingenden)
    dist = np.full(NW, np.inf)
    heap = []
    for p in np.where(~D)[0]:
        if any(D[q] for q, _ in adj[p]):
            dist[p] = 0.0
            heap.append((0.0, int(p)))
    # Teile ganz ohne starren Nachbarn (lose Inseln): Startwert = Luftlinie zum nächsten starren Punkt
    rigid_pts = VW[~D]
    heapq.heapify(heap)
    comp = np.full(NW, -1)
    ncomp = 0
    for s in np.where(D)[0]:
        if comp[s] >= 0:
            continue
        stack, members = [s], []
        comp[s] = ncomp
        while stack:
            p = stack.pop()
            members.append(p)
            for q, _ in adj[p]:
                if D[q] and comp[q] < 0:
                    comp[q] = ncomp
                    stack.append(q)
        attached = any(not D[q] for p in members for q, _ in adj[p])
        if not attached and len(rigid_pts):
            for p in members:
                d0 = float(np.min(np.linalg.norm(rigid_pts - VW[p], axis=1)))
                heapq.heappush(heap, (d0, int(p)))
                dist[p] = min(dist[p], d0)
        ncomp += 1
    while heap:
        d, p = heapq.heappop(heap)
        if d > dist[p]:
            continue
        for q, l in adj[p]:
            if D[q] and d + l < dist[q]:
                dist[q] = d + l
                heapq.heappush(heap, (d + l, q))

    # Gewicht + Phase je Teil
    wW = np.zeros(NW)
    phW = np.zeros(NW)
    parts = []
    for k in range(ncomp):
        m = comp == k
        dk = np.where(np.isfinite(dist[m]), dist[m], 0.0)
        dmax = float(dk.max()) if len(dk) else 0.0
        if dmax <= 1e-9:
            continue
        lo, hi = cfg["min_length"] * size, cfg["full_length"] * size
        reach = float(np.clip((dmax - lo) / max(1e-9, hi - lo), 0.0, 1.0))
        if reach <= 0.0:
            continue
        wW[m] = (dk / dmax) ** cfg["exponent"] * reach
        c = VW[m].mean(0)
        phW[m] = math.modf(abs(math.sin(float(c @ np.array([12.9898, 78.233, 37.719])) * 1000.0)) * 43758.5453)[0]
        parts.append({"verts": int(m.sum()), "length_m": round(dmax, 4), "reach": round(reach, 2),
                      "center": [round(float(x), 3) for x in c]})

    w, ph = wW[wid], phW[wid]
    old = me.color_attributes.get(ATTR)
    if old:
        me.color_attributes.remove(old)
    at = me.color_attributes.new(ATTR, "FLOAT_COLOR", "POINT")
    at.data.foreach_set("color", np.column_stack([w, ph, np.zeros(N), np.ones(N)]).astype(np.float32).ravel())
    me.color_attributes.active_color = at
    me.update()

    parts.sort(key=lambda p: -p["length_m"])
    report = {"size_m": round(size, 3), "vertices": N, "dangling_vertices": int((w > 1e-3).sum()),
              "full_vertices": int((w > 0.9).sum()), "parts": len(parts), "region_positions": region_counts,
              "thin_max_m": round(cfg["thin_max"] * size, 4), "longest_parts": parts[:12],
              "no_thickness_hit": int((~np.isfinite(th)).sum()),
              "no_thickness_after_fill": int((~np.isfinite(thw)).sum())}
    (out / "dangling_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    bpy.ops.wm.save_mainfile()
    print("RIG_DANGLING", json.dumps({k: v for k, v in report.items() if k != "longest_parts"}, ensure_ascii=False))
    if render:
        preview(obj, V, w, size, out / "dangling_preview.png")


def preview(obj, V, w, size, path):
    """Prüfbild: Ausschnitt um die markierten Teile aus 3 Richtungen, Farbe = Gewicht (blau starr → rot frei)."""
    sc = bpy.context.scene
    me = obj.data
    mat = bpy.data.materials.new("DanglePreview")
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = ATTR
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.05, 0.25, 0.8, 1)
    ramp.color_ramp.elements[1].color = (1.0, 0.08, 0.05, 1)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs[0])
    nt.links.new(sep.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bsdf.inputs["Base Color"])
    saved = [s.material for s in obj.material_slots]
    for s in obj.material_slots:
        s.material = mat
    if not obj.material_slots:
        me.materials.append(mat)
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = sc.render.resolution_y = 480
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("DanglePreviewWorld")
    sc.world = world
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.25, 0.25, 0.27, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    sun = bpy.data.objects.new("DanglePreviewSun", bpy.data.lights.new("DanglePreviewSun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (0.5, 0.3, 0.6)
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("DanglePreviewCam", bpy.data.cameras.new("DanglePreviewCam"))
    cam.data.type = "ORTHO"
    sc.collection.objects.link(cam)
    sc.camera = cam
    sel = w > 1e-3
    pts = V[sel] if sel.any() else V
    lo, hi = pts.min(0), pts.max(0)
    ctr = Vector(((lo + hi) / 2).tolist())
    cam.data.ortho_scale = max(float((hi - lo).max()) * 1.5, 0.15 * size)
    tiles = []
    views = {"seite": (0, -1, 0.05), "unten-vorn": (0.6, -0.4, -0.7), "arpg": (0.5, -0.8, 1.0)}
    for name, d in views.items():
        d = Vector(d).normalized()
        cam.location = ctr + d * 3 * size
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        cam.data.clip_end = 10 * size
        f = path.with_name(f"_dangle_{name}.png")
        sc.render.filepath = str(f)
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(str(f))
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        tiles.append(px)
        bpy.data.images.remove(img)
        f.unlink()
    sheet = np.concatenate(tiles, axis=1)
    out = bpy.data.images.new("dangle_sheet", sheet.shape[1], sheet.shape[0], alpha=True)
    out.pixels.foreach_set(sheet.ravel())
    out.filepath_raw = str(path)
    out.file_format = "PNG"
    out.save()
    for s, m in zip(obj.material_slots, saved):
        s.material = m
    print("DANGLING_PREVIEW", path)


if __name__ == "__main__":
    main()
