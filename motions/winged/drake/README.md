# Muster winged/drake – schwerer Wyvern

Kreatur: **14 Cinder Wyvern**. Code: `drake_clips.py`, Parameter: `style.toml`, Baukasten: `../winged_kit.py`.

## Naturbeobachtung (vor dem Animieren gesucht)
> Hinweis: Der Agent kann Videos nicht abspielen. Die Links sind recherchierte Quellen; die Werte stammen aus deren
> Beschreibungen, Literatur und Allgemeinwissen. **Bitte die Bewegung gegen die Videos abnehmen.**

| Vorbild | Wofür | Quelle |
|---|---|---|
| Komodowaran | schwerer Gang, Rumpf biegt sich seitlich, Kopf pendelt, Schwanz schwingt als S-Welle | [Storyblocks: Komodo walks by](https://www.storyblocks.com/video/stock/komodo-dragon-walks-by-4k-a3v0u02), [Getty: wilder Komodowaran](https://www.gettyimages.at/detail/video/wild-komodo-dragon-lizard-walking-komodo-island-stock-filmmaterial/484530178), [Waran-Gang XROMM (EurekAlert)](https://www.eurekalert.org/multimedia/589093) |
| Vampirfledermaus am Boden | Flügel als Stütze/Gang am Boden (Option, siehe offene Frage) | [National Geographic: How to be a bat (Gehen + Rennen)](https://www.nationalgeographic.com/science/article/how-to-be-a-bat-life-in-motion), [Cornell: Vampirfledermäuse rennen](https://news.cornell.edu/node/282646), [Boing Boing: Video](https://boingboing.net/2013/06/18/watch-this-vampire-bat-run-lik.html) |
| Flughund / große Fledermäuse | Flügelschlag: Abschlag gestreckt, Aufschlag angewinkelt (Hand eingeklappt), Spitze folgt verzögert | [JEB: Körpergröße und Flügelbewegung bei Fledermäusen](https://cob.silverchair.com/jeb/article-split/213/23/4110/10086/The-effect-of-body-size-on-the-wing-movements-of) |
| Adler/Pelikan | schwere Landung: Flügel steil bremsen, Beine voraus | (siehe Geier-Quellen im bird-README) |

Abgeleitet: Gang 0,94 Hz (Waran 0,8–1,1 Hz), Standanteil 0,62, Rumpfbiegung 7°, Schwanz-Welle 12° mit Verzögerung 8 %/Glied.
Flügelschlag 1,15 Hz (Flughund ≈ 2–3 Hz; ein Tier dieser Größe schlägt deutlich langsamer), Abschlag 55 % des Zyklus,
Aufschlag mit halb eingeklappter Hand, Flügelspitze 8 % Zyklus verzögert.

## Clips
| Clip | Inhalt |
|---|---|
| Walk / Run | zweibeinig, Becken giert, Gewicht pendelt, Rumpf biegt sich, Kopf hält Blickrichtung, Schwanz-S-Welle, Flügel pendeln gegengleich |
| TurnLeft / TurnRight | auf der Stelle; Rumpf biegt sich in die Kurve, Kopf führt (Prüfung: Brust ±18°, Kopf ±43° voraus), Schwanz schleppt nach |
| Idle | Atmen, Kopf schaut umher, Flügel „ordnen“ sich, Schwanz schwingt |
| Ready | Drohen: Flügel gespreizt, Hals tief, Maul offen, Schwanz peitscht |
| Attack1 | Biss-Ausfall: aufrichten + Flügel hoch → Körper schießt vor, Flügel schlagen nach vorn, Maul schnappt (Event `hit`) |
| Attack2 | Schwanzkeule: Ausholen → Ganzkörper-Peitsche Becken → Rumpf → Schwanz (Glied für Glied verzögert), Körper wirbelt herum |
| Hit | Ruck zurück, Flügel zucken, Hals schnellt zurück, Schwanz peitscht nach |
| Death | **Platzhalter** (Death pausiert, Nutzerregel) |
| Fly | Flügelschlag-Zyklus, Körper hebt sich im Abschlag, Beine angezogen, Schwanz steuert |
| Glide | Segeln mit langsamem Kurven (Rollen), Schwanz als Ruder |
| TakeOff / Land | Ducken → Absprung → 2 Schläge → Fly-Pose · Anflug → Bremsen → Aufsetzen → Stand (Events `jump`, `liftoff`, `land`) |

## Entscheidungen
- **Zweibeinig am Boden** mit erhobenen Flügeln (wie im Referenzbild). Alternative wäre Gang auf den Flügel-
  Handgelenken (Fledermaus/Pterosaurier) – offene Frage an den Nutzer.
- **Flügel und Schwanz absolut** (Tripo: Flügel ungleich, Schwanz seitlich gebogen). Die Gelenkwinkel der Flügel bleiben
  wie modelliert (links/rechts gemittelt); gespreizt wird nur am Ellbogen, nie weiter am Handgelenk als modelliert,
  sonst reißt die Flughaut.
