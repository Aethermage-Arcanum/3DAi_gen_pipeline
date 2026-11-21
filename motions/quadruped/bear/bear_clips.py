"""Bewegungsmuster quadruped/bear (Bär, erstes Modell Rimehide Bear = nackte Basis aller Bären-Varianten):
Schritt (lateraler Viertakt, Passgang-artig, rollende Schultern, Kopf pendelt tief), schwerer Galopp, Drehen (Körper biegt
sich in die Kurve, Kopf führt), Idle (schnüffeln, umschauen), Drohen (Kopf tief, Kiefer klappt, Brüllen, Pranke schlägt
auf den Boden), Attack1 = Prankenhieb, Attack2 = Aufrichten + Doppelpranken-Slam, Treffer, Tod (Platzhalter).
Gemeinsame Bausteine: ../quadruped_kit.py (nur gelesen, nicht verändert). Eigener Code – andere Muster benutzen diese
Datei NICHT (Kapselung, siehe motions/README.md). Entstanden 2026-11-21 mit Teilen aus wolf/deer (kopiert, nicht importiert).

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/bear/bear_clips.py -- <ausgabe> [<creature.toml>]
"""
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
import bpy  # noqa: E402
from mathutils import Quaternion, Vector  # noqa: E402
from quadruped_kit import (FWD, LEFT, UP, LEGS, R, body, ease, ik_off, jaw, neck_head,  # noqa: E402
                           phase, rot, tail)
from quadruped_kit import NECK, SPINE, TAIL, bend, bump, follow, keys  # noqa: E402

ST, SIZE, HGT = K.ST, K.SIZE, K.HGT
TAU = 2 * math.pi
GIRDLE = (K.REST["FL"]["ball"].x - K.REST["BL"]["ball"].x) or 0.4 * SIZE
HIP = (K.DB["Leg_BL_1"].head_local + K.DB["Leg_BR_1"].head_local) / 2     # Drehpunkt beim Aufrichten
H0 = K.DB["Root"].head_local.copy()


def trunk(pel=(0.0, 0.0, 0.0), sh=(0.0, 0.0, 0.0)):
    """Becken- und Schultergürtel getrennt drehen: (pitch + = vorne hoch, yaw + = nach links, roll + = linke Seite hoch),
    rad relativ zu Root. Der Rücken dazwischen verteilt die Differenz → Körper verwindet/biegt sich statt als Block."""
    for axis, a, b, sgn in ((LEFT, pel[0], sh[0], -1), (UP, pel[1], sh[1], 1), (FWD, pel[2], sh[2], 1)):
        bend(SPINE, axis, (sgn * a, sgn * (b - a) / 2, sgn * (b - a) / 2))


def cyc(t, at, cycles=1):
    """cos-Welle mit Maximum bei Zyklus-Anteil `at`."""
    return math.cos(TAU * cycles * (t - at))


def foot(leg, world_target, curl=0.0):
    """Fuß-Ziel als absolute Position (Armature-Raum) statt Versatz."""
    K.set_foot(leg, world_target - K.REST[leg]["ball"], curl)


def rear_body(pitch, piv_shift=Vector(), dx=0.0, dz=0.0, roll=0.0):
    """Ganzer Körper kippt um die Hüfte (nicht um die Körpermitte): pitch + = Brust hoch. piv_shift = Hüfte verschiebt
    sich (auf die Hinterbeine setzen). Füße bleiben per IK stehen."""
    q = Quaternion(LEFT, -pitch)
    loc = (HIP + piv_shift - H0) - q @ (HIP - H0) + Vector((dx, 0, dz))
    rot("Root", LEFT, -pitch)
    if roll:
        rot("Root", FWD, roll)
    K.move("Root", loc)


def chest_xform():
    """Aktuelle Starrkörper-Bewegung der Brust (Armature-Raum, Ruhe → jetzt)."""
    bpy.context.view_layer.update()
    return K.PB["Chest"].matrix @ K.DB["Chest"].matrix_local.inverted()


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
        """→ Root (dz, dy, pitch, roll), Becken (pitch, yaw, roll), Schulter (pitch, yaw, roll) – aus dem Fußtakt."""
        if gallop:
            # Schwerer Galopp: Rücken rund beim Aufsetzen hinten (Kruppe hebt sich), gestreckt beim Abdruck; Buckel
            # schaukelt (Brust hoch beim Abdruck hinten, tief beim Landen vorn); schwerer Körper rollt mit.
            flex = R(P["spine_flex_deg"]) * cyc(t, P["flex_peak"])
            pitch = R(P["pitch_deg"]) * cyc(t, P["pitch_peak"])
            dz = -P["bob"] * HGT * cyc(t, P["bob_low"], 2)
            roll = R(P.get("roll_deg", 0)) * cyc(t, mid_stance["BL"])
            yaw = R(P.get("spine_side_deg", 0)) * cyc(t, mid_stance["BL"])
            return (dz, 0.0, pitch, roll), (flex / 2, -yaw / 2, 0.0), (-flex * P.get("chest_flex", 0.15), yaw / 2, roll)
        # Schritt: schwingt ein Bein, sinkt diese Seite ab und der Gürtel giert mit (Schulter stärker als Becken = Buckel
        # rollt); Rumpf schwankt zum Standbein. Gürtel am höchsten mitten im Stand (umgekehrtes Pendel).
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
        # gait() dreht bei turn > 0 die Füße im Stand gegen den Uhrzeigersinn → Körper dreht nach RECHTS; deshalb −turn:
        # TurnLeft (turn > 0) dreht nach links (gleiche Konvention wie wolf/deer, gemessen in turn_check unten).
        K.gait(t, P, off, turn=-turn)
        rt, pel, sh = girdles(t)
        body(dz=rt[0], dy=rt[1], pitch=rt[2], roll=rt[3])
        if turn:                                            # in die Kurve biegen: Brust/Kopf führen, Becken folgt
            b = sgn * R(P.get("turn_bend_deg", 0)) / 2
            pel, sh = (pel[0], pel[1] - b, pel[2]), (sh[0], sh[1] + b, sh[2])
        trunk(pel, sh)
        # Hals + Kopf: Hals tief, Kopf gleicht teilweise aus; Kopf pendelt seitlich (1× pro Zyklus, verzögert gegen die
        # Schultern), Nicken im Takt der Vorderbeine.
        g = P.get("head_gain", 0.55)
        np_ = follow(chest_pitch, t, 3, lag, g)
        ny = follow(chest_yaw, t, 3, lag, g)
        nl = R(P.get("neck_lift_deg", 0))
        nod = R(P.get("head_bob_deg", 0)) * cyc(t, P.get("nod_peak", mid_stance["FL"]), 2)
        bend(NECK, LEFT, [np_[0] - nl / 2, np_[1] - nl / 2, np_[2] + nl - nod])
        sw = R(P.get("head_swing_deg", 0)) * cyc(t, mid_stance["FL"] + P.get("head_swing_lag", 0.1))
        ny = [ny[0] + sw * 0.2, ny[1] + sw * 0.35, ny[2] + sw * 0.45]
        if turn:
            hd = sgn * R(P.get("turn_head_deg", 0))
            ny = [ny[0] + hd * 0.3, ny[1] + hd * 0.3, ny[2] + hd * 0.4]
        bend(NECK, UP, ny)
        # Stummelschwanz: hängt, zuckt leicht mit dem Becken
        bend(TAIL, LEFT, [R(P.get("tail_lift_deg", 0)) / 4] * 4)
        bend(TAIL, UP, [R(P.get("tail_deg", 0)) * (0.3 + 0.2 * i) * math.sin(TAU * t - i * 0.8) for i in range(4)])
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn,
            "max_stretch": P.get("max_stretch"), "reach_smooth": P.get("reach_smooth"), "reach_flat": P.get("reach_flat", 0),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], d)[0]}


# ---------------------------------------------------------------- Stand-Clips
def look_chain(yaw_fn, pitch_fn, x, lag):
    """Kopf führt, Hals folgt: Kopf bekommt den Zielwinkel sofort, Neck_2 60 % etwas später, Neck_1 30 % noch später.
    pitch_fn + = Kopf hoch."""
    for axis, fn, sg in ((UP, yaw_fn, 1), (LEFT, pitch_fn, -1)):
        w = [0.3 * fn(x - 2 * lag), 0.6 * fn(x - lag), fn(x)]
        bend(NECK, axis, [sg * w[0], sg * (w[1] - w[0]), sg * (w[2] - w[1])])


def clip_idle(P):
    """Schwer atmen, Gewicht verlagern; Kopf senkt sich und schnüffelt am Boden, hebt sich, schaut nach rechts und links
    (Kopf führt, Hals folgt), Kopf leicht tief."""
    N = P["frames"]
    sn = R(P.get("sniff_deg", 14))

    def pose(f):
        t = f / N
        br = math.sin(TAU * 4 * t)                                  # 4 tiefe Atemzüge
        shift = math.sin(TAU * t)
        body(dz=0.006 * HGT * br, dy=0.010 * SIZE * shift, roll=R(1.5) * shift)
        trunk((0, 0, -R(1.2) * shift), (R(P["breathe_deg"]) * br, 0, R(1.0) * shift))
        look = [(0, 0), (0.4, 0), (0.5, 0.9), (0.6, 0.9), (0.72, -0.8), (0.86, -0.8), (1, 0)]
        lift = [(0, -0.3), (0.08, -1.0), (0.14, -0.85), (0.2, -1.0), (0.26, -0.85), (0.34, -0.2), (0.5, 0.25),
                (0.86, 0.2), (1, -0.3)]
        look_chain(lambda x: R(P["look_deg"]) * keys(x, look, loop=True), lambda x: sn * keys(x, lift, loop=True),
                   t, 0.03)
        jaw(2.0 * max(0.0, math.sin(TAU * 12 * t)) * (0.08 < t < 0.3))   # Schnuppern
        bend(TAIL, LEFT, [-R(6) / 4] * 4)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_ready(P):
    """Drohen: Gewicht nach vorn, Kopf tief und pendelt seitlich (Kopf führt), Kiefer klappt 2× (Jaw-Popping) und 1×
    Brüllen angedeutet, Vorderpranke schlägt 1× auf den Boden (Warnsignal), Rumpf schaukelt. Schleife."""
    N = P["frames"]
    slap = P.get("slap_leg", "FL")
    hd = R(P["head_down_deg"])

    def pose(f):
        t = f / N
        rock = math.sin(TAU * t)
        br = math.sin(TAU * 3 * t)
        # Pranke: 0,52–0,62 heben (Rumpf richtet sich etwas auf), 0,62–0,67 hart aufschlagen
        up = keys(t, [(0, 0), (0.5, 0), (0.6, 1), (0.62, 1), (0.665, 0), (1, 0)])
        body(dz=-P["crouch"] * HGT + 0.008 * HGT * br + 0.03 * HGT * up, dx=P.get("lean", 0.02) * SIZE * (0.6 + 0.4 * rock),
             pitch=-R(3) + R(5) * up, roll=R(2) * up)
        trunk((R(1.5) * rock, 0, 0), (-R(1.5) * rock + R(1.2) * br, R(4) * up, R(3) * up))
        K.set_foot(slap, Vector((0.03 * SIZE * up, 0.01 * SIZE * up, P["slap_lift"] * HGT * up)), R(20) * up)
        sweep = R(P.get("sweep_deg", 12)) * math.sin(TAU * t + 0.4)
        roar = keys(t, [(0, 0), (0.18, 0), (0.26, 1), (0.36, 1), (0.44, 0), (1, 0)])
        bend(NECK, LEFT, [hd * 0.45 - R(8) * roar, hd * 0.45 - R(6) * roar, -hd * 0.2 - R(10) * roar + R(8) * up])
        bend(NECK, UP, [sweep * 0.2, sweep * 0.3, sweep * 0.5])
        pop = sum(max(0.0, math.sin(TAU * (t - c) / 0.12)) if 0 <= t - c < 0.06 else 0.0 for c in (0.04, 0.7, 0.82))
        jaw(P["jaw_pop_deg"] * pop + P["roar_deg"] * roar)
        bend(TAIL, LEFT, [-R(4) / 4] * 4)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": [l for l in LEGS if l != slap],
            "events": [{"frame": round(0.665 * N), "event": "slam"}]}


def clip_attack1(P):
    """Prankenhieb (seitlich von oben): Gewicht zur Gegenseite und nach hinten, Brust hebt sich, Schulter dreht weg,
    Pranke hoch + nach außen (Ausholen) → Rumpf verdreht sich schnell zurück, Schulter rollt nach unten, Pranke fährt
    schräg von oben nach innen-vorn (hit) und schlägt auf → Nachfedern → Pranke zurück. Kopf geht in den Hieb."""
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hit_frame"]
    leg = P.get("leg", "FR")
    side = 1 if leg[1] == "L" else -1                     # Seite der Schlagpranke (+ = links)
    rec = N - 4
    land = s + 3
    up_, out, back = P["paw_up"] * HGT, P["paw_out"] * SIZE, P["paw_back"] * SIZE
    reach, across = P["paw_reach"] * SIZE, P["paw_across"] * SIZE
    px = [(0, 0), (4, 0), (w, -back), (s - 2, reach * 0.6), (s, reach), (land, reach), (rec - 9, reach),
          (rec - 4, reach * 0.4), (rec, 0)]
    py = [(0, 0), (4, side * out * 0.3), (w, side * out), (s - 2, side * out * 0.2), (s, -side * across),
          (land, -side * across), (rec - 9, -side * across), (rec - 4, -side * across * 0.4), (rec, 0)]
    pz = [(0, 0), (4, up_ * 0.35), (w, up_), (s - 2, up_ * 0.7), (s, 0.12 * HGT), (land, 0), (rec - 9, 0),
          (rec - 6, 0.14 * HGT), (rec - 2, 0.03 * HGT), (rec, 0)]
    curl = [(0, 0), (w, R(30)), (s - 1, R(-10)), (land, 0), (rec, 0)]
    pitch = [(0, 0), (w, R(P["rear_deg"])), (s, -R(3)), (land + 1, -R(5)), (land + 6, -R(1)), (rec, 0)]
    twist = [(0, 0), (w, side * R(P["twist_deg"])), (s - 1, -side * R(P["twist_deg"]) * 0.7), (land, -side * R(6)),
             (rec, 0)]   # Schultergürtel-Gieren (+ = links): Ausholen zur Schlagseite, Hieb dreht zur Gegenseite
    roll = [(0, 0), (w, side * R(P["roll_deg"])), (s, -side * R(P["roll_deg"]) * 0.6), (land + 4, -side * R(1)),
            (rec, 0)]                                      # roll + = linke Seite hoch
    lean = [(0, 0), (w, -side * P["lean"] * SIZE), (s, side * P["lean"] * SIZE * 0.3), (rec, 0)]
    dx = [(0, 0), (w, -0.02 * SIZE), (s, P["lunge"] * SIZE), (land + 3, P["lunge"] * SIZE * 0.8), (rec, 0)]
    dz = [(0, 0), (w, 0.02 * HGT), (s, -0.04 * HGT), (land + 1, -0.07 * HGT), (land + 6, -0.02 * HGT), (rec, 0)]
    hy = [(0, 0), (w, side * R(12)), (s, -side * R(18)), (land + 4, -side * R(8)), (rec, 0)]   # Kopf in den Hieb
    hp = [(0, 0), (w, R(8)), (s, -R(10)), (land + 4, -R(4)), (rec, 0)]                       # + = Kopf hoch
    jw = [(0, 0), (w - 3, 4), (s - 1, P["jaw_open_deg"]), (land + 2, P["jaw_open_deg"] * 0.7), (land + 8, 0), (N, 0)]

    def pose(f):
        body(dx=keys(f, dx), dy=keys(f, lean), dz=keys(f, dz), pitch=keys(f, pitch), roll=keys(f, roll) * 0.5)
        tw, ro = keys(f, twist), keys(f, roll)
        trunk((0, -tw * 0.3, 0), (keys(f - 1, pitch) * 0.3, tw, ro * 0.5))
        K.set_foot(leg, Vector((keys(f, px), keys(f, py), keys(f, pz))), keys(f, curl))
        look_chain(lambda x: keys(x, hy), lambda x: keys(x, hp), f, 1.0)
        jaw(keys(f, jw))
        bend(TAIL, LEFT, [keys(f - 1 - i, pitch) * 0.5 for i in range(4)])
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": [l for l in LEGS if l != leg],
            "events": [{"frame": h, "event": "hit"}]}


def clip_attack2(P):
    """Aufrichten + Doppelpranken-Slam: kurz ducken (Schwung holen) → um die Hüfte aufrichten, Hüfte setzt sich nach
    hinten/unten auf die Hinterbeine, Rücken streckt sich, Pranken erhoben → oben halten, Brüllen → Körper fällt nach
    vorn, beide Pranken schlagen vor dem Körper auf (hit) → Aufprall federt durch Rumpf, Hals und Kopf → zurück."""
    N = P["frames"]
    c0, r1, h1, s1, hit = P["crouch_end"], P["rise_end"], P["hold_end"], P["slam_end"], P["hit_frame"]
    rec = N - 4
    top, sp = R(P["rear_deg"]), R(P["spine_rear_deg"])
    pitch = [(0, 0), (c0, -R(4)), (r1, top), (h1, top + R(3)), (s1 - 2, top * 0.35), (s1, R(P["slam_pitch_deg"])),
             (s1 + 4, R(P["slam_pitch_deg"]) * 0.6), (s1 + 10, -R(2)), (rec, 0)]
    spine_p = [(0, 0), (c0, -R(3)), (r1, sp), (h1, sp * 1.1), (s1 - 1, -sp * 0.2), (s1 + 3, -sp * 0.5),
               (s1 + 10, 0), (rec, 0)]                     # + = Brust höher als das Becken (Rücken streckt sich)
    sit = [(0, 0), (c0, 0.3), (r1, 1.0), (h1, 1.0), (s1, 0.1), (rec, 0)]
    lunge = [(0, 0), (c0, -0.01 * SIZE), (h1, -0.01 * SIZE), (s1, P["slam_lunge"] * SIZE),
             (s1 + 8, P["slam_lunge"] * SIZE * 0.8), (rec - 6, P["slam_lunge"] * SIZE * 0.3), (rec, 0)]
    dz = [(0, 0), (c0, -0.05 * HGT), (r1, 0), (s1, -0.02 * HGT), (s1 + 2, -P["impact_crouch"] * HGT),
          (s1 + 7, -0.02 * HGT), (s1 + 11, -0.04 * HGT), (rec, 0)]
    # Pranken folgen der Brust bis kurz vor dem Aufprall (fallen mit dem Körper), erst die letzten 2 Frames zum
    # Aufschlagpunkt – sonst läge der Weg dorthin außer Reichweite (Bein überstreckt → Rumpf sackt ab)
    lift = [(0, 0), (c0 + 1, 0), (c0 + 6, 1), (s1 - 1, 1), (s1, 0), (N, 0)]
    raise_ = [(0, 0), (c0 + 4, 0.2), (r1, 1), (h1, 1.1), (s1 - 3, 0.3), (s1 - 1, 0), (N, 0)]
    slam_w = [(0, 0), (s1 - 2, 0), (s1, 1), (rec - 8, 1), (rec, 0)]
    step_up = [(0, 0), (rec - 8, 0), (rec - 5, 1), (rec - 2, 0.2), (rec, 0)]
    # + = runter relativ zur Brust: beim Aufrichten gleicht der Hals ~2/3 der Neigung aus (Kopf schaut nach vorn, leicht
    # hoch zum Brüllen), beim Aufprall schlägt der Kopf nach unten durch und federt zurück
    neck = [(0, 0), (c0, -R(4)), (r1, R(18)), (h1, R(16)), (s1, R(4)), (s1 + 3, R(20)), (s1 + 8, R(2)), (rec, 0)]
    head = [(0, 0), (c0, -R(4)), (r1, R(14)), (h1, R(8)), (s1, R(6)), (s1 + 4, R(12)), (s1 + 9, -R(2)), (rec, 0)]
    jw = [(0, 0), (r1 - 4, 6), (r1, P["jaw_open_deg"]), (h1, P["jaw_open_deg"]), (s1, 10), (s1 + 3, 22),
          (s1 + 10, 0), (N, 0)]
    reach = P["slam_reach"] * SIZE

    def pose(f):
        p, sw = keys(f, pitch), keys(f, sit)
        rear_body(p, Vector((-P["sit_back"] * SIZE * sw, 0, -P["sit_down"] * HGT * sw)),
                  dx=keys(f, lunge), dz=keys(f, dz))
        s_ = keys(f, spine_p)
        bend(SPINE, LEFT, [-s_ * 0.2, -s_ * 0.4, -s_ * 0.4])
        nk = [keys(f - 1, neck), keys(f, neck)]                     # + = Hals runter (Nachfedern 1 Frame später)
        bend(NECK, LEFT, [nk[0] / 2, nk[1] / 2, keys(f, head)])
        jaw(keys(f, jw))
        bend(TAIL, LEFT, [-p * 0.05] * 4)                         # Stummel hebt sich leicht mit
        T = chest_xform()
        lw, rw, gw, su = keys(f, lift), keys(f, raise_), keys(f, slam_w), keys(f, step_up)
        for leg in ("FL", "FR"):
            rest = K.REST[leg]["ball"]
            carried = T @ rest + Vector((-0.04 * SIZE * rw, 0, P["paw_raise"] * HGT * rw))   # hoch, Ellbogen gebeugt
            ground = rest + Vector((reach, 0, 0))
            tgt = rest.lerp(carried, lw)
            tgt = tgt.lerp(ground + Vector((0, 0, 0.12 * HGT * su)), gw) if gw > 0 else tgt
            # Pranke dreht mit dem aufgerichteten Unterarm mit (−p) und hängt im Handgelenk paw_curl_deg nach unten
            # (vorher fester Winkel zur Waagerechten → Handgelenk ~110° abgeknickt, Krallen gedehnt, Lücke 1,7 cm)
            foot(leg, tgt, (R(P.get("paw_curl_deg", 45)) - p) * lw * (1 - gw))
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": ["BL", "BR"],
            "events": [{"frame": hit, "event": "hit"}]}


def clip_hit(P):
    """Treffer: Stoß zurück, Rumpf rollt weg, Kopf schlägt verzögert zur Seite, gedämpftes Nachfedern (schwer)."""
    N = P["frames"]
    j, ro, hd = P["jolt"] * SIZE, R(P["roll_deg"]), R(P["head_deg"])
    e = N - 4
    dx = [(0, 0), (2, -j), (5, -j * 0.55), (8, j * 0.12), (10, -j * 0.04), (e, 0)]
    dz = [(0, 0), (3, -0.05 * HGT), (8, 0.01 * HGT), (e, 0)]
    roll = [(0, 0), (2, ro), (5, -ro * 0.35), (8, ro * 0.12), (e, 0)]
    head = [(0, 0), (3, hd), (6, -hd * 0.35), (9, hd * 0.12), (e, 0)]
    hp = [(0, 0), (3, R(10)), (6, -R(4)), (e, 0)]

    def pose(f):
        body(dx=keys(f, dx), dz=keys(f, dz), roll=keys(f, roll))
        trunk((0, 0, -keys(f - 1, roll) * 0.3), (0, keys(f - 1, head) * 0.15, keys(f - 1, roll) * 0.3))
        bend(NECK, UP, [keys(f - 2, head) * 0.3, keys(f - 1, head) * 0.3, keys(f, head) * 0.4])
        bend(NECK, LEFT, [-keys(f - 1, hp) / 2, -keys(f, hp) / 2, 0])
        jaw(10 * keys(f, [(0, 0), (3, 1), (8, 0), (N, 0)]))
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_death(P):
    """PLATZHALTER (Nutzerregel „Death-Clips nicht anfassen“): Kopie des Hirsch-Tods (zur Seite kippen)."""
    N, c0, c1 = P["frames"], P["collapse_start"], P["collapse_end"]
    side = P["side"]
    piv = (K.REST["F" + ("R" if side > 0 else "L")]["ball"] + K.REST["B" + ("R" if side > 0 else "L")]["ball"]) / 2

    def raw(f):
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        ang = side * R(88) * k
        q = Quaternion(FWD, ang)
        loc = (Vector(piv) - H0) - q @ (Vector(piv) - H0)
        rot("Root", FWD, ang)
        K.move("Root", loc)
        for leg in LEGS:
            ik_off(leg, min(1.0, k * 1.6))
            sgn = 1 if leg[0] == "F" else -1
            rot(f"Leg_{leg}_1", LEFT, sgn * R(P["legs_limp_deg"]) * k)
            rot(f"Leg_{leg}_2", LEFT, -sgn * R(P["legs_limp_deg"]) * k)
        neck_head(pitch=-R(10) * k - R(6) * jolt, yaw=0)
        jaw(14 * k)
        tail(0, 0, 1, -20 * k)
        return k

    K.reset()
    raw(N)
    bpy.context.view_layer.update()
    drop = K.mesh_min_z() - K.GROUND

    def pose(f):
        k = raw(f)
        K.move("Root", Vector((0, 0, -drop * k)))
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "max_stretch": P.get("max_stretch"),
            "events": [{"frame": N, "event": "dead"}]}


# ---------------------------------------------------------------- eigene Prüfungen (nur Info, im clips_report.json)
def yaw_of(bone):
    m = K.PB[bone].matrix
    v = m.to_3x3() @ Vector((0, 1, 0))                       # Knochen-Y = Längsachse
    return math.degrees(math.atan2(v.y, v.x))


def turn_check(spec, expect):
    """Drehrichtung gemessen statt angenommen: Standfüße wandern relativ zum Körper im Uhrzeigersinn → Körper dreht
    links (+). Dazu mittleres Gieren von Kopf, Brust und Becken (Körper biegt sich in die Kurve, Kopf führt)."""
    N = spec["N"]
    rot_sum, cnt, yaws = 0.0, 0, {b: 0.0 for b in ("Head", "Neck_2", "Chest", "Hips")}
    prev = {}
    rest_yaw = {b: math.degrees(math.atan2((K.DB[b].matrix_local.to_3x3() @ Vector((0, 1, 0))).y,
                                           (K.DB[b].matrix_local.to_3x3() @ Vector((0, 1, 0))).x)) for b in yaws}
    c = K.DB["Root"].head_local
    for f in range(N + 1):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        for leg in LEGS:
            if spec["swing"](leg, f):
                prev.pop(leg, None)
                continue
            p = K.IK[leg].matrix_world.translation - c
            a = math.atan2(p.y, p.x)
            if leg in prev:
                rot_sum += (a - prev[leg] + math.pi) % TAU - math.pi
                cnt += 1
            prev[leg] = a
        if f < N:
            for b in yaws:
                yaws[b] += ((yaw_of(b) - rest_yaw[b] + 180) % 360 - 180) / N
    body_deg = -math.degrees(rot_sum) / max(1, cnt) * N * (spec["duty"])       # Drehung pro Zyklus (Standanteil)
    ok = (body_deg > 0) == (expect > 0) and (yaws["Head"] > 0) == (expect > 0) and \
        abs(yaws["Head"]) > abs(yaws["Chest"]) > 0 and (yaws["Chest"] > 0) == (expect > 0)
    return {"body_turn_deg_per_cycle": round(body_deg, 1), "mean_yaw_deg": {k: round(v, 1) for k, v in yaws.items()},
            "turn_dir_ok": ok}


def pose_stats(spec, bones=("Chest", "Head")):
    """Max. Neigung (Brust hoch +) und Höhe der Vorderpranken – zeigt, dass der GANZE Körper arbeitet."""
    out = {"chest_pitch_max_deg": -1e9, "chest_pitch_min_deg": 1e9, "front_paw_max_up_m": 0.0, "chest_rise_max_m": 0.0}
    c0 = K.DB["Chest"].head_local
    for f in range(spec["N"] + 1):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        v = K.PB["Chest"].matrix.to_3x3() @ Vector((0, 1, 0))
        v0 = K.DB["Chest"].matrix_local.to_3x3() @ Vector((0, 1, 0))
        pch = math.degrees(math.atan2(v.z, math.hypot(v.x, v.y)) - math.atan2(v0.z, math.hypot(v0.x, v0.y)))
        out["chest_pitch_max_deg"] = max(out["chest_pitch_max_deg"], round(pch, 1))
        out["chest_pitch_min_deg"] = min(out["chest_pitch_min_deg"], round(pch, 1))
        out["chest_rise_max_m"] = max(out["chest_rise_max_m"], round(K.PB["Chest"].head.z - c0.z, 3))
        for leg in ("FL", "FR"):
            out["front_paw_max_up_m"] = max(out["front_paw_max_up_m"],
                                            round(K.IK[leg].matrix_world.translation.z - K.REST[leg]["ball"].z, 3))
    return out


turn = R(ST["turn"]["turn_deg"])
IK_STIFF = ST.get("ik", {}).get("stiffness", {})


def stiff(spec):
    spec["ik_stiff"] = IK_STIFF
    spec["foot_ground"] = True                                  # kein Fuß unter dem Boden (Kit: feet_on_ground)
    return spec


CLIPS = {
    "Walk": stiff(locomotion(ST["walk"])),
    "Run": stiff(locomotion(ST["run"])),
    "TurnLeft": stiff(locomotion(ST["turn"], turn=turn)),
    "TurnRight": stiff(locomotion(ST["turn"], turn=-turn)),
    "Idle": stiff(clip_idle(ST["idle"])),
    "Ready": stiff(clip_ready(ST["ready"])),
    "Attack1": stiff(clip_attack1(ST["attack1"])),
    "Attack2": stiff(clip_attack2(ST["attack2"])),
    "Hit": stiff(clip_hit(ST["hit"])),
    "Death": clip_death(ST["death"]),
}
if __import__("os").environ.get("BEAR_DEBUG"):             # Diagnose: Reichweite je Bein und Frame, dann Ende
    spec = CLIPS[__import__("os").environ["BEAR_DEBUG"]]
    for f in range(spec["N"] + 1):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        r = {l: round((K.arm.matrix_world.inverted() @ K.IK[l].matrix_world.translation - K.PB[f"Leg_{l}_1"].head).length
                      / K.chain_len(l), 3) for l in LEGS}
        e = {l: round((K.ball(l) - K.IK[l].matrix_world.translation).length, 3) for l in LEGS}
        need = K.reach_fix()
        print("DBG", f, "ratio", r, "err", e, "need", round(need, 3))
    raise SystemExit
EXTRA = {"TurnLeft": turn_check(CLIPS["TurnLeft"], 1), "TurnRight": turn_check(CLIPS["TurnRight"], -1)}
for c in ("Attack1", "Attack2", "Ready"):
    EXTRA[c] = pose_stats(CLIPS[c])
for c, v in EXTRA.items():
    print("BEAR_CHECK", c, json.dumps(v, ensure_ascii=False))
K.reset()
K.bake(CLIPS)
rep_p = K.OUT / "clips_report.json"
rep = json.loads(rep_p.read_text(encoding="utf-8"))
for c, v in EXTRA.items():
    rep["clips"][f"{K.PREFIX}_{c}"].update(v)
rep["turn_dir_ok"] = all(EXTRA[c]["turn_dir_ok"] for c in ("TurnLeft", "TurnRight"))
rep_p.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
