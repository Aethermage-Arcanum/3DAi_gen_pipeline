"""Gemeinsamer Baukasten der Schwebe-Muster (motions/floater/<muster>/<muster>_clips.py).

Prinzip: Core (Kern) schwebt und neigt sich, Tentakel-Ketten (Tent_NN_k) bekommen Wellen mit Phasenversatz
entlang der Kette, Nachschleppen (trail) in Bewegungsrichtung und Spreizen (spread) nach außen.
Gebacken wird direkt als FK. Prüfung: schwebt (nie im Boden), Tod liegt am Boden, Mesh-Dehnung, Schleifen.
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


def init(style_dir):
    global OUT, ST, FPS, PREFIX, arm, body_obj, PB, DB, TENT, SIZE, GROUND, sc, _TINFO
    _TINFO = None
    a = sys.argv[sys.argv.index("--") + 1:]
    OUT = pathlib.Path(a[0]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    ST = tomllib.loads((pathlib.Path(style_dir) / "style.toml").read_text(encoding="utf-8"))
    for clip, base in ST.get("meta", {}).get("inherit", {}).items():
        ST[clip] = merge(ST.get(base, {}), ST.get(clip, {}))
    if len(a) > 1:
        mo = tomllib.loads(pathlib.Path(a[1]).read_text(encoding="utf-8")).get("motion", {})
        ST = merge(ST, {k: v for k, v in mo.items() if isinstance(v, dict)})
    FPS, PREFIX = ST["meta"]["fps"], ST["meta"]["clip_prefix"]
    sc = bpy.context.scene
    sc.render.fps = FPS
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    body_obj = bpy.data.objects["Body_Mesh"]
    PB, DB = arm.pose.bones, arm.data.bones
    for pb in PB:
        pb.rotation_mode = "QUATERNION"
    TENT = {}
    for b in DB:
        if b.name.startswith("Tent_"):
            TENT.setdefault(b.name.rsplit("_", 1)[0], []).append(b.name)
    for k in TENT:
        TENT[k].sort(key=lambda n: int(n.rsplit("_", 1)[1]))
    pts = [b.head_local for b in DB] + [b.tail_local for b in DB]
    SIZE = max(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3))
    reset()
    bpy.context.view_layer.update()
    GROUND = mesh_min_z()
    print(f"FLOATER_INIT {len(TENT)} Tentakel, Größe {SIZE:.3f} m, Stil {ST['meta']['skeleton']}/{ST['meta']['style']}")


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


def core(dz=0.0, dx=0.0, pitch=0.0, roll=0.0, yaw=0.0):
    """Kern bewegen/neigen (pitch + = nach vorn kippen)."""
    move("Root", Vector((dx, 0, dz)))
    if pitch:
        rot("Core", LEFT, pitch)
    if roll:
        rot("Core", FWD, roll)
    if yaw:
        rot("Core", UP, yaw)


def radial(name):
    d = DB[TENT[name][-1]].tail_local - DB["Core"].head_local
    h = Vector((d.x, d.y, 0))
    return h.normalized() if h.length > 1e-6 else FWD


def tentacles(t, amp_deg, speed=1.0, phase_step=0.9, trail_deg=0.0, spread_deg=0.0, curl_deg=0.0, only=None):
    """Wellen entlang jeder Tentakel-Kette (Spitze schwingt mehr), trail = nach hinten schleppen,
    spread = vom Kern weg nach außen spreizen, curl = einrollen (zur Mitte)."""
    for i, (name, bones) in enumerate(TENT.items()):
        if only and name not in only:
            continue
        r = radial(name)
        side_ax = UP.cross(r).normalized()                 # Achse quer zur Tentakel-Richtung
        n = len(bones)
        for k, b in enumerate(bones):
            w = (k + 1) / n
            ph = 2 * math.pi * speed * t - k * phase_step + i * 1.3
            rot(b, side_ax, R(amp_deg) * w * math.sin(ph) / max(n, 3) * 2)   # kurze Stummel schwingen nicht stärker
            rot(b, r, R(amp_deg) * 0.6 * w * math.cos(ph) / max(n, 3) * 2)
            if trail_deg:
                rot(b, LEFT, -R(trail_deg) / max(n, 3))
            if spread_deg:                                   # über die Kette verteilt (nur Wurzel reißt)
                rot(b, side_ax, -R(spread_deg) * 1.6 / n * (1.0 if k < n - 1 else 0.4))
            if curl_deg:
                rot(b, side_ax, R(curl_deg) / n)


# ---------------------------------------------------------------------------------------------------------------
# Wabbel-Tentakel (2026-11-17, Nutzer: "Tentakel sind bis an die Wurzel wabbelig"). Neu, optional – tentacles() oben
# bleibt unverändert (Death benutzt es weiter). Zwei Schichten, beide über die GANZE Kette ab der Wurzel:
#   1. freie Welle: läuft von der Wurzel zur Spitze (Phasenverzug pro Knochen), Wurzel biegt sich root_weight × so
#      stark wie die Spitze, 2. Achse mit eigener Phase/Frequenz → Ellipsen/Achten statt Pendel; Phase je Tentakel anders.
#   2. Nachschwingen (drive): jeder Tentakel-Ansatz ist eine gedämpfte Feder, angeregt von der Beschleunigung des
#      Kerns an genau dieser Stelle (Wippen, Vorschnellen, Rückstoß, Drehen). Die Antwort läuft mit lag_frames
#      Verzug pro Knochen zur Spitze → Peitschen-/Schleppwelle. Loops: exakt periodische Lösung (FFT), sonst Zeitschritte.
# Werte: [wobble] in style.toml.

def _wcfg():
    return ST.get("wobble", {})


def tent_info():
    """Pro Tentakel (Name): Ansatz (Ruhe, Armatur-Raum), Richtung Wurzel→Spitze, Länge, Phase."""
    global _TINFO
    if _TINFO is None:
        _TINFO = {}
        for i, (name, bones) in enumerate(TENT.items()):
            h, tl = DB[bones[0]].head_local, DB[bones[-1]].tail_local
            L = sum((DB[b].tail_local - DB[b].head_local).length for b in bones)
            gold = (i * 0.6180339887) % 1.0
            _TINFO[name] = {"root": h.copy(), "dir": (tl - h).normalized(), "L": max(L, 1e-4),
                            "phase": 2 * math.pi * gold, "phase2": 2 * math.pi * ((i * 0.7548776662) % 1.0),
                            "f2": 1 + (i % 2), "i": i}
    return _TINFO


_TINFO = None


def drive(state_fn, N, loop):
    """Nachschwingen vorberechnen. state_fn(f) → dict für core(). Ergebnis: {tentakel: [Vector (Frame 0..N)]} =
    Auslenkung der Feder (m, im Kern-Raum), daraus winkelt wobble() die Kette ab."""
    W = _wcfg()
    TI = tent_info()
    rest_c = DB["Core"].matrix_local
    pad = 0 if loop else 8
    frames = list(range(-pad, N + pad + 1))
    mats = {}
    for f in frames:
        reset()
        core(**state_fn(min(max(f, 0), N) if not loop else f % N))
        bpy.context.view_layer.update()
        mats[f] = PB["Core"].matrix @ rest_c.inverted()
    reset()
    dt = 1.0 / FPS
    out = {}
    for name, ti in TI.items():
        P = {f: (mats[f] @ ti["root"]) for f in frames}
        Rinv = {f: mats[f].to_3x3().inverted() for f in frames}
        T0 = W.get("period_s", 0.75) * math.sqrt(ti["L"] / (W.get("ref_length", 0.35) * SIZE))
        w0, z = 2 * math.pi / T0, W.get("damping", 0.3)
        if loop:
            import numpy as np
            acc = np.array([list(Rinv[f] @ ((P[(f + 1) % N] - 2 * P[f] + P[(f - 1) % N]) / dt ** 2)) for f in range(N)])
            w = 2 * math.pi * np.fft.fftfreq(N, dt)
            H = 1.0 / (w0 ** 2 - w ** 2 + 2j * z * w0 * w)
            X = np.fft.fft(-acc, axis=0) * H[:, None]
            out[name] = {"X": X, "w": w, "N": N}
        else:
            x, v, xs = Vector(), Vector(), {}
            sub = 8
            for f in frames:
                fa, fb = max(f - 1, frames[0]), min(f + 1, frames[-1])
                a = Rinv[f] @ ((P[fb] - 2 * P[f] + P[fa]) / dt ** 2) if fb - fa == 2 else Vector()
                for _ in range(sub):
                    h = dt / sub
                    v += (-a - w0 * w0 * x - 2 * z * w0 * v) * h
                    x += v * h
                xs[f] = x.copy()
            out[name] = {"xs": xs, "N": N}
    return out


def _drive_at(D, f):
    """Federauslenkung zum (evtl. gebrochenen) Frame f."""
    if "X" in D:
        import numpy as np
        N = D["N"]
        ph = np.exp(1j * D["w"] * (f / FPS))                # periodisch, auch für gebrochene f
        x = (D["X"] * ph[:, None]).sum(0).real / N
        return Vector(x)
    xs = D["xs"]
    lo = math.floor(f)
    if lo < min(xs):
        return Vector()
    a, b = xs.get(lo, Vector()), xs.get(lo + 1, xs.get(lo, Vector()))
    return a.lerp(b, f - lo)


def wobble(t, amp_deg, speed=1, trail_deg=0.0, spread_deg=0.0, curl_deg=0.0, turn_deg=0.0,
           drv=None, f=0, env=1.0):
    """Tentakel über die ganze Länge bewegen (siehe Kommentar oben). t = Anteil des Loops (0..1),
    speed = ganze Wellen pro Loop, turn_deg = Kurven-Schleppen (+ = Tentakel bleiben rechts zurück bei Linkskurve),
    drv/f = Nachschwingen aus drive(), env = Hüllkurve (0 = Ruhe) für Nicht-Loops."""
    W = _wcfg()
    rw, step, swirl = W.get("root_weight", 0.55), W.get("phase_step", 0.7), W.get("swirl", 0.6)
    lag, gain, dmax = W.get("lag_frames", 2.0), W.get("drag_gain", 3.0), R(W.get("drag_max_deg", 45))
    TI = tent_info()
    for name, bones in TENT.items():
        ti = TI[name]
        r = radial(name)
        side_ax = UP.cross(r).normalized()
        n = len(bones)
        g = [rw + (1 - rw) * (k / (n - 1) if n > 1 else 1.0) for k in range(n)]
        gs = sum(g)
        for k, b in enumerate(bones):
            share = g[k] / gs                                   # Anteil an der Gesamtbiegung (Wurzel hat auch was)
            ph = 2 * math.pi * speed * t - k * step + ti["phase"]
            ph2 = 2 * math.pi * speed * ti["f2"] * t - k * step * 1.3 + ti["phase2"]
            rot(b, side_ax, env * R(amp_deg) * share * math.sin(ph))
            rot(b, r, env * R(amp_deg) * swirl * share * math.sin(ph2))
            if trail_deg:
                rot(b, LEFT, -R(trail_deg) * share)
            if turn_deg:
                rot(b, UP, -R(turn_deg) * share)
            if spread_deg:
                rot(b, side_ax, -R(spread_deg) * share)
            if curl_deg:
                rot(b, side_ax, R(curl_deg) * share)
            if drv is not None:
                x = _drive_at(drv[name], f - (k + 1) * lag)
                bd = (DB[b].tail_local - DB[b].head_local).normalized()
                xp = x - bd * x.dot(bd)
                if xp.length > 1e-7:
                    ang = dmax * math.tanh(gain * xp.length / ti["L"] / dmax)
                    rot(b, bd.cross(xp.normalized()), env * ang / n)


def ground_above():
    """Falls irgendein Teil in den Boden ragt: ganzen Körper genau so weit anheben."""
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


def bake(clips):
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
        if kind == "death":
            r["lies_on_ground_ok"] = abs(mins[-1]) <= tol
        if r["loop"]:
            jump = max((first[n].translation - last[n].translation).length +
                       first[n].to_quaternion().rotation_difference(last[n].to_quaternion()).angle for n in first)
            r["loop_ok"] = jump < 1e-3
        if kind == "stand_return":
            # Ruhe eines Schwebers = erster Frame (Schwebehöhe), nicht die Bindepose
            r["returns_to_rest"] = all((last[n].translation - first[n].translation).length < 1e-3 for n in last)
        r["max_stretch"] = round(stretch, 2)
        r["stretch_at"] = where
        r["stretch_ok"] = round(stretch, 2) <= (spec.get("max_stretch") or C["max_stretch"])
        oks = [v for k, v in r.items() if (k.endswith("_ok") and k != "stretch_ok")   # Dehnung = nur Info, bremst nie
               or k in ("returns_to_rest", "no_ground_penetration")]
        r["ok"] = all(oks)
        report[f"{PREFIX}_{cname}"] = r
        events[f"{PREFIX}_{cname}"] = list(spec.get("events", []))
        print("CLIP", f"{PREFIX}_{cname}", json.dumps(r, ensure_ascii=False))
    arm.animation_data.action = bpy.data.actions[f"{PREFIX}_{ST['meta']['clips'][0]}"]
    summary = {"style": f"{ST['meta']['skeleton']}/{ST['meta']['style']}", "variant": None,
               "clips": report, "all_ok": all(r["ok"] for r in report.values())}
    (OUT / "clips_report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "events.json").write_text(json.dumps({"fps": FPS, "clips": events}, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "clips.blend"))
    print("CLIPS_OK", summary["all_ok"])
