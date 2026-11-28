"""Bewegungsmuster quadruped/gorilla (Gorilla, erstes Modell Frost Colossus):
Knöchelgang (Diagonal-Sequenz, Körper stelzt über die gestreckten Arme, Schultern + Eisplatten rollen, Fäuste schwingen außen
herum), Sturm-Galopp, Drehen (Brust dreht voraus, Kopf führt), Idle, Drohen (Brust halb hoch, Kopf schüttelt, Faust schlägt auf
den Boden), Taunt = Aufrichten + Brusttrommeln (Arme weit seitlich), Attack1 = Doppelfaust-Hammer, Attack2 = Sturm-Hieb mit
Root Motion, Treffer, Tod (Platzhalter). Nutzer-Entscheidungen 2026-11-23: Schwanz bleibt, Taunt eigener Clip, Attack2 Sturm-Hieb.
Gemeinsame Bausteine: ../quadruped_kit.py (nur gelesen). Eigener Code – andere Muster benutzen diese Datei NICHT (Kapselung,
motions/README.md). Teile aus bear_clips.py kopiert (nicht importiert). Arme über Kopf / vor der Brust: IK aus (die IK hat
kein Pol-Ziel, der Ellbogen würde umklappen) und Arm per FK in Welt-Richtungen gedreht (aim()), danach zurück in die IK.

& "D:\\Blender\\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/gorilla/gorilla_clips.py -- <ausgabe> [<creature.toml>]
"""
import json
import math
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import quadruped_kit as K  # noqa: E402

K.init(HERE)
import bpy  # noqa: E402
from mathutils import Matrix, Quaternion, Vector  # noqa: E402
from quadruped_kit import (FWD, LEFT, UP, LEGS, R, NECK, SPINE, TAIL, body, bend, bump, ease, follow,  # noqa: E402
                           ik_off, jaw, keys, neck_head, phase, rot, tail)

ST, SIZE, HGT = K.ST, K.SIZE, K.HGT
TAU = 2 * math.pi
GIRDLE = (K.REST["FL"]["ball"].x - K.REST["BL"]["ball"].x) or 0.4 * SIZE
HIP = (K.DB["Leg_BL_1"].head_local + K.DB["Leg_BR_1"].head_local) / 2     # Drehpunkt beim Aufrichten
H0 = K.DB["Root"].head_local.copy()
NOSE0 = K.DB["Head"].tail_local.copy()
Y_MID = H0.y


def trunk(pel=(0.0, 0.0, 0.0), sh=(0.0, 0.0, 0.0)):
    """Becken- und Schultergürtel getrennt drehen (pitch + = vorne hoch, yaw + = links, roll + = linke Seite hoch), rad."""
    for axis, a, b, sgn in ((LEFT, pel[0], sh[0], -1), (UP, pel[1], sh[1], 1), (FWD, pel[2], sh[2], 1)):
        bend(SPINE, axis, (sgn * a, sgn * (b - a) / 2, sgn * (b - a) / 2))


def cyc(t, at, cycles=1):
    return math.cos(TAU * cycles * (t - at))


def foot(leg, world_target, curl=0.0):
    """Fuß-/Faust-Ziel als absolute Position (Armature-Raum)."""
    K.set_foot(leg, world_target - K.REST[leg]["ball"], curl)


def nudge(leg, v):
    """IK-Ziel zusätzlich verschieben (Armature-Raum)."""
    e = K.IK[leg]
    m = e.matrix_world.copy()
    m.translation = m.translation + K.arm.matrix_world.to_3x3() @ v
    e.matrix_world = m


def rear_body(pitch, piv_shift=Vector(), dx=0.0, dz=0.0, roll=0.0, yaw=0.0):
    """Ganzer Körper kippt um die Hüfte: pitch + = Brust hoch. piv_shift = Hüfte verschiebt sich (auf die Hinterbeine setzen)."""
    q = Quaternion(UP, yaw) @ Quaternion(LEFT, -pitch)
    loc = (HIP + piv_shift - H0) - q @ (HIP - H0) + Vector((dx, 0, dz))
    if yaw:
        rot("Root", UP, yaw)
    rot("Root", LEFT, -pitch)
    if roll:
        rot("Root", FWD, roll)
    K.move("Root", loc)


def chest_xform():
    bpy.context.view_layer.update()
    return K.PB["Chest"].matrix @ K.DB["Chest"].matrix_local.inverted()


def aim(bone, w):
    """FK: Knochen so drehen, dass seine Längsachse in Richtung w (Armature-Raum) zeigt – kleinste Drehung."""
    bpy.context.view_layer.update()
    pb = K.PB[bone]
    M = pb.matrix.to_quaternion()
    q = (M @ Vector((0, 1, 0))).rotation_difference(w.normalized())
    A = M @ pb.rotation_quaternion.inverted()
    pb.rotation_quaternion = A.inverted() @ q @ A @ pb.rotation_quaternion


def arm_fk(leg, upper, fore, k, curl=0.0):
    """Vorderarm in Richtungen statt Ziel: Oberarm (Leg_1) und Unterarm (Leg_2) zeigen nach upper/fore, die Faust (Leg_3)
    setzt den Unterarm fort und knickt um curl (rad) ein. Die IK bleibt an: ihr Ziel wird zwischen dem vorher gesetzten Ziel
    und dieser FK-Faust gemischt (k), und die Ausgangspose der Kette auf die FK-Pose gedreht – so knickt der Ellbogen (IK ohne
    Pol-Ziel) wie in der FK-Pose und die Fausthöhe bleibt beim Absenken des Rumpfs (reach_fix) stimmig."""
    if k <= 1e-4:
        return
    tgt0 = K.arm.matrix_world.inverted() @ K.IK[leg].matrix_world
    ik_off(leg, 1.0)
    bones = [f"Leg_{leg}_{i}" for i in (1, 2, 3)]
    aim(bones[0], upper)
    aim(bones[1], fore)
    aim(bones[2], fore)
    if curl:
        rot(bones[2], LEFT, curl)
    bpy.context.view_layer.update()
    fk_ball = K.arm.matrix_world.inverted() @ K.ball(leg)
    fk_mat = K.PB[f"Leg_{leg}_4"].matrix.copy()
    for b in bones:                                     # Ausgangspose der IK = Mischung Ruhe → FK
        K.PB[b].rotation_quaternion = Quaternion().slerp(K.PB[b].rotation_quaternion, k)
    q = tgt0.to_quaternion().slerp(fk_mat.to_quaternion(), k)
    K.IK[leg].matrix_world = K.arm.matrix_world @ (Matrix.Translation(tgt0.translation.lerp(fk_ball, k)) @
                                                   q.to_matrix().to_4x4())
    ik_off(leg, 0.0)


def blend_dir(pairs):
    """[(Gewicht, Vector), …] → normierte Mischrichtung."""
    v = Vector()
    for w, d in pairs:
        v += w * d.normalized()
    return v.normalized() if v.length > 1e-6 else Vector((0, 0, -1))


def tail_lift(p, k):
    """Schwanz gegen das Aufrichten anheben (p = Rumpf-Neigung rad, + = Brust hoch; k = Anteil) – sonst rammt er in den Boden."""
    bend(TAIL, LEFT, [p * k * 0.55, p * k * 0.25, p * k * 0.12, p * k * 0.08])


# ---------------------------------------------------------------- Fortbewegung
def locomotion(P, turn=0.0):
    N = P["cycle_frames"]
    off = P["order"]
    d = P["duty"]
    td = {l: (-off[l]) % 1.0 for l in LEGS}
    mid_swing = {l: (td[l] + d + (1 - d) / 2) % 1.0 for l in LEGS}
    mid_stance = {l: (td[l] + d / 2) % 1.0 for l in LEGS}
    gallop = P.get("body") == "gallop"
    lag = P.get("neck_lag", 0.05)
    sgn = (turn > 0) - (turn < 0)
    arm_out = P.get("arm_out", 0.0) * SIZE

    def girdles(t):
        if gallop:
            flex = R(P["spine_flex_deg"]) * cyc(t, P["flex_peak"])
            pitch = R(P["pitch_deg"]) * cyc(t, P["pitch_peak"])
            dz = -P["bob"] * HGT * cyc(t, P["bob_low"], 2)
            roll = R(P.get("roll_deg", 0)) * cyc(t, mid_stance["FL"])
            yaw = R(P.get("spine_side_deg", 0)) * cyc(t, mid_stance["FL"])
            return (dz, 0.0, pitch, roll * 0.4), (flex / 2, -yaw / 2, 0.0), (-flex * 0.15, yaw / 2, roll)
        # Knöchelgang: schwingt ein Arm, sinkt diese Schulter ab, der Schultergürtel giert + rollt (Schulterplatten pendeln);
        # Rumpf schwankt zur Standfaust; Brust am höchsten mitten im Stand der Arme (Körper stelzt über den Arm).
        hb, fb = mid_swing["BL"], mid_swing["FL"]
        yh, yf = R(P.get("hip_yaw_deg", 0)), R(P.get("shoulder_yaw_deg", 0))
        rh, rf = R(P.get("hip_roll_deg", 0)), R(P.get("shoulder_roll_deg", 0))
        B = P.get("bob", 0) * HGT
        zh, zf = 0.5 * B * cyc(t, mid_stance["BL"], 2), B * cyc(t, mid_stance["FL"], 2)
        dy = -P.get("sway", 0) * SIZE * (0.35 * cyc(t, hb) + 0.65 * cyc(t, fb))
        return ((zh + zf) / 2, dy, math.atan2(zf - zh, GIRDLE), 0.0), \
            (0.0, -yh * cyc(t, hb), -rh * cyc(t, hb)), (0.0, -yf * cyc(t, fb), -rf * cyc(t, fb))

    def chest_pitch(t):
        rt, _, sh = girdles(t)
        return -(rt[2] + sh[0])

    def chest_yaw(t):
        return girdles(t)[2][1] + (sgn * R(P.get("turn_bend_deg", 0)) / 2 if turn else 0.0)

    def pel_yaw(t):
        return girdles(t)[1][1]

    def pose(f):
        t = (f % N) / N
        K.gait(t, P, off, turn=-turn)       # gait dreht bei turn > 0 nach RECHTS → −turn (Konvention wolf/deer/bear)
        if arm_out:                         # Fäuste schwingen außen herum (Bogen nach außen mitten im Schwung)
            for leg in ("FL", "FR"):
                sw, s = phase(t, off[leg], d)
                if sw:
                    nudge(leg, Vector((0, (1 if leg[1] == "L" else -1) * arm_out * bump(s, 0.5), 0)))
        rt, pel, sh = girdles(t)
        body(dz=rt[0], dy=rt[1], pitch=rt[2], roll=rt[3])
        if turn:
            b = sgn * R(P.get("turn_bend_deg", 0)) / 2
            pel, sh = (pel[0], pel[1] - b, pel[2]), (sh[0], sh[1] + b, sh[2])
        trunk(pel, sh)
        g = P.get("head_gain", 0.5)
        np_ = follow(chest_pitch, t, 3, lag, g)
        ny = follow(chest_yaw, t, 3, lag, g)
        nl = R(P.get("neck_lift_deg", 0))
        nod = R(P.get("head_bob_deg", 0)) * cyc(t, mid_stance["FL"], 2)
        bend(NECK, LEFT, [np_[0] - nl / 2, np_[1] - nl / 2, np_[2] + nl - nod])
        sw_ = R(P.get("head_swing_deg", 0)) * cyc(t, mid_stance["FL"] + P.get("head_swing_lag", 0.1))
        ny = [ny[0] + sw_ * 0.2, ny[1] + sw_ * 0.35, ny[2] + sw_ * 0.45]
        if turn:
            hd = sgn * R(P.get("turn_head_deg", 0))
            ny = [ny[0] + hd * 0.3, ny[1] + hd * 0.3, ny[2] + hd * 0.4]
        bend(NECK, UP, ny)
        # Schwerer Schwanz: schwingt verzögert gegen das Becken (Spitze später), beim Drehen schleppt er nach
        ta = R(P.get("tail_deg", 0))
        yh_ = max(1e-6, R(P.get("hip_yaw_deg", 4)))
        tw = [-pel_yaw(t - 0.05 * (i + 1)) / yh_ * ta * (0.35 + 0.2 * i) for i in range(4)] if not gallop else \
            [ta * (0.3 + 0.2 * i) * math.sin(TAU * t - i * 0.8) for i in range(4)]
        if turn:
            tw = [w - sgn * R(4) * (0.4 + 0.2 * i) for i, w in enumerate(tw)]
        bend(TAIL, UP, tw)
        bend(TAIL, LEFT, [R(P.get("tail_lift_deg", 0)) / 4] * 4)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn,
            "max_stretch": P.get("max_stretch"), "reach_smooth": P.get("reach_smooth"), "reach_flat": P.get("reach_flat", 0),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], d)[0]}


# ---------------------------------------------------------------- Stand-Clips
def look_chain(yaw_fn, pitch_fn, x, lag):
    """Kopf führt, Hals folgt (aus bear_clips kopiert). yaw + = links, pitch + = Kopf hoch."""
    for axis, fn, sg in ((UP, yaw_fn, 1), (LEFT, pitch_fn, -1)):
        w = [0.3 * fn(x - 2 * lag), 0.6 * fn(x - lag), fn(x)]
        bend(NECK, axis, [sg * w[0], sg * (w[1] - w[0]), sg * (w[2] - w[1])])


def clip_idle(P):
    """Schwer atmen, Gewicht verlagern, Kopf schaut rechts/links (Kopf führt), eine Faust hebt sich kurz und setzt schwer auf."""
    N = P["frames"]
    leg = P.get("fist_leg", "FL")
    side = 1 if leg[1] == "L" else -1

    def pose(f):
        t = f / N
        br = math.sin(TAU * 4 * t)
        shift = math.sin(TAU * t)
        up = keys(t, [(0, 0), (0.55, 0), (0.62, 1), (0.66, 0.9), (0.7, 0), (1, 0)])
        body(dz=0.006 * HGT * br, dy=0.012 * SIZE * shift - side * 0.01 * SIZE * up, roll=R(1.5) * shift - side * R(2) * up)
        trunk((0, 0, -R(1.2) * shift), (R(P["breathe_deg"]) * br, side * R(3) * up, R(1.0) * shift))
        K.set_foot(leg, Vector((0.02 * SIZE * up, 0, P["fist_lift"] * HGT * up)), R(10) * up)
        look = [(0, 0), (0.25, 0), (0.33, 0.9), (0.45, 0.9), (0.55, 0), (0.72, -0.8), (0.86, -0.8), (1, 0)]
        lift = [(0, -0.2), (0.3, 0.1), (0.6, -0.3), (0.7, -0.1), (1, -0.2)]
        look_chain(lambda x: R(P["look_deg"]) * keys(x, look, loop=True), lambda x: R(10) * keys(x, lift, loop=True),
                   t, 0.03)
        jaw(3.0 * max(0.0, br))
        bend(TAIL, UP, [R(3) * math.sin(TAU * t - 0.6 * i) * (0.4 + 0.2 * i) for i in range(4)])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach_smooth": P.get("reach_smooth"),
            "planted": [l for l in LEGS if l != leg], "events": [{"frame": round(0.7 * N), "event": "slam"}]}


def clip_ready(P):
    """Drohen: Gewicht zurück, Brust hebt sich um die Hüfte, Kopf schüttelt hoch-runter, Maul auf (Brüllen), Gewicht pendelt
    schwer links/rechts, eine Faust hebt sich hoch und schlägt weiter vorn auf den Boden (slam). Schleife."""
    N = P["frames"]
    slap = P.get("slap_leg", "FR")
    side = 1 if slap[1] == "L" else -1

    def pose(f):
        t = f / N
        rock = math.sin(TAU * t)
        up = keys(t, [(0, 0), (0.45, 0), (0.6, 1), (0.63, 1), (0.68, 0), (1, 0)])
        fwd = keys(t, [(0, 0), (0.5, 0), (0.6, 1), (0.85, 1), (0.95, 0), (1, 0)])
        stepback = keys(t, [(0, 0), (0.82, 0), (0.88, 1), (0.95, 0), (1, 0)])
        rear = R(P["rear_deg"]) * (0.6 + 0.4 * math.sin(TAU * t - 1.2)) + R(5) * up
        rear_body(rear, Vector((-0.02 * SIZE, 0, -P["crouch"] * HGT)), dz=0.0,
                  roll=R(3) * rock - side * R(4) * up)
        K.move("Root", Vector((0, P["sway"] * SIZE * rock - side * 0.015 * SIZE * up, 0)))
        trunk((0, -R(3) * rock, 0), (0, R(5) * rock + side * R(6) * up, R(2) * rock))
        tgt = Vector((P["slap_reach"] * SIZE * fwd, side * 0.02 * SIZE * up, P["slap_lift"] * HGT * up
                      + 0.06 * HGT * stepback))
        K.set_foot(slap, tgt, R(25) * up)
        shake = R(P["shake_deg"]) * math.sin(TAU * 4 * t) * keys(t, [(0, 0.3), (0.1, 1), (0.4, 1), (0.5, 0.2), (0.9, 0.3),
                                                                    (1, 0.3)])
        roar = keys(t, [(0, 0), (0.12, 0), (0.2, 1), (0.42, 1), (0.5, 0.3), (0.62, 1), (0.7, 0), (1, 0)])
        bend(NECK, LEFT, [-R(4) - rear * 0.3, -rear * 0.3 - shake * 0.4, -shake * 0.6 - R(10) * roar])
        bend(NECK, UP, [R(4) * rock, R(5) * rock, R(6) * rock])
        jaw(P["roar_deg"] * roar)
        tail_lift(rear, 0.6)
        bend(TAIL, UP, [-R(5) * rock * (0.4 + 0.2 * i) for i in range(4)])
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": [l for l in LEGS if l != slap],
            "events": [{"frame": round(0.68 * N), "event": "slam"}]}


# Arm-Richtungen (Armature-Raum, s = +1 links / −1 rechts) für die aufgerichteten Posen
def DIRS(s):
    return {
        "hang": (Vector((0.1, 0.4 * s, -0.9)), Vector((0.8, 0.1 * s, -0.5))),         # hängt, Ellbogen gebeugt (Faust vorn)
        "open": (Vector((0.12, 1.0 * s, 0.05)), Vector((0.05, 0.55 * s, 1.0))),       # weit seitlich, Unterarm hoch
        "beat": (Vector((0.8, 0.6 * s, -0.25)), Vector((0.3, -1.0 * s, 0.05))),       # Ellbogen außen, Faust vor die Brust
        "over": (Vector((0.25, 0.3 * s, 1.0)), Vector((0.12, -0.3 * s, 1.0))),        # Fäuste über dem Kopf
        "swing": (Vector((1.0, 0.25 * s, 0.25)), Vector((1.0, -0.2 * s, -0.2))),      # Hammer: Arme nach vorn
    }


def clip_taunt(P):
    """Brusttrommeln: ducken → um die Hüfte ganz aufrichten (Hüfte setzt sich zurück/unten, Schwanz hebt sich gegen),
    Arme weit seitlich auf, Brüllen → Hände schlagen abwechselnd vor die Brust (Ellbogen außen), zwischen den Schlägen
    weit auf → Arme weit auf, Kopf zurück → nach vorn auf die Fäuste fallen → Ruhe."""
    N = P["frames"]
    c0, r1, o1, d1, s1, dr = (P[k] for k in ("crouch_end", "rise_end", "open_end", "drum_end", "show_end", "drop_end"))
    top, sp = R(P["rear_deg"]), R(P["spine_rear_deg"])
    pitch = [(0, 0), (c0, -R(4)), (r1, top), (d1, top + R(2)), (s1, top + R(4)), (dr - 2, top * 0.25), (dr, -R(4)),
             (dr + 4, -R(1.5)), (N - 2, 0), (N, 0)]
    spine_p = [(0, 0), (c0, -R(3)), (r1, sp), (d1, sp), (s1, sp * 1.15), (dr - 1, -sp * 0.15), (dr + 3, -sp * 0.25),
               (N - 2, 0), (N, 0)]
    sit = [(0, 0), (c0, 0.3), (r1, 1.0), (s1, 1.0), (dr, 0.15), (N - 2, 0), (N, 0)]
    dz = [(0, 0), (c0, -0.05 * HGT), (r1, 0), (s1, 0), (dr, -0.04 * HGT), (dr + 2, -0.09 * HGT), (dr + 6, -0.02 * HGT),
          (N - 2, 0), (N, 0)]
    lift = [(0, 0), (c0 + 1, 0), (c0 + 7, 1), (dr - 1, 1), (dr, 0), (N, 0)]           # Fäuste mit der Brust getragen
    fk = [(0, 0), (r1 - 8, 0), (r1 - 2, 1), (s1 + 1, 1), (dr - 3, 0), (N, 0)]          # Arme frei (FK)
    wopen = [(0, 0), (r1 - 2, 0), (o1, 1), (s1, 1), (s1 + 4, 0), (N, 0)]
    per = (d1 - o1) / P["beats"]
    beat_t = [o1 + (i + 0.5) * per for i in range(P["beats"])]
    beat_leg = ["FR" if i % 2 == 0 else "FL" for i in range(P["beats"])]
    neck = [(0, 0), (c0, -R(4)), (r1, R(26)), (d1, R(22)), (s1, R(34)), (dr - 2, R(6)), (dr + 2, R(16)), (dr + 7, 0),
            (N, 0)]                                    # + = Kopf runter relativ zur Brust (gleicht das Aufrichten aus)
    jw = [(0, 0), (r1 - 3, 4), (r1 + 2, P["jaw_open_deg"]), (o1 + 2, P["jaw_open_deg"] * 0.4), (d1, 10),
          (s1 - 3, P["jaw_open_deg"]), (s1 + 2, P["jaw_open_deg"]), (dr, 6), (N, 0)]

    def beat_w(leg, f):
        w = 0.0
        for tb, lg in zip(beat_t, beat_leg):
            if lg == leg:
                w = max(w, bump((f - tb + 0.45 * per * 1.6) / (per * 1.6), 0.45))
        return w

    def pose(f):
        p, sw = keys(f, pitch), keys(f, sit)
        rear_body(p, Vector((-P["sit_back"] * SIZE * sw, 0, -P["sit_down"] * HGT * sw)), dz=keys(f, dz))
        s_ = keys(f, spine_p)
        bend(SPINE, LEFT, [-s_ * 0.2, -s_ * 0.4, -s_ * 0.4])
        drum = sum(beat_w(l, f) * (1 if l == "FL" else -1) for l in ("FL", "FR"))
        trunk((0, 0, 0), (0, R(5) * drum, R(4) * drum))           # Schultergürtel dreht in jeden Schlag
        nk = keys(f, neck)
        bend(NECK, LEFT, [nk * 0.4, nk * 0.3, nk * 0.3 - R(8) * keys(f, jw) / max(1, P["jaw_open_deg"])])
        bend(NECK, UP, [0, R(4) * drum, R(6) * drum])
        jaw(keys(f, jw))
        tail_lift(p + s_, P["tail_lift"])
        bend(TAIL, UP, [R(3) * drum * (0.3 + 0.2 * i) for i in range(4)])
        T = chest_xform()
        lw, kf, wo = keys(f, lift), keys(f, fk), keys(f, wopen)
        for leg in ("FL", "FR"):
            s = 1 if leg[1] == "L" else -1
            rest = K.REST[leg]["ball"]
            carried = T @ rest + Vector((0.04 * SIZE * lw, 0, 0.08 * HGT * lw))
            foot(leg, rest.lerp(carried, lw), R(30) * lw)
            D_ = DIRS(s)
            b = beat_w(leg, f)
            up_ = blend_dir([((1 - wo), D_["hang"][0]), (wo * (1 - b), D_["open"][0]), (wo * b, D_["beat"][0])])
            fo_ = blend_dir([((1 - wo), D_["hang"][1]), (wo * (1 - b), D_["open"][1]), (wo * b, D_["beat"][1])])
            arm_fk(leg, up_, fo_, kf, R(25) * wo)
    ev = [{"frame": round(tb), "event": "drum", "leg": lg} for tb, lg in zip(beat_t, beat_leg)]
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": ["BL", "BR"],
            "events": ev + [{"frame": dr, "event": "slam"}]}


def clip_attack1(P):
    """Doppelfaust-Hammer: ducken → hoch aufrichten, beide Fäuste über den Kopf, Brust bläht sich, Brüllen (halten) →
    Körper fällt nach vorn, Arme schwingen nach vorn-unten, beide Fäuste schlagen weit vor dem Kopf zur Mitte hin auf (hit)
    → Aufprall federt durch Schultern, Hals, Kopf, Schwanz peitscht nach → schweres Zurückstemmen."""
    N = P["frames"]
    c0, r1, h1, s1, hit = P["crouch_end"], P["rise_end"], P["hold_end"], P["slam_end"], P["hit_frame"]
    rec = N - 4
    top, sp = R(P["rear_deg"]), R(P["spine_rear_deg"])
    pitch = [(0, 0), (c0, -R(5)), (r1, top), (h1, top + R(4)), (s1 - 2, top * 0.3), (s1, R(P["slam_pitch_deg"])),
             (s1 + 4, R(P["slam_pitch_deg"]) * 0.6), (s1 + 10, -R(2)), (rec, 0), (N, 0)]
    spine_p = [(0, 0), (c0, -R(4)), (r1, sp), (h1, sp * 1.15), (s1 - 1, -sp * 0.2), (s1 + 3, -sp * 0.5), (s1 + 10, 0),
               (rec, 0), (N, 0)]
    sit = [(0, 0), (c0, 0.3), (r1, 1.0), (h1, 1.0), (s1, 0.1), (rec, 0), (N, 0)]
    lunge = [(0, 0), (c0, -0.015 * SIZE), (h1, -0.02 * SIZE), (s1, P["slam_lunge"] * SIZE),
             (s1 + 8, P["slam_lunge"] * SIZE * 0.85), (rec - 6, P["slam_lunge"] * SIZE * 0.3), (rec, 0), (N, 0)]
    dz = [(0, 0), (c0, -0.06 * HGT), (r1, 0), (s1, -0.03 * HGT), (s1 + 2, -P["impact_crouch"] * HGT),
          (s1 + 7, -0.03 * HGT), (s1 + 11, -0.05 * HGT), (rec, 0), (N, 0)]
    lift = [(0, 0), (c0 + 1, 0), (c0 + 6, 1), (s1 - 1, 1), (s1, 0), (N, 0)]
    fk = [(0, 0), (r1 - 8, 0), (r1 - 3, 1), (s1 - 2, 1), (s1, 0), (N, 0)]
    wover = [(0, 0), (r1 - 4, 0), (r1, 1), (h1, 1), (N, 1)]
    wswing = [(0, 0), (h1, 0), (s1 - 2, 1), (N, 1)]
    slam_w = [(0, 0), (s1 - 2, 0), (s1, 1), (rec - 8, 1), (rec, 0), (N, 0)]
    step_up = [(0, 0), (rec - 8, 0), (rec - 5, 1), (rec - 2, 0.2), (rec, 0), (N, 0)]
    neck = [(0, 0), (c0, -R(4)), (r1, R(22)), (h1, R(30)), (s1, -R(12)), (s1 + 3, R(8)), (s1 + 8, R(2)), (rec, 0),
            (N, 0)]                                    # + = Kopf runter relativ zur Brust; beim Aufprall Kopf zurück
    jw = [(0, 0), (r1 - 4, 6), (r1, P["jaw_open_deg"]), (h1, P["jaw_open_deg"]), (s1, 20), (s1 + 3, 28), (s1 + 10, 0),
          (N, 0)]
    reach, inward = P["slam_reach"] * SIZE, P["slam_inward"] * SIZE

    def pose(f):
        p, sw = keys(f, pitch), keys(f, sit)
        rear_body(p, Vector((-P["sit_back"] * SIZE * sw, 0, -P["sit_down"] * HGT * sw)),
                  dx=keys(f, lunge), dz=keys(f, dz))
        s_ = keys(f, spine_p)
        bend(SPINE, LEFT, [-s_ * 0.2, -s_ * 0.4, -s_ * 0.4])
        nk = [keys(f - 1, neck), keys(f, neck)]
        bend(NECK, LEFT, [nk[0] * 0.4, nk[1] * 0.3, nk[1] * 0.3])
        jaw(keys(f, jw))
        tail_lift(p + s_, P["tail_lift"])
        whip = keys(f, [(0, 0), (s1, 0), (s1 + 2, 1), (s1 + 6, -0.5), (s1 + 10, 0.2), (s1 + 14, 0), (N, 0)])
        bend(TAIL, LEFT, [R(10) * keys(f - i, [(0, 0), (s1, 0), (s1 + 2, 1), (s1 + 6, -0.5), (s1 + 10, 0.2),
                                               (s1 + 14, 0), (N, 0)]) for i in range(4)])
        bend(NECK, UP, [0, 0, R(2) * whip])
        T = chest_xform()
        lw, kf, wo, wsw, gw, su = (keys(f, k) for k in (lift, fk, wover, wswing, slam_w, step_up))
        for leg in ("FL", "FR"):
            s = 1 if leg[1] == "L" else -1
            rest = K.REST[leg]["ball"]
            carried = T @ rest + Vector((0.04 * SIZE * lw, 0, 0.08 * HGT * lw))
            ground = rest + Vector((reach, -s * inward, 0))
            tgt = rest.lerp(carried, lw)
            if gw > 0:
                back = rest + Vector((0, 0, 0.12 * HGT * su))
                tgt = tgt.lerp(ground.lerp(back, keys(f, [(0, 0), (rec - 8, 0), (rec - 2, 1), (N, 1)])), gw)
            foot(leg, tgt, R(30) * lw * (1 - gw))
            D_ = DIRS(s)
            up_ = blend_dir([((1 - wo), D_["hang"][0]), (wo * (1 - wsw), D_["over"][0]), (wo * wsw, D_["swing"][0])])
            fo_ = blend_dir([((1 - wo), D_["hang"][1]), (wo * (1 - wsw), D_["over"][1]), (wo * wsw, D_["swing"][1])])
            arm_fk(leg, up_, fo_, kf, R(20) * wo)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "planted": ["BL", "BR"],
            "events": [{"frame": hit, "event": "hit"}], "fists": ["FL", "FR"], "hit": hit}


def clip_attack2(P):
    """Sturm-Hieb (Root Motion): ducken → 2 schwere Galoppsprünge aufs Ziel → im Vorbeistürmen holt der rechte Arm außen
    hinten aus (Rumpf dreht weg) → Schulter führt, Rumpf verdreht sich zurück, die Faust fegt flach von außen nach
    innen-vorn auf Gegnerhöhe (hit) → Abbremsen auf drei Gliedmaßen → Faust setzt auf → Ruhe um `distance` weiter vorn."""
    N, D = P["frames"], P["distance"] * SIZE
    leg = P.get("leg", "FR")
    side = 1 if leg[1] == "L" else -1
    wu, hit, se, pl = P["windup"], P["hit_frame"], P["strike_end"], P["plant_frame"]
    ov = 0.05 * SIZE
    dx = [(0, 0), (5, -0.03 * SIZE), (13, 0.25 * D), (21, 0.58 * D), (hit, 0.92 * D), (hit + 4, D + ov), (pl + 4, D),
          (N, D)]
    dz = [(0, 0), (5, -0.06 * HGT), (9, 0.02 * HGT), (13, -0.04 * HGT), (17, 0.02 * HGT), (21, -0.04 * HGT),
          (25, 0.0), (hit, -0.05 * HGT), (pl, -0.07 * HGT), (pl + 5, -0.01 * HGT), (N, 0)]
    pa = R(P["pitch_deg"])
    pitch = [(0, 0), (5, -R(4)), (9, pa), (13, -pa), (17, pa), (21, -pa), (wu, R(5)), (hit, -R(5)), (pl, -R(6)),
             (pl + 6, -R(1)), (N, 0)]
    tw = R(P["twist_deg"])
    twist = [(0, 0), (wu - 6, 0), (wu, side * tw), (hit - 3, side * tw * 0.6), (hit, -side * tw * 0.8),
             (se + 3, -side * tw), (pl + 4, -side * tw * 0.3), (N, 0)]   # Schultergürtel (+ = links)
    roll = [(0, 0), (wu - 6, 0), (wu, -side * R(6)), (hit, side * R(5)), (pl, side * R(2)), (N, 0)]
    # Schritt-Plan: (Abheben, Aufsetzen) je Bein; Aufsetzpunkt = Ruhe + Root-Weg mitten im folgenden Stand
    steps = {"BL": [(5, 9), (14, 18), (23, 28)], "BR": [(6, 10), (15, 19), (24, 29)],
             "FL": [(8, 12), (17, 21), (27, 32)], "FR": [(9, 13)]}
    stance_end = {"BL": [14, 23, None], "BR": [15, 24, None], "FL": [17, 27, None], "FR": [21]}

    def plant_x(l, k):
        if stance_end[l][k] is None:
            return D
        a = steps[l][k][1]
        return keys((a + stance_end[l][k]) / 2, dx)

    def feet_pos(l, f):
        x, lift, curl = 0.0, 0.0, 0.0
        prev = 0.0
        for k, (a, b) in enumerate(steps[l]):
            nx = plant_x(l, k)
            if f < a:
                return prev, 0.0, 0.0
            if f <= b:
                u = (f - a) / (b - a)
                return prev + (nx - prev) * ease(u), bump(u, 0.45), bump(u, 0.35)
            prev = nx
            x = nx
        return x, lift, curl

    rest_s = K.REST[leg]["ball"]
    ah = P["swing_ahead"] * SIZE
    y_out = rest_s.y + side * 0.10 * SIZE
    z_g = K.GROUND
    path = {  # Schlagfaust (relativ zum Root-Weg in x): Abheben 21 → außen-hinten-hoch → flacher Bogen nach innen-vorn
        "x": [(21, rest_s.x + plant_x(leg, 0) - keys(21, dx)), (wu, rest_s.x - 0.05 * SIZE), (hit - 3, rest_s.x + 0.04 * SIZE),
              (hit, NOSE0.x + ah), (se, NOSE0.x + ah + 0.02 * SIZE), (se + 3, rest_s.x + 0.18 * SIZE),
              (pl, rest_s.x)],
        "y": [(21, rest_s.y), (wu, y_out), (hit - 3, y_out - side * 0.02 * SIZE),
              (hit, Y_MID + side * P["swing_across"] * SIZE), (se, Y_MID - side * 0.06 * SIZE),
              (se + 3, Y_MID + side * 0.12 * SIZE), (pl, rest_s.y)],
        "z": [(21, rest_s.z), (wu, z_g + 0.75 * HGT), (hit - 3, z_g + 0.8 * HGT), (hit, z_g + P["swing_height"] * HGT),
              (se, z_g + P["swing_height"] * HGT * 0.95), (se + 3, z_g + 0.4 * HGT), (pl - 2, rest_s.z + 0.05 * HGT),
              (pl, rest_s.z)],
    }

    def pose(f):
        rd = keys(f, dx)
        p = keys(f, pitch)
        rear_body(p, dx=rd, dz=keys(f, dz), roll=keys(f, roll) * 0.4)
        t_ = keys(f, twist)
        trunk((0, -t_ * 0.35, 0), (-p * 0.3, t_, keys(f, roll)))
        look_chain(lambda x: keys(x, twist) * 0.6, lambda x: R(6) - keys(x, pitch) * 0.5, f, 1.0)
        jaw(keys(f, [(0, 0), (wu - 2, 6), (hit, 30), (pl, 8), (N, 0)]))
        bend(TAIL, UP, [-keys(f - 1 - i, twist) * 0.35 for i in range(4)])
        tail_lift(-p, 0.3)
        for l in LEGS:
            if l == leg and f >= 21:
                if f <= pl:
                    tgt = Vector((keys(f, path["x"]) + (rd if f < pl else D), keys(f, path["y"]), keys(f, path["z"])))
                    foot(l, tgt, R(30) * keys(f, [(21, 0), (wu, 1), (hit, 0.3), (pl, 0)]))
                else:
                    foot(l, K.REST[l]["ball"] + Vector((D, 0, 0)))
                continue
            x, lift, curl = feet_pos(l, f)
            hgt = (P.get("lift_front", 0.18) if l[0] == "F" else 0.13) * HGT
            foot(l, K.REST[l]["ball"] + Vector((x, 0, hgt * lift)), R(20) * curl)
    return {"N": N, "loop": False, "kind": "root_motion", "pose": pose, "max_stretch": P.get("max_stretch"),
            "reach_smooth": P.get("reach_smooth"), "root_motion": D, "fists": [leg], "hit": hit,
            "events": [{"frame": hit, "event": "hit"},
                       {"frame": N, "event": "root_motion", "distance_m": round(D, 4), "axis": "x"}]}


def clip_hit(P):
    """Treffer: Ruck zurück, Schultern ziehen sich zusammen, Kopf duckt verzögert, Schwanz zuckt nach, Ende = Standhaltung."""
    N = P["frames"]
    j, ro, hd = P["jolt"] * SIZE, R(P["roll_deg"]), R(P["head_deg"])
    e = N - 4
    dx = [(0, 0), (2, -j), (5, -j * 0.55), (8, j * 0.12), (10, -j * 0.04), (e, 0)]
    dz = [(0, 0), (3, -0.05 * HGT), (8, 0.01 * HGT), (e, 0)]
    roll = [(0, 0), (2, ro), (5, -ro * 0.35), (8, ro * 0.12), (e, 0)]
    head = [(0, 0), (3, hd), (6, -hd * 0.35), (9, hd * 0.12), (e, 0)]
    hp = [(0, 0), (3, R(12)), (6, -R(4)), (e, 0)]

    def pose(f):
        body(dx=keys(f, dx), dz=keys(f, dz), roll=keys(f, roll))
        trunk((0, 0, -keys(f - 1, roll) * 0.3), (R(4) * keys(f, [(0, 0), (2, 1), (6, 0), (N, 0)]),
                                                 keys(f - 1, head) * 0.15, keys(f - 1, roll) * 0.3))
        bend(NECK, UP, [keys(f - 2, head) * 0.3, keys(f - 1, head) * 0.3, keys(f, head) * 0.4])
        bend(NECK, LEFT, [keys(f - 1, hp) / 2, keys(f, hp) / 2, 0])
        jaw(12 * keys(f, [(0, 0), (3, 1), (8, 0), (N, 0)]))
        bend(TAIL, UP, [R(8) * keys(f - 2 - i, roll) / max(1e-6, ro) * (0.4 + 0.2 * i) for i in range(4)])
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "reach_smooth": P.get("reach_smooth")}


def clip_death(P):
    """PLATZHALTER (Nutzerregel „Death-Clips nicht anfassen“): Kopie des Bär-/Hirsch-Tods (zur Seite kippen)."""
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
    v = K.PB[bone].matrix.to_3x3() @ Vector((0, 1, 0))
    return math.degrees(math.atan2(v.y, v.x))


def turn_check(spec, expect):
    """Drehrichtung gemessen statt angenommen (aus bear_clips kopiert): Standfüße wandern relativ zum Körper im
    Uhrzeigersinn → Körper dreht links (+). Dazu mittleres Gieren von Kopf, Brust, Becken (Kopf führt)."""
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
    body_deg = -math.degrees(rot_sum) / max(1, cnt) * N * (spec["duty"])
    ok = (body_deg > 0) == (expect > 0) and (yaws["Head"] > 0) == (expect > 0) and \
        abs(yaws["Head"]) > abs(yaws["Chest"]) > 0 and (yaws["Chest"] > 0) == (expect > 0)
    return {"body_turn_deg_per_cycle": round(body_deg, 1), "mean_yaw_deg": {k: round(v, 1) for k, v in yaws.items()},
            "turn_dir_ok": ok}


_TAIL_IDX = None


def _tail_verts():
    global _TAIL_IDX
    if _TAIL_IDX is None:
        names = {g.index: g.name for g in K.body_obj.vertex_groups}
        _TAIL_IDX = [v.index for v in K.body_obj.data.vertices if len(v.groups)
                     and names[max(v.groups, key=lambda g: g.weight).group].startswith(("Tail_", "Hips"))]
    return _TAIL_IDX


def pose_stats(spec):
    """Brust-Neigung, Fausthöhe, tiefster Schwanz-/Becken-Vertex über dem Boden (rammt der Schwanz beim Aufrichten?)."""
    out = {"chest_pitch_max_deg": -1e9, "front_fist_max_up_m": 0.0, "tail_min_above_ground_m": 1e9}
    v0 = K.DB["Chest"].matrix_local.to_3x3() @ Vector((0, 1, 0))
    idx = _tail_verts()
    mw = K.body_obj.matrix_world
    for f in range(0, spec["N"] + 1, 2):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        v = K.PB["Chest"].matrix.to_3x3() @ Vector((0, 1, 0))
        pch = math.degrees(math.atan2(v.z, math.hypot(v.x, v.y)) - math.atan2(v0.z, math.hypot(v0.x, v0.y)))
        out["chest_pitch_max_deg"] = max(out["chest_pitch_max_deg"], round(pch, 1))
        for leg in ("FL", "FR"):
            out["front_fist_max_up_m"] = max(out["front_fist_max_up_m"], round(K.ball(leg).z - K.REST[leg]["ball"].z, 3))
        ev = K.body_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        m = ev.to_mesh()
        z = min((mw @ m.vertices[i].co).z for i in idx) - K.GROUND
        ev.to_mesh_clear()
        out["tail_min_above_ground_m"] = min(out["tail_min_above_ground_m"], round(z, 3))
    return out


def strike_check(spec):
    """Trifft der Angriff VOR dem Körper? Faust(e) beim Treffer gegen Nasenspitze (jetzt und Ruhe + Root-Weg), Höhe."""
    f = spec["hit"]
    K.reset()
    spec["pose"](f)
    bpy.context.view_layer.update()
    nose = K.arm.matrix_world @ K.PB["Head"].tail
    root_dx = (K.PB["Root"].head - K.DB["Root"].head_local).x
    out = {"hit_frame": f, "body_advance_m": round(root_dx, 3), "nose_now_x_m": round(nose.x, 3)}
    for leg in spec["fists"]:
        b = K.ball(leg)
        out[leg] = {"fist_ahead_of_nose_now_m": round(b.x - nose.x, 3),
                    "fist_ahead_of_rest_nose_plus_root_m": round(b.x - NOSE0.x - root_dx, 3),
                    "fist_ahead_of_rest_fist_m": round(b.x - K.REST[leg]["ball"].x - root_dx, 3),
                    "fist_height_m": round(b.z - K.GROUND, 3), "fist_y_m": round(b.y - Y_MID, 3),
                    "shoulder_height_m": round((K.arm.matrix_world @ K.PB[f"Leg_{leg}_1"].head).z - K.GROUND, 3)}
    return out


turn = R(ST["turn"]["turn_deg"])
IK_STIFF = ST.get("ik", {}).get("stiffness", {})


def stiff(spec):
    spec["ik_stiff"] = IK_STIFF
    spec["foot_ground"] = True
    return spec


CLIPS = {
    "Walk": stiff(locomotion(ST["walk"])),
    "Run": stiff(locomotion(ST["run"])),
    "TurnLeft": stiff(locomotion(ST["turn"], turn=turn)),
    "TurnRight": stiff(locomotion(ST["turn"], turn=-turn)),
    "Idle": stiff(clip_idle(ST["idle"])),
    "Ready": stiff(clip_ready(ST["ready"])),
    "Taunt": stiff(clip_taunt(ST["taunt"])),
    "Attack1": stiff(clip_attack1(ST["attack1"])),
    "Attack2": stiff(clip_attack2(ST["attack2"])),
    "Hit": stiff(clip_hit(ST["hit"])),
    "Death": clip_death(ST["death"]),
}
if os.environ.get("GORILLA_DEBUG"):                     # Diagnose: Reichweite je Bein und Frame, dann Ende
    spec = CLIPS[os.environ["GORILLA_DEBUG"]]
    for f in range(spec["N"] + 1):
        K.reset()
        spec["pose"](f)
        bpy.context.view_layer.update()
        r = {l: round((K.arm.matrix_world.inverted() @ K.IK[l].matrix_world.translation - K.PB[f"Leg_{l}_1"].head).length
                      / K.chain_len(l), 3) for l in LEGS}
        e = {l: round((K.ball(l) - K.IK[l].matrix_world.translation).length, 3) for l in LEGS}
        print("DBG", f, "ratio", r, "err", e, "need", round(K.reach_fix(), 3))
    if spec.get("reach_smooth"):                         # wie bake(): geglättete Absenkung, danach Rest-Bedarf
        need = []
        for f in range(spec["N"] + 1):
            K.reset()
            spec["pose"](f)
            need.append(K.reach_fix())
        pre = K._smooth_envelope(need, int(spec["reach_smooth"]), spec.get("loop", False))
        for f in range(spec["N"] + 1):
            K.reset()
            spec["pose"](f)
            K.move("Root", Vector((0, 0, -pre[f])))
            print("DBG2", f, "pre", round(pre[f], 3), "extra", round(K.reach_fix(), 3))
    raise SystemExit
EXTRA = {"TurnLeft": turn_check(CLIPS["TurnLeft"], 1), "TurnRight": turn_check(CLIPS["TurnRight"], -1)}
for c in ("Attack1", "Taunt", "Ready"):
    EXTRA[c] = pose_stats(CLIPS[c])
EXTRA["Attack1"].update(strike_check(CLIPS["Attack1"]))
EXTRA["Attack2"] = strike_check(CLIPS["Attack2"])
EXTRA["Attack2"]["root_motion_m"] = round(CLIPS["Attack2"]["root_motion"], 3)
for c, v in EXTRA.items():
    print("GORILLA_CHECK", c, json.dumps(v, ensure_ascii=False))
K.reset()
K.bake(CLIPS)
rep_p = K.OUT / "clips_report.json"
rep = json.loads(rep_p.read_text(encoding="utf-8"))
for c, v in EXTRA.items():
    rep["clips"][f"{K.PREFIX}_{c}"].update(v)
rep["turn_dir_ok"] = all(EXTRA[c]["turn_dir_ok"] for c in ("TurnLeft", "TurnRight"))
rep_p.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
