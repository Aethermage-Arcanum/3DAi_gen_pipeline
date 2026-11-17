# Roadmap: MVP für alle 20 Kreaturen (Planung, noch nicht umgesetzt)

Stand 2026-11-17. Grundlage: `_concept/monster_progression_A_vs_B.webp`. Design nach **Artist A**, Stil nach **Artist B (Low-Poly)**, so wie beim Chitin Crawler. Der B-Name steht jeweils in Klammern.

**MVP-Umfang pro Kreatur = exakt wie Ant:** Walk, Run, Idle, Ready, TurnLeft, TurnRight, Attack1, Hit, Death. Dazu kommen jeweils UV-Prüfung, eigenes Standard-Rig, Selbstprüfung, FBX/GLB und Events.

## 1. Übersicht: Kreatur → Skelett → Bewegungsmuster

| # | Kreatur (B) | Kategorie · Biom | Skelett | Bewegungsmuster | Status |
|---|---|---|---|---|---|
| 1 | **Chitin Crawler** (Leaf Creeper) | Insects · Wald | crawler | ant | ✅ fertig |
| 2 | **Spore Drone** (Spore Beetle) | Insects · Wald | crawler | ant → Variante **beetle** | Variante |
| 3 | **Needle Wasp** (Stalk Wasp) | Insects · Wald | crawler **+ Flügel** | **wasp** (neu) | neues Muster |
| 4 | **Broodling** (Nestling) | Insects · Wald | crawler | ant → Variante **spider** | Variante |
| 5 | **Reef Snapper** (Tide Prowler) | Vertebrates · Küste | **quadruped** | **lizard** (neu) | neues Skelett |
| 6 | **Shore Lurker** (Reef Strider) | Vertebrates · Küste | quadruped | lizard → Variante **lurker** | Variante |
| 7 | **Shellback** (Shellbreaker) | Vertebrates · Küste | quadruped | **tortoise** (neu) | neues Muster |
| 8 | **Eel Stalker** (Depth Serpent) | Vertebrates · Küste | **legless** | **cobra** (neu), Variante **eel** | neues Skelett |
| 9 | **Ravine Stalker** (Cliff Runner) | Mammals · Highlands | quadruped | **wolf** (neu) | Referenz-Vierbeiner |
| 10 | **Stone Boar** (Stone Grazor) | Mammals · Highlands | quadruped | **boar** (neu) | neues Muster |
| 11 | **Hollow Stag** (Hollow Stag) | Mammals · Highlands | quadruped | **deer** (neu) | neues Muster |
| 12 | **Rock Hyena** (Ravine Howler) | Mammals · Highlands | quadruped | wolf → Variante **hyena** | Variante |
| 13 | **Sand Leviathan** (Sand Worm) | Beasts · Wüste | legless | **sandworm** (neu) | neues Muster |
| 14 | **Dune Raptor** (Dune Charger) | Beasts · Wüste | **biped_raptor** | **raptor** (neu) | neues Skelett |
| 15 | **Oasis Behemoth** (Glassback Colossus) | Beasts · Wüste | quadruped | **behemoth** (neu) | neues Muster |
| 16 | **Scorpion Matriarch** (Oasis Tyrant) | Beasts · Wüste | crawler **+ Schwanz** | **scorpion** (neu) | neues Muster |
| 17 | **Frost Colossus** (Glacial Horror) | Monstrosities · Schnee | quadruped | behemoth → Variante **colossus** | Variante ⚠ |
| 18 | **Abyssal Chimera** (Flesh Titan) | Monstrosities · Abyss | quadruped ⚠ | **chimera** (neu) | ⚠ Designfrage |
| 19 | **Void Manifestation** (Void Harbinger) | Monstrosities · Abyss | **floater** | **tentacle** (neu) | neues Skelett ⚠ |
| 20 | **Reality Ripper** (Reality Devourer) | Monstrosities · Abyss | crawler | **mantis** (neu) | neues Muster |

**Bilanz:**
- **6 Skelette:** crawler ✅ (erweitert um optionalen Schwanz und Flügel), quadruped, legless, biped_raptor, floater, ggf. biped_brute
- **15 Bewegungsmuster:** ant ✅, crab ✅ (nur Validierung), wasp, scorpion, mantis, lizard, tortoise, wolf, boar, deer, behemoth, chimera, cobra, sandworm, raptor, tentacle
- **6 Varianten:** beetle, spider, lurker, hyena, colossus, eel

## 2. Pro Kreatur: Was die MVP-Clips konkret bedeuten

Kurzform je Kreatur: **Walk / Run · Idle / Ready · Turn · Attack1 · Hit · Death**, dazu die Naturreferenz, die vor dem Bau gesucht wird.

### Insects (Wald, Early Game), Schwärme → knappes Budget (≤ 3.000 Dreiecke)
**2 · Spore Drone**: ant/beetle
- Gang langsam und schwer. Idle: Pilz-/Sporensack pulsiert (Hinterleib-Knochen „atmet“ stärker). Ready: Sporensack bläht sich.
- Attack1: **Sporen-Stoß**, Hinterleib ruckt nach oben, Event `projectile_spawn` (Fernkampf-AoE). Death: auf den Rücken.
- Referenz: Käfer-Gang, *Ophiocordyceps*/Pilzbefall bei Insekten (Pulsieren)
- Prozedural: Pilzhauben per Geometry Nodes (wie Stacheln)

**3 · Needle Wasp**: crawler + Flügel / wasp
- Walk/Run = **Schwebeflug** (Körper bobbt, Beine hängen, Hinterleib pendelt). Flügel: schneller Zyklus plus **Bewegungsunschärfe per Shader** statt echter Frequenz (Fake it, spart Keyframes). Turn = in der Luft drehen.
- Ready: Hinterleib nach vorne krümmen. Attack1: **Stich-Sturzflug**, Hinterleib schnellt nach vorne, `hit`. Death: fällt herunter, landet auf dem Rücken.
- Referenz: Wespe schwebend und stechend (Zeitlupe)
- Skelett-Erweiterung: `Wing_L1/L2/R1/R2` (bei Krabblern ohne Flügel leer)

**4 · Broodling**: ant/spider
- 8 Laufbeine → alternierender Vierfuß (fertige Variante). Idle: Eiersack auf dem Rücken wackelt nach (sekundäre Bewegung am Hinterleib).
- Attack1: Sprungbiss (kurzer Satz nach vorne mit Root Motion). Death: Eiersack platzt (VFX-Event `burst`).
- Referenz: Wolfsspinne mit Eikokon, Springspinne

### Vertebrates (Küste, Early–Mid)
**5 · Reef Snapper**: quadruped / lizard *(erstes Vierbeiner-Muster der Küste)*
- Gang **gespreizt** (Beine seitlich), Wirbelsäule schlängelt seitlich, Schwanz folgt (Krokodil/Waran). Run = High-Walk.
- Ready: Maul auf, Kopf tief. Attack1: **Schnappbiss** mit Kopf-Lunge plus Kopfschütteln. Death: auf die Seite rollen.
- Referenz: Waran-Gang, Krokodil-High-Walk, Krokodil-Schnappbiss

**6 · Shore Lurker**: lizard/lurker
- Wie Reef Snapper, aber tiefer geduckt und langsamer. Idle: lauert regungslos (nur Atmung).
- Attack1: Hinterhalt-Lunge (Root Motion nach vorne) mit Hauern. ⚠ Concept prüfen: eher Amphibie oder Walross?
- Referenz: Krokodil im Hinterhalt, Walross

**7 · Shellback**: quadruped / tortoise
- Sehr langsamer, schwerer Gang. Ready: **Kopf und Beine halb einziehen** (Panzer als Schild).
- Attack1: Kopf schnellt aus dem Panzer (Schnappschildkröte). Hit: Kopf ruckartig rein. Death: auf den Rücken kippen (Root wie Ant).
- Referenz: Schnappschildkröte, Landschildkröten-Gang

**8 · Eel Stalker**: legless / cobra, Variante eel
- Walk/Run: **seitliches Schlängeln** (Sinuswelle entlang der Kette), Vorderkörper erhoben. Turn: Kopf führt, Körper folgt.
- Ready: aufgerichtet in S-Kurve, schwankt (Kobra). Attack1: Schlag aus der S-Kurve, plus **Elektro-Event** (Drop: Electro Organ). Death: erschlaffen, Kette sackt zusammen.
- Referenz: Muräne, Kobra-Drohhaltung, Zitteraal

### Mammals (Highlands, Mid)
**9 · Ravine Stalker**: quadruped / wolf *(Referenz-Vierbeiner, wird zuerst gebaut)*
- Walk = Schritt, Run = **Galopp** (eigener Zyklus, kein schnellerer Walk). Turn: auf der Stelle trippeln.
- Ready: geduckt, Nackenstacheln hoch, knurren. Attack1: kurzer Anlauf und Sprungbiss (Root Motion). Death: zur Seite kippen.
- Referenz: Wolf trabend und galoppierend (Muybridge-Sequenzen), Wolf-Drohhaltung

**10 · Stone Boar**: quadruped / boar
- Kurzer, stämmiger Trab. Idle: wühlt mit dem Rüssel. Ready: scharrt mit dem Huf und senkt den Kopf.
- Attack1: **Ansturm + Hauer-Stoß nach oben** (Root Motion). Death: kippt schwer zur Seite.
- Referenz: Wildschwein-Angriff, Wildschwein wühlend

**11 · Hollow Stag**: quadruped / deer
- Walk: elegant, Kopf nickt. Run: **Sprünge** (Prellsprung/Galopp). Idle: äst, Ohren- und Kopfzucken.
- Ready: Geweih gesenkt. Attack1: **Geweih-Stoß** (Kopf runter, vorwärts, hoch). Death: knickt vorne ein, sinkt.
- Referenz: Hirsch-Galopp, Hirschkampf (Brunft)

**12 · Rock Hyena**: wolf/hyena
- Wie Wolf, aber **abfallender Rücken** (Vorderbeine länger), schlaksiger, „hinkender“ Galopp. Idle: Kopf tief, schnüffelt.
- Ready: „Lachen“ (Kopf hoch und runter, Event `sfx_cackle`). Attack1: Biss mit Zerren.
- Referenz: Tüpfelhyäne Gang und Lachen

### Beasts (Wüste, Mid–Late), größer → mehr Budget (5.000–8.000)
**13 · Sand Leviathan**: legless / sandworm
- Walk/Run: **Ziehharmonika-Bewegung** (rectilinear: Segmente ziehen sich wellenförmig zusammen), alternativ halb im Sand.
- Idle: Kopf pendelt, Kiefer öffnen sich. Ready: Vorderkörper hoch, Maul weit offen.
- Attack1: **Verschlingen-Lunge** nach vorne-unten. Turn: Kopf führt. Death: bäumt sich auf und fällt um.
- Referenz: Regenwurm (Peristaltik), rectilineare Fortbewegung der Python, Sandboa
- Später: Abtauchen/Auftauchen als Spawn-Clip (mit Sand-VFX)

**14 · Dune Raptor**: biped_raptor / raptor
- Walk/Run: **Vogel-Dino-Gang** (digitigrad, Schwanz balanciert, Kopf stabilisiert wie beim Huhn). Flügel (A-Design) nur für Gleitsprünge.
- Ready: geduckt, Flügel gespreizt, Kopf ruckt. Attack1: **Sprung-Kralle** (Root Motion) oder Pick-Biss. Death: fällt zur Seite.
- Referenz: Strauß und Laufvogel-Gang, Sekretärvogel-Tritt, Kopfstabilisierung beim Huhn
- ⚠ A hat Flügel, B (Dune Charger) nicht → entscheiden

**15 · Oasis Behemoth**: quadruped / behemoth
- **Schwerer, langsamer Gang**, Körper schaukelt, Gewicht sichtbar (Elefant/Nashorn). Idle: schnaubt.
- Ready: bäumt sich halb auf. Attack1: **Stampfer** mit AoE-Event `shockwave`, oder Ansturm. Death: sackt vorne ein, rollt zur Seite.
- Referenz: Elefant (Passgang), Nashorn-Angriff
- ⚠ B (Glassback Colossus) wirkt eher wie ein Knöchelgänger (Gorilla) → gleiche Frage wie bei #17

**16 · Scorpion Matriarch**: crawler + Schwanz / scorpion
- Gang wie Ant (8 Beine, Spinnen-Variante) **plus Scheren aus dem Crab-Baukasten** und eine **Schwanzkette (5–6 Glieder) über dem Rücken**.
- Ready: Scheren gespreizt, Stachel zittert über dem Kopf. Attack1: **Stachelstoß** über den Kopf nach vorne (`hit`), alternativ Scherenschlag als Attack2.
- Death: auf den Rücken, Schwanz rollt sich ein.
- Referenz: Skorpion-Gang und Stich, Drohhaltung
- Wiederverwendung: Gang (ant), Scheren (crab), neu ist nur der Schwanz

### Monstrosities (Schnee/Abyss, Late), Elite/Boss-nah → Dodge relevant (Prio 2)
**17 · Frost Colossus**: behemoth/colossus
- Wie Behemoth, aber **Knöchelgang** (vorne auf Fäusten, Gorilla). Ready: Brust aufrichten, Eiszacken klirren. Attack1: **Doppelfaust-Slam** mit AoE `ice_shockwave`.
- Referenz: Gorilla Knöchelgang und Brusttrommeln
- ⚠ B (Glacial Horror) ist ein vierbeiniges Eis-Raubtier (eher wolf-artig) → Design entscheiden

**18 · Abyssal Chimera**: ⚠ Designfrage
- A = Vierbeiner-Bestie mit Skorpionschwanz und Tentakeln → quadruped / **chimera** (wolf-Basis plus Schwanzkette aus scorpion plus Tentakel aus tentacle)
- B (Flesh Titan) = **zweibeiniger Brutalo** → skelett biped_brute. Dafür ginge sogar **Unity Humanoid plus fertige Animationen** (Mixamo/Asset Store), der billigste Weg überhaupt.
- Attack1: Schwanzstich (A) bzw. Faustschlag (B)
- Referenz: (A) Löwe + Skorpion; (B) Gorilla/Bodybuilder-Gang

**19 · Void Manifestation**: floater / tentacle
- **Schwebt** (kein Bodenkontakt): Kern-Orb bobbt, Tentakel wogen in Wellen (metachronal). Walk/Run = schweben mit Neigung in Flugrichtung.
- Ready: Tentakel spreizen, Orb pulsiert (Emission per Shader). Attack1: **Strahl** aus dem Auge (`projectile_spawn`) oder Tentakelpeitsche. Death: Tentakel erschlaffen, Orb fällt und implodiert (VFX).
- Referenz: Oktopus und Qualle (Tentakelwellen), Kalmar
- ⚠ B (Void Harbinger) hat Beine (humanoid/spinnenartig) → Design entscheiden

**20 · Reality Ripper**: crawler / mantis
- Gang wie Spinne (hintere Beinpaare), **vorderes Paar = Sensenarme**, erhoben (Gottesanbeterin).
- Idle: Sensen wiegen, Körper schaukelt (Mantis-Wiegen = Tarnung). Ready: Sensen weit aufgespannt.
- Attack1: **Sensen-Hieb** in 1–2 Frames (Fangschlag), von oben nach vorne-unten. Death: auf den Rücken.
- Referenz: Gottesanbeterin Fangschlag (Zeitlupe) und Wiegen

## 3. Reihenfolge (Wiederverwendung maximieren)
| Phase | Inhalt | Warum zuerst |
|---|---|---|
| **1 · Krabbler ausbauen** | Spore Drone, Broodling (nur Varianten), Scorpion Matriarch, Reality Ripper, Needle Wasp | Skelett und Baukasten existieren, schnell sichtbare Ergebnisse. Schwanz und Flügel erweitern das Krabbler-Skelett. |
| **2 · Vierbeiner-Skelett** | Ravine Stalker zuerst (Referenz), dann Rock Hyena, Hollow Stag, Stone Boar, Reef Snapper, Shore Lurker, Shellback, Oasis Behemoth, Frost Colossus | 9 von 20 Kreaturen hängen an einem Skelett. Größter Hebel. |
| **3 · Beinlose** | Eel Stalker, Sand Leviathan | eigenes Skelett (Wirbelsäulen-Kette), relativ einfache Mathematik (Wellen) |
| **4 · Sonderfälle** | Dune Raptor, Abyssal Chimera, Void Manifestation | Einzelstücke mit eigenem Skelett, ggf. Humanoid-Abkürzung |

## 4. Technische Vorhaben pro Skelett (Planung)
- **crawler** (vorhanden): optionale Ketten `Tail_1..6` (Skorpion) und `Wing_L1/L2/R1/R2` (Wespe). Erkennung erweitern: Schwanz = lange Kette über dem Rücken, Flügel = flache Teile ohne Bodenkontakt.
- **quadruped** (neu): Root, Hips, Spine_1..3, Chest, Neck_1..2, Head, Jaw, Tail_1..n, 4 Beine × (Upper, Lower, Foot, Toe). Die Erkennung kann Tripos Mesh-Teile nutzen, falls die P-Serie Vierbeiner ebenfalls in Teilen liefert. **Vorher testen:** Tripos `quadruped`-Rig. Rig-Check ist kostenlos, Rig kostet 25 Credits. Ist es brauchbar, reicht eine Umbenennung auf das Standard-Skelett, statt alles selbst zu bauen. Fuß-IK aus dem Krabbler-Baukasten übertragen (digitigrade Beine = 3 Glieder).
- **legless** (neu): Kette aus N Segmenten (N je nach Länge, 12–24), Head, Jaw. Bewegung = Wellenfunktionen entlang der Kette (seitlich, rectilinear, aufgerichtet).
- **biped_raptor** (neu): Hüfte, 2 digitigrade Beine, Schwanzkette, Hals/Kopf, optional Flügel/Arme.
- **floater** (neu): Core, Eye, Tentakel-Ketten (Anzahl aus der Erkennung), kein Bodenkontakt (eigene Prüfregeln: „Schwebehöhe stabil“ statt „Füße am Boden“).
- **Prüfkette** bleibt gleich: UV → Rig → Clips + Selbstprüfung → Lücken → Vorschau → Export → Gegentest.

## 5. Aufwand & Kosten (Schätzung)
- **Tripo-Credits:** ca. 110 pro Modell (P2, Multiview, Standard-Textur). 19 neue Kreaturen ≈ **2.100 Credits**, Guthaben ca. 2.355. Das reicht knapp, Nachgenerierungen (z. B. falsche Beinzahl) und Rig-Tests (25 pro Stück) kommen dazu → **Nachkaufen einplanen**.
- (ich dachte Rig machen wir jetzt selber?)
- **Bilder (ChatGPT):** 4 Ansichten pro Kreatur. Lehre aus Lauf 1: In jedem Prompt die **genaue Beinzahl** nennen und in allen Ansichten sichtbar halten.
   Und bilder auch prüfen: ursache bei der Ant war, dass das letzte bild (das 4.) plötzlich 8 beine hatte und da aht sich Tripo drauf gestützt.
- **Varianten** (beetle, spider, hyena, lurker, colossus, eel) sind fast nur Konfiguration.
- **Neue Muster** auf vorhandenem Skelett (wasp, scorpion, mantis, tortoise, boar, deer, behemoth) sind mittlerer Aufwand.
- **Neue Skelette** (quadruped, legless, biped_raptor, floater) sind großer Aufwand, quadruped zuerst.

## 6. Offene Entscheidungen für dich
1. **A- oder B-Design, wo sie sich im Körperbau unterscheiden:**
   - #17 Frost Colossus (Gorilla) -> Gorilla hat ein sehr eigenes bewegungsmuster, laufen eher vierbienig, im angriff eher humanoid.
   - Flesh Titan (Zweibeiner) - humanoide Skelette erlaubt auch als Teil-Sturkutr (z.b. nur Oberkörper)
   - #19 Void Manifestation (Schwebe-Orb + tentakel (squid-like) ) UND Void Harbinger (mit Beinen - teilweise humanoid aber mit Flügeln) 
   - #14 Dune Raptor ohne flügel (später als elite-Variante mit flügel)
   - #15 Glassback Colossus
2. **Humanoid-Abkürzung** für zweibeinige Brutalos (Unity Humanoid + fertige Animationen) erlaubt als Vorlage auch für Tiel-strukturen. auch Animationen als Vorlage, aber die meisten Mosnter haben wenig menschlich-weiche bewegungen
3. **Bosse und Elite-Varianten** (Broodmother, Tide Aberration, …) gehören nicht zu den 20 und bekommen später eine eigene Roadmap.

## 7. Top 10 für die Pipeline (Stand 2026-11-17, alle Referenzbilder vorhanden)
Ranking-Regel: **jede Kreatur testet ein anderes Bewegungsmuster.** Vorne stehen neue Skelette, die viele weitere Kreaturen freischalten. Danach kommen Erweiterungen bestehender Skelette, zuletzt stark abweichende Muster auf einem schon gebauten Skelett. Varianten (fast nur Konfiguration) kommen danach.

| Rang | Kreatur | Skelett / Muster | Was es Neues testet | schaltet frei |
|---|---|---|---|---|
| 1 | **Ravine Stalker** | quadruped / wolf | erstes Vierbeiner-Skelett, Trab + Galopp, Wirbelsäule biegt sich | 9 Vierbeiner, Variante Rock Hyena |
| 2 | **Eel Stalker** | legless / cobra | erstes beinloses Skelett: Welle entlang der Wirbelsäule, aufgerichteter Vorderkörper | Sand Leviathan |
| 3 | **Dune Raptor** | biped_raptor / raptor | Zweibeiner mit Schwanz als Gegengewicht, Kopfstabilisierung (Huhn) | spätere Raptor-/Vogel-Monster |
| 4 | **Void Manifestation** | floater / tentacle | **kein Bodenkontakt**: Schweben + Tentakelwellen, prozedural pur | Void Harbinger, Schwebe-Bosse |
| 5 | **Scorpion Matriarch** | crawler + Schwanz / scorpion | Krabbler-Skelett + Schwanzkette, Stich über den Rücken, Scheren | Schwanz-Kette für Chimären |
| 6 | **Needle Wasp** | crawler + Flügel / wasp | Schwebeflug, Flügel (Bewegungsunschärfe per Shader), Sturzflug-Stich | alle Flieger-Insekten |
| 7 | **Flesh Titan** | biped_brute / titan | Test der **Unity-Humanoid-Abkürzung** (fertige Clips als Vorlage) | Brutalos, Void Harbinger (falls humanoid) |
| 8 | **Reef Snapper** | quadruped / lizard | gleiches Skelett wie #1, aber **gespreizte Beine** + Körperschwingen (Waran) | Shore Lurker, Shellback-Basis |
| 9 | **Hollow Stag** | quadruped / deer | lange Beine, Prell-Sprünge, Geweihstoß | – |
| 10 | **Frost Colossus** | quadruped / gorilla | Knöchelgang: Vorderbeine werden im Angriff zu Armen | Glassback (behemoth) als Schwester-Muster |

**Top 5 = Rang 1–5**: deckt alle 5 Grund-Skelette ab (Vierbeiner, beinlos, Zweibeiner, Schweber, Krabbler-Erweiterung).
**Danach** (fast nur Konfiguration, billig): Broodling (ant/spider), Spore Drone (ant/beetle), Rock Hyena (wolf/hyena), Shore Lurker (lizard/lurker). Dann Stone Boar, Shellback, Glassback Colossus, Sand Leviathan, Reality Ripper, Void Harbinger.
**Kosten:** ca. 110 Credits pro Modell → Top 5 ≈ 550, Top 10 ≈ 1.100 Credits.
**Risiken:** Bei Rang 4 und 6 können dünne Flügel bzw. Tentakel von Tripo als Klumpen oder Löcher kommen. Vor dem Riggen deshalb die UV-/Mesh-Prüfung genau ansehen, notfalls Flügel/Tentakel als eigene, einfache Flächen nachbauen (Fake it).
