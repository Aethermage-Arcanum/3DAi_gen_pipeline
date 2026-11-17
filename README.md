# 01 – Kreatur-Pipeline

Ziel: Aus einer kurzen Beschreibung wird eine fertige, performante Kreatur (Mesh + UV + PBR-Textur + Rig + Animation) für Blender/Unity. Alles über Konfig-Dateien steuerbar und wiederholbar.

## Ablauf

| # | Schritt | Wer | Kosten |
|---|---|---|---|
| 1 | `creature.toml` schreiben (Bauplan, Stil, Beschreibung) | du | – |
| 2 | `python scripts/make_prompts.py creatures/<name>` → `prompts.md` | Skript | – |
| 3 | **Ein** Prompt pro Kreatur in ChatGPT → 4 Einzelbilder, als `front/left/right/back.png` in `input/` speichern | du | ChatGPT-Abo |
| 4 | `python scripts/tripo_run.py creatures/<name> --steps generate` → Mesh + Textur in `raw/` (Tripo-Rig/Animation für Krabbler nicht nutzen) | Skript | Tripo-Credits |
| 5 | `python scripts/creature_pipeline.py creatures/<name>` (jedes Skelett) → UV-Prüfung, eigenes Rig, alle Clips des Bewegungsmusters, Selbstprüfung, Vorschau-GIFs, FBX/GLB + Events | Skript | – |

Vor Schritt 4 immer zuerst `--dry-run` anhängen. Das zeigt, was passieren würde, und kostet nichts.

**Moveset (welche Animationen jedes Monster braucht):** siehe [MOVESET.md](MOVESET.md).
**Alle Kreaturen-Prompts auf einmal:** `python scripts/make_roster.py` (Liste: `creatures/roster.toml`) → [PROMPTS_ALLE.md](PROMPTS_ALLE.md). Concept-Ausschnitt pro Kreatur: `python scripts/concept_crops.py` → `creatures/<id>/input/concept/design_<A|B>.png`, Übersicht `creatures/concept_crops.png`.
**Plan für alle 20 Kreaturen:** siehe [ROADMAP_20_KREATUREN.md](ROADMAP_20_KREATUREN.md).
**Krabbler-Rig + Animation:** siehe [rigging/README.md](rigging/README.md).

## Stellschrauben

- `pipeline.toml`: globale Standardwerte, z. B. **`face_limit`** (Polygon-Obergrenze = wichtigster Performance-Regler), Texturqualität, Rig-Version, Animationen
- `templates/bodyplans.toml`: Neutralpose + Kamera + Rig-Typ pro Bauplan (octopod, hexapod, quadruped, serpentine, avian, aquatic, biped)
- `templates/styles.toml`: Stil-Vorlagen (dark_fantasy, stylized, realistic)
- `creatures/<name>/creature.toml`: eine Kreatur; kann jeden Wert aus `pipeline.toml` überschreiben

## Ordner pro Kreatur

```
creatures/<name>/
  creature.toml     Eingabe
  prompts.md        generiert – zum Kopieren in ChatGPT
  input/            deine Bilder aus ChatGPT
  raw/              Tripo-Ergebnisse + tripo_state.json (Task-IDs, Credits) – nicht von Hand ändern
  output/           fertige Exporte (Schritt 5)
```

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
`blender -b --factory-startup -P scripts/inspect_model.py -- raw/generate_model.glb review/` (vorn, Seite, oben, ARPG). Prüfen:
1. Hängende oder überzählige Teile unter dem Körper oder zwischen den Beinen (Front- und Unteransicht).
2. Hufe/Füße: Abstand vorne gegen hinten (gleich breit?), Beine stehen auf dem Boden.
3. Verschmolzene Gliedmaßen und Hautbrücken.
4. Grundpose gerade (Wirbelsäule, Schwanz, Schlangenkörper).
5. Einseitige, offene Flächen (Flügel, Segel) und ihre Anzahl.
6. Beinzahl und Teile gegen das Concept.
7. Textur sauber, keine Bildreste.

Ergebnis: Freigabe für das Rig **oder** neues Referenzbild bzw. neuer Tripo-Lauf (Credits: vorher den Nutzer fragen) **oder** eine bekannte Rig-Korrektur mit Begründung.

## Zusammenarbeit (seit 2026-11-17)

1. **Bewegung zuerst grob zeigen:** `python scripts/creature_pipeline.py creatures/<name> --stage motion` → Roh-GIFs in `rig/anim/raw/` (mit allen Dehnungen/Rissen, keine Prüfung bremst). Pro neuem Muster zuerst Walk + Attack, neben Standbildern aus dem Naturvideo. **Der Nutzer nimmt die Bewegung ab.**
2. **Danach bereinigen** – nur am Mesh/Rig/Gewichten, nie durch kleinere Bewegung. Muss die Bewegung doch geändert werden, wird das vorher gezeigt.
3. **Endfassung:** `--stage full` → GIFs in `rig/anim/final/`, FBX/GLB, Gegentest, Fingerabdruck. Die Roh-Fassung bleibt liegen.
4. **Begrenzt iterieren:** Sieht ein Clip nach ~3 Versuchen nicht gut aus → aufhören und fragen.
5. **Freigabe durch den Nutzer:** `python scripts/approve.py creatures/<name>` → gesperrt. Ab dann `python scripts/regression.py` (schnell) bzw. `--deep` vor jedem Commit an gemeinsamem Code.

**Aufbau:** Die Ablaufsteuerung (`creature_pipeline.py`) ist für alle gleich und enthält kein Tierwissen. Pro Beinart gibt es ein eigenes Rig + einen eigenen Baukasten (`rigging/<skelett>_rig.py`, `motions/<skelett>/<skelett>_kit.py`), pro Muster eigenen Clip-Code. Gemeinsam sind nur Allzweck-Teile (UV-Prüfung, Lückenprüfung, Export, Gegentest, Fingerabdruck).

## Stand

- 2026-11-17: Prompt-Generator und Tripo-Skript fertig. API-Kette (Upload, Task, Polling, Rig-Check) mit einem Testmodell geprüft, ohne Credit-Verbrauch.
- 2026-11-17: Stil B (Low-Poly) entschieden → Tripo-Standard auf P-Serie, `face_limit = 4000`. Prozedurale Anbauteile (Stacheln/Platten) als Prototyp in `procedural/`, siehe dortige README.
- Noch offen: Prompt-Generator auf „Concept-Art-Ausschnitt als Vorlage“ umbauen (statt Text-Beschreibung). Erstes echtes Monster aus der Concept Art wählen.
