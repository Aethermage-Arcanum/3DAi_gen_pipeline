"""Schneidet pro Kreatur den Concept-Ausschnitt aus _concept/monster_progression_A_vs_B.webp
→ creatures/<id>/input/concept/design_<A|B>.png (2× vergrößert) + Übersicht creatures/concept_crops.png

  python scripts/concept_crops.py
Zellen (Spalte 1-4, Reihe 1-5) und Version stehen in creatures/roster.toml (cell = "A r1c2").
"""
import pathlib
import tomllib

from PIL import Image, ImageDraw

PIPE = pathlib.Path(__file__).resolve().parent.parent
R = tomllib.loads((PIPE / "creatures" / "roster.toml").read_text(encoding="utf-8"))
SHEET = (PIPE / R["sheet"]).resolve()
# Kreatur-Bereiche (ohne Namen/Drops) in Koordinaten einer 1400 px breiten Vorschau, Reihen/Spalten je Artist
ROWS = {"A": [(44, 156), (236, 330), (392, 518), (578, 690), (756, 868)],
        "B": [(44, 160), (220, 334), (398, 524), (582, 698), (766, 876)]}
C1_TOP = 24   # Spalte 1: Abschnitts-Überschrift oben links aussparen
COLS = {"A": [(5, 182), (178, 352), (343, 528), (518, 697)],
        "B": [(708, 882), (878, 1062), (1048, 1237), (1228, 1398)]}


def crop(img, cell):
    artist, rc = cell.split()
    r, c = int(rc[1]) - 1, int(rc[3]) - 1
    k = img.width / 1400
    (y0, y1), (x0, x1) = ROWS[artist][r], COLS[artist][c]
    if c == 0 and r > 0:
        y0 += C1_TOP
    box = tuple(int(v * k) for v in (x0, y0, x1, y1))
    im = img.crop(box)
    return im.resize((im.width * 2, im.height * 2), Image.LANCZOS)


def main():
    img = Image.open(SHEET).convert("RGB")
    tiles = []
    for c in R["c"]:
        if not c.get("cell"):          # Roster-Erweiterung ohne Concept Art
            continue
        im = crop(img, c["cell"])
        out = PIPE / "creatures" / c["id"] / "input" / "concept" / f"design_{c['artist']}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        tiles.append((c["design"], im))
    W, H = 380, 280
    sheet = Image.new("RGB", (W * 5, (H + 26) * 4), (30, 30, 34))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(tiles):
        t = im.copy()
        t.thumbnail((W, H))
        x, y = (i % 5) * W, (i // 5) * (H + 26)
        sheet.paste(t, (x, y))
        d.text((x + 6, y + H + 6), name, fill=(240, 240, 240))
    sheet.save(PIPE / "creatures" / "concept_crops.png")
    print("CROPS", len(tiles))


if __name__ == "__main__":
    main()
