# Skelett floater (Schweber: Orbs, Quallen, Kraken)

Rig: `rigging/floater_rig.py` (Werte `rigging/floater_defaults.toml`, pro Kreatur `[floater]`). Baukasten: `floater_kit.py`. Muster: `tentacle/`.
Ein Befehl: `python scripts/creature_pipeline.py creatures/<name>`.

## Skelett (automatisch, Anzahl hängt vom Modell ab)
`Root (Boden) → Core (Kern) → Tent_<NN>_<k>` – jede Tentakel-/Stachel-Kette von der **echten Wurzel** zur Spitze (1–5 Knochen, nach Länge).
Void Manifestation: 21 Ketten, 74 Knochen (bis 2026-11-17: 19 Ketten ab der Kernkugel, 46 Knochen – obere Tentakel-Hälften starr).

## Erkennung
1. Kern = dichtester Bereich (iterativ), Kernradius = Dichte-Spitze der Abstände × `core_scale`.
2. Alles außerhalb der Kernkugel zerfällt über Mesh-Kanten in zusammenhängende Stücke = Tentakel.
   **Kernkugel groß genug wählen** (`core_scale` 1,7): sonst hängen Tentakel über einen Ring zusammen und werden ein Klumpen.
3. **Wurzel-Verlängerung** (`root_depth` < 1): Jedes Stück wächst über Mesh-Kanten in die Kernkugel hinein bis zur echten
   Wurzel (nur nach innen, in einer Röhre um die verlängerte Tentakel-Achse, `root_radius`, `root_bend_to_core`). Auch winzige
   Stücke (`seed_min_verts`) wachsen mit und zählen danach als Tentakel. Weicher Saum ins Kern-Mesh (`ring_fade`), gemittelte
   Nähte, wo zwei Tentakel an der Wurzel verwachsen sind. `root_depth = 1.0` = altes Verhalten.
4. `facing`: Tripo kann das Modell gedreht liefern (Void Manifestation schaute nach −Y) → wird nach +X gedreht.

## Bausteine
`core()` schweben/neigen · `wobble()` + `drive()` (seit 2026-11-17, alle Clips außer Death): Wellen über die ganze Kette ab der
Wurzel + Nachschwingen als gedämpfte Feder aus der Kern-Beschleunigung, Werte `[wobble]` in der style.toml des Musters ·
`tentacles()` (alt, nur noch Death) Wellen mit Phasenversatz entlang der Kette, `trail` (nachschleppen), `spread` (spreizen), `curl` (einrollen) – Ausschlag durch max(Knochenzahl, 3) geteilt, sonst schwingen kurze Stummel zu stark · `ground_above()` nie im Boden.

## Selbstprüfung
Schwebt (tiefster Punkt nie im Boden) · Tod liegt am Boden · Schleifen · Rückkehr (Ruhe = Schwebehöhe des 1. Frames) · Mesh-Dehnung · Export-Gegentest.
