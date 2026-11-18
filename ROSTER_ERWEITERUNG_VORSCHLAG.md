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
