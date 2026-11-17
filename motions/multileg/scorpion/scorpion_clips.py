"""Bewegungsmuster multileg/scorpion: Gang (alternierende Beingruppen), Drehen, Idle, Drohen, Stich, Treffer, Tod.
Nutzt den Beine-Baukasten ../multileg_kit.py (Blender-IK für beliebig viele Beine).

& "D:\\Blender\\blender.exe" -b <multileg_rigged.blend> -P motions/multileg/scorpion/scorpion_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import multileg_kit as K  # noqa: E402

K.init(HERE)
from multileg_kit import FWD, LEFT, UP, R, body, ease, gait, ik_off, phase, rot  # noqa: E402

ST, SIZE, HGT, LEGS = K.ST, K.SIZE, K.HGT, K.LEGS
CLAWS = sorted({b.name[5] for b in K.DB if b.name.startswith("Claw_")})
TAIL = [n for n in ("Tail_1", "Tail_2", "Tail_3", "Tail_4", "Tail_5", "Stinger") if n in K.DB]


def offsets(P):
    """Gruppe A = L1 R2 L3 R4 L5 …, Gruppe B gegenphasig; kleine Welle von vorn nach hinten."""
    out = {}
    for leg in LEGS:
        k = int(leg[1:])
        a = (leg[0] == "L") == (k % 2 == 1)
        out[leg] = (0.0 if a else 0.5) + P.get("wave", 0) * (k - 1)
    return out


def claws(raise_deg=0.0, spread_deg=0.0, pinch_deg=0.0):
    for s in CLAWS:
        sg = 1 if s == "L" else -1
        rot(f"Claw_{s}_1", LEFT, -R(raise_deg))
        rot(f"Claw_{s}_1", UP, sg * R(spread_deg))
        rot(f"Claw_{s}_3", UP, -sg * R(pinch_deg))


def tail(curl_deg=0.0, sway_deg=0.0, t=0.0):
    """NUR NOCH FÜR DEN TOD (Death-Clip bleibt unverändert, Nutzer-Anweisung). curl + = Schwanz weiter nach vorn über den Rücken krümmen, sway = seitlich pendeln."""
    for i, n in enumerate(TAIL):
        rot(n, LEFT, R(curl_deg) / len(TAIL))
        rot(n, UP, R(sway_deg) * math.sin(2 * math.pi * t - i * 0.5) / len(TAIL) * 2)



# ---------------------------------------------------------------- Schwanz mit absoluter Form (seit 2026-11-17)
# Nutzer-Feedback: Stich bog nur die Wurzel/rollte den Schwanz ein → Stachel zeigte in den eigenen Rücken.
# Jetzt gibt jeder Clip die Neigung JEDES Glieds vor (K.chain_pose); Biegung = Summe über alle Gelenke.
TREST = K.chain_rest(TAIL)
REST_P = [c["pitch"] for c in TREST]


def tail_shape(pitch=None, bend=None, yaw=None, body_pitch=0.0):
    """pitch: absolute Neigung je Glied (rad, None = Ruheform). bend/yaw: zusätzliche Biegung je GELENK (rad),
    wird entlang der Kette aufsummiert (Wurzel biegt alles dahinter mit). body_pitch: Rumpf-Neigung (Schwanz
    sitzt am Rumpf und kippt mit)."""
    p = list(pitch or REST_P)
    ap = ay = 0.0
    ps, ys = [], []
    for i in range(len(TAIL)):
        ap += bend[i] if bend else 0.0
        ay += yaw[i] if yaw else 0.0
        ps.append(p[i] + ap + body_pitch)
        ys.append(ay)
    K.chain_pose(TAIL, ps, ys)


def wave(amp_deg, t, lag=0.6, grow=0.0):
    """Welle von der Wurzel zur Spitze: Biegung je Gelenk (rad); grow > 0 = zur Spitze hin stärker."""
    n = len(TAIL)
    return [R(amp_deg) / n * 2 * (1 + grow * i / (n - 1)) * math.sin(2 * math.pi * t - i * lag) for i in range(n)]


def blend(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def cocked(P):
    """Ausholen/Drohen: Schwanz hoch über dem Rücken gespannt, Stachel waagerecht nach vorn (auf den Gegner)."""
    return [R(v) for v in P["cock_pitch_deg"]]


def tail_root():
    bpy.context.view_layer.update()
    return K.PB[TAIL[0]].head.copy()        # Armature-Raum


def strike_target(P):
    """Zielpunkt vor dem Skorpion in Angriffshöhe (zwischen den Scheren, Mitte)."""
    x0 = K.DB["Root"].head_local.x
    return Vector((x0 + P["target_ahead"] * SIZE, K.DB["Root"].head_local.y, K.GROUND + P["target_height"] * HGT))


# Prüfung "Stachel zeigt nie in den eigenen Körper": Strahl ab Stachelspitze gegen das Mesh ohne Schwanz
_BVH = None


def self_aim():
    """Abstand (m), nach dem der Strahl der Stachelrichtung den eigenen Körper (ohne Schwanz) trifft, sonst None."""
    global _BVH
    from mathutils.bvhtree import BVHTree
    bo = K.body_obj
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bo.evaluated_get(dg)
    m = ev.to_mesh()
    if _BVH is None:
        tail_vg = {bo.vertex_groups[n].index for n in TAIL if n in bo.vertex_groups}
        _BVH = [p.index for p in bo.data.polygons
                if not any(bo.data.vertices[v].groups and max(bo.data.vertices[v].groups, key=lambda g: g.weight).group
                           in tail_vg for v in p.vertices)]
    verts = [bo.matrix_world @ v.co for v in m.vertices]
    polys = [tuple(m.polygons[i].vertices) for i in _BVH]
    ev.to_mesh_clear()
    tree = BVHTree.FromPolygons(verts, polys)
    pb = K.PB["Stinger"]
    h, t = K.arm.matrix_world @ pb.head, K.arm.matrix_world @ pb.tail
    hit = tree.ray_cast(t, (t - h).normalized(), 0.4 * SIZE)
    return None if hit[0] is None else hit[3]


def self_probe(N, extra=None):
    """Prüfung je Clip: In keinem Frame zeigt der Stachel (Strahl ab Spitze, 0,4 × Körperlänge) in den eigenen Körper.
    extra(f) kann weitere Messwerte liefern (Attack: Treffer am Zielpunkt)."""
    frames = []

    def probe(f):
        out = dict(extra(f) or {}) if extra else {}
        if self_aim() is not None:
            frames.append(f)
        if f == N:
            out.update({"sting_self_aim_frames": list(frames), "sting_never_self_ok": not frames})
        return out
    return probe


def tail_life(P, t, n_wave=1):
    """Schwanz lebt über die ganze Länge: Heben/Senken + seitliches Pendeln als Welle Wurzel → Spitze."""
    return (wave(P.get("tail_bob_deg", 0), n_wave * t, lag=0.7, grow=0.5),
            wave(P.get("tail_sway_deg", 0), n_wave * t + 0.25, lag=0.6, grow=0.5))


def locomotion(P, turn=0.0):
    N, off = P["cycle_frames"], offsets(P)

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=turn) if turn else gait(t, P, off)
        body(dz=-P.get("bob", 0) * HGT * math.cos(4 * math.pi * t))
        claws(raise_deg=P.get("claw_raise_deg", 0))
        bend, yaw = tail_life(P, t, n_wave=2)        # zwei Wellen pro Zyklus (Schritt-Takt)
        tail_shape(bend=bend, yaw=yaw)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "turn": turn,
            "max_stretch": P.get("max_stretch"), "probe": self_probe(N),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        body(dz=0.003 * HGT * math.sin(2 * math.pi * 2 * t))
        for s in CLAWS:
            sg = 1 if s == "L" else -1
            rot(f"Claw_{s}_3", UP, -sg * R(P["claw_deg"]) * max(0, math.sin(2 * math.pi * 2 * t + (0 if s == "L" else math.pi))))
        bend, yaw = tail_life(P, t)
        tail_shape(bend=bend, yaw=yaw)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "probe": self_probe(N)}


def clip_ready(P):
    """Drohen (Naturvideo: Schwanz hoch gespannt, Stachel zeigt nach vorn auf den Gegner, Scheren offen nach vorn)."""
    N = P["frames"]
    shape = blend(REST_P, cocked(ST["attack1"]), P["tail_cock"])

    def pose(f):
        t = f / N
        body(dz=P["raise"] * HGT, roll=R(P["tremble_deg"]) * math.sin(2 * math.pi * 5 * t))
        claws(raise_deg=P["claw_raise_deg"], spread_deg=P["claw_spread_deg"])
        tw = [R(P["tail_tremble_deg"]) * math.sin(2 * math.pi * 5 * t - i * 0.9) for i in range(len(TAIL))]
        sw = wave(P["tail_sway_deg"], t, lag=0.6, grow=0.5)
        tail_shape(pitch=shape, bend=tw, yaw=sw)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"), "probe": self_probe(N)}


def clip_attack1(P):
    """Stich nach Naturvideo (offener Stich, Deathstalker/Kaiserskorpion): Ausholen – Schwanz spannt sich hoch über
    dem Rücken, Rumpf lehnt zurück, Scheren öffnen; Zustoßen – Schwanz streckt sich über den Kopf nach vorn, die
    Stachelspitze trifft den Zielpunkt frontal, Gewicht nach vorn, Scheren packen zu; kurz halten (hit); zurück."""
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    T = strike_target(P)
    COCK = cocked(P)

    def phases(f):
        if f <= w:
            return ease(f / w), 0.0, 0.0
        if f <= s:
            x = ((f - w) / (s - w)) ** 1.5            # zuschnappen: beschleunigt bis zum Treffer
            return 1 - x, x, 0.0
        if f <= h:
            return 0.0, 1.0, math.sin(math.pi * (f - s) / (h - s))    # kurzes Nachdrücken im Halten
        return 0.0, 1 - ease((f - h) / (N - h)), 0.0

    def pose(f):
        k_w, k_s, push = phases(f)
        bp = R(P["body_back_pitch_deg"]) * k_w - R(P["body_fwd_pitch_deg"]) * k_s
        body(dx=(-P["body_back"] * k_w + P["body_fwd"] * k_s) * SIZE, dz=0.04 * HGT * (k_w + k_s), pitch=bp)
        claws(raise_deg=P["claw_open_raise_deg"] * k_w + 4 * k_s,
              spread_deg=P["claw_open_deg"] * k_w - 6 * k_s, pinch_deg=P["claw_grab_deg"] * k_s)
        if k_s == 0:                                   # Ausholen: Ruheform → gespannte Form
            K.chain_pose(TAIL, [p + bp for p in blend(REST_P, COCK, k_w)])
            return
        tgt = T + Vector((P["push"] * SIZE * push, 0, -0.5 * P["push"] * SIZE * push))
        hit, _ = K.chain_reach(TAIL, tail_root(), tgt, R(P["strike_base_deg"]), R(P["strike_aim_deg"]))
        src = COCK if f <= s else REST_P               # Zustoßen aus der gespannten Form, Rückweg zur Ruheform
        K.chain_pose(TAIL, blend([p + bp for p in src], hit, k_s))

    def on_target(f):
        if f != P["hit_frame"]:
            return None
        pb = K.PB["Stinger"]
        tip, head = pb.tail.copy(), pb.head.copy()
        pitch = math.degrees(math.atan2(tip.z - head.z, tip.x - head.x))     # 0 = waagerecht nach vorn
        out = {"sting_target": [round(v, 3) for v in T], "sting_tip": [round(v, 3) for v in tip],
               "sting_tip_to_target_m": round((tip - T).length, 3), "sting_pitch_deg": round(pitch, 1)}
        # Treffer: Spitze am Zielpunkt UND Stachel zeigt frontal nach vorn (nicht nach unten/hinten in den Körper)
        out["sting_on_target_ok"] = out["sting_tip_to_target_m"] <= 0.03 * SIZE and -50 <= pitch <= 10
        return out
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch"),
            "probe": self_probe(N, on_target), "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    """Ruck zurück; der Schwanz zuckt nach hinten/oben weg, verzögert entlang der Kette (Wurzel zuerst, Spitze zuletzt)."""
    N = P["frames"]

    def pulse(x):
        x = max(0.0, min(1.0, x))
        return math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)

    def pose(f):
        x = f / N
        k = 0.0 if f in (0, N) else pulse(x)
        body(dx=-P["jolt"] * SIZE * k, roll=R(P["roll_deg"]) * k)
        claws(raise_deg=-10 * k, spread_deg=-8 * k)
        n = len(TAIL)
        lag = P["tail_lag"]
        bend = [R(P["tail_recoil_deg"]) / n * 2 * pulse((x - i * lag) / (1 - i * lag)) for i in range(n)]
        yaw = [R(P["tail_whip_deg"]) / n * 2 * pulse((x - i * lag) / (1 - i * lag)) for i in range(n)]
        tail_shape(bend=bend, yaw=yaw)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose, "probe": self_probe(N)}


def clip_death(P):
    """Krabbler-Tod: über die Längsachse auf den Rücken kippen (ganzer Körper dreht mit → keine Gelenk-
    Verzerrung), IK aus, Beine in der Luft. Jeder Frame liegt genau auf dem Boden auf."""
    from mathutils import Quaternion
    N, c1 = P["frames"], P["collapse_end"]
    h0 = K.DB["Root"].head_local
    piv = K.DB["Hips"].head_local.copy()

    def pose(f):
        k = ease(f / c1)
        q = Quaternion(FWD, math.pi * k * P.get("flip_side", 1))
        rot("Root", FWD, math.pi * k * P.get("flip_side", 1))
        K.move("Root", (piv - h0) - q @ (piv - h0))
        for leg in LEGS:
            ik_off(leg, ease(k / 0.3))
        claws(raise_deg=10 * k)
        tail(curl_deg=-P["tail_drop_deg"] * k)
        bpy.context.view_layer.update()
        K.move("Root", Vector((0, 0, K.GROUND - K.mesh_min_z())))     # liegt auf dem Boden (nicht drin, nicht drüber)
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
