# Needle Wasp (Insects · Wald) – flyer/wasp

Erstellt 2026-11-17 im autonomen Lauf (zweiter Bilder-Anlauf mit Nutzer-Concept + Stalk-Wasp-Stilvorlage).

```
python scripts/tripo_run.py creatures/needle_wasp --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/needle_wasp             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 4.296 (Tripo 4.172 + 124 Flügel-Rückseiten, siehe unten) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 51: Root + Core + 13 Ketten (6 Flügelstücke, 4 Beine, 2 Fühler, Hinterleib mit 5 Gliedern) |
| UV | Tripo-UV |
| Clips | 9, alle grün (Dehnung ≤ 1,28; im Flug jeder Mesh-Punkt ≥ 3 cm über dem Boden, Tod liegt am Boden) |

## Flügel doppelseitig (2026-11-17, Nutzer-Meldung aus Unity)
**Problem:** In Unity waren die Flügel aus manchen Winkeln (z. B. schräg von oben = ARPG-Kamera) unsichtbar oder halb weg,
ihr Schatten aber immer da. **Ursache (gemessen):** Tripo baut die Flügel als offene Platten aus einer einzigen Lage
Dreiecke. Von allen 4.172 Flächen haben genau 124 eine „freie Rückseite“ (Strahl nach hinten trifft nichts) – das sind
die 6 Flügelstücke (je 15–17 Flächen, 100 %) plus 26 Flächen an den Flügelansätzen; der Körper ist geschlossen.
Jede Engine zeichnet Standard-Materialien nur von vorn (Backface Culling) → Flügel von hinten unsichtbar.

**Lösung (in der Pipeline, kein Handgriff):** `rigging/double_sided.py`, aufgerufen vom Flieger-Rig nach dem Gewichten:
diese Flächen werden kopiert, umgedreht und 1 mm nach hinten versetzt; die Kopien erben Gewichte und UVs (UV-Naht-Duplikate
bekommen denselben Versatz → keine Risse). Ergebnis: 0 einseitige Flächen in FBX und GLB, weiter **1 Material, Standard-Shader**,
+124 Dreiecke (+3 %). Animation unverändert (alle Knochen identisch; nur im Tod liegt die Wespe 0,8 mm anders, weil die
Flügel-Rückseite jetzt den Boden berührt). Schalter: `[double_sided]` in `rigging/flyer_defaults.toml`, pro Kreatur
`[flyer.double_sided] enabled = false`.
Vorher/Nachher in Unity: `temp/wings_before_after.png` (Prüfbilder `arpg`, `arpg_rest`, `top`, `side`, `back`).

**Wie machen das andere Spiele?** Üblich sind zwei Wege: (1) nur die dünnen Teile mit umgedrehten Normalen doppeln –
funktioniert mit jedem Standard-Shader, Licht und Schatten stimmen, kostet nur ein paar Dreiecke; oder (2) ein eigenes
Flügel-Material mit „Cull Off“ (oft zusammen mit Alpha-Cutout/Transparenz für durchscheinende Adern) – spart Geometrie,
braucht aber ein zweites Material/Shader und beleuchtet die Rückseite ohne „Two-Sided Lighting“ falsch. Wir nehmen (1),
weil es engine-unabhängig mit einem Material bleibt; durchscheinende/flirrende Flügel wären später ein Shader-Thema
(„Fake it“), nicht ein Geometrie-Thema.

Hinweis: Die Tripo-Flügel stehen in Ruhe steil nach oben (V-Form). Von oben und schräg von vorn sieht man sie deshalb
teils fast von der Kante – das ist die Form, nicht mehr das Culling.

## Bodenabstand (2026-11-17, Meldung „sinkt in Unity 3,7 cm in den Boden“)
**Ursache:** keine Animation, sondern die Bodenreferenz im Unity-Viewer. Er stellte die Pose auf den Boden, die Unity nach
dem Laden zeigt = erster Take im FBX (Attack1, Frame 0) – bei der Wespe schon die Schwebehöhe (+17,6 cm über der
Tripo-Ruhepose). Walk fliegt 13,9–18,5 cm über der Ruhepose-Unterkante, also −3,7…+0,9 cm relativ zur Schwebepose.
Fix: Viewer misst die Bindepose (`CreatureViewer.RestLowestPoint`), wie die Pipeline in Blender. Laufende Kreaturen
unverändert (beide Posen gleich).
**Zweiter Fund:** In Ready (jeder Frame), Attack1 (Ausholen) und Hit lag der Stachel genau auf dem Boden (0,0 cm).
Jetzt `[hover] min_clearance = 0.03` → ≥ 3 cm (Unity, 240 Stichproben auch zwischen Frames: Attack1 ≥ 2,3, Hit ≥ 1,7 cm).
Nur diese drei Clips sind um genau 3 cm angehoben, alles andere Frame für Frame identisch (Regression). Death unverändert.
Vorher/Nachher: `temp/review/wasp_ground.png`. Naturreferenzen: `motions/flyer/wasp/README.md`.
