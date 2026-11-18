# Bildprompts: Chitin Crawler

Bauplan: **Sechsbeiner (Insekt, Käfer, Ameise)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input`

**Zwei Stufen:** Stufe 1 macht aus dem kleinen Concept-Ausschnitt EIN sauberes Design-Bild, das du gegen dein Concept prüfst. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\1_design_chitin_crawler_A.png`
2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature: take its design, silhouette and colors; the description below adds the details. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Chitin Crawler". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

ant-like forest insect predator: small head with a glossy green carapace and short mandibles, reddish-brown segmented chitin armor plates on thorax and a large rounded abdomen, long thin jointed legs with dark tips, two short antennae.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, all six legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, antennae forward and apart, mandibles closed. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Passt das Bild zu deinem Concept – Charakter, Körperbau, Anzahl der Beine/Teile, Farben? Wenn nicht: neu generieren lassen oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\design.png` (noch nicht vorhanden – erst Stufe 1)

```text
Image 1 is the approved, binding design of my creature "Chitin Crawler": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): ant-like forest insect predator: small head with a glossy green carapace and short mandibles, reddish-brown segmented chitin armor plates on thorax and a large rounded abdomen, long thin jointed legs with dark tips, two short antennae.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body level, all six legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, antennae forward and apart, mandibles closed.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
