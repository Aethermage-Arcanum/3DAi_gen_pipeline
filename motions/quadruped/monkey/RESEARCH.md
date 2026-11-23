# Recherche Bewegungsmuster quadruped/monkey (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten des Affen. Erste Kreatur: `creatures/17_ruin_howler/`. Es gibt noch keinen Code und keine `style.toml`.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Die Aussagen stützen sich auf Abstracts, Suchergebnis-Zusammenfassungen,
einen Volltext (Kühl 2016) und Lehrbuchwissen. Werte ohne Quelle sind als **Annahme** markiert. Der Bau-Agent bzw. der Nutzer sollte die
Videos unten **selbst ansehen** und die Werte dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“).

---

## 0. Skelett-Entscheidung: `quadruped`, Muster `monkey`, kein neues Skelett nötig

| Fundstelle | Inhalt |
|---|---|
| `creatures/roster.toml` (id `ruin_howler`) | `motion = "quadruped/monkey"`, `bodyplan = "quadruped"`, Pose „standing on all fours, the long front arms resting on the knuckles … tail extended straight back“ |
| `creatures/17_ruin_howler/creature.toml` | `[motion] style = "quadruped/monkey"`, Vorbilder: Pavian-Trupp (Vierfüßergang, Drohen), Schimpanse wirft (Zeitlupe), Brüllaffe (Gebrüll) |
| `review/model_check.json` | Skelett quadruped/monkey, **4 Fuß-Gruppen, 2 Paare** = passt zu 4 Beinen |
| BACKLOG G3, Bau-Warteschlange | „monkey“ in der Muster-Warteschlange: … → Gorilla (Frost Colossus) → **Affe (Ruin Howler)** → Frosch … |
| `HANDOVER.md` Z. 27, 87 | `ruin_howler | quadruped/monkey`; quadruped: „+ tortoise, gorilla, monkey, frog … geplant“ |
| BACKLOG G1 | Reihenfolge der Recherche nennt `frog/badger/monkey` als quadruped-Muster |

**Begründung:** Der Ruin Howler läuft im Spiel (fast) immer auf vier Gliedmaßen. Das 30-Knochen-Vierbeiner-Skelett (mit Schwanz, Kiefer, Schulterblättern)
deckt ihn ab. Aufrichten für Wurf und Drohen geht im quadruped-Baukasten schon (Bär Attack2: Rumpf bis 66° um die Hüfte, Pranken 0,85 m hoch).
Ein eigenes „Primaten“-Skelett wäre nur nötig, wenn der Affe dauerhaft zweibeinig laufen oder klettern soll. Das verlangt das Roster nicht.
**Nicht entschieden, nur angemerkt:** Falls der Nutzer später echte Hände (Finger, Greifen) oder zweibeiniges Laufen will, bräuchte es eine Hand-Kette
bzw. ein Skelett wie `upright`. Für einen Schwarm-Gegner aus der Draufsicht empfehle ich das nicht (Fake it).

### Affe vs. Gorilla (Frost Colossus, anderer Prep-Agent)
| | Gorilla `quadruped/gorilla` (Frost Colossus) | Affe `quadruped/monkey` (Ruin Howler) |
|---|---|---|
| Körperbau | riesig, massig, kein Schwanz, Arme sehr dick | schlaksig, mager, Buckel + breite Brust, **langer dicker Schwanz** (~40 % der Modelllänge) |
| Rolle | schwerer Nahkämpfer/Tank | **Schwarm/Fernkampf**: Rudel, wirft Steine, laut |
| Tempo | langsam, schwer, viel Gewicht pro Schritt | flink, nervös, schnelle Kopfrucke, kurze Sprints |
| Gang | Knöchelgang, schwer, Rumpf schaukelt | Knöchelgang, aber leicht; Diagonal-Gang wie Pavian; Run = **Galopp mit Sprüngen**, Schwanz als Gegengewicht |
| Drohen | Aufrichten + Brusttrommeln | **Brüllen mit weit offenem Maul (Eckzähne zeigen)**, Boden schlagen, auf den Armen wippen, Mähne sträuben |
| Angriff | Fäuste/Slam aus der Aufrichtung (humanoid) | **Steinwurf** (Projektil) + **Ansprung-Biss** mit Root Motion |
| Silhouette von oben | breiter Block, Arme | stachelige Mähne über Kopf/Schultern, lange Arme, Schwanzbogen |

Kapselung: Beide Muster sind eigene Ordner mit eigenem Clip-Code. Gemeinsame Ideen (Knöchel-Hand, Aufrichten) werden **kopiert**, nicht importiert.

---

## 1. Stand der Kreatur

| Was | Stand | Fundstelle |
|---|---|---|
| Referenzbilder | 4 Ansichten + `design.png` vorhanden, Prüfung A bestanden nach neuem Frontbild („Rückansicht = Perspektive, Schwanz gestreckt“) | BACKLOG G4 |
| Tripo-Modell | `raw/generate_model.glb`, 110 Credits, Task `fbdaac23…` | `raw/tripo_state.json` |
| Prüfung B | ✅ freigegeben | BACKLOG G5 |
| model_check | 4.404 Tris (face_limit 4.000, 1,10×), 1 Material, 1 Mesh-Objekt, **10 Mesh-Teile**; Füße vorn 0,415 / hinten 0,328 breit (0,79×); **Symmetrie-WARNUNG 11,2 %** (erlaubt 10 %); 2 kleine einseitige Bereiche vorn/unten links+rechts (Info) | `review/model_check.json`, `review/model_check.png` |
| Rig, UV, Clips, Export | **nichts vorhanden** (kein `rig/`, `uv/`, `output/`, kein README der Kreatur) | Ordnerinhalt |
| Muster-Ordner | fehlte, mit dieser Datei angelegt | – |

**Direkte Nutzerkritik am Ruin Howler gibt es nicht** (nie animiert). Es gelten die allgemeinen Lehren (CLAUDE.md, BACKLOG):
- **Ganzkörper** (C4): Turn ist kein gedrehter Walk, Ready kein verschobenes Modell. Beim Brüllen arbeitet der ganze Oberkörper, nicht nur der Kiefer.
- **Nicht roboterhaft** (C1, B3): weiche Fußbahnen (`foot_profile = "smooth"`), Nachziehen von Hals/Kopf/Schwanz (`follow`). Maßstab Needle Wasp (B4).
- **Angriffe aus dem ganzen Körper** (C3): Wurf = Beine → Hüfte → Rumpf → Schulter → Arm, nicht nur der Arm.
- **Feste Krümmung im Modell nicht als Grundlage** (Eel Stalker): Die Schwanzspitze ist im Modell nach unten gehakt → Clips geben die Schwanzform absolut vor.
- **Prüfen aus der Spielkamera** (C15): Mähne/Nacken, Rücken, Schultersteine, Schwanzansatz, nicht Fußgelenke.
- **Dehnung nicht durch kleinere Bewegung lösen**, Roh-GIFs mitspeichern, **Death nicht anfassen** (nur Platzhalter).
- Angriffe per **Kontaktbogen** prüfen (Memory: GIF zeigt nur Bild 1).

---

## 2. Prüfung Teil A der Referenzbilder + Sichtung Tripo-Render

Angesehen: `input/design.png`, `front.png`, `left.png`, `right.png`, `back.png`, `raw/generate_rendered_image.webp`, `review/model_check.png`.
(Die Dateien mit langen deutschen Namen sind Byte-gleiche Kopien der vier Ansichten bzw. des Design-Bilds.)

| Punkt | Befund |
|---|---|
| 1 Reihenfolge/Blick | ✅ front, left = Kopf links, right = Kopf rechts, back. Kamera leicht von oben, noch ok. |
| 2 Gleiche Haltung | ⚠ leicht: In den Seitenansichten stehen die **Arme schräg nach vorn** (Fäuste unter dem Gesicht, ~15–20° vor der Senkrechten), in der Frontansicht senkrecht und nach außen gebogen. Das Modell übernimmt die Schräge (Fäuste bei x 0,41, Nase bei ~0,5). Kein Fehler, aber für das Rig wichtig (Abschnitt 6). |
| 3 Nichts zwischen den Beinen | ✅ Der Schwanz hängt in der Rückansicht scheinbar herab = Perspektive (gestreckt nach hinten, bekannt aus G4/HANDOVER Z. 70). Modell: „nichts hängt“. |
| 4 Beinbreite | ⚠ Fäuste vorn deutlich **breiter** als die Hinterfüße (Bild ~2×, Modell 0,79× hinten/vorn, innerhalb 0,5–1,4). Typisch für Knöchelgänger, gewollt. |
| 5 Gliedmaßen frei | ✅ Arme berühren Körper nicht, Hinterbeine frei, keine Hautbrücken. |
| 6 Neutrale Pose | ⚠ **Schwanzende gehakt** (Seitenansichten: letztes Viertel knickt nach unten). **Hinterbeine gebeugt** (laut look gewollt). **Fäuste eingerollt** mit Daumen. Maul leicht offen mit Fängen (ok). |
| 7 Teilezahl | ✅ 4 Gliedmaßen, 1 Schwanz. ⚠ Kleinkram uneinheitlich: Anzahl Goldringe/Steine je Schulter und Unterarm wechselt zwischen den Ansichten → Symmetrie-Warnung 11,2 % (natürliche Asymmetrie, mit Begründung freigeben). |
| 8 Dünne Teile | ✅ Mähnen-Stacheln sind Volumen-Facetten. model_check: keine großen einseitigen Flächen. |
| 9 Effekte | ✅ keine; rote Augen sind Farbe, kein Glühen. |
| Tripo-Render (`generate_rendered_image.webp`) | Passt zum Design: Mandrill-Gesicht, Stachelmähne, Steine + Ringe an Schultern und Unterarmen, Fäuste auf den Knöcheln, Arme O-förmig nach außen gebogen. Körper wirkt geduckt/kurz, Hinterbeine kaum zu sehen (Blick von vorn). |
| model_check.png | Mähnen-Spitzen und Steine rot (= Symmetrie), sonst unauffällig. Seitenansicht: Rücken fällt von Schulter (Mähnen-Buckel) zur Hüfte leicht ab, Schwanz waagerecht, Spitze hängt. |

**Fazit:** Keine Neu-Generierung nötig. Bekannte Rig-Korrekturen: Schwanzform absolut vorgeben, Armschräge beim Gewichten (Reichweite) beachten, Symmetrie-Warnung begründet freigeben.

---

## 3. Naturreferenzen

**Laut Roster ist der Ruin Howler ein Pavian-/Mandrill-artiger Bodenaffe mit Knöchelgang**, der Steine wirft und brüllt. Darum: Pavian (Gang, Drohen,
Kampf), Schimpanse (Knöchelgang, Imponierlauf, Steinwurf), Brüllaffe (nur Gebrüll).

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen; Inhalt nur laut Titel/Beschreibung)
| Thema | Link | laut Beschreibung |
|---|---|---|
| Pavian rennt (Flucht) | [Baboon Running (Etosha)](https://www.youtube.com/watch?v=ne3Yyyz6c28) · [Baboon Running at Samburu](https://www.youtube.com/watch?v=Yu8f11mCmD8) · [Baboons on the move](https://www.youtube.com/watch?v=aZMqrKY48aI) | Trupp flieht vor Löwen; Galopp, Gruppe |
| Pavian-Sprung, Zeitlupe | [Baboon jumps for Mulberry fruit](https://www.youtube.com/watch?v=FS0zgDj8DhM) | Absprung/Landung in Zeitlupe → Ansprung-Angriff |
| Pavian-Kampf | [Nasty Baboon Fight (Alpha greift an)](https://www.youtube.com/watch?v=UKL887JIZas) · [Baboons fight (Short)](https://www.youtube.com/shorts/WyGiRyLgTr4) | Ausfall, Biss, Nachsetzen, Rückzug |
| Schimpanse Imponieren | [chimp charge and display](https://www.youtube.com/watch?v=99txWeTKQyM) · [A display of strength](https://www.youtube.com/watch?v=JHthnPGYJSw) | Haare gesträubt, Anlauf, Boden schlagen, Äste schleifen |
| Schimpanse wirft | [Chimp Throws Rock at Cameraman (Ol Pejeta)](https://www.youtube.com/watch?v=2bywxLPrvaQ) · [Angry chimpanzee throws stones](https://www.youtube.com/watch?v=LbRFOPxrX8k) · [Chimp throwing rocks, Dallas Zoo](https://www.youtube.com/watch?v=D7lO1zK0zaI) · [Accumulative stone throwing](https://www.youtube.com/watch?v=eVv3IUGPDK8) | Stein aufheben, Wurf aus dem Stand |
| Brüllaffe | [Science News: roaring red howler (Video eingebettet)](https://www.sciencenews.org/?p=19172) · Movies S1/S2 in [Dunn et al. 2015, PMC4635310](https://pmc.ncbi.nlm.nih.gov/articles/PMC4635310) | Gebrüll, Kehlsack |

### Fachliteratur (gelesen: Abstract/Zusammenfassung bzw. Volltext wie angegeben)
- **Druelle et al. 2021**, *J. Exp. Biol.* 224: jeb242587, „The quadrupedal walking gait of the olive baboon“ ([Artikel](https://cob.silverchair.com/jeb/article-split/224/14/jeb242587/271005/The-quadrupedal-walking-gait-of-the-olive-baboon), Volltext gesperrt, nur Zusammenfassung). Pavian: **Diagonalfolge mit diagonalen Paaren (DSDC)**, lange Standphase, niedrige Schrittfrequenz, großes Nachgeben im Ellbogen, Gewicht zu den Hinterbeinen verschoben; langsam (< 0,9 m/s) **Pendel-Energieaustausch 57 % (max. 84 %)** bei **Limb Phase ≈ 55 %**.
- Primaten allgemein: Hinterfuß setzt auf, dann der **diagonale** Vorderfuß (anders als die meisten Säuger mit Lateralfolge, z. B. Bär). [Cartmill et al. 2020 (PDF)](https://linglab.ucla.edu/s/A33-Cartmill-M-et-al-2020.pdf), [Shapiro & Raichlen 2005](https://experts.arizona.edu/en/publications/lateral-sequence-walking-in-infant-papio-cynocephalus-implication/).
- **Knöchelgang Schimpanse** (SICB-Abstract): größte senkrechte Kraft spät im Stand (70–80 %), vorn vor allem Bremskräfte. [sicb.org](https://sicb.org/abstracts/biomechanics-of-knuckle-walking-in-african-apes)
- **Galopp-Typen** (quer/rotierend, Halbsprung): [Bertram & Gutmann 2009, PMC2696142](https://pmc.ncbi.nlm.nih.gov/articles/PMC2696142) – Halbsprünge bei langsamem Galopp beginnen mit den Hinterbeinen. Pavian-spezifische Galopp-Daten **nicht gefunden**.
- **Steinwurf Schimpanse**: [Kühl et al. 2016, Sci. Rep. 6:22219, PMC4770594](https://pmc.ncbi.nlm.nih.gov/articles/PMC4770594) (Volltext gelesen). Wurfformen „hurl“ (mit einer oder beiden Händen werfen), „bang“, „toss“; Stein meist vom Boden aufgehoben; **jeder Wurf mit Pant-Hoot (Ruf) im Aufbau**; teils **zweibeinig, Haare gesträubt, Hin-und-her-Wiegen** vor dem Wurf. Überhand/Unterhand wird nicht beschrieben.
- **Pavian-Drohen**: Drohgähnen mit voll gezeigten Eckzähnen, Augenbrauen-Heben, Boden schlagen mit einer Hand, Ausfall (plötzlicher Vorstoß) und Zurückweichen. [Scientific American](https://www.scientificamerican.com/article/baboons-use-yawns-to-convey-social-messages/) · [EurekAlert (Foto mit Beschreibung)](https://www.eurekalert.org/multimedia/929349) · [Ethogramm-Tabelle PMC7883895](https://pmc.ncbi.nlm.nih.gov/articles/PMC7883895/table/T1)
- **Brüllaffe**: vergrößertes Zungenbein als Resonanzraum, Gebrüll-Folgen bis 15–40 min ([Britannica](https://www.britannica.com/animal/howler-monkey), [Science News](https://www.sciencenews.org/article/inside-roaring-sex-lives-howler-monkeys)). Körperhaltung beim Brüllen **nicht gefunden**.

### Kernaussagen
1. **Walk = Diagonalfolge mit diagonalen Paaren:** HL → (kurz danach) VR → HR → VL. Diagonale Bein-Paare setzen fast gemeinsam auf (Limb Phase ≈ 0,55).
2. **Lange Standphase, niedrige Frequenz, Gewicht hinten.** Die Vorderarme federn sichtbar im Ellbogen nach (Schulter sackt beim Aufsetzen ein).
3. **Run = Galopp/Halbsprung.** Hinterbeine setzen nah beieinander auf, Rücken beugt und streckt sich, Schwanz als Gegengewicht (Annahme, Videos prüfen).
4. **Drohen = Gähnen mit Eckzähnen + Boden schlagen + Vorstoß/Zurückweichen**, Haare gesträubt.
5. **Werfen = Stein greifen → aufrichten (teils zweibeinig), wiegen, Ruf → schleudern.**

---

## 4. Bewegungsregeln (Vorschlag für die `style.toml`)

30 fps. Natur = Richtwert; Spielgefühl: **flink und nervös**, deutlich leichter als Bär und Gorilla.
Offsets im Format des Bären (`order`, Aufsetzen = 1 − Offset, siehe `bear/style.toml`).

### a) Walk (Diagonalfolge)
- `order = { BL = 0.0, FR = 0.95, BR = 0.5, FL = 0.45 }` → Aufsetzen HL 0 · VR 0,05 · HR 0,5 · VL 0,55 (diagonale Paare, Limb Phase 0,55).
- **Zyklus 28 Frames** (≈ 1,07 Schritte/s; Bär 40, Wolf 32) · **Duty 0,66** · Schritt 0,22–0,26 × Länge (lange Arme greifen weit).
- **Arme:** Fuß-Hub vorn 10–12 % (Faust schwingt flach, rollt über die Knöchel), hinten 8 %. **Kein Zehen-Einrollen an der Faust** (`toe_curl` vorn ≈ 0–5°), hinten 20–25° (Greiffuß).
- **Ellbogen-Federn:** Schulter sinkt beim Aufsetzen des Arms 2–3 % Rumpfhöhe und hebt sich zum Abdruck (gut aus der Draufsicht über die Mähne sichtbar).
- Schultern rollen 5° / gieren 6°, Becken 3° / 4° (Annahme). Rumpf seitlich 0,8 % Länge.
- **Kopf:** stabilisiert (`head_gain` ≈ 0,4), dazu **schnelle Blickrucke** (2–3 Frames, 15–25°) einmal pro 2 Zyklen. Mähne folgt dem Kopf.
- **Schwanz:** hinten gestreckt, mit leichtem Aufwärtsbogen in der Mitte (Annahme, ARPG-lesbar), Spitze schwingt verzögert (`follow`, Gain > 1).

### b) Run (Galopp mit Halbsprung)
- Rotierend oder quer, Hinterbeine nah beieinander: Aufsetzen HL 0 · HR 0,08 · VL 0,45 · VR 0,55 (Annahme) · **Zyklus 14–16 Frames** · Duty 0,32–0,36 · eine Schwebe nach dem Hinterbein-Abdruck.
- **Rücken beugen/strecken ±12–15°** (Primaten-Rücken ist steifer als Wolf/Katze, aber der Buckel muss sichtbar arbeiten). Brust nickt 6–8°.
- Arme greifen weit vor (`swing_ext_front` 0,08–0,10), Körper 8–10 % tiefer als im Walk.
- **Schwanz hoch im Bogen** (+15–25° gehoben), peitscht verzögert nach – größte Silhouetten-Bewegung von oben.

### c) Wenden (TurnLeft/Right)
- Auf der Stelle, Gang-Rhythmus bleibt. **Kopf führt** (dreht zuerst, bis 35°), Schultergürtel folgt, Becken zuletzt, Schwanz schwingt zur Außenseite aus.
- **90–120 °/s** (≈ 40°/Zyklus bei 24 Frames). Arme machen die großen Schritte (Außenarm weit vor), Hinterbeine trippeln.

### d) Idle / Ready / Brüllen
- **Idle:** stehen, schnell atmen, **ruckartiges Umschauen** (Kopf schnell, Hals folgt), Gewicht verlagern, ab und zu Mähne schütteln (Kopf-Ruck 3–4 Frames), Schwanz pendelt langsam. Nicht sitzen (versteckt die Gliedmaßen).
- **Ready = Drohen (Loop 2 s):** Vorderkörper hoch (Brust +10–15°), **auf den Armen wippen** (2 Wipper/s, Annahme), 1× **Brüllen**: Kopf nach vorn-oben stoßen, Kiefer **35–45° auf** (Eckzähne), Hals/Brust gehen mit; 1× **Boden schlagen** mit einer Faust (Event `slam`, wie Bär `slap_leg`). Kurzer Vorstoß 5 % Länge und zurück („Scheinangriff“).
- **Brüllen sieht man von oben** nur, wenn der Kopf hochgeht: Kopf zum Brüllen anheben und Maul weit öffnen, die Mähne spreizt sich mit (Kopf + Nacken = größte bewegte Fläche).

### e) Angriffe
- **Attack1 = Steinwurf (Fernkampf, Hauptangriff der Rolle), ≈ 1,1–1,3 s, in place:**
  1. Greifen 6–8 Frames: rechte Faust (FR) tippt vor dem Körper auf den Boden (Event `stone_grab`), Kopf senkt sich mit.
  2. Aufrichten 8–10 Frames: Rumpf um die Hüfte **35–50° hoch** (Pivot Hüfte wie Bär Attack2), Gegenhand (FL) bleibt am Boden = dreibeinig **oder** hebt mit ab (zweibeinig, siehe Frage 2). Wurfarm **weit hinter den Kopf**, Rumpf dreht 20–25° weg (Ausholen = Telegraph), Brüllen andeuten.
  3. Wurf 3–4 Frames: Rumpf dreht zurück, Schulter vor, Arm schnell über Kopf nach vorn; **Event `projectile_spawn` beim Loslassen** (Arm ≈ 30° über der Waagerechten, Hand vor der Schulter), Position = Hand (`Leg_FR_3`-Ende).
  4. Nachschwung 6–8 Frames: Arm schlägt nach vorn-unten durch, Faust landet vor dem Körper, Rumpf fällt zurück auf vier Beine, Schwanz federt nach.
- **Attack2 = Ansprung-Biss (Nahkampf), ≈ 1,0 s, Root Motion:** kurz ducken (Hinterbeine beugen, 6–8 Frames) → **flacher Satz 1–1,5 Körperlängen**, Arme vorgestreckt, Maul weit auf, Schwanz gestreckt → Landung auf den Armen, Biss mit Kopf-Schütteln (Event `hit` bei der Landung) → Kopf zurück, Rumpf federt. Vorbild Pavian-Ausfall + Sprungvideo.
- Der **ganze Körper** arbeitet (Hinterbeine schieben, Rumpf dreht/kippt, Schwanz gleicht aus).

### f) Was die schräge Top-down-Kamera sieht
- **Sehr gut:** stachelige **Mähne** über Kopf/Schultern (größte Fläche), **Schultersteine**, **lange Arme** und ihr weiter Schwung, **Schwanzbogen**, Aufrichten + Wurfarm-Bogen, Sprungweg.
- **Gut, wenn übertrieben:** Brüllen (Kopf hoch!), Kopfrucke, Schultern sacken beim Aufsetzen ein, Rücken beugen im Galopp.
- **Kaum:** Gesicht/Eckzähne (nur bei gehobenem Kopf), Fäuste/Finger, Hinterfüße, Bauch, Unterarm-Ringe von unten.
- **Prüfbilder zuerst aus ARPG-Kamera**, Dehnung an Mähne/Nacken, Schulterstein-Rändern, Rücken und Schwanzansatz messen (C15).

---

## 5. Clip-Liste `Quadruped_Monkey_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Quadruped_Monkey_Idle` | ✓ | 3–4 s | Stehen und schnell atmen, ruckartig umschauen, Gewicht verlagern, einmal Mähne schütteln, Schwanz pendelt langsam. |
| `Quadruped_Monkey_Walk` | ✓ | ≈ 0,93 s | Knöchelgang in Diagonalfolge, Schultern sacken beim Aufsetzen ein, Kopf stabil mit Blickrucken, Schwanz schwingt verzögert. |
| `Quadruped_Monkey_Run` | ✓ | ≈ 0,5 s | Galopp mit Halbsprung und Schwebe, Rücken beugt/streckt sich, Arme greifen weit, Schwanz hoch im Bogen. |
| `Quadruped_Monkey_TurnLeft` / `TurnRight` | ✓ | ≈ 0,8 s | Auf der Stelle, Kopf führt, Schultern folgen, Becken zuletzt, Arme machen die großen Schritte, Schwanz schwingt aus. |
| `Quadruped_Monkey_Ready` | ✓ | 2 s | Drohen: Vorderkörper hoch, auf den Armen wippen, Brüllen mit weit offenem Maul, Faust schlägt auf den Boden, kurzer Scheinvorstoß. |
| `Quadruped_Monkey_Attack1` | – | ≈ 1,2 s | Steinwurf: Stein greifen, aufrichten und ausholen, Überkopf-Wurf (Event `projectile_spawn`), Nachschwung zurück auf vier Beine. |
| `Quadruped_Monkey_Attack2` | – | ≈ 1,0 s | Ansprung-Biss mit Root Motion: ducken, flacher Satz mit vorgestreckten Armen, Landung und Biss mit Kopfschütteln (Event `hit`). |
| `Quadruped_Monkey_Hit` | – | ≈ 0,4 s | Zurückzucken, Kopf schlägt zur Seite, Maul kurz auf (Schrei), Mähne und Schwanz federn nach. |
| `Quadruped_Monkey_Death` | – | – | **Gesperrt** (Nutzer 2026-11-17): nur Platzhalter aus dem Baukasten (z. B. Kopie Bär/Hirsch-Tod), nicht bearbeiten. |

Später (Varianten im Roster, **nicht vorziehen**): Howler Chieftain „Kriegsschrei“ (Cast/Taunt), Biom-Würfe (Giftfrucht, Eis, Glut) = nur anderes Projektil in Unity.

---

## 6. Erwartete Rig-Hürden (`rigging/quadruped_rig.py`, `motions/quadruped/quadruped_kit.py` gelesen, nicht getestet)

1. **Wirbelsäule kann abstürzen (wie C16):** `center_at(..., "body")` nimmt nur Vertices über `max(belly FL, belly BL) − 0,1·H`. Die langen Arme legen die Bauchlinie vorn hoch, der Rumpf fällt zur Hüfte ab → Querschnitt an der Hüfte evtl. leer → `None` → TypeError bei `Vector`. **Zuerst `--stage check` laufen lassen.** Fix nur optional (neuer Schalter, Standard = altes Verhalten), Regression.
2. **Arme schräg nach vorn:** Fäuste liegen weit vor dem Schultergelenk. Mit `leg_x_reach 0,18·L` hingen beim Bären die Pranken an Hals/Brust (Dehnung 32×). Startwerte wie Bär: `leg_x_reach = 0.30`, `leg_capture = 0.16`.
3. **Knöchel-Faust statt Pfote:** `Leg_F_4` (Zehen) reicht vom Ballen zur vordersten Faust-Spitze. Der Kit hat **nur ein `toe_curl_deg` für alle Beine** (`gait_smooth`) → Faust würde wie Zehen einrollen. Im eigenen `monkey_clips.py` eigene Gang-Funktion (Kopie von `gait_smooth` mit `toe_curl_front/back`) oder optionaler Kit-Parameter (abwärtskompatibel).
4. **Hinterfuß = Sohlengänger, gebeugtes Bein:** `bend()` sucht das Sprunggelenk bei 15–45 % Beinhöhe; beim Affen liegt die Ferse fast am Boden → Gelenk evtl. zu hoch. `rig_debug.png` prüfen, ggf. `back_hock` per creature.toml senken; IK-Steifigkeit `Leg_3 = 0,8` wie Bär (Sohle bleibt flach).
5. **Mähne:** groß, stachelig, sitzt über Kopf, Nacken **und** Schultern. **Kein `rigid_head_above` + `rigid_head_connected`** (würde die ganze Schultermähne starr an den Kopf hängen → reißt beim Kopfdrehen). Besser C15-Regeln wie Bär: `zone_lock = true`, `spine_chain_blend = 1.0`, ggf. `chest_extend` (Mähnen-Buckel an der Brust statt am Hals) und `[detect] spine_slice = 0.06` (grobe Facetten). Dehnung am Nacken aus ARPG-Kamera messen. Weich nachschwingen (Shader `weichheit`, G14) erst im Baukasten.
6. **10 Mesh-Teile** = vermutlich Goldringe/Armreifen: `rigid_parts = true` (starr am nächsten Knochen). Achtung: Teile **über** der Bauchlinie dürfen keinen Bein-Knochen wählen → Schulterringe landen an Shoulder/Chest/Neck – prüfen. Falls die Fangzähne lose Teile sind: `rigid_parts_exclude = ["Jaw"]` wie beim Bären (Oberkiefer-Fänge). Steine sind ins Hauptmesh gewachsen → folgen der Haut, Ränder auf Dehnung prüfen.
7. **Schwanz:** 4 Knochen für ~40 % der Länge, Spitze im Modell gehakt. Clips geben die Form **absolut** vor (Lehre Eel). `tail_base` (0,12) prüfen: Kruppe darf nicht am Schwanz hängen (Bär: 87 %, Fix `tail_base = 0.6`; beim Affen sitzt der Schwanz direkt hinter der Hüfte, Standard vermutlich ok).
8. **Aufrichten für Wurf:** Bär-Attack2-Logik (Pivot Hüfte, `paw_raise`, `paw_curl_deg`) in `monkey_clips.py` **kopieren**. Wurfarm über Kopf ist eine Bein-IK-Kette mit Schulterblatt (Steifigkeit 0,6) – Überkopf-Reichweite und Schulter-Dehnung (Steine!) prüfen. `reach_fix` senkt sonst den Rumpf.
9. **Root Motion (Attack2) fehlt im quadruped-Kit:** `bake()` kennt keinen Root-Motion-Typ; `stand_return` verlangt Root-Translation 0 am Ende; `stand` mit `planted = []` stürzt ab (`max()` über leere Liste). Lösung: optionaler Clip-Typ im Kit (abwärtskompatibel, Regression Wolf/Hirsch/Bär identisch) oder Sprung, der am Ende zur Ruhe zurückkehrt + Event `root_motion` mit `distance_m` (Vorbild `octopod/spider/spider_clips.py` Attack2, ab Z. 387).
10. **Projektil-Event:** `events` je Clip werden schon nach `events.json` geschrieben → `stone_grab` und `projectile_spawn` (mit Frame) eintragen; Stein-Prop + Anhängen an `Leg_FR_4` macht Unity. Kein eigener Hand-Socket-Knochen im Skelett.
11. **Symmetrie-Warnung 11,2 %:** in `[model_check.freigabe]` mit Begründung freigeben („Steine/Ringe ungleich verteilt, gewollt“).

---

## 7. Offene Fragen an den Nutzer

1. **Angriffe:** Attack1 = **Steinwurf** (Fernkampf, laut Rolle Hauptangriff), Attack2 = **Ansprung-Biss** mit Root Motion? **Empfehlung: ja.**
2. **Wurfhaltung:** halb aufgerichtet, Gegenhand bleibt am Boden (dreibeinig, schneller, weniger Rig-Risiko) oder ganz aufgerichtet auf zwei Beinen wie ein Schimpanse (dramatischer, länger)? **Empfehlung: halb aufgerichtet (Rumpf 35–50°), dreibeinig** – der Armbogen ist von oben trotzdem gut lesbar, und der Wurf ist für einen Schwarm-Gegner kurz genug.
3. **Stein:** Soll der Stein als eigenes kleines Objekt in Unity erscheinen (ab `stone_grab` in der Hand, bei `projectile_spawn` losgelassen) statt im Mesh? **Empfehlung: ja, eigenes Prop** – Biom-Varianten tauschen dann nur das Projektil (Giftfrucht, Eis, Glut).
