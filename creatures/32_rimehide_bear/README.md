# Rimehide Bear (32) – nackte Basis für die Bären-Varianten

```
python scripts/tripo_run.py creatures/32_rimehide_bear --steps generate   # 110 Credits, erledigt (raw/, Task a042c11f)
python scripts/creature_pipeline.py creatures/32_rimehide_bear --stage motion   # Roh-GIFs → rig/anim/raw/
python scripts/creature_pipeline.py creatures/32_rimehide_bear                  # Endfassung, Export, Gegentest
```

## Stand (2026-11-21, Build-Agent)
- Tripo-Modell da, **Prüfung Teil B: freigegeben** (unten). UV: Tripo-UV. Rig: Vierbeiner-Standard mit C15-Regeln.
- Neues Muster `motions/quadruped/bear/` mit 10 Clips (Walk, Run, Idle, Ready, TurnLeft/Right, Attack1 Prankenhieb,
  Attack2 Aufrichten + Doppelpranken-Slam, Hit, Death = Platzhalter). Roh-GIFs `rig/anim/raw/`, Endfassung `rig/anim/final/`.
- **Wartet auf Abnahme der Bewegung durch den Nutzer.** Nicht committet.
- Varianten-Planung: `VARIANTEN.md` (BACKLOG Q8). Andock-Knochen für den Varianten-Baukasten: unten.

## Kennzahlen (Export `output/RimehideBear.fbx/.glb`, Gegentest beider Dateien ok)
| Kennzahl | Wert |
|---|---|
| Dreiecke | 3.944 (Tripo P-Serie, `face_limit` 4000; keine Gelenk-Verdichtung) |
| Vertices | 2.792 (3 Teile: Körper + 2 lose Fangzähne à 47) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM – Tripo 2048², im Export 1024² (FBX: Farbe + Normal; ORM nur in der GLB, wie bei allen Kreaturen) |
| Knochen | 30 (Vierbeiner-Standard, Unity „Generic“), max. 4 Einflüsse, 0 Vertices ohne Gewicht |
| Maße | 1,00 m lang, 0,74 m hoch, 0,64 m breit |
| UV | Tripo-UV, 72 Inseln, 59 % Abdeckung, 0 % Überlappung |
| Clips | 10, alle Selbstprüfungen grün; Gelenk-Lücken max. 1,4 cm (Grenze 1,5) |

## Prüfung Teil B (Tripo-Modell, Build-Agent 2026-11-21)
Bilder: `review/inspect_views.png` (ARPG, Seite, vorn, oben), `review/model_check.png` (Messung).
- **Messung** (`scripts/model_check.py`): keine Auffälligkeit. 4 Fuß-Gruppen am Boden, Fußabstand hinten/vorne 0,58×
  (erlaubt 0,5–1,4; Vorderbeine gewollt breiter, siehe Teil A), nichts hängt zwischen den Beinen, Mittellinie gerade
  (0,001× Länge), Symmetrie 100 %, Schwerpunkt über der Standfläche, 19 kleine Flächen mit freier Rückseite (Splitter).
- **Sichtprüfung:** Silhouette wie `design.png` (hoher Buckel über den Schultern, Rücken fällt nach hinten ab, Stummelschwanz,
  kleine runde Ohren, Säbel-Fangzähne aus dem Oberkiefer). Alle 4 Füße stehen am Boden, Beine frei (keine Hautbrücken,
  keine verschmolzenen Gliedmaßen), Krallen dunkel und sauber getrennt. Keine Löcher sichtbar. Textur neutral hellgrau,
  ohne Bildreste. Die Fangzähne sind 2 lose Teile (Rig: starr am Kopf). Das Mesh ist etwas weicher schattiert als das
  facettierte Referenzbild (Low-Poly bleibt, Flat Shading im Export).
- **Ergebnis: freigegeben für das Rig**, kein schwerer Mangel.

## UV-Prüfung (Schritt 2b)
`uv/uv_preview.png`, `uv/uv_report.json`. Tripo-UV: 72 Inseln, Abdeckung 59 %, Dichte-Ausreißer 6,8 %, Winkel 8,0°,
Nähte 22 % oben sichtbar; Buckel/Rücken liegen in großen zusammenhängenden Inseln (gut für spätere Material-Ebenen).
Smart UV: 556 Inseln, Abdeckung nur 38 % (unter der Grenze 45 %), Nahtlänge 2,5×. Fehlerwert mit Naht-Strafe Tripo 1,60
gegen Smart 1,89 → **Tripo-UV behalten**, kein Umbacken. Sichtprüfung mit Schachbrett + Wald/Abyss-Textur unauffällig.

## Rig (`rig/`, Einstellungen in `creature.toml [quadruped.*]`)
Vierbeiner-Standard-Rig mit den C15-Regeln von Anfang an (`zone_lock`, `spine_chain_blend`). Gefundene Rig-Fehler und
Behebung (alle am Rig/den Gewichten, keine Bewegung verkleinert):
| Befund | Ursache | Behebung |
|---|---|---|
| Wirbelsäule im Zickzack (Spine_1 auf Bauchhöhe, Hals mit Knick) | grobe Rücken-Facetten: im 3-cm-Querschnitt kaum Rücken-Vertices | neu `[detect] spine_slice = 0.06` (nur Wirbelsäule/Hals) |
| Pranken hingen an Neck_1/Chest (Dehnung bis 32× im Slam) | Vorderbeine schräg nach vorn, Pranken ~17 cm vor dem Schultergelenk → außerhalb der Bein-Reichweite | `leg_x_reach = 0.30`, `leg_capture = 0.16` |
| Buckel hing zu 58 % am Hals | Hals begann am Schultergelenk, Buckel sitzt darüber/davor | neu `chest_extend = 0.6` (Hals beginnt vor dem Buckel) |
| Kruppe hing zu 87 % an Tail_* | Schwanzansatz direkt hinter der Hüfte, der Stummel sitzt ganz hinten | `tail_base = 0.6` → Kruppe 93 % Hips |
| Fangzähne würden am Unterkiefer hängen | lose Teile wählen den nächsten Knochen (Jaw) | `rigid_parts = true`, neu `rigid_parts_exclude = ["Jaw"]` → 100 % Head |
| Erhobene Pranken (Attack2) knickten ~110° ab, Lücke 1,7 cm | Pranke hielt die Waagerechte, Unterarm stand hoch | Pranke dreht mit dem Unterarm, hängt 45° im Handgelenk (Clip-Code) |

Die neuen Rig-Werte sind optional (Standard = altes Verhalten); `regression.py --deep` gegen `temp/br_base`:
Ravine Stalker (Wolf), Hollow Stag (Hirsch), Reef Snapper (Echse) **identisch**.

## Dehnung aus der Spielkamera (`rigging/joint_densify_review.py visible`, sichtbare Flächen, max. Kantendehnung)
| Clip | Rücken/Buckel | Flanke | Hals/Nacken | Schulter/Oberschenkel | Kopf |
|---|---|---|---|---|---|
| Walk | 1,11 | 1,48 | 1,27 | 1,59 | 1,14 |
| Run | 1,24 | 1,66 | 1,46 | 1,71 | 1,07 |
| TurnLeft | 1,22 | 1,44 | 1,58 | 1,45 | 1,20 |
| TurnRight | 1,22 | 1,37 | 1,59 | 1,47 | 1,23 |
| Idle | 1,03 | 1,03 | 1,43 | 1,13 | 1,22 |
| Ready | 1,05 | 1,09 | 1,39 | 1,47 | 2,63 |
| Attack1 | 1,23 | 1,44 | 1,36 | 1,72 | 2,32 |
| Attack2 | 1,38 | 1,49 | 1,27 | 1,61 | 2,75 |
| Hit | 1,03 | 1,06 | 1,37 | 1,49 | 1,46 |

Lesart: 1,0 = unverändert, ≥ 1,5 gelb, ≥ 2,0 rot. **Buckel, Rücken und Nacken bleiben überall ≤ 1,38 bzw. ≤ 1,59**
(Prüfbogen `review/dehnung_arpg.png`: Aufrichten, Slam, Ausholen, Galopp, Drohen – Rücken/Buckel grau).
Restliche Stellen (nur Info, Bewegung nicht verkleinert):
- **Kopf 2,3–2,8** = Maulwinkel beim Brüllen/Kiefer auf (6-mm-Kanten Ober-/Unterlippe, Head/Jaw-Übergang) – kaum sichtbar.
- **Flanke 1,66** (Run) und Schulter/Ellbogen 1,7 (Run, Attack1): Übergang Oberarm ↔ Rumpf beim weiten Ausgreifen.
- **Bauch/Leiste beim Aufrichten** (Attack2 oben, orange im Prüfbogen): Oberschenkel ↔ Bauch, Rumpf steht 66° zum Bein.
- **Krallen/Handgelenk** (Unterbein bis 2,7, rot im Prüfbogen): Krallen hängen gemischt an Leg_2/3/4, das kurze Handgelenk
  (4 cm) knickt beim Anheben der Pranke. Nur aus der Nähe sichtbar.
- Bauch-Unterseite (aus der Spielkamera unsichtbar) bis 2,4 im Prankenhieb: linke/rechte Beine ziehen gemeinsam an der
  Bauchmitte – Kandidat für `exclusive_leg_pairs` (nicht getestet).

## Andock-Knochen für Accessoires (Vorarbeit Varianten-Baukasten)
Accessoires hängen **starr am Knochen, dessen Haut sie bedecken** (Anteil = Gewicht der Haut an dieser Stelle, gemessen).
| Körperstelle | Knochen | Haut-Gewicht (Ruhe) | Hinweis |
|---|---|---|---|
| Buckel (Gipfel, hinterer Teil) | `Chest` | Chest 67 %, Neck_1 21 % | Eisplatten/Basaltplatten/Felszacken; Buckel-Vorderhang folgt dem Hals (Neck_1 62 %) |
| Rücken Mitte | `Spine_1` (vorn) / `Hips` (hinten) | Hips 84 %, Spine_1 14 % | Rücken-Kamm, Moospolster |
| Kruppe | `Hips` | Hips 93 % | Platten hinten, Pilze |
| Nacken | `Neck_1` / `Neck_2` | Neck_2 44 %, Neck_1 42 % | Mähne/Stachelmähne (Lurker) |
| Kopf (Stirn, Schädel) | `Head` | Head 66 %, Neck_2 34 % | Eiszacken-Krone (Elder), Hörner |
| Kiefer | `Jaw` | – | Hauer (Stone Boar, Shore Lurker) |
| Schultern (außen) | `Shoulder_FL/FR` + `Leg_F*_1` | Leg_FL_1 49 %, Shoulder_FL 34 % | Schulterdornen, Schulterplatten |
| Oberarm | `Leg_FL_1` / `Leg_FR_1` | – | – |
| Unterarme | `Leg_FL_2` / `Leg_FR_2` | Leg_FL_2 59 % | Unterarm-Eisplatten (Rimehide) |
| Oberschenkel | `Leg_BL_1` / `Leg_BR_1` | Leg_BL_1 74 % | Platten, Moos |
| Schwanzstummel | `Tail_1`…`Tail_4` | – | – |

**Wichtig für den Baukasten (gemessen):** Die Haut weicht in den Clips von einer starren Bewegung des Knochens ab –
Stirn bis 2,2 cm (TurnLeft), Buckel-Gipfel 2,6 cm (Ready), Kruppe 4,2 cm (Attack2), Unterarm 5,0 cm (Run),
Oberschenkel 4,6 cm (Attack1). Ein **starr** angehängtes Accessoire schwebt/sinkt an diesen Stellen um so viel.
Empfehlung (Entscheidung Nutzer): Accessoires mit etwas Einbettung (1–3 cm in die Haut) bauen **oder** sie die
Gewichte der Haut darunter übernehmen lassen (mitskinnen statt starr) – vor allem an Gelenken (Unterarm, Oberschenkel).

Knochenlage (Ruhe, Meter, Kopf +X, Boden z = −0,369): siehe `rig/rig_debug.json`; Skizze `rig/rig_debug.png`.
**Statur-Regler:** Knochen skalieren nur zusammen mit neu gebackenen Clips oder uniform – siehe
`motions/quadruped/bear/README.md` „Statur ±20 %“.

## Bewegung
Muster `quadruped/bear` (Naturreferenzen, abgeleitete Werte, Drehrichtung, Statur): `motions/quadruped/bear/README.md`.
Roh-GIFs: `rig/anim/raw/`, Endfassung: `rig/anim/final/` (identisch, weil nichts nachträglich bereinigt wurde).
Messwerte: `rig/clips_report.json` (Fußkontakt, Drehrichtung `turn_check`, Neigung der Angriffe).

## Herkunft der Bilder
ChatGPT, vom Nutzer erstellt am 2026-11-20 („nackte“ Basis: facettiert, neutrale glatte Haut, ohne Eis/Fell). Originale bleiben in `input/` liegen, Kopien unter den Pipeline-Namen:

| Pipeline-Datei | Original | Inhalt |
|---|---|---|
| `design.png` | `Facettierter Eisbär mit Reißzähnen.png` | Design-Bild, 3/4-Ansicht |
| `front.png` | `Frontale Rimehide-Bär-Statue-1.png` | vorn |
| `left.png` | `Facettierter Rimehide-Bär im Seitenprofil-2.png` | Kopf im Bild **links** = eigene linke Körperseite |
| `right.png` | `Facettenbär im Seitenprofil-3.png` | Kopf im Bild **rechts** = eigene rechte Körperseite |
| `back.png` | `Facettierter Eisbär von hinten-4.png` | hinten |

Konvention left/right: `scripts/make_prompts.py` („left“ = its own left side, head to the LEFT image edge), so auch bei `14_cinder_wyvern/input/left.png`.
`input/Varianten/` = Varianten-Bilder des Nutzers, gehen nicht an Tripo.

## Prüfung Teil A (Referenzbilder, Claude 2026-11-21)
1. Reihenfolge/Blickrichtung ok (vorn, Kopf links, Kopf rechts, hinten), Kamera auf Augenhöhe. Die Seitenansichten sind leicht schräg (fernes Beinpaar sichtbar), kein Problem.
2. Haltung in allen vier Ansichten gleich: waagerechter Rücken mit Buckel, Kopf leicht gesenkt.
3. Nichts zwischen den Beinen: Stummelschwanz frei am Hinterteil.
4. Beine gerade nach unten, nicht gespreizt. Vorderbeine stehen **breiter als die Hinterbeine** (umgekehrt zum Hollow-Stag-Fehler) – gewollt, passt zum massigen Bären. Bei der Modellprüfung (Teil B, Fußabstand hinten/vorne) als bekannt werten.
5. Gliedmaßen frei, keine Berührungen untereinander.
6. Neutrale Pose, Maul zu. Kleine Säbel-Fangzähne ragen aus dem Oberkiefer (ins Mesh eingebaut, gewollt).
7. Teilezahl stimmt: 4 Beine, 1 Schwanz, 2 Ohren – in allen Ansichten und wie in `design.png`. Kleinigkeit: Krallenzahl schwankt (vorn 4, Seitenansicht 3) – egal für Tripo/Spielkamera.
8. Keine dünnen Teile (Flügel/Flossen).
9. Kein Glühen, neutraler grauer Hintergrund, keine Schrift.

**Ergebnis: freigegeben**, kein Grund, Bilder neu zu machen.

## Tripo-Einstellungen (Dry-Run 2026-11-21)
multiview-to-model, P-Serie `P2-20260801`, `face_limit` 4000, texture + PBR (`v3.5-20260815`, standard), delight, keine Quads. Nur Schritt `generate` (Tripo-Rig/Animation werden nicht genutzt).
