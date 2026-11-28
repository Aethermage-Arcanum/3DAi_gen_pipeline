# Frost Colossus (13) – Muster `quadruped/gorilla`

Riesige, gorillaartige Eisbestie auf den Fäusten, massive Arme mit Eis-Armschienen, Schulterplatten, Rückenkamm aus Eiszacken,
langer Stachelschwanz. Bewegung: `motions/quadruped/gorilla/` (README, style.toml, RESEARCH.md mit Naturreferenzen).
Stand 2026-11-28: gebaut (`--stage full` ✓ ALLES OK), **nicht freigegeben, nicht committet** – wartet auf Abnahme der Bewegung.

## Kennzahlen (Export `output/FrostColossus.fbx/.glb`)
| Tris | Vertices | Materialien / Draw Calls | Texturen | Knochen | Einflüsse | Maße |
|---|---|---|---|---|---|---|
| 4.669 | 7.717 (Facetten aufgetrennt) | 1 / 1 | Color + Normal 1024² (FBX), ORM nur in GLB | 30 | max. 4 | 1,0 × 0,8 × 0,77 (normiert) |

Clips (11): Walk, Run, Idle, Ready, **Taunt**, TurnLeft, TurnRight, Attack1, Attack2 (Root Motion 0,85 m), Hit, Death (Platzhalter).
Events: `footstep`, `slam`, `drum`, `hit`, `root_motion` (`output/FrostColossus_events.json`).

## Prüfung Teil B (Tripo-Modell) – bestanden
`review/model_check.png` + Sichtprüfung (`temp/go_inspect/views.png`): 1 Teil, 1 Material, symmetrisch, 4 Fußgruppen, Arme frei vom
Rumpf, Schwanz gerade, keine Hautbrücken, keine einseitigen Flächen. Fäuste sind Klötze ohne Finger, Ellbogen unter der
Armschiene versteckt (aus der Spielkamera egal). Fußbreite hinten/vorn 0,56× ist gewollt (Gorilla), nichts geändert.

## UV
Tripo-UV behalten (Fehlerwert 2,71 gegen Smart UV 3,66; 1.569 Inseln = eine je Facette, Abdeckung 45 %, Überlappung 0 %),
`uv/uv_preview.png`.

## Rig (`creature.toml [quadruped.*]`)
- `spine_top_pct 78`, `spine_slice 0.06`: Eiszacken heben die Wirbelsäule nicht mehr an.
- `mid_half_width 0.06`: die dicken Oberschenkel lagen im Bauch-Streifen → Bauch über den Hinterbeinen bei 0,18 statt 0,32 m.
- Neue opt-in-Regeln in `rigging/quadruped_rig.py` (ohne die Zeilen wie bisher; Regression `--deep` Wolf, Reef Snapper,
  Hirsch, Bär, Shellback identisch): `leg_joints_fixed` + `front_elbow/front_wrist/back_knee/back_hock` (Ellbogen 0,37 m,
  Handgelenk 0,09 m, Knie 0,23 m – die Biegungs-Suche griff die Kante der Armschiene, links 0,21 / rechts 0,37 m),
  `leg_mirror` (Gelenke links/rechts gemittelt), `joint_track_mean 0.5` (Hüfte über dem Bein statt im Schritt),
  `knee_forward 0.05` (Säulen-Hinterbeine knicken sicher nach vorn), `joint_inset 0.7` (Arm dreht unter der Schulterplatte).
- Schulterblatt-IK-Steifigkeit 0,65 (style.toml): bei 0,4 war der Hals/Schulter-Übergang stärker gedehnt.
- **Eisplatten starr – getestet, nicht übernommen:** Platten per Textur-Helligkeit erkannt (14 Platten, 2.051 Vertices), Variante
  A gemeinsames Mittel-Gewicht, Variante B 100 % Mehrheits-Knochen + Abstands-Übergang. Beide machten die sichtbare Dehnung
  schlechter (Walk Rücken 1,25 → 1,83, Hals 2,27 → 3,33; A: Unterbein bis 9). Die Platten hängen ohnehin überwiegend an einem
  Knochen (Armschiene 93 % Unterarm) → Code wieder entfernt.
- Gelenk-Lücken: `[gaps] pair_eps 0.001` mit Begründung in der creature.toml (Mesh an jeder Facette aufgetrennt; echte Risse
  nur zwischen deckungsgleichen Vertices – 0,0 cm in allen Clips).

## Messwerte
- Fußkontakt Walk 0,0 mm, Schritt 0,25 m, 0,26 m/s; alle Clips `ok` (IK-Fehler ≤ 0,4 mm).
- Drehrichtung: TurnLeft +32°/Zyklus, Kopf +30,7° > Hals +19,7° > Brust +9° > Becken −9° → ok; TurnRight gespiegelt.
- Attack1 (F31): beide Fäuste 7 cm **vor der Nasenspitze**, 32 cm vor der Ruhe-Faust, am Boden, je 16,5 cm neben der Mitte;
  Brust oben 66°, Schwanz ≥ 13,6 cm über dem Boden.
- Attack2 (F30): Faust 18 cm **vor der Nasenspitze**, 45 cm hoch (Schulter 54 cm), genau auf der Körpermitte; Root Motion 0,85 m.
- Taunt: Brust 70°, Schwanz ≥ 13,5 cm über dem Boden.
- Dehnung auf den aus der ARPG-Kamera sichtbaren Flächen (`review/dehnung_sichtbar.json`, Maximum je Bereich):

| Clip | Rücken | Flanke | Hals | Kopf | Schwanz | Schulter/Oberschenkel | Unterbein |
|---|---|---|---|---|---|---|---|
| Walk | 1,29 | 1,79 | 2,01 | 1,07 | 1,49 | 2,15 | 1,37 |
| Run | 1,31 | 1,76 | 2,20 | 1,07 | 1,45 | 2,16 | 1,50 |
| TurnLeft | 1,42 | 1,97 | 2,09 | 1,17 | 1,34 | 2,19 | 1,39 |
| Taunt | 1,21 | 1,34 | 1,85 | 2,10 | 1,23 | 2,19 | 1,80 |
| Attack1 | 1,41 | 1,62 | 1,87 | 2,17 | 1,22 | 2,22 | 1,67 |
| Attack2 | 1,36 | 1,57 | **3,43** | 2,03 | 1,62 | 2,26 | 2,52 |

  Rest: Übergang Schulterplatte ↔ Hals (Gewichte Shoulder_FR/Neck_1/Chest gemischt) beim Ausholen in Attack2 (F24); Kopf ≈ 2,1
  am Kiefer (Maul weit auf).

## Prüfbilder
`rig/anim/final/*.gif` (ARPG + Seite), Kontaktbögen `rig/anim/final/<Clip>_bogen.png` (Walk, Run, TurnLeft, Taunt, Attack1,
Attack2), dazu `Attack2_bogen_mitgefuehrt.png` (Kamera folgt der Root Motion – im festen GIF läuft der Koloss aus dem Bild).

## Naturreferenzen
Siehe `motions/quadruped/gorilla/README.md` und `RESEARCH.md` §3 (Knöchelgang, Brusttrommeln, Boden-Schlag, Bluff-Sturm).
