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

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = CFG["preview"]["resolution"]
wd = bpy.data.worlds.new("w")
sc.world = wd
wd.node_tree.nodes["Background"].inputs["Color"].default_value = (0.3, 0.31, 0.33, 1)
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN"))
sun.data.energy = 3
sun.rotation_euler = (0.6, 0.2, 0.6)
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(obj.dimensions) * 1.25
sc.collection.objects.link(cam)
sc.camera = cam
orig_smooth = [p.use_smooth for p in me.polygons]
for p in me.polygons:          # Flat Shading nur für die Vorschau
    p.use_smooth = False
orig_mat = obj.active_material


def test_material(img_path, repeat, name):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.8
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(img_path))
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = final_uv
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (repeat, repeat, 1)
    nt.links.new(uvn.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def shoot(path, az, el):
    az, el = math.radians(az), math.radians(el)
    from mathutils import Vector
    cam.location = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))) * 6
    cam.rotation_euler = (-cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


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
          "tripo": tripo_m, "smart": smart_m, "renders": [pathlib.Path(r).name for r in renders]}
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
