"""Legt für alle Kreaturen aus creatures/roster.toml Ordner + creature.toml + prompts.md an
und schreibt PROMPTS_ALLE.md (alle Prompts in einem Dokument zum Abarbeiten).

  python scripts/make_roster.py
Bestehende creature.toml werden nie überschrieben (eigene Anpassungen bleiben erhalten).
"""
import pathlib
import tomllib

import make_prompts

PIPE = pathlib.Path(__file__).resolve().parent.parent
R = tomllib.loads((PIPE / "creatures" / "roster.toml").read_text(encoding="utf-8"))
sheet = (PIPE / R["sheet"]).resolve()
style = (PIPE / R["style_ref"]).resolve()
out = ["# Alle ChatGPT-Prompts (je Kreatur ein Prompt → 4 Einzelbilder)", "",
       f"**Pro Kreatur:** neuer ChatGPT-Chat → anhängen: 1. den Ausschnitt `input/concept/design_*.png` der Kreatur "
       f"(Übersicht: `creatures/concept_crops.png`) 2. `{style}` → Prompt einfügen → "
       "die 4 Bilder als `front/left/right/back.png` in den genannten `input`-Ordner speichern.", ""]
for i, c in enumerate(R["c"], 2):
    d = PIPE / "creatures" / c["id"]
    (d / "input").mkdir(parents=True, exist_ok=True)
    toml = d / "creature.toml"
    if not toml.exists():
        toml.write_text(
            f'# {c["design"]} – aus creatures/roster.toml erzeugt (ROADMAP_20_KREATUREN.md)\n'
            f'name = "{c["id"]}"\nbodyplan = "{c["bodyplan"]}"\nstyle = "lowpoly_b"\n'
            f'description = "{c["design"]}: {c["hint"]}"\n'
            f'design_pick = "Image 1 is a crop from a concept sheet: recreate ONLY the large creature in front, '
            f'ignore the grey silhouettes and any text in the background."\n\n'
            f'[[concept]]\nfile = "input/concept/design_{c["artist"]}.png"\nrole = "design"\n\n'
            f'[[concept]]\nfile = "{style.as_posix()}"\nrole = "style"\n', encoding="utf-8")
    make_prompts.build(d)
    txt = (d / "prompts.md").read_text(encoding="utf-8")
    prompt = txt.split("```text\n", 1)[1].split("```", 1)[0]
    out += [f"## {i}. {c['design']} (Artist {c['artist']}) → `{d / 'input'}`", "",
            f"Anhängen: 1. `{d / 'input' / 'concept' / ('design_' + c['artist'] + '.png')}` 2. Stil-Bild", "", "```text", prompt.rstrip(), "```", ""]
(PIPE / "PROMPTS_ALLE.md").write_text("\n".join(out), encoding="utf-8")
print("PROMPTS_ALLE.md:", len(R["c"]), "Kreaturen")
