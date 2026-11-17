"""Bewegungsmuster octopod/crab: Seitwärtsgang per Planar-IK, Scheren-Haltung und -Angriff.

& "D:\\Blender\\blender.exe" -b <octopod_rigged.blend> -P motions/octopod/crab/crab_clips.py -- <ausgabeordner> [<creature.toml>]
Gemeinsame Bausteine: ../octopod_kit.py
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import octopod_kit as K  # noqa: E402

K.init(HERE)
from octopod_kit import *  # noqa: E402,F401,F403
from octopod_kit import ST, LEG, walking, feelers, SIZE, R, FWD, LEFT, UP, ease, phase  # noqa: E402


def side_of(leg):
    return 1 if leg[0] == "L" else -1


def crab_offset(leg, P, direction):
    """Phasenversatz nach Krabben-Schrittfolge: führende Seite = Seite in Laufrichtung."""
    leading = side_of(leg) == direction          # direction: +1 = nach links (+Y), -1 = nach rechts
    order = P["leading_order"] if leading else P["trailing_order"]
    present = [s for s in order if f"L{s}" in walking or f"R{s}" in walking]
    idx = present.index(int(leg[1]))
    return idx / len(present) + (0.0 if leading else 0.5)


def claws_hold(raise_deg, spread_deg=0.0, sway=0.0, back_deg=0.0, fold_deg=0.0, only=None):
    for leg in feelers:
        if only and leg not in only:
            continue
        s = side_of(leg)
        # spread = Scheren nach außen schwenken; back = nach hinten ausholen
        set_leg(leg, back=R(back_deg) + R(sway), lift=R(raise_deg), fold=R(fold_deg),
                tuck=-s * R(spread_deg) * LEG[leg]["back_sign"] * 0 + s * R(spread_deg))


RAISE_MAX = K.max_body_raise() / SIZE          # was die Beine an Körperhebung hergeben (Anteil Größe)


def body_raise_planted(h):
    """Rumpf um h (Anteil Größe) heben/senken; Füße bleiben per IK exakt stehen. Begrenzt auf das,
    was die Beine hergeben (sonst schweben die Füße)."""
    h = min(h, RAISE_MAX)
    move("Thorax", UP * h * SIZE)
    for leg in walking:
        set_leg_ik(leg, 0.0, 0.0, -h * SIZE)


def rear_split(P):
    """Aufbäumen: vorderste Laufbein-Paare heben mit ab, die übrigen (hinteren) tragen den Körper."""
    slots = sorted({int(l[1]) for l in walking})
    lifted_slots = slots[:P.get("lift_front_pairs", 1)]
    carry = [l for l in walking if int(l[1]) not in lifted_slots]
    lifted = [l for l in walking if int(l[1]) in lifted_slots]
    hips = [DB[f"Leg_{l}_Coxa"].head_local for l in carry if int(l[1]) == min(int(c[1]) for c in carry)]
    pivot = sum(hips, Vector()) / len(hips)          # Kipp-Achse = Hüftlinie des vordersten tragenden Paars
    return carry, lifted, Vector((pivot.x, 0.0, pivot.z))


def rear_up(pitch, carry, lifted, pivot, P, k=1.0):
    """Rumpf vorne um 'pitch' (rad) anheben, Kippachse quer durch 'pivot'. Tragende Füße bleiben per
    Fuß-IK exakt stehen, die vorderen Laufbeine heben mit ab und ziehen sich leicht an, der Hinterleib
    wird gegengedreht (sonst sackt er Richtung Boden)."""
    q = Quaternion(LEFT, -pitch)                     # -: Vorderseite (+X) hoch
    h = DB["Thorax"].head_local
    rot("Thorax", LEFT, -pitch, mul=False)
    move("Thorax", (pivot - h) - q @ (pivot - h))
    rot("Abdomen_1", LEFT, pitch * P["abdomen_counter"])
    to_arm = arm.matrix_world.inverted()
    qi = q.inverted()
    for leg in carry:
        F = to_arm @ REST_FOOT[leg]
        d = (pivot + qi @ (F - pivot)) - F           # Ziel im Ruhe-Raum des Rumpfs
        set_foot(leg, d.x, d.y, d.z)
    for leg in lifted:
        set_leg(leg, back=-R(P["front_legs_forward_deg"]) * k, lift=R(P["front_legs_lift_deg"]) * k,
                fold=-R(P["front_legs_fold_deg"]) * k)


def carry_error(carry):
    bpy.context.view_layer.update()
    return max((foot(l) - REST_FOOT[l]).length for l in carry)


def max_rear_pitch(P, carry, lifted, pivot, want):
    """Größter Kippwinkel ≤ want, bei dem die tragenden Füße noch exakt stehen (Bisektion)."""
    tol = ST["checks"]["planted_tolerance"] * SIZE * 0.5
    reset(); rear_up(want, carry, lifted, pivot, P)
    if carry_error(carry) <= tol:
        return want
    lo, hi = 0.0, want
    for _ in range(16):
        mid = (lo + hi) / 2
        reset(); rear_up(mid, carry, lifted, pivot, P)
        lo, hi = (mid, hi) if carry_error(carry) <= tol else (lo, mid)
    return lo


def lateral_amplitudes(P):
    """Pro Bein: Amplitude A (gleiche seitliche Strecke für alle Füße) + Mittelpunkt-Verschiebung c.
    Kann ein Bein nicht weiter hinausreichen (gestreckt), wird sein Arbeitsbereich nach innen verlegt."""
    stride = P["stride"] * SIZE
    amp_, center = {}, {}
    for leg in walking:
        lat = max(0.35, LEG[leg]["ik"]["lateral"])
        A = min(stride / 2 / lat, P["reach_max"] * SIZE)
        out_max = K.ik_limits(leg)[0]
        amp_[leg] = A
        center[leg] = min(0.0, out_max - A)
    return amp_, center, stride


def clip_sideways(P, direction):
    N = P["cycle_frames"]
    # Arbeitsbereich pro Bein: Beine, die nach außen nicht weiter reichen, schieben ihren Bereich nach innen
    CENTER_Y = {}
    half = P["stride"] * SIZE / 2
    for leg in walking:
        out = side_of(leg)                              # +Y = außen für linke Beine
        reach_out = K.max_foot_shift(leg, 0.0, out, half)   # exakt erreichbare Außenverschiebung
        CENTER_Y[leg] = -out * (half - reach_out)       # Rest nach innen verlegen
    print(f"  crab {['links', '', 'rechts'][1 - direction]}: Schrittlänge {P['stride'] * SIZE:.3f} m, "
          f"Körperhebung max {RAISE_MAX * SIZE:.3f} m, Bereich nach innen verschoben: "
          f"{ {k: round(v, 3) for k, v in CENTER_Y.items() if v} }")

    def pose(f):
        t = (f % N) / N
        reset()
        bob = P["body_bob"] * math.sin(2 * math.pi * 2 * t)
        move("Thorax", UP * bob * SIZE)
        rot("Thorax", FWD, -direction * R(P["body_roll_deg"]))
        S = P["stride"] * SIZE
        for leg in walking:
            swing, s = phase(t, crab_offset(leg, P, direction), P["duty"])
            # Körper bewegt sich in 'direction' (+Y links) → Füße relativ zum Körper entgegen.
            # Fuß-IK: nach vorne zeigende Beine erledigen das über die Hüfte, seitliche über die Reichweite.
            dy = -direction * ((-S / 2 + S * s) if not swing else (S / 2 - S * ease(s)))
            dw = P["lift"] * SIZE * math.sin(math.pi * s) if swing else 0.0
            set_foot(leg, 0.0, dy + CENTER_Y[leg], dw - bob * SIZE)
        claws_hold(P["claw_raise_deg"], sway=P["claw_sway_deg"] * math.sin(2 * math.pi * t))
        antennae(t, P["antenna_deg"], P["antenna_speed"], 0.4, P["antenna_stabilize"])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "axis": "y",
            "swing": lambda leg, f: phase((f % N) / N, crab_offset(leg, P, direction), P["duty"])[0]}


def clip_turn(P, mode):
    N = P["cycle_frames"]

    def pose(f):
        t = (f % N) / N
        reset()
        gait(t, P, mode)
        claws_hold(P["claw_raise_deg"])
        antennae(t, P["antenna_deg"], P["antenna_speed"], 0.4, P["antenna_stabilize"])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "axis": "turn",
            "swing": lambda leg, f: phase((f % N) / N, leg_offset(leg, P), P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        reset()
        body_raise_planted(P["body_bob"] * math.sin(2 * math.pi * 2 * t))
        one = 2 * math.pi * t
        for leg in feelers:            # Scheren abwechselnd zum Mund (fressen)
            s = side_of(leg)
            k = max(0.0, math.sin(one + (0 if s > 0 else math.pi)))
            set_leg(leg, back=0.0, lift=R(P["claw_raise_deg"]) + R(P["claw_feed_deg"]) * k,
                    fold=-R(P["claw_feed_deg"]) * 1.5 * k, tuck=-s * R(P["claw_feed_deg"]) * k)
        antennae(t, P["antenna_deg"], P["antenna_speed"], 0.5, 0.0)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        reset()
        tr = P["tremble_deg"] * math.sin(2 * math.pi * P["tremble_speed"] * t)
        body_raise_planted(P["body_raise"])
        claws_hold(P["claw_raise_deg"] + tr, spread_deg=P["claw_spread_deg"])
        antennae(t, 3, 2, 0.4, 0.5, forward_deg=8)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_attack1(P):
    N, w_end, s_end, h_end = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    striker = [l for l in feelers if l[0] == "L"] or feelers[:1]
    carry, lifted, pivot = rear_split(P)
    pitch = max_rear_pitch(P, carry, lifted, pivot, R(P["rear_pitch_deg"]))
    print(f"  crab attack: aufbäumen auf {carry}, Kippwinkel {math.degrees(pitch):.1f}° "
          f"(gewünscht {P['rear_pitch_deg']}°), vorne hoch: {lifted}")

    def pose(f):
        reset()
        if f <= w_end:                                  # Drohhaltung + Ausholen (Telegraph)
            k = ease(f / w_end)
            raise_, back, down = P["claw_raise_deg"] * k, -P["claw_back_deg"] * k, 0.0
        elif f <= s_end:                                # Zuschnappen in 2 Frames
            k2 = (f - w_end) / (s_end - w_end)
            raise_ = P["claw_raise_deg"] * (1 - k2) - P["strike_down_deg"] * k2
            back = -P["claw_back_deg"] * (1 - k2) + P["strike_forward_deg"] * k2
        elif f <= h_end:                                # kurz halten
            raise_, back = -P["strike_down_deg"], P["strike_forward_deg"]
        else:                                           # zurück
            k3 = ease((f - h_end) / (N - h_end))
            raise_, back = -P["strike_down_deg"] * (1 - k3), P["strike_forward_deg"] * (1 - k3)
        body = ease(f / w_end) if f <= h_end else 1 - ease((f - h_end) / (N - h_end))
        # Aufbäumen beim Ausholen, beim Zuschnappen leicht nach vorne "hineinfallen" (mehr Wucht)
        drop = P["strike_pitch_drop"] * (ease((f - w_end) / (s_end - w_end)) if w_end < f <= h_end else 0.0)
        rear_up(pitch * body * (1 - drop), carry, lifted, pivot, P, k=body)
        guard = [l for l in feelers if l not in striker]
        claws_hold(P["claw_raise_deg"] * 0.7 * body, spread_deg=15 * body, only=guard)
        for leg in striker:
            # "back" negativ = Schere nach vorne; Vorzeichen über back_sign der Hüfte
            set_leg(leg, back=-R(back), lift=R(raise_), fold=R(-20 if f > w_end else 10) * body)
        antennae(f / N, 2, 2, 0.4, 0.5, forward_deg=6 * body)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "planted": carry,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        reset()
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        body_raise_planted(-P["body_drop"] * k)
        claws_hold(0.0, spread_deg=-P["claw_tuck_deg"] * k)
        antennae(0, 0, 1, 0.4, 0.0, droop_deg=12 * k)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


K.bake({
    "Walk": clip_sideways(ST["walk"], -1),       # seitwärts nach rechts
    "WalkLeft": clip_sideways(ST["walk"], 1),
    "Run": clip_sideways(ST["run"], -1),
    "TurnLeft": clip_turn(ST["turn"], "turn_left"),
    "TurnRight": clip_turn(ST["turn"], "turn_right"),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": death_flip(ST["death"]),
})
