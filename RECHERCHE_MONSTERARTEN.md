# Recherche: Monsterarten → Skelette → Bewegungsmuster

Stand 2026-11-17 · Backlog **G1** · ausgewertet: PoE-Monster-Datenbank `H:\AIProjects\poe2-MTX\beastCatalog\data\catalog.json`, **`generated_at` 2026-11-17T20:25:47Z, `schema_version` 2** (nur gelesen).
Skripte und Zwischenergebnisse: `temp/monster_research/` (Reihenfolge siehe §9). Echte Monster → Kategorie: `temp/monster_research/kategorien.csv`.

> **Inspiration, keine Kopie.** PoE dient hier nur als **Statistik**: Welche Körperformen, Größen, Rollen und Angriffsarten kommen in einem erfolgreichen Top-down-ARPG wie oft vor? Alle Archetypen unten sind **generisch** beschrieben. Es gibt keine PoE-Namen oder -Designs als Vorschlag. Die echten Monster kommen am Ende **immer aus deiner Concept Art** (CLAUDE.md). Diese Liste ist ein Orientierungsraster.

**Kurzfassung**
- **2.872 echte Monster** (aus 7.133 Einträgen). Davon sind **47 % Kreaturen**, **49 % Humanoide** (Menschen, Untote, menschenförmige Dämonen) und 4 % Objekte/Totems.
- Unsere **8 vorhandenen Skelette decken 72 % der Kreaturen ab** (Vögel/Fledermäuse/Drachen nicht mitgezählt, siehe §3).
- Mit **4 neuen Skeletten** kommen wir auf **99,9 % der Kreaturen** und **98,5 % aller Monster**: `upright` (aufrechter Zweibeiner: Brutalo/Golem/Baumwesen, Humanoid als Proportions-Variante), `winged` (Flügel = Arme: Vogel/Fledermaus/Drache), `amorph` (Schleim/Fleischmasse) und `static` (Totem/Turm/Nest/verwurzelte Pflanze).
- Die drei Muster mit dem größten Nutzen auf vorhandenen Skeletten sind **spider** (8,6 % der Kreaturen), **leopard** und **bear** (je ≈ 4 %).
- PoE selbst baut **im Schnitt 6,9 Monsternamen auf einem Modell-Ordner** auf. Das bestätigt deinen Plan „Basis-Monster × 5–6 Biom-/Elite-Varianten“.

---

## 1. Datenbasis

### 1.1 Was ist eine „Variante“, was ein „echtes Monster“?
Die Datenbank hat **7.133 Einträge**. Jeder Eintrag ist eine *Spielvariante*: dasselbe Monster als Boss, als beschworene Version, in einem Sondermodus, mit anderen Werten. Am internen Pfad (`external_id`) sieht man das an Zusätzen wie *Boss* (837 Einträge), *Standalone* (587), *Spectre* (494), *Map* (375), *Summoned* (93) usw.

**Regel (begründet mit Zahlen):** *Ein echtes Monster = ein eindeutiger, normalisierter Anzeigename.* Normalisiert heißt: Kleinschreibung, Leerzeichen zusammengefasst, `*` entfernt.

| Schritt | Einträge / Monster |
|---|---:|
| Alle Einträge | 7.133 |
| − Wiki-Bestiary-Einträge, deren Name schon bei PoEDB vorkommt (Dubletten aus einer zweiten Quelle) | − 92 |
| − Platzhalter (`is_placeholder`, Namen wie `< >`, `<<HRB…>>`) | − 69 |
| − interne Test-/DNT-Einträge („Do Not Translate“) | − 6 |
| = verwendete Einträge | **6.966** |
| → zusammengefasst nach Name = **echte Monster** | **2.872** |

Warum der Name und nicht eines der anderen Felder?
- `family` (= PoE-„Monstertyp“, **2.704** Werte) ist ein *Datentyp*, kein sichtbares Monster. **607 Namen verteilen sich auf mehrere Familien** (dasselbe Monster wurde pro Spielmodus neu angelegt). Umgekehrt tragen **370 Familien mehrere Namen** (Reskins mit gleichem Datentyp).
- `archetype` ist überall leer, `status` überall „unknown“, `taxonomy` gibt es nur bei den 102 Wiki-Einträgen.
- Fasst man Name **und** Familie zu Gruppen zusammen, bleiben **1.923** Gruppen. Das ist zu grob, weil damit z. B. verschiedene Tiere eines Datentyps verschmelzen.
- **Neu seit `schema_version` 2:** Die Datenbank liefert jetzt selbst eine Gruppierung (`creatures` mit `variant_ids`, dazu `monsters[].creature_id`). Sie zählt **2.902 Kreaturen**, davon 18 Platzhalter. Ihre Regel ist ebenfalls der normalisierte Name. Unterschiede zu unserer Zählung: Sie behält 6 DNT-Testeinträge, und 6 Wiki-Namen mit Sternchen („… *“) zählt sie doppelt. **2.902 − 18 − 6 − 6 = 2.872**: Das Skript prüft das automatisch, die Mengen sind identisch (`matches_own_rule = True`). Die CSV enthält deshalb die `creature_id`.

Verteilung „Einträge pro echtem Monster“: 1.350 Monster haben nur 1 Eintrag, 618 haben 2, 372 haben 3, 267 haben 4, und 28 Monster haben 15 oder mehr.

**Noch strengere Zählung (zur Info):** 348 der 2.872 Namen sind reine *Präfix-Varianten*. Das heißt, der Name ohne das erste Wort existiert ebenfalls, z. B. „Verseuchte X“ zu „X“ oder „Unvollkommene X“ zu „X“. Zieht man sie ab, bleiben **≈ 2.520 Grundmonster**. Für Statistiken nutze ich weiter 2.872, weil auch die Präfix-Varianten oft eigene Fähigkeiten haben.

**Wie viele 3D-Körper stecken dahinter?** Die 2.872 Monster liegen in nur **415 Modell-Ordnern** (Pfad-Ordner der Metadaten). Das sind **≈ 6,9 Namen pro Grundkörper**. Genau dieses Prinzip planen wir: Basis-Monster plus Varianten über Tönung, Anbauteile und Slider (§6.2).

### 1.2 Datenqualität
| Feld | gefüllt (Einträge) | Bemerkung |
|---|---:|---|
| `leg_count`, `arm_count`, `wing_pairs`, `tentacle_count`, `size_class`, `posture`, `silhouette`, `body_mass`, `surface_type`, `special_mechanics`, `native_biome` … | **0 %** | Anatomie-Felder sind im Schema angelegt, aber **leer** |
| `body_plan` | 41 % | kennt praktisch nur den Wert „Humanoid“ (aus dem Tag `humanoid`) |
| `species_class` | 66 % | grob (Humanoid/Construct/Demon/Mammal/Insect/Reptile/Bird/Amphibian) |
| `model_height_class` | 68 % | 8 Stufen, wird zu unseren Größen umgerechnet |
| `spawn_biome` | 15 % (730 von 2.872 Monstern) | aus Fundorten abgeleitet, Verlies/Tempel überwiegen |
| `movement_type` | 0,8 % | unbrauchbar, Ersatz: Tag `flying` und Fähigkeiten |
| `encounter_role` | 2,7 % | Ersatz: Boss-Tags + Namensmuster |
| `movement_speed_class` | 94 % | gut |
| `tags` (Quell-Tags), Pfad, Fähigkeiten-IDs | ≈ 100 % | **Hauptquelle** für die Einordnung |
| `quality.completeness` | 0,08–0,26 | Datenbank selbst sagt: großteils unvollständig |

Seit dem Neuladen haben sich **keine Werte geändert**: Alle 7.133 Einträge haben dieselben Attribute, Tags und Namen. Neu sind nur `schema_version`, `schema.version`, `schema.entities`, das Top-Level-Feld `creatures`, `monsters[].creature_id` und die Kennzahlen `creature_count`/`variant_count` im `snapshot`.

### 1.3 Wie ich die Körperform bestimmt habe (Annahme, regelbasiert)
Weil die Anatomie-Felder leer sind, ordnet `10_classify.py` jedes Monster **semantisch** zu. Das läuft in zwei Durchgängen:
1. **Nur der Modell-Ordner/Pfad**, weil er am verlässlichsten die Tierart nennt (z. B. Ordner für Spinnen, Krabben, Raubkatzen). Variantenwörter wie „befallen“, „Tentakel-Addon“ oder „auftauchend“ zählen hier nicht.
2. Bei unklarem Pfad zusätzlich **Name + Quell-Tags** (z. B. `canine_beast`, `spider`, `crustacean_beast`, `golem`, `liquid_armour`, `flying`, `humanoid`, `skeleton`).

Pro Monster gilt der **Mehrheitsentscheid** über seine Einträge (bei 324 Monstern sind die Einträge uneinig).
**Genauigkeit (Stichprobe 2 × 60 zufällige Monster, von Hand geprüft): ca. 9 von 10 plausibel.** Typische Fehler sind Bosse mit Fantasienamen, Varianten mit Fremd-Addons (z. B. Schlange mit Wurm-Eigenschaften) und Dämonen ohne Bauplan-Tag. Letztere stehen als eigene Kategorie „Dämon (Bauplan unklar, vermutlich aufrecht)“ in den Tabellen. **Alle Prozentwerte sind daher ± einige Prozentpunkte.**

---

## 2. Verteilung der echten Monster (n = 2.872)

### 2.1 Grobe Gruppen
| Gruppe | Anzahl | % |
|---|---:|---:|
| Humanoide (Menschen, Untote, humanoide Dämonen) | 1.397 | 48,6 % |
| **Kreaturen** (Tiere, Bestien, Konstrukte, Aberrationen) | **1.359** | **47,3 %** |
| Objekte/Totems/unklar | 116 | 4,0 % |

→ PoE ist zur Hälfte humanoid, unser Spiel zu ~90 % Kreatur. **Für uns zählt vor allem die Kreaturen-Hälfte (n = 1.359)**, die meisten Tabellen zeigen deshalb beide Werte.

### 2.2 Nach Bauplan (= unser Skelett) und Beinzahl
| Bauplan / Skelett | Beine (Fake-it-Standard) | alle | % alle | Kreaturen | % Kreaturen |
|---|---|---:|---:|---:|---:|
| humanoid (aufrecht, menschlich) | 2 + 2 Arme | 1.377 | 47,9 % | 36 | 2,6 % |
| quadruped (Vierbeiner) | 4 | 355 | 12,4 % | 355 | 26,1 % |
| biped_brute (schwerer Zweibeiner: Golem, Brutalo, Baumwesen) | 2 + 2 Arme | 274 | 9,5 % | 218 | 16,0 % |
| octopod (Spinne, Krabbe) | 8 | 199 | 6,9 % | 199 | 14,6 % |
| floater (schwebt: Geist, Orb, Tentakel) | 0 | 171 | 6,0 % | 171 | 12,6 % |
| hexapod (Insekt) | 6 | 103 | 3,6 % | 103 | 7,6 % |
| winged (Vogel, Fledermaus, Drache) | 2 + Flügelarme | 80 | 2,8 % | 80 | 5,9 % |
| static (Totem, Turm, Nest, Pflanze) | 0 | 76 | 2,6 % | – | – |
| legless (Schlange, Wurm) | 0 | 73 | 2,5 % | 73 | 5,4 % |
| biped_raptor (Laufvogel/Raptor, waagerecht) | 2 | 48 | 1,7 % | 48 | 3,5 % |
| amorph (Schleim, Fleischmasse) | 0 | 46 | 1,6 % | 46 | 3,4 % |
| multileg (Skorpion) | 8 + Scheren + Schwanz | 24 | 0,8 % | 24 | 1,8 % |
| flyer (Insekt mit Flügeln) | 6 | 4 | 0,1 % | 4 | 0,3 % |
| swimmer (Fisch) | 0 | 2 | 0,1 % | 2 | 0,1 % |
| kein Skelett (Objekt/Effekt) / unklar | – | 40 | 1,4 % | – | – |

Beinzahl zusammengefasst, nur Kreaturen: **0 Beine 21 %** (schweben, kriechen, Schleim), **2 Beine 28 %**, **4 Beine 26 %**, **6 Beine 8 %**, **8 Beine 16 %**.

### 2.3 Nach Fortbewegung (aus Bauplan + Tags + Fähigkeiten)
| Fortbewegung | Kreaturen (ca.) | % Kreaturen |
|---|---:|---:|
| Laufen auf 4 Beinen | 355 | 26 % |
| Krabbeln auf 6–8 Beinen (inkl. Skorpion) | 326 | 24 % |
| Aufrecht gehen/stampfen | 254 | 19 % |
| Schweben (kein Bodenkontakt) | 171 | 13 % |
| Fliegen mit Flügeln | 84 | 6 % |
| Schlängeln/Graben | 73 | 5 % |
| Rennen auf 2 Beinen (waagerecht) | 48 | 4 % |
| Gleiten/Hüpfen (Schleim) | 46 | 3 % |

Weitere Werte, **alle Monster**:
- **Tempo:** mittel 33 %, sehr langsam 26 %, langsam 17 %, schnell 16 %, sehr schnell 4 %.
- **Auftauchen** (aus dem Boden, der Decke oder einem Nest; Fähigkeit „emerge/burrow/ambush“): **14 %**. → Unser **Spawn-Clip** (MOVESET #17) ist kein Luxus.

### 2.4 Nach Größe
| Größe | alle | % | Kreaturen | % |
|---|---:|---:|---:|---:|
| Winzig | 334 | 11,6 % | 301 | 22,1 % |
| Klein | 242 | 8,4 % | 212 | 15,6 % |
| Mittel | 1.394 | 48,5 % | 441 | 32,5 % |
| Groß | 226 | 7,9 % | 115 | 8,5 % |
| Riesig | 81 | 2,8 % | 50 | 3,7 % |
| unbekannt | 595 | 20,7 % | 240 | 17,7 % |

→ **Kreaturen sind viel öfter klein bis winzig (38 %) als Humanoide.** Spinnen, Krabben, Insekten und Schlangen sind überwiegend „winzig“. Das sind die **Schwarm-Monster**. Sie brauchen ein knappes Polygon-Budget und später ggf. Vertex Animation Textures. VAT heißt: Die Animation wird in eine Textur gebacken, und die Grafikkarte spielt sie für Hunderte Kopien ab, ohne Skelett-Rechnung.

### 2.5 Nach Kampfrolle
| Rolle | alle | % | Kreaturen | % |
|---|---:|---:|---:|---:|
| Nahkampf | 1.537 | 53,5 % | 802 | 59,0 % |
| Boss/Unique (eindeutige Namen, Boss-Tags) | 463 | 16,1 % | 186 | 13,7 % |
| Fernkampf | 413 | 14,4 % | 118 | 8,7 % |
| Hybrid (beides) | 257 | 8,9 % | 146 | 10,7 % |
| Elite (Alpha, Matriarchin, Anführer …) | 93 | 3,2 % | 30 | 2,2 % |
| Schwarm (winzig + Selbstexplosion/Auftauchen/Beschworen) | 71 | 2,5 % | 71 | 5,2 % |
| Beschwörer | 38 | 1,3 % | 6 | 0,4 % |

**Angriffsmechaniken** (aus den Fähigkeiten-IDs, Mehrfachnennung, alle Monster):

| Mechanik | Anteil |
|---|---:|
| Projektil | 28 % |
| Stampfen/Slam | 16 % |
| Auftauchen | 14 % |
| Beschwören | 11 % |
| Explodieren | 9 % |
| Ansturm | 8 % |
| Teleport | 7 % |
| Sprung | 6 % |
| Strahl/Atem | 5 % |
| Wirbel | 4 % |

**Was die Mechaniken je Muster zeigen:**
- **Fernkampf ist überall wichtig.** Schlangen schießen zu 51 %, Echsen zu 70 %, Skorpione zu 42 %. Das bestätigt die Entscheidung „Fernkampf = Variante von Attack 2“ (MOVESET).
- **Ansturm** dominiert bei Laufvögeln/Raptoren (54 %) und Rammbestien (60 %).
- **Sprung** dominiert bei Fröschen (61 %).
- **Stampfen** prägt die Brutalos (44 %).

### 2.6 Biome (nur 730 Monster mit Angabe, Mehrfachnennung)
| Biom | Anteil |
|---|---:|
| Verlies | 43 % |
| Tempel | 37 % |
| Höhle | 25 % |
| Gebirge | 21 % |
| Küste | 19 % |
| Wald | 16 % |
| Ozean | 6 % |
| Untergrund | 6 % |
| Krypta | 5 % |
| Wüste | 4 % |
| Sumpf | 4 % |
| Fluss | 4 % |
| Mine | 4 % |
| Schnee | 2 % |

PoE ist stark „Innenraum“. Für unser Spiel sind die Biome aus der Concept Art maßgeblich (Wald, Küste, Highlands, Wüste, Schnee, Abyss).
**Beleg für unser Varianten-Schema:** Ein PoE-Spielmodus vergibt **4 Regions-Präfixe** (Wildnis, Höhle, Wüste, Tiefsee) auf **denselben Grundkörpern**: 45 + 21 + 15 + 27 = 108 Namen. Ein anderer Modus nutzt 3 Farb-Präfixe (je ≈ 15–20 Namen) für dieselben Tiere. Biom-Varianten über Präfix + Tönung sind also gängige Praxis.

---

## 3. Abbildung auf unsere 3D-Kategorien

Begriffe:
- **Skelett** = Knochen-Standard eines Bauplans.
- **Muster** = wie sich ein Tiertyp bewegt und kämpft (motions/README.md).

### 3.1 Vorhandene Skelette: Abdeckung
| Skelett (vorhanden) | Muster gebaut | Monster | % alle | % Kreaturen |
|---|---|---:|---:|---:|
| quadruped | wolf, lizard, deer | 355 | 12,4 % | 26,1 % |
| octopod | crab | 199 | 6,9 % | 14,6 % |
| floater | tentacle | 171 | 6,0 % | 12,6 % |
| hexapod | ant | 103 | 3,6 % | 7,6 % |
| legless | cobra | 73 | 2,5 % | 5,4 % |
| biped_raptor | raptor | 48 | 1,7 % | 3,5 % |
| multileg | scorpion | 24 | 0,8 % | 1,8 % |
| flyer | wasp | 4 (+80 Wirbeltier-Flieger, s. u.) | 0,1 % | 0,3 % |
| **Summe** | 10 Muster | **977** | **34,0 %** | **71,9 %** |

Hinweis zu *flyer*: Unser flyer-Skelett ist ein **Insekt mit Flügeln** (Wespe). Vögel, Fledermäuse und Drachen haben **Flügel statt Arme**, dazu Beine und meist einen Schwanz. Das ist eine andere Knochenkette. Ich zähle sie deshalb als eigenes Skelett `winged`. Rechnet man sie trotzdem zu *flyer*, decken die 8 vorhandenen Skelette 36,8 % aller und 77,8 % der Kreaturen ab.

### 3.2 Fehlende Skelette, sortiert nach Nutzen
„Fake it“-Regel: lieber **wenige Skelette, die viel abdecken**. Deshalb fasse ich zusammen, wo es geht.

| Rang | Neues Skelett | deckt ab | + Kreaturen | kumuliert Kreaturen | + alle | kumuliert alle | Fake-it-Hinweis |
|---|---|---|---:|---:|---:|---:|---|
| – | *vorhanden (8)* | | 977 | 71,9 % | 977 | 34,0 % | |
| **1** | **upright** (aufrechter Zweibeiner, schwer) | Golem/Konstrukt, Brutalo, Fleischkoloss, Baumriese, aufrechte Bestie (Werwolf-/Bockartig), Gorilla im Angriff | 218 | **87,9 %** | 274 | 43,6 % | Knochennamen **Unity-Humanoid-kompatibel** anlegen → fertige Clips (Mixamo/Asset Store) als Vorlage für Stampfen/Schlagen nutzbar (ROADMAP §6: erlaubt) |
| **2** | **winged** (Flügel = Arme) | Vogel, Fledermaus, Drache/Wyvern, Gargoyle, geflügelter Dämon | 80 | **93,8 %** | 80 | 46,3 % | **Ein** Skelett: Rumpf, Hals/Kopf, 2 Beine, 2 Flügelketten, Schwanz. Vogel = Schwanz kurz, Fledermaus = Beine klein, Drache = alles groß |
| **3** | **amorph** (Schleim/Fleischmasse) | Schleim, Blut-/Wasserelementar, Fleischklumpen mit Mäulern | 46 | **97,2 %** | 46 | 50,6 % | 3–5 Knochen (Basis, Mitte, Kopf/Deckel) + Squash & Stretch (Stauchen und Dehnen) per Skalierung, sehr billig |
| **4** | **static** (verwurzelt/stationär) | Totem, Turm/Geschütz, Brutnest/Eiersack, Giftpflanze, Kristall-Spawner | – | 97,2 % | 76 | 49,0 % (vor amorph gerechnet) | 1–4 Knochen (Basis, Hals/Kopf, Klappe). Wichtig fürs ARPG: Spawner, Nester, Fallen |
| 5 | **humanoid** = *Proportions-Variante von upright* | Menschen, Skelette, Zombies, Kultisten | 36 | 99,9 % | 1.377 | **98,5 %** | Kein eigenes Skelett: upright mit menschlichen Proportionen. Für uns selten (Kultisten, Untote als Biom-Thema) |
| 6 | swimmer (Fisch) | Fisch/Hai | 2 | 100 % | 2 | 98,6 % | **Nicht bauen.** In der Datenbank fast nicht vorhanden. Falls doch nötig: legless + Flossen (Variante „eel“) oder floater (Fisch schwebt durch die Luft, Fake it) |

Weitere Kandidaten aus deiner Liste, mit Zahlen geprüft:
- **Tausendfüßer**: In der Datenbank 0 Treffer. Lösung: **legless/centipede** als Muster (Kette + kurze Beinpaare mit Welle). Kein eigenes Skelett; die Beine hängen als einfache Knochen an der Kette.
- **Schwarm** (Fliegenwolke, Rattenteppich): 71 Schwarm-Kreaturen in den Daten, aber sie sind einzelne kleine Tiere. **Kein Skelett**; wir verwenden das jeweilige Tier-Skelett plus VAT, oder Partikel für echte Wolken.
- **Konstrukt/Golem** → in **upright** enthalten (175 Monster, das größte einzelne Kreatur-Muster überhaupt).
- **Pflanze/verwurzelt** → **static** (unbeweglich) bzw. **upright/treant** (wandelnder Baum, 28 Monster).
- **Schwerer Brute/Gorilla**: Der aufrechte Brutalo gehört zu **upright**. Der vierbeinige Knöchelgänger bleibt **quadruped/gorilla** (Roster: Frost Colossus).

Ergebnis: **12 Skelette** (8 vorhanden + upright, winged, amorph, static) tragen ≈ 99,9 % der Kreaturen und 98,5 % aller Monster.

---

## 4. Lange Liste der Bewegungsmuster

Regel aus `motions/README.md`:
- **Variante**, wenn sich das Tier nach denselben Regeln mit anderen Werten bewegt (Beinzahl, Tempo, Haltung).
- **Eigenes Muster**, wenn Gang, Koordination oder **Angriffsmechanik** grundsätzlich anders sind.

Spalte „Monster“ = echte Monster in der Datenbank. „–“ heißt: kommt in PoE nicht oder kaum vor. Das ist auch eine Chance, sich abzuheben.

### quadruped (vorhanden: wolf ✅, lizard ✅, deer ✅)
| Muster | Status | Kern-Unterschied (Gang · Koordination · **Angriff**) | Monster | Naturvorbild (Video suchen) |
|---|---|---|---:|---|
| **wolf** | ✅ | Trab/Galopp, Biss nach Anlauf. Varianten: hyena (abfallender Rücken), **hellhound** (+ Atem-Projektil), **rat** (winzig, Schwarm) | 73 | Wolf (Muybridge), Tüpfelhyäne, Wanderratte |
| **leopard** | neu | Schleichen geduckt, **Sprung-Angriff (Pounce, Root Motion)**, Prankenhieb; Varianten: Löwe (Elite, Brüllen) | 57 | Leopard/Gepard auf der Pirsch, Hauskatze springt |
| **bear** | neu | Passgang schwer, **Aufrichten auf Hinterbeine + Prankenhieb/Doppelschlag**, Stampfer (eigene Koordination: Wechsel vier- ↔ zweibeinig) | 53 | Braunbär richtet sich auf, Grizzly-Angriff |
| **frog** | neu | Ruhe → **Sprung** (Hüpf-Fortbewegung statt Gang), **Zungenschlag** als Fernkampf-Nahkampf | 41 | Ochsenfrosch springt, Chamäleon-Zunge (Zeitlupe) |
| **lizard** | ✅ | gespreizter Gang, Seitwärtsschwingen, Schnappbiss. Varianten: lurker (flach, Hinterhalt), **spitter** (Gift spucken, 70 % Projektil!) | 30 | Waran, Krokodil, Speikobra (Spuck-Timing) |
| **badger** | neu | niedrig, watschelnd, **Graben/Auftauchen**, Krallen. Variante **porcupine**: Stacheln aufstellen + verschießen | 30 | Honigdachs, Stachelschwein droht |
| **monkey** | neu | **Hüpfen/Klettern, Vierfüßer ↔ Zweifüßer**, Werfen (Projektil), Rudel-Gekreisch | 23 | Pavian-Trupp, Schimpanse wirft |
| **boar** | Roster | stämmiger Trab, **Ansturm + Hauer-Stoß** (60 % Ansturm). Variante: bull/rhino (Kopf-Ramme) | 20 | Wildschwein-Angriff, Nashorn-Ansturm |
| **gorilla** | Roster | **Knöchelgang**, im Angriff aufrecht: Brusttrommeln, Doppelfaust-Slam | 18 | Gorilla Knöchelgang/Display |
| **deer** | ✅ | Prellsprünge, Geweih-Stoß. Variante **ram** (Steinbock: Anlauf + Kopfstoß) | 5 | Hirsch-Brunft, Steinbock-Kampf |
| **tortoise** | Roster | sehr langsam, Kopf einziehen (Block), Schnapp-Biss | 5 | Schnappschildkröte |
| **behemoth** | Roster | Elefanten-Passgang, Stampf-AoE, Rammen | (in boar/bear) | Elefant, Nashorn |

### octopod (vorhanden: crab ✅)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **spider** | geplant (Broodling) | 8 Laufbeine, alternierender Vierfuß, **Sprungbiss**. Varianten: **web** (Netz-Projektil, verlangsamt), **spitter** (Giftspucke), **brood** (Eiersack, spawnt) | 117 | Springspinne (Zeitlupe), Wolfsspinne mit Jungen, Speispinne |
| **crab** | ✅ | Seitwärtsgang, Scheren-Angriff. Varianten: **mortar** (Krebs, der Brocken/Säure im Bogen schießt; Fernkampf in 29 %), **shell** (Einsiedler, versteckt sich), **hand** (Aberration: krabbelt auf Fingern) | 82 | Winkerkrabbe, Pistolenkrebs, Einsiedlerkrebs |

### hexapod (vorhanden: ant ✅)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **ant** | ✅ | Dreifuß, Mandibel-Biss, Säure. Varianten: beetle (schwer), **larva** (winzig, explodiert), **hopper** (Sprung-Insekt) | 90 | Ameise, Mistkäfer, Heuschrecke |
| **broodmother** | neu | sehr groß, langsam, **Hinterleib legt/spawnt Brut** (77 % Beschwören, 92 % Projektil), kaum Gang | 13 | Termitenkönigin, Bienenkönigin legt Eier |
| **mantis** | Roster | auf 4 Beinen, **Fangschlag** mit Sensen, Wiegen | – | Gottesanbeterin (Zeitlupe) |

### multileg (vorhanden: scorpion ✅)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **scorpion** | ✅ | Scheren + Stich über den Rücken. Variante **tail_shooter** (Stachel als Projektil; Fernkampf 42 %) | 24 | Skorpion-Stich, Peitschenskorpion sprüht |

### legless (vorhanden: cobra ✅)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **cobra** | ✅ | aufgerichtet, Schild, Biss von oben. Varianten: eel (Roster), **spitter** (Giftstrahl; 55 % Projektil!) | 51 | Kobra, Speikobra, Muräne |
| **viper** | neu | flach, **seitliches Schlängeln, Schlag aus der S-Kurve** (Lauer-Angriff, schnell) | (in cobra) | Klapperschlange schlägt (Zeitlupe), Seitenwinder |
| **sandworm** | Roster | Ziehharmonika-Gang, **Abtauchen/Auftauchen** (68 % Auftauchen), Verschlingen | 22 | Regenwurm, Sandboa, Python (rectilinear) |
| **centipede** | neu (optional) | Kette + viele Beinpaare in **metachroner Welle**, Biss mit Giftklauen | – | Riesenläufer (Scolopendra) |

### floater (vorhanden: tentacle ✅)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **tentacle** | ✅ | Schweben + Tentakelwellen, Tentakelpeitsche. Variante **jelly** (Qualle: Pulsieren, Elektro-AoE) | 42 | Oktopus, Qualle, Kalmar |
| **wraith** | neu | **Oberkörper mit Armen, kein Unterleib**, gleitet, Klauenhieb/Zauber, Teleport (17 %) | 82 | Schleierschwanz-Fisch (Stoff-Wehen), Rochen-Flossenwelle; Rest: Stoff-Simulation |
| **orb** | neu (fast Variante) | starre Kugel/Auge/Waffe, **Strahl** oder **Selbstexplosion** (17 %), kreist. Varianten: eye (Strahl), blade (animierte Klinge wirbelt), wisp (explodiert) | 47 | Kugelfisch (Aufblähen), Libelle schwebt |

### flyer (vorhanden: wasp ✅) und winged (neu)
| Muster | Skelett | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---|---:|---|
| **wasp** | flyer | ✅ | Schwebeflug, Stich-Sturzflug. Variante **swarm_fly** (Mückenwolke, VAT/Partikel) | 4 | Wespe/Hornisse Zeitlupe, Mückenschwarm |
| **bird** | winged | neu | **Kreisen + Sturzflug (Krallen)**, Landen/Starten, Federn-Projektil (33 %) | 51 | Geier kreist, Habicht stößt herab, Krähe landet |
| **bat** | winged | neu (oder Variante von bird) | flatternder Zickzack, **Schallkegel (Kontrolle)**, hängt kopfüber (Idle/Spawn) | 13 | Fledermaus Zeitlupe, Flughund |
| **drake** | winged | neu | schwer, **landet zum Kämpfen**, Feueratem (Strahl), Schwanzschlag, Gargoyle-Variante: sitzt als Statue → erwacht (Spawn) | 16 | Komodowaran + Adler (Kombi), Pelikan-Landung |

### biped_raptor (vorhanden: raptor ✅)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **raptor** | ✅ | Laufvogel-Gang, **Ansturm** (54 %), Krallentritt. Varianten: **fowl** (Hackvogel: Pick-Serie, Flattersprung), glider (Roster-Elite mit Flügeln) | 48 | Strauß, Sekretärvogel, Kampfhahn |

### upright (neu): Brutalo, Golem, Baumwesen und Humanoid als Proportions-Variante
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **golem** | neu | steif, **Stampfen + AoE-Slam**, langsame schwere Schläge, Teile lösen sich (Death zerfällt) | 175 | Elefant (Gewicht), Sumo, Stop-Motion-Golems; Mixamo „Mutant“ als Vorlage |
| **brute** | Roster (titan) | massig, **Faust-Slam/Greifen/Werfen**, Brüllen; Varianten: beastman (aufrechte Bestie, Krallen), titan | 71 | Gorilla aufrecht, Bodybuilder-Gang |
| **treant** | neu | **sehr langsam, Wurzel-Slam (Boden-AoE), Äste peitschen**, Wurzeln schlagen beim Stehen | 28 | Baum im Sturm, Elefantenrüssel (Ast-Peitsche) |
| warrior / archer / caster / zombie | nur bei Bedarf | Menschliche Clips aus Unity Humanoid/Mixamo | 917 / 116 / 265 / 79 | Mixamo, Motion-Capture |

### amorph (neu)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **slime** | neu | **Hüpfen mit Stauchen/Dehnen**, Verschlingen, **Teilen beim Tod** (kleinere Kopien) | 35 | Wassertropfen in Zeitlupe, Schleimpilz, Pudding wackelt |
| **aberration** | neu | Fleischmasse **wälzt sich**, Mäuler/Tentakel schnappen (Addon-Knochen), spuckt | 11 | Seegurke, Seeanemone schnappt, Nacktschnecke |

### static (neu)
| Muster | Status | Kern-Unterschied | Monster | Naturvorbild |
|---|---|---|---:|---|
| **turret** | neu | drehen + schießen (Projektil), kein Gang | 76 (inkl. Nest/Pflanze) | Sonnenblume folgt Licht (Dreh-Tempo), Kannenpflanze |
| **nest** | neu (Variante von turret) | pulsiert, **spawnt Schwarm** (Beschwören 22 %) | (in turret) | Wespennest, Eiersack einer Spinne |
| **plant** | neu (Variante) | Fallen schnappen (Venusfliegenfalle), Sporenwolke | (in turret) | Venusfliegenfalle (Zeitlupe), Bovist stäubt |

**Bilanz Muster:**
- **Gebaut: 10** (ant, crab, wolf, lizard, deer, raptor, cobra, tentacle, wasp, scorpion).
- **Im Roster schon geplant: 8** (spider, mantis, boar, tortoise, behemoth, gorilla, sandworm, titan/brute).
- **Neu vorgeschlagen: 16**:

| Skelett | neue Muster |
|---|---|
| quadruped | leopard, bear, frog, badger, monkey |
| hexapod | broodmother |
| legless | viper, centipede |
| floater | wraith, orb |
| winged | bird, bat, drake |
| upright | golem, treant |
| amorph | slime, aberration |
| static | turret |

Gesamt ≈ 34 Muster, dazu ≈ 25 Varianten (nur Werte).

---

## 5. Welche Monsterarten zu unserem Spiel passen

Bewertungskriterien für ein Top-down-ARPG mit vielen Gegnern:
- **Silhouette von oben:** Breite, Beinkranz, Flügel, Schwanz.
- **Lesbarkeit des Angriffs:** Ausholen gut sichtbar?
- **Rolle im Pulk.**
- **Häufigkeit in der Datenbank:** Belegt, dass der Typ im Genre funktioniert.

Alle Beschreibungen sind generisch. Die konkreten Designs kommen aus deiner Concept Art.

### A · Kernbestand (häufig in Gruppen, sehr gut lesbar von oben)
| # | Archetyp | Skelett/Muster | Rolle | Warum es passt |
|---|---|---|---|---|
| 1 | **Rudel-Vierbeiner**, flink, beißt nach Anlauf | quadruped/wolf | Nahkampf, Gruppe | häufigstes Tier-Muster der Datenbank; Rudel = klare Gruppen-Silhouette |
| 2 | **Kleinkrabbler-Schwarm** (Spinne/Insekt/Larve), überrennt | octopod/spider, hexapod/ant | Schwarm | Beinkranz ist von oben perfekt lesbar; 38 % der Kreaturen sind klein/winzig |
| 3 | **Gepanzerter Krabbler**, Scheren, langsam, blockt | octopod/crab | Tank | breite Silhouette, Panzer-Oberseite = Platz für Textur-Detail |
| 4 | **Spucker** (Echse/Krebs/Schlange) aus der zweiten Reihe | lizard/spitter, crab/mortar, cobra/spitter | Fernkampf | Fernkampf ist bei Echsen, Schlangen und Skorpionen die Regel (42–70 %) |
| 5 | **Lauer-Raubkatze**, schleicht, Sprungangriff | quadruped/leopard | Assassine | Pounce ist der klarste Telegraph überhaupt |
| 6 | **Stein-/Kristall-Golem**, stampft mit Flächen-Schaden | upright/golem | Tank, Elite | größte Kreatur-Gruppe der Datenbank (175) |
| 7 | **Kreisender Aasvogel**, stößt herab | winged/bird | Störer, Fernkampf | Schatten + Sturzflug = gut lesbar; nutzt die Höhe |
| 8 | **Explodierende Larve/Orb**, rennt auf den Spieler zu | hexapod/ant-larva, floater/orb-wisp | Schwarm | „Explodieren“ bei 9 % aller Monster; klassischer Druckmacher |

### B · Elite-Kandidaten (eine Mechanik, die man lernen muss)
| # | Archetyp | Skelett/Muster | Mechanik |
|---|---|---|---|
| 9 | **Rammbestie** mit Hauern/Horn | quadruped/boar | Ansturm in gerader Linie (60 % Ansturm), Ausweichen lernen |
| 10 | **Aufrichtender Bär** | quadruped/bear | Aufrichten = Telegraph, dann Doppelprankenhieb |
| 11 | **Sprungfrosch mit Zunge** | quadruped/frog | Sprung (61 %) + Zunge zieht den Spieler heran |
| 12 | **Stachel-Igel** | quadruped/badger-porcupine | Stacheln-Kranz als Rundum-Projektil |
| 13 | **Netzspinne** | octopod/spider-web | Netz verlangsamt (Kontrolle) |
| 14 | **Gespenst** ohne Unterleib | floater/wraith | Teleport + Klauenhieb |
| 15 | **Schwebendes Auge** | floater/orb-eye | Strahl, der langsam nachzieht |
| 16 | **Grabwurm** | legless/sandworm | Abtauchen, dann Auftauchen unter dem Spieler (68 % Auftauchen) |
| 17 | **Schleim, der sich teilt** | amorph/slime | Tod → 2–3 kleinere Kopien (Schwarm-Erzeuger) |

### C · Boss-/Miniboss-Kandidaten (groß, mehrphasig)
| # | Archetyp | Skelett/Muster | Typisch |
|---|---|---|---|
| 18 | **Brutkönigin** (Insekt/Spinne) | hexapod/broodmother, octopod/spider-brood | 12 von 13 riesig; spawnt Brut, Projektile |
| 19 | **Koloss/Lasttier** | quadruped/behemoth, gorilla | Stampf-AoE, Ansturm |
| 20 | **Drache/Wyvern** | winged/drake | landet, Feueratem, Schwanzschlag |
| 21 | **Fleischkoloss/Titan** | upright/brute | Slam, Greifen, Werfen |
| 22 | **Tentakel-Schweber** | floater/tentacle | Tentakel aus dem Boden (Auftauchen 38 %) |
| 23 | **Baumriese** | upright/treant | Wurzel-AoE, ruft Pflanzen-Totems |

### D · Umgebung/Spawner (macht Kämpfe lebendig, kostet fast nichts)
| Archetyp | Skelett | Mechanik |
|---|---|---|
| Brutnest, Eiersack | static/nest | spawnt Schwarm, bis es zerstört ist |
| Giftpflanze, Schnappfalle | static/plant | Fernkampf/Falle |
| Kristall-Totem | static/turret | Buff/Aura für Monster in der Nähe |

### Eher meiden bzw. selten einsetzen
- **Menschen-Krieger und -Bogenschützen** (49 % von PoE): passt nicht zu deinem Kreaturen-Fokus. Nur für Story, z. B. Kultisten.
- **Fisch/Schwimmer**: Ohne Wasserkampf liest man sie von oben schlecht. Nur als schwebende Abyss-Variante.
- **Sehr dünne Formen** (Weberknecht-Beine, filigrane Flügel): Von oben verschwinden sie, und Tripo liefert sie oft als Klumpen (ROADMAP-Risiko). Besser dicke Beine plus Shader-Detail.

---

## 6. Plan für 50–100 Basis-Monster

### 6.1 Vorschlag: 83 Basis-Archetypen auf 12 Skeletten / 34 Mustern
**Legende**
- **Rolle:** S = Schwarm, N = Nahkampf, F = Fernkampf, T = Tank, A = Assassine, K = Kontrolle, E = Elite, B = Boss.
- **Größe:** W = winzig, K = klein, M = mittel, G = groß, R = riesig.
- **Biome:** Wa = Wald, Kü = Küste, Hi = Highlands, Wü = Wüste, Sc = Schnee, Ab = Abyss, Hö = Höhle/Untergrund, Vu = Vulkan, Su = Sumpf, Kr = Krypta.
- **Roster** = deckt sich mit einer der 20 Kreaturen aus `creatures/roster.toml`.

| # | Basis-Archetyp (generisch) | Skelett | Muster (Variante) | Rolle | Größe | Biome | Roster |
|---|---|---|---|---|---|---|---|
| 1 | Waldameisen-Krieger | hexapod | ant | S/N | K | Wa Hö Wü | chitin_crawler |
| 2 | Säurespritz-Ameise | hexapod | ant | F | K | Wa Su Wü | |
| 3 | Panzer-Rammkäfer | hexapod | ant (beetle) | T | M | Wa Hö Wü | |
| 4 | Sporen-Käfer (Wolke) | hexapod | ant (beetle) | F/K | M | Wa Su Ab | spore_drone |
| 5 | Explodierende Brutlarve | hexapod | ant (larva) | S | W | alle | |
| 6 | Sprungschrecke | hexapod | ant (hopper) | S/A | K | Hi Wü Wa | |
| 7 | Sensen-Fangschrecke | hexapod | mantis | A/E | M | Wa Ab Su | reality_ripper |
| 8 | Brutkönigin der Insekten | hexapod | broodmother | B | R | Hö Wa Ab | |
| 9 | Strandkrabbe | octopod | crab | S | W | Kü Hö | |
| 10 | Panzer-Scherenkrebs | octopod | crab | T | M | Kü Sc Vu | |
| 11 | Mörserkrebs (Bogen-Schuss) | octopod | crab (mortar) | F | K | Kü Wü Vu | |
| 12 | Einsiedler mit Schale | octopod | crab (shell) | T/K | M | Kü Hö | |
| 13 | Finger-Krabbler (Aberration) | octopod | crab (hand) | S/N | K | Ab Kr | |
| 14 | Lauerspinne | octopod | spider | N | K | Wa Hö Kr | |
| 15 | Springspinne mit Brut | octopod | spider (brood) | A | K | Wa Hö | broodling |
| 16 | Netzspinne | octopod | spider (web) | K | M | Wa Hö Kr | |
| 17 | Giftspei-Spinne | octopod | spider (spitter) | F | K | Su Wü Hö | |
| 18 | Spinnenmutter | octopod | spider (brood) | E/B | G | Hö Kr Ab | |
| 19 | Wüstenskorpion | multileg | scorpion | N | K | Wü Vu | |
| 20 | Stachel-Schütze-Skorpion | multileg | scorpion (tail_shooter) | F | K | Wü Hö | |
| 21 | Skorpion-Matriarchin | multileg | scorpion | B | R | Wü | scorpion_matriarch |
| 22 | Speikobra | legless | cobra (spitter) | F | K | Wü Su Wa | |
| 23 | Küsten-Aal/Muräne | legless | cobra (eel) | A | M | Kü Ab | eel_stalker |
| 24 | Lauer-Viper | legless | viper | A | K | Wa Wü Su | |
| 25 | Sand-Leviathan | legless | sandworm | B | R | Wü | sand_leviathan |
| 26 | Grabwurm-Brut | legless | sandworm (small) | S | K | Wü Hö Su | |
| 27 | Wurzelschlinger (taucht auf, hält fest) | legless | sandworm (rooted) | K/E | G | Wa Su Ab | |
| 28 | Riesenläufer (Tausendfüßer) | legless | centipede | N/A | M | Hö Wa Vu | |
| 29 | Rudelwolf | quadruped | wolf | N | M | Hi Wa Sc | ravine_stalker |
| 30 | Aas-Hyäne | quadruped | wolf (hyena) | N | M | Hi Wü | rock_hyena |
| 31 | Glutatem-Hund | quadruped | wolf (hellhound) | F/N | M | Vu Ab | |
| 32 | Seuchenratten-Teppich | quadruped | wolf (rat) | S | W | Kr Hö Su | |
| 33 | Lauer-Raubkatze | quadruped | leopard | A | M | Wa Hi Sc | |
| 34 | Mähnen-Raubkatze (Anführer) | quadruped | leopard (lion) | E | G | Wü Hi | |
| 35 | Höhlenbär | quadruped | bear | T/N | G | Wa Sc Hö | |
| 36 | Grabender Dachs | quadruped | badger | N | K | Wa Hi | |
| 37 | Stachel-Igel | quadruped | badger (porcupine) | F | M | Wa Wü Sc | |
| 38 | Trupp-Affe (wirft) | quadruped | monkey | S/F | K | Wa Su | |
| 39 | Stein-Eber | quadruped | boar | N/E | M | Hi | stone_boar |
| 40 | Hornbulle | quadruped | boar (bull) | E | G | Hi Wü | |
| 41 | Hohler Hirsch | quadruped | deer | N | M | Hi Wa | hollow_stag |
| 42 | Fels-Bock (Rammsprung) | quadruped | deer (ram) | N | M | Hi Sc | |
| 43 | Küsten-Echse | quadruped | lizard | N | M | Kü Su | reef_snapper |
| 44 | Lauer-Krokodil | quadruped | lizard (lurker) | A/T | G | Kü Su | shore_lurker |
| 45 | Spuck-Echse (Basilisk-Typ) | quadruped | lizard (spitter) | F | M | Wü Vu Su | |
| 46 | Sprungfrosch mit Zunge | quadruped | frog | N/K | M | Su Kü Wa | |
| 47 | Giftkröte | quadruped | frog (toad) | F | K | Su Ab | |
| 48 | Panzer-Schildkröte | quadruped | tortoise | T | G | Kü Wü | shellback |
| 49 | Glas-/Kristall-Koloss | quadruped | behemoth | B | R | Wü Sc | glassback_colossus |
| 50 | Frost-Knöchelgänger | quadruped | gorilla | E/B | G | Sc Hi | frost_colossus |
| 51 | Chimäre (Vierbeiner + Schwanz/Tentakel-Addon) | quadruped | wolf/leopard + Addon | E | G | Ab | (Abyssal Chimera, A) |
| 52 | Dünen-Raptor | biped_raptor | raptor | N/A | M | Wü Hi | dune_raptor |
| 53 | Hackvogel (Pick-Serie) | biped_raptor | raptor (fowl) | N | K | Wa Hi | |
| 54 | Gleit-Raptor (Elite mit Flügeln) | biped_raptor | raptor (glider) | E | M | Wü | dune_raptor (Elite) |
| 55 | Kreisender Aasvogel | winged | bird | K/F | M | Wü Hi Kü | |
| 56 | Sturmvogel (Federgeschoss) | winged | bird (shooter) | F | K | Kü Hi Sc | |
| 57 | Höhlenfledermaus-Schwarm | winged | bat | S | K | Hö Kr | |
| 58 | Schrei-Fledermaus | winged | bat (screamer) | K | M | Hö Ab | |
| 59 | Wyvern | winged | drake | E/B | G | Vu Hi Wü | |
| 60 | Steinwächter (sitzt als Statue, erwacht) | winged | drake (gargoyle) | E | M | Kr Ab Hi | |
| 61 | Stachelwespe | flyer | wasp | A | K | Wa Su | needle_wasp |
| 62 | Mückenwolke | flyer | wasp (swarm_fly) | S | W | Su Wa | |
| 63 | Tentakel-Schweber | floater | tentacle | F/B | G | Ab | void_manifestation |
| 64 | Schwebende Qualle | floater | tentacle (jelly) | K | M | Kü Ab | |
| 65 | Gespenst ohne Unterleib | floater | wraith | A/F | M | Kr Ab Sc | void_harbinger (Teil) |
| 66 | Schwebendes Auge (Strahl) | floater | orb (eye) | F | K | Ab Kr | |
| 67 | Irrlicht, explodiert | floater | orb (wisp) | S | W | Su Ab Vu | |
| 68 | Tanzende Klinge | floater | orb (blade) | N | K | Kr | |
| 69 | Steingolem | upright | golem | T | G | Hi Hö Wü | |
| 70 | Mechanischer Wächter (Strahl) | upright | golem (construct) | F/T | G | Kr Wü | |
| 71 | Kleiner Elementar-Golem (Schwarm) | upright | golem (small) | S | K | Vu Sc | |
| 72 | Fleisch-Titan | upright | brute (titan) | E/B | R | Ab | flesh_titan |
| 73 | Aufrechte Bestie (werwolfartig) | upright | brute (beastman) | N/E | G | Wa Sc Ab | |
| 74 | Baumriese | upright | treant | T/B | R | Wa Su | |
| 75 | Kultist/Schamane | upright | caster (humanoid) | F | M | Ab Kr | |
| 76 | Skelettkrieger | upright | warrior (humanoid) | N | M | Kr Wü | |
| 77 | Schlurfender Untoter | upright | zombie (humanoid) | S | M | Kr Su | |
| 78 | Hüpfschleim, teilt sich | amorph | slime | S/N | M | Su Hö Ab | |
| 79 | Fleischmasse mit Mäulern | amorph | aberration | E | G | Ab | |
| 80 | Flüssigkeits-Elementar (Wasser/Blut/Lava) | amorph | slime (liquid) | F/N | M | Kü Vu Ab | |
| 81 | Brutnest/Eiersack | static | turret (nest) | Spawner | M | alle | |
| 82 | Giftpflanze/Schnappfalle | static | turret (plant) | F/Falle | M | Wa Su | |
| 83 | Kristall-Totem (Aura) | static | turret | Support | M | Sc Ab Wü | |

**Verteilung:**

| Skelett | Basis-Monster | % |
|---|---:|---:|
| quadruped | 23 | 28 % |
| octopod | 10 | 12 % |
| hexapod | 8 | 10 % |
| upright | 9 | 11 % |
| legless | 7 | 8 % |
| floater | 6 | 7 % |
| winged | 6 | 7 % |
| multileg | 3 | 4 % |
| biped_raptor | 3 | 4 % |
| amorph | 3 | 4 % |
| static | 3 | 4 % |
| flyer | 2 | 2 % |

Rollenmix: ≈ 20 % Schwarm, 35 % Nahkampf, 20 % Fernkampf/Kontrolle, 15 % Elite, 10 % Boss.
**Hebel:** Die 10 fertigen Muster tragen allein 32 der 83 Archetypen. Mit spider, leopard, bear und golem (4 Muster) kommen 11 weitere dazu.

### 6.2 Schema: 5–6 Biom-Varianten bzw. Elite-Addons pro Basis-Monster
Regel aus CLAUDE.md: **Varianten über Slider + Tönung, keine neuen Generierungen.** Ein Basis-Monster bedeutet: 1 Tripo-Mesh, 1 Rig, 1 Clip-Satz. Varianten kosten **keine Credits**.

| Stellschraube | Werkzeug | Beispiel-Werte |
|---|---|---|
| **Tönung** (Grundfarbe, Akzent, Emission/Glühen, Rauheit) | Shader-Parameter / Material-Instanz in Unity | Wald: Moosgrün/Braun · Schnee: Weiß/Eisblau · Wüste: Sand/Ocker · Vulkan: Schwarz + glühende Risse · Abyss: Violett + Emission |
| **Anbauteile** (Stacheln, Kristalle, Pilze, Eisplatten, Korallen/Muscheln, Knochen, Moos) | **Geometry Nodes** mit Slidern (Dichte, Größe, Zufall), starr am nächsten Knochen | Schnee = Eisplatten auf dem Rücken · Höhle = Kristalle · Sumpf = Pilze · Küste = Muscheln |
| **Proportionen** | Bone-Skalierung (Slider), nur so weit die Clips nicht brechen | Größe ±15 %, Kopf/Scheren ±20 %, Beine ±10 % |
| **Bewegungswerte** | Muster-Slider (`style.toml`) | Tempo, Schrittlänge, Haltung tiefer/höher, „Gewicht“ |
| **Element-Effekt** | VFX + Schadensart, Event `projectile_spawn`/`aura` | Feuer, Kälte, Gift, Blitz, Chaos |
| **Fähigkeit** | Option pro Monster (MOVESET: Attack 2 = Stich oder Projektil) | Nahkampf ↔ Fernkampf, Explodieren beim Tod, Brut rufen |

**Standard-Satz pro Basis-Monster (6 Stück):**
1. **Grundform**: Heimatbiom aus der Concept Art.
2. **Biom-Variante A** (z. B. Schnee/Eis): Tönung + Eisplatten-Addon + Kälte-Effekt, Tempo −10 %.
3. **Biom-Variante B** (z. B. Vulkan/Feuer): Tönung + glühende Risse (Emission) + Feuer-Effekt.
4. **Biom-Variante C** (z. B. Sumpf/Gift): Tönung + Pilz-/Blasen-Addon + Gift-Effekt, Fernkampf-Option.
5. **Biom-Variante D** (z. B. Abyss/Korruption): Violett + Tentakel-/Augen-Addon + Chaos-Effekt.
6. **Elite-Addon** (auf jede Biom-Variante legbar statt eigener Variante):
   - Größe ×1,3–1,6
   - Rüstungsplatten/Krone/Hörner per Geometry Nodes
   - Aura-VFX und farbiger Rand (Rim-Light) für Lesbarkeit von oben
   - zusätzlicher Clip: **Dodge** bzw. **Taunt** (MOVESET, vorhanden pro Bauplan)
   - eine Spezialfähigkeit (Ansturm, Brut rufen, Explosion beim Tod, Schild)

So entstehen aus 83 Basis-Monstern rechnerisch **≈ 415–500 spielbare Gegnertypen**. Mit dem Elite-Addon auf jeder Variante sind es bis zu ≈ 830. Zum Vergleich: PoE kommt auf ≈ 6,9 Namen pro Grundkörper.

### 6.3 Abgleich mit den 20 Roster-Kreaturen
**Die 20 decken ab:** hexapod/ant (+beetle, mantis), octopod/spider, multileg/scorpion, flyer/wasp, quadruped/wolf (+hyena), lizard (+lurker), tortoise, boar, deer, behemoth, gorilla, legless/cobra (eel), sandworm, biped_raptor, upright/brute (titan), floater/tentacle (+wraith-ähnlich).

**Lücken (Muster mit vielen Daten-Belegen, aber ohne Roster-Kreatur):**

| Lücke | Monster in der Datenbank | % der Kreaturen | Bedarf |
|---|---:|---:|---|
| upright/golem | 175 | 12,9 % | größte Lücke, Concept Art für einen Golem/Konstrukt anfragen |
| floater/wraith + orb | 82 + 47 | 9,5 % | Void Harbinger deckt nur einen Teil ab |
| winged (bird/bat/drake) | 80 | 5,9 % | **kein einziges Wirbeltier-Flugwesen im Roster** |
| quadruped/leopard | 57 | 4,2 % | |
| quadruped/bear | 53 | 3,9 % | |
| quadruped/frog | 41 | 3,0 % | |
| amorph/slime + aberration | 46 | 3,4 % | |
| quadruped/badger, monkey | 30 + 23 | 3,9 % | |
| hexapod/broodmother | 13 | (Boss) | |
| static (Nest/Turm/Pflanze) | 76 | (alle Monster) | |

Nicht in PoE, aber im Roster (Alleinstellung): **mantis, raptor, deer, wasp, sandworm, centipede (optional)**. Diese Formen gibt es in der Datenbank kaum oder gar nicht. Das ist gut für die Eigenständigkeit.

---

## 7. Empfohlene Reihenfolge (größter Nutzen zuerst)

| Rang | Was | Begründung |
|---|---|---|
| 1 | **octopod/spider** (+ web/spitter/brood als Varianten) | 117 Monster (8,6 % der Kreaturen), Roster-Broodling wartet; Skelett und Baukasten existieren → fast nur Clip-Code |
| 2 | **quadruped/leopard** und **quadruped/bear** | zusammen 110 Monster (8 %) auf dem fertigen Vierbeiner; zwei sehr lesbare Angriffe (Pounce, Aufrichten) |
| 3 | **upright** (neues Skelett) mit **golem** + **brute** | +16 % der Kreaturen (175 + 71), Roster Flesh Titan/Frost Colossus-Angriff; Unity-Humanoid-Knochennamen → Mixamo-Vorlagen sparen Arbeit. Humanoid (Kultist, Skelett) später fast geschenkt |
| 4 | **floater/wraith** + **orb** | 129 Monster (9,5 %), Skelett vorhanden; orb ist trivial (kein Gang) |
| 5 | **winged** (neues Skelett) mit **bird**, dann bat/drake | +6 % der Kreaturen, keine Roster-Abdeckung; Flieger bringen Höhe ins Top-down-Bild. Aufwand: Start/Landung, Kreisen |
| 6 | **static** (turret/nest/plant) | minimaler Aufwand (1–4 Knochen), aber großer Spielwert: Spawner und Fallen |
| 7 | **amorph/slime** | 3,4 %, aber ikonisch (Teilen beim Tod = Schwarm-Erzeuger); sehr billig |
| 8 | **quadruped/frog**, **badger** (porcupine), **monkey** | je 2–3 %, jeweils eine eigene Angriffsmechanik (Sprung/Zunge, Stachel-Kranz, Werfen) |
| 9 | Roster-Muster in Roster-Reihenfolge (boar, tortoise, behemoth, gorilla, sandworm, mantis) | bereits geplant; sie füllen ihre eigenen Lücken |
| 10 | **legless/viper**, **hexapod/broodmother**, **winged/drake**, **upright/treant**, **centipede** | eher Elite/Boss bzw. Feinschliff |
| – | swimmer | nicht bauen (0,1 %) |

---

## 8. Annahmen und Grenzen
- **PoE-Datenbank ≠ unser Spiel.** Häufigkeiten zeigen, was im Genre funktioniert, nicht was wir bauen müssen. PoE ist zu ~49 % humanoid, wir zu ~90 % Kreatur. Deshalb stehen die Kreaturen-Prozente im Vordergrund.
- **Einordnung regelbasiert**, ca. 9 von 10 Stichproben plausibel. „Boss/Unique“ enthält alle Monster mit Eigennamen, auch Story-Figuren. Größe beruht auf `model_height_class` (bei 18–21 % unbekannt).
- **Biome** sind nur für 25 % der Monster bekannt und stark von Innenräumen geprägt.
- „Fake it“: Mehrere Tierarten teilen sich bewusst ein Muster (z. B. Ratte = Wolf-Variante, Hellhund = Wolf + Atem). Wenn das in der Spielkamera nicht überzeugt, wird die Variante später zum eigenen Muster.

## 9. Reproduzierbarkeit
Alle Skripte liegen in `01_kreatur_pipeline/temp/monster_research/` und laufen mit Python 3.11:
```
python 00_explore.py          # liest catalog.json einmal, speichert catalog.pkl (Cache)
python 15_reload_diff.py      # bei neuer DB-Version: neu laden + Schema-Unterschiede zeigen
python 16_creatures_vs_rule.py# offizielle creatures-Gruppierung vs. eigene Regel
python 10_classify.py         # Varianten-Regel + Einordnung → kategorien.csv, monsters_agg.json, stats.json
python 12_tables.py           # alle Tabellen → tables.md
python 13_prefixes.py         # Präfix-Varianten (Belege für Biom-Varianten)
python 14_coverage.py         # kumulierte Skelett-Abdeckung → coverage.md
python 11_inspect.py "Spinne|Bär" 20   # Stichprobe je Kategorie zur Kontrolle
```
Hilfsskripte der Erkundung: `01`–`08`. Die CSV `kategorien.csv` (Trennzeichen `;`, UTF-8) enthält je echtem Monster:
- Quellname, Anzahl Datensätze, Kategorie, Skelett, Muster, Eindeutigkeit der Einordnung
- Größe, Rolle, Tempo, Mechaniken, Biome
- Metadaten-Ordner und `creature_id`
