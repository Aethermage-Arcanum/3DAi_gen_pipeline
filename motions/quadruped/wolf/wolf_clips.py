"""Bewegungsmuster quadruped/wolf: Schritt (lateraler Viertakt), Galopp, Drehen, Idle, Drohen, Sprung-Biss,
Treffer, Tod. Gemeinsame Bausteine: ../quadruped_kit.py

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/wolf/wolf_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

# Andere Vierbeiner-Muster (lizard, deer …) nutzen diesen Generator mit ihrer eigenen style.toml:
#   runpy.run_path(".../wolf/wolf_clips.py", init_globals={"STYLE_DIR": <ihr Ordner>}, run_name="__main__")
HERE = globals().get("STYLE_DIR") or pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
from quadruped_kit import (FWD, LEFT, UP, LEGS, R, body, ease, gait, ik_off, jaw, neck_head,  # noqa: E402
                           phase, rot, set_foot, spine, tail)
from mathutils import Vector  # noqa: E402

ST, SIZE, HGT = K.ST, K.SIZE, K.HGT


def locomotion(P, turn=0.0):
    N = P["cycle_frames"]
    off = P["order"]

    def pose(f):
        t = (f % N) / N
        if turn:
            gait(t, P, off, turn=turn)
        else:
            gait(t, P, off)
        bob = -P.get("bob", 0) * HGT * math.cos(4 * math.pi * t)
        pitch = R(P.get("pitch_deg", 0)) * math.sin(2 * math.pi * t)
        roll = R(P.get("roll_deg", 0)) * math.sin(2 * math.pi * t)
        body(dz=bob, pitch=pitch, roll=roll)
        spine(flex=R(P.get("spine_flex_deg", 0)) * math.sin(2 * math.pi * t + 0.6),
              side=R(P.get("spine_side_deg", 0)) * math.sin(2 * math.pi * t))      # Echsen: seitliche Welle
        neck_head(head_pitch=R(P.get("head_bob_deg", 0)) * math.sin(4 * math.pi * t),
                  stabilize=P.get("head_stabilize", 0))
        tail(t, P.get("tail_deg", 0), 1, P.get("tail_lift_deg", 0))
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "turn": turn,
            "max_stretch": P.get("max_stretch"),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        body(dz=0.004 * HGT * math.sin(2 * math.pi * 3 * t))
        rot("Chest", LEFT, R(P["breathe_deg"]) * math.sin(2 * math.pi * 3 * t))
        look = math.sin(2 * math.pi * t) * ease(min(1, abs(math.sin(2 * math.pi * t)) * 1.5))
        neck_head(yaw=R(P["look_deg"]) * look, pitch=R(4) * math.sin(2 * math.pi * 2 * t))
        tail(t, P["tail_deg"], 2, -10)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        tr = R(P["tremble_deg"]) * math.sin(2 * math.pi * 6 * t)
        body(dz=-P["crouch"] * HGT, pitch=-R(4) + tr * 0.3)
        neck_head(pitch=-R(P["head_down_deg"]), head_pitch=R(P["head_down_deg"]) * 0.6)
        jaw(P["jaw_deg"] + 3 * math.sin(2 * math.pi * 3 * t))
        tail(t, 1.5, 3, P["tail_lift_deg"])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch")}


def clip_attack1(P):
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]

    def pose(f):
        if f <= w:
            k_c, k_l, k_j = ease(f / w), 0.0, ease(f / w) * 0.4
        elif f <= s:
            x = (f - w) / (s - w)
            k_c, k_l, k_j = 1 - x, ease(x), 1.0 - (x > 0.7) * 1.0
        elif f <= h:
            k_c, k_l, k_j = 0.0, 1.0, 0.0
        else:
            x = ease((f - h) / (N - h))
            k_c, k_l, k_j = 0.0, 1 - x, 0.0
        body(dz=-P["crouch"] * HGT * k_c + P["lunge_up"] * HGT * k_l,
             dx=-0.03 * SIZE * k_c + P["lunge"] * SIZE * k_l, pitch=-R(6) * k_c + R(4) * k_l)
        if P.get("type") == "headbutt":                  # Hirsch: Kopf tief, Geweih nach vorn stoßen
            neck_head(pitch=-R(P["neck_reach_deg"]) * (0.6 * k_c + k_l), head_pitch=-R(P["neck_reach_deg"]) * 0.35 * k_l)   # Nase runter = Geweih nach vorn
        else:                                             # Biss: Hals streckt, Maul auf → zu
            neck_head(pitch=-R(10) * k_c + R(P["neck_reach_deg"]) * 0.3 * k_l,
                      head_pitch=R(8) * k_c - R(P["neck_reach_deg"]) * 0.4 * k_l,
                      yaw=R(P.get("snap_yaw_deg", 0)) * k_l)
            jaw(P["jaw_open_deg"] * k_j)
        tail(0, 0, 1, 12 * k_l)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        body(dx=-P["jolt"] * SIZE * k, roll=R(P["roll_deg"]) * k)
        neck_head(yaw=R(P["head_deg"]) * k, pitch=R(6) * k)
        tail(0, 0, 1, -15 * k)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    N, c0, c1 = P["frames"], P["collapse_start"], P["collapse_end"]
    side = P["side"]
    # Drehpunkt: Fuß-Linie der Seite, auf die er fällt → Rumpf kippt darüber
    piv = (K.REST["F" + ("R" if side > 0 else "L")]["ball"] + K.REST["B" + ("R" if side > 0 else "L")]["ball"]) / 2
    h0 = K.DB["Root"].head_local

    def raw(f):
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        ang = side * R(88) * k
        from mathutils import Quaternion
        q = Quaternion(FWD, ang)
        loc = (Vector(piv) - h0) - q @ (Vector(piv) - h0)
        rot("Root", FWD, ang)
        K.move("Root", loc)
        for leg in LEGS:
            s0 = P.get("ik_release_start", 0.0)            # wann die Beine loslassen (0 = sofort beim Kippen)
            ik_off(leg, min(1.0, max(0.0, k - s0) * 1.6 / (1 - s0)))
            sgn = 1 if leg[0] == "F" else -1
            rot(f"Leg_{leg}_1", LEFT, sgn * R(P["legs_limp_deg"]) * k)
            rot(f"Leg_{leg}_2", LEFT, -sgn * R(P["legs_limp_deg"]) * k)
        neck_head(pitch=-R(10) * k - R(6) * jolt, yaw=0)
        jaw(14 * k)
        tail(0, 0, 1, -20 * k)
        return k

    # Höhe so nachführen, dass der liegende Körper den Boden berührt (nicht schwebt, nicht einsinkt)
    K.reset()
    raw(N)
    import bpy
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
