"""Bewegungsmuster upright/treant: schwerer Baum-Riese (Bog Warden). Schritt, Eiltempo, Drehen, Idle, Drohen,
Wurzel-Slam, Ast-Peitsche, Treffer, Tod (Platzhalter). Baukasten: ../upright_kit.py.

& "D:\\Blender\\blender.exe" -b <upright_rigged.blend> -P motions/upright/treant/treant_clips.py -- <ausgabe> [<creature.toml>]

Grundsätze (Regeln des Nutzers): Ganzkörper statt Einzelteil · Haltung absolut (posture) statt auf die gebückte
Ruhepose addiert · Füße stehen (IK) · Überlappung: jedes Glied folgt dem vorherigen verzögert (Federn), Krone schwingt
nach · Schleifen periodisch (nahtlos).
"""
import math
import pathlib
import sys

import bpy
from mathutils import Quaternion, Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import upright_kit as K  # noqa: E402

K.init(HERE)
from upright_kit import (FWD, LEFT, UP, R, arm_fk, arm_ik, body, crown, ease, ease_in, gait, phase,  # noqa: E402
                         posture, rot, spring_curve)

ST, HGT, LEG = K.ST, K.HGT, K.LEGLEN
STAND = ST["stand"]
TW = 2 * math.pi


def stand_posture(flex=0.0, side=0.0, twist=0.0, lean=None):
    posture(STAND["lean_deg"] if lean is None else lean, STAND["side_deg"], flex, side, twist)


# ---------------------------------------------------------------- Gehen / Eiltempo / Drehen
def locomotion(P, turn=0.0):
    """Ganzkörper-Gang (Elefant/Riese): Becken giert mit dem Schwungbein, Gewicht + Oberkörper pendeln übers Standbein,
    Rumpf sackt nach jedem Aufsetzen ein (Last) und nickt nach, Brust dreht verzögert gegen das Becken, Arme pendeln
    gegen die Beine als Welle Oberarm → Unterarm → Finger und federn beim Aufsetzen nach, Krone bleibt zurück.
    Alles periodisch → nahtlose Schleife."""
    N, off, d = P["cycle_frames"], P["order"], P["duty"]
    sgn = (turn > 0) - (turn < 0)

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=turn)
        c = TW * (t - d / 2)                                   # 0 = Mitte Standphase links
        settle = P["settle"]
        bob = math.cos(2 * TW * (t - settle - 0.25))           # −1 kurz nach jedem Aufsetzen, +1 in der Standmitte
        sway = math.cos(c - TW * P["sway_lag"])                # +1 = über dem linken Fuß
        roll_w = -R(P["roll_deg"]) * math.cos(c - TW * (P["sway_lag"] + 0.02))
        body(dz=P["bob"] * HGT * bob, dy=P["sway"] * HGT * sway, roll=roll_w)
        # Becken: Schwungbein-Hüfte vor (links vor bei t=0 → Gieren negativ), Brust verzögert dagegen
        yaw = R(P["hip_yaw_deg"])
        rot("Pelvis", UP, -yaw * math.cos(TW * t))
        nod = R(P["chest_nod_deg"]) * -math.cos(2 * TW * (t - settle - 0.04))
        lead = R(P.get("lead_deg", 0)) * sgn
        posture(P["lean_deg"], STAND["side_deg"], flex=nod, side=R(P.get("bend_deg", 0)) * sgn,
                twist=lead + yaw * P["counter"] * math.cos(TW * (t - P["counter_lag"])) * 1.6)
        # Arme: links vor, wenn das rechte Bein vor ist (t = 0,5); Welle zur Spitze; Nachfedern nach dem Aufsetzen
        for s in ("L", "R"):
            ph = 0.5 if s == "L" else 0.0
            a0 = P["arm_lag"]
            swing = P["arm_swing_deg"] * math.cos(TW * (t - ph - a0))
            elbow = P["elbow_base"] + P["elbow_deg"] * math.cos(TW * (t - ph - a0 - P["elbow_lag"])) \
                - P["arm_bounce_deg"] * math.cos(2 * TW * (t - settle - 0.25 - 0.06))
            fing = P["finger_deg"] * math.cos(TW * (t - ph - a0 - 2 * P["elbow_lag"]))
            out = P["arm_out"] + 1.5 * math.cos(2 * TW * (t - settle - 0.1))
            arm_fk(s, swing=swing, out=out, elbow=elbow, wrist=elbow * 0.3, fingers=fing,
                   sweep=-P.get("arm_trail_deg", 0) * sgn)
        # Krone: Trägheit gegen das seitliche Pendeln und Nicken nach dem Aufsetzen
        k, lag = P["crown_roll_k"], P["crown_lag"]
        roll_lag = -R(P["roll_deg"]) * math.cos(c - TW * (P["sway_lag"] + 0.02 + lag))
        crown(roll=k * (roll_lag - roll_w), pitch=R(P["crown_nod_deg"]) * -math.cos(2 * TW * (t - settle - lag)),
              yaw=-R(P.get("crown_trail_deg", 0)) * sgn)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn, "reach": "smooth",
            "swing": lambda s, f: phase((f % N) / N, off[s], d)[0]}


# ---------------------------------------------------------------- Idle / Ready
def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        br = math.sin(TW * 2 * t)
        sw = math.sin(TW * t)
        body(dy=P["sway"] * HGT * sw, roll=-R(P["roll_deg"]) * sw)
        look = R(P["look_deg"]) * math.sin(TW * t) * (0.6 + 0.4 * math.sin(TW * 2 * t + 1.0))
        stand_posture(flex=R(P["breathe_deg"]) * br, twist=look)
        wind_r = math.sin(TW * 2 * t + 0.7) + 0.5 * math.sin(TW * 3 * t + 2.1)
        wind_p = math.sin(TW * 3 * t + 0.3) * 0.6 + 0.4 * math.sin(TW * 2 * t - 1.2)
        crown(roll=R(P["crown_deg"]) * wind_r * 0.6, pitch=R(P["crown_deg"]) * wind_p * 0.5 - R(P["breathe_deg"]) * 0.6 * math.sin(TW * 2 * (t - 0.05)),
              yaw=-look * 0.35)
        for s in ("L", "R"):
            sg = 1 if s == "L" else -1
            arm_fk(s, swing=P["arm_deg"] * math.sin(TW * (t - 0.08)) - 1.5 * math.sin(TW * 2 * (t - 0.1)),
                   out=1.5 * sg * math.sin(TW * (t - 0.12)) + 1.0,
                   elbow=4 + 3 * math.sin(TW * 2 * (t - 0.14)),
                   fingers=P["finger_deg"] * math.sin(TW * 2 * (t - 0.2) + (0 if s == "L" else 1.3)),
                   sweep=-look * 0.4)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        sw, br = math.sin(TW * t), math.sin(TW * 2 * t)
        body(dz=-P["crouch"] * HGT + 0.004 * HGT * br, dy=P["sway"] * HGT * sw, roll=-R(P["roll_deg"]) * sw)
        posture(P["lean_deg"], STAND["side_deg"], flex=R(P["breathe_deg"]) * br,
                twist=R(4) * math.sin(TW * (t - 0.06)))
        crown(roll=R(P["roll_deg"]) * 0.8 * math.sin(TW * (t - 0.12)),
              pitch=-R(P["crown_deg"]) * math.sin(TW * 2 * (t - 0.1)))
        for s in ("L", "R"):
            ph = 0.0 if s == "L" else 0.5
            arm_fk(s, swing=P["arm_fwd_deg"] + 4 * br, out=P["arm_out_deg"] + 3 * math.sin(TW * (t - ph - 0.1)),
                   elbow=P["elbow_deg"] + 5 * math.sin(TW * 2 * (t - 0.12)), wrist=8,
                   fingers=P["finger_spread_deg"] + P["finger_pulse_deg"] * math.sin(TW * 2 * (t - ph * 0.5 - 0.2)),
                   shrug=4 + 2 * br)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach": "smooth"}


# ---------------------------------------------------------------- Attack1: Wurzel-Slam
def hand_low(s):
    """Tiefster Punkt der Hand (Mesh-Vertices, die vor allem an Hand/Fingers hängen) in der aktuellen Pose."""
    bpy.context.view_layer.update()
    ob = K.body_obj
    gi = {ob.vertex_groups[f"Hand_{s}"].index, ob.vertex_groups[f"Fingers_{s}"].index}
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    z = min((ob.matrix_world @ me.vertices[v.index].co).z for v in ob.data.vertices
            if sum(g.weight for g in v.groups if g.group in gi) > 0.5)
    ev.to_mesh_clear()
    return z


def clip_attack1(P):
    """Gorilla-Bodenschlag mit dem ganzen Körper: Ausholen = Oberkörper richtet sich auf und lehnt zurück, Schultern
    hoch, beide Arme schwingen über die Krone, Ellbogen gebeugt, Finger gespreizt, Krone kippt verzögert nach vorn →
    Schlag (beschleunigt): Rumpf klappt nach vorn, Körper sackt ein, Arme schlagen nieder (Unterarm/Hand/Finger
    verzögert = Peitsche) → Hände treffen den Boden vor den Füßen (Hand-IK, Event hit) → Körper federt über den
    aufgesetzten Händen nach, Krone peitscht nach vorn und schwingt aus → schweres Aufrichten."""
    N, w, s_, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]

    def wind(f):
        if f <= w:
            return ease(f / w)
        return max(0.0, 1 - (f - w) / (s_ - w)) if f <= s_ else 0.0

    def strike(f):
        if f <= w:
            return 0.0
        if f <= s_:
            return ease_in((f - w) / (s_ - w), 2.2)
        return 1.0 if f <= h else 1 - ease((f - h) / (N - 4 - h))

    def sp(fn, fr=3.0, z=0.45, lag=0):
        return spring_curve(lambda f: fn(f - lag), N, fr, z)

    def lean_t(f):
        return STAND["lean_deg"] + (P["lean_back_deg"] - STAND["lean_deg"]) * wind(f)             + (P["slam_lean_deg"] - STAND["lean_deg"]) * strike(f)
    # Zielkurven (TF) und daraus gefederte Kurven (C): Oberarm folgt schnell, Unterarm/Hand/Finger verzögert (Peitsche)
    TF = {
        "lean": (lean_t, 4.2, 0.45, 0),
        "dx": (lambda f: (0.008 * wind(f) - P["slam_lunge"] * strike(f)) * HGT, 2.8, 0.5, 0),
        "dz": (lambda f: -P["slam_drop"] * HGT * strike(f), 3.5, 0.45, 0),
        "swing_u": (lambda f: P["raise_deg"] * wind(f) + P["slam_swing_deg"] * strike(f), 4.5, 0.6, 0),
        "elbow": (lambda f: P["raise_elbow_deg"] * wind(f) + 4 * strike(f), 3.0, 0.45, 1.0),
        "wrist": (lambda f: 25 * wind(f) - 30 * strike(f), 2.6, 0.4, 2.0),
        "fing": (lambda f: P["finger_spread_deg"] * max(wind(f), strike(f)) - 6 * strike(f), 2.2, 0.35, 3.0),
        "shrug": (lambda f: P["shrug_deg"] * wind(f) - 4 * strike(f), 3.0, 0.5, 0),
        "out": (lambda f: P["raise_out_deg"] * wind(f) + 4 * strike(f), 3.0, 0.5, 0),
    }
    C = {k: sp(fn, fr, z, lag) for k, (fn, fr, z, lag) in TF.items()}
    extra = [0.0]                                    # zusätzliches Einsacken, damit die Hände den Boden erreichen
    # Krone: träge – bleibt bei schnellen Rumpf-Neigungen zurück und peitscht nach (Differenz zur langsameren Feder)
    lagc = sp(lean_t, 1.8, 0.28)
    crown_p = [P["crown_k"] * R(lagc[f] - C["lean"][f]) for f in range(N + 1)]

    def pose_fk(f, target=False):
        v = {k: (TF[k][0](f) if target else C[k][f]) for k in TF}
        body(dz=v["dz"] - extra[0] * strike(f), dx=v["dx"])
        posture(v["lean"], STAND["side_deg"])
        crown(pitch=0.0 if target else crown_p[f])
        pre = P["raise_in_deg"] * wind(f)
        for s in ("L", "R"):
            arm_fk(s, swing=v["swing_u"], out=v["out"] - pre, elbow=v["elbow"], wrist=v["wrist"],
                   fingers=v["fing"], shrug=v["shrug"], twist=pre * 0.5)

    # Hände müssen den Boden treffen. Gemessen an der ZIEL-Pose des Aufschlags (die gefederten Arme kommen erst kurz
    # danach an): fehlt etwas, sackt der Körper beim Aufschlag genau so viel tiefer (Knie beugen) – die Bewegung wird
    # nie kleiner. Hand-IK: Handgelenk-Ziel = Position der Ziel-Pose; ab 3 Frames vor dem Aufschlag zieht die IK die
    # (verzögerten) Hände dorthin, während des Haltens bleiben sie stehen und der Körper federt darüber nach.
    for _ in range(2):
        K.reset()
        pose_fk(s_, target=True)
        low = min(hand_low(s) for s in ("L", "R"))
        extra[0] = max(0.0, extra[0] + low - K.GROUND - P["hand_clear"] * HGT)
    print(f"TREANT_SLAM Körper sackt beim Aufschlag zusätzlich {extra[0] * 100:.1f} cm ein, damit die Hände den Boden treffen")
    K.reset()
    pose_fk(s_, target=True)
    bpy.context.view_layer.update()
    tg = {}
    for s in ("L", "R"):
        low = hand_low(s)
        wp = K.arm.matrix_world.inverted() @ K.world_pos(f"Forearm_{s}")
        q = (K.PB[f"Hand_{s}"].matrix.to_quaternion() @ K.DB[f"Hand_{s}"].matrix_local.to_quaternion().inverted())
        tg[s] = (wp - Vector((0, 0, low - K.GROUND - P["hand_clear"] * HGT)), q)

    def ik_k(f):
        a0 = s_ - 3
        if f < a0:
            return 0.0
        if f <= s_:
            return ease((f - a0) / 3)
        if f <= h:
            return 1.0
        return 1 - ease((f - h) / 6)

    def pose(f):
        pose_fk(f)
        k = ik_k(f)
        for s in ("L", "R"):
            arm_ik(s, k, *tg[s])

    def measure():
        K.reset()
        pose(s_ + 2)
        return {s: round(hand_low(s) - K.GROUND, 4) for s in ("L", "R")}
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "reach": "smooth",
            "events": [{"frame": P["hit_frame"], "event": "hit"}], "hand_ground_m": measure}


# ---------------------------------------------------------------- Attack2: Ast-Peitsche
def clip_attack2(P):
    """Elefantenrüssel-Schwung als Ganzkörper-Peitsche: Ausholen = Gewicht aufs rechte Bein, Becken + Brust drehen nach
    rechts, rechter Arm weit hinten-außen, Ellbogen gebeugt, Finger eingerollt → Schlag: Welle läuft Becken → Brust →
    Oberarm → Unterarm → Hand → Finger (jedes Glied später, schneller), Arm fegt fast waagerecht von rechts über vorn
    nach links, Finger schnellen auf → Durchschwingen nach links, Gewicht aufs linke Bein → schwer zurück."""
    N, w, s_ = P["frames"], P["windup_end"], P["strike_end"]
    side = P["side"]
    sg = 1 if side == "L" else -1                     # Peitsche des rechten Arms schwingt nach links (+)
    dirn = -sg

    def wind(f):
        return ease(f / w) if f <= w else (max(0.0, 1 - ease((f - w) / (s_ - w))) if f <= s_ else 0.0)

    def strike(f):
        if f <= w:
            return 0.0
        if f <= s_:
            return ease_in((f - w) / (s_ - w), 1.6)
        return 1 - ease((f - s_ - 4) / (N - 6 - s_ - 4)) if f > s_ + 4 else 1.0

    lag = P["chain_lag"]

    def sp(fn, fr, z, k):
        return spring_curve(lambda f: fn(f - k * lag), N, fr, z)

    C = {
        "yaw": sp(lambda f: R(P["yaw_wind_deg"]) * wind(f) + R(P["yaw_strike_deg"]) * strike(f), 3.0, 0.5, 0),
        "dy": sp(lambda f: P["shift"] * HGT * (-wind(f) + strike(f)) * dirn, 2.5, 0.5, 0),
        "twist": sp(lambda f: R(P["twist_wind_deg"]) * wind(f) + R(P["twist_strike_deg"]) * strike(f), 2.8, 0.45, 1),
        "sweep": sp(lambda f: P["sweep_wind_deg"] * wind(f) + P["sweep_strike_deg"] * strike(f), 2.6, 0.4, 2),
        "out": sp(lambda f: P["out_wind_deg"] * wind(f) + P["out_strike_deg"] * strike(f), 2.8, 0.45, 2),
        "elbow": sp(lambda f: P["elbow_wind_deg"] * wind(f) + P["elbow_strike_deg"] * strike(f) + 8 * (1 - strike(f)) * (f > s_), 2.3, 0.35, 3),
        "wrist": sp(lambda f: 20 * wind(f) - 15 * strike(f), 2.0, 0.3, 4),
        "fing": sp(lambda f: P["finger_wind_deg"] * wind(f) + P["finger_strike_deg"] * strike(f), 1.8, 0.3, 5),
        "other": sp(lambda f: P["other_arm_deg"] * strike(f) + 8 * wind(f), 2.2, 0.4, 2),
        "side": sp(lambda f: R(5) * wind(f) - R(6) * strike(f), 2.5, 0.5, 1),
        "lean": sp(lambda f: STAND["lean_deg"] + (P["lean_deg"] - STAND["lean_deg"]) * max(wind(f), strike(f)), 3.0, 0.5, 0),
    }
    twc = spring_curve(lambda f: C["twist"][max(0, min(N, int(f)))], N, 1.5, 0.3)
    other = "L" if side == "R" else "R"

    def pose(f):
        body(dy=C["dy"][f], yaw=C["yaw"][f] * dirn, roll=C["side"][f] * dirn * 0.4)
        posture(C["lean"][f], STAND["side_deg"], side=C["side"][f] * dirn, twist=C["twist"][f] * dirn)
        crown(yaw=P["crown_k"] * (twc[f] - C["twist"][f]) * dirn, roll=-C["side"][f] * dirn * 0.5)
        arm_fk(side, swing=8 * wind(f), out=C["out"][f], sweep=C["sweep"][f] * dirn, elbow=C["elbow"][f],
               wrist=C["wrist"][f], fingers=C["fing"][f], shrug=10 * max(wind(f), strike(f)))
        arm_fk(other, swing=C["other"][f], out=10 * max(wind(f), strike(f)), elbow=10 + 6 * wind(f), fingers=-6 * strike(f))
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "reach": "smooth",
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


# ---------------------------------------------------------------- Hit
def clip_hit(P):
    """Treffer: Ruck zurück; Brust, Krone, Arme und Finger laufen zeitversetzt nach (Follow-Through), zurück in den Stand."""
    N = P["frames"]

    def k_at(f, lag=0.0):
        if f <= lag:
            return 0.0
        x = (f - lag) / (N - lag)
        return 0.0 if x >= 1 else math.sin(math.pi * min(1.0, x * 2.2)) * (1 - x) ** 1.5

    def pose(f):
        k, k1, k2, k3 = k_at(f), k_at(f, 1.5), k_at(f, 3), k_at(f, 4.5)
        body(dx=-P["jolt"] * HGT * k, roll=R(P["roll_deg"]) * k1)
        stand_posture(flex=-R(P["pitch_deg"]) * k1, twist=R(5) * k2)
        crown(pitch=R(6) * P["crown_k"] * (k3 - k1) * 2.0, roll=-R(4) * k3)
        for s in ("L", "R"):
            arm_fk(s, swing=P["arm_fling_deg"] * k2, out=8 * k2, elbow=14 * k3, fingers=-18 * k3)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


# ---------------------------------------------------------------- Death (PLATZHALTER)
def clip_death(P):
    """PLATZHALTER – Death pausiert (Nutzer, 2026-11-17). Minimal: sackt etwas ein und neigt sich vor. Keine Arbeit
    hineinstecken, bis der Nutzer Death-Clips freigibt."""
    N = P["frames"]

    def pose(f):
        k = ease(f / N)
        body(dz=-P["sag"] * HGT * k)
        stand_posture(lean=STAND["lean_deg"] + (P["lean_deg"] - STAND["lean_deg"]) * k)
        for s in ("L", "R"):
            arm_fk(s, swing=-4 * k, elbow=6 * k)
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "placeholder": "Death pausiert (Nutzer)",
            "events": [{"frame": N, "event": "dead"}]}


turn = R(ST["turn"]["turn_deg"])
K.bake({
    "Walk": locomotion(ST["walk"]),
    "Run": locomotion(ST["run"]),
    "TurnLeft": locomotion(ST["turn"], turn=turn),
    "TurnRight": locomotion(ST["turn"], turn=-turn),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Attack2": clip_attack2(ST["attack2"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
})
