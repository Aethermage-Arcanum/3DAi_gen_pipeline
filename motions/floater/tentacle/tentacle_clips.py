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
from floater_kit import R, core, drive, ease, tentacles, wobble  # noqa: E402

ST, SIZE = K.ST, K.SIZE
HOVER = ST["hover"]["height"] * SIZE


# Alle Clips außer Death: Tentakel über die ganze Länge (wobble) + Nachschwingen aus der Kern-Bewegung (drive).
# Jeder Clip beschreibt seinen Kern als state(f) → core(...); drive() leitet daraus das Nachschwingen ab.

def fly(P, turn=0):
    N = P["cycle_frames"]

    def state(f):
        t = (f % N) / N
        ph = 2 * math.pi * t
        return dict(dz=HOVER + P["bob"] * SIZE * math.sin(ph),
                    dx=P.get("surge", 0) * SIZE * math.sin(ph - P.get("surge_lag", 0.6)),   # Schub nach dem Hub
                    pitch=R(P["pitch_deg"]) + R(P.get("pitch_osc_deg", 0)) * math.sin(ph + 0.8),
                    roll=turn * R(P.get("roll_deg", 0)), yaw=turn * R(P.get("yaw_osc_deg", 4)) * math.sin(ph))
    drv = drive(state, N, True)

    def pose(f):
        t = (f % N) / N
        core(**state(f))
        wobble(t, P["amp_deg"], P["speed"], trail_deg=P["trail_deg"], turn_deg=turn * P.get("turn_trail_deg", 0),
               drv=drv, f=f % N)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose}


def clip_idle(P):
    N = P["frames"]

    def state(f):
        return dict(dz=HOVER + P["bob"] * SIZE * math.sin(2 * math.pi * 2 * f / N))
    drv = drive(state, N, True)

    def pose(f):
        t = f / N
        pulse = math.sin(2 * math.pi * 2 * t - P.get("pulse_lag", 0.9))   # Zusammenziehen folgt dem Hub
        core(**state(f))
        wobble(t, P["amp_deg"], P.get("speed", 1), curl_deg=P["pulse_deg"] * pulse, drv=drv, f=f)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def state(f):
        t = f / N
        return dict(dz=HOVER + P["lift"] * SIZE + P.get("bob", 0) * SIZE * math.sin(2 * math.pi * t),
                    roll=R(P["tremble_deg"]) * math.sin(2 * math.pi * 5 * t))
    drv = drive(state, N, True)

    def pose(f):
        t = f / N
        core(**state(f))
        wobble(t, P["amp_deg"], P.get("speed", 1), spread_deg=P["spread_deg"], drv=drv, f=f)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_attack1(P):
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]

    def phases(f):
        if f <= w:
            return ease(f / w), 0.0
        if f <= s:
            x = ease((f - w) / (s - w))
            return 1 - x, x
        if f <= h:
            return 0.0, 1.0
        return 0.0, 1 - ease((f - h) / (N - h))

    def state(f):
        k_w, k_s = phases(f)
        return dict(dz=HOVER, dx=-P["pull_back"] * SIZE * k_w + P["lunge"] * SIZE * k_s,
                    pitch=-R(10) * k_w + R(18) * k_s)
    drv = drive(state, N, False)

    def pose(f):
        k_w, k_s = phases(f)
        core(**state(f))
        # ausholen = Tentakel nach hinten, Schlag = nach vorn schnellen; Wellen + Peitschen-Nachschwingen darüber
        env = 1 - ease((f - (N - P.get("settle_frames", 5))) / P.get("settle_frames", 5))
        wobble(f / N, P.get("amp_deg", 8), 1, trail_deg=P["windup_deg"] * k_w - P["strike_deg"] * k_s,
               drv=drv, f=f, env=env)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def kick(f):
        x = f / N
        return 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)

    def state(f):
        k = kick(f)
        return dict(dz=HOVER, dx=-P["recoil"] * SIZE * k, pitch=-R(15) * k)
    drv = drive(state, N, False)

    def pose(f):
        x = f / N
        core(**state(f))
        env = math.sin(math.pi * x)                        # 0 am Anfang und Ende → kehrt exakt zur Ruhe zurück
        wobble(x, P["flail_deg"], 2, drv=drv, f=f, env=env)
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
