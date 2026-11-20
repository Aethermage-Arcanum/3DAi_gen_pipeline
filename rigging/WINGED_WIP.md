# winged (drake + bird) – Zwischenstand (WIP, nicht freigegeben) – 2026-11-20

Build-Agent `winged` (Auftrag BACKLOG G6). Kreaturen: 14_cinder_wyvern (winged/drake), 15_bonepicker_vulture (winged/bird).

## Vorab-Prüfung
- Beide Tripo-Modelle + Referenzbilder vorhanden (raw/generate_model.glb, input/design|front|left|right|back.png).
- Modellprüfung B (Sichtprüfung, Bilder in temp/winged_work/*_inspect.png, *_refs.png):
  - Wyvern: Flügel ungleich (links steil hochgestellt + nach hinten gefegt, rechts seitlich), Schwanz seitlich gebogen
    (schon im Referenzbild: Frontansicht zeigt den Schwanz seitlich) → Rig/Clips geben Flügel UND Schwanz absolut vor.
    Flügelhaut einseitig (75 Fl.) → double_sided. Kleine lose Teile = Zähne. Keine verschmolzenen Gliedmaßen. ✅ Rig.
  - Geier: symmetrisch, Flügel halb offen hängend, Federn einseitig (332 Fl.) → double_sided. Lose Teile = Brustknochen-
    Platte (332 V.) und Halsknochen (135 V.) → hängen je Vertex am nächsten Haupt-Mesh-Vertex. ✅ Rig.

## Dateien (eigene)
- rigging/winged_detect.py ✅ (Füße, Beine/Schritt, Flügel über Seitenebene, Hals/Schwanz über Geodäten-Ringe)
- rigging/winged_defaults.toml ✅
- rigging/winged_rig.py (in Arbeit)
- motions/winged/winged_kit.py, motions/winged/drake/*, motions/winged/bird/* (offen)

## Entscheidungen
- Knochen (36): Root · Pelvis → Spine_1 → Spine_2 → Chest · Chest → Neck_1..3 → Head → Jaw · Pelvis → Tail_1..6 ·
  Chest → Clavicle_s → UpperArm_s → Forearm_s → Hand_s → Finger_1_s → Finger_2_s · Pelvis → Thigh_s → Shin_s → Foot_s → Toe_s
- Beine digitigrad (Vogel/Raptor): IK-Kette Thigh+Shin+Foot auf den Fußballen, Zehen folgen dem Ziel.
- Wyvern läuft zweibeinig (Flügel halb gefaltet erhoben, wie Referenzbild). Offene Frage an den Nutzer: Gang auf den
  Flügel-Handgelenken (Fledermaus/Pterosaurier) als Alternative?

## Debug
- temp/winged_work/t_detect.py (Erkennung ohne Blender + Plot), dump.py (Mesh → npz), viz.py

## Stand (laufend aktualisiert)
- Rig + Baukasten + drake/bird Clips laufen (Testordner temp/winged_rigtest/<kreatur>, Skript temp/winged_work/run_drake.sh).
- Gemeinsame Dateien geändert (nur winged-Einträge): rigging/verify_export.py (SKELETONS["winged"], vor upright),
  scripts/model_check.toml ([skelett.winged]). creature.toml beider Kreaturen: [winged.double_sided], [model_check.freigabe],
  Geier zusätzlich [dangling].
- ✅ 2026-11-20: `--stage motion` (Roh-GIFs rig/anim/raw/) und `--stage full --no-preview` für beide: ✓ ALLES OK
  (Export FBX/GLB, Gegentest, Lücken 0,0 cm). Regression --deep: keine freigegebenen Kreaturen; verify_export für
  Bog Warden (upright) neu geprüft → identisch. READMEs: motions/winged/{README, drake/README, bird/README},
  rigging/README (Abschnitt winged), creatures/14 + 15 README.
- Offen: Abnahme der Bewegung durch den Nutzer; Feueratem-Clip (Wyvern); Hinterzehen-Dehnung (Geier); Death = Platzhalter.
- NICHT committet (Auftrag).
