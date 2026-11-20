# Bewegungsmuster octopod/crab

**Eigenes Muster** (nicht nur Variablen von Ant): Seitwärtsgang mit Fuß-IK, eigene Schrittfolge, Scheren erhoben, Angriffe aus den Scheren.

Generator: `crab_clips.py` (nutzt `../octopod_kit.py`). Test auf einem Modell mit anderem eigenem Muster:
```
python scripts/creature_pipeline.py creatures/<NN_name> --style octopod/crab
```
→ Ausgabe in `creatures/<NN_name>/style_tests/crab/`

## Clips (Validierung 2026-11-17 auf dem Chitin Crawler, also einem Ameisenkörper!)
| Clip | Dauer | Inhalt | Prüfung |
|---|---|---|---|
| Octopod_Crab_Walk / WalkLeft | 0,8 s | seitwärts (rechts/links), führende Seite 2-4-3, nachziehende 2-3-4 | Bodenkontakt **0,0 mm**, Schritt 8,7–9,4 cm, 0,19 m/s seitwärts |
| Octopod_Crab_Run | 0,47 s | schneller seitwärts | Bodenkontakt 0,0 mm, 0,41 m/s |
| Octopod_Crab_TurnLeft/Right | 0,73 s | auf der Stelle drehen | 26 °/s |
| Octopod_Crab_Idle | 2,0 s | Scheren abwechselnd zum Mund (fressen), Fühler zucken | Füße stehen |
| Octopod_Crab_Ready | 1,0 s | Drohhaltung: Scheren hoch + gespreizt, Zittern | Füße stehen |
| Octopod_Crab_Attack1 | 0,73 s | **aufbäumen** auf die hinteren Laufbeine (Rumpf vorne 10° hoch, vorderes Laufbeinpaar hebt mit ab) + ausholen → Zuschnappen in 2 Frames mit leichtem Nach-vorne-Fallen → halten → zurück, Event `hit` | tragende Füße 0,0 mm |
| Octopod_Crab_Hit | 0,3 s | Körper sackt kurz, Scheren schützend nach innen | kehrt zur Ruhe zurück |
| Octopod_Crab_Death | 1,2 s | gemeinsamer Tod aus dem Baukasten (auf den Rücken) | kein Teil im Boden |

Alle 10 Clips grün, Gelenk-Lücken max. 0,8 cm.

## Naturreferenzen
- **Seitwärtsgang / Schrittfolge:** Winkerkrabbe *Uca pugnax*, im Mittel ≈ alternierender Vierfuß. Führende Seite 2-4-3-5, nachziehende 2-5-3-4, Scheren (Bein 1) vom Boden gehalten. [Barnes 1975, J Comp Physiol](https://link.springer.com/article/10.1007/BF00612697)
- **Drohhaltung:** hoch auf den Beinen, Scheren erhoben und gespreizt („meral spread“), das Drohen kommt meist vor dem Angriff. [Uni Bristol: Defensive behaviour in intertidal crabs](https://research-information.bris.ac.uk/en/publications/defensive-behaviour-in-intertidal-crabs/) · [Nautilus: The wild world of threats](https://nautil.us/the-wild-world-of-threats-238413)
- **Schlag:** schnelles Beugen der Scheren in 30–60 ms, nur aus der Drohhaltung. [Royal Holloway Thesis](https://repository.royalholloway.ac.uk/items/4e9e8c37-19ce-4967-8dbd-a16025e0fc5b/1/)

## Aufbäumen beim Scherenschlag (Nutzer-Wunsch 2026-11-17)
Statt den Körper senkrecht zu heben (die fast gestreckten Ameisenbeine geben nur ~1 cm her), **kippt** der Rumpf um die Hüftlinie des vordersten tragenden Beinpaars:
- tragende Beine = alle außer den vordersten `lift_front_pairs` Laufbein-Paaren (hier 3+4 = die 4 hinteren Beine); ihre Füße bleiben per Fuß-IK exakt stehen
- vorderste Laufbeine heben mit ab und ziehen sich an (`front_legs_*`)
- Hinterleib wird gegengedreht (`abdomen_counter`), sonst sackt er Richtung Boden
- `rear_pitch_deg` wird automatisch so weit begrenzt, wie die tragenden Beine reichen (Bisektion)
- beim Zuschnappen fällt der Rumpf um `strike_pitch_drop` nach vorne (mehr Wucht)
Die Prüfung „Füße stehen“ gilt in diesem Clip nur für die tragenden Beine (`planted` im Clip, im Bericht `planted_legs`).

## Erkenntnisse aus der Validierung
- **Die Struktur trägt:** gleiches Skelett, zweites Muster mit eigener Mechanik, dieselbe Prüfkette. Gemeinsames liegt in `octopod_kit.py` (Ant wurde ohne Änderung der Ergebnisse darauf umgebaut).
- **Neue Bausteine im Baukasten:** Planar-IK (`ik_angles`), **Fuß-IK** (`set_foot`: Hüfte giert in Zielrichtung, Femur/Tibia stellen die Entfernung ein, Femur-Versatz exakt nachgeführt), Reichweiten-Grenzen (`ik_limits`, `max_foot_shift`), Körper heben mit stehenden Füßen.
- **Gefundene Fehler (behoben):**
  - Die Prüfung ließ „Stillstand“ durch → neue Prüfung `moves_ok` (Mindest-Schrittlänge)
  - Die IK-Ebene passte nicht zur Hebe-Achse
  - **Rig-Fehler:** Knie-Erkennung hatte bei L2 einen 6-%-Oberschenkel erzeugt → Knie jetzt zwischen 25–60 % der Beinlänge, Fuß max. 30 %
- **Lesbarkeit hängt am Modell:** Auf dem Ameisenkörper sind die „Scheren“ nur dünne Taster, und die langen, fast gestreckten Beine erlauben keine Körperhebung in der Drohhaltung. Für echte Krabben-Monster (z. B. Shore Crab, Reef Snapper?) ein Modell mit dicken Scheren und gebeugten Beinen generieren.
- Seitwärts-Clips laufen „in place“. In Unity bewegt sich die Krabbe quer zu ihrer Blickrichtung (`move_axis: y`).
