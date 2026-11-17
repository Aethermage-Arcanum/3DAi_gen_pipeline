"""Bewegungsmuster biped_raptor/raptor: Schritt, Laufvogel-Rennen, Drehen, Idle, Drohen, Stampf-Tritt,
Treffer, Tod. Nutzt den Beine-Baukasten ../../quadruped/quadruped_kit.py (Blender-IK für die Beine).

& "D:\\Blender\\blender.exe" -b <biped_raptor_rigged.blend> -P motions/biped_raptor/raptor/raptor_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Quaternion, Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "quadruped"))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
from quadruped_kit import (FWD, LEFT, UP, R, body, ease, gait, ik_off, jaw, neck_head, phase,  # noqa: E402
                           rot, set_foot, spine, tail)

ST, SIZE, HGT, LEGS = K.ST, K.SIZE, K.HGT, K.LEGS
ARMS = sorted({b.name[4] for b in K.DB if b.name.startswith("Arm_")})


def arms(up_deg=0.0, swing_deg=0.0, t=0.0, spread_deg=0.0):
    """Greifarme: up = nach vorn/oben anheben, swing = Pendeln im Gang, spread = Krallen auseinander."""
    for s in ARMS:
        sg = 1 if s == "L" else -1
        rot(f"Arm_{s}_1", LEFT, -R(up_deg) - R(swing_deg) * math.sin(2 * math.pi * t + (0 if s == "L" else math.pi)))
        rot(f"Arm_{s}_1", FWD, sg * R(spread_deg))
        rot(f"Arm_{s}_2", LEFT, -R(up_deg) * 0.6)


def locomotion(P, turn=0.0):
    N, off = P["cycle_frames"], P["order"]

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=turn) if turn else gait(t, P, off)
        bob = -P.get("bob", 0) * HGT * math.cos(4 * math.pi * t)
        # Rumpf rollt zum Standbein (Gewichtsverlagerung), Rumpf neigt sich beim Rennen nach vorn
        body(dz=bob, roll=R(P.get("roll_deg", 0)) * math.sin(2 * math.pi * t),
             pitch=-R(P.get("lean_deg", 0)) + R(P.get("pitch_deg", 0)) * math.sin(4 * math.pi * t))
        neck_head(stabilize=P.get("head_stabilize", 0))
        tail(t, P.get("tail_deg", 0), 1, P.get("tail_lift_deg", 0) + P.get("lean_deg", 0))
        arms(up_deg=10, swing_deg=P.get("arm_swing_deg", 0), t=t)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "turn": turn,
            "max_stretch": P.get("max_stretch"),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]
    looks = [(0.0, 0.0), (0.15, 1.0), (0.4, -0.6), (0.65, 0.3), (0.85, 0.0)]   # ruckartig + halten

    def look(t):
        for (t0, a0), (t1, a1) in zip(looks, looks[1:] + [(1.0, 0.0)]):
            if t0 <= t < t1:
                return a0 + (a1 - a0) * ease(min(1.0, (t - t0) / 0.05))
        return 0.0

    def pose(f):
        t = f / N
        body(dz=0.004 * HGT * math.sin(2 * math.pi * 3 * t))
        rot("Chest", LEFT, R(P["breathe_deg"]) * math.sin(2 * math.pi * 3 * t))
        neck_head(yaw=R(P["look_deg"]) * look(t))
        tail(t, P["tail_deg"], 2, 0)
        arms(up_deg=10 + 3 * math.sin(2 * math.pi * 2 * t))
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        tr = R(P["tremble_deg"]) * math.sin(2 * math.pi * 6 * t)
        body(dz=-P["crouch"] * HGT, pitch=-R(6) + tr * 0.3)
        neck_head(pitch=-R(P["head_down_deg"]), head_pitch=R(P["head_down_deg"]) * 0.5)
        jaw(P["jaw_deg"] + 3 * math.sin(2 * math.pi * 3 * t))
        tail(t, 2, 3, P["tail_lift_deg"])
        arms(up_deg=P["arms_up_deg"], spread_deg=10)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch")}


def clip_attack1(P):
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    kl = P["kick_leg"]

    def pose(f):
        if f <= w:
            up, fwd, k_b = ease(f / w), 0.3 * ease(f / w), ease(f / w)
        elif f <= s:
            x = ease((f - w) / (s - w))
            up, fwd, k_b = 1 - x, 0.3 + 0.7 * x, 1.0
        elif f <= h:
            up, fwd, k_b = 0.0, 1.0, 1.0
        else:
            x = ease((f - h) / (N - h))
            up, fwd, k_b = 0.0, 1 - x, 1 - x
        set_foot(kl, Vector((P["kick_reach"] * SIZE * fwd, 0, P["kick_height"] * HGT * up)), R(40) * up)
        body(pitch=R(P["lean_back_deg"]) * k_b * (1 - 0.5 * fwd), dy=0.02 * SIZE * k_b * (1 if kl[1] == "R" else -1))
        neck_head(pitch=R(8) * k_b, head_pitch=-R(6) * k_b)
        jaw(P["jaw_deg"] * k_b)
        tail(0, 0, 1, -10 * k_b)
        arms(up_deg=25 * k_b, spread_deg=12 * k_b)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "planted": [l for l in LEGS if l != kl],
            "max_stretch": P.get("max_stretch"),
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        body(dx=-P["jolt"] * SIZE * k, roll=R(P["roll_deg"]) * k)
        neck_head(yaw=R(P["head_deg"]) * k, pitch=R(8) * k)
        tail(0, 0, 1, 10 * k)
        arms(up_deg=15 * k)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    N, c0, c1, side = P["frames"], P["collapse_start"], P["collapse_end"], P["side"]
    feet = [K.REST[l]["ball"] for l in LEGS]
    piv = sum(feet, Vector()) / len(feet) + Vector((0, -side * 0.06 * SIZE, 0))
    h0 = K.DB["Root"].head_local

    def raw(f):
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        q = Quaternion(FWD, side * R(85) * k)
        rot("Root", FWD, side * R(85) * k)
        K.move("Root", (piv - h0) - q @ (piv - h0))
        for leg in LEGS:
            ik_off(leg, ease((k - 0.2) / 0.4))   # Beine geben erst nach, wenn der Körper halb gekippt ist (sonst schwebt er)
            rot(f"Leg_{leg}_1", LEFT, -R(P["legs_limp_deg"]) * k)
            rot(f"Leg_{leg}_2", LEFT, R(P["legs_limp_deg"]) * k)
        neck_head(pitch=-R(15) * k - R(8) * jolt)
        jaw(15 * k)
        tail(0, 0, 1, -15 * k)
        arms(up_deg=-10 * k)
        return k

    K.reset()
    raw(N)
    bpy.context.view_layer.update()
    drop = K.mesh_min_z() - K.GROUND

    def pose(f):
        k = raw(f)
        K.move("Root", Vector((0, 0, -drop * k)))
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
