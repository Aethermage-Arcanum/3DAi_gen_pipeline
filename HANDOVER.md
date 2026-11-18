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
1. Bilder – **zwei Stufen** (seit 2026-11-18, BACKLOG A10): `python scripts/make_roster.py` → `PROMPTS_ALLE.md` + `creatures/<name>/prompts.md`.
   Beschreibung = `look` in `creatures/roster.toml` (qualitativ, Englisch, keine Zahlen/Verhältnisse; Sonder-Pose `pose`). Nutzer macht die Bilder in ChatGPT:
   **Stufe 1** Concept-Ausschnitt + Stil-Referenz + Prompt 1 → ein Design-Bild → **Nutzer prüft gegen sein Concept** → `input/design.png`.
   **Stufe 2** neuer Chat, nur `input/design.png` + Prompt 2 → `front/left/right/back.png`.
   Prüfen (Stufe 2, auch gegen design.png): Reihenfolge (1 vorn, 2 Kopf links, 3 Kopf rechts, 4 hinten), Augenhöhe, gleiche Pose. Raster-Bilder (2×2) per Inhalt zerschneiden.
   **Pflicht: Claude prüft die Bilder gründlich nach der Checkliste in README.md („Prüfung von Referenzbild und Tripo-Modell“, Teil A) – vor jedem Tripo-Lauf.**
2. Tripo: `python scripts/tripo_run.py creatures/<name> --steps generate --dry-run`, dann ohne `--dry-run` (kostet Credits → vorher fragen!).
3. Messen + ansehen: `python scripts/model_check.py creatures/<name>` → `review/model_check.png/.json` (Frühwarnsystem: einseitige Flächen,
   Fuß-Gruppen vs. Beinzahl, Fußbreite hinten/vorne, hängende Teile zwischen den Beinen, Krümmung/Verdrehung, Symmetrie, Schwerpunkt, Dreiecke, lose Teile).
   **Das Skript ersetzt die Sichtprüfung NICHT** (Nutzer-Anweisung): Prüfbild + `blender -b --factory-startup -P scripts/inspect_model.py -- raw/generate_model.glb review/`
   selbst ansehen und gegen Concept/Referenzbilder vergleichen → **Pflichtprüfung Teil B** (hängende Teile, Beinbreite vorn/hinten, Hautbrücken, gerade Pose, einseitige Flächen, Teilezahl).
   Gewollte Befunde in `creature.toml` `[model_check.freigabe]` mit Begründung freigeben.
4. Alles andere kostenlos, ein Befehl: `python scripts/creature_pipeline.py creatures/<name>`
   (UV-Prüfung → Rig → Clips + Selbstprüfung → Lückenprüfung → GIFs → Export → Gegentest). Skelett/Muster aus `creature.toml [motion] style`.
5. Selbst prüfen: Clip-Übersicht, `rig/rig_debug.png` (`python rigging/draw_rig.py rig`), GIFs in `rig/anim/`, Kontaktbogen ansehen.
6. README der Kreatur (Kennzahlen), README des Musters (Naturreferenzen), commit; dem Nutzer ein GIF schicken.

## Skelette (Rig-Skript → Baukasten → Muster)
| Skelett | Rig | Baukasten | Muster |
|---|---|---|---|
| hexapod | rigging/hexapod_rig.py (braucht getrennte Mesh-Inseln) | motions/hexapod/hexapod_kit.py | ant (später mantis) |
| octopod | rigging/octopod_rig.py (Kopie, gleiche Erkennung) | motions/octopod/octopod_kit.py | crab (Test auf Chitin Crawler), später spider |
| multileg | rigging/multileg_rig.py (Oberflächen-Wege, beliebig viele Beine, Scheren, Schwanz) | motions/multileg/multileg_kit.py | scorpion |
| quadruped | rigging/quadruped_rig.py | motions/quadruped/quadruped_kit.py (Blender-IK) | wolf, lizard, deer (je eigener Clip-Code) |
| biped_raptor | rigging/biped_raptor_rig.py | motions/biped_raptor/biped_kit.py | raptor |
| legless | rigging/legless_rig.py | motions/legless/legless_kit.py | cobra |
| floater | rigging/floater_rig.py | motions/floater/floater_kit.py | tentacle (2026-11-18: wabbelt ab der Wurzel – Learnings in motions/floater/tentacle/README.md; Void-Modell wird neu gemacht) |
| flyer | rigging/flyer_rig.py + flyer_defaults.toml | motions/flyer/flyer_kit.py | wasp (gutes Beispiel) |
Gemeinsame Rig-Bausteine: `rigging/rig_common.py`, Lückenprüfung: `rigging/gaps_defaults.toml`. Prüfung/Export für alle: check_gaps.py, export_unity.py, verify_export.py.

## Wiederkehrende Probleme + Lösungen (schon eingebaut)
- **Tripo-Hautbrücken** zwischen sich berührenden Gliedmaßen → reißen bei jeder Gewichtung → Flächen löschen
  (`cut_between_legs` raptor, `cut_fused_limbs` multileg, `cut_leg_bridges` + `exclusive_leg_pairs` quadruped – dort pro Kreatur einschalten).
- **UV-Naht-Duplikate** brauchen identische Gewichte (sonst Risse).
- **Frontbild zeigt Schwanz zwischen den Beinen** → Tripo baut einen hängenden Bauch-Lappen („2. Schwanz“) → `[biped_raptor] cut_belly_flap` (Dune Raptor).
- **Eng stehende Beine** (Hirsch) liegen im Bauch-Messstreifen → Gelenke zu tief → `[quadruped.rig] adaptive_belly_strip`. **Tripo-Hinterbeine zu breit** → `narrow_hind_legs`. **Geweih/Hörner** am Hals gewichtet → `rigid_head_above`.
- **Gestreckte Tripo-Beine** → `reach_fix` senkt Rumpf automatisch.
- **Mittellinien-Vertices** an beiden Seiten gewichtet → reißt; Diagnose mit einem Skript, das die schlimmsten Kanten + Gewichte ausgibt.
- Dehnungsgrenze (`max_stretch`) nur nach **Sichtprüfung** pro Clip erhöhen und in style.toml begründen.
- Tripo kann Modelle gedreht liefern (`[floater] facing`), Beinzahlen falsch erfinden (Skorpion 5 Paare) – Fake it.
- **Einseitige Flügel** (Tripo baut Insektenflügel als offene Platten ohne Rückseite) → in Unity aus manchen Winkeln
  unsichtbar (Backface Culling), Schatten trotzdem da. Fix im Flieger-Rig: `rigging/double_sided.py` findet Flächen, hinter
  denen „draußen“ ist (Strahl nach hinten), und kopiert sie mit umgedrehter Richtung (Gewichte + UVs mit, 1 mm versetzt).
  Schalter `[double_sided]` in `flyer_defaults.toml` (an), pro Kreatur `[flyer.double_sided]`. Wespe: +124 Tris.
  Für andere Skelette mit dünnen Platten (Flossen, Segel, Hautlappen) einfach dort `double_sided.apply()` nach dem Gewichten aufrufen.
  Unity-Prüfbilder haben dafür jetzt auch `top` + `back`.

## Offen
- Flesh Titan (#7) – macht der Nutzer zusammen mit Claude (humanoide Teilstruktur erlaubt).
- **Unity-Test**: Viewer-Projekt `Unity_Creature_Test/` (siehe dortige README) – Import automatisch, 9 Kreaturen/81 Clips headless geprüft (Texturen, Boden, Bewegung). Sichtprüfung durch den Nutzer läuft. Bodenkontakt im Walk gemessen (alle ≈ 0; Wespe sinkt bis 3,7 cm ein, Raptor 1,9 cm – offen).
- Echse: Ready/Attack zu dezent. Wolf-Tod: Beine lassen sofort los (`ik_release_start` nutzen). Hirsch: Tripo-UV sehr zerstückelt.
- **Nutzer-Feedback Unity (2026-11-17):** Death-Clips fast überall unbrauchbar (zu klein) – **Claude macht vorerst keine Death-Animationen (Nutzer-Anweisung)**. Void Manifestation: Tentakel nur an den Enden beweglich, müssen bis zur Wurzel wabbeln. Eel Stalker insgesamt schwach: Tripo-Modell hat feste Krümmung/Drehung, Animation addiert nur darauf; Walk: Kopf starr; Ready: nur Verschieben/Drehen; Turn = gedrehter Walk (slither mit bias); Kopf-Lappen unter dem Kiefer starr (sollen schwingen, Kamm/Hörner starr). → Standard-Baustein „frei hängende Teile“ geplant.
- Prio-2-Clips aus MOVESET.md (Attack2, Dodge, Knockdown …) gibt es noch für kein Muster.

## Neu: Architektur (2026-11-17, nach Nutzer-Feedback – siehe ../CLAUDE.md "Lehren aus Testlauf 1")
- **Eine Pipeline für alle Skelette**: `scripts/creature_pipeline.py` (crawler_pipeline.py leitet nur weiter).
  Stufen: `--stage motion` (Roh-GIFs → rig/anim/raw/, nichts bremst, kein Export) → Nutzer nimmt Bewegung ab →
  `--stage full` (GIFs → rig/anim/final/, Export, Fingerabdruck). `--stage check` = nur Fingerabdruck. `--work <ordner>` = Ausgabe woanders.
- **Freigabe/Sperre**: `python scripts/approve.py creatures/<name>` (nur nach OK des Nutzers) → `approved/`; Pipeline verweigert dann den Neubau (außer `--unlock`).
- **Regressionstest**: `python scripts/regression.py [--deep]` – prüft per Fingerabdruck (alle Knochen + Mesh-Stichprobe, jeder Frame), ob freigegebene Kreaturen gleich bleiben.
  Getestet: harmlose Änderung → "identisch"; Flügelschlag 38→30° → "VERÄNDERT" mit 65 mm pro Clip benannt.
- lizard/deer haben eigenen Clip-Code (Kopie von wolf, Beweis: alle 9 Kreaturen Frame für Frame identisch zum Stand vorher).
- Noch NICHTS freigegeben – die 9 Testlauf-Kreaturen gelten als Testergebnisse. Bisherige GIFs liegen jetzt in rig/anim/final/.
- Offen: Tests von `--stage motion/full` in temp/t_motion, temp/t_full prüfen; Wolf aus Commit 636de5e (temp/wolf_old, Fingerabdruck temp/wolf_old_fp.json)
  mit heutigem vergleichen; README-Abschnitt "Zusammenarbeit"; noch nicht committet. Danach: Wolf-Pilot (Dehnung am Mesh, weichere Bewegung).
