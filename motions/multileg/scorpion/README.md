# Bewegungsmuster multileg/scorpion

Generator `scorpion_clips.py`, Werte `style.toml`. Erstes Modell: **Scorpion Matriarch** (2026-11-17), alle 9 Clips grün.

| Clip | Inhalt |
|---|---|
| Multileg_Scorpion_Walk / Run | alternierende Beingruppen (L1 R2 L3 R4 L5 gegen R1 L2 R3 L4 R5) mit kleiner Welle vorn → hinten, Scheren leicht erhoben, Schwanz lebt über die ganze Länge (Heben/Senken + Pendeln als Welle Wurzel → Spitze, 2 Wellen pro Schrittzyklus) |
| Multileg_Scorpion_TurnLeft/Right | auf der Stelle drehen (Schwanz wie Walk) |
| Multileg_Scorpion_Idle | Scheren öffnen/schließen abwechselnd, Schwanz-Welle über alle Glieder |
| Multileg_Scorpion_Ready | Drohen: Körper hoch, Scheren gespreizt + erhoben, Schwanz hoch über dem Rücken gespannt, **Stachel zeigt waagerecht nach vorn auf den Gegner**, Zittern als schnelle Welle über die Kette |
| Multileg_Scorpion_Attack1 | Stich (siehe unten), Event `hit` Frame 12 |
| Multileg_Scorpion_Hit | Ruck zurück, Schwanz zuckt verzögert entlang der Kette nach hinten/oben weg |
| Multileg_Scorpion_Death | kippt auf den Rücken (Krabbler-Tod) – **unverändert, Death-Clips fasst Claude vorerst nicht an** |

## Naturreferenzen / Videos
- **Coelho et al. 2017**, *Functional Ecology* – Hochgeschwindigkeitsvideo (500 fps, Spiegel-Arena) von Verteidigungsstichen bei 7 Arten:
  Abstract https://ui.adsabs.harvard.edu/abs/2017FuEco..31.1390C · Video https://youtu.be/7dHsNmqs8Bs
  (verlinkt über https://scorpion-files.blogspot.com/2017/04/scorpions-are-infamous-for-their-tail.html)
- Presse dazu: British Ecological Society https://britishecologicalsociety.org/press-sting-tail-high-speed-video-captures-death-stalker-scorpions-strike ·
  Gizmodo https://gizmodo.com/the-worlds-deadliest-scorpion-strike-is-even-more-terri-1793990163 ·
  Live Science https://www.livescience.com/58786-deathstalker-scorpions-defensive-sting-video.html ·
  Smithsonian https://www.smithsonianmag.com/smart-news/slo-mo-footage-shows-how-scorpions-strike-180962803/
- Kaiserskorpion-Stich in Superzeitlupe (Distort/TestTube): https://laughingsquid.com/getting-stung-by-a-scorpion-in-super-slow-motion/
- Gang: „scorpion walking slow motion“; Drohhaltung: „scorpion defensive posture“. Gangmuster wie bei Spinnentieren:
  alternierende Vierergruppen mit metachroner Welle.

### Was daraus für den Stich folgt (2026-11-17)
- **Offener Stich** (Deathstalker, Kaiserskorpion = großer Wüstenskorpion wie unsere Matriarchin): Der Stachel schnellt **über den
  Kopf**, geht **auf geradem Weg** zum Ziel und wird danach sofort wieder in die Angriffshaltung hochgerissen. Schnellste und
  genaueste Stichform (Deathstalker ≈ 130 cm/s). Alternative „O-Bahn“ (Hottentotta: Stachel kreist) → mögliche spätere Variante.
- Dabei **streckt sich der ganze Hinterleib (Metasoma)** nach vorn – nicht nur das Gelenk an der Wurzel. Der Stachel trifft
  frontal, leicht von oben. Beute wird von den Scheren gehalten → Ziel liegt zwischen den Scherenhänden.
- Phasen im Clip (30 fps): **Ausholen 0–9** (Schwanz spannt sich höher über dem Rücken, Stachel waagerecht nach vorn, Rumpf lehnt
  zurück + vorn hoch, Scheren öffnen) → **Zustoßen 9–12** (3 Frames = 100 ms, beschleunigt; Schwanz streckt sich über den Kopf,
  Gewicht nach vorn, Brust runter, Scheren packen zu) → **Halten 12–16** (Treffer-Event 12, leichtes Nachdrücken) → **zurück 16–24**.
  Das Ausholen ist für die Lesbarkeit im Spiel länger als in der Natur (Telegraph für den Spieler).

## Technik: Schwanz mit absoluter Form (seit 2026-11-17)
Nutzer-Feedback: „Der Stachel hat nur eine Wölbung des Hauptgelenks; Schwanz und Stachel bewegen sich nicht → der Skorpion
sticht sich selbst.“ Ursache: Der alte Stich rollte den Schwanz nur weiter ein (gleicher Winkel auf alle Glieder addiert) –
beim Treffer lag die Spitze 3 mm über dem eigenen Rücken und zeigte −62° nach hinten unten.
- Jedes Glied bekommt eine **absolute Neigung** (`K.chain_pose`, 0° = waagerecht nach vorn, 90° = senkrecht hoch). Ausholform =
  `cock_pitch_deg`. Stichform wird pro Frame **berechnet** (`K.chain_reach`): Schwanzwurzel `strike_base_deg`, Stachel
  `strike_aim_deg`, dazwischen glatt verteilte Biegung, so dass die Stachelspitze genau den Zielpunkt trifft
  (`target_ahead`/`target_height`). Übergänge mischen die Neigungen aller Glieder → der ganze Schwanz schwingt.
- Walk/Idle/Ready/Hit: Ruheform bzw. Ausholform + Wellen, deren Biegung **je Gelenk** entlang der Kette aufsummiert wird.
- **Selbstprüfung in jedem Clip (außer Death):** Strahl ab Stachelspitze in Stachelrichtung (0,4 × Körperlänge) darf den
  eigenen Körper (ohne Schwanz) nie treffen → `sting_never_self_ok`. Attack zusätzlich `sting_on_target_ok`: Spitze ≤ 3 % der
  Körperlänge vom Zielpunkt UND Stachel zeigt nach vorn (−50° … +10°). Gegenprobe: der alte Stich wäre in Frame 11–20 durchgefallen.

## Erkenntnisse
- Tripo erzeugte **5 statt 4 Beinpaare** (Fake it: Skelett nimmt beliebig viele). Das 5. Paar sitzt am Schwanzansatz und war mit
  Hüfte/Schwanz verschmolzen → Haupt-Ursache der Rest-Dehnung (Grenzen pro Clip mit Begründung in style.toml).
- Rig-Korrekturen für den Stich (`rigging/multileg_defaults.toml`, 2026-11-17):
  `tail_midline` (Schwanzgelenke lagen 10 cm seitlich auf der Haut statt in der Mitte → einseitige Gewichte),
  `tail_start` 0,15 → 0,28 (Tail_1 begann tief im Hinterleib, halber Rumpf schwang mit), `cut_tail_leg_bridges`
  (Hautbrücken Schwanz ↔ 5. Beinpaar). Dehnung im Stich ×12,9 → ×7,4; Walk ×4,0 → ×2,3, Run ×4,8 → ×2,6.
  Rest: schmaler, geschlossener Hautstreifen zwischen Schwanzwurzel und 5. Beinpaar, solange der Schwanz gestreckt ist.
  Eine lockerere Schnitt-Regel brächte ×3,4, öffnet aber Löcher am Hinterleib → verworfen.
- Lückenprüfung: Das Paar `Leg_L5_2 / Tail_1` (zwei kleine Hautinseln, 16 + 23 Vertices, schon in Ruhe 1,4 cm auseinander) öffnet
  sich im Stich auf 7 cm, weil Schwanz und 5. Bein auseinandergehen – Nahaufnahme ohne sichtbares Loch. Braucht in
  `creatures/scorpion_matriarch/creature.toml` `[gaps] max_opening = 0.075` (mit dieser Begründung), sonst ist `--stage full` rot.
