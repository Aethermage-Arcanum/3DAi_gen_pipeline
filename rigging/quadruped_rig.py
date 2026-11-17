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
foot_band = M[M[:, 2] < GROUND + D["foot_band"] * H]
cx = np.array([foot_band[:, 0].min(), foot_band[:, 0].max()])
for _ in range(20):                                   # 1D-k-means: vorne/hinten
    lab = np.abs(foot_band[:, 0:1] - cx[None]).argmin(1)
    cx = np.array([foot_band[lab == k, 0].mean() for k in (0, 1)])
FEET = {}
for k, fb in ((1, "F"), (0, "B")):
    for side, sn in ((1, "L"), (-1, "R")):
        sel = foot_band[(lab == k) & ((foot_band[:, 1] - Y_MID) * side > 0)]
        if len(sel) < 3:
            raise SystemExit(f"Fuß {fb}{sn} nicht gefunden")
        FEET[f"{fb}{sn}"] = sel


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
    belly = midline_profile(c[0], D["mid_half_width"] * H)
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
def center_at(x, region=None):
    s = M[np.abs(M[:, 0] - x) < D["slice"] * L]
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
spine = [center_at(x_hip + f * (x_sh - x_hip), "body") for f in (0, 1 / 3, 2 / 3, 1)]
x_hb = x_nose - RIG["head_length"] * (x_nose - x_sh)
neck = [spine[3], center_at(x_sh + 0.5 * (x_hb - x_sh)), center_at(x_hb)]
nose_s = M[M[:, 0] > x_nose - 0.03 * L]
nose = np.array([x_nose, Y_MID, float(np.median(nose_s[:, 2]))])
x_tb = x_hip - RIG["tail_base"] * (x_sh - x_hip)
tail = [center_at(x_tb + f * (x_tail - x_tb)) for f in (0, 0.25, 0.5, 0.75)]
tail_tip = M[M[:, 0] < x_tail + 0.02 * L].mean(0)
tail.append(np.array([x_tail, Y_MID, tail_tip[2]]))
tail = [t if t is not None else tail[i - 1] for i, t in enumerate(tail)]
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
# Nebenteile: standardmäßig weiche Abstands-Gewichte wie der Hauptkörper (Pfoten gehen am Knöchel über,
# Rückenflossen biegen mit). rigid_parts = true → starr am nächsten Knochen (für harte Panzerplatten).
for pid in ids:
    if pid == MAIN or not RIG.get("rigid_parts", False):
        continue
    idx = np.where(part == pid)[0]
    c = V[idx].mean(0, keepdims=True)
    dc = np.stack([seg_dist(c, np.array(BONES[n][0]), np.array(BONES[n][1])) for n in names], 1)[0]
    dc[[j for j, n in enumerate(names) if n.startswith("Leg_") and c[0, 2] > LEGS[n[4:6]]["belly"]]] = 1e9
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
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm
for p in me.polygons:
    p.use_smooth = False

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "quadruped_rigged.blend"))
report = {"vertices": N, "parts": int(len(ids)), "height_m": round(H, 3), "length_m": round(L, 3),
          "bones": len(order), "feet": {k: [round(float(c), 3) for c in v[:, :2].mean(0)] for k, v in FEET.items()},
          "belly_z": {k: round(v["belly"] - GROUND, 3) for k, v in LEGS.items()}}
(OUT / "rig_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
sample = V[::max(1, N // 4000)]
(OUT / "rig_debug.json").write_text(json.dumps({
    "verts": np.round(sample, 4).tolist(),
    "bones": {n: [np.round(BONES[n][0], 4).tolist(), np.round(BONES[n][1], 4).tolist()] for n in order},
    "tracks": {k: np.round(v["track"], 4).tolist() for k, v in LEGS.items()}}), encoding="utf-8")
print("RIG_OK", json.dumps(report))
