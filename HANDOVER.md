# Handover (Stand 2026-11-17, Ende autonomer Lauf)

Für die nächste Session: zuerst `../CLAUDE.md` (Regeln des Nutzers), dann diese Datei, dann `AUTONOM_AUFTRAG.md` (Ergebnis-Tabelle).

## Stand
- **9 fertige Kreaturen** (Mesh + UV + Rig + 9 Clips + FBX/GLB + Events, alle Prüfungen grün):
  chitin_crawler (crawler/ant), ravine_stalker (quadruped/wolf), eel_stalker (legless/cobra), dune_raptor (biped_raptor/raptor),
  void_manifestation (floater/tentacle), scorpion_matriarch (multileg/scorpion), needle_wasp (flyer/wasp),
  reef_snapper (quadruped/lizard), hollow_stag (quadruped/deer). Crab = Testmuster auf dem Chitin Crawler (style_tests/).
- Referenzbilder für **alle 20** Kreaturen liegen in `creatures/<name>/input/` (front/left/right/back.png).
- **Tripo-Guthaben 1.475 Credits** (ca. 110 pro Modell). Noch NICHT generiert: spore_drone, broodling, shore_lurker, shellback,
  stone_boar, rock_hyena, sand_leviathan, glassback_colossus, frost_colossus, flesh_titan, void_harbinger, reality_ripper.
- Git: lokales Repo `01_kreatur_pipeline`, Remote `origin` = GitHub Aethermage-Arcanum/3DAi_gen_pipeline. **Pushen nur auf Wunsch**
  (im autonomen Lauf war Push nach jeder Kreatur ausdrücklich erlaubt – das gilt nicht mehr).

## Ablauf pro Kreatur
1. Bilder: `python scripts/make_roster.py` → `PROMPTS_ALLE.md` (ein Prompt → 4 Einzelbilder). Nutzer macht die Bilder in ChatGPT.
   Prüfen: Reihenfolge (1 vorn, 2 Kopf links, 3 Kopf rechts, 4 hinten), Augenhöhe, gleiche Pose. Raster-Bilder (2×2) per Inhalt zerschneiden.
2. Tripo: `python scripts/tripo_run.py creatures/<name> --steps generate --dry-run`, dann ohne `--dry-run` (kostet Credits → vorher fragen!).
3. Ansehen: `blender -b --factory-startup -P scripts/inspect_model.py -- raw/generate_model.glb review/`
4. Alles andere kostenlos, ein Befehl: `python scripts/creature_pipeline.py creatures/<name>`
   (UV-Prüfung → Rig → Clips + Selbstprüfung → Lückenprüfung → GIFs → Export → Gegentest). Skelett/Muster aus `creature.toml [motion] style`.
5. Selbst prüfen: Clip-Übersicht, `rig/rig_debug.png` (`python rigging/draw_rig.py rig`), GIFs in `rig/anim/`, Kontaktbogen ansehen.
6. README der Kreatur (Kennzahlen), README des Musters (Naturreferenzen), commit; dem Nutzer ein GIF schicken.

## Skelette (Rig-Skript → Baukasten → Muster)
| Skelett | Rig | Baukasten | Muster |
|---|---|---|---|
| crawler | rigging/crawler_rig.py (braucht getrennte Mesh-Inseln) | motions/crawler/crawler_kit.py | ant, crab |
| multileg | rigging/multileg_rig.py (Oberflächen-Wege, beliebig viele Beine, Scheren, Schwanz) | motions/quadruped/quadruped_kit.py | scorpion |
| quadruped | rigging/quadruped_rig.py | motions/quadruped/quadruped_kit.py (Blender-IK) | wolf (Generator), lizard, deer (nutzen wolf_clips.py) |
| biped_raptor | rigging/biped_raptor_rig.py | quadruped_kit.py | raptor |
| legless | rigging/legless_rig.py | motions/legless/legless_kit.py | cobra |
| floater | rigging/floater_rig.py | motions/floater/floater_kit.py | tentacle |
| flyer | rigging/flyer_rig.py (= floater) | floater_kit.py | wasp |
Gemeinsame Rig-Bausteine: `rigging/rig_common.py`. Prüfung/Export für alle: check_gaps.py, export_unity.py, verify_export.py.

## Wiederkehrende Probleme + Lösungen (schon eingebaut)
- **Tripo-Hautbrücken** zwischen sich berührenden Gliedmaßen → reißen bei jeder Gewichtung → Flächen löschen
  (`cut_between_legs` raptor, `cut_fused_limbs` multileg, `cut_leg_bridges` + `exclusive_leg_pairs` quadruped – dort pro Kreatur einschalten).
- **UV-Naht-Duplikate** brauchen identische Gewichte (sonst Risse).
- **Gestreckte Tripo-Beine** → `reach_fix` senkt Rumpf automatisch.
- **Mittellinien-Vertices** an beiden Seiten gewichtet → reißt; Diagnose mit einem Skript, das die schlimmsten Kanten + Gewichte ausgibt.
- Dehnungsgrenze (`max_stretch`) nur nach **Sichtprüfung** pro Clip erhöhen und in style.toml begründen.
- Tripo kann Modelle gedreht liefern (`[floater] facing`), Beinzahlen falsch erfinden (Skorpion 5 Paare) – Fake it.

## Offen
- Flesh Titan (#7) – macht der Nutzer zusammen mit Claude (humanoide Teilstruktur erlaubt).
- **Unity-Test** aller Exporte (noch nie gemacht).
- Echse: Ready/Attack zu dezent. Wolf-Tod: Beine lassen sofort los (`ik_release_start` nutzen). Hirsch: Tripo-UV sehr zerstückelt.
- Prio-2-Clips aus MOVESET.md (Attack2, Dodge, Knockdown …) gibt es noch für kein Muster.
