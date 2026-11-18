"""Bewegungsmuster quadruped/wolf: Schritt (lateraler Viertakt), rotierender Galopp, Drehen, Idle, Pirsch, Sprung-Biss,
Treffer, Tod. Gemeinsame Bausteine: ../quadruped_kit.py

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/wolf/wolf_clips.py -- <ausgabe> [<creature.toml>]

Weiche Bewegung (2026-11-17, Nutzer: "Roboter-Wolf, kantig und abrupt"):
- Füße: gait_smooth (Schwung übernimmt die Standgeschwindigkeit, Abheben/Aufsetzen ohne Ruck).
- Rumpf-Absenkung bei überstreckten Beinen als glatte Kurve (reach_smooth) statt Knick an jedem Fußwechsel.
- Becken und Schultergürtel bewegen sich getrennt im Takt "ihrer" Beine (Verwringen statt starrer Block).
- Hals/Kopf und Schwanz ziehen verzögert nach (follow: Follow-Through/Overlap), Kopf wird stabilisiert.
- Einmal-Clips (Ready/Attack/Hit) über weiche Schlüsselkurven (keys) mit Ausholen, Überschwingen und Nachfedern.
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
from quadruped_kit import NECK, SPINE, TAIL, bend, follow, keys  # noqa: E402
from mathutils import Vector  # noqa: E402

ST, SIZE, HGT = K.ST, K.SIZE, K.HGT
TAU = 2 * math.pi
GIRDLE = (K.REST["FL"]["ball"].x - K.REST["BL"]["ball"].x) or 0.4 * SIZE   # Abstand Schulter ↔ Hüfte (für Rumpf-Neigung)


def trunk(pel=(0.0, 0.0, 0.0), sh=(0.0, 0.0, 0.0)):
    """Becken- und Schultergürtel getrennt drehen: (pitch + = vorne hoch, yaw + = nach links, roll + = linke Seite hoch),
    rad relativ zu Root. Der Rücken dazwischen verteilt die Differenz → Körper verwindet/biegt sich statt als Block."""
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
    td = {l: (-off[l]) % 1.0 for l in LEGS}                 # Aufsetz-Zeitpunkt je Bein (Zyklus-Anteil)
    mid_swing = {l: (td[l] + d + (1 - d) / 2) % 1.0 for l in LEGS}
    mid_stance = {l: (td[l] + d / 2) % 1.0 for l in LEGS}
    gallop = P.get("body") == "gallop"
    lag, tlag = P.get("neck_lag", 0.05), P.get("tail_lag", 0.07)
    sgn = (turn > 0) - (turn < 0)

    def girdles(t):
        """→ Root (dz, dy, pitch, roll), Becken (pitch, yaw, roll), Schulter (pitch, yaw, roll) – alles aus dem Fußtakt."""
        if gallop:
            # Rotierender Galopp: Rücken rund (gesammelt) beim Aufsetzen der Hinterbeine, gestreckt in der Schwebe danach;
            # Schaukeln: Brust hoch beim Abdruck hinten, tief über den Vorderbeinen. Rumpf am tiefsten mitten im Stand.
            flex = R(P["spine_flex_deg"]) * cyc(t, P["flex_peak"])
            pitch = R(P["pitch_deg"]) * cyc(t, P["pitch_peak"])
            dz = -P["bob"] * HGT * cyc(t, P["bob_low"], 2)
            roll = R(P.get("roll_deg", 0)) * cyc(t, mid_stance["BL"])
            yaw = R(P.get("spine_side_deg", 0)) * cyc(t, mid_stance["BL"])
            # Beugung sitzt v. a. in der Lende (Becken kippt), der Brustkorb bleibt fast waagerecht (Hund/Wolf)
            return (dz, 0.0, pitch, roll), (flex / 2, -yaw / 2, 0.0), (-flex * P.get("chest_flex", 0.1), yaw / 2, 0.0)
        # Schritt (Lateralsequenz): schwingt das linke Hinterbein, schiebt sich die linke Hüfte vor (Becken giert nach
        # rechts) und sinkt ab; Schultergürtel genauso im Takt der Vorderbeine. Höhe: Gürtel am höchsten mitten im Stand
        # (umgekehrtes Pendel), 2× pro Zyklus; Hüfte und Schulter um ¼ versetzt → Rumpf wiegt vor/zurück.
        hb, fb = mid_swing["BL"], mid_swing["FL"]
        yh, yf = R(P.get("hip_yaw_deg", 0)), R(P.get("shoulder_yaw_deg", 0))
        rh, rf = R(P.get("hip_roll_deg", 0)), R(P.get("shoulder_roll_deg", 0))
        B = P.get("bob", 0) * HGT
        zh, zf = B * cyc(t, mid_stance["BL"], 2), B * cyc(t, mid_stance["FL"], 2)
        dy = -P.get("sway", 0) * SIZE * (cyc(t, hb) + cyc(t, fb)) / 2
        return ((zh + zf) / 2, dy, math.atan2(zf - zh, GIRDLE), 0.0), \
            (0.0, -yh * cyc(t, hb), -rh * cyc(t, hb)), (0.0, -yf * cyc(t, fb), -rf * cyc(t, fb))

    def chest_pitch(t):        # Welt-Drehung der Brust um LEFT (Maß wie rot(): − = Brust hoch)
        rt, _, sh = girdles(t)
        return -(rt[2] + sh[0])

    def chest_yaw(t):
        return girdles(t)[2][1] + (sgn * R(P.get("turn_bend_deg", 0)) / 2 if turn else 0.0)

    def hip_pitch(t):
        rt, pel, _ = girdles(t)
        return -(rt[2] + pel[0]) + R(P.get("tail_bob_deg", 0)) * rt[0] / max(1e-6, P.get("bob", 0) * HGT or 1)

    def hip_yaw(t):
        return girdles(t)[1][1] - (sgn * R(P.get("turn_bend_deg", 0)) / 2 if turn else 0.0)

    def pose(f):
        t = (f % N) / N
        # gait() dreht bei turn > 0 die Füße im Stand gegen den Uhrzeigersinn → Körper dreht nach RECHTS. Bis 2026-11-17
        # war TurnLeft deshalb eine Rechtsdrehung; hier korrigiert: TurnLeft (turn > 0) dreht wirklich nach links.
        gait(t, P, off, turn=-turn)
        rt, pel, sh = girdles(t)
        body(dz=rt[0], dy=rt[1], pitch=rt[2], roll=rt[3])
        if turn:                                            # in die Kurve biegen: Brust/Kopf führen, Becken folgt
            b = sgn * R(P.get("turn_bend_deg", 0)) / 2
            pel, sh = (pel[0], pel[1] - b, pel[2]), (sh[0], sh[1] + b, sh[2])
        trunk(pel, sh)
        # Hals + Kopf: machen die Brustbewegung gedämpft und verzögert mit (stabilisierter Kopf), dazu eigenes Nicken
        g = P.get("head_gain", 0.6)
        np_ = follow(chest_pitch, t, 3, lag, g)
        ny = follow(chest_yaw, t, 3, lag, P.get("head_yaw_gain", g))
        nod = R(P.get("head_bob_deg", 0)) * cyc(t, P.get("nod_peak", mid_stance["FL"]), 2)
        bend(NECK, LEFT, [np_[0] - R(P.get("neck_lift_deg", 0)) / 2, np_[1] - R(P.get("neck_lift_deg", 0)) / 2,
                          np_[2] + R(P.get("neck_lift_deg", 0)) - nod])
        if turn:
            ny = [ny[0] + sgn * R(P.get("turn_head_deg", 0)) * 0.3, ny[1] + sgn * R(P.get("turn_head_deg", 0)) * 0.3,
                  ny[2] + sgn * R(P.get("turn_head_deg", 0)) * 0.4]
        bend(NECK, UP, ny)
        # Schwanz: hängt der Hüfte nach (jedes Glied später + weiter als das vorige)
        tg = P.get("tail_gain", 1.3)
        bend(TAIL, LEFT, [a + R(P.get("tail_lift_deg", 0)) / 4 for a in follow(hip_pitch, t, 4, tlag, tg)])
        side = follow(hip_yaw, t, 4, tlag, tg)
        sway = [R(P.get("tail_deg", 0)) * (0.25 + 0.25 * i) * math.sin(TAU * (t - P.get("tail_phase", 0)) - i * 0.9)
                for i in range(4)]
        tb = [-sgn * R(P.get("turn_tail_deg", 0)) / 4] * 4 if turn else [0.0] * 4
        bend(TAIL, UP, [a + b + c for a, b, c in zip(side, sway, tb)])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn,
            "max_stretch": P.get("max_stretch"), "reach_smooth": P.get("reach_smooth"), "reach_flat": P.get("reach_flat", 0),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], d)[0]}


# ---------------------------------------------------------------- Stand-Clips
def look_chain(yaw_fn, pitch_fn, x, lag):
    """Kopf führt, Hals folgt: Kopf bekommt den Zielwinkel sofort, Neck_2 60 % etwas später, Neck_1 30 % noch später."""
    for axis, fn, sg in ((UP, yaw_fn, 1), (LEFT, pitch_fn, -1)):
        w = [0.3 * fn(x - 2 * lag), 0.6 * fn(x - lag), fn(x)]
        bend(NECK, axis, [sg * w[0], sg * (w[1] - w[0]), sg * (w[2] - w[1])])


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        br = math.sin(TAU * 3 * t)                                  # 3 Atemzüge
        shift = math.sin(TAU * t)                                   # Gewicht langsam links/rechts verlagern
        body(dz=0.006 * HGT * br, dy=0.008 * SIZE * shift, roll=R(1.2) * shift)
        trunk((0, 0, -R(1.0) * shift), (R(P["breathe_deg"]) * br, 0, R(0.8) * shift))
        look = [(0, 0), (0.12, 0), (0.3, 1), (0.45, 1), (0.62, -0.7), (0.8, -0.7), (1, 0)]
        nod = [(0, 0), (0.25, 0.3), (0.5, -0.4), (0.75, 0.2), (1, 0)]
        look_chain(lambda x: R(P["look_deg"]) * keys(x, look, loop=True), lambda x: R(5) * keys(x, nod, loop=True),
                   t, 0.03)
        hip = lambda x: -R(1.0) * math.sin(TAU * x)                 # noqa: E731
        bend(TAIL, UP, [a + R(P["tail_deg"]) * (0.3 + 0.2 * i) * math.sin(TAU * 2 * t - i * 0.8)
                        for i, a in enumerate(follow(hip, t, 4, 0.06, 1.4))])
        bend(TAIL, LEFT, [-R(10) / 4] * 4)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_ready(P):
    """Pirsch-Haltung: geduckt, Kopf tief + vorn, wiegt sich langsam vor/zurück (Gewicht auf die Hinterbeine laden),
    Kopf fixiert das Ziel (bleibt ruhig, während der Körper wiegt), Lefzen zucken, Schwanz steif mit zuckender Spitze."""
    N = P["frames"]

    def pose(f):
        t = f / N
        rock = math.sin(TAU * t)
        br = math.sin(TAU * 2 * t)
        body(dz=-P["crouch"] * HGT + 0.01 * HGT * br, dx=P.get("rock", 0.015) * SIZE * rock,
             pitch=-R(P.get("pitch_deg", 4)) - R(1.5) * rock)
        trunk((R(2) * rock, 0, 0), (-R(2) * rock + R(1.0) * br, 0, 0))
        hd = R(P["head_down_deg"])
        chest = lambda x: -R(1.5) * math.sin(TAU * x)              # noqa: E731
        np_ = follow(chest, t, 3, 0.05, 0.4)                        # Kopf gleicht das Wiegen aus → fixiert das Ziel
        bend(NECK, LEFT, [np_[0] + hd / 2, np_[1] + hd / 2, np_[2] - hd * 0.6])
        bend(NECK, UP, [0, R(3) * math.sin(TAU * t + 1), R(3) * math.sin(TAU * t + 0.6)])
        jaw(P["jaw_deg"] + P.get("snarl_deg", 4) * max(0.0, math.sin(TAU * 2 * t)) ** 2)
        tip = R(P.get("tail_twitch_deg", 8)) * math.sin(TAU * 3 * t) ** 3
        bend(TAIL, LEFT, [R(P["tail_lift_deg"]) / 4] * 4)
        bend(TAIL, UP, [0, 0, tip * 0.4, tip])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth")}


def clip_attack1(P):
    """Sprung-Biss mit stehenden Füßen: ducken + zurückladen (Ausholen) → nach vorn schnellen, Hals streckt, Maul auf →
    zuschnappen (hit) → festbeißen, zerren + Kopfschütteln → zurückfedern. Kopf/Schwanz folgen verzögert."""
    N, w, s = P["frames"], P["windup_end"], P["strike_end"]
    h = P["hit_frame"]
    c, L, U = P["crouch"] * HGT, P["lunge"] * SIZE, P["lunge_up"] * HGT
    rec = N - 5                                                  # alles ist 5 Frames vor Schluss wieder in Ruhe
    dz = [(0, 0), (w, -c), (s - 1, U * 0.3), (s, U), (s + 3, U * 0.4), (s + 7, -c * 0.25), (rec, 0)]
    dx = [(0, 0), (w, -0.04 * SIZE), (s, L), (s + 2, L * 1.05), (s + 6, L * 0.55), (s + 9, L * 0.7), (rec, 0)]
    pitch = [(0, 0), (w, -R(7)), (s, R(6)), (s + 3, R(2)), (s + 7, -R(2)), (rec, 0)]
    flex = [(0, 0), (w, R(12)), (s - 1, -R(8)), (s + 4, -R(3)), (s + 8, R(2)), (rec, 0)]
    nk = P["neck_reach_deg"]
    neck = [(0, 0), (w, -R(12)), (s, R(nk) * 0.3), (s + 4, R(nk) * 0.15), (s + 8, -R(4)), (rec, 0)]
    head = [(0, 0), (w, R(10)), (s, -R(nk) * 0.4), (s + 4, -R(nk) * 0.3), (s + 8, R(3)), (rec, 0)]
    sk = R(P.get("shake_deg", 14))                              # Kopfschütteln ≈ 5 Hz (Hund/Wolf beim Zerren)
    shake = [(0, 0), (h, 0), (h + 3, sk), (h + 6, -sk * 0.8), (h + 9, sk * 0.35), (rec, 0)]
    jw = [(0, 0), (w - 3, P["jaw_open_deg"] * 0.15), (s - 2, P["jaw_open_deg"]), (h - 1, P["jaw_open_deg"]), (h, 0),
          (N, 0)]
    tail_l = [(0, 0), (w, -R(10)), (s + 1, R(14)), (s + 6, -R(6)), (s + 11, R(2)), (rec, 0)]

    def pose(f):
        body(dz=keys(f, dz), dx=keys(f, dx), pitch=keys(f, pitch))
        fl = keys(f, flex)
        trunk((fl / 2, 0, 0), (-fl / 2, 0, 0))
        nl = [keys(f - k, neck) / 2 for k in (1, 0)]                # Neck_1 hängt 1 Frame nach
        bend(NECK, LEFT, [-nl[0], -nl[1], -keys(f, head)])
        bend(NECK, UP, [keys(f - 1, shake) * 0.3, keys(f, shake) * 0.3, keys(f, shake) * 0.4])
        jaw(keys(f, jw))
        bend(TAIL, LEFT, [keys(f - 1 - i, tail_l) * (0.2 + 0.1 * i) for i in range(4)])
        bend(TAIL, UP, [keys(f - 2 - i, shake) * -0.4 for i in range(4)])
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "events": [{"frame": h, "event": "hit"}]}


def clip_hit(P):
    """Treffer: harter Stoß (2 Frames), Kopf schlägt verzögert zur Seite, federt gedämpft nach und kommt zur Ruhe."""
    N = P["frames"]
    j, ro, hd = P["jolt"] * SIZE, R(P["roll_deg"]), R(P["head_deg"])
    e = N - 4
    dx = [(0, 0), (2, -j), (5, -j * 0.55), (7, j * 0.12), (9, -j * 0.04), (e, 0)]
    dz = [(0, 0), (3, -0.05 * HGT), (7, 0.01 * HGT), (e, 0)]
    roll = [(0, 0), (2, ro), (5, -ro * 0.35), (7, ro * 0.12), (e, 0)]
    head = [(0, 0), (3, hd), (5, -hd * 0.35), (8, hd * 0.12), (e, 0)]
    hp = [(0, 0), (3, R(8)), (6, -R(3)), (e, 0)]
    tl = [(0, 0), (3, -R(16)), (7, R(6)), (e, 0)]

    def pose(f):
        body(dx=keys(f, dx), dz=keys(f, dz), roll=keys(f, roll))
        trunk((0, 0, -keys(f - 1, roll) * 0.3), (0, keys(f - 1, head) * 0.15, 0))
        bend(NECK, UP, [keys(f - 2, head) * 0.3, keys(f - 1, head) * 0.3, keys(f, head) * 0.4])
        bend(NECK, LEFT, [-keys(f - 1, hp) / 2, -keys(f, hp) / 2, 0])
        bend(TAIL, LEFT, [keys(f - 1 - i * 0.7, tl) / 4 for i in range(4)])
        bend(TAIL, UP, [-keys(f - 1 - i * 0.7, head) * 0.15 for i in range(4)])
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
IK_STIFF = ST.get("ik", {}).get("stiffness", {})              # z. B. {"Leg_3": 0.8} – gilt nicht für Death


def stiff(spec):
    spec["ik_stiff"] = IK_STIFF
    spec["foot_ground"] = True                                  # kein Fuß unter dem Boden (Kit: feet_on_ground)
    return spec


K.bake({
    "Walk": stiff(locomotion(ST["walk"])),
    "Run": stiff(locomotion(ST["run"])),
    "TurnLeft": stiff(locomotion(ST["turn"], turn=turn)),
    "TurnRight": stiff(locomotion(ST["turn"], turn=-turn)),
    "Idle": stiff(clip_idle(ST["idle"])),
    "Ready": stiff(clip_ready(ST["ready"])),
    "Attack1": stiff(clip_attack1(ST["attack1"])),
    "Hit": stiff(clip_hit(ST["hit"])),
    "Death": clip_death(ST["death"]),
})
