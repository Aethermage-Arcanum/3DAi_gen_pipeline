"""Erzeugt die ChatGPT-Bildprompts für eine Kreatur – ZWEI STUFEN (seit 2026-11-18, BACKLOG A10).

  Stufe 1 – Design-Bild:  Concept-Ausschnitt (+ Stil-Referenz) + ausführliche Beschreibung → EIN sauberes,
                          hochauflösendes Bild. Der Nutzer prüft es gegen sein Concept → `input/design.png`.
  Stufe 2 – 4 Ansichten:  `input/design.png` als verbindliche Vorlage → front/left/right/back.png.
                          Claude prüft sie danach nach der Checkliste (README „Prüfung …“, Teil A).

Warum: Die Concept-Ausschnitte sind winzig und verpixelt (ChatGPT fantasierte), und die alten Prompts beschrieben
die Kreatur in einem Satz, umgeben von vielen Technik-Anweisungen. Jetzt steht die Beschreibung vorn und dominant,
die Technik kompakt am Ende.

Ohne Concept Art (seit 2026-11-18, Roster-Erweiterung: kein [[concept]] mit role = "design"):
  Stufe 1 entwirft die Kreatur nur aus Beschreibung + Stil-Referenz. Das Design-Bild IST dann der Design-Entwurf –
  der Nutzer prüft ihn und lässt ihn ggf. neu generieren. Kreaturen mit Concept bekommen unverändert denselben Text.

Woher die Texte kommen (erster Treffer gilt):
  Beschreibung  `look` in creature.toml → `look` in creatures/roster.toml → `description` in creature.toml
  Pose          `pose` in creature.toml → `pose` in creatures/roster.toml → Bauplan (templates/bodyplans.toml)
  Name          `title` in creature.toml → `design` in creatures/roster.toml → Ordnername

Aufruf:  python scripts/make_prompts.py creatures/<name>
Ergebnis: creatures/<name>/prompts.md  (beide Prompts zum Kopieren + was anhängen + wie speichern)
Alle Kreaturen auf einmal: python scripts/make_roster.py → PROMPTS_ALLE.md
"""
import pathlib
import sys
import tomllib

from PIL import Image

from common import PIPELINE_DIR, load_creature

DESIGN_FILE = "input/design.png"   # Ergebnis von Stufe 1 = Vorlage für Stufe 2
LOWRES_PX = 800                    # Concept-Bild schmaler als das → "kleiner, unscharfer Ausschnitt"

# Ansichten: "left"/"right" = die eigene linke/rechte Körperseite der Kreatur
VIEWS = {
    "front": "facing the camera",
    "left": "its own left side, head to the LEFT image edge",
    "right": "its own right side, head to the RIGHT image edge",
    "back": "from directly behind",
}
ORDER = ["front", "left", "right", "back"]


def roster_entry(name):
    path = PIPELINE_DIR / "creatures" / "roster.toml"
    if not path.exists():
        return {}
    for c in tomllib.loads(path.read_text(encoding="utf-8")).get("c", []):
        if c["id"] == name:
            return c
    return {}


def _clean(text):
    return " ".join(str(text).split()).rstrip(".")


def _width(path):
    try:
        with Image.open(path) as im:
            return im.width
    except OSError:
        return 0


def has_concept(cfg):
    return any(c["role"] == "design" for c in cfg.get("concept", []))


def prompt_design(title, look, style, pose, concepts, cdir, cfg):
    """Stufe 1: ein sauberes Design-Bild aus dem (verpixelten) Concept + Beschreibung –
    oder ohne Concept nur aus Beschreibung + Stil-Referenz (Design-Entwurf)."""
    roles = []
    for i, c in enumerate(concepts, 1):
        if c["role"] == "design":
            if _width((cdir / c["file"]).resolve()) < LOWRES_PX:
                roles.append(f"Image {i} is my concept art of this creature - a small, blurry crop: take the overall "
                             f"design, silhouette and colors from it, the details from the description; do not copy "
                             f"its blur.")
            else:
                roles.append(f"Image {i} is my concept art of this creature: take its design, silhouette and colors; "
                             f"the description below adds the details.")
            if cfg.get("design_pick"):
                roles.append(cfg["design_pick"])
        elif c["role"] == "style":
            roles.append(f"Image {i} is only an art-style reference: copy its rendering style, not the creatures in it.")
    img = cfg["images"]
    if any(c["role"] == "design" for c in concepts):
        task = (f"Paint ONE clean, sharp, high-resolution design image of my creature \"{title}\". Stay true to the "
                f"concept - same character, silhouette, body parts and colors - but redraw it cleanly with these "
                f"details:")
    else:
        task = (f"There is no concept art for this creature yet: design it from the description below. Paint ONE "
                f"clean, sharp, high-resolution design image of my creature \"{title}\" - an original design with a "
                f"bold silhouette that reads well from a top-down game camera:")
    return (f"{' '.join(roles)}\n\n"
            f"{task}\n\n"
            f"{look}\n\n"
            f"Style: {_clean(style)}.\n\n"
            f"Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at "
            f"body height. Pose: {pose}. All limbs clearly visible and apart from each other. "
            f"{_clean(img['background']).capitalize()} background, soft even lighting, no cast shadows, no glow, "
            f"no smoke or particles, no text. One single {img['aspect']} image.")


def prompt_views(title, look, pose, camera, views, cfg):
    """Stufe 2: 4 Ansichten, design.png ist verbindlich. Technik kompakt (Checkliste README Teil A2–A9)."""
    img = cfg["images"]
    vlist = "\n".join(f"{i}. {v}.png - {VIEWS[v]}" for i, v in enumerate(views, 1))
    return (f"Image 1 is the approved, binding design of my creature \"{title}\": keep its anatomy, shapes, colors, "
            f"materials, style and the number of all parts exactly. Do not redesign, add or remove anything.\n\n"
            f"Description (also for the hidden sides): {look}\n\n"
            f"Create {len(views)} SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, "
            f"the camera circles around it:\n{vlist}\n\n"
            f"Rules for the 3D model:\n"
            f"- Same posture in all views, only the camera moves. Pose: {pose}.\n"
            f"- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between "
            f"the legs.\n"
            f"- Thin parts have visible thickness. Same number of parts as in the design, in every view.\n"
            f"- Whole creature centered and uncropped; {_clean(camera)}; {_clean(img['background'])} background, "
            f"soft even light, no shadows, glow, particles or text; {img['aspect']}.")


def build(creature_dir):
    """Schreibt prompts.md und gibt die Bausteine zurück (für make_roster.py)."""
    cdir = pathlib.Path(creature_dir).resolve()
    cfg, bp, st = load_creature(cdir)
    ros = roster_entry(cfg["name"])
    title = cfg.get("title") or ros.get("design") or cfg["name"].replace("_", " ").title()
    look = _clean(cfg.get("look") or ros.get("look") or cfg["description"]) + "."
    pose = _clean(cfg.get("pose") or ros.get("pose") or bp["pose"])
    views = cfg["images"]["views"]
    if "front" not in views:
        raise SystemExit("images.views muss 'front' enthalten.")
    views = [v for v in ORDER if v in views] + [v for v in views if v not in ORDER]
    concepts = cfg.get("concept", [])
    attach1 = [(cdir / c["file"]).resolve() for c in concepts]
    design = (cdir / DESIGN_FILE).resolve()

    p1 = prompt_design(title, look, st["text"], pose, concepts, cdir, cfg)
    p2 = prompt_views(title, look, pose, bp["camera"], views, cfg)
    names = ", ".join(f"`{v}.png`" for v in views)
    have = "✅ liegt schon vor" if design.exists() else "noch nicht vorhanden – erst Stufe 1"
    concept = has_concept(cfg)
    if concept:
        intro = ("**Zwei Stufen:** Stufe 1 macht aus dem kleinen Concept-Ausschnitt EIN sauberes Design-Bild, das du "
                 "gegen dein Concept prüfst. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: "
                 "`look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` "
                 "erneut starten.")
        check = ("**Prüfen (du):** Passt das Bild zu deinem Concept – Charakter, Körperbau, Anzahl der Beine/Teile, "
                 "Farben? Wenn nicht: neu generieren lassen oder `look` anpassen. Wenn ja: als PNG speichern unter")
    else:
        intro = ("**Kein Concept – das Design-Bild ist der Design-Entwurf.** Stufe 1 entwirft die Kreatur nur aus der "
                 "Beschreibung (`look`) und der Stil-Referenz. **Prüfe es (du = Nutzer)** und lass es ggf. neu "
                 "generieren – erst wenn es dir gefällt, wird es als `input/design.png` verbindlich. Stufe 2 macht "
                 "daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder "
                 "`creature.toml`), dann `python scripts/make_prompts.py` erneut starten.")
        check = ("**Prüfen (du):** Ist das dein Monster? Charakter, Silhouette von schräg oben, Anzahl der Beine/Teile, "
                 "Farben, Stil (clean Low-Poly). Wenn nicht: im selben Chat neu generieren lassen („nochmal, aber …“) "
                 "oder `look` anpassen. Wenn ja: als PNG speichern unter")
    parts = [
        f"# Bildprompts: {title}",
        "",
        f"Bauplan: **{bp['label']}** · Stil: **{st['label']}** · Ordner: `{cdir / 'input'}`",
        "",
        intro,
        "",
        "## Stufe 1 – Design-Bild → `input/design.png`",
        "",
        "Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**",
        "",
        *[f"{i}. `{p}`" for i, p in enumerate(attach1, 1)],
        "",
        "```text", p1, "```",
        "",
        check,
        f"`{design}`",
        "",
        f"## Stufe 2 – 4 Ansichten → {names}",
        "",
        f"Neuer ChatGPT-Chat. **Anhängen:** 1. `{design}` ({have})",
        "",
        "```text", p2, "```",
        "",
        f"Die Bilder nacheinander als {names} in `{cdir / 'input'}` speichern. Macht ChatGPT doch ein Raster: "
        "„Bitte jede Ansicht als eigenes Bild“ nachschieben.",
        "",
        "## Prüfung vor Tripo (Claude, Pflicht)",
        "",
        "Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, "
        "Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn "
        "und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, "
        "kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.",
    ]
    out = cdir / "prompts.md"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    (cdir / "input").mkdir(exist_ok=True)
    print(f"Prompts geschrieben: {out}  (Stufe 1 + Stufe 2, {len(views)} Ansichten)")
    return {"title": title, "stage1": p1, "stage2": p2, "attach1": attach1, "design": design,
            "views": views, "input": cdir / "input", "look": look, "concept": concept}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    build(sys.argv[1])
