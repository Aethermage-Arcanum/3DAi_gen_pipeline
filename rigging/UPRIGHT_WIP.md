# upright / treant – Zwischenstand (WIP, nicht freigegeben) – 2026-11-18

**Fertig + getestet (direkt per Blender, noch NICHT über creature_pipeline.py):**
- `rigging/upright_detect.py` (Schnitt-Erkennung: Beine/Schritt, Arme/Achsel, Rumpf-Mitte, Krone) – Bog Warden: Schritt 0,29 H, Achsel 0,49 H, Krone 0,69 H.
- `rigging/upright_rig.py` + `upright_defaults.toml`: 27 Knochen, Gelenke an der Geometrie, Masken je Körperteil, Krone starr (Crown), lose Teile starr an Ansatz. Platzhalter beim Treant: Neck, Head.
- `rigging/upright_review.py`: Prüfbilder (`rig` = Overlay + Gewichte; `strip` = Einzelbilder eines Clips).
- `motions/upright/upright_kit.py` (Bein-IK am Knöchel, Hand-IK für Slam, posture() absolut, bake + Prüfungen inkl. Drehrichtung) und `motions/upright/treant/{treant_clips.py, style.toml}`: alle 10 Clips laufen; Walk/Run/Turn: Fußkontakt + Schleife ok, TurnLeft dreht links, Oberkörper führt.

**Update (später am 18.11.):** Kronen-Übergang geglättet (Attack2-Dehnung 6,6 → 2,9), Crown-Knochen senkrecht, Moos doppelseitig + [dangling], creature.toml ergänzt, verify_export.py + model_check.toml um `upright` erweitert (GEMEINSAM, Regression offen). `--stage motion` lief durch (rig/anim/raw/*.gif), `--stage full` läuft. READMEs: Muster + Kreatur + rigging/README geschrieben.

**Stand 2026-11-20:** Regression `--deep`: keine freigegebenen Kreaturen (nichts zu vergleichen); verify_export-Eintrag greift nur bei Knochen `Thigh_L` (kein anderes Rig hat ihn). Prüfbilder in `temp/review/upright_*.png`, READMEs fertig. Nicht committet (Commit war blockiert).

**Offene Punkte:**
- BACKLOG C13 (Nutzer): Moos an den Ästen komplett steif → Markierung zu knapp (nur Spitzen, Regel `below` an der Crown-Achse) + GIFs zeigen Shader-Schwingen nie.
- render_anim.py: feste ortho_scale → erhobene Hände im ARPG-GIF knapp am Rand.
- Lückenprüfung ohne Aussage (keine Berühr-Paare). Death nur Platzhalter.
- Attack2 Ausholen könnte weiter nach hinten gehen; Bewegung vom Nutzer noch nicht abgenommen.
