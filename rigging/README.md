# Standard-Krabbler-Rig

Eigenes Skelett + Laufzyklus für alle Krabbler (Spinnen, Insekten, Skorpione …), statt Tripos Auto-Rig.
Grund: Tripos Octopod-Rig war beim Chitin Crawler unbrauchbar (nur ~2 von 8 Beinen mit Knochenkette).

**Ein Befehl für alles** (kostenlos, lokal):
```
python scripts/creature_pipeline.py creatures/<NN_name>
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
1. **Erkennung** (`hexapod_detect.py`, gleich in `octopod_detect.py`): Tripo-Low-Poly-Meshes bestehen aus vielen Einzelteilen (Chitin-Segmenten). Die Teile werden über einen Spannbaum nach Nähe verbunden. Fußspitzen sind Teile mit Bodenkontakt, die Beinkette ist der Weg Fuß → Rumpf. Teile, die mehrere Beine teilen (Gelenkringe), zählen zum Rumpf.
2. **Skelett** (`hexapod_rig.py` bzw. `octopod_rig.py`): Die Beingelenke liegen an den **echten Segment-Übergängen**, das Knie ist der höchste Übergang. Die Rumpfachse ergibt sich aus dem Breitenprofil (Engstellen = Taille/Petiolus und Hals).
3. **Gewichte**: Beine nach Position entlang der Kette, starr innerhalb der Glieder, mit **weichen Gelenkmanschetten** um jedes Gelenk inklusive Beinansatz (`joint_blend`). Rumpf-Vertices nahe an Beinen übernehmen anteilig deren Gewichte (`root_blend`), sonst klaffen Ansätze auf. Der Rumpf hat weiche, positionsbasierte Übergänge, damit sich keine Risse zwischen Panzerplatten öffnen. Lose Teile neben einem Bein folgen dem Bein. Max. 4 Einflüsse pro Vertex.
4. **Bewegung** → jetzt im Bewegungsmuster `motions/hexapod/ant/` (früher `crawler_walk.py`): zwei abwechselnde Beingruppen (L1,R2,L3,R4 gegen den Rest).
   - 6 Laufbeine → **Dreifuß-Gang** (Ameise), 8 → alternierender Vierfuß (Spinne).
   - Drehachsen werden pro Bein **aus der Geometrie berechnet**: Gieren um die echte Senkrechte, Heben quer zum Bein.
   - Schwenkwinkel pro Bein so, dass **alle Füße gleich weit schieben** (kein Rutschen in Unity).
5. **Export** (`export_unity.py`): FBX mit Kopf → Unity +Z, Flat Shading, Texturen verkleinert. Dazu GLB.
6. **Selbstprüfung**: Bodenkontakt der Füße, Schleife (alle Knochen), Fühler-Ausschlag, **Gelenk-Lücken** (`check_gaps.py`), Gegentest der Exporte (`verify_export.py`), Vorschau-GIF.

## Stellschrauben
- **Rig** (`hexapod_defaults.toml` / `octopod_defaults.toml`, pro Kreatur `[hexapod.*]` / `[octopod.*]`): Erkennung, Gelenkmanschetten, `[export] texture_size`
- **Bewegung** (`motions/<skelett>/<muster>/style.toml`, pro Kreatur `[motion.*]`): Beinpaare, Schrittlänge, Tempo, Haltung, alle Clip-Parameter, Varianten
- **UV** (`uv/uv_defaults.toml`, pro Kreatur `[uv]`)

## Werkzeuge zum Prüfen
- `debug_detect.py`: Erkennung farbig (jedes Bein eigene Farbe, Gelenkpunkte)
- `pose_test.py`: Testpose mit Skelett-Overlay
- `render_anim.py` + `make_gif.py`: Animation aus 3 Blickwinkeln als GIF

## Bekannte Grenzen / Offen
- Bisher nur an einem Modell (Chitin Crawler) getestet. Krabbler mit verschmolzenem Mesh (keine Einzelteile) bräuchten eine andere Erkennung.
- FBX enthält nur Color + Normal. Die ORM-Textur (Metallic/Roughness/AO) ist nur in der GLB → in Unity per Import-Skript zuweisen.
- Bisher nur der Clip **Walk**. Es fehlen Idle, Angriff, Treffer, Tod (gleiches Prinzip, jeweils mit eigener Naturreferenz).
- Laufen ist „in place“. Die Fortbewegung macht Unity mit der empfohlenen Geschwindigkeit aus `walk_report.json`.

## Frei hängende Teile (Lappen, Fühler, Hautfahnen) – ohne Knochen
Standard-Baustein für alle Skelette (Backlog C7). Kleine Teile, die frei schwingen sollen, bekommen **keine Knochen**,
sondern eine Markierung im Mesh; der Unity-Shader `Creature/Standard Dangling` lässt sie dann weich pendeln –
zusätzlich zu jeder Animation. Große, schwere Teile (lange Schwänze, Tentakel) brauchen weiterhin Knochenketten.

**So markiert man eine Kreatur** – Abschnitt in `creatures/<NN_name>/creature.toml` (Beispiel Eel Stalker):
```toml
[dangling]
amplitude = 0.025                 # optional: Ausschlag an der Spitze (Anteil der Größe)
[[dangling.region]]               # beliebig viele Bereiche
bones = ["Head", "Jaw", "Spine_11", "Spine_12", "Spine_13", "Spine_14"]   # Vertices, die v. a. an diesen Knochen hängen (* erlaubt)
below = 0.0                       # optional: nur unterhalb der Knochenlinie (Anteil Größe; −0.01 = 1 cm tiefer)
# above = 0.0                     # optional: nur oberhalb
# thin_max = 0.04                 # optional: Dicke-Grenze für diesen Bereich
```
Dann `python scripts/creature_pipeline.py creatures/<NN_name>` – fertig. Prüfbild: `rig/dangling_preview.png`
(blau = starr, rot = schwingt; Zahlen in `rig/dangling_report.json`). Ohne `[dangling]` passiert nichts.

**Was das Skript macht** (`rigging/dangling.py`, Standardwerte `dangling_defaults.toml`, läuft direkt nach dem Rig):
1. **Bereich** aus `[[dangling.region]]` (Knochen + oben/unten, in der Ruhepose).
2. **Nur dünne Teile**: Dicke = kürzester Strahl von der Oberfläche nach innen bis zur Gegenseite, < `thin_max` (3 % der
   Größe). Rumpf, Kopf und Kiefer sind dick und schwingen daher nie mit, auch wenn sie im Bereich liegen.
3. **Verlauf Ansatz → Spitze**: Abstand über die Mesh-Kanten vom ersten starren Nachbarn, je Teil auf 0 … 1 (hoch
   `exponent`). Am Ansatz ≈ 0 → nichts reißt ab. Teile kürzer als `min_length` (3,5 %) bleiben starr (Zähne, Noppen,
   kurze Zacken), ab `full_length` (8 %) schwingen sie voll.
4. **Phase je Teil** (zufällig, aber fest) → nicht alle Lappen im Gleichtakt.
5. Ergebnis: Farb-Attribut `_DANGLING` (R = Gewicht, G = Phase). Vertices an derselben Stelle (UV-Nähte) bekommen
   exakt dieselben Werte → keine Risse.

**Export** (`export_unity.py`, nur bei markiertem Mesh): FBX mit Vertex-Farben (linear, 1:1), GLB mit eigenem Attribut
`_DANGLING` (absichtlich nicht `COLOR_0`, sonst färben glTF-Programme das Modell rot ein), dazu `<Name>_dangling.json` mit
den Shader-Startwerten (`amplitude` in Meter umgerechnet, `frequency`, `lag`, `vertical`). Der Gegentest
(`verify_*.json` → `"dangling"`) zeigt, dass die Markierung in beiden Dateien ankommt.
Unity: der Importer gibt Kreaturen mit `_dangling.json` automatisch das Wabbel-Material (siehe `Unity_Creature_Test/README.md`).

**Kosten**: kein Knochen, kein Draw Call, kein Material mehr; +4 Byte pro Vertex (Farbe) und ~20 Rechenschritte pro
Vertex im Vertex-Shader (auch im Schatten-Durchgang). Bei 3.300 Vertices vernachlässigbar, auch bei vielen Gegnern.
**Grenzen**: Der Shader kennt keine Trägheit (Lappen schwingen gleichmäßig, nicht stärker bei schnellen Bewegungen) und
verbiegt nur (keine Kollision mit dem Körper). Für große Ausschläge lieber Knochen-/Federketten.

## Skelett `upright` – aufrechter Zweibeiner mit langen Armen (seit 2026-11-18)
Für Treant (Bog Warden), später Golem und Brute/Flesh Titan. Dateien (gekapselt, nur Allzweck-Bausteine importiert):
`upright_rig.py` (Rig), `upright_detect.py` (Erkennung), `upright_defaults.toml` (Stellschrauben, pro Kreatur `[upright]`),
`upright_review.py` (Prüfbilder). Baukasten: `motions/upright/upright_kit.py`, erstes Muster `motions/upright/treant/`.

**27 Knochen, feste Namen (Unity „Generic“):**
```
Root └ Pelvis → Spine_1 → Spine_2 → Spine_3 → Chest
          Chest → Neck → Head      Chest → Crown
          Chest → Clavicle_{L,R} → UpperArm → Forearm → Hand → Fingers
       Pelvis → Thigh_{L,R} → Shin → Foot → Toe
```
Fehlt ein Teil, bleibt der Knochen ein **Platzhalter ohne Gewicht** (Treant: Neck, Head – das Gesicht sitzt im Stamm = Chest).
Crown = starrer Aufbau oben auf dem Rumpf (Treant: Astkrone; Golem: Kristalle; sonst Platzhalter).

**Erkennung an der echten Geometrie** (Tripo baut diese Kreaturen als EIN verschmolzenes Mesh): Waagerechte Schnitte, und alles
oberhalb eines Schnitts wird weggedacht. Die Stücke mit Bodenkontakt sind die **Beine**. Die höchste Höhe, bei der beide noch
getrennt sind, ist der **Schritt**. Die beiden großen frei hängenden Stücke unterhalb des Schritts sind die **Arme**. Der Schnitt
wird pro Arm hochgeschoben, bis der Arm mit dem Rumpf verschmilzt: das ist die **Achsel**. Die **Krone** beginnt dort, wo der
Rumpf-Schnitt sprunghaft breiter wird. Die Gelenke folgen aus der Mittellinie (Schwerpunkt der Schnittkurven):
- Knöchel: wo die Wurzel-/Zehenspreizung endet.
- Knie: Engstelle, bei gleich dicken Stumpfbeinen 45 % (leicht nach vorn, damit die IK sicher nach vorn knickt).
- Ellbogen: stärkste Biegung.
- Handgelenk: wo die Hand breiter wird.
- Fingeransatz: höchster Schnitt mit ≥ 3 getrennten Fingern.

**Gewichte:** 1/Abstand⁴ mit Masken je Körperteil (Bein-/Arm-Stücke nur eigene Knochen, Übergänge an Schritt, Achsel und
Schulter), danach Glätten über die Kanten (weiche Manschetten), max. 4 Einflüsse, UV-Naht-Duplikate identisch.
- Fußsohle: nur Foot/Toe.
- **Krone starr** an Crown. Dazu zählen Äste und daran hängende Strähnen, erkannt über den kürzesten Weg im Mesh: näher an
  der Krone als am Rumpf-Kern. Am Stamm gibt es einen geglätteten Übergang (`crown_smooth`, sonst Riss an Strähnen, die
  direkt am Stamm ansetzen).
- Lose Mesh-Teile (Moos, Pilze) hängen starr an ihrer Ansatzstelle.
- Einseitige Moos-Platten macht `[upright.double_sided]` doppelseitig. Das Schwingen kommt aus `[dangling]` (keine Knochen).

**Baukasten** (`upright_kit.py`):
- Bein-IK: Oberschenkel + Schienbein auf ein Ziel am Knöchel, Fuß-Ausrichtung vom Ziel. Abrollen: Ferse hebt um den Ballen,
  Zehen bleiben flach.
- Arme frei (FK) mit Federn/Verzögerung, für Bodenkontakt per Hand-IK (Einfluss pro Frame).
- `posture()`: Rumpf-Neigung **absolut** statt auf die gebückte Ruhepose addiert.
- Prüfungen beim Backen: Fußkontakt, Fußrutschen pro Frame, Schleife, Drehrichtung (`body_turns`, `upper_body_leads`),
  Rückkehr in die Standhaltung, Dehnung (nur Info).

**Prüfbilder:**
```
& "D:\Blender\blender.exe" -b <rig>/upright_rigged.blend -P rigging/upright_review.py -- rig <bild.png>
& "D:\Blender\blender.exe" -b <rig>/clips.blend -P rigging/upright_review.py -- strip <bild.png> Upright_Treant_Walk 0,5,10 side,front,arpg
```
