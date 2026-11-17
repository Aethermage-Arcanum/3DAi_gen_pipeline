"""Bewegungsmuster legless/cobra: Schlängeln (laterale Undulation), Drehen, Idle, Kobra-Aufrichten,
Zustoßen, Treffer, Tod. Gemeinsame Bausteine: ../legless_kit.py

& "D:\\Blender\\blender.exe" -b <legless_rigged.blend> -P motions/legless/cobra/cobra_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import legless_kit as K  # noqa: E402

K.init(HERE)
from legless_kit import LEFT, UP, R, bend, ease, ground, head, jaw, keep_centered, wave  # noqa: E402

ST = K.ST


def slither(P, bias=0.0):
    N = P["cycle_frames"]

    def pose(f):
        t = (f % N) / N
        wave(t, P["amp_deg"], P["waves"])
        if bias:
            bend(0.15, 0.95, bias)
        bend(0.85, 1.0, P.get("front_raise_deg", 0), LEFT)
        keep_centered(keep_heading=not bias)
        head(level=P.get("head_level", 0))
        ground("contact")
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        wave(t, P["amp_deg"], 1.0)
        bend(0.8, 1.0, P["front_raise_deg"] + 4 * math.sin(2 * math.pi * 2 * t), LEFT)
        keep_centered()
        head(yaw=R(P["look_deg"]) * math.sin(2 * math.pi * t), level=0.7)
        jaw(2 * max(0, math.sin(2 * math.pi * 3 * t)))
        ground("contact")
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "grounded": True}


def rear(P, k, s_curve=1.0, sway=0.0):
    """Vorderkörper aufrichten (k 0..1) mit S-Kurve im Hals."""
    bend(P["raise_lo"] if "raise_lo" in P else 0.6, 0.85, P["raise_deg"] * k, LEFT)
    bend(0.85, 1.0, -P.get("s_curve_deg", 25) * k * s_curve, LEFT)
    if sway:
        bend(0.6, 1.0, sway, UP)


def clip_ready(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        rear(P, 1.0, sway=P["sway_deg"] * math.sin(2 * math.pi * t))
        keep_centered()
        head(level=1.0)
        jaw(P["jaw_deg"])
        ground("above")
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_attack1(P):
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    P = dict(P, raise_lo=ST["ready"]["raise_lo"], s_curve_deg=25)

    def pose(f):
        if f <= w:
            k_r, k_s, k_j, pull = ease(f / w), 0.0, 0.3 * ease(f / w), ease(f / w)
        elif f <= s:
            x = ease((f - w) / (s - w))
            k_r, k_s, k_j, pull = 1.0, x, 1.0 if x < 0.8 else 0.0, 1 - x
        elif f <= h:
            k_r, k_s, k_j, pull = 1.0, 1.0, 0.0, 0.0
        else:
            x = ease((f - h) / (N - h))
            k_r, k_s, k_j, pull = 1 - x, 1 - x, 0.0, 0.0
        rear(P, k_r * (1 - P["strike_drop"] * k_s), s_curve=1.0 + 0.6 * pull - 1.0 * k_s)
        bend(0.6, 1.0, -P["strike_down_deg"] * k_s, LEFT)         # nach vorn-unten zustoßen
        keep_centered(dx=P["strike_lunge"] * K.SIZE * k_s - 0.03 * K.SIZE * pull)
        head(level=0.6 * (1 - k_s))
        jaw(P["jaw_open_deg"] * k_j)
        ground("above")
    return {"N": N, "loop": False, "kind": "stand", "pose": pose,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    N = P["frames"]

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)
        bend(0.75, 1.0, P["recoil_deg"] * k, LEFT)
        bend(0.5, 1.0, P["jolt_deg"] * k, UP)
        keep_centered(dx=-0.03 * K.SIZE * k)
        head(level=0.5)
        jaw(10 * k)
        ground("contact")
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "grounded": True}


def clip_death(P):
    N, c1 = P["frames"], P["collapse_end"]

    def pose(f):
        k = ease(f / c1)
        wave(0.25, 25 * (1 - k), 1.0)                               # letzte Zuckung, dann schlaff
        bend(0.0, 1.0, P["twist_deg"] * k, UP)
        bend(0.8, 1.0, -15 * k, LEFT)                               # Kopf sinkt auf den Boden
        keep_centered(keep_heading=False)
        jaw(14 * k)
        ground("contact")
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "grounded": True,
            "events": [{"frame": N, "event": "dead"}]}


K.bake({
    "Walk": slither(ST["walk"]),
    "Run": slither(ST["run"]),
    "TurnLeft": slither(ST["turn"], bias=ST["turn"]["bias_deg"]),
    "TurnRight": slither(ST["turn"], bias=-ST["turn"]["bias_deg"]),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
})
