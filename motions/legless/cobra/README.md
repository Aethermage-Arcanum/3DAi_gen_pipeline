# Bewegungsmuster legless/cobra

Generator `cobra_clips.py`, Werte `style.toml`. Erstes Modell: **Eel Stalker** (2026-11-17).

## Umbau 2026-11-17: Körperform absolut statt auf die Ruhepose addiert
Nutzer-Feedback aus Unity: Attack bewegte nur Hals/Kopf, Walk mit starrem Kopf, Ready nur verschoben/gedreht,
Turn = gedrehter Walk. **Ursache:** Das Tripo-Modell liegt schon verbogen da (Draufsicht S-Kurve, Wirbel-Gieren
−44° … +45°; Vorderkörper bis +54° aufgerichtet; Bauchunterseite wellt sich 0–9 cm über dem Boden; Kopf −26° geneigt).
Die alten Bausteine `wave()/bend()/head()` drehen jeden Wirbel *relativ* zu dieser Ruhepose – die feste S-Kurve
blieb in jedem Clip sichtbar, die Bewegung war nur ein kleiner Zusatz. Dazu hielt `keep_centered()` die
Blickrichtung des Kopfes in jedem Frame fest → Kopf wirkte starr.

**Neu:** `legless_kit.shape(yaw, pitch, head_yaw, head_pitch)` gibt für jeden Wirbel die **Richtung absolut** vor
(Gieren/Neigen gegenüber einer geraden, waagerechten Linie entlang +X). Die Ruhepose spielt keine Rolle mehr; der
Körper kann gerade, S-förmig oder aufgerichtet sein, wie der Clip es verlangt. Rollen bleibt wie modelliert.
Der Knick zwischen Kopf und letztem Wirbel wird auf 2 Halswirbel + Kopf verteilt (sonst reißen Kamm/Lappen).
Death ist unverändert (Nutzer-Anweisung) und nutzt weiter die alten Bausteine.

| Clip | Dauer | Inhalt |
|---|---|---|
| Legless_Cobra_Walk / Run | 1,2 / 0,67 s | Serpenoid-Welle (Gieren ±40° / ±50°, 1,4 / 1,25 Wellen) läuft Kopf → Schwanz über den **ganzen** Körper; Kopf geht mit (40 % Ausschlag, der Welle voraus), Kopfpartie leicht erhoben, Rest liegt flach |
| Legless_Cobra_TurnLeft/Right | 1,2 s | Körper liegt auf der Kurvenbahn (90° Richtungsänderung Schwanz → Hals), Hals +25° und Kopf +10° zusätzlich in die Kurve, Welle läuft weiter (70 %). Unity dreht das Objekt |
| Legless_Cobra_Idle | 4,0 s | lockere S-Schlinge am Boden, Hals erhoben; atmet (Schlinge/Hals heben-senken), langsame Welle läuft durch, Kopf schaut umher (Hals dreht mit), 2× kurzes Tasten/Züngeln (Kopf senkt sich, Maul zuckt) |
| Legless_Cobra_Ready | 1,33 s | **Drohhaltung:** Hinterkörper als gespannte S-Schlinge (±65°), vorderes Drittel steil aufgerichtet (bis 78°), Hals-S nach vorn, Kopf fixiert aufs Ziel; Vorderkörper pendelt ±14°, Schlinge „pumpt“ (±8 %), langsame Welle läuft durch die Schlinge |
| Legless_Cobra_Attack1 | 1,0 s | Ausholen (Schlinge zieht sich zusammen, Vorderkörper lehnt zurück, Körper rutscht 3 % zurück) → **Stoß aus dem ganzen Körper** in 4 Frames: S-Schlinge und Aufrichtung entladen sich, Körper streckt sich, Kopf schießt nach vorn-unten (Reichweite ≈ 0,36 Körperlänge), Maul auf → Biss (Event `hit` Frame 13) → schnell zurück in die Ready-Spannung (letzter Frame = Ready) |
| Legless_Cobra_Hit | 0,6 s | aus Ready: Vorderkörper kippt zurück, Kopf schnappt hoch/zur Seite, ein seitlicher Knick läuft vom Hals bis in den Schwanz, Körper rutscht zurück → zurück in Ready |
| Legless_Cobra_Death | 1,33 s | (unverändert, alte Bausteine) |

Stand-Clips (Idle/Ready/Attack/Hit) halten den **hinteren Körper (s < 0,4) fest** (Anker), damit der Stoß
wirklich aus dem gestreckten Körper nach vorn geht; Fortbewegung hält die Körpermitte fest (Clips „in place“).

## Naturreferenzen + abgeleitete Werte
- **Laterale Undulation an Land**: alle Körperpunkte folgen ungefähr derselben Bahn wie Kopf/Hals („wie Waggons
  hinter der Lok“), Krümmung entlang des Körpers fast konstant → Serpenoid-Kurve mit gleichem Ausschlag über die Länge,
  Hals leicht gedämpft. [Undulatory locomotion (Wikipedia)](https://wikipedia.com/wiki/Lateral_undulation) ·
  [Snake Locomotion (Univ. Louisiana)](https://userweb.ucs.louisiana.edu/~brm2286/locomotn.htm) ·
  Video [OUP: lateral undulation](https://learninglink.oup.com/access/content/scott1e-student-resources/scott1e-video-4-4-lateral-undulation) ·
  Hu et al. 2009, [Mechanics of Slithering](https://www.originalwisdom.com/wp-content/uploads/bsk-pdf-manager/2021/01/Hu-et-al_2009_The-Mechanics-of-Slithering-Locomotion.pdf) ·
  Sharpe et al. (CRAB Lab): [PDF](https://crablab.gatech.edu/pages/publications/pdf/icaa125.pdf)
  → `amp_deg 40/50`, `waves 1.4/1.25`, `envelope` (Schwanz etwas weiter = Aal-Anteil, Hals 0,6).
- **Wasser (Aal)**: Ausschlag wächst zum Schwanz hin – nur als leichte Betonung übernommen (Tripo-Aal bewegt sich an Land).
- **Kurve**: kleine Kopfdrehung lenkt den ganzen Körper um ein Hindernis, der Körper folgt der Bahn –
  Astley et al. 2020, [Bioinspir. Biomim.](https://crablab.gatech.edu/pages/publications/pdf/Astley_2020_Bioinspir._Biomim._15_065005[2655].pdf)
  → konstante Kurvenkrümmung (`arc_deg`) + Kopf/Hals voraus (`lead_deg`, `head_lead_deg`).
- **Kobra-Aufrichten**: nur 13–22 % der Länge aufgerichtet, Scheinstöße aus dieser Haltung – Nasoori et al. 2016,
  *Naja oxiana*: [ATSU](https://scholarworks.atsu.edu/kcom-faculty/83) · Haube/Halten erfordert Dauerspannung –
  Young & Kardong 2010, [J Exp Biol](https://cob.silverchair.com/jeb/article-pdf/213/9/1521/1275225/1521.pdf)
  → `coil_end 0.6` (Aufrichtung + Hals), Pendeln `sway_deg`, „Pumpen“ `tension`.
- **Zustoßen**: Vipern erreichen die Beute meist in < 100 ms (21–208 ms), Elapiden (Kobras) 30–340 ms; Ablauf:
  vorderes Drittel streckt sich aus der Krümmung, Kontakt ≈ 80 ms, Rückzug 130–160 ms; Elapiden „kriechen“ oft
  näher und stoßen weniger explosiv – [Kinematics of strikes in venomous snakes (JEB 2025, 36 Arten)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12582407/),
  Zeitlupe [Vipera ammodytes (Movie 2)](https://movie.biologists.com/video/10.1242/jeb.250347/video-2) ·
  Ratten-/Wassermokassin/Klapperschlange: [Higham et al. 2017](https://biomechanics.ucr.edu/Higham_etal_2017_SciRep.pdf)
  → Stoß 4 Frames (133 ms, für die Lesbarkeit etwas langsamer als Natur), Biss halten 4 Frames, schnelles
  Zurückziehen (Ease-out) und Einpendeln; Maul ≤ 20° (Mesh-Grenze, s. u.).
- Zeitlupen-Bisse: [Brave Wilderness „snake bites in super slow motion“](https://rosetta.to/u/bravewilderness/snake-bites-in-super-slow-motion).

## Erkenntnisse
- Kiefer: über ~20° Öffnung reißen die Mundwinkel des Tripo-Mesh → Maulöffnung klein halten, Wirkung über Kopf-/Körperbewegung.
- Dehnung (nur Info): Walk/Turn bis ~2,6–3,4 an winzigen Kanten (0,6 cm) am Ansatz der Hals-Stacheln (Gewichte
  Spine_14/Head uneinheitlich) – im Bild nicht als Riss sichtbar. Bauch unter Spine_09/10 ~2,0, weil dort die
  +54°-Aufrichtung der Ruhepose geradegebogen wird. Behebung gehört ins Rig (Gewichte), nicht in kleinere Bewegung.
- UV: Formel wählte Smart UV, Sichtprüfung → Tripo-UV per `[uv] mode = "tripo"` (siehe creature.toml).
