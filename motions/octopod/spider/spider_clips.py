"""Bewegungsmuster octopod/spider: Vorwärtsgang als alternierender Vierfuß (Welle hinten → vorn), Ganzkörper-Angriffe.

& "D:\\Blender\\blender.exe" -b <octopod_rigged.blend> -P motions/octopod/spider/spider_clips.py -- <ausgabe> [<creature.toml>]
Gemeinsame Bausteine: ../octopod_kit.py (Fuß-IK, Backen, Selbstprüfung). Alles Spinnen-Eigene steht hier
(Kippen ums tragende Paar ist aus crab_clips.py KOPIERT, nicht importiert – eigener Clip-Code pro Muster).
Recherche + Bewegungsregeln: RESEARCH.md · Werte: style.toml

Grundidee: Jede Pose = Körperpose (Vorderkörper/Thorax: Versatz, Gieren, Kippen um einen Drehpunkt) + Hinterleib
(relativ, mit Verzögerung) + Fußziele. Standfüße bekommen Ziele im Armature-Raum (Welt) und werden per Fuß-IK
durch den bewegten Körper hindurch exakt dorthin gesetzt (plant). Schwebende Beine bekommen Ziele im Körper-Raum.
"""
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import octopod_kit as K  # noqa: E402

K.init(HERE)
from octopod_kit import *  # noqa: E402,F401,F403
from octopod_kit import ST, LEG, walking, SIZE, R, FWD, LEFT, UP, ease, phase  # noqa: E402

TAU = 2 * math.pi


def side_of(leg):
    return 1 if leg[0] == "L" else -1


def slot(leg):
    return int(leg[1])


# ---------------------------------------------------------------- Ruhe, Boden, Drehpunkte
REST_TIP = {leg: DB[f"Leg_{leg}_Tarsus"].tail_local.copy() for leg in walking}   # Armature-Raum, Ruhe
GZ = min(p.z for p in REST_TIP.values())                                          # Boden = tiefste Fußspitze
if ST["legs"].get("feet_to_ground", True):
    # Prüfungen des Baukastens messen gegen REST_FOOT → auf den Boden legen (Standfüße stehen immer am Boden)
    for leg in walking:
        K.REST_FOOT[leg].z = (arm.matrix_world @ Vector((0, 0, GZ))).z
ROOTS = {leg: DB[f"Leg_{leg}_Coxa"].head_local.copy() for leg in walking}
PIV = sum(ROOTS.values(), Vector()) / len(ROOTS)            # Mitte des Vorderkörpers (Beinwurzeln)
BODY_H = PIV.z - GZ                                          # Rumpfhöhe über dem Boden
TH = DB["Thorax"]
TH_R = TH.matrix_local.to_3x3()
print(f"  spider: Boden {GZ:.3f}, Vorderkörper-Mitte {tuple(round(c, 3) for c in PIV)}, Rumpfhöhe {BODY_H:.3f}, "
      f"Fuß-Abstand zum Boden in Ruhe: { {l: round(REST_TIP[l].z - GZ, 3) for l in walking} }")


def ground(leg, dx=0.0, dy=0.0, dz=0.0):
    r = REST_TIP[leg]
    return Vector((r.x + dx, r.y + dy, GZ + dz))


def body(dx=0.0, dy=0.0, dz=0.0, yaw=0.0, pitch=0.0, roll=0.0, pivot=None):
    """Vorderkörper (Thorax + alles daran) als Ganzes: Versatz + Drehung um 'pivot' (Standard: Mitte der
    Beinwurzeln). pitch + = Vorderseite hoch, yaw + = nach links, roll + = linke Seite runter."""
    pivot = PIV if pivot is None else pivot
    q = Quaternion(UP, yaw) @ Quaternion(LEFT, -pitch) @ Quaternion(FWD, roll)
    PB["Thorax"].rotation_quaternion = (TH_R.inverted() @ q.to_matrix() @ TH_R).to_quaternion()
    h = TH.head_local
    move("Thorax", (pivot - h) - q @ (pivot - h) + Vector((dx, dy, dz)))


def abdomen(yaw=0.0, pitch=0.0):
    """Hinterleib (samt Eierhaufen, starr an Abdomen_1) relativ zum Vorderkörper, Drehpunkt = Stiel."""
    rot("Abdomen_1", UP, yaw, mul=False)
    rot("Abdomen_1", LEFT, -pitch)


def body_matrix():
    bpy.context.view_layer.update()
    return PB["Thorax"].matrix @ TH.matrix_local.inverted()      # Ruhe-Raum → Pose-Raum des Vorderkörpers


def plant(leg, T, M):
    """Fuß an Welt-Ziel T (Armature-Raum) – durch den bewegten Körper hindurch (M = body_matrix())."""
    d = M.inverted() @ T - REST_TIP[leg]
    set_foot(leg, d.x, d.y, d.z)


def local_foot(leg, d):
    """Fuß im Körper-Raum um d (Vector) gegenüber Ruhe verschieben (Bein in der Luft, bewegt sich mit dem Körper)."""
    set_foot(leg, d.x, d.y, d.z)


def world_of_local(leg, d, M):
    return M @ (REST_TIP[leg] + d)


def lerp(a, b, k):
    return a + (b - a) * k


def smooth_seg(f, keys):
    """Stückweise weiche Interpolation: keys = [(frame, wert), …] (Werte: float oder Vector)."""
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1:
            return lerp(v0, v1, ease((f - f0) / max(1e-9, f1 - f0)))
    return keys[-1][1]


# ---------------------------------------------------------------- Gang
def leg_cfg(leg, P):
    front = slot(leg) == 1
    duty = P["duty_front"] if front else P["duty"]
    off = (0.0 if leg in K.group_a else 0.5) + P["ripple"] * (slot(leg) - 1)   # Bein 4 setzt zuerst auf
    return {"duty": duty, "off": off, "lift": (P["lift_front"] if front else P["lift"]) * SIZE,
            "reach": (P.get("front_reach", 0.0) if front else 0.0) * SIZE}


def swing_of(P):
    N = P["cycle_frames"]
    return lambda leg, f: phase((f % N) / N, leg_cfg(leg, P)["off"], leg_cfg(leg, P)["duty"])[0]


def body_follow(t, P, lead=0.0, trail=0.0):
    """Vorderkörper giert im Takt, Hinterleib folgt verzögert (Welt-Ausschlag größer, Phase später)."""
    yaw_t = R(P["body_yaw_deg"]) * math.sin(TAU * t)
    yaw_a = R(P["abdomen_sway_deg"]) * math.sin(TAU * (t - P["abdomen_lag"]))
    bob_a = R(P["abdomen_bob_deg"]) * math.sin(TAU * 2 * (t - P["abdomen_lag"]))
    return yaw_t + lead, (yaw_a - yaw_t) - lead - trail, bob_a


def stance_centers(P, S):
    """Arbeitsbereich je Bein: reicht ein Bein vorn nicht weit genug (gestreckt), wird sein Bereich nach hinten
    verlegt (wie crab nach innen) – sonst schwebt der Fuß am vorderen Ende des Schritts."""
    cx = {}
    for leg in walking:
        c = leg_cfg(leg, P)
        half = S * c["duty"] / P["duty"] / 2
        want = c["reach"] + half
        fwd = K.max_foot_shift(leg, 1.0, 0.0, want)
        cx[leg] = c["reach"] - (want - fwd) - 0.004 * SIZE * (fwd < want)
    print(f"  spider {P['cycle_frames']} Frames: Schritt {S:.3f} m, Arbeitsbereich verschoben: "
          f"{ {l: round(v, 3) for l, v in cx.items() if abs(v) > 1e-4} }")
    return cx


def clip_walk(P):
    N = P["cycle_frames"]
    S = P["stride"] * SIZE
    drop = P["body_drop"] * BODY_H
    CX = stance_centers(P, S)

    def pose(f):
        t = (f % N) / N
        reset()
        yaw_t, yaw_a, bob_a = body_follow(t, P)
        body(dz=-drop + P["body_bob"] * SIZE * math.sin(TAU * 2 * t), yaw=yaw_t)
        abdomen(yaw_a, bob_a)
        M = body_matrix()
        for leg in walking:
            c = leg_cfg(leg, P)
            sw, s = phase(t, c["off"], c["duty"])
            S_leg = S * c["duty"] / P["duty"]                   # gleiche Körpergeschwindigkeit für alle Beine
            x = (S_leg / 2 - S_leg * s) if not sw else (-S_leg / 2 + S_leg * ease(s))
            z = c["lift"] * math.sin(math.pi * s) if sw else 0.0
            plant(leg, ground(leg, CX[leg] + x, side_of(leg) * P["spread"] * SIZE, z), M)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "axis": "x",
            "swing": swing_of(P)}


def clip_turn(P, direction):
    """direction +1 = links (gegen den Uhrzeigersinn von oben), −1 = rechts. Standfüße drehen relativ zum Körper
    gegen die Drehrichtung um die Körpermitte → Außenbeine treten im Schwung vor, Innenbeine zurück."""
    N = P["cycle_frames"]
    TH_C = R(P["turn_deg_cycle"])
    c0 = Vector((PIV.x, PIV.y, 0.0))

    def foot_at(leg, ang, z=0.0):
        r = REST_TIP[leg]
        v = Vector((r.x, r.y, 0.0)) - c0
        v = Quaternion(UP, ang) @ v
        return Vector((c0.x + v.x, c0.y + v.y, GZ + z))

    def pose(f):
        t = (f % N) / N
        reset()
        wob = R(1.5) * math.sin(TAU * t)
        body(yaw=direction * R(P["lead_deg"]) + wob, dz=P["body_bob"] * SIZE * math.sin(TAU * 2 * t))
        abdomen(-direction * (R(P["lead_deg"]) + R(P["abdomen_trail_deg"])) - wob * 0.6,
                R(P["abdomen_bob_deg"]) * math.sin(TAU * 2 * (t - P["abdomen_lag"])))
        M = body_matrix()
        for leg in walking:
            c = leg_cfg(leg, P)
            sw, s = phase(t, c["off"], c["duty"])
            arc = TH_C * c["duty"]                               # Winkel, den der Fuß im Stand relativ überstreicht
            a = (arc / 2 - arc * s) if not sw else (-arc / 2 + arc * ease(s))
            z = c["lift"] * math.sin(math.pi * s) if sw else 0.0
            plant(leg, foot_at(leg, direction * a, z), M)     # links: Füße wandern im Uhrzeigersinn
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "axis": "turn",
            "swing": swing_of(P), "turn_dir": direction}


# ---------------------------------------------------------------- Stehen, Drohen
def clip_idle(P):
    N = P["frames"]
    taps = {"L1": (0.12, 0.30), "R1": (0.52, 0.68)}             # Bein I tastet/tippt (zweimal kurz)
    step = P["step_leg"]

    def pose(f):
        t = f / N
        reset()
        body(dz=P["body_sway"] * SIZE * math.sin(TAU * t), yaw=R(0.6) * math.sin(TAU * t + 1.0))
        abdomen(R(0.5) * math.sin(TAU * t - 0.8), R(P["breath_deg"]) * math.sin(TAU * t))
        M = body_matrix()
        for leg in walking:
            T = ground(leg)
            if leg in taps:
                a, b = taps[leg]
                if a < t < b:
                    u = (t - a) / (b - a)
                    h = abs(math.sin(TAU * u))                    # zwei Tipper
                    T = ground(leg, P["tap_reach"] * SIZE * math.sin(math.pi * u), 0.0, P["tap_lift"] * SIZE * h)
            if leg == step and 0.78 < t < 0.94:                  # ein Bein nachsetzen (heben, leicht vor, zurück)
                u = (t - 0.78) / 0.16
                T = ground(leg, 0.02 * SIZE * math.sin(math.pi * u), 0.0, P["step_lift"] * SIZE * math.sin(math.pi * u))
            plant(leg, T, M)
    planted = [l for l in walking if l not in taps and l != step]
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "planted": planted}


def rear_split(lift_slots=(1, 2)):
    carry = [l for l in walking if slot(l) not in lift_slots]
    lifted = [l for l in walking if slot(l) in lift_slots]
    front_carry = min(slot(l) for l in carry)
    hips = [ROOTS[l] for l in carry if slot(l) == front_carry]
    pivot = sum(hips, Vector()) / len(hips)                  # Kippachse = Hüftlinie des vordersten tragenden Paars
    return carry, lifted, Vector((pivot.x, 0.0, pivot.z))


def carry_error(carry, targets):
    bpy.context.view_layer.update()
    return max((arm.matrix_world.inverted() @ foot(l) - targets[l]).length for l in carry)


def max_pitch(pose_fn, carry, targets, want):
    """Größter Kippwinkel ≤ want, bei dem die tragenden Füße noch exakt stehen (Bisektion, wie crab)."""
    tol = ST["checks"]["planted_tolerance"] * SIZE * 0.5
    reset(); pose_fn(want)
    if carry_error(carry, targets) <= tol:
        return want
    lo, hi = 0.0, want
    for _ in range(16):
        mid = (lo + hi) / 2
        reset(); pose_fn(mid)
        lo, hi = (mid, hi) if carry_error(carry, targets) <= tol else (lo, mid)
    return lo


CARRY, LIFTED, HIP = rear_split()


def abdomen_floor_ok(margin=0.02):
    bpy.context.view_layer.update()
    return K.mesh_part_lowest_z(["Abdomen_1", "Abdomen_2"]) >= GZ + margin * SIZE


def rear_pose(pitch, P, raise_=0.0, dx=0.0, counter=None, k_front=1.0, tremble=0.0):
    """Aufbäumen um die Hüftlinie von Bein III: tragende Füße stehen exakt, I+II hoch und weit gespreizt."""
    counter = P["abdomen_counter"] if counter is None else counter
    body(dx=dx, dz=raise_ * SIZE, pitch=pitch + tremble, pivot=HIP)
    abdomen(0.0, -pitch * counter)
    M = body_matrix()
    for leg in CARRY:
        plant(leg, ground(leg), M)
    for leg in LIFTED:
        s = side_of(leg)
        if slot(leg) == 1:
            d = Vector((P["front_fwd"], s * P["front_out"], P["front_up"])) * SIZE
        else:
            d = Vector((P["second_fwd"], s * P["second_out"], P["second_up"])) * SIZE
        local_foot(leg, d * k_front + Vector((0, 0, (GZ - REST_TIP[leg].z))) * (1 - k_front))
    return M


def clip_ready(P):
    N = P["frames"]
    want = R(P["rear_pitch_deg"])
    targets = {l: ground(l) for l in CARRY}
    pitch = max_pitch(lambda p: rear_pose(p, P, P["body_raise"]), CARRY, targets, want)
    # Hinterleib so weit gegendrehen, dass er den Boden nicht berührt
    counter = P["abdomen_counter"]
    reset(); rear_pose(pitch, P, P["body_raise"], counter=counter)
    while not abdomen_floor_ok() and counter < 1.2:
        counter += 0.05
        reset(); rear_pose(pitch, P, P["body_raise"], counter=counter)
    print(f"  spider ready: aufbäumen auf {CARRY}, Kippwinkel {math.degrees(pitch):.1f}° (gewünscht "
          f"{P['rear_pitch_deg']}°), Hinterleib-Gegendrehung {counter:.2f}")
    INFO["Ready"] = {"pitch_deg": round(math.degrees(pitch), 1), "abdomen_counter": round(counter, 2)}

    def pose(f):
        t = f / N
        reset()
        tr = R(P["tremble_deg"]) * math.sin(TAU * P["tremble_speed"] * t)
        rear_pose(pitch, P, P["body_raise"], counter=counter, tremble=tr * 0.4)
        # Vorderbeine zittern/wiegen zusätzlich (Körper-Raum)
        for leg in LIFTED:
            s = side_of(leg)
            ph = TAU * P["tremble_speed"] * t + (0.0 if s > 0 else 1.3) + slot(leg)
            P_ = P
            base = (Vector((P_["front_fwd"], s * P_["front_out"], P_["front_up"])) if slot(leg) == 1 else
                    Vector((P_["second_fwd"], s * P_["second_out"], P_["second_up"]))) * SIZE
            local_foot(leg, base + Vector((0.0, s * 0.012, 0.018)) * SIZE * math.sin(ph))
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "planted": CARRY}


# ---------------------------------------------------------------- Angriffe
def clip_attack1(P):
    """Ausfall-Biss: ausholen (aufbäumen + zurück) → Zustoß nach vorn-unten, Bein I+II schließen als Käfig über dem
    Ziel → festhalten + schütteln → zurück in die Ruhe. Tragend: III/IV (Füße stehen exakt)."""
    N, w, s_, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    R_ = ST["ready"]
    targets = {l: ground(l) for l in CARRY}
    pw = max_pitch(lambda p: rear_pose(p, R_, 0.0, dx=-P["windup_back"] * SIZE), CARRY, targets,
                   R(P["windup_pitch_deg"]))

    # Zustoß: wie weit trägt III/IV den Körper nach vorn? (Bisektion über dx)
    def strike_body(lunge):
        body(dx=lunge, dz=-P["strike_drop"] * SIZE, pitch=R(P["strike_pitch_deg"]))
        M = body_matrix()
        for leg in CARRY:
            plant(leg, ground(leg), M)
    want = P["strike_lunge"] * SIZE
    reset(); strike_body(want)
    lunge = want
    if carry_error(CARRY, targets) > ST["checks"]["planted_tolerance"] * SIZE * 0.5:
        lo, hi = 0.0, want
        for _ in range(16):
            mid = (lo + hi) / 2
            reset(); strike_body(mid)
            lo, hi = (mid, hi) if carry_error(CARRY, targets) <= ST["checks"]["planted_tolerance"] * SIZE * 0.5 \
                else (lo, mid)
        lunge = lo
    head_x = max(v.x for v in (DB["Head"].tail_local,))
    print(f"  spider attack1: ausholen {math.degrees(pw):.1f}°, Zustoß {lunge / SIZE:.2f} × Größe "
          f"(gewünscht {P['strike_lunge']})")
    INFO["Attack1"] = {"windup_pitch_deg": round(math.degrees(pw), 1), "lunge_size": round(lunge / SIZE, 3)}

    def cage_target(leg, k_close, fwd):
        r = REST_TIP[leg]
        return Vector((max(r.x, head_x) + fwd * SIZE + lunge, r.y * (1 - k_close), GZ))

    keys_dx = [(0, 0.0), (w, -P["windup_back"] * SIZE), (s_, lunge), (h, lunge), (N, 0.0)]
    keys_p = [(0, 0.0), (w, pw), (s_, R(P["strike_pitch_deg"])), (h, R(P["strike_pitch_deg"])), (N, 0.0)]
    keys_dz = [(0, 0.0), (w, 0.0), (s_, -P["strike_drop"] * SIZE), (h, -P["strike_drop"] * SIZE), (N, 0.0)]

    def pose(f):
        reset()
        dx, pitch, dz = smooth_seg(f, keys_dx), smooth_seg(f, keys_p), smooth_seg(f, keys_dz)
        shake = R(P["shake_deg"]) * math.sin(TAU * (f - s_) / 3.0) * (s_ < f < h)
        body(dx=dx, dz=dz, pitch=pitch, yaw=shake, pivot=HIP)
        abdomen(-shake * 1.5, -pitch * (P["abdomen_counter"] if pitch > 0 else 0.3))   # Hinterleib bleibt tiefer/ruhiger
        M = body_matrix()
        for leg in CARRY:
            plant(leg, ground(leg), M)
        for leg in LIFTED:
            s = side_of(leg)
            up = (Vector((R_["front_fwd"], s * R_["front_out"], R_["front_up"])) if slot(leg) == 1 else
                  Vector((R_["second_fwd"], s * R_["second_out"], R_["second_up"]))) * SIZE
            W_up = world_of_local(leg, up, M)
            W_rest = ground(leg)
            W_cage = cage_target(leg, P["cage_close"] if slot(leg) == 1 else P["cage2_close"],
                                 P["cage_fwd"] if slot(leg) == 1 else P["cage2_fwd"])
            if f <= w:
                T = lerp(W_rest, W_up, ease(f / w))
            elif f <= s_:
                k = (f - w) / (s_ - w)
                T = lerp(W_up, W_cage, k * k)                     # beschleunigt zuschlagen
                T.z = max(T.z, GZ)
            elif f <= h:
                T = W_cage
            else:
                T = lerp(W_cage, W_rest, ease((f - h) / (N - h)))
                T.z = GZ + 0.04 * SIZE * math.sin(math.pi * (f - h) / (N - h))   # Bein hebt beim Zurücksetzen
            plant(leg, T, M)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "planted": CARRY,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_attack2(P):
    """Sprungbiss mit Root Motion: Hocke → Absprung (III/IV stoßen ab) → flacher Satz, I+II vorgestreckt, III/IV
    nach hinten → Landung auf I/II → abfedern + Biss (Event hit) → Ruhe, um jump_distance nach vorn versetzt."""
    N = P["frames"]
    c_end, to_end, land, bite = P["crouch_end"], P["takeoff_end"], P["land_frame"], P["bite_end"]
    D = P["jump_distance"] * SIZE
    crouch = P["crouch"] * BODY_H
    INFO["Attack2"] = {"root_motion_m": round(D, 3), "root_motion_size": P["jump_distance"]}

    def root_at(f):
        if f <= c_end:
            return 0.0, 0.0
        if f >= land:
            return D, 0.0
        u = (f - c_end) / (land - c_end)
        return D * u, 4 * P["apex"] * SIZE * u * (1 - u)

    flight_front = {l: Vector((P["front_fwd"], side_of(l) * 0.02, P["front_up"])) * SIZE for l in LIFTED}
    flight_rear = {l: Vector((-P["rear_back"], 0.0, P["rear_up"])) * SIZE for l in CARRY}
    keys_dz = [(0, 0.0), (c_end, -crouch), (to_end, 0.02 * SIZE), (land - 1, 0.0), (land + 2, -P["bite_drop"] * SIZE),
               (bite, -P["bite_drop"] * SIZE * 0.6), (N, 0.0)]
    keys_p = [(0, 0.0), (c_end, R(P["crouch_pitch_deg"])), (to_end, R(P["flight_pitch_deg"])),
              (land - 1, R(P["flight_pitch_deg"]) * 0.3), (land + 2, R(P["bite_pitch_deg"])), (bite, R(P["bite_pitch_deg"])),
              (N, 0.0)]

    LOCAL0 = {}                                    # Fuß-Versatz (Körper-Raum) beim Lösen vom Boden

    def pose(f):
        reset()
        if f == 0:
            LOCAL0.clear()
        rx, rz = root_at(f)
        move("Root", Vector((rx, 0.0, rz)))
        pitch = smooth_seg(f, keys_p)
        body(dz=smooth_seg(f, keys_dz), pitch=pitch)
        lag = 0.0
        if c_end < f < land + 6:                                  # Hinterleib schwingt im Flug nach (Trägheit)
            lag = R(6) * math.sin(math.pi * min(1.0, (f - c_end) / (land + 6 - c_end)))
        abdomen(0.0, -pitch * 0.5 - lag)
        M = body_matrix()
        off = Vector((D, 0, 0))
        for leg in walking:
            front = leg in LIFTED
            G0, G1 = ground(leg), ground(leg) + off
            fl = flight_front[leg] if front else flight_rear[leg]
            W_fl = world_of_local(leg, fl, M)
            if front:
                land_T = G1 + Vector((P["land_reach"] * SIZE * (1.0 if slot(leg) == 1 else 0.5), 0, 0))
                if f <= c_end - 3:
                    T = G0
                elif f <= to_end:                                  # vor dem Absprung schon anheben (im Körper-Raum
                    d0 = LOCAL0.setdefault((leg, "f"), M.inverted() @ G0 - REST_TIP[leg])   # überblenden, sonst
                    local_foot(leg, lerp(d0, fl, ease((f - (c_end - 3)) / (to_end - c_end + 3))))  # knickt die IK)
                    continue
                elif f < land - 2:
                    T = W_fl
                elif f <= land:
                    T = lerp(W_fl, land_T, ease((f - (land - 2)) / 2))
                elif f <= bite:
                    T = land_T
                else:                                              # zurück in die Ruhe-Stellung (kleiner Schritt)
                    u = (f - bite) / (N - bite)
                    T = lerp(land_T, G1, ease(u))
                    T.z = GZ + 0.03 * SIZE * math.sin(math.pi * u)
            else:
                if f <= c_end:
                    T = G0                                         # stößt ab, bis der Körper abhebt …
                    if f == c_end:
                        LOCAL0[(leg, "r")] = M.inverted() @ G0 - REST_TIP[leg]
                elif f <= to_end + 1:                              # … dann löst sich der Fuß und streckt nach hinten
                    d0 = LOCAL0[(leg, "r")]
                    local_foot(leg, lerp(d0, fl, ease((f - c_end) / (to_end + 1 - c_end))))
                    continue
                elif f < land + 1:
                    T = W_fl
                elif f <= land + 4:                                # landen kurz nach den Vorderbeinen, etwas zu weit hinten
                    tgt = G1 + Vector((-0.04 * SIZE, 0, 0))
                    T = lerp(W_fl, tgt, ease((f - (land + 1)) / 3))
                    T.z = max(T.z, GZ)
                else:
                    u = (f - (land + 4)) / (N - (land + 4))
                    T = lerp(G1 + Vector((-0.04 * SIZE, 0, 0)), G1, ease(u))
                    T.z = GZ + 0.025 * SIZE * math.sin(math.pi * u)
            plant(leg, T, M)
    return {"N": N, "loop": False, "kind": "jump", "pose": pose,
            "events": [{"frame": to_end, "event": "takeoff"}, {"frame": land, "event": "hit"},
                       {"frame": land, "event": "land"},
                       {"frame": N, "event": "root_motion", "distance_m": round(D, 4), "axis": "x"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        reset()
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        kl = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, max(0.0, x - 0.1) * 2.2)) * (1 - x)   # Hinterleib später
        body(dz=-P["body_drop"] * SIZE * k, pitch=-R(4) * k)
        abdomen(R(P["abdomen_jerk_deg"]) * 0.4 * kl, R(P["abdomen_jerk_deg"]) * kl)
        M = body_matrix()
        for leg in walking:
            if slot(leg) == 1:                                    # Vorderbeine zucken schützend an
                plant(leg, ground(leg, -P["front_tuck"] * SIZE * k, -side_of(leg) * 0.03 * SIZE * k,
                                  0.05 * SIZE * k), M)
            else:
                plant(leg, ground(leg), M)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose,
            "planted": [l for l in walking if slot(l) != 1]}


# ---------------------------------------------------------------- eigene Prüfungen (ergänzen den Baukasten)
INFO = {}


def spider_checks(clips):
    """Nach dem Backen: Drehrichtung (Vorzeichen) der Turns, Fußkontakt je Bein, Körperhöhe, Sprungweite."""
    out = {}
    for cname, spec in clips.items():
        act = bpy.data.actions.get(f"{K.PREFIX}_{cname}")
        if act is None:
            continue
        arm.animation_data.action = act
        N = spec["N"]
        r = dict(INFO.get(cname, {}))
        th_z = []
        feet = {l: [] for l in walking}
        for f in range(N + 1):
            sc.frame_set(f)
            th_z.append((arm.matrix_world @ PB["Thorax"].head).z)
            for l in walking:
                feet[l].append(arm.matrix_world.inverted() @ foot(l))
        r["thorax_z_min_max_m"] = [round(min(th_z), 4), round(max(th_z), 4)]
        if spec["kind"] == "locomotion":
            stance_err, slide = {}, {}
            for l in walking:
                st = [(f, p) for f, p in enumerate(feet[l]) if not spec["swing"](l, f)]
                stance_err[l] = round(max(abs(p.z - GZ) for _, p in st), 4)
            r["stance_height_above_ground_m"] = stance_err
            if spec.get("axis") == "turn":
                # Vorzeichen: Standfüße wandern relativ zum Körper im Uhrzeigersinn → Körper dreht links (+)
                c0 = Vector((PIV.x, PIV.y, 0))
                rates = []
                for l in walking:
                    st = [(f, p) for f, p in enumerate(feet[l]) if not spec["swing"](l, f)]
                    for (f0, a), (f1, b) in zip(st, st[1:]):
                        if f1 == f0 + 1:
                            va, vb = Vector((a.x, a.y, 0)) - c0, Vector((b.x, b.y, 0)) - c0
                            rates.append(-math.atan2(va.x * vb.y - va.y * vb.x, va.dot(vb)) * K.FPS)
                w_ = sum(rates) / len(rates)
                r["turn_rate_deg_s_signed"] = round(math.degrees(w_), 1)
                r["turn_direction"] = "links (gegen Uhrzeigersinn von oben)" if w_ > 0 else "rechts (im Uhrzeigersinn)"
                r["turn_direction_ok"] = (w_ > 0) == (spec["turn_dir"] > 0)
            else:
                xs = [p.x for l in walking for f, p in enumerate(feet[l]) if not spec["swing"](l, f)]
                st_main = [l for l in walking if slot(l) != 1]
                v = []
                for l in st_main:
                    st = [(f, p) for f, p in enumerate(feet[l]) if not spec["swing"](l, f)]
                    for (f0, a), (f1, b) in zip(st, st[1:]):
                        if f1 == f0 + 1:
                            v.append((a.x - b.x) * K.FPS)
                r["body_speed_mps"] = round(sum(v) / len(v), 3)
                r["body_speed_size_per_s"] = round(sum(v) / len(v) / SIZE, 3)
        if cname == "Attack2":
            r["feet_final_offset_x_m"] = {l: round(feet[l][-1].x - REST_TIP[l].x, 3) for l in walking}
            r["feet_final_height_m"] = {l: round(feet[l][-1].z - GZ, 4) for l in walking}
        out[f"{K.PREFIX}_{cname}"] = r
        print("SPIDER_CHECK", f"{K.PREFIX}_{cname}", json.dumps(r, ensure_ascii=False))
    (K.OUT / "spider_checks.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    arm.animation_data.action = bpy.data.actions[f"{K.PREFIX}_{ST['meta']['clips'][0]}"]
    bpy.ops.wm.save_as_mainfile(filepath=str(K.OUT / "octopod_clips.blend"))


CLIPS = {
    "Walk": clip_walk(ST["walk"]),
    "Run": clip_walk(ST["run"]),
    "TurnLeft": clip_turn(ST["turn"], 1),
    "TurnRight": clip_turn(ST["turn"], -1),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Attack2": clip_attack2(ST["attack2"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": death_flip(ST["death"]),
}
K.bake(CLIPS)
spider_checks(CLIPS)
