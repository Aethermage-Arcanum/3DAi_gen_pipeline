# Bildprompts: Tomb Shroud

Bauplan: **Schwebend (Geist, Auge, Kugel)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\tomb_shroud\input`

**Kein Concept – das Design-Bild ist der Design-Entwurf.** Stufe 1 entwirft die Kreatur nur aus der Beschreibung (`look`) und der Stil-Referenz. **Prüfe es (du = Nutzer)** und lass es ggf. neu generieren – erst wenn es dir gefällt, wird es als `input/design.png` verbindlich. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Tomb Shroud" - an original design with a bold silhouette that reads well from a top-down game camera:

A silent crypt wraith - a hooded shroud that floats above the ground, mournful and menacing. It has no legs: the hunched, hooded upper body is wrapped in heavy, tattered grave cloth that hangs down and narrows into a ragged, pointed tail of cloth. Inside the deep hood there is only darkness and a pale, cracked bone mask with two hollow eye holes. Two long, thin, bony arms reach out from the cloth, each ending in a hand with long, hooked, bone-white claws. The cloth is thick and heavy, layered in folds, with torn edges and a few broad, dangling strips, and old rusted chains are wrapped around the chest. Colors: faded ash-grey and dusty bone-white cloth that darkens to deep charcoal at the hem, with a sickly pale green tint in the folds; mask and claws are old ivory. Materials: heavy, coarse burial linen, dry bone and corroded iron.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: floating upright above the ground, both arms held out and angled down away from the body, claws open and apart, the cloth tail hanging straight down without touching the ground. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Ist das dein Monster? Charakter, Silhouette von schräg oben, Anzahl der Beine/Teile, Farben, Stil (clean Low-Poly). Wenn nicht: im selben Chat neu generieren lassen („nochmal, aber …“) oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\tomb_shroud\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\tomb_shroud\input\design.png` (noch nicht vorhanden – erst Stufe 1)

```text
Image 1 is the approved, binding design of my creature "Tomb Shroud": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A silent crypt wraith - a hooded shroud that floats above the ground, mournful and menacing. It has no legs: the hunched, hooded upper body is wrapped in heavy, tattered grave cloth that hangs down and narrows into a ragged, pointed tail of cloth. Inside the deep hood there is only darkness and a pale, cracked bone mask with two hollow eye holes. Two long, thin, bony arms reach out from the cloth, each ending in a hand with long, hooked, bone-white claws. The cloth is thick and heavy, layered in folds, with torn edges and a few broad, dangling strips, and old rusted chains are wrapped around the chest. Colors: faded ash-grey and dusty bone-white cloth that darkens to deep charcoal at the hem, with a sickly pale green tint in the folds; mask and claws are old ivory. Materials: heavy, coarse burial linen, dry bone and corroded iron.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: floating upright above the ground, both arms held out and angled down away from the body, claws open and apart, the cloth tail hanging straight down without touching the ground.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\tomb_shroud\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
