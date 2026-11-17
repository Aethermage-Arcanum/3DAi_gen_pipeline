"""Gemeinsamer Baukasten aller Muster mit IK-Beinen: Vierbeiner (motions/quadruped/*) und Zweibeiner
(motions/biped_raptor/*). Beine werden aus dem Rig gelesen (Leg_<XX>_1..4).

Prinzip ("Aufwand nach Blender"): Die Beine rechnet Blenders eigene IK. Pro Bein ein Ziel-Empty am Fußballen
(trägt auch die Zehen-Ausrichtung), IK-Kette Oberarm/Oberschenkel → Mittelhand/-fuß. Ein Clip setzt pro Frame
nur Fuß-Ziele + Rumpf/Hals/Kopf/Kiefer/Schwanz. bake() liest die fertige (visuelle) Pose jedes Frames aus und
schreibt sie als normale Keyframes – danach werden Constraints + Empties entfernt (Unity braucht nur FK).
"""
import json
import math
import pathlib
import sys
import tomllib

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

UP, FWD, LEFT = Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))
LEGS = ["FL", "FR", "BL", "BR"]
R = math.radians


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
    global OUT, ST, FPS, PREFIX, arm, body_obj, PB, DB, SIZE, HGT, GROUND, REST, IK, sc
    a = sys.argv[sys.argv.index("--") + 1:]
    OUT = pathlib.Path(a[0]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    ST = load_style(style_dir, a[1] if len(a) > 1 else None)
    FPS, PREFIX = ST["meta"]["fps"], ST["meta"]["clip_prefix"]
    sc = bpy.context.scene
    sc.render.fps = FPS
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")      # Quadruped_Rig, Biped_Rig …
    body_obj = bpy.data.objects["Body_Mesh"]
    PB, DB = arm.pose.bones, arm.data.bones
    global LEGS                                        # Beine aus dem Rig: Vierbeiner FL/FR/BL/BR, Zweibeiner BL/BR
    LEGS = sorted({b.name[4:6] for b in DB if b.name.startswith("Leg_") and b.name.endswith("_1")})
    for pb in PB:
        pb.rotation_mode = "QUATERNION"
    xs = [b.head_local.x for b in DB] + [b.tail_local.x for b in DB]
    SIZE = max(xs) - min(xs)
    GROUND = min(DB[f"Leg_{l}_4"].tail_local.z for l in LEGS)
    HGT = DB["Chest"].head_local.z - GROUND
    REST, IK = {}, {}
    for leg in LEGS:
        ball, toe = DB[f"Leg_{leg}_3"], DB[f"Leg_{leg}_4"]
        REST[leg] = {"ball": ball.tail_local.copy(), "tip": toe.tail_local.copy(),
                     "toe_mat": toe.matrix_local.copy()}
        e = bpy.data.objects.new(f"IK_{leg}", None)
        sc.collection.objects.link(e)
        e.matrix_world = Matrix.Translation(ball.tail_local) @ toe.matrix_local.to_3x3().to_4x4()
        IK[leg] = e
        c = PB[f"Leg_{leg}_3"].constraints.new("IK")
        shoulder = f"Shoulder_{leg}" in PB
        c.target, c.chain_count, c.use_stretch = e, (4 if shoulder else 3), False
        if shoulder:                                   # Schulterblatt gleitet teilweise mit (IK-Steifigkeit)
            sp = PB[f"Shoulder_{leg}"]
            sp.ik_stiffness_x = sp.ik_stiffness_y = sp.ik_stiffness_z = ST.get("rig", {}).get("scapula_stiffness", 0.6)
        thigh = ST.get("rig", {}).get("thigh_stiffness", 0.0)   # Vogel: Oberschenkel steckt im Körper, bewegt sich kaum
        if thigh:
            tp = PB[f"Leg_{leg}_1"]
            tp.ik_stiffness_x = tp.ik_stiffness_y = tp.ik_stiffness_z = thigh
        cr = PB[f"Leg_{leg}_4"].constraints.new("COPY_ROTATION")
        cr.target = e
    global REST_RATIO
    REST_RATIO = {l: (REST[l]["ball"] - DB[f"Leg_{l}_1"].head_local).length / chain_len(l) for l in LEGS}
    print("QUAD_REST_STRETCH", {l: round(v, 3) for l, v in REST_RATIO.items()})
    print(f"QUAD_INIT Größe {SIZE:.3f} m, Rumpfhöhe {HGT:.3f} m, Stil {ST['meta']['skeleton']}/{ST['meta']['style']}"
          f"{' / ' + ST['meta']['variant'] if ST['meta']['variant'] else ''}")


# ---------------------------------------------------------------- Grundlagen
def reset():
    for pb in PB:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()
    for leg in LEGS:
        set_foot(leg, Vector(), 0.0)
        for c in PB[f"Leg_{leg}_3"].constraints:
            c.influence = 1.0
        for c in PB[f"Leg_{leg}_4"].constraints:
            c.influence = 1.0


def rot(name, axis_world, angle):
    """Drehung um eine Achse im Armature-Raum, auf die bestehende Pose multipliziert."""
    ax = (DB[name].matrix_local.to_3x3().inverted() @ axis_world).normalized()
    PB[name].rotation_quaternion = PB[name].rotation_quaternion @ Quaternion(ax, angle)


def move(name, vec_world):
    PB[name].location = PB[name].location + DB[name].matrix_local.to_3x3().inverted() @ vec_world


def set_foot(leg, offset, toe_curl=0.0):
    """Fuß-Ziel = Ruhe-Ballen + offset (Armature-Raum, Meter). toe_curl > 0 = Zehen nach unten einrollen."""
    e = IK[leg]
    m = REST[leg]["toe_mat"].to_3x3()
    if toe_curl:
        m = Quaternion(LEFT, toe_curl).to_matrix() @ m
    e.matrix_world = arm.matrix_world @ (Matrix.Translation(REST[leg]["ball"] + offset) @ m.to_4x4())


def ik_off(leg, k):
    """IK + Zehen-Ausrichtung ausblenden (0 = Bein hängt frei, z. B. im Tod)."""
    for c in PB[f"Leg_{leg}_3"].constraints:
        c.influence = 1 - k
    for c in PB[f"Leg_{leg}_4"].constraints:
        c.influence = 1 - k


def ease(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def phase(t, offset, duty):
    p = (t + offset) % 1.0
    return (False, p / duty) if p < duty else (True, (p - duty) / (1 - duty))


def tip(leg):
    return arm.matrix_world @ PB[f"Leg_{leg}_4"].tail


def ball(leg):
    return arm.matrix_world @ PB[f"Leg_{leg}_3"].tail


# ---------------------------------------------------------------- Bausteine
def body(dz=0.0, dx=0.0, dy=0.0, pitch=0.0, roll=0.0, yaw=0.0):
    """Ganzer Rumpf (Root): Höhe/Versatz in Metern, Winkel in rad (pitch + = Brust hoch)."""
    move("Root", Vector((dx, dy, dz)))
    if pitch:
        rot("Root", LEFT, -pitch)
    if roll:
        rot("Root", FWD, roll)
    if yaw:
        rot("Root", UP, yaw)


def spine(flex=0.0, side=0.0):
    """Rücken beugen: flex + = Rundrücken (Brust + Hüfte nach unten), side + = nach links biegen."""
    for n, k in (("Hips", -0.5), ("Spine_1", 0.5), ("Chest", 0.5)):
        rot(n, LEFT, -flex * k)
        rot(n, UP, side / 3)


def neck_head(pitch=0.0, yaw=0.0, head_pitch=0.0, stabilize=0.0):
    """pitch + = Hals hoch. stabilize 0..1 gleicht die Rumpf-Neigung am Kopf aus (Kopf bleibt ruhig)."""
    for n in ("Neck_1", "Neck_2"):
        rot(n, LEFT, -pitch / 2)
        rot(n, UP, yaw / 2)
    if stabilize:
        bpy.context.view_layer.update()
        q = (PB["Neck_2"].matrix.to_quaternion() @ DB["Neck_2"].matrix_local.to_quaternion().inverted())
        e = q.to_euler()
        rot("Head", LEFT, e.y * stabilize)
    rot("Head", LEFT, -head_pitch)


def jaw(open_deg):
    rot("Jaw", LEFT, R(open_deg))


def tail(t, amp_deg, speed=1.0, lift_deg=0.0, phase0=0.0):
    """Schwanz: seitliches Pendeln als Welle von der Wurzel zur Spitze, lift + = hoch."""
    for i in range(1, 5):
        ph = 2 * math.pi * (speed * t) - i * 0.6 + phase0
        rot(f"Tail_{i}", UP, R(amp_deg) * math.sin(ph) * (0.5 + 0.25 * i))
        rot(f"Tail_{i}", LEFT, -R(lift_deg) / 4)


def gait(t, P, offsets, direction=FWD, turn=0.0):
    """Gangzyklus: Füße bewegen sich im Stand rückwärts (Körper läuft "in place" vorwärts), im Schwung
    vor + angehoben. turn (rad pro Zyklus) = auf der Stelle drehen statt laufen.
    P["foot_profile"] = "smooth" (optional, sonst altes Verhalten): weiche Fußbahn ohne Ruck – siehe smooth_foot()."""
    if P.get("foot_profile") == "smooth":
        return gait_smooth(t, P, offsets, direction, turn)
    S = P["stride"] * SIZE
    for leg in LEGS:
        swing, s = phase(t, offsets[leg], P["duty"])
        u = (0.5 - s) if not swing else (-0.5 + ease(s))      # +0,5 vorne … −0,5 hinten
        lift = P["lift_front" if leg[0] == "F" else "lift_back"] * HGT * math.sin(math.pi * s) if swing else 0.0
        if turn:
            r = REST[leg]["ball"] - DB["Root"].head_local
            r = Vector((r.x, r.y, 0))
            off = Quaternion(UP, -turn * u).to_matrix() @ r - r
        else:
            off = direction * (S * u)
        curl = R(P.get("toe_curl_deg", 30)) * math.sin(math.pi * s) if swing else 0.0
        set_foot(leg, off + Vector((0, 0, lift)), curl)


# ---------------------------------------------------------------- Weiche Bewegung (2026-11-17, Nutzer: "Roboter-Wolf")
# Alles hier ist OPTIONAL und wird nur von Clips benutzt, die es ausdrücklich aufrufen. Bestehende Funktionen oben
# behalten ihr Verhalten (Death-Clips u. a. bleiben Frame für Frame identisch).
def clamp01(x):
    return max(0.0, min(1.0, x))


def hermite(s, p0, p1, m0, m1):
    """Kubische Kurve von p0 nach p1 mit Anfangs-/Endsteigung m0/m1 (pro Einheit s)."""
    s2, s3 = s * s, s * s * s
    return (2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * m1


def bump(s, peak=0.5):
    """0 → 1 → 0 mit Steigung 0 an beiden Enden (weiches Abheben/Aufsetzen); Maximum bei `peak` (0..1)."""
    if s <= 0.0 or s >= 1.0:
        return 0.0
    g = math.log(0.5) / math.log(min(0.9, max(0.1, peak)))
    return math.sin(math.pi * s ** g) ** 2


def keys(x, pts, loop=False):
    """Weiche Kurve durch Schlüsselwerte [(x, wert), …] wie Blenders "Auto Clamped"-Keyframes: an Extremwerten
    flach (Bewegung bremst weich ab), zwischen gleichgerichteten Keys fließt sie ohne Halt durch, kein Überschwingen.
    loop=True: erster und letzter Key gleich, Steigung dort aus den Nachbarn (nahtlose Schleife)."""
    xs, vs = [p[0] for p in pts], [p[1] for p in pts]
    n = len(pts)
    if loop:
        x = xs[0] + (x - xs[0]) % (xs[-1] - xs[0])
    if x <= xs[0]:
        return vs[0]
    if x >= xs[-1]:
        return vs[-1]

    def slope(i):
        if i in (0, n - 1):
            if not loop:
                return 0.0
            dl = (vs[-1] - vs[-2]) / (xs[-1] - xs[-2])
            dr = (vs[1] - vs[0]) / (xs[1] - xs[0])
        else:
            dl = (vs[i] - vs[i - 1]) / (xs[i] - xs[i - 1])
            dr = (vs[i + 1] - vs[i]) / (xs[i + 1] - xs[i])
        if dl * dr <= 0:
            return 0.0                                   # Umkehrpunkt → flach
        m = (dl + dr) / 2
        return math.copysign(min(abs(m), 3 * abs(dl), 3 * abs(dr)), m)   # Fritsch-Carlson: nie überschwingen
    i = max(k for k in range(n - 1) if xs[k] <= x)
    h = xs[i + 1] - xs[i]
    return hermite((x - xs[i]) / h, vs[i], vs[i + 1], slope(i) * h, slope(i + 1) * h)


def wave(t, cycles=1.0, ph=0.0):
    """sin über den Zyklus: t 0..1, ph in Zyklus-Anteilen."""
    return math.sin(2 * math.pi * (cycles * t + ph))


def bend(names, axis, angles):
    """Jedem Knochen der Kette seinen eigenen Winkel geben (rad, um die Welt-Achse axis)."""
    for n, a in zip(names, angles):
        if a:
            rot(n, axis, a)


def follow(fn, x, n, lag, gain=1.0):
    """Nachziehen/Überlappen entlang einer Kette (Follow-Through): Glied i hat den Welt-Winkel
    gain^i · fn(x − i·lag), d. h. jedes Glied macht die Bewegung des vorherigen verzögert nach (gain > 1 = peitscht auf,
    z. B. Schwanz; gain < 1 = beruhigt, z. B. Kopf). fn(x) = Welt-Winkel des Elternknochens der Kette.
    Liefert die n LOKALEN Winkel (Differenz zum Vorgänger) – direkt für bend()."""
    w = [fn(x)] + [gain ** i * fn(x - i * lag) for i in range(1, n + 1)]
    return [w[i] - w[i - 1] for i in range(1, n + 1)]


SPINE = ("Hips", "Spine_1", "Chest")
NECK = ("Neck_1", "Neck_2", "Head")
TAIL = ("Tail_1", "Tail_2", "Tail_3", "Tail_4")


def gait_smooth(t, P, offsets, direction=FWD, turn=0.0):
    """Wie gait(), aber ohne Ruck an den Fußwechseln:
    - Schwung startet/endet mit genau der Geschwindigkeit des Standbeins (Fuß steht beim Aufsetzen relativ zum Boden still,
      statt aus Geschwindigkeit 0 zu beschleunigen) – swing_match 0..1 (1 = voll angeglichen).
    - Hubkurve bump(): Fuß verlässt den Boden/setzt auf mit vertikaler Geschwindigkeit 0, höchster Punkt bei lift_peak.
    - Zehen rollen weich ein (curl_peak) und strecken sich vor dem Aufsetzen.
    - reach_front/reach_back (Anteil Länge): Stand-Bereich der Vorder-/Hinterbeine nach vorn (+) / hinten (−) schieben."""
    S = P["stride"] * SIZE
    d = P["duty"]
    m = -(1 - d) / d * P.get("swing_match", 1.0)
    for leg in LEGS:
        swing, s = phase(t, offsets[leg], d)
        front = leg[0] == "F"
        shift = P.get("reach_front" if front else "reach_back", 0.0) * SIZE
        if swing:
            u = hermite(s, -0.5, 0.5, m, m)
            lift = P["lift_front" if front else "lift_back"] * HGT * bump(s, P.get("lift_peak", 0.4))
            curl = R(P.get("toe_curl_deg", 30)) * bump(s, P.get("curl_peak", 0.3))
            # Ausgreifen in der Luft (Galopp): nach dem Abdruck weit nach hinten strecken, vor dem Aufsetzen weit nach
            # vorn greifen und zum Aufsetzpunkt zurückziehen. Ein Bein in der Luft darf "zu kurz" sein (Bein gestreckt).
            ext = P.get("swing_ext_front" if front else "swing_ext_back", 0.0) * SIZE
            shift += ext * (bump(s, 0.75) - bump(s, 0.2))
        else:
            u, lift, curl = 0.5 - s, 0.0, 0.0
        if turn:
            r = REST[leg]["ball"] - DB["Root"].head_local
            r = Vector((r.x, r.y, 0))
            off = Quaternion(UP, -turn * u).to_matrix() @ r - r
        else:
            off = direction * (S * u + shift)
        set_foot(leg, off + Vector((0, 0, lift)), curl)


def _smooth_envelope(need, radius, loop):
    """Glatte Kurve ≥ need: erst Maximum über ±radius, dann Hann-gewichtetes Mittel über ±radius."""
    n = len(need)
    if radius <= 0 or n < 3:
        return list(need)
    core = need[:-1] if loop else need                   # Schleife: letzter Frame = erster
    m = len(core)

    def at(a, i):
        return a[i % m] if loop else a[max(0, min(m - 1, i))]
    dil = [max(at(core, i + k) for k in range(-radius, radius + 1)) for i in range(m)]
    w = [0.5 + 0.5 * math.cos(math.pi * k / (radius + 1)) for k in range(-radius, radius + 1)]
    out = [sum(wk * at(dil, i + k) for wk, k in zip(w, range(-radius, radius + 1))) / sum(w) for i in range(m)]
    return out + [out[0]] if loop else out


def chain_len(leg):
    return sum(DB[f"Leg_{leg}_{k}"].length for k in (1, 2, 3))   # Schulterblatt nicht mitgezählt (steif)


def reach_fix(margin=0.97, iters=4, legs=None):
    """Kann ein Bein sein Ziel nicht erreichen (überstreckt), sinkt der ganze Rumpf genau so weit ab, bis
    alle Ziele erreichbar sind – wie ein Tier, das beim weiten Ausgreifen tiefer geht. Liefert die Absenkung.
    legs (optional): nur diese Beine berücksichtigen (z. B. nur Standbeine – ein Bein in der Luft muss den Boden
    nicht erreichen, sonst zieht es den Rumpf in der Schwebephase nach unten)."""
    total = 0.0
    for _ in range(iters):
        bpy.context.view_layer.update()
        need = 0.0
        for leg in (LEGS if legs is None else legs):
            root = PB[f"Leg_{leg}_1"].head
            tgt = arm.matrix_world.inverted() @ IK[leg].matrix_world.translation
            d = tgt - root
            m = max(margin, REST_RATIO[leg] + 0.002)          # in Ruhe schon gestreckter → Ruhe ist die Grenze
            over = d.length - m * chain_len(leg)
            if over > 0 and root.z > tgt.z:
                # wie weit muss die Hüfte senkrecht runter, damit |d| = margin*L?
                h = math.sqrt(max(0.0, (m * chain_len(leg)) ** 2 - d.x ** 2 - d.y ** 2))
                need = max(need, (root.z - tgt.z) - h)
        if need <= 1e-5:
            break
        move("Root", Vector((0, 0, -need)))
        total += need
    return total


def ground_above():
    """Ragt irgendein Teil in den Boden, wird der Rumpf genau so weit angehoben (Füße bleiben per IK stehen)."""
    bpy.context.view_layer.update()
    dz = GROUND - mesh_min_z()
    if dz > 0:
        move("Root", Vector((0, 0, dz)))


def mesh_min_z():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_obj.evaluated_get(dg)
    m = ev.to_mesh()
    z = min((body_obj.matrix_world @ v.co).z for v in m.vertices)
    ev.to_mesh_clear()
    return z


_REST_EDGES = None


def max_stretch():
    """Größte Kantendehnung (Länge/Ruhelänge) des Mesh – misst, ob Gewichte reißen/verzerren."""
    global _REST_EDGES
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
        if l0 > 1e-4:
            r = (m.vertices[a].co - m.vertices[b].co).length / l0
            if r > worst:
                worst, wa = r, a
    ev.to_mesh_clear()
    gs = me.vertices[wa].groups
    global STRETCH_WHERE
    STRETCH_WHERE = body_obj.vertex_groups[max(gs, key=lambda g: g.weight).group].name if len(gs) else "?"
    return worst


# ---------------------------------------------------------------- Backen + Selbstprüfung
def bake(clips):
    """clips: {Name: {N, loop, kind (locomotion|stand|stand_return|death), pose(f), swing(leg,f), duty,
    planted: [Beine], events}}. Schreibt Actions <PREFIX>_<Name>, clips_report.json, events.json, quadruped_clips.blend."""
    C = ST["checks"]
    tol_c, tol_p = C["contact_tolerance"] * SIZE, C["planted_tolerance"] * SIZE
    arm.animation_data_create()
    report, events, baked = {}, {}, {}
    for cname in ST["meta"]["clips"]:
        spec = clips[cname]
        N, kind = spec["N"], spec["kind"]
        frames, feet, stretch, ev = [], {l: [] for l in LEGS}, 1.0, list(spec.get("events", []))
        prev, lowered, where = {}, 0.0, ""
        # Optional "reach_smooth": <Frames> – die nötige Rumpf-Absenkung (überstreckte Beine) wird vorab für alle Frames
        # gemessen und als glatte Kurve angewandt. Ohne das sackt der Rumpf an jedem Fußwechsel mit einem Knick ab
        # (Maximum über 4 Beine) – eine Hauptursache für "kantig/abrupt".
        pre = None
        stance_only = spec.get("reach_smooth") and kind == "locomotion"

        def reach_legs(f):                               # bei weichen Gangarten: nur Standbeine bestimmen die Höhe
            return [l for l in LEGS if not spec["swing"](l, f)] if stance_only else None
        if spec.get("reach_smooth") and kind != "death":
            need = []
            for f in range(N + 1):
                reset()
                spec["pose"](f)
                need.append(reach_fix(legs=reach_legs(f)))
            if __import__("os").environ.get("QUAD_DEBUG"):
                print("NEED", cname, [round(v, 3) for v in need], [reach_legs(f) for f in range(N + 1)])
            pre = _smooth_envelope(need, int(spec["reach_smooth"]), spec.get("loop", False))
            fl = spec.get("reach_flat", 0.0)               # 0..1: Anteil konstanter Absenkung (kein Auf/Ab durch Reichweite)
            if fl:
                top = max(pre)
                pre = [fl * top + (1 - fl) * v for v in pre]
            if kind == "stand_return":                   # Endpose = Ruhe (Rumpf nicht abgesenkt)
                pre = [v * (1 - ease((f - (N - spec["reach_smooth"])) / spec["reach_smooth"])) if need[-1] < 1e-5 else v
                       for f, v in enumerate(pre)]
        for f in range(N + 1):
            reset()
            spec["pose"](f)
            if pre is not None:
                move("Root", Vector((0, 0, -pre[f])))
                lowered = max(lowered, pre[f] + reach_fix(legs=reach_legs(f)))
            elif kind != "death":
                lowered = max(lowered, reach_fix())
            bpy.context.view_layer.update()
            frames.append({pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE",
                                                      to_space="LOCAL").copy() for pb in PB})
            for leg in LEGS:
                sw = spec["swing"](leg, f) if kind == "locomotion" else False
                if kind == "locomotion" and prev.get(leg) and not sw and f < N:
                    ev.append({"frame": f, "event": "footstep", "leg": leg})
                prev[leg] = sw
                feet[leg].append((tip(leg).copy(), ball(leg).copy(), sw, IK[leg].matrix_world.translation.copy()))
            if f % C.get("stretch_every", 3) == 0:
                st_now = max_stretch()
                if st_now > stretch:
                    stretch, where = st_now, f"{STRETCH_WHERE} @ Frame {f}"
        baked[cname] = frames
        r = {"frames": N, "seconds": round(N / FPS, 3), "loop": spec.get("loop", False)}
        # IK erreicht das Ziel? (sonst schwebt/rutscht der Fuß)
        reach = 0.0 if kind == "death" else max((b - tgt).length for s in feet.values() for _, b, sw, tgt in s if not sw)
        r["ik_reach_error_m"] = round(reach, 4)
        r["body_lowered_max_m"] = round(lowered, 4)
        if kind == "locomotion":
            fl, st_ = [], []
            for leg, s in feet.items():
                stance = [(t_, b) for t_, b, sw, _ in s if not sw]
                fl.append(max(abs(b.z - REST[leg]["ball"].z) for _, b in stance))
                xs = [b.x for _, b in stance]
                ys = [b.y for _, b in stance]
                st_.append(math.hypot(max(xs) - min(xs), max(ys) - min(ys)))
            r["foot_contact_max_m"] = round(max(fl), 4)
            r["foot_contact_ok"] = max(fl) <= tol_c and reach <= tol_c
            r["stride_m"] = [round(min(st_), 3), round(max(st_), 3)]
            r["moves_ok"] = min(st_) >= C["min_stride"] * SIZE
            if spec.get("turn"):
                r["turn_speed_deg_s"] = round(math.degrees(spec["turn"]) / (N / FPS), 1)
            else:
                r["move_speed_mps"] = round(sum(st_) / len(st_) / (spec["duty"] * N / FPS), 3)
        if kind in ("stand", "stand_return"):
            planted = spec.get("planted", LEGS)
            mv = max((t_ - feet[l][0][0]).length for l in planted for t_, _, _, _ in feet[l])
            r["feet_moved_max_m"] = round(mv, 4)
            r["feet_planted_ok"] = mv <= tol_p and reach <= tol_p
        if r["loop"]:
            jump = max((frames[0][n].translation - frames[N][n].translation).length +
                       (frames[0][n].to_quaternion().rotation_difference(frames[N][n].to_quaternion()).angle)
                       for n in frames[0])
            r["loop_ok"] = jump < 1e-3
        if kind == "stand_return":
            r["returns_to_rest"] = all(frames[N][n].translation.length < 1e-3 and
                                       frames[N][n].to_quaternion().angle < 1e-2 for n in frames[N] if not n.startswith("Leg_"))
        if kind == "death":
            reset()
            spec["pose"](N)
            bpy.context.view_layer.update()
            z = mesh_min_z()
            r["final_min_z_vs_ground_m"] = round(z - GROUND, 4)
            r["no_ground_penetration"] = z >= GROUND - tol_c
        r["max_stretch"] = round(stretch, 2)
        r["stretch_at"] = where if stretch > 1.0 else ""
        r["stretch_ok"] = round(stretch, 2) <= (spec.get("max_stretch") or C["max_stretch"])
        oks = [v for k, v in r.items() if (k.endswith("_ok") and k != "stretch_ok")   # Dehnung = nur Info, bremst nie
               or k in ("returns_to_rest", "no_ground_penetration")]
        r["ok"] = all(oks)
        report[f"{PREFIX}_{cname}"] = r
        events[f"{PREFIX}_{cname}"] = ev
        print("CLIP", f"{PREFIX}_{cname}", json.dumps(r, ensure_ascii=False))
    # Constraints + Empties weg, dann die gesammelten Posen als Keyframes schreiben (reines FK für Unity)
    for pb in PB:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
    for e in IK.values():
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
