"""Beinlos-Standard-Rig (Schlangen, Aale, Würmer): Wirbelkette entlang der Körpermittellinie + Kopf + Kiefer.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/legless_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/legless_rigged.blend, rig_report.json, rig_debug.json

Skelett (Unity "Generic"): Root → Spine_01 (Schwanzspitze) → … → Spine_<n> → Head → Jaw
Annahme: Kopf zeigt nach +X, der Körper verläuft grob entlang X (Querschnitte entlang X treffen ihn einmal).

Optionale Erweiterungen (opt-in pro Kreatur unter [legless]; ohne Angabe = altes Verhalten. Seit 2026-11-27 für
gedrungene Ringel-Würmer wie den Sand Leviathan):
  joints = [0, …, 0.86]   Wirbel-Grenzen als Anteil der Länge ab Schwanzspitze (z. B. auf die Ringfurchen gelegt);
                          letzter Wert = Kopfansatz (ersetzt segments + head_length)
  axial_weights = true    Gewichte nach Lage entlang X statt nach Abstand: jeder Ring hängt starr an seinem Wirbel,
  axial_blend = 0.02      gebogen wird nur in der Furche (± axial_blend × Länge; Zahl oder Liste je Grenze 1…n,
                          z. B. breiter zwischen großen Panzerplatten). Nur für gerade liegende Modelle.
  rigid_spikes = true     Stacheln (radiale Ausreißer: Abstand zur Mittellinie > spike_factor × Körperradius
                          + spike_min × Länge; Körperradius = Perzentil spike_core_pct der Nachbarn im Fenster
                          spike_window × Länge / spike_window_deg) übernehmen das Gewicht ihres Ansatzes
                          → starr am nächsten Wirbel
  ground_ignore_spikes = true   Stacheln als Mesh-Attribut "_NO_GROUND" markieren: der Bodenkontakt im Baukasten
                          zählt nur den Körper, Stacheln dürfen in den Sand stechen
  ring_bones = true       zusätzliche Blatt-Knochen Ring_<i> (Kind von Spine_<i>, gleiche Lage) tragen die Haut;
                          per Skalierung dick/dünn (Peristaltik), ohne dass sich die Skalierung vererbt (Unity-tauglich)
"""
import pathlib
import sys
import tomllib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rig_common as RC  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = pathlib.Path(a[0]).resolve(), pathlib.Path(a[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CFG = tomllib.loads((HERE / "legless_defaults.toml").read_text(encoding="utf-8"))
if len(a) > 2:
    CFG.update(tomllib.loads(pathlib.Path(a[2]).read_text(encoding="utf-8")).get("legless", {}))

obj, V, part, MAIN = RC.load_mesh(SRC)
main = part == MAIN
M = V[main]
GROUND = V[:, 2].min()
x0, x1 = M[:, 0].min(), M[:, 0].max()
L = x1 - x0
H = M[:, 2].max() - GROUND
JOINTS = CFG.get("joints")                              # opt-in: Wirbel-Grenzen (Anteil Länge ab Schwanzspitze)
if JOINTS:
    n = len(JOINTS) - 1
    x_hb = x0 + JOINTS[-1] * L
else:
    n = CFG["segments"]
    x_hb = x1 - CFG["head_length"] * L                  # Kopfansatz


def center(x, slab):
    s = M[np.abs(M[:, 0] - x) < slab]
    if len(s) < 3:
        return None
    return np.array([x, (np.percentile(s[:, 1], 10) + np.percentile(s[:, 1], 90)) / 2,
                     (np.percentile(s[:, 2], 10) + np.percentile(s[:, 2], 90)) / 2])


def _smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def axial_skin(names, xs):
    """opt-in Gewichte (siehe Kopf der Datei). names = n Wirbel- bzw. Ring-Knochen + Head + Jaw."""
    me = obj.data
    N = len(V)
    W = np.zeros((N, len(names)))
    x = V[:, 0]
    if CFG.get("axial_weights"):
        b = np.broadcast_to(np.asarray(CFG.get("axial_blend", 0.02), float) * L, (n,))   # Zahl oder je Grenze
        S = [np.ones(N)] + [_smooth((x - xj + bj) / (2 * bj)) for xj, bj in zip(xs[1:], b)]   # S_j = 1 vor Grenze j
        for i in range(n):
            W[:, i] = S[i] - S[i + 1]
        W[:, n] = S[n]
    else:                                               # Abstand wie rig_common.skin (ohne Glätten)
        Dm = np.stack([RC.seg_dist(V, B[nm][0], B[nm][1]) for nm in names[:n + 1]], 1)
        W[:, :n + 1] = 1.0 / (Dm + 1e-4) ** CFG["falloff"]
        W /= W.sum(1, keepdims=True)
    # Kiefer: unterer, vorderer Kopfbereich (gleiche Maske wie bisher), weich ausgeblendet
    bj = 0.015 * L
    zj = B["Jaw"][0][2] + 0.01 * H
    jf = _smooth((x - (x_hb + 0.25 * (x1 - x_hb)) + bj) / (2 * bj)) * (1 - _smooth((V[:, 2] - zj + bj) / (2 * bj)))
    W[:, n + 1] = W[:, n] * jf
    W[:, n] *= 1 - jf
    rep = {"weights": "axial" if CFG.get("axial_weights") else "distance"}
    E = np.array([e.vertices[:] for e in me.edges])
    groups = {}
    for i, co in enumerate(np.round(V, 5)):
        groups.setdefault(tuple(co), []).append(i)
    weld = [g for g in groups.values() if len(g) > 1]
    if weld:
        E = np.vstack([E] + [np.array([[g[0], v] for v in g[1:]]) for g in weld])
    spike = np.zeros(N, bool)
    if CFG.get("rigid_spikes") or CFG.get("ground_ignore_spikes"):
        # Mittellinie aus den Wirbel-Punkten → Abstand + Winkel je Vertex; Körperradius = Median im Fenster (x, Winkel)
        cp = np.array([B[f"Spine_{i + 1:02d}"][0] for i in range(n)] + [B["Head"][0], B["Head"][1]])
        dy, dz = V[:, 1] - np.interp(x, cp[:, 0], cp[:, 1]), V[:, 2] - np.interp(x, cp[:, 0], cp[:, 2])
        r, th = np.hypot(dy, dz), np.arctan2(dz, dy)
        wx, wt = CFG.get("spike_window", 0.03) * L, np.radians(CFG.get("spike_window_deg", 25))
        R = np.empty(N)
        for i in range(N):
            m = (np.abs(x - x[i]) < wx) & (np.abs(np.angle(np.exp(1j * (th - th[i])))) < wt)
            R[i] = np.percentile(r[m], CFG.get("spike_core_pct", 50))
        spike = r > R * CFG.get("spike_factor", 1.2) + CFG.get("spike_min", 0.01) * L
        for g in weld:                                  # Doppel-Vertices gleich behandeln
            spike[g] = spike[g].any()
        par = np.arange(N)

        def find(i):
            while par[i] != i:
                par[i] = par[par[i]]
                i = par[i]
            return i
        for a_, b_ in E:
            if spike[a_] and spike[b_]:
                par[find(a_)] = find(b_)
        comp = {}
        for i in np.nonzero(spike)[0]:
            comp.setdefault(find(i), []).append(i)
        rep["spike_vertices"] = int(spike.sum())
        rep["spike_groups"] = len(comp)
        if CFG.get("rigid_spikes"):
            nb = {}
            for a_, b_ in E:
                if spike[a_] != spike[b_]:
                    s_, c_ = (a_, b_) if spike[a_] else (b_, a_)
                    nb.setdefault(find(s_), set()).add(c_)
            core = np.nonzero(~spike)[0]
            for k, vs in comp.items():
                base = sorted(nb.get(k, ()))
                if not base:                            # ohne Kante zum Körper: nächster Körper-Vertex
                    base = [core[np.argmin(np.linalg.norm(V[core] - V[vs].mean(0), axis=1))]]
                W[vs] = W[base].mean(0)
    for g in weld:
        W[g] = W[g].mean(0)
    top = np.argsort(-W, 1)[:, :4]
    for nm in names:
        obj.vertex_groups.new(name=nm)
    for i in range(N):
        ws = W[i, top[i]]
        ws = ws / ws.sum()
        for j, w in zip(top[i], ws):
            if w > 1e-3:
                obj.vertex_groups[names[j]].add([i], float(w), "REPLACE")
    if CFG.get("ground_ignore_spikes"):
        at = me.attributes.new("_NO_GROUND", "BOOLEAN", "POINT")
        at.data.foreach_set("value", spike.tolist())
        rep["lowest_body_z"] = round(float(V[~spike, 2].min()), 4)
        rep["lowest_spike_z"] = round(float(V[spike, 2].min()), 4) if spike.any() else None
    return rep


xs = x0 + np.asarray(JOINTS, float) * L if JOINTS else np.linspace(x0, x_hb, n + 1)
pts = []
for i, x in enumerate(xs):
    c = center(x, CFG["slab"] * L)
    pts.append(c if c is not None else (pts[-1] if pts else np.array([x, 0, GROUND + 0.05 * H])))
pts[0] = np.array([x0, *M[M[:, 0] < x0 + 0.01 * L][:, 1:].mean(0)])     # Schwanzspitze
nose_s = M[M[:, 0] > x1 - 0.02 * L]
nose = np.array([x1, float(np.median(nose_s[:, 1])), float(np.median(nose_s[:, 2]))])
head_s = M[M[:, 0] > x_hb]
head_low = float(np.percentile(head_s[:, 2], 8))
B = {"Root": (np.array([(x0 + x1) / 2, pts[n // 2][1], GROUND]),
              np.array([(x0 + x1) / 2, pts[n // 2][1], GROUND + 0.1 * H]), None)}
order = ["Root"]
for i in range(n):
    nm = f"Spine_{i + 1:02d}"
    B[nm] = (pts[i], pts[i + 1], "Root" if i == 0 else f"Spine_{i:02d}")
    order.append(nm)
B["Head"] = (pts[n], nose, f"Spine_{n:02d}")
B["Jaw"] = (np.array([x_hb + 0.3 * (x1 - x_hb), nose[1], (pts[n][2] + head_low) / 2]),
            np.array([x1, nose[1], head_low + 0.3 * (nose[2] - head_low)]), "Head")
order += ["Head", "Jaw"]
RINGS = bool(CFG.get("ring_bones"))
if RINGS:                                               # opt-in: Blatt-Knochen für Dick/Dünn (Skalierung)
    for i in range(n):
        B[f"Ring_{i + 1:02d}"] = (pts[i], pts[i + 1], f"Spine_{i + 1:02d}")
        order.append(f"Ring_{i + 1:02d}")
arm = RC.build_armature("Legless_Rig", B, order, H)

extra = {}
if CFG.get("axial_weights") or CFG.get("rigid_spikes") or CFG.get("ground_ignore_spikes") or RINGS:
    names = [f"{'Ring' if RINGS else 'Spine'}_{i + 1:02d}" for i in range(n)] + ["Head", "Jaw"]
    if RINGS:
        for i in range(n):
            arm.data.bones[f"Spine_{i + 1:02d}"].use_deform = False
    extra = axial_skin(names, xs)
else:
    names = order[1:]
    allow = np.ones((len(V), len(names)), bool)
    j_jaw, j_head = names.index("Jaw"), names.index("Head")
    allow[:, j_jaw] = (V[:, 0] > x_hb + 0.25 * (x1 - x_hb)) & (V[:, 2] < B["Jaw"][0][2] + 0.01 * H)
    allow[:, j_head] = V[:, 0] > x_hb - 0.03 * L
    RC.skin(obj, V, part, MAIN, B, names, allow, CFG)
report = {"vertices": int(len(V)), "parts": int(len(np.unique(part))), "length_m": round(float(L), 3),
          "height_m": round(float(H), 3), "bones": len(order), "segments": n, **extra}
RC.finish(obj, arm, OUT, "legless_rigged.blend", report, B, order, V)
