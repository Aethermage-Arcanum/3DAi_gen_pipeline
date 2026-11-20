"""Skelett `winged`: Zweibeiner mit Flügeln – Wyvern/Drache (Muster drake), großer Vogel (Muster bird).

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/winged_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/winged_rigged.blend, rig_report.json, rig_debug.json

Standard-Skelett (Unity "Generic", 36 Knochen, immer vollständig – feste Namen für alle winged-Kreaturen):
  Root
  └ Pelvis → Spine_1 → Spine_2 → Chest
       Chest → Neck_1 → Neck_2 → Neck_3 → Head → Jaw          (Vogel: Jaw = Unterschnabel)
       Chest → Clavicle_{L,R} → UpperArm → Forearm → Hand → Finger_1 → Finger_2
                                (Drache: Finger = Flügelfinger bis zur Spitze · Vogel: Handschwingen/Federspitzen)
  Pelvis → Tail_1 … Tail_6                                      (Vogel: kurzer Steuerfeder-Fächer)
  Pelvis → Thigh_{L,R} → Shin → Foot → Toe                      (digitigrad: Foot = Lauf/Mittelfuß, Toe = Zehen)

Gelenke an der echten Geometrie (rigging/winged_detect.py). Flügel UND Schwanz folgen der Tripo-Form, auch wenn sie
schief/gebogen ist – die Clips geben die Haltung danach ABSOLUT vor (Lehre Eel Stalker). Die Ruhe-Ebene jedes Flügels
(Normale der Oberseite) steht als Eigenschaft `wing_normal_L/R` am Armature-Objekt, damit der Baukasten die Flügel in
eine symmetrische Soll-Pose drehen kann.
Gewichte: 1/Abstand mit Masken je Körperteil + Glätten über Kanten (weiche Übergänge, Flügelhaut verteilt die
Dehnung über die ganze Fläche statt an einer Naht), max. 4 Einflüsse, UV-Naht-Duplikate identisch. Lose Teile (Zähne,
Knochen-Schmuck) hängen je Vertex am nächsten Haupt-Mesh-Vertex.
"""
import pathlib
import sys
import tomllib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import double_sided  # noqa: E402
import rig_common as RC  # noqa: E402
import winged_detect as D  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CFG = tomllib.loads((HERE / "winged_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    own = tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("winged", {})
    for k, v in own.items():
        CFG[k] = {**CFG[k], **v} if isinstance(v, dict) and isinstance(CFG.get(k), dict) else v

obj, V, part, MAIN = RC.load_mesh(SRC)
T = np.array([[p.vertices[0], p.vertices[i], p.vertices[i + 1]] for p in obj.data.polygons
              for i in range(1, len(p.vertices) - 1)])
E = np.array([e.vertices[:] for e in obj.data.edges])
R = D.detect(V, T, E, part, MAIN, CFG)
G, H, main, y_mid = R["GROUND"], R["H"], R["main"], R["y_mid"]
zc = R["z_crotch"]
z = V[:, 2]
B = {}


def lerp(p, q, t):
    return np.asarray(p, float) + t * (np.asarray(q, float) - np.asarray(p, float))


# ------------------------------------------------------------------ Beine (digitigrad)
LEG = {}
for s in ("L", "R"):
    m = R["LEGS"][s]
    F = R["feet"][s]
    ball = np.array([*V[F, :2].mean(0), G + CFG["ball_height"] * H])
    front = V[F][np.argmax(V[F, 0])]
    tip = np.array([front[0], ball[1], G])
    step = CFG["cut_step"] * H
    tr = []
    for zz in np.arange(G + CFG["ball_height"] * H, zc, step):
        band = m & (z >= zz) & (z < zz + step)
        if band.sum() >= 3:
            tr.append(V[band].mean(0))
    tr = D.smooth_line(np.array(tr), 2)
    top = tr[-1]
    hip = np.array([top[0], top[1], zc + CFG["hip_up"] * H])
    # Ferse („Vogelknie“): am weitesten hinten liegender Punkt der Mittellinie (relativ zur Geraden Ballen → Hüfte)
    lo, hi = CFG["heel_window"]
    best, heel = -1e9, None
    for p in tr:
        f = (p[2] - ball[2]) / max(1e-9, hip[2] - ball[2])
        if lo <= f <= hi:
            xl = ball[0] + f * (hip[0] - ball[0])
            if xl - p[0] > best:
                best, heel = xl - p[0], p.copy()
    if heel is None or best < 0.01 * H:                     # gerades Bein: Ferse bei 40 % und leicht nach hinten
        heel = lerp(ball, hip, 0.4) - np.array([0.03 * H, 0, 0])
    knee = hip + np.array([CFG["knee_forward"] * H, 0, -CFG["knee_down"] * H])
    B[f"Thigh_{s}"] = (hip, knee, "Pelvis")
    B[f"Shin_{s}"] = (knee, heel, f"Thigh_{s}")
    B[f"Foot_{s}"] = (heel, ball, f"Shin_{s}")
    B[f"Toe_{s}"] = (ball, tip, f"Foot_{s}")
    LEG[s] = {"mask": m, "track": tr, "heel_back": round(float(best) / H, 3)}

# ------------------------------------------------------------------ Rumpf
pel, chest = R["pelvis"], R["chest"]
hips_c = (B["Thigh_L"][0] + B["Thigh_R"][0]) / 2
pel = np.array([hips_c[0], y_mid, hips_c[2]])
neck_line = R["neck_line"][::-1]                              # Hals-Ansatz (Ring-Ende) → Schnauze
root = np.array([pel[0], pel[1], G])
B["Root"] = (root, root + np.array([0, 0, 0.1 * H]), None)
B["Pelvis"] = (pel, lerp(pel, chest, 1 / 3), "Root")
B["Spine_1"] = (lerp(pel, chest, 1 / 3), lerp(pel, chest, 2 / 3), "Pelvis")
B["Spine_2"] = (lerp(pel, chest, 2 / 3), chest, "Spine_1")

# ------------------------------------------------------------------ Hals, Kopf, Kiefer
# Linie Brust → (Ring-Mittellinie, wo der Hals ein Schlauch ist) → Schnauze; dicke Hälse (Wyvern) werden gerade verbunden
nl = np.vstack([chest, neck_line, R["head_tip"]]) if len(neck_line) else np.vstack([chest, R["head_tip"]])
nl = D.smooth_line(D.resample(nl, 60), 3)
seg = np.linalg.norm(np.diff(nl, axis=0), axis=1)
sl = np.concatenate([[0], np.cumsum(seg)])
L_nh = sl[-1]
ic = int(np.searchsorted(sl, CFG["chest_share"] * L_nh))
ih = int(np.searchsorted(sl, (1 - CFG["head_share"]) * L_nh))
B["Chest"] = (chest, nl[ic], "Spine_2")
neck_pts = D.resample(nl[ic:ih + 1], 3)
head_base, head_tip = nl[ih], R["head_tip"]
B["Neck_1"] = (neck_pts[0], neck_pts[1], "Chest")
B["Neck_2"] = (neck_pts[1], neck_pts[2], "Neck_1")
B["Neck_3"] = (neck_pts[2], neck_pts[3], "Neck_2")
B["Head"] = (head_base, head_tip, "Neck_3")
hax = (head_tip - head_base) / np.linalg.norm(head_tip - head_base)
up = np.array([0, 0, 1.0]) - hax[2] * hax
up /= np.linalg.norm(up)
head_len = float(np.linalg.norm(head_tip - head_base))
# Kopf-Vertices: über die Oberfläche näher an der Schnauze als die Kopflänge (+ etwas), vor dem Kopfansatz
dh = R["dist_head"]
head_region = main & ~R["wing_any"] & (dh < 1.15 * (L_nh - sl[ih])) & (((V - head_base) @ hax) > -0.05 * H)
rel = V - head_base
t_ax = rel @ hax / head_len
depth = rel @ up                                             # + = über der Kopfachse
hinge_t = CFG["jaw_hinge"]
jaw_c = head_region & (t_ax > hinge_t) & (depth < -CFG["jaw_gap"] * H)
if jaw_c.sum() > 10:
    jlow = V[jaw_c]
    jt = jlow[np.argmax(jlow @ hax)]
    hinge = head_base + hinge_t * head_len * hax + float(np.median(depth[jaw_c])) * 0.6 * up
else:
    hinge = head_base + hinge_t * head_len * hax - 0.03 * H * up
    jt = head_tip - 0.03 * H * up
B["Jaw"] = (hinge, jt, "Head")

# ------------------------------------------------------------------ Schwanz
tl = R["tail_line"][::-1]                                     # Ansatz → Spitze
tl = np.vstack([tl, R["tail_tip"]]) if len(tl) else np.vstack([pel - np.array([0.1 * H, 0, 0]), R["tail_tip"]])
tpts = D.resample(tl, 6)
for i in range(6):
    B[f"Tail_{i + 1}"] = (tpts[i], tpts[i + 1], "Pelvis" if i == 0 else f"Tail_{i}")

# ------------------------------------------------------------------ Flügel
WING = {}
for s in ("L", "R"):
    W_ = R["WINGS"][s]
    S = W_["shoulder"]
    cl0 = lerp(chest, S, CFG["clavicle_in"])
    cl0[1] = lerp(np.array([y_mid]), np.array([S[1]]), CFG["clavicle_in"])[0]
    B[f"Clavicle_{s}"] = (cl0, S, "Chest")
    B[f"UpperArm_{s}"] = (S, W_["elbow"], f"Clavicle_{s}")
    B[f"Forearm_{s}"] = (W_["elbow"], W_["wrist"], f"UpperArm_{s}")
    B[f"Hand_{s}"] = (W_["wrist"], W_["k1"], f"Forearm_{s}")
    B[f"Finger_1_{s}"] = (W_["k1"], W_["k2"], f"Hand_{s}")
    B[f"Finger_2_{s}"] = (W_["k2"], W_["tip"], f"Finger_1_{s}")
    WING[s] = W_

WING_B = ("Clavicle", "UpperArm", "Forearm", "Hand", "Finger_1", "Finger_2")
LEG_B = ("Thigh", "Shin", "Foot", "Toe")
order = (["Root", "Pelvis", "Spine_1", "Spine_2", "Chest", "Neck_1", "Neck_2", "Neck_3", "Head", "Jaw"]
         + [f"Tail_{i}" for i in range(1, 7)]
         + [f"{b}_{s}" for s in ("L", "R") for b in WING_B]
         + [f"{b}_{s}" for s in ("L", "R") for b in LEG_B])
arm = RC.build_armature("Winged_Rig", B, order, H)
for s in ("L", "R"):
    arm[f"wing_normal_{s}"] = [float(x) for x in WING[s]["normal"]]
arm["y_mid"] = float(y_mid)
print("RIG_INFO Schritt %.2f H · Brust %.2f H · Kopf %.2f m lang · Schwanz %.2f m · Flügel-Spannweite %.2f m" % (
    (zc - G) / H, (chest[2] - G) / H, head_len, float(np.sum(np.linalg.norm(np.diff(tpts, axis=0), axis=1))),
    float(np.linalg.norm(WING["L"]["tip"] - WING["R"]["tip"]))))
for n in order:
    print(f"RIG_BONE {n:12} {np.round(B[n][0], 3).tolist()} → {np.round(B[n][1], 3).tolist()}")

# ------------------------------------------------------------------ Körperteile je Vertex (Masken)
names = order[1:]
J = {n: j for j, n in enumerate(names)}
trunk_bones = ["Pelvis", "Spine_1", "Spine_2", "Chest"]
neck_bones = ["Neck_1", "Neck_2", "Neck_3", "Head"]
tail_bones = [f"Tail_{i}" for i in range(1, 7)]
allow = np.zeros((len(V), len(names)), bool)
leg_any, wing_any = R["leg_any"], R["wing_any"]
core = main & ~wing_any & ~leg_any
# Rumpf, Hals, Kopf und Schwanz teilen sich den Kern: die Abstands-Gewichte entscheiden (Knochen liegen auf den echten
# Mittellinien), die Beine und Flügel haben eigene Masken. Schwanz-Knochen nie in der vorderen Körperhälfte.
front = (V[:, 0] > pel[0] + 0.5 * (chest[0] - pel[0])) & (V[:, 2] > zc)
# Hals/Kopf nur vor der Ebene durch die Brust (senkrecht zur Linie Brust → Kopf), sonst dreht der Hals den Oberkörper mit
nd = (head_base - chest) / np.linalg.norm(head_base - chest)
ahead = (V - chest) @ nd > -CFG["neck_blend"] * H
for n in trunk_bones:
    allow[:, J[n]] = core
for n in neck_bones:
    allow[:, J[n]] = core & ahead
for n in tail_bones:
    allow[:, J[n]] = core & ~front
for n in ("Pelvis", "Spine_1"):
    allow[:, J[n]] |= leg_any & (z > zc - CFG["leg_blend"] * H)
allow[:, J["Jaw"]] = False                                    # Kiefer: eigene Regel unten
for s, sg in (("L", 1), ("R", -1)):
    lm, wm = LEG[s]["mask"], R["WINGS"][s]["mask"]
    side = (V[:, 1] - y_mid) * sg > 0
    for b in LEG_B:
        allow[:, J[f"{b}_{s}"]] = lm
    allow[:, J[f"Thigh_{s}"]] |= core & side & (z < zc + CFG["leg_blend"] * H)
    sole = lm & (z < G + CFG["foot_rigid"] * H)
    allow[sole] = False
    allow[sole, J[f"Toe_{s}"]] = True
    # Sohle vor dem Ballen: Foot/Toe nach Abstand · hinter dem Ballen (Hinterzehe, Ferse am Boden): nur Toe – folgt dem
    # Boden-Ziel, sonst kippt die Hinterzehe mit dem Lauf in den Boden
    allow[sole & (V[:, 0] >= B[f"Foot_{s}"][1][0]), J[f"Foot_{s}"]] = True
    ball_, heel_ = B[f"Foot_{s}"][1], B[f"Foot_{s}"][0]
    hallux = lm & (V[:, 0] < ball_[0] - 0.02 * H) & (z < G + CFG["hallux_height"] * (heel_[2] - G))
    allow[hallux] = False
    allow[hallux, J[f"Toe_{s}"]] = True
    for b in WING_B[1:]:
        allow[:, J[f"{b}_{s}"]] = wm
    S = WING[s]["shoulder"]
    # Übergang Flügel ↔ Rumpf über die Oberfläche (Flughaut setzt am Rumpf an): beidseits der Grenze ein Band, in dem
    # Flügel- und Rumpfknochen erlaubt sind → das Glätten macht daraus einen Verlauf statt einer Naht (sonst reißt die
    # Haut an der Grenze, Lehre: Dehnung am Mesh/Gewicht lösen, nicht durch kleinere Bewegung)
    dW, _ = D.geodesic(V, R["Ew"], np.where(wm)[0], main)
    dB, _ = D.geodesic(V, R["Ew"], np.where(core & side)[0], main)
    band_b = core & side & (dW < CFG["wing_body_blend"] * H)
    band_w = wm & (dB < CFG["wing_body_blend"] * H)
    allow[:, J[f"UpperArm_{s}"]] |= band_b
    for n in ("Chest", "Spine_2", "Spine_1"):
        allow[:, J[n]] |= band_w
    near_sh = core & side & (np.linalg.norm(V - S, axis=1) < CFG["shoulder_radius"] * H)
    allow[:, J[f"UpperArm_{s}"]] |= near_sh
    allow[:, J[f"Clavicle_{s}"]] = near_sh | band_b | band_w | (wm & (np.linalg.norm(V - S, axis=1) < CFG["shoulder_radius"] * H))
    for n in ("Chest", "Spine_2"):
        allow[:, J[n]] |= wm & (np.linalg.norm(V - S, axis=1) < 0.5 * CFG["shoulder_radius"] * H)
nomask = ~allow.any(1)
for n in trunk_bones:
    allow[nomask & main, J[n]] = True
W = RC.skin(obj, V, part, MAIN, B, names, allow, CFG)

# ------------------------------------------------------------------ Kiefer: untere Kopfhälfte vor dem Scharnier
Ew = R["Ew"]
tt = np.clip((t_ax - hinge_t) / max(1e-6, CFG["jaw_hinge_blend"]), 0, 1)
dd = np.clip((-CFG["jaw_gap"] * H - depth) / max(1e-6, CFG["jaw_depth_blend"] * H), 0, 1)
bj = np.where(head_region, (tt * tt * (3 - 2 * tt)) * (dd * dd * (3 - 2 * dd)), 0.0)
for _ in range(CFG["jaw_smooth"]):
    acc, cnt = np.zeros(len(V)), np.zeros(len(V))
    np.add.at(acc, Ew[:, 0], bj[Ew[:, 1]])
    np.add.at(acc, Ew[:, 1], bj[Ew[:, 0]])
    np.add.at(cnt, Ew[:, 0], 1)
    np.add.at(cnt, Ew[:, 1], 1)
    bj = np.where(head_region, 0.5 * bj + 0.5 * acc / np.maximum(cnt, 1), 0.0)
W = W * (1 - bj)[:, None]
W[:, J["Jaw"]] += bj
print(f"RIG_INFO Kiefer: {int((bj > 0.5).sum())} Vertices überwiegend am Jaw")

# ------------------------------------------------------------------ lose Teile (Zähne, Knochen-Schmuck): je Vertex am nächsten Haupt-Vertex
others = [p for p in np.unique(part) if p != MAIN]
mi = np.where(main)[0]
for p in others:
    pm = np.where(part == p)[0]
    d = np.linalg.norm(V[pm][:, None, :] - V[mi][None, :, :], axis=2)
    W[pm] = W[mi[d.argmin(1)]]
if others:
    print(f"RIG_INFO lose Teile je Vertex am nächsten Haupt-Vertex: {len(others)}")

# ------------------------------------------------------------------ UV-Naht-Duplikate identisch, max. 4 Einflüsse, schreiben
grp = {}
for i, w in enumerate(R["wid"]):
    grp.setdefault(w, []).append(i)
for g in grp.values():
    if len(g) > 1:
        W[g] = W[g].mean(0)
top4 = np.argsort(-W, 1)[:, :4]
for vg in list(obj.vertex_groups):
    obj.vertex_groups.remove(vg)
for n in names:
    obj.vertex_groups.new(name=n)
for i in range(len(V)):
    ws = W[i, top4[i]]
    ws = ws / ws.sum()
    for j, w in zip(top4[i], ws):
        if w > 1e-3:
            obj.vertex_groups[names[j]].add([i], float(w), "REPLACE")
used = {n: float(W[:, J[n]].sum()) for n in names}
placeholders = [n for n in names if used[n] < 1.0]
print("RIG_INFO Platzhalter ohne (nennenswertes) Gewicht:", placeholders)

report = {"vertices": int(len(V)), "parts": int(len(np.unique(part))), "height_m": round(float(H), 3),
          "bones": len(order), "placeholders": placeholders,
          "landmarks_rel_height": {"crotch": round((zc - G) / H, 3), "chest": round((chest[2] - G) / H, 3),
                                   "shoulder_L": round((WING["L"]["shoulder"][2] - G) / H, 3),
                                   "shoulder_R": round((WING["R"]["shoulder"][2] - G) / H, 3)},
          "wing_span_m": round(float(np.linalg.norm(WING["L"]["tip"] - WING["R"]["tip"])), 3),
          "wing_rest_normal": {s: np.round(WING[s]["normal"], 3).tolist() for s in ("L", "R")},
          "wing_vertices": {s: int(R["WINGS"][s]["mask"].sum()) for s in ("L", "R")},
          "jaw_vertices": int((bj > 0.5).sum()), "heel_back_rel": {s: LEG[s]["heel_back"] for s in ("L", "R")}}
if CFG["double_sided"]["enabled"]:
    report["double_sided"] = double_sided.apply(obj, H, CFG["double_sided"])
RC.finish(obj, arm, OUT, "winged_rigged.blend", report, B, order, V,
          tracks={**{f"Leg_{k}": np.round(v["track"], 4).tolist() for k, v in LEG.items()},
                  **{f"Wing_{k}": np.round(np.vstack([R["WINGS"][k]["arm_path"], R["WINGS"][k]["fin_path"]]), 4).tolist()
                     for k in ("L", "R")},
                  "Neck": np.round(nl, 4).tolist(), "Tail": np.round(tl, 4).tolist()})
