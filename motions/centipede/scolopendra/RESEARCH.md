# Recherche Bewegungsmuster centipede/scolopendra (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten des Tausendfüßers (erste Kreatur: `creatures/19_gloomfang_centipede/`). Noch kein Code, keine `style.toml`.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Die Aussagen stützen sich auf Abstracts, Suchzusammenfassungen und
Beschreibungen. Zwei Volltexte (Diaz 2023, arXiv 2207.10604) ließen sich nicht als Text lesen. Bau-Agent bzw. Nutzer sollten die
Videos unten **selbst ansehen** und die Werte dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“).

**Ablage-Ort = Vorschlag, noch nicht entschieden (Frage 1):** Die Datei liegt unter `motions/centipede/scolopendra/`, weil die Regeln das so verlangen
(siehe 1a). Entscheidet der Nutzer für `legless/centipede`, die Datei einfach nach `motions/legless/centipede/` verschieben.

---

## 1. Stand der Kreatur

### a) Skelett: Was ist eingetragen, was gilt?
| Quelle | Aussage |
|---|---|
| `creatures/19_gloomfang_centipede/creature.toml` `[motion]`, `creatures/roster.toml` Z. 826 | `style = "legless/centipede"`, `bodyplan = "serpentine"`. Beides wurde automatisch aus dem Roster erzeugt („bitte prüfen/korrigieren“). |
| `HANDOVER.md` Z. 30, Z. 89 | legless: „cobra (+ sandworm, centipede, viper geplant)“ |
| `motions/README.md` Z. 37 | `legless/centipede`: „viele Beine in Wellen (metachronal), **eigentlich eher ein Krabbler-Grenzfall**“ |
| `CLAUDE.md` „Lehren aus Testlauf 1“, `BACKLOG.md` A2 | **„Sonderfälle (beinlos, Tentakel, Flieger, Humanoid, Tausendfüßer) je eigene Instanz. Kein Skelett hängt am Baukasten eines anderen.“** A2 steht auf ✅, aber eine Tausendfüßer-Instanz gibt es noch nicht. |
| `BACKLOG.md` G3 / Bau-Warteschlange Z. 104 | Tausendfüßer (Gloomfang) ist das **letzte** Glied der Warteschlange (nach Shellback, Sand Leviathan, Frost Colossus, Ruin Howler, Oasis Gulper, Reality Ripper). |

**Ergebnis:** Laut Nutzerregel (A2) braucht der Tausendfüßer ein **eigenes Skelett** mit eigenem Rig und Baukasten. Der Eintrag `legless/centipede`
widerspricht dem. `legless` hat keine Beinknochen, und eine Erweiterung von `legless_kit.py` würde das freigabenahe `legless/cobra` (Eel Stalker) gefährden.
Vorschlag: **Skelett `centipede`, Muster `scolopendra`** (Riesenläufer; benannt nach dem Tier wie ant, crab und spider). Clips heißen dann `Centipede_Scolopendra_*`.
Später als Variante denkbar: `millipede` (Doppelfüßer, langsam, ohne Giftklauen); **nicht vorziehen**.

Für ein eigenes Skelett braucht es diese Dateien (die Pipeline leitet sie aus `<skelett>/<muster>` ab, `scripts/creature_pipeline.py` Z. 101–102):
`rigging/centipede_rig.py` + `centipede_defaults.toml` · `motions/centipede/centipede_kit.py` + `README.md` ·
`motions/centipede/scolopendra/{scolopendra_clips.py, style.toml, README.md}` · `[skelett.centipede]` in `scripts/model_check.toml` (z. B. 28 Füße erwartet) ·
`motion.style` in `creature.toml` und `roster.toml` umstellen · `motions/README.md`, `rigging/README.md` und HANDOVER nachziehen (macht der Doku-Agent).

### b) Vorhandenes Rig und Clips
- **Kein Rig, keine Clips, keine GIFs.** `creatures/19_gloomfang_centipede/` enthält nur `input/`, `raw/` (Tripo-Modell, 110 Credits) und `review/model_check.*`.
- **Direkte Nutzerkritik an einer Tausendfüßer-Animation gibt es nicht**, weil nie eine gebaut wurde.

### c) Bekannte Mängel und Befunde (mit Fundstelle)
| Befund | Fundstelle |
|---|---|
| Prüfung A ❌: front/back sind Draufsichten, Augenhöhe war mit ChatGPT nicht zu bekommen. Nutzer: **nur aus `design.png` generieren** (`tripo_run.py --single design.png`). | BACKLOG G4 |
| Prüfung B ✅ mit Rig-Auflage: **„Beine stehen waagerecht ab → Rig setzt sie nach unten“**. Gleiches Vorgehen wird beim Frosch zitiert („wie beim Tausendfüßer“). | BACKLOG G5, HANDOVER Z. 30 |
| `model_check`: WARNUNG Mittellinie (seitlich bis 0,028 × Länge versetzt; Querschnitt bis 90° gedreht, Spanne 179°). Nur 1 Bodenkontakt-Gruppe, und das ist die **Fühlerspitze** (siehe 2b). | `review/model_check.json`, `.png` |

### d) Allgemeine Lehren, die hier besonders gelten
- **Ganzkörper statt Einzelteil** (Eel Stalker: nur Kopf/Hals bewegt; Kobra: Rest starr). Der Körper muss in jedem Clip mitarbeiten, Drehen = in die Kurve biegen, Kopf führt.
- **Absolute Form statt verbogener Ruhepose** (Eel Stalker): Das Modell hat eine leichte seitliche Verschiebung im hinteren Drittel (2b). Clips geben Wirbel- **und Bein-Richtungen absolut** vor. Vorbild ist `shape()` in `legless_kit.py`, aber **kopiert**.
- **Chitin = starre Segmente:** Dehnung am Mesh/Rig lösen (Platten starr, Biegung nur in der Gelenkfuge), nie durch kleinere Wellen.
- **Kein Roboter-Gleichtakt** (Wolf, C1/B3). Maßstab ist die Needle Wasp. **Roh-Animation mitspeichern.** **Death nicht anfassen.**
- **Prüfen aus der Spielkamera:** am Rücken, an der Silhouette und am Beinkranz, nicht an Fußgelenken. Angriffe per **Kontaktbogen** prüfen (GIF zeigt nur Bild 1).

---

## 2. Prüfung der Bilder

### a) Referenzbilder `input/*.png`, Checkliste A
(`Facettierter…`, `Frontale…`, `Niedrigpolymer…`, `Gloomfang-Tausendfüßer…` und `Symmetrischer…` sind byte-gleiche Kopien von design/front/left/right/back.)

| Bild | Befund |
|---|---|
| `design.png` | 3/4-Ansicht schräg von oben. Langer, flacher Körper aus ≈ 14 Rückenplatten, ≈ 14–15 Laufbeinpaare, waagerecht abgespreizt und leicht nach unten gebogen, keine Überkreuzungen. Lange Fühler nach vorn, große sichelförmige Giftklauen (leicht offen statt „closed“ laut Pose). Endbeine nach hinten wie zweite Fühler. Körper gerade. **Brauchbar, Stil passt.** |
| `front.png`, `back.png` | ❌ **Draufsichten** statt Augenhöhe (A1). Front: Kopf unten im Bild. Back: Kopf oben. Beide zeigen ≈ 14 Beinpaare. (Bekannt, G4; nicht für Tripo genutzt.) |
| `left.png`, `right.png` | Echte Profile auf Augenhöhe ✅, Körper gerade und waagerecht ✅. Beine hängen hier **nach unten** (anders als im Design). Beinzahl im Profil ≈ 13–15, nicht exakt gleich zwischen den Bildern (A7, leichte Abweichung). Giftklauen im Profil offen. |
| Gesamt | Gliedmaßen berühren sich nicht ✅, nichts hängt unter dem Körper ✅, kein Glühen außer roten Augen (unkritisch). Hauptmangel A1 (Draufsichten), deshalb Einzelbild-Lauf. |

### b) Tripo-Ergebnis `raw/generate_rendered_image.webp` + `review/model_check.png`, eigene Messung am GLB
Ich habe das GLB ohne Blender eingelesen (Python, nur lesen), um die Teile zu zählen. Achsen in Blender: +X = Kopf, +Z = oben, Länge = 1,0.

| Teil | Inseln | Lage (x, y, z) | Bemerkung |
|---|---|---|---|
| Rumpf + Kopf + **Endbeine** | 1 (903 Vertices) | x −0,50 … +0,386, z −0,021 … +0,069 | Endbeine hängen **am Rumpf** (x −0,5 = Endbeinspitzen), müssen per Maske eigene Knochen bekommen |
| **Laufbeine** | **28 Einzel-Inseln** (56–79 Vertices) | 14 Paare bei x ≈ +0,33, +0,29, +0,24, +0,18, +0,12, +0,06, 0,00, −0,05, −0,11, −0,16, −0,21, −0,26, −0,31, −0,35 (Abstand ≈ 0,055) | **waagerecht** (z −0,015 … +0,03), reichen bis \|y\| ≈ 0,10–0,16. Kein Bein berührt den Boden. |
| Fühler | 2 (137 + 131) | x +0,34 … +0,50 | **asymmetrisch:** rechter Fühler (−y) hängt bis z −0,070 herab = **tiefster Punkt des Modells** |
| Giftklauen | 2 (62 + 56) | x +0,35 … +0,45, y ±0,03 | eigene Inseln, gut für eigene Knochen |

Weitere Befunde:
- **Teilezahl stimmt mit Design:** 14 Laufbeinpaare + Endbeinpaar + Fühler + Giftklauen. Nichts erfunden, nichts verschmolzen (die Beine sind getrennte Inseln).
- **Ansicht vorn (webp):** Die Beine stehen als waagerechte „Büschel“ seitlich ab. Der Körper liegt flach, der Kopf ist breit und flach, die Klauen sind groß. Das passt zum Design.
- **Mittellinien-Warnung:** In der Draufsicht wirkt der Körper gerade. Der gelbe Zickzack liegt im hinteren Drittel (≈ Platte 5–7 vom Schwanz), und die hinteren Beinpaare sitzen ≈ 0,01–0,015 nach +y versetzt. Die 90°-Drehung kommt vermutlich von den Beinen im Querschnitt (Messartefakt). Kein Grund für einen neuen Lauf, weil die absolute Körperform es ausgleicht.
- **Prüfen beim Rig:** Gibt es eine sichtbare Lücke zwischen Bein-Insel und Rumpf, wenn der Körper sich biegt? Dazu Draufsicht im Kontaktbogen ansehen.
- Kennzahlen: **4.097 Tris**, 3.117 Vertices, **1 Material**, 33 Mesh-Teile, Maße 1,0 × 0,33 × 0,14 (normiert).

---

## 3. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen)
| Thema | Link | Was man laut Titel/Beschreibung sieht |
|---|---|---|
| Laufen, Beinwelle in Zeitlupe | [Slow motion centipede in nature](https://www.youtube.com/watch?v=Eh48h_vsEqw) | Nahaufnahme, Beine in Zeitlupe |
| Beinwelle (Animation) | [Wikipedia: Centipede backward propagation (GIF)](https://en.wikipedia.org/wiki/File:Centipede_backward_propagation.gif) | Modell der rückläufigen Welle, Phasenversatz 45° je Segment, Duty 0,5 |
| Beutefang Riesenläufer | [Asian Giant Centipede Attack](https://www.youtube.com/watch?v=hqmH3kPdwnk) · [Giant Centipede Eats a Gecko](https://www.youtube.com/watch?v=QY9bxhfn-hc) | Zugriff, Festhalten mit den Vorderbeinen, Fressen |
| Kampf gegen Schlange | [Giant centipede attack on venomous snake](https://www.youtube.com/shorts/1ylraCK2se8) | Tausendfüßer verbeißt sich im Kopf der Schlange, Körper windet sich |
| Schnelles Rennen (andere Familie) | [House Centipede in Slo Mo](https://www.youtube.com/watch?v=UUflYKEWmu4) | Spinnenläufer *Scutigera*: sehr lange Beine, kein Vorbild für die Form, aber die Welle ist gut sichtbar |

Einen echten Zeitlupen-Biss eines *Scolopendra* habe ich nicht gefunden. Suchbegriff für den Nutzer: „Scolopendra strike high speed camera“.

### Fachliteratur
- **Zhong et al., SICB-Abstract** „Coordination of body undulation and leg wave during centipede locomotion“, [sicb.org/?p=39562](https://sicb.org/?p=39562): *Scolopendra polymorpha*, 19 Beinpaare. **Körperwelle 1,6 Wellen auf der Körperlänge, Beinwelle 2 Wellen**, Beinwinkel max. 0,65 rad (≈ 37°). Am schnellsten, wenn die **Körperwelle der Beinwelle um 2,51 rad (≈ 0,4 Zyklus) vorausläuft**. Gemessen auf dem Laufband: **0,41 ± 0,05 Körperlängen pro Zyklus**, Versatz 2,51 ± 0,71 rad. Ohne Körperwelle nur 0,25 Körperlängen pro Zyklus.
- **Diaz et al. 2023, J. Exp. Biol.** ([PDF, CRAB Lab](https://crablab.gatech.edu/pages/publications/pdf/Diaz_et_al_2023_JEB.pdf), [NSF](https://par.nsf.gov/servlets/purl/10459152)), nur Zusammenfassung gelesen: *Scolopendra* läuft mit **rückläufiger Welle (retrograd)**, und **die Körperwelle wächst mit dem Tempo**. Arten mit direkter Welle bleiben auch schnell gerade.
- **Anderson, Full & Garcia, SICB-Abstract** „A Spring-Mass Model of Centipede Locomotion“, [sicb.org/?p=37551](https://sicb.org/?p=37551): *S. heros*. **Die Beine an der Innenseite (konkav) der Körperkurve treffen am Boden fast auf einem Punkt zusammen.** Jede Beinwelle wirkt wie eine Feder.
- **Chong et al., arXiv 2207.10604** „Self-propulsion via slipping“, [Abstract](https://arxiv.org/abs/2207.10604): *S. polymorpha* ≈ 0,5 Körperlängen/s bei hohem Tempo. **Wenn die Körperwelle einsetzt, wird der Beinausschlag kleiner.**
- **Kronmüller & Lewis 2015, ZooKeys 510** „On the function of the ultimate legs of some Scolopendridae“, [PMC4523778](https://pmc.ncbi.nlm.nih.gov/articles/PMC4523778/), nur Suchzusammenfassung gelesen: Bei Berührung hinten nehmen die Tiere eine **Warnhaltung mit erhobenen Endbeinen** ein. Teils **schlagen sie mit den erhobenen Endbeinen nach unten**.
- **Beutefang an Fledermäusen** (Acta Amazonica 2015, *S. viridicornis*, nach Zusammenfassung von [a-z-animals](https://a-z-animals.com/articles/meet-the-foot-long-centipede-powerful-enough-to-hunt-bats/)): Zugriff **in einer schnellen Bewegung**, Giftklauen in den Nacken, Festhalten mit den vorderen Beinpaaren. *S. gigantea* bewegt beim Fressen den **Kopf seitlich hin und her**.

### Kernaussagen
1. **Beinwelle rückläufig (Kopf → Schwanz).** Ein Bein hebt kurz nach seinem vorderen Nachbarn ab. Linke und rechte Seite laufen **im Gegentakt (0,5 Zyklus)**.
2. **Auf der Körperlänge liegen ≈ 1,5–2 Beinwellen.** Pro Segment ergibt das ≈ 0,1–0,14 Zyklus Versatz. Bei unseren 14 Paaren ist **0,125 (45°)** ein guter Startwert: 1,75 Wellen.
3. **Körperwelle seitlich (Schlängeln)**, ≈ 1,5 Wellen auf der Länge. Sie läuft in die gleiche Richtung wie die Beinwelle, mit **gleicher Frequenz** und **≈ 0,4 Zyklus Vorsprung**. Sie ist **klein beim Gehen und groß beim Rennen**. Die Beine an der Innenseite der Kurve rücken zusammen, die an der Außenseite fächern auf.
4. Pro Zyklus kommt der Körper **≈ 0,4 Körperlängen** voran.
5. **Angriff:** schneller Zugriff in einem Zug, Biss in den Nacken, Festhalten mit den Vorderbeinen, Kopf ruckt seitlich.
6. **Verteidigung hinten:** Endbeine heben (Warnung) und nach unten schlagen.

---

## 4. Bewegungsregeln für das Muster (Vorschlag für die `style.toml`)

Alle Zeitwerte bei 30 fps. „Fake it“: Rhythmus und Koordination wie in der Natur, Tempo nach Spielgefühl. Laut Roster ist das Tier ein **schneller** Nahkämpfer.

### a) Beinwelle (metachron)
- **Richtung:** Kopf → Schwanz (retrograd). Paar *i* (1 = vorn) hat die Phase `phase_i = i × ripple`, mit **`ripple` = 0,125 Zyklus** (Slider 0,10–0,14). Rechte Seite = links + **0,5**.
- **Duty:** Walk **0,55**, Run **0,50**. Bei 14 Paaren steht immer ≈ die Hälfte der Beine. Keine Gruppen, keine Gleichtakt-Momente: Die Welle **muss sichtbar wandern**.
- **Ausschlag:** Bein schwingt um die Hüfte **±25–30°** vor und zurück (Natur bis ≈ 37°). Im Schwung hebt die Spitze ≈ 0,02–0,03 × Länge (bzw. 15–20° Hub). Ruhestellung: Spitze **nach unten auf den Boden** (siehe 6b).
- **Feste Füße:** In der Standphase fährt die Spitze mit Körpertempo nach hinten (in-place). Kleines Rutschen ist aus der Spielkamera unsichtbar, aber die Selbstprüfung soll es messen.
- **Vorderstes Paar:** läuft mit, darf etwas höher und tastender greifen. **Endbeine laufen nicht mit**, sie schleppen nach hinten, leicht angehoben, und schwingen mit der Körperwelle nach (Follow-Through).

### b) Körperwelle gegen Tempo
| Clip | Zyklus | Frequenz | Gieren pro Wirbel (max.) | Wellen auf dem Körper | Beinausschlag |
|---|---|---|---|---|---|
| Walk | **18–20 Frames** | 1,5–1,7 Hz | **±6–8°** | 1,5 | ±28° |
| Run | **10–12 Frames** | 2,5–3 Hz | **±15–20°** | 1,3–1,5 | ±24° (kleiner, Chong 2022) |

- Körperwelle läuft **Kopf → Schwanz**, gleiche Frequenz wie die Beine, **Vorsprung 0,4 Zyklus** (Slider `body_leg_offset`). Die Hüllkurve ist am Kopf gedämpft (Kopf hält Kurs), zum Schwanz hin voll.
- **Kein senkrechtes Wippen** (Körper getragen von vielen Beinen). Run **≈ 15 % tiefer** (Beine weiter gespreizt).
- Chitin: **Gieren nur in den Fugen**, Platten bleiben starr. Höchstens ±10° pro Fuge im Walk, ±20° im Run. Mehr verlangt Gelenk-Verdichtung (C9), **nicht kleinere Wellen**.

### c) Kopf, Fühler, Giftklauen
- **Kopf führt** und bleibt fast auf Kurs (gedämpft ≈ 30 % der Welle). Kleine Suchbewegung ±5°.
- **Fühler:** nach vorn, leicht angehoben (absolut vorgeben, Modellhaltung ignorieren; der rechte Fühler hängt im Modell). Im Gang wechselseitig ±10–15° schwingen, verzögert, mit weicher Welle bis an die Wurzel (Lehre Tentakel). Im Idle tasten sie langsam.
- **Giftklauen:** im Gang geschlossen, in Ready offen (seitlich auseinander, ≈ 30–40°), beim Biss **zangenartig zueinander**.

### d) Angriff (aufbäumen und zuschlagen)
- **Ready (Loop):** Die **vorderen 3–5 Segmente** (≈ 25–35 % der Länge) heben sich auf **20–30°**, der Kopf ist leicht nach unten aufs Ziel gerichtet. Klauen offen, Fühler vorgestreckt und gespreizt. Die vorderen 2–3 Beinpaare sind frei in der Luft, seitlich gespreizt. Der Rest liegt als **flaches S** unter Spannung. **Endbeine erhoben** (Warnhaltung). Langsames Pendeln ±8°, Beinwelle zittert leicht.
- **Attack1 = Aufbäumen und Biss (Root Motion):**
  1. Ausholen 8–10 Frames: Vorderkörper höher (35–45°) und zurück, S-Kurve spannt sich (Telegraph).
  2. **Zustoß 3–4 Frames:** Der Vorderkörper schlägt **nach vorn-unten**, der ganze Körper schiebt ≈ 0,15–0,25 × Länge nach. Die Vorderbeine umklammern das Ziel wie einen Käfig, die Klauen schließen sich. Event `hit` beim Schließen.
  3. Festhalten 5–6 Frames mit **seitlichem Kopfruck** (±15°), den der Körper als Welle weitergibt.
  4. Zurück in Ready, 8–10 Frames. Gesamt ≈ 0,9 s.
- **Attack2 (Vorschlag, Frage 3) = Endbein-Schlag:** Der Körper biegt sich in ein C, Kopf und Schwanz kommen zum Ziel. Die Endbeine heben sich und **schlagen nach unten**. Gut lesbar als Zweitangriff, weil er von hinten kommt (Kronmüller & Lewis 2015). Alternative: flacher, schneller Vorstoß mit Biss ohne Aufbäumen.
- **Der ganze Körper arbeitet** (Lehre C3): Kein Angriff, bei dem nur Kopf oder Klauen sich bewegen. Die S-Kurve entlädt sich in den Stoß.

### e) Drehen
- Wie eine Schlange auf Beinen: Der **Kopf führt in die Kurve**, der Körper legt sich in einen Bogen (C-Form, ≈ 60–90° Richtungsänderung Kopf ↔ Schwanz), und der Bogen wandert nach hinten. Die Beinwelle läuft weiter. Außenseite: lange Schritte. Innenseite: kurze, die Füße rücken zusammen.
- Tempo **≈ 120–180 °/s** (schneller Jäger, Spinne 90–120 °/s). Kein starr gedrehter Walk (Lehre C4).

### f) Was die schräge ARPG-Kamera sieht
- **Sehr gut sichtbar:** der **bernsteinfarbene Beinkranz** mit der **wandernden Welle** (das wichtigste Erkennungsmerkmal, muss flüssig laufen), die S-Kurve des Körpers, die **lange Silhouette** mit Fühlern vorn und Endbeinen hinten, das Aufbäumen des Vorderkörpers.
- **Gut sichtbar, wenn übertrieben:** Aufbäumen wird von oben verkürzt, deshalb **Vorderbeine, Fühler und Klauen weit seitlich spreizen**, damit die Silhouette breiter wird. Der Vorstoß wird per Root Motion lesbar.
- **Kaum sichtbar:** Details der Giftklauen und der Beingelenke, Bauchseite, senkrechtes Wippen.
- **Prüf-GIFs zuerst aus der Spielkamera.** Dazu eine Draufsicht für die Beinwelle.

### Tod (nur Info, Death bleibt gesperrt)
Sterbende Tausendfüßer **rollen sich seitlich zu einem C bzw. einer Spirale ein**, Beine zucken unkoordiniert, oft kippen sie auf den Rücken. Umsetzen erst nach Freigabe durch den Nutzer.

---

## 5. Vorschlag Clip-Liste `Centipede_Scolopendra_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Centipede_Scolopendra_Idle` | ✓ | 2–3 s | Liegt lauernd fast still, Fühler tasten langsam, alle paar Sekunden läuft eine kurze Beinwelle durch und der Körper verlagert sich minimal. |
| `Centipede_Scolopendra_Walk` | ✓ | ≈ 0,6 s | Rückläufige Beinwelle (0,125 Zyklus/Segment, links gegen rechts im Gegentakt) mit kleiner Körperwelle, die 0,4 Zyklus vorausläuft, Kopf führt ruhig. |
| `Centipede_Scolopendra_Run` | ✓ | ≈ 0,35 s | Gleiche Welle, schneller, Körper tiefer, deutlich stärkeres Schlängeln, Endbeine schwingen nach. |
| `Centipede_Scolopendra_TurnLeft` / `TurnRight` | ✓ | ≈ 0,6 s | Kopf führt in die Kurve, der Körper legt sich in einen wandernden Bogen, Außenbeine machen lange und Innenbeine kurze Schritte. |
| `Centipede_Scolopendra_Ready` | ✓ | 1–1,5 s | Vorderkörper 20–30° aufgerichtet, Klauen offen, Fühler und Vorderbeine gespreizt, Körper als gespanntes S, Endbeine erhoben, langsames Pendeln. |
| `Centipede_Scolopendra_Attack1` | – | ≈ 0,9 s | Aufbäumen und Ausholen, dann Biss nach vorn-unten mit Vorderbein-Käfig und Kopfruck (Event `hit`), zurück in Ready, Root Motion. |
| `Centipede_Scolopendra_Attack2` | – | ≈ 1,0 s | Vorschlag: Der Körper biegt sich in ein C und die Endbeine schlagen von oben auf das Ziel (Event `hit`); Alternative siehe Frage 3. |
| `Centipede_Scolopendra_Hit` | – | ≈ 0,3 s | Ein Knick läuft vom Treffpunkt durch den ganzen Körper, Beine zucken, Vorderkörper fährt kurz zurück, endet in Ready. |
| `Centipede_Scolopendra_Death` | – | – | **Gesperrt** (Nutzer 2026-11-17). Nur Platzhalter, nicht bearbeiten. |

Später möglich (Roster-Varianten, **nicht vorziehen**): Eingraben/Auftauchen (Dune Centipede, Gloomfang Matriarch) als Spawn-Clip.

---

## 6. Erwartete Rig-Hürden (Code gelesen: `rigging/legless_rig.py`, `rig_common.py`, `motions/legless/legless_kit.py`)

### a) Warum `legless` so nicht reicht
- **Keine Beinknochen.** `legless_rig.py` baut nur `Root → Spine_01…14 → Head → Jaw`. `rig_common.skin()` gewichtet **alle** Vertices mit 1/Abstand⁴ zu allen Knochen. Die 28 Bein-Inseln bekämen gemischte Gewichte von 2–3 Wirbeln, verbiegen sich mit dem Körper und können keine Welle laufen.
- **`Jaw`** gibt es beim Tausendfüßer nicht. Stattdessen braucht es **`Forcipule_L/R`** (eigene Inseln, x 0,35–0,45).
- **Boden:** `GROUND = V[:,2].min()` (Rig) und `mesh_min_z()` (Kit) nehmen den **herabhängenden rechten Fühler** (z −0,070). Der Rumpf liegt dann 5 cm „über dem Boden“, und `ground("contact")` drückt den Körper falsch. Boden muss über die **Beinspitzen** bestimmt werden, Fühler und Klauen ausgenommen.
- **Wirbel gleichmäßig verteilt** (`np.linspace`) statt an den Plattenfugen. Dadurch biegen sich die Chitinplatten in der Mitte. Für Chitin müssen die **Gelenke auf die Fugen** zwischen den Platten (≈ in der Mitte zwischen zwei Beinpaaren bei Abstand 0,055).
- `head_length = 0.08` bezieht sich auf die Länge **inklusive Endbeine** (x −0,5). Ansatz für den Kopf besser aus der Lage des vordersten Beinpaars (x ≈ 0,33) ableiten.
- `legless_kit.py` und `legless_rig.py` **nicht ändern** (Eel Stalker/Cobra muss unverändert bleiben, `scripts/regression.py`). Brauchbares (`shape()`, `abs_info()`, `seg_s()`, `interp()`, `bake()`, `max_stretch()`, Schwerpunkt-Mittellinie) in das neue Skelett **kopieren**.

### b) Vorschlag Skelett `centipede`
```
Root → Spine_01 (hinter den Endbeinen) … Spine_14 → Head → Forcipule_L/R, Antenna_L/R_1..3
Spine_i → Leg_L<i>_1 → Leg_L<i>_2   (und R)     i = 1 vorn … 14 hinten (Zählung im Muster festlegen)
Spine_01 → Ultimate_L_1..2, Ultimate_R_1..2
```
- **Ein Wirbel pro Beinpaar** (14, passt 1:1 zu den Platten). Bein *i* hängt am Wirbel seines Segments.
- **Bein-Inseln starr zuordnen:** Jede Insel gehört vollständig ihrem Bein. Den zweiten Knochen (Schiene) nur auf der äußeren Hälfte der Insel setzen, die Grenze per Abstand entlang der Beinachse. Erkennung: Inseln seitlich des Rumpfs (`|y| > Rumpfbreite`), sortiert nach x und Seite. Reines Insel-Zählen genügt, es braucht **kein Dijkstra** wie in multileg.
- **Endbeine** liegen in der Rumpf-Insel: über eine Maske (x < Schwanzende des Rumpfs und `|y|` > halbe Rumpfbreite) eigenen Knochen zuweisen.
- **Ruhepose absolut:** Die Beine stehen im Modell waagerecht. Das Kit gibt jede Beinrichtung absolut vor: Hüfte ≈ 25–35° nach unten, Schiene weiter nach unten, bis die Spitze den Boden berührt (BACKLOG G5). Der Rumpf hebt sich dadurch ≈ 0,02–0,03 × Länge.
- **Knochenzahl:** 1 + 14 + 1 + 2 + 6 + 56 + 4 ≈ **84 Knochen** (mit 1 Knochen pro Bein: ≈ 56). Das ist viel für Massengegner; siehe Frage 2.

### c) Weitere Stolpersteine
- **Lücke Bein ↔ Rumpf:** Die Beine sind lose Inseln. Wenn ihr Wirbel sich dreht, dreht die Hüfte mit, und es entsteht keine Dehnung. Aber zwischen gebogenem Rumpf und starrem Bein kann ein **Spalt** sichtbar werden (`check_gaps.py` nutzen; Draufsicht).
- **Dehnung nur am Rumpf:** 903 Vertices für 14 Platten ergeben wenige Kanten pro Fuge. Läuft die Welle im Run mit ±20°/Fuge, reißt es vermutlich. Dann Fugen verdichten (C9-Baustein `joint_densify.py`, als Kopie bzw. über seine vorhandene Schnittstelle) oder Platten starr mit schmaler Übergangszone gewichten.
- **Leichte Asymmetrie** (hintere Beinpaare +0,01–0,015 in y, rechter Fühler hängt): Die absolute Form gleicht das aus, Fühler absolut setzen.
- **Selbstprüfung:** Bodenkontakt nur über die Beinspitzen messen, Fühler und Klauen ausnehmen. `model_check.toml` bekommt `[skelett.centipede]` mit 28 erwarteten Füßen, sobald die Beine unten sind (Ruhepose vor dem Check: Hinweis, dass Tripo sie waagerecht liefert).
- **Sparsam bauen:** `--stage check` bzw. `motion`, nur diese Kreatur, `--no-preview`. Höchstens 1 Blender-Agent gleichzeitig.

---

## 7. Offene Fragen an den Nutzer
1. **Eigenes Skelett `centipede` (Muster `scolopendra`) statt `legless/centipede`?** Empfehlung: **ja**. Deine Regel „Tausendfüßer = eigene Instanz“ (BACKLOG A2) verlangt es, `legless` hat keine Beine, und so bleibt der Eel Stalker sicher unberührt. Clips hießen `Centipede_Scolopendra_Walk` usw.
2. **Knochen pro Bein: 2 (≈ 84 Knochen) oder 1 (≈ 56)?** Empfehlung: **2**. Das Knie macht den Schritt weich und hält die Spitze am Boden. Bei vielen gleichzeitigen Gegnern lässt sich später eine LOD-Fassung mit 1 Knochen ableiten.
3. **Zweiter Angriff:** Empfehlung **Endbein-Schlag** (Körper biegt sich zum C, die Endbeine hauen von oben), weil er echt belegt ist und sich aus der Spielkamera klar vom Biss unterscheidet. Alternative: schneller, flacher Vorstoß mit Biss ohne Aufbäumen.
