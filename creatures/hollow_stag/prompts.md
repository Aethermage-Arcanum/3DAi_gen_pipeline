# Bildprompts: Hollow Stag

Bauplan: **Vierbeiner (Bestie, Wolf, Echse)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input`

**Zwei Stufen:** Stufe 1 macht aus dem kleinen Concept-Ausschnitt EIN sauberes Design-Bild, das du gegen dein Concept prüfst. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input\concept\design_A.png`
2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Hollow Stag". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A gaunt, haunted stag - eerie, silent and noble, like a deer that has been hollowed out. The body is tall and thin, with a long, slender neck, a narrow chest and long, thin legs ending in small dark hooves. Its hide is charcoal black with dark red, raw-looking streaks and patches on the neck, shoulders and flanks. The head is narrow and deer-like with small red eyes. Large, branching antlers rise high above the head, rust-brown to dark red with pale tips. A ragged tuft of pale grey, bone-like bristles and spines sticks up from the back above the shoulders and the hips. A short tail. Materials: thin, matte hide stretched over bones, hard antlers.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing calmly on all four long legs, every leg straight and vertical directly under the body like pillars, front and hind legs equally close together with the hooves about hip-width apart and parallel, hind legs not splayed or bowed outward, head held high facing forward, mouth closed, tail hanging short behind (never between the legs), the antlers rising freely above the head without touching the back or the neck. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Passt das Bild zu deinem Concept – Charakter, Körperbau, Anzahl der Beine/Teile, Farben? Wenn nicht: neu generieren lassen oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input\design.png` (noch nicht vorhanden – erst Stufe 1)

```text
Image 1 is the approved, binding design of my creature "Hollow Stag": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A gaunt, haunted stag - eerie, silent and noble, like a deer that has been hollowed out. The body is tall and thin, with a long, slender neck, a narrow chest and long, thin legs ending in small dark hooves. Its hide is charcoal black with dark red, raw-looking streaks and patches on the neck, shoulders and flanks. The head is narrow and deer-like with small red eyes. Large, branching antlers rise high above the head, rust-brown to dark red with pale tips. A ragged tuft of pale grey, bone-like bristles and spines sticks up from the back above the shoulders and the hips. A short tail. Materials: thin, matte hide stretched over bones, hard antlers.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing calmly on all four long legs, every leg straight and vertical directly under the body like pillars, front and hind legs equally close together with the hooves about hip-width apart and parallel, hind legs not splayed or bowed outward, head held high facing forward, mouth closed, tail hanging short behind (never between the legs), the antlers rising freely above the head without touching the back or the neck.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
