# Moveset für Monster im Top-down-Auto-Battler (ARPG-Stil)

Stand: 2026-11-17 · Ausgangsliste vom Nutzer, ergänzt und für Krabbler konkretisiert.
Gilt **pro Bauplan** (Krabbler, Vierbeiner, Schlange, Flieger …): Jeder Bauplan hat ein Standard-Skelett, also werden die Clips **einmal pro Bauplan** erzeugt und von allen Monstern dieses Bauplans geteilt. Pro Monster werden nur Slider angepasst (Tempo, Ausschlag, Gewicht).

## Grundregeln
- **Naturbeobachtung zuerst:** Vor jedem Clip ein Referenzvideo eines echten, ähnlichen Tiers suchen und im README verlinken. Die Spalte „Referenz“ unten sagt, wonach gesucht wird.
- **Fake it:** Es muss aus der Top-down-Kamera gut lesbar aussehen. Lieber **wenige, klare Clips plus Parameter** als viele Spezialclips.
- **Lesbarkeit im Kampf:** Angriffe brauchen ein deutliches **Ausholen (Telegraph)**, damit Spieler sie erkennen, dann einen schnellen Treffer und eine kurze Erholung.
- **Events statt Raten:** Jeder Clip liefert Ereignis-Frames (Treffer-Frame, Fußaufsetzer, Spawn-Punkt für Projektile) als JSON neben der FBX. Unity setzt daraus Animation Events.
- **In place vs. Root Motion:** Fortbewegung (Walk/Run/Turn) läuft *in place*, bewegen tut Unity (NavMesh). Kurze Ortswechsel (Dodge, Sprung, Lunge) bekommen **Root Motion**, damit Weg und Animation exakt passen.

## Clip-Liste

Spalte **Prio:** 1 = MVP, ohne das geht kein Kampf · 2 = macht es lebendig · 3 = Kür.
Spalte **Typ:** P = prozedural mit Slidern (wie Walk) · K = Keyposen + prozedurale Feinheiten · A = additiv (wird über andere Clips gelegt).

| # | Clip | Prio | Typ | Loop | Dauer | Inhalt beim Krabbler | Referenz (Naturvideo) |
|---|---|---|---|---|---|---|---|
| 1 | **Idle** | 1 | P | ✓ | 2–3 s | Hinterleib „atmet“, Fühler tasten langsam, ab und zu Gewicht verlagern | Ameise steht still, Fühler tasten |
| 2 | **Ready** (Kampfbereit) | 1 | P | ✓ | 1–2 s | Körper tiefer, Vorderbeine/Taster leicht erhoben, Mandibeln geöffnet, Fühler nach vorne | Ameise in Drohhaltung, Mandibeln offen |
| 3 | **Think** (Idle-Variante) | 3 | K | – | 2–4 s | Fühler mit Vorderbeinen putzen, Kopf dreht sich | Ameise putzt Fühler (Grooming) |
| 4 | **Walk** | 1 | P | ✓ | 0,67 s | ✅ vorhanden: Dreifuß-Gang | ✅ Ameisen-Gang (Studien verlinkt) |
| 5 | **Run** | 1 | P | ✓ | ~0,4 s | Gleicher Gang, längere Schritte und höhere Frequenz, Körper tiefer. Unity mischt Walk ↔ Run nach Tempo. | Ameise rennt (Gangart bleibt Dreifuß!) |
| 6 | **Turn** (auf der Stelle) | 1 | P | ✓ | ~0,5 s | Beine trippeln seitlich, Körper dreht. **Nicht in der Ausgangsliste, aber nötig:** Auto-Battler-Units drehen sich ständig zum Ziel. | Ameise wendet |
| 7 | **Attack 1** (Biss) | 1 | K | – | ~0,8 s | Ausholen (Kopf zurück, Mandibeln auf), Vorschnellen + Zubeißen (Treffer-Frame), zurück | Ameise beißt / Bulldoggenameise |
| 8 | **Attack 2** (Stachel / Säure) | 2 | K | – | ~1,0 s | Hinterleib unter dem Körper nach vorne krümmen. **Option pro Monster:** stechen (Nahkampf) oder Säure spritzen (Fernkampf, Projektil-Event) | Waldameise spritzt Ameisensäure, Wespe sticht |
| 9 | **Dodge** | 2 | K | – | ~0,4 s | Schneller Seit- oder Rückwärtssatz mit Root Motion, Beine trippeln. **Genutzt von Bossen und Elite-Monstern.** | Insekt weicht Berührung aus |
| 10 | **Hit** (leicht) | 1 | A | – | ~0,25 s | Kurzes Zurückzucken von Kopf und Rumpf. **Additiv**, läuft also über Walk/Attack, ohne sie zu unterbrechen. | – (Spiel-Konvention) |
| 11 | **Hit Heavy** (stark) | 2 | K | – | ~0,6 s | Taumeln nach hinten, Beine spreizen sich zum Abstützen, unterbricht die aktuelle Aktion | – |
| 12 | **Knockdown** (umfallen) | 2 | K | – | ~0,8 s | Insekten-typisch: **auf den Rücken kippen**. Danach Loop „Beine strampeln“ als eigener kurzer Loop. | Käfer liegt auf dem Rücken, strampelt |
| 13 | **Get Up** (aufstehen) | 2 | K | – | ~0,8 s | Mit Beinschwung zurück auf die Füße rollen | Käfer dreht sich zurück |
| 14 | **Death** | 1 | K | – | ~1,0 s | Einknicken, **Beine rollen sich ein** (typische Insekten-Todeshaltung), danach Auflösen per Shader statt Leiche | tote Insekten, eingerollte Beine |
| 15 | **Jump Far** (Sprung-Angriff / Lücke schließen) | 3 | K | – | ~0,7 s | Ducken, weiter Satz mit Root Motion, Landung abfedern. Ersetzt beim Krabbler den Sprung. | Springspinne beim Sprung |
| 16 | **Jump High** | 3 | K | – | ~0,8 s | Für Krabbler eher selten (z. B. auf Hindernisse). Vorschlag: **ein** Sprung-Clip mit Slider „Weite ↔ Höhe“ statt zwei Clips. | Springspinne / Grashüpfer |
| 17 | **Spawn** | 2 | K | – | ~1,0 s | **Ergänzung:** aus dem Boden/Nest krabbeln. In Auto-Battlern spawnen ständig Units. | Ameisen kommen aus dem Nest |
| 18 | **Stun** | 2 | P | ✓ | 1 s | **Ergänzung:** benommen, Fühler hängen, Beine zittern. Typischer CC-Effekt im ARPG. | – |
| 19 | **Taunt / Victory** | 3 | K | – | ~1,5 s | **Ergänzung:** Aufrichten, Mandibeln klappern, Fühler hoch | Ameise in Drohhaltung, aufgerichtet |
| 20 | **Cast / Special** | 3 | K | – | ~1,0 s | **Ergänzung:** Platzhalter für Fähigkeiten (z. B. Brut rufen bei der Broodmother) | je nach Fähigkeit |

## Zusammenlegen statt verdoppeln (Performance + weniger Arbeit)
- **Walk ↔ Run:** derselbe Generator mit anderen Slidern, in Unity als Blend Tree nach Geschwindigkeit
- **Ready / Idle:** derselbe Generator, Parameter „Anspannung“ 0…1
- **Hit leicht:** additiv statt eigener Zustand, dadurch keine Unterbrechung der Bewegung
- **Jump Far / High:** ein Clip mit Slider, wenn wir beide überhaupt brauchen
- **Knockdown + Get Up:** Get Up kann zum großen Teil der rückwärts abgespielte Knockdown sein (Fake it), mit eigenem Schluss
- **Death:** kurze Animation plus Auflösen per Shader, keine liegenbleibenden Leichen (spart Draw Calls)

## Unity-Seite (Zielbild)
- **Animator pro Bauplan** (Animator Override Controller pro Monster nur für Ausnahmen)
  - Layer 0: Locomotion (Blend Tree Idle/Walk/Run + Turn), Aktionen (Attack, Dodge, Jump, Hit Heavy, Knockdown/GetUp, Death, Spawn)
  - Layer 1: additiv für Hit (leicht), Fühler-/Atem-Overlays
- **Events aus JSON:** `hit`, `footstep`, `projectile_spawn`, `vulnerable_start/end`
- **Schwärme** (z. B. 30 Hive Larvae gleichzeitig): Walk/Idle/Death zusätzlich als **Vertex Animation Texture** backen, damit die GPU sie instanziert ohne Skinning. Erst nötig, wenn das Profiling es verlangt.

## Vorschlag Reihenfolge
1. **MVP-Kampf:** Idle, Ready, Run, Turn, Attack 1, Hit (additiv), Death (Walk existiert schon)
2. **Lebendig:** Attack 2, Hit Heavy, Knockdown, Get Up, Dodge, Spawn, Stun
3. **Kür:** Think, Jump, Taunt, Cast

## Entscheidungen des Nutzers (2026-11-17)
- **Fernkampf = Variante von Attack 2.** Ein Regler bzw. eine Option pro Monster: Stich (Nahkampf) oder Säure spritzen (Projektil-Event).
- **Knockdown gibt es** (echter Kontroll-Effekt) → Knockdown, Strampel-Loop und Get Up bleiben.
- **Dodge: zumindest Bosse und Elite-Monster weichen aus.** Normale Monster brauchen den Clip nicht, er wird aber pro Bauplan trotzdem erzeugt (Standard-Skelett), damit Elite-Varianten ihn nutzen können.
- **Keine Clips gestrichen**, die Liste bleibt vollständig.
