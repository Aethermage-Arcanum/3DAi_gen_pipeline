# Recherche Bewegungsmuster quadruped/tortoise (Stand 2026-11-23)

Vorarbeit für den Bau-Agenten der Schildkröte. Erste Kreatur: `creatures/11_shellback/`. Es gibt noch keinen Code, keine `style.toml` und keinen Clip.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Alle Aussagen stützen sich auf Fachartikel bzw. deren Abstracts,
Behörden-Steckbriefe und Video-Beschreibungen. Die Werte unten sind Startwerte. Der Bau-Agent bzw. der Nutzer sollte die Videos
**selbst ansehen** und die Werte dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“).

---

## 1. Stand der Kreatur

| Was | Fundstelle |
|---|---|
| Skelett **quadruped**, Muster **tortoise** (neu). Vorbilder: „Schnappschildkröte – Biss“ und „Landschildkröte – langsamer Gang, Kopf einziehen“. | `creatures/roster.toml` Z. 122–138, `creatures/11_shellback/creature.toml` `[motion]`, HANDOVER Z. 24, Z. 87 |
| **Erste Kreatur in der Bau-Warteschlange:** Schildkröte → Sandwurm → Gorilla → … | BACKLOG Z. 104, HANDOVER Z. 46 |
| Ansichten wurden aus `grid_4_ansichten.png` nach Inhalt neu geschnitten, weil die Köpfe ins Nachbarbild gerutscht waren. Die Originale liegen in `input/_orig/`. | BACKLOG G3, HANDOVER Z. 24 und Z. 68 |
| Tripo-Modell vom 18.11. (110 Credits, Commit 1cf4996). **Pflichtprüfung B bestanden.** | BACKLOG G3, HANDOVER Z. 20–24 |
| `review/model_check.json`: keine automatischen Auffälligkeiten. **4.344 Tris**, 1 Material, **3 Mesh-Teile** (vermutlich Hauptkörper + Augen; das muss der Bau-Agent prüfen), Maße 1,0 × 0,62 × 0,60, Symmetrie exakt (0 %). 4 Fußgruppen: vorne x = +0,33, hinten x = −0,19, Fußbreite vorne/hinten 1,02×. | `creatures/11_shellback/review/model_check.json` |
| **Noch nicht vorhanden:** README der Kreatur, `rig/`, `output/`, `uv/`, `[quadruped.*]`-Einstellungen in der creature.toml, der Muster-Ordner (nur diese Datei). | Ordnerinhalt 2026-11-23 |

**Nutzerkritik direkt an der Shellback gibt es nicht**, denn es wurde noch nie etwas gebaut. Für den Bau gelten die allgemeinen Lehren:
- **Kapselung (A1):** Im BACKLOG steht wörtlich „Änderungen an der Schildkröte haben den fertigen Wolf kaputt gemacht“. Daraus folgt: eigene `tortoise_clips.py`. Neue Rig-Optionen gibt es **nur opt-in** in `quadruped_rig.py`, und Wolf, Hirsch, Echse und Bär müssen per `scripts/regression.py` identisch bleiben (`motions/README.md` „Kapselung“).
- **Nicht roboterhaft (C1, B3).** Schwer und stur heißt nicht ruckig. Die Füße setzen weich auf, Kopf und Schwanz ziehen nach.
- **Ganzkörper (C4):** Ein Turn ist kein gedrehter Walk, und Ready ist kein verschobenes Modell. Beim Biss arbeiten Hinterbeine, Panzer und Hals mit, nicht nur der Kopf (Kobra-Lehre).
- **Prüfen aus der Spielkamera (C15):** Hier zählen Panzer-Silhouette, Kopf und Hals vor dem Panzer und die Krallen an den Seiten, nicht die Fußgelenke.
- Dehnung nicht durch kleinere Bewegung lösen. Roh-GIFs mitspeichern. **Death nicht anfassen** (E1).

---

## 2. Prüfung Teil A der Referenzbilder (`input/front|left|right|back.png`) + Sichtung `raw/generate_rendered_image.webp`

| # | Punkt | Befund |
|---|---|---|
| 1 | Reihenfolge/Blickrichtung | ✓ vorn, Kopf links, Kopf rechts, hinten. Die Kamera schaut leicht von oben, das ist in Ordnung. |
| 2 | Gleiche Haltung | ✓ weitgehend. Der Kopf ist überall tief und vorgestreckt. |
| 3 | Nichts zwischen den Beinen | ⚠ **gering:** In `back.png` zeigt der Schwanzstachel **schräg nach unten zwischen die Hinterbeine**, die Spitze sitzt bei ca. 10 % Höhe über dem Boden. In `left.png`/`right.png` liegt er waagerecht auf Bauchhöhe. Tripo hat ihn waagerecht gebaut (model_check „nichts hängt“). Kein Handlungsbedarf, aber der Bau-Agent soll die Schwanzkette in `rig_debug.png` prüfen. |
| 4 | Beine vorn/hinten gleich breit | ✓ (Modell 1,02×). Die Beine stehen **gespreizt** (Ellbogen und Knie nach außen), wie bei einer echten Schildkröte. Das ist gewollt und kein Fehler. |
| 5 | Gliedmaßen frei | ⚠ **für das Rig wichtig:** Oberarm und Oberschenkel gehen breit in den Körper über, und der **Panzerrand liegt direkt auf** (left/right: der Rand berührt Oberarm und Oberschenkel fast). Die Beine untereinander sind frei. |
| 6 | Neutrale Grundpose | ✓ mit Einschränkung: Das Maul ist leicht offen und zeigt die Zähne (erlaubt). In der Seitenansicht stehen die Vorderbeine schräg nach vorn und die Hinterbeine schräg nach hinten, also eher eine Schritt- als eine Säulenstellung. Für die IK ist das unkritisch. |
| 7 | Teilezahl | ✓ 4 Beine, Schwanz, Kopf. Abweichend vom `look` hat er **nur 1 Auge pro Seite** statt „several small orange eyes“, und die „horn spikes“ sind eher Brauenwülste. Das ist eine reine Design-Frage, die das Rig nicht betrifft. |
| 8 | Dünne Teile mit Volumen | ✓ Stacheln mit Volumen. |
| 9 | Kein Glühen/Schrift | ✓ |
| – | **Hals** | ⚠ **für die Animation wichtig:** In **keiner Ansicht ist ein Hals sichtbar**. Der Kopf kommt direkt unter der vorderen Panzerplatte (Nackenschild) heraus. Im Frontbild und im Tripo-Render sitzt die mittlere Panzerplatte **auf dem Kopf** („Kopf halb im Panzer“), und die Grenze zwischen Kopfplatte und Panzer ist nicht eindeutig. |
| – | **Schwanz** | Der Schwanz ist ein langer, dünner Stachel (Draufsicht in `model_check.png`: ca. 20–23 % der Körperlänge), der flach unter dem hinteren Panzerrand liegt und optisch wie eine Verlängerung des Panzers wirkt. |
| – | Tripo-Render | Er passt zu den Bildern. Die Vorderbeine sind massig, gespreizt und weit vorn (die Füße stehen fast unter dem Kopf), mit großen Krallen. Die Unterseite (Bauchpanzer) liegt tief, der Bodenabstand beträgt ca. 1/4 der Höhe. |

**Fazit Teil A:** Kein Grund für neue Bilder. Zwei Merkmale bestimmen die Rig-Arbeit: der **fehlende sichtbare Hals** (begrenzt Zustoßen und Einziehen) und der **Panzerrand, der auf Oberarm, Oberschenkel, Kopf und Schwanzansatz aufliegt**. Teil B mit Blender-Renders (vorn/Seite/oben/ARPG) macht der Bau-Agent.

---

## 3. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen; selbst nicht angesehen)
| Thema | Quelle | Was man laut Beschreibung sieht |
|---|---|---|
| Biss der Schnappschildkröte, Zeitlupe 1000 fps | Brave Wilderness, „Snapper Bites Hand in Super Slow Motion“ (YouTube, ca. 9 Mio. Aufrufe; Transkript: [rosetta.to](https://rosetta.to/u/bravewilderness/snapper-bites-hand-in-super-slow-motion?t=0)) | Hals schießt vor, Maul öffnet weit und schließt schlagartig |
| Biss, Zeitlupe | [Snapping turtle strike in super slow motion (justapinch)](https://www.justapinch.com/video/view/2yWfhHCa0WC9m18SgVqP5w/snapping-turtle-strike-in-super-slow-motion) | Zustoßen des Kopfes aus der Ruhe |
| Alligator-Schnappschildkröte, Bisstest | Coyote Peterson (Brave Wilderness), verlinkt bei [Wide Open Spaces](https://wideopenspaces.com/?p=236923) (ab ca. Minute 7, Zeitlupe) | Kopf zurück, Biss auf eine Latex-Hand |
| Gang Riesenschildkröte | [Aldabra-Riesenschildkröte, Zanzibar (motionelements)](https://www.motionelements.com/stock-video-16332452-a-huge-aldabra-giant-tortoise-walking-on-a-prison-island-in-zanzibar-africa), [Leopardschildkröte (storyblocks)](https://www.storyblocks.com/video/stock/leopard-tortoise-walks-slowly-away-bdx7abxjokk2vqptq) | schwerer Gang, Panzer schaukelt, Kopf vorgestreckt |
| Gang Landschildkröte | [Indian star tortoise walking (uppbeat)](https://uppbeat.io/stock-video/asset/indian-star-tortoise-walking-10140), [Tortoise walking slowly (uppbeat)](https://uppbeat.io/stock-video/asset/tortoise-walking-slowly-10136) | kleine Landschildkröte, Beinfolge gut sichtbar |

Auf YouTube direkt nach „tortoise walking slow motion“, „snapping turtle defensive strike on land“ und „tortoise head retract“ suchen. Bei der Suche fanden sich keine geprüften YouTube-Links.

### Fachliteratur und Steckbriefe (gelesen: Abstracts bzw. Zusammenfassungen)
- **Schmidt, Mehlhorn & Fischer 2016**, *J. Exp. Biol.* 219:2693: Biplanares Röntgen bei der **Griechischen Landschildkröte** (*Testudo hermanni*). Ergebnis: langsamer Gang mit **niedriger Schrittfrequenz**, **lateraler Sequenz, diagonal gekoppelt**, **hoher Duty Factor**. Die **Drehung des Schultergürtels** in der Waagerechten liefert **über 30 % des Vorderbein-Ausschlags**. [Artikel](https://cob.silverchair.com/jeb/article/219/17/2693/15373/Shoulder-girdle-rotation-forelimb-movement-and-the)
- **Zani, Gottschall & Kram 2005**, *J. Exp. Biol.* 208:1489: Galápagos-Riesenschildkröten (143 kg) gehen mit **8–22 cm/s (Mittel 15,8 cm/s)**, „**nearly pausing with each step**“. Der Schwerpunkt hebt sich um **≈ 2,0 cm** pro Schritt, und zwar aktiv angehoben, ohne Pendel (≈ 30 % Energierückgewinnung). [Abstract SICB](https://sicb.org/?p=34601) · [PSU](https://pure.psu.edu/en/publications/giant-gal%C3%A1pagos-tortoises-walk-without-inverted-pendulum-mechanic/)
- **Jayes & Alexander 1980**, *J. Zool.*, „The gaits of chelonians“: Schildkröten nutzen Gänge, bei denen zeitweise **nur 2 Füße** am Boden sind, obwohl eine statisch stabile Gangart einen Duty Factor ≥ 0,75 bräuchte. Nur als Zitat gefunden, z. B. [eLife 2017](https://elifesciences.org/articles/29495).
- **Abwehr der Schnappschildkröte an Land** (*Chelydra serpentina*): Sie **hebt das Hinterteil**, **reißt das Maul auf** und **schlägt plötzlich schlangenartig zu**. [NC Wildlife](https://ncwildlife.gov/species/common-snapping-turtle). Der Kopf schießt **nach vorn-oben**, oft sogar über den eigenen Panzer. Die Reichweite beträgt **½–⅔ der Panzerlänge** ([Virginia Herpetological Society](https://www.virginiaherpetologicalsociety.com/reptiles/turtles/eastern-snapping-turtle/index.php)). Fauchen ist nur anekdotisch belegt ([Coastal Review](https://coastalreview.org/2026/07/my-uncommon-interactions-with-common-snapping-turtles/)). Laut [The Land Between](https://www.thelandbetween.ca/the-land-between-species-at-risk/snapping-turtle/) ist der Panzer **zu klein zum Zurückziehen**, und deshalb wehrt sich das Tier aggressiv.
- **Biss-Kinematik der Alligator-Schnappschildkröte** (*Macrochelys*): Kiefer- und Ausfallgeschwindigkeit hängen stark von der Temperatur ab. Zahlen standen nicht in den Abstracts. [Missouri State](https://bearworks.missouristate.edu/articles00/9). Die Gewöhnliche Schnappschildkröte ist ein **Ramm-Fresser** (Körper und Kopf stoßen vor, kaum Saugen; [Lauder & Prendergast 1992](https://sites.harvard.edu/glauder/files/2022/03/LauderPendergast1992.pdf)).
- **Lehrbuchwissen, nicht aus den Links geprüft:** Halsberger-Schildkröten (Cryptodira) ziehen den Hals in einer **senkrechten S-Kurve** ein. Bei Landschildkröten ist die Wirbelsäule im Rumpf **mit dem Panzer verwachsen**, und Becken und Schultergürtel liegen **im** Panzer. Männliche Landschildkröten **rammen** Rivalen beim Kommentkampf mit dem vorderen Bauchpanzer (Gularschild) und versuchen, sie umzuwerfen.

---

## 4. Bewegungsregeln (Vorschlag für die `style.toml`)

Alle Zeitwerte gelten bei 30 fps. **Echte Schildkröten sind zu langsam für ein ARPG.** Eine Riesenschildkröte „pausiert fast bei jedem Schritt“, was im Spiel
wie eingefroren wirkt. „Fake it“: Rhythmus und Koordination nach Natur, Tempo nach Spielgefühl („schwer und stur“, aber nicht in Zeitlupe).

### a) Gangart und Beinfolge
- **Lateraler Viertakt mit diagonaler Kopplung:** Die Füße setzen in der Folge HL → VL → HR → VR auf. Das Vorderbein setzt **deutlich nach** dem gleichseitigen Hinterbein auf, sodass VL und HR fast als Diagonalpaar laufen.
  Vorschlag `order = { BL = 0.0, FL = 0.40, BR = 0.5, FR = 0.90 }` (Limb Phase ≈ 0,4). Zum Vergleich der Bär: FL 0,86, also lateral gekoppelt. **Das ist der Kernunterschied zum Bär.**
- **Hoher Duty Factor:** Walk **0,75–0,80**, also meist 3 Füße am Boden und kurze 2-Fuß-Phasen (Jayes & Alexander). Run **0,60–0,65**.
- **Fußbahn:** Der Fuß hebt **flach** (Hub ≈ 6–10 % der Beinhöhe), schwingt im **Bogen nach außen** (gespreizte Beine) und setzt mit den Krallen zuerst auf. Erst dann rollt die Sohle ab. Ein Schleifen an der Kralle ist kurz erlaubt.
- **Vorderbein:** Ein guter Teil des Schwungs kommt aus der **Drehung des Oberarms um die senkrechte Achse an der Schulter** (Schultergürtel-Drehung > 30 %). Der Oberarm schwenkt also vor und zurück, statt nur zu pendeln. Der Ellbogen bleibt außen.
- **Hinterbein:** Es schiebt wie ein stämmiger Stempel, das Knie zeigt nach außen und vorn.

### b) Frequenz und Schrittlänge
| Clip | Zyklus | Frequenz | Duty | Schrittlänge | Natur zum Vergleich |
|---|---|---|---|---|---|
| Walk | **40–44 Frames** | 0,7–0,75 Hz | 0,78 | 0,14–0,18 × Körperlänge | Riesenschildkröte ≈ 0,16 m/s, Pausen pro Schritt |
| Run („hastiger Trab“) | **24–26 Frames** | 1,2–1,25 Hz | 0,62 | 1,3 × Walk | Landschildkröten rennen nicht. Kurze, hastige Schübe gibt es bei Schnappschildkröten an Land. |

Run ist **kein Galopp** und hat keine Schwebe. Es ist derselbe diagonal gekoppelte Gang mit höherer Frequenz und tieferem Panzer.

### c) Panzer (Rumpf) und Körperhöhe
- **Der Panzer ist starr:** `spine(flex=0, side=0)` in allen Clips. Hips, Spine_1 und Chest bewegen sich als **ein Block**. Die Rumpfbewegung kommt nur über `body(...)`.
- **Heben pro Schritt:** ≈ **2–3 % der Körperhöhe**, zweimal pro Zyklus (bei jedem Diagonal-Aufsetzen). Zani: ≈ 2 cm bei ca. 50–60 cm Panzerhöhe, aktiv angehoben. Wichtiger als das Heben ist die Neigung:
- **Rollen ±2–4° und Gieren ±2–3° im Takt der Diagonalpaare.** Der Panzer „schaukelt“ von Seite zu Seite, das typische Schildkrötenbild. Dazu ein leichtes Nicken (±1–2°).
- Der Panzer sackt beim Aufsetzen kurz nach (2–3 Frames verzögert). Das macht das Gewicht spürbar, ohne dass es kantig wirkt.

### d) Kopf, Hals, Schwanz
- **Walk:** Der Kopf ist vorgestreckt und tief und wird **stabilisiert** (`neck_head(stabilize=…)`, Kopf ruhiger als der Panzer). Ein leichtes Vor- und Zurückschieben des Halses im Takt (±2–3 % Körperlänge) ist erlaubt. Ab und zu schaut der Kopf zur Seite, nur im Idle.
- **Hals:** Er ist im Modell kaum sichtbar (siehe 2). Bewegungen laufen daher **über Neck_1/Neck_2 als Vor/Zurück (Translation + Pitch)** und nicht über große Biegungen.
- **Schwanz:** Der Stachel ist starr in der Form und pendelt nur gering (±3–5°) verzögert seitlich mit. Er wird nicht angehoben.

### e) Drehen auf der Stelle
- Weil der Panzer starr ist, **dreht nur das Treten**: Die Beine der Außenseite treten nach vorn, die der Innenseite nach hinten, alle Füße schieben tangential. Der Takt bleibt diagonal gekoppelt.
- **Der Kopf führt:** Er giert zuerst 15–25° in die neue Richtung, 4–6 Frames bevor der Panzer folgt. Der Panzer rollt dabei leicht zur Außenseite.
- **Tempo:** ≈ **45–60 °/s** (≈ 30–40° pro Walk-Zyklus). Das ist träge, aber im ARPG noch reaktionsfähig. Zum Vergleich: Krabbe 26 °/s, Spinne 78 °/s erreicht.

### f) Angriffsmechanik (Schnappschildkröte)
- **Ready (Drohen, Loop):** **Hinterteil hoch** (der Panzer kippt 8–12° nach vorn, die Hinterbeine strecken sich, die Vorderbeine beugen sich), dazu **Kopf ein Stück zurück** (Telegraph), **Maul weit offen**, ein langsames Wiegen nach links und rechts. So steht es bei NC Wildlife. Aus der Kamera liest sich das als sichtbares Kippen des Panzers plus offener Rachen.
- **Attack1 = Schnappbiss (Root Motion):**
  1. Ausholen 8–10 Frames: Der Kopf zieht weiter zurück, der Panzer sinkt hinten etwas ein, die Hinterbeine spannen.
  2. **Zustoß 3–4 Frames:** Die **Hinterbeine schieben**, der ganze Körper rückt **0,10–0,15 Körperlängen vor**, der Panzer kippt vorn nach unten, und **Hals und Kopf schießen nach vorn-oben** (Neck-Translation 0,08–0,12 L). Das Maul ist dabei offen und **schlägt beim Treffer zu** (Event `hit`).
  3. Halten und Zerren 4–6 Frames: kurzes seitliches Reißen des Kopfes ±10°, der Panzer ruckt mit.
  4. Zurück 10–12 Frames, schwer und gedämpft.

  Gesamt ≈ 0,9 s. **Reichweite ½–⅔ Panzerlänge** wie in der Natur ist nur mit Hals **und** Körper-Ausfall erreichbar (der Hals fehlt, siehe 6).
- **Attack2 = Panzer-Rammstoß (Root Motion), Vorschlag:** Kopf einziehen, tief ducken, dann ein kurzer, schwerer Ausfall **0,2–0,3 Körperlängen**, bei dem der **vordere Panzerrand und die Stachelreihe** das Ziel treffen, mit Aufbäumen vorn um 10–15° (Treffer-Event). Danach rutscht er nach und die Beine stemmen sich. Vorbild ist der Kommentkampf männlicher Landschildkröten. Dauer ≈ 1,1 s. Siehe Frage 1.
- **Der ganze Körper arbeitet** (Lehre C3/C4): Kein Clip darf nur den Kopf bewegen.

### g) Was die schräge Top-down-Kamera davon sieht
- **Sehr gut sichtbar:** der **Panzer** als ca. 80 % der Silhouette mit der Stachelreihe, sein **Rollen, Gieren und Kippen**, der **Ausfall nach vorn** (Root Motion), der **Abstand Kopf ↔ Panzerrand** (Zustoßen/Einziehen) und die **Krallen**, die seitlich unter dem Panzer hervortreten.
- **Gut sichtbar, wenn übertrieben:** Hinterteil hoch im Ready (der Panzer kippt, die Rückseite hebt sich), offenes Maul (Rachen innen hell färben?) und das Kopf-Gieren beim Drehen.
- **Kaum sichtbar:** Beinfolge im Detail (die Beine sind großteils unter dem Panzer), Heben pro Schritt, Bauchpanzer, Augen.
- **Folge:** Den Gang über **Panzer-Schaukeln + Krallen-Rhythmus** lesbar machen, Angriffe über **Körper-Ausfall + Panzerkippen + Kopfweg**. Prüf-GIFs **zuerst aus der ARPG-Kamera** ansehen und für Angriffe **Kontaktbögen** verwenden.

---

## 5. Clip-Liste `Quadruped_Tortoise_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Quadruped_Tortoise_Idle` | ✓ | 3–4 s | Steht schwer, der Kopf schaut langsam nach links und rechts und zieht sich einmal kurz halb ein, der Panzer „atmet“ minimal, ein Bein wird nachgesetzt. |
| `Quadruped_Tortoise_Walk` | ✓ | ≈ 1,4 s | Diagonal gekoppelter Viertakt mit hohem Duty, flacher Fußbogen nach außen, der Panzer schaukelt (Rollen/Gieren), der Kopf bleibt ruhig vorgestreckt. |
| `Quadruped_Tortoise_Run` | ✓ | ≈ 0,8 s | Hastiger Trab ohne Schwebe, gleiche Kopplung, höhere Frequenz, Panzer tiefer und stärker schaukelnd, Kopf weiter vorgestreckt. |
| `Quadruped_Tortoise_TurnLeft` / `TurnRight` | ✓ | ≈ 1,4 s | Außenbeine treten vor, Innenbeine zurück, der Kopf giert voraus, der starre Panzer folgt mit leichtem Rollen (45–60 °/s). |
| `Quadruped_Tortoise_Ready` | ✓ | 1,5–2 s | Hinterteil hoch und Panzer nach vorn gekippt, Kopf zurückgezogen, Maul weit offen, langsames Wiegen (Schnappschildkröten-Drohen). |
| `Quadruped_Tortoise_Attack1` | – | ≈ 0,9 s | Schnappbiss: ausholen, mit Hinterbeinschub und Panzerkippen vorschnellen, Hals und Kopf nach vorn-oben, zuschnappen (Event `hit`), zerren, zurück. |
| `Quadruped_Tortoise_Attack2` | – | ≈ 1,1 s | Panzer-Rammstoß: Kopf einziehen, ducken, schwerer Ausfall mit dem vorderen Panzerrand und der Stachelreihe voran (Event `hit`), nachrutschen. |
| `Quadruped_Tortoise_Hit` | – | ≈ 0,35 s | Schreck-Reflex: Kopf und Beine zucken halb unter den Panzer, der Panzer sackt ab und kippt leicht zurück, dann zurück in die Ruhe. |
| `Quadruped_Tortoise_Death` | – | – | **Gesperrt** (Nutzer 2026-11-17). Nur Platzhalter aus dem Baukasten, nicht bearbeiten. (Info: „Auf den Rücken kippen“ wäre schildkrötentypisch, erst nach Freigabe.) |

---

## 6. Erwartete Rig-Hürden (aus `rigging/quadruped_rig.py` gelesen, nicht getestet)

1. **Der Panzer ist kein loses Teil.** Er gehört zum Hauptkörper, deshalb hilft `rigid_parts` (wirkt nur auf Nebenteile, Z. 426–437) nicht. Die Gewichte entstehen über 1/Abstand⁴ mit Masken, und folgende Knochen greifen in den Panzerrand:
   - **Bein/Schulter:** erlaubt bis Gelenkhöhe + `leg_top_margin` (0,14 bzw. hinten 0,22 H) im Bereich `leg_x_reach` (Z. 340–351). Der Panzerrand liegt genau dort auf Oberarm und Oberschenkel, also **wackelt der Rand bei jedem Schritt**.
   - **Hals:** erlaubt für x > Schulter + `neck_free_ahead` (Z. 358–363), also auch das **Nackenschild über dem Kopf**.
   - **Schwanz:** erlaubt für x < `x_tb` + 0,05 L (Z. 356–357), also auch der **hintere Panzerrand**.
   - `zone_lock` (b) sperrt nur den Rückenstreifen nahe der Mittellinie (35 % der halben Breite), nicht die Panzerflanken.

   → **Neue opt-in-Option nötig**, z. B. `rigid_shell = true` mit einer Panzer-Maske: alles oberhalb der Bauchlinie + Rand, außerhalb von `leg_capture` und hinter dem Kopfansatz, 100 % an Spine_1 (bzw. Hips/Spine_1/Chest, die im Clip ohnehin starr sind), mit 1–2 Übergangsringen an den Bein-, Hals- und Schwanzöffnungen (Vorbild: `rigid_head_blend_rings`, Z. 532–554). Standard aus, Regression für Wolf, Hirsch, Echse und Bär.
2. **`rigid_head_above` NICHT einschalten.** Diese Option bindet alles über der Kopf-Oberkante vor der Schulter starr an den Kopf (Z. 502–529). Bei der Shellback sind das **die vorderen Panzerplatten und Stacheln**, der Panzer würde mit dem Kopf nicken. Vorher in den Renders klären, welche Platte zum Kopf gehört und welche zum Panzer.
3. **Sehr kurzer, verdeckter Hals.** `x_hb = Nase − 0,42 · (Nase − x_sh)` (Z. 225). Die Vorderbeine stehen weit vorn (Füße x = +0,33 bei Nase ≈ +0,5), sodass Neck_1/Neck_2 nur wenige Zentimeter lang werden und unter dem Nackenschild liegen. Der Mesh hat **keine Hautreserve** zum Ausfahren, das Zustoßen dehnt also die Halsöffnung. Gemäß B1 nicht durch kleinere Bewegung lösen, sondern über (a) den Körper-Ausfall als Hauptweg, (b) `joint_densify` (C9) an der Halsöffnung und (c) die Prüfung, ob die Dehnung unter dem Nackenschild aus der Kamera verdeckt ist. **Kopf einziehen** heißt, dass der Kopf in den geschlossenen Panzer-Mesh eintaucht (Durchdringung, von oben verdeckt) → Frage 3.
4. **Gespreizte Beine:** `bend()` (Z. 164–176) sucht Knie und Ellbogen nur als Ausbiegung in **X**. Schildkröten-Gelenke biegen **seitlich (Y)**, deshalb greifen vermutlich die Standardanteile (`front_elbow` 0,85, `back_knee` 0,75 usw.). Das muss in `rig_debug.png` geprüft werden. Bei falscher Lage pro Kreatur die Anteile setzen oder `bend` als opt-in um Y erweitern. Die stämmigen Beine können breiter sein als `leg_radius` = 0,12 H, dann wandert die Bein-Spur. Ggf. per `[quadruped.detect]` erhöhen.
5. **Schulter-/Hüftgelenk im Panzer:** `joint_depth` 0,35 und `scapula_height` 0,8 beziehen sich auf die Rückenhöhe, und das ist hier die hohe Panzerkuppel. Das Schulterblatt liegt damit tief im Panzer. Das ist unkritisch, **solange die Panzer-Maske (1) Schulterblatt-Gewichte auf dem Panzer verhindert**. Für die Schultergürtel-Drehung (4a) reicht eine Drehung von `Leg_F*_1` um die Senkrechte, die Steifigkeit des Schulterblatts kann hoch bleiben.
6. **Schwanz:** `center_at` mittelt Querschnitte über alle Vertices bei x (Z. 207–215). Am Schwanzansatz liegt der hintere Panzerrand im selben Schnitt, deshalb wird die **Schwanzlinie nach oben gezogen**. Ggf. `tail_base` größer wählen (Bär 0,6) oder die Schnitte auf Höhen unter der Panzerkante begrenzen (opt-in).
7. **Wenig Hubreserve für Ready/Attack:** `reach_fix` senkt den Rumpf, wenn ein Bein überstreckt wäre. Die Beine sind kurz, aber in Ruhe gebeugt. Das Hinterteil-Heben um 8–12° muss gegen `chain_len` getestet werden. Ist zu wenig Reserve da: Ursache am Rig (Gelenkpositionen) suchen, nicht den Winkel kleiner machen.
8. **Füße weit vorn, nahe am Kopf:** Die Head-Maske ist x > `x_hb` − 0,1 · (…) (Z. 355). Die Vorderkrallen liegen nahe dieser Grenze. Unterhalb der Bauchlinie zählen zwar nur Bein-Knochen (Z. 366–369), trotzdem soll der Bau-Agent prüfen, dass keine Kralle am Kopf hängt.
9. Vermutlich **nicht** nötig: `cut_leg_bridges` (die Beine sind frei) und `narrow_hind_legs` (1,02×). `zone_lock` (a) gegen Zug des Unterbeins an der Flanke ist sinnvoll.

**Empfehlung zum Ablauf:** zuerst `creature_pipeline.py creatures/11_shellback --stage check` mit `rig_debug.png` und der Gewichts-Sichtprüfung des Panzerrands, dann `rigid_shell` bauen, dann `--stage motion` mit Walk + Attack1 als Roh-GIFs (README „Zusammenarbeit“ Schritt 1).

---

## 7. Offene Fragen an den Nutzer
1. **Attack2:** Ein **Panzer-Rammstoß** (Kopf eingezogen, Stachelpanzer voran, Vorbild Kommentkampf; **Empfehlung**, nutzt die stärkste Silhouette) oder ein zweiter Biss, etwa ein Doppelbiss bzw. Festbeißen und Zerren?
2. **Tempo:** Deutlich lebhafter als echte Schildkröten (Walk ≈ 0,7 Hz, Run als hastiger Trab ≈ 1,2 Hz) fürs Spielgefühl (**Empfehlung**), oder bewusst sehr träge wie eine Riesenschildkröte (≈ 0,3–0,4 Hz)?
3. **Kopf einziehen:** Der Mesh hat keinen Hohlraum, beim Einziehen taucht der Kopf also in den Panzer ein (aus der Spielkamera verdeckt). Ist das als „Fake it“ in Ordnung (**Empfehlung**: nur halb einziehen, in Hit, Idle und Attack2)? Oder soll der Kopf nie hinter den Panzerrand?
