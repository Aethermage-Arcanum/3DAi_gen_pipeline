"""Schwebe-Rig (Orb/Qualle/Krake): Kern-Knochen + automatisch erkannte Tentakel-Ketten.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/floater_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/floater_rigged.blend, rig_report.json, rig_debug.json

Erkennung: Kern-Mittelpunkt (dichtester Bereich) + Kernradius; alle Vertices außerhalb der Kernkugel zerfallen
über Mesh-Kanten in zusammenhängende Stücke = Tentakel/Stacheln. Jedes Stück bekommt eine Kette aus bis zu
`max_bones` Knochen vom Ansatz (nah am Kern) zur Spitze, entlang der Querschnitte nach Abstand zum Kern.
Wurzel-Verlängerung (root_depth < 1): jedes Stück wächst innerhalb der Kernkugel bis zur echten Wurzel weiter,
damit Tentakel bis zum Ansatz beweglich sind (sonst sind ihre oberen ~30 % starr am Kern).
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
PIECES = []
for cid in ids[np.argsort(-counts)]:
    idx = np.where(comp == cid)[0]
    if len(idx) < CFG["min_verts"]:
        continue
    if d[idx].max() - d[idx].min() < CFG["min_length"] * size:
        continue
    PIECES.append(idx)
N_MAIN = len(PIECES)
if CFG["root_depth"] < 1.0:          # kurze Tentakel, die kaum aus der Kernkugel ragen: erst nach dem Wachsen beurteilen
    for cid in ids[np.argsort(-counts)]:
        idx = np.where(comp == cid)[0]
        if CFG["seed_min_verts"] <= len(idx) and not any(np.array_equal(idx, p) for p in PIECES[:N_MAIN]):
            PIECES.append(idx)

# Wurzel-Verlängerung (2026-11-17, Nutzer: "Tentakel sind bis an die Wurzel wabbelig"): die große Kernkugel trennt die
# Tentakel sauber, schneidet aber ihre oberen ~30 % ab (starr am Kern). Jedes Stück wächst darum über Mesh-Kanten nach
# innen bis zur echten Wurzel: nur Vertices mit fallendem Abstand zur Mitte (kein Seitwärts-Kriechen über den Kern),
# innerhalb einer Röhre um die nach innen verlängerte Tentakel-Achse, nicht tiefer als root_depth × Kernradius.
r_root = r_core * CFG["root_depth"]
SEG = []
for idx in PIECES:
    band = idx[d[idx] < d[idx].min() + 0.04 * size]
    cen = V[band].mean(0)
    rad = max(CFG["root_min_radius"] * size, float(np.linalg.norm(V[band] - cen, axis=1).mean()))
    # Achse nach innen verlängern: Tangente am Ansatz (hängende Tentakel kommen nicht radial aus dem Kern),
    # gemischt mit der Richtung zur Mitte; so weit, bis die Achse root_depth erreicht (max. Kernradius lang)
    nxt = idx[(d[idx] >= d[idx].min() + 0.04 * size) & (d[idx] < d[idx].min() + 0.10 * size)]
    tang = cen - V[nxt].mean(0) if len(nxt) else c - cen
    tang /= max(1e-9, np.linalg.norm(tang))
    toc = (c - cen) / max(1e-9, np.linalg.norm(c - cen))
    u = tang * (1 - CFG["root_bend_to_core"]) + toc * CFG["root_bend_to_core"]
    u /= max(1e-9, np.linalg.norm(u))
    end = cen
    for s in np.linspace(0, r_core, 60):
        end = cen + u * s
        if np.linalg.norm(end - c) <= r_root:
            break
    SEG.append((end, cen, rad * CFG["root_radius"]))
lab = np.full(len(V), -1)
for t, idx in enumerate(PIECES):
    lab[idx] = t
if CFG["root_depth"] < 1.0 and PIECES:
    import heapq
    adj = [[] for _ in range(len(V))]
    for x, y in E:
        adj[x].append(y)
        adj[y].append(x)
    for g in groups.values():
        for x in g:
            adj[x].extend(y for y in g if y != x)
    tol = 0.003 * size
    segd = [lambda p, S=S: float(RC.seg_dist(p[None], S[0], S[1])[0]) for S in SEG]
    dist = np.where(lab >= 0, 0.0, np.inf)
    pq = [(0.0, int(i)) for i in np.where(lab >= 0)[0]]
    heapq.heapify(pq)
    while pq:
        g, x = heapq.heappop(pq)
        if g > dist[x]:
            continue
        L = lab[x]
        for y in adj[x]:
            if outside[y] or d[y] < r_root or d[y] > d[x] + tol or segd[L](V[y]) > SEG[L][2]:
                continue
            ng = g + float(np.linalg.norm(V[y] - V[x]))
            if ng < dist[y]:
                dist[y], lab[y] = ng, L
                heapq.heappush(pq, (ng, y))
    for g in groups.values():                                         # UV-Naht-Duplikate gleich behandeln
        ls = lab[g]
        if (ls >= 0).any():
            lab[g] = ls[ls >= 0][0]
    print(f"RIG_INFO Wurzel-Verlängerung bis {r_root:.3f}: {int(((lab >= 0) & ~outside).sum())} Kern-Vertices "
          f"gehören jetzt zu Tentakeln")

TENT = []
for pi in range(len(PIECES)):
    idx = np.where(lab == pi)[0]
    P = V[idx]
    dd = d[idx]
    length = dd.max() - dd.min()
    if pi >= N_MAIN and (len(idx) < CFG["min_verts"] or length < CFG["min_length"] * size):
        lab[idx] = -1                                                  # bleibt am Kern
        continue
    nb = int(np.clip(round(length / (CFG["bone_length"] * size)), 1, CFG["max_bones"]))
    qs = np.linspace(dd.min(), dd.max(), nb + 1)
    pts = []
    for k, q in enumerate(qs):
        band = P[np.abs(dd - q) < max(0.02 * size, (qs[1] - qs[0]) * 0.5)]
        pts.append(band.mean(0) if len(band) else P[np.argmin(np.abs(dd - q))])
    pts[-1] = P[np.argmax(dd)]                                         # Spitze
    base_dir = pts[0] - c
    root_d = r_core * 0.9 if CFG["root_depth"] >= 1.0 else dd.min()             # Ansatz: Kernkugel bzw. echte Wurzel
    pts[0] = c + base_dir / max(1e-9, np.linalg.norm(base_dir)) * root_d
    t = len(TENT) + 1
    for k in range(nb):
        n = f"Tent_{t:02d}_{k + 1}"
        B[n] = (pts[k], pts[k + 1], "Core" if k == 0 else f"Tent_{t:02d}_{k}")
        order.append(n)
    TENT.append({"name": f"Tent_{t:02d}", "verts": idx, "bones": nb, "length": float(length), "root_d": float(root_d),
                 "dir": (P.mean(0) - c).tolist()})
arm = RC.build_armature("Floater_Rig", B, order, size)

# Gewichte: Kern-Vertices → Core; Tentakel-Vertices nur an die eigene Kette (+ Core am Ansatz)
names = order[1:]
allow = np.zeros((len(V), len(names)), bool)
allow[:, names.index("Core")] = True
RING = {}                                                             # Kern-Vertex → (Anteil, Tentakel-Knochen)
for T in TENT:
    cols = [names.index(f"{T['name']}_{k + 1}") for k in range(T["bones"])]
    for j in cols:
        allow[T["verts"], j] = True
    allow[T["verts"], names.index("Core")] = d[T["verts"]] < r_core * CFG["core_blend"]
    if CFG["root_depth"] < 1.0 and CFG["ring_fade"]:
        # Saum: Kern-Vertices direkt neben dem Tentakel gehen abgeschwächt mit (ring_fade je Kanten-Ring), sonst springt
        # das Gewicht an der Grenze von 1 auf 0 → die Wurzel reißt, sobald sie sich bewegt
        mine = set(int(i) for i in T["verts"])
        front, seen = set(mine), set(mine)
        for hop, fade in enumerate(CFG["ring_fade"]):
            front = {y for x in front for y in adj[x] if lab[y] < 0} - seen
            seen |= front
            for y in front:
                if fade > RING.get(y, (0, None))[0]:
                    RING[y] = (fade, cols)
Wt = RC.skin(obj, V, part, MAIN, B, names, allow, CFG)
if RING:
    ci = names.index("Core")
    tw = 1.0 / (np.stack([RC.seg_dist(V, B[n][0], B[n][1]) for n in names], 1) + 1e-4) ** CFG["falloff"]
    for g in groups.values():                                         # UV-Naht-Duplikate: gleicher Saum-Anteil
        r = [RING[i] for i in g if i in RING]
        if r:
            for i in g:
                RING[i] = max(r, key=lambda x: x[0])
    for i, (fade, cols) in RING.items():
        top = sorted(cols, key=lambda j: -tw[i, j])[:3]                 # max. 4 Einflüsse (Unity-Standard): 3 Knochen + Core
        w = tw[i, top] / max(1e-12, tw[i, top].sum()) * fade
        for gname in [names[j] for j in cols] + ["Core"]:
            obj.vertex_groups[gname].remove([int(i)])
        obj.vertex_groups["Core"].add([int(i)], float(1 - fade), "REPLACE")
        for j, wj in zip(top, w):
            if wj > 1e-3:
                obj.vertex_groups[names[j]].add([int(i)], float(wj), "REPLACE")
if CFG["root_depth"] < 1.0:
    # Wo zwei Tentakel an der Wurzel verwachsen sind, mitteln die Grenz-Vertices beide Ketten (sonst reißt die Naht)
    TL = np.full(len(V), -1)
    for k, T in enumerate(TENT):
        TL[T["verts"]] = k
    newW = {}
    for i in np.where(TL >= 0)[0]:
        nb = [y for y in adj[i] if TL[y] >= 0 and TL[y] != TL[i]]
        if nb:
            newW[int(i)] = 0.5 * Wt[i] + 0.5 * Wt[nb].mean(0)
    for i, w in newW.items():
        top = np.argsort(-w)[:4]
        w4 = w[top] / w[top].sum()
        for g in obj.vertex_groups:
            g.remove([i])
        for j, wj in zip(top, w4):
            if wj > 1e-3:
                obj.vertex_groups[names[j]].add([i], float(wj), "REPLACE")
    print(f"RIG_INFO Saum: {len(RING)} Kern-Vertices weich, {len(newW)} Tentakel-Nähte gemittelt")
report = {"vertices": int(len(V)), "size_m": round(size, 3), "core_radius_m": round(r_core, 3),
          "root_radius_m": round(r_root, 3), "root_verts": int(((lab >= 0) & ~outside).sum()),
          "tentacles": [{"name": T["name"], "bones": T["bones"], "length_m": round(T["length"], 3)} for T in TENT],
          "bones": len(order)}
RC.finish(obj, arm, OUT, "floater_rigged.blend", report, B, order, V)
