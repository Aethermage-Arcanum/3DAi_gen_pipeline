# Bewegungsmuster quadruped/deer (Hirsch)

Generator: `deer_clips.py` (eigener Code, nutzt `../quadruped_kit.py`), Werte `style.toml`. Erstes Modell: **Hollow Stag** (2026-11-17).

## Was dieses Muster ausmacht
- **Walk**: lateraler Viertakt, steifer Huftier-Rücken (wenig Gieren), deutliches **Kopfnicken 2× pro Schritt, ¼ Zyklus gegen den Widerrist versetzt**, Hufe werden hoch angehoben und klappen nach hinten weg.
- **Run = Transvers-Galopp** (Huftiere): HL → HR → VL → VR, gesammelte Schwebe; Rücken steif (6°), dafür starkes Schaukeln (8°) und Hals pumpt mit; Wedel hoch.
- **Ready = Drohen**: Geweih gesenkt und pendelnd, **Vorderhuf stampft** 2× (Warnsignal beim Rotwild), Gewicht hinten.
- **Attack1 = Geweihstoß**: Kopf tief, zurückladen → Hinterhand schiebt vor, Stoß (Event `hit` Frame 14), Geweih hakt nach oben/seitlich, zurückfedern.
- Death unverändert (Nutzer-Anweisung; bekannt: 2,5 cm Lücke).

## Naturreferenzen
- Loscher et al. 2016, *Timing of head movements is consistent with energy minimization in walking ungulates* (19 Arten): Kopf nickt 2× pro Schritt, Phasenversatz Kopf ↔ Widerrist ≈ 25 % des Zyklus (Pferd: Kopf 9 cm, Widerrist 3 cm Hub) – [PMC5136594](https://pmc.ncbi.nlm.nih.gov/articles/PMC5136594), Daten: [Dryad](https://datadryad.org:443/stash/dataset/doi:10.5061/dryad.rf5bj)
- Galopp-Arten (transvers bei Huftieren, rotierend bei Raubtieren): [vanat.ahc.umn.edu/gaits](https://vanat.ahc.umn.edu/gaits/) · Biancardi & Minetti 2012 (J Exp Biol)
- Videos (Stock-Vorschau): [Rothirsch läuft, Zeitlupe (Kurator)](https://kurator.com/en/video/detail/2242698) · [Rothirsch-Galopp als Loop (Adobe Stock)](https://stock.adobe.com/search/video?k=deers) · [Rotwild, Schottland (Getty)](https://www.gettyimages.com/detail/video/red-deer-stock-footage/1082615470) · Suchbegriffe „red deer gallop slow motion“, „stag fight rut“, „deer stomping foreleg warning“.

## Abgeleitete Werte (2026-11-17)
| Wert | vorher | jetzt | Herleitung |
|---|---|---|---|
| Kopfnicken Walk | 3°, im Takt des Rumpfs | 6°, 2×/Schritt, +¼ Zyklus versetzt | Loscher 2016 |
| Run | Wolfsgalopp (rotierend, Kopie) | Transvers-Galopp HL 0 · HR 0,1 · VL 0,5 · VR 0,6, Stand 32 % | Huftier-Galopp |
| Run Rücken/Schaukeln | 5° / 3° | 6° / 8° | steifer Rücken, Schaukelpferd-Bewegung |
| Fußbahn/Rumpfhöhe | Ruck, Knicke | `gait_smooth`, `reach_smooth` | siehe wolf/README |
| Ready | Kopf 18° tief, statisch + Zittern | Geweih 30° tief + pendelt 12°, Huf stampft | Rotwild-Warnverhalten |
| Attack1 | Stoß über einfache Ein-/Ausblendung | Schlüsselkurven mit Ausholen, Stoß, Haken 16° (Kopf rollt mit), Nachfedern | Brunftkampf |

## Bodenkontakt
Vorher ≤ 0,13 cm, jetzt ≤ 0,1 cm (`feet_on_ground`). Death unverändert.
