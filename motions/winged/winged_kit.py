"""Baukasten des Skeletts `winged` (motions/winged/*): Zweibeiner mit Flügeln – Wyvern/Drache (drake), Vogel (bird).
Eigenständig (2026-11-20): kein Import aus anderen Baukästen. Inhaltlich angelehnt an upright_kit/biped_kit
(Prinzip "Aufwand nach Blender", Backen, Selbstprüfung), aber für die winged-Knochen (rigging/winged_rig.py):
  Beine Thigh/Shin/Foot/Toe_{L,R} (digitigrad) – IK-Kette Oberschenkel+Unterschenkel+Lauf auf ein Ziel am Fußballen,
  die Zehen folgen der Ausrichtung des Ziels. In der Luft wird die IK ausgeblendet (Beine frei/angezogen).
  Flügel Clavicle/UpperArm/Forearm/Hand/Finger_1/Finger_2_{L,R} – ABSOLUT gesetzt (wing()): Richtung + Flügelebene jedes
  Knochens werden aus wenigen Parametern (Ausbreiten/Falten, Heben, Fegen, Anstellwinkel) symmetrisch vorgegeben,
  unabhängig davon, wie schief Tripo die Flügel gestellt hat (Lehre Eel Stalker).
  Schwanz Tail_1..6 – ebenfalls absolut (tail()): Richtung je Glied, die Tripo-Krümmung zählt nicht.
Ein Clip setzt pro Frame nur Ziele + Drehungen. bake() liest die fertige Pose jedes Frames aus und schreibt normale
Keyframes; danach werden Constraints + Ziel-Empties entfernt (Unity braucht nur FK).

Achsen (Blender, Armature-Raum): vorn +X (FWD), links +Y (LEFT), oben +Z (UP).
Vorzeichen: rot(n, LEFT, +a) = nach vorn neigen/beugen (Spitze nach unten) · rot(n, UP, +a) = nach links drehen ·
rot(n, FWD, +a) = nach rechts kippen (Oberseite wandert nach −Y).
"""
import json
import math
import pathlib
import sys
import tomllib

import bpy
from mathutils import Matrix, Quaternion, Vector

UP, FWD, LEFT = Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))
SIDES = ("L", "R")
R = math.radians
TRUNK = ("Pelvis", "Spine_1", "Spine_2", "Chest")
NECK = ("Neck_1", "Neck_2", "Neck_3", "Head")
TAIL = tuple(f"Tail_{i}" for i in range(1, 7))
WING = ("UpperArm", "Forearm", "Hand", "Finger_1", "Finger_2")


def merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_style(style_dir, creature_toml=None):
    st = tomllib.loads((pathlib.Path(style_dir) / "style.toml").read_text(encoding="utf-8"))
    for clip, base in st.get("meta", {}).get("inherit", {}).items():
        st[clip] = merge(st.get(base, {}), st.get(clip, {}))
    variant = None
    if creature_toml:
        mo = tomllib.loads(pathlib.Path(creature_toml).read_text(encoding="utf-8")).get("motion", {})
        variant = mo.get("variant") or None
        if variant:
            st = merge(st, st.get("variants", {}).get(variant, {}))
        st = merge(st, {k: v for k, v in mo.items() if isinstance(v, dict)})
    st["meta"]["variant"] = variant
    return st


def init(style_dir):
    global OUT, ST, FPS, PREFIX, arm, body_obj, PB, DB, HGT, LEGLEN, GROUND, REST, IK, sc, SIZE, WN, Y_MID, REST_RATIO
    a = sys.argv[sys.argv.index("--") + 1:]
    OUT = pathlib.Path(a[0]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    ST = load_style(style_dir, a[1] if len(a) > 1 else None)
    FPS, PREFIX = ST["meta"]["fps"], ST["meta"]["clip_prefix"]
    sc = bpy.context.scene
    sc.render.fps = FPS
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    body_obj = bpy.data.objects["Body_Mesh"]
    PB, DB = arm.pose.bones, arm.data.bones
    for pb in PB:
        pb.rotation_mode = "QUATERNION"
    GROUND = mesh_min_z()
    zs = [(body_obj.matrix_world @ v.co).z for v in body_obj.data.vertices]
    HGT = max(zs) - GROUND
    LEGLEN = DB["Thigh_L"].head_local.z - GROUND
    SIZE = HGT
    WN = {s: Vector(arm[f"wing_normal_{s}"]) for s in SIDES}
    Y_MID = float(arm.get("y_mid", 0.0))
    REST, IK = {}, {}
    rig = ST.get("rig", {})
    for s in SIDES:
        foot, toe = DB[f"Foot_{s}"], DB[f"Toe_{s}"]
        REST[s] = {"ball": foot.tail_local.copy(), "tip": toe.tail_local.copy(), "heel": foot.head_local.copy(),
                   "toe_mat": toe.matrix_local.copy()}
        e = bpy.data.objects.new(f"IK_{s}", None)
        sc.collection.objects.link(e)
        IK[s] = e
        c = PB[f"Foot_{s}"].constraints.new("IK")
        c.target, c.chain_count, c.use_stretch = e, 3, False
        th = rig.get("thigh_stiffness", 0.6)                 # Oberschenkel steckt im Körper, bewegt sich wenig
        tp = PB[f"Thigh_{s}"]
        tp.ik_stiffness_x = tp.ik_stiffness_y = tp.ik_stiffness_z = th
        PB[f"Toe_{s}"].constraints.new("COPY_ROTATION").target = e
    REST_RATIO = {s: (REST[s]["ball"] - DB[f"Thigh_{s}"].head_local).length / chain_len(s) for s in SIDES}
    # Flügel-Grundform aus der Ruhe: Winkel jedes Flügelknochens in der eigenen Flügelebene (0° = Spannweiten-Richtung
    # Schulter → Spitze, + = zur Hinterkante), Mittel aus links/rechts → beide Flügel bekommen dieselbe Form. Die Gelenk-
    # winkel (Ellbogen, Handgelenk) bleiben so wie modelliert; die Clips drehen den ganzen Flügel und falten/spreizen nur
    # um Zuschläge (sonst reißt die Haut, die Tripo im Ruhezustand zwischen den Knochen aufgespannt hat).
    global TH_REST, WING_REST
    th, WING_REST = {}, {}
    for s in SIDES:
        sg = 1 if s == "L" else -1
        n = WN[s].normalized()
        u = DB[f"Finger_2_{s}"].tail_local - DB[f"UpperArm_{s}"].head_local
        u = (u - n * u.dot(n)).normalized()
        b = sg * n.cross(u)
        th[s] = []
        for w in WING:
            d = (DB[f"{w}_{s}"].tail_local - DB[f"{w}_{s}"].head_local).normalized()
            th[s].append(math.degrees(math.atan2(d.dot(b), d.dot(u))))
        um = u if s == "L" else mirror(u)
        nm = n if s == "L" else mirror(n)
        elev = math.degrees(math.asin(max(-1, min(1, um.z))))
        sweep = math.degrees(math.atan2(um.x, um.y))
        # Anstellwinkel: Normale gegen die Normale bei pitch 0 (gleiche Spannweite) um die Spannweite
        v = (Quaternion(UP, -R(sweep)) @ Quaternion(FWD, R(elev))).inverted() @ nm
        pitch = math.degrees(math.atan2(-v.x, v.z))
        WING_REST[s] = {"elev": round(elev, 1), "sweep": round(sweep, 1), "pitch": round(pitch, 1),
                        "inplane_deg": [round(x, 1) for x in th[s]]}
    TH_REST = [(a_ + b_) / 2 for a_, b_ in zip(th["L"], th["R"])]
    print("WINGED_WING_REST", json.dumps(WING_REST), "mittel", [round(x, 1) for x in TH_REST])
    # Bezugs-Rahmen für absolute Flügel/Schwanz-Posen: Brust/Becken in der Standhaltung des Musters (nicht in der
    # Tripo-Ruhepose). In der Standhaltung gelten die Flügel-/Schwanz-Parameter also genau so, wie sie im style.toml stehen;
    # neigt sich der Körper weiter (Gehen, Biss), gehen Flügel und Schwanz mit.
    global REF
    reset()
    posture(ST["stand"]["rise_deg"])
    REF = {n: body_change(n) for n in ("Chest", "Pelvis")}
    reset()
    print("WINGED_INIT", json.dumps({"height_m": round(HGT, 3), "leg_m": round(LEGLEN, 3),
                                     "rest_stretch": {s: round(v, 3) for s, v in REST_RATIO.items()},
                                     "style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}"}))


# ---------------------------------------------------------------- Grundlagen
def reset():
    for pb in PB:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()
    for s in SIDES:
        set_foot(s, Vector())
        ik_set(s, 1.0)


def ik_set(s, k):
    """Bein-IK + Zehen-Ausrichtung einblenden (1 = Fuß steht am Ziel, 0 = Bein frei/FK, z. B. im Flug)."""
    for n in (f"Foot_{s}", f"Toe_{s}"):
        for c in PB[n].constraints:
            c.influence = k


def rot(name, axis_world, angle):
    """Drehung um eine Achse (Armature-Raum der Ruhepose), auf die bestehende Drehung des Knochens multipliziert."""
    if not angle:
        return
    ax = (DB[name].matrix_local.to_3x3().inverted() @ axis_world).normalized()
    PB[name].rotation_quaternion = PB[name].rotation_quaternion @ Quaternion(ax, angle)


def move(name, vec_world):
    PB[name].location = PB[name].location + DB[name].matrix_local.to_3x3().inverted() @ vec_world


def ease(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def ease_in(x, p=2.0):
    return max(0.0, min(1.0, x)) ** p


def ease_out(x, p=2.0):
    return 1 - (1 - max(0.0, min(1.0, x))) ** p


def phase(t, offset, duty):
    p = (t + offset) % 1.0
    return (False, p / duty) if p < duty else (True, (p - duty) / (1 - duty))


def hermite(s, p0, p1, m0, m1):
    s2, s3 = s * s, s * s * s
    return (2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * m1


def bump(s, peak=0.5):
    s = max(0.0, min(1.0, s))
    k = math.log(0.5) / math.log(max(0.05, min(0.95, peak)))
    return math.sin(math.pi * s ** k) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def spring_curve(fn, N, freq=3.0, zeta=0.5, sub=8, fade=3, loop=False):
    """Gedämpfte Feder, die der Zielkurve fn(frame) folgt → Liste je Frame (Nachschwingen). loop=True: periodisch."""
    w, dt = 2 * math.pi * freq, 1.0 / FPS / sub
    x, v = fn(0), 0.0
    if loop:
        for _ in range(3):
            out = []
            for f in range(N):
                out.append(x)
                for k in range(sub):
                    a = w * w * (fn((f + k / sub) % N) - x) - 2 * zeta * w * v
                    v += a * dt
                    x += v * dt
        return out + [out[0]]
    out = []
    for f in range(N + 1):
        out.append(x)
        for k in range(sub):
            a = w * w * (fn(f + k / sub) - x) - 2 * zeta * w * v
            v += a * dt
            x += v * dt
    res = []
    for f in range(N + 1):
        g = 1.0 if f <= N - fade else ease((N - f) / max(1, fade))
        res.append(fn(f) + (out[f] - fn(f)) * g)
    return res


def wave(t, amp, freq=1.0, lag=0.0, ph=0.0):
    """Periodische Welle (t = 0..1 im Clip), Verzögerung lag in Zyklen."""
    return amp * math.sin(2 * math.pi * (freq * t - lag) + ph)


# ---------------------------------------------------------------- absolute Drehungen (eigene Vorwärtskinematik)
def rest_q(name):
    return DB[name].matrix_local.to_quaternion()


def pose_q(name):
    """Armature-Raum-Drehung des Knochens in der aktuell gesetzten Pose (ohne Constraints – gilt für Rumpf, Hals,
    Flügel, Schwanz; die Beine hängen an der IK)."""
    b = DB[name]
    q = PB[name].rotation_quaternion
    if b.parent is None:
        return rest_q(name) @ q
    return pose_q(b.parent.name) @ (rest_q(b.parent.name).inverted() @ rest_q(name)) @ q


def set_abs(name, q_target):
    """Knochen so drehen, dass seine Armature-Raum-Drehung q_target ist (Eltern-Pose bereits gesetzt)."""
    b = DB[name]
    qp = pose_q(b.parent.name) @ (rest_q(b.parent.name).inverted() @ rest_q(name))
    PB[name].rotation_quaternion = qp.inverted() @ q_target


def body_change(name):
    """Drehung, die ein Knochen gegenüber seiner Ruhe erfahren hat (Armature-Raum)."""
    return pose_q(name) @ rest_q(name).inverted()


def body_frame(name):
    """Körper-Rahmen für absolute Posen: Drehung gegenüber der Standhaltung des Musters (REF)."""
    return body_change(name) @ REF[name].inverted()


def frame(d, n):
    """Orthonormale Basis aus Richtung d (Knochen-Achse) und Ebenen-Normale n."""
    d = d.normalized()
    n = (n - d * n.dot(d)).normalized()
    return Matrix((d, n, d.cross(n))).transposed()


def aim(name, d_target, n_target=None, n_rest=None, frame_q=None):
    """Knochen absolut ausrichten: Richtung d_target (und, falls gegeben, Ebene n_target statt n_rest), beides im
    Körper-Rahmen frame_q (Standard: Ruhe-Armature-Raum)."""
    q0 = rest_q(name)
    d0 = (DB[name].tail_local - DB[name].head_local).normalized()
    fq = frame_q or Quaternion()
    dt = fq @ d_target
    if n_target is None:
        delta = d0.rotation_difference(dt)
    else:
        nt = fq @ n_target
        delta = (frame(dt, nt) @ frame(d0, n_rest).transposed()).to_quaternion()
    set_abs(name, delta @ q0)


# ---------------------------------------------------------------- Flügel (absolut)
def wing_dirs(P):
    """Soll-Richtungen + Ebenen-Normalen (Oberseite) der 5 Flügelknochen des LINKEN Flügels im Körper-Rahmen.
    Grundform = Ruheform (TH_REST, links/rechts gemittelt), ausgebreitet nach außen (+Y), Oberseite oben.
    P (Grad): arm = ganzen Flügel in seiner Ebene drehen (+ = nach hinten) · fold > 0 falten / < 0 weiter spreizen
    (Zuschläge je Knochen aus wing_shape) · elev = Heben um die Längsachse (+ = Spitze hoch) · sweep = Fegen
    (+ = Spitze nach vorn) · pitch = Anstellwinkel um die Spannweite (+ = Vorderkante hoch) · bend = Knick je Glied
    nach unten (Liste 5, kumulativ) · twist = Anstellwinkel je Glied zusätzlich (Liste 5) · curl = Winkel je Glied in
    der Ebene zusätzlich (Liste 5, + = nach hinten)."""
    S = ST["wing_shape"]
    f = P.get("fold", 0.0)
    dl = S["fold_delta_deg"] if f >= 0 else S["spread_delta_deg"]
    th = [t0 + P.get("arm", 0.0) + abs(f) * d + c
          for t0, d, c in zip(TH_REST, dl, P.get("curl", [0] * 5))]
    out = []
    bends = P.get("bend", [0] * 5)
    tw = P.get("twist", [0] * 5)
    for i in range(5):
        elev_i = P.get("elev", 0.0) - sum(bends[:i + 1])
        t = R(th[i])
        d = Vector((-math.sin(t), math.cos(t), 0.0))
        n = Vector((0, 0, 1))
        q = (Quaternion(UP, -R(P.get("sweep", 0.0))) @ Quaternion(FWD, R(elev_i))
             @ Quaternion(LEFT, -R(P.get("pitch", 0.0) + tw[i])))
        out.append((q @ d, q @ n))
    return out


def mirror(v):
    return Vector((v.x, -v.y, v.z))


def wing(s, P, clav=None):
    """Flügel s absolut setzen (nach Rumpf/Brust aufrufen). clav = (vor, hoch) Grad für das Schlüsselbein (Schulter
    vor/zurück, hoch/runter), ebenfalls absolut (Tripo-Schultern liegen oft ungleich)."""
    fq = body_frame("Chest")
    cv = clav or P.get("clav", (0.0, 0.0))
    base = ST["wing_shape"].get("clavicle_deg", (0.0, 10.0))
    a_f, a_u = R(base[0] + cv[0]), R(base[1] + cv[1])
    dc = Vector((math.sin(a_f) * math.cos(a_u), math.cos(a_f) * math.cos(a_u), math.sin(a_u)))
    aim(f"Clavicle_{s}", dc if s == "L" else mirror(dc), frame_q=fq)
    for name, (d, n) in zip(WING, wing_dirs(P)):
        if s == "R":
            d, n = mirror(d), mirror(n)
        aim(f"{name}_{s}", d, n, WN[s], fq)


def wing_blend(Pa, Pb, k):
    """Zwei Flügel-Posen mischen (Zahlen und Listen)."""
    out = {}
    for key in set(Pa) | set(Pb):
        a, b = Pa.get(key), Pb.get(key)
        if a is None:
            a = [0.0] * len(b) if isinstance(b, (list, tuple)) else (0.0 if not isinstance(b, tuple) else b)
        if b is None:
            b = [0.0] * len(a) if isinstance(a, (list, tuple)) else 0.0
        if isinstance(a, (list, tuple)):
            out[key] = [lerp(x, y, k) for x, y in zip(a, b)]
        else:
            out[key] = lerp(a, b, k)
    return out


# ---------------------------------------------------------------- Schwanz (absolut), Hals/Kopf, Kiefer
def tail(yaw=None, pitch=None, droop=None):
    """Schwanz absolut: Grundrichtung nach hinten, um droop (Grad, + = nach unten) gesenkt; yaw/pitch = Listen je Glied
    (Grad, relativ zum vorigen Glied: yaw + = Spitze nach links, pitch + = nach unten). Körper-Rahmen = Becken."""
    fq = body_frame("Pelvis")
    yaw = yaw or [0.0] * 6
    pitch = pitch or [0.0] * 6
    dr = ST["tail_shape"]["droop_deg"] if droop is None else droop
    ay, ap = 0.0, dr
    for i, n in enumerate(TAIL):
        ay += yaw[i]
        ap += pitch[i] + ST["tail_shape"].get("curve_deg", [0] * 6)[i]
        d = Quaternion(UP, -R(ay)) @ (Quaternion(LEFT, -R(ap)) @ Vector((-1, 0, 0)))
        aim(n, d, frame_q=fq)


def tail_wave(t, yaw_amp, pitch_amp=0.0, freq=1, lag=0.07, yaw_bias=0.0, pitch_bias=0.0, droop=None):
    """Welle von der Wurzel zur Spitze (periodisch in t, nahtlos), Ausschlag wächst zur Spitze."""
    ys = [yaw_bias / 6 + yaw_amp * (0.4 + 0.12 * i) * math.sin(2 * math.pi * (freq * t - i * lag)) for i in range(6)]
    ps = [pitch_bias / 6 + pitch_amp * (0.4 + 0.12 * i) * math.sin(2 * math.pi * (freq * t - i * lag) + 1.0)
          for i in range(6)]
    tail(ys, ps, droop)


def neck(pitch=0.0, yaw=0.0, roll=0.0, head_pitch=0.0, head_yaw=0.0, shares=(0.3, 0.35, 0.35)):
    """Hals als Kette (rad): pitch + = nach unten/vorn beugen, yaw + = nach links; Kopf zusätzlich."""
    for n, k in zip(NECK[:3], shares):
        rot(n, UP, yaw * k)
        rot(n, LEFT, pitch * k)
        rot(n, FWD, roll * k)
    rot("Head", UP, head_yaw)
    rot("Head", LEFT, head_pitch)


def jaw(open_deg):
    """Kiefer/Unterschnabel öffnen (Grad, + = auf)."""
    rot("Jaw", LEFT, R(open_deg))


# ---------------------------------------------------------------- Rumpf
def body(dz=0.0, dx=0.0, dy=0.0, pitch=0.0, roll=0.0, yaw=0.0):
    """Ganzer Körper (Root): Versatz in m, Winkel in rad (pitch + = nach vorn neigen, roll + = nach rechts kippen,
    yaw + = nach links drehen)."""
    move("Root", Vector((dx, dy, dz)))
    rot("Root", UP, yaw)
    rot("Root", LEFT, pitch)
    rot("Root", FWD, roll)


def spine(flex=0.0, side=0.0, twist=0.0, shares=(0.2, 0.3, 0.3, 0.2)):
    """Rumpf als Kette (rad): flex + = nach vorn krümmen, side + = nach links biegen (Brust wandert nach +Y,
    um die Senkrechte), twist + = um die Längsachse (Oberseite nach links)."""
    for n, k in zip(TRUNK, shares):
        rot(n, UP, side * k)
        rot(n, LEFT, flex * k)
        rot(n, FWD, -twist * k)


def rest_pitch():
    """Neigung der Rumpf-Achse (Becken → Brust) in der Tripo-Ruhepose, Grad über der Waagerechten."""
    a, b = DB["Pelvis"].head_local, DB["Spine_2"].tail_local
    d = b - a
    return math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))


def posture(rise_deg, flex=0.0, side=0.0, twist=0.0):
    """Haltung ABSOLUT: Rumpf-Achse (Becken → Brust) rise_deg über der Waagerechten (90 = senkrecht aufgerichtet),
    unabhängig von der Tripo-Ruhepose. flex/side/twist (rad) kommen als Bewegung dazu."""
    spine(flex=R(rest_pitch() - rise_deg) + flex, side=side, twist=twist)


# ---------------------------------------------------------------- Beine
def chain_len(s):
    return DB[f"Thigh_{s}"].length + DB[f"Shin_{s}"].length + DB[f"Foot_{s}"].length


def set_foot(s, offset, toe_curl=0.0, yaw=0.0):
    """Ballen-Ziel = Ruhe-Ballen + offset (Armature-Raum). toe_curl > 0 = Zehen nach unten einrollen (rad)."""
    m = REST[s]["toe_mat"].to_3x3()
    if toe_curl:
        m = Quaternion(LEFT, toe_curl).to_matrix() @ m
    if yaw:
        m = Quaternion(UP, yaw).to_matrix() @ m
    IK[s].matrix_world = arm.matrix_world @ (Matrix.Translation(REST[s]["ball"] + offset) @ m.to_4x4())


def reach_fix(margin=0.97, iters=4, sides=SIDES):
    """Kann ein Bein sein Ziel nicht erreichen, sinkt der Körper genau so weit (Knie beugen statt Überstrecken)."""
    total = 0.0
    for _ in range(iters):
        bpy.context.view_layer.update()
        need = 0.0
        for s in sides:
            hip = PB[f"Thigh_{s}"].head
            tgt = arm.matrix_world.inverted() @ IK[s].matrix_world.translation
            d = tgt - hip
            m = max(margin, REST_RATIO[s] + 0.002)
            if d.length - m * chain_len(s) > 0 and hip.z > tgt.z:
                h = math.sqrt(max(0.0, (m * chain_len(s)) ** 2 - d.x ** 2 - d.y ** 2))
                need = max(need, (hip.z - tgt.z) - h)
        if need <= 1e-5:
            break
        move("Root", Vector((0, 0, -need)))
        total += need
    return total


def gait(t, P, offsets, turn=0.0):
    """Gangzyklus „in place“: Standbein schiebt gleichmäßig nach hinten, Schwungbein ohne Ruck (Hermite, Boden-
    geschwindigkeit 0 beim Ab-/Aufsetzen), Hub früh hoch, Zehen rollen im Schwung ein (Vogel: Zehen schließen sich).
    turn (rad pro Zyklus) > 0 = Körper dreht nach LINKS."""
    S = P.get("stride", 0.0) * LEGLEN
    d = P["duty"]
    m = -(1 - d) / d * P.get("speed_match", 1.0)
    for s in SIDES:
        swing, x = phase(t, offsets[s], d)
        if swing:
            u = hermite(x, -0.5, 0.5, m, m)
            lift = P["lift"] * LEGLEN * bump(x, P.get("lift_peak", 0.4))
            curl = R(P.get("toe_curl_deg", 25)) * bump(x, P.get("toe_peak", 0.45))
        else:
            u, lift, curl = 0.5 - x, 0.0, 0.0
        yaw = 0.0
        if turn:
            r = REST[s]["ball"] - DB["Root"].head_local
            r = Vector((r.x, r.y, 0))
            yaw = turn * u
            off = Quaternion(UP, yaw).to_matrix() @ r - r
        else:
            off = FWD * (S * u)
        set_foot(s, off + Vector((0, 0, lift)), curl, yaw)


def legs_tuck(k, fold_deg=(30, -70, 60, 50)):
    """Beine in der Luft anziehen (k 0..1, IK vorher ausblenden): Oberschenkel vor, Lauf nach hinten-oben, Zehen
    eingerollt (Grad: Thigh, Shin, Foot, Toe)."""
    for s in SIDES:
        rot(f"Thigh_{s}", LEFT, -R(fold_deg[0]) * k)
        rot(f"Shin_{s}", LEFT, -R(fold_deg[1]) * k)
        rot(f"Foot_{s}", LEFT, -R(fold_deg[2]) * k)
        rot(f"Toe_{s}", LEFT, R(fold_deg[3]) * k)


# ---------------------------------------------------------------- Messen
def mesh_min_z():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_obj.evaluated_get(dg)
    m = ev.to_mesh()
    z = min((body_obj.matrix_world @ v.co).z for v in m.vertices)
    ev.to_mesh_clear()
    return z


_REST_EDGES = None
STRETCH_WHERE = ""


def max_stretch():
    """Größte Kantendehnung (Länge/Ruhelänge) – nur Info, bremst nie eine Bewegung."""
    global _REST_EDGES, STRETCH_WHERE
    me = body_obj.data
    if _REST_EDGES is None:
        _REST_EDGES = [(e.vertices[0], e.vertices[1], (me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length)
                       for e in me.edges]
        _REST_EDGES = [x for x in _REST_EDGES if x[2] > ST["checks"].get("stretch_min_edge", 0.004) * SIZE]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_obj.evaluated_get(dg)
    m = ev.to_mesh()
    worst, wa = 1.0, 0
    for a, b, l0 in _REST_EDGES:
        r = (m.vertices[a].co - m.vertices[b].co).length / l0
        if r > worst:
            worst, wa = r, a
    ev.to_mesh_clear()
    gs = me.vertices[wa].groups
    STRETCH_WHERE = body_obj.vertex_groups[max(gs, key=lambda g: g.weight).group].name if len(gs) else "?"
    return worst


def smooth_envelope(v, r, loop):
    n = len(v) - 1 if loop else len(v)
    at = (lambda i: v[i % n]) if loop else (lambda i: v[max(0, min(n - 1, i))])  # noqa: E731
    mx = [max(at(i + k) for k in range(-r, r + 1)) for i in range(-r, n + r)]
    w = [r + 1 - abs(k) for k in range(-r, r + 1)]
    out = [sum(w[k + r] * mx[i + r + k] for k in range(-r, r + 1)) / sum(w) for i in range(n)]
    return out + [out[0]] if loop else out


def sole(s):
    bpy.context.view_layer.update()
    mw = arm.matrix_world
    return mw @ PB[f"Foot_{s}"].tail, mw @ PB[f"Toe_{s}"].tail


def bone_yaw(name):
    """Blickrichtung eines Knochens (Grad, + = nach links), gemessen an seiner Vorwärts-Komponente in der Pose."""
    bpy.context.view_layer.update()
    q = PB[name].matrix.to_quaternion() @ DB[name].matrix_local.to_quaternion().inverted()
    v = q @ FWD
    return math.degrees(math.atan2(v.y, v.x))


def wing_tips():
    bpy.context.view_layer.update()
    mw = arm.matrix_world
    return {s: mw @ PB[f"Finger_2_{s}"].tail for s in SIDES}


# ---------------------------------------------------------------- Backen + Selbstprüfung
def bake(clips):
    """clips: {Name: {N, loop, kind (locomotion|stand|stand_return|air|transition|death), pose(f), swing(s, f),
    duty, turn, planted: [Seiten], ground(f) → Seiten mit Bodenkontakt (transition), events, symmetric}}.
    Schreibt Actions <PREFIX>_<Name>, clips_report.json, events.json, clips.blend."""
    C = ST["checks"]
    tol_c, tol_p = C["contact_tolerance"] * SIZE, C["planted_tolerance"] * SIZE
    arm.animation_data_create()
    report, events, baked = {}, {}, {}
    for cname in ST["meta"]["clips"]:
        spec = clips[cname]
        N, kind = spec["N"], spec["kind"]
        frames, feet, stretch, ev = [], {s: [] for s in SIDES}, 1.0, list(spec.get("events", []))
        prev, lowered, where, yaws, hyaws, wsym, minz = {}, 0.0, "", [], [], 0.0, 1e9
        smooth = spec.get("reach") == "smooth" and kind not in ("death", "air")

        def ground_sides(f):
            if kind == "air":
                return []
            if kind == "transition":
                return spec["ground"](f)
            return [s for s in SIDES if not (kind == "locomotion" and spec["swing"](s, f))]
        if smooth:
            need = []
            for f in range(N + 1):
                reset()
                spec["pose"](f)
                need.append(reach_fix(sides=ground_sides(f)))
            low_s = smooth_envelope(need, spec.get("reach_radius", 3), spec.get("loop", False))
        for f in range(N + 1):
            reset()
            spec["pose"](f)
            if smooth:
                move("Root", Vector((0, 0, -low_s[f])))
                lowered = max(lowered, low_s[f] + reach_fix(sides=ground_sides(f)))
            elif kind not in ("death", "air"):
                lowered = max(lowered, reach_fix(sides=ground_sides(f)))
            bpy.context.view_layer.update()
            frames.append({pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE",
                                                      to_space="LOCAL").copy() for pb in PB})
            yaws.append(bone_yaw("Chest"))
            hyaws.append(bone_yaw("Head"))
            if spec.get("symmetric"):
                tp = wing_tips()
                wsym = max(wsym, (Vector((tp["L"].x - tp["R"].x, tp["L"].y + tp["R"].y - 2 * Y_MID,
                                          tp["L"].z - tp["R"].z))).length)
            gs = ground_sides(f)
            for s in SIDES:
                sw = s not in gs
                if kind == "locomotion" and prev.get(s) and not sw and f < N:
                    ev.append({"frame": f, "event": "footstep", "leg": s})
                prev[s] = sw
                bl, tp_ = sole(s)
                tgt = arm.matrix_world.inverted() @ IK[s].matrix_world.translation
                feet[s].append((bl.copy(), tp_.copy(), sw, tgt.copy()))
            if f % C.get("stretch_every", 3) == 0:
                st_now = max_stretch()
                if st_now > stretch:
                    stretch, where = st_now, f"{STRETCH_WHERE} @ Frame {f}"
            if kind in ("stand", "stand_return", "locomotion", "transition") and f % 4 == 0:
                minz = min(minz, mesh_min_z())
        baked[cname] = frames
        r = {"frames": N, "seconds": round(N / FPS, 3), "loop": spec.get("loop", False)}
        stance = [(bl, tgt) for s in feet.values() for bl, _, sw, tgt in s if not sw]
        reach = 0.0 if kind in ("death", "air") or not stance else max((bl - tgt).length for bl, tgt in stance)
        r["ik_reach_error_m"] = round(reach, 4)
        r["body_lowered_max_m"] = round(lowered, 4)
        if kind == "locomotion":
            fl, st_, slip, sweeps = [], [], [], []
            for s, seq in feet.items():
                fl.append(max(max(abs(bl.z - REST[s]["ball"].z), abs(tp_.z - REST[s]["tip"].z))
                              for bl, tp_, sw, _ in seq if not sw))
                runs, run = [], []
                for bl, tp_, sw, _ in seq:
                    if not sw:
                        run.append(bl)
                    elif run:
                        runs.append(run)
                        run = []
                if run:
                    runs.append(run)
                rn = max(runs, key=len)
                st_.append(math.hypot(rn[0].x - rn[-1].x, rn[0].y - rn[-1].y))
                if len(rn) > 2 and not spec.get("turn"):
                    v = [(rn[i + 1] - rn[i]) for i in range(len(rn) - 1)]
                    vm = sum(v, Vector()) / len(v)
                    slip.append(max((x - vm).length for x in v))
                if len(rn) > 2:
                    o = DB["Root"].head_local
                    a0 = math.atan2(rn[0].y - o.y, rn[0].x - o.x)
                    a1 = math.atan2(rn[-1].y - o.y, rn[-1].x - o.x)
                    sweeps.append(math.degrees(a1 - a0))
            r["foot_contact_max_m"] = round(max(fl), 4)
            r["foot_contact_ok"] = max(fl) <= tol_c and reach <= tol_c
            r["foot_slip_per_frame_m"] = round(max(slip), 5) if slip else 0.0
            r["stride_m"] = [round(min(st_), 3), round(max(st_), 3)]
            if spec.get("turn"):
                r["turn_speed_deg_s"] = round(math.degrees(spec["turn"]) / (N / FPS), 1)
                sweep = sum(sweeps) / max(1, len(sweeps))
                r["stance_foot_sweep_deg"] = round(sweep, 1)
                r["body_turns"] = "left" if sweep < 0 else "right"
                r["chest_lead_deg_mean"] = round(sum(yaws) / len(yaws), 1)
                r["head_lead_deg_mean"] = round(sum(hyaws) / len(hyaws), 1)
                left = r["body_turns"] == "left"
                r["body_leads"] = (r["chest_lead_deg_mean"] > 0) == left
                r["head_leads"] = (r["head_lead_deg_mean"] > r["chest_lead_deg_mean"]) == left
                r["turn_ok"] = r["body_leads"] and r["head_leads"] and left == (spec["turn"] > 0)
            else:
                r["move_speed_mps"] = round(sum(st_) / len(st_) / (spec["duty"] * N / FPS), 3)
        if kind in ("stand", "stand_return"):
            planted = spec.get("planted", SIDES)
            mv = max(max((bl - feet[s][0][0]).length, (tp_ - feet[s][0][1]).length)
                     for s in planted for bl, tp_, _, _ in feet[s])
            r["feet_moved_max_m"] = round(mv, 4)
            r["feet_planted_ok"] = mv <= tol_p and reach <= tol_p
        if kind in ("stand", "stand_return", "locomotion", "transition") and minz < 1e8:
            r["min_z_vs_ground_m"] = round(minz - GROUND, 4)
            r["no_ground_penetration"] = minz >= GROUND - C.get("ground_tolerance", 0.02) * SIZE
        if spec.get("symmetric"):
            r["wing_symmetry_err_m"] = round(wsym, 4)
        if r["loop"]:
            jump = max((frames[0][n].translation - frames[N][n].translation).length +
                       frames[0][n].to_quaternion().rotation_difference(frames[N][n].to_quaternion()).angle
                       for n in frames[0])
            r["loop_jump"] = round(jump, 5)
            r["loop_ok"] = jump < 1e-3
        if kind == "stand_return":
            r["returns_to_rest"] = all((frames[N][n].translation - frames[0][n].translation).length < 1e-3 and
                                       frames[N][n].to_quaternion().rotation_difference(frames[0][n].to_quaternion()).angle < 1e-2
                                       for n in frames[N] if not n.startswith(("Thigh", "Shin", "Foot", "Toe")))
        if kind == "death":
            reset()
            spec["pose"](N)
            bpy.context.view_layer.update()
            z = mesh_min_z()
            r["final_min_z_vs_ground_m"] = round(z - GROUND, 4)
        for k in ("placeholder", "air_height_m"):
            if k in spec:
                r[k] = spec[k]() if callable(spec[k]) else spec[k]
        r["max_stretch"] = round(stretch, 2)
        r["stretch_at"] = where if stretch > 1.0 else ""
        oks = [v for k, v in r.items() if k.endswith("_ok") or k in ("returns_to_rest", "no_ground_penetration")]
        r["ok"] = all(oks)
        report[f"{PREFIX}_{cname}"] = r
        events[f"{PREFIX}_{cname}"] = ev
        print("CLIP", f"{PREFIX}_{cname}", json.dumps(r, ensure_ascii=False))
    for pb in PB:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
    for e in list(IK.values()):
        bpy.data.objects.remove(e)
    for cname, frames in baked.items():
        act = bpy.data.actions.new(f"{PREFIX}_{cname}")
        act.use_fake_user = True
        arm.animation_data.action = act
        for f, fr in enumerate(frames):
            for pb in PB:
                pb.matrix_basis = fr[pb.name]
                pb.keyframe_insert("rotation_quaternion", frame=f)
                pb.keyframe_insert("location", frame=f)
    arm.animation_data.action = bpy.data.actions[f"{PREFIX}_{ST['meta']['clips'][0]}"]
    summary = {"style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}", "variant": ST["meta"]["variant"],
               "clips": report, "all_ok": all(r["ok"] for r in report.values())}
    (OUT / "clips_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "events.json").write_text(json.dumps({"fps": FPS, "clips": events}, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "clips.blend"))
    print("CLIPS_OK", summary["all_ok"])
