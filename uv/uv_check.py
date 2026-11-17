"""UV-Prüfung direkt nach Tripo: Tripo-UV vs. Blender Smart UV messen, bessere wählen, Sichtprüfung rendern.

& "D:\\Blender\\blender.exe" -b --factory-startup -P uv/uv_check.py -- <generate_model.glb> <ausgabeordner> [<creature.toml>]
Ergebnis: <ausgabe>/model_uv.glb (Eingabe für das Rig), uv_report.json, uv_preview.png, uv_layouts.png
"""
import json
import math
import pathlib
import sys
import tomllib

import bmesh
import bpy
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CFG = tomllib.loads((HERE / "uv_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    over = tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("uv", {})
    for k, v in over.items():
        CFG[k] = {**CFG[k], **v} if isinstance(v, dict) and isinstance(CFG.get(k), dict) else v
TEX = HERE / "textures"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SRC))
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in bpy.data.objects:
    o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
obj = bpy.context.active_object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = obj.data
TRIPO_UV = me.uv_layers.active.name


# ------------------------------------------------------------------ Messung
def measure(uv_name):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    uvl = bm.loops.layers.uv[uv_name]
    P, U = [], []
    for f in bm.faces:
        P.append([l.vert.co.copy() for l in f.loops])
        U.append([l[uvl].uv.copy() for l in f.loops])
    # UV-Inseln: Flächen verbunden, wenn sie eine Kante mit identischen UVs teilen
    bm.faces.ensure_lookup_table()
    parent = list(range(len(bm.faces)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        f1, f2 = e.link_faces
        def uvs(f):
            return {l.vert.index: tuple(round(c, 5) for c in l[uvl].uv) for l in f.loops if l.vert in e.verts}
        if uvs(f1) == uvs(f2):
            parent[find(f1.index)] = find(f2.index)
    islands = len({find(i) for i in range(len(bm.faces))})
    bm.free()
    P = np.array([[list(v) for v in t] for t in P], np.float64)
    U = np.array([[list(v) for v in t] for t in U], np.float64)
    a3 = 0.5 * np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1)
    e1, e2 = U[:, 1] - U[:, 0], U[:, 2] - U[:, 0]
    signed = 0.5 * (e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0])
    a2 = np.abs(signed)
    ok = (a3 > 1e-12) & (a2 > 1e-14)
    dens = np.sqrt(a2[ok] / a3[ok])
    w = a3[ok] / a3[ok].sum()
    med = float(np.median(np.repeat(dens, np.maximum(1, (w * 5000).astype(int)))))
    rel = dens / med
    outlier = float(w[(rel < 0.5) | (rel > 2.0)].sum())
    cv = float(np.sqrt(np.sum(w * (rel - np.sum(w * rel)) ** 2)))

    def angles(T):
        A = []
        for i in range(3):
            v1, v2 = T[:, (i + 1) % 3] - T[:, i], T[:, (i + 2) % 3] - T[:, i]
            c = np.sum(v1 * v2, 1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1) + 1e-12)
            A.append(np.degrees(np.arccos(np.clip(c, -1, 1))))
        return np.stack(A, 1)
    ang = float(np.sum(w * np.abs(angles(P[ok]) - angles(U[ok])).mean(1)))
    # Abdeckung/Überlappung per Rasterung
    R = CFG["raster"]
    cnt = np.zeros((R, R), np.uint8)
    oob = 0.0
    for t in U[ok]:
        if t.min() < 0 or t.max() > 1:
            oob += 1
        px = t * R
        x0, y0 = np.floor(px.min(0)).astype(int)
        x1, y1 = np.ceil(px.max(0)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, R), min(y1, R)
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1] + 0.5
        (ax, ay), (bx, by), (cx, cy) = px
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-12:
            continue
        l1 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / d
        l2 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / d
        inside = (l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0)
        cnt[y0:y1, x0:x1] += inside.astype(np.uint8)
    covered = (cnt >= 1).sum()
    m = {
        "uv_map": uv_name, "islands": islands,
        "coverage": round(float(covered / R / R), 3),
        "overlap": round(float((cnt >= 2).sum() / max(1, covered)), 4),
        "density_outlier_fraction": round(outlier, 3),
        "density_cv": round(cv, 3),
        "angle_distortion_deg": round(ang, 2),
        "mirrored_fraction": round(float(w[signed[ok] < 0].sum()), 3),
        "out_of_bounds_tris": int(oob),
    }
    L = CFG["limits"]
    m["checks"] = {
        "overlap": m["overlap"] <= L["overlap_max"],
        "density": m["density_outlier_fraction"] <= L["density_outlier_max"],
        "angles": m["angle_distortion_deg"] <= L["angle_distortion_max_deg"],
        "coverage": m["coverage"] >= L["coverage_min"],
    }
    # Fehlerwert (kleiner = besser)
    m["error_score"] = round(4 * m["overlap"] + 2 * m["density_outlier_fraction"] + m["density_cv"]
                             + m["angle_distortion_deg"] / 20 + max(0, 0.7 - m["coverage"]), 4)
    return m, cnt


def smart_uv():
    uv = me.uv_layers.new(name="UVSmart")
    me.uv_layers.active = uv
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    s = CFG["smart_uv"]
    bpy.ops.uv.smart_project(angle_limit=math.radians(s["angle_limit_deg"]), island_margin=s["island_margin"],
                             area_weight=s["area_weight"], correct_aspect=True, scale_to_bounds=False)
    # dicht packen (Smart UV allein lässt viel UV-Raum leer → verschenkte Texturauflösung)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(rotate=True, margin=s["pack_margin"])
    bpy.ops.object.mode_set(mode="OBJECT")
    me.uv_layers.active = me.uv_layers[TRIPO_UV]
    return "UVSmart"


tripo_m, tripo_cnt = measure(TRIPO_UV)
smart_name = smart_uv()
smart_m, smart_cnt = measure(smart_name)
mode = CFG["mode"]
use_smart = mode == "smart" or (mode == "auto" and smart_m["error_score"] < CFG["switch_ratio"] * tripo_m["error_score"])
print("UV_TRIPO", json.dumps(tripo_m, ensure_ascii=False))
print("UV_SMART", json.dumps(smart_m, ensure_ascii=False))


# ------------------------------------------------------------------ Inspektion: Inseln, Nähte, Dichte pro Körperteil
from mathutils import Vector  # noqa: E402

SIZE = max(obj.dimensions)
orig_mat = obj.active_material
orig_smooth = [p.use_smooth for p in me.polygons]


def _uf(n):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a_, b_):
        parent[find(a_)] = find(b_)
    return find, union


def geometry_parts():
    """Körperteile = zusammenhängende Geometrie (Vertices per Position verschweißt)."""
    key = {}
    for v in me.vertices:
        key.setdefault(tuple(round(c, 5) for c in v.co), []).append(v.index)
    find, union = _uf(len(me.vertices))
    for vs in key.values():
        for x in vs[1:]:
            union(vs[0], x)
    for e in me.edges:
        union(e.vertices[0], e.vertices[1])
    roots = {}
    return [roots.setdefault(find(p.vertices[0]), len(roots)) for p in me.polygons]


def uv_islands(uv_name):
    """Pro Polygon die UV-Insel-Nummer + Liste der Insel-Randkanten (Nähte) als Weltkoordinaten-Paare."""
    uv = me.uv_layers[uv_name].uv
    pos = lambda vi: tuple(round(c, 5) for c in me.vertices[vi].co)  # noqa: E731
    edges = {}                                      # verschweißte Kante → [(poly, uv_a, uv_b)]
    for p in me.polygons:
        n = p.loop_total
        for i in range(n):
            la, lb = p.loop_start + i, p.loop_start + (i + 1) % n
            va, vb = me.loops[la].vertex_index, me.loops[lb].vertex_index
            ka, kb = pos(va), pos(vb)
            ua = tuple(round(c, 5) for c in uv[la].vector)
            ub = tuple(round(c, 5) for c in uv[lb].vector)
            k = (ka, kb) if ka < kb else (kb, ka)
            edges.setdefault(k, []).append((p.index, ua if ka < kb else ub, ub if ka < kb else ua))
    find, union = _uf(len(me.polygons))
    for lst in edges.values():
        if len(lst) == 2 and lst[0][1:] == lst[1][1:]:
            union(lst[0][0], lst[1][0])
    ids, isl = {}, []
    for p in me.polygons:
        isl.append(ids.setdefault(find(p.index), len(ids)))
    seams = []
    for k, lst in edges.items():
        if len(lst) == 2 and isl[lst[0][0]] == isl[lst[1][0]]:
            continue                                # innerhalb einer Insel
        nz = sum(me.polygons[e[0]].normal.z for e in lst) / len(lst)
        seams.append((Vector(k[0]), Vector(k[1]), nz))
    return isl, len(ids), seams


def poly_density(uv_name):
    uv = me.uv_layers[uv_name].uv
    d, A = [], []
    for p in me.polygons:
        ls = list(range(p.loop_start, p.loop_start + p.loop_total))
        a2 = 0.0
        for i in range(1, len(ls) - 1):
            u0, u1, u2 = uv[ls[0]].vector, uv[ls[i]].vector, uv[ls[i + 1]].vector
            a2 += abs((u1.x - u0.x) * (u2.y - u0.y) - (u1.y - u0.y) * (u2.x - u0.x)) / 2
        A.append(p.area)
        d.append(math.sqrt(a2 / p.area) if p.area > 1e-12 else 0.0)
    d, A = np.array(d), np.array(A)
    med = float(np.median(np.repeat(d, np.maximum(1, (A / A.sum() * 5000).astype(int)))))
    return d / max(med, 1e-9), A


def island_colors(n):
    import colorsys
    return [colorsys.hsv_to_rgb((i * 0.618034) % 1.0, 0.7 + 0.3 * ((i * 7) % 3) / 2, 0.75 + 0.25 * ((i * 5) % 2)) for i in range(n)]


def heat(r):
    """Dichte relativ zum Median → Farbe: blau = gröber (unscharf), grün = gleichmäßig, rot = feiner."""
    x = max(-1.0, min(1.0, math.log2(max(r, 1e-3))))      # ×0,5 … ×2
    if x < 0:
        t = -x
        return (0.15 * (1 - t) + 0.1 * t, 0.75 * (1 - t) + 0.25 * t, 0.25 * (1 - t) + 1.0 * t)
    return (0.15 * (1 - x) + 1.0 * x, 0.75 * (1 - x) + 0.2 * x, 0.25 * (1 - x) + 0.1 * x)


def set_face_colors(name, cols):
    attr = me.color_attributes.get(name) or me.color_attributes.new(name, "FLOAT_COLOR", "CORNER")
    for p in me.polygons:
        c = (*cols[p.index], 1.0)
        for li in range(p.loop_start, p.loop_start + p.loop_total):
            attr.data[li].color = c


def attr_material(name):
    m = bpy.data.materials.new(f"insp_{name}")
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = name
    nt.links.new(at.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(at.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.6
    return m


def seam_object(seams, name):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = SIZE * CFG["inspect"]["seam_width"]
    cu.bevel_resolution = 0
    for a_, b_, _ in seams:
        sp = cu.splines.new("POLY")
        sp.points.add(1)
        sp.points[0].co = (*a_, 1)
        sp.points[1].co = (*b_, 1)
    ob = bpy.data.objects.new(name, cu)
    mt = bpy.data.materials.new(name)
    mt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0.95, 0.2, 1)
    mt.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1, 0.95, 0.2, 1)
    mt.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.5
    cu.materials.append(mt)
    return ob


def layout_islands_png(uv_name, isl, cols, path, tex_img=None):
    """2D-UV-Layout: jede Insel in ihrer Modell-Farbe, Inselränder weiß, Textur (falls passend) darunter."""
    R = CFG["inspect"]["layout_resolution"]
    ids = np.full((R, R), -1, np.int32)
    uv = me.uv_layers[uv_name].uv
    for p in me.polygons:
        ls = list(range(p.loop_start, p.loop_start + p.loop_total))
        for i in range(1, len(ls) - 1):
            px = np.array([list(uv[ls[j]].vector) for j in (0, i, i + 1)]) * R
            x0, y0 = np.maximum(np.floor(px.min(0)).astype(int), 0)
            x1, y1 = np.minimum(np.ceil(px.max(0)).astype(int), R)
            if x1 <= x0 or y1 <= y0:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1] + 0.5
            (ax, ay), (bx, by), (cx, cy) = px
            d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(d) < 1e-12:
                continue
            l1 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / d
            l2 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / d
            ins = (l1 >= -1e-3) & (l2 >= -1e-3) & (1 - l1 - l2 >= -1e-3)
            ids[y0:y1, x0:x1][ins] = isl[p.index]
    C = np.array(cols + [(0, 0, 0)], np.float32)
    rgb = C[ids]                                     # -1 → letzte Zeile (schwarz)
    if tex_img is not None:
        w, h = tex_img.size
        tp = np.array(tex_img.pixels[:], np.float32).reshape(h, w, 4)[..., :3]
        yi = (np.arange(R) * h // R)[:, None]
        xi = (np.arange(R) * w // R)[None, :]
        tex = tp[yi, xi]
        rgb = np.where((ids >= 0)[..., None], tex * 0.6 + rgb * 0.4, tex * 0.25)
    edge = np.zeros((R, R), bool)
    edge[:, :-1] |= ids[:, :-1] != ids[:, 1:]
    edge[:-1, :] |= ids[:-1, :] != ids[1:, :]
    rgb[edge] = 1.0
    img = bpy.data.images.new("lay_" + uv_name, R, R)
    img.pixels = np.concatenate([rgb, np.ones((R, R, 1), np.float32)], 2).ravel()
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()


# Render-Bühne
sc = bpy.context.scene
wd = bpy.data.worlds.new("w")
sc.world = wd
wd.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.31, 0.33, 1)
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (0.6, 0.2, 0.6)
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
cam.data.type = "ORTHO"
sc.collection.objects.link(cam)
sc.camera = cam
CENTER = sum((obj.matrix_world @ Vector(b) for b in obj.bound_box), Vector()) / 8
# Kopf = vorderstes Stück entlang der längsten Waagerechten (+X wie im Rig)
xs = np.array([v.co.x for v in me.vertices])
head_pts = [v.co for v in me.vertices if v.co.x > xs.max() - CFG["inspect"]["head_fraction"] * (xs.max() - xs.min())]
HEAD = sum(head_pts, Vector()) / len(head_pts)


def shoot(path, az, el, target=None, scale=1.25):
    az, el = math.radians(az), math.radians(el)
    sc.render.engine = "BLENDER_EEVEE"
    sc.view_settings.view_transform = "Standard" if pathlib.Path(path).name.startswith("insp_") else "AgX"
    sc.render.resolution_x = sc.render.resolution_y = CFG["preview"]["resolution"]
    t = target if target is not None else CENTER
    cam.data.ortho_scale = SIZE * scale
    cam.location = t + Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))) * 6
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def with_material(mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def inspect(uv_name, tag, tex_img):
    parts = geometry_parts()
    isl, n_isl, seams = uv_islands(uv_name)
    dens, A = poly_density(uv_name)
    cols = island_colors(n_isl)
    set_face_colors(f"isl_{tag}", [cols[i] for i in isl])
    set_face_colors(f"dens_{tag}", [heat(r) for r in dens])
    # Kennzahlen pro Körperteil
    n_parts = max(parts) + 1
    per_part_isl = [set() for _ in range(n_parts)]
    part_area, part_dw = np.zeros(n_parts), np.zeros(n_parts)
    for pi, (pt, il) in enumerate(zip(parts, isl)):
        per_part_isl[pt].add(il)
        part_area[pt] += A[pi]
        part_dw[pt] += A[pi] * dens[pi]
    part_d = part_dw / np.maximum(part_area, 1e-12)
    splits = np.array([len(s) for s in per_part_isl])
    big = part_area >= np.percentile(part_area, 50)          # große Teile: dort sieht man Nähte
    seam_len = sum((b_ - a_).length for a_, b_, _ in seams)
    top_len = sum((b_ - a_).length for a_, b_, nz in seams if nz > 0.3)
    head_parts = {parts[p.index] for p in me.polygons if (p.center - HEAD).length < 0.12 * SIZE}
    m = {
        "parts": int(n_parts), "uv_islands": n_isl,
        "parts_in_one_island": round(float((splits == 1).mean()), 3),
        "parts_split_max": int(splits.max()),
        "big_parts_split_mean": round(float(splits[big].mean()), 2),
        "seam_length_per_size": round(seam_len / SIZE, 2),
        "seams_on_top_fraction": round(top_len / max(seam_len, 1e-9), 3),
        "part_density_min_max": [round(float(part_d.min()), 2), round(float(part_d.max()), 2)],
        "parts_density_outside_0.6_1.6": int(((part_d < 0.6) | (part_d > 1.6)).sum()),
        "head_density": round(float(sum(part_dw[i] for i in head_parts) / max(1e-12, sum(part_area[i] for i in head_parts))), 2),
    }
    print(f"UV_INSPECT_{tag.upper()}", json.dumps(m, ensure_ascii=False))
    # Bilder
    for p in me.polygons:
        p.use_smooth = False
    seam_ob = seam_object(seams, f"seams_{tag}")
    files = {}
    with_material(attr_material(f"isl_{tag}"))
    for v, az, el in (("arpg", -55, 50), ("side", -90, 8)):
        files[f"islands_{v}"] = OUT / f"insp_{tag}_islands_{v}.png"
        shoot(files[f"islands_{v}"], az, el)
    sc.collection.objects.link(seam_ob)
    files["islands_head"] = OUT / f"insp_{tag}_islands_head.png"
    shoot(files["islands_head"], *CFG["inspect"]["head_view"], HEAD, CFG["inspect"]["head_zoom"])
    with_material(orig_mat if tex_img is not None else test_material(TEX / "uv_checker.png", 1, "chk", uv_name))
    files["seams_arpg"] = OUT / f"insp_{tag}_seams_arpg.png"
    shoot(files["seams_arpg"], -55, 50)
    files["seams_head"] = OUT / f"insp_{tag}_seams_head.png"
    shoot(files["seams_head"], *CFG["inspect"]["head_view"], HEAD, CFG["inspect"]["head_zoom"])
    sc.collection.objects.unlink(seam_ob)
    with_material(attr_material(f"dens_{tag}"))
    files["density_arpg"] = OUT / f"insp_{tag}_density_arpg.png"
    shoot(files["density_arpg"], -55, 50)
    files["layout"] = OUT / f"insp_{tag}_layout.png"
    layout_islands_png(uv_name, isl, cols, files["layout"], tex_img)
    with_material(orig_mat)
    for p, s in zip(me.polygons, orig_smooth):
        p.use_smooth = s
    return m, {k: v.name for k, v in files.items()}


def test_material(img_path, repeat, name, uv_name=None):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.8
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path))
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = uv_name or final_uv
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (repeat, repeat, 1)
    nt.links.new(uvn.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return m


# ------------------------------------------------------------------ Textur-Übertragung auf neue UV
def principled_images(mat):
    """Bildknoten, die an Base Color / Normal / Metallic+Roughness hängen."""
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    found = {}

    def upstream_image(sock):
        stack = [l.from_node for l in sock.links]
        while stack:
            n = stack.pop()
            if n.type == "TEX_IMAGE":
                return n
            for i in n.inputs:
                stack += [l.from_node for l in i.links]
        return None
    for key, sock in (("color", "Base Color"), ("normal", "Normal"), ("orm", "Roughness")):
        n = upstream_image(bsdf.inputs[sock])
        if n:
            found[key] = n
    return bsdf, found


def rebake_to(uv_target):
    """Überträgt Tripos Texturen (auf Tripo-UV) per Cycles-Bake auf die neue UV."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 1
    sc.cycles.device = "CPU"
    mat = obj.active_material
    nt = mat.node_tree
    bsdf, imgs = principled_images(mat)
    # Quell-Texturen explizit an die Tripo-UV binden
    uvnode = nt.nodes.new("ShaderNodeUVMap")
    uvnode.uv_map = TRIPO_UV
    for n in imgs.values():
        nt.links.new(uvnode.outputs["UV"], n.inputs["Vector"])
    S = CFG["bake_size"]
    me.uv_layers.active = me.uv_layers[uv_target]
    for o in bpy.data.objects:
        o.select_set(o is obj)
    bpy.context.view_layer.objects.active = obj
    out_imgs = {}
    emit = nt.nodes.new("ShaderNodeEmission")
    mout = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    orig_surface = mout.inputs["Surface"].links[0].from_socket
    for key in ("color", "orm"):
        if key not in imgs:
            continue
        tgt = bpy.data.images.new(f"{key}_smartuv", S, S, alpha=False, float_buffer=False)
        if key != "color":
            tgt.colorspace_settings.name = "Non-Color"
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = tgt
        nt.nodes.active = tn
        nt.links.new(imgs[key].outputs["Color"], emit.inputs["Color"])
        nt.links.new(emit.outputs["Emission"], mout.inputs["Surface"])
        bpy.ops.object.bake(type="EMIT", margin=8, use_clear=True)
        out_imgs[key] = tgt
        nt.nodes.remove(tn)
    nt.links.new(orig_surface, mout.inputs["Surface"])
    nt.nodes.remove(emit)
    if "normal" in imgs:
        # Tangentenraum hängt an der UV → Normal Map per "selected to active" von einer Kopie mit alter UV
        src = obj.copy()
        src.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(src)
        src.data.uv_layers.active = src.data.uv_layers[TRIPO_UV]
        tgt = bpy.data.images.new("normal_smartuv", S, S, alpha=False, float_buffer=False)
        tgt.colorspace_settings.name = "Non-Color"
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = tgt
        nt.nodes.active = tn
        src.select_set(True)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.bake(type="NORMAL", use_selected_to_active=True, cage_extrusion=0.01,
                            max_ray_distance=0.05, margin=8, use_clear=True)
        out_imgs["normal"] = tgt
        nt.nodes.remove(tn)
        bpy.data.objects.remove(src)
    # Material auf neue Bilder + neue UV umstellen
    uvnode.uv_map = uv_target
    for key, n in imgs.items():
        if key in out_imgs:
            n.image = out_imgs[key]
            out_imgs[key].pack()
    # nur noch die neue UV behalten, unter Standardnamen
    me.uv_layers.remove(me.uv_layers[TRIPO_UV])
    me.uv_layers[uv_target].name = "UVMap"
    uvnode.uv_map = "UVMap"
    return list(out_imgs)


_tex_color = principled_images(orig_mat)[1].get("color")
insp = {}
insp["tripo"] = inspect(TRIPO_UV, "tripo", _tex_color.image if _tex_color else None)
insp["smart"] = inspect(smart_name, "smart", None)
# Nähte zählen mit: viele/lange Nähte = Teile zerschnitten, sichtbare Textur-Sprünge (die Flächen-Messung sieht das nicht)
for _m, _k in ((tripo_m, "tripo"), (smart_m, "smart")):
    _m["seam_penalty"] = round(CFG["seam_weight"] * insp[_k][0]["seam_length_per_size"], 4)
    _m["error_score"] = round(_m["error_score"] + _m["seam_penalty"], 4)
use_smart = mode == "smart" or (mode == "auto" and smart_m["error_score"] < CFG["switch_ratio"] * tripo_m["error_score"])
print("UV_SCORE tripo", tripo_m["error_score"], "smart", smart_m["error_score"])
for _a in [a_ for a_ in me.color_attributes if a_.name.startswith(("isl_", "dens_"))]:
    me.color_attributes.remove(_a)                  # nur für die Bilder – nicht ins Modell exportieren

baked = []
if use_smart:
    baked = rebake_to(smart_name)
else:
    me.uv_layers.remove(me.uv_layers[smart_name])
final_uv = me.uv_layers.active.name


# ------------------------------------------------------------------ Sichtprüfung
def layout_png(cnt, path):
    img = bpy.data.images.new("lay", cnt.shape[1], cnt.shape[0])
    rgba = np.zeros((cnt.shape[0], cnt.shape[1], 4), np.float32)
    rgba[..., 3] = 1
    rgba[cnt == 1] = (0.25, 0.6, 0.3, 1)
    rgba[cnt >= 2] = (0.9, 0.2, 0.2, 1)
    img.pixels = rgba.ravel()
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()


layout_png(tripo_cnt, OUT / "uv_layout_tripo.png")
layout_png(smart_cnt, OUT / "uv_layout_smart.png")

for p in me.polygons:          # Flat Shading nur für die Vorschau
    p.use_smooth = False
variants = [("original", None, 1)] + [("checker", TEX / "uv_checker.png", 1)] + \
           [(b, TEX / f"biome_{b}.png", CFG["preview"]["tile_repeat"]) for b in CFG["preview"]["test_biomes"]]
renders = []
for label, path, rep in variants:
    obj.data.materials.clear()
    obj.data.materials.append(orig_mat if path is None else test_material(path, rep, label))
    for vname, az, el in (("arpg", -55, 50), ("side", -90, 8)):
        p = OUT / f"uv_{label}_{vname}.png"
        shoot(p, az, el)
        renders.append(str(p))
obj.data.materials.clear()
obj.data.materials.append(orig_mat)

# Modell mit finaler UV für das Rig exportieren. WICHTIG: Original-Schattierung zurück, sonst trennt der
# glTF-Export bei Flat Shading jedes Dreieck in eigene Vertices → die Anatomie-Erkennung sieht nur Einzelteile.
for p, s in zip(me.polygons, orig_smooth):
    p.use_smooth = s
for o in bpy.data.objects:
    o.select_set(o is obj)
bpy.ops.export_scene.gltf(filepath=str(OUT / "model_uv.glb"), export_format="GLB", use_selection=True)
# Gegenprobe: gleiche Vertex-Zahl wie das Original?
n_before = len(me.vertices)
report = {"source": SRC.name, "mode": mode, "chosen": "smart_uv" if use_smart else "tripo_uv", "rebaked": baked,
          "tripo": tripo_m, "smart": smart_m, "renders": [pathlib.Path(r).name for r in renders],
          "inspect": {k: {"metrics": v[0], "images": v[1]} for k, v in insp.items()}}
fails = [k for k, v in (smart_m if use_smart else tripo_m)["checks"].items() if not v]
report["warnings"] = [f"UV-Grenzwert verletzt: {k}" for k in fails]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT / "model_uv.glb"))
n_after = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == "MESH")
report["export_vertices"] = {"before": n_before, "after": n_after}
if not use_smart and n_after != n_before:
    report["warnings"].append(f"Export hat die Vertex-Zahl verändert ({n_before} → {n_after})")
(OUT / "uv_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print("UV_CHOSEN", report["chosen"], "warnings", report["warnings"])
print("UV_OK")
