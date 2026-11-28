# Bewegungsmuster quadruped/gorilla (Gorilla)

Generator: `gorilla_clips.py` (eigener Code, nutzt `../quadruped_kit.py` nur lesend), Werte `style.toml`, Vorarbeit
`RESEARCH.md` (Bewegungsregeln, Naturreferenzen, Rig-Hürden). Erstes Modell: **Frost Colossus** (`creatures/13_frost_colossus/`,
2026-11-27). Andere Vierbeiner-Muster bleiben unverändert – der Gorilla hat keine Zeile in ihrem Code geändert.

## Entscheidungen des Nutzers (2026-11-23)
- **Der Schwanz bleibt** (Bilder + Modell haben einen langen Eis-Stachelschwanz) und schwingt schwer mit; beim Aufrichten
  hebt er sich gegen das Kippen, sonst rammt er in den Boden.
- **Brusttrommeln = eigener Clip `Taunt`** (in der Natur ein seltenes, starkes Signal); Ready bleibt Drohen mit Boden-Schlag.
- **Attack2 = Sturm-Hieb mit Root Motion** (Galopp aufs Ziel + seitlicher Schwinger).

## Clips (Präfix `Quadruped_Gorilla_`)
| Clip | Dauer | Inhalt |
|---|---|---|
| Walk | 1,4 s, Loop | **Knöchelgang in Diagonal-Sequenz** (Aufsetzen HL 0 · VR 0,1 · HR 0,5 · VL 0,6), Stand 70 %. Schultergürtel giert 13° und rollt 14° (Becken 5°/3°) → Schulterplatten und Eiszacken pendeln von oben deutlich; Rumpf schwankt 3 % L zur Standfaust; Brust steigt mitten im Stand der Arme (Stelze); Fäuste schwingen flach und **außen herum** nach vorn; Kopf tief und ruhig; schwerer Schwanz schwingt verzögert gegen das Becken |
| Run | 0,73 s, Loop | Sturm-Galopp (Füße HL 0 · HR 0,1, Fäuste VL 0,5 · VR 0,6), weit ausgreifende Arme, Buckel pumpt 8°, Rücken rund/gestreckt ±10°, Kopf tief vorgestreckt, Schwanz leicht gehoben |
| TurnLeft / TurnRight | 1,2 s, Loop | auf der Stelle (32°/Zyklus), Fäuste wandern außen um die Füße, Brust dreht voraus, **Kopf führt**, Becken + Schwanz schleppen nach. Richtung gemessen (siehe unten) |
| Idle | 4,0 s, Loop | schwer atmen, Gewicht verlagern, Kopf schaut rechts/links (Kopf führt), linke Faust hebt sich und setzt schwer auf |
| Ready | 2,0 s, Loop | Drohen: Gewicht zurück, Brust etwas hoch, Kopf schüttelt, Maul auf (Brüllen), Gewicht pendelt, rechte Faust hebt sich hoch und **schlägt auf den Boden** (Event `slam`) |
| Taunt | 2,67 s | **Brusttrommeln**: ducken → um die Hüfte ganz aufrichten (Brust ≈ 70°), Hüfte setzt sich zurück, Schwanz hebt sich gegen → **Arme weit seitlich** auf, Brüllen → 8 Schläge, Hände **abwechselnd vor die Brust** (Ellbogen außen), der andere Arm jeweils weit auf (von oben lesbar) → Arme weit auf, Kopf zurück → nach vorn auf die Fäuste (Event `slam`). Events `drum` je Schlag |
| Attack1 | 1,9 s | **Doppelfaust-Hammer**: ducken → hoch aufrichten (Brust 66°), **beide Fäuste über dem Kopf**, Brüllen (7 F halten) → Körper fällt nach vorn, Arme schwingen nach vorn-unten, beide Fäuste schlagen **vor dem Kopf** zur Mitte hin auf (Event `hit` F31) → Aufprall federt durch Schultern, Hals, Kopf, Schwanz peitscht nach |
| Attack2 | 1,67 s | **Sturm-Hieb, Root Motion 0,85 L**: ducken → 2 Galoppsprünge → rechter Arm holt außen-hinten aus (Schultergürtel dreht 24° weg) → Schulter führt, Rumpf verdreht sich zurück, Faust fegt **flach von außen nach innen-vorn vor die Nase auf Gegnerhöhe** (Event `hit` F30) → Abbremsen auf drei Gliedmaßen, Faust setzt auf. Event `root_motion` am Ende |
| Hit | 0,53 s | Ruck zurück, Schultern ziehen zusammen, Kopf duckt verzögert, Schwanz zuckt nach, Ende = Standhaltung |
| Death | 1,33 s | **Platzhalter** (Nutzerregel „Death-Clips nicht anfassen“): Kopie des Bär-Tods (zur Seite kippen) |

**Ganzkörper:** Kein Angriff bewegt nur einen Arm. Attack1: ganzer Körper kippt um die Hüfte, Rücken streckt sich, Arme über
Kopf, Fall nach vorn mit Ausfall 11 % L, Aufprall federt durch. Attack2: Root Motion, Schultergürtel verdreht sich ±24°,
Schulter rollt, Kopf schaut in den Hieb, Schwanz schwingt gegen. Messwerte in `clips_report.json` (`strike`-Werte unten).

**Arme über Kopf / vor der Brust:** Die Bein-IK hat kein Pol-Ziel – der Ellbogen würde umklappen. `arm_fk()` dreht den Arm in
Welt-Richtungen (Oberarm, Unterarm) und gibt der IK diese Pose als Ausgangspose plus die FK-Faust als Ziel; so bleibt der
Ellbogen außen und `reach_fix` sieht keinen überstreckten Arm. Der Baukasten bleibt unverändert.

## Naturreferenzen
Videos (zum Abgleich durch den Nutzer, der Build-Agent kann keine Videos ansehen; Details und Literatur in `RESEARCH.md` §3):
- Kampf/Sturm in Zeitlupe: [Carrier & Cunningham 2017, Movie 1](https://movie.biologists.com/video/10.1242/bio.022640/video-1)
- Brusttrommeln: [Silberrücken (My Modern Met)](https://mymodernmet.com/silverback-gorilla-beat-his-chest-wildlife-photographer/) ·
  [PetaPixel 2023](https://petapixel.com/2023/09/08/large-silverback-gorilla-beats-his-chest-right-in-front-of-photographer) ·
  [Max-Planck-Video (EurekAlert)](https://www.eurekalert.org/multimedia/915420)
- Boden schlagen: [A-Z Animals – Spiegelbild](https://a-z-animals.com/blog/gorilla-shows-his-strength-to-his-reflection/)
- Bluff-Sturm: [A-Z Animals – Zoo](https://a-z-animals.com/blog/watch-the-terrifying-moment-when-a-silverback-charges-children-at-the-zoo/)
- Suchbegriffe: „gorilla knuckle walking slow motion side view“, „silverback chest beat slow motion“, „silverback charge display“.

## Abgeleitete Werte (2026-11-27)
| Wert | Gorilla | Bär zum Vergleich | Herleitung |
|---|---|---|---|
| Walk Fußfolge | Diagonal: HL 0 · VR 0,1 · HR 0,5 · VL 0,6 | lateral HL 0 · VL 0,14 | Primaten gehen diagonal (Sellers & Hirasaki 2018) |
| Walk Stand / Takt | 70 % / 42 F (1,4 s) | 68 % / 40 F | Menschenaffen Duty 0,62–0,74; Gorilla-Zyklus 0,5–2,1 s |
| Schritt | 0,26 L | 0,24 L | über Natur (0,22) – Lesbarkeit aus der ARPG-Kamera |
| Schultern gieren/rollen | 13° / 14° | 6° / 7° | Haupt-Lesemerkmal von oben (Lehre Schildkröte/Sandwurm: Walk kaum lesbar) |
| seitlich schwanken | 3 % L | 1,4 % | breite Armstellung, Gewichtsverlagerung sichtbar |
| Fäuste außen herum | 5 % L | – | Arm schwingt im Bogen, von oben gut lesbar |
| Schulterblatt-IK-Steifigkeit | 0,65 | 0,45 | Rollen kommt aus dem Schultergürtel; weicher → Hals/Schulter-Übergang gedehnt |
| Run | 22 F, Stand 38 %, Schritt 0,30 L | 20 F, 36 % | Schritt → Galopp ohne Trab |
| Taunt | Brust 70°, 8 Schläge in 1 s | – | Brusttrommeln ganz aufgerichtet (Wright et al. 2021, Schaller 1963) |

## Drehrichtung (gemessen, nicht angenommen)
`turn_check()` (aus bear_clips kopiert): Standfüße wandern relativ zum Körper im Uhrzeigersinn ⇒ Körper dreht links.
Frost Colossus: TurnLeft +32°/Zyklus, mittleres Gieren Kopf +30,7° > Hals +19,8° > Brust +9° (Becken −9° = Körper biegt sich
in die Kurve) → `turn_dir_ok: true`; TurnRight genau gespiegelt (−32°).

## Statur
Alle Längen relativ (Körperlänge, Rumpfhöhe), Clips werden pro Rig gebacken – wie beim Bären (siehe `../bear/README.md`
„Statur ±20 %“): Varianten mit anderer Statur über den Baukasten neu backen oder nur uniform skalieren.

## Dehnung, Treffpunkte, Kennzahlen
Siehe `creatures/13_frost_colossus/README.md`.
