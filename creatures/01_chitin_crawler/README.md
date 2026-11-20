# Chitin Crawler

Insects · Forest · Early Game · Schwarmgegner. Drops: Chitin, Ichor, Mandible.
Concept: `_concept/monster_progression_A_vs_B.webp` (Design Artist A, Stil Artist B Low-Poly).

## Lauf 1 (2026-11-17)

| Schritt | Ergebnis | Credits |
|---|---|---|
| Bilder (ChatGPT) | 4 Ansichten, Low-Poly-Look gut; kleine Abweichungen bei Fühlern, Kopf, Hinterleib-Muster, Beinhaltung | – |
| Modell (P2, face_limit 3000, multiview) | 3.122 Dreiecke, 1 Material, 2048² Color + Normal + ORM, UVs vorhanden | 110 |
| Rig-Check | riggbar, **empfiehlt octopod** | 0 |
| Rig (octopod) | 30 Knochen, max. 4 Gewichte/Vertex. Benennung nur teilweise sprechend (`tripo::Spine_*`, `Head_*`, ein `Limb`-Strang, Rest `bone_6..25`) | 25 |
| Animation `hexapod:walk` | **kaputt**: Preset passt nicht zum Achtbeiner-Rig | 10 |
| **Summe** | | **145** |

### Befunde
- **Das Modell hat 8 Beine statt 6.** Die ChatGPT-Ansichten waren bei der Beinzahl nicht eindeutig (gespreizte Front, verdeckte Beine in den Seitenansichten). Der Rig-Check hatte recht.
- Skript-Fehler (behoben): „auto“ folgte dem Rig-Check statt dem Bauplan, und das Animations-Preset folgte dem Bauplan statt dem tatsächlichen Rig. Jetzt gilt: der Bauplan gewinnt, und bei einer Abweichung **stoppt das Skript vor dem Bezahlen**. Das Preset richtet sich nach dem echten Rig-Typ.
- Rig-/Animations-GLB ist auf ca. 2 m normiert und anders ausgerichtet als das Generierungs-GLB. Es enthält ein 2. Mesh-Objekt. → In der Blender-Nachbearbeitung prüfen.
- Look: Tripo liefert **weich schattierte** Normalen, der Facetten-Look geht verloren → in Blender auf Flat Shading stellen (kostenlos). Das Streifen-Muster ist schwächer als in den Bildern.
- Texturen 3 × 2048² sind für einen kleinen Schwarmgegner zu viel → in Blender auf 512–1024 verkleinern.

### Rig-Analyse (scripts/rig_report.py, scripts/render_rig.py)
- **Tripos Octopod-Rig ist für dieses Modell unbrauchbar:** 30 Knochen in 19 Ketten, nur ca. 2 von 8 Beinen haben eine durchgehende Beinkette. Der Rest sind lose Einzelknochen, teils außerhalb des Körpers. Die Benennung ist größtenteils generisch (`bone_6..25`).
- Zusätzlich liegt ein Fremdobjekt `Icosphere` (42 Vertices) in der Datei.
- → Ein `octopod:walk` (10 Credits) würde nur dieses kaputte Rig bewegen. **Nicht gekauft.**
- Konsequenz: eigenes **Standard-Krabbler-Skelett** (8 Beine, bei Sechsbeinern bleibt ein Paar ungenutzt) in Blender aufbauen und automatisch ans Mesh anpassen. Tripo nur noch für Mesh + Textur.

## Bewegungs-Referenz (Naturbeobachtung)
- **Gangart Ameise = Dreifuß-Gang (tripod):** Abwechselnd stehen je drei Beine am Boden, und zwar Vorder- und Hinterbein der einen Seite plus Mittelbein der anderen Seite. Das Muster bleibt über viele Geschwindigkeiten gleich. Schneller wird die Ameise durch längere Schritte und höhere Schrittfrequenz, nicht durch eine andere Gangart.
  - [Stepping patterns in ants (J Exp Biol 1994)](https://cob.silverchair.com/jeb/article-pdf/192/1/95/2854548/jexbio_192_1_95.pdf)
  - [Desert ants, slow vs. fast walking, mit Video-Frames (2015)](https://link.springer.com/article/10.1007/s00359-015-0999-2) · [Abbildung](https://pmc.ncbi.nlm.nih.gov/articles/PMC4439428/figure/Fig5)
  - [ScienceDaily: Ameisen erhöhen Tempo über Schrittlänge/-frequenz](https://sciencedaily.com/releases/2014/07/140701193249.htm)
- **Video:** YouTube-Kanal „Ant Lab“ (Dr. Adrian Smith), Makro- und Zeitlupenaufnahmen von Ameisen ([Hinweis](https://digitalcameraworld.com/news/this-incredible-slow-motion-video-shows-insects-taking-flight)). Freie Makro-Clips: [Videezy: rote Ameisen in Nahaufnahme](https://www.videezy.com/abstract/33664-close-up-of-red-ants-walking-around-on-the-ground)
- Falls 8 Beine bleiben: Spinnen laufen mit abwechselnden 4er-Gruppen (alternating tetrapod). Dafür bräuchten wir ein Spinnen-Video als Referenz.

## Lauf 2: eigenes Standard-Rig (2026-11-17, 0 Credits)
`python scripts/crawler_pipeline.py creatures/01_chitin_crawler --name ChitinCrawler` → **✓ alle Prüfungen bestanden**

- Erkennung: 8/8 Beinketten, Fühler, Rumpfachse (Taille x = −0.043, Hals x = 0.215)
- **Das vorderste Paar (Slot 1) sind erhobene Taster** und erreichen den Boden nicht → `feeler_slots = [1]`. Gelaufen wird auf den Paaren 2–4: Ameisen-Dreifuß A = {R2, L3, R4}, B = {L2, R3, L4}.
- Rig: 43 Knochen, 0 Vertices ohne Gewicht, max. 2 Einflüsse pro Vertex
- Walk: 20 Frames @ 30 fps (0,67 s), Bodenkontakt in der Standphase ≤ 7 mm, Schrittlänge 8–11 cm, Fußhöhe im Schwung 7–14 cm
- **Unity-Laufgeschwindigkeit: 0,28 m/s** (bei Modellgröße ~1 m; skaliert linear mit der Größe)
- Export: `output/ChitinCrawler.fbx` (3.122 Dreiecke, 1 Material, Texturen 1024², Clip „ChitinCrawler|Walk“) + `.glb`
- Iterationen bis dahin: Beine nicht erkannt (Lücken) → Spannbaum. Untere Segmente als Füße → nur Spitzen. Taille falsch (zu wenige Vertices) → Oberflächen-Sampling. Lose Segmente/Panzerrisse → Zuordnung + weiche Rumpfgewichte. Füße hoben sich nicht/sanken ein → Achsen aus der Geometrie. Ungleiche Schritte → Schwenkwinkel pro Bein.

### Refinement 1: Fühler zu unruhig (Feedback Nutzer)
| | Ausschlag Spitze (Welt) | Ausschlag ggü. Kopf | max. Geschwindigkeit |
|---|---|---|---|
| vorher | 14 cm | 11,5 cm | 1,27 m/s (4,5× Lauftempo) |
| nachher | 4–5 cm | 4 cm | 0,26 m/s (< Lauftempo 0,28) |

- Ausschlag 12° → 4°, Frequenz 2 → 1 pro Zyklus, Spitzenglied 0,8 → 0,4, Kopfwackeln reduziert
- Neu: **Fühler-Stabilisierung** (`antenna_stabilize = 0.8`): Die Fühler gleichen die Kopfdrehung aus, wie bei echten Insekten
- **Fehler dabei gefunden:** Die Seitwärtsbewegung von Fühlern und Tastern lief mit halber Frequenz → Sprung bei jedem Loop-Übergang. Behoben. Die Schleifenprüfung umfasst jetzt **alle** Knochen statt nur der Füße (max. Sprung 0,0 mm).
- Alle Werte gelten als neue Standardwerte für alle Krabbler (`rigging/crawler_defaults.toml`).

### Refinement 2: Brüche an Knien/Beinansätzen (Feedback Nutzer)
Neue Selbstprüfung `rigging/check_gaps.py`: Vertex-Paare aus verschiedenen Mesh-Teilen, die in Ruhe aneinanderliegen, werden über alle Frames verfolgt.

| Stand | max. Aufklaffen | Gelenke über Grenze |
|---|---|---|
| Segmente starr (vorher) | 3,4 cm (Coxa ↔ Thorax) | 7 |
| + Gelenkmanschetten (weiche Zone an jedem Gelenk) | 1,9 cm | 4 |
| + Rumpf übernimmt Gewichte naher Bein-Vertices (max. 80 %) | **1,3 cm** | **0** (Grenze 1,5 cm) |

- Die verbleibenden 1,3 cm liegen zwischen den Ansätzen von L2 und L3, die sich in Ruhe berühren und im Gegentakt schwingen, und treten nur im ungünstigsten Frame auf. Aus der ARPG-Kamera nicht sichtbar.
- Jetzt max. 4 Einflüsse pro Vertex (Unity-Standard).
- Die Lückenprüfung ist fester Teil der Pipeline (`[gaps]` in `crawler_defaults.toml`).

## Nächste Entscheidung
- **A) 8 Beine akzeptieren:** nur Animation `octopod:walk` neu (≈10 Credits)
- **B) 6 Beine wie geplant:** Bilder mit eindeutig 6 Beinen neu machen, dann Modell + Rig + Animation neu (≈145 Credits)
