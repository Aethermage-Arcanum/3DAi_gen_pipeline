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

Schritt 0 – Varianten zuerst (seit 2026-11-20, BACKLOG G9, nur für NEUE Kreaturen):
  --stage variants schreibt  VARIANTEN.md          aus templates/VARIANTEN_VORLAGE.md, vorbefüllt aus `varianten`
                                                   (nur wenn noch keine da ist – wird nie überschrieben)
                             prompts_varianten.md  optionaler ChatGPT-Prompt: ein Bild mit allen Varianten in einer Reihe
  Danach `base_look` (eingedampfte Basis) eintragen – Stufe 1 und 2 nehmen dann diesen Text statt `look`.

Woher die Texte kommen (erster Treffer gilt):
  Beschreibung  `base_look` (creature.toml → roster.toml) → `look` in creature.toml → `look` in creatures/roster.toml
                → `description` in creature.toml
  Pose          `pose` in creature.toml → `pose` in creatures/roster.toml → Bauplan (templates/bodyplans.toml)
  Zusatz St. 1  `design_note` in creature.toml → `design_note` in creatures/roster.toml (optional, nur Stufe 1,
                z. B. „Pose NICHT aus dem Concept übernehmen“ – Hollow Stag 2026-11-20, BACKLOG C12)
  Name          `title` in creature.toml → `design` in creatures/roster.toml → `name` (Kreatur-ID)

Aufruf:  python scripts/make_prompts.py creatures/<NN_name>   (oder nur die ID)
Ergebnis: creatures/<NN_name>/prompts.md  (beide Prompts zum Kopieren + was anhängen + wie speichern)
Schritt 0: python scripts/make_prompts.py <id> --stage variants [--out <ordner>]   (--out: woanders hin, zum Testen)
Alle Kreaturen auf einmal: python scripts/make_roster.py → PROMPTS_ALLE.md
"""
import argparse
import datetime
import pathlib
import tomllib

from PIL import Image

from common import CREATURES_DIR, PIPELINE_DIR, find_creature, load_creature, load_toml

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
    path = CREATURES_DIR / "roster.toml"
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


def prompt_design(title, look, style, pose, concepts, cdir, cfg, note=""):
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
            if note:
                roles.append(_clean(note) + ".")
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
            f"body height. Pose: {pose}. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. "
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
            f"- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.\n"
            f"- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between "
            f"the legs.\n"
            f"- Thin parts have visible thickness. Same number of parts as in the design, in every view.\n"
            f"- Whole creature centered and uncropped; {_clean(camera)}; {_clean(img['background'])} background, "
            f"soft even light, no shadows, glow, particles or text; {img['aspect']}.")


def build(creature_dir):
    """Schreibt prompts.md und gibt die Bausteine zurück (für make_roster.py)."""
    cdir = find_creature(creature_dir)
    cfg, bp, st = load_creature(cdir)
    ros = roster_entry(cfg["name"])
    title = cfg.get("title") or ros.get("design") or cfg["name"].replace("_", " ").title()
    look = _clean(cfg.get("base_look") or ros.get("base_look") or cfg.get("look") or ros.get("look")
                  or cfg["description"]) + "."
    pose = _clean(cfg.get("pose") or ros.get("pose") or bp["pose"])
    views = cfg["images"]["views"]
    if "front" not in views:
        raise SystemExit("images.views muss 'front' enthalten.")
    views = [v for v in ORDER if v in views] + [v for v in views if v not in ORDER]
    concepts = cfg.get("concept", [])
    attach1 = [(cdir / c["file"]).resolve() for c in concepts]
    design = (cdir / DESIGN_FILE).resolve()

    note = cfg.get("design_note") or ros.get("design_note") or ""
    p1 = prompt_design(title, look, st["text"], pose, concepts, cdir, cfg, note)
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


# ------------------------------------------------------------------------------------ Schritt 0 – Varianten zuerst
# Datenformat (roster.toml oder creature.toml), baut auf dem Bestand auf:
#   base_look = """..."""   eingedampfte Basis (Englisch, qualitativ) – ersetzt `look` in Stufe 1 + 2
#   varianten = [ { art = "grund|biom|elite", name, biome, tint, addons, size, effect,      ← Bestand
#                   slider = "Beine kürzer …", eigene_basis = "nein|grenzfall|ja",            ← neu, optional
#                   look = "short English visual note for the variant sheet" }, … ]         ← neu, optional
# Spalten der Einsortier-Tabelle: tint = Tönung · addons = Anbauteile · size + slider = Proportions-Slider ·
# effect = Shader/Partikel (Element) · eigene_basis.
VARIANTS_TEMPLATE = PIPELINE_DIR / "templates" / "VARIANTEN_VORLAGE.md"
EMPTY_VARIANTS = [{"art": a} for a in ("grund", "biom", "biom", "biom", "biom", "elite")]


def _cell(text):
    return " ".join(str(text).split()).replace("|", "/") or "–"


def _size(v):
    s = v.get("size", 1.0)
    return "" if s in ("", 1, 1.0) else f"Größe {str(s).replace('.', ',')}"


def _variant_line(v):
    """Eine Zeile im Varianten-Bogen: eigene Kurzbeschreibung `look` oder aus Tönung/Anbauteilen/Proportionen."""
    if v.get("look"):
        return _clean(v["look"])
    bits = [f"colors: {_clean(v['tint'])}" if v.get("tint") else "",
            f"added parts: {_clean(v['addons'])}" if v.get("addons") else "",
            f"proportions: {_clean(v['slider'])}" if v.get("slider") else "",
            f"about {v['size']}x the size of the base" if _size(v) else ""]
    return "; ".join(b for b in bits if b) or "variant of the base"


def prompt_variant_sheet(title, base, has_base, style, pose, concepts, variants, cfg):
    """Optional: EIN Bild mit allen Varianten nebeneinander (gleiche Pose/Ansicht) zum Vergleichen."""
    roles = [f"Image {i} is my concept art of this creature: keep its overall design as the base." if c["role"] == "design"
             else f"Image {i} is only an art-style reference: copy its rendering style, not the creatures in it."
             for i, c in enumerate(concepts, 1)]
    n = len(variants)
    vlist = "\n".join(f"{i}. {v.get('name', '?')}: {_variant_line(v)}." for i, v in enumerate(variants, 1))
    base_intro = ("Base creature - all variants share exactly this body:" if has_base else
                  "Base creature - variant 1 as described; the other variants keep only its body build, silhouette, "
                  "limbs and head shape and replace the surface details:")
    img = cfg["images"]
    return (f"{' '.join(roles)}\n\n"
            f"Paint ONE wide variant sheet of my creature \"{title}\": {n} variants of the same creature standing side "
            f"by side in one row, evenly spaced, so I can compare them. All variants share one base body - the same "
            f"silhouette, body build, limbs and head shape. They differ only in colors, added parts (plates, spikes, "
            f"moss, crystals ...), proportions and size.\n\n"
            f"{base_intro} {base}\n\n"
            f"Variants, from left to right:\n{vlist}\n\n"
            f"Style: {_clean(style)}.\n\n"
            f"Every variant in exactly the same pose and the same three-quarter view (from the front and a bit from the "
            f"side) at body height, same scale except the stated size differences. Pose: {pose}. Every leg, arm, wing "
            f"and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, "
            f"sitting or crouching. The variants do not overlap or touch each other. "
            f"{_clean(img['background']).capitalize()} background, soft even lighting, no cast shadows, no glow, no "
            f"smoke or particles. Only a small number (1-{n}) under each variant, no other text. One single wide "
            f"landscape image.")


def build_variants(creature_dir, out_dir=None):
    """Schritt 0: VARIANTEN.md (nur falls keine existiert) + prompts_varianten.md (optionaler Varianten-Bogen)."""
    cdir = find_creature(creature_dir)
    out = pathlib.Path(out_dir).resolve() if out_dir else cdir
    out.mkdir(parents=True, exist_ok=True)
    cfg, bp, st = load_creature(cdir)
    ros = roster_entry(cfg["name"])
    biomes = load_toml(PIPELINE_DIR / "templates" / "biomes.toml")
    title = cfg.get("title") or ros.get("design") or cfg["name"].replace("_", " ").title()
    base_look = cfg.get("base_look") or ros.get("base_look") or ""
    look = _clean(base_look or cfg.get("look") or ros.get("look") or cfg["description"]) + "."
    pose = _clean(cfg.get("pose") or ros.get("pose") or bp["pose"])
    variants = cfg.get("varianten") or ros.get("varianten") or []
    concepts = cfg.get("concept", [])

    done = []
    md = out / "VARIANTEN.md"
    if md.exists():
        print(f"VARIANTEN.md existiert schon – bleibt unverändert: {md}")
    else:
        rows = variants or EMPTY_VARIANTS
        blab = lambda k: biomes.get(k, {}).get("label", k) if k else "…"
        entwurf = "\n".join(
            f"| {i} | {_cell(v.get('name', '…'))} | {v.get('art', '…')} | {_cell(blab(v.get('biome')))} | "
            f"{_cell(' · '.join(x for x in (v.get('tint'), v.get('addons'), v.get('effect')) if x) or '…')} |"
            for i, v in enumerate(rows, 1))
        einsort = "\n".join(
            f"| {_cell(v.get('name', '…'))} | {_cell(v.get('tint', ''))} | {_cell(v.get('addons', ''))} | "
            f"{_cell(', '.join(x for x in (_size(v), v.get('slider', '')) if x))} | {_cell(v.get('effect', ''))} | "
            f"{v.get('eigene_basis', 'nein') if variants else '…'} |" for v in rows)
        addons = list(dict.fromkeys(_clean(v["addons"]) for v in variants if v.get("addons")))
        basis = (_clean(base_look) + "." if base_look else
                 f"*noch nicht festgelegt.* Bisher `look` (mit Details, die zu Anbauteilen werden): {look}")
        text = VARIANTS_TEMPLATE.read_text(encoding="utf-8")
        for k, val in {"TITEL": title, "DATUM": datetime.date.today().isoformat(), "ID": cfg["name"],
                       "ENTWURF": entwurf, "EINSORTIER": einsort, "NICHT_IM_MESH": "; ".join(addons) or "…",
                       "BASIS": basis, "POSE": pose}.items():
            text = text.replace("{{" + k + "}}", val)
        md.write_text(text, encoding="utf-8")
        done.append(md)

    if variants:
        p = prompt_variant_sheet(title, look, bool(base_look), st["text"], pose, concepts, variants, cfg)
        attach = [(cdir / c["file"]).resolve() for c in concepts]
        parts = [f"# Varianten-Bogen (optional, Schritt 0): {title}", "",
                 "Ein ChatGPT-Bild mit allen Varianten nebeneinander – nur zum Vergleichen, **nicht** für Tripo. "
                 "Danach Basis eindampfen und Unterschiede einsortieren (`VARIANTEN.md`), `base_look` in "
                 "`creatures/roster.toml` eintragen, dann `python scripts/make_prompts.py "
                 f"{cfg['name']}` für Stufe 1 + 2 der Basis.", "",
                 "Neuer ChatGPT-Chat. **Anhängen:**", "",
                 *[f"{i}. `{a}`" for i, a in enumerate(attach, 1)], "",
                 "```text", p, "```", "",
                 "Speichern (optional) als `input/varianten.png`. Varianten ändern: `varianten` in "
                 "`creatures/roster.toml` (pro Variante optional `look` = kurze englische Bildbeschreibung), dann "
                 "neu erzeugen."]
        pv = out / "prompts_varianten.md"
        pv.write_text("\n".join(parts) + "\n", encoding="utf-8")
        done.append(pv)
    else:
        print("Keine `varianten` im Roster/creature.toml – erst eintragen, dann gibt es den Varianten-Bogen.")
    for f in done:
        print(f"geschrieben: {f}")
    return done


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("creature", help="Kreatur-Ordner oder ID")
    ap.add_argument("--stage", choices=["images", "variants"], default="images",
                    help="images = Stufe 1 + 2 (Standard) · variants = Schritt 0")
    ap.add_argument("--out", help="nur --stage variants: Ausgabeordner statt des Kreatur-Ordners")
    a = ap.parse_args()
    if a.stage == "variants":
        build_variants(a.creature, a.out)
    else:
        build(a.creature)
