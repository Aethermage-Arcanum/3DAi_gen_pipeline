"""Bewegungsmuster quadruped/tortoise (Schildkröte, erstes Modell Shellback).
Panzer STARR (Rig-Option rigid_shell in creature.toml): der Rumpf bewegt sich nur als Ganzes (Root um einen Drehpunkt in
der Panzermitte), Hips/Spine_1/Chest werden nie gegeneinander gedreht. Schritt = diagonal gekoppelter lateraler Viertakt
mit hohem Duty Factor, Panzer schaukelt (Rollen/Gieren/Heben), Kopf ruhig; Run = hastiger Trab ohne Schwebe; Drehen auf
der Stelle (Kopf führt, Panzer giert leicht in die Kurve); Idle; Ready = Drohen der Schnappschildkröte (Hinterteil hoch,
Maul offen); Attack1 = Schnappbiss mit Körper-Ausfall; Attack2 = Panzer-Rammstoß (Root Motion); Hit; Death (Platzhalter).
Gemeinsame Bausteine: ../quadruped_kit.py (nur gelesen). Eigener Code – andere Muster benutzen diese Datei NICHT
(Kapselung, motions/README.md). Teile aus bear_clips.py kopiert (nicht importiert).

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/tortoise/tortoise_clips.py -- <ausgabe> [<creature.toml>]
"""
import json
import math
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
import bpy  # noqa: E402
from mathutils import Quaternion, Vector  # noqa: E402
from quadruped_kit import FWD, LEFT, UP, LEGS, R, NECK, TAIL, bend, bump, ease, ik_off, jaw, keys, phase, rot  # noqa: E402

ST, SIZE, HGT = K.ST, K.SIZE, K.HGT
TAU = 2 * math.pi
H0 = K.DB["Root"].head_local.copy()
SHELL_C = Vector((H0.x, H0.y, K.DB["Spine_1"].head_local.z))          # Drehpunkt Panzermitte
SHOULDER = (K.DB["Leg_FL_1"].head_local + K.DB["Leg_FR_1"].head_local) / 2
HIP = (K.DB["Leg_BL_1"].head_local + K.DB["Leg_BR_1"].head_local) / 2     # Kippen vorn runter: Hinterbeine sind in Ruhe
# fast gestreckt (Shellback: 0,96–0,98 der Kettenlänge) → Drehpunkt Hüfte, die Vorderbeine beugen sich


def shell(dx=0.0, dy=0.0, dz=0.0, pitch=0.0, roll=0.0, yaw=0.0, pivot=None):
    """Ganzer starrer Panzer (Root) um einen Drehpunkt: pitch + = vorn hoch, roll + = linke Seite hoch, yaw + = links.
    Versatz in Metern (Armature-Raum, nach der Drehung)."""
    P = SHELL_C if pivot is None else pivot
    q = Quaternion(UP, yaw) @ Quaternion(LEFT, -pitch) @ Quaternion(FWD, roll)
    rot("Root", UP, yaw)
    rot("Root", LEFT, -pitch)
    rot("Root", FWD, roll)
    K.move("Root", (P - H0) - q @ (P - H0) + Vector((dx, dy, dz)))


def neck_slide(dx, dz=0.0):
    """Hals fährt aus (+) bzw. zieht ein (−) entlang der Körperachse (Neck_1 verschoben, Kopf folgt)."""
    K.move("Neck_1", Vector((dx, 0, dz)))


def look_chain(yaw_fn, pitch_fn, x, lag):
    """Kopf führt, Hals folgt (aus bear_clips kopiert). yaw + = links, pitch + = Kopf hoch."""
    for axis, fn, sg in ((UP, yaw_fn, 1), (LEFT, pitch_fn, -1)):
        w = [0.3 * fn(x - 2 * lag), 0.6 * fn(x - lag), fn(x)]
        bend(NECK, axis, [sg * w[0], sg * (w[1] - w[0]), sg * (w[2] - w[1])])


def cyc(t, at, cycles=1):
    return math.cos(TAU * cycles * (t - at))


def foot(leg, offset, curl=0.0):
    K.set_foot(leg, offset, curl)


# ---------------------------------------------------------------- Fortbewegung
def locomotion(P, turn=0.0):
    N, off, d = P["cycle_frames"], P["order"], P["duty"]
    td = {l: (-off[l]) % 1.0 for l in LEGS}                          # Aufsetz-Zeitpunkt je Bein
    ms = {l: (td[l] + d + (1 - d) / 2) % 1.0 for l in LEGS}           # Mitte Schwung
    pair_td = (td["FL"] + td["BR"]) / 2                               # Diagonalpaar VL+HR setzt auf
    sgn = (turn > 0) - (turn < 0)

    def rock(t):
        """Panzer: (dz, pitch, roll, yaw) aus dem Fußtakt."""
        dz = -P["bob"] * HGT * cyc(t, pair_td + P.get("sag_lag", 0.05), 2) - P.get("crouch", 0.0) * HGT
        pitch = R(P.get("nod_deg", 0)) * math.sin(2 * TAU * (t - pair_td))
        roll = -R(P["roll_deg"]) * cyc(t, ms["FL"])                    # VL schwingt → linke Seite sinkt
        yaw = -R(P["yaw_deg"]) * cyc(t, ms["FL"])                      # … linke Schulter geht vor
        if turn:
            yaw += sgn * R(P.get("turn_shell_deg", 0))
            roll += sgn * R(P.get("turn_roll_deg", 0))                 # Außenseite sinkt
        return dz, pitch, roll, yaw

    def pose(f):
        t = (f % N) / N
        K.gait(t, P, off, turn=-turn)                                  # −turn: TurnLeft (turn > 0) dreht links (wie bear)
        out = P.get("swing_out", 0.0) * SIZE                           # Fußbogen nach außen (gespreizte Beine)
        for leg in LEGS:
            sw, s = phase(t, off[leg], d)
            if sw and out:
                m = K.IK[leg].matrix_world.copy()
                m.translation.y += (1 if leg[1] == "L" else -1) * out * bump(s, 0.5)
                K.IK[leg].matrix_world = m
        dz, pitch, roll, yaw = rock(t)
        # Drehen: Panzer giert um die Hüfte in die Kurve (Vorderteil schwenkt voraus; um die Mitte würde die innere Hüfte
        # nach innen wandern und das innere Hinterbein überstrecken)
        shell(dz=dz, pitch=pitch, roll=roll, yaw=yaw, pivot=HIP if turn else None)
        # Hals: vorgestreckt, schiebt im Takt; Kopf gleicht Panzer-Gieren/-Nicken teilweise aus (ruhig)
        neck_slide(P.get("neck_reach", 0.0) * SIZE + P.get("neck_pump", 0.0) * SIZE * cyc(t, pair_td + 0.1, 2))
        k = P.get("head_steady", 0.6)
        nl = R(P.get("neck_lift_deg", 0))
        lag = P.get("head_lead", 0.0)
        hd = sgn * R(P.get("turn_head_deg", 0)) if turn else 0.0
        bend(NECK, LEFT, [-nl * 0.5, -nl * 0.5, pitch * k])
        y_ = -yaw * k + (rock(t - 0.04)[3] - yaw) * 0.3                # verzögertes Nachpendeln
        if turn:
            y_ = -(yaw - sgn * R(P.get("turn_shell_deg", 0))) * k
        bend(NECK, UP, [hd * 0.25 + y_ * 0.3, hd * 0.3 + y_ * 0.3, hd * 0.45 + y_ * 0.4])
        # Stachelschwanz: starr in der Form, pendelt gering und verzögert; beim Drehen nach außen
        tw = -R(P.get("tail_deg", 0)) * cyc(t - 0.08, ms["FL"])
        bend(TAIL, UP, [tw * 0.4 - sgn * R(4) * 0.4, tw * 0.3 - sgn * R(4) * 0.3, tw * 0.2, tw * 0.1])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn,
            "max_stretch": P.get("max_stretch"), "reach_smooth": P.get("reach_smooth"), "reach_flat": P.get("reach_flat", 0),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], d)[0]}


# ---------------------------------------------------------------- Stand-Clips
def clip_idle(P):
    """Steht schwer, Panzer atmet; Kopf schaut langsam rechts/links (Kopf führt), zieht einmal halb in den Panzer ein und
    kommt wieder heraus; ein Vorderbein wird nachgesetzt (Gewicht verlagert sich zur Gegenseite)."""
    N = P["frames"]
    leg = P.get("step_leg", "FR")
    side = 1 if leg[1] == "L" else -1
    look = [(0, 0), (0.08, 0), (0.18, -1), (0.28, -1), (0.36, 0), (0.62, 0), (0.72, 0.9), (0.82, 0.9), (0.94, 0), (1, 0)]
    ret = [(0, 0), (0.4, 0), (0.45, 1), (0.54, 1), (0.6, 0), (1, 0)]
    step = [(0, 0), (0.66, 0), (0.72, 1), (0.78, 0), (1, 0)]

    def pose(f):
        t = f / N
        br = math.sin(TAU * 3 * t)
        st = keys(t, step)
        shell(dz=P["breathe"] * HGT * br, dy=-side * 0.008 * SIZE * st, roll=side * R(1.5) * st,
              pitch=R(0.6) * br)
        r_ = keys(t, ret)
        neck_slide(-P["retract"] * SIZE * r_)
        look_chain(lambda x: R(P["look_deg"]) * keys(x, look, loop=True),
                   lambda x: -R(8) * keys(x, ret, loop=True) + R(2) * math.sin(TAU * 2 * x), t, 0.02)
        foot(leg, Vector((0.015 * SIZE * math.sin(math.pi * min(1, max(0, (t - 0.66) / 0.12))), 0,
                          P["step_lift"] * HGT * bump(min(1, max(0, (t - 0.66) / 0.12)), 0.45))))
        bend(TAIL, UP, [R(2) * math.sin(TAU * t) * k for k in (0.4, 0.3, 0.2, 0.1)])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth"),
            "planted": [l for l in LEGS if l != leg]}


def clip_ready(P):
    """Drohen (Schnappschildkröte): Panzer kippt vorn nach unten (Drehpunkt Hüfte – Hinterbeine haben keine Streckreserve), wirkt als Hinterteil hoch, Kopf zurück und
    hoch, Maul weit offen, langsames Wiegen links/rechts (Kopf führt, Panzer folgt). Schleife."""
    N = P["frames"]

    def pose(f):
        t = f / N
        sway = math.sin(TAU * t)
        br = math.sin(TAU * 2 * t)
        shell(dz=-P["crouch"] * HGT + 0.006 * HGT * br, pitch=-R(P["tilt_deg"]) + R(1) * br,
              yaw=R(P["sway_deg"]) * 0.4 * math.sin(TAU * (t - 0.06)), roll=-R(1.5) * sway, pivot=HIP)
        neck_slide(-P["neck_back"] * SIZE * (1 + 0.15 * br), 0.01 * SIZE)
        look_chain(lambda x: R(P["sway_deg"]) * 1.6 * math.sin(TAU * x),
                   lambda x: R(P["head_up_deg"]) + R(3) * math.sin(TAU * 2 * x), t, 0.03)
        jaw(P["jaw_open_deg"] * (0.85 + 0.15 * math.sin(TAU * 3 * t)))
        bend(TAIL, UP, [R(3) * math.sin(TAU * (t - 0.1)) * k for k in (0.4, 0.3, 0.2, 0.1)])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_attack1(P):
    """Schnappbiss: Ausholen (Kopf zurück, Hinterteil sinkt, Maul öffnet) → Zustoß: Hinterbeine schieben, ganzer Körper
    fährt vor, Panzer kippt vorn nach unten, Hals + Kopf schießen nach vorn-oben, Maul schlägt zu (hit) → Zerren (Kopf
    reißt seitlich, Panzer ruckt mit) → schwer zurück."""
    N, w, s, h, hold = P["frames"], P["windup_end"], P["strike_end"], P["hit_frame"], P["hold_end"]
    L_, rec = SIZE, N - 2
    dx = [(0, 0), (w, -0.02 * L_), (s, P["lunge"] * L_), (hold, P["lunge"] * L_ * 0.92), (rec, 0)]
    dz = [(0, 0), (w, -0.015 * HGT), (s, -0.035 * HGT), (hold, -0.03 * HGT), (rec, 0)]
    pitch = [(0, 0), (w, R(P["windup_tilt_deg"])), (s, -R(P["tilt_deg"])), (hold, -R(P["tilt_deg"]) * 0.7), (rec, 0)]
    nx = [(0, 0), (w, -P["neck_back"] * L_), (s - 1, P["neck_out"] * L_ * 0.85), (s, P["neck_out"] * L_),
          (hold, P["neck_out"] * L_ * 0.85), (rec - 2, 0), (rec, 0)]
    nz = [(0, 0), (w, 0), (s, P["neck_up"] * L_), (hold, P["neck_up"] * L_ * 0.5), (rec, 0)]
    hp = [(0, 0), (w, R(6)), (h - 1, R(P["head_up_deg"])), (s + 1, R(P["head_up_deg"]) * 0.7), (hold, R(3)), (rec, 0)]
    tug = [(0, 0), (h, 0), (h + 2, 1), (h + 4, -1), (h + 6, 0.6), (hold, 0), (N, 0)]
    jw = [(0, 0), (w - 3, 8), (w, P["jaw_open_deg"] * 0.6), (h - 1, P["jaw_open_deg"]), (h, 3), (hold, 3),
          (hold + 4, 6), (N, 0)]

    def pose(f):
        tg = R(P["tug_deg"]) * keys(f, tug)
        shell(dx=keys(f, dx), dz=keys(f, dz), pitch=keys(f, pitch), yaw=0.3 * R(P["tug_deg"]) * keys(f - 1, tug),
              roll=0.25 * R(P["tug_deg"]) * keys(f - 1, tug), pivot=HIP)
        neck_slide(keys(f, nx), keys(f, nz))
        look_chain(lambda x: R(P["tug_deg"]) * keys(x, tug), lambda x: keys(x, hp) - keys(x, pitch), f, 1.0)
        jaw(keys(f, jw))
        bend(TAIL, UP, [-tg * 0.2 * k for k in (1.0, 0.8, 0.6, 0.4)])
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth"),
            "events": [{"frame": h, "event": "hit"}]}


def clip_attack2(P):
    """Panzer-Rammstoß (Root Motion): Kopf halb einziehen + tief ducken (Schwung holen) → schwerer Ausfall nach vorn,
    vorderer Panzerrand und Stachelreihe voran, vorn aufbäumen beim Treffer (hit) → nachrutschen, Beine stemmen sich,
    Panzer federt zurück → Ruhe um `distance` weiter vorn (Root endet dort, Event root_motion)."""
    N, de, re, h, se = P["frames"], P["duck_end"], P["ram_end"], P["hit_frame"], P["settle_end"]
    D, ov = P["distance"] * SIZE, P["overshoot"] * SIZE
    dx = [(0, 0), (de, -0.03 * SIZE), (h, D * 0.85), (re, D + ov), (re + 4, D + ov * 0.6), (se, D), (N, D)]
    dz = [(0, 0), (de, -P["duck"] * HGT), (h - 2, -0.03 * HGT), (h, 0.01 * HGT), (re + 3, -0.04 * HGT), (se, 0), (N, 0)]
    pitch = [(0, 0), (de, -R(P["duck_tilt_deg"])), (h - 3, -R(1)), (h, R(P["rear_deg"])), (re + 2, R(P["rear_deg"]) * 0.5),
             (re + 6, -R(2.5)), (se, 0), (N, 0)]
    roll = [(0, 0), (re, 0), (re + 3, R(2.5)), (re + 7, -R(1.5)), (se, 0), (N, 0)]
    nx = [(0, 0), (de - 4, -P["neck_back"] * SIZE), (se, -P["neck_back"] * SIZE * 0.7), (N - 2, 0), (N, 0)]
    hp = [(0, 0), (de - 4, -R(10)), (h, -R(4)), (se, -R(6)), (N, 0)]
    jw = [(0, 0), (h - 1, 0), (h + 1, 14), (h + 5, 4), (N, 0)]
    # Füße: vorne treten mit dem Ausfall mit (VL einen Frame vor VR), hinten schieben erst und rutschen/treten nach
    # Vorderfüße lösen sich beim Aufbäumen vom Boden (vorn hebt sich um rear_deg) und setzen weiter vorn auf (VL einen Frame
    # vor VR); Hinterfüße schieben und treten schnell nach (hastiger Ausfall, alle vier Füße kommen um `distance` weiter vorn an)
    steps = {"FL": (de + 1, re + 3, P["front_step"], P["front_lift"], 0.6), "FR": (de + 2, re + 4, P["front_step"], P["front_lift"], 0.6),
             "BL": (de + 2, re + 2, P["back_step"], P["step_lift"], 0.4), "BR": (de + 3, re + 3, P["back_step"], P["step_lift"], 0.4)}

    def pose(f):
        shell(dx=keys(f, dx), dz=keys(f, dz), pitch=keys(f, pitch), roll=keys(f, roll), pivot=HIP)
        neck_slide(keys(f, nx))
        bend(NECK, LEFT, [0, 0, -keys(f, hp) - keys(f, pitch) * 0.5])
        jaw(keys(f, jw))
        bend(TAIL, UP, [R(5) * keys(f - 2, roll) / R(2.5) * k for k in (0.4, 0.3, 0.2, 0.1)])
        for leg, (a, b, k, lift, pk) in steps.items():
            u = min(1.0, max(0.0, (f - a) / (b - a)))
            p = ease(u)
            stride_ = D * k + (D - D * k) * ease(min(1.0, max(0.0, (f - se) / max(1, N - se))))
            foot(leg, Vector((stride_ * p, 0, lift * HGT * bump(u, pk))), R(15) * bump(u, pk))
    return {"N": N, "loop": False, "kind": "root_motion", "pose": pose, "reach_smooth": P.get("reach_smooth"),
            "root_motion": D,
            "events": [{"frame": h, "event": "hit"},
                       {"frame": N, "event": "root_motion", "distance_m": round(D, 4), "axis": "x"}]}


def clip_hit(P):
    """Schreck-Reflex: Kopf zuckt halb unter den Panzer, Panzer sackt ab und kippt leicht zurück, rollt weg → Ruhe."""
    N = P["frames"]
    e = N - 3
    k_ = [(0, 0), (2, 1), (5, 0.8), (9, 0.25), (e, 0)]
    roll = [(0, 0), (2, 1), (5, -0.4), (8, 0.15), (e, 0)]

    def pose(f):
        k = keys(f, k_)
        shell(dz=-P["drop"] * HGT * keys(f - 1, k_), dx=-0.02 * SIZE * k, pitch=R(P["tilt_deg"]) * k,
              roll=R(P["roll_deg"]) * keys(f, roll))
        neck_slide(-P["retract"] * SIZE * k)
        bend(NECK, LEFT, [0, R(4) * k, R(8) * keys(f - 1, k_)])
        jaw(10 * keys(f, [(0, 0), (2, 1), (6, 0), (N, 0)]))
        bend(TAIL, UP, [R(4) * keys(f - 2, roll) * c for c in (0.4, 0.3, 0.2, 0.1)])
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_death(P):
    """PLATZHALTER (Nutzerregel „Death-Clips nicht anfassen“): Kopie des Bären-/Hirsch-Tods (zur Seite kippen)."""
    N, c0, c1 = P["frames"], P["collapse_start"], P["collapse_end"]
    side = P["side"]
    piv = (K.REST["F" + ("R" if side > 0 else "L")]["ball"] + K.REST["B" + ("R" if side > 0 else "L")]["ball"]) / 2

    def raw(f):
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        ang = side * R(88) * k
        q = Quaternion(FWD, ang)
        loc = (Vector(piv) - H0) - q @ (Vector(piv) - H0)
        rot("Root", FWD, ang)
        K.move("Root", loc)
        for leg in LEGS:
            ik_off(leg, min(1.0, k * 1.6))
            sgn = 1 if leg[0] == "F" else -1
            rot(f"Leg_{leg}_1", LEFT, sgn * R(P["legs_limp_deg"]) * k)
            rot(f"Leg_{leg}_2", LEFT, -sgn * R(P["legs_limp_deg"]) * k)
        K.neck_head(pitch=-R(10) * k - R(6) * jolt, yaw=0)
        jaw(14 * k)
        K.tail(0, 0, 1, -20 * k)
        return k

    K.reset()
    raw(N)
    bpy.context.view_layer.update()
    drop = K.mesh_min_z() - K.GROUND

    def pose(f):
        k = raw(f)
        K.move("Root", Vector((0, 0, -drop * k)))
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "events": [{"frame": N, "event": "dead"}]}


# ---------------------------------------------------------------- eigene Prüfungen (nur Info, im clips_report.json)
def yaw_of(bone):
    v = K.PB[bone].matrix.to_3x3() @ Vector((0, 1, 0))
    return math.degrees(math.atan2(v.y, v.x))


def turn_check(spec, expect):
    """Drehrichtung gemessen (aus bear_clips): Standfüße wandern relativ zum Körper → Körperdrehung; dazu mittleres Gieren
    von Kopf und Brust (Kopf führt: |Kopf| > |Brust| > 0, beide in Drehrichtung)."""
    N = spec["N"]
    rot_sum, cnt, yaws = 0.0, 0, {b: 0.0 for b in ("Head", "Neck_2", "Chest", "Hips")}
    prev = {}
    rest_yaw = {b: math.degrees(math.atan2((K.DB[b].matrix_local.to_3x3() @ Vector((0, 1, 0))).y,
                                           (K.DB[b].matrix_local.to_3x3() @ Vector((0, 1, 0))).x)) for b in yaws}
    c = K.DB["Root"].head_local
    for f in range(N + 1):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        for leg in LEGS:
            if spec["swing"](leg, f):
                prev.pop(leg, None)
                continue
            p = K.IK[leg].matrix_world.translation - c
            a = math.atan2(p.y, p.x)
            if leg in prev:
                rot_sum += (a - prev[leg] + math.pi) % TAU - math.pi
                cnt += 1
            prev[leg] = a
        if f < N:
            for b in yaws:
                yaws[b] += ((yaw_of(b) - rest_yaw[b] + 180) % 360 - 180) / N
    body_deg = -math.degrees(rot_sum) / max(1, cnt) * N * (spec["duty"])
    ok = (body_deg > 0) == (expect > 0) and (yaws["Head"] > 0) == (expect > 0) and \
        abs(yaws["Head"]) > abs(yaws["Chest"]) > 0 and (yaws["Chest"] > 0) == (expect > 0)
    return {"body_turn_deg_per_cycle": round(body_deg, 1), "mean_yaw_deg": {k: round(v, 1) for k, v in yaws.items()},
            "turn_dir_ok": ok}


def _shell_front():
    """Vorderster Punkt der starren Panzer-Vertices (100 % shell_bone) und Kopfspitze im aktuellen Frame."""
    bpy.context.view_layer.update()
    ev = K.body_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = ev.to_mesh()
    me = K.body_obj.data
    gi = K.body_obj.vertex_groups.get("Spine_1").index
    xs = [m.vertices[v.index].co for v in me.vertices if len(v.groups) == 1 and v.groups[0].group == gi]
    front = max(xs, key=lambda c: c.x).copy() if xs else Vector()
    ev.to_mesh_clear()
    return front


def strike_check(spec, frame):
    """Trifft der Angriff VOR dem Körper? Kopfspitze (Head-Ende) und vorderster Panzerpunkt beim Treffer gegen Ruhe."""
    K.reset()
    rest_nose = K.DB["Head"].tail_local.copy()
    rest_front = _shell_front()
    spec["pose"](frame)
    bpy.context.view_layer.update()
    nose = K.arm.matrix_world @ K.PB["Head"].tail
    front = _shell_front()
    root_dx = (K.PB["Root"].head - K.DB["Root"].head_local).x
    return {"hit_frame": frame,
            "nose_ahead_of_rest_nose_m": round(nose.x - rest_nose.x, 3),
            "nose_ahead_of_shell_front_m": round(nose.x - front.x, 3),
            "nose_height_m": round(nose.z - K.GROUND, 3), "rest_nose_height_m": round(rest_nose.z - K.GROUND, 3),
            "shell_front_advance_m": round(front.x - rest_front.x, 3),
            "shell_front_height_m": round(front.z - K.GROUND, 3), "body_advance_m": round(root_dx, 3)}


turn = R(ST["turn"]["turn_deg"])
IK_STIFF = ST.get("ik", {}).get("stiffness", {})


def stiff(spec):
    spec["ik_stiff"] = IK_STIFF
    spec["foot_ground"] = True
    return spec


CLIPS = {
    "Walk": stiff(locomotion(ST["walk"])),
    "Run": stiff(locomotion(ST["run"])),
    "TurnLeft": stiff(locomotion(ST["turn"], turn=turn)),
    "TurnRight": stiff(locomotion(ST["turn"], turn=-turn)),
    "Idle": stiff(clip_idle(ST["idle"])),
    "Ready": stiff(clip_ready(ST["ready"])),
    "Attack1": stiff(clip_attack1(ST["attack1"])),
    "Attack2": stiff(clip_attack2(ST["attack2"])),
    "Hit": stiff(clip_hit(ST["hit"])),
    "Death": clip_death(ST["death"]),
}
if os.environ.get("TORTOISE_DEBUG"):                     # Diagnose: Reichweite je Bein und Frame, dann Ende
    spec = CLIPS[os.environ["TORTOISE_DEBUG"]]
    for f in range(spec["N"] + 1):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        r = {l: round((K.arm.matrix_world.inverted() @ K.IK[l].matrix_world.translation - K.PB[f"Leg_{l}_1"].head).length
                      / K.chain_len(l), 3) for l in LEGS}
        print("DBG", f, "ratio", r, "need", round(K.reach_fix(), 3))
    raise SystemExit
EXTRA = {"TurnLeft": turn_check(CLIPS["TurnLeft"], 1), "TurnRight": turn_check(CLIPS["TurnRight"], -1),
         "Attack1": strike_check(CLIPS["Attack1"], ST["attack1"]["hit_frame"]),
         "Attack2": strike_check(CLIPS["Attack2"], ST["attack2"]["hit_frame"])}
EXTRA["Attack2"]["root_motion_m"] = round(CLIPS["Attack2"]["root_motion"], 3)
for c, v in EXTRA.items():
    print("TORTOISE_CHECK", c, json.dumps(v, ensure_ascii=False))
K.reset()
K.bake(CLIPS)
rep_p = K.OUT / "clips_report.json"
rep = json.loads(rep_p.read_text(encoding="utf-8"))
for c, v in EXTRA.items():
    rep["clips"][f"{K.PREFIX}_{c}"].update(v)
rep["turn_dir_ok"] = all(EXTRA[c]["turn_dir_ok"] for c in ("TurnLeft", "TurnRight"))
rep_p.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
