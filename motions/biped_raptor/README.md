# Skelett biped_raptor (Zweibeiner mit Schwanz: Raptoren, Laufvögel)

Rig: `rigging/biped_raptor_rig.py` (Werte `rigging/biped_raptor_defaults.toml`, pro Kreatur `[biped_raptor]`).
Clips nutzen den **Beine-Baukasten** `motions/quadruped/quadruped_kit.py` (Blender-IK, Rumpf-Absenkung, Prüfung) – er liest die Beine aus dem Rig.
Muster: `raptor/`. Ein Befehl: `python scripts/creature_pipeline.py creatures/<name>`.

## Skelett (26 Knochen)
`Root · Hips → Spine_1 → Chest → Neck_1 → Neck_2 → Head → Jaw · Hips → Tail_1..4 · Chest → Arm_L/R_1..3`
Beine `Leg_BL/BR_1..4`: Oberschenkel (im Körper), Schienbein, Mittelfuß (Sprunggelenk → Ballen), Zehen.

## Besonderheiten (aus dem ersten Modell gelernt)
- **Vogelbein:** Knie sitzt verdeckt am Bauch und zeigt nach vorn, sichtbar ist nur das Sprunggelenk (nach hinten). Knie wird deshalb anatomisch gesetzt, Sprunggelenk aus der Beinspur.
- **Arme:** tiefste Krallenspitze vorn unter der Brust (Bein-Bereich ausgeschlossen), nach oben verfolgt; Schulter auf Brustbreite begrenzt.
- **Tripo-Hautbrücke zwischen den Beinen** (verschmolzene Innenseiten + hängende Membran): reißt bei JEDER Gewichtung → `cut_between_legs` löscht Flächen, deren Ecken zu beiden Beinen gehören, unterhalb des Bauchs. Danach gehört jeder Vertex exklusiv zum näheren Bein.
- Lückenprüfung ignoriert Paare linkes/rechtes Glied (Beine im Gegentakt sind keine Gelenk-Lücke).
