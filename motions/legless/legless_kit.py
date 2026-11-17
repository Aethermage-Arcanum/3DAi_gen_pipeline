"""Gemeinsamer Baukasten der Beinlos-Muster (motions/legless/<muster>/<muster>_clips.py).

Prinzip: Krümmungswellen entlang der Wirbelkette (Spine_01 = Schwanzspitze … Spine_n = hinter dem Kopf).
keep_centered() hält Blickrichtung + Körpermitte fest (Clips laufen "in place"), ground() sorgt für
Bodenkontakt ohne Einsinken. Gebacken wird direkt als FK (keine Constraints nötig).
"""
import json
import math
import pathlib
import sys
import tomllib

import bpy
from mathutils import Quaternion, Vector

UP, FWD, LEFT = Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))
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
    global OUT, ST, FPS, PREFIX, arm, body_obj, PB, DB, SPINE, NSEG, SIZE, HGT, GROUND, sc, REST_DIR, REST_MID
    a = sys.argv[sys.argv.index("--") + 1:]
    OUT = pathlib.Path(a[0]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    ST = load_style(style_dir, a[1] if len(a) > 1 else None)
    FPS, PREFIX = ST["meta"]["fps"], ST["meta"]["clip_prefix"]
    sc = bpy.context.scene
    sc.render.fps = FPS
    arm = bpy.data.objects["Legless_Rig"]
    body_obj = bpy.data.objects["Body_Mesh"]
    PB, DB = arm.pose.bones, arm.data.bones
    for pb in PB:
        pb.rotation_mode = "QUATERNION"
    SPINE = sorted([b.name for b in DB if b.name.startswith("Spine_")])
    NSEG = len(SPINE)
    xs = [b.head_local.x for b in DB] + [b.tail_local.x for b in DB]
    SIZE = max(xs) - min(xs)
    reset()
    bpy.context.view_layer.update()
    GROUND = mesh_min_z()
    HGT = max(b.head_local.z for b in DB) - GROUND
    REST_DIR, REST_MID = heading(), spine_mid()
    print(f"LEGLESS_INIT Länge {SIZE:.3f} m, {NSEG} Wirbel, Stil {ST['meta']['skeleton']}/{ST['meta']['style']}")


def reset():
    for pb in PB:
        pb.rotation_quaternion = Quaternion()
        pb.location = Vector()


def rot(name, axis_world, angle):
    ax = (DB[name].matrix_local.to_3x3().inverted() @ axis_world).normalized()
    PB[name].rotation_quaternion = PB[name].rotation_quaternion @ Quaternion(ax, angle)


def move(name, vec_world):
    PB[name].location = PB[name].location + DB[name].matrix_local.to_3x3().inverted() @ vec_world


def ease(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def heading():
    """Waagerechte Richtung vom Kopfansatz zur Nase (Weltraum)."""
    bpy.context.view_layer.update()
    h = arm.matrix_world @ PB["Head"].tail - arm.matrix_world @ PB["Head"].head
    return Vector((h.x, h.y, 0)).normalized()


def spine_mid():
    bpy.context.view_layer.update()
    pts = [arm.matrix_world @ PB[n].head for n in SPINE]
    c = sum(pts, Vector()) / len(pts)
    return Vector((c.x, c.y, 0))


# ---------------------------------------------------------------- Bausteine
def seg_frac(i):
    return (i + 0.5) / NSEG                      # 0 = Schwanzspitze … 1 = Kopfansatz


def wave(t, amp_deg, waves, lo=0.0, hi=1.0, axis=None, taper_head=0.6, phase0=0.0):
    """Wandernde Krümmungswelle (Kopf → Schwanz) auf den Wirbeln im Bereich [lo, hi] der Körperlänge.
    axis = UP (seitlich, Standard) oder LEFT (auf/ab)."""
    axis = axis or UP
    for i, n in enumerate(SPINE):
        f = seg_frac(i)
        if not lo <= f <= hi:
            continue
        env = math.sin(math.pi * min(1.0, f / 0.85)) ** 0.5             # Schwanzspitze + Kopf ruhiger
        if f > 0.85:
            env *= taper_head
        ph = 2 * math.pi * t + 2 * math.pi * waves * f + phase0
        rot(n, axis, R(amp_deg) * env * math.sin(ph) / NSEG * 6)


def bend(lo, hi, deg, axis=None):
    """Gleichmäßige Krümmung (deg gesamt) über den Bereich [lo, hi]. axis LEFT: + = Vorderteil hoch."""
    axis = axis or UP
    segs = [n for i, n in enumerate(SPINE) if lo <= seg_frac(i) <= hi]
    for n in segs:
        rot(n, axis, R(deg) / max(1, len(segs)) * (-1 if axis == LEFT else 1))


def head(pitch=0.0, yaw=0.0, level=0.0):
    """pitch + = Kopf hoch. level 0..1 richtet den Kopf waagerecht aus (gleicht Hals-Neigung aus)."""
    if level:
        bpy.context.view_layer.update()
        d = (arm.matrix_world.to_3x3() @ (PB["Head"].tail - PB["Head"].head)).normalized()
        rest = (DB["Head"].tail_local - DB["Head"].head_local).normalized()
        dz = math.asin(max(-1, min(1, d.z))) - math.asin(max(-1, min(1, rest.z)))
        neck_spread("Head", LEFT, dz * level)
    if pitch:
        neck_spread("Head", LEFT, -pitch)
    if yaw:
        neck_spread("Head", UP, yaw)


def neck_spread(_, axis, angle):
    """Kopfdrehung auf Kopf + die letzten beiden Wirbel verteilen (ein Gelenk allein reißt das Mesh)."""
    for n in (SPINE[-2], SPINE[-1], "Head"):
        rot(n, axis, angle / 3)


def jaw(open_deg):
    rot("Jaw", LEFT, R(open_deg))


def keep_centered(dx=0.0, keep_heading=True):
    """Blickrichtung (Kopf) und Körpermitte auf Ruhewerte zurückholen (+ dx nach vorn verschieben)."""
    if keep_heading:
        d = heading()
        ang = math.atan2(REST_DIR.y, REST_DIR.x) - math.atan2(d.y, d.x)
        PB["Root"].rotation_quaternion = Quaternion(
            (DB["Root"].matrix_local.to_3x3().inverted() @ UP).normalized(), ang) @ PB["Root"].rotation_quaternion
    off = REST_MID + Vector((dx, 0, 0)) - spine_mid()
    move("Root", Vector((off.x, off.y, 0)))


def ground(mode="contact", lift=0.0):
    """contact: tiefster Punkt genau auf dem Boden · above: nur anheben, falls etwas einsinkt."""
    bpy.context.view_layer.update()
    dz = GROUND + lift - mesh_min_z()
    if mode == "contact" or dz > 0:
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


# ---------------------------------------------------------------- Backen + Selbstprüfung
def bake(clips):
    """clips: {Name: {N, loop, kind (locomotion|stand|stand_return|death), pose(f), grounded, events}}"""
    C = ST["checks"]
    tol = C["ground_tolerance"] * SIZE
    arm.animation_data_create()
    report, events = {}, {}
    for cname in ST["meta"]["clips"]:
        spec = clips[cname]
        N, kind = spec["N"], spec["kind"]
        act = bpy.data.actions.new(f"{PREFIX}_{cname}")
        act.use_fake_user = True
        arm.animation_data.action = act
        mins, stretch, where, first, last = [], 1.0, "", None, None
        for f in range(N + 1):
            reset()
            spec["pose"](f)
            bpy.context.view_layer.update()
            for pb in PB:
                pb.keyframe_insert("rotation_quaternion", frame=f)
                pb.keyframe_insert("location", frame=f)
            mats = {pb.name: pb.matrix.copy() for pb in PB}
            first = first or mats
            last = mats
            mins.append(mesh_min_z() - GROUND)
            if f % C.get("stretch_every", 3) == 0:
                s = max_stretch()
                if s > stretch:
                    stretch, where = s, f"{STRETCH_WHERE} @ Frame {f}"
        r = {"frames": N, "seconds": round(N / FPS, 3), "loop": spec.get("loop", False)}
        r["lowest_point_m"] = [round(min(mins), 4), round(max(mins), 4)]
        r["no_ground_penetration"] = min(mins) >= -tol
        if spec.get("grounded", kind == "locomotion"):
            r["ground_contact_ok"] = max(mins) <= tol
        if r["loop"]:
            jump = max((first[n].translation - last[n].translation).length for n in first)
            r["loop_ok"] = jump < 1e-3
        if kind == "stand_return":
            r["returns_to_rest"] = all((last[n].translation - DB[n].matrix_local.translation).length < 1e-3 for n in last)
        r["max_stretch"] = round(stretch, 2)
        r["stretch_at"] = where
        r["stretch_ok"] = round(stretch, 2) <= (spec.get("max_stretch") or C["max_stretch"])
        oks = [v for k, v in r.items() if k.endswith("_ok") or k in ("returns_to_rest", "no_ground_penetration")]
        r["ok"] = all(oks)
        report[f"{PREFIX}_{cname}"] = r
        events[f"{PREFIX}_{cname}"] = list(spec.get("events", []))
        print("CLIP", f"{PREFIX}_{cname}", json.dumps(r, ensure_ascii=False))
    arm.animation_data.action = bpy.data.actions[f"{PREFIX}_{ST['meta']['clips'][0]}"]
    summary = {"style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}", "variant": ST["meta"]["variant"],
               "clips": report, "all_ok": all(r["ok"] for r in report.values())}
    (OUT / "clips_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "events.json").write_text(json.dumps({"fps": FPS, "clips": events}, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "clips.blend"))
    print("CLIPS_OK", summary["all_ok"])
