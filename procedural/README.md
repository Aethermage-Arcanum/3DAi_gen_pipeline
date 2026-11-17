# Prozedurale Anbauteile ("Monster Anbauteile")

Geometry-Nodes-System für Blender: wiederkehrende Details (Stacheln, Panzerplatten, später Hörner, Kristalle, Seepocken, Eier, Tentakel) werden über Slider auf einen Grundkörper gesetzt, statt von Hand modelliert oder einzeln generiert zu werden.

## Dateien
- `addon_nodes.py`: baut die Node-Gruppe „Monster Anbauteile“ (alle Slider + Standardwerte in `SLIDERS`)
- `demo.py`: Testkörper + Varianten aus `demo_variants.toml` rendern
- `demo_variants.toml`: 6 Varianten, nur über Slider-Werte und Farben definiert
- `make_grid.py`: Renders zu einem beschrifteten Raster zusammensetzen
- `demo_output/procedural_parts.blend`: **zum Selbst-Ausprobieren** in Blender öffnen, Objekt „Testkoerper“ wählen, Modifier-Tab, an den Slidern drehen

## Ausführen
```
& "D:\Blender\blender.exe" -b --factory-startup -P procedural/demo.py -- procedural/demo_output
python procedural/make_grid.py procedural/demo_output
```

## Slider (Auszug)
**Stacheln:** Dichte, Abstand, Länge, Breite, Kanten (Polygon-Kosten), Neigung nach hinten, Zufall Größe, Abdeckung (nur Oberseite … überall), Kammbreite (Streifen entlang Rückgrat), Seed
**Platten:** Dichte, Abstand, Größe, Streckung, Dicke, Kanten, Schuppung (Überlappung), Zufall Größe, Abdeckung, Seed
**Materialien:** Körper/Stachel/Platten-Material, Flat Shading

## Erkenntnisse aus der ersten Demo (2026-11-17)
| Variante | Dreiecke |
|---|---|
| Grundkörper | 240 |
| Rückenkamm | 308 |
| viele Dornen | 728 |
| **dichte Platten** | **4.520** |
| große Platten + Stacheln | 988 |
| Frost | 1.668 |

- **Stacheln sind spottbillig:** 4-kantige Stacheln kosten 4 Dreiecke pro Stück.
- **Dichte Platten als Geometrie sind teuer** (20 Dreiecke pro Platte) und wirken aufgesetzt. → Kleine Schuppen gehören in die **Normal Map/Textur**. Nur große, silhouettenbildende Platten sind echte Geometrie.
- Achsen-Konvention: Kopf zeigt nach −Y, oben ist +Z. Die Kamm-Maske nutzt aktuell die Mittellinie x=0, später die Wirbelsäulen-Knochen des Rigs.

## Offen
- Masken über Rig-Knochen (Kamm entlang Wirbelsäule, Hörner am Kopf-Knochen)
- Starres Anhängen an den nächsten Knochen (Gewichte übertragen) + Unity-Export-Test
- Schuppen/Platten als gebackene Normal Map statt Geometrie
- Weitere Elemente: Hörner, Kristalle, Seepocken, Eier, Tentakel
- Gemeinsamer Material-Atlas für alle Anbauteile
