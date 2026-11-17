"""Bewegungsmuster crawler/ant: backt alle Clips auf ein gerigtes Krabbler-Modell + Selbstprüfung.

& "D:\\Blender\\blender.exe" -b <crawler_rigged.blend> -P motions/crawler/ant/ant_clips.py -- <ausgabeordner> [<creature.toml>]
Ergebnis: <ausgabe>/crawler_clips.blend (alle Actions), clips_report.json, events.json
Gemeinsame Bausteine: ../crawler_kit.py
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import crawler_kit as K  # noqa: E402

K.init(HERE)
from crawler_kit import *  # noqa: E402,F401,F403
from crawler_kit import ST, LEG, walking, feelers, SIZE, R, FWD, LEFT, UP, ease, phase  # noqa: E402


def clip_locomotion(P, mode):
    N = P["cycle_frames"]

    def pose(f):
        t = (f % N) / N
        reset()
        gait(t, P, mode)
        feeler_motion(t, P["feeler_deg"], P["feeler_speed"])
        body_wave(t, P)
        antennae(t, P["antenna_deg"], P["antenna_speed"], P["antenna_tip_factor"], P["antenna_stabilize"])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"],
            "axis": "x" if mode == "forward" else "turn",
            "swing": lambda leg, f: phase((f % N) / N, leg_offset(leg, P), P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        reset()
        feeler_motion(t, P["feeler_deg"], 1)
        one = 2 * math.pi * t
        rot("Abdomen_1", LEFT, -R(P["breathe_deg"]) * (0.5 - 0.5 * math.cos(2 * one)))
        rot("Thorax", FWD, R(P["weight_shift_deg"]) * math.sin(one))
        rot("Head", UP, R(P["head_look_deg"]) * math.sin(one) * (0.6 + 0.4 * math.sin(2 * one)))
        rot("Head", LEFT, -R(P["head_look_deg"]) * 0.3 * math.sin(3 * one))
        antennae(t, P["antenna_deg"], P["antenna_speed"], P["antenna_tip_factor"], P["antenna_stabilize"])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        reset()
        tr = R(P["tremble_deg"]) * math.sin(2 * math.pi * P["tremble_speed"] * t)
        feeler_motion(t, 4, 1, raise_deg=P["feeler_raise_deg"])
        rot("Head", LEFT, -R(P["head_up_deg"]) + tr)
        rot("Abdomen_1", LEFT, -R(P["gaster_raise_deg"]) + tr * 1.5)
        rot("Abdomen_2", LEFT, -R(P["gaster_raise_deg"]) * 0.5)
        antennae(t, 2, 1, 0.4, 0.5, forward_deg=P["antenna_forward_deg"])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_attack1(P):
    N, w_end, s_end = P["frames"], P["windup_end"], P["strike_end"]

    def pose(f):
        reset()
        if f <= w_end:
            k = ease(f / w_end)
            pitch, pull = -R(P["head_pitch_up_deg"]) * k, -P["head_pull"] * k
        elif f <= s_end:
            k2 = ease((f - w_end) / (s_end - w_end))
            pitch = -R(P["head_pitch_up_deg"]) * (1 - k2) + R(P["head_pitch_down_deg"]) * k2
            pull = -P["head_pull"] * (1 - k2) + P["head_lunge"] * k2
        else:
            k3 = ease((f - s_end) / (N - s_end))
            pitch, pull = R(P["head_pitch_down_deg"]) * (1 - k3), P["head_lunge"] * (1 - k3)
        windup = ease(f / w_end) if f <= w_end else max(0.0, 1 - ease((f - w_end) / (N - w_end)))
        move("Head", FWD * pull * SIZE)
        rot("Head", LEFT, pitch)
        rot("Thorax", LEFT, -R(P["thorax_pitch_deg"]) * windup + R(P["thorax_pitch_deg"]) * (1 - windup) * (f > w_end) * (f < N))
        rot("Abdomen_1", LEFT, -R(P["gaster_deg"]) * windup)
        feeler_motion(f / N, 3, 1, raise_deg=P["feeler_raise_deg"] * windup)
        antennae(f / N, 2, 1, 0.4, 0.6, forward_deg=8 * windup)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        reset()
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        rot("Head", LEFT, -R(P["head_back_deg"]) * k)
        rot("Thorax", UP, R(P["thorax_jerk_deg"]) * k)
        rot("Abdomen_1", UP, -R(P["abdomen_deg"]) * k)
        antennae(0, 0, 1, 0.4, 0.0, droop_deg=-P["antenna_flick_deg"] * k)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


K.bake({
    "Walk": clip_locomotion(ST["walk"], "forward"),
    "Run": clip_locomotion(ST["run"], "forward"),
    "TurnLeft": clip_locomotion(ST["turn"], "turn_left"),
    "TurnRight": clip_locomotion(ST["turn"], "turn_right"),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": death_flip(ST["death"]),
})
