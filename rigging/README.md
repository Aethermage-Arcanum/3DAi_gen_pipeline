# Standard-Krabbler-Rig

Eigenes Skelett + Laufzyklus für alle Krabbler (Spinnen, Insekten, Skorpione …), statt Tripos Auto-Rig.
Grund: Tripos Octopod-Rig war beim Chitin Crawler unbrauchbar (nur ~2 von 8 Beinen mit Knochenkette).

**Ein Befehl für alles** (kostenlos, lokal):
```
python scripts/crawler_pipeline.py creatures/<name>
```
Eingabe: `raw/generate_model.glb` von Tripo (nur Mesh + Textur, kein Tripo-Rig/Animation nötig → spart 35 Credits pro Monster).

## Standard-Skelett (43 Knochen, immer vollständig)
```
Root
└ Thorax
  ├ Abdomen_1 └ Abdomen_2
  ├ Head ├ Antenna_L_1 └ Antenna_L_2 · Antenna_R_1 └ Antenna_R_2 · Mandible_L · Mandible_R
  └ Leg_{L|R}{1..4}_Coxa └ _Femur └ _Tibia └ _Tarsus     (1 = vorne … 4 = hinten)
```
**Fake it:** Fehlt ein Körperteil (z. B. Sechsbeiner oder keine Mandibeln), bleiben die Knochen als unsichtbare Platzhalter ohne Gewichte. Damit passen alle Animationen auf alle Krabbler.

## Wie es funktioniert
1. **Erkennung** (`crawler_detect.py`): Tripo-Low-Poly-Meshes bestehen aus vielen Einzelteilen (Chitin-Segmenten). Die Teile werden über einen Spannbaum nach Nähe verbunden. Fußspitzen sind Teile mit Bodenkontakt, die Beinkette ist der Weg Fuß → Rumpf. Teile, die mehrere Beine teilen (Gelenkringe), zählen zum Rumpf.
2. **Skelett** (`crawler_rig.py`): Die Beingelenke liegen an den **echten Segment-Übergängen**, das Knie ist der höchste Übergang. Die Rumpfachse ergibt sich aus dem Breitenprofil (Engstellen = Taille/Petiolus und Hals).
3. **Gewichte**: Beine nach Position entlang der Kette, starr innerhalb der Glieder, mit **weichen Gelenkmanschetten** um jedes Gelenk inklusive Beinansatz (`joint_blend`). Rumpf-Vertices nahe an Beinen übernehmen anteilig deren Gewichte (`root_blend`), sonst klaffen Ansätze auf. Der Rumpf hat weiche, positionsbasierte Übergänge, damit sich keine Risse zwischen Panzerplatten öffnen. Lose Teile neben einem Bein folgen dem Bein. Max. 4 Einflüsse pro Vertex.
4. **Laufzyklus** (`crawler_walk.py`): zwei abwechselnde Beingruppen (L1,R2,L3,R4 gegen den Rest).
   - 6 Laufbeine → **Dreifuß-Gang** (Ameise), 8 → alternierender Vierfuß (Spinne).
   - Drehachsen werden pro Bein **aus der Geometrie berechnet**: Gieren um die echte Senkrechte, Heben quer zum Bein.
   - Schwenkwinkel pro Bein so, dass **alle Füße gleich weit schieben** (kein Rutschen in Unity).
5. **Export** (`export_unity.py`): FBX mit Kopf → Unity +Z, Flat Shading, Texturen verkleinert. Dazu GLB.
6. **Selbstprüfung**: Bodenkontakt der Füße, Schleife (alle Knochen), Fühler-Ausschlag, **Gelenk-Lücken** (`check_gaps.py`), Gegentest der Exporte (`verify_export.py`), Vorschau-GIF.

## Stellschrauben (`crawler_defaults.toml`, pro Kreatur überschreibbar in `creature.toml` unter `[crawler.*]`)
- `[walk] walking_slots` / `feeler_slots`: welche Beinpaare laufen bzw. nur tasten
- `stride` (Schrittlänge), `lift_deg` (Schritthöhe), `cycle_frames` (Tempo), `duty` (Standanteil)
- Körper: `body_sway_deg`, `abdomen_sway_deg`, `abdomen_lag`, `head_sway_deg`, `antenna_deg` …
- `[export] texture_size`

## Werkzeuge zum Prüfen
- `debug_detect.py`: Erkennung farbig (jedes Bein eigene Farbe, Gelenkpunkte)
- `pose_test.py`: Testpose mit Skelett-Overlay
- `render_anim.py` + `make_gif.py`: Animation aus 3 Blickwinkeln als GIF

## Bekannte Grenzen / Offen
- Bisher nur an einem Modell (Chitin Crawler) getestet. Krabbler mit verschmolzenem Mesh (keine Einzelteile) bräuchten eine andere Erkennung.
- FBX enthält nur Color + Normal. Die ORM-Textur (Metallic/Roughness/AO) ist nur in der GLB → in Unity per Import-Skript zuweisen.
- Bisher nur der Clip **Walk**. Es fehlen Idle, Angriff, Treffer, Tod (gleiches Prinzip, jeweils mit eigener Naturreferenz).
- Laufen ist „in place“. Die Fortbewegung macht Unity mit der empfohlenen Geschwindigkeit aus `walk_report.json`.
