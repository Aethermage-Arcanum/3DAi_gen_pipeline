# Recherche Bewegungsmuster legless/sandworm (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten des Sandwurms (erste Kreatur: `creatures/12_sand_leviathan/`). Noch kein Code, keine `style.toml`.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Alle Aussagen stützen sich auf Fachartikel bzw. Abstracts,
Zusammenfassungen und Video-Beschreibungen. Der Bau-Agent bzw. der Nutzer sollte die Videos unten **selbst ansehen** und die Werte
dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“). Zahlen, die nicht aus einer gelesenen Quelle stammen, sind markiert.

---

## 1. Stand der Kreatur

| Was | Fundstelle |
|---|---|
| Skelett **legless**, Muster **sandworm** (eigenes Muster, nicht Variante von cobra: andere Fortbewegung + Abtauchen/Auftauchen + Angriff aus dem Boden) | `creatures/roster.toml` Z. 232–236 (`motion = "legless/sandworm"`), `creature.toml` `[motion] style`, HANDOVER Z. 25/89, `motions/legless/README.md` Z. 4 („geplant: sandworm“), `docs/recherche/RECHERCHE_MONSTERARTEN.md` Z. 278 |
| Vorbilder laut Roster: Regenwurm (Peristaltik), Python (rectilinear), Sandboa (Abtauchen) | `creature.toml` `[motion] vorbild` |
| Muster-Kern laut Recherche: „Ziehharmonika-Gang, **Abtauchen/Auftauchen** (68 % Auftauchen), Verschlingen“; Folge-Kreaturen: Grabwurm-Brut (small), Wurzelschlinger (rooted) | `RECHERCHE_MONSTERARTEN.md` Z. 278, 374, 436–438 |
| **Nutzer: „rundes Maul behalten“** (besser als Krokodilmaul); `look` darauf umgestellt (Commit 49c9ae8) | BACKLOG G3 (Z. 76), HANDOVER Z. 25 |
| Tripo-Modell vorhanden (110 Credits), Prüfung B bestanden; Mittellinien-Befund freigegeben („Stachelkrause um das runde Maul, Fehlalarm“) | `raw/tripo_state.json`, `review/model_check.json`, `creature.toml` `[model_check.freigabe]`, BACKLOG G3 (Commit 1cf4996) |
| **Kein Rig, keine Clips, keine README der Kreatur** (Ordner enthält nur `input/`, `raw/`, `review/`, `creature.toml`, `prompts.md`). Naturvideo-Links müssen beim Bau ins neue `creatures/12_sand_leviathan/README.md`. | Ordnerinhalt |
| Platz 2 der Bau-Warteschlange (nach Shellback) | BACKLOG Z. 104, HANDOVER Z. 46 |

**Direkte Nutzerkritik an Sandwurm-Clips gibt es nicht** (nie gebaut). Es gelten die Lehren aus Testlauf 1, die bei den
beinlosen Kreaturen schon aufgefallen sind (CLAUDE.md, `motions/legless/cobra/README.md`):
- **Ganzkörper:** Eel Stalker Walk/Ready/Attack bewegten nur Kopf/Hals; Kobra-Angriff nur Hals/Kopf, Rest starr. → Jeder Sandwurm-Clip bewegt den **ganzen Körper**, Angriffe kommen aus der Rumpf-Kontraktion.
- **Drehen = Körper biegt sich in die Kurve, Kopf führt**, kein starr gedrehtes Modell.
- **Absolute Körperform** (`legless_kit.shape()`), nicht auf eine Ruhepose addieren. Beim Leviathan liegt das Modell gerade (gut), trotzdem `shape()` verwenden.
- **Dehnung nie durch kleinere Bewegung lösen**, Roh-Animation mitspeichern, **Death nicht anfassen** (gesperrt).
- **Prüfen aus der Spielkamera** an sichtbaren Stellen: Rücken-Panzer, Ringe, Silhouette, Maul von schräg oben. Angriffe per Kontaktbogen (nicht nur Bild 1 des GIFs).

---

## 2. Prüfung Referenzbilder (Teil A) + Sichtung Tripo

Gesehen: `input/front.png`, `left.png`, `grid_4_ansichten.png` (enthält alle 4), `input/concept/design_A.png`,
`raw/generate_rendered_image.webp`, `review/model_check.png`.

| Punkt A | Befund |
|---|---|
| 1 Reihenfolge/Blick | ok (vorn = Maul, Seiten, hinten = Schwanzspitze), Augenhöhe. |
| 2 Gleiche Haltung | ok: in allen Ansichten **gerade und flach**. Der Roster-`pose` wollte „Vorderteil leicht erhoben“; das Bild hat es nicht umgesetzt – für das Rig **besser** (keine feste Krümmung). Das Aufrichten aus dem Concept kommt über Ready/Emerge. |
| 3/4 Beine | entfällt. |
| 5 Teile frei | ⚠ **Bauch-Stacheln zeigen nach unten wie Stummelbeine**; der Körper liegt auf ihnen statt auf dem Bauch. Im Modell: tiefste Punkte = 2 Stacheln seitlich im Panzerbereich (x ≈ +0,22, `fussgruppen` in `model_check.json`), Bauch und Schwanzspitze schweben. Viele seitliche Stacheln → beim Biegen stechen sie auf der Innenseite ineinander. |
| 6 Neutrale Grundpose | Körper gerade ✓. ⚠ **Maul weit offen** (Checkliste: „zu oder nur leicht offen“). Für ein Neunaugen-Maul ist dauerhaft offen stimmig, Schließen ist aber praktisch nicht möglich. |
| 7 Teilezahl | konsistent (≈ 10–11 Ringsegmente, Panzer vorn, Schwanzstachel). |
| 8/9 | ok, keine Effekte, keine Schrift. |

**Maulform:** Front = rundes Maul mit Zahnkranz ✓ (Nutzerwunsch). Seitlich liest es sich aber wie ein **Drachen-/Krokodilkopf**: Oben steht
eine Schnauzen-Haube mit Nasengrat über, darunter ein Unterkiefer-artiger Bogen (auch im Tripo-Render). Es ist ein **Mischmaul**: rund
von vorn, mit Ober-„Lippe“. Aus der schrägen ARPG-Kamera sieht man vor allem Haube + Zahnkranz.

**Tripo-Modell (Sichtung, keine Messung):** 4.228 Tris, 1 Mesh, 1 Material, symmetrisch, Maße 1,0 × 0,31 × 0,33 (inkl. Stacheln).
⚠ **Sehr gedrungen:** Länge : Dicke ≈ 3 : 1 (inkl. Stacheln, Rumpf allein grob 4–5 : 1). Eine Schlange ist 20–40 : 1. Daraus folgt
fast alles in Abschnitt 4 und 6. Das Concept zeigt einen viel längeren Wurm. Der Panzer- und Kopfbereich nimmt das **vordere Drittel** ein.
Keine feste Krümmung, keine Verdrehung (Mittellinie 0,004 × Länge).

---

## 3. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen; Links nicht selbst gesehen)
| Thema | Quelle | Was man laut Beschreibung sieht |
|---|---|---|
| Angriff aus dem Sand, Zeitlupe | [Bobbit-Wurm schlägt aus dem Sand zu (500 fps, PetaPixel 2025)](https://petapixel.com/2025/12/26/ultra-slow-motion-footage-shows-terrifying-bobbit-worm-striking-its-prey-from-under-the-sand/) · [LiveScience „Sand striker“](https://www.livescience.com/animals/sand-striker-the-glittering-bobbit-worm-that-chops-fish-in-half-with-its-retractable-jaws) | Körper liegt tief im Sand, nur das Maul ragt heraus; Zuschlag nach oben, Beute wird **ganz in den Bau gezogen** |
| Regenwurm-Peristaltik | Suchbegriff „earthworm peristalsis slow motion / time lapse“ | Verdickungs- und Streckungswellen, Borsten verankern |
| Rectilinear (Boa, Python) | Suchbegriff „rectilinear locomotion boa“ (Newman & Jayne haben HD-Video über Rastermarken gefilmt) | gerader Körper, nur die Bauchhaut wandert in Wellen |
| Sandboa gräbt sich ein | Suchbegriff „Kenyan sand boa burrowing“ | Keilkopf voran, Körper folgt, nur Augen/Nase bleiben oben |
| Sandfisch schwimmt im Sand | [Maladen et al. 2009, arXiv mit Videos](https://www.arxiv.org/abs/0910.3248) | Eintauchen Kopf voran, unter der Oberfläche eine Sinuswelle |

### Fachliteratur (gelesen: Abstracts / Zusammenfassungen)
- **Newman & Jayne 2018**, *J. Exp. Biol.* 221, jeb166199, „Crawling without wiggling“ (Rectilinear bei Boas): [PDF](https://cob.silverchair.com/jeb/article-pdf/doi/10.1242/jeb.166199/1905044/jeb166199.pdf) · [ScienceDaily](https://www.sciencedaily.com/releases/2018/01/180112132922.htm) · [Wikipedia](https://en.wikipedia.org/wiki/Rectilinear_locomotion)
- **Quillin 1999**, *J. Exp. Biol.* 202:661–674, Peristaltik von *Lumbricus terrestris* (nur Abstract/Zitate): kinematisch ähnlich über 3 Größenordnungen Masse, wenn auf Körperlänge normiert. Robotik-Review: [Case Western PDF](https://engineering.case.edu/sites/default/files/005_WormRobotAnalyticalReview[1].pdf)
- **Maladen, Ding, Li & Goldman 2009**, *Science* 325:314, Sandfisch: [arXiv](https://www.arxiv.org/abs/0910.3248) · [Goldman, American Scientist](https://goldmanlab.gatech.edu/pages/publications/pdf/AmericanSci_2010-07Goldman.pdf)
- **Sandboa (*Eryx colubrinus*) Graben**, Neoichnologie-Studie 2007: [PDF](https://doc.rero.ch/record/14109/files/PAL_E1219.pdf) · [Britannica](https://kids.britannica.com/students/article/sand-boa/313379)
- **Neunauge, Saugscheibe**: [Smithsonian Ocean „A Lamprey's Lips“](https://ocean.si.edu/node/110682) · [Clark & Uyeno 2019](https://blog.valdosta.edu/uyeno/wp-content/uploads/sites/146/2023/05/Clark_Uyeno_2019_Feeding_Jawless_Fish.pdf)

### Kernaussagen
1. **Rectilinear (Boa/Python):** Das Skelett bleibt fast gerade, die **Haut gleitet** darüber. Bauchabschnitte heben sich, setzen vorne auf und ziehen; die Kontaktzonen laufen **von vorn nach hinten**. Die Körpermitte gleitet gleichmäßig. Sehr langsam (0,01–0,06 m/s), fast lautlos (Anschleichen).
2. **Regenwurm-Peristaltik:** Abschnitte werden abwechselnd **dick+kurz** (verankern) und **dünn+lang** (strecken vor). Die Welle läuft vom Kopf zum Schwanz (retrograd); jeder Abschnitt rückt schrittweise vor. Mehrere Wellen gleichzeitig auf dem Körper (2–3, Lehrbuchwissen, nicht selbst geprüft). Bewegung skaliert mit der Körperlänge.
3. **Sandfisch im Sand:** Unter der Oberfläche **eine** große Sinuswelle (eine Periode) Kopf → Schwanz; Tempo hängt nur von der Frequenz ab; bis ≈ 1,5 Körperlängen/s; laut Zusammenfassung ≈ 0,4 Körperlängen pro Zyklus.
4. **Sandboa:** Keilkopf voran, Körper folgt in den Sand, vergraben knapp unter der Oberfläche, nur Augen/Nase oben. Lauerjäger.
5. **Bobbit-Wurm:** Körper komplett vergraben, nur das Maul oben; **explosiver Zuschlag nach oben**, danach Rückzug samt Beute nach unten (laut Videobeschreibung).
6. **Neunauge:** runde Scheibe mit konzentrischen Zahnreihen; **saugt sich fest und raspelt** (Zunge reibt). Für den Angriff: Andocken + Mahlen statt Zuschnappen.

---

## 4. Bewegungsregeln (Vorschlag für die `style.toml`)

Alle Zeitwerte bei 30 fps. „Fake it“: Rhythmus nach Natur, Tempo und Ausschlag nach Spielgefühl **und Modell-Grenze** (gedrungener Körper, Stacheln).

### a) Wellenart: Hybrid statt Schlange
Ein Körper mit Länge : Dicke ≈ 3–5 : 1 **kann nicht schlängeln wie die Kobra** (±40° bei 1,4 Wellen würde den Rumpf innen zerquetschen,
die Stacheln stechen ineinander). Vorschlag:
- **Hauptbewegung = peristaltisch/rectilinear:** 2 **Verdickungswellen** laufen Kopf → Schwanz. Ein dicker Abschnitt ist 10–15 % breiter und höher und 8–12 % kürzer, ein dünner entsprechend gestreckt. Dazu eine kleine **Buckelwelle** (Neigen ±4–6° je Wirbel) im gleichen Takt, damit sich Rückenplatten heben und senken.
- **Darüber ein leichtes seitliches Wiegen** für die Draufsicht: **±8–12°** Gieren, **0,5–0,7 Wellen** auf der Länge (lang, ruhig), Kopf führt um ≈ 20° Phase.
- **Kopf „schiebt“:** Der Kopf schießt in jeder Streckphase 2–3 % der Länge vor und stoppt beim Verankern. Das ergibt einen Ruck-Gleit-Rhythmus und macht die Masse spürbar.

### b) Frequenz und Tempo
| Clip | Zyklus | Wellen | Ausschlag | Vortrieb (für Unity-Tempo) |
|---|---|---|---|---|
| Walk (Kriechen) | **40–48 Frames** (1,3–1,6 s) | 2 Verdickungswellen + 0,6 Gier-Welle | Breite ±12 %, Gieren ±10° | ≈ 0,15–0,2 L pro Zyklus (Wurm, Vorschlag) |
| Run (Sand-Pflügen) | **24–28 Frames** | 1 Sinuswelle (Sandfisch-artig) | Gieren **±18–22°** (Modell-Grenze testen), Breite ±8 % | ≈ 0,35–0,4 L pro Zyklus (Sandfisch-Wert) |

Groß und schwer: lieber langsamer und wuchtiger als die Kobra (36/20 Frames).

### c) Kopf und Maul
- Kopf **dauernd leicht erhoben** (5–10°), pendelt in Walk ±5° mit.
- **Maul nie ganz schließen** (Modell offen, ≤ 20° Kiefer-Bewegung reißt sonst – Kobra-Erkenntnis). Stattdessen **„Pumpen“**: Jaw ±6–10° plus Kopf-Nicken; im Idle langsam, im Ready schnell (Hecheln). Das runde Maul liest sich über die Kopf-Ausrichtung zur Kamera, nicht über die Kieferöffnung.
- **Neunaugen-Raspeln** im Angriff: Kopf-Rollen ±10–15° zweimal hin und her, während das Maul „anliegt“.

### d) Eingraben und Auftauchen (Clip-Idee)
- **Burrow (Abtauchen) ≈ 1,6–2,0 s:** Kopf neigt sich 30–40° nach unten und bohrt am **festen Eintrittspunkt** in den Boden. Jeder Wirbel taucht ab, wenn er diesen Punkt erreicht („follow the leader“ wie bei der Sandboa). Root Motion nach vorn ≈ 1 L. Zum Schluss ragt höchstens die Schwanzspitze kurz heraus. Ein letzter Peitschenschlag ist erlaubt. Events: `sand_burst` (Eintritt), `burrowed` (Ende).
- **Emerge (Auftauchen) ≈ 1,2–1,5 s:** Kopf bricht **steil (50–70°)** aus dem Boden, das vordere 40–50 % schießt hoch, Maul zum Himmel, Hochpunkt halten (2–4 Frames), dann kippt der Vorderkörper **mit Gewicht nach vorn** auf den Boden (Nachfedern) und endet in der Ready-Pose. Der hintere Körper zieht dabei aus dem Boden nach. Events: `sand_burst` (Durchbruch), `emerged`.
- Unter der Erde bewegt Unity nur einen Sand-Wellen-Effekt (Decal/Partikel), das Mesh ist versteckt (Renderer aus oder unter dem Boden). Kein eigener Clip nötig.

### e) Drehen
- Der Körper legt sich auf einen **flachen Bogen** (Gesamt-Krümmung Schwanz → Kopf ≈ **45–60°**, nicht 90° wie Kobra – Modell-Grenze), Hals/Panzer führen 15–20° zusätzlich, der Kopf 10°. Die Peristaltik läuft weiter (70 %). Tempo ≈ 60–90 °/s, schwerfällig. Unity dreht das Objekt.

### f) Angriff
- **Ready (Loop):** Wie im Concept: **vorderes Drittel bis 40 % aufgerichtet** (Neigung bis 35–50°, verteilt über s 0,55–1,0 – der dicke Panzer braucht viele Wirbel dafür), Maul zum Ziel, Vorderkörper pendelt ±6–8°, Maul pumpt schnell, hinterer Körper liegt (Anker wie Kobra `anchor_hi ≈ 0,45`), schwache Verdickungswelle hält Spannung.
- **Attack1 = Vorstoß-Biss (Verschlingen), Root Motion, ≈ 1,1 s:**
  1. Ausholen 10–12 Frames: Vorderkörper **staucht sich zusammen** (dick + kurz, Ziehharmonika), richtet sich höher auf, Kopf zurück.
  2. **Zustoß 4–5 Frames:** Der Rumpf streckt sich explosiv (dünn + lang), der Kopf fällt nach vorn-unten aufs Ziel. Vortrieb 0,25–0,35 L. Event `hit` beim Aufsetzen.
  3. Raspeln/Festhalten 6–8 Frames: Kopf-Rollen ±12°, Rumpf ruckt 2× nach (Neunauge + Bobbit-Wurm zieht).
  4. Zurück in Ready 8–10 Frames (`returns_to_start`).
- **Attack2 = Wucht-Schlag oder Auftauch-Angriff** (siehe Frage 1): entweder **Body Slam** (Vorderkörper steil hoch, dann mit dem ganzen vorderen Drittel krachend auf den Boden, Event `hit` + AoE) oder **Erupt** (aus vergrabenem Zustand steil hochschießen und am Hochpunkt zubeißen, Bobbit-Wurm). Gewicht + Nachfedern sind Pflicht.
- **Ganzkörper:** Kein Clip, in dem sich nur der Kopf bewegt. Die Wucht kommt aus der Stauchen-Strecken-Bewegung des Rumpfs.

### g) Was die schräge Top-down-Kamera sieht
- **Sehr gut:** Silhouette von oben (breiter Panzerkopf, Ringe, Stachelkranz), **seitliches Wiegen**, **Breiten-Pulsieren** der Ringe (Peristaltik wird von oben als „Atmen/Pumpen“ der Breite sichtbar), Auf- und Abtauchen (Höhenänderung + Sand-Effekt), Aufrichten im Ready (verkürzt sich von oben → **stark übertreiben**, Kopf weit nach vorn über den Körper).
- **Gut, wenn übertrieben:** Buckelwelle der Rückenplatten (Licht/Schatten), Vorstoß (Root Motion).
- **Kaum:** Bauch, Kieferöffnung, Zähne im Detail, Raspel-Rollen (nur als Wackeln).
- **Folge:** Fortbewegung über Breite + Wiegen lesbar machen; Angriffe über Körperweg + Aufrichten. Prüf-GIFs zuerst aus der Spielkamera.

### h) Unterschied zu legless/cobra
| | cobra | sandworm |
|---|---|---|
| Körper | lang, dünn | gedrungen, dick, Panzer vorn |
| Fortbewegung | Serpenoid ±40–50°, 1,25–1,4 Wellen | **Peristaltik/Rectilinear + leichtes Wiegen** ±10° (Run ±20°) |
| Drohen | S-Schlinge + steil aufgerichtet (78°) | Vorderdrittel aufgerichtet (35–50°), Maul pumpt |
| Angriff | Stoß aus der S-Kurve | **Stauchen → Strecken**, Verschlingen + Raspeln; Slam oder Auftauchen |
| Sonder-Clips | – | **Burrow, Emerge** |

---

## 5. Clip-Liste `Legless_Sandworm_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Legless_Sandworm_Idle` | ✓ | 3–4 s | Liegt fast still, Ringe atmen (Breite ±3 %), langsame Verdickungswelle, Kopf hebt sich leicht und wittert, Maul pumpt langsam. |
| `Legless_Sandworm_Walk` | ✓ | 1,3–1,6 s | Zwei Verdickungswellen Kopf → Schwanz mit Buckelwelle, ruhiges seitliches Wiegen ±10°, Kopf schiebt ruckartig voran. |
| `Legless_Sandworm_Run` | ✓ | 0,8–0,9 s | Sandfisch-artig eine große Welle ±20°, Körper flacher, Kopf gesenkt wie ein Pflug. |
| `Legless_Sandworm_TurnLeft` / `TurnRight` | ✓ | ≈ 1,5 s | Körper legt sich auf einen flachen Bogen (45–60°), Panzer und Kopf führen, die Peristaltik läuft weiter. |
| `Legless_Sandworm_Ready` | ✓ | 1,3–1,6 s | Vorderes Drittel aufgerichtet, Maul aufs Ziel, schnelles Pumpen, Pendeln ±7°, Rest liegt als Anker. |
| `Legless_Sandworm_Attack1` | – | ≈ 1,1 s | Stauchen und Ausholen, explosives Strecken mit Vorstoß und Biss (Event `hit`), Raspeln/Nachziehen, zurück in Ready. |
| `Legless_Sandworm_Attack2` | – | ≈ 1,2 s | Body Slam (steil hoch, krachend aufschlagen, `hit`) **oder** Erupt aus dem Boden (siehe Frage 1). |
| `Legless_Sandworm_Hit` | – | ≈ 0,5 s | Vorderkörper zuckt zurück, eine Stauchwelle läuft bis zum Schwanz, zurück in Ready. |
| `Legless_Sandworm_Burrow` | – | 1,6–2,0 s | Kopf bohrt nach unten, der Körper folgt am festen Eintrittspunkt in den Boden (Root Motion, `sand_burst`, `burrowed`). |
| `Legless_Sandworm_Emerge` | – | 1,2–1,5 s | Steiler Durchbruch nach oben, Hochpunkt, Vorderkörper fällt mit Gewicht nach vorn, endet in Ready (`sand_burst`, `emerged`). |
| `Legless_Sandworm_Death` | – | – | **Gesperrt** (Nutzer 2026-11-17). Nur Platzhalter, nicht bearbeiten. |

---

## 6. Erwartete Rig-Hürden (Code gelesen, nicht getestet)

`rigging/legless_rig.py`, `rigging/legless_defaults.toml`, `motions/legless/legless_kit.py`, `rigging/rig_common.py`.
**legless_rig.py und legless_kit.py werden vom Eel Stalker mitbenutzt → nur abwärtskompatibel erweitern** (neue optionale
Parameter, Standard = altes Verhalten), danach `python scripts/regression.py`.

1. **Dicker, kurzer Körper beim Biegen:** 14 gleich verteilte Wirbel (`segments`, Rig Z. 33/45) liegen nicht auf den ≈ 10–11 Ringfurchen. Gebogen wird mitten im Ring → Ringe verformen sich, die Innenseite quetscht, Stacheln stechen ineinander. Ideen: Wirbelzahl pro Kreatur an die Ringe anpassen (`[legless] segments`), Gewichte pro Ring härter (`smooth_iterations` niedriger, Ringe fast starr wie Chitin-Lehre). Dehnung/Quetschung am Mesh/Rig lösen, nicht durch kleineres Wiegen.
2. **Kopf zu kurz:** `head_length = 0.08` (Rig Z. 34) erfasst nur das Maul. Der Panzer reicht über das vordere Drittel und würde über Spine_10–14 mitgebogen (Platten dehnen sich). Pro Kreatur `head_length` ≈ 0,15–0,2 testen oder den Panzerbereich steifer wichten; Biegung in die Ringe dahinter verlagern.
3. **Rundes Maul vs. ein Unterkiefer:** Das Rig kennt nur `Jaw` als unteren Kieferknochen (Z. 63–64, 71). Beim runden Maul verformt er nur den unteren Bogen des Zahnkranzes; > ~20° reißt das Mesh (Kobra-Erkenntnis). Ein echtes radiales „Pumpen“ bräuchte Skalierung oder mehrere Maul-Knochen (siehe Punkt 4 bzw. Frage 2).
4. **Peristaltik braucht Skalierung, der Baukasten backt keine:** `bake()` setzt Keys nur auf `rotation_quaternion` und `location` (Kit Z. 329–331). Verdicken/Strecken der Ringe = Knochen-Skalierung → neue optionale Option im Kit (z. B. `key_scale=True` nur für sandworm), Unity „Generic“ kann Skalierungs-Kurven. Alternative ohne Skalierung (schwächer): nur Buckelwelle + Vor-/Zurückversatz der Wirbel (Knochen sind nicht verbunden, `use_connect = False`, rig_common Z. 134) → erzeugt aber Dehnung zwischen den Ringen.
5. **Abtauchen scheitert an der Selbstprüfung:** `bake()` verlangt `no_ground_penetration` (Kit Z. 342, 357–359), `ground("contact")` zieht den tiefsten Punkt immer auf den Boden. Burrow/Emerge brauchen eine neue optionale Clip-Art (z. B. `kind="burrow"` bzw. `allow_below=True`), die Einsinken erlaubt und stattdessen den Eintrittspunkt prüft. `keep_centered()` passt nicht (Root Motion nach vorn).
6. **Auflage auf Stacheln:** Tiefste Punkte sind 2 Bauch-Stacheln im Panzerbereich, Bauch und Schwanzspitze schweben (`model_check.json` → `fussgruppen`). `ground("contact")` stellt den Wurm auf diese Stacheln. Beim Biegen springen die tiefsten Punkte zwischen Stacheln → Root zuckt in der Höhe. Ggf. eine leichte Neigung im Walk, damit der Bauch „schleift“, oder Bodenkontakt über einen geglätteten Wert (nur Info, Bewegung nicht verkleinern).
7. **Mittellinie durch Stacheln verzerrt:** `center()` nutzt 10/90-Perzentile je Querschnitt (Rig Z. 37–42); Rücken- und Bauchstacheln können die Wirbelhöhe verschieben. Bei der Symmetrie des Modells unkritisch, beim ersten `--stage check` im `rig_debug.json` prüfen.
8. **Kein Problem:** keine feste Krümmung (anders als Eel Stalker), 1 Mesh-Teil, keine frei hängenden Teile (Stacheln/Zähne starr, kein `[dangling]` nötig).

Neues Muster braucht: `motions/legless/sandworm/style.toml`, `sandworm_clips.py` (eigener Clip-Code, Kobra-Ideen **kopieren**, nicht importieren), `README.md`.
Pipeline findet den Generator unter `motions/<skelett>/<muster>/<muster>_clips.py` (`scripts/creature_pipeline.py` Z. 106).

---

## 7. Offene Fragen an den Nutzer

1. **Abtauchen/Auftauchen jetzt mitbauen?** Empfehlung: **ja**, `Burrow` + `Emerge` als eigene Clips, und **Attack2 = Body Slam** (funktioniert auch ohne vergraben zu sein). Ein Auftauch-Biss (Erupt) kann später aus Emerge abgeleitet werden. Braucht eine kleine, abwärtskompatible Erweiterung des Beinlos-Baukastens.
2. **Maul:** Das Modell hat ein dauerhaft weit offenes Mischmaul (rund von vorn, mit Schnauzen-Haube). Empfehlung: **offen lassen und nur „pumpen“** (kleine Kieferbewegung + Kopf), Wirkung über den Körper. Alternative: zusätzliche Maul-Knochen für radiales Öffnen/Schließen (mehr Arbeit, Eingriff ins gemeinsame Rig).
3. **Fortbewegung:** Empfehlung: **Wurm-Kriechen** (Peristaltik + leichtes Wiegen), weil der dicke Körper nicht wie eine Schlange schlängeln kann und der Sandwurm sich so klar von der Kobra unterscheidet. Alternative: schlangenartiges Schlängeln mit kleinerem Ausschlag (näher an cobra, wirkt beim gedrungenen Körper gequetscht).
