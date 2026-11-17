"""Erzeugt die ChatGPT-Bildprompts für eine Kreatur.

Aufruf:  python scripts/make_prompts.py creatures/spinne_01
Ergebnis: creatures/spinne_01/prompts.md  (Prompts zum Kopieren + Speicheranweisung)
"""
import sys
import pathlib

from common import load_creature

# Regeln, die für JEDES Bild gelten – sie machen das Bild 3D-tauglich.
RULES = """Requirements for a 3D-model reference image:
- exactly one creature, centered, the entire body in frame with some margin, nothing cut off
- {background} background, no ground texture, no scenery, no props, no text, no watermark
- soft, even, diffuse studio lighting from all sides, no cast shadows, no strong highlights, \
no rim light, no glow or bloom effects
- sharp focus everywhere, no depth of field, no motion blur, no smoke, no particles
- {pose}
- {camera}
- {aspect} image"""

# Wie jede Ansicht formuliert wird. "left"/"right" = die eigene linke/rechte Körperseite der Kreatur.
VIEWS = {
    "front": "front view: the creature faces the camera directly",
    "left": "exact side view of the creature's own LEFT flank: rotated 90 degrees, its head points to the LEFT edge of the image",
    "back": "exact rear view: rotated 180 degrees, we see the creature from directly behind",
    "right": "exact side view of the creature's own RIGHT flank: rotated 90 degrees, its head points to the RIGHT edge of the image",
}


def build(creature_dir):
    creature_dir = pathlib.Path(creature_dir).resolve()
    cfg, bp, st = load_creature(creature_dir)
    img = cfg["images"]
    views = img["views"]
    if "front" not in views:
        raise SystemExit("images.views muss 'front' enthalten.")
    rules = RULES.format(background=img["background"], pose=bp["pose"],
                         camera=bp["camera"], aspect=img["aspect"])

    parts = [
        f"# Bildprompts: {cfg['name']}",
        "",
        f"Bauplan: **{bp['label']}** · Stil: **{st['label']}**",
        "",
        "**So geht's:** Neuen ChatGPT-Chat öffnen. Prompt 1 einfügen. Wenn dir das Bild gefällt, "
        "die weiteren Prompts **im selben Chat** nacheinander einfügen, damit es dieselbe Kreatur bleibt. "
        "Jedes Bild als PNG unter dem angegebenen Namen speichern in:",
        "",
        f"`{creature_dir / 'input'}`",
        "",
        "Gefällt Bild 1 nicht: einfach neu generieren lassen oder die Beschreibung in "
        "`creature.toml` anpassen und dieses Skript erneut starten.",
        "",
    ]

    n = 1
    concepts = cfg.get("concept", [])
    if concepts:
        # Concept-Modus: Design (und optional Stil) kommen aus angehängten Bildern
        lines, attach = [], []
        for i, c in enumerate(concepts, 1):
            attach.append(f"{i}. `{creature_dir / c['file']}`")
            if c["role"] == "design":
                lines.append(f"Image {i} shows the creature DESIGN to recreate: keep its anatomy, body "
                             f"segments, number of legs, head shape, proportions and color scheme.")
            elif c["role"] == "style":
                lines.append(f"Image {i} is only an ART STYLE reference: copy its rendering style, "
                             f"not the creatures shown in it.")
        intro = ("I attached reference images. " + " ".join(lines) +
                 " Ignore any text, labels, scenery and background in the attached images.\n\n"
                 "Create a clean reference image of the creature from the design image for 3D modeling.")
        parts += ["**Anhängen in ChatGPT, in dieser Reihenfolge:**", ""] + attach + [""]
    else:
        intro = "Create a reference image of this creature for 3D modeling."
    front = (f"{intro}\n\n"
             f"Creature: {cfg['description']}\n\n"
             f"Style: {st['text']}\n\n"
             f"View: {VIEWS['front']}\n\n{rules}")
    parts += [f"## {n}. Vorderansicht → speichern als `front.png`", "", "```text", front, "```", ""]

    for v in views:
        if v == "front":
            continue
        n += 1
        p = (f"Now show EXACTLY the same creature from the previous image - identical design, "
             f"proportions, colors, materials, pose and lighting. Only the camera angle changes.\n\n"
             f"View: {VIEWS[v]}\n\n{rules}")
        parts += [f"## {n}. Ansicht `{v}` → speichern als `{v}.png`", "", "```text", p, "```", ""]

    parts += [
        "## Kontrolle vor dem Tripo-Schritt",
        "",
        "- Alle Bilder zeigen dieselbe Kreatur (Farben, Anzahl Beine/Augen, Muster)?",
        "- Beine/Flügel klar getrennt, nichts überkreuzt, nichts abgeschnitten?",
        "- Keine harten Schatten, keine Glüh-Effekte?",
        "",
        "Wenn eine Ansicht danebengeht, lass sie weg. Tripo braucht nur `front.png` plus mindestens eine weitere.",
    ]
    out = creature_dir / "prompts.md"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    (creature_dir / "input").mkdir(exist_ok=True)
    print(f"Prompts geschrieben: {out}  ({n} Bilder)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    build(sys.argv[1])
