# Backlog – alle Anweisungen und Meldungen des Nutzers

Stand: 2026-11-17 abends. **Hauptliste**: Jede neue Meldung des Nutzers kommt hier hinein. Claude im Hauptchat = **Orchestrator + Prüfer**
(siehe `../CLAUDE.md`): verteilt die Arbeit an Subagenten (getrennte Dateien), prüft jedes Ergebnis selbst und zeigt es dem Nutzer.

Status: ✅ erledigt · 🔄 Subagent arbeitet · ⏭ als Nächstes · ⏸ zurückgestellt (Nutzer) · ❓ Frage an den Nutzer

## A. Architektur & Zusammenarbeit

| # | Meldung / Anweisung des Nutzers | Status | Ergebnis |
|---|---|---|---|
| A1 | Eine Pipeline für alles ist kaputte Architektur – Änderungen an der Schildkröte haben den fertigen Wolf kaputt gemacht. Gemeinsame Teile ja, aber gekapselt. | ✅ | Sperre fertiger Kreaturen (`approve.py`), Regressionstest per Fingerabdruck (`regression.py`), eigener Clip-Code pro Muster. Antwort des Nutzers zum Wolf: Kaputt war die Bewegung selbst – wegen „zerrissener Kanten/Hautdehnung“ wurden Werte runtergedreht, **der Run sieht jetzt aus wie das Hoppeln eines Häschens** → C1. |
| A2 | Ein Baukasten pro Beinart (2, 4, 6, 8); Humanoid, beinlos, Tausendfüßer, Tentakel je eigene Instanz. Kein Universal-Baukasten. | ✅ | biped / quadruped / hexapod / octopod / multileg / legless / floater / flyer – je eigenes Rig + Baukasten. |
| A3 | 6- und 8-Beiner trennen. | ✅ | hexapod (Ameise), octopod (Krabbe, Spinne). |
| A4 | Roh-Animation immer mitspeichern (mit Dehnungen/Rissen). Original vom Wolf ansehen? | ✅ / ❌ | `--stage motion` → `rig/anim/raw/`. Das damalige Wolf-Original wurde nie gespeichert, ist also nicht wiederherstellbar. |
| A5 | Pipeline + Zusammenarbeit so aufstellen, dass kein Aufwand in Animationen fließt, die man wegwirft. | ✅ | README „Zusammenarbeit“. |
| A6 | „Eine Pipeline für alle“ erklären. | ✅ | Nur die Ablaufsteuerung ist gemeinsam. |
| A7 | Arbeit über Subagenten; Claude = Orchestrator und Prüfer. | ✅ | `../CLAUDE.md` |
| A8 | Nicht panisch fixen, gründlich arbeiten, alle Befehle aufnehmen; Claude setzt um (über Subagenten), möglichst heute noch. | ✅ | Diese Datei + `../CLAUDE.md` |
| A9 | Viele Bugs kommen schon aus dem Modell und eigentlich schon aus der ChatGPT-Bildvorlage – die muss Claude viel gründlicher prüfen; in die bestehende Vorgehensweise aufnehmen. | ✅ | Pflichtprüfung mit Checkliste (Bild vor Tripo, Modell vor Rig) in `README.md`, `HANDOVER.md`, `../CLAUDE.md`. 🔄 Agent Prüfskript `scripts/model_check.py` (Nutzer: Skript ist nur Frühwarnsystem – **individuelle Sichtprüfung durch den Agenten bleibt IMMER Pflicht**, muss im Skript deutlich stehen). |

## B. Grundsätze für Animation

| # | Meldung | Status |
|---|---|---|
| B1 | Dehnung nicht durch kleinere/verbogene Bewegung „lösen“, sondern am Mesh (mehr Vertices am Gelenk, mehrteiliges Mesh). | ✅ Regel, Dehnung ist nur Info · Mesh-Lösung → C9 |
| B2 | Zu zahlenbasiert, einige Animationen völlig unrealistisch. | Regel; Fälle in C |
| B3 | Animationen „schnell schnell“, viele roboterhaft. | → C1, C2 |
| B4 | Gutes Beispiel: **Needle Wasp**. | Maßstab |

## C. Korrekturen

| # | Meldung des Nutzers | Spezifikation (Kurzform) | Status |
|---|---|---|---|
| C1 | Wolf „wie ein Roboter-Wolf, kantig, abrupt, keine eleganten weichen Bewegungen“. **Run hoppelt wie ein Häschen**, weil wegen Dehnung Werte reduziert wurden. (Alt: Echse Ready/Attack zu dezent.) | Fußgeschwindigkeit ohne Ruck, Follow-Through entlang Kopf/Hals/Rücken/Schwanz, natürliche Ausschläge nach Video. Wolf, Echse, Hirsch. Dateien `motions/quadruped/*`. | 🔄 Agent Vierbeiner |
| C2 | (folgt aus B3) | Raptor-Baukasten ist eine Kopie des Vierbeiner-Baukastens → dieselben Probleme prüfen/beheben, Ganzkörper bei Ready/Attack; dazu C8 (Raptor). | 🔄 Agent Raptor |
| C3 | Skorpion-Stich: nur das Hauptgelenk wölbt sich, der Skorpion sticht sich selbst. Schwanz gerade ausfahren, Stachel frontal auf den Gegner. | Ganze Schwanzkette, Stachelspitze zielt auf einen Punkt vor dem Skorpion; Körper arbeitet mit. Andere Clips auf dasselbe prüfen. | 🔄 Agent Skorpion |
| C4 | Eel Stalker: Attack nur Hals+Kopf, Rest starr · Walk Kopf starr · Ready alles starr, nur verschoben/rotiert · Turn nur gedrehter Walk · Modell fest verbogen, Animation addiert nur darauf. | Körperform absolut vorgeben; Ganzkörper-Undulation, Kopf führt; Turn = Körper biegt sich in die Kurve; Ready = S-Kurve mit Spannung; Attack aus dem ganzen Körper. Keine Tripo-Credits. | 🔄 Agent Eel |
| C5 | Tentakel zu steif; nur die unteren Enden bewegen sich, der Rest starr. Tentakel sind **bis an die Wurzel** wabbelig. | Rig-Ketten bis zur Wurzel prüfen, Wellen über die ganze Länge, je Tentakel eigene Phase, alle Clips außer Death. | 🔄 Agent Tentakel |
| C6 | Wespenflügel aus manchen Kamerawinkeln unsichtbar oder halb. Wie machen andere Spiele das? | Ursache belegen (einseitige Flächen/Backface Culling), Flügel doppelseitig mit einem Material, Unity-Prüfbilder aus 4 Winkeln, Recherche. | ✅ Ursache belegt: 124 einseitige Flächen. Flügel jetzt doppelseitig (`rigging/double_sided.py`), 1 Material, +3 % Tris, aus allen Winkeln sichtbar (Prüfbild `temp/wings_before_after.png`). Rest: Rückseiten dunkler, kein Durchscheinen (Shader-Thema später). |
| C7 | Eel-Kopf: Lappen unten sollen frei schwingen (möglichst ohne Knochen), Kamm/Hörner starr. Frage: Standard für frei hängende Teile oder zu individuell? | Antwort: Standard-Baustein; pro Kreatur nur festlegen, welche Bereiche schwingen. Empfehlung: Shader-Wabbeln ohne Knochen für kleine Teile, Federketten für große. | ✅ bis auf Neubau: Standard-Baustein ohne Knochen gebaut – `rigging/dangling.py` markiert dünne Teile in konfigurierten Bereichen (`[dangling]` in der creature.toml, Verlauf Ansatz → Spitze, Phase je Teil) als Vertex-Farbe, Export FBX + GLB, Unity-Shader `Creature/Standard Dangling` (Importer wählt ihn automatisch). Eel: 13 Lappen/Fühler unter Kopf + Hals schwingen, Kamm/Hörner/Kiefer starr – Unity-Prüfbild `temp/review/dangling_eel.png`. Kreaturen ohne Markierung unverändert (Regression). **Offen: Eel-Neubau `--stage full` nach dem Eel-Agenten.** Doku: `rigging/README.md` „Frei hängende Teile“. |
| C8 | (Messung) Bodenkontakt: Raptor sinkt im Walk bis 1,9 cm ein, Wespe bis 3,7 cm. | Ursache finden, Füße auf dem Boden. | 🔄 Raptor (in C2) · 🔄 Agent Wespe-Boden |
| C9 | (zu B1) Dehnung an der Ursache lösen. | Mehr Vertices an Gelenken bzw. starre Segmente für Chitin-Tiere (ein Mesh, getrennte Teile). | ⏭ |

## G. Recherche & Planung

| # | Meldung / Anweisung des Nutzers | Status |
|---|---|---|
| G1 | Monster-Datenbank `H:\AIProjects\poe2-MTXeastCatalog\data\catalog.json` (alle PoE-Monster) eigenständig auswerten: Monsterarten auflisten, semantisch in 3D-Kategorien einordnen → lange Liste, welche **Skelette und Bewegungsmuster** wir noch brauchen und welche **Monsterarten zu unserem Game passen**. **Inspiration, keine Kopie!** Ziel des Spiels: später mindestens **50–100 Basis-Monster**, je 5–6 Biom-Varianten oder Elite-Addons. Hinweis des Nutzers: von 7.133 Einträgen sind nur ~2.800 echte Monster, der Rest Varianten. | ✅ `RECHERCHE_MONSTERARTEN.md` (2.872 echte Monster, Stand DB 2026-11-17T20:25Z, Schema v2). Vorhandene 8 Skelette decken 71,9 % der Kreaturen; mit `upright`, `winged`, `amorph`, `static` 99,9 %. 83 generische Basis-Archetypen, 6er-Variantenschema, Reihenfolge: spider → leopard/bear → upright (golem, brute) → wraith/orb → winged → static → slime → frog/badger/monkey. Zuordnung: `temp/monster_research/kategorien.csv`. |

## D. Erledigt in dieser Session

| # | Meldung | Ergebnis |
|---|---|---|
| D1 | Unity-Testszene: alle Kreaturen automatisch, Dropdown, Walk startet automatisch, Auto-Loop, Tempo, 9 Clip-Buttons. | ✅ `Unity_Creature_Test/` (+ Zeitleiste, Frame-Schritt, Kameraansichten, Selbsttest headless). Ordner vom Nutzer umbenannt, Pfade angepasst. |
| D2 | Input-Manager-Warnung in Unity. | ✅ Harmlos, der Viewer nutzt ihn nicht. Optional später: Umstellung auf das Input-System-Paket. |
| D3 | Raptor: „zweiter Schwanz“. | ✅ Hautstreifen aus dem Tripo-Modell im Rig entfernt (Ursache: Frontbild mit Schwanz zwischen den Beinen). |
| D4 | Raptor schwebt (Schatten). | ✅ Viewer misst jetzt das echte Mesh statt Unitys zu großem Rahmen. Rest: C8. |
| D5 | Hirsch: Vorderknie knicken nach innen. | ✅ Gelenkerkennung bei eng stehenden Beinen repariert. |
| D6 | Hirsch: Hinterbeine doppelt so breit wie vorne. | ✅ Kam aus dem Tripo-Modell → Mesh-Korrektur. |
| D7 | Hirsch: Geweih wackelt, muss starr sein. | ✅ Geweih 100 % am Kopf. |

## E. Zurückgestellt

| # | Meldung | Status |
|---|---|---|
| E1 | Death-Animationen fast überall „grottig“ (Mini-Bewegung + Rotation; Skorpion rotiert und steht auf dem Schwanz). | ⏸ Nutzer: vorerst nicht anfassen. Folge von D6: Hirsch-Death reißt 2,5 cm auf (bekannt). |

## F. Aus früheren Sessions noch offen

- Hirsch: Tripo-UV sehr zerstückelt.
- Prio-2-Clips aus MOVESET.md (Attack2, Dodge, Knockdown …).
- Flesh Titan (#7) – mit dem Nutzer zusammen.
- 12 Kreaturen noch nicht bei Tripo generiert (1.475 Credits).
- Nichts aus dieser Session ist committet.
