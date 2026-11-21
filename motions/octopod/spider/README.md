# Bewegungsmuster octopod/spider

**Eigenes Muster** (nicht Variante von Ant oder Crab): Vorwärtsgang als alternierender Vierfuß, Vorderkörper führt,
Hinterleib samt Aufsatz zieht verzögert nach, Angriffe aus dem ganzen Körper (Ausfall mit Beinkäfig, Sprungbiss).
Grundlage, Quellen und Begründungen: **[RESEARCH.md](RESEARCH.md)**. Werte: [style.toml](style.toml). Generator:
[spider_clips.py](spider_clips.py) (nutzt `../octopod_kit.py` für Fuß-IK, Backen und Prüfungen; Kippen ums tragende
Paar ist aus crab kopiert, nicht importiert). Erste Kreatur: `creatures/10_broodling/`.

```
python scripts/creature_pipeline.py creatures/10_broodling --stage motion   # Roh-GIFs → rig/anim/raw/
python scripts/creature_pipeline.py creatures/10_broodling --stage full     # Export + Gegentest
```

## Entscheidungen des Nutzers (2026-11-21)
1. Das vordere Beinpaar **läuft im Gang mit und setzt kurz auf** (Duty 0,35 statt 0,6, schwebt höher) – kein reines Tastbein.
   *Befund beim Bau:* Im Broodling-Modell schwebt nicht das vordere, sondern das **3. Paar** am meisten (2,4 cm = 3,4 % der
   Höhe); Paar 1 steht 0,9 cm, Paar 4 1,2 cm über dem Boden. Alle Clips setzen Standfüße auf den Boden (`feet_to_ground`).
2. **Attack2 = Sprungbiss** (Springspinne) mit Root Motion. Attack1 = Vorstoß mit Käfig der Vorderbeine und Biss nach unten.
3. **Lebhaftes Tempo:** Walk 1,36 Hz (statt 0,7 Hz einer Vogelspinne).

## Clips (Broodling, Größe 1,0 m)
| Clip | Dauer | Inhalt | Messwerte |
|---|---|---|---|
| Octopod_Spider_Walk | 0,73 s Loop | Gruppen L1-R2-L3-R4 / R1-L2-R3-L4 im Gegentakt, Welle hinten → vorn (+0,04 Zyklus je Paar), Bein I tippt kurz | alle Standfüße 0,0 mm über Boden, 0,41 m/s (0,41 Größen/s) |
| Octopod_Spider_Run | 0,37 s Loop | 2,7 Hz, Schritt ×1,45, Körper 13 % tiefer, Beine weiter gespreizt, Hinterleib pendelt stärker | 0,0 mm, 1,35 m/s |
| Octopod_Spider_TurnLeft / TurnRight | 0,67 s Loop | auf der Stelle; Standfüße wandern tangential um die Körpermitte (Außenbeine treten vor, Innenbeine zurück), Vorderkörper 4° voraus, Hinterleib 5° hinterher | 0,0 mm; Vorzeichen geprüft: Left +78 °/s (gegen Uhrzeigersinn von oben), Right −78 °/s |
| Octopod_Spider_Idle | 2,5 s Loop | lauern: Bein I tastet/tippt (erst links, dann rechts), R3 wird einmal nachgesetzt, Hinterleib „atmet“ | übrige Füße 0,0 mm bewegt |
| Octopod_Spider_Ready | 1,2 s Loop | Drohen: 34° aufgebäumt um die Hüftlinie von Bein III, I+II hoch und weit seitlich gespreizt, Zittern, Hinterleib gegengedreht | III/IV stehen exakt (0,0 mm) |
| Octopod_Spider_Attack1 | 0,87 s | ausholen (24° hoch + zurück) → Zustoß in 3 Frames 0,16 × Größe nach vorn-unten (−10°), I+II schließen sich als Käfig vor dem Kopf → halten + schütteln → zurück; Event `hit` Frame 12 | III/IV 0,0 mm, kehrt in Ruhe zurück |
| Octopod_Spider_Attack2 | 1,1 s | Hocke (Körper 22 % tiefer) → flacher Satz, I+II vorn-oben, III/IV nach hinten gestreckt → Landung auf I/II, Biss nach unten → Ruhe. **Root Motion:** Knochen `Root` endet 1,59 m (1,6 Größen) weiter vorn. Events `takeoff` (12), `hit` + `land` (21), `root_motion` (33, `distance_m`) | Endpose = Ruhe, alle Füße am Boden |
| Octopod_Spider_Hit | 0,33 s | Körper sackt + kippt vorn, Vorderbeine zucken schützend an, Hinterleib ruckt verzögert nach | II–IV 0,0 mm, kehrt zurück |
| Octopod_Spider_Death | 1,2 s | **Platzhalter** aus dem Baukasten (Death gesperrt, Nutzer 2026-11-17) | – |

Hinweis Baukasten-Bericht: `move_speed_mps` / `turn_speed_deg_s` in `clips_report.json` rechnen mit EINEM Duty-Wert für alle
Beine und liegen wegen Bein I (kürzerer Duty) zu tief. Genau: `rig/spider_checks.json` (aus den Standfüßen gemessen).

**Root Motion in Unity (Attack2):** Generic-Rig, Root node = `Root`, „Apply Root Motion“ an – oder per Code um
`distance_m` aus dem Event `root_motion` versetzen. Die Standard-Vorschau (`render_anim.py`, feste Kamera, vgl. G12a)
schneidet die Landung ab; zusätzlich gibt es `rig/anim/raw/Octopod_Spider_Attack2_wide.gif` mit weiter Kamera.

## Ganzkörper
- **Vorderkörper** (Thorax + Kopf, starr wie Chitin) giert im Takt (±2,5°, Run ±3°) um die Mitte der Beinwurzeln.
- **Hinterleib + Eierhaufen** hängen starr an `Abdomen_1` (Drehpunkt = Stiel) und folgen mit 12–15 % Zyklus Verzögerung und
  größerem Ausschlag (3,5°/5°) → Follow-Through. Beim Drehen hängt er 5° hinterher, beim Aufbäumen dreht er gegen.
- Standfüße werden per Fuß-IK **durch den bewegten Körper hindurch** auf Welt-Ziele gesetzt (`plant`), Schwebebeine im Körper-Raum.

## Dehnung (nur sichtbare Flächen, `rigging/joint_densify_review.py visible`, alle Clips, jeder Frame)
| Bereich | max | Bemerkung |
|---|---|---|
| Hinterleib oben (Eierhaufen) | **1,00** | starr |
| Rücken Vorderkörper | 1,09–1,46 (Turn) | keine Kante > 1,5 außer im gesperrten Death (1,89) |
| Flanke / Kopf | ≤ 1,40 / 1,00 | |
| Unterbein | ≤ 1,41 | |
| Bein-Ansatz Coxa/Femur | 1,56–2,64 | 2–14 Kanten > 1,5, am Gelenk Coxa↔Femur von Bein III/IV, das unter dem überhängenden Eierhaufen liegt (von oben kaum sichtbar). Max 2,64 im Attack1-Zustoß. |

Vor den Rig-Korrekturen lag die sichtbare Dehnung bei bis zu 6,7 (Bein-IV-Knie an den Eierhaufen gewichtet, Kniehaut der
Vorderbeine an Kopf/Rumpf gezogen) – behoben über die Erkennung (Wand-Dicke) und die Gewichte, nicht über kleinere Bewegung.

## Naturreferenzen (Videos, aus RESEARCH.md; vom Bau-Agenten nicht ansehbar → bitte vom Nutzer gegenprüfen)
- Laufen, Zeitlupe: [Spider running in slow motion (1000 fps)](https://www.youtube.com/watch?v=7CxOPakRsSU)
- Drohen: [Tarantula attack & threat pose](https://www.youtube.com/watch?v=6yoK5OB-Nyg) · [Tarantula Threat Posture](https://www.youtube.com/watch?v=XZ4H7vjFf-E)
- Beuteangriff: [Tarantulas: speed attack (slow motion)](https://www.youtube.com/watch?v=jn2Cfow4nwE) · [Wolf Spider Attacks Fly](https://www.youtube.com/watch?v=6kW31h1wNUw)
- Sprung: [Jumping spider „Kim“, Univ. Manchester](https://www.youtube.com/watch?v=C6PAClh1IZo)
- Wenden: [Flattie spider – world's fastest spin](https://www.youtube.com/watch?v=HKRL6Y7Oyvw)
