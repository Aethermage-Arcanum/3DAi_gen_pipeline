# Shellback – schwere Küsten-Schildkröte mit Stachelpanzer

Skelett **quadruped**, Muster **quadruped/tortoise** (`motions/quadruped/tortoise/`, Details und Messwerte dort).
Vorbilder: Schnappschildkröte (Biss), Landschildkröte (Gang, Kopf einziehen). Stand 2026-11-27: **noch nicht vom
Nutzer abgenommen** (Roh-GIFs in `rig/anim/raw/`).

```
python scripts/creature_pipeline.py creatures/11_shellback --stage motion   # Roh-GIFs
python scripts/creature_pipeline.py creatures/11_shellback --stage full     # Export + Gegentest
```

## Kennzahlen (Export `output/Shellback.fbx` / `.glb`)
| | |
|---|---|
| Dreiecke | **4.344** (1 Mesh; Hauptkörper + 2 Augen) |
| Materialien / Draw Calls | **1** / 1 |
| Texturen | Color, Normal, ORM je **1024²** (Tripo 2048² verkleinert; ORM nur in der GLB) |
| Knochen | **30** (Standard-Vierbeiner, Unity „Generic“), max. 4 Einflüsse, 0 ungewichtete Vertices |
| Clips | 10 × `Quadruped_Tortoise_*` (Death = Platzhalter) |
| UV | Tripo-UV (89 Inseln, Abdeckung 59 %, keine Überlappung; Warnung Dichte 1,05–1,74× an den Krallen, Winkel – Smart UV mit 901 Inseln schlechter) |
| Maße | Länge 1,0 · Höhe 0,6 (Modell-Einheiten) |

## Prüfung Teil B Tripo-Modell (2026-11-23) – bestanden
Messung `review/model_check.png`: keine Auffälligkeiten (4 Fußgruppen, Fußbreite hinten/vorne 1,02×, nichts hängt,
Symmetrie exakt, 3 Teile = Körper + 2 Augen). Sichtprüfung (`temp/sh_inspect/view_*.png`, vorn/Seite/oben/ARPG):
- Kein hängendes Teil zwischen den Beinen, Schwanzstachel waagerecht hinter dem Panzer (nicht wie in `back.png` nach unten).
- Beine frei, keine Hautbrücken; Beine gespreizt (gewollt), Vorderbeine massig und weit vorn.
- Grundpose gerade; Maul leicht offen (erlaubt).
- Abweichung zum Concept (bekannt, Design-Frage): 1 Auge pro Seite statt mehrerer, kein sichtbarer Hals, Kopf kommt direkt
  unter dem Nackenschild hervor.
- Textur sauber.

## Rig-Einstellungen (`creature.toml [quadruped.rig]`)
`rigid_shell` (Panzer 100 % starr an Spine_1, Übergang nach Abstand 7 cm), `shell_neck_free` (Halsöffnung/Kehle ohne
Schulterblatt), `knee_out = 0.07` (Hinterbeine als gerade Säulen modelliert → Knie 4 cm nach außen, Kette 0,89/0,92 statt
0,96/0,98 gestreckt). Begründung und Messungen: `motions/quadruped/tortoise/README.md`.
Gewichte als Farben (grau = Panzer starr): `rig/gewichte_panzer.png` (Seite, vorn, oben, ARPG, hinten-unten; Prüfwerkzeug `temp/sh_scripts/weights_view.py`).

## Selbstprüfung (`--stage full`, 2026-11-27): ✓ alles ok
- Fußkontakt Walk/Run/Turn 0,0 mm, Stand-Clips Füße 0,0 mm, Schleifen nahtlos.
- Drehrichtung gemessen: TurnLeft +30 °/s, Kopf +31,5° > Brust +6° (Kopf führt); TurnRight spiegelbildlich.
- Attack1: Nase beim Treffer 22,7 cm vor der Ruhe-Nase, 28,7 cm vor dem Panzer, 24 cm hoch. Attack2: Root Motion 0,24 m,
  Panzerfront beim Treffer 18,4 cm vor der Ruhe, 30 cm hoch.
- Gelenk-Lücken max. 0,9 cm (Grenze 1,5 cm). Export-Gegentest FBX + GLB ok.
- **Dehnung auf den aus der Spielkamera sichtbaren Flächen** (`rig/dehnung_sichtbar.json`): Rücken/Flanke (Panzer) 1,00 in
  allen Clips; Walk max 1,65 · Run 1,78 · Turn 1,62 · Idle 1,61 · Ready 1,76 · Hit 1,40 · Attack2 2,09 ·
  **Attack1 Halsansatz/Kehle 2,6, Hals 2,1** (Rest: Hals ohne Hautreserve, liegt unter dem Kopf).

## Naturreferenzen
`motions/quadruped/tortoise/RESEARCH.md` §3: Schnappschildkröten-Biss in Zeitlupe (Brave Wilderness „Snapper Bites Hand in
Super Slow Motion“), Gang Aldabra-Riesenschildkröte / Leopardschildkröte / Indische Sternschildkröte (Stock-Videos),
Schmidt et al. 2016 (Gangart, Schultergürtel), Zani et al. 2005 (Tempo, Heben), NC Wildlife (Abwehrhaltung).
Videos vom Agenten nicht selbst angesehen – bitte beim Abnehmen dagegenhalten.
