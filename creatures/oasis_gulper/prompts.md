# Bildprompts: Oasis Gulper

Bauplan: **Vierbeiner (Bestie, Wolf, Echse)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\oasis_gulper\input`

**Kein Concept – das Design-Bild ist der Design-Entwurf.** Stufe 1 entwirft die Kreatur nur aus der Beschreibung (`look`) und der Stil-Referenz. **Prüfe es (du = Nutzer)** und lass es ggf. neu generieren – erst wenn es dir gefällt, wird es als `input/design.png` verbindlich. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Oasis Gulper" - an original design with a bold silhouette that reads well from a top-down game camera:

A huge, bloated oasis toad - a lazy-looking ambusher that snaps prey from afar with its long tongue. The body is broad, round and squat, sitting low, with a wide, flat head that merges into the body without a neck. The mouth is enormous, a wide grinning slit across the whole front of the head, with a pale yellow throat pouch below. Two big, bulging amber eyes sit on top of the head. The front legs are short and sturdy, the hind legs big and powerful with long webbed feet. The back is covered with warty bumps, and a few small, flat lily pads and reeds grow from the skin like a living pond. The skin is turquoise and teal on top with dark spots, sandy yellow on the belly, with bold orange warning stripes along the sides. Materials: smooth, glossy, wet skin with rough warts. Palette: turquoise water colors with warm sand and orange accents.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: sitting low on all fours, front legs straight down, the big hind legs folded beside the body with a clear gap to the belly, feet flat on the ground, head forward, mouth closed. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Ist das dein Monster? Charakter, Silhouette von schräg oben, Anzahl der Beine/Teile, Farben, Stil (clean Low-Poly). Wenn nicht: im selben Chat neu generieren lassen („nochmal, aber …“) oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\oasis_gulper\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\oasis_gulper\input\design.png` (noch nicht vorhanden – erst Stufe 1)

```text
Image 1 is the approved, binding design of my creature "Oasis Gulper": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A huge, bloated oasis toad - a lazy-looking ambusher that snaps prey from afar with its long tongue. The body is broad, round and squat, sitting low, with a wide, flat head that merges into the body without a neck. The mouth is enormous, a wide grinning slit across the whole front of the head, with a pale yellow throat pouch below. Two big, bulging amber eyes sit on top of the head. The front legs are short and sturdy, the hind legs big and powerful with long webbed feet. The back is covered with warty bumps, and a few small, flat lily pads and reeds grow from the skin like a living pond. The skin is turquoise and teal on top with dark spots, sandy yellow on the belly, with bold orange warning stripes along the sides. Materials: smooth, glossy, wet skin with rough warts. Palette: turquoise water colors with warm sand and orange accents.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: sitting low on all fours, front legs straight down, the big hind legs folded beside the body with a clear gap to the belly, feet flat on the ground, head forward, mouth closed.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\oasis_gulper\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
