"""Mehrbein-Rig (Skorpione, Spinnen, Insekten aus EINEM zusammenhängenden Mesh) über Oberflächen-Wege.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/multileg_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/multileg_rigged.blend, rig_report.json, rig_debug.json

Warum: rigging/crawler_rig.py braucht getrennte Mesh-Inseln pro Beinsegment (wie beim Chitin Crawler). Neuere
Tripo-Modelle sind ein zusammenhängendes Mesh → hier wird jede Gliedmaße als kürzester Weg über die Oberfläche
(Dijkstra) von ihrer Spitze zur Körpermitte gefunden. Funktioniert auch für Spinnenbeine (erst hoch zum Knie,
dann runter zum Körper), Scheren und gebogene Schwänze.

Skelett (Namen passen zum Beine-Baukasten motions/quadruped/quadruped_kit.py):
  Root · Hips (Mitte→hinten) · Spine_1 · Chest (→vorn) · Neck_1 · Neck_2 · Head · Jaw
  Leg_<L|R><1..n>_1..4 (Hüfte, Oberschenkel, Schiene, Fuß; 1 = vorderstes Laufbein)
  Claw_<L|R>_1..3 (Scheren/Taster, falls vorhanden) · Tail_1..5 + Stinger (falls vorhanden)
"""
import heapq
import pathlib
import sys
import tomllib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rig_common as RC  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CFG = tomllib.loads((HERE / "multileg_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    CFG.update(tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("multileg", {}))

obj, V, part, MAIN = RC.load_mesh(SRC)
N = len(V)
GROUND = V[:, 2].min()
size = float(np.max(V.max(0) - V.min(0)))
H = float(V[:, 2].max() - GROUND)

# ------------------------------------------------------------------ Graph über die Oberfläche (Duplikate verschweißt)
key = {}
rep = np.zeros(N, int)
for i, co in enumerate(np.round(V, 5)):
    rep[i] = key.setdefault(tuple(co), i)
adj = {}
for e in obj.data.edges:
    x, y = rep[e.vertices[0]], rep[e.vertices[1]]
    if x == y:
        continue
    w = float(np.linalg.norm(V[x] - V[y]))
    adj.setdefault(x, []).append((y, w))
    adj.setdefault(y, []).append((x, w))

# Körpermitte: iterativ zum dichtesten Bereich
c = np.median(V, 0)
for rad in (0.35, 0.25, 0.18, 0.12):
    sel = V[np.linalg.norm(V - c, axis=1) < rad * size]
    if len(sel) > 20:
        c = sel.mean(0)
src = int(rep[np.argmin(np.linalg.norm(V - c, axis=1))])
dist = {src: 0.0}
prev = {}
pq = [(0.0, src)]
while pq:
    dd, u = heapq.heappop(pq)
    if dd > dist.get(u, 1e18):
        continue
    for v, w in adj.get(u, []):
        nd = dd + w
        if nd < dist.get(v, 1e18):
            dist[v], prev[v] = nd, u
            heapq.heappush(pq, (nd, v))
G = np.array([dist.get(rep[i], np.inf) for i in range(N)])


def path_to_center(i):
    p, u = [], int(rep[i])
    while u in prev:
        p.append(u)
        u = prev[u]
    p.append(u)
    return np.array([V[k] for k in p])                     # Spitze → Mitte


def centerline(path):
    """Oberflächen-Weg → Mittellinie: jeden Punkt durch den Schwerpunkt seiner Umgebung ersetzen."""
    r = CFG["section_radius"] * size
    out = []
    for p in path:
        nb = V[np.linalg.norm(V - p, axis=1) < r]
        out.append(nb.mean(0) if len(nb) else p)
    return np.array(out)


def resample(path, n):
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n)
    return np.array([np.array([np.interp(x, s, path[:, k]) for k in range(3)]) for x in t])


def attach_index(path):
    """Wo betritt der Weg (Spitze → Mitte) den Körper? Dort, wo die Umgebung plötzlich viel dichter wird."""
    r = CFG["thickness_radius"] * size
    cnt = np.array([(np.linalg.norm(V - p, axis=1) < r).sum() for p in path])
    base = np.median(cnt[: max(3, len(cnt) // 3)])
    for i, k in enumerate(cnt):
        if i > len(cnt) * 0.3 and k > CFG["thickness_jump"] * base:
            return i
    return int(len(cnt) * 0.8)


B = {}
order = []
DEBUG = {}
LIMB_PATHS = {}

# Körperachse
front = V[(np.abs(V[:, 1] - c[1]) < CFG["mid_half_width"] * size) & (V[:, 2] > GROUND + 0.3 * H)]
x_front = float(front[:, 0].max())
x_back = float(V[(np.abs(V[:, 1] - c[1]) < CFG["mid_half_width"] * size)][:, 0].min())
head_tip = front[np.argmax(front[:, 0])]
body_front = c + np.array([CFG["chest_ahead"] * (x_front - c[0]), 0, 0])
body_back = c + np.array([-CFG["hips_back"] * (c[0] - x_back), 0, 0])
root = np.array([c[0], c[1], GROUND])
B.update({"Root": (root, root + np.array([0, 0, 0.1 * size]), None),
          "Hips": (c, body_back, "Root"),
          "Spine_1": (c, c + 0.5 * (body_front - c), "Root"),
          "Chest": (c + 0.5 * (body_front - c), body_front, "Spine_1"),
          "Neck_1": (body_front, body_front + 0.3 * (head_tip - body_front), "Chest"),
          "Neck_2": (body_front + 0.3 * (head_tip - body_front), body_front + 0.5 * (head_tip - body_front), "Neck_1"),
          "Head": (body_front + 0.5 * (head_tip - body_front), head_tip, "Neck_2")})
# ------------------------------------------------------------------ Füße: Bodenkontakt-Flecken
fb = np.where(V[:, 2] < GROUND + CFG["foot_band"] * H)[0]
clusters = []
for i in fb:
    for cl in clusters:
        if np.min(np.linalg.norm(V[cl][:, :2] - V[i, :2], axis=1)) < CFG["foot_merge"] * size:
            cl.append(i)
            break
    else:
        clusters.append([i])
feet = [cl for cl in clusters if len(cl) >= 2]
feet = sorted(feet, key=lambda cl: -V[cl, 0].mean())         # vorn → hinten
LEGS = {"L": [], "R": []}
CLAW_TIPS = {}
for cl in feet:
    tip = cl[int(np.argmax(G[cl]))]                        # Fußspitze = am weitesten von der Mitte
    side = "L" if V[tip, 1] > c[1] else "R"
    if CFG["claws"] and V[tip, 0] > head_tip[0] and side not in CLAW_TIPS:
        CLAW_TIPS[side] = tip                              # Bodenkontakt VOR dem Kopf = Scherenspitze
        continue
    LEGS[side].append(tip)
print(f"RIG_INFO Körpermitte {np.round(c, 3).tolist()} · Füße links {len(LEGS['L'])}, rechts {len(LEGS['R'])}")



def chain(prefix, tip, fracs, parent, knee=False):
    p = path_to_center(tip)
    ai = attach_index(p)
    limb = centerline(p[: ai + 1])[::-1]                     # Ansatz → Spitze
    limb[-1] = V[tip]
    pts = resample(limb, 60)
    js = [pts[int(round(f * (len(pts) - 1)))] for f in fracs]
    if knee:                                                # Spinnenknie = höchster Punkt im mittleren Bereich
        lo, hi = int(0.15 * len(pts)), int(0.65 * len(pts))
        js[2] = pts[lo + int(np.argmax(pts[lo:hi, 2]))]
    names = []
    for k in range(len(js) - 1):
        n = f"{prefix}_{k + 1}"
        B[n] = (js[k], js[k + 1], parent if k == 0 else f"{prefix}_{k}")
        order.append(n)
        names.append(n)
    LIMB_PATHS[prefix] = pts
    DEBUG[prefix] = np.round(pts, 4).tolist()
    return names


order += ["Root", "Hips", "Spine_1", "Chest", "Neck_1", "Neck_2", "Head"]

for side in ("L", "R"):
    for k, tip in enumerate(LEGS[side], 1):
        chain(f"Leg_{side}{k}", tip, CFG["leg_fracs"], "Chest" if k <= len(LEGS[side]) / 2 else "Hips", knee=True)

# Scheren: vorderste Spitze je Seite oberhalb des Bodens, weit von der Mitte
if CFG["claws"]:
    for side, sg in (("L", 1), ("R", -1)):
        cand = np.where(((V[:, 1] - c[1]) * sg > CFG["claw_min_side"] * size) & (V[:, 2] > GROUND + CFG["foot_band"] * H * 2)
                        & (V[:, 0] > c[0]))[0]
        cand = cand[np.isfinite(G[cand])]
        if side in CLAW_TIPS:
            chain(f"Claw_{side}", CLAW_TIPS[side], CFG["claw_fracs"], "Chest")
        elif len(cand):
            tip = cand[np.argmax(V[cand, 0] + 0.3 * G[cand])]
            chain(f"Claw_{side}", tip, CFG["claw_fracs"], "Chest")

# Schwanz: geodätisch am weitesten entfernte Spitze hinter der Mitte
if CFG["tail"]:
    cand = np.where((V[:, 0] < c[0]) & np.isfinite(G))[0]
    tip = cand[np.argmax(G[cand])]
    p = centerline(path_to_center(tip))[::-1]
    p[-1] = V[tip]
    pts = resample(p, 80)
    start = int(CFG["tail_start"] * len(pts))
    js = [pts[start + int(round(f * (len(pts) - 1 - start)))] for f in np.linspace(0, 1, CFG["tail_bones"] + 2)]
    for k in range(len(js) - 1):
        n = f"Tail_{k + 1}" if k < CFG["tail_bones"] else "Stinger"
        B[n] = (js[k], js[k + 1], "Hips" if k == 0 else (f"Tail_{k}"))
        order.append(n)
    LIMB_PATHS["Tail"] = pts[start:]
    DEBUG["Tail"] = np.round(pts, 4).tolist()

arm = RC.build_armature("Multileg_Rig", B, order, size)

# ------------------------------------------------------------------ Gewichte: jeder Vertex gehört zur nächsten Gliedmaße
names = order[1:]
limb_of = {n: (n.rsplit("_", 1)[0] if n.startswith(("Leg_", "Claw_")) else ("Tail" if n.startswith(("Tail", "Stinger")) else None))
           for n in names}
limbs = sorted({v for v in limb_of.values() if v})
body_cols = [j for j, n in enumerate(names) if limb_of[n] is None]


def limb_dist():
    dl_ = np.stack([np.min(np.stack([RC.seg_dist(V, B[n][0], B[n][1]) for n in names if limb_of[n] == L], 1), 1) for L in limbs], 1)
    db_ = np.min(np.stack([RC.seg_dist(V, B[names[j]][0], B[names[j]][1]) for j in body_cols], 1), 1)
    return dl_, db_, np.argmin(dl_, 1)


dl, dbody, nearest = limb_dist()
# Tripo verschmilzt sich berührende Gliedmaßen (z. B. zwei Hinterbeine) → Flächen, deren Ecken zu verschiedenen
# Gliedmaßen gehören (abseits des Körpers), löschen. Sonst zieht jede Gliedmaße die gemeinsame Haut mit.
if CFG.get("cut_fused_limbs", True):
    limbish = np.min(dl, 1) * CFG["body_reach"] < dbody
    # Schwanzbogen, der den Rücken berührt (ab Tail_3): Verbindung Schwanz ↔ Körper ist ebenfalls eine Tripo-Brücke
    tail_far = np.zeros(N, bool)
    if "Tail" in limbs:
        far_bones = [n for n in names if n in ("Tail_3", "Tail_4", "Tail_5", "Stinger")]
        if far_bones:
            d_far = np.min(np.stack([RC.seg_dist(V, B[n][0], B[n][1]) for n in far_bones], 1), 1)
            tail_far = limbish & (nearest == limbs.index("Tail")) & (d_far <= dl[:, limbs.index("Tail")] + 1e-9)
    fmask = [(len({int(nearest[v]) for v in poly.vertices}) > 1 and all(limbish[v] for v in poly.vertices)) or
             (any(tail_far[v] for v in poly.vertices) and any(not limbish[v] for v in poly.vertices))
             for poly in obj.data.polygons]
    n_cut = int(sum(fmask))
    if n_cut:
        RC.delete_faces(obj, fmask)
        V, part, MAIN = RC.arrays(obj)
        N = len(V)
        dl, dbody, nearest = limb_dist()
    print(f"RIG_INFO verschmolzene Gliedmaßen getrennt: {n_cut} Flächen entfernt")
allow = np.zeros((N, len(names)), bool)
for j, n in enumerate(names):
    L = limb_of[n]
    if L is None:
        allow[:, j] = dbody < CFG["body_reach"] * np.min(dl, 1) + 1e-9   # Körper nur, wo er nicht viel weiter weg ist
    else:
        allow[:, j] = nearest == limbs.index(L)
RC.skin(obj, V, part, MAIN, B, names, allow, CFG)
report = {"vertices": int(N), "size_m": round(size, 3), "legs": {s: len(v) for s, v in LEGS.items()},
          "limbs": limbs, "bones": len(order)}
RC.finish(obj, arm, OUT, "multileg_rigged.blend", report, B, order, V, tracks=DEBUG)
