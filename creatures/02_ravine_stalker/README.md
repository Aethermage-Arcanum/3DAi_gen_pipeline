# Ravine Stalker (Mammals · Highlands) – quadruped/wolf

Erster Vierbeiner, Referenz für das Vierbeiner-Skelett. Erstellt 2026-11-17 im autonomen Lauf.

## Ablauf (reproduzierbar)
```
python scripts/tripo_run.py creatures/02_ravine_stalker --steps generate   # 110 Credits, schon erledigt (raw/)
python scripts/creature_pipeline.py creatures/02_ravine_stalker             # kostenlos: UV, Rig, Clips, Prüfung, GIFs, Export
```

## Kennzahlen
| | |
|---|---|
| Dreiecke | 4.258 (Tripo P-Serie, face_limit 4000) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² (Tripo lieferte 2048²) |
| Knochen | 30 (Standard-Vierbeiner inkl. Schulterblätter, Kiefer, 4 Schwanzglieder) |
| UV | Tripo-UV behalten: 113 Inseln, 61 % Abdeckung, 0 % Überlappung (Winkelverzerrung knapp über Grenze) |
| Clips | 9 (Walk 0,26 m/s, Run 0,90 m/s, Turn 32 °/s, Idle, Ready, Attack1, Hit, Death) – alle grün |
| Gelenk-Lücken | max. 1,1 cm (seit C15; vorher 1,05) |

Ausgabe: `output/RavineStalker.fbx` (Unity), `.glb`, `_events.json` (footstep/hit/dead). Vorschau: `rig/anim/*.gif`, Rig-Skizze `rig/rig_debug.png`, UV-Prüfblatt `uv/uv_preview.png`.

## Erkenntnisse
- Tripo-Beine fast gestreckt → automatische Rumpf-Absenkung (`reach_fix`), kürzere Schritte.
- UV-Naht-Duplikate brauchten identische Gewichte (sonst Risse bis 5 cm) – im Rig behoben, gilt für alle Vierbeiner.
- Schulterblätter mit IK-Steifigkeit verhindern Risse an der Schulter im Galopp.
- Details: `motions/quadruped/README.md`, `motions/quadruped/wolf/README.md`.

## C9-Test: Gelenk-Verdichtung (2026-11-20) – NICHT eingeschaltet, Entscheidung Nutzer
Testkreatur für den Baustein `rigging/joint_densify.py` (Beschreibung: `rigging/README.md` → „Gelenk-Verdichtung“).
Getestet an einer **Kopie** (`temp/c9_test/02_ravine_stalker/creature.toml`), weil der Wolf fertig ist und sich nicht
ändern darf: diese `creature.toml` hat KEINEN `[joint_densify]`-Abschnitt, der Wolf baut weiter exakt wie vorher.
Zum dauerhaften Einschalten diesen Abschnitt hier in die `creature.toml` übernehmen (danach Wolf neu bauen + abnehmen):
```toml
[joint_densify]
[[joint_densify.joint]]
bones = ["Leg_*_2", "Leg_*_3"]      # Ellbogen/Knie + Handgelenk/Sprunggelenk
```
| | ohne | mit Verdichtung |
|---|---|---|
| Dreiecke / Vertices | 4.258 / 3.208 | 5.058 / 3.682 (+800 Tris = +19 %) |
| Dehnung in den Gelenk-Ringen, Run (max · Kanten > 1,5 · > 2,0) | 2,05 · 18 · 2 | 1,78 · 12 · 0 |
| … Walk / Ready / TurnLeft (max) | 1,63 / 1,55 / 1,64 | 1,51 / 1,43 / 1,49 |
| Dehnung gesamt (Run 2,89 Flanke Hüfte, Attack1 2,27 Kopf) | unverändert | unverändert – Gewichts-Frage, nicht Gelenk |
| Gelenk-Lücken, Export, Gegentest FBX/GLB | 1,05 cm, ok | 1,05 cm, ok (alle Prüfungen grün) |

Prüfbilder (Render | Drahtgitter | Dehnung je Dreieck): `rig/c9_joint_densify/wolf_sprunggelenk_run8_vorher_nachher.png`,
`rig/c9_joint_densify/wolf_knie_run4_vorher_nachher.png`, Nahaufnahme über den ganzen Run-Clip:
`rig/c9_joint_densify/wolf_sprunggelenk_run_vorher_nachher.gif`. Kompletter Testbau (Roh-GIFs `rig/anim/raw/`, End-GIFs
`rig/anim/final/`, FBX/GLB `output/`): `temp/c9_wolf_test/` (nicht versioniert, mit dem Befehl oben reproduzierbar:
`python scripts/creature_pipeline.py temp/c9_test/02_ravine_stalker --work temp/c9_wolf_test`).
Bewertung: weniger und schwächer gedehnte Dreiecke direkt am Knie/Sprunggelenk; die Bewegung ist unverändert. Sichtbar
nur in der Nahaufnahme – aus der Spielkamera kaum. Hauptzweck des Bausteins ist der Frosch (lange Kanten, tiefe Hocke).

## C15: Dehnung an Bauch/Rücken aus der Spielkamera (2026-11-21) – eingeschaltet
Nutzer: Der C9-Test am Sprunggelenk ist aus der schrägen ARPG-Kamera kaum sichtbar; gemeldet war von Anfang an die
Dehnung an **Bauch/Rücken**. Gemessen wurde deshalb nur auf den aus der Spielkamera sichtbaren Flächen
(`rigging/joint_densify_review.py visible`, Erklärung `rigging/README.md` → „Gewichte nach Körperbereichen“).

**Schlimmste sichtbare Stellen vorher** (Kantenlänge/Ruhelänge, sichtbare Flächen):
| Stelle | Clip | max | Ursache (Fehlerklasse) |
|---|---|---|---|
| Bauchlinie/Flanke vor der Hüfte | Run F10 | 2,50 (24 Kanten > 1,5) | Schienbein Leg_B*_2 (13 %) und Oberschenkel (38 %) ziehen an der Flanke 13 cm vor der Hüfte → *fremder Körperbereich* + *schmaler Übergang Bein→Rumpf* |
| Bauchlinie | Walk F5 | 2,05 (12) | dito |
| Hals/Nacken | Ready F10 | 1,90 | Schulterblätter auf dem Nacken-Ansatz, Neck_1/Neck_2 hart gemischt → *fremder Bereich* + *Wirbelkette* |
| Maulwinkel | Attack1 F13 | 2,29 | Kiefer öffnet (Jaw 27 % neben Head 98 % auf 0,9 cm) – gewollte Bewegung, klein |
| Bug (Brust vor dem Oberarm) | Run F14 | 2,09 | Oberarm schwingt weit, Hals-Gewicht auf der Brust → *schmaler Übergang* |

**Fix** (`creature.toml [quadruped.rig]`, nur dieser Wolf; Bewegung unverändert – Knochen 0,0 mm / 0,0° in allen Clips):
`zone_lock = true` (Unterbein nicht über dem Knie, Bein/Schulterblatt nicht auf der Rückenlinie), `zone_leg_margin = 0.12`
(das Wolf-Knie sitzt tief; mit 0.03 entstand eine harte Kante direkt am Knie), `spine_chain_blend = 1.0`
(Wirbelkette Becken→Hals entlang der Kette weich verteilt). Kein Gelenk-Verdichten: Dreiecke unverändert **4.258**.

**Messwerte sichtbare Flächen, vorher → nachher** (max · Kanten > 1,5):
| Clip | Bauchlinie | Hals | Rücken | Schulter/Oberschenkel |
|---|---|---|---|---|
| Run | 2,50 · 24 → 1,93 · 22 | 1,83 · 12 → 1,76 · 9 | 1,43 → 1,43 | 2,09 · 24 → 2,13 · 20 |
| Walk | 2,05 · 12 → 1,69 · 9 | 1,48 → 1,45 | 1,26 → 1,27 | 1,61 · 8 → 1,63 · 3 |
| Ready | 1,75 · 6 → 1,40 · 0 | 1,90 · 2 → 1,23 · 0 | 1,13 → 1,18 | 1,48 · 0 → 1,60 · 1 |
| Attack1 | 1,85 · 8 → 1,56 · 2 | 1,49 → 1,41 | 1,17 → 1,17 | 1,54 · 2 → 1,58 · 4 |
| TurnLeft/Right | 1,69/1,70 → 1,34/1,35 | 1,31/1,26 → 1,28/1,24 | gleich | 1,48/1,49 → 1,52/1,53 |
Anteil je Regel: `zone_lock` allein Bauchlinie Run 2,50 → 1,91, Hals Ready 1,90 → 1,45; `spine_chain_blend` dazu Hals Ready → 1,23.

**Rest (nur noch iterativ):** Bauchlinie im Galopp ~1,9 – der Oberschenkel schwingt weit, die Haut vor der Hüfte muss
mit. Getestet und verworfen: breiterer Übergang Bein→Rumpf (Flanke wird 1,46 → 1,80) und Reichweiten-Grenze für den
Oberschenkel (Oberschenkel 2,09 → 3,00) – beide verschieben die Dehnung nur. Maulwinkel 2,29 (Kiefer) und Bug 2,1 unverändert.

Prüfbogen ARPG-Ansicht (Render | Drahtgitter | Dehnung): `review/c15_wolf_bauch_vorher_nachher.png`,
Dehnung über den ganzen Run: `review/c15_wolf_run_dehnung_vorher_nachher.gif`. Roh-GIFs `rig/anim/raw/`
(vorherige Fassung als Kopie in `temp/rd_before/02_ravine_stalker/anim/`, nicht versioniert).
Erneut messen: `& "D:\Blender\blender.exe" -b creatures/02_ravine_stalker/rig/clips.blend -P rigging/joint_densify_review.py -- visible temp/wolf_visible.json`
