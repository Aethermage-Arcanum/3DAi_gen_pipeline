# Bewegungsmuster legless/cobra

Generator `cobra_clips.py`, Werte `style.toml`. Erstes Modell: **Eel Stalker** (2026-11-17), alle 9 Clips grün.

| Clip | Dauer | Inhalt |
|---|---|---|
| Legless_Cobra_Walk / Run | 1,2 / 0,67 s | laterale Undulation, Welle Kopf → Schwanz, Kopf waagerecht + ruhig |
| Legless_Cobra_TurnLeft/Right | 1,2 s | Welle + Krümmung zur Drehseite (Unity dreht das Objekt) |
| Legless_Cobra_Idle | 3,0 s | schwaches Wogen, Kopf leicht erhoben, schaut umher |
| Legless_Cobra_Ready | 1,33 s | **Kobra-Haltung**: vorderes Viertel aufgerichtet, S-Kurve im Hals, Pendeln, Maul leicht offen |
| Legless_Cobra_Attack1 | 0,87 s | aufrichten + Hals zurück → nach vorn-unten zustoßen (Vorstoß 18 % Länge), Maul auf → zu (Event `hit` Frame 14) |
| Legless_Cobra_Hit | 0,4 s | Vorderkörper zuckt zurück + zur Seite |
| Legless_Cobra_Death | 1,33 s | letzte Zuckung, Körper verdreht, Kopf sinkt, liegt schlaff am Boden |

## Naturreferenzen
- **Laterale Undulation**: Krümmungen laufen vom Kopf zum Schwanz, Wellenlänge/Krümmung entlang des Körpers fast konstant – Sharpe et al., *Chionactis occipitalis* (Georgia Tech CRAB Lab): [PDF](https://crablab.gatech.edu/pages/publications/pdf/icaa125.pdf) · Überblick [Undulatory locomotion](https://wikipedia.com/wiki/Lateral_undulation) · Hu & Shelley 2012, Slithering: [PDF](https://www.originalwisdom.com/wp-content/uploads/bsk-pdf-manager/2021/01/Hu-and-Shelley_2012_slithering-locomotion.pdf)
- **Kobra-Aufrichten**: nur 13–22 % der Körperlänge werden aufgerichtet, Scheinstöße aus dieser Haltung – Nasoori et al. 2016, *Naja oxiana*: [ATSU](https://scholarworks.atsu.edu/kcom-faculty/83) · Haube spreizt von vorn nach hinten: Young & Kardong 2010, *J Exp Biol*: [PubMed](https://pubmed.ncbi.nlm.nih.gov/20400637)
- Videos zum Abgleich: „cobra strike slow motion“, „snake lateral undulation slow motion“, „moray eel lunge“.

## Erkenntnisse
- Kiefer: über ~20° Öffnung reißen die Mundwinkel des Tripo-Mesh (Dehnung > 1,9) → Maulöffnung klein halten, Wirkung über Kopf-/Körperbewegung.
- Aufrichten ursprünglich 40 % der Länge, nach Naturreferenz auf das vordere Viertel reduziert (`raise_lo = 0.75`).
- UV: Formel wählte Smart UV, Sichtprüfung → Tripo-UV per `[uv] mode = "tripo"` (siehe creature.toml).
