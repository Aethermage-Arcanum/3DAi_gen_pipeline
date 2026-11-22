# Handover (Stand 2026-11-20, Nächste Schritte + Git + Baukasten: 2026-11-22)

Für die nächste Session lesen, in dieser Reihenfolge:
1. `../CLAUDE.md` mit den Regeln des Nutzers. Besonders wichtig: **Claude = Orchestrator + Prüfer** (Hauptchat erkundet/schreibt nichts selbst, alles über Subagenten, Kontext sparen), Subagenten **nacheinander** (max. 1 Bau-Agent + 1 leichter), gründlich statt hektisch, Death-Clips vorerst nicht anfassen, selbständig committen, nur Push mit Freigabe.
2. Diese Datei.
3. **`BACKLOG.md`**: die Hauptliste aller Nutzer-Meldungen mit Status. Jede neue Meldung kommt zuerst dorthin.

## Stand

### Fertig (Mesh + UV + Rig + Clips + FBX/GLB)
- **9 Kreaturen (Stand 17./18.11.):** Chitin Crawler (hexapod/ant), Ravine Stalker (quadruped/wolf), Reef Snapper (quadruped/lizard), Hollow Stag (quadruped/deer), Dune Raptor (biped_raptor/raptor), Eel Stalker (legless/cobra), Scorpion Matriarch (multileg/scorpion), Needle Wasp (flyer/wasp), Void Manifestation (floater/tentacle).
- Seit dem 18.–20.11. sind außerdem fertig: Bog Warden (upright/treant, Commit 9686a8f), Cinder Wyvern und Bonepicker Vulture (winged, Commit 38ce1c7). Die Abnahme durch den Nutzer steht noch aus.
- **Void Manifestation** wird neu gemacht. Ihr Tentakel-Agent hat nur die allgemeinen Learnings erarbeitet.
- **Am 18.11. überarbeitet und von Claude geprüft:**
  - Vierbeiner weich: echter Wolfsgalopp statt Hoppeln, Turn-Vorzeichen behoben.
  - Raptor, Eel (Ganzkörper), Skorpion-Stich, Tentakel ab der Wurzel.
  - Wespenflügel doppelseitig, Hirsch-Rig.
  - Baustein „frei hängende Teile“: `rigging/dangling.py` + Unity-Shader.

### Tripo-Modelle bereit für Rig und Muster (alle Pflichtprüfung B bestanden)
| Kreatur | Muster | Hinweis für den Rig |
|---|---|---|
| broodling | octopod/spider | vorderes Beinpaar leicht angehoben |
| shellback | quadruped/tortoise | Ansichten aus dem Raster nach Inhalt neu geschnitten |
| sand_leviathan | legless/sandworm | rundes Maul (Nutzer bevorzugt) |
| frost_colossus | quadruped/gorilla | – |
| ruin_howler | quadruped/monkey | – |
| oasis_gulper | quadruped/frog | **v2 aus der Sprung-Pose** (alle 4 Füße am Boden, Beine gestreckt) ist Claudes Empfehlung. ❓ Der Nutzer hat **noch nicht zwischen v1 und v2 entschieden** (BACKLOG G5, Q5). v1 liegt in `raw/_v1`. Die Hocke braucht ggf. **Gelenk-Verdichtung (C9, Baustein fertig)**. Rig bricht ab (C16). |
| reality_ripper | hexapod/mantis | Sensenklingen lose → starr an die Arm-Knochen; Hinterbeine per IK auf den Boden |
| gloomfang_centipede | legless/centipede | aus dem Design-Bild allein generiert (`tripo_run.py --single design.png`); Beine stehen waagerecht ab → nach unten setzen |
| bog_warden | upright/treant | **neues Skelett `upright`** ✅ fertig (Commit 9686a8f), offen: Moos (C13), Abnahme (BACKLOG Q4) |
| cinder_wyvern | winged/drake | neues Skelett `winged`; Tripo hat die Flügel ungleich gestellt → Flügel-Haltung absolut vorgeben |
| bonepicker_vulture | winged/bird | `winged`; Federspitzen einseitig → `double_sided` |

### Weitere Eckdaten
- **Tripo-Guthaben ≈ 155 Credits** (ca. 110 pro Modell, **≈ 1 $ pro Modell**; Preisrecherche: `docs/recherche/RECHERCHE_3D_DIENSTE.md`).
- **Roster:** 36 Kreaturen (`creatures/roster.toml`): 20 ursprüngliche plus 16 aus der Monster-Recherche (ohne Concept, Design aus der Beschreibung). Dazu kommen 18 Biome (`templates/biomes.toml`). Vorschlag und Auswahl stehen in `docs/recherche/ROSTER_ERWEITERUNG_VORSCHLAG.md`, die Recherche in `docs/recherche/RECHERCHE_MONSTERARTEN.md`.
- **Noch keine Modelle (17, geprüft 2026-11-20: kein `raw/generate_model.glb`):** spore_drone, shore_lurker, stone_boar, rock_hyena, glassback_colossus, flesh_titan, void_harbinger, geode_golem, tomb_shroud, idol_eye, umbral_panther, rimehide_bear, sporecap_mortar, bog_ooze, quillback_burrower, tallgrass_viper, mound_queen. Das wären 17 × 110 = 1.870 Credits. Die 155 Credits reichen für 1 Modell, und das ist für den Rimehide Bear vorgesehen (G10). Die Void Manifestation hat ein altes Modell und soll neu gemacht werden. Die Prompts für alle sind fertig.
- **Varianten-Baukasten (G9):** M1 ✅ (87ff233, Unity-Fenster, Ebenen-Shader, Backen, Slagback + Cragplate), M2 ✅ (5f7466c, Blender-Panel mit Live-Reglern, Bedeckung per Geometry Nodes, „In Blender bauen“, Textur-Backen, Presets A B C E F G I, 15 Bausteintypen). Anleitung `docs/VARIANTEN_BAUKASTEN.md`, Reste in BACKLOG G9 bzw. `docs/VARIANTEN_BAUKASTEN_WIP.md`.
- **Git:** Abgeschlossene Schritte sind committet, zuletzt `5f7466c` (Varianten-Baukasten M2). Push nur mit Freigabe des Nutzers.

## Nächste Schritte
0. 🔜 **ZUERST (Nutzer 2026-11-22): G14 Nachschwingen der Bedeckung im Shader („Foliage-Trick“).** Bedeckungsteile bekommen beim Erzeugen (Geometry Nodes) einen Beweglichkeitswert pro Vertex (Wurzel 0, Spitze 1), der Shader verbiegt die Spitzen auf der GPU aus Trägheit (Ansatz-Knochen), Wackeln (Rauschen/Wind) und Stößen (Clip-Events). Neuer Regler `weichheit` pro Lage (Spec 2.2). Gilt für `VariantKit/Layered` und `VariantKit/Baked`, bleibt 1 Material, keine Physik, keine Zusatz-Knochen. Nimmt die M2-Reste zu `schwingen` und hängenden Gehängen mit; C13 (Moos Bog Warden) danach. Spring Bones nur später für wenige große Teile, echte Haar-/Stoff-Physik verworfen. Spezifikation: BACKLOG G14. Ein Bau-Agent.

Danach die bisherige Reihenfolge (Priorität des Nutzers: erst neue Skelette, dann Muster):
1. ✅ **`upright` fertig** (Commit 9686a8f, Bog Warden, Muster treant). Offen daran: Moos steif (C13, später).
2. ✅ **G7 fertig** (73990c3): Ordner heißen `creatures/NN_name/`, IDs und Exportnamen ohne Nummer.
3. ✅ **`winged` fertig** (Commit 38ce1c7): Cinder Wyvern 14 (winged/drake, bleibt zweibeinig – Nutzer 2026-11-20) und Bonepicker Vulture 15 (winged/bird), je 14 Clips, Death nur Platzhalter. Bewegung muss der Nutzer noch per Roh-GIFs abnehmen. Reste (Vorschau-Kamera, Feueratem, Geier-Hinterzehe) in BACKLOG G12; echte Fledermaus = G11 (Todo, nicht vorziehen).
4. ✅ **Geweih-Fix Hollow Stag (C14)** erledigt 2026-11-20 (Commit 5b09992; Geweih 0,0 cm Abweichung, Wolf und Echse identisch; Abnahme der GIFs durch den Nutzer steht aus).
   - ✅ **C9 Gelenk-Verdichtung** als Baustein fertig (Commit 1d2305b, `rigging/joint_densify.py`, opt-in `[joint_densify]`, bei keiner Kreatur eingeschaltet). Wolf-Kopie: +800 Tris, Dehnung im Run 2,05 → 1,78, aus der Spielkamera kaum sichtbar, Raptor sogar schlechter. Nutzerkritik: am irrelevanten Sprunggelenk getestet.
   - 🔄 **jetzt C15: Rumpf/Hals-Dehnung** (Wolf Bauch/Rücken, Hirsch Hals), Build-Agent läuft. Ursache sind die Gewichte (Wolf Hüftflanke 2,89; Hirsch Tail_1 zieht mit 42 % am Knie; Raptor/Geier/Wyvern an der harten Sohle). **Regel: Prüfungen zuerst an dem, was die ARPG-Kamera sieht.**
   - Danach die **Muster-Warteschlange mit der Spinne neu** (alter Agent ohne Spuren): Spinne → Schildkröte → Sandwurm → Gorilla → Affe → Frosch (inkl. Rig-Fehler **C16**: `center_at` liefert None → TypeError in `quadruped_rig.py`, vor dem Frosch-Muster lösen) → Mantis → Tausendfüßer. Immer nur ein Bau-Agent.
   - ⏸ **Hirsch C12 = vorgemerkt, ferne Zukunft** (Nutzer 2026-11-20): nur **neue Basisbilder + Tripo-Neulauf** warten, bis der Nutzer es ausdrücklich aufruft. Der Geweih-Fix gehört nicht dazu (→ C14).
5. **C13 Moos** (Bog Warden, `dangling.py`) bleibt offen.
6. **Offene Fragen an den Nutzer:** Alle stehen gesammelt in `BACKLOG.md` → „❓ Offene Fragen an den Nutzer“ (Q1–Q9, je mit Fundstelle). Darunter fallen: Raptor-Arme (A11), Schwanz des Raptors im Attack, Sohlen bei Wolf und Echse, Bog Warden (Slam und Walk), Oasis Gulper v1/v2 (G5), Test der zweistufigen Prompts (A10), die 16 Ergänzungen (G2), die Bären-Varianten (G10) sowie die Abnahme der Roh-GIFs von winged (G6) und C14.
7. **G9:** Prompt-Schritt Varianten-Brainstorming ✅, Varianten-Baukasten M1 ✅ (87ff233) und M2 ✅ (5f7466c). Offene Reste siehe BACKLOG G9; Nachschwingen → G14 (oben, zuerst).

## Ablauf pro Kreatur
0. **Varianten zuerst (neue Kreaturen, Entscheidung 2026-11-20, BACKLOG G8 d/G9):** 5–6 Varianten brainstormen, Gemeinsames = Basis-Kreatur (nur sie geht ohne variable Details zu Tripo), Unterschiede → Tönung / Anbauteile (Geometry Nodes) / Proportions-Slider / Shader + Partikel in Unity; starke Silhouetten-Abweichung = eigene Basis-Kreatur; alle Varianten teilen Rig + Clips. Bestehende Modelle bleiben (eingebrannte Details, Varianten nur Tönung + Anbauteile). **Prompt-Schritt und Baukasten sind noch nicht gebaut** (nach den Skeletten); bis dahin Brainstorming von Hand mit dem Nutzer. Details: README „Ablauf“.
1. **Bilder in zwei Stufen:** `python scripts/make_roster.py` → `PROMPTS_ALLE.md` + `creatures/<NN_name>/prompts.md`.
   - Die Beschreibung ist `look` in `roster.toml`: qualitativ, keine Zahlen. Die Pose (`pose`) zeigt **alle Gliedmaßen in voller Länge**, nie sitzend oder gefaltet.
   - **Stufe 1:** Design-Bild → Nutzer prüft es gegen sein Concept → `input/design.png`. **Stufe 2:** 4 Ansichten aus design.png.
   - **Grenze der Bild-KI:** ChatGPT klebt an der Vorlage und übernimmt deren Pose. Die Pose muss also schon im Design-Bild stimmen. Trick des Nutzers für den Frosch: „mitten im Sprung“.
   - ChatGPT-Dateinamen enden auf -1…-4 (vorn, links, rechts, hinten), ohne Nummer = Design. Auf die Standardnamen **kopieren**, die Originale bleiben liegen.
   - Raster-Bilder nach Inhalt schneiden, mit gemeinsamem Maßstab (siehe Shellback).
   - **Pflichtprüfung A durch Claude** nach der README-Checkliste.
   - **Achtung Perspektive:** Die Kamera schaut leicht von oben. Ein gerade nach hinten gestreckter Schwanz wirkt in der Rückansicht wie ein herabhängender Streifen (Fehleinschätzungen bei Gorilla und Affe).
2. **Tripo:** `python scripts/tripo_run.py creatures/<NN_name> --steps generate --dry-run`, dann ohne `--dry-run`. Der Nutzer hat das Generieren für fertig geprüfte Bilder freigegeben, die Credits trotzdem im Blick behalten.
   - Option `--single design.png` erzeugt das Modell aus einem einzigen Bild.
   - Neu generieren mit `--force generate`, die alte Fassung vorher nach `raw/_v1` sichern (raw nie überschreiben).
3. **Prüfskript:** `python scripts/model_check.py creatures/<NN_name>` – nur Frühwarnsystem, die **Sichtprüfung B ist Pflicht**. Gewollte Befunde kommen nach `[model_check.freigabe]` mit Begründung. Erlaubte Schlüssel: boden, dreiecke, fussbreite, fussgruppen, haengende_teile, mesh_teile, mittellinie, offene_flaechen, symmetrie.
4. **Pipeline:** `python scripts/creature_pipeline.py creatures/<NN_name> [--stage motion|full|check]`.
   - `motion` erzeugt Roh-GIFs in `rig/anim/raw/`, die der Nutzer abnimmt.
   - `full` macht den Export und die End-GIFs in `rig/anim/final/`.
5. **Unity:** Projekt `Unity_Creature_Test/` (der Nutzer hat es meist offen → für Batch-Läufe eine Kopie verwenden, siehe dortige README). Menü **Kreaturen › Alle importieren + Szene bauen**.
6. README der Kreatur (Kennzahlen) und des Musters (Naturreferenzen) pflegen, dann committen.

## Skelette (Rig → Baukasten → Muster)
| Skelett | Rig | Baukasten | Muster |
|---|---|---|---|
| hexapod | rigging/hexapod_rig.py | motions/hexapod/hexapod_kit.py | ant (mantis, broodmother geplant) |
| octopod | rigging/octopod_rig.py | motions/octopod/octopod_kit.py | crab, spider (Agent läuft) |
| multileg | rigging/multileg_rig.py | motions/multileg/multileg_kit.py | scorpion |
| quadruped | rigging/quadruped_rig.py | motions/quadruped/quadruped_kit.py | wolf, lizard, deer (+ tortoise, gorilla, monkey, frog … geplant) |
| biped_raptor | rigging/biped_raptor_rig.py | motions/biped_raptor/biped_kit.py | raptor |
| legless | rigging/legless_rig.py | motions/legless/legless_kit.py | cobra (+ sandworm, centipede, viper geplant) |
| floater | rigging/floater_rig.py | motions/floater/floater_kit.py | tentacle |
| flyer | rigging/flyer_rig.py | motions/flyer/flyer_kit.py | wasp |
| **upright** | rigging/upright_rig.py ✅ | motions/upright/upright_kit.py | treant (golem, brute geplant) |
| **winged** | rigging/winged_rig.py ✅ | motions/winged/winged_kit.py | drake, bird (bat als Todo, G11) |
| amorph, static | geplant | – | slime; turret/nest/plant |

**Gemeinsame Bausteine:** `rig_common.py`, `gaps_defaults.toml`, `double_sided.py`, `dangling.py`, export_unity / verify_export / check_gaps, `pose_fingerprint.py`.
**Architektur:**
- Baukästen nur abwärtskompatibel erweitern.
- Nach Änderungen an gemeinsamen Dateien `scripts/regression.py --deep` laufen lassen.
- Freigabe mit `scripts/approve.py`, nur auf Wunsch des Nutzers. Freigegeben ist bisher nichts.

## Wiederkehrende Probleme und Lösungen
- **Tripo-Hautbrücken** → Flächen löschen: `cut_between_legs`, `cut_fused_limbs`, `cut_leg_bridges`, `cut_tail_leg_bridges`, `cut_belly_flap`.
- **UV-Naht-Duplikate** brauchen identische Gewichte.
- **Eng stehende Beine** → `adaptive_belly_strip`. Zu breite Hinterbeine → `narrow_hind_legs`. Geweih/Hörner → `rigid_head_above`.
- **Einseitige Flächen** (Flügel, Krausen) → `double_sided.py`.
- **Unity-Viewer:** Boden = Bindepose (`RestLowestPoint`), nicht die erste Take-Pose.
- **Dehnung** ist nur eine Info. Sie wird am Mesh gelöst, nie durch kleinere Bewegung. Die Gelenk-Verdichtung (C9) ist als Baustein fertig (opt-in). Die größten Dehnungen kommen aber aus den Gewichten (C15).
- **TurnLeft-Vorzeichen** war bei Vierbeiner und Raptor falsch. Bei jedem neuen Muster prüfen.
- **Windows-Dateisperre** beim GIF-Aufräumen → in der Pipeline behoben (Wiederholung).
- **Death-Clips:** Der Code ist überall unverändert (Nutzer-Anweisung). Durch Rig-Änderungen weichen einzelne Death-Ergebnisse leicht ab (Skorpion, Tentakel, Raptor-Füße, Hirsch-Lücke 3,05 cm begründet freigegeben).
