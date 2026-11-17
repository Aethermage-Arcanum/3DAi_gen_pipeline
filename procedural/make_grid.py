"""Setzt die Varianten-Renders zu einem beschrifteten Raster zusammen.
Aufruf: python procedural/make_grid.py procedural/demo_output
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

out = pathlib.Path(sys.argv[1])
stats = json.loads((out / "stats.json").read_text(encoding="utf-8"))
imgs = [Image.open(out / f"variant_{s['index']}.png").convert("RGB") for s in stats]
w, h = imgs[0].size
cols = 3
rows = (len(imgs) + cols - 1) // cols
bar = 56
grid = Image.new("RGB", (cols * w, rows * (h + bar)), (18, 20, 24))
try:
    f1, f2 = ImageFont.truetype("arialbd.ttf", 22), ImageFont.truetype("arial.ttf", 19)
except OSError:
    f1 = f2 = ImageFont.load_default()
d = ImageDraw.Draw(grid)
for i, (img, s) in enumerate(zip(imgs, stats)):
    x, y = (i % cols) * w, (i // cols) * (h + bar)
    grid.paste(img, (x, y + bar))
    d.text((x + 14, y + 6), s["label"], font=f1, fill=(235, 235, 235))
    d.text((x + 14, y + 32), f"{s['tris']:,} Dreiecke".replace(",", "."), font=f2, fill=(150, 200, 160))
grid.save(out / "grid.png")
print("Raster:", out / "grid.png")
