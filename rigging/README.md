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
   **Ein-Mesh-Spinnen (octopod, seit 2026-11-21, Broodling):** Neuere Tripo-Spinnen sind EIN zusammenhängendes Mesh. Hat das
   verschweißte Mesh höchstens 3 Teile, nimmt `octopod_detect.detect_single` den anderen Weg (`[detect] single_mesh = "auto"`,
   Stellschrauben `sm_*` in `octopod_defaults.toml`): Fußspitzen = am weitesten entfernte Punkte über die Oberfläche nahe am
   Boden; Beinwurzel = wo die Wand-Dicke (Shape Diameter, Strahl ins Innere) vom dünnen Bein auf Rumpf-Dicke springt;
   Gelenkketten links/rechts gespiegelt gemittelt; Bein-Haut = dünn + nah an der Bein-Mittellinie; von Tripo verschmolzene
   Flächen (Bein ↔ Rumpf weit weg von der Wurzel, Bein ↔ Bein) werden gelöscht (beim Broodling: keine nötig). Im Rig dazu:
   Trennebene Vorderkörper/Hinterleib (`sm_abdomen_split`), alles dahinter (Eierhaufen!) **starr** an `Abdomen_1`, Rumpf-Mitnahme
   nur an der Coxa. Mehrteilige Meshes (Chitin Crawler/Crab) laufen unverändert (Regression 2026-11-21: Fingerabdruck identisch).
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

## Gelenk-Verdichtung – mehr Vertices nur am Gelenk (Backlog C9, seit 2026-11-20)
Allzweck-Baustein `joint_densify.py` (Standardwerte `joint_densify_defaults.toml`, Prüfwerkzeug `joint_densify_review.py`).
Regel des Nutzers: Dehnung nie durch kleinere Bewegung lösen, sondern am Mesh. Tripo-Low-Poly hat an Gelenken oft
lange Dreiecke; eine lange Kante zwischen zwei Knochen kann beim Beugen nur „abkürzen“ oder sich dehnen.

**Opt-in pro Kreatur** in `creatures/<NN_name>/creature.toml` (ohne Abschnitt ändert sich nichts – Mesh, Gewichte und
Export bleiben Bit für Bit gleich; Nachweis `scripts/regression.py --deep`, 6 Kreaturen identisch, siehe unten):
```toml
[joint_densify]
# max_extra_tris = 800            # optional: Obergrenze zusätzlicher Dreiecke (ganze Kreatur)
# target_edge = 0.012             # optional: Kanten im Ring halbieren, bis kürzer als das (Anteil Größe)
# levels = 2                      # optional: höchstens so oft halbieren
[[joint_densify.joint]]           # beliebig viele
bones = ["Leg_*_2", "Leg_*_3"]    # Gelenk = Kopf dieses Knochens (Übergang zum Eltern-Knochen), * erlaubt
# radius = 0.06                   # optional: Ringbreite (Kugel um das Gelenk, Anteil Größe)
```
Eingebaut in `quadruped_rig.py` und `biped_raptor_rig.py` (je 2 Stellen: vor und nach dem Gewichten). Für ein anderes
Skelett: dieselben Zeilen einbauen (Beschreibung oben in `joint_densify.py`), danach Regression.

**Was passiert** (im Rig-Skript, NACH dem Skelett, VOR dem Gewichten):
1. Kandidaten: Kanten des Hauptkörpers im Ring, länger als `target_edge`. Kanten, die die Gelenk-Ebene kreuzen, zuerst
   (Ebene ⟂ mittlere Richtung Eltern-/Kind-Knochen), bis `max_extra_tris` erreicht ist (jede halbierte Kante = +1 Dreieck
   je anliegender Fläche, die Zählung ist exakt).
2. Halbieren mit bmesh: neue Vertices liegen **genau auf der alten Kante** (kein Glätten → Facetten-Look bleibt), UVs und
   Ecken-Daten werden interpoliert, Material/Flat-Flag übernommen. UV-Naht-Duplikate werden immer gemeinsam geteilt
   (gleiche Position) → keine T-Stöße, nichts reißt. Alte Vertices behalten ihre Nummer.
3. Danach gewichtet das Rig ganz normal – seine Abstands-Gewichte geben den neuen Stützpunkten Zwischenwerte.
4. Bericht in `rig/rig_report.json` → `joint_densify` (Tris vorher/nachher, Mehr-Tris, Budget erreicht?) und
   `rig/joint_densify.json` (Zuordnung alte Kante → neue Vertices, für den fairen Vergleich).

Optional `soft_iterations` (Standard 0 = aus): zusätzliches Glätten der Gewichte nur im Ring. Gemessen an Wolf und Raptor
wurde die Dehnung damit **größer** – deshalb aus.

**Prüfen** (Dehnung je Clip, fair = Länge entlang der ALTEN Kanten, damit kürzere neue Kanten nicht schönrechnen;
„ring“ = nur Kanten in den Gelenk-Ringen):
```
& "D:\Blender\blender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- stretch <aus.json> <verdichtet>/rig/joint_densify.json
& "D:\Blender\blender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- shot <bild.png> <Action> <frame> <Knochen> <radius_m>
python rigging/joint_densify_review.py sheet <bogen.png> "Vorher" <bild1.png> "Nachher" <bild2.png>
```
Prüfbild: Render | Drahtgitter | Dehnung je Dreieck (grau ≤ 1,1 · gelb 1,5 · rot ≥ 2,0).

**Ergebnis Test 2026-11-20** (Kopien in `temp/`, fertige Kreaturen unverändert):
| Kreatur (Gelenke) | Tris | Dehnung in den Gelenk-Ringen (max · Kanten > 1,5) | gesamt max |
|---|---|---|---|
| Wolf (Knie, Sprunggelenk, Ellbogen, Handgelenk) | 4.258 → 5.058 (+800, +19 %) | Run 2,05 → 1,78 · 18 → 12 (> 2,0: 2 → 0); Walk 1,63 → 1,51 · 5 → 2; Ready 1,55 → 1,43 · 3 → 0; TurnLeft 1,64 → 1,49 | unverändert (Run 2,89 Flanke Hüfte, Attack1 2,27 Kopf) |
| Hollow Stag (gleich) | 4.243 → 5.043 (+800) | Run 3,93 → 3,99 · 8 → 4 | unverändert (3,9–4,2) |
| Dune Raptor (Knie, Sprunggelenk) | 4.184 → 4.984 (+800) | schlechter: Run 2,55 → 2,65, Walk 2,14 → 2,23 | unverändert/schlechter |

Was das heißt:
- **Hilft dort, wo lange Kanten über ein stark beugendes Gelenk laufen** (Wolf-Beine): weniger und schwächer gedehnte
  Dreiecke am Gelenk. Gedacht vor allem für den Frosch (Oasis Gulper: lange Kanten, extremes Beugen in die Hocke).
- **Hilft nicht** gegen Dehnung aus der Gewichts-Verteilung: Die größten Werte aller getesteten Kreaturen liegen auf
  ohnehin kurzen Kanten mit falschen/harten Gewichten (Wolf: Flanke Oberschenkel↔Rücken; Hirsch: Vertex am Knie mit
  42 % Schwanz-Gewicht; Raptor/Geier/Wyvern: harte Sohle am Ballen). Das bleibt Arbeit an den Gewichten des jeweiligen Rigs.
- Raptor wird schlechter: das Glätten des Rigs zählt Kanten-Schritte; im verdichteten Ring wird der Übergang in Metern
  schmaler. Nur einschalten, wo der Vergleich (stretch + Prüfbild) eine Verbesserung zeigt.

## Gewichte nach Körperbereichen – Dehnung aus der Spielkamera (Backlog C15, seit 2026-11-21)
Nutzer-Kritik: Dehnung wird dort geprüft, wo man sie im Spiel sieht – Silhouette und Oberseite (Rücken, Widerrist,
Hals, Kruppe, Flanke), nicht Fußgelenke. Messung und Prüfbilder deshalb immer in der ARPG-Ansicht (s. u.).

**Optionen im Vierbeiner-Rig** (`creature.toml [quadruped.rig]`, ohne die Zeilen ändert sich nichts – Regression
identisch für Reef Snapper; Raptor/Bog Warden/Geier nutzen andere Rigs, ebenfalls identisch):
```toml
zone_lock = true          # Fremdbereich-Sperre (weich auslaufend, vor UND nach dem Glätten):
                          #  (a) Unterbein Leg_*_2..4 nicht über Knie/Ellbogen (+ zone_leg_margin · H, Standard 0.03)
                          #  (b) Bein/Schulterblatt nicht auf dem Rückenstreifen über der Wirbelsäule
                          #      (zone_dorsal 0.35 der halben Rumpfbreite gesperrt, zone_dorsal_soft 0.25 weicher Rand)
spine_chain_blend = 1.0   # Anteil der Wirbelkette (Hips…Neck_2) nach Lage ENTLANG der Kette verteilen
                          # (lineare Rampe dieser Breite in Knochenlängen um jedes Gelenk) statt nach Abstand je Knochen
```
Die Knochen und damit die Bewegung bleiben exakt gleich (Fingerabdruck: Knochen 0,0 mm / 0,0° in allen Clips), nur die
Haut-Gewichte ändern sich. Eingeschaltet: Ravine Stalker (Wolf, mit `zone_leg_margin = 0.12`), Hollow Stag.

**Fehlerklassen** (gemessen an Wolf und Hirsch, Details + Zahlen in den READMEs der Kreaturen):
| Fehlerklasse | Beispiel | per Regel? | Regel |
|---|---|---|---|
| Fremder Körperbereich zieht mit | Hirsch: beide Schulterblätter auf dem Widerrist, Oberschenkel auf der Kruppe; Wolf: Schienbein (Leg_B*_2) an der Bauchlinie, Mittelfuß am Oberschenkel | ja | `zone_lock` |
| Falscher Wirbelknochen / harter Übergang in der Kette | Hirsch: steiler Hals → oberer Halsknochen Neck_2 gleich weit vom Widerrist wie Neck_1 (43 % Neck_2) | ja | `spine_chain_blend` (wirkt voll erst zusammen mit `zone_lock`) |
| Schmaler Übergang Bein → Rumpf | Wolf: Flanke 13 cm vor der Hüfte, Oberschenkel-Anteil springt 0,43 → 0,24 über eine 2-cm-Kante, Galopp | nein (getestet: mehr Glätten im Übergang, Reichweiten-Grenze für den Oberschenkel → Dehnung wandert nur auf Flanke/Oberschenkel) | Rest, iterativ |
| Rig-Aufbau | Hirsch: Schwanzkette läuft im Zickzack durch die Hinterbeine (Mittelpunkt-Suche greift die weit hinten stehenden Beine) | nur gemildert | Knochen umsetzen würde die Schwanzbewegung ändern → Entscheidung Nutzer |
| Zu grobes Mesh | Hirsch: Widerrist-Kanten 3,5–4,2 cm | nach den Gewichtsregeln nicht mehr nötig (max 1,46) | `[joint_densify]` bei Bedarf |

**Messen und Prüfbilder** (`joint_densify_review.py`, siehe Kopf der Datei):
```
& "D:\Blenderlender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- visible <aus.json> [every]
& "D:\Blenderlender.exe" -b <rig>/clips.blend -P rigging/joint_densify_review.py -- arpg <bild.png> <Action> <frames> [az] [scale]
python rigging/joint_densify_review.py sheet <bogen.png> "Vorher" <a.png> "Nachher" <b.png> …
python rigging/joint_densify_review.py gif <aus.gif> <fps> "Vorher" "<a_*.png>" "Nachher" "<b_*.png>"
```
`visible` = Dehnung nur auf Flächen, die aus der Spielkamera (50° von oben, 8 Richtungen rundum, Verdeckung per Strahl)
sichtbar sind, je Bereich (Rücken, Flanke, Bauchlinie, Hals, Kopf, Schwanz, Schulter/Oberschenkel, Unterbein; Bereich
geometrisch nach nächstem Knochen → vorher/nachher fair), dazu die 40 schlimmsten Kanten mit den Gewichten beider Enden.

**Ergänzung Rimehide Bear (2026-11-21)** – drei neue, optionale Werte (ohne sie alles wie bisher; Regression `--deep`
Wolf, Hirsch, Reef Snapper identisch):
```toml
[quadruped.detect]
spine_slice = 0.06            # dickere Querschnitte nur für Wirbelsäule + Hals (grobes Low-Poly: im 3-cm-Schnitt fehlten
                              # Rücken-Vertices → Wirbelsäulen-Mitte fiel auf Bauchhöhe, Zickzack)
[quadruped.rig]
chest_extend = 0.6            # Brust endet / Hals beginnt erst so weit vor dem Schultergelenk (Anteil bis Kopfansatz):
                              # Bären-Buckel hing sonst am Hals und sackte beim Kopfsenken ein
rigid_parts_exclude = ["Jaw"] # mit rigid_parts: lose Teile nie an diese Knochen (Oberkiefer-Fangzähne → Head)
```
Außerdem: leere Querschnitte in der Schwanzkette werden fortlaufend vom Vorgänger gefüllt (vorher nur eine Lücke →
Absturz bei gestrecktem Bären-Mesh im Statur-Test). Dazu beim Bären nur Werte: `leg_x_reach`/`leg_capture` (schräge Vorderbeine, Pranken weit vor der Schulter),
`tail_base` (Stummelschwanz ganz hinten → Kruppe an Hips statt an Tail_*). Details: `creatures/32_rimehide_bear/README.md`.

## Schildkröten-Panzer starr (`rigid_shell`, Shellback 2026-11-23)
Opt-in im Vierbeiner-Rig, nur für die Shellback eingeschaltet (ohne die Zeilen alles wie bisher; Regression `--deep`
Wolf, Reef Snapper, Hirsch, Bär identisch). Panzer = Hauptkörper ohne Bein-, Hals/Kopf- und Schwanz-Öffnungen
(geometrisch: Beinkette + Randhöhe, Ebene der Halsöffnung, Schwanzöffnung, Mindesthöhe) → 100 % an `shell_bone`.
Übergang in die Haut nach **Abstand** (`shell_blend_width`), nicht nach Kanten-Ringen – am Panzerrand liegen sehr kurze
Kanten neben langen, ein Ring-Übergang war dort nur 1–2 cm breit (Dehnung bis 6,8). Dazu `shell_neck_free`
(Halsöffnung/Kehle ohne Schulterblatt, weich auslaufend) und `knee_out` (Hinterbein-Knie seitlich, gegen gestreckte
Säulenbeine). Alle Werte, Messungen und Begründung: `motions/quadruped/tortoise/README.md`.

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

## Skelett `winged` – Zweibeiner mit Flügeln (seit 2026-11-20)

`winged_rig.py` (Rig), `winged_detect.py` (Erkennung, reines numpy), `winged_defaults.toml` (Stellschrauben, pro Kreatur
`[winged]`), `winged_review.py` (Prüfbilder). Baukasten: `motions/winged/winged_kit.py`, Muster `motions/winged/drake/`
(Cinder Wyvern) und `motions/winged/bird/` (Bonepicker Vulture). Knochen und Baukasten: `motions/winged/README.md`.

**Erkennung** (auch bei schiefen Tripo-Flügeln und seitlich gebogenem Schwanz):
- Füße = 2 Gruppen am Boden; ihre Mitte ist die Körper-Mittelebene (nicht die Mitte des Tripo-Rahmens).
- Beine/Schritt über waagerechte Schnitte (Stücke, die den Boden berühren). Ferse = am weitesten hinten liegender Punkt
  der Bein-Mittellinie, Knie im Körper vor der Hüfte (digitigrad).
- Flügel = je Seite das größte Stück jenseits der Seitenebene `wing_plane`, das die Ebene hoch kreuzt (der Schwanz
  kreuzt tief). Schultern symmetrisch (vordere Kreuzungsstelle), Handgelenk = höchster Flügelpunkt, Spitze = weitester
  Punkt, Ellbogen/Hand/Finger entlang kürzester Wege über das Mesh. Flügelebene (Oberseite) aus Spannweite × Profil →
  Eigenschaft `wing_normal_L/R` am Armature-Objekt.
- Hals und Schwanz folgen der echten Mittellinie (Schwerpunkte gleich weit von der Spitze über die Oberfläche).

**Gewichte:** 1/Abstand + Masken (Beine, Flügel, Kern), Glätten über Kanten; Band `wing_body_blend` beidseits der
Grenze Flügel ↔ Rumpf (Flughaut-Ansatz verteilt die Dehnung statt einer Naht); Kiefer = untere Kopfhälfte vor dem
Gelenk; Sohle starr, Hinterzehe nur am Toe; lose Teile je Vertex am nächsten Haupt-Vertex; `[winged.double_sided]`.

```
& "D:\Blender\blender.exe" -b <rig>/winged_rigged.blend -P rigging/winged_review.py -- rig <bild.png>
& "D:\Blender\blender.exe" -b <rig>/clips.blend -P rigging/winged_review.py -- strip <bild.png> Winged_Drake_Walk 0,8,16 arpg,side,front
```

## Säulenartige Gliedmaßen (Frost Colossus 2026-11-27)
Opt-in in `quadruped_rig.py` (ohne die Zeilen alles wie bisher; Regression `--deep` Wolf, Reef Snapper, Hirsch, Bär, Shellback
identisch): `leg_joints_fixed` (feste Gelenk-Anteile statt Biegungs-Suche, die an Eis-Armschienen verrauscht war), `leg_mirror`
(links/rechts gemittelt), `joint_track_mean` (Hüfte über dem Bein statt im Schritt), `knee_forward`. Werte und Begründung:
`creatures/13_frost_colossus/README.md`. Starre Eisplatten per Textur-Helligkeit wurden getestet und verworfen (sichtbare Dehnung
schlechter), Details dort.
