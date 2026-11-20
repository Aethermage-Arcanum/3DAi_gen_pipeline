# Muster winged/bird – großer Aasvogel

Kreatur: **15 Bonepicker Vulture**. Code: `bird_clips.py` (eigener Code, nur der Baukasten ist mit drake gemeinsam),
Parameter: `style.toml`, Baukasten: `../winged_kit.py`.

## Naturbeobachtung (vor dem Animieren gesucht)
> Hinweis: Der Agent kann Videos nicht abspielen. Die Links sind recherchierte Quellen; die Werte stammen aus deren
> Beschreibungen, Literatur und Allgemeinwissen. **Bitte die Bewegung gegen die Videos abnehmen.**

| Vorbild | Wofür | Quelle |
|---|---|---|
| Gänsegeier am Aas | Hacken/Reißen, Hüpfen, Landung neben dem Kadaver | [Macaulay Library ML201522211 (Zeitlupe, Landung am fressenden Gänsegeier)](https://macaulaylibrary.org/asset/201522211), [Macaulay ML201579361 (Geier am Aas, Zeitlupe)](https://macaulaylibrary.org/asset/201579361) |
| Geier am Boden | Watschelnder Gang | [Storyblocks: Gänsegeier geht im Gehege](https://www.storyblocks.com/video/stock/griffon-vulture-walking-in-zoo-enclosure-351861553) |
| Geier springt/hebt ab | Absprung, schwere erste Schläge | [Getty: Himalaya-Geier springt und fliegt (Zeitlupe)](https://gettyimages.ca/detail/video/the-himalayan-vulture-standing-at-the-dry-stock-video-footage/1361922395), [NFB-Archiv: Geier startet (Zeitlupe)](https://archives.nfb.ca/stockshot/47968/) |
| Gänsegeier im Flug | Flügelschlag, Segeln/Kreisen, gefächerte Handschwingen | [Getty: Gänsegeier im Flug, Zeitlupe](https://gettyimages.ie/detail/video/slow-motion-griffon-vulture-in-flight-blue-sky-in-stock-video-footage/567646887), [Getty: Sperbergeier im Sturzflug](https://www.gettyimages.com/detail/video/with-ruppells-vulture-power-diving-over-wooded-stock-video-footage/680762731) |
| Flügelschlagfrequenz | Skalierung nach Masse/Spannweite | [Pennycuick: Predicting wingbeat frequency (JEB)](https://cob.silverchair.com/jeb/article/150/1/171/5695/Predicting-Wingbeat-Frequency-and-Wavelength-of) |

Abgeleitet: Gang 1,15 Hz mit starkem Watscheln (Rollen 6°), Kopfnicken 2× pro Zyklus (halten → vorschnellen);
Lauf = beidbeiniges Hüpfen 1,7 Sprünge/s mit Flügelschlag pro Sprung. Flug 1,36 Hz (Gänsegeier ≈ 1,5–2 Hz nach
Pennycuick-Skalierung; für die Spielkamera etwas langsamer), tiefe Abschläge, Aufschlag angewinkelt.

## Clips
| Clip | Inhalt |
|---|---|
| Walk | Watscheln, Kopfnicken, Flügel hängen halb offen und balancieren |
| Run | beidbeiniges Hüpfen, Körper im Bogen, Flügel heben sich bei jedem Sprung |
| TurnLeft / TurnRight | Trippeln auf der Stelle; Rumpf biegt sich in die Kurve, Kopf führt (Prüfung: Brust ±14°, Kopf ±46°), Schwanz schleppt nach |
| Idle | Kopf schaut umher, Flügel lüften, Schwanz wippt |
| Ready | Drohen: Flügel als Mantel gespreizt, Hals tief vorgestreckt, Schnabel offen (Fauchen) |
| Attack1 | Hacken: Hals zur S-Kurve zurück → ganzer Körper kippt vor, Hals streckt sich gerade, Schnabel schnappt (Event `hit`) → Reißen/Schütteln |
| Attack2 | Sprung-Krallenhieb: Ducken → Absprung mit Abschlag → Krallen voraus (Event `hit`) → Landung (Events `jump`, `land`) |
| Hit | Ruck zurück, Flügel zucken, Hals schnellt zurück |
| Death | **Platzhalter** (Death pausiert, Nutzerregel) |
| Fly / Glide | Ruderflug · Kreisen in der Thermik mit gefächerten (verdrehten) Handschwingen |
| TakeOff / Land | Ducken → Absprung → schwere Schläge → Fly-Pose · Anflug → Bremsen → Aufsetzen → Stand |

## Entscheidungen
- Federspitzen sind bei Tripo einseitig → `double_sided` im Rig. Halskrause + Brust-/Bauchfedern schwingen über
  `[dangling]` (Unity-Shader). Schnabel, Knochenkamm und Halsknochen bleiben starr.
- Hacken: der S-Hals wird beim Stoß **absolut** gerade gestreckt (sonst rollt er sich beim Vorneigen ein), der Schädel
  behält seine Form und neigt sich nur nach unten.
- Hinterzehe hängt am Toe (folgt dem Boden), sonst kippt sie mit dem Lauf in den Boden.
