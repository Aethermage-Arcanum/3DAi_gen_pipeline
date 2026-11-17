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

## Nächste Entscheidung
- **A) 8 Beine akzeptieren:** nur Animation `octopod:walk` neu (≈10 Credits)
- **B) 6 Beine wie geplant:** Bilder mit eindeutig 6 Beinen neu machen, dann Modell + Rig + Animation neu (≈145 Credits)
