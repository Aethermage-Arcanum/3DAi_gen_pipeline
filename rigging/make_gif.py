"""Setzt die Frames aus render_anim.py zu GIFs zusammen (eins pro Ansicht + eins kombiniert).
python rigging/make_gif.py <ordner> [fps]
"""
import pathlib
import sys
from PIL import Image

d = pathlib.Path(sys.argv[1])
fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
views = sorted({p.name.rsplit("_", 1)[0] for p in d.glob("*_[0-9][0-9][0-9].png")})
frames = {v: [Image.open(p).convert("RGB") for p in sorted(d.glob(f"{v}_[0-9][0-9][0-9].png"))] for v in views}
n = min(len(f) for f in frames.values())
w, h = frames[views[0]][0].size
combo = []
for i in range(n):
    c = Image.new("RGB", (w * len(views), h))
    for k, v in enumerate(views):
        c.paste(frames[v][i], (k * w, 0))
    combo.append(c)
dur = int(1000 / fps)
name = sys.argv[3] if len(sys.argv) > 3 else "walk_combined"
combo[0].save(d / f"{name}.gif", save_all=True, append_images=combo[1:], duration=dur, loop=0)
# Kontaktbogen: jedes 2. Frame der Seitenansicht
side = frames.get("side", combo)
sheet = Image.new("RGB", (w * 5, h * 2))
for i, fr in enumerate(side[::2][:10]):
    sheet.paste(fr, ((i % 5) * w, (i // 5) * h))
sheet.save(d / "walk_side_sheet.png")
print("GIF:", d / "walk_combined.gif", f"{n} Frames, Ansichten {views}")
