"""Setzt die UV-Prüfbilder zu einem beschrifteten Prüfblatt zusammen (System-Python mit Pillow).

  python uv/uv_sheet.py <uv-ordner>      → <uv-ordner>/uv_preview.png
Liest uv_report.json (von uv_check.py).
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

T = 340                         # Kachelgröße
CAP = 52                        # Platz für Bildunterschrift


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_T, F_C, F_S = font(24), font(16), font(14)

COLS = [("islands_arpg", "Inseln (schräg)", "jede Farbe = eine UV-Insel"),
        ("islands_side", "Inseln (Seite)", ""),
        ("islands_head", "Kopf: Inseln + Nähte", "trennt Augen/Kiefer sauber?"),
        ("seams_arpg", "Nähte (gelb) auf Textur/Schachbrett", "Nähte sollen an Segmentkanten liegen"),
        ("seams_head", "Kopf: Nähte auf Textur", ""),
        ("density_arpg", "Texel-Dichte", "grün gleichmäßig · blau unscharf · rot fein"),
        ("layout", "2D-Layout (gleiche Farben)", "weiß = Inselrand")]


def tile(path):
    im = Image.open(path).convert("RGB")
    return im.resize((T, T), Image.LANCZOS)


def main():
    d = pathlib.Path(sys.argv[1])
    rep = json.loads((d / "uv_report.json").read_text(encoding="utf-8"))
    rows = [("tripo", "Tripo-UV"), ("smart", "Blender Smart UV")]
    W = T * len(COLS)
    H = 60 + len(rows) * (T + CAP + 70) + T + CAP + 40
    sheet = Image.new("RGB", (W, H), (34, 35, 38))
    dr = ImageDraw.Draw(sheet)
    y = 14
    chosen = "Tripo-UV" if rep["chosen"] == "tripo_uv" else "Smart UV"
    dr.text((14, y), f"UV-Prüfung – gewählt: {chosen}", font=F_T, fill=(240, 240, 240))
    y += 46
    for key, label in rows:
        ins = rep["inspect"][key]
        m, imgs = ins["metrics"], ins["images"]
        mark = "  (gewählt)" if (key + "_uv") == rep["chosen"] else ""
        dr.text((14, y), label + mark, font=F_T, fill=(255, 220, 120) if mark else (220, 220, 220))
        txt = (f"{m['uv_islands']} Inseln auf {m['parts']} Körperteilen · Teile in 1 Insel: "
               f"{m['parts_in_one_island']:.0%} · große Teile zerschnitten in Ø {m['big_parts_split_mean']} · "
               f"Nahtlänge {m['seam_length_per_size']}× Größe ({m['seams_on_top_fraction']:.0%} oben sichtbar) · "
               f"Dichte pro Teil {m['part_density_min_max'][0]}–{m['part_density_min_max'][1]}× · Kopf {m['head_density']}×")
        dr.text((14, y + 32), txt, font=F_S, fill=(190, 190, 190))
        y += 62
        for i, (k, cap, sub) in enumerate(COLS):
            sheet.paste(tile(d / imgs[k]), (i * T, y))
            dr.text((i * T + 8, y + T + 4), cap, font=F_C, fill=(235, 235, 235))
            dr.text((i * T + 8, y + T + 26), sub, font=F_S, fill=(160, 160, 160))
        y += T + CAP + 8
    # Biom-Testtexturen auf der gewählten UV
    dr.text((14, y), "Gewählte UV mit Testtexturen", font=F_T, fill=(220, 220, 220))
    y += 40
    names = [r for r in rep["renders"] if r.endswith("_arpg.png")]
    for i, r in enumerate(names[:len(COLS)]):
        sheet.paste(tile(d / r), (i * T, y))
        dr.text((i * T + 8, y + T + 4), r[3:-9].capitalize(), font=F_C, fill=(235, 235, 235))
    sheet = sheet.crop((0, 0, W, y + T + CAP))
    sheet.save(d / "uv_preview.png")
    print("UV_SHEET", d / "uv_preview.png")


if __name__ == "__main__":
    main()
