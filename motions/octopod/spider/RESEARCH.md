# Recherche Bewegungsmuster octopod/spider (Stand 2026-11-20)

Vorarbeit für den Bau-Agenten der Spinne (erste Kreatur: `creatures/10_broodling/`). Noch kein Code, keine `style.toml`.
**Hinweis zur Quelle:** Der Recherche-Agent kann keine Videos ansehen. Alle Aussagen stützen sich auf Fachartikel,
Abstracts, Video-Beschreibungen und Fotos. Der Bau-Agent bzw. der Nutzer sollte die Videos unten **selbst ansehen**
und die Werte dagegen prüfen (CLAUDE.md „Naturbeobachtung zuerst“).

---

## 1. Warum der Neustart?

| Was | Fundstelle |
|---|---|
| Bis 2026-11-17 war die Spinne nur eine **Variante `spider` von hexapod/ant** (8 Laufbeine → alternierender Vierfuß aus derselben Gruppenregel, Taster weg). Startwerte damals: `cycle_frames 18, stride 0.13, lift_deg 13, abdomen_sway_deg 2`. | `motions/hexapod/ant/style.toml` Z. 119–121, `motions/README.md` Z. 20, `docs/archiv/ROADMAP_20_KREATUREN.md` Z. 16/56 |
| Nutzer: **„6- und 8-Beiner trennen“** und **„Ein Baukasten pro Beinart“** → Spinne gehört zu `octopod`, eigenes Muster. | BACKLOG A2, A3; CLAUDE.md „Fake it…“ (Hinweis zur Trennung hexapod/octopod) |
| Der erste Spinnen-Agent (18.11.) ging beim Kontext-Reset verloren: **„Spinnen-Agent ohne Spuren“**, „Spinne danach neu ansetzen“. Es gibt keinen Code, keinen Ordner, keine GIFs. | BACKLOG G6; HANDOVER Z. 47 („alter Agent ohne Spuren“) |
| Veraltet: HANDOVER Z. 77 nennt bei octopod noch „spider (Agent läuft)“. | HANDOVER Z. 77 (für den Doku-Agenten) |
| Es gab **nie eine Naturbeobachtung** für die Spinne. Beim Chitin Crawler hieß es schon: „Dafür bräuchten wir ein Spinnen-Video als Referenz.“ | `creatures/01_chitin_crawler/README.md` Z. 36 |

**Direkte Nutzerkritik an einer Spinnen-Animation gibt es nicht**, weil nie eine abgenommen wurde. Für den Neubau gelten die
allgemeinen Lehren aus Testlauf 1, die bei Krabblern bereits aufgefallen sind:
- **Ganzkörper statt Einzelteil:** Turn darf kein gedrehter Walk sein, Ready kein verschobenes Modell. Bei der Spinne heißt das: Vorderkörper (Prosoma) führt, Hinterleib samt Eierhaufen zieht verzögert nach (BACKLOG C4, CLAUDE.md).
- **Nicht roboterhaft/kantig** (C1, B3). Maßstab ist die **Needle Wasp** (B4).
- **Angriffe aus dem ganzen Körper:** Beim Skorpion arbeitete nur ein Gelenk (C3), bei der Kobra nur Kopf und Hals.
- **Lesbarkeit hängt am Modell:** Crab wurde auf dem Ameisenkörper validiert. Dort erlaubten die fast gestreckten Beine kaum Körperhub (`motions/octopod/crab/README.md` „Erkenntnisse“). Der Broodling hat echte, gebeugte Spinnenbeine, also ist Aufbäumen möglich.
- **Dehnung nicht durch kleinere Bewegung lösen**, Roh-Animation mitspeichern, **Death nicht anfassen** (gesperrt).

### Technische Stolpersteine vor dem Bau (nur gelesen, nicht getestet)
- **Mesh-Inseln:** `rigging/octopod_detect.py` erwartet laut Docstring ein Mesh „aus vielen Einzelteilen (Inseln)“. Füße sind dort „Inseln mit Bodenkontakt, nicht Rumpf“. Laut `review/model_check.json` hat der Broodling aber **1 zusammenhängendes Teil** (gezählt vom Prüfskript, ggf. nach dem Verschweißen). Falls die Erkennung tatsächlich nur eine Insel sieht, findet sie keine Beine. **Zuerst `--stage check` laufen lassen.** Falls nötig, eine Ein-Mesh-Erkennung **innerhalb von octopod** bauen. Vorbild ist der Ansatz von `multileg_rig.py` (Dijkstra über Mesh-Kanten), aber als eigene Kopie, ohne Abhängigkeit (Regel „kein Skelett hängt am Baukasten eines anderen“). Crab bzw. Chitin Crawler danach per Regression unverändert.
- **Vorderes Beinpaar angehoben:** 6 statt 8 Bodenkontakte (freigegeben, „spinnentypisch“). Das deckt sich mit echten Spinnen: Bein I tastet oft vor (siehe 3a).
- **Eierhaufen auf dem Rücken:** große, unregelmäßige Masse (14 % ohne Spiegelpartner). Sie bestimmt die Silhouette von oben und muss starr am Hinterleib hängen, mit Nachziehen.
- Kennzahlen Modell: 4.218 Tris, 1 Material, Größe normiert (0,88 × 1,0 × 0,71).

---

## 2. Naturreferenzen

### Videos (vom Bau-Agenten bzw. Nutzer anzusehen)
| Thema | Link | Was man laut Beschreibung sieht |
|---|---|---|
| Laufen, Zeitlupe | [Spider running in slow motion (1000 fps)](https://www.youtube.com/watch?v=7CxOPakRsSU) | „moves 4 legs at a time“, also alternierender Vierfuß |
| Drohgebärde Vogelspinne | [Tarantula attack & threat pose – Phormictopus auratus](https://www.youtube.com/watch?v=6yoK5OB-Nyg) · [Tarantula Threat Posture](https://www.youtube.com/watch?v=XZ4H7vjFf-E) | Aufbäumen, Vorderbeine hoch, Fänge zeigen, Zuschlagen |
| Beuteangriff Vogelspinne, Zeitlupe | [Tarantulas: speed attack (slow motion)](https://www.youtube.com/watch?v=jn2Cfow4nwE) | Nhandu/Brachypelma stürzen sich auf Beute |
| Beuteangriff Wolfsspinne | [Wolf Spider Attacks Fly in Slow Motion](https://www.youtube.com/watch?v=6kW31h1wNUw) | Ansprung und Biss auf eine Fliege |
| Sprungangriff | [Jumping spider „Kim“, Univ. Manchester](https://www.youtube.com/watch?v=C6PAClh1IZo) | Springspinne, Hochgeschwindigkeit, Absprung und Landung |
| Wenden zur Beute | [Flattie spider – world's fastest spin (NatGeo)](https://www.youtube.com/watch?v=HKRL6Y7Oyvw) | Drehung um ein verankertes Bein, Beine angezogen |

### Fachliteratur (gelesen: Abstracts, Tabellen bzw. Volltext wie angegeben)
- **Spagna, Valdivia & Mohan 2011**, *J. Arachnology* 39:84–91: Gangart schneller Trichterspinnen (Hololena). Volltext gelesen: [PDF (archive.org)](https://archive.org/download/biostor-217406/biostor-217406.pdf)
- **Silva-Pereyra et al. 2019**, *PeerJ* 7:e7748: Vogelspinne *Eupalaestrus weijenberghi*, Gehen. Tabellen gelesen: [Artikel](https://peerj.com/articles/7748)
- **Kelsey & Ashley-Ross (SICB, ~2010)**: 3D-Kinematik des Beutefangs bei 5 Vogelspinnen-Arten mit 500 fps. Abstract: [sicb.org](https://sicb.org/?p=25858)
- **Crews et al. 2018**, *J. Exp. Biol.*: Flattie-Spinne (Selenopidae), Drehangriff. Zusammenfassung: [National Geographic](https://www.nationalgeographic.com/animals/article/spinning-selenopidae-spider-hunts-prey-spd)
- **Nabawy et al. 2018**, *Sci. Rep.*: Sprünge von *Phidippus regius*. [PMC5940701](https://pmc.ncbi.nlm.nih.gov/articles/PMC5940701) · [ScienceDaily](https://sciencedaily.com/releases/2018/05/180508081459.htm)
- **Wilson 1967**, *J. Exp. Biol.* 47:133: Schrittmuster bei Vogelspinnen, nur Abstract: [scilit](https://scilit.com/publications/abc3309cfc4f65081183f2826379248e)
- **Ward & Humphreys 1981**, *J. Exp. Biol.*: Wolfsspinnen *Lycosa tarentula* und *Trochosa*. Nicht abrufbar (403), nur aus Zitaten: [PDF](https://library.museum.wa.gov.au/internaldocs/49467/WardHumphreys1981SpiderLocoJexpBiol.pdf)
- **Tod/Einkrümmen (nur Info, Death gesperrt):** Spinnen strecken ihre Beine hydraulisch mit Blutdruck und beugen sie mit Muskeln. Nach dem Tod fällt der Druck weg und die Beuger ziehen die Beine ein. [Mental Floss](https://www.mentalfloss.com/animals/invertebrates/why-spider-legs-curl-up-when-they-die) · [IFLScience](https://www.iflscience.com/plants-and-animals/why-do-spiders-curl-when-they-die/)

### Kernaussagen der Quellen
1. **Alternierender Vierfuß (Tetrapod-Gang):** Bein L1, R2, L3 und R4 gegen R1, L2, R3 und L4 (Spagna 2011). Gegenüberliegende und benachbarte Beine laufen im Gegentakt (Wilson 1967).
2. **Die vier Beine einer Gruppe setzen nicht exakt gleichzeitig auf.** Der Gleichlauf-Index liegt nur bei 0,30 (Hololena), und das gleichseitige Nachbarbein setzt bei **≈ 40 %** statt bei 50 % des Zyklus auf (Spagna 2011). Bei Vogelspinnen und großen Spinnen ist der Gang locker, die Phasen streuen stark (Wilson 1967; Ward & Humphreys 1981 zu *Lycosa*).
3. **Vogelspinne beim Gehen** (Silva-Pereyra 2019): **Schrittfrequenz 0,6–0,75 Hz**, **Duty Factor 0,58–0,61** (Anteil am Boden), Tempo ≈ 1 Körperlänge/s. Schneller wird sie vor allem über die **Frequenz**, die Schrittlänge bleibt fast gleich. **Vorderes „Vierbeiner-Paar“ (Bein I+II) lenkt, hinteres (III+IV) trägt das meiste Gewicht.** Die Energierückgewinnung liegt bei nur 2–10 %, der Körper wippt also nicht wie ein Pendel oder eine Feder.
4. **Schnelle Spinne** (Hololena): Duty Factor beim Rennen **0,53–0,58**. Ab etwa 54 Körperlängen/s kommen kurze Flugphasen dazu. Bein IV schleift teils nur nach („shuffle“). Tempo steigt mit Frequenz *und* Schrittlänge.
5. **Beutefang Vogelspinne:** 250–300 ms von der ersten Beinbewegung bis die Beute am Mund ist (kleine Tiere < 100 ms). Meist **geradeaus nach vorn**, kleine Tiere drehen auch 180° vor dem Zugriff (Kelsey & Ashley-Ross).
6. **Drohgebärde Vogelspinne:** Sie bäumt sich auf den Hinterbeinen auf, **Bein I+II (und Taster) gehen hoch und auseinander**, die Fänge werden gezeigt. Das ist die letzte Warnung vor dem Biss. Eine schwache Form mit nur leicht gehobenen Vorderbeinen zeigt Unruhe. ([YPTE](https://ypte.org.uk/factsheets/tarantulas/defences), [TPWD-Broschüre](https://texashistory.unt.edu/ark:/67531/metapth661996/m2/1/high_res_d/TXPUB_00235.pdf))
7. **Wenden (Flattie):** Das Bein, das der Beute am nächsten ist, wird verankert und dient als Drehpunkt. Die übrigen Beine werden angezogen, das macht die Drehung ≈ 40 % schneller (Pirouette). Mit dem Mund voran stößt die Spinne gleichzeitig vor.
8. **Sprung (Springspinne):** Bis zu 4–6 Körperlängen weit. Kurze Sprünge laufen **flach** (kurze Flugzeit), weite steiler. Die Absprungkraft beträgt bis zu 5× das Körpergewicht. Abgestoßen wird nach allgemeiner Fachkenntnis (Parry & Brown 1959, nicht selbst geprüft) vor allem mit **Bein III/IV**, Bein I/II zeigen nach vorn.
9. **Fänge:** Vogelspinnen (Mygalomorphae) stechen mit den Fängen **parallel nach unten** („orthognath“), Wolfsspinnen klappen sie **zangenartig zueinander**. Das ist Lehrbuchwissen, nicht aus den Links oben.

---

## 3. Bewegungsregeln für das Muster (Vorschlag für die `style.toml`)

Alle Zeitwerte bei 30 fps. **Echte Spinnen sind hier nur Richtwert.** Ein Monster in Spielgröße muss lebendiger wirken als eine
ruhige Vogelspinne (0,7 Hz wäre träge). „Fake it“: Rhythmus und Koordination nach Natur, Tempo nach Spielgefühl.

### a) Beinreihenfolge
- **Gruppe A** = L1, R2, L3, R4 · **Gruppe B** = R1, L2, R3, L4 · Versatz zwischen den Gruppen **0,5 Zyklus**.
- **Welle innerhalb der Gruppe** (nicht roboterhaft synchron!): von hinten nach vorn je **+0,03 bis 0,05 Zyklus pro Beinpaar** (Bein 4 zuerst, Bein 1 zuletzt). So setzt das gleichseitige Nachbarbein bei ≈ 0,45 auf, nahe am gemessenen Wert von 40 %. Als Slider `ripple`.
- Häufig zitierte Reihenfolge einer Seite: **4-2-3-1** (Foelix, *Biology of Spiders*, nicht selbst geprüft). Sie folgt automatisch aus Gruppen + Welle.
- **Bein I (Broodling: im Modell angehoben):** läuft im Takt mit, aber **leichter**. Es greift weit nach vorn, tippt nur kurz auf (eigener, kürzerer Duty-Wert, z. B. 0,35) und schwebt im Schwung höher. Bein I tastet und lenkt, Bein III/IV tragen und schieben. Kleines Zittern bzw. Tasten von Bein I auch im Stand.

### b) Schrittfrequenz und Schrittlänge
| Clip | Zyklus | Frequenz | Duty | Schrittlänge | Natur zum Vergleich |
|---|---|---|---|---|---|
| Walk | **20–24 Frames** | 1,25–1,5 Hz | **0,60** | 0,12–0,15 × Körpergröße | Vogelspinne 0,7 Hz / Duty 0,6 |
| Run | **10–12 Frames** | 2,5–3 Hz | **0,50–0,53** | 1,4–1,6 × Walk | Hololena Duty 0,53–0,58; bei kleinen Spinnen um 20 Hz |

Schneller wird die Spinne vor allem über die **Frequenz** (Vogelspinne), beim Rennen zusätzlich über die Schrittlänge. Eine Flugphase braucht es nicht.
Alter Startwert der Ant-Variante zum Vergleich: 18 Frames, Schritt 0,13, Hub 13°.

### c) Körperhöhe und Wippen
- **Kaum senkrechtes Wippen:** höchstens ≈ 1 % der Höhe. Bei 2–10 % Energierückgewinnung federt nichts (Silva-Pereyra 2019). Aus der Draufsicht sieht man das ohnehin kaum.
- **Körperhöhe:** Walk = Ruhehöhe. **Run ≈ 10–15 % tiefer und flacher**: Die Beine spreizen weiter, das „Hinhuschen“ ist typisch für Wolfsspinnen.
- **Was man sieht, kommt von den Seiten:** leichtes Gieren des Vorderkörpers ±2–3° im Takt der Gruppen. Der **Hinterleib samt Eierhaufen zieht 2–4 Frames verzögert nach** (seitlich 2–4°, im Run etwas mehr) = Follow-Through, Ganzkörper.
- **Kniegelenke** stehen deutlich über dem Körper, die Spinnen-Silhouette lebt davon. Beim Schwung hebt das Knie, der Fuß folgt im Bogen. Die Füße schleifen nicht (Ausnahme: Bein IV im Run darf kurz nachschleifen).

### d) Drehen auf der Stelle
- Der Rhythmus des Vierfuß-Gangs bleibt. **Die Beine der Außenseite treten nach vorn, die der Innenseite nach hinten**, alle Füße schieben tangential um die Körpermitte. Fuß-IK aus dem Baukasten hält die Standbeine fest.
- **Prosoma führt, Hinterleib hängt 3–5° nach** (biegt sich am Stiel mit in die Kurve). Das ist kein starr gedrehter Walk (Lehre C4).
- **Tempo:** ≈ **90–120 °/s**, also 45° pro Walk-Zyklus. Die Krabbe dreht mit 26 °/s; das ist für eine Jägerin im ARPG zu träge.
- Optional als Kür: **Ruck-Drehung zum Ziel** wie bei der Flattie. Ein Bein bleibt verankert, die anderen ziehen an, 90° in ≈ 6–8 Frames. Das kann Teil von Attack1 sein, wenn das Ziel seitlich steht.

### e) Angriffsmechanik
- **Ready (Drohen, Loop):** Rumpf vorn **25–40° hoch** auf Bein III/IV. Diese spreizen sich weiter nach hinten und außen, die Füße stehen per IK. **Bein I+II gehen hoch und weit nach außen** gespreizt, die Taster heben sich, die Fänge klappen auf. Der Hinterleib dreht gegen und bleibt tief. Dazu leichtes Zittern bzw. Wiegen. Das Crab-Prinzip „Kippen um die Hüftlinie der tragenden Beine“ (`rear_up`, `max_rear_pitch`) passt, aber hier ist der Winkel **groß** (gebeugte Spinnenbeine erlauben es).
- **Attack1 = Ausfall-Biss (Lunge), Root Motion:**
  1. Ausholen 8–10 Frames: aus Ready noch etwas zurück und tiefer über Bein III/IV (Telegraph).
  2. **Zustoß 3–4 Frames:** Der Körper schnellt **0,2–0,3 Körperlängen vor** und kippt nach vorn-unten. Bein I+II schlagen **von oben auf das Ziel und schließen sich wie ein Käfig**. Die Fänge stechen **nach unten** (Vogelspinnen-Art). Treffer-Event beim Aufsetzen.
  3. Festhalten 4–6 Frames mit kleinem Ruck bzw. Schütteln.
  4. Zurück 8–10 Frames.

  Gesamt ≈ 0,8 s. Der Zugriff selbst passt zum gemessenen 250–300-ms-Fenster.
- **Attack2 = Sprungbiss (Pounce, Vorbild im Roster: Springspinne), Root Motion:** In die Hocke (Bein III/IV beugen, Körper 20–30 % tiefer, 8–10 Frames). Dann **flacher** Sprung über 2–4 Körperlängen, Scheitel ≈ 0,3 Körperlängen. Bein I+II zeigen nach vorn-oben, III/IV sind nach hinten gestreckt. Landung auf Bein I/II, abfedern, Biss mit Treffer-Event bei der Landung. Gesamt ≈ 1,0 s.
- **Der ganze Körper arbeitet** (Lehre C3): Kein Clip, in dem sich nur der Kopf bzw. die Fänge bewegen. Die Fänge sind aus der Spielkamera fast unsichtbar (siehe g).

### f) Unterschied zum Crab-Muster
| | Crab (`octopod/crab`) | Spider (`octopod/spider`) |
|---|---|---|
| Laufrichtung | seitwärts, `move_axis: y` | **vorwärts** (Kopf voran) |
| Schrittfolge | führende 2-4-3-5 / nachziehende 2-5-3-4 | **zwei Vierergruppen im Gegentakt** + Welle hinten → vorn, beide Seiten gleich |
| Bein I | Scheren, beim Laufen vom Boden (`feeler_slots`) | **Laufbein mit Tast-Rolle**: läuft mit, kurzer Bodenkontakt |
| Duty | 0,62 | Walk 0,60 · Run 0,50–0,53 |
| Körper | flach, kein Rollen | flach, aber **Hinterleib zieht nach** (Stiel/Pedicel) |
| Drohen | Scheren hoch und gespreizt, Körper wenig gehoben | **steiles Aufbäumen** 25–40°, Bein I+II hoch, Fänge auf |
| Angriff | Scheren-Schnapp aus der Drohhaltung (1–2 Frames) | **Ausfall nach vorn + Beinkäfig + Biss nach unten**, zweiter Angriff = **Sprung** |
| Drehen | 26 °/s, gleicher Gang | 90–120 °/s, Außenbeine vor, Innenbeine zurück, Hinterleib zieht nach |

Gemeinsam nutzbar aus `octopod_kit.py`: Fuß-IK (`set_foot`), Körper heben mit stehenden Füßen, Bodenbegrenzung, Backen + Selbstprüfung.
Ebenfalls übertragbar ist das Kippen ums tragende Paar aus `crab_clips.py` (`rear_up`), aber **kopiert** in `spider_clips.py`, nicht importiert (eigener Clip-Code pro Muster).

### g) Was die schräge Top-down-Kamera davon sieht
- **Sehr gut sichtbar:** der **Beinkranz** (8 Beine strahlenförmig, die Knie ragen hoch, die Silhouette ist sofort „Spinne“), das **Flackern der zwei Vierergruppen**, der **Eierhaufen** als hellste Form, das Nachziehen bzw. Pendeln des Hinterleibs und die Gierbewegung beim Drehen.
- **Gut sichtbar, wenn übertrieben:** Aufbäumen. Von oben verkürzt sich ein Kippwinkel, darum Bein I+II **weit seitlich spreizen** (nicht nur nach oben), damit die Silhouette breiter wird. Ausfall nach vorn (Root Motion) und der Beinkäfig beim Zugriff.
- **Kaum sichtbar:** Fänge, Taster, Augen (der Kopf ist klein und vorn eingezogen), senkrechtes Wippen, Bauchseite, Fußdetails.
- **Folge:** Angriffe über **Körperweg + Vorderbeine** lesbar machen, nicht über die Fänge. Prüf-GIFs **zuerst aus der Spielkamera-Perspektive** ansehen (Regel aus C15).

### Tod (nur Info, Death bleibt gesperrt)
Beine krümmen sich **unter dem Körper ein** (Beuger ohne Hydraulik-Gegendruck). Weil Rumpf und Hinterleib schwerer sind als die Beine,
landen tote Spinnen oft auf dem Rücken. Das passt zum vorhandenen `death_flip` mit Einrollen, aber erst nach Freigabe durch den Nutzer.

---

## 4. Vorschlag Clip-Liste `Octopod_Spider_*`

| Clip | Loop | Dauer | Inhalt (1 Satz) |
|---|---|---|---|
| `Octopod_Spider_Idle` | ✓ | 2–3 s | Fast reglos lauern wie eine echte Jägerin: Bein I tastet bzw. tippt kurz, Taster zucken, einmal pro Loop wird ein Bein nachgesetzt, der Hinterleib „atmet“ minimal. |
| `Octopod_Spider_Walk` | ✓ | 0,7–0,8 s | Alternierender Vierfuß mit Welle hinten → vorn, Bein I tastend, Hinterleib samt Eierhaufen pendelt verzögert nach. |
| `Octopod_Spider_Run` | ✓ | 0,35–0,4 s | Gleiche Gruppen, höhere Frequenz und längere Schritte, Körper tiefer und flacher, Hinterleib zieht deutlicher nach. |
| `Octopod_Spider_TurnLeft` / `TurnRight` | ✓ | ≈ 0,75 s | Auf der Stelle: Außenbeine treten vor, Innenbeine zurück, der Vorderkörper führt die Drehung, der Hinterleib biegt sich nach (90–120 °/s). |
| `Octopod_Spider_Ready` | ✓ | 1–1,5 s | Drohgebärde: steil aufgebäumt auf Bein III/IV, Bein I+II hoch und weit gespreizt, Fänge offen, leichtes Zittern. |
| `Octopod_Spider_Attack1` | – | ≈ 0,8 s | Ausfall-Biss mit Root Motion: ausholen, nach vorn schnellen, Bein I+II schließen als Käfig über dem Ziel, Biss nach unten (Event `hit`), zurück. |
| `Octopod_Spider_Attack2` | – | ≈ 1,0 s | Sprungbiss mit Root Motion: Hocke, flacher Satz über 2–4 Körperlängen mit vorgestreckten Vorderbeinen, Landung und Biss (Event `hit`). |
| `Octopod_Spider_Hit` | – | ≈ 0,3 s | Zusammenzucken: Beine kurz angezogen, Körper sackt ab, Hinterleib ruckt nach, dann zurück in die Ruhe. |
| `Octopod_Spider_Death` | – | – | **Gesperrt** (Nutzer 2026-11-17). Nur Platzhalter aus dem Baukasten, nicht bearbeiten. |

Später möglich (Varianten laut `docs/recherche/RECHERCHE_MONSTERARTEN.md`, **nicht vorziehen**): `brood` (Jungspinnen abwerfen = Spawn-Event),
`web` (Netz-Projektil), `spitter` (Giftspucke).

## 5. Offene Fragen an den Nutzer
1. **Vorderes Beinpaar des Broodlings** (im Modell angehoben): soll es im Gang **mitlaufen und kurz aufsetzen** (Empfehlung, wirkt wie eine echte Spinne) oder dauerhaft **als Tastbeine in der Luft** bleiben (dann läuft sie auf 6 Beinen)?
2. **Attack2 Sprungbiss** gleich mitbauen? Das Roster nennt „Springspinne – Sprungbiss“ als Vorbild. Empfehlung: ja.
3. **Tempo:** lebhafter als echte Vogelspinnen (Walk ≈ 1,3 Hz statt 0,7 Hz) für Spielgefühl. Einverstanden, oder eher die träge, lauernde Vogelspinne?
