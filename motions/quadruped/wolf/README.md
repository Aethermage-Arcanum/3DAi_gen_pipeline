# Bewegungsmuster quadruped/wolf (Referenz-Vierbeiner)

Generator: `wolf_clips.py` (nutzt `../quadruped_kit.py`), Werte in `style.toml`. Erstes Modell: **Ravine Stalker** (2026-11-17).

## Clips
| Clip | Dauer | Inhalt | Naturvorbild |
|---|---|---|---|
| Quadruped_Wolf_Walk | 1,07 s | lateraler Viertakt HL → VL → HR → VR, Rumpf wippt 2× pro Zyklus, Kopf stabilisiert, Schwanz hängend | Hunde-/Wolfs-Schritt (Lateralsequenz) |
| Quadruped_Wolf_Run | 0,53 s | rotierender Galopp (HL, HR, VR, VL), Rücken beugt/streckt sich | Galopp der Caniden |
| Quadruped_Wolf_TurnLeft/Right | 0,93 s | auf der Stelle drehen, Füße setzen im Kreis um | – |
| Quadruped_Wolf_Idle | 3,0 s | atmen, umschauen, Schwanz pendelt | – |
| Quadruped_Wolf_Ready | 1,0 s | **Pirsch-Haltung**: geduckt, Kopf tief + vorn, Lefzen leicht hoch, leichtes Zittern | Anschleichen vor dem Sprung (nicht Dominanz-Drohen – das wäre Kopf hoch, Körper steif) |
| Quadruped_Wolf_Attack1 | 0,8 s | ducken → nach vorn schnellen, Hals streckt, Maul auf → zuschnappen (Event `hit` Frame 13) | Sprung-Biss |
| Quadruped_Wolf_Hit | 0,33 s | Ruck zurück, Kopf weg, Schwanz ein | – |
| Quadruped_Wolf_Death | 1,33 s | kippt auf die Seite, Beine erschlaffen (IK aus), liegt exakt am Boden | – |

Alle 9 Clips grün (Füße 0,0 mm am Boden, IK erreicht jedes Ziel, Schleifen nahtlos, Lücken max. 0,7 cm).

## Naturreferenzen
- **Gangarten Caniden** (Schritt = Lateralsequenz-Viertakt, Trab = Diagonalpaare, Galopp): Catavitello et al. 2015, *PLoS ONE* – [PMC4517757](https://pmc.ncbi.nlm.nih.gov/articles/PMC4517757) · Uni Minnesota „Canine Gaits“ mit Animationen: [vanat.ahc.umn.edu/mGaits](https://vanat.ahc.umn.edu/mGaits/)
- **Rotierender Galopp** (nur bei Raubtieren typisch): [vanat.ahc.umn.edu – Gallop](https://vanat.ahc.umn.edu/run/plate9.html)
- **Körpersprache**: Drohen = Kopf hoch, steif, Zähne gebleckt; geduckt + Kopf tief = Unterwerfung bzw. Pirsch. [Living with Wolves – Body Language](https://www.livingwithwolves.org/body-language-of-wolves/) · [UK Wolf Conservation Trust – Ethogramm (PDF)](https://www.ukwct.org.uk/files/JBEthogram.pdf)
- Videos zum Abgleich: Suchbegriffe „wolf trot slow motion“, „wolf gallop slow motion“, „Muybridge dog galloping“.

## Erkenntnisse
- **Tripo baut Vierbeiner mit fast gestreckten Beinen** (Ruhe 93–98 % der Beinlänge). Lösung im Baukasten: `reach_fix` senkt den Rumpf automatisch, wenn ein Bein sein Ziel nicht erreicht. Daher kürzere Schritte als beim echten Wolf (Schritt 18 %, Galopp 21 % der Körperlänge).
- **Schulterblätter** (`Shoulder_FL/FR`) gleiten über IK-Steifigkeit mit dem Vorderbein mit, sonst reißt die Schulter im Galopp.
- **Dehnung** wird pro Clip gemessen (`max_stretch`, inkl. Ort). Galopp darf 2,4: die Haut hinten am Oberschenkel zieht sich beim Vorschwingen sichtbar lang (Sichtprüfung ok).
