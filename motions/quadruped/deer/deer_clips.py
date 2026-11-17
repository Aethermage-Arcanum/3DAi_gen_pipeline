"""Bewegungsmuster quadruped/deer (Hirsch): Schritt (lateraler Viertakt, Kopf nickt 2× pro Schritt um ¼ versetzt zum
Widerrist), Transvers-Galopp mit Schaukeln + Hals-Pumpen, Drehen, Idle (äsen/sichern), Drohen (Kopf hoch → Geweih
senken, Vorderhuf stampft), Geweihstoß mit Hochreißen, Treffer, Tod. Gemeinsame Bausteine: ../quadruped_kit.py
(Entstanden als Kopie von wolf_clips.py, 2026-11-17 – ab jetzt eigenständig, Änderungen hier betreffen nur deer.)

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/deer/deer_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

# Eigener Code dieses Musters – andere Muster importieren/benutzen diese Datei NICHT (Kapselung, siehe motions/README.md).
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
from quadruped_kit import (FWD, LEFT, UP, LEGS, R, body, ease, gait, ik_off, jaw, neck_head,  # noqa: E402
                           phase, rot, set_foot, spine, tail)
from quadruped_kit import NECK, SPINE, TAIL, bend, bump, follow, keys  # noqa: E402
from mathutils import Vector  # noqa: E402

ST, SIZE, HGT = K.ST, K.SIZE, K.HGT
TAU = 2 * math.pi
GIRDLE = (K.REST["FL"]["ball"].x - K.REST["BL"]["ball"].x) or 0.4 * SIZE


def trunk(pel=(0.0, 0.0, 0.0), sh=(0.0, 0.0, 0.0)):
    """Becken- und Schultergürtel getrennt drehen: (pitch + = vorne hoch, yaw + = nach links, roll + = linke Seite hoch),
    rad relativ zu Root. Der Rücken dazwischen verteilt die Differenz."""
    for axis, a, b, sgn in ((LEFT, pel[0], sh[0], -1), (UP, pel[1], sh[1], 1), (FWD, pel[2], sh[2], 1)):
        bend(SPINE, axis, (sgn * a, sgn * (b - a) / 2, sgn * (b - a) / 2))


def cyc(t, at, cycles=1):
    """cos-Welle mit Maximum bei Zyklus-Anteil `at`."""
    return math.cos(TAU * cycles * (t - at))


# ---------------------------------------------------------------- Fortbewegung
def locomotion(P, turn=0.0):
    N = P["cycle_frames"]
    off = P["order"]
    d = P["duty"]
    td = {l: (-off[l]) % 1.0 for l in LEGS}
    mid_swing = {l: (td[l] + d + (1 - d) / 2) % 1.0 for l in LEGS}
    mid_stance = {l: (td[l] + d / 2) % 1.0 for l in LEGS}
    gallop = P.get("body") == "gallop"
    lag, tlag = P.get("neck_lag", 0.05), P.get("tail_lag", 0.07)
    sgn = (turn > 0) - (turn < 0)

    def girdles(t):
        if gallop:
            # Transvers-Galopp (Huftiere): steifer Rücken, dafür starkes Schaukeln (Brust hoch beim Abdruck hinten,
            # tief beim Aufsetzen vorn); Rumpf am tiefsten mitten im Stand, höchster Punkt in der (gesammelten) Schwebe.
            flex = R(P["spine_flex_deg"]) * cyc(t, P["flex_peak"])
            pitch = R(P["pitch_deg"]) * cyc(t, P["pitch_peak"])
            dz = -P["bob"] * HGT * cyc(t, P["bob_low"], 2)
            return (dz, 0.0, pitch, 0.0), (flex / 2, 0.0, 0.0), (-flex * P.get("chest_flex", 0.1), 0.0, 0.0)
        hb, fb = mid_swing["BL"], mid_swing["FL"]
        yh, yf = R(P.get("hip_yaw_deg", 0)), R(P.get("shoulder_yaw_deg", 0))
        rh, rf = R(P.get("hip_roll_deg", 0)), R(P.get("shoulder_roll_deg", 0))
        B = P.get("bob", 0) * HGT
        zh, zf = B * cyc(t, mid_stance["BL"], 2), B * cyc(t, mid_stance["FL"], 2)
        dy = -P.get("sway", 0) * SIZE * (cyc(t, hb) + cyc(t, fb)) / 2
        return ((zh + zf) / 2, dy, math.atan2(zf - zh, GIRDLE), 0.0), \
            (0.0, -yh * cyc(t, hb), -rh * cyc(t, hb)), (0.0, -yf * cyc(t, fb), -rf * cyc(t, fb))

    def chest_pitch(t):
        rt, _, sh = girdles(t)
        return -(rt[2] + sh[0])

    def chest_yaw(t):
        return girdles(t)[2][1] + (sgn * R(P.get("turn_bend_deg", 0)) / 2 if turn else 0.0)

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=-turn)                         # −: gait dreht bei turn > 0 nach rechts (siehe wolf_clips.py)
        rt, pel, sh = girdles(t)
        body(dz=rt[0], dy=rt[1], pitch=rt[2], roll=rt[3])
        if turn:
            b = sgn * R(P.get("turn_bend_deg", 0)) / 2
            pel, sh = (pel[0], pel[1] - b, pel[2]), (sh[0], sh[1] + b, sh[2])
        trunk(pel, sh)
        # Hals: Huftiere nicken 2× pro Schritt, um ~25 % des Zyklus gegen den Widerrist versetzt (Loscher et al. 2016):
        # Kopf am höchsten, wenn der Widerrist am tiefsten ist. Galopp: Hals pumpt 1× pro Sprung (tief beim Aufsetzen vorn).
        g = P.get("head_gain", 0.6)
        np_ = follow(chest_pitch, t, 3, lag, g)
        if gallop:
            nod = R(P.get("head_bob_deg", 0)) * cyc(t, P.get("nod_peak", 0.3))
        else:
            nod = R(P.get("head_bob_deg", 0)) * cyc(t, mid_stance["FL"] + P.get("nod_shift", 0.25), 2)
        nl = R(P.get("neck_lift_deg", 0))
        bend(NECK, LEFT, [np_[0] - nl / 2 - nod * 0.4, np_[1] - nl / 2 - nod * 0.4, np_[2] + nl - nod * 0.2])
        ny = follow(chest_yaw, t, 3, lag, P.get("head_yaw_gain", g))
        if turn:
            hd = sgn * R(P.get("turn_head_deg", 0))
            ny = [ny[0] + hd * 0.3, ny[1] + hd * 0.3, ny[2] + hd * 0.4]
        bend(NECK, UP, ny)
        # kurzer Wedel: zuckt im Takt
        bend(TAIL, LEFT, [R(P.get("tail_lift_deg", 0)) / 4 + R(P.get("tail_deg", 0)) * 0.25 *
                          math.sin(TAU * 2 * t - i * 0.8) for i in range(4)])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn,
            "max_stretch": P.get("max_stretch"), "reach_smooth": P.get("reach_smooth"), "reach_flat": P.get("reach_flat", 0),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], d)[0]}


# ---------------------------------------------------------------- Stand-Clips
def look_chain(yaw_fn, pitch_fn, x, lag):
    """Kopf führt, Hals folgt."""
    for axis, fn, sg in ((UP, yaw_fn, 1), (LEFT, pitch_fn, -1)):
        w = [0.3 * fn(x - 2 * lag), 0.6 * fn(x - lag), fn(x)]
        bend(NECK, axis, [sg * w[0], sg * (w[1] - w[0]), sg * (w[2] - w[1])])


def clip_idle(P):
    """Sichern: atmen, Gewicht verlagern, Kopf hebt sich, schaut weich nach links/rechts (Kopf führt), Wedel zuckt."""
    N = P["frames"]

    def pose(f):
        t = f / N
        br = math.sin(TAU * 3 * t)
        shift = math.sin(TAU * t)
        body(dz=0.005 * HGT * br, dy=0.006 * SIZE * shift, roll=R(1.0) * shift)
        trunk((0, 0, -R(0.8) * shift), (R(P["breathe_deg"]) * br, 0, R(0.6) * shift))
        look = [(0, 0), (0.12, 0), (0.3, 1), (0.45, 1), (0.62, -0.7), (0.8, -0.7), (1, 0)]
        lift = [(0, 0), (0.2, 0.6), (0.45, 0.6), (0.6, -0.3), (0.85, -0.3), (1, 0)]
        look_chain(lambda x: R(P["look_deg"]) * keys(x, look, loop=True), lambda x: R(8) * keys(x, lift, loop=True),
                   t, 0.03)
        flick = max(0.0, math.sin(TAU * 4 * t)) ** 6
        bend(TAIL, LEFT, [R(P["tail_deg"]) * flick * (0.3 + 0.2 * i) for i in range(4)])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_ready(P):
    """Drohen: Geweih gesenkt und zum Gegner gedreht, Kopf pendelt seitlich (Geweih zeigen), Vorderhuf stampft
    (Warnsignal beim Rotwild), Rumpf lädt auf die Hinterhand. Schleife."""
    N = P["frames"]
    stomp = P.get("stomp_leg", "FL")

    def pose(f):
        t = f / N
        rock = math.sin(TAU * t)
        body(dz=-P["crouch"] * HGT, dx=-0.01 * SIZE + 0.008 * SIZE * rock, pitch=-R(P.get("pitch_deg", 3)))
        trunk((R(1.5) * rock, 0, 0), (-R(1.5) * rock, 0, 0))
        hd = R(P["head_down_deg"])
        sweep = R(P.get("sweep_deg", 10)) * math.sin(TAU * t + 0.5)
        bend(NECK, LEFT, [hd * 0.45, hd * 0.45, -hd * 0.1])
        bend(NECK, UP, [sweep * 0.2, sweep * 0.3, sweep * 0.5])
        # Stampfen: Huf hoch (weich) → schnell runter (2× pro Schleife), Zehen dabei angezogen
        s = (2 * t) % 1.0
        up = bump(s / 0.45, 0.6) if s < 0.45 else 0.0
        K.set_foot(stomp, Vector((0.01 * SIZE * up, 0, P.get("stomp_lift", 0.12) * HGT * up)), R(25) * up)
        bend(TAIL, LEFT, [R(P["tail_lift_deg"]) / 4] * 4)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": [l for l in LEGS if l != stomp]}


def clip_attack1(P):
    """Geweihstoß: Kopf tief, Geweih nach vorn, Gewicht nach hinten laden → Hinterhand schiebt den Körper nach vorn,
    Geweih stößt vor (hit) und reißt nach oben/seitlich (Haken) → zurückfedern. Füße bleiben stehen."""
    N, w, s = P["frames"], P["windup_end"], P["strike_end"]
    h = P["hit_frame"]
    L, c = P["lunge"] * SIZE, P["crouch"] * HGT
    nk = R(P["neck_reach_deg"])
    rec = N - 5
    dx = [(0, 0), (w, -0.05 * SIZE), (s, L), (s + 3, L * 0.9), (s + 8, L * 0.2), (rec, 0)]
    dz = [(0, 0), (w, -c), (s, -c * 0.3), (s + 3, c * 0.3), (s + 8, -c * 0.1), (rec, 0)]
    pitch = [(0, 0), (w, R(3)), (s, -R(6)), (s + 3, R(5)), (s + 8, -R(1)), (rec, 0)]
    neck = [(0, 0), (w, -nk * 0.8), (s, -nk), (s + 3, -nk * 0.2), (s + 8, -nk * 0.3), (rec, 0)]    # + = hoch
    head = [(0, 0), (w, -nk * 0.25), (s, -nk * 0.4), (s + 3, nk * 0.25), (s + 8, -nk * 0.05), (rec, 0)]
    hook = [(0, 0), (s, 0), (s + 3, R(P.get("hook_deg", 14))), (s + 7, -R(4)), (rec, 0)]

    def pose(f):
        body(dx=keys(f, dx), dz=keys(f, dz), pitch=keys(f, pitch))
        p = keys(f, pitch)
        trunk((p * 0.3, 0, 0), (-p * 0.3, 0, 0))
        n = [keys(f - 1, neck), keys(f, neck)]
        bend(NECK, LEFT, [-n[0] / 2, -n[1] / 2, -keys(f, head)])
        hk = [keys(f - 1, hook), keys(f, hook)]
        bend(NECK, UP, [hk[0] * 0.3, hk[1] * 0.3, hk[1] * 0.2])
        bend(NECK, FWD, [0, 0, hk[1] * 0.8])                        # Geweih dreht beim Haken (Roll)
        bend(TAIL, LEFT, [keys(f - 1 - i, pitch) * 1.5 for i in range(4)])
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "events": [{"frame": h, "event": "hit"}]}


def clip_hit(P):
    """Treffer: Stoß zurück, Rumpf rollt weg, Hals/Geweih schlagen verzögert zur Seite, gedämpftes Nachfedern."""
    N = P["frames"]
    j, ro, hd = P["jolt"] * SIZE, R(P["roll_deg"]), R(P["head_deg"])
    e = N - 4
    dx = [(0, 0), (2, -j), (5, -j * 0.55), (7, j * 0.12), (9, -j * 0.04), (e, 0)]
    dz = [(0, 0), (3, -0.05 * HGT), (7, 0.01 * HGT), (e, 0)]
    roll = [(0, 0), (2, ro), (5, -ro * 0.35), (7, ro * 0.12), (e, 0)]
    head = [(0, 0), (3, hd), (5, -hd * 0.35), (8, hd * 0.12), (e, 0)]
    hp = [(0, 0), (3, R(12)), (6, -R(4)), (e, 0)]

    def pose(f):
        body(dx=keys(f, dx), dz=keys(f, dz), roll=keys(f, roll))
        trunk((0, 0, -keys(f - 1, roll) * 0.3), (0, keys(f - 1, head) * 0.15, 0))
        bend(NECK, UP, [keys(f - 2, head) * 0.3, keys(f - 1, head) * 0.3, keys(f, head) * 0.4])
        bend(NECK, LEFT, [-keys(f - 1, hp) / 2, -keys(f, hp) / 2, 0])
        bend(TAIL, LEFT, [keys(f - 1 - i * 0.7, hp) * 0.4 for i in range(4)])
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "reach_smooth": P.get("reach_smooth")}


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
