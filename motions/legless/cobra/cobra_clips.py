"""Bewegungsmuster legless/cobra: Schlängeln (laterale Undulation), Drehen, Idle, Kobra-Aufrichten,
Zustoßen, Treffer, Tod. Gemeinsame Bausteine: ../legless_kit.py

& "D:\\Blender\\blender.exe" -b <legless_rigged.blend> -P motions/legless/cobra/cobra_clips.py -- <ausgabe> [<creature.toml>]

Seit 2026-11-17 (Nutzer-Feedback Unity): alle Clips außer Death geben die Körperform ABSOLUT vor (K.shape: Richtung
jedes Wirbels gegenüber einer geraden Grundlinie). Die feste S-Kurve/Aufrichtung der Tripo-Ruhepose fließt nicht mehr ein.
Death ist unverändert (Nutzer-Anweisung: Death-Clips nicht anfassen) und arbeitet weiter relativ zur Ruhepose.
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import legless_kit as K  # noqa: E402

K.init(HERE)
from legless_kit import LEFT, UP, R, bend, ease, ground, head, jaw, keep_centered, wave  # noqa: E402,F401

ST = K.ST
TAU = 2 * math.pi
S = K.seg_s()                                   # Bogenlänge je Wirbel (0 Schwanz … 1 Kopfansatz)
LENS = K.abs_info()["len"][:K.NSEG]


def mean_yaw(yaw):
    return sum(y * l for y, l in zip(yaw, LENS)) / sum(LENS)


def pitch_profile(pts, scale=1.0):
    return [K.interp(pts, s) * scale for s in S]


# ---------------------------------------------------------------- Fortbewegung (laterale Undulation)
def undulation(P, t, amp_scale=1.0):
    """Serpenoid-Kurve: Gierwinkel sinusförmig entlang des Körpers, Welle läuft vom Kopf zum Schwanz.
    Hüllkurve: Schwanzspitze etwas mehr (Aal), Hals weniger (Kopf stabilisiert)."""
    env = [K.interp(P["envelope"], s) for s in S]
    yaw = [P["amp_deg"] * amp_scale * e * math.sin(TAU * (P["waves"] * s + t)) for s, e in zip(S, env)]
    head_yaw = P["amp_deg"] * amp_scale * P["head_follow"] * math.sin(TAU * (P["waves"] * 1.0 + t) - R(P["head_lag_deg"]))
    return yaw, head_yaw


def slither(P, turn=0.0):
    """turn: +1 links, -1 rechts, 0 geradeaus. Kurve = gleichmäßige Krümmung (Körper liegt auf der Kreisbahn)
    + Kopf/Hals führen zusätzlich in die Kurve."""
    N = P["cycle_frames"]

    def pose(f):
        t = (f % N) / N
        yaw, head_yaw = undulation(P, t, P.get("turn_amp_scale", 1.0) if turn else 1.0)
        if turn:
            for i, s in enumerate(S):
                yaw[i] += turn * (P["arc_deg"] * (s - 0.5) + P["lead_deg"] * K.interp([(0.7, 0), (1.0, 1)], s))
            head_yaw += turn * (P["arc_deg"] * 0.5 + P["lead_deg"] + P["head_lead_deg"])
        m = mean_yaw(yaw)                                        # mittlere Körperrichtung = Blickrichtung des Objekts
        yaw = [y - m for y in yaw]
        bob = P.get("head_bob_deg", 0) * math.sin(TAU * 2 * t)
        K.shape(yaw, pitch_profile(P["pitch"]), head_yaw - m, bob)
        K.place(K.REST_MID)
        ground("contact")
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose}


# ---------------------------------------------------------------- Stand-Haltungen (Idle / Ready / Attack / Hit)
NUM_KEYS = ("coil_amp_deg", "coil_waves", "front_yaw_deg", "head_yaw_deg", "head_pitch_deg", "ripple_deg", "jaw_deg")


def stance(Q, t=0.0):
    """Hinterkörper liegt als S-Schlinge am Boden (endet bei coil_end mit Richtung 0 = nach vorn),
    davor erhebt sich der Vorderkörper nach Q['pitch']. Gibt (yaw, pitch, head_yaw, head_pitch)."""
    ce = Q["coil_end"]
    yaw = []
    for s in S:
        if s < ce:
            u = (ce - s) / ce
            y = Q["coil_amp_deg"] * math.sin(TAU * Q["coil_waves"] * u) * K.interp([(0, 0.6), (0.15, 1.0)], u)
        else:
            y = Q["front_yaw_deg"] * K.interp([(ce, 0.0), (min(1.0, ce + 0.15), 1.0)], s)
        y += Q.get("ripple_deg", 0) * math.sin(TAU * (1.2 * s + t)) * K.interp([(0, 1), (ce, 1), (min(1, ce + .1), 0)], s)
        yaw.append(y)
    pitch = [K.interp(Q["pitch"], s) for s in S]
    return yaw, pitch, Q["head_yaw_deg"], Q["head_pitch_deg"]


def mixq(a, b, k):
    out = dict(a)
    for key in NUM_KEYS:
        out[key] = K.mix(a.get(key, 0.0), b.get(key, 0.0), k)
    out["coil_end"] = K.mix(a["coil_end"], b["coil_end"], k)
    out["pitch"] = [(sa, K.mix(va, vb, k)) for (sa, va), (_, vb) in zip(a["pitch"], b["pitch"])]
    return out


def stance_q(name):
    q = dict(ST[name])
    q.setdefault("ripple_deg", 0.0)
    q.setdefault("front_yaw_deg", 0.0)
    q.setdefault("head_yaw_deg", 0.0)
    q.setdefault("head_pitch_deg", 0.0)
    q.setdefault("jaw_deg", 0.0)
    return q


IDLE_Q, READY_Q = stance_q("idle"), stance_q("ready")
REAR = ST["ready"]["anchor_hi"]                # Schwerpunkt dieses hinteren Bereichs bleibt bei Stand-Clips liegen
# Ankerpunkt: wo der Hinterkörper liegt, wenn die Idle-Haltung mittig steht (Übergänge Walk ↔ Idle ↔ Ready ohne Sprung)
K.reset()
_y, _p, _hy, _hp = stance(IDLE_Q)
K.shape(_y, _p, _hy, _hp)
K.place(K.REST_MID)
ANCHOR = K.centroid(0.0, REAR)
K.reset()


def pose_stance(Q, t=0.0, dx=0.0):
    yaw, pitch, hy, hp = stance(Q, t)
    K.shape(yaw, pitch, hy, hp)
    K.place(ANCHOR + K.Vector((dx * K.SIZE, 0, 0)), 0.0, REAR)
    jaw(Q.get("jaw_deg", 0.0))
    ground("contact")


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        br = math.sin(TAU * P["breaths"] * t)                       # Atmen: Schlinge + Vorderkörper heben/senken
        look = math.sin(TAU * t) * P["look_deg"] + math.sin(TAU * 3 * t + 1.0) * P["look_deg"] * 0.25
        taste = sum(math.exp(-((t - c) / 0.035) ** 2) for c in P["taste_at"])    # kurzes Tasten/Züngeln
        q = dict(IDLE_Q)
        q["coil_amp_deg"] = IDLE_Q["coil_amp_deg"] * (1 + P["breath_coil"] * br)
        q["pitch"] = [(s, v * (1 + P["breath_raise"] * br)) for s, v in IDLE_Q["pitch"]]
        q["head_yaw_deg"] = look
        q["front_yaw_deg"] = look * P["neck_follow"]
        q["head_pitch_deg"] = IDLE_Q["head_pitch_deg"] - P["taste_dip_deg"] * taste + 2 * br
        q["jaw_deg"] = P["taste_jaw_deg"] * taste * max(0.0, math.sin(TAU * 40 * t))
        pose_stance(q, t)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "grounded": True}


def ready_q(t, P):
    q = dict(READY_Q)
    sway = math.sin(TAU * t)
    br = math.sin(TAU * 2 * t)
    q["front_yaw_deg"] = P["sway_deg"] * sway
    q["head_yaw_deg"] = 0.0                                          # Kopf bleibt aufs Ziel gerichtet
    q["coil_amp_deg"] = READY_Q["coil_amp_deg"] * (1 + P["tension"] * br)
    q["pitch"] = [(s, v + P["bob_deg"] * br * (1 if 0.6 < s < 0.95 else 0)) for s, v in READY_Q["pitch"]]
    return q


def clip_ready(P):
    N = P["frames"]
    return {"N": N, "loop": True, "kind": "stand", "pose": lambda f: pose_stance(ready_q(f / N, P), f / N),
            "grounded": True}


def clip_attack1(P):
    """Ready → Ausholen (Schlinge spannt sich, Vorderkörper lehnt zurück) → Stoß (S-Kurve entlädt sich, Körper
    streckt sich, Kopf schießt nach vorn-unten) → Biss halten → zurück in die Ready-Spannung."""
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    base = ready_q(0.0, ST["ready"])
    W = mixq(base, dict(base, **{k: v for k, v in P["windup"].items()}), 1.0)
    X = mixq(base, dict(base, **{k: v for k, v in P["strike"].items()}), 1.0)
    meas = {}

    def pose(f):
        if f <= w:
            k = ease(f / w)
            q, dx = mixq(base, W, k), -P["windup_slide"] * k
        elif f <= s:
            x = ((f - w) / (s - w)) ** 1.5                           # beschleunigt bis zum Kontakt
            q, dx = mixq(W, X, x), K.mix(-P["windup_slide"], P["lunge_slide"], x)
        elif f <= h:
            q, dx = dict(X), P["lunge_slide"]
            q["jaw_deg"] = X["jaw_deg"] * max(0.0, 1 - (f - s) / 2)   # zubeißen
        else:
            u = (f - h) / (N - h)
            y = 1 - (1 - u) ** 2.5                                   # schnell zurückziehen, dann einpendeln
            q, dx = mixq(dict(X, jaw_deg=0.0), base, y), P["lunge_slide"] * (1 - y)
        pose_stance(q, 0.0, dx)
        tip = K.head_tip()
        if f == 0:
            meas["start"] = tip.copy()
        if f == P["hit_frame"]:
            meas["hit"] = tip.copy()

    def measure():
        d = meas["hit"] - meas["start"]
        return {"strike_reach_m": round(d.x, 3), "strike_reach_body_frac": round(d.x / K.SIZE, 2),
                "strike_head_drop_m": round(-d.z, 3)}
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "grounded": True, "returns_to_start": True,
            "measure": measure, "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    """Ganzkörper-Reaktion aus der Ready-Haltung: Vorderkörper/Kopf fliegen zurück, ein Knick läuft vom Hals
    bis in den Schwanz, Körper rutscht etwas zurück, dann zurück in die Spannung."""
    N = P["frames"]
    base = ready_q(0.0, ST["ready"])

    def pose(f):
        x = f / N
        e = math.sin(0.5 * math.pi * min(1.0, x / P["peak"])) * (1 - ease((x - P["peak"]) / (1 - P["peak"]))
                                                                  if x > P["peak"] else 1.0)
        c = 1.0 - x / P["ripple_end"]                                # Knick wandert Hals → Schwanz
        q = dict(base)
        q["pitch"] = [(sp, v + P["recoil_deg"] * e * K.interp([(0.55, 0), (0.75, 1), (1.0, 0.6)], sp))
                      for sp, v in base["pitch"]]
        q["head_pitch_deg"] = base["head_pitch_deg"] + P["head_snap_deg"] * e
        q["head_yaw_deg"] = P["head_jolt_deg"] * e
        q["front_yaw_deg"] = P["jolt_deg"] * e
        q["jaw_deg"] = P["jaw_deg"] * e
        yaw, pitch, hy, hp = stance(q)
        for i, sp in enumerate(S):
            yaw[i] += P["kink_deg"] * e * math.exp(-((sp - c) / 0.12) ** 2) * (1 if x < P["ripple_end"] else 0)
        K.shape(yaw, pitch, hy, hp)
        K.place(ANCHOR + K.Vector((-P["slide"] * K.SIZE * e, 0, 0)), 0.0, REAR)
        jaw(q["jaw_deg"])
        ground("contact")
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "grounded": True, "returns_to_start": True}


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
    "TurnLeft": slither(ST["turn"], turn=1.0),
    "TurnRight": slither(ST["turn"], turn=-1.0),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
})
