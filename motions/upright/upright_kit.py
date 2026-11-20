"""Baukasten des Skeletts `upright` (motions/upright/*): aufrechte Zweibeiner mit langen Armen – Treant, Golem, Brute.
Eigenständig (2026-11-18): kein Import aus anderen Baukästen. Inhaltlich angelehnt an motions/biped_raptor/biped_kit.py
(Prinzip "Aufwand nach Blender", Backen, Selbstprüfung), aber für die upright-Knochen (rigging/upright_rig.py):
  Beine Thigh/Shin/Foot/Toe_{L,R} – IK-Kette Oberschenkel+Schienbein auf ein Ziel am Knöchel (trägt auch die
  Fuß-Ausrichtung); Arme Clavicle/UpperArm/Forearm/Hand/Fingers_{L,R} – frei (FK) mit Nachschwingen, für Bodenkontakt
  (Slam) per IK auf ein Ziel am Handgelenk, Einfluss pro Frame einblendbar.
Ein Clip setzt pro Frame nur Ziele + Drehungen. bake() liest die fertige Pose jedes Frames aus und schreibt normale
Keyframes; danach werden Constraints + Ziel-Empties entfernt (Unity braucht nur FK).

Achsen (Blender, Armature-Raum): vorn +X (FWD), links +Y (LEFT), oben +Z (UP).
Vorzeichen der Hilfen: rot(n, LEFT, +a) = nach vorn neigen/beugen · rot(n, UP, +a) = nach links drehen ·
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
TRUNK = ("Pelvis", "Spine_1", "Spine_2", "Spine_3", "Chest")


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
    global OUT, ST, FPS, PREFIX, arm, body_obj, PB, DB, HGT, LEGLEN, GROUND, REST, IK, AIK, sc, SIZE
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
    HGT = max(zs) - GROUND                                 # Höhe der Kreatur
    LEGLEN = DB["Thigh_L"].head_local.z - GROUND           # Hüfthöhe = Beinlänge
    SIZE = HGT
    REST, IK, AIK = {}, {}, {}
    for s in SIDES:
        shin, foot, toe = DB[f"Shin_{s}"], DB[f"Foot_{s}"], DB[f"Toe_{s}"]
        REST[s] = {"ankle": shin.tail_local.copy(), "ball": foot.tail_local.copy(), "tip": toe.tail_local.copy(),
                   "foot_mat": foot.matrix_local.copy(),
                   "wrist": DB[f"Forearm_{s}"].tail_local.copy(), "hand_mat": DB[f"Hand_{s}"].matrix_local.copy()}
        e = bpy.data.objects.new(f"IK_{s}", None)
        sc.collection.objects.link(e)
        IK[s] = e
        c = PB[f"Shin_{s}"].constraints.new("IK")
        c.target, c.chain_count, c.use_stretch = e, 2, False
        PB[f"Foot_{s}"].constraints.new("COPY_ROTATION").target = e
        ea = bpy.data.objects.new(f"AIK_{s}", None)
        sc.collection.objects.link(ea)
        AIK[s] = ea
        c = PB[f"Forearm_{s}"].constraints.new("IK")
        c.target, c.chain_count, c.use_stretch = ea, 2, False
        PB[f"Hand_{s}"].constraints.new("COPY_ROTATION").target = ea
    global REST_RATIO
    REST_RATIO = {s: (REST[s]["ankle"] - DB[f"Thigh_{s}"].head_local).length / chain_len(s) for s in SIDES}
    print("UPRIGHT_INIT", json.dumps({"height_m": round(HGT, 3), "leg_m": round(LEGLEN, 3),
                                      "rest_stretch": {s: round(v, 3) for s, v in REST_RATIO.items()},
                                      "style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}"}))


# ---------------------------------------------------------------- Grundlagen
def reset():
    for pb in PB:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()
    for s in SIDES:
        set_foot(s, Vector())
        for c in PB[f"Shin_{s}"].constraints:
            c.influence = 1.0
        for c in PB[f"Foot_{s}"].constraints:
            c.influence = 1.0
        arm_ik(s, 0.0)


def rot(name, axis_world, angle):
    """Drehung um eine Achse (Armature-Raum der Ruhepose), auf die bestehende Drehung des Knochens multipliziert.
    Mehrere rot() auf denselben Knochen: der zuerst aufgerufene wirkt „außen“ (z. B. erst Schwingen, dann Abspreizen)."""
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
    """Beschleunigt (langsam los, schnell am Ende) – Schlag, der Wucht aufbaut."""
    return max(0.0, min(1.0, x)) ** p


def phase(t, offset, duty):
    p = (t + offset) % 1.0
    return (False, p / duty) if p < duty else (True, (p - duty) / (1 - duty))


def hermite(s, p0, p1, m0, m1):
    s2, s3 = s * s, s * s * s
    return (2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * m1


def bump(s, peak=0.5):
    """0 → 1 → 0 mit Steigung 0 an beiden Enden; Maximum bei s = peak."""
    s = max(0.0, min(1.0, s))
    k = math.log(0.5) / math.log(max(0.05, min(0.95, peak)))
    return math.sin(math.pi * s ** k) ** 2


def spring_curve(fn, N, freq=3.0, zeta=0.5, sub=8, fade=3, loop=False):
    """Gedämpfte Feder, die der Zielkurve fn(frame) folgt → Liste je Frame (Nachschwingen/Überschwingen).
    Einmal-Clips: die letzten `fade` Frames laufen exakt aufs Ziel zurück. loop=True: Feder läuft zwei Runden ein,
    die zweite wird verwendet (nahtlos für periodische Ziele)."""
    w, dt = 2 * math.pi * freq, 1.0 / FPS / sub
    x, v = fn(0), 0.0
    if loop:
        for _ in range(3):                                   # eingeschwungen: dritte Runde verwenden
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


def lagged(fn, lag):
    """Zielkurve um lag Frames verzögert (Glieder einer Kette folgen nacheinander)."""
    return lambda f: fn(f - lag)


# ---------------------------------------------------------------- Beine
def set_foot(s, offset, heel=0.0, yaw=0.0):
    """Knöchel-Ziel = Ruhe-Knöchel + offset (Armature-Raum, m). heel > 0 = Ferse hebt sich um den Ballen (rad),
    yaw = Fuß um die Senkrechte gedreht (Drehen auf der Stelle)."""
    e = IK[s]
    m = REST[s]["foot_mat"].to_3x3()
    ank = REST[s]["ankle"].copy()
    if heel:
        q = Quaternion(LEFT, heel)
        ank = REST[s]["ball"] + q @ (ank - REST[s]["ball"])
        m = q.to_matrix() @ m
    if yaw:
        m = Quaternion(UP, yaw).to_matrix() @ m
    e.matrix_world = arm.matrix_world @ (Matrix.Translation(ank + offset) @ m.to_4x4())


def foot_toe(s, heel):
    """Zehen bleiben bei gehobener Ferse flach am Boden (gegen die Fuß-Neigung drehen)."""
    rot(f"Toe_{s}", LEFT, -heel)


def chain_len(s):
    return DB[f"Thigh_{s}"].length + DB[f"Shin_{s}"].length


def reach_fix(margin=0.985, iters=4, sides=SIDES):
    """Kann ein Bein sein Ziel nicht erreichen, sinkt der ganze Körper genau so weit (Knie beugen statt Überstrecken)."""
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
    """Gangzyklus „in place“: Standbein schiebt gleichmäßig nach hinten, Schwungbein ohne Ruck (Hermite-Kurve mit
    Bodengeschwindigkeit 0 beim Ab-/Aufsetzen), Ferse löst sich am Ende der Standphase (heel_deg), Hub früh hoch.
    turn (rad pro Zyklus) > 0 = Körper dreht nach LINKS (Standfüße wandern im Körper-Raum im Uhrzeigersinn)."""
    S = P.get("stride", 0.0) * LEGLEN
    d = P["duty"]
    m = -(1 - d) / d * P.get("speed_match", 1.0)
    for s in SIDES:
        swing, x = phase(t, offsets[s], d)
        heel = 0.0
        if swing:
            u = hermite(x, -0.5, 0.5, m, m)
            lift = P["lift"] * LEGLEN * bump(x, P.get("lift_peak", 0.4))
            heel = R(P.get("heel_deg", 0)) * (1 - ease(x / 0.45)) if x < 0.45 else 0.0
        else:
            u, lift = 0.5 - x, 0.0
            pre = P.get("heel_pre", 0.0)                     # Ferse hebt schon kurz vor dem Abheben (Abrollen)
            if pre and x > 1 - pre:
                heel = R(P.get("heel_deg", 0)) * ease((x - (1 - pre)) / pre)
        yaw = 0.0
        if turn:
            r = REST[s]["ankle"] - DB["Root"].head_local
            r = Vector((r.x, r.y, 0))
            yaw = turn * u
            off = Quaternion(UP, yaw).to_matrix() @ r - r
        else:
            off = FWD * (S * u)
        set_foot(s, off + Vector((0, 0, lift)), heel, yaw)
        if heel and not swing:
            foot_toe(s, heel)


# ---------------------------------------------------------------- Rumpf, Arme, Krone
def body(dz=0.0, dx=0.0, dy=0.0, pitch=0.0, roll=0.0, yaw=0.0):
    """Ganzer Körper (Root): Versatz in m, Winkel in rad (pitch + = nach vorn neigen, roll + = nach rechts kippen,
    yaw + = nach links drehen)."""
    move("Root", Vector((dx, dy, dz)))
    rot("Root", UP, yaw)
    rot("Root", LEFT, pitch)
    rot("Root", FWD, roll)


def spine(flex=0.0, side=0.0, twist=0.0, shares=(0.12, 0.2, 0.22, 0.22, 0.24)):
    """Rumpf als Kette biegen (über Pelvis … Chest verteilt): flex + = nach vorn krümmen, side + = nach links neigen
    (Oberseite nach +Y), twist + = Oberkörper nach links drehen."""
    for n, k in zip(TRUNK, shares):
        rot(n, UP, twist * k)
        rot(n, LEFT, flex * k)
        rot(n, FWD, -side * k)


def rest_lean():
    """Neigung der Rumpf-Achse (Becken → Brust-Oberkante) in der Tripo-Ruhepose, Grad: (vorn +, links +)."""
    a, b = DB["Pelvis"].head_local, DB["Chest"].tail_local
    d = b - a
    return math.degrees(math.atan2(d.x, d.z)), math.degrees(math.atan2(d.y, d.z))


def posture(lean_deg, side_deg=0.0, flex=0.0, side=0.0, twist=0.0):
    """Haltung ABSOLUT vorgeben (nicht auf die krumme/gebückte Tripo-Ruhepose addieren): Rumpf-Achse soll lean_deg nach
    vorn und side_deg nach links geneigt sein; flex/side/twist (rad) kommen als Bewegung dazu."""
    rl, rs = rest_lean()
    spine(flex=R(lean_deg - rl) + flex, side=R(side_deg - rs) + side, twist=twist)


def pelvis_counter(pitch=0.0):
    """Becken gegen die Rumpf-Neigung zurückdrehen (Hüfte bleibt über den Beinen, nur der Oberkörper kippt)."""
    rot("Pelvis", LEFT, -pitch)


def arm_fk(s, swing=0.0, out=0.0, twist=0.0, elbow=0.0, wrist=0.0, fingers=0.0, shrug=0.0, sweep=0.0):
    """Arm frei (Grad): swing + = nach vorn/oben schwingen, out + = vom Körper abspreizen, sweep + = waagerecht nach
    links schwenken (um die Senkrechte), elbow + = Unterarm nach vorn beugen, wrist + = Hand nach vorn abknicken,
    fingers + = Finger einrollen (nach vorn/innen), − = spreizen/strecken, shrug + = Schulter hoch."""
    sg = 1 if s == "L" else -1
    rot(f"Clavicle_{s}", FWD, -sg * R(shrug))
    rot(f"UpperArm_{s}", UP, R(sweep))
    rot(f"UpperArm_{s}", LEFT, -R(swing))
    rot(f"UpperArm_{s}", FWD, sg * R(out))
    rot(f"UpperArm_{s}", UP, -sg * R(twist))
    rot(f"Forearm_{s}", LEFT, -R(elbow))
    rot(f"Hand_{s}", LEFT, -R(wrist))
    rot(f"Fingers_{s}", LEFT, -R(fingers))


def arm_ik(s, k, pos=None, hand_q=None):
    """Hand-IK: k 0..1 Einfluss; pos = Ziel des Handgelenks (Armature-Raum), hand_q = Drehung der Hand gegenüber der
    Ruhe (Armature-Raum)."""
    for c in PB[f"Forearm_{s}"].constraints:
        c.influence = k
    for c in PB[f"Hand_{s}"].constraints:
        c.influence = k
    if k <= 0 or pos is None:
        return
    m = REST[s]["hand_mat"].to_3x3()
    if hand_q is not None:
        m = hand_q.to_matrix() @ m
    AIK[s].matrix_world = arm.matrix_world @ (Matrix.Translation(pos) @ m.to_4x4())


def crown(pitch=0.0, roll=0.0, yaw=0.0):
    """Krone/Kopfaufbau (starr) gegenüber der Brust: nachschwingen lassen (rad)."""
    rot("Crown", UP, yaw)
    rot("Crown", LEFT, pitch)
    rot("Crown", FWD, roll)


def head(pitch=0.0, yaw=0.0):
    """Kopf (bei Kreaturen mit eigenem Kopf; Treant: Platzhalter ohne Gewicht – bewegt nichts)."""
    rot("Neck", UP, yaw / 2)
    rot("Neck", LEFT, pitch / 2)
    rot("Head", UP, yaw / 2)
    rot("Head", LEFT, pitch / 2)


def world_pos(bone, tail=True):
    bpy.context.view_layer.update()
    pb = PB[bone]
    return arm.matrix_world @ (pb.tail if tail else pb.head)


def chest_yaw():
    """Blickrichtung der Brust in Grad (+ = nach links) – für die Prüfung der Drehrichtung."""
    bpy.context.view_layer.update()
    q = PB["Chest"].matrix.to_quaternion() @ DB["Chest"].matrix_local.to_quaternion().inverted()
    v = q @ FWD
    return math.degrees(math.atan2(v.y, v.x))


# ---------------------------------------------------------------- Messen
def mesh_min_z():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_obj.evaluated_get(dg)
    m = ev.to_mesh()
    z = min((body_obj.matrix_world @ v.co).z for v in m.vertices)
    ev.to_mesh_clear()
    return z


_REST_EDGES = None


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
    """Glatte Kurve, die nie unter v liegt: gleitendes Maximum (Radius r), dann Dreiecksfilter (Radius r)."""
    n = len(v) - 1 if loop else len(v)
    at = (lambda i: v[i % n]) if loop else (lambda i: v[max(0, min(n - 1, i))])  # noqa: E731
    mx = [max(at(i + k) for k in range(-r, r + 1)) for i in range(-r, n + r)]
    w = [r + 1 - abs(k) for k in range(-r, r + 1)]
    out = [sum(w[k + r] * mx[i + r + k] for k in range(-r, r + 1)) / sum(w) for i in range(n)]
    return out + [out[0]] if loop else out


def sole(s):
    """Bodenpunkte des Fußes in der aktuellen Pose: Knöchel (Ferse), Ballen (Drehpunkt beim Abrollen), Zehenspitze."""
    bpy.context.view_layer.update()
    mw = arm.matrix_world
    return mw @ PB[f"Shin_{s}"].tail, mw @ PB[f"Foot_{s}"].tail, mw @ PB[f"Toe_{s}"].tail


# ---------------------------------------------------------------- Backen + Selbstprüfung
def bake(clips):
    """clips: {Name: {N, loop, kind (locomotion|stand|stand_return|death), pose(f), swing(s, f), duty, turn,
    planted: [Seiten], events}}. Schreibt Actions <PREFIX>_<Name>, clips_report.json, events.json, clips.blend."""
    C = ST["checks"]
    tol_c, tol_p = C["contact_tolerance"] * SIZE, C["planted_tolerance"] * SIZE
    arm.animation_data_create()
    report, events, baked = {}, {}, {}
    for cname in ST["meta"]["clips"]:
        spec = clips[cname]
        N, kind = spec["N"], spec["kind"]
        frames, feet, stretch, ev = [], {s: [] for s in SIDES}, 1.0, list(spec.get("events", []))
        prev, lowered, where, yaws = {}, 0.0, "", []
        smooth = spec.get("reach") == "smooth" and kind != "death"

        def ground_sides(f):
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
            elif kind != "death":
                lowered = max(lowered, reach_fix())
            bpy.context.view_layer.update()
            frames.append({pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE",
                                                      to_space="LOCAL").copy() for pb in PB})
            yaws.append(chest_yaw())
            for s in SIDES:
                sw = spec["swing"](s, f) if kind == "locomotion" else False
                if kind == "locomotion" and prev.get(s) and not sw and f < N:
                    ev.append({"frame": f, "event": "footstep", "leg": s})
                prev[s] = sw
                ank, bl, tp = sole(s)
                tgt = arm.matrix_world.inverted() @ IK[s].matrix_world.translation
                feet[s].append((ank.copy(), tp.copy(), sw, tgt.copy(), bl.copy()))
            if f % C.get("stretch_every", 3) == 0:
                st_now = max_stretch()
                if st_now > stretch:
                    stretch, where = st_now, f"{STRETCH_WHERE} @ Frame {f}"
        baked[cname] = frames
        r = {"frames": N, "seconds": round(N / FPS, 3), "loop": spec.get("loop", False)}
        reach = 0.0 if kind == "death" else max((a_ - tgt).length for s in feet.values() for a_, _, sw, tgt, _ in s if not sw)
        r["ik_reach_error_m"] = round(reach, 4)
        r["body_lowered_max_m"] = round(lowered, 4)
        if kind == "locomotion":
            fl, st_, slip, sweeps = [], [], [], []
            for s, seq in feet.items():
                # Bodenkontakt in der Standphase: Fuß flach (Knöchel auf Ruhehöhe) ODER beim Abrollen Ballen + Zehen am Boden
                fl.append(max(min(abs(a_.z - REST[s]["ankle"].z), max(abs(bl.z - REST[s]["ball"].z), abs(tp.z - REST[s]["tip"].z)))
                              for a_, tp, sw, _, bl in seq if not sw))
                # zusammenhängende Standphasen (Ballen = Drehpunkt, rutscht beim Abrollen nicht)
                runs, run = [], []
                for a_, tp, sw, _, bl in seq:
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
                    # Rutschen: Standfuß muss gleichmäßig nach hinten wandern (Körper läuft „in place“) – größte
                    # Abweichung der Fußgeschwindigkeit von der mittleren, je Frame
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
                # Drehrichtung: Standfüße wandern im Körper-Raum entgegen der Körperdrehung (Uhrzeigersinn = links)
                sweep = sum(sweeps) / max(1, len(sweeps))
                r["stance_foot_sweep_deg"] = round(sweep, 1)
                r["body_turns"] = "left" if sweep < 0 else "right"
                r["chest_lead_deg_mean"] = round(sum(yaws) / len(yaws), 1)
                r["upper_body_leads"] = (r["chest_lead_deg_mean"] > 0) == (r["body_turns"] == "left")
                r["turn_ok"] = r["upper_body_leads"] and (r["body_turns"] == ("left" if spec["turn"] > 0 else "right"))
            else:
                r["move_speed_mps"] = round(sum(st_) / len(st_) / (spec["duty"] * N / FPS), 3)
        if kind in ("stand", "stand_return"):
            planted = spec.get("planted", SIDES)
            mv = max(max((a_ - feet[s][0][0]).length, (tp - feet[s][0][1]).length) for s in planted for a_, tp, _, _, _ in feet[s])
            r["feet_moved_max_m"] = round(mv, 4)
            r["feet_planted_ok"] = mv <= tol_p and reach <= tol_p
        if r["loop"]:
            jump = max((frames[0][n].translation - frames[N][n].translation).length +
                       frames[0][n].to_quaternion().rotation_difference(frames[N][n].to_quaternion()).angle
                       for n in frames[0])
            r["loop_jump"] = round(jump, 5)
            r["loop_ok"] = jump < 1e-3
        if kind == "stand_return":
            # zurück in die Ausgangshaltung (= Standhaltung des Musters, Frame 0)
            r["returns_to_rest"] = all((frames[N][n].translation - frames[0][n].translation).length < 1e-3 and
                                       frames[N][n].to_quaternion().rotation_difference(frames[0][n].to_quaternion()).angle < 1e-2
                                       for n in frames[N] if not n.startswith(("Thigh", "Shin", "Foot", "Toe")))
        if kind == "death":
            reset()
            spec["pose"](N)
            bpy.context.view_layer.update()
            z = mesh_min_z()
            r["final_min_z_vs_ground_m"] = round(z - GROUND, 4)
            r["no_ground_penetration"] = z >= GROUND - tol_c
        for k in ("hand_ground_m", "placeholder"):
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
    for e in list(IK.values()) + list(AIK.values()):
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
