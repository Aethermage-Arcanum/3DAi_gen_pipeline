# Recherche Bewegungsmuster hexapod/mantis (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten der Gottesanbeterin. Erste Kreatur ist `creatures/20_reality_ripper/`. Es gibt noch keinen Code und keine `style.toml`.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Alle Aussagen stützen sich auf Fachartikel bzw. Abstracts,
Video-Titel und -Beschreibungen sowie die Referenzbilder. Der Bau-Agent bzw. der Nutzer sollte die Videos unten **selbst ansehen**
und die Werte dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“).

---

## 1. Stand der Kreatur

| Was | Fundstelle |
|---|---|
| Skelett **hexapod**, Muster **mantis** (`style = "hexapod/mantis"`). Vorbilder: „Gottesanbeterin – Fangschlag (Zeitlupe)“, „– Wiegen/Schaukeln (Tarnung)“ | `creatures/20_reality_ripper/creature.toml` [motion], `creatures/roster.toml` Z. 378–389, `motions/README.md` Z. 28 |
| Ursprünglicher Plan: Gang wie Spinne mit den hinteren Beinpaaren, **vorderes Paar = Sensenarme**, erhoben. Idle: Sensen wiegen, Körper schaukelt. Ready: Sensen weit aufgespannt. Attack1: Sensen-Hieb in 1–2 Frames von oben nach vorn-unten. | `docs/archiv/ROADMAP_20_KREATUREN.md` Z. 148–152 |
| Bilder: Der Nutzer hat neue Bilder geliefert. Ein brauchbares Seitenbild ist `right.png`, gespiegelt als `left.png` (Nutzer-Anweisung). Danach Tripo-Lauf, Modell geprüft (Teil B ✅). | BACKLOG G4 (Z. 77), G3 (Z. 76) |
| Tripo-Modell `raw/generate_model.glb` (Task 0d2b889c…, 110 Credits): **4.192 Tris, 3.266 Vertices, 1 Material, 3 Mesh-Teile**, normiert auf 0,90 (X) × 1,00 (Y) × 0,97 (Z). Das Modell ist also breiter als lang und fast so hoch wie breit (Klingen und Fühler). | `raw/tripo_state.json`, `review/model_check.json` |
| Freigaben Teil B: **Sensenklingen sind lose Teile** neben den Armen und sollen im Rig starr an die Arm-Knochen. **Nur das vordere Laufbeinpaar berührt den Boden**, die Hinterbeine sollen per IK auf den Boden. Der Schwerpunkt liegt deshalb außerhalb der Standfläche. | `creature.toml` [model_check.freigabe], HANDOVER Z. 29 |
| **Rig und Clips gibt es noch nicht.** Kein `rig/`, kein `output/`. Bau-Warteschlange: … Frosch → **Mantis (Reality Ripper)** → Tausendfüßer. | BACKLOG Z. 104, HANDOVER Z. 46 |

**Direkte Nutzerkritik an einer Mantis-Animation gibt es nicht**, weil nie eine gebaut wurde. Es gelten die allgemeinen Lehren:
- **Angriff muss frontal den Gegner treffen** (Skorpion C3: Der Schwanz bog nur am Ansatz, der Skorpion stach sich selbst). Für die Mantis heißt das: Die Klingenspitzen müssen einen **Zielpunkt vor dem Kopf** erreichen. Sie dürfen nie in den eigenen Körper oder in die eigenen Vorderbeine zeigen bzw. hindurchschlagen.
- **Ganzkörper statt Einzelteil** (C4, Kobra): Kein Fangschlag nur aus den Armen. Prothorax, Körper und Laufbeine arbeiten mit (Ausfallschritt).
- **Nicht roboterhaft** (C1, B3). Maßstab ist die **Needle Wasp** (B4).
- **Prüfen aus der Spielkamera** (C15): Prüfbilder zuerst schräg von oben ansehen. Dehnung zuerst an Rücken, Prothorax und Klingenansatz messen, nicht an den Fußgelenken.
- **Angriffe per Kontaktbogen prüfen** (Memory): Ein GIF zeigt nur Bild 1. Für Attack-Clips einen Kontaktbogen (Einzelbilder) erzeugen und den Treffpunkt prüfen.
- Dehnung nicht durch kleinere Bewegung lösen, Roh-Animation mitspeichern, **Death nicht anfassen** (gesperrt).

---

## 2. Prüfung der Referenzbilder (Teil A) und Sichtung des Tripo-Modells

### Referenzbilder `input/front|left|right|back.png` (+ `design.png`)
| Punkt | Befund |
|---|---|
| A1 Blickrichtung/Augenhöhe | front ✓, left/right ✓ (Kopf links bzw. rechts). **back.png ist deutlich von oben**: Man sieht die Rückenplatten von Thorax und Hinterleib flächig, die Beine sind verkürzt. Das ist keine Augenhöhe. |
| A2 gleiche Haltung | ✓ in allen Ansichten derselbe **steil aufgerichtete Prothorax** (Seitenbild ca. 50–60°), der Kopf sitzt hoch und der Hinterleib fällt nach hinten leicht ab. Das ist mantis-typisch, aber **nicht „body level“** wie im Pose-Prompt gefordert. |
| A3 nichts zwischen den Beinen | ✓ |
| A4 Beinstellung | ✓ vorn und hinten etwa gleich breit (Rückansicht). |
| A5 Gliedmaßen frei | **knapp:** In der Seitenansicht kommt der Ellbogen bzw. Oberarm des nahen Sensenarms sehr nah an Kinn bzw. Maul. In der Frontansicht reichen die **unteren Klingenspitzen bis neben die Knie der vorderen Laufbeine**. Tripo hat daraus keine Hautbrücke gebaut, aber die Klingen als **lose Teile mit Abstand** erzeugt (siehe unten). |
| A6 neutrale Grundpose | Prothorax aufgerichtet (gewollt), Klingen hoch erhoben und gespreizt. Das ist schon fast eine Drohpose. Maul offen und gezackt. |
| A7 Teilezahl | 4 Laufbeine + 2 Sensenarme ✓. **Fühler uneinheitlich:** front und back zeigen 6 (4 lange + 2 kurze, gebogene), die Seitenansicht 4 und `design.png` 2–3. **Keine Flügel**, weder im Design noch im Concept. |
| A8 dünne Teile | Klingen haben Volumen ✓. Die Fühler sind sehr dünn (Peitschen). |
| A9 Effekte/Hintergrund | ✓ grau, keine Effekte. Das Auge ist orange, aber gemalt und nicht glühend. |
| Sonstiges | left = gespiegeltes right, deshalb exakt symmetrisch (gewollt, G4). Der Hinterleib ist lang und schwer, mit gezackten, aufgefächerten Platten am Ende. Die Unterschenkel sind dünn, die Oberschenkel kräftig und facettiert. |

### Tripo-Modell (`raw/generate_rendered_image.webp`, `review/model_check.png`)
- **Sensenklingen sind 2 lose Inseln** (je ≈ 187 Vertices), Mitte bei (0,35 | ±0,29 | 0,20). Ihr **Abstand zum Hauptmesh beträgt 0,119 = 12 % der Größe**. Das ist eine deutlich sichtbare Lücke. Die **Arme selbst sind kurze Stummel** an der Brust (Coxa + Oberarm). Die Klinge schwebt daneben und davor, ihr unteres Ende nahe am Knie des vorderen Laufbeins.
- **Ein zusammenhängender Rumpf** mit allen Beinen, Kopf und Fühlern (Teil 1). Die Fühler (≈ 5–6) sind in den Kopf verschmolzen.
- **Nur die vorderen Laufbeine stehen auf dem Boden.** Die Hinterbeine schweben in der Seitenansicht sichtbar (≈ 2–3 % der Höhe).
- Von oben bilden die Laufbeine ein **X**: Die Vorderbeine greifen weit nach vorn-außen, die Hinterbeine weit nach hinten-außen. Die **Klingen liegen an den vorderen Ecken** und bestimmen die Silhouette von oben. Der Hinterleib ist lang und flach.
- Prothorax und Kopf stehen hoch, der Kopf etwa über den Hüften der Vorderbeine (nicht vorn an der Spitze).
- Symmetrie 0,1 % Abweichung, Mittellinie gerade, 1 Material ✓.

---

## 3. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen, Inhalt nur laut Titel/Beschreibung)
| Thema | Link |
|---|---|
| Fangschlag, Zeitlupe | [BBC Earth – Praying Mantis Attack in Slow Motion](https://www.youtube.com/watch?v=6uow3dM1Jzs) · [Praying Mantis strike in slow motion](https://www.youtube.com/watch?v=Dg5Loz-Gy9o) · [Mantis Attack in Slow Motion (400 fps, Grille)](https://www.youtube.com/watch?v=aDkR5uvoTaE) |
| Gehen | [Walking Praying Mantis](https://www.youtube.com/watch?v=5yGW2tej0gA) · [Praying Mantis walking and climbing](https://www.youtube.com/watch?v=jkT75z7JZaI) |
| Wiegen/Schaukeln | [Swaying Praying Mantis](https://www.youtube.com/watch?v=TJvehMfUawg) · [Praying Mantis Swaying](https://www.youtube.com/watch?v=H6vhP7aF3MM) · [Praying Mantis Wobble](https://www.youtube.com/watch?v=TvdHbeoYprA) |
| Rennen (Flucht, 300 fps) | [Praying Mantis Running Away in Slow Motion](https://www.youtube.com/watch?v=Lrqcdl7_Ftw) |
| Drohgebärde | [„Fear me!“ – Mantis Startle Display](https://www.youtube.com/watch?v=1uOS-3mryik) · [Mantis THREAT POSE!](https://www.youtube.com/watch?v=raWpqOjAPSE) · [Idolomantis Threat Display](https://www.youtube.com/watch?v=Q1LDrWS9Z1U) · [Dead Leaf Mantis – Threat Display](https://www.youtube.com/watch?v=8RyUCPPEsmY) |

### Fachliteratur (gelesen: Abstracts bzw. Zusammenfassungen)
- **Rossoni & Niven 2020**, *Biology Letters*: Fangschlag von *Polyspilota aeruginosa* bei 200 fps. [PMC7280040](https://pmc.ncbi.nlm.nih.gov/articles/PMC7280040/) · [Daten (Dryad)](https://datadryad.org/dataset/doi:10.5061/dryad.59zw3r244) · [Uni Sussex](https://sussex.ac.uk/broadcast/read/52024)
- **Oufiero et al. 2016**, *J. Exp. Biol.* 219:2733: Geistmantis *Phyllocrania paradoxa*, 1000 fps. Die Ausholphase variiert, der Schlag (Sweep) ist stereotyp. [JEB](https://cob.silverchair.com/jeb/article-split/219/17/2733/15387/Patterns-of-variation-in-feeding-strike-kinematics) (Volltext 403)
- **Corrette 1990**, *J. Exp. Biol.* 148:147: *Tenodera*. Kopf-Sakkaden und Körperdrehung richten die Mantis vor dem Zugriff aus, dann sind **Schlag und Ausfallschritt (Lunge) koordiniert**. [PDF](https://cob.silverchair.com/jeb/article-pdf/148/1/147/2868718/jexbio_148_1_147.pdf) (403, nur Abstract-Zitate)
- **Science News** zu Riesen-Regenwaldmantis: Schlag **≈ 50–100 ms**. [Artikel](https://www.sciencenews.org/article/female-mantises-strike-harder-strike) · [Live Science (4 Phasen)](https://livescience.com/mantis-strikes-deadly-precision-video.html)
- **Wosnitza et al. 2022**, *Front. Neural Circuits*: *Tenodera* auf Beutejagd. Bestimmte Neurone feuern **vor der Ausrichtung** zur Beute bzw. vor dem Drehen. [Frontiers](https://www.frontiersin.org/articles/10.3389/fncir.2022.893004)
- **Grabowska et al. 2012**, *J. Exp. Biol.* 215:4255: Stabheuschrecke. Die Vorderbeine treten oft unregelmäßig („Tasten“). **Mittel- und Hinterbeine bleiben dabei regelmäßig koordiniert wie ein Vierfuß- bzw. Wellengang.** Das ist das beste Modell für Gottesanbeterinnen, deren Vorderbeine nicht laufen. Eine eigene Gangstudie zur Mantis wurde nicht gefunden. Eine Stabheuschrecken-Studie (2015) nennt die Mantis ausdrücklich als Spezialfall. [Abstract](https://kups.ub.uni-koeln.de/47772)
- **Wiegen = Tarnung** (*Hierodula patellifera*, Ann. Entomol. Soc. Am. 2009): Wiegen und Laufen nehmen mit dem Wind zu, und auf schwankenden Blättern wurden Mantiden seltener entdeckt. [BioOne](https://bioone.org/journals/annals-of-the-entomological-society-of-america/volume-102/issue-3/008.102.0323/Behavioral-Response-of-Mantid-Hierodula-patellifera-to-Wind-as-an/10.1603/008.102.0323.full) · ruckartig-schaukelnder Gang: [HowStuffWorks](https://animals.howstuffworks.com/insects/praying-mantis.htm) · [NatGeo Dragon Mantis](https://www.nationalgeographic.com/animals/article/animals-insects-brazil-rainforests)
- **Drohgebärde** (Umbers et al. 2020, *Proc. R. Soc. B*, 58 Arten, 31 mit Display): Komponenten sind **Flügel heben bzw. spreizen** und **Arme (Fangbeine) heben und spreizen**. *Idolomantis* bäumt sich auf und wirkt fast doppelt so groß. [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.4qrfj6q7c) · [Western Sydney Univ.](https://www.westernsydney.edu.au/news-centre/stories/2020/scientists-praying-mantises-surprise-survive) · [HHMI Fotos](https://www.hhmi.org/beautifulbiology/media-detail/flamboyance-personified)

### Kernaussagen
1. **Fangschlag in 2 Hälften** (Rossoni & Niven): **Approach** = Schienbein strecken, ≈ 65 ms (in 30 % mit ≈ 20 ms Pause). **Sweep** ≈ 35 ms: Zuerst **Thrust** ≈ 10 ms (Coxa schwingt vor, Femur senkt sich, die Klaue fährt nach vorn), dann **Capture** ≈ 20 ms (Schienbein klappt gegen den Femur und schließt die Falle). **Gesamt Median 100 ms** (60–290 ms). Davor kommt die Vorbereitung: Gelenke anwinkeln, Arm einziehen. Danach folgt die Retraktion zum Maul. Phasen laut Live Science: approach, thrust, capture, retraction.
2. **Der Körper arbeitet mit:** Bei *Tenodera* sind Schlag und Ausfallschritt der Laufbeine koordiniert (Corrette). Vorher drehen Kopf und Körper zur Beute.
3. **Gang:** Es laufen nur Mittel- und Hinterbeine. Sie laufen regelmäßig, die Fangbeine sind erhoben bzw. vor der Brust gefaltet. Der Gang wirkt **ruckartig und schaukelnd** (Blatt im Wind), mit **Stop-and-go**. Auf der Flucht wird gerannt (Video oben).
4. **Wiegen:** Seitliches bzw. vor-zurück Schaukeln des ganzen Körpers, unregelmäßig wie Wind, auch im Stand.
5. **Drohen:** aufbäumen, **Fangbeine hoch und weit gespreizt** (Innenseite zum Gegner), Flügel fächern auf, teils Hinterleib hoch bzw. eingerollt und Zischen. Ziel ist, größer zu wirken.
6. **Drehen:** Kopf bzw. Prothorax richtet sich zuerst aus (Sakkade), dann folgen die Beine (Corrette, Wosnitza).

---

## 4. Bewegungsregeln (Vorschlag für die `style.toml`)

Zeitwerte bei 30 fps. **Fake it:** Rhythmus und Koordination nach Natur, Tempo nach Spielgefühl. Ein echter Fangschlag (≈ 100 ms) entspricht 3 Frames. Das bleibt so, braucht aber ein deutliches Ausholen als Telegraph.

### a) Beine
- **Slots:** Die Erkennung nummeriert von vorn. **Sensenarme = Slot 1** (`feeler_slots = [1]`), **Laufbeine = Slots 2, 3** (`walking_slots = [2, 3]`).
- **Walk = Wellengang mit Metachronwelle hinten → vorn** (lateral sequence): **LH → LF → RH → RF**, je 0,25 Zyklus versetzt. Duty **0,70–0,75**, also stehen meist 3 Füße am Boden. Das wirkt staksig und vorsichtig und passt zum Schaukeln.
  Im Baukasten heißt das: Gruppen (L3, R2) und (L2, R3) mit 0,5 Versatz plus `wave_offset` ±0,25. **Das Vorzeichen muss der Bau-Agent über die Reihenfolge der `footstep`-Events in `events.json` bestätigen.** Laut Lesart des Codes erzeugt `phase(t + offset)` mit größerem Offset den *früheren* Schritt, deshalb ist vermutlich `wave_offset = -0,25` richtig.
- **Run = diagonaler Trab** (L2+R3 gegen R2+L3, `wave_offset ≈ 0,03`), Duty 0,5.
- Die Sensenarme laufen nie mit. Beim Gehen sind sie **gefaltet vor der Brust** („Gebetshaltung“), beim Rennen eng angelegt.

### b) Frequenz, Schritt, Körper
| Clip | Zyklus | Duty | Schritt | Körper |
|---|---|---|---|---|
| Walk | **28–32 Frames** (≈ 1 Hz) | 0,72 | 0,10–0,12 × Größe | **Schaukeln vor/zurück 1,5–2,5 % Größe** + seitlich ±2–3° Gieren, Prothorax schwingt 2–4 Frames verzögert nach |
| Run | **12–14 Frames** | 0,50 | 1,4 × Walk | 8–10 % tiefer, Prothorax 10–15° flacher nach vorn geneigt, Arme angelegt, kaum Schaukeln |

- **Stop-and-go im Walk (Fake it, optional):** Innerhalb eines Loops eine kurze Mini-Pause von 2–3 Frames, in der der Körper weiter schaukelt. Das ist nur machbar, wenn Fußkontakt und Schleife erhalten bleiben. Sonst weglassen und das Ruckhafte nur über das Schaukeln erzeugen.
- **Hinterleib** zieht mit 10–15 % Zyklus Verzögerung nach (seitlich 3–5°). Die Platten am Ende sind starr (Chitin).
- **Kopf:** bleibt beim Gehen im Raum möglichst ruhig, gegen das Schaukeln stabilisiert (Jäger, Blick aufs Ziel). Dazu kleine, ruckartige Kopfdrehungen (Sakkaden) von ±10–15°.
- **Fühler:** schwingen nach. Sie sind in den Kopf verschmolzen, also ohne eigene Knochen → Baustein `rigging/dangling.py` (`[dangling]`, Region `Head`, nur dünne Teile).

### c) Idle (Lauern + Wiegen)
- Ganzer Körper wiegt sich **unregelmäßig** wie im Wind: 2 überlagerte Sinus (z. B. 1× und 2,3× pro Loop, wobei der Loop nahtlos bleiben muss). Vor/zurück 2–3 % Größe, seitlich ±3–5°. Die Füße bleiben per IK stehen.
- Der **Prothorax pendelt etwas stärker als der Thorax** (Ganzkörper, Kopf führt). Der Kopf macht 1–2 Sakkaden pro Loop.
- Die Sensen sind gefaltet vor der Brust und wiegen leicht mit. Die Klingen sind immer starr.

### d) Ready (Drohen, Loop)
- **Prothorax 15–25° steiler** aufgerichtet, Körper etwas zurück auf die Hinterbeine.
- **Sensenarme hoch und weit seitlich gespreizt** (Y-Richtung, nicht nur nach oben, sonst verkürzt die Draufsicht den Effekt), Klingen offen mit der Innenseite zum Ziel. Die Silhouette soll von oben **deutlich breiter** werden.
- **Ohne Flügel (Fake it):** Ersatz ist der Hinterleib, 15–25° gehoben bzw. aufgerollt. Wenn möglich, fächern die Endplatten etwas auf. Dazu seitliches Wiegen ±4° und leichtes Zittern.

### e) Attack1 = Fangschlag (Doppelsense frontal)
Root Motion optional (klein). Gesamt ≈ 0,8–0,9 s.
1. **Ausholen 8–10 Frames** (Telegraph): Prothorax hoch und zurück, Arme weit hoch und auseinander, Klingen geöffnet, Gewicht auf die Hinterbeine.
2. **Zustoß 3 Frames** (≈ 100 ms wie in der Natur): Thrust = Arme schwingen nach vorn-unten. Capture = Klingen klappen zu. Gleichzeitig **Ausfallschritt 0,10–0,15 × Größe** nach vorn, Prothorax kippt nach vorn-unten. **Beide Klingenspitzen treffen einen Zielpunkt** ≈ 0,35–0,45 × Größe vor dem Kopf, auf Höhe des Gegners. Das liegt **vor** den vorderen Füßen und mittig, damit die Klingen nicht durch die eigenen Vorderbeine schlagen. Event `hit` am Ende des Zustoßes.
3. **Halten/Reißen 3–4 Frames**: kleiner Ruck zurück („Reality Rip“).
4. **Zurück 8–10 Frames.**
- **Neue Selbstprüfung** (analog zum Skorpion C3): Die Klingenspitze erreicht den Zielpunkt (Abstand in cm) und schneidet weder den eigenen Körper noch die Vorderbeine.

### f) Attack2 = Kreuzschnitt (Vorschlag, siehe Frage 3)
Wechselhiebe links, dann rechts, aus einer **Drehung des Prothorax um ±20–25°**. Jeder Hieb läuft schräg von oben-außen nach vorn-innen. 2 Events `hit`, gesamt ≈ 1,0 s. Der Körper giert mit, die Hinterbeine stehen.

### g) Drehen auf der Stelle
- **Kopf bzw. Prothorax führt** 10–15° voraus (Sakkade), Thorax folgt, **Hinterleib hängt 5° nach**.
- Füße tangential (wie bei der Spinne: Außenbeine vor, Innenbeine zurück), Wellengang wie Walk. Tempo **60–90 °/s**.

### h) Hit
Prothorax ruckt zurück und zur Seite, die Arme ziehen sich schützend vor die Brust, der Hinterleib ruckt verzögert nach. ≈ 0,3 s, kehrt zur Ruhe zurück.

### i) Was die ARPG-Kamera sieht
- **Sehr gut sichtbar:** die zwei **hellen Klingen** (größte, hellste Formen), das Bein-**X**, der lange Hinterleib, die Bewegung des Prothorax (steht hoch, ist von oben gut lesbar), Spreizen der Arme, Ausfallschritt, Schaukeln des ganzen Körpers.
- **Kaum sichtbar:** Maul, Auge, Fußgelenke, senkrechtes Wippen. Fühler nur als dünne Linien.
- **Folge:** Alle Angriffe und Drohgebärden **über Weg und Breite der Klingen** lesbar machen. Prüf-GIFs und Kontaktbögen zuerst aus der Spielkamera ansehen.

### Tod (nur Info, Death bleibt gesperrt)
Wie bei Insekten üblich: auf den Rücken bzw. zur Seite kippen, Laufbeine einrollen, Sensen fallen auseinander. Erst nach Freigabe durch den Nutzer.

---

## 5. Vorschlag Clip-Liste `Hexapod_Mantis_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Hexapod_Mantis_Idle` | ✓ | 2,5–3 s | Lauern und unregelmäßiges Wiegen wie ein Blatt im Wind, Prothorax pendelt nach, Kopf-Sakkaden, Sensen gefaltet. |
| `Hexapod_Mantis_Walk` | ✓ | ≈ 1,0 s | Wellengang der 4 Laufbeine (LH→LF→RH→RF) mit schaukelndem Körper, Sensen vor der Brust, Hinterleib zieht nach. |
| `Hexapod_Mantis_Run` | ✓ | ≈ 0,43 s | Diagonaler Trab, Körper tiefer und flacher, Arme angelegt. |
| `Hexapod_Mantis_TurnLeft` / `TurnRight` | ✓ | ≈ 1,0 s | Prothorax und Kopf führen die Drehung, Füße treten tangential, Hinterleib hängt nach (60–90 °/s). |
| `Hexapod_Mantis_Ready` | ✓ | 1–1,5 s | Drohen: Prothorax steil, Sensen hoch und weit seitlich gespreizt, Hinterleib gehoben, Wiegen und Zittern. |
| `Hexapod_Mantis_Attack1` | – | ≈ 0,85 s | Fangschlag: ausholen, Zustoß in 3 Frames mit Ausfallschritt, beide Klingen frontal auf den Zielpunkt (`hit`), reißen, zurück. |
| `Hexapod_Mantis_Attack2` | – | ≈ 1,0 s | Kreuzschnitt: Wechselhieb links und rechts aus der Prothorax-Drehung, 2× `hit` (nur nach Freigabe, Frage 3). |
| `Hexapod_Mantis_Hit` | – | ≈ 0,3 s | Zurückzucken des Prothorax, Arme schützend angezogen, Hinterleib ruckt nach, Rückkehr zur Ruhe. |
| `Hexapod_Mantis_Death` | – | – | **Gesperrt** (Nutzer 2026-11-17), nur Platzhalter `death_flip` aus dem Baukasten. |

---

## 6. Erwartete Rig-Hürden (nur gelesen, nicht getestet)

1. **Die Erkennung findet keine Beine.** `rigging/hexapod_detect.py` arbeitet nur mit vielen Inseln. Füße sind dort „Inseln mit Bodenkontakt, nicht Rumpf“, und der Rumpf ist jede Insel, die die Mittellinie berührt. Der Ripper hat **1 Rumpf-Insel mit allen Beinen + 2 Klingen**. Dann ist `feet` leer, alle 8 Bein-Slots werden Platzhalter („nicht vorhanden“). Auch das Breitenprofil (`body_profile`) misst die Beine mit, sodass Petiolus und Hals falsch liegen.
   → Eine **Ein-Mesh-Erkennung innerhalb von hexapod** bauen, nach dem Vorbild `octopod_detect.detect_single` (Fußspitzen = Extremitäten der Oberflächen-Entfernung, Beinwurzel = Sprung der Wand-Dicke, `single_mesh = "auto"` nur bei ≤ 3 Teilen). Das muss eine **Kopie sein, kein Import** (Regel „kein Skelett hängt am Baukasten eines anderen“). Chitin Crawler bzw. ant müssen per Regression identisch bleiben. **Zuerst `--stage check` laufen lassen.**
2. **Fußspitzen nicht über den Boden suchen.** Nur die Vorderbeine berühren den Boden (2 statt 4), die Hinterbeine schweben, und die **Arme berühren nie den Boden**. Extremitäten müssen deshalb auch oberhalb des Bodenbands gefunden werden (Arm-Enden, Hinterfüße). Danach die Standfüße per IK auf den Boden setzen (wie `feet_to_ground` bei der Spinne).
3. **Klingen werden als Fühler erkannt.** Im Insel-Code landen lose Teile im vorderen Bereich (`head_fraction = 0.22`) oberhalb der halben Höhe bei `antennae`. Die Klingen (x ≈ 0,35, z ≈ 0,2) erfüllen das. Sie müssen stattdessen **starr an `Leg_{L|R}1_Tibia`** (bzw. Tarsus) hängen, z. B. über eine neue optionale Einstellung `[hexapod.rig]` in `creature.toml`. Die **12 % Lücke** zum Armstummel bleibt sichtbar, siehe Frage 1. Fake-it-Lösung: Klinge = Unterarm, die Tibia-Achse entlang der Klinge legen.
4. **Aufrechter Prothorax.** Das Standard-Skelett hat nur `Thorax` (waagerecht Petiolus → Hals) und `Head` (Hals → vorderster Punkt). Beim Ripper ist der vorderste Punkt die Klinge bzw. der Vorderfuß, nicht der Kopf. Der Kopf sitzt hoch auf einem langen, steilen Prothorax. Wiegen, Drohen, Sakkaden und Ausfallschritt brauchen ein Gelenk an der Prothorax-Basis.
   → Vorschlag: einen **optionalen Knochen `Prothorax`** (Thorax → Prothorax → Head), nur wenn die Erkennung bzw. Konfig ihn verlangt. Damit bleibt das Skelett abwärtskompatibel, und ant-Clips fassen ihn nicht an. Den Kopf über die Lage am höchsten Punkt vorn erkennen, nicht über `x1`. `joint_densify_review.py visible` muss den neuen Namen kennen.
5. **Arme als „Taster“ reichen nicht.** `feeler_motion` im Baukasten kann nur gieren und heben (`set_leg`). Fangschlag, Falten und Spreizen brauchen eine **Arm-IK auf einen Zielpunkt** (Klingenspitze → Ziel) plus Klapp-Winkel der Tibia. Das gehört in `mantis_clips.py` oder als neue optionale Funktion in `hexapod_kit.py` (nur abwärtskompatibel).
6. **Körper bewegen, Füße stehen lassen.** Laut `ant/README.md` trägt der Thorax die Beine (FK), deshalb maximal ~1° Drehung in Stand-Clips. Schaukeln, Ausfallschritt und Drohen brauchen aber große Körperbewegungen mit stehenden Füßen. Die hexapod-IK `set_foot` existiert. Das **„plant“-Prinzip aus `spider_clips.py`** (Standfüße durch den bewegten Körper auf Welt-Ziele setzen) muss **kopiert** werden.
7. **Gang mit 4 Laufbeinen:** `group_a` und `leg_offset` funktionieren mit Slots 2/3 (diagonale Paare). Den Wellengang über `wave_offset` ±0,25 einstellen und das Vorzeichen prüfen (4a). `amp()` nutzt `phi` der Beine. Die stark nach vorn bzw. hinten zeigenden Beine (X-Form) haben große `sin(phi)`-Unterschiede, deshalb die gleiche Schrittlänge aller Füße prüfen (`stride_m`).
8. **Fühler:** Sie sind verschmolzen, `Antenna_*` bleiben ohne echte Fühler-Gewichte. Lösung: starr am Kopf + `dangling.py`.
9. **Dehnung erwartet** an Schulter bzw. Armstummel (große Armwege) und an der Prothorax-Basis (beides von oben sichtbar!). Sonst an den dünnen Unterschenkeln. Messen mit `joint_densify_review.py visible`. Gegebenenfalls Gelenk-Verdichtung, aber **nicht die Bewegung verkleinern**.
10. **Größe:** `SIZE = max(arm.dimensions)` ist hier die Breite bzw. Höhe mit Klingen und Fühlern (≈ 1,0), nicht die Körperlänge. Schritt- und Ausfall-Anteile darauf beziehen bzw. im Bau gegen die Körperlänge (ohne Klingen) prüfen.

---

## 7. Offene Fragen an den Nutzer

1. **Lücke zwischen Arm und Klinge** (12 % der Modellgröße, von oben sichtbar): Im Rig die Klingen an die Armstummel heranrücken, sodass die Klinge zum Unterarm wird (kein neuer Tripo-Lauf), oder so lassen? **Empfehlung: heranrücken** (Fake it, kostet nichts). Ein neuer Tripo-Lauf mit freieren Armen wäre die teure Alternative.
2. **Drohgebärde ohne Flügel:** Das Modell hat keine Flügel. Als Ersatz Sensen weit seitlich spreizen + Hinterleib heben bzw. Endplatten auffächern? **Empfehlung: ja**, keine Flügel nachrüsten.
3. **Attack2 „Kreuzschnitt“** (Wechselhieb links und rechts, 2 Treffer) gleich mitbauen oder erst nur Attack1? **Empfehlung: gleich mitbauen**, wie bei der Spinne. Er nutzt dieselbe Arm-IK.
