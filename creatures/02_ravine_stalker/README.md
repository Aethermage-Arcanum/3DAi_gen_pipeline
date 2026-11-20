# Ravine Stalker (Mammals · Highlands) – quadruped/wolf

Erster Vierbeiner, Referenz für das Vierbeiner-Skelett. Erstellt 2026-11-17 im autonomen Lauf.

## Ablauf (reproduzierbar)
```
python scripts/tripo_run.py creatures/02_ravine_stalker --steps generate   # 110 Credits, schon erledigt (raw/)
python scripts/creature_pipeline.py creatures/02_ravine_stalker             # kostenlos: UV, Rig, Clips, Prüfung, GIFs, Export
```

## Kennzahlen
| | |
|---|---|
| Dreiecke | 4.258 (Tripo P-Serie, face_limit 4000) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² (Tripo lieferte 2048²) |
| Knochen | 30 (Standard-Vierbeiner inkl. Schulterblätter, Kiefer, 4 Schwanzglieder) |
| UV | Tripo-UV behalten: 113 Inseln, 61 % Abdeckung, 0 % Überlappung (Winkelverzerrung knapp über Grenze) |
| Clips | 9 (Walk 0,26 m/s, Run 0,90 m/s, Turn 32 °/s, Idle, Ready, Attack1, Hit, Death) – alle grün |
| Gelenk-Lücken | max. 0,7 cm |

Ausgabe: `output/RavineStalker.fbx` (Unity), `.glb`, `_events.json` (footstep/hit/dead). Vorschau: `rig/anim/*.gif`, Rig-Skizze `rig/rig_debug.png`, UV-Prüfblatt `uv/uv_preview.png`.

## Erkenntnisse
- Tripo-Beine fast gestreckt → automatische Rumpf-Absenkung (`reach_fix`), kürzere Schritte.
- UV-Naht-Duplikate brauchten identische Gewichte (sonst Risse bis 5 cm) – im Rig behoben, gilt für alle Vierbeiner.
- Schulterblätter mit IK-Steifigkeit verhindern Risse an der Schulter im Galopp.
- Details: `motions/quadruped/README.md`, `motions/quadruped/wolf/README.md`.
