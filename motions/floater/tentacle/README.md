# Bewegungsmuster floater/tentacle

Generator `tentacle_clips.py`, Werte `style.toml`. Erstes Modell: **Void Manifestation** (2026-11-17), alle 9 Clips grün.

| Clip | Inhalt |
|---|---|
| Floater_Tentacle_Walk / Run | Kern wippt + schiebt (Schub nach dem Hub) und neigt sich nach vorn, Tentakel wellen ab der Wurzel, schleppen nach und schwingen bei jedem Hub nach |
| Floater_Tentacle_TurnLeft/Right | neigt sich in die Kurve, Tentakel bleiben außen in der Kurve zurück |
| Floater_Tentacle_Idle | Quallen-Pulsieren: Tentakel ziehen sich verzögert nach dem Hub zusammen, Wellen laufen ständig von der Wurzel zur Spitze |
| Floater_Tentacle_Ready | Tentakel weit gespreizt, Kern hebt sich, zittert; Tentakel züngeln schneller (2 Wellen pro Loop) |
| Floater_Tentacle_Attack1 | ausholen (Tentakel nach hinten) → nach vorn peitschen (Event `hit` Frame 14), Peitschenwelle läuft durch, klingt in 5 Frames aus |
| Floater_Tentacle_Hit | Rückstoß, Tentakel schlagen wild und schwingen nach, exakt zurück zur Ruhe |
| Floater_Tentacle_Death | Tentakel erschlaffen, Kern kippt und sinkt zu Boden (**unverändert**, benutzt weiter `tentacles()`) |

## Tentakel bis zur Wurzel wabbelig (2026-11-17)
Nutzer: *„Tentakel sind bis an die Wurzel wabbelig!“* – vorher bewegten sich nur die unteren Enden.

**Ursache (vor allem Rig, dann Bewegung):**
1. Rig: Die Kernkugel (Radius 0,31 m bei 1 m Größe, absichtlich groß, damit die Tentakel sauber getrennt werden)
   schnitt die oberen ~30–60 % jedes Tentakels ab – alles innerhalb war **zu 100 % an `Core` gewichtet** (Messung:
   Bewegung relativ zum Kern im Abstand < 0,30 m = 0,0 cm in jedem Clip). Einige kurze hängende Tentakel ragten kaum
   aus der Kugel und waren ganz starr.
2. Bewegung: Ausschlag pro Knochen wuchs linear zur Spitze (Wurzel-Knochen 1/n des Spitzen-Ausschlags), kein Nachschwingen.

**Lösung:**
- Rig (`rigging/floater_rig.py`, `[root_*]`, `ring_fade`, `seed_min_verts` in `floater_defaults.toml`): Jedes Tentakel-Stück
  wächst über Mesh-Kanten nach innen bis zur echten Wurzel (fallender Abstand zur Mitte, in einer Röhre um die nach innen
  verlängerte Tentakel-Achse). Kurze Stücke wachsen mit und zählen erst danach. Ein weicher Saum (2 Kanten-Ringe, 50 %/20 %)
  und gemittelte Nähte, wo zwei Tentakel verwachsen sind, verhindern Risse. Void Manifestation: 21 statt 19 Ketten, 74 statt 46 Knochen.
- Bewegung (`floater_kit.py`: `wobble()` + `drive()`, Werte `[wobble]` in `style.toml`):
  1. **Freie Welle** über die ganze Kette, läuft von der Wurzel zur Spitze; die Wurzel biegt sich mit 55 % der Spitze;
     zweite Biegeachse mit eigener Phase (jeder 2. Tentakel doppelte Frequenz) → Ellipsen/Achten statt Pendeln;
     Phase pro Tentakel nach goldenem Schnitt verteilt → nie synchron.
  2. **Nachschwingen**: jeder Ansatz ist eine gedämpfte Feder, angeregt von der Beschleunigung des Kerns genau dort
     (Wippen, Schub, Drehen, Ausholen/Vorschnellen, Rückstoß); 2 Frames Verzug pro Knochen → Peitschenwelle.
     Längere Tentakel schwingen langsamer (Periode ∝ √Länge). Loops sind exakt periodisch (FFT-Lösung), Attack/Hit klingen aus.

| Messung (Bewegung relativ zum Kern, Mittel cm) | Abstand 0,25 | 0,30 | 0,35 | 0,40 |
|---|---|---|---|---|
| Walk vorher → nachher | 0,0 → 2,1 | 1,1 → 5,3 | 2,6 → 7,3 | 4,9 → 10,6 |
| Attack1 vorher → nachher | 0,0 → 4,4 | 1,3 → 10,4 | 4,1 → 14,1 | 7,9 → 20,4 |

Vorher/Nachher-Bild: `temp/review/tentacle.png` (Idle + Walk, Seite, mit Zwiebelhaut = Bewegungsumfang).

## Naturreferenzen
- **Qualle**: Pulsation mit Arbeitsanteil ~0,4–0,5 des Zyklus; Drehen durch ungleichzeitiges Zusammenziehen der Schirmseiten – TU Delft (Sarsia-Modell): [PDF](https://repository.tudelft.nl/file/File_d3de7605-d494-4ba5-9fad-9367ed692da8) · Saugschub statt Drücken: [MBL](https://new-www.mbl.edu/news/push-or-pull-how-many-limbed-marine-organisms-swim)
  Tentakel treiben passiv hinter dem Schirm her und schwingen nach jedem Puls aus: Video Pazifische Seenessel
  [Getty 605470453](https://www.gettyimages.no/detail/video/sea-nettle-jellyfish-trails-tentacles-in-dark-stock-video-footage/605470453) ·
  [Uppbeat „golden pacific sea nettles drifting“](https://uppbeat.io/stock-video/asset/golden-pacific-sea-nettles-drifting-116359) ·
  Warum sie schleppen (Schirm schwimmt, Tentakel nicht): [EarthSky](https://earthsky.org/biodiversity/how-do-jellyfish-swim)
  → `drive()` (passives Nachschleppen/-schwingen), `pulse_lag` (Zusammenziehen folgt dem Hub), `damping` 0,3 (2–3 Nachschwinger).
- **Oktopus-Arm**: Ausstrecken als Biegewelle vom Ansatz zur Spitze (Gutfreund et al. 1996 *J Neurosci*; Yekutieli et al. 2005)
  – Zusammenfassung [PMC6793066](https://pmc.ncbi.nlm.nih.gov/articles/PMC6793066), Peitschen-Vergleich [arXiv 2510.25520](https://arxiv.org/html/2510.25520v2)
  → `phase_step` (Welle läuft Wurzel → Spitze), `lag_frames` (Peitsche beim Schlag).
  Arm-Verformungen im Video (Kennedy et al. 2020, *Sci Rep*): [EurekAlert-Video](https://www.eurekalert.org/multimedia/855959),
  Studie [PMC7704652](https://pmc.ncbi.nlm.nih.gov/articles/PMC7704652): Biegen = 67 % aller Verformungen, im distalen Drittel
  78 %, im proximalen Drittel immer noch 41 % → **die Wurzel biegt sich auch, nur weniger** → `root_weight` 0,55.
  Wildes Oktopus-Arm-Video: [EurekAlert 1091123](https://www.eurekalert.org/multimedia/1091123).
- **Oktopus schwimmend**: Arme schleppen beim Kopf-voran-/Düsenschwimmen hinterher, beim Armschlag peitschen die
  eingerollten Spitzen am Ende gerade – [Scientific American](https://www.scientificamerican.com/blog/octopus-chronicles/new-views-into-the-octopuse28099s-bizarre-moves/)
  → `trail_deg` (Walk/Run), Attack: Ausholen → Peitschen.
- **Seeanemone in Strömung**: Tentakel schwingen weich, jeder etwas anders, Bewegung bis zum Fuß –
  [Uppbeat „swaying green sea anemone tentacles“](https://uppbeat.io/stock-video/asset/swaying-green-sea-anemone-tentacles-36937) ·
  [USF ETC Clip](https://etc.usf.edu/clipvideo/2993-wavering-bulbed-tentacles-of-a-sea-anemone)
  → `swirl` (zweite Achse), Phasen je Tentakel verschieden.

## Noch schwach
- Dehnung an verwachsenen Wurzeln (Tent_14/15) und an den kurzen Haken oben bis ~2,5 im Attack (Info, keine Sperre).
- Der Kern selbst (Mantel) bleibt starr; ein „Atmen“ des Mantels gibt es noch nicht.
