"""Bewegungsmuster crawler/ant: backt ALLE Clips des Musters auf ein gerigtes Krabbler-Modell + Selbstprüfung.

& "D:\\Blender\\blender.exe" -b <crawler_rigged.blend> -P motions/crawler/ant/ant_clips.py -- <ausgabeordner> [<creature.toml>]
Ergebnis: <ausgabe>/crawler_clips.blend (alle Actions), clips_report.json (Prüfwerte), events.json (Unity-Events)

Achsen (Armature-Raum): vorne +X, links +Y, oben +Z.
"""
import copy
import json
import math
import pathlib
import sys
import tomllib

import bpy
from mathutils import Euler, Quaternion, Vector

HERE = pathlib.Path(__file__).resolve().parent
R = math.radians
FWD, LEFT, UP = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


# ---------------------------------------------------------------- Konfiguration
def merge(a, b):
    out = copy.deepcopy(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_style(creature_toml=None):
    st = tomllib.loads((HERE / "style.toml").read_text(encoding="utf-8"))
    m = {}
    if creature_toml:
        m = tomllib.loads(pathlib.Path(creature_toml).read_text(encoding="utf-8")).get("motion", {})
    variant = m.get("variant")
    if variant:
        st = merge(st, st["variants"][variant])
    st = merge(st, {k: v for k, v in m.items() if isinstance(v, dict)})
    for sec in ("run", "turn"):            # erben von walk
        st[sec] = merge(st["walk"], st[sec])
    st["meta"]["variant"] = variant
    return st


args = sys.argv[sys.argv.index("--") + 1:]
OUT = pathlib.Path(args[0]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
ST = load_style(args[1] if len(args) > 1 else None)
FPS = ST["meta"]["fps"]
PREFIX = ST["meta"]["clip_prefix"]

arm = bpy.data.objects["Crawler_Rig"]
body_obj = bpy.data.objects["Body_Mesh"]
sc = bpy.context.scene
sc.render.fps = FPS
PB, DB = arm.pose.bones, arm.data.bones
SIZE = max(arm.dimensions)

walking = [f"{s}{k}" for k in ST["legs"]["walking_slots"] for s in ("L", "R")]
feelers = [f"{s}{k}" for k in ST["legs"]["feeler_slots"] for s in ("L", "R")]
group_a = {leg for leg in walking if (leg[0] == "L") == (int(leg[1]) % 2 == 1)}

for pb in PB:
    pb.rotation_mode = "QUATERNION"


def reset():
    for pb in PB:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()


def local_axis(name, axis_world):
    return (DB[name].matrix_local.to_3x3().inverted() @ axis_world).normalized()


def rot(name, axis_world, angle, mul=True):
    """Drehung um eine Achse im Armature-Raum (Ruhelage) – wird auf bestehende Pose multipliziert."""
    q = Quaternion(local_axis(name, axis_world), angle)
    PB[name].rotation_quaternion = (PB[name].rotation_quaternion @ q) if mul else q


def move(name, vec_world):
    PB[name].location = DB[name].matrix_local.to_3x3().inverted() @ vec_world


# ---------------------------------------------------------------- Bein-Achsen aus der Geometrie
LEG = {}
thorax_mid = (DB["Thorax"].head_local + DB["Thorax"].tail_local) / 2
for leg in walking + feelers:
    b = {p: DB[f"Leg_{leg}_{p}"] for p in ("Coxa", "Femur", "Tibia", "Tarsus")}
    root, tip, fh = b["Coxa"].head_local, b["Tarsus"].tail_local, b["Femur"].head_local
    h = Vector((tip.x - root.x, tip.y - root.y, 0))
    dir_h = h.normalized() if h.length > 1e-6 else LEFT
    lift_axis = UP.cross(dir_h).normalized()
    lift_sign = 1 if (Quaternion(lift_axis, 0.2) @ (tip - fh)).z > (tip - fh).z else -1
    back_sign = 1 if (Quaternion(UP, 0.2) @ (tip - root)).x < (tip - root).x else -1
    LEG[leg] = {"r": h.length, "phi": math.atan2(h.y, h.x), "back_sign": back_sign,
                "lift_axis": lift_axis * lift_sign,
                "R_center": (Vector((tip.x, tip.y, 0)) - Vector((thorax_mid.x, thorax_mid.y, 0))).length}


def amp(leg, stride, max_deg):
    L = LEG[leg]
    ratio = stride * SIZE / max(1e-6, 2 * L["r"] * abs(math.sin(L["phi"])))
    return min(math.asin(min(1.0, ratio)), R(max_deg))


def set_leg(leg, back=0.0, lift=0.0, fold=0.0, tuck=0.0):
    L = LEG[leg]
    rot(f"Leg_{leg}_Coxa", UP, L["back_sign"] * back + tuck, mul=False)
    rot(f"Leg_{leg}_Femur", L["lift_axis"], lift, mul=False)
    rot(f"Leg_{leg}_Tibia", L["lift_axis"], fold, mul=False)


LEG_MESH_PTS = {}  # pro Bein: Mesh-Punkte von Unterschenkel/Fuß (Ruhelage) + ihr Knochen


PART_MESH_PTS = {}  # Knochenname → Mesh-Punkte (Ruhelage), für Boden-Tests beliebiger Teile


def mesh_part_lowest_z(bone_names):
    low = 1e9
    for bname in bone_names:
        pts = PART_MESH_PTS.get(bname)
        if not pts:
            continue
        pb = PB[bname]
        m = arm.matrix_world @ pb.matrix @ pb.bone.matrix_local.inverted()
        low = min(low, min((m @ p).z for p in pts))
    return low


def leg_lowest_z(leg):
    """Tiefster Mesh-Punkt von Unterschenkel+Fuß in der aktuellen Pose (starr pro Knochen genähert)."""
    low = 1e9
    for bname, pts in LEG_MESH_PTS[leg].items():
        pb = PB[bname]
        m = arm.matrix_world @ pb.matrix @ pb.bone.matrix_local.inverted()
        low = min(low, min((m @ p).z for p in pts))
    return low


def fold_ground_clamped(leg, lift, fold, margin=0.005, max_extra_deg=110):
    """Setzt Bein-Heben/Falten. Geht das Bein-MESH unter den Boden (z. B. weil der Körper absackt),
    wird der Oberschenkel per Bisektion gerade so weit ANGEHOBEN (Knie hoch), dass es aufliegt –
    wie ein Tier, das unter seinem Gewicht die Beine einknickt."""
    set_leg(leg, 0.0, lift, fold)
    bpy.context.view_layer.update()
    floor = GROUND + margin * SIZE
    if leg_lowest_z(leg) >= floor:
        return
    lo, hi = 0.0, R(max_extra_deg)          # zusätzlicher Hebewinkel
    for _ in range(12):
        mid = (lo + hi) / 2
        set_leg(leg, 0.0, lift + mid, fold)
        bpy.context.view_layer.update()
        if leg_lowest_z(leg) >= floor:
            hi = mid
        else:
            lo = mid
    set_leg(leg, 0.0, lift + hi, fold)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def phase(t, offset, duty):
    p = (t + offset) % 1.0
    return (False, p / duty) if p < duty else (True, (p - duty) / (1 - duty))


def leg_offset(leg, P):
    return (0.0 if leg in group_a else 0.5) + P["wave_offset"] * (int(leg[1]) - 2)


# ---------------------------------------------------------------- Bausteine
def antennae(t, deg, speed, tip, stabilize, forward_deg=0.0, droop_deg=0.0):
    bpy.context.view_layer.update()
    q_head = PB["Head"].matrix.to_quaternion() @ DB["Head"].matrix_local.to_quaternion().inverted()
    cancel = Quaternion().slerp(q_head.inverted(), stabilize)
    for side, sign in (("L", 1), ("R", -1)):
        ph = 2 * math.pi * t * speed + (0 if sign > 0 else 1.7)
        own = Euler((R(deg) * math.sin(ph) + R(droop_deg) - R(forward_deg), 0,
                     sign * R(deg) * 0.7 * math.cos(ph + 0.8))).to_quaternion()
        bl = DB[f"Antenna_{side}_1"].matrix_local.to_quaternion()
        PB[f"Antenna_{side}_1"].rotation_quaternion = (bl.inverted() @ cancel @ bl) @ own
        PB[f"Antenna_{side}_2"].rotation_quaternion = Euler(
            (R(deg) * tip * math.sin(ph - 0.9) + R(droop_deg) * 0.8, 0, 0)).to_quaternion()


def feeler_motion(t, deg, speed, raise_deg=0.0):
    for leg in feelers:
        side = 1 if leg[0] == "L" else -1
        ph = 2 * math.pi * (t * speed + (0.25 if side > 0 else 0.75))
        set_leg(leg, back=R(deg) * math.sin(ph) * side * LEG[leg]["back_sign"],
                lift=R(raise_deg) + R(deg) * 0.6 * (0.5 + 0.5 * math.cos(ph + 1)))


def body_wave(t, P):
    two, one = 2 * math.pi * 2 * t, 2 * math.pi * t
    move("Thorax", UP * P["body_bob"] * SIZE * math.sin(two))
    rot("Thorax", FWD, R(P["body_roll_deg"]) * math.sin(one))
    rot("Thorax", UP, R(P["body_sway_deg"]) * math.sin(one))
    rot("Abdomen_1", LEFT, -R(P["abdomen_bob_deg"]) * math.sin(two - P["abdomen_lag"]))
    rot("Abdomen_1", UP, -R(P["abdomen_sway_deg"]) * math.sin(one - P["abdomen_lag"]))
    rot("Abdomen_2", UP, -R(P["abdomen_sway_deg"]) * 0.6 * math.sin(one - 2 * P["abdomen_lag"]))
    rot("Head", LEFT, R(P["head_nod_deg"]) * math.sin(two + 0.5))
    rot("Head", UP, -R(P["head_sway_deg"]) * math.sin(one + 0.3))


def gait(t, P, mode="forward"):
    for leg in walking:
        side = 1 if leg[0] == "L" else -1
        swing, s = phase(t, leg_offset(leg, P), P["duty"])
        A = amp(leg, P["stride"], P["stride_max_deg"])
        d = -1 if (mode == "turn_left" and side > 0) or (mode == "turn_right" and side < 0) else 1
        back = ((-A + 2 * A * s) if not swing else (A - 2 * A * ease(s))) * d
        lift = R(P["lift_deg"]) * math.sin(math.pi * s) if swing else 0.0
        fold = R(P["tibia_fold_deg"]) * math.sin(math.pi * s) if swing else 0.0
        set_leg(leg, back, lift, fold)


# ---------------------------------------------------------------- Clips
def clip_locomotion(P, mode):
    N = P["cycle_frames"]

    def pose(f):
        t = (f % N) / N
        reset()
        gait(t, P, mode)
        feeler_motion(t, P["feeler_deg"], P["feeler_speed"])
        body_wave(t, P)
        antennae(t, P["antenna_deg"], P["antenna_speed"], P["antenna_tip_factor"], P["antenna_stabilize"])
    return N, True, "locomotion", pose


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        reset()
        feeler_motion(t, P["feeler_deg"], 1)
        one = 2 * math.pi * t
        rot("Abdomen_1", LEFT, -R(P["breathe_deg"]) * (0.5 - 0.5 * math.cos(2 * one)))   # 2 Atemzüge
        rot("Thorax", FWD, R(P["weight_shift_deg"]) * math.sin(one))
        rot("Head", UP, R(P["head_look_deg"]) * math.sin(one) * (0.6 + 0.4 * math.sin(2 * one)))
        rot("Head", LEFT, -R(P["head_look_deg"]) * 0.3 * math.sin(3 * one))
        antennae(t, P["antenna_deg"], P["antenna_speed"], P["antenna_tip_factor"], P["antenna_stabilize"])
    return N, True, "stand", pose


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        reset()
        tr = R(P["tremble_deg"]) * math.sin(2 * math.pi * P["tremble_speed"] * t)
        feeler_motion(t, 4, 1, raise_deg=P["feeler_raise_deg"])
        rot("Head", LEFT, -R(P["head_up_deg"]) + tr)
        rot("Abdomen_1", LEFT, -R(P["gaster_raise_deg"]) + tr * 1.5)   # Hinterleib hoch (gaster flagging)
        rot("Abdomen_2", LEFT, -R(P["gaster_raise_deg"]) * 0.5)
        antennae(t, 2, 1, 0.4, 0.5, forward_deg=P["antenna_forward_deg"])
    return N, True, "stand", pose


def clip_attack1(P):
    N, w_end, s_end = P["frames"], P["windup_end"], P["strike_end"]

    def pose(f):
        reset()
        if f <= w_end:                       # Ausholen
            k, lunge = ease(f / w_end), 0.0
            pitch = -R(P["head_pitch_up_deg"]) * k
            pull = -P["head_pull"] * k
        elif f <= s_end:                     # Zuschnappen (schnell)
            k2 = ease((f - w_end) / (s_end - w_end))
            k = 1.0 - k2
            pitch = -R(P["head_pitch_up_deg"]) * (1 - k2) + R(P["head_pitch_down_deg"]) * k2
            pull = -P["head_pull"] * (1 - k2) + P["head_lunge"] * k2
        else:                                # Erholen
            k3 = ease((f - s_end) / (N - s_end))
            k = 0.0
            pitch = R(P["head_pitch_down_deg"]) * (1 - k3)
            pull = P["head_lunge"] * (1 - k3)
        windup = ease(f / w_end) if f <= w_end else max(0.0, 1 - ease((f - w_end) / (N - w_end)))
        move("Head", FWD * pull * SIZE)
        rot("Head", LEFT, pitch)
        rot("Thorax", LEFT, -R(P["thorax_pitch_deg"]) * windup + R(P["thorax_pitch_deg"]) * (1 - windup) * (f > w_end) * (f < N))
        rot("Abdomen_1", LEFT, -R(P["gaster_deg"]) * windup)
        feeler_motion(f / N, 3, 1, raise_deg=P["feeler_raise_deg"] * windup)
        antennae(f / N, 2, 1, 0.4, 0.6, forward_deg=8 * windup)
    return N, False, "stand", pose


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        reset()
        x = f / N
        k = math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x) if x < 1 else 0.0   # schneller Ausschlag, abklingen
        k = 0.0 if f in (0, N) else k
        rot("Head", LEFT, -R(P["head_back_deg"]) * k)
        rot("Thorax", UP, R(P["thorax_jerk_deg"]) * k)
        rot("Abdomen_1", UP, -R(P["abdomen_deg"]) * k)
        antennae(0, 0, 1, 0.4, 0.0, droop_deg=-P["antenna_flick_deg"] * k)
    return N, False, "stand_return", pose


def clip_death_flip(P):
    """Tot auf den Rücken kippen (typisches totes Insekt). Gedreht wird am Root-Knochen → der ganze
    Körper bewegt sich gemeinsam, keine Gelenk-Lücken. Auf dem Rücken rollen sich die Beine ein."""
    N, c0, c1 = P["frames"], P["collapse_start"], P["collapse_end"]
    h0 = DB["Root"].head_local.copy()
    pivot = Vector((thorax_mid.x, 0, (BODY_TOP + GROUND) / 2))   # Drehachse auf halber Körperhöhe

    def pose(f):
        reset()
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        ang = math.pi * k * P["flip_side"]
        q = Quaternion(FWD, ang)
        loc = (pivot - h0) - q @ (pivot - h0) + UP * P["flip_hop"] * SIZE * math.sin(math.pi * k)
        # kleiner Nachfeder-Hüpfer nach dem Aufprall
        if f > c1:
            loc += UP * P["flip_hop"] * 0.25 * SIZE * max(0.0, math.sin(math.pi * (f - c1) / 5)) * (f - c1 < 5)
        rot("Root", FWD, ang, mul=False)
        move("Root", loc)
        # zur Bauchseite krümmen (auf dem Rücken = nach oben), sonst drücken Kopf/Hinterleib in den Boden
        rot("Head", LEFT, -R(8) * jolt - R(10) * k)
        rot("Abdomen_1", LEFT, -R(10) * k)
        curl = ease((f - c0 * 1.5) / (c1 - c0)) if f > c0 * 1.5 else 0.0
        for leg in walking + feelers:
            twitch = 0.0
            if leg == walking[-2] and P["twitch_frame"] - 2 <= f <= P["twitch_frame"] + 2:
                twitch = R(P["twitch_deg"]) * math.sin(math.pi * (f - P["twitch_frame"] + 2) / 4)
            # auf dem Rücken: Beine zum Bauch hin einrollen (= vom Rücken aus gesehen nach oben/innen)
            set_leg(leg, back=0.0, lift=-R(P["femur_curl_deg"]) * curl + twitch,
                    fold=-R(P["tibia_curl_deg"]) * curl)
        # auf dem Rücken würden die Fühler im Boden stecken → Klappwinkel automatisch so wählen,
        # dass die Fühler-Meshes den größten Bodenabstand haben (Richtung ist je nach Modell verschieden)
        best = None
        for cand in range(-80, 81, 10):
            antennae(0, 0, 1, 0.4, 0.0, droop_deg=cand * k)
            bpy.context.view_layer.update()
            z = mesh_part_lowest_z(("Antenna_L_1", "Antenna_L_2", "Antenna_R_1", "Antenna_R_2"))
            if best is None or z > best[0] + 1e-4 or (abs(z - best[0]) <= 1e-4 and abs(cand) < abs(best[1])):
                best = (z, cand)
        antennae(0, 0, 1, 0.4, 0.0, droop_deg=best[1] * k)
    return N, False, "death", pose


def clip_death(P, clearance):
    if P.get("style", "collapse") == "flip":
        return clip_death_flip(P)
    N, c0, c1 = P["frames"], P["collapse_start"], P["collapse_end"]

    def pose(f):
        reset()
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        move("Thorax", -UP * clearance * P["drop_fraction"] * k)
        rot("Thorax", FWD, R(P["roll_deg"]) * k)
        rot("Head", LEFT, R(10) * k - R(8) * jolt)
        rot("Abdomen_1", LEFT, R(6) * k)
        for leg in walking + feelers:
            twitch = 0.0
            # Zucken am hintersten Laufbein (dort ist Platz – vorne liegen die Beinansätze eng am Thorax)
            if leg == walking[-2] and P["twitch_frame"] - 2 <= f <= P["twitch_frame"] + 2:
                twitch = R(P["twitch_deg"]) * math.sin(math.pi * (f - P["twitch_frame"] + 2) / 4)
            # Einrollen = Unterschenkel zur Körpermitte falten (negative "Heben"-Richtung),
            # aber nur so weit, dass die Fußspitze nicht in den Boden geht
            lift = R(P["femur_curl_deg"]) * k + twitch
            fold_ground_clamped(leg, lift, -R(P["tibia_curl_deg"]) * k)
        antennae(0, 0, 1, 0.4, 0.0, droop_deg=P["antenna_droop_deg"] * k)
    return N, False, "death", pose


# ---------------------------------------------------------------- Messen + Backen
def foot(leg):
    return arm.matrix_world @ PB[f"Leg_{leg}_Tarsus"].tail


reset()
bpy.context.view_layer.update()
REST_FOOT = {leg: foot(leg).copy() for leg in walking}
GROUND = min(p.z for p in REST_FOOT.values())
# Bodenfreiheit des Rumpfs (für Death)
names = {g.index: g.name for g in body_obj.vertex_groups}
body_min = min((body_obj.matrix_world @ v.co).z for v in body_obj.data.vertices
               if v.groups and not names[max(v.groups, key=lambda g: g.weight).group].startswith(("Leg_", "Antenna_")))
CLEARANCE = body_min - GROUND
# Mesh-Punkte pro Bein (Unterschenkel + Fuß) für die Boden-Begrenzung
for v in body_obj.data.vertices:
    if not v.groups:
        continue
    n = names[max(v.groups, key=lambda g: g.weight).group]
    PART_MESH_PTS.setdefault(n, []).append(body_obj.matrix_world @ v.co)
    if n.startswith("Leg_") and n.endswith(("_Tibia", "_Tarsus", "_Femur")):
        leg_id = n.split("_")[1]
        LEG_MESH_PTS.setdefault(leg_id, {}).setdefault(n, []).append(body_obj.matrix_world @ v.co)
GROUND = min(GROUND, min(p.z for d_ in LEG_MESH_PTS.values() for ps in d_.values() for p in ps))
BODY_TOP = max((body_obj.matrix_world @ v.co).z for v in body_obj.data.vertices
               if v.groups and not names[max(v.groups, key=lambda g: g.weight).group].startswith(("Leg_", "Antenna_")))


def mesh_min_z():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_obj.evaluated_get(dg)
    m = ev.to_mesh()
    z = min((body_obj.matrix_world @ v.co).z for v in m.vertices)
    ev.to_mesh_clear()
    return z


tol_c = ST["checks"]["contact_tolerance"] * SIZE
tol_p = ST["checks"]["planted_tolerance"] * SIZE
clips = {
    "Walk": (clip_locomotion(ST["walk"], "forward"), ST["walk"]),
    "Run": (clip_locomotion(ST["run"], "forward"), ST["run"]),
    "TurnLeft": (clip_locomotion(ST["turn"], "turn_left"), ST["turn"]),
    "TurnRight": (clip_locomotion(ST["turn"], "turn_right"), ST["turn"]),
    "Idle": (clip_idle(ST["idle"]), ST["idle"]),
    "Ready": (clip_ready(ST["ready"]), ST["ready"]),
    "Attack1": (clip_attack1(ST["attack1"]), ST["attack1"]),
    "Hit": (clip_hit(ST["hit"]), ST["hit"]),
    "Death": (clip_death(ST["death"], CLEARANCE), ST["death"]),
}
arm.animation_data_create()
report, events = {}, {}
for cname in ST["meta"]["clips"]:
    (N, loop, kind, pose), P = clips[cname]
    full = f"{PREFIX}_{cname}"
    act = bpy.data.actions.get(full) or bpy.data.actions.new(full)
    act.use_fake_user = True
    arm.animation_data.action = act
    feet, tails, ev = {leg: [] for leg in walking}, {}, []
    prev_swing = {}
    for f in range(N + 1):
        pose(f)
        for pb in PB:
            pb.keyframe_insert("rotation_quaternion", frame=f)
            pb.keyframe_insert("location", frame=f)
        bpy.context.view_layer.update()
        if f in (0, N):
            tails[f] = {pb.name: (arm.matrix_world @ pb.tail).copy() for pb in PB}
        for leg in walking:
            sw = False
            if kind == "locomotion":
                sw, _ = phase((f % N) / N, leg_offset(leg, P), P["duty"])
                if prev_swing.get(leg) and not sw and f < N:
                    ev.append({"frame": f, "event": "footstep", "leg": leg})
                prev_swing[leg] = sw
            feet[leg].append((foot(leg).copy(), sw))
    r = {"frames": N, "seconds": round(N / FPS, 3), "loop": loop}
    jump = max((tails[0][n] - tails[N][n]).length for n in tails[0])
    if loop:
        r["loop_max_jump_m"] = round(jump, 5)
        r["loop_ok"] = jump < 1e-4
    if kind == "locomotion":
        floats, strides, omegas = [], [], []
        for leg, s in feet.items():
            st = [p for p, sw in s if not sw]
            if not st:
                continue
            floats.append(max(abs(p.z - REST_FOOT[leg].z) for p in st))
            # Vorwärts: nur die Strecke in Laufrichtung zählt; Drehen: horizontale Strecke
            d = (max(p.x for p in st) - min(p.x for p in st)) if cname in ("Walk", "Run") else \
                max((Vector((a.x - b.x, a.y - b.y, 0))).length for a in st for b in st)
            strides.append(d)
            omegas.append(d / LEG[leg]["R_center"] / (P["duty"] * N / FPS))
        r["foot_contact_max_m"] = round(max(floats), 4)
        r["foot_contact_ok"] = max(floats) <= tol_c
        r["stride_m"] = [round(min(strides), 3), round(max(strides), 3)]
        if cname.startswith("Turn"):
            r["turn_speed_deg_s"] = round(math.degrees(sum(omegas) / len(omegas)), 1)
        else:
            r["move_speed_mps"] = round(sum(strides) / len(strides) / (P["duty"] * N / FPS), 3)
    if kind in ("stand", "stand_return"):
        mv = max((p - REST_FOOT[leg]).length for leg, s in feet.items() for p, _ in s)
        r["feet_moved_max_m"] = round(mv, 4)
        r["feet_planted_ok"] = mv <= tol_p
    if kind == "stand_return":
        r["returns_to_rest"] = jump < 1e-4
    if kind == "death":
        sc.frame_set(N)
        bpy.context.view_layer.update()
        z = mesh_min_z()
        r["final_min_z_vs_ground_m"] = round(z - GROUND, 4)
        r["no_ground_penetration"] = z >= GROUND - tol_c
        ev.append({"frame": N, "event": "dead"})
    if cname == "Attack1":
        ev.append({"frame": P["hit_frame"], "event": "hit"})
    oks = [v for k, v in r.items() if k.endswith("_ok") or k in ("returns_to_rest", "no_ground_penetration")]
    r["ok"] = all(oks)
    report[full] = r
    events[full] = ev
    print("CLIP", full, json.dumps(r, ensure_ascii=False))

arm.animation_data.action = bpy.data.actions[f"{PREFIX}_Walk"]
sc.frame_start, sc.frame_end = 0, ST["walk"]["cycle_frames"]
summary = {"style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}", "variant": ST["meta"]["variant"],
           "walking_legs": walking, "feelers": feelers, "group_A": sorted(group_a),
           "group_B": sorted(set(walking) - group_a), "clips": report,
           "all_ok": all(r["ok"] for r in report.values())}
(OUT / "clips_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "events.json").write_text(json.dumps({"fps": FPS, "clips": events}, indent=2, ensure_ascii=False), encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "crawler_clips.blend"))
print("CLIPS_OK", summary["all_ok"])
