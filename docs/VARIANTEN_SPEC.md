# Varianten-Spezifikation – alle Eigenschaften des Schichtmodells

Stand 2026-11-21 · Status: **Spezifikation entschieden (Nutzer 2026-11-21, E1–E8 siehe Abschnitt 7), noch nichts
gebaut** (BACKLOG G9, Teil 2).
Beispiel-Kreatur durchgehend: Rimehide Bear (`creatures/32_rimehide_bear/`, Skelett `quadruped`, Muster `quadruped/bear`)
mit den 7 Varianten-Bildern des Nutzers in `creatures/32_rimehide_bear/input/Varianten/`.

**Entscheidungen des Nutzers (2026-11-21), die hier gelten:**
- Der Baukasten ist **hybrid**:
  - **Unity:** ein Regler-Fenster mit Live-Vorschau für Statur, Accessoires an Knochen und Material-Ebenen. Dazu der
    Knopf **„In Blender bauen“** für die Bedeckung (Blender headless, Geometry Nodes, Export, Auto-Import) und am Ende
    **„Backen“** zu 1 Mesh + standardmäßig 1 Material pro Variante (Material-Regel siehe 6.4).
  - **Blender** bekommt **zusätzlich Live-Regler** (eigenes Panel bzw. Geometry-Nodes-Eingänge), damit man ein Gefühl
    für die Werte bekommt, z. B. bei Platten.
- **Eine gemeinsame Varianten-Datei pro Variante** ist die einzige Quelle der Wahrheit. Unity und Blender lesen und
  schreiben sie.
- **Zuerst die Eigenschaften durchdefinieren** (dieses Dokument), dann bauen.
- **Umgebungs-Gruppen als Haupt-Achse** (Nutzer 2026-11-21, `docs/biome_uebersicht.webp`): 9 Gruppen A–I → pro
  Monster bis zu 9 Varianten, je über ein wiederverwendbares Gruppen-Preset. Sondervarianten (Kristall, Schwefel,
  Vulkan, Hölle, Himmel, Abyss) später. Schwefelebene, Hölle und Himmel sind zugleich **MVP-Biome** in H bzw. I
  (bestätigt, Nutzer 2026-11-21). Siehe Abschnitt 5.
- **Material-Regel** (Nutzer 2026-11-21, E5): Standard **1 Material** pro gebackener Variante, ein 2. Material nur für
  echte Transparenz, additive Effekte oder Spezial-Shader, mehr als 2 nur bei Bossen. Siehe 6.4.

Wer nur einen Überblick will: Abschnitt 0 lesen, dann die Tabellen in 1–4 überfliegen, dann 5 (Umgebungs-Gruppen) und 7 (Entscheidungen E1–E8).

---

## 0. Kurz erklärt

### 0.1 Die vier Schichten

| Schicht | Was | Beispiel Bär | Technik in einem Satz |
|---|---|---|---|
| **1 Statur** | Größe und Proportionen des Grundkörpers | Quillback: länger, flacher, kurze Beine | Knochen länger/kürzer machen und wenige Formziele (Shape Keys) |
| **2 Bedeckung** | die Haupt-Oberfläche: Haut, Leder, Schuppen, Fell, Federn, Stacheln, Platten | Eisriese: weißes Zottelfell überall | Haut-Arten nur im Shader; Fell/Stacheln/Platten als viele kleine Teile per Geometry Nodes |
| **3 Accessoires** | Zusatzteile an bestimmten Körperstellen | Slagback: Basaltbrocken auf dem Buckel | fertige Bausteine (Kristall, Platte, Pilz …) werden an „Andock-Zonen“ verteilt und hängen starr am Körper |
| **4 Material-Ebenen** | Farbe und Look über allem, auch mehrere Ebenen | Slagback: Rußschwarz + glühende Risse | Shader-Ebenen in der Vorschau, beim Backen in Texturen eingebrannt |

### 0.2 Fachbegriffe

| Begriff | Bedeutung |
|---|---|
| **Mesh** | das 3D-Modell aus Dreiecken. |
| **Tris** | Anzahl der Dreiecke. Das ist das Hauptmaß für die Kosten eines Modells. Die Bär-Basis hat ca. 4.000. |
| **Knochen / Rig** | unsichtbares Skelett im Modell. Clips (Animationen) drehen die Knochen, die Haut folgt. |
| **Gewichte** | legen fest, wie stark ein Punkt der Haut welchem Knochen folgt. |
| **Ruhepose** | Grundhaltung des Modells ohne Animation. |
| **Shape Key** (in Unity: Blendshape) | gespeichertes Formziel, z. B. „dicker Bauch“. Ein Regler 0…1 blendet stufenlos dorthin über. |
| **Geometry Nodes** (GN) | Blenders Baukasten für prozedurale Geometrie: Werte rein, Geometrie raus, z. B. 300 Stacheln auf dem Rücken verteilen. |
| **Baustein** | ein kleines fertiges Teil-Mesh (Kristall, Platte, Pilz) aus der Baustein-Bibliothek. |
| **Instanz** | ein konkretes Exemplar eines Bausteins an einer Stelle, mit Größe und Drehung. |
| **Andock-Zone** | benannte Körperstelle (z. B. `schulter_l`), an der Accessoires sitzen dürfen. Dieselben Namen dienen als Masken. |
| **Maske** | legt fest, *wo* etwas gilt: 0 = gar nicht, 1 = voll, dazwischen weicher Übergang. |
| **Shader** | Programm auf der Grafikkarte, das die Farbe jedes Pixels berechnet. |
| **Material** | ein Shader plus seine Einstellungen und Texturen. |
| **Draw Call** | ein Zeichen-Auftrag an die Grafikkarte. Jedes Material eines Modells kostet einen. Viele Gegner × viele Draw Calls = langsam. |
| **Textur / Atlas** | ein Bild, das auf das Modell geklebt wird. Ein Atlas fasst die Bilder vieler Teile in einem Bild zusammen. Dann reicht 1 Material. |
| **UV** | legt fest, welcher Punkt der Textur auf welchem Punkt des Modells landet. |
| **Normal Map** | Textur, die feine Unebenheiten nur vortäuscht (Schuppen, Falten), ohne zusätzliche Dreiecke. |
| **Emission** | Selbstleuchten, z. B. Glut. |
| **Rim-Light** | heller Rand an der Silhouette, wie Gegenlicht. Macht Elite-Gegner von oben gut erkennbar. |
| **Backen** | alles Live-Berechnete endgültig festschreiben: 1 Mesh, standardmäßig 1 Material (Ausnahmen siehe 6.4), fertige Texturen. Danach kostet die Variante im Spiel nicht mehr als ein normales Modell. |
| **Seed** | Startzahl für den Zufall. Gleicher Seed = exakt gleiches Ergebnis, damit alles reproduzierbar bleibt. |
| **LOD** | „Level of Detail“: vereinfachte Fassungen für große Entfernung (LOD1 ≈ halbe Tris, LOD2 ≈ ein Viertel). |
| **dangling** | unser Baustein für frei schwingende Teile *ohne* Knochen (`rigging/dangling.py`, Unity-Shader `Creature/Standard Dangling`). |
| **double_sided** | macht einseitige dünne Flächen (Moosfransen, Barteln) von beiden Seiten sichtbar (`rigging/double_sided.py`). Verdoppelt deren Tris. |

### 0.3 Einheiten und Konventionen (für alle Schichten)

- **Faktoren** (Statur): `1.0` = wie die Basis. `1.2` = 20 % mehr.
- **Längen** (Accessoires, Bedeckung, Muster): als **Anteil der Kreaturgröße** = längste Kante des Begrenzungsrahmens
  der Basis, wie bei `dangling`. Beim Bären (ca. 2,4 m lang) ist `0.05` also etwa 12 cm. Die Werkzeuge zeigen
  zusätzlich cm an, gespeichert wird der Anteil. So passen Werte auch auf andere Kreaturen.
- **Winkel** in Grad. **Anteile/Stärken** 0…1.
- **Farben** als `"#RRGGBB"` (sRGB, wie in jedem Malprogramm). Leuchtstärke immer als eigene Zahl (`intensitaet`,
  `leuchten`), nie in der Farbe.
- **Richtungen** immer körperbezogen (vorn, hinten, oben, außen), nie als Blender- oder Unity-Achse. Die Achsen
  unterscheiden sich zwischen beiden Programmen.
- **Feldnamen**: deutsch, klein, ASCII, Unterstrich (`bein_laenge_vorn`), wie die bestehenden Felder (`eigene_basis`).
- **Links/Rechts** = die eigene Seite der Kreatur (wie `left.png`/`right.png`, README Bär).

### 0.4 Grundregel „Jede Berechnung genau einmal“

Damit Unity und Blender nie zwei verschiedene Ergebnisse zeigen, wird jede Rechnung in **genau einem** Programm
umgesetzt. Das andere zeigt nur das Ergebnis an. Einzige Ausnahme ist die Statur: Deren Formeln sind trivial
(Längen mal Faktor) und sind hier exakt festgelegt.

| Rechnung | Wo umgesetzt | Das andere Programm … |
|---|---|---|
| Statur (Knochenlängen, Shape Keys) | beide, nach den Formeln in Abschnitt 1 | – |
| Bedeckung (Fell, Stacheln, Platten verteilen) | **Blender** (Geometry Nodes) | Unity zeigt das importierte Ergebnis |
| Baustein-Formen (Kristall, Platte, Pilz …) | **Blender** (Baustein-Werkbank) | Unity nutzt die exportierte Bibliothek |
| Accessoires platzieren (welche Instanz wohin) | **Unity** (C#) | Blender liest die Instanzen-Liste und zeigt sie an |
| Material-Ebenen | **Unity** (Vorschau-Shader, Backen per UV-Render) | Blender zeigt nur eine Annäherung (Grundfarben, Glühen) |
| Geometrie backen (Zusammenführen, Gewichte, UV-Atlas, LODs) | **Blender** | Unity startet es per Knopf |

---

## 1. Schicht 1 – Statur

### 1.1 Was die Regler tun

Zwei Techniken:
- **Knochenlänge** (Typ `K`): Ein Knochen wird länger oder kürzer, die Haut daran wird mitgestreckt. Die Clips drehen
  nur Knochen, deshalb funktionieren sie weiter. Grenzen siehe 1.3.
- **Formziel / Shape Key** (Typ `S`): verändert die Form der Haut, *nicht* die Knochen. Für die Clips unsichtbar.
  Shape Keys werden **prozedural** in Blender erzeugt (Verschieben entlang der Normalen bzw. nach vorn, mit weicher
  Maske über die Zonen aus 3.2), nicht von Hand modelliert. Pro Basis gibt es 6 Stück (siehe Tabelle).
- Typ `G` (gesamt): Skalierung des ganzen Modells am Wurzelknochen.

In der Varianten-Datei stehen **immer alle 17 Regler** (auch wenn sie 1.0 sind). Das ist lesbarer und eindeutig.
Im Unity-Fenster gibt es zusätzlich den **Makro-Regler „Masse“**: Er bewegt `rumpf_dicke` und `glied_dicke`
gemeinsam. Gespeichert werden nur die beiden Einzelwerte.

### 1.2 Regler-Tabelle

Knochennamen = Standard-Skelett `quadruped` (`motions/quadruped/README.md`). Ob der Bär davon abweicht (z. B. mehr
Wirbel), ermittelt der Bär-Agent → `creatures/32_rimehide_bear/README.md`, Abschnitt Rig. Bis dahin gelten die Namen
hier als **vorläufig**.

| # | Regler | Feld | Bedeutung | Typ | Bereich | Std | Betroffene Knochen (vorläufig) |
|---|---|---|---|---|---|---|---|
| 1 | Gesamtgröße | `groesse` | alles gleichmäßig größer/kleiner (Jungtier … Elite) | G | 0.5–2.0 | 1.0 | `Root` (gleichmäßig) |
| 2 | Körperlänge | `koerper_laenge` | Rumpf zwischen Schulter und Hüfte länger/kürzer | K | 0.8–1.4 | 1.0 | `Spine_1`, `Chest` (Länge); `Hips` bleibt |
| 3 | Rumpfhöhe | `rumpf_hoehe` | Rumpf flacher (Quillback, Lurker) oder höher, ohne Beine zu ändern | S | 0.6–1.3 | 1.0 | – (Haut an `Hips`, `Spine_1`, `Chest`) |
| 4 | Rumpfdicke | `rumpf_dicke` | Bauch/Brust/Flanken dicker oder schlanker (Gewicht) | S | 0.8–1.3 | 1.0 | – (Haut an `Hips` … `Neck_1`) |
| 5 | Buckel | `buckel` | Höhe des Muskelbuckels über den Schultern; 0 = flach, 1 = Basis | S | 0.0–1.6 | 1.0 | – (Haut an `Chest` oben, Zone `buckel`) |
| 6 | Gliederdicke | `glied_dicke` | Beine dicker/dünner (Gewicht) | S | 0.8–1.3 | 1.0 | – (Haut an `Leg_*_1..3`) |
| 7 | Beinlänge vorn | `bein_laenge_vorn` | Vorderbeine länger/kürzer (ohne Pfoten) | K | 0.6–1.3 | 1.0 | `Leg_FL_1..3`, `Leg_FR_1..3` |
| 8 | Beinlänge hinten | `bein_laenge_hinten` | Hinterbeine länger/kürzer (ohne Pfoten) | K | 0.6–1.3 | 1.0 | `Leg_BL_1..3`, `Leg_BR_1..3` |
| 9 | Spurbreite | `spur_breite` | Beine weiter auseinander (breitbeinig, Lurker) oder enger | K | 0.8–1.6 | 1.0 | `Shoulder_FL/FR` (seitlich), Ansatz `Leg_BL/BR_1` |
| 10 | Pranken vorn | `pranken_vorn` | Vorderpfoten samt Krallen größer (Grabkrallen) | K | 0.8–1.6 | 1.0 | `Leg_FL_4`, `Leg_FR_4` (gleichmäßig) |
| 11 | Pranken hinten | `pranken_hinten` | Hinterpfoten größer | K | 0.8–1.5 | 1.0 | `Leg_BL_4`, `Leg_BR_4` |
| 12 | Halslänge | `hals_laenge` | Hals länger/kürzer | K | 0.7–1.5 | 1.0 | `Neck_1`, `Neck_2` |
| 13 | Kopfgröße | `kopf_groesse` | ganzer Kopf samt Kiefer größer/kleiner | K | 0.7–1.4 | 1.0 | `Head`, `Jaw` (gleichmäßig) |
| 14 | Kopfbreite | `kopf_breite` | Kopf breiter und flacher (Lurker) oder schmaler | S | 0.8–1.5 | 1.0 | – (Haut an `Head`, `Jaw`) |
| 15 | Schnauzenlänge | `schnauze_laenge` | Schnauze länger (Dachs, Eber) oder stumpfer | S | 0.8–1.6 | 1.0 | – (Haut vorderes Drittel `Head` + `Jaw`) ¹ |
| 16 | Schwanzlänge | `schwanz_laenge` | Schwanz länger/kürzer | K | 0.5–2.0 | 1.0 | `Tail_1..4` ² |
| 17 | Schwanzdicke | `schwanz_dicke` | Schwanz dicker/dünner | K (quer) | 0.6–1.6 | 1.0 | `Tail_1..4` (nur quer) |

¹ Das Standard-Skelett hat keinen Schnauzen-Knochen. Die Schnauze wird per Shape Key verlängert, der Kiefer
(`Jaw`) bekommt dazu dieselbe Länge, sonst klafft das Maul. Wird ein Biss-Clip mit langer Schnauze unsauber, braucht
das Skelett einen Knochen `Snout`. Das ist eine Erweiterung des Rigs, nicht dieser Spec.
² Die Bär-Basis hat nur einen Stummel. Über 1.5 wird der Stummel nur gestreckt und sieht nicht wie ein Schwanz aus.
Für lange Schwänze braucht es ein Accessoire „Schwanz-Aufsatz“ oder eine eigene Basis (VARIANTEN.md, Frage 2).

**Formeln (müssen in Unity und Blender gleich sein):**
- Knochenlänge: neue Länge = Basislänge × Faktor. Kindknochen wandern mit dem Ende des Elternknochens mit und behalten
  ihre eigene Länge.
- `spur_breite`: Ansätze der Beine seitlich um (Faktor − 1) × halber Basis-Spurbreite nach außen. Die Füße stehen dann
  entsprechend weiter außen.
- `pranken_*`, `kopf_groesse`, `groesse`: gleichmäßige Skalierung um den Knochenansatz.
- Shape Keys: Wert = (Faktor − 1) / (Max − 1) für Faktoren > 1 auf den Key „…_plus“, entsprechend für < 1 auf
  „…_minus“. Pro S-Regler gibt es also 2 Keys, insgesamt 12. `buckel`: 0…1 auf `buckel_minus`, 1…1.6 auf `buckel_plus`.
- **Bodenhöhe**: Nach jeder Änderung wird das Modell so verschoben, dass die Pfoten wieder auf dem Boden stehen.
  Hüfthöhe in den Clips × mittlerer Beinfaktor (siehe 1.3).

**Vorschau gegen Backen:** Die Unity-Vorschau darf die Knochenlängen annähern (z. B. Skalierung mit Ausgleich am
Kind). Das exakte Ergebnis entsteht beim Backen in Blender: Die neue Ruhepose wird eingebacken, die Shape Keys werden
fest angewendet und danach entfernt. Danach kostet die Statur zur Laufzeit nichts. Weichen Vorschau und gebackenes
Ergebnis im Begrenzungsrahmen um mehr als 3 % ab, meldet das Backen eine Warnung.

**Voraussetzung an die Clips (zu prüfen beim Bau):** Die gebackenen Clips dürfen nur an `Root` und `Hips` Positionen
enthalten, an allen anderen Knochen nur Drehungen. Sonst überschreiben die Clips die neuen Knochenlängen.

### 1.3 Ab wann brechen die gemeinsamen Clips? – **Vermutung Claude, nicht getestet**

Die Werte sind geschätzt aus dem Aufbau der Clips: IK-Füße, gebacken als reine Drehungen, Hüfthöhe als Position.
Sie müssen am echten Bären-Clip-Satz gemessen werden. Prüfung über die bestehenden Selbsttests: Fußkontakt,
Fußrutschen, Dehnung, Durchdringung.

| Regler | 🟢 Clips teilen | 🟡 Clips teilen + automatische Korrektur | 🔴 eigener Clip-Satz nötig | Was bricht zuerst |
|---|---|---|---|---|
| `groesse` | 0.5–2.0 | – | – | nichts. Laufgeschwindigkeit im Spiel × `groesse`, sonst rutschen die Füße. |
| `bein_laenge_vorn` und `_hinten` **gleich** | 0.9–1.1 | 0.8–1.2 (Hüfthöhe × Beinfaktor) | < 0.8 / > 1.2 | Füße schweben oder sinken ein, Schritt wirkt zu kurz/lang |
| Unterschied vorn ↔ hinten | ≤ 8 % | ≤ 15 % (Rumpf-Neigung korrigiert) | > 15 % | Rücken kippt, ein Beinpaar erreicht den Boden nicht |
| `koerper_laenge` | 0.9–1.1 | 0.8–1.2 | > 1.2 / < 0.8 | Vorder- und Hinterfüße treten ineinander bzw. Spreizschritt |
| `spur_breite` | 0.9–1.1 | 0.8–1.25 | > 1.25 | Beine stehen schräg, Füße rutschen seitlich |
| `rumpf_dicke`, `glied_dicke` | ≤ 1.15 | ≤ 1.25 | > 1.25 | Beine durchdringen Brust/Bauch (Prankenhieb, Aufrichten) |
| `rumpf_hoehe`, `buckel`, `kopf_*`, `schnauze_laenge` | ganzer Bereich | – | – | nichts (Shape Keys). Ausnahme: `rumpf_hoehe` < 0.75 → Bauch schleift im Gang. |
| `hals_laenge` | 0.8–1.25 | bis 1.5 | – | Biss-Reichweite ändert sich (Hitbox im Spiel anpassen) |
| `pranken_*` | ≤ 1.3 | ≤ 1.5 | > 1.5 | Pranken treffen sich beim Gehen |
| `schwanz_*` | ganzer Bereich | – | – | nichts. Langer Schwanz mit Stummel-Clip wirkt aber steif (ab 1.5 gelb). |

**Was „eigener Clip-Satz“ heißt:** Unsere Clips sind prozedural (`motions/quadruped/quadruped_kit.py` erzeugt sie
aus Fuß-Zielen und bäckt sie). Für Varianten in der roten Zone kann der Clip-Satz desselben Musters (`bear`) mit
den neuen Proportionen **neu gebacken** werden, ohne Handarbeit. Mehrere Varianten mit ähnlicher Statur teilen sich
dann eine **Statur-Klasse** (z. B. `bear` und `bear@flach`). Clip-Namen bleiben `Quadruped_Bear_<Clip>`, der
Clip-Satz liegt pro Klasse in einem eigenen Ordner. → Offene Entscheidung E3.

Das Unity-Fenster zeigt pro Variante eine **Statur-Ampel** (schlechteste Farbe aller Regler).

---

## 2. Schicht 2 – Haupt-Bedeckung

### 2.1 Aufbau: Haut + Lagen

Vorschlag (→ E2):
- **Haut** – genau **1**, nur im Shader, kostet 0 Tris: `glatt`, `leder`, `schuppen`. Sie liegt immer unter allem.
- **Lagen** – **0 bis 2** geometrische Bedeckungen: `fell`, `federn`, `stacheln`, `platten`. Ihre Masken dürfen sich
  nur am weichen Rand überlappen, z. B. beim Quillback: Stacheln auf Rücken/Flanken + kurzes Fell an Gesicht/Nacken.
  Standardfall ist 1 Lage.
- Gemeinsames Tris-Budget aller Lagen: **≤ 2.500** (Elite ≤ 3.500), siehe 6.4.

Warum nicht „Fell + Platten überall gleichzeitig“: doppelt teuer und von oben unruhig. Große Einzelplatten sind
**Accessoires** (Schicht 3), nicht Bedeckung. **Unterscheidung:** Bedeckung = viele gleichartige Teile flächig über
einen Bereich (Hunderte Zotteln, Dutzende Schuppenplatten). Accessoire = wenige, einzeln gesetzte, meist größere Teile
an bestimmten Körperstellen (3 Eisplatten an der Schulter).

### 2.2 Gemeinsame Felder jeder Lage

| Feld | Bedeutung | Bereich | Std |
|---|---|---|---|
| `typ` | `fell` · `federn` · `stacheln` · `platten` | – | – |
| `maske` | wo die Lage wächst, siehe 2.5 | – | `{"zonen":["ganzer_koerper"]}` |
| `anzahl` | Gesamtzahl der Teile in der Maske. Steuert direkt die Kosten (Tris ≈ `anzahl` × Tris pro Teil). | 0–1500 | je Typ |
| `laenge` | Länge eines Teils (Anteil Größe) | je Typ | je Typ |
| `laenge_zufall` | Streuung der Länge | 0–1 | 0.3 |
| `laenge_nach_zone` | Faktor pro Zone, z. B. längeres Fell am Nacken: `{"nacken":1.4}` | 0.2–3 | `{}` |
| `richtung` | Strich-Richtung: `knochen` (entlang der Knochen nach hinten/unten, wie Fell) · `hinten` · `unten` · `aussen` (senkrecht weg) | – | `knochen` |
| `anlege_winkel` | 0° = liegt flach an, 90° = steht senkrecht ab | 0–90 | je Typ |
| `richtung_zufall` | zufällige Abweichung der Richtung in Grad | 0–45 | 12 |
| `abstand_min` | Mindestabstand zwischen Teilen (Anteil Größe), verhindert Klumpen | 0–0.1 | je Typ |
| `farbgruppe` | Farbgruppe aus Schicht 4: `bedeckung_1` oder `bedeckung_2` | – | `bedeckung_1` |
| `weichheit` | **gebaut (G14, 2026-11-22)**, ersetzt das frühere `schwingen` (Migration beim Laden, `docs/VARIANTEN_BAUKASTEN.md` Teil E). Wie stark die Spitzen nachschwingen: 0 = starr wie Felszacken, 1 = schwingendes Fell. Regler in der Varianten-Datei, im Blender-Panel und im Unity-Fenster. Wirkt nur im Shader, kein neues „In Blender bauen“. | 0–1 | je Typ: `platten` 0 · `stacheln` 0.1 · `federn` 0.4 · `fell` 0.6 |
| `accessoires_aussparen` | unter Accessoires keine Teile erzeugen (spart Tris, nichts sticht durch) | bool | true |
| `seed` | eigener Seed, sonst abgeleitet (6.2) | int/null | null |
| `weg_ab_lod` | ab welcher LOD-Stufe die Lage nur noch als Textur existiert | 1–3/null | 2 |

**Nachschwingen im Shader („Foliage-Trick“) – gebaut (G14, 2026-11-22), Umsetzung: `docs/VARIANTEN_BAUKASTEN.md` Teil E.**
Beim Erzeugen der Bedeckung (Geometry Nodes, `procedural/variantkit_blender/`) bekommt jedes Teil einen
Beweglichkeitswert pro Vertex: Wurzel 0, Spitze 1 (z. B. in der Vertex-Farbe oder einem UV-Kanal, wird beim Backen
mitgenommen). Der Shader verbiegt die Spitzen auf der GPU, skaliert mit `weichheit`, aus drei Quellen: **Trägheit**
(Beschleunigung bzw. Geschwindigkeit des Ansatz-Knochens → Nachschwingen beim Anlaufen, Bremsen, Drehen),
**Wackeln** (leichtes Rauschen bzw. Wind) und **Stöße** (kurzer Impuls bei Slam oder Hit über Clip-Events). Keine Physik,
keine Zusatz-Knochen, Kosten praktisch null auch bei vielen Gegnern. Baut auf dem `_DANGLING`-Prinzip auf
(`rigging/dangling.py`, `Creature/Standard Dangling`) und gilt in `VariantKit/Layered` (Vorschau) wie in `VariantKit/Baked`
(Spiel), weiterhin 1 Material. Schwingende Accessoires (`weichheit` > 0, z. B. `moosfransen`, `tang`, `gehaenge`,
`kette`) nutzen denselben Weg mit ihrem Typ-Standard. `weichheit` ersetzt das bisherige `schwingen`
(ein Feld, entschieden im Bau). **Nicht** dafür: Spring Bones (später, nur für wenige große Teile wie
Mähnen-Strähnen) und echte Haar-/Stoff-Physik (verworfen, zu teuer).

### 2.3 Haut (nur Shader, 0 Tris)

| `typ` | Look | Felder (Bereich, Std) |
|---|---|---|
| `glatt` | „nackte“ facettierte Haut wie die Basis | `rauheit` (0–1, 0.8) |
| `leder` | matt, leichte Falten/Narben, auch für steinartige Haut (Slagback) | `rauheit` (0–1, 0.85) · `falten` (0–1, 0.3) · `narben` (0–1, 0.0) · `skala` = Größe des Faltenmusters (0.01–0.2, 0.05) |
| `schuppen` | Echsen-/Fischhaut (Lurker) | `rauheit` (0–1, 0.6) · `schuppen_groesse` (0.005–0.05, 0.015) · `form` (`rund` · `rhombus` · `sechseck`, `rhombus`) · `relief` = Tiefe in der Normal Map (0–1, 0.5) · `rand_dunkel` = dunkle Schuppenränder (0–1, 0.3) |

`leder` und `schuppen` brauchen eine Normal Map. Bei `glatt` entfällt sie (spart eine Textur, passt zu Artist B).
Kleine Schuppen sind **nie** Geometrie (Lehre aus `procedural/README.md`: dichte Platten = 4.520 Tris).

### 2.4 Geometrische Lagen

| `typ` | Look / Baustein | Eigene Felder (Bereich, Std) | Std `anzahl`, `laenge`, `anlege_winkel`, `abstand_min` | Tris pro Teil |
|---|---|---|---|---|
| `fell` | **Low-Poly-Zotteln**: flache, spitze, facettierte Büschel, überlappend wie im Eisriesen-Bild | `breite` = Breite relativ zur Länge (0.2–1.0, 0.45) · `form` (`spitz` · `rund` · `zackig` · `buschel` = 2–3 Spitzen, `spitz`) · `kanten` (3–5, 3) · `kruemmung` = biegt zur Spitze ab (0–1, 0.3) · `modus` (`geometrie` · `nur_shader` · `silhouette` = Zotteln nur an Rückenlinie, Nacken, Schultern, Beinrändern; Rest Strich-Textur, `geometrie`) | 500 · 0.05 · 25° · 0.015 | 3–4 (`buschel` 7–9) |
| `federn` | flache Federblätter, überlappend wie Dachziegel | `breite` (0.2–1.0, 0.35) · `kruemmung` (0–1, 0.4) · `kiel` = sichtbare Mittelrippe in der Textur (bool, true) · `modus` wie Fell | 300 · 0.06 · 15° · 0.02 | 4 (doppelseitig) |
| `stacheln` | Quills/Dornen wie Quillback, Lurker-Mähne bei hoher Dichte | `dicke` = Dicke an der Basis (0.003–0.03, 0.01) · `kanten` (3–5, 4) · `spitze` = wie spitz (0–1, 0.9) · `kruemmung` (0–1, 0.1) | 250 · 0.10 · 35° · 0.02 | 3–5 (= `kanten`) |
| `platten` | flächige Schuppen-/Panzerplatten, überlappend (Pangolin, Panzer) | `groesse` = Durchmesser (0.02–0.15, 0.06) · `dicke` (0.003–0.03, 0.01) · `streckung` (0.5–2, 1.2) · `ecken` (4–8, 6) · `schuppung` = Überlappung (0–0.8, 0.4) · `woelbung` (0–1, 0.3) · `groesse_zufall` (0–1, 0.3) | 60 · – · 10° · 0.03 | 12–20 |

**Technik (Blender, Geometry Nodes):** Punkte in der Maske verteilen (Poisson, `abstand_min`), Baustein je Punkt
instanzieren, nach `richtung`/`anlege_winkel` drehen, Länge/Farbe/Zufall aus Attributen. Jedes Teil bekommt die
**Gewichte seines Ansatzpunkts** auf der Haut (bewegt sich mit der Haut, verformt sich nicht). Mit `weichheit` > 0
schwingt die Lage im Shader nach (G14: Beweglichkeit `vk_h` Ansatz 0 → Spitze 1, Phase pro Teil zufällig).
Die Dicke-Erkennung von `dangling.py` wird dabei nicht gebraucht, weil die Geometrie bekannt ist.
Shape Keys (Statur): Jede Instanz bekommt pro Shape Key den Versatz ihres Ansatzpunkts (wandert mit, verformt sich
nicht).

**Geschätzte Kosten (Vermutung):** Eisriese mit Fell überall: 550 Zotteln × 4 = **2.200 Tris**. Mit
`modus: silhouette` ≈ 200 Zotteln = 800 Tris, der Rest kommt aus der Textur. Quillback: 250 Stacheln × 4 = 1.000 Tris.

### 2.5 Masken (gilt auch für Schicht 4)

```json
"maske": { "zonen": ["ruecken_gesamt", "flanke_l", "flanke_r"], "ohne": ["bauch"], "oben": 0.3, "rand": 0.1, "rauschen": 0.2, "gruppen": ["haut"] }
```

| Feld | Bedeutung | Bereich | Std |
|---|---|---|---|
| `zonen` | Zonen oder Sammelnamen aus 3.2, die dazugehören | Liste | `["ganzer_koerper"]` |
| `ohne` | Zonen, die herausgenommen werden | Liste | `[]` |
| `oben` | > 0 bevorzugt nach oben zeigende Flächen, < 0 die Unterseite, 0 = egal | −1…1 | 0 |
| `rand` | Breite des weichen Übergangs am Maskenrand (Anteil Größe) | 0–0.2 | 0.05 |
| `rauschen` | unregelmäßiger, fleckiger Rand statt glatter Linie | 0–1 | 0.2 |
| `gruppen` | nur Schicht 4, Körper-Ebenen: auf welche Körper-Farbgruppen die Ebene wirkt (Accessoires haben eigene Ebenen, 4.3) | Liste | alle |

Material-Ebenen: `zonen` fehlt = `["ganzer_koerper"]`, `zonen: []` = nirgends (seit Format 2, 4.3).

---

## 3. Schicht 3 – Accessoires

### 3.1 Ablauf für den Nutzer

1. **Körperstellen wählen** (Andock-Zonen, Klick auf den Körper oder Liste).
2. **Typ wählen** (Kristall-Cluster, Steinplatte, Pilze …).
3. **Einstellungen** (Anzahl, Größe, Zufall, Neigung …). Die Vorschau in Unity zeigt das sofort.

### 3.2 Andock-Zonen – Standard-Satz Vierbeiner (`quadruped`)

Jede Zone ist eine **Fläche auf der Haut**, festgelegt durch Knochen + Abschnitt entlang des Knochens (0 = Ansatz,
1 = Ende) + Seite (oben/außen/vorn). Sie wird **automatisch** aus Rig-Gewichten und Flächen-Ausrichtung erzeugt, wie
die Bereiche bei `dangling`. Standardwerte liegen pro Skelett in einer Datei (`rigging/quadruped_zonen.toml`),
Korrekturen pro Kreatur in `creature.toml` unter `[zonen.<id>]`. Ergebnis: ein Gewichts-Attribut pro Zone im Mesh,
exportiert als `<Name>_zonen.json`, damit Unity live platzieren kann.

**Knochen beim Bären:** Platzhalter ⟨Bär⟩ = wird vom Bär-Agenten ermittelt → `creatures/32_rimehide_bear/README.md`
(Abschnitt Rig/Andock-Zonen). Die Spalte „vorläufig“ nennt die Knochen des Standard-Skeletts.

| Zone (Feld) | Name | Knochen vorläufig | Knochen Bär | Fläche | Typische Accessoires |
|---|---|---|---|---|---|
| `kopf_oben` | Kopf oben (Scheitel) | `Head` 0–0.5, oben | ⟨Bär⟩ | Schädeldach hinter den Augen | Hörner, Krone, Kristalle |
| `stirn` | Stirn | `Head` 0.4–0.7, oben/vorn | ⟨Bär⟩ | über den Augen, Brauenwulst | Eis-/Steinbrauen, Stirnplatte, Kristall-Cluster |
| `schnauze` | Schnauze | `Head` 0.7–1.0, oben | ⟨Bär⟩ | Nasenrücken | Nasenhorn, Schnauzenplatte |
| `kiefer` | Kiefer/Maul | `Jaw` + `Head` unten vorn | ⟨Bär⟩ | Maulwinkel, Unterkiefer | Stoßzähne, Hauer, Barteln, Bart |
| `wange_l` / `wange_r` | Wange | `Head` seitlich | ⟨Bär⟩ | seitlich unter den Augen | Barteln, Wangenstacheln |
| `nacken` | Nacken | `Neck_1`, `Neck_2`, oben | ⟨Bär⟩ | Hals-Oberseite | Mähne, Stachelmähne, Kamm-Anfang |
| `buckel` | Buckel/Widerrist | `Chest`, oben | ⟨Bär⟩ | höchster Punkt über den Schultern | große Kristalle, Basaltbrocken, Pilze |
| `ruecken_mitte` | Rücken-Mitte | `Spine_1`, oben | ⟨Bär⟩ | Rücken zwischen Buckel und Hüfte | Platten, Moospolster, Kamm |
| `kruppe` | Kruppe | `Hips`, oben | ⟨Bär⟩ | Hinterteil oben | Platten, Pilze, Kamm-Ende |
| `schulter_l` / `schulter_r` | Schulter | `Shoulder_F*`, `Leg_F*_1` 0–0.5, außen | ⟨Bär⟩ | Schulterblatt + Oberarm außen | Schulterplatten, Schulterdornen |
| `unterarm_l` / `unterarm_r` | Unterarm | `Leg_F*_2`, außen/vorn | ⟨Bär⟩ | Vorderbein zwischen Ellbogen und Pfote | Armplatten, Eis-Schienen |
| `oberschenkel_l` / `oberschenkel_r` | Oberschenkel | `Leg_B*_1`, außen | ⟨Bär⟩ | Hinterbein oben außen | Platten, Moospolster |
| `flanke_l` / `flanke_r` | Flanke | `Spine_1`, `Chest` seitlich, unterhalb der Rückenkante | ⟨Bär⟩ | Rumpfseite | Platten, Moos, Gehänge |
| `schwanz` | Schwanz | `Tail_1..4`, oben | ⟨Bär⟩ | ganzer Schwanz | Stachel, Keule, Flosse, Schwanz-Aufsatz |
| `pranke_vorn_l` / `_r` | Vorderpranke | `Leg_F*_4` | ⟨Bär⟩ | Pfote vorn | Grabkrallen |
| *nur Maske:* `brust`, `bauch`, `gesicht`, `beine_unten`, `pfoten` | – | – | ⟨Bär⟩ | Unterseiten, Gesicht, untere Beine | (für Masken in 2 und 4) |

**Sammelnamen** (nur in Masken und `zonen`-Listen erlaubt):
`ganzer_koerper` · `ruecken_gesamt` = nacken + buckel + ruecken_mitte + kruppe · `kopf` = kopf_oben + stirn +
schnauze + kiefer + wangen + gesicht · `beine` = alle Bein-Zonen + beine_unten + pfoten · `seiten` = flanken +
schultern + oberschenkel.

**Linie `rueckenlinie`:** Mittellinie auf der Oberseite vom Stirnansatz über Nacken, Buckel, Rücken und Kruppe bis zur
Schwanzspitze, Position 0…1. Für Reihen (Kamm, Stachelmähne). Wird aus den Wirbelsäulen-Knochen + Strahl von oben auf
die Haut erzeugt.

Andere Skelette bekommen später eigene Zonen-Sätze nach demselben Muster (hexapod: `kopf`, `pronotum`,
`hinterleib_oben` …). Die Zonennamen sind pro Skelett fest, damit Varianten-Dateien zwischen Kreaturen desselben
Skeletts übertragbar sind.

### 3.3 Gemeinsame Felder jedes Accessoire-Eintrags

| Feld | Bedeutung | Bereich | Std |
|---|---|---|---|
| `id` | frei wählbarer, eindeutiger Name in dieser Datei (bestimmt auch den Seed) | Text | – |
| `typ` | Typ aus 3.4 | – | – |
| `formen` | welche Baustein-Formen aus der Bibliothek zufällig gemischt werden | Liste | alle Formen des Typs |
| `zonen` | Andock-Zonen (Liste) | – | Typ-Standard |
| `auf` | statt Zonen: auf einem anderen Accessoire sitzen (Kristalle auf Tropfsteinplatten, Pilze auf Moospolstern, Fransen am Polsterrand) | `id` / null | null |
| `stelle` | nur mit `auf`: `oben` oder `rand_unten` | – | `oben` |
| `spiegeln` | bei `_l`-Zonen automatisch gespiegelt auf `_r` (gleiche Form, gespiegelt) | bool | true |
| `asymmetrie` | wie stark die gespiegelte Seite abweichen darf | 0–1 | 0.2 |
| `verteilung` | `einzeln` (1 Teil in der Zonenmitte) · `streuen` (frei verteilt) · `cluster` (Haufen aus mehreren Teilen) · `reihe` (entlang `rueckenlinie`) · `kranz` (Ring um die Zone, z. B. Krone) | – | Typ-Standard |
| `anzahl` | Teile pro Zone. Bei `cluster` = Anzahl Haufen, bei `reihe` = Teile insgesamt | 1–40 | Typ-Standard |
| `teile` | nur `cluster`: Teile pro Haufen | 1–12 | 4 |
| `von`, `bis` | nur `reihe`: Abschnitt auf der Linie | 0–1 | 0.1, 0.8 |
| `reihen` | nur `reihe`: 1 = Mittelkamm, 2 = zwei versetzte Reihen | 1–2 | 1 |
| `groesse` | Größe eines Teils (Anteil Kreaturgröße) | 0.01–0.4 | Typ-Standard |
| `groesse_zufall` | Streuung der Größe | 0–1 | 0.3 |
| `groesse_verlauf` | nur `reihe`/`kranz`: Faktor [Anfang, Mitte, Ende] | je 0.1–2 | [1, 1, 1] |
| `streckung` | Verzerrung [Länge, Breite, Höhe] des Bausteins | je 0.3–3 | [1, 1, 1] |
| `abstand_min` | Mindestabstand zwischen Teilen (Anteil Größe) | 0–0.2 | 0.02 |
| `ausrichtung` | Grundrichtung: `normale` (senkrecht zur Haut) · `oben` · `hinten` · `aussen` · `knochen` (entlang des Knochens) · `unten` (hängt, G14) | – | `normale`, Gehänge `unten` |
| `neigung` | Kippen nach hinten (−) oder vorn (+) in Grad | −90…90 | 0 |
| `drehung_zufall` | zufällige Drehung um die eigene Achse | 0–180 | 180 |
| `kipp_zufall` | zufälliges Kippen | 0–45 | 10 |
| `einsinken` | wie tief das Teil in die Haut einsinkt (Anteil seiner Höhe), verhindert sichtbare Lücken | 0–0.6 | 0.25 |
| `auf_bedeckung` | wie weit das Teil auf der Bedeckung statt auf der Haut sitzt (1 = obenauf, sonst versinkt es im Fell) | 0–1 | 0.7 |
| `bindung` | `anker` = alle Punkte bekommen die Gewichte des Ansatzpunkts (bewegt sich mit der Haut, bleibt formstabil) · `knochen` = 100 % am nächsten Knochen · `haut` = jeder Punkt die Gewichte der Haut darunter (biegt sich mit, für große Platten über Gelenken) | – | `anker` (→ E4) |
| `weichheit` | Nachschwingen im Shader (G14): 0 = starr … 1 = schwingt voll; ersetzt die früheren Felder `bewegung` + `schwingen` (Migration: `schwingt` → Stärke × Typ-Standard). Gehänge (`moosfransen`, `tang`, `gehaenge`, `kette`) folgen zusätzlich der Schwerkraft. | 0–1 | Typ-Standard: Gehänge 0.9, `kette` 0.7, `barteln` 0.6, `grasbueschel` 0.5, sonst 0 |
| `farbgruppe` | `accessoire_a` · `accessoire_b` · `accessoire_c` · `horn` | – | `accessoire_a` |
| `farb_zufall` | pro Teil zufällige Mischung zwischen `farbe` und `farbe_2` der Gruppe (Cragplate: grau/rostbraun gemischt) | 0–1 | 0 |
| `weg_ab_lod` | ab welcher LOD-Stufe das Teil weggelassen wird (kleine Teile früh) | 1–3/null | null |
| `seed` | eigener Seed, sonst abgeleitet (6.2) | int/null | null |

**Platzierung (Unity, C#, genau eine Umsetzung):** Punkte in der Zone nach `verteilung` und `abstand_min` →
Ansatzpunkt auf der Haut → Ausrichtung → Baustein + Transformation. Ergebnis ist die **Instanzen-Liste**
(`<id>.instanzen.json`, siehe 6.1). Blender baut beim Backen genau diese Instanzen, ohne selbst zu platzieren.

**Shape Keys:** Instanzen wandern mit dem Ansatzpunkt mit (wie bei der Bedeckung).

**Bindung:** Standard `anker` ist eine Verfeinerung der bisherigen Regel „starr am nächsten Knochen“: Das Teil bleibt
formstabil, sitzt aber auch an Stellen zwischen zwei Knochen genau auf der Haut (Schulter, Buckel) und rutscht beim
Gehen nicht heraus.

### 3.4 Typ-Katalog (aus den 7 Bildern + Roster)

Die **Form** eines Bausteins (wie viele Ecken, wie zackig) wird nicht pro Variante eingestellt, sondern in der
**Baustein-Bibliothek**: pro Typ 3–8 fertige Formen (`kristall_a`, `kristall_schlank` …), erzeugt in Blender mit der
**Baustein-Werkbank** (Geometry Nodes mit Live-Reglern). Gespeichert in `procedural/bausteine/<typ>.json` (Werte) +
`procedural/bausteine/<typ>.fbx` (Meshes). Die Variante wählt nur über `formen` aus. Größe, Streckung und Neigung
gelten pro Variante und wirken in Unity live.

| Typ (Feld) | Familie | Aus Bild | Form-Regler in der Werkbank | Std-Zonen | Std-Verteilung, Anzahl, Größe | Bewegung | Tris pro Teil |
|---|---|---|---|---|---|---|---|
| `kristall` | Zacke | Eisriese (Kamm), Höhlenbär (klein, blau) | `kanten` 4–6 · `schlankheit` · `spitze_versatz` · `facetten_bruch` | buckel, ruecken_mitte, stirn | cluster, 1×5, 0.05 | starr | 12–18 |
| `eiszacke` | Zacke | Elder Rimehide (Krone) | wie Kristall + `kruemmung` | kopf_oben | kranz, 7, 0.06 | starr | 12–18 |
| `felszacke` | Zacke | Cragplate (Rückenreihe) | `kanten` 4–5 · `schlankheit` · `bruchkante` | rueckenlinie | reihe, 11, 0.10 | starr | 12–20 |
| `dorn` | Zacke | Elder (Schulterdornen), Lurker-Mähne | `kanten` 3–4 · `kruemmung` | schulter, nacken | streuen, 3, 0.06 | starr | 9–12 |
| `horn` | Zacke | Roster (Hörner) | `segmente` 3–6 · `kruemmung` · `drall` · `kanten` 4–6 | kopf_oben, stirn | einzeln, 1, 0.12 | starr | 30–60 |
| `stosszahn` | Zacke | Küstenlurker | `segmente` 3–5 · `kruemmung` · `kanten` 5–6 | kiefer | einzeln, 1, 0.15 | starr | 30–50 |
| `grabkralle` | Zacke | Quillback | `kanten` 3–4 · `kruemmung` | pranke_vorn | einzeln, 4, 0.04 (sitzt über den Mesh-Krallen) | starr | 9–12 |
| `eisplatte` | Platte | Eisriese (Schulter, Unterarm, Oberschenkel) | `ecken` 5–8 · `dicke` · `woelbung` · `facetten_bruch` | schulter, unterarm, oberschenkel | cluster, 1×3, 0.12 | starr | 20–40 |
| `steinplatte` | Platte | Cragplate (Stirn, Schulter, Arm, Rücken) | `ecken` 5–8 · `dicke` · `woelbung` · `kantenfase` · `risse` (Kerben) | stirn, schulter, unterarm, oberschenkel, ruecken_mitte | streuen, 2, 0.12 | starr | 20–40 |
| `tropfsteinplatte` | Platte | Höhlenbär | wie Steinplatte + `zacken_unten` 0–8 · `zacken_laenge` | buckel, ruecken_mitte, kruppe, schulter, unterarm, oberschenkel, stirn | streuen, 2, 0.14 | starr | 40–80 |
| `basaltbrocken` | Platte | Slagback | `ecken` 5–7 · `blockig` · `dicke` (hoch) | buckel, ruecken_mitte, kruppe, schulter | cluster, 1×8, 0.13 | starr | 24–48 |
| `knochenplatte` | Platte | Roster (Lurker, Stone Boar) | `ecken` · `rippen` | ruecken_mitte, schulter | streuen, 3, 0.08 | starr | 20–36 |
| `moospolster` | Bewuchs | Mossback | `kuppel_hoehe` · `zottel_rand` (Zotteln am Rand) · `rand_zacken` | ruecken_gesamt, schulter, oberschenkel, unterarm | streuen, 2, 0.18 | starr | 30–70 |
| `pilze` | Bewuchs | Mossback | `stiel_hoehe` · `hut_breite` · `hut_form` (flach/glocke) · `pro_gruppe` 2–5 | buckel, schulter, kruppe, unterarm, oberschenkel (oder `auf` Moospolster) | cluster, 1×3, 0.05 | starr | 20 pro Pilz |
| `grasbueschel` | Bewuchs | Mossback (Blattbüschel) | `blaetter` 3–6 · `kruemmung` | ruecken_gesamt (`auf` Moospolster) | streuen, 4, 0.04 | schwingt (0.5) | 6–12 (doppelseitig) |
| `moosfransen` | Gehänge | Mossback (hängendes Moos) | `streifen` 3–6 · `breite` · `zacken` | `auf` Moospolster, `stelle: rand_unten` | streuen, 4, 0.08 | schwingt (1.0) | 4–8 pro Streifen (doppelseitig) |
| `barteln` | Gehänge | Küstenlurker (Schnurrhaare) | `dicke` · `kruemmung` | wange | streuen, 4, 0.12 | schwingt (0.6) | 4–6 (doppelseitig) |
| `gehaenge` | Gehänge | Roster (Ketten, Tang, Stofffetzen) | `glieder` · `breite` | flanke, nacken | streuen, 2, 0.10 | schwingt (1.0) | 8–20 |
| `schwanz_flosse` | Sonstige | Küstenlurker | `zacken` · `hoehe` | schwanz (Ende) | einzeln, 1, 0.12 | starr | 16–30 |
| `schwanz_aufsatz` | Sonstige | lange Schwänze auf Stummel-Basis | `segmente` · `verjuengung` | schwanz | einzeln, 1, 0.3 | starr, Bindung `haut` | 40–80 |

Typen, die in keiner Variante vorkommen, sind trotzdem gültig. Die Bibliothek wächst nach Bedarf. **Dünne
Gehänge-Teile** werden in der Werkbank gleich doppelseitig gebaut (wie `double_sided.py`), deshalb ist der doppelte
Tris-Preis oben schon eingerechnet.

---

## 4. Schicht 4 – Material- und Textur-Ebenen

### 4.1 Prinzip

- **In der Vorschau (Unity-Editor):** ein Vorschau-Shader rechnet alle Ebenen live. Das darf teuer sein, es läuft nur
  im Editor.
- **Beim Backen:** Unity rendert den Ebenen-Stapel einmal im UV-Raum in die Texturen der Variante. Dadurch ist das
  Ergebnis genau das, was die Vorschau zeigt. Im Spiel läuft danach ein **einfacher Shader mit standardmäßig
  1 Material** und festen Kosten, egal wie viele Ebenen es waren. Matt, glänzend, leuchtend (Emission), Metall und
  Muster laufen über Texturen und Masken im selben Shader: Beispiel Platten-Ebene matt + Kristall-Ebene leuchtend →
  ein Material, die Masken beider Ebenen werden beim Backen in dieselben Texturen (Rauheit, Emission …) geschrieben.
  Ausnahmen (2. Material) siehe Material-Regel in 6.4.
- **Bleibt zur Laufzeit live** (zeit- oder blickabhängig, kann nicht eingebrannt werden): Emission-**Puls**,
  **Rim-Light**, **dangling**. Das sind 3 einfache Shader-Funktionen, alle im selben Material.
- **Gebackener Textursatz pro Variante (Haupt-Material):**
  - `Albedo` (Farbe, RGB)
  - `Maske` (R = Rauheit, G = Emission-Maske, B = Glasigkeit/Nässe, A = frei)
  - `Normal` (nur, wenn Haut `leder`/`schuppen` oder eine Ebene Relief hat)
- **Facetten-Look (Artist B):** flache Schattierung kommt im Shader aus den Flächen-Ableitungen. Dafür müssen keine
  Vertices aufgetrennt werden, das Mesh bleibt klein. Feld `stil.facetten` 0–1 (Std 1.0) mischt zwischen flach und
  weich.

### 4.2 Farbgruppen (Grundtönung)

Jeder Teil des Modells gehört zu einer **Farbgruppe**. Die Gruppe steckt als Attribut `_GRUPPE` (0–8) im Mesh und
wird nur bis zum Backen gebraucht. Krallen, Zähne, Augen und Maul der Basis werden **einmal pro Basis-Kreatur** als
Gruppe markiert (automatisch aus der dunklen Tripo-Textur + Sichtprüfung, Korrektur in `creature.toml`).

| Gruppe (Feld) | Enthält |
|---|---|
| `haut` | Grundkörper |
| `bedeckung_1`, `bedeckung_2` | Lagen aus Schicht 2 |
| `accessoire_a`, `accessoire_b`, `accessoire_c` | Accessoires je nach Eintrag |
| `horn` | Krallen, Zähne, Hörner, Stoßzähne |
| `akzent` | Nase, Maul innen, Lefzen |
| `augen` | Augen |

Felder pro Gruppe:

| Feld | Bedeutung | Bereich | Std |
|---|---|---|---|
| `farbe` | Grundfarbe (bei Bedeckung/Accessoires = Farbe am Ansatz) | Hex | Gruppen-Standard (neutral grau) |
| `farbe_2` | zweite Farbe: Spitze (Verlauf) oder Mischfarbe für `farb_zufall` | Hex/null | null |
| `verlauf` | `keiner` · `ansatz_spitze` (Fellspitzen heller) | – | `ansatz_spitze` bei Bedeckung, sonst `keiner` |
| `farb_zufall` | pro Teil zufällig zwischen `farbe` und `farbe_2` mischen | 0–1 | 0 |
| `helligkeit_zufall` | leichte Helligkeitsstreuung pro Facette (lebendiger Low-Poly-Look) | 0–0.3 | 0.08 |
| `detail` | wie stark die Tripo-/Baustein-Textur (Schattierung, Kanten) durchscheint | 0–1 | 0.5 |
| `rauheit` | matt (1) bis glänzend (0) | 0–1 | 0.8 |
| `glasig` | **falsche Transparenz** für Eis/Kristall: Fresnel-Aufhellung + hellere innere Facetten. Echte Transparenz ist bei vielen Gegnern zu teuer und macht Sortierfehler; wo sie wirklich nötig ist (Glaskristall), läuft sie über ein 2. Material (Material-Regel 6.4). | 0–1 | 0 |
| `leuchten` | Selbstleuchten in `farbe` (Augen, Kristalle) | 0–8 | 0 |

### 4.3 Ebenen

**Zwei Ebenen-Gruppen (Nutzer 2026-11-22, `format_version` 2):**

| Gruppe (Feld in `material`) | wirkt auf | Maske | Limit |
|---|---|---|---|
| **Körper-Ebenen** `ebenen` | Haut und Bedeckung (Lagen), **nie auf Accessoires** | Zonen + `ohne` (pro Vertex), `oben`, `rauschen`, `gruppen` (nur Körper-Gruppen: `haut`, `bedeckung_1/2`, `horn`, `akzent`, `augen`) | **8**, Empfehlung 3–5 |
| **Accessoire-Ebenen** `ebenen_accessoires` | nur Accessoires, liegen **immer obenauf** | `ziel` + innerhalb des Teils `oben`, `rauschen` (Körper-Zonen gelten hier nicht) | **4**, Empfehlung 1–3 |

- Beide Gruppen kennen dieselben Typen und Felder (Tabelle unten). Innerhalb einer Gruppe gilt die Reihenfolge der Liste.
  Jeder Typ höchstens 2× pro Gruppe (`naesse` und `rim` je 1× pro Gruppe).
- **`ziel`** einer Accessoire-Ebene: `"alle"` oder `{ "typen": ["kristall"], "eintraege": ["eis_kamm"] }` (Vereinigung:
  Typen und/oder einzelne Accessoire-Einträge). Beide Listen leer = Ebene wirkt nirgends (das Fenster warnt). Typisch:
  Platten-Ebene matt (`typen: ["steinplatte"]`) + Kristall-Ebene leuchtend (`typen: ["kristall"]`), unabhängig vom Körper.
- **Zonen:** Fehlt `zonen`, gilt `["ganzer_koerper"]`. Eine **leere** Liste heißt „nirgends“ (bis Format 1 galt leer als
  ganzer Körper, siehe unten).
- **Weiterhin 1 Material (E5).** Die Zuordnung läuft im Shader: Jeder Accessoire-Vertex trägt die Nummer seines Eintrags
  (`TEXCOORD2.w = −(1 + n)`, Basis 1, Bedeckung 0), jede Accessoire-Ebene eine Bit-Tabelle der getroffenen Einträge
  (`−1` = alle). Gezielt wählbar sind die ersten **24 Einträge** einer Variante, „alle“ gilt für jede Anzahl.
  Accessoire-Vertices haben keine Körper-Masken (0), Bedeckung bleibt Körper.

**Warum (Fehler bis Format 1):** Es gab eine Liste für alles. Ein Accessoire hatte keine eigene Maske, sondern übernahm
den Masken-Wert der Haut an seinem **Ansatzpunkt** für alle seine Vertices, nur die Farbgruppe filterte. Weiche
Zonenränder, Lücken zwischen den Zonen und das multiplikative `ohne` ließen dort 0,3–0,7 stehen → das ganze Teil bekam
die Ebene. Zusätzlich galt eine leere Zonen-Liste als ganzer Körper. Belegt mit `VkLayerBatch.Diagnose`
(`temp/mg_diag/diagnose.txt`): Slagback, alle Einzelzonen in `ohne` → Körper im Mittel 0,13, Basaltbrocken an der
Schulter weiter 0,67. Zonen leer → unverändert wie „ganzer Körper“.

**Migration Format 1 → 2** (beim Laden, Unity `VkSpec.MigrateMaterialV1`; Speichern schreibt Format 2): Die alte Datei
wird gegen das eingefrorene Preset `templates/umgebungs_gruppen/_v1/<gruppe>.json` aufgelöst (alte Bedeutung). Jede alte
Ebene bleibt Körper-Ebene (gleiche id, Farbgruppen-Filter ohne Accessoire-Gruppen; hatte sie nur Accessoire-Gruppen, entfällt
sie im Körper). Wirkte sie sichtbar auf Accessoires (an, Stärke > 0, Farbgruppe passt, Eintrag sitzt in einer ihrer Zonen),
entsteht eine Accessoire-Ebene mit **derselben id** (gleicher Seed → gleiches Muster) und denselben Werten, Ziel `"alle"`,
wenn sie alle Einträge traf, sonst genau die getroffenen Einträge. Begründung: Die id-Gleichheit hält Muster und Risse
deckungsgleich, „alle“ entspricht dem alten Verhalten in allen bisherigen Dateien (dort lagen die Ansatzpunkte bei Maske 1).
Ergebnis: Slagback, Cragplate, Quillback, Eisriese und die Testdateien des Nutzers sehen nach der Migration gleich aus
(mittlere Abweichung ≤ 0,02 von 255). Blender liest Format-1-Dateien ebenfalls gegen `_v1/` und schreibt sie unverändert
im Format 1 zurück (Material-Ebenen bearbeitet Blender nicht).

Jede Ebene hat zusätzlich `maske` (2.5 bzw. oben), `staerke` (0–1, Std 1) und `an` (bool).

| Ebene (`typ`) | Wofür | Felder (Bereich, Std) | Gebacken? |
|---|---|---|---|
| `verlauf` | Gegenschattierung: Rücken dunkler, Bauch heller; oder vorn/hinten | `richtung` (`oben_unten` · `vorn_hinten` · `ansatz_spitze`, `oben_unten`) · `farbe_a` (oben/vorn) · `farbe_b` (unten/hinten) · `mischung` (`multiplizieren` · `ueberlagern` · `ersetzen`, `ueberlagern`) · `mitte` (0–1, 0.5) · `weichheit` (0–1, 0.5) | ja |
| `muster` | Streifen, Flecken, Tupfen, Ringe, Marmor, Zellen (Dachs-Gesicht, Lurker-Flecken) | `art` (`streifen` · `flecken` · `tupfen` · `ringe` · `marmor` · `zellen`) · `farbe` · `skala` (0.01–0.5, 0.08) · `dichte` (0–1, 0.5) · `kontrast` (0–1, 0.7) · `richtung` (`quer` · `laengs` · `knochen`, `quer`) · `verzerrung` (0–1, 0.3) · `mischung` · `seed` | ja |
| `risse` | Risse/Adern, optional leuchtend: Glut, Frost, Gift, Arkan, Moos-Adern ohne Leuchten | `element` (`glut` · `frost` · `gift` · `arkan` · `blitz` · `heilig` · `keins` = setzt nur Standardfarben) · `art` (`risse` · `adern` · `zellfugen` = Fugen zwischen Facetten · `runen`) · `farbe` · `intensitaet` (0–8, 0 = nicht leuchtend) · `breite` (0.001–0.02, 0.005) · `dichte` (0–1, 0.4) · `verzweigung` (0–1, 0.5) · `hof` = Glühen um den Riss (0–1, 0.3) · `puls_frequenz` (0–2 Hz, 0) · `puls_staerke` (0–1, 0) · `seed` | Form + Maske ja, Puls live |
| `ueberzug` | Schmutz, Frost, Asche, Schleim, Staub, Moosflecken über allem | `art` (`schmutz` · `frost` · `asche` · `schleim` · `staub` · `moos`) · `farbe` · `menge` (0–1, 0.3) · `kanten` = sammelt sich an Kanten/Vertiefungen (0–1, 0.4) · `rauschen_skala` (0.01–0.3, 0.08) · `rauheit` (0–1, je Art) · `seed` | ja |
| `naesse` | nasser Glanz (Küste, Sumpf) | `menge` (0–1, 0.5) · `glanz` (0–1, 0.8) · `abdunkeln` (0–1, 0.3) | ja (Masken-Kanal) |
| `rim` | Rim-Light in Biom-Farbe (Elite) | `farbe` · `intensitaet` (0–4, 1.5) · `breite` (0–1, 0.35) | **live** |

**Element-Voreinstellungen** für `risse` (nur Startwerte, alles überschreibbar):
`glut` #FF6A10 / 4.0 · `frost` #8FD8FF / 1.5 · `gift` #9BFF3A / 2.0 · `arkan` #7A6CFF / 2.5 ·
`blitz` #E8F4FF / 5.0 · `heilig` #FFE08A / 2.5.

Partikel (Funken, Frost-Atem, Sporen, Staub, Tropfen) sind **keine** Material-Ebene. Sie stehen unter `effekte` in
der Varianten-Datei und werden in Unity als eigene Komponenten angehängt (zählen extra, siehe 6.4).

---

## 5. Umgebungs-Gruppen – die Haupt-Achse der Varianten

*Vorgabe des Nutzers 2026-11-21, Biom-Übersicht: `docs/biome_uebersicht.webp`.*

### 5.1 Idee

Die einzelnen Biome sind nicht so wichtig. Entscheidend sind die **9 Umgebungs-Gruppen**. Daraus ergeben sich pro
Monster **bis zu 9 Varianten** (eine pro Gruppe), später dazu ein paar **Sondervarianten** (5.5).

Pro Gruppe gibt es **ein Gruppen-Preset**, das für alle Monster wiederverwendbar ist: Farbpalette und
Material-Ebenen, typische Bedeckung, typische Accessoires, Effekte. Eine Variante entsteht so:

```
Variante = Basis-Kreatur  +  Gruppen-Preset  (+ Biom-Feinabstimmung)  +  monsterspezifische Anpassung
           (Schicht 1 = 1.0)  (z. B. E Kalt: Frost, Eis,     (z. B. Taiga:      (z. B. Bär: Kristall-Kamm
                               kalte Palette)                 + Tannengrün)       größer, Fell länger)
```

Damit entstehen viele Varianten mit wenig Handarbeit. Ein neues Monster bekommt alle passenden Gruppen fast
geschenkt. Man justiert nur noch nach, wo es am Monster nicht passt.

### 5.2 Die 9 Gruppen und ihre MVP-Biome (aus dem Bild)

Durchgestrichene Biome gehören nicht ins MVP. Die Kopfzahl im Bild, z. B. „(3)“, zählt die gestrichenen Biome mit.

| Gruppe | Feld `gruppe` | MVP-Biome (Feld `biom`) | Gestrichen (nicht MVP) | Unsicher |
|---|---|---|---|---|
| **A** Gemäßigt | `gemaessigt` | Grasland `grasland` · Wald `wald` | Heide- & Buschland | – |
| **B** Feucht | `feucht` | Sumpf `sumpf` · Moor `moor` | Urwald, Mangrovenwald | – |
| **C** Sandlandschaften | `sand` | Wüste `wueste` · Oase `oase` | Savanne, Steppe | – |
| **D** Steinlandschaften | `stein` | Mesa/Tafelberge `mesa` · Salzwüste `salzwueste` | Steinwüste/Badlands | – |
| **E** Kalt | `kalt` | Taiga `taiga` · Eiswüste `eiswueste` | Tundra, Gletscherlandschaft | – |
| **F** Küsten | `kueste` | Felsküste `felskueste` · Wattland/Gezeitenzone `wattland` | Sandküste, Tropenküste | – |
| **G** Geologisch | `geologisch` | Thermalquellen `thermalquellen` | Versteinerter Wald, Kristallwildnis | – |
| **H** Lebensfeindlich | `lebensfeindlich` | Obsidian-/Basalt-Ebene `basalt` · Schwefelebene `schwefel` | Vulkanische Ödnis, Kristallwüste | **MVP bestätigt (Nutzer 2026-11-21).** „Schwefel“ bleibt zusätzlich als Vorlage für eine Sondervariante (5.5). |
| **I** Außergewöhnlich | `aussergewoehnlich` | Hölle `hoelle` · Himmel `himmel` | Pilzwald/Leuchtflora, Abyss | **MVP bestätigt (Nutzer 2026-11-21).** Hölle und Himmel bleiben zusätzlich als Vorlage für Sondervarianten (5.5). **Offene Kleinigkeit:** Die Kopfzeile zeigt „(5)“, im Bild sind aber nur 4 Biome zu sehen. |

**Abgleich mit `creatures/roster.toml`** (18 Biome aus `templates/biomes.toml`; Zahl = Einträge mit diesem Biom,
Kreaturen + Varianten):

| Roster-Biom | Gruppe | Abweichung |
|---|---|---|
| `forest` (5) | A | passt (Wald) |
| `steppe` (5) | A ❓ | Steppe ist in C **gestrichen**. Grasland (A) ist der nächste Nachbar → auf A umhängen, bitte bestätigen |
| `swamp` (8) | B | passt (Sumpf). Moor fehlt im Roster |
| `jungle` (12) | B | Urwald ist **gestrichen**. Viele Einträge → B (Sumpf) oder A (Wald) umhängen |
| `desert` (12), `oasis` (2) | C | passt |
| `stone` (3) | D | passt. Mesa und Salzwüste fehlen als eigene Biome |
| `highlands` (7) | D ❓ | kein eigenes Biom im Bild. Nächster Nachbar Mesa (D), bitte bestätigen |
| `snow` (5), `ice` (7) | E | passt (Taiga/Eiswüste). Gletscher ist gestrichen, `ice` wird zu Eiswüste |
| `coast` (5) | F | passt. Felsküste und Wattland fehlen als eigene Biome |
| `volcano` (11) | H | Vulkanische Ödnis ist **gestrichen**, Obsidian-/Basalt-Ebene ist MVP → `volcano` wird zu `basalt`. „Vulkan“ kommt später als Sondervariante |
| `crystal` (5) | Sonder | Kristallwildnis (G) und Kristallwüste (H) sind **gestrichen** → Sondervariante „Kristall“ (später) |
| `abyss` (7) | Sonder | Abyss ist **gestrichen** → Sondervariante (später) |
| `fungal` (3) | – | Pilzwald ist **gestrichen**, keine Sondervariante genannt → A/B oder streichen, bitte bestätigen |
| `cave` (8), `crypt` (6), `temple` (5) | **keine** | Das sind **Orte** (Dungeons), keine Umgebungen. Sie kommen im Bild nicht vor. Vorschlag: Ort ist eine eigene, spätere Achse, unabhängig von der Gruppe. Bitte bestätigen |
| – | G | **Thermalquellen fehlen im Roster ganz** |
| – | B, D, F | Moor, Mesa, Salzwüste, Felsküste, Wattland fehlen als Biome im Roster |
| – | I | Hölle und Himmel fehlen im Roster |

Das Roster wird hier **nicht** geändert. Die Umstellung (`gruppe` pro Variante, Biome umhängen, fehlende MVP-Biome,
Achse „Ort“ für Höhle/Krypta/Tempel) ist ein eigener kleiner Punkt im BACKLOG (G9, Abgleich Roster ↔ Biome). Die
Zeilen mit „bitte bestätigen“ in dieser Tabelle sind dort noch offen.

### 5.3 Gruppen-Presets

**Ablage:** `templates/umgebungs_gruppen/<gruppe>.json`, ein Preset pro Gruppe, gleiche Struktur wie die
Varianten-Datei (Abschnitt 6.1), aber **ohne Statur** (die Statur ist monsterspezifisch):
`bedeckung`, `accessoires`, `material`, `effekte`. Dazu ein Block `biome` mit kleinen Abweichungen pro MVP-Biom
(z. B. Taiga: Tannengrün-Akzent statt Eisblau). Presets sind **skelett-neutral**: Accessoires nennen nur
Sammel-Zonen (`ruecken_gesamt`, `seiten`, `kopf`, `beine`), die jedes Skelett definiert. Größen sind Anteile der
Kreaturgröße und passen damit auf jedes Monster.

**Erste Inhalte der Presets (Vorschlag Claude, vom Nutzer anpassbar):**

| Gruppe | Palette (Haut / Bedeckung / Accessoires) | Typische Bedeckung | Typische Accessoires | Material-Ebenen | Effekte (Unity) |
|---|---|---|---|---|---|
| **A** Gemäßigt | Erdbraun, Moosgrün, Rinde | Haut `leder`; ggf. `fell` kurz | `moospolster`, `grasbueschel`, wenige `pilze` | Verlauf Rücken dunkler, `ueberzug` moos leicht | Blätter/Pollen; Element physisch |
| **B** Feucht | Torfbraun, Oliv, Faulgrün | Haut `leder` | `moosfransen` (schwingt), `gehaenge` (Ranken), `pilze` | `naesse` 0.6, `ueberzug` schleim unten (`oben` −0.5) | Tropfen, Gift-Sporen; Gift |
| **C** Sand | Ocker, Sandgelb, gebleichter Knochen | Haut `leder` | `knochenplatte`, `steinplatte` in Sandfarbe, `dorn` | Verlauf oben gebleicht, `ueberzug` staub an Kanten | Sandstaub; Blendung |
| **D** Stein | Steingrau, Mesa-Rostrot, Salzweiß | Haut `leder` | `steinplatte`, `felszacke`, Salz-`kristall` | `muster` streifen (Gesteinsschichten), `ueberzug` staub/Salzkruste | Staub, Steinsplitter; Erde/Betäubung |
| **E** Kalt | Weiß, Stahlblau (Taiga: + Tannengrün) | `fell` | `kristall` (Eis), `eisplatte`, `eiszacke` | `ueberzug` frost oben, `risse` frost im Eis, Eis `glasig` | Frost-Atem, Schneeflocken; Kälte |
| **F** Küsten | Schiefer, Blaugrau, Algengrün | Haut `leder`/`schuppen` | `seepocken`, `tang` (schwingt) | `naesse` 0.5, `muster` flecken, `ueberzug` Salz an Kanten | Tropfen; Wasser/Kälte |
| **G** Geologisch | Sinterweiß, Ocker, Mineral-Türkis | Haut `leder` | `sinterplatte`, Mineral-`kristall` | `muster` ringe (Sinterterrassen), `ueberzug` Mineralkruste, `naesse` | Dampf; Verbrühen (Hitze/Wasser) |
| **H** Lebensfeindlich | Anthrazit, Obsidian-Schwarz + Glut-Orange (Schwefel: + Gelb) | Haut `leder` | `basaltbrocken`, Obsidian-`kristall` (schwarz, glasig), Schwefel-`kristall` | `risse` glut (Puls), `ueberzug` asche | Funken, Rauch; Feuer/Gift |
| **I** Außergewöhnlich | **kein gemeinsamer Look:** Hölle = Blutrot/Schwarz + Glut, Himmel = Weiß/Gold + Leuchten | je Biom | Hölle: `horn`, `dorn`, `kette` · Himmel: `kristall` gold, Lichtkranz (`kranz`) | Hölle: `risse` glut · Himmel: `rim` gold, `leuchten` | Hölle: Glut · Himmel: Lichtpartikel |

Bei **I** tragen die Biom-Presets fast alles, das Gruppen-Preset bleibt dünn.

**Neue Accessoire-Typen** für die Presets (ergänzen den Katalog in 3.4, gleiche Regeln):
`seepocken` (Bewuchs, cluster, 10–20 Tris pro Stück, starr) · `tang` (Gehänge, schwingt, 8–16 Tris, doppelseitig) ·
`sinterplatte` (Platte mit Terrassen-Rand, 20–40 Tris) · `kette` (Gehänge, schwingt, 8–20 Tris).

### 5.4 Wie Preset und Anpassung in der Datei stehen

- Neue Kopf-Felder der Varianten-Datei: `gruppe` (z. B. `"kalt"`), `biom` (MVP-Biom innerhalb der Gruppe oder
  `null`), `sonder` (5.5, sonst `null`).
- **Gespeichert wird nur die Anpassung.** Die Datei enthält Kopf + Statur + nur die Werte, die vom Preset abweichen.
  **Reihenfolge beim Zusammensetzen:** Standardwerte dieser Spec → Gruppen-Preset → Biom-Block des Presets →
  Varianten-Datei.
- **Zusammenführen:** Objekte werden feldweise überschrieben. Listen (`lagen`, `accessoires`, `ebenen`) werden über
  `id` abgeglichen. Gleiche `id` = Eintrag ändern, neue `id` = Eintrag hinzufügen, `"an": false` = Preset-Eintrag
  abschalten. Ebenen ohne `id` heißen automatisch `<typ>#<n>` (wie beim Seed, 6.2).
- Die vollständigen Beispiele in 6.1 sind die **aufgelöste Fassung** (alles zusammengesetzt). Unity kann sie
  jederzeit anzeigen und exportieren. So sieht auch eine Variante ohne Preset aus (`gruppe: null`).
- **Preset ändern = viele Varianten ändern sich.** Das ist gewollt. Freigegebene Varianten bleiben aber nach der Regel
  in 6.2 gebacken, bis der Nutzer zustimmt. `_gebaut` merkt sich dafür die Preset-Version (`presets: {"kalt": 3}`).

Gespeicherte Fassung des Slagback (Gruppe H) – nur Kopf, Statur und Abweichungen vom Preset:

```json
{
  "format": "kreatur_variante",
  "format_version": 1,
  "revision": 1,
  "id": "slagback_bear",
  "name": "Slagback Bear",
  "basis": "rimehide_bear",
  "skelett": "quadruped",
  "muster": "quadruped/bear",
  "art": "biom",
  "gruppe": "lebensfeindlich",
  "biom": "basalt",
  "sonder": null,
  "budget_klasse": "elite",
  "seed": 3101,
  "freigegeben": false,
  "statur": { "rumpf_dicke": 1.05, "buckel": 1.1, "glied_dicke": 1.05, "hals_laenge": 0.95, "kopf_breite": 1.05, "schnauze_laenge": 0.95 },
  "accessoires": [
    { "id": "basalt_buckel", "teile": 9, "groesse": 0.13 },
    { "id": "basalt_schulter", "typ": "basaltbrocken", "zonen": ["schulter_l"], "spiegeln": true, "verteilung": "einzeln", "anzahl": 1, "groesse": 0.17, "ausrichtung": "aussen" }
  ],
  "material": { "farbgruppen": { "augen": { "farbe": "#FF7A1A", "leuchten": 3.0 } } },
  "_gebaut": null
}
```
*(In der gespeicherten Fassung darf `statur` lückenhaft sein, fehlende Regler = 1.0. Die Regel „immer alle 17“ aus
1.1 gilt für die aufgelöste Fassung.)*

### 5.5 Sondervarianten – **später**

Eigene Kategorie neben den 9 Gruppen, **noch nicht im MVP**: **Kristall · Schwefel · Vulkan · Hölle · Himmel ·
Abyss.** Technisch genauso aufgebaut: ein Preset pro Sondervariante in `templates/umgebungs_gruppen/sonder/<name>.json`,
in der Varianten-Datei `sonder: "kristall"` (dann `art: "sonder"`, `gruppe` optional als Grundlage).
Überschneidungen: Schwefelebene, Hölle und Himmel sind **MVP-Biome in H/I** (bestätigt, Nutzer 2026-11-21). Als
Sondervariante bleiben sie zusätzlich eine Vorlage für stärkere Ausprägungen später (5.2).

### 5.6 Die 7 Bär-Bilder nach Gruppen – Vorschlag

| Bild | Gruppe | Begründung |
|---|---|---|
| Eisriese | **E** Kalt (Eiswüste) | Fell, Eiskristalle, Frost |
| Mossback | **A** Gemäßigt (Wald) | Moos + Pilze, trocken. Mit Nässe + hängendem Moos auch als **B** nutzbar |
| Höhlenbär | **D** Stein ❓ | Tropfstein-Platten. Höhle ist ein Ort, keine Gruppe (5.2). Die blauen Kristalle passen auch zur späteren Sondervariante Kristall |
| Cragplate | **D** Stein (Mesa) | Steinplatten, Felszacken |
| Slagback | **H** Lebensfeindlich (Basalt) | Basaltbrocken, Glutrisse |
| Quillback | – (Statur-Variante) | Gibt eher eine Statur-Klasse vor als eine Gruppe. Grau/Stein → am ehesten D |
| Küstenlurker | **F** Küsten | eigene Basis (6.5), gehört aber in F |

**Beim Bären noch ohne Bild** (nur Hinweis, was das Preset liefern würde, kein Entwurf neuer Kreaturen):
- **B Feucht:** Mossback mit Nässe, Moosfransen, Schlamm-Überzug, Torf-Palette.
- **C Sand:** Ocker-Palette, Knochenplatten, Sand an den Kanten.
- **F Küsten** (Bären-Basis, nicht Lurker): Seepocken, Tang, nasser Glanz.
- **G Geologisch:** Sinterplatten, Mineral-Türkis, Dampf.
- **I Außergewöhnlich:** Hölle bzw. Himmel.

Mit Mossback in A und dem Höhlenbären in D wären **D doppelt** (Höhlenbär + Cragplate) und **B, C, F, G, I**
offen. Ob der Bär alle Gruppen braucht → E7.

---

## 6. Querschnitt

### 6.1 Format der Varianten-Datei – Vorschlag **JSON**

**Begründung** (→ E1):
- Beide Programme **schreiben** die Datei. Python (`json`) und Unity (Newtonsoft JSON, offizielles Unity-Paket)
  können JSON ohne Zusatzbibliothek lesen und schreiben. TOML kann Blender nur lesen (`tomllib`). Zum Schreiben bräuchte
  es eine mitgelieferte Bibliothek, und Unity bräuchte für TOML in jedem Fall eine fremde DLL.
- Der Hauptvorteil von TOML, die Kommentare, geht ohnehin verloren, sobald ein Programm die Datei neu schreibt.
  Erklärungen stehen deshalb hier in der Spec, nicht in der Datei.
- Verschachtelte Listen (Accessoires mit Masken) sind in JSON eindeutiger als in TOML.
- Die bestehenden Konfigurationen (`creature.toml`, `roster.toml`, `*_defaults.toml`) bleiben TOML. Sie werden von
  Hand gepflegt und von Programmen nur gelesen.

**Regeln für git-freundliche Dateien:** UTF-8, 2 Leerzeichen Einzug, feste Reihenfolge der Felder (wie in dieser
Spec), Zahlen auf höchstens 3 Nachkommastellen gerundet, `\n` als Zeilenende, Schreiben atomar (temporäre Datei,
dann umbenennen). Später gibt es ein JSON-Schema `docs/varianten.schema.json` zur Prüfung.

**Ablage:**
```
creatures/<NN_name>/varianten/
  <id>.variant.json        Quelle der Wahrheit (von Hand, Unity oder Blender bearbeitet) – versioniert
  <id>.instanzen.json      abgeleitet: Accessoire-Instanzen aus Unity – nie von Hand bearbeiten; versioniert,
                           damit Blender ohne Unity reproduzierbar backen kann
creatures/<NN_name>/output/varianten/<ExportName>/   gebackene FBX/GLB + Texturen + Vorschau
procedural/bausteine/<typ>.json + <typ>.fbx          Baustein-Bibliothek (gemeinsam für alle Kreaturen)
rigging/<skelett>_zonen.toml                         Standard-Andock-Zonen pro Skelett
```
`id` = snake_case (`slagback_bear`), Exportname = CamelCase (`SlagbackBear`). Die Clips bleiben die des Musters
(`Quadruped_Bear_*`).

**Felder der obersten Ebene:**

| Feld | Bedeutung |
|---|---|
| `format`, `format_version` | immer `"kreatur_variante"`, Schema-Version (Ganzzahl, siehe 6.2) |
| `revision` | zählt bei jedem Speichern um 1 hoch |
| `id`, `name` | technischer und angezeigter Name |
| `basis` | Kreatur-ID der Basis im Roster (`rimehide_bear`) |
| `skelett`, `muster` | `quadruped`, `quadruped/bear` (bzw. Statur-Klasse `quadruped/bear@flach`) |
| `art` | wie im Roster: `grund` · `biom` · `elite`, neu `sonder` |
| `gruppe`, `biom`, `sonder` | Umgebungs-Gruppe (Haupt-Achse, Abschnitt 5), MVP-Biom innerhalb der Gruppe, Sondervariante (später) |
| `budget_klasse` | `normal` · `elite` · `boss` (6.4) |
| `seed` | Haupt-Seed der Variante |
| `freigegeben` | vom Nutzer abgenommen → darf sich nicht mehr unbemerkt ändern (6.2) |
| `quelle` | Bild des Nutzers + Roster-Eintrag, aus dem die Variante stammt |
| `statur` | Schicht 1 (alle 17 Regler) |
| `bedeckung` | Schicht 2: `haut` + `lagen` |
| `accessoires` | Schicht 3: Liste |
| `material` | Schicht 4: `stil`, `farbgruppen`, `ebenen` |
| `effekte` | Element + Partikel (nur Unity-Laufzeit, nicht gebacken) |
| `_gebaut` | wird nur von den Werkzeugen geschrieben: Hash der Quelle, Werkzeug-Versionen, Tris, Ampel, Dateien. `null` = noch nie gebaut |

**Beispiel 1 – Slagback Bear**, aufgelöste Fassung = Preset H + Anpassung (gespeicherte Fassung siehe 5.4; aus `Varianten/Slagback-Bär mit glühenden Magmarissen-3.png`: rußschwarze, matte
Haut, glühende Risse an Gesicht/Flanke/Beinen, großer Haufen Basaltbrocken auf Buckel und Rücken mit glühenden
Fugen, je ein großer Brocken auf den Schultern, glühende Augen):

```json
{
  "format": "kreatur_variante",
  "format_version": 1,
  "revision": 1,
  "id": "slagback_bear",
  "name": "Slagback Bear",
  "basis": "rimehide_bear",
  "skelett": "quadruped",
  "muster": "quadruped/bear",
  "art": "biom",
  "gruppe": "lebensfeindlich",
  "biom": "basalt",
  "sonder": null,
  "budget_klasse": "elite",
  "seed": 3101,
  "freigegeben": false,
  "quelle": {
    "bild": "creatures/32_rimehide_bear/input/Varianten/Slagback-Bär mit glühenden Magmarissen-3.png",
    "roster": "Slagback Bear"
  },
  "statur": {
    "groesse": 1.0,
    "koerper_laenge": 1.0,
    "rumpf_hoehe": 1.0,
    "rumpf_dicke": 1.05,
    "buckel": 1.1,
    "glied_dicke": 1.05,
    "bein_laenge_vorn": 1.0,
    "bein_laenge_hinten": 1.0,
    "spur_breite": 1.0,
    "pranken_vorn": 1.0,
    "pranken_hinten": 1.0,
    "hals_laenge": 0.95,
    "kopf_groesse": 1.0,
    "kopf_breite": 1.05,
    "schnauze_laenge": 0.95,
    "schwanz_laenge": 1.0,
    "schwanz_dicke": 1.0
  },
  "bedeckung": {
    "haut": { "typ": "leder", "rauheit": 0.9, "falten": 0.15, "narben": 0.0, "skala": 0.05 },
    "lagen": []
  },
  "accessoires": [
    {
      "id": "basalt_buckel", "typ": "basaltbrocken", "formen": ["basalt_a", "basalt_b", "basalt_c"],
      "zonen": ["buckel", "ruecken_mitte"], "spiegeln": false, "verteilung": "cluster", "anzahl": 1, "teile": 9,
      "groesse": 0.13, "groesse_zufall": 0.4, "streckung": [1.0, 0.85, 0.75], "abstand_min": 0.015,
      "ausrichtung": "normale", "neigung": -10, "drehung_zufall": 180, "kipp_zufall": 15, "einsinken": 0.35,
      "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "farb_zufall": 0.2, "weg_ab_lod": null
    },
    {
      "id": "basalt_kruppe", "typ": "basaltbrocken", "formen": ["basalt_b", "basalt_c"],
      "zonen": ["kruppe"], "spiegeln": false, "verteilung": "cluster", "anzahl": 1, "teile": 4,
      "groesse": 0.09, "groesse_zufall": 0.35, "streckung": [1.0, 0.9, 0.7], "abstand_min": 0.015,
      "ausrichtung": "normale", "neigung": -15, "drehung_zufall": 180, "kipp_zufall": 15, "einsinken": 0.35,
      "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "farb_zufall": 0.2, "weg_ab_lod": 2
    },
    {
      "id": "basalt_schulter", "typ": "basaltbrocken", "formen": ["basalt_a"],
      "zonen": ["schulter_l"], "spiegeln": true, "asymmetrie": 0.2, "verteilung": "einzeln", "anzahl": 1,
      "groesse": 0.17, "groesse_zufall": 0.1, "streckung": [1.2, 1.0, 0.6], "abstand_min": 0.02,
      "ausrichtung": "aussen", "neigung": -5, "drehung_zufall": 30, "kipp_zufall": 5, "einsinken": 0.4,
      "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "farb_zufall": 0.0, "weg_ab_lod": null
    }
  ],
  "material": {
    "stil": { "facetten": 1.0 },
    "farbgruppen": {
      "haut": { "farbe": "#3A3540", "rauheit": 0.9, "helligkeit_zufall": 0.08, "detail": 0.5 },
      "accessoire_a": { "farbe": "#2E2A31", "farbe_2": "#4A4048", "verlauf": "keiner", "farb_zufall": 0.2, "rauheit": 0.95, "detail": 0.6 },
      "horn": { "farbe": "#2A2628", "rauheit": 0.6 },
      "akzent": { "farbe": "#1C1A1C", "rauheit": 0.7 },
      "augen": { "farbe": "#FF7A1A", "leuchten": 3.0 }
    },
    "ebenen": [
      {
        "typ": "verlauf", "an": true, "richtung": "oben_unten", "farbe_a": "#2A262E", "farbe_b": "#4A4450",
        "mischung": "multiplizieren", "mitte": 0.5, "weichheit": 0.5, "staerke": 0.4,
        "maske": { "zonen": ["ganzer_koerper"], "gruppen": ["haut"] }
      },
      {
        "typ": "risse", "an": true, "element": "glut", "art": "risse", "farbe": "#FF6A10", "intensitaet": 4.0,
        "breite": 0.006, "dichte": 0.45, "verzweigung": 0.5, "hof": 0.4, "puls_frequenz": 0.4, "puls_staerke": 0.35,
        "staerke": 1.0,
        "maske": { "zonen": ["ganzer_koerper"], "ohne": ["bauch", "pfoten"], "oben": 0.0, "rand": 0.05, "rauschen": 0.5, "gruppen": ["haut"] }
      },
      {
        "typ": "ueberzug", "an": true, "art": "asche", "farbe": "#6B6266", "menge": 0.25, "kanten": 0.4,
        "rauschen_skala": 0.08, "rauheit": 1.0, "staerke": 1.0,
        "maske": { "zonen": ["ganzer_koerper"], "oben": 0.6, "gruppen": ["haut"] }
      }
    ],
    "ebenen_accessoires": [
      {
        "id": "glut_fugen", "typ": "risse", "an": true, "element": "glut", "art": "zellfugen", "farbe": "#FF8A20", "intensitaet": 3.0,
        "breite": 0.008, "dichte": 0.7, "verzweigung": 0.2, "hof": 0.5, "puls_frequenz": 0.4, "puls_staerke": 0.35,
        "staerke": 1.0, "ziel": "alle",
        "maske": { "oben": 0.4, "rauschen": 0.2 }
      },
      {
        "id": "asche", "typ": "ueberzug", "an": true, "art": "asche", "farbe": "#6B6266", "menge": 0.25, "kanten": 0.4,
        "rauschen_skala": 0.08, "rauheit": 1.0, "staerke": 1.0, "ziel": { "typen": ["basaltbrocken"], "eintraege": [] },
        "maske": { "oben": 0.6, "rauschen": 0.2 }
      }
    ]
  },
  "effekte": { "element": "feuer", "partikel": ["funken"] },
  "_gebaut": null
}
```
Geschätzte Kosten: Basis 4.000 + Brocken (9 + 4) × 36 + 2 × 48 ≈ **4.600 Tris**, 1 Material, ohne Normal Map.

**Beispiel 2 – Rimehide Bear „Eisriese“**, aufgelöste Fassung, Gruppe E (aus `Varianten/Facettierter Eisriese mit Kristallrüstung.png`: Grundform des
Rosters. Weißes, facettiertes Zottelfell am ganzen Körper, am Nacken/den Schultern länger, im Gesicht kürzer; großer
Eiskristall-Kamm über Nacken und Rücken; Eisplatten auf Schultern, Unterarmen und Oberschenkeln; Eis an den Brauen;
eisblaue Augen):

```json
{
  "format": "kreatur_variante",
  "format_version": 1,
  "revision": 1,
  "id": "rimehide_eisriese",
  "name": "Rimehide Bear (Eisriese)",
  "basis": "rimehide_bear",
  "skelett": "quadruped",
  "muster": "quadruped/bear",
  "art": "grund",
  "gruppe": "kalt",
  "biom": "eiswueste",
  "sonder": null,
  "budget_klasse": "elite",
  "seed": 1201,
  "freigegeben": false,
  "quelle": {
    "bild": "creatures/32_rimehide_bear/input/Varianten/Facettierter Eisriese mit Kristallrüstung.png",
    "roster": "Rimehide Bear"
  },
  "statur": {
    "groesse": 1.1,
    "koerper_laenge": 1.0,
    "rumpf_hoehe": 1.0,
    "rumpf_dicke": 1.0,
    "buckel": 1.15,
    "glied_dicke": 1.0,
    "bein_laenge_vorn": 1.0,
    "bein_laenge_hinten": 1.0,
    "spur_breite": 1.0,
    "pranken_vorn": 1.05,
    "pranken_hinten": 1.0,
    "hals_laenge": 1.0,
    "kopf_groesse": 1.0,
    "kopf_breite": 1.0,
    "schnauze_laenge": 1.0,
    "schwanz_laenge": 1.2,
    "schwanz_dicke": 1.2
  },
  "bedeckung": {
    "haut": { "typ": "glatt", "rauheit": 0.8 },
    "lagen": [
      {
        "typ": "fell", "modus": "geometrie", "anzahl": 550, "laenge": 0.05, "laenge_zufall": 0.3,
        "laenge_nach_zone": { "nacken": 1.4, "schulter_l": 1.3, "schulter_r": 1.3, "schwanz": 1.3, "gesicht": 0.5, "pfoten": 0.4 },
        "breite": 0.45, "form": "spitz", "kanten": 3, "kruemmung": 0.3, "richtung": "knochen", "anlege_winkel": 25,
        "richtung_zufall": 15, "abstand_min": 0.015, "farbgruppe": "bedeckung_1", "weichheit": 0.6,
        "accessoires_aussparen": true, "seed": null, "weg_ab_lod": 2,
        "maske": { "zonen": ["ganzer_koerper"], "ohne": ["schnauze", "pfoten"], "oben": 0.0, "rand": 0.05, "rauschen": 0.2 }
      }
    ]
  },
  "accessoires": [
    {
      "id": "eis_kamm", "typ": "kristall", "formen": ["kristall_a", "kristall_schlank", "kristall_breit"],
      "zonen": ["rueckenlinie"], "spiegeln": false, "verteilung": "reihe", "anzahl": 9, "von": 0.12, "bis": 0.72,
      "reihen": 1, "groesse": 0.16, "groesse_zufall": 0.3, "groesse_verlauf": [0.6, 1.0, 0.45],
      "streckung": [1.0, 0.8, 1.3], "abstand_min": 0.03, "ausrichtung": "oben", "neigung": -20,
      "drehung_zufall": 60, "kipp_zufall": 20, "einsinken": 0.3, "auf_bedeckung": 0.6,
      "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "farb_zufall": 0.0, "weg_ab_lod": null
    },
    {
      "id": "eis_ruecken_klein", "typ": "kristall", "formen": ["kristall_a", "kristall_schlank"],
      "zonen": ["buckel", "ruecken_mitte"], "spiegeln": false, "verteilung": "cluster", "anzahl": 2, "teile": 5,
      "groesse": 0.06, "groesse_zufall": 0.4, "streckung": [1.0, 1.0, 1.0], "abstand_min": 0.02,
      "ausrichtung": "normale", "neigung": -15, "drehung_zufall": 180, "kipp_zufall": 25, "einsinken": 0.3,
      "auf_bedeckung": 0.6, "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "weg_ab_lod": 2
    },
    {
      "id": "eisplatte_schulter", "typ": "eisplatte", "formen": ["eisplatte_a", "eisplatte_zackig"],
      "zonen": ["schulter_l"], "spiegeln": true, "asymmetrie": 0.2, "verteilung": "cluster", "anzahl": 1, "teile": 3,
      "groesse": 0.15, "groesse_zufall": 0.35, "streckung": [1.2, 1.0, 0.8], "abstand_min": 0.02,
      "ausrichtung": "aussen", "neigung": -10, "drehung_zufall": 45, "kipp_zufall": 10, "einsinken": 0.3,
      "auf_bedeckung": 0.8, "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "weg_ab_lod": null
    },
    {
      "id": "eisplatte_unterarm", "typ": "eisplatte", "formen": ["eisplatte_a"],
      "zonen": ["unterarm_l"], "spiegeln": true, "verteilung": "streuen", "anzahl": 2,
      "groesse": 0.09, "groesse_zufall": 0.3, "streckung": [1.3, 1.0, 0.8], "abstand_min": 0.02,
      "ausrichtung": "aussen", "neigung": 0, "drehung_zufall": 45, "kipp_zufall": 10, "einsinken": 0.3,
      "auf_bedeckung": 0.8, "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "weg_ab_lod": null
    },
    {
      "id": "eisplatte_oberschenkel", "typ": "eisplatte", "formen": ["eisplatte_a", "eisplatte_zackig"],
      "zonen": ["oberschenkel_l"], "spiegeln": true, "verteilung": "streuen", "anzahl": 2,
      "groesse": 0.10, "groesse_zufall": 0.3, "streckung": [1.2, 1.0, 0.8], "abstand_min": 0.02,
      "ausrichtung": "aussen", "neigung": -10, "drehung_zufall": 45, "kipp_zufall": 10, "einsinken": 0.3,
      "auf_bedeckung": 0.8, "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "weg_ab_lod": null
    },
    {
      "id": "eis_brauen", "typ": "kristall", "formen": ["kristall_breit"],
      "zonen": ["stirn"], "spiegeln": false, "verteilung": "cluster", "anzahl": 1, "teile": 5,
      "groesse": 0.035, "groesse_zufall": 0.3, "streckung": [1.4, 1.0, 0.7], "abstand_min": 0.008,
      "ausrichtung": "normale", "neigung": -40, "drehung_zufall": 40, "kipp_zufall": 15, "einsinken": 0.3,
      "auf_bedeckung": 0.5, "bindung": "anker", "weichheit": 0.0, "farbgruppe": "accessoire_a", "weg_ab_lod": 1
    }
  ],
  "material": {
    "stil": { "facetten": 1.0 },
    "farbgruppen": {
      "haut": { "farbe": "#C9CED8", "rauheit": 0.85 },
      "bedeckung_1": { "farbe": "#9AA6BC", "farbe_2": "#F4F6FA", "verlauf": "ansatz_spitze", "helligkeit_zufall": 0.1, "rauheit": 0.9, "detail": 0.4 },
      "accessoire_a": { "farbe": "#7CC8F0", "farbe_2": "#D8F2FF", "verlauf": "ansatz_spitze", "rauheit": 0.15, "glasig": 0.7, "leuchten": 0.3 },
      "horn": { "farbe": "#2B2D33", "rauheit": 0.5 },
      "akzent": { "farbe": "#1F2228", "rauheit": 0.6 },
      "augen": { "farbe": "#5AB4FF", "leuchten": 0.8 }
    },
    "ebenen": [
      {
        "typ": "verlauf", "an": true, "richtung": "oben_unten", "farbe_a": "#FFFFFF", "farbe_b": "#8E9AB0",
        "mischung": "multiplizieren", "mitte": 0.45, "weichheit": 0.6, "staerke": 0.35,
        "maske": { "zonen": ["ganzer_koerper"], "gruppen": ["haut", "bedeckung_1"] }
      },
      {
        "typ": "risse", "an": true, "element": "frost", "art": "adern", "farbe": "#E6F7FF", "intensitaet": 0.8,
        "breite": 0.003, "dichte": 0.3, "verzweigung": 0.6, "hof": 0.2, "puls_frequenz": 0.0, "puls_staerke": 0.0,
        "staerke": 0.8,
        "maske": { "zonen": ["ganzer_koerper"], "gruppen": ["accessoire_a"] }
      },
      {
        "typ": "ueberzug", "an": true, "art": "frost", "farbe": "#E8F4FF", "menge": 0.2, "kanten": 0.5,
        "rauschen_skala": 0.06, "rauheit": 0.6, "staerke": 1.0,
        "maske": { "zonen": ["ganzer_koerper"], "oben": 0.5, "gruppen": ["bedeckung_1", "horn"] }
      }
    ]
  },
  "effekte": { "element": "kaelte", "partikel": ["frost_atem"] },
  "_gebaut": null
}
```
Geschätzte Kosten: Basis 4.000 + Fell 2.200 + Kristalle (9 + 10 + 5) × 15 + Eisplatten (6 + 4 + 4) × 30 ≈
**7.000 Tris**, also im Elite-Budget. Wird es knapp: `fell.modus: "silhouette"` spart rund 1.400 Tris.

**Beispiel `_gebaut`** (so sieht der Block nach dem Backen aus, nur zur Illustration):
```json
"_gebaut": {
  "quell_hash": "sha1:<Hash der Datei ohne _gebaut>",
  "datum": "2026-11-21T14:00:00",
  "werkzeuge": { "unity_varianten": "0.1.0", "blender_bedeckung": "0.1.0", "bausteine": "0.1.0", "zonen": "0.1.0" },
  "tris": { "basis": 4000, "bedeckung": 2200, "accessoires": 780, "gesamt": 6980, "lod1": 3500, "lod2": 1750 },
  "texturen": 1024,
  "statur_ampel": "gruen",
  "dateien": ["output/varianten/RimehideEisriese/RimehideEisriese.fbx"]
}
```

### 6.2 Versionierung und Seed (reproduzierbar)

- **`format_version`** (Ganzzahl): ändert sich, wenn Felder umbenannt oder entfernt werden. Neue *optionale* Felder
  brauchen keine neue Version. Werkzeuge lesen alte Versionen über ein Migrationsskript
  (`scripts/variant_migrate.py`, später) und schreiben immer die neueste.
  **Version 2 (2026-11-22):** Material-Ebenen in zwei Gruppen (`ebenen` = Körper, `ebenen_accessoires`), Migration beim
  Laden in Unity (4.3). Presets tragen ebenfalls `format_version: 2`; die Fassung 1 liegt eingefroren in
  `templates/umgebungs_gruppen/_v1/` (nur zum Lesen alter Dateien, nicht bearbeiten).
- **`revision`**: +1 bei jedem Speichern. **Gleichzeitiges Bearbeiten:** Jedes Werkzeug merkt sich die Revision
  beim Laden. Ist die Datei beim Speichern neuer (das andere Programm hat gespeichert), wird nicht überschrieben.
  Stattdessen kommt die Meldung „Datei wurde geändert – neu laden?“. Unity und Blender beobachten die Datei und laden
  automatisch neu, wenn sie selbst keine ungespeicherten Änderungen haben. Empfehlung: immer nur in einem Programm
  gleichzeitig Regler bewegen.
- **Git** ist das Gedächtnis: Varianten-Dateien und Instanzen-Listen werden versioniert. Gebackene Ausgaben werden
  nur bei freigegebenen Varianten versioniert (wie `raw/`), sonst sind sie reproduzierbar.
- **Seed:** `seed` der Variante (0 … 2.147.483.647). Jeder Eintrag (Lage, Accessoire, Muster) bekommt seinen eigenen
  Seed = `fnv1a32("<seed>:<eintrag-id>")`, außer er setzt `seed` selbst. Dadurch verändert das Ändern eines
  Accessoires **nicht** die Verteilung der anderen. Umbenennen einer `id` würfelt dieses Accessoire neu. Ebenen ohne
  `id` nutzen `"<typ>#<position>"`.
- **Gleiches Ergebnis garantiert** nur bei gleichen Werkzeug-Versionen (`_gebaut.werkzeuge`). Ändert sich ein
  Algorithmus (z. B. die Platzierung), zeigt ein Vergleichslauf (Fingerabdruck wie bei den Kreaturen), welche
  Varianten sich ändern würden. **Freigegebene Varianten** (`freigegeben: true`) werden dann **nicht automatisch**
  neu gebacken. Ihre gebackene Fassung bleibt, bis der Nutzer zustimmt (Lehre aus Testlauf 1: fertige Kreaturen
  dürfen sich nie nebenbei ändern).
- **`quell_hash`**: Hash der Varianten-Datei ohne `_gebaut`. Stimmt er nicht mehr, zeigt Unity „veraltet – neu
  backen“.

### 6.3 Wer stellt was live dar?

| Was | Unity-Regler-Fenster | Blender-Panel | Nur beim Bauen/Backen |
|---|---|---|---|
| **1 Statur** | ✅ live (Knochen + Blendshapes, angenähert) mit Statur-Ampel | ✅ live (Pose-Skalierung + Shape Keys) | Ruhepose einbacken, Shape Keys anwenden, Hüfthöhe der Clips anpassen, ggf. Clip-Satz der Statur-Klasse neu backen |
| **2 Haut** | ✅ live (Vorschau-Shader) | ≈ Annäherung | Normal Map backen |
| **2 Lagen** (Fell, Stacheln, Platten) | Ergebnis nach **„In Blender bauen“** (headless, Auto-Import). Farben live. | ✅ **live** (GN-Eingänge im Panel) | Gewichte, `_DANGLING`, LOD |
| **3 Accessoires: Platzierung** | ✅ **live** (C#, schreibt Instanzen-Liste) | zeigt die Instanzen aus der Liste an (nur lesen). Ändert man dort Werte, steht „Platzierung veraltet – in Unity aktualisieren“. | Zusammenführen, Bindung, `_DANGLING` |
| **3 Accessoires: Formen** | wählt aus der Bibliothek | ✅ **live** in der Baustein-Werkbank (z. B. Platten: Ecken, Dicke, Wölbung) | Bibliothek exportieren |
| **4 Farbgruppen + Ebenen** | ✅ live (Vorschau-Shader, alle Ebenen) | ≈ nur Grundfarben + Leuchten | **Unity** rendert Albedo/Maske/Normal im UV-Raum |
| **Rim, Puls, dangling** | ✅ live (auch im Spiel) | – | bleiben Laufzeit-Parameter |
| **Partikel (`effekte`)** | ✅ (Komponenten) | – | – |
| **Tris-Zähler + Budget-Ampel** | ✅ live | ✅ live | endgültige Zahl in `_gebaut` |

**Ablauf der Knöpfe:**
- **„In Blender bauen“** (Unity): Datei + Instanzen-Liste speichern → Blender headless baut die Lagen der Bedeckung
  auf der Basis in Ruhepose (Statur bleibt Vorschau) → Export → Unity importiert automatisch und tauscht die Vorschau
  aus. Dauer geschätzt 10–30 s (Vermutung).
- **„Backen“** (Unity): (1) Blender: Statur in die Ruhepose, Bedeckung + Accessoire-Instanzen zu **einem** Mesh
  zusammenführen, Gewichte (max. 4 pro Punkt), `_DANGLING`, gemeinsames UV-Atlas (Basis-UV + Baustein-Kacheln),
  LOD1/LOD2, Export FBX/GLB, Gegentest wie bei den Kreaturen. (2) Unity: Ebenen-Stapel per UV-Raum-Render in
  Albedo/Maske/Normal (1024²) → Prefab mit 1 SkinnedMeshRenderer, 1 Material (2. Material nur nach Material-Regel
  6.4, als eigener Teilbereich desselben Meshes), Clip-Satz des Musters bzw. der
  Statur-Klasse. (3) Vorschau-Bild + `_gebaut` schreiben.
- **Blender-Panel** (Sidebar „Variante“ im 3D-Fenster, Skript `procedural/variant_panel.py`, kein Plugin nötig):
  Laden/Speichern der Varianten-Datei, Statur-Regler, Lagen-Regler (live), Instanzen anzeigen, Baustein-Werkbank,
  Tris-Zähler.

### 6.4 Performance-Budget pro gebackener Variante

Top-down-ARPG mit vielen Gegnern gleichzeitig. **Entschieden (Nutzer 2026-11-21, E5):** Tris- und Texturbudgets wie
vorgeschlagen, Materialien nach der Material-Regel unten.

| | normal | elite | boss |
|---|---|---|---|
| **Tris LOD0** (gesamt) | ≤ 6.000 | ≤ 9.000 | ≤ 15.000 |
| davon Bedeckung | ≤ 2.000 | ≤ 3.000 | ≤ 5.000 |
| davon Accessoires | ≤ 1.500 | ≤ 2.500 | ≤ 4.000 |
| LOD1 / LOD2 | ≈ 50 % / 25 % | ≈ 50 % / 25 % | ≈ 50 % / 25 % |
| **Texturen** | 1024² | 1024² | 2048² |
| Texturen pro Variante | Albedo + Maske (+ Normal nur bei `leder`/`schuppen`) | gleich | gleich |
| **Materialien / Draw Calls** | **1** Standard, max. **2** (+ Schatten) | 1 Standard, max. 2 | 1 Standard, mehr als 2 erlaubt |
| Knochen | die des Skeletts, **keine zusätzlichen** für Varianten | gleich | gleich |
| Gewichte pro Punkt | max. 4 | max. 4 | max. 4 |
| Partikel-Systeme | ≤ 1 | ≤ 2 | ≤ 3 |

**Material-Regel (Nutzer 2026-11-21, E5):**
- **Standard ist 1 Material** pro gebackener Variante. Matt, glänzend, leuchtend (Emission), Metall und Muster laufen
  über Texturen und Masken im selben Shader. Beispiel: Platten-Ebene matt und Kristall-Ebene leuchtend gehen in einem
  Material; die Masken beider Ebenen werden beim Backen in dieselben Texturen (Rauheit, Emission …) geschrieben.
- **Ein 2. Material ist erlaubt**, wenn eine Variante echte **Transparenz** braucht (Glaskristall, Schleier), einen
  **additiven Effekt** (Aura, Hitzeflimmern) oder einen **Spezial-Shader** (z. B. Fell mit mehreren Schichten).
- **Mehr als 2 Materialien** nur bei **Bossen**.
- Jedes zusätzliche Material kostet einen Draw Call pro Gegner. Die Budget-Ampel zählt die Materialien mit.

- Die Bär-Basis hat ca. 4.000 Tris (Tripo `face_limit` 4000). Für Normal-Gegner bleiben also ~2.000 für alles
  Zusätzliche. Der Rimehide ist laut Roster Elite.
- Speicher: 1024² mit Kompression (BC7) ≈ 1,3 MB pro Textur inkl. Mipmaps → ca. 2,7–4 MB pro Variante. Geladen
  werden nur die Varianten des aktuellen Bioms.
- Spätere Sparmöglichkeit: Varianten mit identischen Schichten 1–3 teilen sich ein Mesh und unterscheiden sich nur
  im Material.
- Die Werkzeuge zeigen die Budget-Ampel live. Backen bei Überschreitung nur mit Warnung.

### 6.5 Die 7 Bilder des Nutzers in der Spec

Grob ausgefüllt, Werte als Startpunkt. **Statur** nur Abweichungen von 1.0.

| Bild | 1 Statur | 2 Haut + Lagen | 3 Accessoires (Zone) | 4 Farbgruppen + Ebenen | Eigene Basis? |
|---|---|---|---|---|---|
| **Eisriese** (Rimehide-Grundform) | groesse 1.1 · buckel 1.15 · schwanz 1.2 | Haut glatt · **Fell** ganzer Körper, 550 Zotteln, spitz, länger an Nacken/Schultern | `kristall` reihe rueckenlinie (9, groß) · `kristall` cluster buckel/ruecken_mitte · `eisplatte` schulter, unterarm, oberschenkel (gespiegelt) · `kristall` klein stirn | Fell #9AA6BC → Spitze #F4F6FA · Eis #7CC8F0 glasig 0.7 · Frost-Adern im Eis · Frost-Überzug oben · Augen blau leuchtend | nein |
| **Mossback** | glied_dicke 1.05 | Haut leder dunkelbraun · keine Lagen (Moos ist Accessoire + Ebene) | `moospolster` buckel, ruecken_mitte, kruppe, schulter, oberschenkel, unterarm_l · `moosfransen` auf den Polstern, schwingt · `pilze` cluster buckel, schulter_l, kruppe, unterarm_l, oberschenkel_r · `grasbueschel` auf Polstern | Haut #4A3428, Gesicht/Schnauze heller (verlauf + Maske) · `risse` art adern, element keins, moosgrün, auf Beinen/Flanken · `ueberzug` moos oben · Augen gelbgrün 0.4 | nein |
| **Höhlenbär** | kopf_groesse 1.05 | Haut leder schwarzbraun | `tropfsteinplatte` buckel, ruecken_mitte, kruppe, schulter, unterarm, oberschenkel, stirn · `kristall` klein, blau, `auf` den Platten | Haut #4B3530 · Platten #9B8268 · `risse` arkan blau, schwach (1.0), nur auf Platten · Kristalle blau glasig 0.5, leuchten 0.6 · Augen blau | nein |
| **Slagback** | rumpf_dicke 1.05 · buckel 1.1 · glied_dicke 1.05 | Haut leder anthrazit | `basaltbrocken` cluster buckel + ruecken_mitte (9) · kruppe (4) · einzeln schulter (gespiegelt) | Haut #3A3540 · Brocken #2E2A31 · `risse` glut auf Haut · `risse` zellfugen glut auf Brocken · Asche-Überzug · Augen orange 3.0 | nein |
| **Cragplate** | groesse 1.05 · buckel 1.15 | Haut leder graubraun | `steinplatte` stirn, schulter, unterarm, oberschenkel, ruecken_mitte, kruppe · `felszacke` reihe rueckenlinie (11, 2 Reihen versetzt) | Haut #8A7A70 · Platten #77777A / #9A6A48 farb_zufall 0.35 (grau/rostbraun) · Staub-Überzug | nein |
| **Quillback** | koerper_laenge 1.25 · rumpf_hoehe 0.75 · buckel 0.3 · bein_laenge vorn/hinten 0.7 · pranken_vorn 1.5 · kopf_groesse 0.85 · schnauze 1.45 · hals 0.8 · schwanz 1.5 | Haut leder dunkel blaugrau · **Stacheln** ruecken_gesamt + flanken + kopf_oben + schwanz (250, lang 0.12, angelegt 30°) · Lage 2 **Fell kurz** gesicht + nacken (creme) | `grabkralle` pranke_vorn (4, groß) | Stacheln #E8E2D6, Ansatz #6A6C78 · `muster` streifen längs, Maske gesicht (Dachs-Streifen dunkel) · Beine #4A4C5C | **Grenzfall:** über die Statur machbar, aber Beine 0.7 + Länge 1.25 sind 🔴 → eigener Clip-Satz (Statur-Klasse `bear@flach`) oder eigene Basis (VARIANTEN.md Frage 4) |
| **Küstenlurker** | bein_laenge 0.5 · spur_breite 1.6 · koerper_laenge 1.5 · rumpf_hoehe 0.6 · kopf_breite 1.4 · schnauze 1.3 · schwanz 3.0 (!) · schwanz_dicke 1.6 | Haut **schuppen** (rhombus, blaugrau), Bauch heller | `stosszahn` kiefer (2) · `barteln` wange, schwingt · `dorn` reihe rueckenlinie (Stachelmähne, groß am Nacken → klein am Schwanz) · `schwanz_flosse` | Schuppen #4E6E7A · `verlauf` oben_unten zu Creme #C8B48A (Bauch) · `muster` flecken · `naesse` 0.5 | **ja**: liegende Haltung, seitliche Beine, langer dicker Schwanz liegen weit in 🔴, der Stummel reicht nicht. Die Schichten-Werte bleiben für eine eigene Basis brauchbar. |

### 6.6 Übergang von `roster.toml`

Heute stehen die Varianten als **Text** in `creatures/roster.toml` (`varianten = [{ art, name, biome, tint, addons,
size, effect, slider, eigene_basis, look }]`). Das bleibt die **Planungsliste** (Brainstorming, Schritt 0). Die
Varianten-Datei ist das **Bau-Rezept**.

| Roster-Feld | wird in der Varianten-Datei … |
|---|---|
| `name` | `name`; `id` = snake_case davon |
| `art`, `biome` | `art`; `biome` → `gruppe` + `biom` nach der Abgleich-Tabelle in 5.2 |
| `size` | `statur.groesse` |
| `slider` (Text) | Startwerte der Statur-Regler (von Hand bzw. vom Agenten aus dem Bild gesetzt) |
| `addons` (Text) | Einträge in `accessoires` und/oder `bedeckung.lagen` (Regel 2.1: flächig = Lage, einzeln = Accessoire) |
| `tint` (Text) | `material.farbgruppen` + `verlauf`/`muster` |
| `effect` | Material-Ebene `risse`/`ueberzug` (Look) **und** `effekte` (Element, Partikel) |
| `eigene_basis = "ja"` | **keine** Varianten-Datei auf dieser Basis → eigene Kreatur |
| `look` | bleibt im Roster (nur für Bild-Prompts) |

**Übergang Schritt für Schritt:**
1. Neues optionales Roster-Feld `datei = "varianten/<id>.variant.json"` pro Variante. Ist es gesetzt, gilt die Datei,
   und die Textfelder sind nur noch Beschreibung.
2. Ein Skript (später, `scripts/variant_new.py <kreatur> "<Variantenname>"`) legt die Datei aus dem Roster-Eintrag
   an: Kopf, `statur.groesse = size`, alle anderen Regler 1.0, leere Schichten. Die Textfelder kommen als `notiz`
   in den Block `quelle`. Text wird **nicht** automatisch in Werte übersetzt (das wäre Raten). Die Werte setzt der
   Nutzer im Unity-Fenster oder ein Agent aus dem Bild (wie in 6.5).
3. Bestandskreaturen (Strategie G8 b, eingebrannte Details) bekommen Varianten-Dateien mit leerer `bedeckung.lagen`.
   Sie nutzen nur Accessoires (Zusatzteile) und Material-Ebenen. Statur nur in der grünen Zone.
4. `make_prompts.py --stage variants` und `templates/VARIANTEN_VORLAGE.md` bleiben unverändert. Die Einsortier-Tabelle
   dort entspricht schon den 4 Schichten.

---

## 7. Entscheidungen des Nutzers

Alle Punkte E1–E8 sind **entschieden (Nutzer 2026-11-21)**. E1–E4 und E6–E8 wie empfohlen, E5 mit geänderter
Material-Regel (6.4).

| # | Frage | Empfehlung Claude | Status |
|---|---|---|---|
| **E1** | Format der Varianten-Datei: **JSON** oder TOML? | **JSON.** Unity und Blender lesen und schreiben es ohne Zusatzbibliothek. Die Kommentare von TOML gingen beim Schreiben durch die Programme ohnehin verloren. | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |
| **E2** | Bedeckung: genau 1 Lage oder **Haut + bis zu 2 Lagen** mit getrennten Bereichen? | **Haut + bis zu 2 Lagen**, Standard 1. Der Quillback braucht Stacheln auf dem Rücken + kurzes Fell im Gesicht. Gemeinsames Tris-Budget. | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |
| **E3** | Statur in der roten Zone: Regler hart begrenzen oder **Clip-Satz pro Statur-Klasse neu backen**? | **Neu backen erlauben** (unsere Clips sind prozedural, also ohne Handarbeit), aber nur als bewusste „Statur-Klasse“ mit eigener Abnahme. Sonst Regler auf Gelb begrenzen. | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |
| **E4** | Accessoire-Bindung: Standard **`anker`** (Gewichte des Ansatzpunkts) oder streng 100 % am nächsten Knochen? | **`anker`**: bleibt genauso formstabil, sitzt aber auch zwischen zwei Knochen (Schulter, Buckel) sauber auf der Haut. `knochen` bleibt als Option. | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |
| **E5** | Budget: **6.000 / 9.000 / 15.000 Tris** (normal/elite/boss), 1024² (Boss 2048²)? | **Ja.** Damit passt der Eisriese mit vollem Fell ins Elite-Budget, normale Gegner bleiben schlank. Nach dem ersten Unity-Test mit 30–50 Gegnern nachjustieren. | **Entschieden (Nutzer 2026-11-21), geändert:** Tris- und Texturbudgets wie empfohlen. Material: Standard 1, ein 2. Material nur für echte Transparenz, additive Effekte oder Spezial-Shader, mehr als 2 nur bei Bossen (Material-Regel 6.4). |
| **E6** | Accessoire-Platzierung und Material-Backen **nur in Unity** (Blender zeigt nur an), oder in beiden Programmen? | **Nur Unity.** Doppelte Umsetzung würde früher oder später auseinanderlaufen, und das gebackene Material ist dann exakt die Vorschau. Blender bekommt die Live-Regler dort, wo es selbst rechnet: Lagen der Bedeckung, Baustein-Formen (z. B. Platten), Statur. | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |
| **E7** | Braucht **jedes Monster alle 9 Umgebungs-Gruppen** oder nur die passenden? | **Nur die passenden**, typischerweise 4–6 pro Monster. Sie stehen als Liste `gruppen` beim Monster im Roster. Ein Eis-Wesen in der Wüste wirkt beliebig, und 50–100 Basen × 5 ergeben genau die Zielgröße von 250–500 Varianten. Über die Presets ist eine weitere Gruppe später fast ohne Aufwand ergänzt. Für den Bären: A, B, D, E, H (+ F, falls der Lurker eine eigene Basis wird). | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |
| *(Biome)* | Biom-Liste aus dem Bild: Schwefelebene, Hölle, Himmel MVP oder Sondervariante? Steppe → A, Highlands → D, `fungal`? Höhle/Krypta/Tempel als eigene Achse „Ort“? | siehe 5.2, Abgleich-Tabelle | **Schwefelebene, Hölle, Himmel: MVP bestätigt (Nutzer 2026-11-21).** Steppe, Highlands, `fungal` und Achse „Ort“ sind Teil des Abgleichs Roster ↔ Biome (eigener Punkt im BACKLOG G9). Offene Kleinigkeit: Gruppe I zeigt „(5)“, im Bild nur 4 Biome. |
| **E8** | Quillback und Küstenlurker: auf der Bären-Basis oder eigene Basis? (ergänzt VARIANTEN.md Frage 4) | **Quillback** als Bären-Variante mit eigener Statur-Klasse `bear@flach` (E3). **Küstenlurker** eigene Basis: Haltung, Beinstellung und Schwanz liegen zu weit außerhalb. | **Entschieden (Nutzer 2026-11-21):** wie empfohlen. |

---

## 8. Für den Entwickler-Agenten: Bau-Reihenfolge (Vorschlag)

Nicht Teil dieses Auftrags, nur damit die Spec umsetzbar bleibt:
1. Andock-Zonen + Farbgruppen-Markierung für `quadruped` (Blender, nach dem Bären-Rig), Export `<Name>_zonen.json`.
2. Varianten-Datei: Schema, Lesen/Schreiben in Python und C#, Revision/Hash.
3. Unity-Fenster: Statur (Blendshapes + Knochen) + Ampel.
4. Baustein-Werkbank + Bibliothek (Platten, Kristalle zuerst), Unity-Platzierung.
5. Blender-Lagen (Fell, Stacheln) + „In Blender bauen“.
6. Vorschau-Shader Schicht 4 + Backen (Blender Geometrie, Unity Texturen).
7. Gruppen-Presets A–I (zuerst E und H, passend zu den Beispielen), Zusammensetzen Preset + Anpassung.
8. Erste Abnahme mit Slagback und Eisriese (Beispiele oben) gegen die Bilder des Nutzers.
