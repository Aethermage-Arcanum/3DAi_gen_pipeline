"""Skelett `upright`: aufrechter Zweibeiner mit langen, schweren Armen (Treant, später Golem und Brute/Flesh Titan).

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/upright_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/upright_rigged.blend, rig_report.json, rig_debug.json

Standard-Skelett (Unity "Generic", 27 Knochen, immer vollständig – feste Namen für alle upright-Kreaturen):
  Root
  └ Pelvis → Spine_1 → Spine_2 → Spine_3 → Chest
       Chest → Neck → Head          (Golem/Brute: eigener Kopf · Treant: Gesicht sitzt im Stamm → Platzhalter ohne Gewicht)
       Chest → Crown                (Treant: Astkrone, starr · Golem: Kristalle/Aufbau · sonst Platzhalter)
       Chest → Clavicle_{L,R} → UpperArm → Forearm → Hand → Fingers
  Pelvis → Thigh_{L,R} → Shin → Foot → Toe
„Fake it“: Fehlt ein Teil (Kopf, Krone), bleibt der Knochen als Platzhalter ohne Gewicht – die Clips eines Musters
laufen trotzdem auf allen Kreaturen dieses Skeletts.

Gelenke an der echten Geometrie (rigging/upright_detect.py): Schritt, Achseln, Krone über waagerechte Schnitte;
Knie = Engstelle, Knöchel = Beginn der Wurzel-/Zehenspreizung, Ellbogen = stärkste Biegung, Handgelenk = Beginn der
Hand, Fingeransatz = wo die Finger getrennt werden. Gewichte: 1/Abstand mit Masken je Körperteil + Glätten über
Kanten (weiche Manschetten), max. 4 Einflüsse, UV-Naht-Duplikate identisch. Krone/Äste starr an Crown,
lose Teile (Moos, Pilze) hängen starr an ihrer Ansatzstelle (Schwingen macht der Baustein [dangling], ohne Knochen).
"""
import pathlib
import sys
import tomllib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import double_sided  # noqa: E402
import rig_common as RC  # noqa: E402
import upright_detect as D  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CFG = tomllib.loads((HERE / "upright_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    own = tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("upright", {})
    for k, v in own.items():
        CFG[k] = {**CFG[k], **v} if isinstance(v, dict) and isinstance(CFG.get(k), dict) else v

obj, V, part, MAIN = RC.load_mesh(SRC)
T = np.array([[p.vertices[0], p.vertices[i], p.vertices[i + 1]] for p in obj.data.polygons
              for i in range(1, len(p.vertices) - 1)])
R = D.detect(V, T, part, MAIN, CFG)
GROUND, H, main = R["GROUND"], R["H"], R["main"]
zc, za, zk = R["z_crotch"], R["z_armpit"], R["z_crown"]
step = CFG["cut_step"] * H
if len(R["ARMS"]) < 2:
    raise SystemExit(f"upright_rig: nur Arme {sorted(R['ARMS'])} gefunden")
trunk = R["trunk"]


def trunk_at(z):
    """Rumpf-Mitte auf Höhe z (geglättet, zwischen den Schnitten interpoliert)."""
    tr = D.smooth_track(trunk[:, :4], 2)
    return np.array([np.interp(z, tr[:, 2], tr[:, 0]), np.interp(z, tr[:, 2], tr[:, 1]), z])


def trunk_r(z):
    return float(np.interp(z, trunk[:, 2], D.smooth_track(trunk[:, :4], 2)[:, 3]))


B = {}
# ------------------------------------------------------------------ Beine
LEG = {}
for s, L_ in R["LEGS"].items():
    m = L_["mask"]
    tr = D.smooth_track(D.track(V, T, m, GROUND + 0.5 * step, zc - 0.5 * step, step), 1)
    typ = float(np.median(tr[len(tr) // 3:, 3]))                       # typische Beindicke (ohne Fuß)
    ia = next((i for i in range(len(tr)) if tr[i, 3] < CFG["ankle_ratio"] * typ), len(tr) // 4)
    ankle = tr[ia, :3].copy()
    top = tr[max(0, len(tr) - 3), :3].copy()                          # knapp unter dem Schritt (letzte Schnitte rauschen)
    hip = np.array([top[0], top[1], zc + CFG["hip_up"] * H])
    lo, hi = CFG["knee_window"]
    seg = [i for i in range(ia, len(tr)) if lo <= (tr[i, 2] - ankle[2]) / max(1e-9, hip[2] - ankle[2]) <= hi]
    rr = D.smooth_track(tr, 3)[:, 3]
    if seg and (rr[seg].max() - rr[seg].min()) / rr[seg].min() >= CFG["knee_flat"]:
        ik = min(seg, key=lambda i: rr[i])                            # deutliche Engstelle
    else:                                                             # Bein überall gleich dick (Baumstumpf): Mitte
        zt = ankle[2] + CFG["knee_mid"] * (hip[2] - ankle[2])
        ik = int(np.argmin(np.abs(tr[:, 2] - zt)))
    knee = tr[ik, :3].copy()
    t = (knee[2] - ankle[2]) / max(1e-9, hip[2] - ankle[2])
    line_x = ankle[0] + t * (hip[0] - ankle[0])
    knee[0] = max(knee[0], line_x + CFG["knee_forward"] * H)          # Knie zeigt nach vorn (IK-Biegerichtung)
    fv = V[m & (V[:, 2] < GROUND + CFG["foot_rigid"] * H)]
    fc = fv[:, :2].mean(0)
    front = fv[fv[:, 0].argmax()]
    ball = np.array([fc[0] + CFG["ball_forward"] * (front[0] - fc[0]), fc[1], GROUND + CFG["ball_height"] * H])
    tip = np.array([front[0], ball[1], GROUND])
    B[f"Thigh_{s}"] = (hip, knee, "Pelvis")
    B[f"Shin_{s}"] = (knee, ankle, f"Thigh_{s}")
    B[f"Foot_{s}"] = (ankle, ball, f"Shin_{s}")
    B[f"Toe_{s}"] = (ball, tip, f"Foot_{s}")
    LEG[s] = {"track": tr, "mask": m, "hip": hip, "ankle": ankle, "knee": knee}

# ------------------------------------------------------------------ Rumpf, Kopf (Platzhalter), Krone
hips_c = (LEG["L"]["hip"] + LEG["R"]["hip"]) / 2
p0 = np.array([hips_c[0], hips_c[1], zc])
lv = [zc + f * (za - zc) for f in (0.25, 0.5, 0.75, 1.0)]
pts = [p0] + [trunk_at(z) for z in lv]
z_top_trunk = zk if zk is not None else R["z_top"] - 0.1 * H
# Oberkante Brust: Höhe der Krone, seitlich die mittlere Rumpf-Mitte zwischen Achsel und Krone (an der Kronen-Basis
# zieht die erste Astgabel den Schnitt-Schwerpunkt zur Seite)
up_tr = trunk[(trunk[:, 2] >= za) & (trunk[:, 2] <= z_top_trunk - 0.04 * H)]
chest_top = np.array([*(up_tr[:, :2].mean(0) if len(up_tr) else trunk_at(z_top_trunk)[:2]), z_top_trunk])
root = np.array([p0[0], p0[1], GROUND])
B["Root"] = (root, root + np.array([0, 0, 0.1 * H]), None)
B["Pelvis"] = (pts[0], pts[1], "Root")
B["Spine_1"] = (pts[1], pts[2], "Pelvis")
B["Spine_2"] = (pts[2], pts[3], "Spine_1")
B["Spine_3"] = (pts[3], pts[4], "Spine_2")
B["Chest"] = (pts[4], chest_top, "Spine_3")
# Treant: kein eigener Kopf – Neck/Head als Platzhalter oben im Stamm (Head zeigt nach vorn = Blickrichtung)
B["Neck"] = (chest_top, chest_top + np.array([0, 0, 0.05 * H]), "Chest")
B["Head"] = (chest_top + np.array([0, 0, 0.05 * H]), chest_top + np.array([0.12 * H, 0, 0.05 * H]), "Neck")
# Crown senkrecht von der Kronen-Basis bis zur Höhe des höchsten Punkts (eine schräge Achse zur zufälligen Astspitze
# würde u. a. die Höhen-Regel von [dangling] verfälschen: Astspitzen gälten als „unterhalb“ und würden schwingen)
B["Crown"] = (chest_top, np.array([chest_top[0], chest_top[1], R["z_top"] if zk is not None else chest_top[2] + 0.1 * H]),
              "Chest")

# ------------------------------------------------------------------ Arme
ARM = {}
for s, A in R["ARMS"].items():
    m = A["mask"]
    sg = 1 if s == "L" else -1
    tr = D.smooth_track(D.track(V, T, m, A["armpit"] - 0.5 * step, A["tip"][2] + 0.5 * step, step), 1)
    # tr läuft von oben (Achsel) nach unten (Fingerspitzen)
    # Handgelenk: von unten aufwärts, wo der Arm schmaler als wrist_ratio × Handbreite wird
    hand_w = float(tr[len(tr) // 2:, 3].max())
    iw = next((i for i in range(len(tr) - 1, -1, -1) if tr[i, 3] < CFG["wrist_ratio"] * hand_w
               and i < int(np.argmax(tr[:, 3]))), len(tr) // 2)
    wrist = tr[iw, :3].copy()
    # Fingeransatz: höchster Schnitt unterhalb des Handgelenks mit ≥ knuckle_min_fingers getrennten Fingern
    Tm = T[m[T].all(1)]
    knuck = None
    for z in np.arange(wrist[2] - step, A["tip"][2], -step):
        cs = [c for c in D.slice_contours(V, Tm, z, R["wid"]) if len(c) >= 8]   # Splitter (Rinde, Moos) zählen nicht
        if len(cs) >= CFG["knuckle_min_fingers"]:
            knuck = np.array([*np.vstack(cs)[:, :2].mean(0), z])
            break
    if knuck is None:
        knuck = (wrist + A["tip"]) / 2
    lowest = V[m & (V[:, 2] < A["tip"][2] + 0.03 * H)]
    ftip = np.array([*lowest[:, :2].mean(0), A["tip"][2]])
    # Schulter: über der Achsel, seitlich wie die Arm-Mitte knapp unter der Achsel
    t2 = tr[min(1, len(tr) - 1)]
    zs = A["armpit"] + CFG["shoulder_up"] * H
    tc = trunk_at(zs)
    sh = np.array([t2[0], tc[1] + CFG["shoulder_in"] * (t2[1] - tc[1]), zs])
    seg = np.array([r for r in tr if r[2] >= wrist[2]])
    pathp = np.vstack([sh[None, :], seg[:, :3]])
    lo, hi = CFG["elbow_window"]
    ie, _ = D.bend_point(np.column_stack([pathp, np.zeros(len(pathp))]), lo, hi)
    elbow = pathp[ie if ie is not None else len(pathp) // 2].copy()
    cl0 = tc + CFG["clavicle_in"] * (sh - tc)
    B[f"Clavicle_{s}"] = (cl0, sh, "Chest")
    B[f"UpperArm_{s}"] = (sh, elbow, f"Clavicle_{s}")
    B[f"Forearm_{s}"] = (elbow, wrist, f"UpperArm_{s}")
    B[f"Hand_{s}"] = (wrist, knuck, f"Forearm_{s}")
    B[f"Fingers_{s}"] = (knuck, ftip, f"Hand_{s}")
    ARM[s] = {"track": tr, "mask": m, "armpit": A["armpit"]}

order = (["Root", "Pelvis", "Spine_1", "Spine_2", "Spine_3", "Chest", "Neck", "Head", "Crown"]
         + [f"{b}_{s}" for s in ("L", "R") for b in ("Clavicle", "UpperArm", "Forearm", "Hand", "Fingers")]
         + [f"{b}_{s}" for s in ("L", "R") for b in ("Thigh", "Shin", "Foot", "Toe")])
arm = RC.build_armature("Upright_Rig", B, order, H)
print("RIG_INFO Gelenke (Höhe über Boden, Anteil H): Schritt %.2f · Achsel %.2f · Krone %s" % (
    (zc - GROUND) / H, (za - GROUND) / H, "–" if zk is None else f"{(zk - GROUND) / H:.2f}"))
for n in order:
    print(f"RIG_BONE {n:12} {np.round(B[n][0], 3).tolist()} → {np.round(B[n][1], 3).tolist()}")

# ------------------------------------------------------------------ Körperteile je Vertex
names = order[1:]
J = {n: j for j, n in enumerate(names)}
trunk_bones = ["Pelvis", "Spine_1", "Spine_2", "Spine_3", "Chest"]
allow = np.zeros((len(V), len(names)), bool)
leg_any = np.zeros(len(V), bool)
arm_any = np.zeros(len(V), bool)
for s in ("L", "R"):
    leg_any |= LEG[s]["mask"]
    arm_any |= ARM[s]["mask"]
body = main & ~leg_any & ~arm_any
# Krone: Rumpf-Vertices, die über das Mesh näher an der Krone als am Rumpf-Kern liegen (Äste + daran hängende Strähnen)
crown_lab = np.zeros(len(V), bool)
if zk is not None:
    core = body & (V[:, 2] > zc) & (V[:, 2] < zk - CFG["crown_blend"] * H)
    core &= np.array([np.linalg.norm(V[i, :2] - trunk_at(V[i, 2])[:2]) < trunk_r(V[i, 2]) for i in range(len(V))])
    top = body & (V[:, 2] > zk + CFG["crown_blend"] * H)
    dc = D.geodesic(V, R["E"], top, R["wid"])
    dk = D.geodesic(V, R["E"], core, R["wid"])
    crown_lab = body & (dc < dk)
for j, n in enumerate(names):
    if n in trunk_bones:
        allow[:, j] = body | (arm_any & (V[:, 2] > za - CFG["arm_blend"] * H)) | \
            (leg_any & (V[:, 2] > zc - CFG["leg_blend"] * H))
for s in ("L", "R"):
    sg = 1 if s == "L" else -1
    lm, am = LEG[s]["mask"], ARM[s]["mask"]
    side = (V[:, 1] - R["y_mid"]) * sg > 0
    for b in ("Thigh", "Shin", "Foot", "Toe"):
        allow[:, J[f"{b}_{s}"]] = lm
    allow[:, J[f"Thigh_{s}"]] |= body & side & (V[:, 2] < zc + CFG["leg_blend"] * H)
    sole = lm & (V[:, 2] < GROUND + CFG["foot_rigid"] * H)          # Fußsohle nur Fuß/Zehen
    allow[sole] = False
    allow[sole, J[f"Foot_{s}"]] = allow[sole, J[f"Toe_{s}"]] = True
    for b in ("UpperArm", "Forearm", "Hand", "Fingers"):
        allow[:, J[f"{b}_{s}"]] = am
    # Schulter: Rumpf-Vertices um das Schultergelenk und oben auf dem Oberarm (über der Achsel, außerhalb des Rumpfs)
    shp = B[f"UpperArm_{s}"][0]
    near_sh = body & side & ~crown_lab & (np.linalg.norm(V - shp, axis=1) < CFG["shoulder_radius"] * H)
    outer = body & side & ~crown_lab & ((V[:, 1] - R["y_mid"]) * sg > (shp[1] - R["y_mid"]) * sg - 0.02 * H) &         (V[:, 2] < shp[2] + CFG["shoulder_radius"] * H)
    allow[:, J[f"UpperArm_{s}"]] |= near_sh | outer
    allow[:, J[f"Clavicle_{s}"]] = near_sh | outer | (am & (V[:, 2] > za - CFG["arm_blend"] * H))
nomask = ~allow.any(1)
allow[nomask & main] = False
for n in trunk_bones:
    allow[nomask & main, J[n]] = True
W = RC.skin(obj, V, part, MAIN, B, names, allow, CFG)

# ------------------------------------------------------------------ Krone starr: Äste/Strähnen 100 % Crown, weicher Übergang am Stamm
if zk is not None:
    zz = V[:, 2]
    tt = np.clip((zz - (zk - CFG["crown_blend"] * H)) / (2 * CFG["crown_blend"] * H), 0, 1)
    b = tt * tt * (3 - 2 * tt)
    inside = np.array([np.linalg.norm(V[i, :2] - trunk_at(V[i, 2])[:2]) < CFG["crown_core"] * trunk_r(V[i, 2])
                       for i in range(len(V))])
    b = np.where(crown_lab & ~inside, 1.0, np.where(body, b, 0.0))
    # Übergang glätten (über Mesh-Kanten): Strähnen/Äste, die direkt am Stamm ansetzen, sonst harte Kante → Riss.
    # Fest bleiben: Krone oberhalb des Übergangs (1) und alles außerhalb des Rumpfs (Arme, Beine: 0).
    Eb = R["E"]
    fixed = ~body | (zz > zk + CFG["crown_blend"] * H)
    for _ in range(CFG["crown_smooth"]):
        acc, cnt = np.zeros(len(V)), np.zeros(len(V))
        np.add.at(acc, Eb[:, 0], b[Eb[:, 1]])
        np.add.at(acc, Eb[:, 1], b[Eb[:, 0]])
        np.add.at(cnt, Eb[:, 0], 1)
        np.add.at(cnt, Eb[:, 1], 1)
        b = np.where(fixed | (cnt == 0), b, 0.5 * b + 0.5 * acc / np.maximum(cnt, 1))
    W = W * (1 - b)[:, None]
    W[:, J["Crown"]] += b
    print(f"RIG_INFO Krone starr: {int((b > 0.999).sum())} Vertices ganz an Crown, {int(((b > 0) & (b < 0.999)).sum())} im Übergang")

# ------------------------------------------------------------------ lose Teile (Moos-Strähnen, Pilze): starr an der Ansatzstelle
others = [p for p in np.unique(part) if p != MAIN]
mi = np.where(main)[0]
for p in others:
    pm = np.where(part == p)[0]
    d = np.linalg.norm(V[pm][:, None, :] - V[mi][None, :, :], axis=2)
    near = d.argmin(1)
    dmin = d.min(1)
    att = dmin < max(CFG["part_attach"] * H, dmin.min() * 1.5)
    W[pm] = W[mi[near[att]]].mean(0)
if others:
    print(f"RIG_INFO lose Teile starr an ihrer Ansatzstelle: {len(others)}")

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
          "landmarks_rel_height": {"crotch": round((zc - GROUND) / H, 3), "armpit": round((za - GROUND) / H, 3),
                                   "crown": None if zk is None else round((zk - GROUND) / H, 3)},
          "crown_vertices": int((W[:, J["Crown"]] > 0.999).sum())}
if CFG["double_sided"]["enabled"]:
    report["double_sided"] = double_sided.apply(obj, H, CFG["double_sided"])
RC.finish(obj, arm, OUT, "upright_rigged.blend", report, B, order, V,
          tracks={**{f"Leg_{k}": np.round(v["track"][:, :3], 4).tolist() for k, v in LEG.items()},
                  **{f"Arm_{k}": np.round(v["track"][:, :3], 4).tolist() for k, v in ARM.items()}})
