# Varianten-Baukasten (Unity + Blender) – Meilensteine 1 und 2

Stand 2026-11-22 · Werkzeug-Version 0.2.0 · Grundlage: `docs/VARIANTEN_SPEC.md` (Entscheidungen E1–E8).
- **M1:** Unity-Fenster für Statur, Accessoires und Material-Ebenen, Backen zu 1 Mesh + 1 Material (Teile A und B).
- **M2:** Blender-Panel mit Live-Reglern (Statur, Bedeckungs-Lagen Fell/Federn/Stacheln/Platten, Baustein-Werkbank),
  Unity-Knopf **„In Blender bauen“**, **Textur-Backen** (Albedo, Maske, Leuchten, Normal → Spiel-Shader „VariantKit/Baked“),
  Gruppen-Presets A–I und 15 neue Bausteintypen (Teile C und D).
Die Reste stehen am Ende von Teil D.

---

## Teil A – Kurzanleitung (ohne 3D-Erfahrung)

### 1. Fenster öffnen
1. Unity-Projekt `01_kreatur_pipeline/Unity_Creature_Test` öffnen.
2. Menü **Kreaturen › Varianten-Baukasten**. Beim ersten Öffnen holt der Baukasten den Bären (`RimehideBear.fbx`)
   als eigene Kopie ins Projekt. Das dauert ein paar Sekunden.
3. Oben **Basis** wählen (z. B. `RimehideBear`). Darunter **Variante**: `slagback_bear.variant.json` oder
   `cragplate_bear.variant.json`.

### 2. Vorschau
- Oben liegt das Vorschaubild mit laufendem Clip. Die Knöpfe **Ruhe / Walk / Idle / Run / Attack1 / Attack2** wählen den Clip,
  **❚❚** hält an, der Regler daneben stellt das Tempo ein.
- **Kamera:** ARPG (schräg von oben wie im Spiel), Seite, Vorn, Oben. Mit der Maus im Bild ziehen dreht die Kamera,
  das Mausrad zoomt.
- Die Lämpchen oben zeigen die **Statur-Ampel** und das **Budget** (Tris gegen die Grenze der Budget-Klasse).

### 3. Regler (vier Reiter)
| Reiter | Was man dort tut |
|---|---|
| **Statur** | 17 Regler für Größe und Proportionen, dazu „Masse“ (Rumpf- und Gliederdicke zusammen). Jeder Regler hat ein Lämpchen: grün = Clips passen, gelb = Clips passen mit Korrektur. Die Regler gehen nur bis Gelb. „1“ setzt einen Regler zurück. **Rutschen die Füße in der Vorschau, ist das normal.** Die fertige Variante muss später mit angepassten Clips neu gebacken werden (Blender, Meilenstein 2). |
| **Material** | *Farbgruppen*: Farbe von Haut, Accessoires, Krallen/Zähnen (horn), Nase/Maul (akzent) und Augen, jeweils mit matt ↔ glänzend, Leuchten usw. *Ebenen*: Verlauf, Muster, Risse (Glut, Frost … mit Leuchten und Puls), Überzug (Staub, Asche …), Nässe, Rim-Licht. Pro Ebene gibt es eine **Maske**: auf welchen Körperzonen sie wirkt, „ohne“ welche Zonen, oben/unten, fleckiger Rand und welche Farbgruppen. Mit ▲ ▼ ändert man die Reihenfolge, mit ✕ löscht man eine Ebene. |
| **Accessoires** | Pro Eintrag zuerst die **Zonen** wählen („Wählen…“, z. B. `buckel`, `schulter_l`), dann den **Typ** (Basaltbrocken, Steinplatte, Felszacke) und die Einstellungen: Anzahl, Größe (in cm angezeigt), Größen-Zufall, Ausrichtung, Neigung, Einsinken, Seed („Neu würfeln“ = andere Verteilung). Bei `_l`-Zonen setzt **Spiegeln** automatisch das Gegenstück rechts. Unten wählt man einen Typ und klickt „Accessoire hinzufügen“. |
| **Datei & Kennzahlen** | Name, **Umgebungs-Gruppe** (z. B. `H lebensfeindlich`, `D stein`) und Biom, Budget-Klasse, Seed der Variante, „Freigegeben“. Darunter die Kennzahlen: Tris (Basis + Accessoires), Materialien, Texturen, Knochen. Ganz unten steht, ob die gebackene Fassung noch aktuell ist. |

### 4. Speichern, Neu, Laden
- **Speichern** schreibt die Varianten-Datei `creatures/<NN_name>/varianten/<id>.variant.json`. Ein `*` am Knopf heißt:
  Es gibt ungespeicherte Änderungen.
- **Neu**: ID (z. B. `rimehide_salzkruste`), Name und Umgebungs-Gruppe eingeben, dann „Anlegen“. Die neue Variante
  startet mit allen Werten des Gruppen-Presets.
- **Laden** liest die Datei neu von der Festplatte, z. B. wenn sie jemand anderes geändert hat.
- Gespeichert werden nur Kopf, Statur und die **Abweichungen vom Gruppen-Preset**. Ändert man das Preset später, ändern
  sich alle Varianten dieser Gruppe mit.

### 5. Backen
- Knopf **Backen** (oben rechts). Ergebnis unter `Assets/VariantKit/Baked/<Name>/`:
  - `<Name>.prefab`: das fertige Monster (1 SkinnedMeshRenderer, 1 Material, Clips des Bären)
  - `<Name>_mesh.asset`: Körper + Bedeckung + Accessoires in einem Mesh
  - `<Name>.mat`: das eine Material (seit M2 „VariantKit/Baked“ mit gebackenen Texturen)
  - `<Name>_Albedo.png`, `<Name>_Maske.png`, ggf. `<Name>_Leuchten.png` und `<Name>_Normal.png` (je 1024², Boss 2048²)
- Hat die Variante Bedeckungs-Lagen, vorher **„In Blender bauen“** drücken (Teil C). Sonst warnt das Backen.
- Außerdem schreibt das Backen die Instanzen-Liste `<id>.instanzen.json` neben die Varianten-Datei und trägt den Block
  `_gebaut` ein (Tris, Ampeln, Datum).
- Das Prefab in eine Szene ziehen. Die Animation steuert man wie bei den anderen Kreaturen (Clips `Quadruped_Bear_*` aus
  `Assets/VariantKit/Generated/Bases/RimehideBear/RimehideBear.fbx`).

---

## Teil B – Entwickler-Notiz

### Ordner (gekapselt, CreatureImporter und Kreaturen unverändert)
```
Unity_Creature_Test/Assets/
  Editor/VariantKit/            Assembly „VariantKit.Editor“ (eigene asmdef → Fehler hier brechen den CreatureImporter nicht)
    VariantKitWindow.cs         Fenster (IMGUI), Vorschau über PreviewRenderUtility (eigene Vorschau-Szene, ändert keine Nutzer-Szene)
    VkJson.cs                   kleiner JSON-Leser/-Schreiber mit fester Feldreihenfolge, Merge/Diff nach Spec 5.4, fnv1a32
    VkSpec.cs                   alle Zahlen der Spec: Regler + Ampel-Zonen, Typ-Standards, Farbgruppen, Ebenen, Budget
    VkDoc.cs                    Varianten-Datei: Laden (Preset → Biom → Datei), Speichern (nur Abweichungen, atomar, Revisions-Schutz), Hash
    VkBase.cs                   Basis-Import (eigene FBX-Kopie, lesbar), Analyse im Mesh-Raum, Andock-Zonen (VkZones)
    VkBuilder.cs                Statur-Formziele → Mesh, Platzierung der Accessoires, Zusammenführen zu 1 Mesh, Material, Statur-Knochen
    VkBake.cs                   Backen → Prefab/Mesh/Material, Instanzen-Liste, _gebaut; Import-Einstellungen (VkImport)
    VkBatch.cs                  Selbstprüfung headless (Bilder + Sitz-Messung)
  VariantKit/
    Scripts/VariantStatur.cs    Laufzeit-Komponente (Assembly „VariantKit.Runtime“): Knochen-Statur nach der Animation
    Shaders/VariantLayered.shader  „VariantKit/Layered“: Farbgruppen + bis zu 8 Ebenen, Built-in RP, Surface-Shader
    Generated/Bases/<Name>/     Kopien der Basis-FBX + Texturen (erzeugt, nicht versioniert)
    Baked/<Name>/               gebackene Varianten (erzeugt, nicht versioniert; Spec 6.2)
```
Pipeline-Seite:
```
creatures/32_rimehide_bear/varianten/<id>.variant.json   Quelle der Wahrheit (versioniert)
creatures/32_rimehide_bear/varianten/<id>.instanzen.json abgeleitet (Accessoire-Instanzen für Blender)
templates/umgebungs_gruppen/lebensfeindlich.json, stein.json   Gruppen-Presets H und D
rigging/quadruped_zonen.json                             Andock-Zonen Vierbeiner
procedural/bausteine/make_bausteine.py                   Baustein-Bibliothek (Blender headless) → <typ>.fbx/.glb/.json
```

### Ablauf einer Rechnung (Vorschau = Backen)
1. **Basis** (`VkBase.Load`): FBX nach `Assets/VariantKit/Generated/Bases` kopieren (nur wenn neuer), Import Generic + Read/Write,
   eingebettete Texturen herausziehen. Analyse: Körperachsen aus den Knochen (vorn = Hüfte → Kopf, links = Seite von Leg_FL_1),
   Kreaturgröße L, Knochen-Enden, Rumpf-Querschnitt, Farbgruppen der Basis (dunkle Texturpixel = Krallen/Nase/Augen je nach
   Körperstelle, lose kleine Teile am Kopf = Fangzähne → `horn`).
2. **Zonen** (`VkZones`, Definition `rigging/quadruped_zonen.json`): pro Vertex eine weiche Maske aus Skin-Gewichten, Abschnitt
   entlang eines Knochens, Abschnitt entlang der Körperachse, relativer Höhe im Rumpf und Flächenrichtung. Sammelnamen (z. B.
   `ruecken_gesamt`) = Maximum der Teilzonen. `rueckenlinie` = Strahl von oben entlang der Mittellinie.
3. **Statur S** (Formziele: Rumpfhöhe/-dicke, Buckel, Gliederdicke, Kopfbreite, Schnauze): Verschiebung der Vertices mit
   weichen Masken, direkt ins Mesh. Kein Blendshape, zur Laufzeit kostenlos.
4. **Accessoires** (`VkBuilder.Place`): Kandidatenpunkte flächengewichtet in der Zone (Seed pro Eintrag = fnv1a32("seed:id")),
   Verteilung einzeln/streuen/cluster/reihe/kranz, Ausrichtung + Neigung + Zufall, Einsinken. Gespiegelte Seite wird
   gespiegelt und auf die Haut der Gegenseite gesetzt. **Bindung `anker`** (E4): alle Vertices des Teils bekommen die
   Gewichte des Ansatzpunkts (baryzentrisch aus dem Dreieck, auf 4 Knochen gekürzt). `knochen` = 100 % am stärksten Knochen,
   `haut` = jeder Vertex die Gewichte des nächsten Hautpunkts.
5. **Zusammenführen**: Basis + Teile → 1 Mesh, 1 Submesh, gleiche Bindeposen. Zusatzkanäle: TEXCOORD2 Farbgruppe/Zufall,
   TEXCOORD3 Ruhe-Position im Körperraum (Muster kleben am Körper), TEXCOORD4 Ruhe-Normale, TEXCOORD5/6 Masken der 8 Ebenen.
6. **Material**: Shader „VariantKit/Layered“, alle Werte als Material-Parameter (Farbgruppen `_G0..8*`, Ebenen `_L0..7*`).
7. **Statur K/G** (Knochenlängen): Komponente `VariantStatur` – Beine, Pranken, Kopf, Schwanz gleichmäßig skaliert mit Ausgleich
   am Kind; Rumpf- und Halslänge über Verschieben der Kinder entlang der Knochenachse; Spurbreite und Bodenhöhe als Versatz.

### Abweichungen von der Spec (mit Grund)
| Spec | M1 | Grund |
|---|---|---|
| Andock-Zonen werden in Blender erzeugt und als `<Name>_zonen.json` exportiert | Unity rechnet die Zonen selbst aus `rigging/quadruped_zonen.json` (JSON statt TOML) | M1 hat keine Blender-Brücke; Unity braucht die Zonen live. Die Definition ist skelett-weit und funktioniert für jeden Vierbeiner mit Standard-Knochennamen. Korrekturen pro Kreatur (`[zonen.<id>]` in `creature.toml`) fehlen noch. |
| Statur S als Shape Keys aus Blender | Formziele direkt beim Zusammenbau ins Mesh gerechnet | Gleiches Ergebnis ohne Blendshapes, kostet zur Laufzeit nichts. Die Formeln stehen in `VkBuilder.ApplyShape`. |
| Statur K: Ruhepose in Blender einbacken | Laufzeit-Komponente `VariantStatur` (LateUpdate) im gebackenen Prefab | Ohne Blender-Backen bleibt nur die Knochen-Skalierung nach der Animation. Kosten: wenige Transform-Zugriffe pro Gegner. Die Vorschau ist eine Näherung (Beine werden mit der Länge auch etwas dicker). |
| Backen: Ebenen per UV-Render in Albedo/Maske/Normal (1024²) | ~~Ebenen bleiben Shader-Parameter~~ **seit M2 erledigt** (Teil D) | – |
| Baustein-Bibliothek `procedural/bausteine/<typ>.json` = Werte, Meshes in `<typ>.fbx` | `<typ>.json` enthält zusätzlich die Meshes; Unity liest das JSON, FBX/GLB bleiben die Standard-Ablage | Achsen eindeutig (X vorn, Y links, Z oben wie in Blender), keine FBX-Achsen-Umrechnung nötig. |
| Bausteine aus der Werkbank (Geometry Nodes mit Live-Reglern) | ~~bmesh-Skript~~ **seit M2 Werkbank** (Teil C/D); die 3 M1-Typen behalten ihre bmesh-Formen, bis man sie in der Werkbank neu speichert | – |
| Masken-Feld `rand` | fester weicher Übergang (≈ 2,5 % der Größe) | genügt für M1; `rauschen` und `oben` wirken pro Pixel. |
| Feldreihenfolge „wie in der Spec“ | Kopf in fester Reihenfolge, innerhalb von Einträgen die Reihenfolge der Quelle | einfacher, bleibt trotzdem git-stabil. |
| Leuchten (Emission) | ohne Bloom wird die Helligkeit farbtonerhaltend begrenzt | Built-in ohne HDR-Bloom brennt 4× Orange sonst nach Gelb aus. |

### Selbstprüfung (headless)
```
& "D:\Unity\6000.3.28f1\Editor\Unity.exe" -batchmode -projectPath "<pfad>\01_kreatur_pipeline\Unity_Creature_Test" `
  -executeMethod VariantKit.VkBatch.Run -logFile <log>
# optional: -vkVariants "pfad1;pfad2"   -vkShots <ordner>   (Standard: alle varianten/*.variant.json, temp/vk_shots)
```
Backt jede Variante und rendert nach `temp/vk_shots/`: `<Name>_arpg_rest/side_rest/front_rest/design_view.png`,
`_walk_15/40/64`, `_attack2_30/55/80`, `_attack2_55_side`, `_fenster_walk` (gleiche Vorschau wie im Fenster). Danach misst sie
den **Sitz der Accessoires**: Unterseite jedes Teils gegen den nächsten Hautpunkt, Abstand entlang der Hautnormale, in Walk, Run,
Attack1, Attack2, Idle und TurnLeft (je 17 Zeitpunkte) gegen die Ruhepose. Ergebnis in `selbstpruefung.json`. Läuft das Projekt
gerade im Editor des Nutzers, startet der Batch nicht: dann das Projekt schließen oder eine Kopie benutzen (siehe README).

### Bekannte Grenzen
- Teile mit Bindung `anker` sind formstabil. An Stellen mit großen, stark gebogenen Dreiecken (Buckel, Rücken beim
  Aufrichten, Unterarm) weicht die Haut darunter um 2–5 cm ab. `einsinken` versteckt das Einsinken, sichtbar wäre nur
  das Abheben. Für Platten über Gelenken gibt es `bindung: "haut"`.
- Die Zonen sind für den Standard-Vierbeiner gebaut. Andere Skelette brauchen eigene `rigging/<skelett>_zonen.json`.
- Das Fenster zeigt die Statur nur angenähert (Knochen-Skalierung). Das exakte Ergebnis kommt mit dem Blender-Backen.

---

## Teil C – Meilenstein 2: Kurzanleitung (ohne 3D-Erfahrung)

### C1. Blender-Panel öffnen (ohne Installation)
1. Doppelklick auf **`procedural/variantkit_blender/Varianten_Blender.cmd`**. Blender startet mit dem Varianten-Panel.
   (Steht Blender nicht unter `D:\Blender\blender.exe`, den Pfad oben in der .cmd-Datei anpassen.)
2. Das Startbild von Blender wegklicken. Rechts im 3D-Fenster ist die **Seitenleiste** offen (sonst Maus ins 3D-Fenster,
   Taste **N**). Ganz rechts senkrecht den Reiter **„Variante“** anklicken. Die Leiste lässt sich am linken Rand breiter ziehen.
3. Oben **Basis** (z. B. RimehideBear) und **Variante** (z. B. `rimehide_eisriese.variant.json`) wählen, **Laden** klicken.
   Der Bär erscheint mit Rig, Clips, Bedeckung und den Accessoires aus Unity.
4. **Clip** wählen (Walk, Attack2 …) und ▶ drücken – die Regler wirken auch während der Clip läuft.
   **ARPG-Ansicht** stellt die Spielkamera ein (schräg von oben).
5. Regler ändern, dann **Speichern**. Das schreibt in dieselbe Varianten-Datei wie Unity (`creatures/<NN>/varianten/`).

Andere Wege: `blender.exe --python procedural/variantkit_blender/vk_start.py -- --variante <datei>` (lädt die Datei gleich
mit), oder in Blender „Scripting“ → `vk_start.py` öffnen → ▶. Als Add-on: Ordner `variantkit` zippen,
Bearbeiten › Einstellungen › Add-ons › „Install from Disk“.

### C2. Was die Bereiche im Panel tun
| Bereich | Inhalt |
|---|---|
| Kopf | Basis, Variante, Laden/Speichern (Stern = ungespeichert; „Überschreiben“ erscheint, wenn Unity die Datei inzwischen gespeichert hat), Clip, ARPG-Ansicht, Accessoires zeigen. **Budget-Zeile:** Tris der Bedeckung gegen das Budget der Klasse (normal 2.000 / elite 3.000 / boss 5.000) und Gesamt-Tris (Basis + Bedeckung + Accessoires). |
| **1 · Statur** | die 17 Regler wie im Unity-Fenster (gleiche Bereiche bis Gelb, gleiche Ampel), dazu „Masse“. Formziele wirken als Shape Key, Knochenlängen als Pose-Skalierung. |
| **2 · Bedeckung** | Haut-Typ (wirkt nur im Unity-Shader) und **bis zu 2 Lagen** (E2): Typ **Fell, Federn, Stacheln, Platten**; Anzahl (steuert direkt die Tris), Länge (in cm angezeigt), Zufall, Richtung (entlang Knochen / hinten / unten / senkrecht), Anlege-Winkel, Form/Breite/Kanten/Krümmung (Fell), Dicke/Spitze (Stacheln), Größe/Ecken/Schuppung/Wölbung (Platten), Seed („Neu würfeln“). **Maske:** Zonen und „ohne“ über „Wählen…“, Oben/Unterseite, fleckiger Rand, „Länge pro Zone“ (z. B. Nacken 1,4). Überlappen sich die Masken beider Lagen, hat Lage 1 Vorrang (Warnung im Panel). |
| **3 · Baustein-Werkbank** | Form der Accessoire-Bausteine (Kristall, Platte, Pilz, Moospolster …) mit Live-Vorschau neben dem Bären. Typ + Form wählen, Regler ziehen, Namen eintragen, **Form speichern** → `procedural/bausteine/<typ>.json`. Unity nimmt die Form beim nächsten Aufbau. |
| Export | **Bedeckung für Unity exportieren** schreibt `creatures/<NN>/output/varianten/<Name>/<Name>.bedeckung.json` (macht der Unity-Knopf auch selbst). |

Accessoires werden **nur in Unity** platziert (E6). Blender zeigt sie nach der letzten Unity-Platzierung an
(`<id>.instanzen.json`, Knopf ↻ liest neu) und spart die Bedeckung darunter aus.

### C3. Unity-Knopf „In Blender bauen“
1. Unity öffnen, **Kreaturen › Varianten-Baukasten**, Variante wählen.
2. Oben auf **In Blender bauen** klicken. Unity speichert die Datei und die Instanzen-Liste und startet Blender unsichtbar
   im Hintergrund. Ein Fortschrittsbalken zeigt den Stand („Abbrechen“ möglich), Unity bleibt bedienbar.
3. Nach wenigen Sekunden erscheint die Bedeckung automatisch in der Vorschau. Die Zeile darunter nennt die Tris pro Lage.
   „Bedeckung veraltet“ heißt: Die Lagen in der Datei wurden geändert → noch einmal „In Blender bauen“.
4. **Backen** → Prefab mit Texturen (Teil A, Punkt 5).
5. Fehler zeigt das Fenster rot an, das Protokoll steht in `temp/vk2_blender_letzter_lauf.log`. Den Blender-Pfad stellt
   man unter „Datei & Kennzahlen“ ein.

Die Farben der Bedeckung (`bedeckung_1`, `bedeckung_2`, Ansatz → Spitze) stellt man im Unity-Reiter **Material** ein. Sie
wirken sofort, ohne neu zu bauen.

---

## Teil D – Meilenstein 2: Entwickler-Notiz

### Neue Dateien
```
procedural/variantkit_blender/
  Varianten_Blender.cmd · vk_start.py      Start mit Panel (ohne Installation)
  vk_headless.py                           Kommandozeile: bauen | bausteine | bild  (Ausgabe VK_FORTSCHRITT/VK_FERTIG/VK_FEHLER)
  variantkit/                              Add-on-Paket (bl_info), nur Blender + numpy
    vk_json.py    Varianten-Datei: Merge/Diff/Writer byte-gleich zu Unity VkJson/VkDoc (Rundlauf geprüft: kein Unterschied)
    vk_base.py    Basis anhängen (.blend), Analyse/Zonen/Statur-S wie Unity, Statur K als Pose (inherit_scale NONE)
    vk_cover.py   Geometry-Nodes-Gruppe „VK_Bedeckung“ + Masken + Export <Name>.bedeckung.json
    vk_parts.py   Baustein-Werkbank: 7 GN-Familien (zacke, platte, brocken, pilz, polster, streifen, kette)
    vk_acc.py     Accessoires aus <id>.instanzen.json anzeigen, Aussparen-Punktwolke
    vk_nodes.py   Helfer zum Bauen von Node-Bäumen
    vk_ui.py      Panel „Variante“, Eigenschaften, Operatoren
Unity_Creature_Test/Assets/Editor/VariantKit/
  VkCover.cs      Bedeckung aus Blender laden (Körperraum → Mesh, Gewichte nach Namen, Ansatz für den Statur-Versatz)
  VkBlender.cs    Blender-Prozess im Hintergrund (Fortschritt, Fehler, Abbrechen, Wait für den Batch)
  VkTexBake.cs    UV-Atlas + Textur-Backen + Spiel-Material
Unity_Creature_Test/Assets/VariantKit/Shaders/
  VariantLayers.cginc    gemeinsame Ebenen-Rechnung (Vorschau UND Backen)
  VariantBake.shader     „Hidden/VariantKit/Bake“ – UV-Raum-Render (Albedo, Maske, Leuchten, Normal)
  VariantBaked.shader    „VariantKit/Baked“ – Spiel-Shader, 1 Material
templates/umgebungs_gruppen/  + gemaessigt (A), feucht (B), sand (C), kalt (E), kueste (F), geologisch (G), aussergewoehnlich (I)
procedural/bausteine/         + 15 Typen: kristall, eiszacke, dorn, horn, seepocken, eisplatte, knochenplatte, sinterplatte,
                                pilze, moospolster, grasbueschel, moosfransen, tang, gehaenge, kette
creatures/32_rimehide_bear/varianten/  + rimehide_eisriese (Fell, Gruppe E), quillback_bear (Stacheln + Gesichtsfell, Gruppe D)
```
Geändert: `VkJson.cs` (Parser ohne `Substring` – große Dateien waren quadratisch langsam), `VkBase.cs` (Zonen-Kriterien
`ueber`, `nicht_knochen`), `VkSpec.cs` (Typ-Standards, Budget Bedeckung), `VkBuilder.cs` (Bedeckung als Instanzen;
`RestPose` setzt die Knochen-Skalierung zurück – vorher hing die Statur in der Ruhepose vom Vorzustand ab), `VkBake.cs`
(Texturen, `_gebaut.tris.bedeckung`), `VkBatch.cs` (`-vkBlender`, Vergleich Vorschau ↔ gebacken), `VariantKitWindow.cs`
(Knopf, Fortschritt, Bedeckungs-Farbgruppen, Blender-Pfad), `VariantLayered.shader` (nutzt die .cginc),
`rigging/quadruped_zonen.json` (`flanke_l/_r` neu – die alte Definition war beim Bären leer), `.gitignore`
(`creatures/*/output/varianten/` ist reproduzierbar).

### Bedeckung: Ablauf
1. **Python** rechnet pro Lage die Maske (Zonen ∪, minus „ohne“, oben/unten, fleckiger Rand, Modus Silhouette, Lage 2 weicht
   Lage 1) und den Längenfaktor pro Zone als Vertex-Attribute (`vk_maske_N`, `vk_laenge_N`), dazu einmal `vk_rest`
   (Ruhe-Position) und `vk_strich` (Strich-Richtung entlang der Knochen).
2. **Geometry Nodes** (`VK_Bedeckung`, ein Modifier pro Lage *vor* dem Armature-Modifier): Punkte per Poisson auf der
   *Ruhe*-Form verteilen (die Statur ändert die Verteilung nicht; Dichte = Anzahl / maskierte Fläche), unter Accessoires
   aussparen, pro Punkt Richtung (Strich, Anlege-Winkel, Zufall), Länge, Teil-Mesh (Fell spitz/rund/zackig/büschel, Feder,
   Stachel, Platte) instanzieren, an die *verformte* Haut setzen, Krümmung in Metern. Die Punkte erben alle Vertex-Gruppen →
   jedes Teil hat die Gewichte seines Ansatzpunkts (läuft mit, verformt sich nicht). Attribute `vk_lage`, `vk_teil`, `vk_h`
   (Ansatz → Spitze), `vk_anker`, `vk_rand`.
3. **Export** (Armature aus, Statur-Shape-Key 0): `<Name>.bedeckung.json` – Vertices im Körperraum / Kreaturgröße
   (x vorn, y oben, z links, Ursprung Mitte Begrenzungsrahmen → unabhängig von Blender- und Unity-Achsen), pro Teil Anker und
   höchstens 4 Gewichte nach Knochennamen, `quelle` = die Bedeckung, aus der gebaut wurde (Unity vergleicht → „veraltet“).
4. **Unity** (`VkCover`) legt jeden Ansatz einmal auf die Basis (nächstes Dreieck). Statur S verschiebt das Teil um den
   Versatz des Ansatzes. Farbgruppe `bedeckung_1/2`, Muster kleben an der Ruhe-Position, Masken der Material-Ebenen am Ansatz.

### Textur-Backen: Ablauf
- **Atlas** (`VkTexBake.AtlasMesh`): Basis-UV verkleinert auf 80 % × 80 % oben links. Jedes Teil-Dreieck bekommt eine
  eigene Kachel (paarweise in Quadrate, Größe ∝ √Fläche, Regalpacken in die L-förmige Restfläche, Größe per Halbierung
  maximiert).
- **Render** im UV-Raum mit `Hidden/VariantKit/Bake` (gleiche `VKEval` wie die Vorschau) → Albedo, Maske
  (R Rauheit, G Puls-Anteil, B Glasig, A Rim-Maske), Leuchten (nur wenn etwas leuchtet), Normal (nur bei Facetten < 1),
  8 Pixel Rand-Auffüllung, PNG + Import-Einstellungen.
- **Spiel-Shader** „VariantKit/Baked“: Texturen, live nur Facetten-Look, Glasig-Fresnel, Rim und Puls.
- **Prüfung:** gleiche Kamera, Vorschau (Ebenen-Shader) gegen gebackene Fassung, mittlere Abweichung auf dem Körper
  (0–255): 0,4 – 1,9 bei allen vier Varianten.

### Selbstprüfung M2
```
temp/vk2_work/run_batch.sh -vkBlender -vkShots <ordner>     # Unity 6000.3.28f1: Bedeckung in Blender bauen, backen, rendern, vergleichen
"D:\Blender\blender.exe" -b --factory-startup -P procedural/variantkit_blender/vk_headless.py -- bauen --variante <datei>
"D:\Blender\blender.exe" -b --factory-startup -P procedural/variantkit_blender/vk_headless.py -- bild --variante <datei> --out <ordner> --clip Walk --bild 12
```
Ergebnis 2026-11-22 (`temp/vk2_shots/selbstpruefung.json`):

| Variante | Tris gesamt (Basis + Bedeckung + Acc.) | Bedeckung | Material | Texturen | Sitz Bedeckung in Clips | Vorschau ↔ gebacken |
|---|---|---|---|---|---|---|
| Eisriese (Fell, E) | 5.397 (3.944 + 1.095 + 358) | 365 Zotteln | 1 | Albedo, Maske, Leuchten 1024² | +5,4 / −3,1 cm | 1,7 |
| Quillback (Stacheln + Gesichtsfell, D) | 6.452 (3.944 + 2.508 + 0) | 284 Teile | 1 | Albedo, Maske 1024² | Stacheln ±1 cm, Fell +2,8 / −2,3 cm | 0,6 |
| Slagback (M1) | 4.550 (3.944 + 0 + 606) | – | 1 | Albedo, Maske, Leuchten 1024² | – | 1,4 |
| Cragplate (M1) | 4.682 (3.944 + 0 + 738) | – | 1 | Albedo, Maske 1024² | – | 1,5 |

„In Blender bauen“ dauert ca. 1 s (mit Blender-Start). Alle Varianten liegen im Elite-Budget (≤ 9.000, Bedeckung ≤ 3.000).
30 Knochen, keine zusätzlichen. M1-Varianten: Instanzen-Listen unverändert (gleiche Platzierung), nur `_gebaut` ist neu.
Gegenprobe CreatureImporter in einer Projekt-Kopie (`CreatureImporter.Batch`, Unity 6000.3.28f1): 14 Kreaturen, alle Clips
bewegen sich, Bodenwerte identisch zu M1 (`temp/vk2_work/importer_check.log` gegen `temp/vk_work/importer_check.log`).

### Abweichungen von der Spec (M2, mit Grund)
| Spec | M2 | Grund |
|---|---|---|
| Blender-Panel `procedural/variant_panel.py` | Paket `procedural/variantkit_blender/variantkit/` + Start-Skript | mehrere Module (Datei, Basis, Bedeckung, Werkbank, Panel); als Add-on installierbar, aber auch ohne Installation startbar. |
| Statur S: 12 Shape Keys (plus/minus) | 1 Shape Key „VK_Statur“, bei jeder Regleränderung aus denselben Formeln wie in Unity neu gerechnet | gleiche Rechnung in beiden Programmen (Spec 0.4: Formeln exakt festgelegt), weniger Daten. |
| Statur K in Blender | Pose-Skalierung (Kinder erben keine Skalierung) + Copy-Location-Empties für die Spurbreite + Rig anheben | Die Clips keyen Ort und Drehung aller Knochen, aber keine Skalierung. So bleibt der Clip unverändert. Wie in Unity nur eine Vorschau. |
| Andock-Zonen nur in Unity | Blender rechnet die Zonen zusätzlich selbst (gleiche Definition `rigging/quadruped_zonen.json`, gleicher Code) | Blender braucht die Masken live für die Lagen. Der Zonen-Export aus Blender ist nicht Teil von M2. |
| Geometrie backen (Zusammenführen, UV-Atlas) in Blender | Zusammenführen + Atlas in Unity, nur die Bedeckung kommt aus Blender | Seit M1 setzt Unity Basis + Accessoires zusammen, das Atlas muss alle Teile kennen. Das Textur-Backen ist laut Spec ohnehin Unity. |
| Bedeckungs-Export als FBX | `<Name>.bedeckung.json` (+ auf Wunsch GLB mit `--glb`) | wie die Baustein-Bibliothek achsen-eindeutig (Körperraum), Gewichte nach Knochennamen, keine FBX-Achsen-Umrechnung. |
| Maske: R Rauheit, G Emission, B Glasig/Nässe, A frei | R Rauheit, G Puls-Anteil, B Glasig, A Rim-Maske; Leuchten als eigene Textur (nur wenn etwas leuchtet) | Glut und Augen haben eigene Farbtöne. Eine einzelne Emissions-Maske verliert den Farbton. Nässe steckt schon in Albedo + Rauheit. |
| Normal-Map bei Haut leder/schuppen | Normal nur bei `facetten` < 1 | Bei vollem Facetten-Look (Standard) ersetzt der Shader die Normale, die Textur hätte keine Wirkung. Haut-Relief (Falten/Schuppen) rechnet der Ebenen-Shader noch nicht. |
| Lagen-Masken überlappen nur am weichen Rand | Lage 2 wird dort automatisch ausgeblendet, wo Lage 1 wächst (Warnung ab 15 % Überlappung) | einfache, eindeutige Regel für E2. |
| Glasig-Fresnel vor den Ebenen | nach den Ebenen aufaddiert | gleiche Rechnung in Vorschau und Spiel-Shader. |

### Reste (nicht in M2)
- **Statur-Klassen** mit neu gebackenen Clips (E3), Ruhepose in Blender einbacken.
- **LODs** (LOD1/LOD2, `weg_ab_lod`).
- **Partikel** aus `effekte`.
- **Zonen-Export aus Blender** (`<Name>_zonen.json`), Zonen-Korrekturen pro Kreatur.
- `schwingen` der Lagen und schwingende Accessoires (dangling): Feld vorhanden, noch ohne Wirkung. Gehänge (Fransen,
  Tang, Ketten) hängen noch nicht nach unten (`auf`/`stelle` fehlen in der Unity-Platzierung).
- Fell-Modus `nur_shader` (Strich-Textur), Feder-`kiel`, Haut-Relief `leder`/`schuppen` im Shader.
- Datei-Beobachtung mit automatischem Neu-Laden (Spec 6.2). Jetzt: Revisions-Schutz + Knopf „Neu laden“.
- Startwerte der neuen Presets und Bausteine sind Platzhalter (der Nutzer stellt sie ein).
