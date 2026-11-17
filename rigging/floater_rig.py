"""Schwebe-Rig (Orb/Qualle/Krake): Kern-Knochen + automatisch erkannte Tentakel-Ketten.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/floater_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/floater_rigged.blend, rig_report.json, rig_debug.json

Erkennung: Kern-Mittelpunkt (dichtester Bereich) + Kernradius; alle Vertices außerhalb der Kernkugel zerfallen
über Mesh-Kanten in zusammenhängende Stücke = Tentakel/Stacheln. Jedes Stück bekommt eine Kette aus bis zu
`max_bones` Knochen vom Ansatz (nah am Kern) zur Spitze, entlang der Querschnitte nach Abstand zum Kern.
Skelett: Root (Boden) → Core → Tent_<NN>_<k>. Tentakel sind nach Größe sortiert (Tent_01 = längster).
Blickrichtung: [floater] facing = "+x" | "-y" | … – Modell wird so gedreht, dass vorn = +X.
"""
import math
import pathlib
import sys
import tomllib

import bpy
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rig_common as RC  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CFG = tomllib.loads((HERE / "floater_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    CFG.update(tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("floater", {}))

obj, V, part, MAIN = RC.load_mesh(SRC)
# Blickrichtung → +X drehen
ANG = {"+x": 0, "-y": 90, "-x": 180, "+y": -90}[CFG["facing"]]
if ANG:
    obj.rotation_euler = (0, 0, math.radians(ANG))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    V, part, MAIN = RC.arrays(obj)
GROUND = V[:, 2].min()
size = float(np.max(V.max(0) - V.min(0)))

# Kern: iterativ zum dichtesten Bereich wandern, Radius = Dichte-Spitze der Abstände
c = np.median(V, 0)
for rad in (0.4, 0.3, 0.22, 0.16):
    sel = V[np.linalg.norm(V - c, axis=1) < rad * size]
    if len(sel) > 20:
        c = sel.mean(0)
d = np.linalg.norm(V - c, axis=1)
hist, edges = np.histogram(d[d < CFG["core_search"] * size], bins=40)
r_core = float(edges[np.argmax(hist) + 1]) * CFG["core_scale"]
print(f"RIG_INFO Kern bei {np.round(c, 3).tolist()}, Radius {r_core:.3f} (Größe {size:.3f})")

# Tentakel = zusammenhängende Stücke außerhalb der Kernkugel
outside = d > r_core
E = np.array([e.vertices[:] for e in obj.data.edges])
groups = {}
for i, co in enumerate(np.round(V, 5)):
    groups.setdefault(tuple(co), []).append(i)
parent = np.arange(len(V))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


for x, y in E:
    if outside[x] and outside[y]:
        parent[find(x)] = find(y)
for g in groups.values():
    if outside[g[0]]:
        for x in g[1:]:
            parent[find(x)] = find(g[0])
comp = np.array([find(i) if outside[i] else -1 for i in range(len(V))])
ids, counts = np.unique(comp[comp >= 0], return_counts=True)
B = {"Root": (np.array([c[0], c[1], GROUND]), np.array([c[0], c[1], GROUND + 0.1 * size]), None),
     "Core": (c, c + np.array([CFG["core_bone"] * size, 0, 0]), "Root")}
order = ["Root", "Core"]
TENT = []
for cid in ids[np.argsort(-counts)]:
    idx = np.where(comp == cid)[0]
    if len(idx) < CFG["min_verts"]:
        continue
    P = V[idx]
    dd = d[idx]
    length = dd.max() - dd.min()
    if length < CFG["min_length"] * size:
        continue
    nb = int(np.clip(round(length / (CFG["bone_length"] * size)), 1, CFG["max_bones"]))
    qs = np.linspace(dd.min(), dd.max(), nb + 1)
    pts = []
    for k, q in enumerate(qs):
        band = P[np.abs(dd - q) < max(0.02 * size, (qs[1] - qs[0]) * 0.5)]
        pts.append(band.mean(0) if len(band) else P[np.argmin(np.abs(dd - q))])
    pts[-1] = P[np.argmax(dd)]                                         # Spitze
    base_dir = pts[0] - c
    pts[0] = c + base_dir / max(1e-9, np.linalg.norm(base_dir)) * r_core * 0.9   # Ansatz auf der Kernkugel
    t = len(TENT) + 1
    for k in range(nb):
        n = f"Tent_{t:02d}_{k + 1}"
        B[n] = (pts[k], pts[k + 1], "Core" if k == 0 else f"Tent_{t:02d}_{k}")
        order.append(n)
    TENT.append({"name": f"Tent_{t:02d}", "verts": idx, "bones": nb, "length": float(length),
                 "dir": (P.mean(0) - c).tolist()})
arm = RC.build_armature("Floater_Rig", B, order, size)

# Gewichte: Kern-Vertices → Core; Tentakel-Vertices nur an die eigene Kette (+ Core am Ansatz)
names = order[1:]
allow = np.zeros((len(V), len(names)), bool)
allow[:, names.index("Core")] = True
for T in TENT:
    cols = [names.index(f"{T['name']}_{k + 1}") for k in range(T["bones"])]
    for j in cols:
        allow[T["verts"], j] = True
    allow[T["verts"], names.index("Core")] = d[T["verts"]] < r_core * CFG["core_blend"]
RC.skin(obj, V, part, MAIN, B, names, allow, CFG)
report = {"vertices": int(len(V)), "size_m": round(size, 3), "core_radius_m": round(r_core, 3),
          "tentacles": [{"name": T["name"], "bones": T["bones"], "length_m": round(T["length"], 3)} for T in TENT],
          "bones": len(order)}
RC.finish(obj, arm, OUT, "floater_rigged.blend", report, B, order, V)
