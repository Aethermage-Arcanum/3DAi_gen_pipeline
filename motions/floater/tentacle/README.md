# Bewegungsmuster floater/tentacle

Generator `tentacle_clips.py`, Werte `style.toml`. Erstes Modell: **Void Manifestation** (2026-11-17), alle 9 Clips grün.

| Clip | Inhalt |
|---|---|
| Floater_Tentacle_Walk / Run | Kern wippt + neigt sich nach vorn, Tentakel wellen und schleppen nach |
| Floater_Tentacle_TurnLeft/Right | neigt sich in die Kurve |
| Floater_Tentacle_Idle | Quallen-Pulsieren: Tentakel ziehen sich rhythmisch zusammen |
| Floater_Tentacle_Ready | Tentakel weit gespreizt, Kern hebt sich, zittert |
| Floater_Tentacle_Attack1 | ausholen (Tentakel nach hinten) → nach vorn peitschen (Event `hit` Frame 14) |
| Floater_Tentacle_Hit | Rückstoß, Tentakel schlagen wild |
| Floater_Tentacle_Death | Tentakel erschlaffen, Kern kippt und sinkt zu Boden |

## Naturreferenzen
- **Qualle**: Pulsation mit Arbeitsanteil ~0,4–0,5 des Zyklus; Drehen durch ungleichzeitiges Zusammenziehen der Schirmseiten – TU Delft (Sarsia-Modell): [PDF](https://repository.tudelft.nl/file/File_d3de7605-d494-4ba5-9fad-9367ed692da8) · Saugschub statt Drücken: [MBL](https://new-www.mbl.edu/news/push-or-pull-how-many-limbed-marine-organisms-swim)
- **Oktopus-Arm**: Ausstrecken als Biegewelle vom Ansatz zur Spitze (Yekutieli et al. 2005, *J Neurophysiol*; Gutfreund et al. 2001, *Science*) – Videos: „octopus arm reaching slow motion“, „squid tentacle strike slow motion“.
