# Bewegungsmuster quadruped/wolf (Referenz-Vierbeiner)

Generator: `wolf_clips.py` (nutzt `../quadruped_kit.py`), Werte in `style.toml`. Erstes Modell: **Ravine Stalker** (2026-11-17).

## Clips
| Clip | Dauer | Inhalt | Naturvorbild |
|---|---|---|---|
| Quadruped_Wolf_Walk | 1,07 s | lateraler Viertakt HL → VL → HR → VR; Becken und Schultergürtel gieren/rollen getrennt im Takt ihrer Beine, Kopf stabilisiert + nickt, Schwanz pendelt verzögert nach | Hunde-/Wolfs-Schritt (Lateralsequenz) |
| Quadruped_Wolf_Run | 0,53 s | **rotierender Galopp** HL → HR → VR → VL mit zwei Schwebephasen: gestreckt (Vorderbeine greifen weit vor, Hinterbeine weit zurück) und gesammelt (Beine unter dem Bauch, Lende rund); Rumpf schaukelt | Galopp der Caniden |
| Quadruped_Wolf_TurnLeft/Right | 0,93 s | auf der Stelle drehen, Körper biegt sich in die Kurve, Kopf führt, Schwanz folgt dem Bogen | – |
| Quadruped_Wolf_Idle | 3,0 s | atmen, Gewicht links/rechts verlagern, umschauen (Kopf führt, Hals folgt), Schwanz pendelt nach | – |
| Quadruped_Wolf_Ready | 1,6 s | **Pirsch**: geduckt, Kopf tief + vorn, wiegt langsam vor/zurück, Kopf fixiert das Ziel, Lefzen zucken, steifer Schwanz mit zuckender Spitze | Anschleichen vor dem Sprung |
| Quadruped_Wolf_Attack1 | 1,07 s | ducken/zurückladen → vorschnellen, Hals streckt, Maul auf → zuschnappen (Event `hit` Frame 14) → festbeißen, zerren, Kopf schütteln (≈ 5 Hz) → zurückfedern | Sprung-Biss |
| Quadruped_Wolf_Hit | 0,5 s | Stoß zurück (2 Frames), Kopf schlägt verzögert zur Seite, gedämpftes Nachfedern | – |
| Quadruped_Wolf_Death | 1,33 s | (unverändert, siehe Nutzer-Anweisung „Death nicht anfassen“) | – |

## Naturreferenzen
- **Gangarten Caniden** (Schritt = Lateralsequenz-Viertakt, Trab = Diagonalpaare, Galopp): Catavitello et al. 2015, *PLoS ONE* – [PMC4517757](https://pmc.ncbi.nlm.nih.gov/articles/PMC4517757) · Uni Minnesota „Canine Gaits“ mit Animationen (normal/langsam/Einzelschritte): [vanat.ahc.umn.edu/gaits](https://vanat.ahc.umn.edu/gaits/)
- **Rotierender Galopp** (Vierschlag, zwei Schwebephasen, Rücken beugt/streckt sich): [vanat.ahc.umn.edu/gaits/rotGallop.html](https://vanat.ahc.umn.edu/gaits/rotGallop.html) · Biancardi & Minetti 2012, *Biomechanical determinants of transverse and rotary gallop in cursorial mammals* (J Exp Biol)
- **Kopf-/Rumpfbewegung beim Gehen**: Loscher et al. 2016 (19 Arten inkl. Hund, Mähnenwolf): Kopf nickt 2× pro Schritt, bei Caniden unter 1,3 Hz im Takt des Widerrists – [PMC5136594](https://pmc.ncbi.nlm.nih.gov/articles/PMC5136594) · Katze gehend: Kopf ≈ 1,5 cm Hub, ≈ 3° Nicken, 1,5–3° Rollen; Affe vierbeinig: Rumpf ≤ 10° Nicken/Rollen ([J Exp Biol 211:3889](https://cob.silverchair.com/jeb/article-split/211/24/3889/18018/Stabilization-and-mobility-of-the-head-neck-and))
- **Körpersprache**: [Living with Wolves – Body Language](https://www.livingwithwolves.org/body-language-of-wolves/) · [UK Wolf Conservation Trust – Ethogramm (PDF)](https://www.ukwct.org.uk/files/JBEthogram.pdf)
- Videos zum Abgleich (frei zugängliche YouTube-Videos fand die Websuche nicht zuverlässig; Stock-Clips mit Vorschau): [Wolf trabt (Kurator)](https://kurator.com/video/detail/685384) · [Wolf geht, Zeitlupe (Storyblocks)](https://www.storyblocks.com/video/stock/canadian-wildlife-wolf-walking-between-trees-slow-motion-1-348501618) · Suchbegriffe „wolf gallop slow motion“, „Muybridge dog galloping“.

## Abgeleitete Werte (2026-11-17, Umbau „weich statt Roboter“)
| Wert | vorher | jetzt | Herleitung |
|---|---|---|---|
| Fußbahn | Schwung startet aus Geschwindigkeit 0, Hub `sin` (max. Vertikaltempo beim Abheben) | `foot_profile = "smooth"`: Schwung übernimmt 70 % (Galopp 60 %) der Standgeschwindigkeit, Hub/Zehen mit `bump` (Tempo 0 an beiden Enden), höchster Punkt bei 40 % | Pfote rollt ab und wird angezogen, setzt weich auf |
| Rumpfhöhe | `reach_fix` pro Frame = Knick an jedem Fußwechsel (Hauptursache „kantig“) | `reach_smooth` (glatte Kurve), nur **Standbeine** zählen, `reach_flat` (Galopp 0,75) | Ein Bein in der Luft muss den Boden nicht erreichen |
| Walk: Gieren Becken/Schulter | – (nur Rollen 2° des ganzen Körpers) | 5° / 3,5° im Takt des schwingenden Hinter-/Vorderbeins | aus der ARPG-Kamera ist Gieren am besten sichtbar |
| Walk: Rollen | 2° ganzer Körper | Becken 3,5°, Schulter 2,5° getrennt | Katze 1,5–3°, Affe ≤ 10° |
| Walk: Heben/Senken | 1,2 % Rumpfhöhe, Körper als Block | 2 %, Hüfte und Schulter ¼ Zyklus versetzt (Rumpf wiegt) | umgekehrtes Pendel, Widerrist 2× pro Schritt |
| Walk: Schritt | 0,18 (wegen Reichweite verkleinert) | 0,22 | Bewegung nicht wegen Dehnung/Reichweite kürzen |
| Run: Fußfolge | HL 0 · HR 0,1 · VR 0,45 · VL 0,55, Stand 36 % → keine gestreckte Schwebe | HL 0 · HR 0,1 · VR 0,5 · VL 0,6, Stand 30 % → Schwebe gestreckt (0,4–0,5) + gesammelt (0,9–1,0) | vanat: „four-beat, double suspension“ |
| Run: Rückenbeugung | 5° auf alle Wirbel | 13° (26° Spanne), v. a. Lende; rund beim Aufsetzen hinten | Lendenbeugung verlängert den Schritt (vanat) |
| Run: Schaukeln | 3° | 6°, Brust hoch beim Abdruck hinten | – |
| Run: Auf/Ab | 3 %, **am höchsten mitten im Stand** (= Hüpfen/„Hoppeln“) | 3,5 %, am tiefsten mitten im Stand, höchster Punkt in der Schwebe | Feder-Masse-Modell beim Rennen |
| Run: Ausgreifen | Schritt 0,21 nur am Boden | Stand 0,24 + in der Luft vorn 0,10 / hinten 0,09 weiter | weite Galoppsprünge, Beine gestreckt |
| Kopf/Hals | phasengleich mit dem Rumpf | `follow`: jedes Halsglied 5 % Zyklus später, Kopf macht nur ~55 % mit | Kopfstabilisierung (Katze, Pferd) |
| Schwanz | eigene Sinuswelle, unabhängig vom Körper | `follow`: zieht Becken-Gieren/-Heben verzögert nach (7 % pro Glied), peitscht auf (×1,35/Glied) | Follow-Through |
| Ready | statisch + Zittern 6 Hz (wirkte mechanisch) | langsames Wiegen, fixierender Kopf, Lefzen, Schwanzspitze | Pirsch |
| Attack1 | 24 Frames, Kurven mit Halt an jedem Abschnitt | 32 Frames, weiche Schlüsselkurven (`keys`) mit Ausholen, Überschwingen, Zerren + Schütteln | Sprung-Biss |
| TurnLeft | drehte in Wirklichkeit nach **rechts** (Vorzeichen in `gait`) | dreht nach links | Fußbahn geprüft |

Dehnung (`max_stretch`) ist nur Info und hat keinen Wert mehr verkleinert.

## Erkenntnisse
- **Tripo baut Vierbeiner mit fast gestreckten Beinen** (Ruhe 93–98 % der Beinlänge). Jede Fußverschiebung zwingt den Rumpf tiefer. Früher geschah das pro Frame mit Knick (Maximum über 4 Beine) – das war die Hauptursache für „abrupt“. Jetzt glatt und nur für Standbeine.
- **Hoppeln im Galopp** kam von drei Dingen: Rumpf am höchsten mitten im Stand (falsche Phase), Absenkung an jedem Fußwechsel (Rumpf fiel in der Schwebe nach unten) und starrer Rücken (5°).
- **Bodenkontakt** (Unity-Messung: Ready/Attack1 bis −1,4 cm, Walk −1,1 cm unter dem Boden): Ursache war die Sohle hinter dem Ballen – sie hängt am Mittelfuß-Knochen und kippt beim Ducken/Ausgreifen in den Boden. Jetzt hebt `feet_on_ground` (Kit) pro Frame genau dieses Fuß-Ziel an, bis der tiefste Unterbein-Vertex auf Bindepose-Bodenhöhe liegt (Fuß rollt auf die Sohle; Kennzahl `sole_lift_max_m`). Ergebnis: alle Clips außer Death ≤ 2 mm. Death ist unverändert (−0,8 cm, Nutzer-Anweisung).
- **Schulterblätter** (`Shoulder_FL/FR`) gleiten über IK-Steifigkeit mit dem Vorderbein mit.
