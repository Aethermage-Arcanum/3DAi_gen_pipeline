# 01 – Kreatur-Pipeline

Ziel: Aus einer kurzen Beschreibung wird eine fertige, performante Kreatur (Mesh + UV + PBR-Textur + Rig + Animation) für Blender/Unity. Alles über Konfig-Dateien steuerbar und wiederholbar.

## Ablauf

**Varianten zuerst (seit 2026-11-20, BACKLOG G8 d – Standard für neue Kreaturen, Schritt 0):** Pro Monster erst 5–6 Varianten designen/brainstormen (Grundform, Biome, Elite). Was alle gemeinsam haben (Silhouette, Körperbau, Gliedmaßen, Kopf-Grundform) wird die **Basis-Kreatur**; nur sie geht ohne variable Details durch die Schritte 1–5 (Tripo). Unterschiede: nur Farbe → Tönung · Teile dazu/weg (Stacheln, Eiszapfen, Moos, Kristalle …) → Anbauteile per Geometry Nodes mit Slidern · dicker/größer/längere Hörner → Proportions-Slider · Glut/Frost/Gift → Shader + Partikel in Unity · starke Silhouetten-Abweichung → eigene Basis-Kreatur. Alle Varianten teilen ein Rig und einen Clip-Satz. **Bestehende Modelle** bleiben: eingebrannte Details, Varianten nur über Tönung + Anbauteile. Ziel: 250–500 Varianten aus 50–100 Basis-Monstern. Prompt-Schritt dafür: „Schritt 0 – Varianten“ unten. *Noch nicht gebaut:* Varianten-Baukasten (Geometry Nodes, BACKLOG G9, nach den Skeletten). Die Tabelle unten beschreibt Schritt 1–5 pro Basis-Kreatur.

| # | Schritt | Wer | Kosten |
|---|---|---|---|
| 1 | Kreatur eintragen: `creatures/roster.toml` (Bauplan, Concept-Zelle, **`look`** = ausführliche Beschreibung, ggf. `pose`, Heimat-`biome`, bei neuen auch `role` + `varianten`) bzw. `creature.toml` | du / Claude | – |
| 2 | `python scripts/make_prompts.py creatures/<NN_name>` (alle: `make_roster.py`) → `prompts.md` mit **zwei** Prompts | Skript | – |
| 3a | **Stufe 1 – Design-Bild:** Concept-Ausschnitt + Stil-Referenz + Prompt 1 in ChatGPT → **ein** sauberes Bild. **Du prüfst es gegen dein Concept** und speicherst es als `input/design.png` | du | ChatGPT-Abo |
| 3b | **Stufe 2 – 4 Ansichten:** `input/design.png` + Prompt 2 in einen neuen Chat → 4 Einzelbilder als `front/left/right/back.png` in `input/`. **Claude prüft** sie nach Checkliste Teil A | du, dann Claude | ChatGPT-Abo |
| 4 | `python scripts/tripo_run.py creatures/<NN_name> --steps generate` → Mesh + Textur in `raw/` (Tripo-Rig/Animation für Krabbler nicht nutzen) | Skript | Tripo-Credits |
| 5 | `python scripts/creature_pipeline.py creatures/<NN_name>` (jedes Skelett) → UV-Prüfung, eigenes Rig, alle Clips des Bewegungsmusters, Selbstprüfung, Vorschau-GIFs, FBX/GLB + Events | Skript | – |

Vor Schritt 4 immer zuerst `--dry-run` anhängen. Das zeigt, was passieren würde, und kostet nichts.

**Warum zwei Stufen (seit 2026-11-18, BACKLOG A10):** Die Concept-Ausschnitte sind winzig und verpixelt (Original-Sheet nur 1536×1024, ein Ausschnitt ≈ 190×110 px), und die alten Prompts beschrieben die Kreatur in einem einzigen Satz zwischen vielen Technik-Anweisungen → ChatGPT fantasierte. Jetzt:
- **Stufe 1** macht aus Ausschnitt + ausführlicher Beschreibung **ein** sauberes, hochauflösendes Design-Bild (Dreiviertel-Ansicht, Neutralpose, neutraler Hintergrund, ganze Kreatur). Du entscheidest, ob es dein Monster ist → `input/design.png`.
- **Stufe 2** nimmt nur noch `input/design.png` als **verbindliche** Vorlage (nicht mehr den verpixelten Ausschnitt) und macht daraus die 4 Ansichten.
- **Beschreibung (`look`)**: Englisch, ca. 6–12 Sätze, **qualitativ** – Charakter/Wirkung, Silhouette, Körperbau, Kopf, Gliedmaßen (Anzahl ja), Schwanz, markante Merkmale, Farben pro Körperbereich, Material. **Keine Zahlen, Maße oder Verhältnisse** – der KI Kreativität lassen. Nur, was im Concept zu sehen ist bzw. dazu passt. Steht vorn und dominant; Technik (Pose, Hintergrund, Licht, Ansichten, Checkliste A2–A9) kompakt am Ende.
- **Ohne Concept Art** (Roster-Erweiterung 2026-11-18, 16 Kreaturen): Stufe 1 bekommt nur die Stil-Referenz und **entwirft** die Kreatur aus `look` – das Design-Bild ist dann der Design-Entwurf. Du prüfst, ob es dir gefällt, und lässt es ggf. neu generieren. Erkennung automatisch: kein `[[concept]]` mit `role = "design"`. Kreaturen mit Concept behalten exakt ihren Prompt-Text.
- Quelle der Texte (erster Treffer gilt): `look`/`pose` in `creature.toml` → in `creatures/roster.toml` → `description` bzw. Bauplan-Pose (`templates/bodyplans.toml`). Vorhandene Bilder werden nie angefasst – fertige Kreaturen bleiben, wie sie sind; nur `prompts.md` wird neu geschrieben.

**Moveset (welche Animationen jedes Monster braucht):** siehe [MOVESET.md](docs/MOVESET.md).
**Alle Kreaturen-Prompts auf einmal:** `python scripts/make_roster.py` (Liste: `creatures/roster.toml`) → [PROMPTS_ALLE.md](PROMPTS_ALLE.md). Concept-Ausschnitt pro Kreatur: `python scripts/concept_crops.py` → `creatures/<NN_id>/input/concept/design_<A|B>.png`, Übersicht `creatures/concept_crops.png`.
**Plan für alle 20 Kreaturen:** siehe [ROADMAP_20_KREATUREN.md](docs/archiv/ROADMAP_20_KREATUREN.md). **16 Ergänzungen** (ohne Concept, Claude hat ausgewählt): [ROSTER_ERWEITERUNG_VORSCHLAG.md](docs/recherche/ROSTER_ERWEITERUNG_VORSCHLAG.md) → Abschnitt „Gewählt“.
**Biome:** [templates/biomes.toml](templates/biomes.toml) – zentrale Liste mit 18 Biomen (Wald, Küste, Highlands, Wüste, Schnee, Abyss, Höhle, Vulkan, Sumpf, Krypta, Gras/Steppe, Stein, Kristall, Tempel/Ruinen, Oase, Dschungel, Pilzwald, Eis), je Stimmung, Tönungs-Palette, Akzent/Glühen, typische Anbauteile (Geometry Nodes) und Element-Effekt. Varianten pro Kreatur (Grundform + 4 Biome + Elite-Addon) stehen in `creatures/roster.toml` → `varianten` (Bestand; neue Kreaturen: „Varianten zuerst“, siehe oben).
**Krabbler-Rig + Animation:** siehe [rigging/README.md](rigging/README.md).

### Schritt 0 – Varianten (seit 2026-11-20, BACKLOG G9; nur neue Kreaturen)

1. **Varianten festlegen (Nutzer):** 5–6 Varianten (Grundform, Biome, Elite) als `varianten` in `creatures/roster.toml` eintragen (bzw. `creature.toml`). Danach `python scripts/make_roster.py`, falls die Kreatur noch keinen Ordner hat.
2. `python scripts/make_prompts.py <id> --stage variants` → `creatures/<NN_id>/VARIANTEN.md` (aus [templates/VARIANTEN_VORLAGE.md](templates/VARIANTEN_VORLAGE.md), vorbefüllt; wird **nie überschrieben**, wenn sie schon existiert) und `prompts_varianten.md`. Mit `--out <ordner>` landet beides woanders, z. B. zum Testen.
3. **Optional – Varianten-Bogen:** Prompt aus `prompts_varianten.md` + Stil-Referenz in ChatGPT → **ein** Bild mit allen Varianten nebeneinander (gleiche Pose und Ansicht, alle Beine in voller Länge). Das Bild dient nur zum Vergleichen und geht nicht zu Tripo.
4. **Basis eindampfen + einsortieren** in `VARIANTEN.md`: Gemeinsames → Basis-Kreatur; Unterschiede → Tönung (`tint`) · Anbauteile (`addons`) · Proportions-Slider (`size`, `slider`) · Shader/Partikel (`effect`). Bei starker Silhouetten-Abweichung `eigene_basis = "ja"` setzen: Die Variante wird dann eine eigene Kreatur.
5. **`base_look`** (Englisch, qualitativ, ohne variable Details) in den Roster-Eintrag schreiben. Danach erzeugt `python scripts/make_prompts.py <id>` die Stufen 1 und 2 aus `base_look` statt aus `look`. Ab hier läuft alles wie in der Tabelle oben.

Datenformat (baut auf dem bestehenden `varianten` auf, alle neuen Felder sind optional):
```toml
base_look = """A massive, hump-backed quadruped ... (no ice, no plates)"""
varianten = [
  { art = "grund", name = "Rimehide Bear", biome = "ice", tint = "Weiß/Stahlblau", addons = "Eisplatten", size = 1.0,
    effect = "Frost-Atem", slider = "", eigene_basis = "nein", look = "pale blue-white fur, clear ice slabs on the back" },
]
```
`look` pro Variante ist eine kurze englische Beschreibung für den Varianten-Bogen. Fehlt sie, setzt das Skript die Zeile aus `tint`/`addons`/`slider`/`size` zusammen. Kreaturen ohne die neuen Felder bekommen exakt dieselben Prompts wie vorher.

## Stellschrauben

- `pipeline.toml`: globale Standardwerte, z. B. **`face_limit`** (Polygon-Obergrenze = wichtigster Performance-Regler), Texturqualität, Rig-Version, Animationen
- `creatures/roster.toml`: alle Kreaturen aus der Concept Art, je mit **`look`** (Beschreibung für die Prompts) und optional `pose` (Sonder-Neutralpose, z. B. Knöchelgang, Flügel, Tentakel)
- `templates/bodyplans.toml`: Neutralpose (kompakt) + Kamera + Rig-Typ pro Bauplan (octopod, hexapod, quadruped, serpentine, avian, aquatic, biped; seit 2026-11-18 auch upright, winged, floater, amorph, static)
- `templates/biomes.toml`: alle Biome mit Tönung, Anbauteilen und Effekt für die Varianten
- `templates/styles.toml`: Stil-Vorlagen (dark_fantasy, stylized, realistic)
- `creatures/<NN_name>/creature.toml`: eine Kreatur; kann jeden Wert aus `pipeline.toml` überschreiben

## Ordner pro Kreatur

```
creatures/<NN_name>/
  creature.toml     Eingabe
  prompts.md        generiert – zwei Prompts (Stufe 1 Design-Bild, Stufe 2 4 Ansichten) zum Kopieren in ChatGPT
  input/            deine Bilder aus ChatGPT: design.png (Stufe 1) + front/left/right/back.png (Stufe 2);
                    concept/ = Concept-Ausschnitt(e)
  raw/              Tripo-Ergebnisse + tripo_state.json (Task-IDs, Credits) – nicht von Hand ändern
  output/           fertige Exporte (Schritt 5)
```

**Laufende Nummer im Ordnernamen** (seit 2026-11-20, BACKLOG G7): `creatures/01_chitin_crawler/`, `02_ravine_stalker/` … in der Reihenfolge, in der die Kreaturen bearbeitet bzw. erstellt wurden (zuerst die fertigen, dann die Tripo-Modelle vom 18.11., dann der Rest in Roster-Reihenfolge). **Nur der Ordner trägt die Nummer.** Die Kreatur-ID (`id` im Roster, `name` in creature.toml), der Exportname (`ChitinCrawler.fbx`, abgeleitet aus `name`) sowie die Clip- und Unity-Namen bleiben ohne Nummer. Alle Skripte nehmen den Ordner oder nur die ID (`python scripts/creature_pipeline.py chitin_crawler` reicht). Die Übersetzung zwischen Ordner und ID steckt an einer einzigen Stelle: `scripts/common.py` (`find_creature`, `creature_id`, `export_name`, `creature_dir_for`). Eine neue Kreatur im Roster bekommt bei `make_roster.py` automatisch die nächste freie Nummer.

## Gut zu wissen

- **Wiederholbar und kostensicher:** `tripo_run.py` merkt sich erledigte Schritte. Ein zweiter Aufruf mit gleichen Einstellungen kostet nichts. Mit geänderten Einstellungen bricht es ab, bis du `--force <schritt>` angibst. Neue Bilder machen Rig und Animation automatisch ungültig.
- **Rig-Check ist kostenlos** und sagt, ob das Modell riggbar ist und welcher Typ empfohlen wird.
- **Animationen:** Tripo hat für Kreaturen nur je einen Laufzyklus (octopod/hexapod/quadruped walk, serpentine/aquatic march, Flieger gar keinen). Alles Weitere wird prozedural in Unity gelöst (IK-Beine, Wellen, Flügelschlag).
- **Kein Glühen ins Bild:** Leuchteffekte landen sonst fest in der Textur. Die kommen später als Emission-Map/Shader dazu.
- **Ansichten left/right** meinen die eigene linke/rechte Körperseite der Kreatur. Falls Tripo mit vertauschten Seiten schlechte Modelle baut, ist das der erste Verdacht. *(Noch nicht verifiziert.)*

## Prüfung von Referenzbild und Tripo-Modell (Pflicht, macht Claude – seit 2026-11-17)

**Erkenntnis des Nutzers:** Viele Fehler, die erst in der Animation auffallen, stecken schon im Tripo-Modell und davor im ChatGPT-Referenzbild.
Deshalb prüft Claude **gründlich vor jedem bezahlten Tripo-Lauf** die Bilder und **vor dem Riggen** das Modell. Die Ergebnisse kommen ins README der Kreatur.
Bei einem Befund gilt: Bild neu machen lassen (kostet nichts) statt später im Rig reparieren.

**Gilt für beide Bild-Stufen** (seit 2026-11-18): Das **Design-Bild** (Stufe 1, `input/design.png`) prüft **der Nutzer gegen sein Concept** – ist es das Monster, das er meint (Charakter, Körperbau, Anzahl Beine/Teile, Farben)? Fehler hier wandern in alle 4 Ansichten. Die **4 Ansichten** (Stufe 2) prüft **Claude nach der Checkliste A** – zusätzlich gegen `design.png` (gleiche Kreatur, gleiche Teilezahl, nichts hinzuerfunden).

**A. Referenzbilder (vor Tripo), jedes Bild einzeln und alle vier im Vergleich:**
1. Reihenfolge und Blickrichtung stimmen (1 vorn, 2 Kopf links, 3 Kopf rechts, 4 hinten), Kamera auf Augenhöhe, keine Draufsicht.
2. **Gleiche Körperhaltung in allen vier Ansichten.** Waagerechter Körper in der Seitenansicht heißt waagerecht auch vorne und hinten. *(Dune Raptor: vorne aufrecht, seitlich waagerecht → Tripo hat einen Hautlappen gebaut.)*
3. **Nichts hängt zwischen den Beinen**, zum Beispiel ein Schwanz, der in der Frontansicht zwischen den Beinen zu sehen ist. *(Raptor: „zweiter Schwanz“.)*
4. **Beinstellung vorne und hinten gleich breit**, Beine gerade nach unten, nicht gespreizt. *(Hollow Stag: Hinterbeine 2,4× so breit wie vorne.)*
5. **Gliedmaßen frei:** Beine, Arme, Scheren, Tentakel berühren sich nicht und berühren den Körper nicht, sonst baut Tripo Hautbrücken. *(Raptor-Beine, Skorpion-Gliedmaßen.)*
6. **Neutrale, gerade Grundpose:** Schlangen und Schwänze gestreckt, nicht verdreht oder eingerollt; Maul zu oder nur leicht offen. *(Eel Stalker: feste Krümmung/Drehung im Modell, die Animation kommt dagegen nicht an.)*
7. **Anzahl der Teile stimmt:** Beinpaare, Flügel, Tentakel wie im Concept und in jeder Ansicht gleich. *(Skorpion: Tripo hat 5 Beinpaare erfunden.)*
8. **Dünne Teile mit Volumen** (Flügel, Flossen, Hautsegel) und klar vom Körper getrennt. *(Wespe: Flügel als einseitige Fläche → unsichtbar aus manchen Winkeln.)*
9. Kein Glühen und keine Effekte im Bild, neutraler Hintergrund, keine Schrift.

**B. Tripo-Modell (nach Tripo, vor dem Rig), Bilder ansehen und messen:**
1. **Messung (Frühwarnsystem):** `python scripts/model_check.py creatures/<NN_name>` (alle: `--all`) →
   `review/model_check.json` + `review/model_check.png` (vorn/Seite/oben/unten, Auffälligkeiten **rot**, mit Begründung freigegebene **orange**).
   Misst: einseitige Flächen, Fuß-Gruppen am Boden gegen die Beinzahl des Skeletts, Fußabstand hinten/vorne (Vierbeiner),
   hängende Teile unter der Bauchlinie zwischen den Beinen, Krümmung/Verdrehung der Mittellinie, Symmetrie, Schwerpunkt über den Füßen,
   Dreiecke gegen `face_limit`, lose Mesh-Teile. Schwellen: `scripts/model_check.toml`; pro Kreatur `[model_check]` in `creature.toml`,
   gewollte Befunde **nur mit Begründung** freigeben: `[model_check.freigabe] haengende_teile = "Tentakel hängen gewollt unter dem Körper"`.
   Blender-Teil: `rigging/model_check_blender.py`. Belegt an den bekannten Fällen (Stag 2,46×, Raptor-Lappen, Wespe 124 einseitige Flächen,
   Skorpion 12 statt 8–10 Bodenkontakte, Eel Krümmung/Drehung); Ravine Stalker ohne Befund.

   > ⚠ **Automatische Messung = nur Frühwarnsystem. Eine individuelle Sichtprüfung des Modells (Bilder ansehen, gegen Concept und
   > Referenzbilder vergleichen) durch den Agenten ist IMMER zusätzlich notwendig.** „Keine automatischen Auffälligkeiten“ ist **keine Freigabe** –
   > viele Fehler (falsche Form, verschmolzene Gliedmaßen, Textur, Abweichung vom Concept) misst das Skript gar nicht.
2. **Sichtprüfung (Pflicht):** `model_check.png` und zusätzlich `blender -b --factory-startup -P scripts/inspect_model.py -- raw/generate_model.glb review/`
   (vorn, Seite, oben, ARPG) ansehen, gegen Concept und Referenzbilder vergleichen. Prüfen:
1. Hängende oder überzählige Teile unter dem Körper oder zwischen den Beinen (Front- und Unteransicht).
2. Hufe/Füße: Abstand vorne gegen hinten (gleich breit?), Beine stehen auf dem Boden.
3. Verschmolzene Gliedmaßen und Hautbrücken.
4. Grundpose gerade (Wirbelsäule, Schwanz, Schlangenkörper).
5. Einseitige, offene Flächen (Flügel, Segel) und ihre Anzahl.
6. Beinzahl und Teile gegen das Concept.
7. Textur sauber, keine Bildreste.

Ergebnis: Freigabe für das Rig **oder** neues Referenzbild bzw. neuer Tripo-Lauf (Credits: vorher den Nutzer fragen) **oder** eine bekannte Rig-Korrektur mit Begründung.

**Grenze der KI-Bildgenerierung (Nutzer 2026-11-18):** ChatGPT hält sich sehr stark an angehängte Vorlagen (Concept-Ausschnitt, `design.png`) – auch wenn man mehrfach ausdrücklich eine andere Pose verlangt. Beispiel Frosch: gestreckte Beine oder T-Pose waren nicht zu bekommen, weil die Vorlage hockend war. Folgerung: Die **Pose muss schon im Design-Bild (Stufe 1) stimmen**; in Stufe 2 lässt sie sich kaum noch ändern. Geht es trotzdem nicht, löst das der Rig/Baukasten (Gliedmaßen per IK auf den Boden setzen, Teile starr anhängen) – Fake it.

## Zusammenarbeit (seit 2026-11-17)

1. **Bewegung zuerst grob zeigen:** `python scripts/creature_pipeline.py creatures/<NN_name> --stage motion` → Roh-GIFs in `rig/anim/raw/` (mit allen Dehnungen/Rissen, keine Prüfung bremst). Pro neuem Muster zuerst Walk + Attack, neben Standbildern aus dem Naturvideo. **Der Nutzer nimmt die Bewegung ab.**
2. **Danach bereinigen** – nur am Mesh/Rig/Gewichten, nie durch kleinere Bewegung. Muss die Bewegung doch geändert werden, wird das vorher gezeigt.
3. **Endfassung:** `--stage full` → GIFs in `rig/anim/final/`, FBX/GLB, Gegentest, Fingerabdruck. Die Roh-Fassung bleibt liegen.
4. **Begrenzt iterieren:** Sieht ein Clip nach ~3 Versuchen nicht gut aus → aufhören und fragen.
5. **Freigabe durch den Nutzer:** `python scripts/approve.py creatures/<NN_name>` → gesperrt. Ab dann `python scripts/regression.py` (schnell) bzw. `--deep` vor jedem Commit an gemeinsamem Code.

**Aufbau:** Die Ablaufsteuerung (`creature_pipeline.py`) ist für alle gleich und enthält kein Tierwissen. Pro Beinart gibt es ein eigenes Rig + einen eigenen Baukasten (`rigging/<skelett>_rig.py`, `motions/<skelett>/<skelett>_kit.py`), pro Muster eigenen Clip-Code. Gemeinsam sind nur Allzweck-Teile (UV-Prüfung, Lückenprüfung, Export, Gegentest, Fingerabdruck).

## Stand

- 2026-11-17: Prompt-Generator und Tripo-Skript fertig. API-Kette (Upload, Task, Polling, Rig-Check) mit einem Testmodell geprüft, ohne Credit-Verbrauch.
- 2026-11-17: Stil B (Low-Poly) entschieden → Tripo-Standard auf P-Serie, `face_limit = 4000`. Prozedurale Anbauteile (Stacheln/Platten) als Prototyp in `procedural/`, siehe dortige README.
- 2026-11-18: Prompt-Generator **zweistufig** (Design-Bild → 4 Ansichten) mit ausführlicher qualitativer Beschreibung (`look`) für alle 20 Roster-Kreaturen (BACKLOG A10).
