# Bewegungsmuster crawler/crab

**Eigenes Muster** (nicht nur Variablen von Ant): Seitwärtsgang mit Fuß-IK, eigene Schrittfolge, Scheren erhoben, Angriffe aus den Scheren.

Generator: `crab_clips.py` (nutzt `../crawler_kit.py`). Test auf einem Modell mit anderem eigenem Muster:
```
python scripts/crawler_pipeline.py creatures/<name> --style crawler/crab
```
→ Ausgabe in `creatures/<name>/style_tests/crab/`

## Clips (Validierung 2026-11-17 auf dem Chitin Crawler, also einem Ameisenkörper!)
| Clip | Dauer | Inhalt | Prüfung |
|---|---|---|---|
| Crawler_Crab_Walk / WalkLeft | 0,8 s | seitwärts (rechts/links), führende Seite 2-4-3, nachziehende 2-3-4 | Bodenkontakt **0,0 mm**, Schritt 8,7–9,4 cm, 0,19 m/s seitwärts |
| Crawler_Crab_Run | 0,47 s | schneller seitwärts | Bodenkontakt 0,0 mm, 0,41 m/s |
| Crawler_Crab_TurnLeft/Right | 0,73 s | auf der Stelle drehen | 26 °/s |
| Crawler_Crab_Idle | 2,0 s | Scheren abwechselnd zum Mund (fressen), Fühler zucken | Füße stehen |
| Crawler_Crab_Ready | 1,0 s | Drohhaltung: Scheren hoch + gespreizt, Zittern | Füße stehen |
| Crawler_Crab_Attack1 | 0,73 s | aus der Drohhaltung ausholen → Zuschnappen in 2 Frames → halten → zurück, Event `hit` | Füße stehen |
| Crawler_Crab_Hit | 0,3 s | Körper sackt kurz, Scheren schützend nach innen | kehrt zur Ruhe zurück |
| Crawler_Crab_Death | 1,2 s | gemeinsamer Tod aus dem Baukasten (auf den Rücken) | kein Teil im Boden |

Alle 10 Clips grün, Gelenk-Lücken max. 0,8 cm.

## Naturreferenzen
- **Seitwärtsgang / Schrittfolge:** Winkerkrabbe *Uca pugnax*, im Mittel ≈ alternierender Vierfuß. Führende Seite 2-4-3-5, nachziehende 2-5-3-4, Scheren (Bein 1) vom Boden gehalten. [Barnes 1975, J Comp Physiol](https://link.springer.com/article/10.1007/BF00612697)
- **Drohhaltung:** hoch auf den Beinen, Scheren erhoben und gespreizt („meral spread“), das Drohen kommt meist vor dem Angriff. [Uni Bristol: Defensive behaviour in intertidal crabs](https://research-information.bris.ac.uk/en/publications/defensive-behaviour-in-intertidal-crabs/) · [Nautilus: The wild world of threats](https://nautil.us/the-wild-world-of-threats-238413)
- **Schlag:** schnelles Beugen der Scheren in 30–60 ms, nur aus der Drohhaltung. [Royal Holloway Thesis](https://repository.royalholloway.ac.uk/items/4e9e8c37-19ce-4967-8dbd-a16025e0fc5b/1/)

## Erkenntnisse aus der Validierung
- **Die Struktur trägt:** gleiches Skelett, zweites Muster mit eigener Mechanik, dieselbe Prüfkette. Gemeinsames liegt in `crawler_kit.py` (Ant wurde ohne Änderung der Ergebnisse darauf umgebaut).
- **Neue Bausteine im Baukasten:** Planar-IK (`ik_angles`), **Fuß-IK** (`set_foot`: Hüfte giert in Zielrichtung, Femur/Tibia stellen die Entfernung ein, Femur-Versatz exakt nachgeführt), Reichweiten-Grenzen (`ik_limits`, `max_foot_shift`), Körper heben mit stehenden Füßen.
- **Gefundene Fehler (behoben):**
  - Die Prüfung ließ „Stillstand“ durch → neue Prüfung `moves_ok` (Mindest-Schrittlänge)
  - Die IK-Ebene passte nicht zur Hebe-Achse
  - **Rig-Fehler:** Knie-Erkennung hatte bei L2 einen 6-%-Oberschenkel erzeugt → Knie jetzt zwischen 25–60 % der Beinlänge, Fuß max. 30 %
- **Lesbarkeit hängt am Modell:** Auf dem Ameisenkörper sind die „Scheren“ nur dünne Taster, und die langen, fast gestreckten Beine erlauben keine Körperhebung in der Drohhaltung. Für echte Krabben-Monster (z. B. Shore Crab, Reef Snapper?) ein Modell mit dicken Scheren und gebeugten Beinen generieren.
- Seitwärts-Clips laufen „in place“. In Unity bewegt sich die Krabbe quer zu ihrer Blickrichtung (`move_axis: y`).
