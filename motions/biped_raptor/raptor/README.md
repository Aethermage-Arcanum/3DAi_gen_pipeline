# Bewegungsmuster biped_raptor/raptor

Generator `raptor_clips.py`, Werte `style.toml`. Erstes Modell: **Dune Raptor** (2026-11-17), alle 9 Clips grün.

| Clip | Dauer | Inhalt | Vorbild |
|---|---|---|---|
| Biped_Raptor_Walk | 1,0 s | Beine im Gegentakt, Rumpf rollt zum Standbein, Kopf bleibt im Raum stehen | Strauß/Emu-Schritt, Huhn-Kopfstabilisierung |
| Biped_Raptor_Run | 0,53 s | kurze Bodenphase, Flugphase, Rumpf nach vorn, Schwanz hoch als Gegengewicht | Laufvogel-Rennen |
| Biped_Raptor_TurnLeft/Right | 0,87 s | auf der Stelle drehen | – |
| Biped_Raptor_Idle | 3,0 s | ruckartige Kopfwendungen mit Halten (vogeltypisch), Atmen | Huhn/Strauß |
| Biped_Raptor_Ready | 1,0 s | tief geduckt, Kopf vor, Maul auf (Fauchen), Krallen hoch, Schwanz steif | – |
| Biped_Raptor_Attack1 | 0,87 s | **Stampf-Tritt**: Gewicht aufs linke Bein, rechter Fuß hoch → in 2 Frames nach vorn-unten stampfen (Event `hit` Frame 12) | Sekretärvogel |
| Biped_Raptor_Hit | 0,33 s | Ruck zurück, Kopf weg | – |
| Biped_Raptor_Death | 1,33 s | knickt ein, kippt zur Seite, Beine erschlaffen ab ¼ des Kippens | – |

## Naturreferenzen
- **Sekretärvogel-Tritt**: Kontakt nur ~15 ms, Kraft ≈ 5× Körpergewicht – Portugal et al. 2016, *Current Biology* 26(2): [Royal Holloway](https://pure.royalholloway.ac.uk/en/publications/the-fast-and-forceful-kicking-strike-of-the-secretary-bird/) · [PDF](https://pure.royalholloway.ac.uk/files/26253728/Portugal_et_al_Curr_Biol_Author_Accepted_Copy.pdf) · [Sci.News](https://www.sci.news/biology/secretary-birds-their-prey-force-5-times-their-weight-03589.html)
- Laufvögel (Strauß/Emu): Videos „ostrich running slow motion“, „emu walking side view“; Kopfstabilisierung: „chicken head stabilization“.

## Erkenntnisse
- Oberschenkel-IK-Steifigkeit (`[rig] thigh_stiffness`) brachte hier nichts Messbares – die Dehnung kam von der Hautbrücke, nicht vom Oberschenkel.
- Dehnungs-Grenzen pro Clip erhöht (bis 6): schlimmste Dreiecke innen am Oberschenkel an der entfernten Brücke, Sichtprüfung seitlich + schräg ohne sichtbare Risse.
