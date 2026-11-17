"""Erzeugt kachelbare Test-Texturen im düster-gemalten Stil – eine pro Biom – plus eine UV-Prüftextur.

  python uv/biome_textures.py [ausgabeordner] [größe]

Zweck: UV-Maps prüfen. Eine kachelbare Struktur auf dem Modell zeigt sofort Verzerrung (gestauchte/
gezogene Muster), Nähte (Musterbrüche) und Größenunterschiede zwischen UV-Inseln.
Stil: painterly-düster (passend zur Concept Art), Farbpaletten aus den Biom-Sheets.
"""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "textures")
S = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
OUT.mkdir(parents=True, exist_ok=True)

# Paletten (dunkel → hell) + Akzentfarbe, abgeleitet aus den Biom-Concepts
BIOMES = {
    "forest":    {"pal": [(14, 18, 10), (34, 44, 20), (64, 78, 34), (110, 118, 58), (150, 140, 80)],
                  "accent": (120, 150, 60), "cracks": 0.35, "spots": 0.5, "warp": 1.0},
    "coast":     {"pal": [(10, 16, 22), (26, 42, 52), (52, 76, 86), (92, 116, 120), (170, 176, 164)],
                  "accent": (200, 196, 176), "cracks": 0.25, "spots": 0.8, "warp": 0.8},
    "highlands": {"pal": [(22, 18, 16), (52, 42, 34), (92, 76, 60), (136, 116, 92), (176, 160, 132)],
                  "accent": (200, 120, 60), "cracks": 0.8, "spots": 0.2, "warp": 0.6},
    "desert":    {"pal": [(36, 20, 10), (92, 54, 24), (150, 96, 46), (196, 140, 76), (226, 188, 124)],
                  "accent": (240, 200, 140), "cracks": 0.9, "spots": 0.1, "warp": 0.7},
    "snow":      {"pal": [(18, 26, 40), (50, 70, 96), (100, 132, 160), (168, 196, 214), (226, 236, 242)],
                  "accent": (120, 200, 255), "cracks": 0.6, "spots": 0.3, "warp": 0.9},
    "abyss":     {"pal": [(8, 4, 14), (26, 12, 40), (52, 24, 78), (88, 44, 130), (130, 80, 180)],
                  "accent": (190, 110, 255), "cracks": 0.7, "spots": 0.4, "warp": 1.3},
}


def tile_noise(res, octaves, rng, persistence=0.5):
    """Kachelbares fBm-Rauschen über periodisch interpoliertes Zufallsgitter."""
    out = np.zeros((S, S), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = res * 2 ** o
        grid = rng.random((n, n)).astype(np.float32)
        x = np.linspace(0, n, S, endpoint=False)
        i0 = np.floor(x).astype(int) % n
        i1 = (i0 + 1) % n
        t = x - np.floor(x)
        t = t * t * (3 - 2 * t)
        a = grid[i0][:, i0] * (1 - t)[None, :] + grid[i0][:, i1] * t[None, :]
        b = grid[i1][:, i0] * (1 - t)[None, :] + grid[i1][:, i1] * t[None, :]
        out += amp * (a * (1 - t)[:, None] + b * t[:, None])
        total += amp
        amp *= persistence
    return out / total


def warp(img, dx, dy, strength):
    """Domain Warping (periodisch) → organische, gemalte Formen."""
    yy, xx = np.mgrid[0:S, 0:S]
    xs = (xx + (dx - 0.5) * strength * S).astype(int) % S
    ys = (yy + (dy - 0.5) * strength * S).astype(int) % S
    return img[ys, xs]


def voronoi_edges(cells, rng):
    """Kachelbare Voronoi-Kanten → Risse/Plattenfugen."""
    pts = rng.random((cells, 2)) * S
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d1 = np.full((S, S), 1e9, np.float32)
    d2 = np.full((S, S), 1e9, np.float32)
    for px, py in pts:
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                d = np.hypot(xx - (px + ox), yy - (py + oy))
                d2 = np.where(d < d1, d1, np.minimum(d2, d))
                d1 = np.minimum(d1, d)
    return np.clip((d2 - d1) / (S / cells ** 0.5 * 0.12), 0, 1)   # 0 an der Kante


def directional_blur(img, steps=6, dx=1, dy=1):
    """Pinselstrich-Eindruck: Weichzeichnen entlang einer Richtung (periodisch)."""
    acc = img.copy()
    for k in range(1, steps):
        acc += np.roll(np.roll(img, k * dy, 0), k * dx, 1)
    return acc / steps


def ramp(v, pal):
    pal = np.array(pal, np.float32)
    x = np.clip(v, 0, 1) * (len(pal) - 1)
    i = np.clip(np.floor(x).astype(int), 0, len(pal) - 2)
    t = (x - i)[..., None]
    return pal[i] * (1 - t) + pal[i + 1] * t


def make_biome(name, cfg, seed):
    rng = np.random.default_rng(seed)
    base = tile_noise(4, 6, rng)
    wx, wy = tile_noise(3, 3, rng), tile_noise(3, 3, rng)
    v = warp(base, wx, wy, 0.18 * cfg["warp"])
    v = directional_blur(v, 7, 1, 2) * 0.6 + v * 0.4            # gemalte Striche
    v = np.round(v * 9) / 9 * 0.35 + v * 0.65                    # leichte Posterisierung (Pinsel-Flächen)
    edges = voronoi_edges(18, rng)
    crack = (1 - edges) ** 3 * cfg["cracks"]
    v = v - crack * 0.45                                         # dunkle Fugen/Risse (düster)
    spots = np.clip((tile_noise(16, 2, rng) - 0.72) * 6, 0, 1) * cfg["spots"]
    col = ramp((v - v.min()) / (v.max() - v.min()), cfg["pal"])
    acc = np.array(cfg["accent"], np.float32)
    col = col * (1 - spots[..., None] * 0.6) + acc * spots[..., None] * 0.6
    grime = tile_noise(2, 3, rng)                                # großflächige Abdunklung (düster)
    col *= (0.42 + 0.5 * grime)[..., None]
    # Plattenmitte heller, Ränder dunkler → gemalte Plastizität
    col *= (0.75 + 0.3 * np.clip(edges, 0, 1) ** 0.5)[..., None]
    rim = np.clip(edges * 1.4 - 0.9, 0, 1) * 0.12                # helle Kanten neben Fugen (gemalter Lichtsaum)
    col += acc * rim[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


def make_checker():
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    n = 8
    c = S // n
    try:
        font = ImageFont.truetype("arialbd.ttf", c // 3)
    except OSError:
        font = ImageFont.load_default()
    for y in range(n):
        for x in range(n):
            hue = (x * 37 + y * 71) % 360
            base = Image.new("HSV", (1, 1), (int(hue / 360 * 255), 120, 200 if (x + y) % 2 else 120)).convert("RGB")
            d.rectangle([x * c, y * c, (x + 1) * c - 1, (y + 1) * c - 1], fill=base.getpixel((0, 0)))
            d.text((x * c + c * 0.18, y * c + c * 0.25), f"{chr(65 + y)}{x + 1}", fill=(20, 20, 20), font=font)
            # Pfeil nach "oben" (+V) zeigt Drehung der UV-Insel
            d.polygon([(x * c + c * 0.8, y * c + c * 0.15), (x * c + c * 0.7, y * c + c * 0.35),
                       (x * c + c * 0.9, y * c + c * 0.35)], fill=(20, 20, 20))
    return img


if __name__ == "__main__":
    make_checker().save(OUT / "uv_checker.png")
    for i, (name, cfg) in enumerate(BIOMES.items()):
        make_biome(name, cfg, 100 + i).save(OUT / f"biome_{name}.png")
        print("Textur:", OUT / f"biome_{name}.png")
    # Übersicht
    ims = [Image.open(OUT / f"biome_{n}.png").resize((256, 256)) for n in BIOMES]
    sheet = Image.new("RGB", (256 * len(ims), 256))
    for k, im in enumerate(ims):
        sheet.paste(im, (k * 256, 0))
    sheet.save(OUT / "biomes_overview.png")
