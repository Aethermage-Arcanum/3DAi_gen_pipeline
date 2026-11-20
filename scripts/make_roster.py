"""Legt für alle Kreaturen aus creatures/roster.toml Ordner + creature.toml + prompts.md an
und schreibt PROMPTS_ALLE.md (alle Prompts in einem Dokument zum Abarbeiten, je Kreatur 2 Stufen).

  python scripts/make_roster.py
Ordner: creatures/<NN>_<id> (laufende Nummer, BACKLOG G7) – neue Kreaturen bekommen die nächste freie Nummer.
Bestehende creature.toml werden nie überschrieben (eigene Anpassungen bleiben erhalten).
Die Beschreibung (`look`) und Sonder-Posen (`pose`) stehen in creatures/roster.toml – make_prompts.py liest sie dort.
Vorhandene Bilder (design.png, front/left/right/back.png) werden nie angefasst, nur die Prompts neu geschrieben.
Kreaturen ohne Concept Art (kein `artist`/`cell` im Roster, seit 2026-11-18): creature.toml nur mit Stil-Referenz,
Stufe 1 entwirft das Design aus der Beschreibung (make_prompts.py), `input/.gitkeep` hält den leeren Ordner im Git.
"""
import pathlib
import tomllib

import make_prompts
from common import creature_dir_for

PIPE = pathlib.Path(__file__).resolve().parent.parent
R = tomllib.loads((PIPE / "creatures" / "roster.toml").read_text(encoding="utf-8"))
BIOMES = tomllib.loads((PIPE / "templates" / "biomes.toml").read_text(encoding="utf-8"))


def biome_label(key):
    return BIOMES.get(key, {}).get("label", key or "?")


style = (PIPE / R["style_ref"]).resolve()
out = ["# Alle ChatGPT-Prompts – zwei Stufen pro Kreatur", "",
       "Seit 2026-11-18 (BACKLOG A10). Pro Kreatur:", "",
       "1. **Stufe 1 – Design-Bild:** neuer ChatGPT-Chat → die genannten Bilder anhängen (Concept-Ausschnitt + "
       "Stil-Referenz) → Prompt 1 einfügen → **ein** Bild. **Du prüfst es gegen dein Concept** (Charakter, "
       "Körperbau, Anzahl Beine/Teile, Farben). Passt es nicht: neu generieren lassen oder `look` in "
       "`creatures/roster.toml` anpassen und `python scripts/make_roster.py` neu starten. Passt es: als "
       "`input/design.png` speichern.",
       "2. **Stufe 2 – 4 Ansichten:** neuer ChatGPT-Chat → nur `input/design.png` anhängen → Prompt 2 einfügen → "
       "4 Einzelbilder als `front.png`, `left.png`, `right.png`, `back.png` in denselben `input`-Ordner speichern.",
       "3. **Claude prüft** die 4 Ansichten nach der Checkliste (`README.md`, Teil A), erst dann Tripo.", "",
       "Kreaturen mit fertigem Tripo-Modell (markiert) brauchen das nur bei einem Neubau – ihre Bilder bleiben, wie sie sind.",
       "**Ohne Concept** (markiert, Roster-Erweiterung 2026-11-18): Stufe 1 bekommt nur die Stil-Referenz und entwirft die "
       "Kreatur aus der Beschreibung – **das Design-Bild ist der Design-Entwurf**, du prüfst es (gefällt es dir?) und "
       "lässt es ggf. neu generieren.",
       "Übersicht aller Concept-Ausschnitte: `creatures/concept_crops.png`.", "",
       "| # | Kreatur | Tripo-Modell | design.png |", "|---|---|---|---|"]
body = []
for i, c in enumerate(R["c"], 2):
    d = creature_dir_for(c["id"])                     # creatures/NN_<id>; neue Kreatur → nächste freie Nummer
    (d / "input").mkdir(parents=True, exist_ok=True)
    toml = d / "creature.toml"
    if not toml.exists() and not c.get("artist"):          # ohne Concept: nur Stil-Referenz
        (d / "input" / ".gitkeep").touch()
        toml.write_text(
            f'# {c["design"]} – aus creatures/roster.toml erzeugt (Roster-Erweiterung 2026-11-18, OHNE Concept Art:\n'
            f'# das Design-Bild aus Stufe 1 ist der Design-Entwurf, der Nutzer prüft es).\n'
            f'# Heimat-Biom: {biome_label(c.get("biome"))} ({c.get("biome", "?")}) · Rolle: {c.get("role", "?")} · Beschreibung (look), Pose und '
            f'Varianten: creatures/roster.toml · Biome: templates/biomes.toml\n'
            f'name = "{c["id"]}"\nbodyplan = "{c["bodyplan"]}"\nstyle = "lowpoly_b"\n'
            f'description = "{c["design"]}: {c["hint"]}"   # Fallback – die Beschreibung steht in roster.toml (look)\n\n'
            f'[[concept]]\nfile = "{style.as_posix()}"\nrole = "style"\n', encoding="utf-8")
    elif not toml.exists():
        toml.write_text(
            f'# {c["design"]} – aus creatures/roster.toml erzeugt (docs/archiv/ROADMAP_20_KREATUREN.md)\n'
            f'name = "{c["id"]}"\nbodyplan = "{c["bodyplan"]}"\nstyle = "lowpoly_b"\n'
            f'description = "{c["design"]}: {c["hint"]}"   # Fallback – die Beschreibung steht in roster.toml (look)\n'
            f'design_pick = "Recreate only the large creature in front; ignore the grey silhouettes, any text and '
            f'the background of the concept."\n\n'
            f'[[concept]]\nfile = "input/concept/design_{c["artist"]}.png"\nrole = "design"\n\n'
            f'[[concept]]\nfile = "{style.as_posix()}"\nrole = "style"\n', encoding="utf-8")
    cur = toml.read_text(encoding="utf-8")
    if "[motion]" not in cur and c.get("motion"):      # Bewegungsmuster + Vorbild nachtragen (nie überschreiben)
        refs = ", ".join(f'"{v}"' for v in c.get("vorbild", []))
        block = ["", "# Bewegung: Skelett/Muster (motions/<skelett>/<muster>), Variante, Vorbild-Tiere für die",
                 "# Naturbeobachtung (Videos werden VOR dem Animieren dazu gesucht) – bitte prüfen/korrigieren",
                 "[motion]", f'style = "{c["motion"]}"', f'variant = "{c.get("variant", "")}"', f"vorbild = [{refs}]", ""]
        toml.write_text(cur.rstrip() + "\n" + "\n".join(block), encoding="utf-8")
    p = make_prompts.build(d)
    model = (d / "raw" / "generate_model.glb").exists()
    out.append(f"| {i} | [{c['design']}](#{i}-{c['design'].lower().replace(' ', '-')}) | "
               f"{'✅ vorhanden' if model else '–'} | {'✅' if p['design'].exists() else '–'} |")
    names = ", ".join(f"`{v}.png`" for v in p["views"])
    body += [f"## {i}. {c['design']}", "",
             (f"Artist {c['artist']}" if c.get("artist") else "**Ohne Concept** – Design-Entwurf aus der Beschreibung, "
              f"Heimat-Biom {biome_label(c.get('biome'))}, Rolle {c.get('role', '?')}") + f" · Ordner `{p['input']}`" +
             (" · **Tripo-Modell vorhanden – nur bei Neubau nötig**" if model else ""), "",
             "### Stufe 1 – Design-Bild → `input/design.png`", "",
             "Anhängen: " + "  ".join(f"{k}. `{x}`" for k, x in enumerate(p["attach1"], 1)), "",
             "```text", p["stage1"], "```", "",
             f"### Stufe 2 – 4 Ansichten → {names}", "",
             f"Anhängen: 1. `{p['design']}`", "",
             "```text", p["stage2"], "```", ""]
(PIPE / "PROMPTS_ALLE.md").write_text("\n".join(out + [""] + body), encoding="utf-8")
print("PROMPTS_ALLE.md:", len(R["c"]), "Kreaturen, je 2 Stufen")
