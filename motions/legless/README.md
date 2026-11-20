# Skelett legless (beinlos: Schlangen, Aale, Würmer)

Rig: `rigging/legless_rig.py` (Werte `rigging/legless_defaults.toml`, pro Kreatur `[legless]`), gemeinsame Rig-Bausteine `rigging/rig_common.py`.
Baukasten: `legless_kit.py`. Muster: `cobra/` (geplant: sandworm, Variante eel).
Ein Befehl: `python scripts/creature_pipeline.py creatures/<NN_name>`.

## Standard-Skelett (17 Knochen bei 14 Wirbeln, Unity „Generic“)
`Root → Spine_01 (Schwanzspitze) → … → Spine_14 → Head → Jaw`. Wirbel liegen auf der Körpermittellinie (Querschnitte entlang X).

## Bausteine
- `wave()` – Krümmungswelle, läuft vom Kopf zum Schwanz (laterale Undulation), Schwanzspitze + Kopf gedämpft
- `bend()` – gleichmäßige Krümmung über einen Bereich (seitlich oder auf/ab, z. B. Aufrichten)
- `head()` – Kopf drehen/nivellieren, **verteilt auf Kopf + 2 letzte Wirbel** (ein Gelenk allein reißt das Mesh)
- `keep_centered()` – Blickrichtung + Körpermitte bleiben fest (Clips „in place“)
- `ground("contact"|"above")` – tiefster Punkt auf dem Boden bzw. nur nicht einsinken

**Absolute Körperform (seit 2026-11-17, für alle neuen Clips verwenden):** Tripo liefert Schlangen oft schon verbogen
(Eel Stalker: S-Kurve ±45°, Vorderkörper +54°). Die Bausteine oben addieren auf diese Ruhepose.
- `shape(yaw[], pitch[], head_yaw, head_pitch, neck=2)` – Richtung jedes Wirbels absolut (Grad, gegenüber gerader
  waagerechter Linie entlang +X); Kopfneigung relativ zur modellierten Kopfhaltung; Kopf-Knick auf Hals verteilt
- `seg_s()` Bogenlänge je Wirbel · `interp([[s, wert], …], s)` glatte Profile · `place(punkt, lo, hi)` Schwerpunkt
  eines Körperbereichs festhalten · `centroid()`, `head_tip()` für Messungen
- `bake`: optional `returns_to_start` (Clip endet in seiner Anfangspose, z. B. Attack/Hit → Ready) und `measure`

## Selbstprüfung pro Clip
Bodenkontakt / kein Einsinken (tiefster Mesh-Punkt jedes Frames) · Schleife nahtlos · Rückkehr zur Ruhe · Mesh-Dehnung (Ort + Frame) · Lückenprüfung · Export-Gegentest.
