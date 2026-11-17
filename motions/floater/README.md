# Skelett floater (Schweber: Orbs, Quallen, Kraken)

Rig: `rigging/floater_rig.py` (Werte `rigging/floater_defaults.toml`, pro Kreatur `[floater]`). Baukasten: `floater_kit.py`. Muster: `tentacle/`.
Ein Befehl: `python scripts/creature_pipeline.py creatures/<name>`.

## Skelett (automatisch, Anzahl hängt vom Modell ab)
`Root (Boden) → Core (Kern) → Tent_<NN>_<k>` – jede Tentakel-/Stachel-Kette vom Ansatz zur Spitze (1–5 Knochen, nach Länge).
Void Manifestation: 19 Ketten.

## Erkennung
1. Kern = dichtester Bereich (iterativ), Kernradius = Dichte-Spitze der Abstände × `core_scale`.
2. Alles außerhalb der Kernkugel zerfällt über Mesh-Kanten in zusammenhängende Stücke = Tentakel.
   **Kernkugel groß genug wählen** (`core_scale` 1,7): sonst hängen Tentakel über einen Ring zusammen und werden ein Klumpen.
3. `facing`: Tripo kann das Modell gedreht liefern (Void Manifestation schaute nach −Y) → wird nach +X gedreht.

## Bausteine
`core()` schweben/neigen · `tentacles()` Wellen mit Phasenversatz entlang der Kette, `trail` (nachschleppen), `spread` (spreizen), `curl` (einrollen) – Ausschlag durch max(Knochenzahl, 3) geteilt, sonst schwingen kurze Stummel zu stark · `ground_above()` nie im Boden.

## Selbstprüfung
Schwebt (tiefster Punkt nie im Boden) · Tod liegt am Boden · Schleifen · Rückkehr (Ruhe = Schwebehöhe des 1. Frames) · Mesh-Dehnung · Export-Gegentest.
