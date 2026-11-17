"""Bewegungsmuster quadruped/lizard: Echse/Waran. Diagonal-Trab mit stehender Rumpfwelle (Schulter- und Beckengürtel
gieren gegenläufig, Schwanz setzt die Welle fort), Lauf = schneller Trab mit größerer Welle, Idle, Drohen (Seitenprofil,
Hals gebogen, Maul weit auf, Schwanz peitscht), Schnappbiss mit Kopfschwung von der Seite zur Mitte + Zurückreißen,
Treffer, Tod. Gemeinsame Bausteine: ../quadruped_kit.py
(Entstanden als Kopie von wolf_clips.py, 2026-11-17 – ab jetzt eigenständig, Änderungen hier betreffen nur lizard.)

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/lizard/lizard_clips.py -- <ausgabe> [<creature.toml>]
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
GIRDLE = (K.REST["FL"]["ball"].x - K.REST["BL"]["ball"].x) or 0.4 * SIZE


def trunk(pel=(0.0, 0.0, 0.0), sh=(0.0, 0.0, 0.0)):
    """Becken- und Schultergürtel getrennt drehen: (pitch + = vorne hoch, yaw + = nach links, roll + = linke Seite hoch),
    rad relativ zu Root. Der Rücken dazwischen verteilt die Differenz → Körper biegt sich statt als Block zu drehen."""
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
    mid_stance = {l: (td[l] + d / 2) % 1.0 for l in LEGS}
    lag, tlag = P.get("neck_lag", 0.05), P.get("tail_lag", 0.07)
    sgn = (turn > 0) - (turn < 0)
    w0 = td["FR"] + P.get("wave_shift", 0.0)              # größte Krümmung beim Aufsetzen des rechten Vorderbeins

    def girdles(t):
        """Waran-Gang (Ritter 1992, XROMM Varanus 2020): Schultergürtel giert zum aufsetzenden Vorderbein hin
        (rechts vorn setzt auf → rechte Schulter vorn → Brust zeigt nach links), Becken gegenläufig → S-Welle;
        beim Aufsetzen eines Vorderbeins ist die Krümmung maximal. wave_lag lässt die Welle leicht nach hinten laufen."""
        A_s, A_p = R(P.get("shoulder_yaw_deg", 0)), R(P.get("hip_yaw_deg", 0))
        sh_yaw = A_s * cyc(t, w0)
        pel_yaw = -A_p * cyc(t, w0 + P.get("wave_lag", 0.0))
        rl = R(P.get("roll_deg", 0)) * cyc(t, mid_stance["BL"])
        dz = P.get("bob", 0) * HGT * cyc(t, mid_stance["BL"], 2)
        dy = -P.get("sway", 0) * SIZE * cyc(t, w0)
        return (dz, dy, 0.0, rl), (0.0, pel_yaw, -rl * 0.5), (0.0, sh_yaw, rl * 0.3)

    def chest_yaw(t):
        return girdles(t)[2][1] + (sgn * R(P.get("turn_bend_deg", 0)) / 2 if turn else 0.0)

    def hip_yaw(t):
        return girdles(t)[1][1] - (sgn * R(P.get("turn_bend_deg", 0)) / 2 if turn else 0.0)

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=-turn)                         # −: gait dreht bei turn > 0 nach rechts (siehe wolf_clips.py)
        rt, pel, sh = girdles(t)
        body(dz=rt[0], dy=rt[1], roll=rt[3])
        if turn:                                            # in die Kurve biegen: Brust/Kopf führen, Becken folgt
            b = sgn * R(P.get("turn_bend_deg", 0)) / 2
            pel, sh = (pel[0], pel[1] - b, pel[2]), (sh[0], sh[1] + b, sh[2])
        trunk(pel, sh)
        # Kopf: Echsen halten den Kopf relativ ruhig in Laufrichtung → Hals gleicht die Schulter-Drehung verzögert aus
        ny = follow(chest_yaw, t, 3, lag, P.get("head_gain", 0.5))
        if turn:
            hd = sgn * R(P.get("turn_head_deg", 0))
            ny = [ny[0] + hd * 0.3, ny[1] + hd * 0.3, ny[2] + hd * 0.4]
        bend(NECK, UP, ny)
        nod = R(P.get("head_bob_deg", 0)) * cyc(t, mid_stance["FL"], 2)
        bend(NECK, LEFT, [-R(P.get("neck_lift_deg", 0)) / 2, -R(P.get("neck_lift_deg", 0)) / 2,
                          R(P.get("neck_lift_deg", 0)) - nod])
        # Schwanz: setzt die Rumpfwelle fort (Welle läuft nach hinten), jedes Glied später + weiter
        tg = P.get("tail_gain", 1.3)
        side = follow(hip_yaw, t, 4, tlag, tg)
        tb = [-sgn * R(P.get("turn_tail_deg", 0)) / 4] * 4 if turn else [0.0] * 4
        bend(TAIL, UP, [a + b for a, b in zip(side, tb)])
        bend(TAIL, LEFT, [R(P.get("tail_lift_deg", 0)) / 4] * 4)
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
    """Ruhig liegen/stehen wie ein Waran: tiefe, langsame Atmung (Flanken), Kopf ruckt in kurzen Blicken (Echsen
    bewegen den Kopf in Sprüngen mit Pausen, weich abgebremst), Schwanzspitze schlängelt träge."""
    N = P["frames"]

    def pose(f):
        t = f / N
        br = math.sin(TAU * 2 * t)
        body(dz=0.008 * HGT * br, roll=R(1.0) * math.sin(TAU * t))
        trunk((0, R(2) * math.sin(TAU * t), 0), (R(P["breathe_deg"]) * br, -R(2) * math.sin(TAU * t), 0))
        look = [(0, 0), (0.1, 0), (0.16, 1), (0.4, 1), (0.46, 0.2), (0.6, 0.2), (0.66, -0.8), (0.88, -0.8), (0.94, 0),
                (1, 0)]
        lift = [(0, 0), (0.16, 0.5), (0.4, 0.5), (0.46, 0), (0.66, 0.3), (0.88, 0.3), (0.94, 0), (1, 0)]
        look_chain(lambda x: R(P["look_deg"]) * keys(x, look, loop=True), lambda x: R(6) * keys(x, lift, loop=True),
                   t, 0.015)
        hip = lambda x: R(2) * math.sin(TAU * x)                     # noqa: E731
        bend(TAIL, UP, [a + R(P["tail_deg"]) * (0.2 + 0.25 * i) * math.sin(TAU * 2 * t - i * 1.0)
                        for i, a in enumerate(follow(hip, t, 4, 0.06, 1.3))])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_ready(P):
    """Drohen (Waran-Drohgebärde): Körper biegt sich seitlich zum Gegner (Seitenprofil = größer wirken), Hals hoch
    gebogen, Maul weit auf und Fauchen in Stößen (Brust pumpt), Schwanz zur Seite gespannt und peitscht langsam.
    Ganzkörper: Rumpf wiegt, Kopf fixiert."""
    N = P["frames"]
    arc = R(P.get("arc_deg", 14))

    def pose(f):
        t = f / N
        hiss = max(0.0, math.sin(TAU * 2 * t)) ** 2                 # 2 Fauch-Stöße pro Schleife
        sway = math.sin(TAU * t)
        body(dz=-P["crouch"] * HGT + 0.012 * HGT * hiss, dy=0.01 * SIZE * sway, roll=R(P.get("lean_deg", 4)) + R(1.5) * sway,
             pitch=R(P.get("pitch_deg", 3)))
        trunk((0, -arc + R(2) * sway, 0), (R(2) * hiss, arc - R(2) * sway, 0))
        # Hals hoch, Kopf zum Gegner (nach vorn) – gleicht den Rumpfbogen aus
        hu = R(P["head_up_deg"])
        bend(NECK, LEFT, [-hu * 0.6, -hu * 0.4 - R(3) * hiss, hu * 0.5 + R(4) * hiss])
        bend(NECK, UP, [-arc * 0.4, -arc * 0.4 + R(2) * sway, -arc * 0.2 - R(2) * sway])
        jaw(P["jaw_deg"] + P.get("hiss_jaw_deg", 8) * hiss)
        lash = [R(P["tail_lash_deg"]) * (0.3 + 0.25 * i) * math.sin(TAU * t - i * 0.9) for i in range(4)]
        bend(TAIL, UP, [l + arc * 0.5 for l in lash])
        bend(TAIL, LEFT, [R(P["tail_lift_deg"]) / 4] * 4)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth")}


def clip_attack1(P):
    """Schnappbiss (Waran/Komodo): Kopf + Hals holen zur Seite aus (S-Kurve, Körper lädt zurück) → Körper schnellt vor,
    Kopf schwingt von der Seite zur Mitte, Maul weit auf → zuschnappen (hit) → Kopf reißt zurück und zur anderen Seite
    (Fleisch reißen), Schwanz schwingt gegen. Füße bleiben stehen."""
    N, w, s = P["frames"], P["windup_end"], P["strike_end"]
    h = P["hit_frame"]
    L, c = P["lunge"] * SIZE, P["crouch"] * HGT
    sy = R(P["snap_yaw_deg"])
    rec = N - 5
    dx = [(0, 0), (w, -0.05 * SIZE), (s, L), (s + 2, L * 1.05), (s + 6, -0.02 * SIZE), (s + 10, 0.01 * SIZE), (rec, 0)]
    dz = [(0, 0), (w, -c), (s, c * 0.2), (s + 6, -c * 0.4), (rec, 0)]
    bodyyaw = [(0, 0), (w, sy * 0.35), (s, -sy * 0.15), (s + 5, -sy * 0.3), (s + 10, sy * 0.05), (rec, 0)]
    arc = [(0, 0), (w, sy * 0.6), (s, -sy * 0.2), (s + 5, -sy * 0.5), (s + 10, sy * 0.1), (rec, 0)]
    headyaw = [(0, 0), (w, sy), (s - 1, sy * 0.2), (s, -sy * 0.15), (s + 5, -sy * 0.6), (s + 10, sy * 0.1), (rec, 0)]
    nk = R(P["neck_reach_deg"])
    neckp = [(0, 0), (w, nk * 0.5), (s, -nk * 0.2), (s + 5, nk * 0.3), (rec, 0)]        # + = hoch
    headp = [(0, 0), (w, -nk * 0.3), (s, nk * 0.1), (s + 5, -nk * 0.2), (rec, 0)]
    jw = [(0, 0), (w - 3, P["jaw_open_deg"] * 0.2), (s - 2, P["jaw_open_deg"]), (h - 1, P["jaw_open_deg"]), (h, 0), (N, 0)]

    def pose(f):
        by = keys(f, bodyyaw)
        body(dx=keys(f, dx), dz=keys(f, dz), yaw=by)
        a = keys(f - 1, arc)
        trunk((0, -a * 0.5, 0), (0, a * 0.5, 0))
        C = by + a * 0.5                                            # Welt-Gieren der Brust
        H = [keys(f - 2, headyaw) - C, keys(f - 1, headyaw) - C, keys(f, headyaw) - C]
        bend(NECK, UP, [0.35 * H[0], 0.35 * H[1], H[2] - 0.35 * H[0] - 0.35 * H[1]])   # Kopf führt, Hals folgt
        bend(NECK, LEFT, [-keys(f - 1, neckp) / 2, -keys(f, neckp) / 2, -keys(f, headp)])
        jaw(keys(f, jw))
        bend(TAIL, UP, [keys(f - 2 - i, arc) * (0.3 + 0.15 * i) for i in range(4)])
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "events": [{"frame": h, "event": "hit"}]}


def clip_hit(P):
    """Treffer: Stoß von vorn-rechts, Rumpf knickt seitlich ein, Kopf schlägt verzögert weg, Schwanz peitscht nach,
    gedämpftes Nachfedern bis zur Ruhe."""
    N = P["frames"]
    j, ro, hd = P["jolt"] * SIZE, R(P["roll_deg"]), R(P["head_deg"])
    e = N - 4
    dx = [(0, 0), (2, -j), (5, -j * 0.55), (7, j * 0.12), (9, -j * 0.04), (e, 0)]
    roll = [(0, 0), (2, ro), (5, -ro * 0.35), (7, ro * 0.12), (e, 0)]
    bendk = [(0, 0), (2, R(10)), (5, -R(4)), (8, R(1.5)), (e, 0)]
    head = [(0, 0), (3, hd), (5, -hd * 0.35), (8, hd * 0.12), (e, 0)]

    def pose(f):
        body(dx=keys(f, dx), roll=keys(f, roll))
        b = keys(f - 1, bendk)
        trunk((0, -b * 0.5, 0), (0, b * 0.5, 0))
        bend(NECK, UP, [keys(f - 2, head) * 0.3, keys(f - 1, head) * 0.3, keys(f, head) * 0.4])
        bend(TAIL, UP, [keys(f - 1 - i * 0.7, bendk) * (0.4 + 0.2 * i) for i in range(4)])
        jaw(6 * max(0.0, keys(f, head) / hd) if hd else 0)
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
