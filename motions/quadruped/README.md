# Skelett quadruped (Vierbeiner)

Rig: `rigging/quadruped_rig.py` (Werte: `rigging/quadruped_defaults.toml`, pro Kreatur `[quadruped.*]` in creature.toml).
Baukasten: `quadruped_kit.py`. Muster: `wolf/` (weitere geplant: lizard, deer, boar, tortoise, behemoth, gorilla).
Ein Befehl: `python scripts/creature_pipeline.py creatures/<NN_name>`.

## Standard-Skelett (30 Knochen, Unity „Generic“)
`Root · Hips → Spine_1 → Chest → Neck_1 → Neck_2 → Head → Jaw · Hips → Tail_1..4 · Chest → Shoulder_FL/FR`
Beine `Leg_<FL|FR|BL|BR>_1..4`: vorne Oberarm · Unterarm · Mittelhand · Zehen, hinten Oberschenkel · Schienbein · Mittelfuß · Zehen.

## Wie das Rig entsteht (automatisch)
1. Füße = Vertices am Boden, per k-means in vorne/hinten × links/rechts.
2. Beine von unten nach oben verfolgen (Querschnitt-Schwerpunkte) bis zur Bauchlinie; Knie/Sprunggelenk = stärkste Biegung, sonst Standardanteile.
3. Wirbelsäule/Hals/Kopf/Schwanz aus Querschnitten entlang X (Kopf zeigt +X).
4. Gewichte: 1/Abstand⁴ zu den Knochen mit **anatomischen Masken** (Bein-Knochen nur eigene Seite + unterhalb Schulter/Hüfte, Hals nicht an der Brust …), 6× über Kanten geglättet, max. 4 Einflüsse.
   **Wichtig:** Tripo trennt Vertices an UV-Nähten → doppelte Vertices bekommen exakt gleiche Gewichte (sonst reißt das Mesh bis 5 cm auf).
5. Debug-Skizze: `rig/rig_debug.png` (Seite + Draufsicht, Knochen über Mesh-Punkten).

## Wie die Clips entstehen („Aufwand nach Blender“)
- Beine = **Blenders IK** (Kette 3 Knochen, vorne +Schulterblatt mit Steifigkeit 0,6), Ziel-Empty am Fußballen trägt die Zehen-Ausrichtung.
- Clip setzt pro Frame nur Fuß-Ziele + Rumpf/Hals/Kopf/Kiefer/Schwanz. `reach_fix` senkt den Rumpf, falls ein Bein überstreckt wäre.
- `bake()` liest die visuelle Pose aus, entfernt Constraints/Empties und schreibt reine FK-Keyframes (Unity-tauglich).

## Selbstprüfung pro Clip
Fußkontakt (Ballen im Stand auf Bodenhöhe, rutscht nicht) · IK erreicht Ziel · Mindestschritt · Schleife nahtlos · Füße stehen (Stand-Clips) · Rückkehr zur Ruhe · Tod ohne Bodendurchdringung · **Mesh-Dehnung** (größte Kantendehnung + Knochen + Frame) · Lückenprüfung · Export-Gegentest.
