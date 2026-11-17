# Skelett multileg (Mehrbeiner aus EINEM zusammenhängenden Mesh: Skorpione, Spinnen, Insekten)

Rig: `rigging/multileg_rig.py` (Werte `rigging/multileg_defaults.toml`, pro Kreatur `[multileg]`). Clips nutzen den Beine-Baukasten
`motions/quadruped/quadruped_kit.py` (Blender-IK für beliebig viele Beine). Muster: `scorpion/`.
Unterschied zu `crawler`: `rigging/crawler_rig.py` braucht getrennte Mesh-Inseln pro Beinsegment (Chitin Crawler). Neuere Tripo-Modelle
sind ein zusammenhängendes Mesh → hier werden Gliedmaßen als **kürzeste Wege über die Oberfläche** (Dijkstra) gefunden.

## Erkennung
1. Körpermitte = dichtester Bereich; Graph über alle Mesh-Kanten (UV-Naht-Duplikate verschweißt), Dijkstra ab der Mitte.
2. Füße = Bodenkontakt-Flecken; Weg Fußspitze → Mitte, Mittellinie aus Querschnitten; Ansatz = wo die Umgebung schlagartig dichter wird.
   Knie = höchster Punkt im mittleren Wegstück (Spinnenbein).
3. Bodenkontakt **vor dem Kopf** = Scherenspitze. Schwanz = geodätisch entferntester Punkt hinter der Mitte (Stachel).
4. **Tripo verschmilzt sich berührende Gliedmaßen** (Nachbarbeine, Schwanzbogen auf dem Rücken) → `cut_fused_limbs` löscht Flächen,
   deren Ecken zu verschiedenen Gliedmaßen gehören bzw. hinteren Schwanz mit Körper verbinden.
5. Gewichte: jeder Vertex gehört exklusiv zur nächsten Gliedmaße (+ Körper in Ansatznähe), geglättet, Duplikate gleich.

Skelett: `Root · Hips · Spine_1 · Chest · Neck_1/2 · Head · Leg_<L|R><n>_1..4 · Claw_<L|R>_1..3 · Tail_1..5 · Stinger`.
