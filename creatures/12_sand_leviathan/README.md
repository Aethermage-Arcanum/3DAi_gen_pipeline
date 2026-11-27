# Sand Leviathan (Wüste) – legless/sandworm

Erste Kreatur des Musters `legless/sandworm` (Wurm-Kriechen, Eingraben, Auftauchen). Gebaut 2026-11-27.
Muster, Clips und Nutzer-Entscheidungen: `motions/legless/sandworm/README.md`, Recherche: `motions/legless/sandworm/RESEARCH.md`.

```
python scripts/tripo_run.py creatures/12_sand_leviathan --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/12_sand_leviathan --stage motion   # Roh-GIFs rig/anim/raw/
python scripts/creature_pipeline.py creatures/12_sand_leviathan                  # Endfassung + Export (kostenlos)
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 4.228 (1 Mesh) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal (+ ORM im Blend) je 1024² (Tripo 2048² verkleinert) |
| Knochen | 29: Root, 13 Wirbel `Spine_01–13` (9 Ringe + 4 Panzer), Head, Jaw, 13 Ring-Knochen `Ring_01–13` (tragen die Haut, Skalierung = Peristaltik) |
| UV | Tripo-UV (150 Inseln, Abdeckung 57 %, Überlappung 0 %; Winkelverzerrung 9,4° > Grenze 8° – Smart UV mit 1.133 Inseln und 19 % Abdeckung ist klar schlechter, Sichtprüfung `uv/uv_preview.png` ok) |
| Clips | 12 (`Legless_Sandworm_*`), alle grün: Bodenkontakt exakt (Körper liegt auf), Schleifen nahtlos, Lücken 0,0 cm, FBX/GLB-Gegentest ok |
| Export | `output/SandLeviathan.fbx/.glb`, Events `output/SandLeviathan_events.json` |

## Prüfung Tripo-Modell (Teil B, 2026-11-27)
**Bestanden, keine schweren Mängel.** `review/model_check.png` (automatisch: keine Auffälligkeiten, Mittellinie freigegeben) +
Sichtprüfung vorn/Seite/oben/ARPG (`temp/sw_inspect/`): Körper gerade und symmetrisch, 1 Teil, Textur sauber, rundes Maul mit
Zahnkranz wie gewünscht (seitlich Mischform mit Schnauzen-Haube), ≈ 9 Ringe + Panzer vorn + Schwanzstachel wie im Referenzbild.
Bekannte Befunde, per Rig gelöst statt neu generiert:
- **Bauchstacheln zeigen wie Stummelbeine nach unten** (tiefste Punkte = 2 Stacheln, Bauch schwebte 1,9 cm) → Stacheln zählen
  nicht für den Bodenkontakt (`ground_ignore_spikes`), der Körper liegt auf, die Stacheln stecken im Sand.
- **Viele seitliche Stacheln** → starr am Ansatz (`rigid_spikes`), Ringe starr, Biegen nur in den Furchen.
- **Maul weit offen** → bleibt offen und pumpt nur (Nutzer-Entscheidung).
- Gedrungen (Länge : Dicke ≈ 3 : 1) → Kriechen statt Schlängeln.

## Rig (`[legless]` in `creature.toml`)
Wirbel-Grenzen auf den Ringfurchen (gemessen in der Draufsicht), Panzer 4 Wirbel auf den Plattenreihen, Kopf = Maul ab 86 %
der Länge. Übergänge: Ringfurchen ±2 % (Ringe starr), zwischen Panzerplatten ±3 %, Kopfansatz ±3,5 %. 698 Stachel-Vertices in
70 Gruppen erkannt. Prüfbild Gewichte: `rig/rig_debug.png`.

## Messwerte (2026-11-27)
- **Bodenkontakt:** alle Stand-/Lauf-Clips tiefster Körperpunkt 0,0 mm über dem Boden (Stacheln ausgenommen).
- **Drehrichtung:** TurnLeft Kopf im Mittel +50° (links), TurnRight −50° (rechts) → `turn_dir_ok`.
- **Angriffe vor dem Körper:** Attack1 Reichweite 0,22 L, Maul 0,15 L vor dem Kopfansatz, 0,16 m über dem Boden; Attack2
  (Body Slam) Reichweite 0,20 L, Aufprall 0,14 L vor dem Kopfansatz → `hit_in_front_ok`.
- **Burrow:** Root Motion 0,9 L, unter dem Boden nur hinter dem Eintrittspunkt (`entry_ok`). **Emerge:** Kopf-Hochpunkt 0,64 m,
  endet exakt in Ready Frame 0 (`ends_in_ready_ok`).
- **Dehnung auf den aus der ARPG-Kamera sichtbaren Flächen** (`rigging/joint_densify_review.py … visible`, max je Clip):
  Walk 1,36 · Run 1,54 · Idle 1,24 · Ready 1,79 · Attack1 1,91 · Attack2 1,77 · Hit 1,78 · Burrow 1,86 · Emerge 2,03 (Rücken,
  Biegung am Loch) · TurnLeft/Right 2,31/2,33 (nur 3–5 Kanten an der Bauchlinie am Panzerende; Rücken ≤ 1,8).
  Erreicht durch Rig-Änderungen (4 statt 3 Panzer-Wirbel, breitere Plattenübergänge, Kopf-Knick auf 3 Wirbel verteilt,
  Loch-Biegung unter den Boden gelegt), nicht durch kleinere Bewegung (vorher bis 3,6).

## Naturvideos (vom Nutzer anzusehen, Links aus RESEARCH.md nicht selbst gesehen)
- Bobbit-Wurm, Angriff aus dem Sand (Zeitlupe): https://petapixel.com/2025/12/26/ultra-slow-motion-footage-shows-terrifying-bobbit-worm-striking-its-prey-from-under-the-sand/
- Sandfisch schwimmt im Sand (Maladen et al. 2009, mit Videos): https://www.arxiv.org/abs/0910.3248
- Suchbegriffe: „earthworm peristalsis slow motion“, „rectilinear locomotion boa“, „Kenyan sand boa burrowing“

## Prüfbilder
- Roh-GIFs: `rig/anim/raw/`, Kontaktbögen `rig/anim/raw/sheet_<Walk|Run|TurnLeft|Attack1|Attack2|Burrow|Emerge>.png`
- Endfassung: `rig/anim/final/`

## Offen
- Death ist nur ein Platzhalter (Death-Clips gesperrt).
- Bewegung vom Nutzer abnehmen lassen (Roh-GIFs), Naturvideos gegenprüfen.
