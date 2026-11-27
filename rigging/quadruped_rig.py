"""Vierbeiner-Standard-Rig: Anatomie aus dem Mesh erkennen, Skelett bauen, Gewichte setzen.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/quadruped_rig.py -- <model.glb> <ausgabeordner> [<creature.toml>]
Ergebnis: <ausgabe>/quadruped_rigged.blend, rig_report.json, rig_debug.json (für rigging/draw_rig.py)

Annahmen (wie bei allen Tripo-Modellen hier): Kopf zeigt nach +X, Z ist oben, Füße stehen am Boden.
Skelett (Unity "Generic", gleiche Namen für alle Vierbeiner):
  Root · Hips → Spine_1 → Chest → Neck_1 → Neck_2 → Head → Jaw · Hips → Tail_1..4
  Leg_<FL|FR|BL|BR>_1..4: vorne Oberarm, Unterarm, Mittelhand, Zehen · hinten Oberschenkel, Schienbein,
  Mittelfuß (Sprunggelenk → Ballen), Zehen
"""
import json
import pathlib
import sys
import tomllib

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(args[0]).resolve(), pathlib.Path(args[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)


def load_cfg():
    cfg = tomllib.loads((HERE / "quadruped_defaults.toml").read_text(encoding="utf-8"))
    if len(args) > 2:
        over = tomllib.loads(pathlib.Path(args[2]).read_text(encoding="utf-8")).get("quadruped", {})
        for k, v in over.items():
            cfg[k] = {**cfg.get(k, {}), **v} if isinstance(v, dict) else v
    return cfg


CFG = load_cfg()
D, RIG = CFG["detect"], CFG["rig"]

# ------------------------------------------------------------------ Mesh laden
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SRC))
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in bpy.data.objects:
    o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
body = bpy.context.active_object
body.name = "Body_Mesh"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = body.data
V = np.array([v.co[:] for v in me.vertices])
N = len(V)

# Teile (zusammenhängende Geometrie, Vertices per Position verschweißt)
parent = np.arange(N)


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


key = {}
for i, co in enumerate(np.round(V, 5)):
    j = key.setdefault(tuple(co), i)
    if j != i:
        parent[find(i)] = find(j)
for e in me.edges:
    a_, b_ = find(e.vertices[0]), find(e.vertices[1])
    parent[a_] = b_
part = np.array([find(i) for i in range(N)])
ids, counts = np.unique(part, return_counts=True)
MAIN = ids[np.argmax(counts)]
main = part == MAIN
M = V[main]
GROUND = V[:, 2].min()
H = M[:, 2].max() - GROUND
L = M[:, 0].max() - M[:, 0].min()
Y_MID = float(np.median(M[:, 1]))
print(f"RIG_INFO Teile {len(ids)}, Hauptteil {main.sum()}/{N} Vertices, Höhe {H:.3f}, Länge {L:.3f}")


# ------------------------------------------------------------------ Füße + Beine
def detect_feet():
    foot_band = M[M[:, 2] < GROUND + D["foot_band"] * H]
    cx = np.array([foot_band[:, 0].min(), foot_band[:, 0].max()])
    for _ in range(20):                                   # 1D-k-means: vorne/hinten
        lab = np.abs(foot_band[:, 0:1] - cx[None]).argmin(1)
        cx = np.array([foot_band[lab == k, 0].mean() for k in (0, 1)])
    feet = {}
    for k, fb in ((1, "F"), (0, "B")):
        for side, sn in ((1, "L"), (-1, "R")):
            sel = foot_band[(lab == k) & ((foot_band[:, 1] - Y_MID) * side > 0)]
            if len(sel) < 3:
                raise SystemExit(f"Fuß {fb}{sn} nicht gefunden")
            feet[f"{fb}{sn}"] = sel
    return feet, cx


FEET, CX = detect_feet()

# Tripo setzt die Hinterbeine manchmal viel breiter als die Vorderbeine (Hollow Stag: 2,4×). Mesh-Korrektur:
# Hinterbeine unterhalb der Bauchlinie zur Mitte schieben, linear zunehmend bis zum Huf (Oberschenkel bleibt).
# narrow_hind_legs = Anteil der Breiten-Differenz, der ausgeglichen wird (1 = Hinterhufe so breit wie vorne).
if RIG.get("narrow_hind_legs", 0):
    off = lambda k: float(np.abs(FEET[k][:, 1] - Y_MID).mean())  # noqa: E731
    front_w, back_w = (off("FL") + off("FR")) / 2, (off("BL") + off("BR")) / 2
    delta = RIG["narrow_hind_legs"] * max(0.0, back_w - front_w)
    x_split = CX.mean()
    hind_x = (FEET["BL"][:, 0].mean() + FEET["BR"][:, 0].mean()) / 2
    s = M[(np.abs(M[:, 0] - hind_x) < D["slice"] * L) & (np.abs(M[:, 1] - Y_MID) < 0.5 * front_w)]
    z_b = float(np.percentile(s[s[:, 2] > GROUND + D["min_belly"] * H][:, 2], 5))   # Bauchlinie über den Hinterbeinen
    sel = (V[:, 0] < x_split) & (V[:, 2] < z_b)
    w = np.clip((z_b - V[:, 2]) / max(1e-6, z_b - GROUND), 0, 1)
    V[sel, 1] -= np.sign(V[sel, 1] - Y_MID) * delta * w[sel]
    for i in np.where(sel)[0]:
        me.vertices[i].co.y = V[i, 1]
    me.update()
    M = V[main]
    FEET, CX = detect_feet()
    print(f"RIG_INFO Hinterbeine schmaler: Hufe {back_w:.3f} → {back_w - delta:.3f} (vorne {front_w:.3f}), "
          f"{int(sel.sum())} Vertices unter der Bauchlinie {z_b - GROUND:.3f}")


def midline_profile(x, half_width):
    """Bauch-/Rückenhöhe des Hauptteils bei x (schmaler Streifen um die Mittellinie)."""
    s = M[(np.abs(M[:, 0] - x) < D["slice"] * L) & (np.abs(M[:, 1] - Y_MID) < half_width)]
    s = s[s[:, 2] > GROUND + D["min_belly"] * H]
    if len(s) < 3:
        return None
    return float(np.percentile(s[:, 2], 5)), float(np.percentile(s[:, 2], 97))


LEGS = {}
for name, fv in FEET.items():
    side = 1 if name[1] == "L" else -1
    c = fv[:, :2].mean(0)
    pts = [np.array([c[0], c[1], GROUND])]
    hw = D["mid_half_width"] * H
    if RIG.get("adaptive_belly_strip", False):        # eng stehende Beine (Hirsch) liegen sonst IM Bauch-Streifen
        hw = min(hw, 0.5 * abs(c[1] - Y_MID))           # → Beine würden als Bauch gelesen, Gelenke viel zu tief
    belly = midline_profile(c[0], hw)
    z_top = belly[0] if belly else GROUND + 0.55 * H
    z = GROUND + D["track_step"] * H
    while z < z_top:
        band = M[(np.abs(M[:, 2] - z) < D["track_step"] * H)
                 & (np.linalg.norm(M[:, :2] - c, axis=1) < D["leg_radius"] * H)
                 & ((M[:, 1] - Y_MID) * side > -0.02 * H)]
        if len(band) >= 3:
            c = band[:, :2].mean(0)
        pts.append(np.array([c[0], c[1], z]))
        z += D["track_step"] * H
    back = midline_profile(pts[-1][0], D["mid_half_width"] * H)
    top_z = back[1] if back else z_top + 0.2 * H
    joint = np.array([pts[-1][0], Y_MID + RIG["joint_inset"] * (pts[-1][1] - Y_MID),
                      z_top + RIG["joint_depth"] * (top_z - z_top)])
    LEGS[name] = {"track": np.array(pts), "belly": z_top, "back": top_z, "joint": joint, "foot": fv}


def bend(track, lo, hi, sign):
    """Punkt im Höhenbereich [lo, hi] (Anteil) mit größter Abweichung in X (sign +1 = nach vorne)."""
    z0, z1 = track[0, 2], track[-1, 2]
    p0, p1 = track[0], track[-1]
    best, bi = -1e9, None
    for i, p in enumerate(track):
        f = (p[2] - z0) / max(1e-9, z1 - z0)
        if lo <= f <= hi:
            t = (p[2] - p0[2]) / max(1e-9, p1[2] - p0[2])
            dev = sign * (p[0] - (p0[0] + t * (p1[0] - p0[0])))
            if dev > best:
                best, bi = dev, i
    return track[bi] if bi is not None else None


BONES = {}                                             # Name → (Kopf, Schwanz, Eltern)
for name, lg in LEGS.items():
    tr, fv = lg["track"], lg["foot"]
    tip = fv[fv[:, 0].argmax()].copy()
    tip[2] = GROUND
    ball = np.array([*fv[:, :2].mean(0), GROUND + D["ball_height"] * H])
    h = lambda f: tr[min(len(tr) - 1, int(round(f * (len(tr) - 1))))]  # noqa: E731
    if name[0] == "F":                                 # vorne: fast gerade, Ellbogen hinten
        wrist = h(RIG["front_wrist"])
        elbow = bend(tr, 0.5, 0.95, -1)
        elbow = elbow if elbow is not None else h(RIG["front_elbow"])
    else:                                              # hinten: Sprunggelenk hinten, Knie vorne
        wrist = bend(tr, 0.15, 0.45, -1)
        wrist = wrist if wrist is not None else h(RIG["back_hock"])
        elbow = bend(tr, 0.5, 0.95, 1)
        elbow = elbow if elbow is not None else h(RIG["back_knee"])
        # knee_out (optional, Shellback 2026-11-23): Knie seitlich nach außen (Anteil H). Gespreizte Schildkröten-Hinterbeine
        # sind als gerade Säule modelliert → Kette in Ruhe fast gestreckt (0,96–0,98), jede Rumpfbewegung zwang den Rumpf
        # nach unten. Mit dem Knie außen beugt die IK seitlich (Knie nach außen, wie beim echten Tier). Ohne Wert wie bisher.
        if RIG.get("knee_out", 0):
            elbow = elbow + np.array([0, (1 if name[1] == "L" else -1) * RIG["knee_out"] * H, 0])
    par = f"Shoulder_{name}" if name[0] == "F" else "Hips"
    if name[0] == "F":                                 # Schulterblatt: Widerrist-Seite → Schultergelenk
        top = np.array([lg["joint"][0] - RIG["scapula_back"] * L, Y_MID + 0.7 * (lg["joint"][1] - Y_MID),
                        lg["joint"][2] + RIG["scapula_height"] * (lg["back"] - lg["joint"][2])])
        BONES[f"Shoulder_{name}"] = (top, lg["joint"], "Chest")
    BONES[f"Leg_{name}_1"] = (lg["joint"], elbow, par)
    BONES[f"Leg_{name}_2"] = (elbow, wrist, f"Leg_{name}_1")
    BONES[f"Leg_{name}_3"] = (wrist, ball, f"Leg_{name}_2")
    BONES[f"Leg_{name}_4"] = (ball, tip, f"Leg_{name}_3")


# ------------------------------------------------------------------ Wirbelsäule, Hals, Kopf, Schwanz
def center_at(x, region=None, sl=None):
    s = M[np.abs(M[:, 0] - x) < (sl or D["slice"]) * L]
    if region == "body":
        s = s[s[:, 2] > max(LEGS["FL"]["belly"], LEGS["BL"]["belly"]) - 0.1 * H]
    if len(s) < 3:
        return None
    mid = s[np.abs(s[:, 1] - Y_MID) < D["mid_half_width"] * H]
    zz = mid[:, 2] if len(mid) >= 3 else s[:, 2]
    return np.array([x, Y_MID, (np.percentile(zz, 8) + np.percentile(zz, RIG.get("spine_top_pct", 92))) / 2])  # Rückenkamm ignorieren


x_hip = (LEGS["BL"]["joint"][0] + LEGS["BR"]["joint"][0]) / 2
x_sh = (LEGS["FL"]["joint"][0] + LEGS["FR"]["joint"][0]) / 2
x_nose, x_tail = M[:, 0].max(), M[:, 0].min()
# spine_slice (optional, Rimehide Bear 2026-11-21): dickere Querschnitte nur für Wirbelsäule + Hals. Grobes Low-Poly mit
# wenigen Vertices auf dem Rücken: im 3-cm-Schnitt fehlen Rücken-Vertices → Mitte fällt auf Bauchhöhe (Zickzack).
# Schwanz/Kopf/Beine bleiben beim normalen `slice`. Ohne den Wert alles wie bisher.
SSL = D.get("spine_slice")
x_hb = x_nose - RIG["head_length"] * (x_nose - x_sh)
# chest_extend (optional, Rimehide Bear 2026-11-21): Brust endet / Hals beginnt erst so weit (Anteil Schulter → Kopfansatz)
# vor dem Schultergelenk. Bär: der Muskelbuckel sitzt über und vor den Schultern; mit dem Halsansatz am Schultergelenk
# hing der Buckel zu 58 % am Hals (Neck_1) und sackte mit jedem Kopfsenken ein. Ohne den Wert (0) alles wie bisher.
x_ce = x_sh + RIG.get("chest_extend", 0.0) * (x_hb - x_sh)
spine = [center_at(x_hip + f * (x_ce - x_hip), "body", SSL) for f in (0, 1 / 3, 2 / 3, 1)]
neck = [spine[3], center_at(x_ce + 0.5 * (x_hb - x_ce), sl=SSL), center_at(x_hb, sl=SSL)]
nose_s = M[M[:, 0] > x_nose - 0.03 * L]
nose = np.array([x_nose, Y_MID, float(np.median(nose_s[:, 2]))])
x_tb = x_hip - RIG["tail_base"] * (x_sh - x_hip)
tail = [center_at(x_tb + f * (x_tail - x_tb)) for f in (0, 0.25, 0.5, 0.75)]
tail_tip = M[M[:, 0] < x_tail + 0.02 * L].mean(0)
tail.append(np.array([x_tail, Y_MID, tail_tip[2]]))
# Lücken (Schnitt ohne Vertices, z. B. kurzer Stummelschwanz bei gestreckter Statur) vom Vorgänger füllen – fortlaufend,
# damit auch mehrere Lücken hintereinander gefüllt werden (früher: nur eine, sonst None → Absturz). Ohne Lücken identisch.
for i in range(len(tail)):
    if tail[i] is None:
        tail[i] = tail[i - 1]                                # i = 0: Schwanzspitze (wie bisher)
root = np.array([(x_hip + x_sh) / 2, Y_MID, GROUND])
head_s = M[M[:, 0] > x_hb]
head_low = float(np.percentile(head_s[:, 2], 10))

BONES.update({
    "Root": (root, root + np.array([0, 0, 0.15 * H]), None),
    "Hips": (spine[0], spine[1], "Root"),
    "Spine_1": (spine[1], spine[2], "Hips"),
    "Chest": (spine[2], spine[3], "Spine_1"),
    "Neck_1": (neck[0], neck[1], "Chest"),
    "Neck_2": (neck[1], neck[2], "Neck_1"),
    "Head": (neck[2], nose, "Neck_2"),
    "Jaw": (np.array([x_hb + 0.25 * (x_nose - x_hb), Y_MID, (neck[2][2] + head_low) / 2]),
            np.array([x_nose, Y_MID, head_low + 0.3 * (nose[2] - head_low)]), "Head"),
    "Tail_1": (spine[0], tail[1], "Hips"),
    "Tail_2": (tail[1], tail[2], "Tail_1"),
    "Tail_3": (tail[2], tail[3], "Tail_2"),
    "Tail_4": (tail[3], tail[4], "Tail_3"),
})

# ------------------------------------------------------------------ Armature bauen
arm_data = bpy.data.armatures.new("Quadruped_Rig")
arm = bpy.data.objects.new("Quadruped_Rig", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
order = ["Root", "Hips", "Spine_1", "Chest", "Neck_1", "Neck_2", "Head", "Jaw",
         "Tail_1", "Tail_2", "Tail_3", "Tail_4", "Shoulder_FL", "Shoulder_FR"] +     [f"Leg_{n}_{k}" for n in ("FL", "FR", "BL", "BR") for k in range(1, 5)]
for n in order:
    hd, tl, _ = BONES[n]
    eb = arm_data.edit_bones.new(n)
    eb.head, eb.tail = Vector(hd), Vector(tl)
    if (eb.tail - eb.head).length < 1e-4:
        eb.tail = eb.head + Vector((0, 0, 0.01 * H))
    eb.roll = 0.0
for n in order:
    p = BONES[n][2]
    if p:
        eb = arm_data.edit_bones[n]
        eb.parent = arm_data.edit_bones[p]
        eb.use_connect = False
bpy.ops.object.mode_set(mode="OBJECT")


# ------------------------------------------------------------------ Tripo-Hautbrücken zwischen linkem/rechtem Bein entfernen
def seg_dist(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(1e-12, ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


if RIG.get("cut_leg_bridges", False):
    sys.path.insert(0, str(HERE))
    import rig_common as RC
    fmask = np.zeros(len(me.polygons), bool)
    for pair in (("FL", "FR"), ("BL", "BR")):
        dpl = [np.min(np.stack([seg_dist(V, np.array(BONES[f"Leg_{lg}_{k}"][0]), np.array(BONES[f"Leg_{lg}_{k}"][1]))
                                for k in (1, 2, 3)], 1), 1) for lg in pair]
        left = dpl[0] < dpl[1]
        low = V[:, 2] < min(LEGS[pair[0]]["belly"], LEGS[pair[1]]["belly"])
        near_mid = np.abs(V[:, 1] - Y_MID) < RIG.get("bridge_half_width", 0.12) * H
        for i, poly in enumerate(me.polygons):
            vs = poly.vertices
            if len({bool(left[v]) for v in vs}) == 2 and all(low[v] and near_mid[v] for v in vs):
                fmask[i] = True
    if fmask.any():
        RC.delete_faces(body, fmask)
        V, part, MAIN = RC.arrays(body)
        N = len(V)
        main = part == MAIN
        ids = np.unique(part)
    print(f"RIG_INFO Hautbrücken zwischen den Beinen: {int(fmask.sum())} Flächen entfernt")

# ------------------------------------------------------------------ Gelenk-Verdichtung (C9, nur mit [joint_densify])
# Allzweck-Baustein rigging/joint_densify.py: mehr Vertices im Ring um stark beugende Gelenke, VOR dem Gewichten.
# Ohne Abschnitt in der creature.toml passiert hier nichts.
sys.path.insert(0, str(HERE))
import joint_densify as JD  # noqa: E402
JDS = JD.load_cfg(args[2] if len(args) > 2 else None)
if JDS:
    import rig_common as RC
    JDS = JD.densify(body, BONES, JDS)
    V, part, MAIN = RC.arrays(body)
    N = len(V)
    main = part == MAIN
    ids = np.unique(part)

# ------------------------------------------------------------------ Gewichte
def seg_dist(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(1e-12, ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


names = order[1:]                                      # Root bekommt keine Gewichte
Dm = np.stack([seg_dist(V, np.array(BONES[n][0]), np.array(BONES[n][1])) for n in names], 1)
allow = np.ones_like(Dm, bool)
for j, n in enumerate(names):
    if n.startswith("Leg_"):
        leg = n[4:6]
        side = 1 if leg[1] == "L" else -1
        lg = LEGS[leg]
        own_side = (V[:, 1] - Y_MID) * side > -RIG["leg_cross"] * H
        x_ok = np.abs(V[:, 0] - lg["joint"][0]) < RIG["leg_x_reach"] * L
        top_m = RIG["leg_top_margin"] if leg[0] == "F" else RIG.get("leg_top_margin_back", RIG["leg_top_margin"])
        allow[:, j] = own_side & x_ok & (V[:, 2] < lg["joint"][2] + top_m * H)
    if n.startswith("Shoulder_"):
        side = 1 if n[-1] == "L" else -1
        allow[:, j] = ((V[:, 1] - Y_MID) * side > -RIG["leg_cross"] * H) &             (np.abs(V[:, 0] - LEGS[n[-2:]]["joint"][0]) < RIG["leg_x_reach"] * L)
    if n == "Jaw":
        allow[:, j] = (V[:, 0] > x_hb + 0.2 * (x_nose - x_hb)) & (V[:, 2] < BONES["Jaw"][0][2] + 0.02 * H)
    if n == "Head":
        allow[:, j] = V[:, 0] > x_hb - 0.1 * (x_nose - x_hb)
    if n.startswith("Tail"):
        allow[:, j] = V[:, 0] < x_tb + 0.05 * L
    if n.startswith("Neck"):
        # Brust zwischen den Vorderbeinen gehört zu Chest/Schulter, nicht zum Hals (reißt sonst im Galopp)
        fb, ft = LEGS["FL"]["belly"], LEGS["FL"]["back"]
        center = np.abs(V[:, 1] - Y_MID) < RIG["neck_center_width"] * H     # Nacken oben, nicht Schulterseite
        allow[:, j] = ((V[:, 2] > fb + RIG["neck_min_height"] * (ft - fb)) & center) | \
                      (V[:, 0] > x_sh + RIG["neck_free_ahead"] * (x_hb - x_sh))
# Unterhalb der Bauchlinie zählen nur Bein-Knochen (Beine kleben sonst am Rumpf)
body_names = [j for j, n in enumerate(names) if not n.startswith(("Leg_", "Shoulder_"))]
for leg, lg in LEGS.items():
    near = (np.linalg.norm(V[:, :2] - lg["track"][:, :2].mean(0), axis=1) < RIG["leg_capture"] * H) \
        & (V[:, 2] < lg["belly"] - RIG["below_belly"] * H)
    allow[np.ix_(near, body_names)] = False
# Linkes/rechtes Bein eines Paares: jeder Vertex nur am NÄHEREN (sonst ziehen beide gegenläufig an der Bauchmitte);
# die Bauchmitte darf zusätzlich wieder an den Rumpf
for pair in ((("FL", "FR"), ("BL", "BR")) if RIG.get("exclusive_leg_pairs", False) else ()):
    dpl = [np.min(np.stack([seg_dist(V, np.array(BONES[f"Leg_{lg}_{k}"][0]), np.array(BONES[f"Leg_{lg}_{k}"][1]))
                            for k in (1, 2, 3, 4)], 1), 1) for lg in pair]
    left = dpl[0] < dpl[1]
    for j, n in enumerate(names):
        if n.startswith((f"Leg_{pair[0]}", f"Shoulder_{pair[0]}")):
            allow[:, j] &= left
        elif n.startswith((f"Leg_{pair[1]}", f"Shoulder_{pair[1]}")):
            allow[:, j] &= ~left
if RIG.get("exclusive_leg_pairs", False):
    mid = np.abs(V[:, 1] - Y_MID) < RIG.get("belly_mid_width", 0.04) * H
    allow[np.ix_(mid, body_names)] = True
W = np.where(allow, 1.0 / (Dm + 1e-4) ** RIG["falloff"], 0.0)
W[W.sum(1) == 0, :] = 1.0 / (Dm[W.sum(1) == 0] + 1e-4) ** RIG["falloff"]
# C15 Fremdbereich-Sperre (nur mit zone_lock = true): ein Knochen wirkt nur in seinem Körperbereich, weich auslaufend.
# Faktor je Vertex/Knochen (1 = unverändert), wird vor UND nach dem Glätten angewendet (Glätten trägt sonst zurück).
TAPER = None
if RIG.get("zone_lock", False):
    TAPER = np.ones_like(W)
    # (a) Unterbein (Leg_*_2..4) nicht über Knie/Ellbogen (Kopf von Leg_*_2): sonst zieht das Schienbein an Flanke und
    #     Oberschenkel. Pfote/Sprunggelenk (unterhalb des Knies) bleiben unverändert.
    lm = RIG.get("zone_leg_margin", 0.03) * H
    for j, n in enumerate(names):
        if n.startswith("Leg_") and int(n[-1]) >= 2:
            hz = BONES[n[:7] + "2"][0][2]
            TAPER[:, j] *= np.clip(1.0 - (V[:, 2] - hz) / lm, 0.0, 1.0)
    # (b) Rückenlinie nur Wirbelkette/Schwanz: Schulterblatt/Bein nicht auf dem Rückenstreifen (oberhalb der Wirbelsäule,
    #     nahe der Mittellinie) – sonst halten Schulterblätter den Widerrist fest, Oberschenkel ziehen die Kruppe
    cx = np.array([BONES[c][0] for c in ("Hips", "Spine_1", "Chest", "Neck_1")] + [BONES["Neck_1"][1]])
    zs = np.interp(V[:, 0], cx[:, 0], cx[:, 2])               # Wirbelsäulen-Höhe bei x (außerhalb: Endwert)
    xb = np.linspace(M[:, 0].min(), M[:, 0].max(), 41)
    hw_b = np.zeros(40)
    for k in range(40):
        s = M[(M[:, 0] >= xb[k]) & (M[:, 0] < xb[k + 1])]
        s = s[s[:, 2] > np.interp(s[:, 0], cx[:, 0], cx[:, 2]) - 0.02 * H] if len(s) else s
        hw_b[k] = np.percentile(np.abs(s[:, 1] - Y_MID), 90) if len(s) >= 5 else np.nan
    ok_b = ~np.isnan(hw_b)
    hw = np.interp(V[:, 0], ((xb[:-1] + xb[1:]) / 2)[ok_b], hw_b[ok_b])
    rel_y = np.abs(V[:, 1] - Y_MID) / np.maximum(hw, 1e-6)
    d0, d1 = RIG.get("zone_dorsal", 0.35), RIG.get("zone_dorsal_soft", 0.25)
    f = np.clip((rel_y - d0) / d1, 0.0, 1.0)                  # quer: Mittellinie gesperrt, seitlich weich frei
    s_z = np.clip((V[:, 2] - zs) / np.maximum(d1 * hw, 1e-6), 0.0, 1.0)   # hoch: ab Wirbelsäulen-Höhe weich zunehmend
    f = np.where(V[:, 0] < BONES["Neck_2"][0][0], 1.0 - s_z * (1.0 - f), 1.0)
    for j, n in enumerate(names):
        if n.startswith(("Leg_", "Shoulder_")):
            TAPER[:, j] *= f
    lower = [j for j, n in enumerate(names) if n.startswith("Leg_") and int(n[-1]) >= 2]
    n_low = int(((W[:, lower] > 0) & (TAPER[:, lower] < 1)).any(1).sum())
    W *= TAPER
    W[W.sum(1) == 0, :] = 1.0 / (Dm[W.sum(1) == 0] + 1e-4) ** RIG["falloff"] * (TAPER[W.sum(1) == 0] > 0)
    print(f"RIG_INFO Fremdbereich-Sperre: Unterbein über Knie/Ellbogen gedämpft {n_low} Vertices, "
          f"Rückenstreifen (Bein/Schulterblatt gedämpft) {int((f < 1).sum())} Vertices")
# Nebenteile: standardmäßig weiche Abstands-Gewichte wie der Hauptkörper (Pfoten gehen am Knöchel über,
# Rückenflossen biegen mit). rigid_parts = true → starr am nächsten Knochen (für harte Panzerplatten).
for pid in ids:
    if pid == MAIN or not RIG.get("rigid_parts", False):
        continue
    idx = np.where(part == pid)[0]
    c = V[idx].mean(0, keepdims=True)
    dc = np.stack([seg_dist(c, np.array(BONES[n][0]), np.array(BONES[n][1])) for n in names], 1)[0]
    dc[[j for j, n in enumerate(names) if n.startswith("Leg_") and c[0, 2] > LEGS[n[4:6]]["belly"]]] = 1e9
    # optional (Rimehide Bear 2026-11-21): diese Knochen nie für lose Teile wählen – z. B. ["Jaw"], damit Säbel-Fangzähne
    # aus dem OBERkiefer starr am Kopf hängen statt am (näheren) Unterkiefer. Standard leer = Verhalten wie bisher.
    dc[[j for j, n in enumerate(names) if n in RIG.get("rigid_parts_exclude", [])]] = 1e9
    W[idx] = 0.0
    W[idx, int(np.argmin(dc))] = 1.0
# Glätten über Kanten (nur Hauptteil), danach max. 4 Einflüsse
W = W / W.sum(1, keepdims=True)
E = np.array([e.vertices[:] for e in me.edges])
# Vertices an derselben Position (Tripo trennt sie an UV-Nähten) MÜSSEN gleiche Gewichte haben, sonst reißt
# das Mesh dort auf → beim Glätten als verbunden behandeln und am Ende exakt angleichen
key_groups = {}
for i, co in enumerate(np.round(V, 5)):
    key_groups.setdefault(tuple(co), []).append(i)
WELD = [g for g in key_groups.values() if len(g) > 1]
if WELD:
    E = np.vstack([E] + [np.array([[g[0], x] for x in g[1:]]) for g in WELD])
for _ in range(RIG["smooth_iterations"]):
    acc = np.zeros_like(W)
    cnt = np.zeros(N)
    np.add.at(acc, E[:, 0], W[E[:, 1]])
    np.add.at(acc, E[:, 1], W[E[:, 0]])
    np.add.at(cnt, E[:, 0], 1)
    np.add.at(cnt, E[:, 1], 1)
    sm = np.where(cnt[:, None] > 0, acc / np.maximum(cnt, 1)[:, None], W)
    smooth_mask = (main | ~RIG.get("rigid_parts", False))[:, None]
    W = np.where(smooth_mask, (1 - RIG["smooth_factor"]) * W + RIG["smooth_factor"] * sm, W)
    W = np.where(allow | ~smooth_mask, W, 0.0)
    W = W / np.maximum(W.sum(1, keepdims=True), 1e-12)
if TAPER is not None:                                  # C15: Sperre nach dem Glätten erneut (Rest wird umverteilt)
    Wt = W * TAPER
    keep = Wt.sum(1) > 1e-9
    W[keep] = Wt[keep] / Wt[keep].sum(1, keepdims=True)
# C15 Glätten entlang der Wirbelkette (nur mit spine_chain_blend > 0): Der Anteil, den Hips/Spine_1/Chest/Neck_1/Neck_2
# zusammen haben, wird nach der Lage ENTLANG der Kette neu verteilt (weiche lineare Rampe der Breite b um jedes Gelenk)
# statt nach dem Abstand zu jedem einzelnen Knochen. Sonst greift z. B. beim steilen Hirsch-Hals der obere Halsknochen
# auf den Widerrist durch (gleich weit entfernt wie Neck_1) → harter Wechsel, Widerrist reißt beim Senken des Kopfes.
if RIG.get("spine_chain_blend", 0) > 0:
    b = float(RIG["spine_chain_blend"])
    chain = ["Hips", "Spine_1", "Chest", "Neck_1", "Neck_2"]
    ci = [names.index(c) for c in chain]
    tparts, wparts = [], []
    for k, c in enumerate(chain + ["Head"]):
        h_, t_ = np.array(BONES[c][0]), np.array(BONES[c][1])
        ab = t_ - h_
        u = np.clip(((V - h_) @ ab) / max(1e-12, ab @ ab), 0, 1)
        d = np.linalg.norm(V - (h_ + u[:, None] * ab), axis=1)
        tparts.append(k + u)
        wparts.append(1.0 / (d + 1e-4) ** RIG["falloff"])
    tparts, wparts = np.stack(tparts, 1), np.stack(wparts, 1)
    tch = (tparts * wparts).sum(1) / wparts.sum(1)          # Lage entlang der Kette (0 = Becken … 5 = Kopfansatz)
    nk = len(chain)
    hat = np.zeros((N, nk))
    for k in range(nk):                                     # Knochen k: Plateau, an jedem Gelenk lineare Rampe der Breite b
        lo = np.clip((tch - (k - b / 2)) / b, 0, 1) if k > 0 else np.ones(N)
        hi = np.clip(((k + 1 + b / 2) - tch) / b, 0, 1) if k < nk - 1 else np.ones(N)
        hat[:, k] = np.minimum(lo, hi)
    hat /= np.maximum(hat.sum(1, keepdims=True), 1e-12)
    share = W[:, ci].sum(1)
    newc = hat * share[:, None]
    newc = np.where(allow[:, ci], newc, 0.0)
    ok_c = newc.sum(1) > 1e-9
    newc[ok_c] *= (share[ok_c] / newc[ok_c].sum(1))[:, None]
    sel_c = ok_c & (share > 1e-6)
    Wc = W[:, ci]
    Wc[sel_c] = newc[sel_c]
    W[:, ci] = Wc
    print(f"RIG_INFO Wirbelkette entlang der Kette verteilt (Rampe {b}): {int(sel_c.sum())} Vertices")
# Geweih/Hörner starr am Kopf: alles oberhalb des Kopf-Knochens (vor den Schultern) nur an "Head".
# Sonst liegen die Geweihspitzen näher am Hals-Knochen und verbiegen sich bei jedem Schritt mit dem Hals.
if RIG.get("rigid_head_above") is not None:
    hb_top = max(BONES["Head"][0][2], BONES["Head"][1][2])
    above = V[:, 2] > hb_top + RIG["rigid_head_above"] * H
    hi_ = names.index("Head")
    if RIG.get("rigid_head_connected", False):
        # C14 (Hollow Stag): Statt "vor der Schulter" (x > x_sh) zählt der Zusammenhang. Hintere Geweihsprossen ragen
        # in der Draufsicht bis hinter die Schulter → hingen sonst an Hals/Brust/Schulter und wurden nach hinten gezogen.
        # Starr am Kopf = alles über der Kopf-Oberkante, das INNERHALB dieser Zone mit dem Schädel verbunden ist
        # (Rückenstacheln/Mähne liegen tiefer bzw. hängen nicht am Geweih → bleiben am Rumpf).
        par_h = np.arange(N)

        def find_h(i):
            while par_h[i] != i:
                par_h[i] = par_h[par_h[i]]
                i = par_h[i]
            return i
        for u, v in E[above[E[:, 0]] & above[E[:, 1]]]:
            par_h[find_h(u)] = find_h(v)
        comp_h = np.array([find_h(i) for i in range(N)])
        seed = above & (V[:, 0] >= BONES["Head"][0][0])          # über dem Schädel (ab Kopfansatz nach vorn)
        rh = above & np.isin(comp_h, np.unique(comp_h[seed]))
        print(f"RIG_INFO Kopf-Aufbau zusammenhängend: {int(rh.sum())} Vertices, davon {int((rh & (V[:, 0] <= x_sh)).sum())} "
              f"hinter der Schulter; über der Kopf-Oberkante, aber nicht verbunden: {int((above & ~rh).sum())}")
    else:
        rh = above & (V[:, 0] > x_sh)
    W[rh] = 0.0
    W[rh, hi_] = 1.0
    print(f"RIG_INFO Kopf-Aufbau starr am Kopf: {int(rh.sum())} Vertices")
    # Weicher Übergang starr → Hals über n Kanten-Ringe UNTER der starren Zone (die starre Zone bleibt 100 % Kopf):
    # sonst harte Kante am Nacken (Head 1,0 direkt neben Neck_2 1,0).
    rings = int(RIG.get("rigid_head_blend_rings", 0))
    if rings:
        rep = np.arange(N)                                      # UV-Naht-Duplikate gemeinsam behandeln
        for g in WELD:
            rep[g] = g[0]
        done, n_ring = rh.copy(), []
        for k in range(rings):
            nb = np.zeros(N, bool)
            cut = done[E[:, 0]] != done[E[:, 1]]
            nb[E[cut].ravel()] = True
            nb &= ~done
            nr = np.zeros(N, bool)
            nr[rep[nb]] = True
            nb = nr[rep] & ~done
            t = (rings - k) / (rings + 1)                        # 2 Ringe: 2/3, 1/3 Kopf-Anteil dazumischen
            W[nb] *= 1 - t
            W[nb, hi_] += t
            done |= nb
            n_ring.append(nb)
        allr = np.any(n_ring, 0)
        print(f"RIG_INFO Übergang Kopf→Hals: {rings} Ringe, {[int(r.sum()) for r in n_ring]} Vertices, "
              f"x {V[allr, 0].min():.3f}..{V[allr, 0].max():.3f}, z über Boden {V[allr, 2].min() - GROUND:.3f}.."
              f"{V[allr, 2].max() - GROUND:.3f}")

# Panzer 100 % starr (rigid_shell, Shellback 2026-11-23; ohne die Option ändert sich nichts):
# Panzer = Hauptkörper ohne Bein-, Hals/Kopf- und Schwanz-Öffnungen, alles an EINEM Knochen (shell_bone). Sonst greifen
# Schulterblatt/Oberarm/Oberschenkel, Hals und Schwanz in den Panzerrand → Rand wackelt bei jedem Schritt.
# Übergang starr → weich über shell_blend_rings Kanten-Ringe AUSSERHALB des Panzers (Haut in den Öffnungen).
SHELL = None
if RIG.get("rigid_shell", False):
    sb = names.index(RIG.get("shell_bone", "Spine_1"))
    zg = V[:, 2] - GROUND
    soft = np.zeros(N, bool)
    # (1) Beine: nahe an der Beinkette (Leg_*_1..4) und unter dem Panzerrand (vorne/hinten eigene Randhöhe)
    for leg in LEGS:
        dl = np.min(np.stack([seg_dist(V, np.array(BONES[f"Leg_{leg}_{k}"][0]), np.array(BONES[f"Leg_{leg}_{k}"][1]))
                              for k in (1, 2, 3, 4)], 1), 1)
        rim = RIG.get("shell_rim_front" if leg[0] == "F" else "shell_rim_back", 0.4) * H
        soft |= (dl < RIG.get("shell_leg_radius", 0.16) * H) & (zg < rim)
    # (2) Hals/Kopf: vor der Halsöffnung (Ebene, oben ggf. weiter vorn: Nackenschild über dem Hals bleibt Panzer)
    zn = BONES["Neck_1"][0][2]
    x_open = x_sh + RIG.get("shell_front", 0.3) * (x_hb - x_sh) + RIG.get("shell_front_slope", 0.0) * (V[:, 2] - zn)
    soft |= V[:, 0] > x_open
    # (3) Schwanz: hinter der Schwanzöffnung und unter dem Panzerrand hinten
    x_back = x_tail + RIG.get("shell_back", 0.12) * L
    soft |= (V[:, 0] < x_back) & (zg < RIG.get("shell_rim_tail", 1.0) * H)
    soft |= zg < RIG.get("shell_min_height", 0.0) * H                 # (4) nichts am Boden (Krallen/Fersen) gehört zum Panzer
    SHELL = main & ~soft
    # (5) Halsöffnung frei von Schulterblatt/Bein: über dem vorderen Panzerrand und vor dem Schultergelenk zählen nur Hals,
    #     Kopf und Panzer – sonst reißt die Haut zwischen vorschießendem Hals und Schulterblatt (Shellback Attack1)
    if RIG.get("shell_neck_free", False):
        # weich auslaufend (shell_neck_free_soft · H), sonst entsteht am Zonenrand eine harte Naht (Lückenprüfung 5,8 cm)
        sft = max(1e-6, RIG.get("shell_neck_free_soft", 0.06) * H)
        kx = np.clip(1.0 - (V[:, 0] - x_sh) / sft, 0.0, 1.0)                                 # hinter der Schulter: frei
        ky = np.clip((np.abs(V[:, 1] - Y_MID) - RIG.get("shell_neck_free_width", 0.0) * H) / sft, 0.0, 1.0)  # Kehle
        kz = np.clip((RIG.get("shell_rim_front", 0.4) * H - zg) / sft, 0.0, 1.0)            # über dem Panzerrand
        kk = np.maximum(kx, np.minimum(ky, kz))
        nz = kk < 1.0
        lj = [j for j, n in enumerate(names) if n.startswith(("Leg_", "Shoulder_"))]
        Wn = W[nz].copy()
        Wn[:, lj] *= kk[nz, None]
        ok_n = Wn.sum(1) > 1e-6
        Wn[ok_n] /= Wn[ok_n].sum(1, keepdims=True)
        Wn[~ok_n] = W[nz][~ok_n]
        W[nz] = Wn
        print(f"RIG_INFO Halsöffnung ohne Schulter/Bein: {int((kk == 0).sum())} Vertices, Übergang {int((nz & (kk > 0)).sum())}")
    W[SHELL] = 0.0
    W[SHELL, sb] = 1.0
    if RIG.get("shell_blend_width"):
        # Übergang nach ABSTAND (Meter) statt Kanten-Ringen: Tripo-Low-Poly hat am Panzerrand sehr kurze Kanten (0,5–1 cm)
        # neben langen; ein Ring-Übergang ist dort nur 1–2 cm breit → Haut reißt an der kurzen Kante. Anteil Panzer-Knochen
        # fällt linear mit dem Abstand zum nächsten Panzer-Vertex (0 ab shell_blend_width · H).
        from mathutils.kdtree import KDTree
        kd = KDTree(int(SHELL.sum()))
        for i in np.where(SHELL)[0]:
            kd.insert(V[i], int(i))
        kd.balance()
        bw = RIG["shell_blend_width"] * H
        out_ = np.where(~SHELL)[0]
        dist = np.array([kd.find(V[i])[2] for i in out_])
        t = np.clip(1.0 - dist / bw, 0.0, 1.0) ** RIG.get("shell_blend_power", 1.0)
        W[out_] *= (1 - t)[:, None]
        W[out_, sb] += t
        n_ring = [(t > 0.5), (t > 0) & (t <= 0.5)]
        rings = f"Abstand {bw:.3f} m"
    else:
        rings = int(RIG.get("shell_blend_rings", 2))
        rep = np.arange(N)
        for g in WELD:
            rep[g] = g[0]
        done, n_ring = SHELL.copy(), []
        for k in range(rings):
            nb = np.zeros(N, bool)
            cut = done[E[:, 0]] != done[E[:, 1]]
            nb[E[cut].ravel()] = True
            nb &= ~done
            nr = np.zeros(N, bool)
            nr[rep[nb]] = True
            nb = nr[rep] & ~done
            t = (rings - k) / (rings + 1)
            W[nb] *= 1 - t
            W[nb, sb] += t
            done |= nb
            n_ring.append(nb)
    print(f"RIG_INFO Panzer starr an {names[sb]}: {int(SHELL.sum())} Vertices, Übergang {rings} Ringe "
          f"{[int(r.sum()) for r in n_ring]} Vertices (Übergang > 0,5 | ≤ 0,5)")
for g in WELD:
    W[g] = W[g].mean(0)
top = np.argsort(-W, 1)[:, :4]
for n in names:
    body.vertex_groups.new(name=n)
for i in range(N):
    ws = W[i, top[i]]
    ws = ws / ws.sum()
    for j, w in zip(top[i], ws):
        if w > 1e-3:
            body.vertex_groups[names[j]].add([i], float(w), "REPLACE")
if JDS:                                                  # weiche Gewichte über mehrere Ringe (nur im Ring)
    JD.soften(body, JDS)
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm
for p in me.polygons:
    p.use_smooth = False

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "quadruped_rigged.blend"))
report = {"vertices": N, "parts": int(len(ids)), "height_m": round(H, 3), "length_m": round(L, 3),
          "bones": len(order), "feet": {k: [round(float(c), 3) for c in v[:, :2].mean(0)] for k, v in FEET.items()},
          "belly_z": {k: round(v["belly"] - GROUND, 3) for k, v in LEGS.items()}}
if JDS:
    report["joint_densify"] = JD.finish(JDS, OUT)
if SHELL is not None:
    report["rigid_shell"] = {"bone": RIG.get("shell_bone", "Spine_1"), "vertices": int(SHELL.sum())}
(OUT / "rig_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
sample = V[::max(1, N // 4000)]
(OUT / "rig_debug.json").write_text(json.dumps({
    "verts": np.round(sample, 4).tolist(),
    "bones": {n: [np.round(BONES[n][0], 4).tolist(), np.round(BONES[n][1], 4).tolist()] for n in order},
    "tracks": {k: np.round(v["track"], 4).tolist() for k, v in LEGS.items()}}), encoding="utf-8")
print("RIG_OK", json.dumps(report))
