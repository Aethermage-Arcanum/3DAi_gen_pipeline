"""Zweibeiner-Raptor-Rig (waagerechter Körper, Schwanz als Gegengewicht, kurze Greifarme).

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/biped_raptor_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/biped_raptor_rigged.blend, rig_report.json, rig_debug.json

Skelett (Unity "Generic", Namen kompatibel zum Beine-Baukasten motions/quadruped/quadruped_kit.py):
  Root · Hips → Spine_1 → Chest → Neck_1 → Neck_2 → Head → Jaw · Hips → Tail_1..4
  Beine Leg_BL/BR_1..4 (Oberschenkel, Schienbein, Mittelfuß, Zehen) · Arme Arm_L/R_1..3 (Ober-, Unterarm, Hand)
"""
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
CFG = tomllib.loads((HERE / "biped_raptor_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    CFG.update(tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("biped_raptor", {}))

obj, V, part, MAIN = RC.load_mesh(SRC)
main = part == MAIN
M = V[main]
GROUND = V[:, 2].min()
H = M[:, 2].max() - GROUND
x0, x1 = M[:, 0].min(), M[:, 0].max()
L = x1 - x0
Y_MID = float(np.median(M[:, 1]))

# ------------------------------------------------------------------ Füße + Beine (wie Vierbeiner, nur 2)
fb = M[M[:, 2] < GROUND + CFG["foot_band"] * H]
FEET = {"BL": fb[fb[:, 1] > Y_MID], "BR": fb[fb[:, 1] <= Y_MID]}


def midline(x, hw):
    s = M[(np.abs(M[:, 0] - x) < CFG["slice"] * L) & (np.abs(M[:, 1] - Y_MID) < hw)]
    s = s[s[:, 2] > GROUND + CFG["min_belly"] * H]
    return (float(np.percentile(s[:, 2], 5)), float(np.percentile(s[:, 2], 97))) if len(s) >= 3 else None


LEGS = {}
for name, fv in FEET.items():
    side = 1 if name[1] == "L" else -1
    c = fv[:, :2].mean(0)
    belly = midline(c[0], CFG["mid_half_width"] * H)
    z_top = belly[0] if belly else GROUND + 0.5 * H
    pts, z = [np.array([c[0], c[1], GROUND])], GROUND + CFG["track_step"] * H
    while z < z_top:
        band = M[(np.abs(M[:, 2] - z) < CFG["track_step"] * H) & (np.linalg.norm(M[:, :2] - c, axis=1) < CFG["leg_radius"] * H)
                 & ((M[:, 1] - Y_MID) * side > -0.02 * H)]
        if len(band) >= 3:
            c = band[:, :2].mean(0)
        pts.append(np.array([c[0], c[1], z]))
        z += CFG["track_step"] * H
    back = midline(pts[-1][0], CFG["mid_half_width"] * H)
    top_z = back[1] if back else z_top + 0.2 * H
    joint = np.array([pts[-1][0], Y_MID + CFG["joint_inset"] * (pts[-1][1] - Y_MID), z_top + CFG["joint_depth"] * (top_z - z_top)])
    LEGS[name] = {"track": np.array(pts), "belly": z_top, "back": top_z, "joint": joint, "foot": fv}


def bend(track, lo, hi, sign):
    z0, z1, p0, p1 = track[0, 2], track[-1, 2], track[0], track[-1]
    best, bi = -1e9, None
    for i, p in enumerate(track):
        f = (p[2] - z0) / max(1e-9, z1 - z0)
        if lo <= f <= hi:
            t = (p[2] - p0[2]) / max(1e-9, p1[2] - p0[2])
            dev = sign * (p[0] - (p0[0] + t * (p1[0] - p0[0])))
            if dev > best:
                best, bi = dev, i
    return track[bi] if bi is not None else None


B = {}
for name, lg in LEGS.items():
    tr, fv = lg["track"], lg["foot"]
    tip = fv[fv[:, 0].argmax()].copy()
    tip[2] = GROUND
    ball = np.array([*fv[:, :2].mean(0), GROUND + CFG["ball_height"] * H])
    h = lambda f: tr[min(len(tr) - 1, int(round(f * (len(tr) - 1))))]  # noqa: E731
    hock = bend(tr, 0.15, 0.9, -1)                       # Sprunggelenk = stärkste Biegung nach hinten
    hock = hock if hock is not None else h(0.35)
    # Vogel-/Raptorknie sitzt verdeckt am Bauch und zeigt nach vorn (sichtbar ist nur das Sprunggelenk)
    knee = np.array([lg["joint"][0] + CFG["knee_forward"] * L, lg["joint"][1] + 0.3 * (tr[-1][1] - lg["joint"][1]),
                     lg["belly"] - CFG["knee_below_belly"] * H])
    B[f"Leg_{name}_1"] = (lg["joint"], knee, "Hips")
    B[f"Leg_{name}_2"] = (knee, hock, f"Leg_{name}_1")
    B[f"Leg_{name}_3"] = (hock, ball, f"Leg_{name}_2")
    B[f"Leg_{name}_4"] = (ball, tip, f"Leg_{name}_3")


# ------------------------------------------------------------------ Wirbelsäule, Hals, Kopf, Schwanz
def center_at(x):
    s = M[np.abs(M[:, 0] - x) < CFG["slice"] * L]
    if len(s) < 3:
        return None
    mid = s[np.abs(s[:, 1] - Y_MID) < CFG["mid_half_width"] * H]
    zz = mid[:, 2] if len(mid) >= 3 else s[:, 2]
    return np.array([x, Y_MID, (np.percentile(zz, 10) + np.percentile(zz, 90)) / 2])


x_hip = (LEGS["BL"]["joint"][0] + LEGS["BR"]["joint"][0]) / 2
x_ch = x_hip + CFG["chest_ahead"] * (x1 - x_hip)
x_hb = x1 - CFG["head_length"] * (x1 - x_hip)
spine = [center_at(x_hip + f * (x_ch - x_hip)) for f in (0, 0.5, 1)]
neck = [spine[2], center_at(x_ch + 0.5 * (x_hb - x_ch)), center_at(x_hb)]
nose_s = M[M[:, 0] > x1 - 0.02 * L]
nose = np.array([x1, Y_MID, float(np.median(nose_s[:, 2]))])
head_low = float(np.percentile(M[M[:, 0] > x_hb][:, 2], 10))
x_tb = x_hip - CFG["tail_base"] * L
tail = [spine[0]] + [center_at(x_tb + f * (x0 - x_tb)) for f in (0.0, 0.33, 0.66)]
tip_s = M[M[:, 0] < x0 + 0.02 * L].mean(0)
tail.append(np.array([x0, Y_MID, tip_s[2]]))
tail = [t if t is not None else tail[i - 1] for i, t in enumerate(tail)]
root = np.array([x_hip, Y_MID, GROUND])
B.update({
    "Root": (root, root + np.array([0, 0, 0.15 * H]), None),
    "Hips": (spine[0], spine[1], "Root"),
    "Spine_1": (spine[1], spine[2], "Hips"),
    "Chest": (spine[2], spine[2] + 0.5 * (neck[1] - spine[2]), "Spine_1"),
    "Neck_1": (spine[2] + 0.5 * (neck[1] - spine[2]), neck[1], "Chest"),
    "Neck_2": (neck[1], neck[2], "Neck_1"),
    "Head": (neck[2], nose, "Neck_2"),
    "Jaw": (np.array([x_hb + 0.25 * (x1 - x_hb), Y_MID, (neck[2][2] + head_low) / 2]),
            np.array([x1, Y_MID, head_low + 0.3 * (nose[2] - head_low)]), "Head"),
    "Tail_1": (tail[0], tail[2], "Hips"), "Tail_2": (tail[2], tail[3], "Tail_1"),
    "Tail_3": (tail[3], tail[3] + 0.5 * (tail[4] - tail[3]), "Tail_2"),
    "Tail_4": (tail[3] + 0.5 * (tail[4] - tail[3]), tail[4], "Tail_3"),
})

# ------------------------------------------------------------------ Arme: tiefste Krallenspitze vor den Beinen, nach oben verfolgen
ARMS = {}
for side, sn in ((1, "L"), (-1, "R")):
    win = M[(M[:, 0] > x_hip + CFG["arm_window"][0] * (x_hb - x_hip)) & (M[:, 0] < x_hip + CFG["arm_window"][1] * (x_hb - x_hip))
            & ((M[:, 1] - Y_MID) * side > CFG["arm_min_side"] * H) & (M[:, 2] > GROUND + CFG["foot_band"] * H * 2)]
    for lg in LEGS.values():                               # Bein-Bereich ausschließen (sonst findet man den Oberschenkel)
        win = win[np.linalg.norm(win[:, :2] - lg["joint"][:2], axis=1) > CFG["arm_leg_clear"] * L]
    if len(win) < 5:
        continue
    tipv = win[win[:, 2].argmin()]
    c, z, pts = tipv[[0, 1]], tipv[2], [tipv]
    chest_low = (midline(x_ch, CFG["mid_half_width"] * H) or (tipv[2] + 0.2 * H,))[0]
    while z < chest_low:
        z += CFG["track_step"] * H
        band = win[(np.abs(win[:, 2] - z) < CFG["track_step"] * H) & (np.linalg.norm(win[:, :2] - c, axis=1) < CFG["arm_radius"] * H)]
        if len(band) >= 3:
            c = band[:, :2].mean(0)
        pts.append(np.array([c[0], c[1], z]))
    tr = np.array(pts)
    sl = M[np.abs(M[:, 0] - tr[-1][0]) < CFG["slice"] * L]
    sl = sl[sl[:, 2] > chest_low]                           # Brust-Querschnitt (ohne hängende Arme)
    hw = float(np.percentile(np.abs(sl[:, 1] - Y_MID), 85)) if len(sl) > 5 else 0.1 * H
    sh = np.array([tr[-1][0], Y_MID + side * min(abs(0.6 * (tr[-1][1] - Y_MID)), 0.8 * hw),
                   chest_low + 0.3 * H * CFG["joint_depth"]])
    el = tr[int(len(tr) * 0.55)]
    wr = tr[int(len(tr) * 0.2)]
    B[f"Arm_{sn}_1"] = (sh, el, "Chest")
    B[f"Arm_{sn}_2"] = (el, wr, f"Arm_{sn}_1")
    B[f"Arm_{sn}_3"] = (wr, tipv, f"Arm_{sn}_2")
    ARMS[sn] = tr

order = ["Root", "Hips", "Spine_1", "Chest", "Neck_1", "Neck_2", "Head", "Jaw", "Tail_1", "Tail_2", "Tail_3", "Tail_4"] + \
    [f"Arm_{s}_{k}" for s in ARMS for k in (1, 2, 3)] + [f"Leg_{n}_{k}" for n in ("BL", "BR") for k in range(1, 5)]
arm = RC.build_armature("Biped_Rig", B, order, H)

# ------------------------------------------------------------------ Tripo-Hautbrücke zwischen den Beinen entfernen
if CFG.get("cut_between_legs", True):
    dl = {sd: np.min(np.stack([RC.seg_dist(V, B[f"Leg_{sd}_{k}"][0], B[f"Leg_{sd}_{k}"][1]) for k in (1, 2, 3)], 1), 1)
          for sd in LEGS}
    belly = min(lg["belly"] for lg in LEGS.values())
    web = (np.abs(dl["BL"] - dl["BR"]) < CFG["web_tolerance"] * H) & (V[:, 2] < belly) &         (V[:, 2] > GROUND + CFG["between_min_z"] * H) & (np.abs(V[:, 1] - Y_MID) < CFG["web_half_width"] * H)
    me = obj.data
    # Flächen, die linke und rechte Bein-Seite direkt verbinden (unterhalb des Bauchs), sind die Brücke
    left = dl["BL"] < dl["BR"]
    low = (V[:, 2] < belly) & (V[:, 2] > GROUND + CFG["between_min_z"] * H)
    fmask = [all(web[v] for v in poly.vertices) or
             (all(low[v] for v in poly.vertices) and len({bool(left[v]) for v in poly.vertices}) == 2
              and all(abs(V[v, 1] - Y_MID) < CFG["bridge_half_width"] * H for v in poly.vertices))
             for poly in me.polygons]
    n_cut = sum(fmask)
    if n_cut:
        RC.delete_faces(obj, fmask)
        V, part, MAIN = RC.arrays(obj)
        main = part == MAIN
    print(f"RIG_INFO Hautbrücke zwischen den Beinen: {n_cut} Flächen entfernt")

# ------------------------------------------------------------------ Hängender Lappen unter dem Bauch (Tripo-Fehlinterpretation)
# Zeigt das Front-Referenzbild den Schwanz zwischen den Beinen, baut Tripo dort einen Hautstreifen, der an den
# Schienbeinen hängt und wie ein zweiter Schwanz mitschwingt (Dune Raptor). Schmales Band an der Mittellinie,
# knapp hinter der Hüfte, unterhalb der Bauchlinie → löschen. Unterseite ist aus der Spielkamera nicht sichtbar.
if CFG.get("cut_belly_flap", False):
    hx = B["Hips"][0][0]
    fv = (np.abs(V[:, 1] - Y_MID) < CFG["flap_half_width"] * H) & (V[:, 0] > hx - CFG["flap_x_back"] * H) \
        & (V[:, 0] < hx + CFG["flap_x_front"] * H) & (V[:, 2] < GROUND + CFG["flap_max_height"] * H) \
        & (V[:, 2] > GROUND + CFG["flap_min_height"] * H)
    fmask = [any(fv[v] for v in poly.vertices) for poly in obj.data.polygons]
    n_flap = sum(fmask)
    if n_flap:
        RC.delete_faces(obj, fmask)
        V, part, MAIN = RC.arrays(obj)
        main = part == MAIN
    print(f"RIG_INFO Bauch-Lappen: {int(fv.sum())} Vertices, {n_flap} Flächen entfernt")

# ------------------------------------------------------------------ Gewichte mit anatomischen Masken
names = order[1:]
allow = np.ones((len(V), len(names)), bool)
leg_top = max(lg["joint"][2] for lg in LEGS.values())
for j, n in enumerate(names):
    if n.startswith("Leg_"):
        lg = LEGS[n[4:6]]
        side = 1 if n[5] == "L" else -1
        allow[:, j] = ((V[:, 1] - Y_MID) * side > CFG["leg_side_min"] * H) & (np.abs(V[:, 0] - lg["joint"][0]) < CFG["leg_x_reach"] * L) \
            & (V[:, 2] < lg["joint"][2] + CFG["leg_top_margin"] * H)
    if n.startswith("Arm_"):
        side = 1 if n[4] == "L" else -1
        tr = ARMS[n[4]]
        allow[:, j] = ((V[:, 1] - Y_MID) * side > CFG["arm_min_side"] * H * 0.5) & \
            (np.abs(V[:, 0] - tr[:, 0].mean()) < CFG["arm_x_reach"] * L)
    if n == "Jaw":
        allow[:, j] = (V[:, 0] > x_hb + 0.2 * (x1 - x_hb)) & (V[:, 2] < B["Jaw"][0][2] + 0.02 * H)
    if n == "Head":
        allow[:, j] = V[:, 0] > x_hb - 0.1 * (x1 - x_hb)
    if n.startswith("Tail"):
        # nur hinter der Hüfte UND nicht im Oberschenkel (sonst zieht der Schwanz die Beinhaut mit)
        thigh = np.zeros(len(V), bool)
        for lg in LEGS.values():
            thigh |= (np.linalg.norm(V[:, :2] - lg["joint"][:2], axis=1) < CFG["thigh_radius"] * L) &                 (V[:, 2] < lg["joint"][2] + 0.1 * H)
        allow[:, j] = (V[:, 0] < x_hip - CFG["tail_clear"] * L) & ~thigh
# Tripo verschmilzt eng stehende Beine an der Innenseite → jeder Vertex gehört EXKLUSIV zum näheren Bein
# (sonst ziehen ihn beide Beine gegenläufig und er reißt)
dleg = {sd: np.min(np.stack([RC.seg_dist(V, B[f"Leg_{sd}_{k}"][0], B[f"Leg_{sd}_{k}"][1]) for k in (1, 2, 3, 4)], 1), 1)
        for sd in LEGS}
if len(dleg) == 2:
    closer_L = dleg["BL"] < dleg["BR"]
    # Haut zwischen den Beinen (etwa gleich weit von beiden, oberhalb Sprunggelenk) → gehört zum Rumpf
    between = (np.abs(dleg["BL"] - dleg["BR"]) < CFG["between_legs"] * H) & (V[:, 2] > GROUND + CFG["between_min_z"] * H)
    for j, n in enumerate(names):
        if n.startswith("Leg_"):
            allow[between, j] = False
    for j, n in enumerate(names):
        if n.startswith("Leg_BL"):
            allow[:, j] &= closer_L
        elif n.startswith("Leg_BR"):
            allow[:, j] &= ~closer_L
body_cols = [j for j, n in enumerate(names) if not n.startswith(("Leg_", "Arm_"))]
for nm, lg in LEGS.items():                                   # unterhalb des Bauchs nur Bein
    near = (np.linalg.norm(V[:, :2] - lg["track"][:, :2].mean(0), axis=1) < CFG["leg_capture"] * H) & \
        (V[:, 2] < lg["belly"] - 0.05 * H)
    allow[np.ix_(near, body_cols)] = False
for sn, tr in ARMS.items():                                   # Arm unterhalb der Brust nur Arm
    near = (np.linalg.norm(V[:, :2] - tr[:, :2].mean(0), axis=1) < CFG["arm_radius"] * H * 1.5) & \
        (V[:, 2] < tr[-1][2] - 0.05 * H)
    allow[np.ix_(near, body_cols + [j for j, n in enumerate(names) if n.startswith("Leg_")])] = False
RC.skin(obj, V, part, MAIN, B, names, allow, CFG)

# ------------------------------------------------------------------ Fußsohle starr am Fuß (Bodenkontakt)
# Vogelfuß: alle Zehen (auch die nach hinten zeigende Hallux-Kralle) sitzen am Ballen-Gelenk = Leg_X_4. Hingen
# bodennahe Vertices teils am Mittelfuß (Leg_3) oder sogar am Schienbein (Leg_2), kippten sie beim Ausgreifen mit
# dem Mittelfuß mit – die hintere Kralle sank im Walk 1,9 cm in den Boden (Unity-Messung 2026-11-17).
# Fix: alles unterhalb foot_rigid_height gehört ganz zu Leg_X_4, darüber weicher Übergang bis + foot_blend.
n_sole = 0
if CFG.get("foot_rigid_height", 0) > 0:
    za = GROUND + CFG["foot_rigid_height"] * H
    zb = za + CFG.get("foot_blend", 0.05) * H
    gname = {g.index: g.name for g in obj.vertex_groups}
    for i, v in enumerate(obj.data.vertices):
        z = V[i, 2]
        if z >= zb or not len(v.groups):
            continue
        ws = {gname[g.group]: g.weight for g in v.groups}
        side = {sd: sum(w for n, w in ws.items() if n.startswith(f"Leg_{sd}_")) for sd in LEGS}
        sd = max(side, key=side.get)
        if side[sd] < 0.5:                                   # Rumpf/Schwanz, kein Fuß
            continue
        t = 1.0 if z <= za else (zb - z) / (zb - za)
        b = t * t * (3 - 2 * t)
        new = {n: w * (1 - b) for n, w in ws.items()}
        new[f"Leg_{sd}_4"] = new.get(f"Leg_{sd}_4", 0.0) + b
        for n in ws:
            obj.vertex_groups[n].remove([i])
        for n, w in new.items():
            if w > 1e-3:
                obj.vertex_groups[n].add([i], float(w), "REPLACE")
        n_sole += 1
    print(f"RIG_INFO Fußsohle starr am Fuß: {n_sole} Vertices (bis {CFG['foot_rigid_height']:.2f}·H, Übergang {CFG.get('foot_blend', 0.05):.2f}·H)")
report ={"vertices": int(len(V)), "parts": int(len(np.unique(part))), "height_m": round(float(H), 3),
          "length_m": round(float(L), 3), "bones": len(order), "arms": sorted(ARMS)}
RC.finish(obj, arm, OUT, "biped_raptor_rigged.blend", report, B, order, V,
          tracks={**{k: np.round(v["track"], 4).tolist() for k, v in LEGS.items()},
                  **{f"Arm_{k}": np.round(v, 4).tolist() for k, v in ARMS.items()}})
