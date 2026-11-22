# Varianten-Baukasten (Unity) – Meilenstein 1

Stand 2026-11-22 · Werkzeug-Version 0.1.0 · Grundlage: `docs/VARIANTEN_SPEC.md` (Entscheidungen E1–E8).
M1 umfasst Statur, Accessoires, Material-Ebenen und das Backen in Unity. **Noch nicht enthalten:** Bedeckung
(Fell, Stacheln, Platten als Lage), die Blender-Brücke („In Blender bauen“), die Blender-Live-Regler und das Backen von
Texturen. Die Liste der Reste steht am Ende.

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
  - `<Name>_mesh.asset`: Körper + Accessoires in einem Mesh
  - `<Name>.mat`: das eine Material
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
| Backen: Ebenen per UV-Render in Albedo/Maske/Normal (1024²) | Ebenen bleiben Shader-Parameter am einen Material | Im Auftrag für M1 so erlaubt. Für das Textur-Backen fehlt ein gemeinsames UV-Atlas für Körper + Bausteine (Blender-Schritt). Folge: Der Ebenen-Shader läuft auch im Spiel (1 Material, 1 Draw Call, aber mehr Rechenarbeit pro Pixel). |
| Baustein-Bibliothek `procedural/bausteine/<typ>.json` = Werte, Meshes in `<typ>.fbx` | `<typ>.json` enthält zusätzlich die Meshes; Unity liest das JSON, FBX/GLB bleiben die Standard-Ablage | Achsen eindeutig (X vorn, Y links, Z oben wie in Blender), keine FBX-Achsen-Umrechnung nötig. |
| Bausteine aus der Werkbank (Geometry Nodes mit Live-Reglern) | einfaches bmesh-Skript mit festen Werten pro Form | Blender-Live-Regler sind laut Auftrag M2. Die Werte stehen pro Form im Skript und im JSON. |
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
