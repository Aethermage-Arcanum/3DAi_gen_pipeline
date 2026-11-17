"""Beinlos-Standard-Rig (Schlangen, Aale, Würmer): Wirbelkette entlang der Körpermittellinie + Kopf + Kiefer.

& "D:\\Blender\\blender.exe" -b --factory-startup -P rigging/legless_rig.py -- <model.glb> <ausgabe> [<creature.toml>]
Ergebnis: <ausgabe>/legless_rigged.blend, rig_report.json, rig_debug.json

Skelett (Unity "Generic"): Root → Spine_01 (Schwanzspitze) → … → Spine_<n> → Head → Jaw
Annahme: Kopf zeigt nach +X, der Körper verläuft grob entlang X (Querschnitte entlang X treffen ihn einmal).
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
n = CFG["segments"]
x_hb = x1 - CFG["head_length"] * L                      # Kopfansatz


def center(x, slab):
    s = M[np.abs(M[:, 0] - x) < slab]
    if len(s) < 3:
        return None
    return np.array([x, (np.percentile(s[:, 1], 10) + np.percentile(s[:, 1], 90)) / 2,
                     (np.percentile(s[:, 2], 10) + np.percentile(s[:, 2], 90)) / 2])


xs = np.linspace(x0, x_hb, n + 1)
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
arm = RC.build_armature("Legless_Rig", B, order, H)

names = order[1:]
allow = np.ones((len(V), len(names)), bool)
j_jaw, j_head = names.index("Jaw"), names.index("Head")
allow[:, j_jaw] = (V[:, 0] > x_hb + 0.25 * (x1 - x_hb)) & (V[:, 2] < B["Jaw"][0][2] + 0.01 * H)
allow[:, j_head] = V[:, 0] > x_hb - 0.03 * L
RC.skin(obj, V, part, MAIN, B, names, allow, CFG)
report = {"vertices": int(len(V)), "parts": int(len(np.unique(part))), "length_m": round(float(L), 3),
          "height_m": round(float(H), 3), "bones": len(order), "segments": n}
RC.finish(obj, arm, OUT, "legless_rigged.blend", report, B, order, V)
