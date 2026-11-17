# Bewegungsmuster quadruped/lizard (Echse/Krokodil)

Generator: `../wolf/wolf_clips.py` (gemeinsamer Vierbeiner-Generator), Werte `style.toml`. Erstes Modell: **Reef Snapper** (2026-11-17), alle 9 Clips grün.

Unterschiede zum Wolf (nur Werte): **Trab mit Diagonalpaaren** + **seitliche Wirbelsäulenwelle** (`spine_side_deg`, Waran-Gang), großer Schwanzschwung,
Drohen mit aufgerissenem Maul (Kopf hoch statt Pirsch), Schnappbiss mit Kopfschlag zur Seite (`snap_yaw_deg`), Tod: Beine lassen spät los (`ik_release_start`).

## Naturreferenzen / Videos
„komodo dragon walking slow motion“ (seitliche Welle, Diagonalgang), „crocodile high walk“, „crocodile snap bite slow motion“, „monitor lizard threat gape“.

## Offen
Ready/Attack wirken aus der Spielkamera noch dezent (Maul darf wegen Mundwinkel-Dehnung nur ~13° öffnen) → Kopf-/Körperbewegung verstärken.
