"""Bewegungsmuster floater/tentacle: Schweben, Drehen, Quallen-Idle, Drohen (Spreizen), Tentakelschlag,
Treffer, Tod. Gemeinsame Bausteine: ../floater_kit.py

& "D:\\Blender\\blender.exe" -b <floater_rigged.blend> -P motions/floater/tentacle/tentacle_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import floater_kit as K  # noqa: E402

K.init(HERE)
from floater_kit import R, core, ease, tentacles  # noqa: E402

ST, SIZE = K.ST, K.SIZE
HOVER = ST["hover"]["height"] * SIZE


def fly(P, turn=0):
    N = P["cycle_frames"]

    def pose(f):
        t = (f % N) / N
        core(dz=HOVER + P["bob"] * SIZE * math.sin(2 * math.pi * t), pitch=R(P["pitch_deg"]),
             roll=turn * R(P.get("roll_deg", 0)), yaw=turn * R(4) * math.sin(2 * math.pi * t))
        tentacles(t, P["amp_deg"], P["speed"], trail_deg=P["trail_deg"])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        pulse = math.sin(2 * math.pi * 2 * t)
        core(dz=HOVER + P["bob"] * SIZE * pulse)
        tentacles(t, P["amp_deg"], 2, curl_deg=P["pulse_deg"] * pulse)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        core(dz=HOVER + P["lift"] * SIZE, roll=R(P["tremble_deg"]) * math.sin(2 * math.pi * 5 * t))
        tentacles(t, P["amp_deg"], 2, spread_deg=P["spread_deg"])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


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
        core(dz=HOVER, dx=-P["pull_back"] * SIZE * k_w + P["lunge"] * SIZE * k_s,
             pitch=-R(10) * k_w + R(18) * k_s)
        # ausholen = Tentakel nach hinten, Schlag = nach vorn schnellen
        tentacles(f / N, 6, 1, trail_deg=P["windup_deg"] * k_w - P["strike_deg"] * k_s)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        core(dz=HOVER, dx=-P["recoil"] * SIZE * k, pitch=-R(15) * k)
        tentacles(x, P["flail_deg"] * k, 3)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    N, c1 = P["frames"], P["collapse_end"]

    def raw(f):
        k = ease(f / c1)
        core(dz=HOVER * (1 - k), pitch=R(P["tilt_deg"]) * k)
        tentacles(0.0, 10 * (1 - k), 1, curl_deg=-25 * k)         # erschlaffen: Tentakel strecken sich schlaff
        return k

    K.reset()
    raw(N)
    bpy.context.view_layer.update()
    drop = K.mesh_min_z() - K.GROUND                                 # liegt danach genau am Boden

    def pose(f):
        k = raw(f)
        K.move("Root", Vector((0, 0, -drop * k)))
        K.ground_above()
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "events": [{"frame": N, "event": "dead"}]}


K.bake({
    "Walk": fly(ST["walk"]),
    "Run": fly(ST["run"]),
    "TurnLeft": fly(ST["turn"], 1),
    "TurnRight": fly(ST["turn"], -1),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
})
