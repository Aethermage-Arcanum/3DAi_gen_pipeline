# Recherche Bewegungsmuster quadruped/frog (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten des Froschs (erste Kreatur: `creatures/16_oasis_gulper/`). Noch kein Code, keine `style.toml`.
Skelett/Muster laut `creatures/roster.toml` (Z. 660) und `creature.toml` (`[motion] style = "quadruped/frog"`, `bodyplan = "quadruped"`).
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Alle Aussagen stützen sich auf Artikel, Abstracts und
Video-Beschreibungen. Der Bau-Agent bzw. der Nutzer sollte die Videos unten **selbst ansehen** und die Werte dagegen prüfen
(CLAUDE.md „Naturbeobachtung zuerst“). Die C16-Analyse (Abschnitt 3) stammt aus einem reinen Lese-Nachbau der Erkennung
in Python (numpy, ohne Blender) auf genau der Datei, die das Rig bekommt.

---

## 1. Stand der Kreatur

| Was | v1 (Erstfassung, 18.11.) | v2 (Sprung-Pose, 18.11.) |
|---|---|---|
| Bilder | `input/_v1/front|left|right|back.png` | `input/front|left|right|back.png` (aus den Dateien „…im Sprung-1..4“) |
| Design-Bild | `input/design.png` = `Low-Poly-Oasengulper mit Seerosen.png` (hockende Kröte, Maul zu) | dasselbe Design-Bild, Pose per Trick des Nutzers „mitten im Sprung“ |
| Tripo-Modell | `raw/_v1/generate_model.glb` (+ `generate_rendered_image.webp`) | `raw/generate_model.glb` (Task c21d3d89…, 110 Credits) |
| Kennzahlen | 78 Mesh-Teile, Höhe 0,65 × Länge 0,73 (normiert) | **4.145 Tris, 1 Material, 59 Mesh-Teile**, 0,99 × 1,0 × 0,50 |
| Haltung | Hinterbeine senkrecht, steht hoch; Vorderbeine **waagerecht zur Seite** (T-Pose), Maul **weit offen** mit Zunge, Krallen | Alle 4 Füße am Boden, **alle Beine voll gestreckt**, Hinterbeine weit nach hinten-außen, Vorderfüße **vor der Schnauze**; Maul zu (Grinsen); runde Haftballen statt Krallen |

**Mängel, Kritik, Entscheidungen (mit Fundstelle):**
- Nutzer 2026-11-18: „sitzend“ versteckte beim Frosch die Beine → Prompts „alle Gliedmaßen in voller Länge“ (CLAUDE.md 1a, Commit fb88b0e).
- Nutzer 2026-11-18: ChatGPT klebt an der Vorlage, gestreckte Beine/T-Pose waren nicht zu bekommen → Trick „mitten im Sprung“ (README Z. 126, HANDOVER Z. 66, BACKLOG G6).
- v1: Vorderbeine stehen waagerecht ab → sollten per IK auf den Boden (Commit 040376a, `creature.toml` Kommentar, BACKLOG G5).
- v2: Claude-Prüfung „v2 klar besser“ (BACKLOG G5, Commit 2735b56). **Entscheidung des Nutzers offen (Q5).** Freigabe in `creature.toml`: `fussbreite` (Hinterfüße 1,97× breiter als vorn, froschtypisch).
- Nutzer 2026-11-18 (C9): Frosch ist sehr beweglich, aus gestreckter Sprung-Pose in die Hocke → Gelenke/Haut stark gedehnt → Gelenk-Verdichtung. Baustein `rigging/joint_densify.py` fertig, opt-in, bei keiner Kreatur an. **Nutzerkritik dazu:** am Sprunggelenk getestet, das aus der Spielkamera keine Rolle spielt → beim Frosch an **sichtbaren** Stellen prüfen (Oberschenkel/Hüfte, Rücken), siehe C15 und Memory „Prüfen aus Spielkamera“.
- C16: Rig bricht ab (Abschnitt 3). Lauf vom 20.11. in `temp/c9_frog_base/` (nur `uv/`, `rig/` leer).
- `temp/mc_gulper.log`: Freigabe-Schlüssel `schwerpunkt` war ungültig (betraf die auskommentierte v1-Freigabe, irrelevant für v2).

## 2. Prüfung Teil A (Bilder angesehen) und Modellsicht

**v2 (`input/*.png`, `raw/generate_rendered_image.webp`, `review/model_check.png`)**
1. Reihenfolge/Blickrichtung ✓ (left = Kopf links, right = Kopf rechts), Augenhöhe ✓.
2. Gleiche Haltung ⚠: Seiten zeigen einen fliegenden Frosch (Vorderbeine nach vorn, Hinterbeine waagerecht nach hinten), vorn/hinten zeigen die Beine schräg nach unten-außen. Für Tripo passte es: Modell steht mit 4 Füßen am Boden.
3. Nichts zwischen den Beinen ✓. 4. Hinten deutlich breiter als vorn (freigegeben, froschtypisch). 5. Gliedmaßen frei ✓ (Vorderarme nah an der Kehle, berühren nicht).
6. Grundpose gerade ✓, Maul zu ✓. **Aber:** Beine extrem gestreckt → jede Ruhe-/Hockpose braucht große Beugung (C9).
7. Teilezahl ✓ (4 Beine, Seerosen + Schilf; Anzahl Blätter/Halme schwankt leicht je Ansicht, unkritisch).
8. Dünne Teile: Seerosenblätter/Schilfhalme flach; 13 kleine einseitige Bereiche (nur Info). 9. Kein Glühen ✓.
Gegen `design.png`: Farben, Warzen, Streifen, Augen passen; Pose bewusst anders (Hocke → Sprung).
Modell: sauber, symmetrisch (9,4 % ohne Partner), Rücken mit Seerosen/Schilf, gestreifte Oberschenkel gut lesbar. Seerosen/Schilf = lose Teile (59).

**v1 (`input/_v1/*.png`, `raw/_v1/generate_rendered_image.webp`)**
1. ✓. 2. ✗ vorn T-Pose-Arme, seitlich Arme an die Brust gezogen (widersprüchlich). 5. ✗ Arme berühren seitlich den Körper.
6. ✗ Maul weit offen mit Zunge (Checkliste: zu oder nur leicht offen). 7. Krallen statt Haftballen, mehr Warzen.
Modell: Vorderbeine waagerecht, nur die Hinterfüße am Boden, Hinterbeine senkrecht (stehende Kröte, untypisch).

## 3. C16-Analyse (nur gelesen, nichts geändert)

**Code-Stelle** `rigging/quadruped_rig.py` Z. 207–215 und 230:
```python
def center_at(x, region=None, sl=None):
    s = M[np.abs(M[:, 0] - x) < (sl or D["slice"]) * L]
    if region == "body":
        s = s[s[:, 2] > max(LEGS["FL"]["belly"], LEGS["BL"]["belly"]) - 0.1 * H]
    if len(s) < 3:
        return None
...
spine = [center_at(x_hip + f * (x_ce - x_hip), "body", SSL) for f in (0, 1 / 3, 2 / 3, 1)]
```
Der Schwanz hat seit dem Bären eine Lückenfüllung (Z. 238–242), **Wirbelsäule und Hals nicht** → `BONES["Hips"] = (spine[0], …)` → `Vector(None)` (Z. 274) → TypeError.

**Nachgerechnet auf `temp/c9_frog_base/uv/model_uv.glb` (= Rig-Eingabe, v2):** Höhe H 0,374, Länge L 0,986.
- Füße korrekt gefunden: vorn x = +0,48 (y ±0,23), hinten x = −0,34 (y ±0,46).
- **Bauch-Erkennung scheitert an allen 4 Beinen:** `midline_profile` an der Fuß-x-Position liefert None, weil dort kein Rumpf ist (Vorderfüße liegen *vor* der Schnauze, Hinterfüße *hinter* dem Rumpf). Fallback `belly = Boden + 0,55·H` = 0,206.
- Das Hochverfolgen der Beine (Z. 147–156) setzt senkrechte Beine voraus. Die flach gespreizten Froschbeine liefern Unsinn und sogar **asymmetrische Hüften**: BL bei x −0,32, BR bei x −0,48. → `x_hip` = −0,40.
- Bei x −0,40 liegt nur noch Hinterbein (Höhe ≤ 0,134), die Schwelle `region="body"` ist 0,168 → **0 Vertices → `spine[0]` = None → Absturz.** spine[1..3], Hals und Schwanz liefern Werte.
- Auch ohne Absturz wäre das Rig falsch: `x_nose`/`x_tail` = Mesh-Extremwerte = **Vorderzehen (+0,49) bzw. Hinterzehen (−0,49)**. Kopf-Knochen würde in den Vorderfüßen enden, die Schwanzkette in den Hinterbeinen liegen, die Schultern bei x 0,36 (fast an der Schnauze).
- Echter Rumpf laut Mittellinien-Streifen: **x −0,20 … +0,39** (Schnauze ≈ +0,39, Steiß ≈ −0,20).
- v1 zum Vergleich: kein Absturz, aber `detect_feet` nimmt die zwei Hinterfüße als vorn *und* hinten (Vorderbeine in der Luft) → Hüfte ≈ Schulter, Wirbelsäule ohne Länge. **v1 braucht also ebenfalls eine eigene Erkennung.**

**Fix-Vorschlag (gekapselt, andere Vierbeiner unverändert):**
1. Neues opt-in in `[quadruped.rig]` der creature.toml, z. B. `detect = "frog"` (Standard `"default"` = heutiger Code-Pfad, byte-gleich). Die Frosch-Erkennung kommt in eine **eigene Datei** `rigging/quadruped_frog_detect.py`; `quadruped_rig.py` bekommt nur eine Verzweigung, die `LEGS`/`BONES`-Landmarken aus dieser Datei holt.
2. Rumpf aus dem Mittellinien-Streifen (|y| < `mid_half_width`·H, z > `min_belly`·H): `x_nose` = max, `x_tail` = min dieses Streifens, nicht vom ganzen Mesh.
3. Hüfte/Schulter: Weg vom Fuß zur Rumpfmitte über die Mesh-Kanten (Dijkstra, Ansatz wie `multileg_rig.py`, aber **kopiert**, nicht importiert). Der Punkt, an dem der Weg in den Rumpf eintritt, ist das Gelenk. Knie/Sprunggelenk/Ballen nach Bogenlänge entlang des Wegs, Startwerte Hinterbein Oberschenkel : Schienbein : Fußwurzel : Fuß ≈ 1 : 1 : 0,6 : 0,8 (Faustwert, prüfen). Danach links/rechts spiegeln (symmetrisch erzwingen).
4. Wirbelsäule nur über den Rumpf-Bereich, ohne `region="body"`-Filter; **None-Schutz wie beim Schwanz** (vom Nachbarn füllen) zusätzlich und mit `RIG_WARN`-Ausgabe, damit es nie wieder still abstürzt.
5. Frosch hat keinen Schwanz: Tail_1..4 als kurzer Stummel am Steiß behalten (Skelett-Standard), praktisch ohne Gewichte.
6. Seerosen/Schilf (lose Teile): `rigid_parts = true` → starr an Spine/Chest; Schilfhalme optional über `rigging/dangling.py` leicht nachschwingen lassen (Standard-Baustein für frei hängende Teile).
7. `[joint_densify]` für Hüfte, Knie, Sprunggelenk hinten und Ellbogen vorn. Prüfen an Oberschenkel-Ansatz und Rücken aus der Spielkamera, nicht an den Füßen.
8. Test: `--stage check` nur für 16_oasis_gulper; danach `python scripts/regression.py --deep` → Wolf, Echse, Hirsch, Bär identisch.

## 4. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen)
| Thema | Link | Was man laut Beschreibung sieht |
|---|---|---|
| Ochsenfrosch-Sprung, Zeitlupe | [YouTube sgB0gsvpg2c](https://www.youtube.com/watch?v=sgB0gsvpg2c) (über [Gizmodo](https://gizmodo.com/slow-motion-bullfrogs-look-super-dramatic-1594305496)) · [Britannica: Bullfrog jump](https://www.britannica.com/video/22215/bullfrog-North-America-parts) | Kraft aus den Hinterbeinen, Streckung, Flug |
| Froschsprung Super-Zeitlupe | [National Geographic](https://nationalgeographic.com/animals/article/100512-frog-muscle-study-embed-video) | Sehnen-Katapult, Absprung |
| Kröten-Zungenschlag | [Britannica: Toad tongue, real time + slow motion](https://www.britannica.com/video/22454/toad-footage-tongue-prey) · [PBS/KQED: Toad tongues](https://www.pbs.org/video/toad-tongues-slay-with-seriously-sticky-spit-pi4g1g) · [Cane-Toad-Zeitlupe](https://rmkeeffe.github.io/projects/1_project) | Annähern, Zunge raus, Beute ins Maul; danach Schlucken |
| Kröte hüpft vs. „bounding“ | [Science News: Toads prefer to bound](https://www.sciencenews.org/blog/wild-things/toads-prefer-bound-not-hop) | Landung erst vorn, dann Hinterbeine; Serien-Sprünge ohne Pause |

### Quellen
- **Reilly et al. 2015**, *Functional Ecology* 29:1308 – Kröten (u. a. Aga-Kröte) „hüpfen“ meist im **Bounding**: Einzelsprung = Landung **zuerst auf den Vorderbeinen**, die gefalteten Hinterbeine folgen; Serie = Vorder- und gestreckte Hinterbeine landen fast gleichzeitig, sofort nächster Absprung, ≈ 18 % billiger. [ADS](https://ui.adsabs.harvard.edu/abs/2015FuEco..29.1308R) · [Science News](https://www.sciencenews.org/blog/wild-things/toads-prefer-bound-not-hop)
- **Cox & Gillis 2016**, *Biology Open* – Aga-Kröten richten die **Vorderbeine vor dem Aufprall nach dem Landewinkel aus** und bremsen damit ab. [PMC5278434](https://pmc.ncbi.nlm.nih.gov/articles/PMC5278434)
- **Frosch-Sprungstudie** (PLoS ONE 2017, Tabelle): Antriebsphase **109 ± 4 ms**, Absprungwinkel **54°**, Weite 59 cm. [PMC5345813](https://pmc.ncbi.nlm.nih.gov/articles/PMC5345813)
- **Noel, Hu et al. 2017**, *J. R. Soc. Interface* 14:20160764 – Zunge fängt Insekten in **< 0,07 s**, Zunge weich wie Hirngewebe, Speichel klebt beim Rückzug. [Georgia Tech](https://news.gatech.edu/news/2017/01/31/reversible-saliva-allows-frogs-hang-next-meal)
- **Lappin/Deban** – Kröten-Zungenschuss ballistisch über **gespeicherte elastische Energie**, Maul-Öffnen löst ihn aus. [NAU](https://experts.nau.edu/en/publications/storage-and-recovery-of-elastic-potential-energy-powers-ballistic/)
- **Abwehr bei Kröten:** Aufblähen (Lunge füllen), Körper vom Boden heben, „stiff-legged“ (steife, gestreckte Beine). [Copeia 2018, Bufonidae vs. Ranidae](https://bioone.org/journals/copeia/volume-106/issue-1/CE-16-567/Do-Bufonids-Employ-Different-Anti-Predator-Behaviors-Than-Ranids-Comparison/10.1643/CE-16-567.full) · [Stiff-legged, Rhinella humboldti](https://herpetologia.fciencias.unam.mx/index.php/revista/article/view/28/version/23)
- **Krötengang:** diagonales Schreiten (Kreuzgang), auch nach Deafferentierung erzeugt. [J. Exp. Biol. 53:255](https://cob.silverchair.com/jeb/article/53/2/255/21460/Diagonal-Locomotion-in-De-Afferentated-Toads) (nur Titel/Abstract).

### Kernaussagen
1. Große Frösche **springen weit** (Absprung ≈ 0,1 s, Winkel 45–55°), **Kröten hüpfen kurz und flach** oder schreiten. Ein riesiger, aufgeblähter Gulper wirkt glaubwürdiger als Kröte: kurze, schwere Hüpfer.
2. **Landung:** Vorderbeine strecken sich vor dem Aufprall nach vorn-unten, fangen ab, der Körper kippt nach vorn, dann klappen die Hinterbeine unter den Körper (Gewicht, Nachfedern).
3. **Zunge:** extrem schnell (< 70 ms), ballistisch, Maul-Öffnen löst aus. Für Spieler zu schnell → Ausholen davor nötig (MOVESET „Telegraph“).
4. **Drohen:** aufblähen, auf gestreckten Beinen hochstemmen, zum Gegner kippen. Das „Kippen zum Gegner“ ist in den Quellen **nicht belegt** (nur Fauchen beim Sonora-Kröten-Bericht).

## 5. Bewegungsregeln (Vorschlag für die `style.toml`)

Alle Zeitwerte bei 30 fps, Längen in Körperlängen (KL = Rumpf + Kopf ≈ 0,6 Modelleinheiten). Natur nur Richtwert, Tempo nach Spielgefühl.

**a) Ruhehaltung = Hocke (nicht die Tripo-Pose):** Hinterbeine im Z gefaltet (Oberschenkel nach vorn-außen, Schienbein nach hinten, Fuß flach nach vorn-außen), Knie ≈ 30–40° Innenwinkel; Vorderbeine kurz, senkrecht stützend; Bauch knapp über dem Boden. Die gestreckte Tripo-Pose ist nur Bind-Pose. **Dehnung beim Falten:** Ursache am Mesh lösen (C9 an Hüfte, Knie, Sprunggelenk), nie die Hocke flacher machen. Roh-GIF mit allen Dehnungen mitspeichern.

**b) Fortbewegung:**
| Clip | Art | Zyklus | Werte |
|---|---|---|---|
| Walk | **Krötenschreiten**, diagonal (VL+HR, VR+HL) | 24–30 Frames | Duty ≈ 0,75, Schritt 0,1–0,15 KL, Körper niedrig, wiegt seitlich ±3°, Hinterbeine bleiben halb gefaltet |
| Run | **Hüpfserie (bounding)**, in place | 14–18 Frames pro Satz | Absprung 3–4 F (Hinterbeine schnellen gestreckt nach hinten), Flug 6–8 F, Scheitel 0,2–0,3 KL, Landung vorn zuerst + 3–4 F Abfedern, sofort nächster Absprung; Weite ≈ 1–1,5 KL pro Satz (Unity-Tempo daraus) |

Root-Motion-Hinweis: In-place-Hüpfen mit gleichmäßigem NavMesh-Tempo lässt die Füße in der Bodenphase rutschen. Bodenphase daher kurz halten (bounding) oder Run mit Root Motion backen. Der Bau-Agent soll das sichtbar machen und nachfragen, nicht still entscheiden.

**c) Körper:** Beim Sprung **ganzer Körper** strecken (Rücken flach, Kopf voran), in der Luft Vorderbeine nach vorn, Hinterbeine nach hinten gestreckt. Das ist die Tripo-Pose, sie dient als Flug-Keypose. Bauch/Rücken wackeln beim Landen nach (Gewicht, 2–4 F Follow-Through über Spine-Skalierung/Biegung). Seerosen starr, Schilf schwingt nach.

**d) Drehen (TurnLeft/Right):** Kein gedrehter Walk. Vorderbeine treten zur Seite, Hinterbeine schieben in kleinen Rucken nach, Kopf führt, Rumpf biegt sich leicht mit. Alternativ ein kurzer Dreh-Hüpfer (30–45° pro Hüpfer). Tempo ≈ 90 °/s.

**e) Kehle/Maul:** Idle: Kehle pumpt 1–2 Hz (Jaw minimal + Skalierung unter dem Kopf). Kaum sichtbar von oben, daher klein halten. **Aufblähen** (Ready/Drohen): Rumpf seitlich +10–20 % (Skalierung Spine/Chest), deutlich sichtbar in der Silhouette.

**f) Angriffe** (Rolle laut Roster: „Zungenschlag zieht heran“):
- **Attack1 = Zungenschlag** (≈ 1,0 s): Ausholen 10–12 F (Körper duckt sich, Kopf zielt, Kehle bläht), Maul auf + Zunge raus **3–4 F** bis 2–3 KL Reichweite (Event `hit` bei voller Länge), 2–3 F halten, Zurückziehen 6–8 F (Event `pull`, Ziel wird herangezogen), Schlucken/Kehle 4 F. Ganzkörper: Hinterbeine stemmen, Rumpf ruckt beim Schuss nach vorn und beim Ziehen zurück.
  **Problem Zunge:** v2 hat das Maul zu, im Mesh gibt es keine Zunge. Fake it: eigenes Zungen-Teil (einfacher Schlauch, 4–6 Knochen `Tongue_1..n` am Jaw) im Rig erzeugen, im Ruhezustand im Maul versteckt bzw. auf 0 skaliert. Dicke ≥ 0,06 KL, sonst von oben unsichtbar. Dazu einen dunklen Maul-Einsatz, damit beim Öffnen kein Loch klafft.
- **Attack2 = Sprung-Plumps** (≈ 1,2 s, Root Motion, Vorschlag): tiefe Hocke 8–10 F (Telegraph), Satz 1,5–2 KL, Landung mit ganzem Gewicht auf dem Ziel (Event `hit`), 6–8 F Nachfedern/Ausrollen. Passt zum Elite-„Great Gulper“.

**g) Was die schräge Top-down-Kamera sieht:**
- **Gut sichtbar:** Rücken mit Seerosen/Schilf (größte Fläche), die **orange gestreiften Oberschenkel**, die Silhouette Hocke ↔ gestreckt (beim Sprung schießt die Silhouette nach hinten), Aufblähen, die Zunge als lange rosa Linie.
- **Kaum sichtbar:** Kehle, Maul-Innenraum, Zehen/Haftballen, Bauch, Fußgelenke.
- **Folge:** Dehnung zuerst an **Hüfte/Oberschenkel-Ansatz und Rücken** prüfen; Prüf-GIFs zuerst aus der Spielkamera, Angriffe per Kontaktbogen (Treffpunkt der Zunge, Ganzkörper).

## 6. Clip-Liste `Quadruped_Frog_*`

| Clip | Loop | Inhalt (1 Satz) |
|---|---|---|
| `Quadruped_Frog_Idle` | ✓ | Träge Hocke, Kehle pumpt langsam, Rücken atmet, Schilf wiegt, ab und zu ein Augen-/Kopfrucken. |
| `Quadruped_Frog_Walk` | ✓ | Schweres Krötenschreiten im Kreuzgang, Körper niedrig und seitlich wiegend, Hinterbeine halb gefaltet. |
| `Quadruped_Frog_Run` | ✓ | Hüpfserie (bounding): Absprung mit voll gestreckten Hinterbeinen, flacher Flug, Landung vorn zuerst, sofort weiter. |
| `Quadruped_Frog_TurnLeft` / `TurnRight` | ✓ | Vorderbeine treten seitlich, Hinterbeine schieben ruckweise nach, Kopf führt, Rumpf biegt mit (≈ 90 °/s). |
| `Quadruped_Frog_Ready` | ✓ | Aufgebläht auf gestreckten Beinen hochgestemmt, Kopf zum Ziel, Kehle pumpt schnell, leichtes Wiegen. |
| `Quadruped_Frog_Attack1` | – | Zungenschlag: ducken und zielen, Zunge schießt 2–3 KL vor (`hit`), zieht das Ziel heran (`pull`), Schlucken. |
| `Quadruped_Frog_Attack2` | – | Sprung-Plumps mit Root Motion: tiefe Hocke, Satz auf das Ziel, schwere Landung (`hit`), Nachfedern. |
| `Quadruped_Frog_Hit` | – | Körper staucht zusammen und sackt ab, Beine zucken an, Rücken federt nach. |
| `Quadruped_Frog_Death` | – | **Nur Platzhalter** aus dem Baukasten (Death gesperrt, Nutzer 2026-11-17). |

Eigener Clip-Code `motions/quadruped/frog/frog_clips.py` (nichts aus wolf/bear importieren); Baukasten `quadruped_kit.py` nur abwärtskompatibel erweitern.

## 7. Offene Fragen an den Nutzer
1. **v1 oder v2? (Q5)** Empfehlung **v2**: alle 4 Füße am Boden, Maul zu, symmetrisch, Haftballen; die gestreckte Pose ist zugleich die Flug-Keypose. v1 hat widersprüchliche Arme, ein offenes Maul und braucht ebenfalls eine Sonder-Erkennung. Kein neuer Tripo-Lauf nötig.
2. **Zunge:** als eigenes Teil mit Knochen im Modell (Empfehlung: liegt im FBX, Clip steuert Reichweite und Treffer-Frame) oder als reiner Unity-Effekt (Linie/Shader)?
3. **Gangart:** Walk = Krötenschreiten, Run = Hüpfserie (Empfehlung), oder soll der Frosch auch im Walk nur hüpfen? Dazu: Run mit Root Motion backen (Empfehlung, keine rutschenden Füße)?
