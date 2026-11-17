# 01 – Kreatur-Pipeline

Ziel: Aus einer kurzen Beschreibung wird eine fertige, performante Kreatur (Mesh + UV + PBR-Textur + Rig + Animation) für Blender/Unity. Alles über Konfig-Dateien steuerbar und wiederholbar.

## Ablauf

| # | Schritt | Wer | Kosten |
|---|---|---|---|
| 1 | `creature.toml` schreiben (Bauplan, Stil, Beschreibung) | du | – |
| 2 | `python scripts/make_prompts.py creatures/<name>` → `prompts.md` | Skript | – |
| 3 | Prompts in ChatGPT kopieren, Bilder als `front/left/back/right.png` in `input/` speichern | du | ChatGPT-Abo |
| 4 | `python scripts/tripo_run.py creatures/<name>` → Mesh, Rig-Check, Rig, Laufanimation in `raw/` | Skript | Tripo-Credits |
| 5 | Blender-Nachbearbeitung (LODs, Texturgrößen, Unity-Export) | Skript | – *(kommt als Nächstes)* |

Vor Schritt 4 immer zuerst `--dry-run` anhängen. Das zeigt, was passieren würde, und kostet nichts.

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

## Stand

- 2026-11-17: Prompt-Generator und Tripo-Skript fertig. API-Kette (Upload, Task, Polling, Rig-Check) mit einem Testmodell geprüft, ohne Credit-Verbrauch.
- 2026-11-17: Stil B (Low-Poly) entschieden → Tripo-Standard auf P-Serie, `face_limit = 4000`. Prozedurale Anbauteile (Stacheln/Platten) als Prototyp in `procedural/`, siehe dortige README.
- Noch offen: Prompt-Generator auf „Concept-Art-Ausschnitt als Vorlage“ umbauen (statt Text-Beschreibung). Erstes echtes Monster aus der Concept Art wählen.
