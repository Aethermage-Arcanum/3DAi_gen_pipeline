"""Kontaktbogen aus einem GIF: alle bzw. N gleichmäßig verteilte Frames als Raster in ein PNG.

Zweck: Animationen vollständig prüfen (ein Bildbetrachter zeigt von GIFs oft nur Frame 1).

    python scripts/gif_sheet.py <clip.gif> [--n 12] [--cols 4] [--out <bogen.png>]
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gif")
    ap.add_argument("--n", type=int, default=12, help="Anzahl Frames (0 = alle)")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()

    src = Path(a.gif)
    frames = [f.convert("RGB") for f in ImageSequence.Iterator(Image.open(src))]
    total = len(frames)
    n = total if a.n <= 0 or a.n >= total else a.n
    idx = [round(i * (total - 1) / max(n - 1, 1)) for i in range(n)]
    w, h = frames[0].size
    cols = min(a.cols, n)
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    for k, i in enumerate(idx):
        x, y = (k % cols) * w, (k // cols) * h
        sheet.paste(frames[i], (x, y))
        draw.rectangle([x, y, x + 70, y + 16], fill=(0, 0, 0))
        draw.text((x + 3, y + 2), f"F{i}/{total - 1}", fill=(255, 220, 80))
    out = Path(a.out) if a.out else src.with_name(src.stem + "_bogen.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
