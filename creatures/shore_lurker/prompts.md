# Bildprompts: shore_lurker

Bauplan: **Vierbeiner (Bestie, Wolf, Echse)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)**

**So geht's:** Neuen ChatGPT-Chat öffnen, Bilder anhängen, den einen Prompt einfügen. Die Bilder als PNG unter den angegebenen Namen speichern in:

`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shore_lurker\input`

Gefällt Bild 1 nicht: einfach neu generieren lassen oder die Beschreibung in `creature.toml` anpassen und dieses Skript erneut starten.

**Anhängen in ChatGPT, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\_concept\monster_categories_A_vs_B.webp`
2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

## Ein Prompt für alle 4 Ansichten

ChatGPT erzeugt die Bilder nacheinander. Speichern als `front.png`, `left.png`, `right.png`, `back.png`. Falls es doch ein Raster macht: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

```text
I attached reference images. Image 1 shows the creature DESIGN to recreate: keep its anatomy, body segments, number of legs, head shape, proportions and color scheme. Image 2 is only an ART STYLE reference: copy its rendering style, not the creatures shown in it. Ignore any text, labels, scenery and background in the attached images.

Create clean reference images of the creature from the design image for 3D modeling. Image 1 is a concept sheet with many creatures: use ONLY the creature labeled "Shore Lurker", Artist A version, and ignore all others.

Creature: the creature labeled "Shore Lurker" (Artist A version) in the design image: low, flat coastal ambush reptile, four legs

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset

Please generate 4 SEPARATE images, one after another (NOT a grid, NOT a collage, NOT one sheet with several views). All images show EXACTLY the same creature - identical design, proportions, number of legs, colors, materials, pose and lighting. Only the camera angle changes:
1. `front.png` - front view: the creature faces the camera directly
2. `left.png` - exact side view of the creature's own LEFT flank: rotated 90 degrees, its head points to the LEFT edge of the image
3. `right.png` - exact side view of the creature's own RIGHT flank: rotated 90 degrees, its head points to the RIGHT edge of the image
4. `back.png` - exact rear view: rotated 180 degrees, we see the creature from directly behind

Keep the exact number of legs, wings, tails and claws of the design and keep all of them clearly visible and separated in every view.

Requirements for a 3D-model reference image:
- exactly one creature, centered, the entire body in frame with some margin, nothing cut off
- plain flat medium-grey (#9a9a9a) background, no ground texture, no scenery, no props, no text, no watermark
- soft, even, diffuse studio lighting from all sides, no cast shadows, no strong highlights, no rim light, no glow or bloom effects
- sharp focus everywhere, no depth of field, no motion blur, no smoke, no particles
- neutral rigging pose: standing still, all four legs straight and slightly apart, each leg clearly separated and visible, weight evenly on all four feet, head facing straight forward, mouth closed, tail extended straight back, no twisting
- camera at body height, very slightly elevated, orthographic-like, no perspective distortion
- square 1:1 image
```

## Kontrolle vor dem Tripo-Schritt

- Alle Bilder zeigen dieselbe Kreatur (Farben, Anzahl Beine/Augen, Muster)?
- Beine/Flügel klar getrennt, nichts überkreuzt, nichts abgeschnitten?
- Keine harten Schatten, keine Glüh-Effekte?

Wenn eine Ansicht danebengeht, lass sie weg. Tripo braucht nur `front.png` plus mindestens eine weitere.
