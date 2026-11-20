# Bog Warden (Elite · Sumpf) – upright/treant

Wandelnder Sumpfbaum, langsamer Tank mit Wurzel-Slam. Erste Kreatur des Skeletts **`upright`** (2026-11-18).
Design ohne Concept Art (Roster-Erweiterung, Design-Bild Stufe 1 vom Nutzer geprüft).

```
python scripts/tripo_run.py creatures/18_bog_warden --steps generate        # erledigt (raw/), Credits bezahlt
python scripts/creature_pipeline.py creatures/18_bog_warden --stage motion  # Roh-GIFs rig/anim/raw/
python scripts/creature_pipeline.py creatures/18_bog_warden                 # Export + Gegentest + End-GIFs
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 4.003 (Tripo 3.666 + 337 für doppelseitiges Moos) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² (ORM nur im GLB) |
| Knochen | 27 (Skelett `upright`; Platzhalter ohne Gewicht: Neck, Head – das Gesicht sitzt im Stamm) |
| UV | Tripo-UV (902 Inseln, 57 % Abdeckung, 0,2 % Überlappung; Smart-UV schlechter) |
| Frei hängend | Moos-Strähnen unter der Krone über `[dangling]` (Shader, keine Knochen) |
| Clips | 10 (Walk, Run, Idle, Ready, TurnLeft/Right, Attack1 Wurzel-Slam, Attack2 Ast-Peitsche, Hit, Death = Platzhalter) |

## Modellprüfung (vor dem Rig)
- Massiger, gebückter Stamm, zwei kurze, dicke Wurzelbeine mit Krallen-Wurzelfüßen (2 Bodenkontakt-Gruppen).
- Zwei sehr lange Astarme, die Wurzelfinger-Hände hängen frei neben den Beinen (≈ 5 cm über dem Boden).
- Kein eigener Kopf: Das Gesicht sitzt oben im Stamm. Darüber eine breite Krone aus toten Ästen mit Moos-Strähnen.
- Baumpilze am Stamm. 3.666 Dreiecke, 30 Mesh-Teile, 1 Material.
- `model_check` warnt bei Mittellinie (0,33) und Symmetrie (60 %). Das ist die gewollte krumme, asymmetrische Baumform und
  ist mit Begründung in `creature.toml` → `[model_check.freigabe]` freigegeben.

## Rig (upright)
- Gelenke aus der Geometrie (Anteil der Höhe): Schritt 0,29, Achsel 0,49, Kronen-Basis 0,69.
- Knie und Knöchel an Bein-Engstelle bzw. Ende der Wurzelspreizung. Ellbogen an der stärksten Biegung, Handgelenk wo die
  Hand breiter wird, Fingeransatz wo sich die Wurzelfinger trennen.
- Krone + Äste 100 % starr an `Crown` (schwingt im Clip als Ganzes verzögert nach), mit weichem Übergang am Stamm.
- Moos-Strähnen sind Tripo-Platten ohne Rückseite und werden doppelseitig gemacht (`[upright.double_sided]`, +337 Dreiecke).
  Die Strähnen-Enden schwingen per `[dangling]` nach (Prüfbild `rig/dangling_preview.png`).
- Pilze und lose Moos-Teile hängen starr an ihrer Ansatzstelle.

## Prüfbilder
- `rig/upright_rig.png`: Skelett vorn/seitlich + Gewichte.
- `rig/rig_debug.png`, `rig/dangling_preview.png`.
- `rig/anim/raw/*.gif` (Roh) und `rig/anim/final/*.gif` (Endfassung).
- Einzelbild-Streifen der Clips: `temp/review/upright_*.png`.

## Naturreferenzen
Elefant (Schritt), Gorilla (Boden-Schlag), Elefantenrüssel (Peitsche), Baum im Sturm (Krone). Links und abgeleitete Werte:
`motions/upright/treant/README.md`.

## Messwerte (Pipeline `full`, 2026-11-18)
- Alle 10 Clips grün, Gegentest FBX + GLB ok (27 Knochen, max. 4 Einflüsse, 0 ungewichtete Vertices, Moos-Markierung kommt an).
- Fußkontakt: 0 cm, Rutschen 0 mm pro Frame. Schleifen nahtlos.
- TurnLeft dreht links (Standfüße −34°), der Oberkörper führt (+14°).
- Slam: Hände 0,9 bzw. 1,9 cm im Boden (Hand-IK).
- Dehnung (nur Info): max. 2,9 (Attack2, Brust/Krone).
- Lückenprüfung: keine Berühr-Paare (Mesh ist ein Stück), also ohne Aussage.

## Offen
- BACKLOG C13: Moos unter den Ästen wirkt steif. Nur die Strähnen-Spitzen sind für den Shader markiert, und in Blender-GIFs schwingt Moos nie.
- Death ist nur ein Platzhalter (Death-Clips sind vom Nutzer pausiert).
- Bewegung vom Nutzer noch nicht abgenommen.
