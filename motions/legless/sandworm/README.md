# Bewegungsmuster legless/sandworm

Gedrungene Ringel-Würmer, die kriechen, sich eingraben und aus dem Boden auftauchen. Erste Kreatur: **Sand Leviathan**
(`creatures/12_sand_leviathan/`). Recherche, Quellen und Naturvideos: `RESEARCH.md`. Werte: `style.toml`.
Clip-Code: `sandworm_clips.py` (eigener Code, Ideen aus `cobra` kopiert, nicht importiert).

```
python scripts/creature_pipeline.py creatures/12_sand_leviathan --stage motion   # Roh-GIFs
python scripts/creature_pipeline.py creatures/12_sand_leviathan                  # Endfassung + Export
```

## Entscheidungen des Nutzers (2026-11-23)
- **Fortbewegung = Wurm-Kriechen**, nicht Schlängeln: Verdickungswellen (Peristaltik) + leichtes Wiegen (±10°).
  Grund: Länge : Dicke ≈ 3–5 : 1, wie eine Kobra zu schlängeln würde den Rumpf zerquetschen; klarer Unterschied zu cobra.
- **Maul bleibt dauerhaft offen** und „pumpt“ nur (Kiefer öffnet sich weiter + Kopf nickt). Keine neuen Maul-Knochen.
- **Rundes Maul bleibt** (BACKLOG G3).
- **Burrow** (Eingraben) und **Emerge** (Auftauchen) gleich mitgebaut; **Attack2 = Body Slam**.

## Clips (`Legless_Sandworm_<Clip>`, 30 fps)
| Clip | Loop | Inhalt |
|---|---|---|
| Walk | ✓ | 2 Verdickungswellen Kopf → Schwanz (Ringe dick+kurz / dünn+lang, ±12 %), Buckelwelle ±5°, Wiegen ±10° (0,6 Wellen, Kopf führt 20°), Ruck-Gleiten ±2,2 % L |
| Run | ✓ | Sand-Pflügen: eine Welle ±20°, Kopf gesenkt, Breite ±8 % |
| TurnLeft / TurnRight | ✓ | flacher Bogen 50° über den ganzen Körper, Panzer +18°, Kopf +10° führen, Peristaltik läuft mit 70 % weiter |
| Idle | ✓ | Ringe atmen (±3 %), langsame Welle, Kopf hebt sich zweimal und wittert, Maul pumpt langsam |
| Ready | ✓ | vorderes Drittel bis 42° aufgerichtet (über 6 Wirbel verteilt), Maul nach vorn, Pendeln ±7°, schnelles Pumpen |
| Attack1 | – | Vorstoß-Biss: Stauchen (Ziehharmonika) → 5 Frames Strecken + Vorstoß → Raspeln (Kopf rollt ±13°, Rumpf ruckt 2×) → Ready; Event `hit` |
| Attack2 | – | Body Slam: Vorderkörper steil hoch (70°), halten, beschleunigt nach vorn auf den Boden, Ringe quetschen breit, Nachfedern → Ready; Event `hit` |
| Hit | – | Vorderkörper zuckt zurück, Stauchwelle läuft Kopf → Schwanz, → Ready |
| Burrow | – | Kopf neigt sich, bohrt am festen Eintrittspunkt 38° in den Boden, jeder Wirbel taucht genau dort ab, Schub-Peristaltik, Peitschenschlag der Schwanzspitze; Root Motion ≈ 0,9 L; Events `sand_burst`, `burrowed` |
| Emerge | – | Kopf bricht 62° steil aus dem Loch, vordere 45 % schießen hoch (Maul zum Himmel), Hochpunkt, kippt mit Gewicht nach vorn, Aufprall + Nachfedern, Rest zieht aus dem Loch, endet exakt in Ready Frame 0; Events `sand_burst`, `land`, `emerged` |
| Death | – | **Platzhalter** (liegt still). Death-Clips sind gesperrt (Nutzer 2026-11-17). |

Unity: Unter der Erde Renderer aus bzw. nur Sand-Effekt; Burrow/Emerge nutzen Root Motion (Root-Knochen).
Vortrieb Walk ≈ 0,18 L/Zyklus, Run ≈ 0,38 L/Zyklus (`move_speed_mps` im clips_report), Drehen ≈ 75 °/s.

## Rig (opt-in im Beinlos-Rig, `[legless]` der Kreatur)
- `joints`: Wirbel auf den Ringfurchen (Leviathan: 9 Ringe + 4 Panzer-Wirbel + Kopf ab 86 % der Länge).
- `axial_weights` + `axial_blend`: jeder Ring hängt starr an seinem Wirbel, gebogen wird nur in der Furche; zwischen den
  Panzerplatten breiter (Platten schieben sich übereinander).
- `rigid_spikes`: Stacheln übernehmen das Gewicht ihres Ansatzes (starr am Ring, verbiegen sich nicht, stechen beim
  Biegen nicht ineinander).
- `ground_ignore_spikes`: Bauchstacheln zählen nicht für den Bodenkontakt → **der Körper liegt auf**, die Stacheln
  stecken im Sand (statt dass der Wurm auf 2 Stacheln steht wie Stummelbeinen).
- `ring_bones`: Blatt-Knochen `Ring_NN` (Kind von `Spine_NN`) tragen die Haut und werden für die Peristaltik skaliert;
  die Wirbelkette rückt dabei nach (kein Spalt). Skalierung vererbt sich nicht (Unity „Generic“ sicher).

## Körperform
Grundlinie = **gerade Liege-Haltung des Modells** (Ruhe-Richtung der Wirbel). Das Tripo-Modell liegt gerade
(Mittellinie 0,004 × L versetzt); die Mittellinie steigt nur zum dicken Vorderkörper an (Bauch flach). Eine waagerechte
Mittellinie würde den Bauch in den Boden drücken und jedes Gelenk knicken. Gieren/Neigen/Kopf sind Abweichungen davon;
eine feste Krümmung wie beim Eel Stalker gibt es hier nicht.

## Prüfung
Kontaktbögen der Roh-GIFs (`python scripts/gif_sheet.py <gif> --n 8 --cols 4`), Dehnung auf sichtbaren Flächen
(`rigging/joint_densify_review.py … visible`), Messwerte im `clips_report.json`: `turn_dir_ok` (Vorzeichen Drehen),
`hit_in_front_ok` (Treffer vor dem Körper, nah am Boden), `entry_ok` (Burrow/Emerge: unter dem Boden nur auf der
Lochseite), `ends_in_ready_ok` (Emerge).
