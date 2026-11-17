"""Sechsbeiner-Baukasten: alles, was die Bewegungsmuster des Sechsbeiner-Skeletts (motions/hexapod/*) gemeinsam nutzen.
Entstanden 2026-11-17 aus dem Krabbler-Baukasten (crawler_kit.py) – ab jetzt nur für Sechsbeiner.

Ein Muster-Skript (z. B. ant/ant_clips.py) macht:
    import hexapod_kit as K; K.init(STYLE_DIR); from hexapod_kit import *
    ... Clips definieren (spec-Dicts) ...
    K.bake(clips)

Bausteine: Konfiguration laden/mischen, Bein-Achsen aus der Geometrie, Hüft-Gieren/Heben/Falten,
Planar-IK (Fuß an Zielpunkt), Fühler mit Stabilisierung, Taster, Rumpfwiegen, Boden-Begrenzung,
Backen aller Clips + Selbstprüfung (Bodenkontakt, Schleife, Füße stehen, Boden, Events).
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

R = math.radians
FWD, LEFT, UP = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


# ---------------------------------------------------------------- Konfiguration
def merge(a, b):
    out = copy.deepcopy(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_style(style_dir, creature_toml=None):
    st = tomllib.loads((pathlib.Path(style_dir) / "style.toml").read_text(encoding="utf-8"))
    m = {}
    if creature_toml:
        m = tomllib.loads(pathlib.Path(creature_toml).read_text(encoding="utf-8")).get("motion", {})
    variant = m.get("variant")
    if variant:
        st = merge(st, st["variants"][variant])
    st = merge(st, {k: v for k, v in m.items() if isinstance(v, dict)})
    for sec, parent in st["meta"].get("inherit", {}).items():   # z. B. run/turn erben von walk
        st[sec] = merge(st[parent], st[sec])
    st["meta"]["variant"] = variant
    return st


def init(style_dir):
    """Liest argv (<ausgabe> [<creature.toml>]), lädt Stil + Rig, berechnet Bein-Achsen und Bodenwerte."""
    global OUT, ST, FPS, PREFIX, arm, body_obj, sc, PB, DB, SIZE, walking, feelers, group_a, LEG, thorax_mid
    global REST_FOOT, GROUND, CLEARANCE, BODY_TOP, names
    args = sys.argv[sys.argv.index("--") + 1:]
    OUT = pathlib.Path(args[0]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    ST = load_style(style_dir, args[1] if len(args) > 1 else None)
    FPS = ST["meta"]["fps"]
    PREFIX = ST["meta"]["clip_prefix"]
    arm = bpy.data.objects["Hexapod_Rig"]
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
    thorax_mid = (DB["Thorax"].head_local + DB["Thorax"].tail_local) / 2
    LEG = {}
    for leg in walking + feelers:
        LEG[leg] = _leg_geometry(leg)
        k = LEG[leg]["ik"]
        print(f"  IK {leg}: Streckung in Ruhe {math.hypot(k['uT'], k['wT']) / (k['L1'] + k['L2']):.2f} "
              f"(1.0 = ganz gestreckt), Knie {'oben' if k['knee_up'] else 'unten'}")
    reset()
    bpy.context.view_layer.update()
    REST_FOOT = {leg: foot(leg).copy() for leg in walking}
    names = {g.index: g.name for g in body_obj.vertex_groups}
    for v in body_obj.data.vertices:
        if not v.groups:
            continue
        n = names[max(v.groups, key=lambda g: g.weight).group]
        PART_MESH_PTS.setdefault(n, []).append(body_obj.matrix_world @ v.co)
    leg_pts = [p for n, ps in PART_MESH_PTS.items() if n.startswith("Leg_") for p in ps]
    GROUND = min([p.z for p in REST_FOOT.values()] + [p.z for p in leg_pts])
    body_pts = [p for n, ps in PART_MESH_PTS.items() if not n.startswith(("Leg_", "Antenna_")) for p in ps]
    CLEARANCE = min(p.z for p in body_pts) - GROUND
    BODY_TOP = max(p.z for p in body_pts)


# ---------------------------------------------------------------- Pose-Grundlagen
PART_MESH_PTS = {}


def reset():
    for pb in PB:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()


def local_axis(name, axis_world):
    return (DB[name].matrix_local.to_3x3().inverted() @ axis_world).normalized()


def rot(name, axis_world, angle, mul=True):
    """Drehung um eine Achse im Armature-Raum (Ruhelage) – wird auf die bestehende Pose multipliziert."""
    q = Quaternion(local_axis(name, axis_world), angle)
    PB[name].rotation_quaternion = (PB[name].rotation_quaternion @ q) if mul else q


def move(name, vec_world):
    PB[name].location = DB[name].matrix_local.to_3x3().inverted() @ vec_world


def foot(leg):
    return arm.matrix_world @ PB[f"Leg_{leg}_Tarsus"].tail


def ease(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def phase(t, offset, duty):
    p = (t + offset) % 1.0
    return (False, p / duty) if p < duty else (True, (p - duty) / (1 - duty))


# ---------------------------------------------------------------- Beine
def _leg_geometry(leg):
    b = {p: DB[f"Leg_{leg}_{p}"] for p in ("Coxa", "Femur", "Tibia", "Tarsus")}
    root, tip, fh = b["Coxa"].head_local, b["Tarsus"].tail_local, b["Femur"].head_local
    knee = b["Femur"].tail_local
    h = Vector((tip.x - root.x, tip.y - root.y, 0))
    dir_h = h.normalized() if h.length > 1e-6 else LEFT
    lift_axis = UP.cross(dir_h).normalized()
    lift_sign = 1 if (Quaternion(lift_axis, 0.2) @ (tip - fh)).z > (tip - fh).z else -1
    back_sign = 1 if (Quaternion(UP, 0.2) @ (tip - root)).x < (tip - root).x else -1
    # Planar-IK in DERSELBEN Ebene, in der set_leg hebt: waagerecht = dir_h (Hüfte→Fuß), senkrecht = UP.
    # (Eine andere Ebene, z. B. Femur-Kopf→Fuß, passt wegen des Coxa-Versatzes nicht → Füße schweben.)
    hf = dir_h
    uK, wK = (knee - fh).dot(hf), (knee - fh).z
    uT, wT = (tip - fh).dot(hf), (tip - fh).z
    L1 = math.hypot(uK, wK)
    L2 = math.hypot(uT - uK, wT - wK)
    a1 = math.atan2(wK, uK)
    a2 = math.atan2(wT - wK, uT - uK)
    # Welcher IK-Ast entspricht der Ruhepose? Bei (fast) gestrecktem Bein: Knie oben (Krabbler-typisch)
    cross = uT * wK - wT * uK
    knee_up = cross > -0.02 * (L1 * L2)
    return {"r": h.length, "phi": math.atan2(h.y, h.x), "back_sign": back_sign,
            "lift_axis": lift_axis * lift_sign, "lift_sign": lift_sign,
            "R_center": (Vector((tip.x, tip.y, 0)) - Vector((thorax_mid.x, thorax_mid.y, 0))).length,
            "ik": {"uT": uT, "wT": wT, "L1": L1, "L2": L2, "a1": a1, "a2": a2, "knee_up": knee_up,
                   "lateral": abs(math.sin(math.atan2(hf.y, hf.x)))}}


def amp(leg, stride, max_deg):
    """Hüft-Schwenkwinkel, damit der Fuß 'stride' (Anteil Größe) in X zurücklegt (gleich für alle Beine)."""
    L = LEG[leg]
    ratio = stride * SIZE / max(1e-6, 2 * L["r"] * abs(math.sin(L["phi"])))
    return min(math.asin(min(1.0, ratio)), R(max_deg))


def set_leg(leg, back=0.0, lift=0.0, fold=0.0, tuck=0.0):
    L = LEG[leg]
    rot(f"Leg_{leg}_Coxa", UP, L["back_sign"] * back + tuck, mul=False)
    rot(f"Leg_{leg}_Femur", L["lift_axis"], lift, mul=False)
    rot(f"Leg_{leg}_Tibia", L["lift_axis"], fold, mul=False)


def ik_angles(leg, du=0.0, dw=0.0):
    """Planar-IK: Fuß um du (weiter raus +) und dw (höher +) relativ zur Ruhelage verschieben.
    Liefert (Femur-Δ, Tibia-Δ) im 'Heben'-Sinn von set_leg."""
    k = LEG[leg]["ik"]
    u, w = k["uT"] + du, k["wT"] + dw
    D = max(abs(k["L1"] - k["L2"]) + 1e-6, min(k["L1"] + k["L2"] - 1e-6, math.hypot(u, w)))
    beta = math.atan2(w, u)
    gamma = math.acos(max(-1.0, min(1.0, (k["L1"] ** 2 + D ** 2 - k["L2"] ** 2) / (2 * k["L1"] * D))))
    a1n = beta + gamma if k["knee_up"] else beta - gamma
    ku, kw = k["L1"] * math.cos(a1n), k["L1"] * math.sin(a1n)
    a2n = math.atan2(w - kw, u - ku)
    # IK rechnet Winkel mathematisch positiv "nach oben"; lift_axis ist so orientiert, dass +Winkel hebt
    d1 = a1n - k["a1"]
    d2 = (a2n - k["a2"]) - d1
    return d1, d2


def ik_limits(leg, margin=0.94):
    """Wie weit kann das Bein reichen? → (max. du nach außen, max. Körperhebung h) in Metern.
    margin < 1 hält das Bein leicht gebeugt (gestreckt sieht steif aus und die IK springt)."""
    k = LEG[leg]["ik"]
    # Beine, die schon in Ruhe gestreckter sind als 'margin', dürfen nicht weiter gestreckt werden
    Dm = max((k["L1"] + k["L2"]) * margin, math.hypot(k["uT"], k["wT"]))
    du_out = math.sqrt(max(0.0, Dm ** 2 - k["wT"] ** 2)) - k["uT"]
    h_max = math.sqrt(max(0.0, Dm ** 2 - k["uT"] ** 2)) + k["wT"]
    return max(0.0, du_out), max(0.0, h_max)


def max_body_raise():
    return min(ik_limits(leg)[1] for leg in walking)


def set_leg_ik(leg, back=0.0, du=0.0, dw=0.0, tuck=0.0):
    """Hüfte gieren (back) + Fuß per IK verschieben: du = Reichweite (+ nach außen), dw = Höhe (+ hoch)."""
    d1, d2 = ik_angles(leg, du, dw)
    set_leg(leg, back, d1, d2, tuck)


def foot_reachable(leg, dx, dy, margin=0.94):
    """Ist die Fußposition (dx, dy gegenüber Ruhelage) ohne Überstrecken erreichbar?"""
    return _foot_solve(leg, dx, dy)[1] <= ik_limits(leg, margin)[0] + 1e-6


def max_foot_shift(leg, ux, uy, limit):
    """Wie weit (Meter, ≤ limit) kann der Fuß in Richtung (ux, uy) verschoben werden? (Bisektion)"""
    if foot_reachable(leg, ux * limit, uy * limit):
        return limit
    lo, hi = 0.0, limit
    for _ in range(20):
        mid = (lo + hi) / 2
        if foot_reachable(leg, ux * mid, uy * mid):
            lo = mid
        else:
            hi = mid
    return lo


def _foot_solve(leg, dx, dy):
    root = DB[f"Leg_{leg}_Coxa"].head_local
    tip = DB[f"Leg_{leg}_Tarsus"].tail_local
    fh = DB[f"Leg_{leg}_Femur"].head_local
    r2 = Vector((root.x, root.y))
    v0 = Vector((tip.x - root.x, tip.y - root.y))
    v1 = v0 + Vector((dx, dy))
    psi = math.atan2(v0.x * v1.y - v0.y * v1.x, v0.dot(v1))
    # exakt: der Femur-Kopf liegt seitlich versetzt zur Hüfte und dreht beim Gieren mit →
    # psi so nachführen, dass der seitliche Versatz Ziel↔Femur-Kopf dem der Ruhelage entspricht
    h0 = Vector((v0.x, v0.y)).normalized()
    n0 = Vector((-h0.y, h0.x))
    f2 = Vector((fh.x, fh.y))
    tgt = Vector((tip.x, tip.y)) + Vector((dx, dy))
    e0 = (Vector((tip.x, tip.y)) - f2).dot(n0)

    def rot2(v, a):
        return Vector((v.x * math.cos(a) - v.y * math.sin(a), v.x * math.sin(a) + v.y * math.cos(a)))
    for _ in range(5):
        fp = r2 + rot2(f2 - r2, psi)
        n1 = rot2(n0, psi)
        err = (tgt - fp).dot(n1) - e0
        psi += err / max(1e-6, (tgt - r2).length)
    fp = r2 + rot2(f2 - r2, psi)
    du = (tgt - fp).dot(rot2(h0, psi)) - LEG[leg]["ik"]["uT"]
    return psi, du


def set_foot(leg, dx=0.0, dy=0.0, dw=0.0, du_max=None):
    """Fuß-IK: Fuß um (dx, dy) waagerecht (Armature-Raum, Meter) und dw senkrecht gegenüber Ruhelage
    verschieben. Hüfte giert in Zielrichtung, Femur/Tibia stellen die Entfernung + Höhe ein."""
    psi, du = _foot_solve(leg, dx, dy)
    if du_max is not None:
        du = min(du, du_max)
    rot(f"Leg_{leg}_Coxa", UP, psi, mul=False)
    d1, d2 = ik_angles(leg, du, dw)
    rot(f"Leg_{leg}_Femur", LEG[leg]["lift_axis"], d1, mul=False)
    rot(f"Leg_{leg}_Tibia", LEG[leg]["lift_axis"], d2, mul=False)


def leg_offset(leg, P):
    return (0.0 if leg in group_a else 0.5) + P["wave_offset"] * (int(leg[1]) - 2)


def gait(t, P, mode="forward"):
    """Vorwärts-/Dreh-Gang über Hüft-Gieren (Ant-Prinzip)."""
    for leg in walking:
        side = 1 if leg[0] == "L" else -1
        swing, s = phase(t, leg_offset(leg, P), P["duty"])
        A = amp(leg, P["stride"], P["stride_max_deg"])
        d = -1 if (mode == "turn_left" and side > 0) or (mode == "turn_right" and side < 0) else 1
        back = ((-A + 2 * A * s) if not swing else (A - 2 * A * ease(s))) * d
        lift = R(P["lift_deg"]) * math.sin(math.pi * s) if swing else 0.0
        fold = R(P["tibia_fold_deg"]) * math.sin(math.pi * s) if swing else 0.0
        set_leg(leg, back, lift, fold)


# ---------------------------------------------------------------- Kopf, Fühler, Taster, Rumpf
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


# ---------------------------------------------------------------- Boden
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
    return mesh_part_lowest_z([f"Leg_{leg}_{p}" for p in ("Femur", "Tibia", "Tarsus")])


def fold_ground_clamped(leg, lift, fold, margin=0.005, max_extra_deg=110):
    """Bein heben/falten; geht das Bein-Mesh unter den Boden, wird das Knie per Bisektion gerade so weit
    angehoben, dass es aufliegt (Tier knickt unter seinem Gewicht ein)."""
    set_leg(leg, 0.0, lift, fold)
    bpy.context.view_layer.update()
    floor = GROUND + margin * SIZE
    if leg_lowest_z(leg) >= floor:
        return
    lo, hi = 0.0, R(max_extra_deg)
    for _ in range(12):
        mid = (lo + hi) / 2
        set_leg(leg, 0.0, lift + mid, fold)
        bpy.context.view_layer.update()
        if leg_lowest_z(leg) >= floor:
            hi = mid
        else:
            lo = mid
    set_leg(leg, 0.0, lift + hi, fold)


def antennae_ground_safe(t, deg, speed, tip, stabilize, k, max_droop=80):
    """Fühler-Klappwinkel so wählen, dass die Fühler den größten Bodenabstand haben."""
    best = None
    for cand in range(-max_droop, max_droop + 1, 10):
        antennae(t, deg, speed, tip, stabilize, droop_deg=cand * k)
        bpy.context.view_layer.update()
        z = mesh_part_lowest_z(("Antenna_L_1", "Antenna_L_2", "Antenna_R_1", "Antenna_R_2"))
        if best is None or z > best[0] + 1e-4 or (abs(z - best[0]) <= 1e-4 and abs(cand) < abs(best[1])):
            best = (z, cand)
    antennae(t, deg, speed, tip, stabilize, droop_deg=best[1] * k)


def death_flip(P, curl_fn=None):
    """Gemeinsamer Tod: auf den Rücken kippen per Root-Drehung (keine Gelenk-Lücken), Beine einrollen."""
    N, c0, c1 = P["frames"], P["collapse_start"], P["collapse_end"]
    h0 = DB["Root"].head_local.copy()
    pivot = Vector((thorax_mid.x, 0, (BODY_TOP + GROUND) / 2))

    def pose(f):
        reset()
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        ang = math.pi * k * P["flip_side"]
        q = Quaternion(FWD, ang)
        loc = (pivot - h0) - q @ (pivot - h0) + UP * P["flip_hop"] * SIZE * math.sin(math.pi * k)
        if f > c1:
            loc += UP * P["flip_hop"] * 0.25 * SIZE * max(0.0, math.sin(math.pi * (f - c1) / 5)) * (f - c1 < 5)
        rot("Root", FWD, ang, mul=False)
        move("Root", loc)
        rot("Head", LEFT, -R(8) * jolt - R(10) * k)
        rot("Abdomen_1", LEFT, -R(10) * k)
        curl = ease((f - c0 * 1.5) / (c1 - c0)) if f > c0 * 1.5 else 0.0
        for leg in walking + feelers:
            twitch = 0.0
            if leg == walking[-2] and P["twitch_frame"] - 2 <= f <= P["twitch_frame"] + 2:
                twitch = R(P["twitch_deg"]) * math.sin(math.pi * (f - P["twitch_frame"] + 2) / 4)
            set_leg(leg, back=0.0, lift=-R(P["femur_curl_deg"]) * curl + twitch, fold=-R(P["tibia_curl_deg"]) * curl)
            if curl_fn:
                curl_fn(leg, curl, f)
        antennae_ground_safe(0, 0, 1, 0.4, 0.0, k)
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "events": [{"frame": N, "event": "dead"}]}


def mesh_min_z():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_obj.evaluated_get(dg)
    m = ev.to_mesh()
    z = min((body_obj.matrix_world @ v.co).z for v in m.vertices)
    ev.to_mesh_clear()
    return z


# ---------------------------------------------------------------- Backen + Selbstprüfung
def bake(clips):
    """clips: {Name: spec}. spec = {N, loop, kind, pose(f), swing(leg, f)->bool (Locomotion),
    axis: "x" | "y" | "turn", events: [...], planted: [Beine] (Standard: alle Laufbeine – z. B. beim
    Aufbäumen nur die tragenden) }"""
    tol_c = ST["checks"]["contact_tolerance"] * SIZE
    tol_p = ST["checks"]["planted_tolerance"] * SIZE
    arm.animation_data_create()
    report, events = {}, {}
    for cname in ST["meta"]["clips"]:
        spec = clips[cname]
        N, loop, kind, pose = spec["N"], spec["loop"], spec["kind"], spec["pose"]
        full = f"{PREFIX}_{cname}"
        act = bpy.data.actions.get(full) or bpy.data.actions.new(full)
        act.use_fake_user = True
        arm.animation_data.action = act
        feet, tails, ev = {leg: [] for leg in walking}, {}, list(spec.get("events", []))
        prev = {}
        for f in range(N + 1):
            pose(f)
            for pb in PB:
                pb.keyframe_insert("rotation_quaternion", frame=f)
                pb.keyframe_insert("location", frame=f)
            bpy.context.view_layer.update()
            if f in (0, N):
                tails[f] = {pb.name: (arm.matrix_world @ pb.tail).copy() for pb in PB}
            for leg in walking:
                sw = spec["swing"](leg, f) if kind == "locomotion" else False
                if kind == "locomotion" and prev.get(leg) and not sw and f < N:
                    ev.append({"frame": f, "event": "footstep", "leg": leg})
                prev[leg] = sw
                feet[leg].append((foot(leg).copy(), sw))
        r = {"frames": N, "seconds": round(N / FPS, 3), "loop": loop}
        jump = max((tails[0][n] - tails[N][n]).length for n in tails[0])
        if loop:
            r["loop_max_jump_m"] = round(jump, 5)
            r["loop_ok"] = jump < 1e-4
        if kind == "locomotion":
            floats, strides, omegas = [], [], []
            ax = spec.get("axis", "x")
            for leg, s in feet.items():
                st = [p for p, sw in s if not sw]
                if not st:
                    continue
                floats.append(max(abs(p.z - REST_FOOT[leg].z) for p in st))
                if ax in ("x", "y"):
                    d = max(getattr(p, ax) for p in st) - min(getattr(p, ax) for p in st)
                else:
                    d = max((Vector((a.x - b.x, a.y - b.y, 0))).length for a in st for b in st)
                strides.append(d)
                omegas.append(d / LEG[leg]["R_center"] / (spec["duty"] * N / FPS))
            r["foot_contact_max_m"] = round(max(floats), 4)
            r["foot_contact_ok"] = max(floats) <= tol_c
            r["stride_m"] = [round(min(strides), 3), round(max(strides), 3)]
            # Bewegt sich überhaupt etwas? (Stillstand würde sonst jede Bodenprüfung bestehen)
            r["moves_ok"] = min(strides) >= ST["checks"].get("min_stride", 0.03) * SIZE
            if ax == "turn":
                r["turn_speed_deg_s"] = round(math.degrees(sum(omegas) / len(omegas)), 1)
            else:
                r["move_speed_mps"] = round(sum(strides) / len(strides) / (spec["duty"] * N / FPS), 3)
                r["move_axis"] = ax
        if kind in ("stand", "stand_return"):
            planted = spec.get("planted", walking)       # z. B. Aufbäumen: nur die tragenden Beine
            mv = max((p - REST_FOOT[leg]).length for leg, s in feet.items() if leg in planted for p, _ in s)
            if len(planted) < len(walking):
                r["planted_legs"] = planted
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
        oks = [v for k_, v in r.items() if k_.endswith("_ok") or k_ in ("returns_to_rest", "no_ground_penetration")]
        r["ok"] = all(oks)
        report[full] = r
        events[full] = ev
        print("CLIP", full, json.dumps(r, ensure_ascii=False))
    first = ST["meta"]["clips"][0]
    arm.animation_data.action = bpy.data.actions[f"{PREFIX}_{first}"]
    summary = {"style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}", "variant": ST["meta"]["variant"],
               "walking_legs": walking, "feelers": feelers, "clips": report,
               "all_ok": all(r["ok"] for r in report.values())}
    (OUT / "clips_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "events.json").write_text(json.dumps({"fps": FPS, "clips": events}, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "hexapod_clips.blend"))
    print("CLIPS_OK", summary["all_ok"])
