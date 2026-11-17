"""Bewegungsmuster multileg/scorpion: Gang (alternierende Beingruppen), Drehen, Idle, Drohen, Stich, Treffer, Tod.
Nutzt den Beine-Baukasten ../../quadruped/quadruped_kit.py (Blender-IK für beliebig viele Beine).

& "D:\\Blender\\blender.exe" -b <multileg_rigged.blend> -P motions/multileg/scorpion/scorpion_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "quadruped"))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
from quadruped_kit import FWD, LEFT, UP, R, body, ease, gait, ik_off, phase, rot  # noqa: E402

ST, SIZE, HGT, LEGS = K.ST, K.SIZE, K.HGT, K.LEGS
CLAWS = sorted({b.name[5] for b in K.DB if b.name.startswith("Claw_")})
TAIL = [n for n in ("Tail_1", "Tail_2", "Tail_3", "Tail_4", "Tail_5", "Stinger") if n in K.DB]


def offsets(P):
    """Gruppe A = L1 R2 L3 R4 L5 …, Gruppe B gegenphasig; kleine Welle von vorn nach hinten."""
    out = {}
    for leg in LEGS:
        k = int(leg[1:])
        a = (leg[0] == "L") == (k % 2 == 1)
        out[leg] = (0.0 if a else 0.5) + P.get("wave", 0) * (k - 1)
    return out


def claws(raise_deg=0.0, spread_deg=0.0, pinch_deg=0.0):
    for s in CLAWS:
        sg = 1 if s == "L" else -1
        rot(f"Claw_{s}_1", LEFT, -R(raise_deg))
        rot(f"Claw_{s}_1", UP, sg * R(spread_deg))
        rot(f"Claw_{s}_3", UP, -sg * R(pinch_deg))


def tail(curl_deg=0.0, sway_deg=0.0, t=0.0):
    """curl + = Schwanz weiter nach vorn über den Rücken krümmen, sway = seitlich pendeln."""
    for i, n in enumerate(TAIL):
        rot(n, LEFT, R(curl_deg) / len(TAIL))
        rot(n, UP, R(sway_deg) * math.sin(2 * math.pi * t - i * 0.5) / len(TAIL) * 2)


def locomotion(P, turn=0.0):
    N, off = P["cycle_frames"], offsets(P)

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=turn) if turn else gait(t, P, off)
        body(dz=-P.get("bob", 0) * HGT * math.cos(4 * math.pi * t))
        claws(raise_deg=P.get("claw_raise_deg", 0))
        tail(sway_deg=P.get("tail_sway_deg", 0), t=t)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "turn": turn,
            "max_stretch": P.get("max_stretch"),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        body(dz=0.003 * HGT * math.sin(2 * math.pi * 2 * t))
        for s in CLAWS:
            sg = 1 if s == "L" else -1
            rot(f"Claw_{s}_3", UP, -sg * R(P["claw_deg"]) * max(0, math.sin(2 * math.pi * 2 * t + (0 if s == "L" else math.pi))))
        tail(sway_deg=P["tail_sway_deg"], t=t)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        body(dz=P["raise"] * HGT, roll=R(P["tremble_deg"]) * math.sin(2 * math.pi * 5 * t))
        claws(raise_deg=P["claw_raise_deg"], spread_deg=P["claw_spread_deg"])
        tail(curl_deg=P["tail_curl_deg"], sway_deg=2, t=t)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch")}


def clip_attack1(P):
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]

    def pose(f):
        if f <= w:
            k_w, k_s = ease(f / w), 0.0
        elif f <= s:
            x = ease((f - w) / (s - w))
            k_w, k_s = 1 - x, x
        elif f <= h:
            k_w, k_s = 0.0, 1.0
        else:
            k_w, k_s = 0.0, 1 - ease((f - h) / (N - h))
        body(dz=0.04 * HGT * (k_w + k_s), pitch=-R(5) * k_w + R(4) * k_s)
        claws(raise_deg=10 * k_w, spread_deg=12 * k_w - 6 * k_s, pinch_deg=P["claw_grab_deg"] * k_s)
        tail(curl_deg=-P["tail_back_deg"] * k_w + P["tail_strike_deg"] * k_s)
        rot(TAIL[0], LEFT, R(P.get("tail_base_strike_deg", 0)) * k_s - R(10) * k_w)   # Schwanzwurzel kippt mit
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        body(dx=-P["jolt"] * SIZE * k, roll=R(P["roll_deg"]) * k)
        claws(raise_deg=-10 * k, spread_deg=-8 * k)
        tail(curl_deg=-15 * k)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    """Krabbler-Tod: über die Längsachse auf den Rücken kippen (ganzer Körper dreht mit → keine Gelenk-
    Verzerrung), IK aus, Beine in der Luft. Jeder Frame liegt genau auf dem Boden auf."""
    from mathutils import Quaternion
    N, c1 = P["frames"], P["collapse_end"]
    h0 = K.DB["Root"].head_local
    piv = K.DB["Hips"].head_local.copy()

    def pose(f):
        k = ease(f / c1)
        q = Quaternion(FWD, math.pi * k * P.get("flip_side", 1))
        rot("Root", FWD, math.pi * k * P.get("flip_side", 1))
        K.move("Root", (piv - h0) - q @ (piv - h0))
        for leg in LEGS:
            ik_off(leg, ease(k / 0.3))
        claws(raise_deg=10 * k)
        tail(curl_deg=-P["tail_drop_deg"] * k)
        bpy.context.view_layer.update()
        K.move("Root", Vector((0, 0, K.GROUND - K.mesh_min_z())))     # liegt auf dem Boden (nicht drin, nicht drüber)
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "max_stretch": P.get("max_stretch"),
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
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
})
