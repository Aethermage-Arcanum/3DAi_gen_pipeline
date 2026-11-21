# BEAR_WIP – Zwischenstand Build-Agent Rimehide Bear (2026-11-21)

**Stand: fertig gebaut, nicht committet, wartet auf Abnahme der Bewegung durch den Nutzer.**

## Fertig
- Teil B Modellprüfung: freigegeben → `creatures/32_rimehide_bear/review/inspect_views.png`, `model_check.png`
- UV: Tripo-UV behalten (`creatures/32_rimehide_bear/uv/uv_preview.png`)
- Rig-Code `rigging/quadruped_rig.py`: optionale Werte `[detect] spine_slice`, `[rig] chest_extend`,
  `[rig] rigid_parts_exclude`; Schwanzketten-Lücken fortlaufend füllen. Regression `--deep` (gegen `temp/br_base`):
  Wolf, Hirsch, Reef Snapper identisch; Bär identisch zur eigenen Endfassung.
- Muster `motions/quadruped/bear/` (bear_clips.py, style.toml, README.md), 10 Clips, `--stage full` ✓ ALLES OK
- Roh-GIFs `creatures/32_rimehide_bear/rig/anim/raw/`, End-GIFs `rig/anim/final/`, Export `output/RimehideBear.fbx/.glb`
- README des Bären mit Kennzahlen, Andock-Knochen, Dehnung; Prüfbogen `review/dehnung_arpg.png`

## Offen / für den Nutzer
- Bewegung abnehmen (Walk, Run, Attack1, Attack2, Turn)
- Accessoires starr vs. mitskinnen (Haut weicht bis 2–5 cm vom Knochen ab) – siehe README des Bären
- Statur-Varianten nur neu gebacken oder uniform skalieren – siehe README des Musters
