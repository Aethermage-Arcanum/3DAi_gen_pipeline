# Cinder Wyvern (Elite · Vulkan) – winged/drake

Schwerer Vulkan-Wyvern mit Flügel-Armen, Basaltschuppen und Felskeule am Schwanz; landet zum Kämpfen. Erste Kreatur des
Skeletts **`winged`** (2026-11-20), Muster **drake**. Design ohne Concept Art (Roster-Erweiterung, Design-Bild vom
Nutzer geprüft).

```
python scripts/tripo_run.py creatures/14_cinder_wyvern --steps generate        # erledigt (raw/), Credits bezahlt
python scripts/creature_pipeline.py creatures/14_cinder_wyvern --stage motion  # Roh-GIFs rig/anim/raw/
python scripts/creature_pipeline.py creatures/14_cinder_wyvern                 # Export + Gegentest
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 4.303 (Tripo 4.212 + 91 für doppelseitige Flughaut) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² (ORM nur im GLB) |
| Knochen | 36 (Skelett `winged`, keine Platzhalter) |
| UV | Tripo-UV (1.240 Inseln, 60 % Abdeckung, 0,2 % Überlappung) |
| Clips | 14: Walk, Run, Idle, Ready, TurnLeft/Right, Attack1 Biss-Ausfall, Attack2 Schwanzkeule, Hit, Death (Platzhalter), Fly, Glide, TakeOff, Land |
| Prüfung | `--stage full`: ✓ ALLES OK (Fußkontakt, Schleifen, Drehrichtung, Gegentest FBX+GLB, Lücken 0,0 cm) |
| Dehnung (Info) | Gehen 4,0 · Idle 3,3 · Fly 5,6 · Biss 6,7 (Schulter/Flughaut-Ansatz, Rumpf) |

## Modellprüfung (vor dem Rig, Sichtprüfung B 2026-11-20)
- Bilder: `review/model_check.png`, `review/inspect_views.png` (ARPG, Seite, vorn, oben).
- Zwei kräftige Hinterbeine mit Krallen, keine Vorderbeine, Flügel-Arme mit Kralle am Handgelenk, Hörner, Rückenplatten,
  Schwanz mit Stachelkeule – passt zu Design-Bild und Ansichten.
- **Flügel ungleich gestellt:** links steil hochgestellt und weit nach hinten gefegt, rechts seitlich. **Schwanz seitlich
  gebogen** – schon im Referenzbild (Frontansicht zeigt den Schwanz seitlich). Beides ist kein Grund für einen neuen
  Tripo-Lauf: Rig + Clips geben Flügel und Schwanz absolut vor (gleiche Gelenkwinkel links/rechts, Schwanz gerade).
- Flügelhaut einseitig (2 Bereiche, 75 Flächen) → `[winged.double_sided]`. Kleine lose Teile = Zähne.
- Keine verschmolzenen Gliedmaßen, keine Hautbrücken. Befunde Symmetrie/Mittellinie/Boden/Fußgruppen sind Folgen der
  schiefen Flügel/des gebogenen Schwanzes und mit Begründung freigegeben. ✅ Freigabe für das Rig.

## Rig (winged, 36 Knochen)
- Gelenke aus der Geometrie: Schritt 0,26 H, Brust 0,50 H, Kopf 0,08 m, Schwanz 0,80 m (6 Glieder), Spannweite 1,10 m.
- Schultern symmetrisch gesetzt (der nach hinten gefegte linke Flügel hätte sonst seine Schulter 13 cm weiter hinten).
- Flügel-Ruheform (links/rechts gemittelt): Arm steht senkrecht, Finger laufen nach außen-unten, die Haut hängt
  dazwischen. Gespreizt wird nur am Ellbogen; das Handgelenk wird nie weiter geöffnet als modelliert (sonst reißt die Haut).
- Übergang Flughaut ↔ Rumpf als Gewichtsverlauf (`wing_body_blend`), dadurch fiel die größte Dehnung von 6× auf ≈ 3,5×.
- Kiefer = untere Kopfhälfte vor dem Gelenk. Hörner, Rückenplatten und Keule bleiben starr (keine `[dangling]`).

## Bewegung (Muster drake)
Naturreferenzen und Clip-Liste: [motions/winged/drake/README.md](../../motions/winged/drake/README.md).
Zweibeiniger Waran-Gang mit erhobenen Flügeln, Biss-Ausfall, Schwanzkeulen-Hieb, Flughund-Flügelschlag, Segeln,
Abheben/Landen. Death = Platzhalter.

## Prüfbilder
- `rig/winged_rig.png`: Skelett vorn/seitlich/oben + Gewichte. `review/model_check.png`, `review/inspect_views.png`.
- Roh-GIFs (ARPG + Seite): `rig/anim/raw/Winged_Drake_*.gif` – zentral: Walk, Fly, Attack1, Attack2, TurnLeft.
- End-GIFs nicht separat gerendert (`--no-preview`): nach der Roh-Fassung wurde nichts bereinigt, sie sind identisch.

## Offen
- Bewegung vom Nutzer abnehmen (Roh-GIFs). Offene Frage: Gang auf den Flügel-Handgelenken (Fledermaus) statt zweibeinig?
- Feueratem (Rolle „Elite, Feueratem“) ist noch kein eigener Clip (Attack1 = Biss, Attack2 = Schwanzkeule).
- Death = Platzhalter (Nutzerregel). Lange Schwanzkeule ragt im Vorschau-GIF teils aus dem Bild (feste Kamera in render_anim).
