# Recherche Bewegungsmuster quadruped/gorilla (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten des Gorillas (erste Kreatur: `creatures/13_frost_colossus/`). Noch kein Code, keine `style.toml`.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Alles stützt sich auf Fachartikel bzw. Abstracts,
Video-Beschreibungen und die vorhandenen Bilder. Bau-Agent bzw. Nutzer sollten die Videos unten **selbst ansehen** und die
Werte dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“). Einige PMC-Volltexte waren gesperrt (Browser-Prüfung); das ist
unten jeweils vermerkt.

---

## 0. Skelett: `quadruped` (kein neues Skelett nötig)

| Hinweis | Fundstelle |
|---|---|
| Muster ist überall als `quadruped/gorilla` eingetragen | `creatures/roster.toml` Z. 308, `creatures/13_frost_colossus/creature.toml` (`[motion] style`), `review/model_check.json` (`skelett: quadruped, muster: gorilla`), HANDOVER Z. 26 |
| quadruped-README nennt gorilla als geplantes Muster | `motions/quadruped/README.md` Z. 5, HANDOVER Z. 87 |
| Bau-Warteschlange: Schildkröte → Sandwurm → **Gorilla** → Affe → … | BACKLOG Z. 104, HANDOVER Z. 46 |

**Warum nicht `upright` (Bog Warden)?** `upright` ist ein Zweibeiner mit freien Armen (`Pelvis → Thigh/Shin/Foot`, Arme
`Clavicle → UpperArm → Forearm → Hand → Fingers`, `rigging/upright_rig.py` Z. 1–20). Der Frost Colossus **steht und läuft auf
vier Gliedmaßen** (4 Bodenkontakt-Gruppen, `model_check.json` → `fussgruppen`) und hat einen **langen Schwanz**, für den
`upright` keine Kette hat. Ein Knöchelgang im upright-Baukasten wäre ein neuer Vierfuß-Gang = Umbau eines fremden Baukastens.
**Warum `quadruped` reicht:** Das Skelett hat Schultern + 4-gliedrige Beine + `Tail_1..4`. Das Aufrichten auf die Hinterbeine
gibt es schon im Bären (`bear_clips.py` → `rear_body()`, Attack2 bis 66° Brustneigung, Pranken per IK hoch). Was fehlt
(Ellbogen-Richtung beim Trommeln), lässt sich mit `ik_off()` + direkter Knochendrehung im eigenen Clip-Code lösen.
**Kein neues Skelett nötig.** (Entscheidung beim Orchestrator/Nutzer; dies ist die Empfehlung.)

### Abgrenzung Gorilla (Frost Colossus) ↔ Affe (Ruin Howler, `quadruped/monkey`)
| | Gorilla – Frost Colossus | Affe – Ruin Howler |
|---|---|---|
| Rolle | schwerer Brecher/Tank, Nahkampf | Schwarm/Fernkampf, Rudel, wirft Steine (roster Z. 722) |
| Körper | massiv, Arme riesig und säulenartig, breite Front (Vorderhände 0,56 vs. Füße 0,31 auseinander) | schlaksig, lange Arme, kürzere gebeugte Beine, langer dicker Schwanz |
| Gang | langsamer, schwerer Knöchelgang, Körper „stelzt“ über die gestreckten Arme, Schultern rollen | schneller, federnder Vierfüßergang (Pavian), mehr Hüpfen/Hopsen |
| Tempo-Gang | schwerer Galopp beim Sturmangriff (kurz) | häufige Sprünge, Wendigkeit |
| Drohen | Aufrichten, Brusttrommeln, Faust auf den Boden | Brüllen (Brüllaffe), Zähne zeigen, Hüpfen |
| Angriffe | Doppelfaust-Hammer, Sturm + Hieb (Ganzkörper, Gewicht) | Steinwurf (Projektil-Event), Biss/Sprung |
Gemeinsam nur der Baukasten `quadruped_kit.py` (lesend). **Kein gemeinsamer Clip-Code** (Kapselungsregel `motions/README.md`).

---

## 1. Stand der Kreatur

| Was | Stand | Fundstelle |
|---|---|---|
| Referenzbilder | `input/front/left/right/back.png` vom 18.11., noch aus der Zeit **vor** dem zweistufigen Prompt (kein `input/design.png`). Concept `input/concept/design_A.png` (stark verpixelt). | Ordner, BACKLOG A10 |
| Prüfung A | ✅ Claude hatte erst Einwände; Nutzer: „Gorilla-Bilder sind gut – Claudes Einwand war eine Fehleinschätzung wegen der Perspektive“ | BACKLOG G3, G4; HANDOVER Z. 70 (gestreckter Schwanz wirkt in der Rückansicht wie hängender Streifen) |
| Tripo-Modell | `raw/generate_model.glb` (110 Credits, Task be817a02…), Commit 02e48e8 | `raw/tripo_state.json`, BACKLOG G3 |
| Prüfung B | ✅ „Frost Colossus“ ohne Befund freigegeben | BACKLOG G5; `review/model_check.json` / `.png` |
| Kennzahlen Modell | **4.669 Tris**, 7.715 Vertices, 1 Teil, 1 Material, Maße normiert 1,0 × 0,80 × 0,77 (L × B × H). Füße vorn x = +0,33 (y ±0,28), hinten x = −0,115 (y ±0,155). Bauchlinie 0,44 H. Schwerpunkt x = +0,13 (über der Standfläche). | `review/model_check.json` |
| README der Kreatur | **fehlt** (Bau-Agent legt sie an, mit Videolinks aus Abschnitt 3) | – |
| Rig / Clips / Export | **nichts vorhanden** (kein `rig/`, kein `output/`) | Ordner |
| Nutzer-Kritik an der Bewegung | keine (nie gebaut). Es gelten die allgemeinen Lehren: Ganzkörper (C4), nicht roboterhaft (C1), Angriffe aus dem ganzen Körper (C3), Dehnung an der Ursache beheben, Roh-GIFs speichern, Prüfen aus der Spielkamera (C15), **Death nicht anfassen** | CLAUDE.md „Lehren aus Testlauf 1“, BACKLOG C1/C3/C4/C15 |
| Vorbild im Roster | „Gorilla – Knöchelgang (vierbeinig)“, „Gorilla – Aufrichten, Brusttrommeln, Schläge (Angriff eher humanoid)“ | roster Z. 310 |
| Nachbar-Muster | `quadruped/bear` (Rimehide Bear) ist das nächste Vorbild: schwer, Aufrichten, Doppel-Slam, Statur-Hinweise | `motions/quadruped/bear/README.md` |
| Varianten | Im Roster hat der Frost Colossus (Original-Kreatur) **keine** `varianten`-Liste; die Glassback Colossus (B r4c3, ebenfalls Knöchelgänger, Muster `quadruped/behemoth`, noch kein Modell) wäre ein Kandidat für eine spätere Variante dieses Musters – **nicht vorziehen**. | roster Z. 269–286 |

---

## 2. Prüfung Teil A der Referenzbilder + Sichtung `raw/generate_rendered_image.webp`

Angesehen: `input/front.png`, `left.png`, `right.png`, `back.png`, `input/concept/design_A.png`, `raw/generate_rendered_image.webp`,
`review/model_check.png`.

| Punkt | Befund |
|---|---|
| 1 Reihenfolge/Blick | ✅ vorn, Kopf links, Kopf rechts, hinten; leicht erhöhte Kamera, keine Draufsicht. |
| 2 Gleiche Haltung | ✅ in allen vier gleich: Rücken fällt von den hohen Schultern zur Hüfte ab, Arme senkrecht. |
| 3 Nichts zwischen den Beinen | ✅ Der Streifen in `back.png` ist der **gerade nach hinten gestreckte Schwanz** (Perspektive, wie im HANDOVER beschrieben). Seitenansichten zeigen ihn waagerecht. |
| 4 Beinbreite | ⚠ gewollt: Arme ≈ doppelt so breit wie die Hinterbeine (Messung hinten/vorn 0,56×, erlaubt 0,5–1,4). Gorilla-typisch, kein Fehler – aber knapp an der Grenze. |
| 5 Gliedmaßen frei | ✅ Arme in Front-/Rückansicht klar vom Rumpf getrennt (Lücke sichtbar), Hinterbeine frei. Keine Hautbrücken im Modell (`model_check.png`). |
| 6 Grundpose | ✅ gerade, Schwanz gestreckt. Maul leicht offen mit Fängen (erlaubt). |
| 7 Teilezahl | ⚠ **Schwanz:** `look` sagt „like a gorilla it has no tail“ (roster Z. 317–318), Bilder **und Modell** haben einen **langen Stachelschwanz** (≈ 1/3 der Länge, `model_check.png` oben). Nutzer hat die Bilder abgenommen → Frage 1. Sonst 4 Gliedmaßen, 1 Kopf, stimmt. |
| 8 Dünne Teile | ✅ Eiszacken haben Volumen, keine einseitigen Flächen (0 laut Messung). |
| 9 Effekte | ✅ neutral; nur leicht leuchtende hellblaue Augen (unkritisch). |
| **Knöchel** | ⚠ Die „Fäuste“ sind als **massive Pfotenklötze mit 4–5 nach vorn zeigenden Eiskrallen** gestaltet (eher Elefanten-/Bärenpranke als echte eingerollte Gorilla-Fingerknöchel). Die Knöchel selbst sind nicht verdeckt, aber es gibt **keine Finger**, die sich bewegen könnten. Folge: Hand = starrer Block, `Leg_F*_4` ist nur die Spitze des Klotzes. Aus der Spielkamera egal (Fake it). |
| **Ellbogen** | ⚠ Arm wirkt in der Seite fast **gerade wie eine Säule**; der Ellbogen ist unter Schulterplatte + Eis-Armschiene versteckt. Die Armschiene reicht vom Ellbogen bis zur Faust (großer, heller Eisblock) → beim Beugen verformt sich ihre Oberkante. Siehe Rig-Hürden 2 und 5. |
| Kopf | Kopf sitzt **tief und weit vorn zwischen den Schultern**, praktisch kein sichtbarer Hals. Kopf-Krone aus Eiszacken. |
| Concept `design_A.png` | zu verpixelt für Details; erkennbar: gebückte, massige Bestie mit langen Armen. Schwanz im Concept nicht entscheidbar. |
| `generate_rendered_image.webp` | Tripo-Render entspricht den Bildern: riesige Eis-Armschienen, Schulterplatten mit Kristall, tiefer Kopf, gespreizte Arme; Schwanz aus dieser 3/4-Front kaum zu sehen. Keine verschmolzenen Teile sichtbar. |

**Ergebnis:** Keine Bildmängel, die ein neues Modell erzwingen (Guthaben 45 Credits reicht ohnehin nicht, BACKLOG Z. 132). Rig-
seitig zu beachten: Schwanz (vorhanden), säulenartige Arme mit verstecktem Ellbogen, Klotz-Fäuste ohne Finger, Eis-Platten.

---

## 3. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen)
| Thema | Link | Was man laut Beschreibung sieht |
|---|---|---|
| Kampf, Sturmangriff, Zeitlupe | [Movie 1 zu Carrier & Cunningham 2017 (Omaha Zoo, 2 Männchen)](https://movie.biologists.com/video/10.1242/bio.022640/video-1) | Sohlengänger-Füße; **jeder Hinterbein-Schritt des Angreifers beginnt mit Fersenaufsatz** (0:14–0:21); Unterarm-Block (0:40–1:03); Zehen krallen sich beim Kontakt in den Boden |
| Brusttrommeln | [Silberrücken trommelt vor Fotograf (My Modern Met)](https://mymodernmet.com/silverback-gorilla-beat-his-chest-wildlife-photographer/) · [PetaPixel 2023](https://petapixel.com/2023/09/08/large-silverback-gorilla-beats-his-chest-right-in-front-of-photographer) · [Max-Planck-Video (EurekAlert)](https://www.eurekalert.org/multimedia/915420) | Aufrichten auf die Hinterbeine, schnelles Trommeln mit (hohlen) Händen |
| Boden schlagen | [Gorilla stürmt auf sein Spiegelbild zu und schlägt auf den Boden (A-Z Animals)](https://a-z-animals.com/blog/gorilla-shows-his-strength-to-his-reflection/) | Ausholen, beidhändiger Schlag auf den Boden mit dem ganzen Oberkörper |
| Bluff-Angriff | [Silberrücken stürmt auf Kinder zu, Scheibe bricht (A-Z Animals)](https://a-z-animals.com/blog/watch-the-terrifying-moment-when-a-silverback-charges-children-at-the-zoo/) | kurzer vierbeiniger Sturm, Aufprall mit Schulter/Händen |
| Knöchelgang | Stock-Clip „Knuckle Walking Gorilla Slow Motion“ (Storyblocks, Suche `storyblocks.com/video/search/gorilla`) | Zeitlupe Knöchelgang (nur Titel bekannt) |

Suchbegriffe zum Selbst-Ansehen: „gorilla knuckle walking slow motion side view“, „silverback chest beat slow motion“,
„silverback charge display“, „gorilla ground slap“, „gorilla turning around knuckle walk“.

### Fachliteratur
- **Finestone et al. 2018**, *Great ape walking kinematics: implications for hominoid evolution*, Am. J. Phys. Anthropol. 166(1):43–55 (Bonobo, Schimpanse, **Flachlandgorilla**, Orang). Nur Zusammenfassung + Zitate gelesen: [Katalog-Eintrag](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_miscellaneous_1989563594). Menschenaffen **wechseln zwischen Diagonal- und Lateral-Sequenz**, statt wie andere Primaten fest diagonal zu gehen; das Tempo (größenbereinigt) bestimmt die Gangwerte am stärksten.
- **Sellers & Hirasaki 2018**, *Quadrupedal locomotor simulation…*, R. Soc. Open Sci. 5:171836 ([PMC5882714](https://pmc.ncbi.nlm.nih.gov/articles/PMC5882714)) – zitiert Messwerte: **Zykluszeit Gorilla 0,5–2,1 s**, Schimpanse 1,2–1,9 s; **Duty Factor Menschenaffen 0,62–0,74**; Phasenversatz des gleichseitigen Vorderfußes **40–75 %**; Schimpansen gehen vom Schritt direkt in den Galopp, **ohne Trab** (Simulationsstudie Schimpanse, [academia.edu](https://www.academia.edu/4992307/Exploring_Diagonal_Gait_Using_a_Forward_Dynamic_Three_Dimensional_Chimpanzee_Simulation)).
- **Kimura 1979 / Demes et al. 1994**, J. Hum. Evol. (doi 10.1006/jhev.1994.1023): Primaten tragen mehr Gewicht auf den **Hinterbeinen** („hindlimb driven“), die Vorderbeine haben niedrigere Spitzenkräfte. Nur Abstracts: [Duke Scholars](https://scholars.duke.edu/publication/1286804).
- **Thompson, Demes et al. (SICB-Abstract)**, *Biomechanics of Knuckle-Walking in African Apes*: Spitzenkraft beim Knöchelgang **spät im Stand (≈ 70–80 %)**, vorläufige Daten: [sicb.org](https://sicb.org/abstracts/biomechanics-of-knuckle-walking-in-african-apes).
- **Kent-Studie (KAR) zu wilden Berggorillas**: Knöchelgang bei **≈ 90 % der Bodenschritte**, Rest Faust-/Handrückengang: [kar.kent.ac.uk](https://kar.kent.ac.uk/67175).
- **Wright et al. 2021**, *Chest beats as an honest signal of body size in male mountain gorillas*, Sci. Rep. 11 ([DOAJ](https://doaj.org/article/21454aed48914413beb86dc54da4a2ca), [PDF](https://link.springer.com/content/pdf/10.1038/s41598-021-86261-8.pdf)): 503 Trommel-Folgen in 3.211 h (≈ 1,6 pro 10 h) → **seltenes, starkes Signal**; Dauer und Schlagzahl hängen nicht an der Körpergröße. Tabelle mit Schlagrate pro Sekunde nicht selbst gelesen (Volltext gesperrt).
- **Drohsequenz Silberrücken** (Schaller 1963, über National Zoo und Sekundärquellen, nicht selbst geprüft): schneller werdendes Hu-hu-Rufen → symbolisches Fressen → **Aufrichten** → Pflanzen werfen → **Brusttrommeln** (oft mit einem Bein kickend) → seitwärts rennen → Pflanzen schlagen/reißen → **mit der Hand auf den Boden schlagen**. Der Sturm ist meist ein **Bluff**, der am Gegner vorbeigeht: [National Zoo](https://www.nationalzoo.si.edu/node/6823), [Tanner & Perlman (MPG, Gesten-Sequenzen)](https://pure.mpg.de/pubman/item/item_2377799_4/component/file_2377798/gorillaSequences_Tanner%26PerlmanInPress.pdf).
- **Carrier & Cunningham 2017**, Biology Open 6:269–277: Sohlengänger-Füße erzeugen beim Kämpfen Drehmomente am Boden (Video oben).

---

## 4. Bewegungsregeln (Vorschlag für die `style.toml`)

Alle Zeitwerte bei 30 fps; Längen relativ (Körperlänge L bzw. Rumpfhöhe H) wie beim Bären, damit Statur-Varianten mitskalieren.
**Fake it:** Rhythmus und Koordination nach Natur, Tempo und Ausschlag nach Spielgefühl – ein Eis-Koloss darf schwerer wirken
als ein echter Gorilla.

### a) Knöchelgang – Beinfolge
- **Diagonal-Sequenz** als Grundform (primatentypisch): Aufsetzen **HL 0 · VR 0,1 · HR 0,5 · VL 0,6**, d. h. das gleichseitige
  Vorderbein setzt **0,6 Zyklus** nach dem Hinterbein auf (Messbereich 0,40–0,75). → `order = { BL = 0.0, FR = 0.1, BR = 0.5, FL = 0.6 }`.
  Unterschied zum Bären (Lateral, VL 0,14 nach HL): Beim Gorilla folgt auf den linken Fuß die **rechte** Faust.
- **Duty 0,70** (Menschenaffen 0,62–0,74; schwer → oben im Bereich), immer 3 Gliedmaßen am Boden.
- Optional Slider `ds_ls_mix` nicht nötig (Menschenaffen wechseln, aus der Kamera unsichtbar) – Fake it.

### b) Frequenz, Schritt, Körper
| Clip | Zyklus | Duty | Schritt (Fußweg) | Natur |
|---|---|---|---|---|
| Walk | **42 F (1,4 s)** | 0,70 | 0,22 L vorn, 0,18 L hinten | Gorilla 0,5–2,1 s; Bär 40 F zum Vergleich |
| Run (Sturm) | **20–22 F** | 0,40 vorn / 0,35 hinten | 0,30 L | Schritt → Galopp ohne Trab |

- **Arm als Stelze („vaulting“):** Der Arm bleibt im Stand fast gestreckt; der Körper schwingt **über** die Faust wie über einen
  Stab. Die Schulter steigt zur Standmitte leicht und sinkt danach – Vertikal-Wippen der **Brust** 1,5–2 % H, Becken nur 1 %.
- **Schultern rollen** sichtbar: `shoulder_roll_deg` 8–10, `shoulder_yaw_deg` 7–8 (Bär 7/6). Die riesigen Schulterplatten + Eiszacken
  pendeln dadurch von oben deutlich – das **Haupt-Lesemerkmal aus der ARPG-Kamera**.
- **Gewicht hinten:** Primaten tragen mehr auf den Hinterbeinen; Rücken fällt von der Schulter zur Hüfte (steht schon so im Modell,
  Ruhepose übernehmen). Becken kaum Rollen (3°), Hüfte tief, Hinterbeine gebeugt.
- **Seitliches Schwanken** 1,5 % L zur Standfaust hin (breite Armstellung = viel Seitenkraft, wie Bär).
- **Spitzenkraft spät im Stand (70–80 %)**: Abdruck aus der Faust am Ende → Faust rollt über die Knöchel nach vorn ab,
  Unterarm kippt vor, **erst dann** hebt die Faust (kurzes Nachziehen, kein hohes Anheben: `lift_front` ≈ 0,08 H).
- **Hinterfüße:** Sohlengänger, **Fersenaufsatz** (Carrier 2017), flach abrollen, `lift_back` ≈ 0,07 H, `toe_curl` klein (≈ 10°).
- **Kopf:** tief, stabilisiert (`head_gain` ≈ 0,4), kleines Seitpendeln 4–5° gegen die Schultern; kaum Nicken.
- **Schwanz** (falls behalten, Frage 1): schwer, waagerecht, schwingt verzögert gegen das Becken 4–6°, Spitze 2–3 F später.

### c) Run = Sturmangriff
- Schwerer **Galopp** (Menschenaffen: Schritt → Galopp, kein Trab): Fäuste setzen kurz nacheinander auf (VL 0,5 · VR 0,6),
  dann die Füße (HL 0 · HR 0,1), die Hinterbeine schwingen **außen an den Armen vorbei** nach vorn. Eine kurze, gesammelte Schwebe.
- Rücken rund beim Aufsetzen der Füße, gestreckt beim Abdruck (±10°), Brust schaukelt 7–8° (aus der Kamera: Buckel pumpt).
- Kopf tief und nach vorn gestreckt, Schultern hochgezogen. Fersenaufsatz hinten.

### d) Drehen auf der Stelle
- Gorilla dreht meist, indem er **die Fäuste um die Füße herum versetzt** (Vorderhand wandert außen herum, Hinterbeine treten auf
  der Stelle). Brust + Schultern drehen voraus, **Kopf führt** (dreht zuerst und am weitesten), Becken folgt, Schwanz schleppt nach.
- ≈ **30–35° pro Zyklus**, Zyklus 36 F (≈ 30 °/s; schwer). Drehrichtung **messen** wie beim Bären (`turn_check()`), nicht annehmen.

### e) Drohen (Ready)
- Aus der Natur-Sequenz nur die gut lesbaren Teile: **Kopf hoch-runter schütteln**, Maul auf (Brüllen/Hu-Rufe), **Brust heben**
  (20–30° Pitch um die Hüfte, Fäuste bleiben am Boden oder eine hebt ab) und **mit einer Faust auf den Boden schlagen**
  (Event `slam`, 1× pro Loop). Gewicht pendelt schwer links/rechts.
- **Brusttrommeln** ist das Signature-Motiv, aber in der Natur **selten** (≈ 1,6 pro 10 h): eher als einmaliger Clip
  (Taunt/Aggro-Start) als im Ready-Loop → Frage 2.
- Brusttrommeln selbst: **ganz aufgerichtet** (Brust 70–80°), Hüfte setzt sich nach hinten-unten, Hände **abwechselnd** vor die
  Brust (Ellbogen **nach außen**), schnelle Folge ≈ 6–8 Schläge in ~1 s (Spielwert; echtes Tempo laut Wright 2021 noch prüfen),
  Kopf leicht zurück, Maul offen; optional ein Bein kickt.

### f) Angriffsmechanik
- **Attack1 = Doppelfaust-Hammer (Ground Pound):** Ducken (Telegraph, 6–8 F) → Aufrichten um die Hüfte auf 60–70°, **beide
  Fäuste über den Kopf**, Brust bläht sich, Brüllen (Halten 6–8 F = deutlich lesbar) → Körper fällt nach vorn, **beide Fäuste
  schlagen 0,15–0,2 L vor der Ruheposition auf** (Event `hit`, 4–5 F Fall, beschleunigt) → Aufprall federt durch Schultern, Hals,
  Kopf, Schwanz peitscht nach → schweres Zurückstemmen. ≈ 1,8–2,0 s. Wie Bär-Attack2, aber **höher** aufgerichtet, Fäuste **über**
  dem Kopf (nicht nur vor der Brust), Aufprall härter (Eis-Koloss).
- **Attack2 = Sturm-Hieb (Root Motion, Vorschlag):** 2–3 Galoppsprünge über ≈ 1 Körperlänge auf das Ziel, im Vorbeistürmen ein
  **seitlicher Schwinger** mit einem Arm (Rumpf verdreht sich zurück, Schulter führt, Faust fegt in flachem Bogen von außen nach
  innen-vorn, Event `hit`), Abbremsen auf drei Gliedmaßen. Passt zum Bluff-Sturm der Natur und ist aus der Draufsicht als Bogen
  lesbar. Alternative ohne Root Motion: Rückhand-Schwinger auf der Stelle → Frage 3.
- **Ganzkörper (Lehre C3/C4):** In beiden Angriffen arbeiten Hüfte, Rücken, Schultern, Kopf und Schwanz; nie nur ein Arm.

### g) Was die schräge Top-down-Kamera sieht
- **Sehr gut:** Breite der Arme/Fäuste (Silhouette eines „A“), **rollende Schultern mit Eisplatten**, Rückenkamm aus Zacken,
  Schwanz, Root-Motion-Wege, der Bogen des Schwingers, Staub/Schockwelle beim Hammer.
- **Gut, wenn übertrieben:** Aufrichten (verkürzt sich von oben → **Arme weit seitlich** spreizen, Schultern nach hinten,
  Kopf hoch), Fäuste über dem Kopf, Gewichtsverlagerung.
- **Kaum:** Gesicht/Maul (Kopf tief unter dem Kamm), Fersenaufsatz, Knöchel-Abrollen, Fingerdetails.
- Prüf-GIFs/Kontaktbögen **zuerst aus der Spielkamera**; Dehnung an Rücken, Schulterplatten, Nacken prüfen, nicht an Fußgelenken (C15).

---

## 5. Clip-Liste `Quadruped_Gorilla_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Quadruped_Gorilla_Walk` | ✓ | ≈ 1,4 s | Schwerer Knöchelgang in Diagonal-Sequenz, Körper stelzt über die gestreckten Arme, Schultern + Eisplatten rollen, Kopf tief und ruhig, Schwanz pendelt verzögert. |
| `Quadruped_Gorilla_Run` | ✓ | ≈ 0,7 s | Sturm-Galopp: Fäuste kurz nacheinander, Hinterbeine schwingen außen vorbei, Buckel pumpt, Kopf vorgestreckt, Fersenaufsatz. |
| `Quadruped_Gorilla_Idle` | ✓ | 3–4 s | Schwer atmen, Gewicht verlagern, eine Faust hebt sich kurz und setzt schwer wieder auf, Kopf schaut links/rechts (Kopf führt, Hals folgt). |
| `Quadruped_Gorilla_Ready` | ✓ | ≈ 2 s | Drohen: Brust halb hoch, Kopf schüttelt, Maul auf, eine Faust schlägt auf den Boden (Event `slam`), Gewicht pendelt. |
| `Quadruped_Gorilla_TurnLeft` / `TurnRight` | ✓ | ≈ 1,2 s | Fäuste wandern außen um die Füße herum, Brust dreht voraus, Kopf führt, Becken und Schwanz schleppen nach (≈ 30–35°/Zyklus, Richtung gemessen). |
| `Quadruped_Gorilla_Attack1` | – | ≈ 1,9 s | Doppelfaust-Hammer: ducken, hoch aufrichten mit Fäusten über dem Kopf, nach vorn fallen, beide Fäuste schlagen auf (Event `hit`), Aufprall federt durch. |
| `Quadruped_Gorilla_Attack2` | – | ≈ 1,3 s | Sturm-Hieb mit Root Motion: Galopp auf das Ziel, seitlicher Schwinger im Vorbeistürmen (Event `hit`), Abbremsen (Variante nach Frage 3). |
| `Quadruped_Gorilla_Hit` | – | ≈ 0,5 s | Ruck zurück, Schultern ziehen sich zusammen, Kopf duckt verzögert, Schwanz zuckt nach, Ende exakt in der Standhaltung. |
| `Quadruped_Gorilla_Death` | – | – | **Platzhalter** (Nutzerregel „Death nicht anfassen“), z. B. Kopie des Bär-Platzhalters; nicht bearbeiten. |
| *(optional)* `Quadruped_Gorilla_Taunt` | – | ≈ 1,5 s | Brusttrommeln ganz aufgerichtet, Ellbogen außen, Hände abwechselnd, Brüllen – nur nach Frage 2. |

Events: `footstep` (Fäuste + Füße), `slam`, `hit`; Root Motion nur in Attack2.

---

## 6. Erwartete Rig-Hürden (`rigging/quadruped_rig.py`, `motions/quadruped/quadruped_kit.py` gelesen, nichts getestet)

1. **Rückenzacken verfälschen Wirbelsäule und Schultergelenk.** `center_at()` nimmt die Mitte zwischen 8. und 92. Perzentil
   (`spine_top_pct`), `midline_profile()` das 97. Perzentil als Rückenhöhe → die hohen Eiszacken auf dem Mittelstreifen heben
   Wirbelsäule und Schultergelenk (`joint_depth`) an. Ansatz: `[quadruped.detect] spine_slice` (wie Bär) und
   `[quadruped.rig] spine_top_pct` ≈ 75–80 in der creature.toml; `rig/rig_debug.png` prüfen.
2. **Ellbogen nicht gefunden.** Vorderbein ist fast gerade, `bend(tr, 0.5, 0.95, -1)` sucht die stärkste X-Abweichung und könnte die
   Kante der Eis-Armschiene erwischen; sonst Rückfall `front_elbow = 0.85`. Ellbogenhöhe im Debug-Bild gegen die Seitenansicht
   prüfen, ggf. `front_elbow`/`front_wrist` setzen (Handgelenk: Oberkante des Faust-Klotzes, ≈ 0,15–0,2 der Beinhöhe).
3. **Breite Schultern.** Hände stehen ±0,28 neben der Mitte; `joint_inset = 0.6` setzt das Schultergelenk ±0,17 ins Schulterpaket.
   Bei der riesigen Schulterplatte evtl. weiter außen (0,7–0,75), damit der Arm unter der Platte dreht und nicht der Rumpf.
4. **Kurzer, tiefer Hals.** Schulter x ≈ 0,33, Nase ≈ 0,5 → `head_length 0.42` lässt nur ≈ 0,1 L Hals; Hals-Gewichte greifen leicht
   in Schulterplatten/Brustzacken. Prüfen: `chest_extend` (Bär-Option), `neck_center_width`, `zone_lock = true`.
5. **Eisplatten und Zacken sollen starr bleiben** (CLAUDE.md: Kämme/Hörner starr). Das Mesh ist **ein** Teil → `rigid_parts` greift
   nicht (wirkt nur auf lose Teile). Kopfkrone: `rigid_head_above` + `rigid_head_connected` (C14-Optionen). Für Schulterplatten und
   Armschienen gibt es **keine** Option → mit `zone_lock` testen; reicht das nicht, eine neue **optionale** Regel (z. B. „Armschiene
   starr an Leg_F*_2“) abwärtskompatibel ergänzen, Regression `--deep` (Wolf, Hirsch, Bär, Reef Snapper identisch).
6. **Arm in Ruhe gestreckt → `reach_fix` senkt den Rumpf.** `REST_RATIO` der Vorderbeine wird nahe 0,98 liegen; jeder Schritt nach vorn
   überstreckt → Rumpf sackt (Wolf-Erfahrung „läuft geduckt“). Gegenmittel im Clip: Schritt vorn vor allem über **Schulterschwung**
   (`scapula_stiffness` niedrig, ≈ 0,4) und Stelzen-Bewegung des Körpers statt Armstreckung; **nicht** die Bewegung verkleinern.
7. **Keine Pol-Ziele im IK.** `init()` setzt IK ohne Pole (`chain_count` 4 mit Schulter). Beim Brusttrommeln und Doppelfaust über dem
   Kopf können Ellbogen umklappen. Lösung im eigenen Clip-Code: `ik_off(leg, k)` und Arm per `rot()` direkt drehen (FK), danach
   zurückblenden – ohne Änderung am Baukasten.
8. **Schwanz rammt beim Aufrichten in den Boden.** `rear_body()` kippt den ganzen Körper um die Hüfte; ein langer, waagerechter
   Schwanz an `Hips` dreht dabei nach unten. `ground_above()` würde dann den **ganzen Rumpf anheben** → Hinterbeine überstreckt.
   Schwanz im Aufrichten aktiv gegenheben (`tail(..., lift_deg)` bzw. `bend(TAIL, …)` ≈ −Pitch × 0,8) und `mesh_min_z()` pro Frame messen.
9. **Faust ohne Finger.** `Leg_F*_4` (Zehen) ist nur die Spitze des Klotzes; `toe_curl` vorn ≈ 0 lassen, das Abrollen über die Knöchel
   über `Leg_F*_3` (Handgelenk) und den Unterarm machen, sonst knickt die Eis-Krallenreihe.
10. **Fußbreite vorn/hinten 0,56×** liegt knapp über der Prüfgrenze 0,5; bei `narrow_hind_legs` **nichts** ändern (gewollt).
11. **Dehnung zuerst an sichtbaren Flächen messen** (Rücken, Schulterplatten, Nacken, Schwanzansatz), Roh-GIFs + Kontaktbögen der
    Angriffe abspeichern (Treffpunkt sichtbar).

Gekapselt: eigener `gorilla_clips.py`, `style.toml`, README im Ordner; `quadruped_kit.py` nur lesend. Hilfsfunktionen aus
`bear_clips.py` (`rear_body`, `chest_xform`, `foot`, `turn_check`, `pose_stats`) **kopieren**, nicht importieren.
Sparsam bauen: `--stage check` zuerst, nur `13_frost_colossus`.

---

## 7. Offene Fragen an den Nutzer (max. 3, je mit Empfehlung)

1. **Schwanz:** Bilder und Modell haben einen langen Eis-Stachelschwanz, die Beschreibung sagt „wie ein Gorilla ohne Schwanz“.
   **Empfehlung: behalten** und schwer mitschwingen lassen (er ist im Modell, ein neues Modell kostet 110 Credits, Guthaben 45; er
   macht die Silhouette von oben länger und lesbarer). Alternative: Schwanz-Gewichte steif an die Hüfte (wirkt wie ein starrer Eiszapfen).
2. **Brusttrommeln:** im **Ready-Loop** (würde alle 2 s wiederkehren) oder als **eigener Clip `Taunt`** (einmal beim Kampfbeginn)?
   **Empfehlung: eigener Clip `Taunt`** – in der Natur ist das ein seltenes, starkes Signal; Ready bleibt Drohen mit Boden-Schlag.
3. **Attack2:** **Sturm-Hieb mit Root Motion** (Galopp aufs Ziel + seitlicher Schwinger) oder **Rückhand-Schwinger auf der Stelle**?
   **Empfehlung: Sturm-Hieb** – passt zum Bluff-Sturm des Silberrückens, unterscheidet sich klar vom Hammer (Attack1) und ist aus der
   Draufsicht als Weg + Bogen lesbar.
