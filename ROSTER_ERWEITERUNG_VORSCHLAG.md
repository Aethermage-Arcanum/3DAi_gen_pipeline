# Vorschlag: Roster-Erweiterung aus der Monster-Recherche

Stand 2026-11-18. Grundlage: `RECHERCHE_MONSTERARTEN.md` (2.872 echte Monster ausgewertet) und `creatures/roster.toml`.
**Das sind Archetypen zur Auswahl, keine fertigen Designs.** Der Nutzer wählt aus, die konkreten Monster entstehen weiter aus seiner Concept Art.
Biome wie im Roster: Wald, Küste, Highlands, Wüste, Schnee, Abyss, Höhle, Vulkan, Sumpf, Krypta.

## 1. Stand des Rosters (20 Kreaturen)

| Status | Kreaturen |
|---|---|
| **fertig** (9) | Chitin Crawler (hexapod/ant), Needle Wasp (flyer/wasp), Reef Snapper (quadruped/lizard), Eel Stalker (legless/cobra), Ravine Stalker (quadruped/wolf), Hollow Stag (quadruped/deer), Dune Raptor (biped_raptor/raptor), Scorpion Matriarch (multileg/scorpion), Void Manifestation (floater/tentacle – Modell wird neu gemacht) |
| **offen** (11) | Spore Drone (ant/beetle), Broodling (octopod/spider), Shore Lurker (lizard/lurker), Shellback (quadruped/tortoise), Stone Boar (quadruped/boar), Rock Hyena (wolf/hyena), Sand Leviathan (legless/sandworm), Glassback Colossus (quadruped/behemoth), Frost Colossus (quadruped/gorilla), Flesh Titan (upright/brute), Void Harbinger (floater/wraith-artig), Reality Ripper (hexapod/mantis) |

Die offenen 11 decken schon ab: spider, beetle, lurker, tortoise, boar, hyena, sandworm, behemoth, gorilla, brute, mantis.

## 2. Lücken laut Recherche → Vorschläge (je 2–3 Archetypen)

Sortiert nach Nutzen: wie viele Monster der Datenbank das Muster abdeckt und ob dafür ein neues Skelett nötig ist.

| Rang | Muster (Skelett) | neu? | Anteil Kreaturen | Vorschläge zur Auswahl |
|---|---|---|---:|---|
| 1 | **golem** (upright) | neues Skelett | 12,9 % | **Kristallgolem** (Höhle/Highlands, Kristalle per Geometry Nodes = Biom-Varianten) · **Knochenkonstrukt** aus Gebeinen (Krypta) · **Lavagolem** mit glühenden Fugen (Vulkan) |
| 2 | **wraith** (floater) | Skelett vorhanden | 6,0 % | **Schleiergeist** mit wehendem Stoff (Krypta) · **Sandgeist** aus wirbelndem Staub (Wüste) · **Ertrunkene Seele** mit Algenfetzen (Küste) |
| 3 | **orb** (floater) | Skelett vorhanden, sehr billig | 3,5 % | **Wächterauge** mit Strahl (Abyss) · **Irrlicht**, das explodiert (Sumpf) · **schwebende Klingen**, wirbelnd (Krypta) |
| 4 | **bird** (winged) | neues Skelett | 3,8 % | **Aasgeier**, kreist und stößt herab (Wüste) · **Sturmkrähe** im Schwarm (Highlands) · **Federstachel-Greif** schießt Federn (Highlands, Elite) |
| 5 | **bat** / **drake** (winged) | gleiches neues Skelett | 2,1 % | **Höhlenfledermaus** mit Schallkegel (Höhle) · **Aschen-Wyvern**, landet zum Kämpfen, Feueratem (Vulkan, Elite/Boss) · **Gargoyle**, sitzt als Statue und erwacht (Krypta) |
| 6 | **leopard** (quadruped) | Skelett vorhanden | 4,2 % | **Schattenpanther** mit Sprung aus dem Hinterhalt (Wald) · **Dünenlöwin** im Rudel (Wüste) · **Frostluchs** (Schnee) |
| 7 | **bear** (quadruped) | Skelett vorhanden | 3,9 % | **Moos-Höhlenbär**, richtet sich auf (Wald/Höhle) · **Panzerbär** mit Steinplatten (Highlands) · **Eisbär-Koloss** (Schnee, Elite) |
| 8 | **turret / nest / plant** (static) | neues Skelett, 1–4 Knochen | Spawner | **Insekten-Brutnest**, spawnt Ameisen (Wald/Höhle) · **Sporen-Pilzturm**, schießt Sporen (Sumpf) · **Kristall-Geschütz** (Höhle) · **Schnappfalle-Pflanze** (Sumpf) |
| 9 | **slime / aberration** (amorph) | neues Skelett, sehr billig | 3,4 % | **Säureschleim**, teilt sich beim Tod (Sumpf/Höhle) · **Blutklumpen** (Krypta) · **Fleischmasse mit Mäulern** (Abyss, Elite) |
| 10 | **frog** (quadruped) | Skelett vorhanden | 3,0 % | **Sumpfkröte** mit Zungenschlag (Sumpf) · **Giftfrosch**, spuckt (Wald) · **Schlinger-Riesenkröte** (Sumpf, Elite) |
| 11 | **badger / porcupine** (quadruped) | Skelett vorhanden | 2,2 % | **Stachelwühler**, gräbt sich ein und verschießt Stacheln (Wüste/Highlands) · **Höhlengräber** mit Grabkrallen (Höhle) |
| 12 | **monkey** (quadruped) | Skelett vorhanden | 1,7 % | **Klippenaffen-Rudel**, wirft Steine (Highlands) · **Dschungel-Kreischer** (Wald) |
| 13 | **viper** (legless) | Skelett vorhanden | (in cobra) | **Dünenviper**, Schlag aus der S-Kurve, gräbt sich ein (Wüste) · **Sumpfnatter** (Sumpf) |
| 14 | **broodmother** (hexapod) | Skelett vorhanden | Boss | **Brutkönigin** der Insekten, legt Brut (Höhle/Wald, Boss) |
| 15 | **treant** (upright) | mit golem | 2,1 % | **Moor-Baumhüter** mit Wurzel-Slam (Sumpf/Wald) · **Dornen-Treant**, verdorrt (Wald, Elite) |
| 16 | **centipede** (legless) | Skelett vorhanden | – (Alleinstellung) | **Riesenläufer** mit Giftklauen (Höhle) |

## 3. Empfohlene Reihenfolge (Kurzfassung)

1. Erst die offenen 11 fertigstellen. Die meisten nutzen vorhandene Skelette; neu sind nur die Muster spider, beetle, tortoise, boar, hyena, sandworm, behemoth, gorilla und mantis. Für den Flesh Titan kommt `upright` dazu.
2. **upright** mit Golem + Flesh Titan zusammen bauen: ein neues Skelett für die größte Lücke.
3. **wraith + orb** auf dem vorhandenen Schwebe-Skelett (Void Harbinger passt dazu).
4. **winged** mit bird, danach bat/drake: bisher gibt es kein einziges Flugwesen mit Wirbelskelett.
5. leopard + bear auf dem fertigen Vierbeiner-Skelett.
6. static (Spawner, Fallen) und slime: billig, großer Spielwert.

## 4. Hinweis zur Menge
Ziel sind 50–100 Basis-Monster mit je 5–6 Biom-Varianten oder Elite-Addons. Wählt der Nutzer pro Rang 1–2 Vorschläge, kommen zu den 20 etwa 20–25 dazu. Das ergibt ~40–45 Basis-Monster auf 12 Skeletten und ~30 Mustern, also ≈ 250 Gegnertypen ohne neue Tripo-Läufe für die Varianten.

## 5. Gewählt (2026-11-18)

Der Nutzer hat Claude die Auswahl überlassen: **je Zeile genau eine Kreatur**, für alle 16 sind Ordner, `creature.toml` und `prompts.md` angelegt (`creatures/<id>/`). Kriterien: coolste Idee, gut lesbar von schräg oben (Silhouette + Oberseite), Stil Artist B, und **Abwechslung der Heimat-Biome** über alle Kreaturen – die neuen gehen bewusst in Biome, die bisher leer waren. Keine PoE-Namen oder -Designs übernommen.

**Ohne Concept Art:** Stufe 1 entwirft das Design aus der Beschreibung (`look`) + Stil-Referenz. Das Design-Bild ist der Design-Entwurf: **du prüfst es** und lässt es ggf. neu generieren (siehe `prompts.md` der Kreatur).
Alle Daten (Beschreibung, Pose, Rolle, Varianten, Naturvorbilder): `creatures/roster.toml`. Biome: `templates/biomes.toml`.

| Zeile | Kreatur | Muster | Bauplan | Heimat-Biom | Rolle | Kurzbeschreibung | Varianten (Grundform · 4 Biome · Elite) |
|---:|---|---|---|---|---|---|---|
| 1 | **Geode Golem** (`geode_golem`) | upright/golem | upright | Kristall | Nahkampf (Tank) | Aufgeplatzter Fels-Golem, Kristall-Krone auf Rücken/Schultern, Doppelfaust-Slam. | Deepstone Golem (Höhle) · Ember Golem (Vulkan) · Rime Golem (Eis) · Ruin Golem (Tempel/Ruinen) · Geode Colossus (×1.5) |
| 2 | **Tomb Shroud** (`tomb_shroud`) | floater/wraith | floater | Krypta | Nahkampf (Assassine, Teleport) | Schwebende Grabtuch-Kapuze mit Knochenmaske und langen Klauenarmen, kein Unterleib. | Drowned Shroud (Küste) · Ash Shroud (Vulkan) · Sand Shroud (Wüste) · Rime Shroud (Eis) · Shroud Lord (×1.4) |
| 3 | **Idol Eye** (`idol_eye`) | floater/orb (eye) | floater | Tempel/Ruinen | Fernkampf (Strahl) | Steinernes Tempel-Idol, wie eine Blüte aufgeklappt um ein lebendes Riesenauge, schießt einen Strahl. | Overgrown Idol (Dschungel) · Prism Eye (Kristall) · Grave Eye (Krypta) · Void Idol (Abyss) · High Idol (×1.5) |
| 4 | **Bonepicker Vulture** (`bonepicker_vulture`) | winged/bird | winged | Gras/Steppe | Schwarm (kreist, Sturzflug) | Zerzauster Steppengeier mit kahlem roten Hals, breite gefingerte Flügel, kreist und stößt herab. | Dune Vulture (Wüste) · Crag Vulture (Highlands) · Plague Vulture (Sumpf) · Snow Vulture (Schnee) · Kingpicker (×1.4) |
| 5 | **Cinder Wyvern** (`cinder_wyvern`) | winged/drake | winged | Vulkan | Elite (landet zum Kämpfen, Feueratem) | Schwere Basalt-Wyvern mit Flügel-Armen, Lavaplatten und Steinkeule am Schwanz, Feueratem. | Frost Wyvern (Eis) · Venom Wyvern (Dschungel) · Storm Wyvern (Highlands) · Dune Wyvern (Wüste) · Elder Cinder Wyvern (×1.6) |
| 6 | **Umbral Panther** (`umbral_panther`) | quadruped/leopard | quadruped | Dschungel | Nahkampf (Assassine, Sprung aus dem Hinterhalt) | Blauschwarzer Dschungel-Panther mit Säbelzähnen und Knochenblatt-Kamm, Sprung aus dem Hinterhalt. | Rime Panther (Schnee) · Dune Panther (Wüste) · Grave Panther (Krypta) · Void Panther (Abyss) · Panther Matriarch (×1.35) |
| 7 | **Rimehide Bear** (`rimehide_bear`) | quadruped/bear | quadruped | Eis | Elite (Tank, richtet sich auf) | Gletscherbär mit festgefrorenen Eisplatten als Rüstung, richtet sich zum Doppelschlag auf. | Mossback Bear (Wald) · Cave Bear (Höhle) · Slagback Bear (Vulkan) · Cragplate Bear (Stein) · Elder Rimehide (×1.5) |
| 8 | **Sporecap Mortar** (`sporecap_mortar`) | static/turret (spore) | static | Pilzwald | Fernkampf (stationär, Bogenschuss) | Verwurzelter Riesenpilz mit Mörser-Öffnung im Hut, schießt Sporenbomben im Bogen. | Bog Mortar (Sumpf) · Glowcap Mortar (Höhle) · Grave Mortar (Krypta) · Bloom Mortar (Dschungel) · Mother Cap (×1.5) |
| 9 | **Bog Ooze** (`bog_ooze`) | amorph/slime | amorph | Sumpf | Schwarm (teilt sich beim Tod) | Trüber Sumpfschleim mit halbverdauten Knochen im Inneren, teilt sich beim Tod. | Cave Ooze (Höhle) · Magma Ooze (Vulkan) · Blood Ooze (Krypta) · Frost Ooze (Eis) · Ooze Mother (×1.6) |
| 10 | **Oasis Gulper** (`oasis_gulper`) | quadruped/frog | quadruped | Oase | Nahkampf/Kontrolle (Zungenschlag zieht heran) | Riesige türkise Oasen-Kröte mit Riesenmaul und Seerosen auf dem Rücken, Zungenschlag zieht heran. | Mire Gulper (Sumpf) · Venom Gulper (Dschungel) · Pale Gulper (Höhle) · Ember Gulper (Vulkan) · Great Gulper (×1.5) |
| 11 | **Quillback Burrower** (`quillback_burrower`) | quadruped/badger (porcupine) | quadruped | Stein | Fernkampf (gräbt sich ein, Stachel-Salve) | Dachsartiger Gräber mit Stachelmantel und Grabkrallen, taucht auf und verschießt Stacheln. | Dune Burrower (Wüste) · Frost Burrower (Eis) · Shard Burrower (Kristall) · Thatch Burrower (Gras/Steppe) · Quill Alpha (×1.4) |
| 12 | **Ruin Howler** (`ruin_howler`) | quadruped/monkey | quadruped | Tempel/Ruinen | Schwarm/Fernkampf (Rudel, wirft Steine) | Hagerer Tempelaffe mit Mandrill-Gesicht und eingewachsenen Goldringen, Knöchelgang, wirft Steine. | Canopy Howler (Dschungel) · Crag Howler (Highlands) · Snow Howler (Schnee) · Ash Howler (Vulkan) · Howler Chieftain (×1.4) |
| 13 | **Tallgrass Viper** (`tallgrass_viper`) | legless/viper | serpentine | Gras/Steppe | Nahkampf (Hinterhalt, Schlag aus der S-Kurve) | Strohgelbe Hornviper mit Zickzack-Rücken und Rassel, Schlag aus der S-Kurve. | Dune Viper (Wüste) · Marsh Viper (Sumpf) · Emerald Viper (Dschungel) · Ash Viper (Vulkan) · Viper Queen (×1.5) |
| 14 | **Mound Queen** (`mound_queen`) | hexapod/broodmother | hexapod | Dschungel | Boss (legt Brut) | Termiten-Königin: kleiner Panzerkörper, riesiger heller Eier-Hinterleib, ruft Brut. | Deep Queen (Höhle) · Sand Queen (Wüste) · Spore Queen (Pilzwald) · Void Queen (Abyss) · Hive Empress (×1.3) |
| 15 | **Bog Warden** (`bog_warden`) | upright/treant | upright | Sumpf | Elite (Tank, Wurzel-Slam) | Wandelnder Sumpfbaum mit Wurzelbeinen, Hohlgesicht und moosbehangener Krone, Wurzel-Slam. | Thorn Warden (Wald) · Strangler Warden (Dschungel) · Frost Warden (Schnee) · Charred Warden (Vulkan) · Elder Warden (×1.5) |
| 16 | **Gloomfang Centipede** (`gloomfang_centipede`) | legless/centipede | serpentine | Höhle | Nahkampf (schnell, Giftklauen) | Blutroter Höhlen-Riesenläufer mit Bernstein-Beinsaum und Giftklauen. | Magma Centipede (Vulkan) · Dune Centipede (Wüste) · Shard Centipede (Kristall) · Jungle Centipede (Dschungel) · Gloomfang Matriarch (×1.5) |

### Heimat-Biome über alle 37 Kreaturen

(36 in `roster.toml` + Chitin Crawler, der dort nicht steht)

| Biom | Anzahl | Kreaturen |
|---|---:|---|
| Wald | 4 | Chitin Crawler, Spore Drone, Needle Wasp, Broodling |
| Küste | 4 | Reef Snapper, Shore Lurker, Shellback, Eel Stalker |
| Highlands | 4 | Ravine Stalker, Stone Boar, Hollow Stag, Rock Hyena |
| Wüste | 4 | Sand Leviathan, Dune Raptor, Glassback Colossus, Scorpion Matriarch |
| Schnee | 1 | Frost Colossus |
| Abyss | 4 | Flesh Titan, Void Manifestation, Void Harbinger, Reality Ripper |
| Höhle | 1 | Gloomfang Centipede |
| Vulkan | 1 | Cinder Wyvern |
| Sumpf | 2 | Bog Ooze, Bog Warden |
| Krypta | 1 | Tomb Shroud |
| Gras/Steppe | 2 | Bonepicker Vulture, Tallgrass Viper |
| Stein | 1 | Quillback Burrower |
| Kristall | 1 | Geode Golem |
| Tempel/Ruinen | 2 | Idol Eye, Ruin Howler |
| Oase | 1 | Oasis Gulper |
| Dschungel | 2 | Umbral Panther, Mound Queen |
| Pilzwald | 1 | Sporecap Mortar |
| Eis | 1 | Rimehide Bear |

### Neue Baupläne (Bild-Pose, `templates/bodyplans.toml`)

- **upright**: aufrecht, Beine leicht auseinander, Arme hängen schräg vom Körper weg (Golem, Treant).
- **winged**: auf zwei Beinen, Flügel weit und symmetrisch ausgebreitet, frei vom Körper, Schwanz gerade (Geier, Wyvern).
- **floater**: schwebt waagerecht, nichts berührt den Boden, Hängendes hängt gerade und getrennt (Geist, Auge).
- **amorph**: eine kompakte, gleichmäßig gerundete Masse, nicht gestaucht/geneigt (Schleim).
- **static**: steht aufrecht auf flacher Basis, Klappen/Ranken offen und getrennt (Pilz-Mörser).

Die Skelette upright, winged, amorph, static und die meisten neuen Muster sind **noch nicht gebaut** – die Einträge sind für Bilder und Tripo vorbereitet. Reihenfolge des Baus wie in Abschnitt 3.
