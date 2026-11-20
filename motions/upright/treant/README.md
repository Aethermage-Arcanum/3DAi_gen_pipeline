# Bewegungsmuster upright/treant

Generator `treant_clips.py`, Werte `style.toml`, Baukasten `../upright_kit.py`, Skelett `rigging/upright_rig.py`.
Erstes Modell: **Bog Warden** (2026-11-18). Ein wandelnder Sumpfbaum: schwer, langsam, Äste und Krone schwingen nach.

| Clip | Dauer | Inhalt | Vorbild |
|---|---|---|---|
| Upright_Treant_Walk | 1,27 s (38 F) | Schwerer Schritt mit langer Doppelstütze (Standanteil 0,68). Das Gewicht pendelt seitlich übers Standbein, der Oberkörper kippt mit. Der Rumpf sackt kurz nach jedem Aufsetzen ein und nickt nach. Das Becken dreht mit dem Schwungbein vor, die Brust verzögert dagegen. Die Ferse löst sich zuerst (Abrollen über die Wurzelzehen). Die Arme pendeln gegen die Beine als Welle Oberarm → Unterarm → Finger und federn beim Aufsetzen nach. Die Krone bleibt hinter dem Pendeln zurück. | Elefant |
| Upright_Treant_Run | 0,87 s (26 F) | Schweres Eiltempo **ohne Flugphase** (Standanteil 0,52, wie ein schneller Elefant). 18° Vorlage, mehr Federn, weiter ausholende Arme. | Elefant schnell |
| Upright_Treant_TurnLeft/Right | 1,2 s (36 F) | Auf der Stelle 40° pro Zyklus. Der Oberkörper dreht voraus (14°) und neigt sich in die Kurve, Krone und Arme schleppen nach. **TurnLeft dreht links** (gemessen: `body_turns`, `upper_body_leads` im clips_report). | Regel „Körper dreht in die Kurve, Oberkörper führt“ |
| Upright_Treant_Idle | 4,0 s (120 F) | Der Stamm „atmet“ langsam vor und zurück. Das Gewicht wandert, der Oberkörper wendet sich einmal links und einmal rechts. Wind in der Krone mit zwei Frequenzen (2 und 3 pro Clip), die Arme hängen schwer und schwingen verzögert, die Finger kriechen. | Baum im Wind |
| Upright_Treant_Ready | 1,6 s (48 F) | Tiefer (Knie gebeugt), 20° vorgebeugt, Arme vor und gespreizt. Die Krallenfinger öffnen und schließen sich, das Gewicht pendelt schwer links-rechts, schweres Atmen. | Gorilla vor dem Angriff |
| Upright_Treant_Attack1 | 2,07 s (62 F) | **Wurzel-Slam:** Ausholen (Oberkörper zurück, Schultern hoch, beide Arme vor-oben über das Gesicht, Krone kippt verzögert). Dann der Schlag in 6 Frames (beschleunigt): Der Rumpf klappt auf 56° vor, der Körper sackt ein, die Arme schlagen nieder (Unterarm, Hand und Finger verzögert). Die **Hände treffen den Boden** (Hand-IK, Event `hit` Frame 26). Der Körper federt über den aufgesetzten Händen nach, die Krone peitscht vor. Danach schweres Aufrichten. | Gorilla schlägt auf den Boden |
| Upright_Treant_Attack2 | 1,87 s (56 F) | **Ast-Peitsche** mit dem rechten Arm. Ausholen: Gewicht aufs rechte Bein, Rumpf nach rechts gedreht, Arm weit hinten-außen. Dann die Welle Becken → Brust → Oberarm → Unterarm → Hand → Finger, jedes Glied 1,6 Frames später. Der Arm fegt fast waagerecht von rechts über vorn nach links (Event `hit` Frame 24), die Finger schnellen auf. Der Arm schwingt nach links durch, der andere Arm schwingt zum Ausgleich zurück. | Elefantenrüssel |
| Upright_Treant_Hit | 0,73 s (22 F) | Ruck zurück. Brust, Krone, Arme und Finger laufen zeitversetzt nach. Endet exakt in der Standhaltung. | – |
| Upright_Treant_Death | 1,0 s (30 F) | **PLATZHALTER – Death pausiert (Nutzer).** Sackt nur etwas ein und neigt sich vor. Bewusst keine Arbeit, bis der Nutzer Death-Clips freigibt. | – |

## Naturreferenzen
Hinweis: Claude kann Videos nicht abspielen. Die Werte stammen aus den Messwerten der Studien und aus Beschreibungen bzw. Standbildern der verlinkten Clips. **Der Nutzer sollte die Videos gegen die GIFs ansehen.**

- **Elefant – schwerer Schritt, Gewichtsverlagerung**
  - Studie: Hutchinson et al. 2006, *The locomotor kinematics of Asian and African elephants*, J Exp Biol 209 ([RVC-Repository](https://rvc-repository.worktribe.com/output/1433280), [PDF](https://rvc-repository.worktribe.com/OutputFile/1433288)). Über 2400 Schritte von 62 Tieren. Elefanten werden vor allem über die **Schrittfrequenz** schneller und behalten auch schnell einen lateralen Fußfolge-Gang **ohne Flugphase** bei. Der Standanteil sinkt erst schnell bis ≈ 0,37.
  - Dazu: [„Do elephants run?“ (SICB-Abstract)](https://sicb.org/?p=36424) und [Nature News 2007 „Elephants run in slow motion“](https://www.nature.com/news/2007/070625/full/news070625-6.html).
  - Videos: Herde in Seitenansicht, Zeitlupe ([Getty](https://www.gettyimages.in/detail/video/stunning-herd-of-african-elephants-majestically-walking-stock-footage/1478757212)) und Elefanten gehend, Zeitlupe, Masai Mara ([Videvo](https://static.videvo.net/video/slow-motion-of-african-elephant-in-beautiful-savanna-landscape-africa-wildlife-animals-in-masai-mara-national-reserve-kenya-steadicam-gimbal-tracking-shot-of-elephants-walking/5197457)).
- **Gorilla – aufgerichtet, Schlag auf Boden und Brust**
  - Silberrücken trommelt auf die Brust: [PetaPixel 2023](https://petapixel.com/2023/09/08/large-silverback-gorilla-beats-his-chest-right-in-front-of-photographer), [My Modern Met](https://mymodernmet.com/silverback-gorilla-beat-his-chest-wildlife-photographer/), [Max-Planck-Video (EurekAlert)](https://www.eurekalert.org/multimedia/915420).
  - Gorilla stürmt auf sein Spiegelbild zu und **schlägt mit den Händen auf den Boden** (Studie in Gabon): [A-Z Animals](https://a-z-animals.com/blog/gorilla-shows-his-strength-to-his-reflection/). Vorbild für Ausholen über Kopf → beidhändiger Schlag mit dem ganzen Oberkörper.
- **Elefantenrüssel – Peitschen-/Schwungbewegung**
  - Zeitlupe, Rüssel über dem Kopf geschwungen: [NFB-Archiv 73229](https://archives.nfb.ca/stockshot/73229/).
  - Studie: Schulz, Hu et al. 2022, *Skin wrinkles and folds enable asymmetric stretch in the elephant trunk*, PNAS ([PDF](https://hu.gatech.edu/wp-content/uploads/2022/12/Hu22-wrinkles.pdf), [ScienceDaily](https://sciencedaily.com/releases/2022/07/220718154340.htm)). Der Rüssel bewegt sich in Wellen abschnittsweise, die Spitze ist beweglicher als der Ansatz. Daraus folgt die Kette mit wachsender Verzögerung und weicherer Feder zur Spitze.
- **Baum im Sturm – Äste schwingen verzögert**
  - Videos: [Adobe Stock, Baum im Wind, Zeitlupe](https://stock.adobe.com/video/windy-tree-rainy-day-windy-weather-waving-tree-branches-slow-motion-blowing-wind-rainy-weather-windy-day-tree-strong-wind-swaying-branches-wind-blowing-tree-branches-nasty-day-overcast-weather/535562160) und [Kiefern im Sturm](https://stock.adobe.com/video/strong-wind-moving-tree-trees-swaying-during-storm-pine-tree-branches-swaying-in-strong-wind-swaying-trees-in-strong-wind-looking-up-at-tall-swaying-pine-trees-in-forest-wind-moving-tops-of-pine/1581253256).
  - Studien: Jackson et al. 2019, *An architectural understanding of natural sway frequencies in trees* ([UCL, PDF](https://discovery.ucl.ac.uk/10078184/1/Jackson%20et%20al%20%282019%29%20An%20architectural%20understanding%20of%20natural%20sway%20frequencies%20in%20trees%20-%20accepted.pdf)): Laubbäume haben **mehrere** Eigenfrequenzen. Silberahorn-Studie 2014 ([PDF](https://auf.isa-arbor.com/content/40/3/125.full.pdf)): Äste dämpfen das Schwingen stark (wie viele kleine Tilger). [Oscillation damping in trees](https://hal-polytechnique.archives-ouvertes.fr/hal-00996427v1).
  - Daraus: Die Krone folgt dem Stamm verzögert (weiche, gedämpfte Feder), Idle-Wind mit zwei Frequenzen, Moos-Strähnen schwingen langsam (Shader 0,6 Hz).

## Daraus abgeleitete Werte (style.toml)
Bog Warden: Höhe 1,0 m (Modell), Hüfthöhe = Beinlänge 0,32 m. Kurze, dicke Wurzelbeine, sehr lange Arme.

| Wert | Wert | Herleitung |
|---|---|---|
| Walk `duty` | 0,68 | Elefant geht mit Standanteil 0,65–0,75 → immer ein Fuß fest, schwer |
| Walk Zyklus | 38 F (0,79 Hz) | Elefant langsam ≈ 0,6–0,8 Hz; schwer, aber nicht zäh |
| Walk Schritt | 0,75 Beinlängen Fußweg → ≈ 1,1 Hüfthöhen pro Zyklus, 0,24 m/s | Elefant 1,0–1,5 Hüfthöhen pro Zyklus |
| Walk Federn | 1,2 % H, tiefster Punkt 7 % Zyklus **nach** dem Aufsetzen | Last sackt nach (schwer) statt reinem umgekehrten Pendel |
| Walk Seitenpendeln | 1,8 % H + 3° Rollen | Elefant/Riese verlagert das Gewicht deutlich übers Standbein |
| Run | Standanteil 0,52, 26 F, keine Flugphase, 0,65 m/s | Elefanten „rennen“ ohne Flugphase |
| Arme | Pendeln 13° (Run 24°), Unterarm 7 % Zyklus später, Finger noch später | schwere Äste: wenig Ausschlag, viel Verzögerung = Gewicht |
| Krone | folgt dem Rollen zu 80 % mit 8 % Zyklus Verzögerung, nickt nach dem Aufsetzen | Baum: Äste dämpfen und schwingen nach |
| Attack1 | Ausholen 20 F, Schlag 6 F (beschleunigt), Hände 10 F am Boden | Gorilla: langsames Aufrichten, explosiver Schlag |
| Attack2 | Kette Becken → Finger je 1,6 F später, Feder zur Spitze weicher | Rüssel: Welle läuft zur Spitze |

## Haltung absolut
Die Tripo-Ruhepose ist gebückt (Rumpf-Achse ≈ 8,5° vor) und leicht schief. Jeder Clip gibt die Neigung der Rumpf-Achse **absolut** vor (`posture()` im Baukasten: Stand 9°, Walk 11°, Run 18°, Ready 20°, Slam 56°) und stellt die Seitenneigung gerade. Hit endet exakt in der Standhaltung (Frame 0).

## Varianten (geplant, nur Werte)
- **Elder Warden** (Elite, 1,5×): langsamer (Walk ≈ 44 F), Krone schwingt stärker nach (`crown_roll_k`).
- Golem und Brute bekommen **eigene Muster** (`upright/golem`, `upright/brute`): andere Angriffsmechanik und ein eigener Kopf.
