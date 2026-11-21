# 10 Broodling (octopod/spider)

Kleine Waldspinne mit Eierhaufen auf dem Rücken. Bewegungsmuster: [`motions/octopod/spider`](../../motions/octopod/spider/README.md)
(Recherche + Naturvideos: [RESEARCH.md](../../motions/octopod/spider/RESEARCH.md)). Vorbilder: Wolfsspinne mit Eikokon, Springspinne (Sprungbiss).

```
python scripts/creature_pipeline.py creatures/10_broodling --stage motion   # Roh-GIFs
python scripts/creature_pipeline.py creatures/10_broodling --stage full     # Export + Gegentest
```

## Kennzahlen (Stand 2026-11-21, `--stage full` ✓ ALLES OK)
| | |
|---|---|
| Dreiecke | 4.218 (1 Mesh) |
| Materialien / Draw Calls | 1 / 1 |
| Texturen | Color + Normal, je 1024² (Tripo liefert 2048²) |
| Knochen | 43 (35 mit Gewichten; Fühler/Mandibeln/Abdomen_2 sind Standard-Platzhalter ohne Gewichte) |
| UV | Tripo-UV (50 Inseln, 60 % Abdeckung, Winkel-Grenzwert knapp verletzt) |
| Größe | 1,0 × 0,97 × 0,71 m |
| Clips | 10 (`Octopod_Spider_*`), Gelenk-Lücken 0,0 cm |

## Rig
Ein zusammenhängendes Tripo-Mesh → Ein-Mesh-Erkennung von `rigging/octopod_detect.py` (8/8 Beine, siehe `rigging/README.md`).
Hinterleib samt Eierhaufen hängt starr an `Abdomen_1` (Trennebene schräg vor dem Eierhaufen). Befund: Nicht das vordere,
sondern das 3. Beinpaar schwebt im Modell am meisten (Spitze 2,4 cm über dem Boden); alle Clips setzen die Standfüße auf.

## Ausgaben
- `rig/anim/raw/` Roh-GIFs (ARPG + Seite), dazu `Octopod_Spider_Attack2_wide.gif` (weite Kamera für den Sprung)
- `rig/anim/final/` GIFs der Endfassung · `output/Broodling.fbx|.glb` + `Broodling_events.json`
- Messwerte: `rig/clips_report.json` (Baukasten), `rig/spider_checks.json` (Fußkontakt, Drehrichtung, Tempo, Sprungweite),
  `rig/stretch_visible.json` (Dehnung auf den aus der Spielkamera sichtbaren Flächen)
