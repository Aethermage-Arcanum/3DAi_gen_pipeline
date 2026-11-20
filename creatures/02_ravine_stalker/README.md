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

## C9-Test: Gelenk-Verdichtung (2026-11-20) – NICHT eingeschaltet, Entscheidung Nutzer
Testkreatur für den Baustein `rigging/joint_densify.py` (Beschreibung: `rigging/README.md` → „Gelenk-Verdichtung“).
Getestet an einer **Kopie** (`temp/c9_test/02_ravine_stalker/creature.toml`), weil der Wolf fertig ist und sich nicht
ändern darf: diese `creature.toml` hat KEINEN `[joint_densify]`-Abschnitt, der Wolf baut weiter exakt wie vorher.
Zum dauerhaften Einschalten diesen Abschnitt hier in die `creature.toml` übernehmen (danach Wolf neu bauen + abnehmen):
```toml
[joint_densify]
[[joint_densify.joint]]
bones = ["Leg_*_2", "Leg_*_3"]      # Ellbogen/Knie + Handgelenk/Sprunggelenk
```
| | ohne | mit Verdichtung |
|---|---|---|
| Dreiecke / Vertices | 4.258 / 3.208 | 5.058 / 3.682 (+800 Tris = +19 %) |
| Dehnung in den Gelenk-Ringen, Run (max · Kanten > 1,5 · > 2,0) | 2,05 · 18 · 2 | 1,78 · 12 · 0 |
| … Walk / Ready / TurnLeft (max) | 1,63 / 1,55 / 1,64 | 1,51 / 1,43 / 1,49 |
| Dehnung gesamt (Run 2,89 Flanke Hüfte, Attack1 2,27 Kopf) | unverändert | unverändert – Gewichts-Frage, nicht Gelenk |
| Gelenk-Lücken, Export, Gegentest FBX/GLB | 1,05 cm, ok | 1,05 cm, ok (alle Prüfungen grün) |

Prüfbilder (Render | Drahtgitter | Dehnung je Dreieck): `rig/c9_joint_densify/wolf_sprunggelenk_run8_vorher_nachher.png`,
`rig/c9_joint_densify/wolf_knie_run4_vorher_nachher.png`, Nahaufnahme über den ganzen Run-Clip:
`rig/c9_joint_densify/wolf_sprunggelenk_run_vorher_nachher.gif`. Kompletter Testbau (Roh-GIFs `rig/anim/raw/`, End-GIFs
`rig/anim/final/`, FBX/GLB `output/`): `temp/c9_wolf_test/` (nicht versioniert, mit dem Befehl oben reproduzierbar:
`python scripts/creature_pipeline.py temp/c9_test/02_ravine_stalker --work temp/c9_wolf_test`).
Bewertung: weniger und schwächer gedehnte Dreiecke direkt am Knie/Sprunggelenk; die Bewegung ist unverändert. Sichtbar
nur in der Nahaufnahme – aus der Spielkamera kaum. Hauptzweck des Bausteins ist der Frosch (lange Kanten, tiefe Hocke).
