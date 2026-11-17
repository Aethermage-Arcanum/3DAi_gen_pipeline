"""Bewegungsmuster flyer/wasp: Flug, Drehen (Kurvenlage), Schwebeflug, Drohen (Stachel nach vorn), Sturzflug-Stich,
Treffer, Absturz. Rig = Schwebe-Rig (Kern + automatisch erkannte Ketten), Baukasten = ../flyer_kit.py.

Ketten werden nach Lage zugeordnet: Flügel (seitlich, |y| groß), Beine (unten), Fühler (vorn-oben),
Hinterleib (hinten, längste Kette).

& "D:\\Blender\\blender.exe" -b <floater_rigged.blend> -P motions/flyer/wasp/wasp_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Quaternion, Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import flyer_kit as K  # noqa: E402

K.init(HERE)
from flyer_kit import FWD, LEFT, UP, R, ease, rot  # noqa: E402

ST, SIZE, DB = K.ST, K.SIZE, K.DB
C0 = DB["Core"].head_local
HOV = ST["hover"]
CLEAR = HOV.get("min_clearance", 0.0) * SIZE          # Flug: Mindestabstand jedes Mesh-Punkts zum Boden


def tip(ch):
    return DB[K.TENT[ch][-1]].tail_local - C0


chains = list(K.TENT)
ABDOMEN = min(chains, key=lambda c: tip(c).x)                                   # am weitesten hinten
rest = [c for c in chains if c != ABDOMEN]
LEGS_ = [c for c in rest if tip(c).z < -0.15 * SIZE]
ANT = [c for c in rest if c not in LEGS_ and tip(c).x > 0.1 * SIZE]
WINGS = [c for c in rest if c not in LEGS_ and c not in ANT]
print(f"WASP Flügel {len(WINGS)}, Beine {len(LEGS_)}, Fühler {len(ANT)}, Hinterleib {ABDOMEN}")


def flap(f, amp=1.0):
    ph = 2 * math.pi * f / HOV["flap_frames"]
    for c in WINGS:
        sg = 1 if tip(c).y > 0 else -1
        rot(K.TENT[c][0], FWD, sg * R(HOV["flap_deg"]) * amp * math.sin(ph))


def abdomen(curl_deg=0.0, pump=0.0):
    bones = K.TENT[ABDOMEN]
    for b in bones:
        rot(b, LEFT, -R(curl_deg + pump) / len(bones))          # − = nach unten/vorn einkrümmen


def legs(trail_deg=0.0, t=0.0, dangle=4.0):
    for i, c in enumerate(LEGS_):
        for k, b in enumerate(K.TENT[c]):
            rot(b, LEFT, -R(trail_deg) / len(K.TENT[c]) + R(dangle) * math.sin(2 * math.pi * t + i) / len(K.TENT[c]))


def antennae(t):
    for i, c in enumerate(ANT):
        rot(K.TENT[c][0], UP, R(6) * math.sin(2 * math.pi * 2 * t + i * 2))


def hover(dz=0.0, dx=0.0, pitch=0.0, roll=0.0):
    K.core(dz=HOV["height"] * SIZE + dz, dx=dx, pitch=pitch, roll=roll)


def fly(P, turn=0):
    N = P["cycle_frames"]

    def pose(f):
        t = f / N
        hover(dz=P["bob"] * SIZE * math.sin(2 * math.pi * t), pitch=R(P["pitch_deg"]), roll=turn * R(P.get("roll_deg", 0)))
        flap(f)
        abdomen(pump=P["pump_deg"] * math.sin(2 * math.pi * 2 * t))
        legs(P["legs_trail_deg"], t)
        antennae(t)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        hover(dz=P["bob"] * SIZE * math.sin(2 * math.pi * t), roll=R(3) * math.sin(2 * math.pi * 2 * t))
        flap(f)
        abdomen(pump=P["pump_deg"] * math.sin(2 * math.pi * 3 * t))
        legs(0, t)
        antennae(t)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        hover(dz=P["lift"] * SIZE, pitch=-R(6))
        flap(f)
        abdomen(curl_deg=P["curl_deg"] + 4 * math.sin(2 * math.pi * 2 * t))
        legs(-10, t)
        antennae(t)
        K.ground_above(CLEAR)                                # eingekrümmter Stachel nie am/im Boden
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
        hover(dz=P["rise"] * SIZE * k_w - P["dive"] * SIZE * k_s, dx=P["lunge"] * SIZE * k_s,
              pitch=-R(15) * k_w + R(25) * k_s)
        flap(f, 1.0 + 0.3 * k_s)
        abdomen(curl_deg=P["curl_deg"] * (0.4 * k_w + k_s))
        legs(-15 * k_s, 0)
        K.ground_above(CLEAR)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        hover(dx=-P["knock"] * SIZE * k, pitch=-R(P["tumble_deg"]) * k, roll=R(P["tumble_deg"]) * 0.5 * k)
        flap(f, 1 - 0.7 * k)
        abdomen(curl_deg=20 * k)
        legs(20 * k, 0)
        K.ground_above(CLEAR)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    N, c1 = P["frames"], P["fall_end"]
    piv = C0.copy()
    h0 = DB["Root"].head_local

    def pose(f):
        k = ease(f / c1)
        q = Quaternion(FWD, math.pi * k)                         # fällt und dreht sich auf den Rücken
        K.core(dz=HOV["height"] * SIZE * (1 - k))
        rot("Root", FWD, math.pi * k)
        K.move("Root", (piv - h0) - q @ (piv - h0))
        flap(f, max(0.0, 1 - 2 * k))
        abdomen(curl_deg=30 * k)
        legs(-30 * k, 0, dangle=0)
        if k > 0.0:
            bpy.context.view_layer.update()
            z = K.mesh_min_z()
            if f >= c1 or z < K.GROUND:                           # landet genau auf dem Boden, nie darunter
                K.move("Root", Vector((0, 0, K.GROUND - z)))
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
