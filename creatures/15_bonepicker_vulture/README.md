# Bonepicker Vulture (Schwarm · Gras/Steppe) – winged/bird

Zerzauster Steppengeier mit kahlem rotem Hals, Knochenschnabel und Knochenkamm auf den Flügeln. Zweite Kreatur des
Skeletts **`winged`** (2026-11-20), Muster **bird**. Design ohne Concept Art (Roster-Erweiterung, Design-Bild vom
Nutzer geprüft).

```
python scripts/tripo_run.py creatures/15_bonepicker_vulture --steps generate        # erledigt (raw/), Credits bezahlt
python scripts/creature_pipeline.py creatures/15_bonepicker_vulture --stage motion  # Roh-GIFs rig/anim/raw/
python scripts/creature_pipeline.py creatures/15_bonepicker_vulture                 # Export + Gegentest
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 4.552 (Tripo 4.124 + 428 für doppelseitige Federn) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² (ORM nur im GLB) |
| Knochen | 36 (Skelett `winged`, keine Platzhalter) |
| UV | Tripo-UV (977 Inseln, 69 % Abdeckung, 1,3 % Überlappung) |
| Frei hängend | Halskrause + Brust-/Bauchfedern über `[dangling]` (Shader, `output/BonepickerVulture_dangling.json`) |
| Clips | 14: Walk, Run (Hüpfen), Idle, Ready, TurnLeft/Right, Attack1 Hacken, Attack2 Sprung-Krallenhieb, Hit, Death (Platzhalter), Fly, Glide, TakeOff, Land |
| Prüfung | `--stage full`: ✓ ALLES OK (Fußkontakt, Schleifen, Drehrichtung, Gegentest FBX+GLB, Lücken 0,0 cm) |
| Dehnung (Info) | Idle 3,4 · Gehen 6,5 · Hüpfen 8,0 · Drehen 8,5 (Übergang Hinterzehe ↔ Lauf, weil die Hinterzehe flach am Boden bleibt) · Fly 5,8 |

## Modellprüfung (vor dem Rig, Sichtprüfung B 2026-11-20)
- Bilder: `review/model_check.png`, `review/inspect_views.png` (ARPG, Seite, vorn, oben).
- Symmetrisch, S-Hals mit Knochenkamm, zwei Vogelbeine mit je 3 Vorderzehen + Hinterzehe fest am Boden.
- Flügel halb offen hängend, Knochen-Bugkante mit Dornen, Federn hängen darunter; beide Flügel gleich gestellt.
- Federspitzen und Halskrause sind einseitige Platten (6 Bereiche, 332 Flächen) → `[winged.double_sided]`.
- Lose Teile: Brustknochen-Platte (332 V.) und Halsknochen vorn (135 V.) → hängen je Vertex am nächsten Haupt-Vertex.
- Schwerpunkt vor den Füßen (vorgebeugt mit S-Hals) = gewollt, mit Begründung freigegeben. Keine verschmolzenen
  Gliedmaßen, keine Hautbrücken. ✅ Freigabe für das Rig.

## Rig (winged, 36 Knochen)
- Gelenke aus der Geometrie: Schritt 0,37 H, Brust 0,59 H, Kopf 0,13 m, Schwanz-Fächer 0,26 m, Spannweite 0,96 m.
- Flügel-Ruheform: Bugkante steigt steil zum Handgelenk (höchster Punkt), Handschwingen hängen nach außen-unten.
  Die Clips drehen den ganzen Flügel absolut (beide Seiten gleich), die Gelenkwinkel bleiben wie modelliert.
- Unterschnabel = `Jaw` (untere Schnabelhälfte vor dem Gelenk), Knochenkamm starr am Kopf.
- Hinterzehe starr am `Toe` (folgt dem Boden).
- `[dangling]`: Halskrause + Brust-/Bauchfedern schwingen im Unity-Shader nach (`rig/dangling_preview.png`).

## Bewegung (Muster bird)
Naturreferenzen und Clip-Liste: [motions/winged/bird/README.md](../../motions/winged/bird/README.md).
Watscheln mit Kopfnicken, Hüpf-Lauf, Hacken mit gestrecktem Hals, Sprung-Krallenhieb, Ruderflug, Thermik-Segeln,
Abheben/Landen. Death = Platzhalter.

## Prüfbilder
- `rig/winged_rig.png`: Skelett vorn/seitlich/oben + Gewichte, `rig/dangling_preview.png`. `review/model_check.png`,
  `review/inspect_views.png`.
- Roh-GIFs (ARPG + Seite): `rig/anim/raw/Winged_Bird_*.gif` – zentral: Walk, Run, Fly, Attack1, Attack2, TurnLeft.
- End-GIFs nicht separat gerendert (`--no-preview`): nach der Roh-Fassung wurde nichts bereinigt, sie sind identisch.

## Offen
- Bewegung vom Nutzer abnehmen (Roh-GIFs).
- Zehen-Dehnung bis 8× im Hüpfen/Drehen: Hinterzehe hängt starr am Boden-Ziel (sonst steckt sie 3 cm im Boden).
  Bessere Lösung wäre ein eigenes Abrollen der Hinterzehe im Gang (kommt mit dem nächsten Vogel-Muster).
- Death = Platzhalter (Nutzerregel; Death-Dehnung 12,6 an den Zehen ist Folge des Platzhalters).
