"""Zeichnet Skelett + Bein-Verfolgung über die Mesh-Punkte (Seite + Draufsicht) → rig_debug.png.

  python rigging/draw_rig.py <rig-ordner>
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw

d = pathlib.Path(sys.argv[1])
dbg = json.loads((d / "rig_debug.json").read_text(encoding="utf-8"))
P = dbg["verts"]
W, Hh = 900, 520
xs = [p[0] for p in P]
x0, x1 = min(xs), max(xs)
zs_, ys_ = [p[2] for p in P], [p[1] for p in P]
s = min((W - 40) / (x1 - x0), (Hh - 60) / (max(zs_) - min(zs_)), (Hh - 60) / (max(ys_) - min(ys_)))  # beide Achsen einpassen
COL = {"Leg_F": (230, 80, 60), "Leg_B": (60, 120, 230), "Tail": (60, 180, 80), "Neck": (200, 160, 30),
       "Head": (220, 40, 200), "Jaw": (255, 120, 220)}


def col(n):
    return next((c for k, c in COL.items() if n.startswith(k)), (20, 20, 20))


img = Image.new("RGB", (W, Hh * 2), "white")
dr = ImageDraw.Draw(img)
zs = [p[2] for p in P]
ys = [p[1] for p in P]
for k, (ax, base, mn) in enumerate(((2, Hh - 20, min(zs)), (1, 2 * Hh - 30, min(ys)))):
    def pt(p):
        return 20 + (p[0] - x0) * s, (base - (p[ax] - mn) * s) if ax == 2 else (base - (p[ax] - mn) * s)
    for p in P:
        x, y = pt(p)
        dr.point((x, y), fill=(185, 185, 185))
    for n, (a, b) in dbg["bones"].items():
        dr.line([pt(a), pt(b)], fill=col(n), width=3)
        dr.ellipse([pt(a)[0] - 3, pt(a)[1] - 3, pt(a)[0] + 3, pt(a)[1] + 3], fill=col(n))
    for tr in dbg["tracks"].values():
        dr.line([pt(p) for p in tr], fill=(0, 0, 0), width=1)
    dr.text((8, base - Hh + 30 if k else 8), "Seite" if k == 0 else "Draufsicht", fill="black")
img.save(d / "rig_debug.png")
print("DRAW_OK", d / "rig_debug.png")
