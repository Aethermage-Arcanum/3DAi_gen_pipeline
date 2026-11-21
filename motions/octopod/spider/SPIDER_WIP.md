# SPIDER_WIP – Zwischenstand Bau octopod/spider (Broodling)

Stand 2026-11-21, Bau-Agent. Nicht committet.

## Erledigt
- **Beinerkennung für Ein-Mesh-Spinnen** (`rigging/octopod_detect.py` → `detect_single`, greift nur bei ≤ 3 verschweißten
  Mesh-Teilen, `single_mesh = "auto"` in `rigging/octopod_defaults.toml`): Fußspitzen = Extremitäten der
  Oberflächen-Entfernung am Boden, Beinwurzel = Sprung der Wand-Dicke (SDF), Gelenkketten L/R gespiegelt gemittelt,
  von Tripo verschmolzene Flächen (Bein ↔ Rumpf weit weg von der Wurzel, Bein ↔ Bein) werden gelöscht. 8/8 Beine.
- **Rig** (`rigging/octopod_rig.py`, nur im Ein-Mesh-Fall): Trennebene Vorderkörper/Hinterleib, Hinterleib + Eierhaufen
  starr an `Abdomen_1`; Rumpf-Mitnahme am Beinansatz nur an der Coxa.
- **Muster** `style.toml` + `spider_clips.py`: Walk, Run, Idle, Ready, TurnLeft/Right, Attack1, Attack2 (Root Motion),
  Hit, Death (Baukasten-Platzhalter). Alle Baukasten-Prüfungen grün, Drehrichtung geprüft.
- `rigging/joint_densify_review.py visible` kennt jetzt Achtbeiner-Namen (Thorax, Abdomen_* → Hinterleib, Coxa/Femur).

## Arbeitsdateien
`temp/sp_work/` (uv, rig, clips, anim, Skripte rigview.sh / clips_stretch.sh / gifs.sh / render_wide.py / sheet.py),
Ausgangsstand für Regression: `temp/sp_base/` (crab auf Chitin Crawler + ant).

- Pipeline `--stage motion` (Roh-GIFs `creatures/10_broodling/rig/anim/raw/`) und `--stage full` (✓ ALLES OK) gelaufen.
- Regression: crab auf Chitin Crawler (`--style octopod/crab --stage check`) Fingerabdruck **gleich** wie `temp/sp_base`;
  `regression.py --deep --creatures chitin_crawler --against temp/sp_base` **identisch**.
- READMEs: Muster, Kreatur, `rigging/README.md` (Ein-Mesh-Abschnitt), `motions/README.md` (Tabelle).

## Offen (für Nutzer/Orchestrator)
- Roh-GIFs abnehmen. Naturvideos konnte der Agent nicht ansehen.
- Coxa↔Femur-Gelenk Bein III/IV dehnt sich bis 2,64 (Attack1), liegt unter dem Eierhaufen. Mögliche Abhilfe: Gelenk-Verdichtung
  (`joint_densify.py`) auch im octopod-Rig einbauen (bisher nur quadruped/raptor).
- Standard-Vorschau schneidet Attack2 ab (feste Kamera, G12a); Ersatz: `Octopod_Spider_Attack2_wide.gif`.
