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
  verlängerte Tentakel-Achse). Kurze Stücke wachsen mit und zählen erst danach. Ein weicher Saum (2 Kanten-Ringe Kern-Mesh gehen zu 50 %/20 % mit)
  und gemittelte Nähte, wo zwei Tentakel verwachsen sind, verhindern Risse. Void Manifestation: 21 statt 19 Ketten, 74 statt 46 Knochen.
- Bewegung (`floater_kit.py`: `wobble()` + `drive()`, Werte `[wobble]` in `style.toml`):
  1. **Freie Welle** über die ganze Kette, läuft von der Wurzel zur Spitze; die Wurzel biegt sich mit 75 % der Spitze;
     zweite Biegeachse mit eigener Phase (jeder 2. Tentakel doppelte Frequenz) → Ellipsen/Achten statt Pendeln;
     Phase pro Tentakel nach goldenem Schnitt verteilt → nie synchron.
  2. **Nachschwingen**: jeder Ansatz ist eine gedämpfte Feder, angeregt von der Beschleunigung des Kerns genau dort
     (Wippen, Schub, Drehen, Ausholen/Vorschnellen, Rückstoß); 2 Frames Verzug pro Knochen → Peitschenwelle.
     Längere Tentakel schwingen langsamer (Periode ∝ √Länge). Loops sind exakt periodisch (FFT-Lösung), Attack/Hit klingen aus.

Messung (Bewegung relativ zum Kern, Spannweite über den Clip, Mittel in cm; Modell 1 m). Tentakel-Drittel nach der neuen
Erkennung (21 Tentakel, gleiche Vertices vorher/nachher; Werkzeug `temp/agent_tentacle/tools/diag_thirds.py`):

| Clip | oberes Drittel (Wurzel) | mittleres | unteres (Spitze) | Tentakel mit starrem oberem Drittel (< 1 cm) |
|---|---|---|---|---|
| Walk vorher → nachher | 0,1 → 2,3 | 1,7 → 7,2 | 6,3 → 13,5 | 21 → 0 |
| Idle | 0,1 → 2,2 | 1,9 → 7,1 | 6,9 → 14,3 | 21 → 0 |
| Run | 0,1 → 2,9 | 2,1 → 8,9 | 8,0 → 16,7 | 21 → 0 |
| Ready | 0,0 → 1,6 | 0,7 → 4,8 | 2,9 → 8,9 | 21 → 1 |
| Attack1 | 0,1 → 4,2 | 3,0 → 12,8 | 10,6 → 24,7 | 21 → 0 |
| Hit | 0,0 → 2,1 | 1,0 → 5,8 | 4,1 → 10,7 | 21 → 1 |

Das obere Drittel beginnt jetzt an der echten Wurzel im Körper – die ersten Zentimeter stecken im Mantel und bewegen
sich bewusst weniger (weicher Übergang statt Riss).

Vorher/Nachher-Bilder: `temp/review/tentacle.png` (Idle + Walk, Seite, mit Zwiebelhaut = Bewegungsumfang), `temp/review/tentacle_weights.png` (Gewichte rot = starr). Prüfwerkzeuge: `temp/agent_tentacle/tools/` (render_weights, diag_thirds, stretch_view).

## Learnings für jede künftige Tentakel-Kreatur (gelten unabhängig vom Modell)
1. **Erst das Gewicht prüfen, dann die Bewegung.** „Steife Tentakel“ war kein Animationsproblem, sondern ein Rig-Problem:
   Vertices, die zu 100 % am Kern hängen, kann keine Animation bewegen. Prüfbild: Gewichte einfärben
   (`temp/agent_tentacle/tools/render_weights.py <rigged.blend> <prefix> [core|label]`, rot = starr am Kern), Messung pro Tentakel-Drittel
   (`diag_thirds.py`). Ziel: kein Tentakel mit starrem oberem Drittel.
2. **Erkennen und Gewichten trennen.** Eine große Kernkugel ist gut zum *Trennen* der Tentakel (sonst verkleben sie über
   Ringe/Kragen), aber schlecht als *Wurzel*. Darum: Stücke außen erkennen, dann nach innen bis zur echten Wurzel wachsen lassen
   (`root_depth` ≈ 0,6 des Kernradius; Röhre `root_radius` ≈ 2× Tentakel-Radius um die verlängerte Tentakel-Achse;
   `root_bend_to_core` 0,3, weil hängende Tentakel nicht radial aus dem Kern kommen). Auch winzige Stücke als Keim
   zulassen (`seed_min_verts` 3) und erst nach dem Wachsen filtern – kurze Tentakel, die kaum aus der Kugel ragen, sind sonst ganz starr.
3. **Weiche Grenzen statt harter Kanten.** Ein Gewichts-Sprung 1→0 zwischen Kern- und Tentakel-Vertex reißt, sobald die Wurzel sich
   bewegt (gemessen: Dehnung 4,3). Lösung: 2 Kanten-Ringe Kern-Mesh gehen abgeschwächt mit (`ring_fade` [0,5, 0,2] → Dehnung ~1,9).
   Mehr/stärkere Ringe sind *schlechter* ([0,7, 0,45, 0,2] → 4,0), weil sich dann Säume benachbarter Tentakel überlappen.
   Wo zwei Tentakel an der Wurzel verwachsen sind, Grenz-Vertices beider Ketten mitteln.
   Saum-Vertices bekommen max. 3 Tentakel-Knochen + Core = **max. 4 Einflüsse** (Unity-Standard; erster Versuch hatte 5 → FBX-Gegentest zeigte es).
4. **Wurzel-Knochen tief in den Körper setzen**, nicht auf die Kugeloberfläche: der Drehpunkt liegt dann dort, wo der Tentakel
   wirklich ansetzt, und der Ansatz bewegt sich mit, ohne dass der Mantel aufreißt.
5. **Ausschlag über die Kette verteilen, nicht linear zur Spitze steigern.** Alte Formel: Wurzel-Knochen 1/n der Spitze → oben
   praktisch starr. Neu: Anteil pro Knochen `root_weight + (1 − root_weight)·k/(n−1)`, normiert auf die Gesamtbiegung
   (`amp_deg` = Biegung der ganzen Kette). `root_weight` 0,75.
6. **Zwei Schichten, beide ab der Wurzel:** freie Welle (Wurzel → Spitze, `phase_step` 0,7 rad/Knochen, 2. Achse `swirl` mit
   eigener Phase und teils doppelter Frequenz, Phasen pro Tentakel nach goldenem Schnitt) + **Nachschwingen** (gedämpfte Feder pro Tentakel,
   angeregt von der Kern-Beschleunigung an der Ansatzstelle; `period_s` 0,75 bei `ref_length`, ∝ √Länge; `damping` 0,3; `lag_frames` 2).
   Das Nachschwingen braucht Kern-Bewegung mit Beschleunigung: Walk hat dafür jetzt `surge` (Schub nach dem Hub) und `pitch_osc_deg`.
7. **Loops exakt schließen:** Feder-Antwort für Loops über FFT als periodische Lösung (kein Einschwingen, `loop_ok` exakt);
   Nicht-Loops zeitschrittweise + Hüllkurve (`settle_frames`, Hit: sin-Hüllkurve) → Rückkehr zur Ruhe exakt.
8. **Death getrennt halten:** neues Verhalten als neue Funktion (`wobble`/`drive`), alte `tentacles()` bleibt für Death unverändert.
9. Kosten: mehr Knochen (hier 46 → 74). Für viele gleichzeitige Gegner ggf. `max_bones` 4 oder `bone_length` 0,1 testen.

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
  78 %, im proximalen Drittel immer noch 41 % → **die Wurzel biegt sich auch, nur weniger** → `root_weight` 0,75 (bewusst über dem Studienverhältnis ~0,53, weil die Wurzel sichtbar wabbeln soll – Nutzer).
  Wildes Oktopus-Arm-Video: [EurekAlert 1091123](https://www.eurekalert.org/multimedia/1091123).
- **Oktopus schwimmend**: Arme schleppen beim Kopf-voran-/Düsenschwimmen hinterher, beim Armschlag peitschen die
  eingerollten Spitzen am Ende gerade – [Scientific American](https://www.scientificamerican.com/blog/octopus-chronicles/new-views-into-the-octopuse28099s-bizarre-moves/)
  → `trail_deg` (Walk/Run), Attack: Ausholen → Peitschen.
- **Seeanemone in Strömung**: Tentakel schwingen weich, jeder etwas anders, Bewegung bis zum Fuß –
  [Uppbeat „swaying green sea anemone tentacles“](https://uppbeat.io/stock-video/asset/swaying-green-sea-anemone-tentacles-36937) ·
  [USF ETC Clip](https://etc.usf.edu/clipvideo/2993-wavering-bulbed-tentacles-of-a-sea-anemone)
  → `swirl` (zweite Achse), Phasen je Tentakel verschieden.

## Noch schwach
- Dehnung (nur Info): Walk 1,9 · Run 2,2 · Idle 1,6 · Ready 2,3 · Turn 1,9–2,0 · Attack1 2,6 · Hit 1,6 · Death 1,5 (vorher 1,2–1,7).
  Die höchsten Werte sitzen an verwachsenen Wurzeln (Tent_14/15) und an den kurzen Haken oben auf dem Körper – teils Eigenheit
  dieses Tripo-Meshes (wird ohnehin neu gemacht).
- Der Kern selbst (Mantel) bleibt starr; ein „Atmen“ des Mantels gibt es noch nicht.
- Hit ist mit 12 Frames kurz – das Nachschwingen wird von der Hüllkurve früh gedämpft.
- Die Bewegung ist noch nicht vom Nutzer abgenommen (Roh-GIFs: `creatures/void_manifestation/rig/anim/raw/`).
