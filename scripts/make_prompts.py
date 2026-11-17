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
        "**So geht's:** Neuen ChatGPT-Chat öffnen, Bilder anhängen, den einen Prompt einfügen. "
        "Die Bilder als PNG unter den angegebenen Namen speichern in:",
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
                 f"Create {len(views)} separate clean reference images of the creature from the design image "
                 f"for 3D modeling." +
                 (f" {cfg['design_pick']}" if cfg.get("design_pick") else ""))
        parts += ["**Anhängen in ChatGPT, in dieser Reihenfolge:**", ""] + attach + [""]
    else:
        intro = f"Create {len(views)} separate clean reference images of this creature for 3D modeling."
    order = ["front", "left", "right", "back"]
    views = [v for v in order if v in views] + [v for v in views if v not in order]
    vlist = "\n".join(f"{i}. `{v}.png` - {VIEWS[v]}" for i, v in enumerate(views, 1))
    prompt = (f"{intro}\n\n"
              f"Creature: {cfg['description']}\n\n"
              f"Style: {st['text']}\n\n"
              f"Please generate {len(views)} SEPARATE images, one after another (NOT a grid, NOT a collage, "
              f"NOT one sheet with several views). All images show EXACTLY the same creature - identical "
              f"design, proportions, number of legs, colors, materials, pose and lighting. Only the camera "
              f"angle changes - the body posture is IDENTICAL in every view (do not stand the creature upright "
              f"in the front/back views if it leans forward in the side views; imagine one frozen 3D model and "
              f"a camera circling around it):\n{vlist}\n\n"
              f"Keep the exact number of legs, wings, tails and claws of the design and keep all of them "
              f"clearly visible and separated in every view.\n\n{rules}")
    parts += [f"## Ein Prompt für alle {len(views)} Ansichten", "",
              "ChatGPT erzeugt die Bilder nacheinander. Speichern als " +
              ", ".join(f"`{v}.png`" for v in views) + ". Falls es doch ein Raster macht: "
              "„Bitte jede Ansicht als eigenes Bild“ nachschieben.", "", "```text", prompt, "```", ""]
    n = len(views)

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
