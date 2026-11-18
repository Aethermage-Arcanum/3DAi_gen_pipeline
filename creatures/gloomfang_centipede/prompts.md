# Bildprompts: Gloomfang Centipede

Bauplan: **Schlange, Wurm** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\gloomfang_centipede\input`

**Kein Concept – das Design-Bild ist der Design-Entwurf.** Stufe 1 entwirft die Kreatur nur aus der Beschreibung (`look`) und der Stil-Referenz. **Prüfe es (du = Nutzer)** und lass es ggf. neu generieren – erst wenn es dir gefällt, wird es als `input/design.png` verbindlich. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Gloomfang Centipede" - an original design with a bold silhouette that reads well from a top-down game camera:

A giant cave centipede - a fast, writhing hunter of the deep tunnels with venomous claws. The body is a long, flat chain of armored segments, each with a pair of long, jointed, sharp-tipped legs spread out to the sides, giving it a dense fringe of legs along its whole length. The head is flat and shield-shaped, with a pair of long, segmented antennae sweeping forward and a pair of huge, curved, pincer-like venom claws at the front. At the rear end, two long trailing legs point backward like a second pair of antennae. The armor plates are glossy dark maroon to black-red, each segment edged with a lighter rust-orange rim; the legs are pale amber with dark tips. Materials: polished, hard, segmented chitin. Palette: deep blood red and black, with the amber legs as a bright fringe.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long and straight on the ground, not coiled, all leg pairs spread evenly to both sides, none crossing, head slightly raised and facing forward, venom claws closed. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Ist das dein Monster? Charakter, Silhouette von schräg oben, Anzahl der Beine/Teile, Farben, Stil (clean Low-Poly). Wenn nicht: im selben Chat neu generieren lassen („nochmal, aber …“) oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\gloomfang_centipede\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\gloomfang_centipede\input\design.png` (noch nicht vorhanden – erst Stufe 1)

```text
Image 1 is the approved, binding design of my creature "Gloomfang Centipede": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A giant cave centipede - a fast, writhing hunter of the deep tunnels with venomous claws. The body is a long, flat chain of armored segments, each with a pair of long, jointed, sharp-tipped legs spread out to the sides, giving it a dense fringe of legs along its whole length. The head is flat and shield-shaped, with a pair of long, segmented antennae sweeping forward and a pair of huge, curved, pincer-like venom claws at the front. At the rear end, two long trailing legs point backward like a second pair of antennae. The armor plates are glossy dark maroon to black-red, each segment edged with a lighter rust-orange rim; the legs are pale amber with dark tips. Materials: polished, hard, segmented chitin. Palette: deep blood red and black, with the amber legs as a bright fringe.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body stretched out long and straight on the ground, not coiled, all leg pairs spread evenly to both sides, none crossing, head slightly raised and facing forward, venom claws closed.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\gloomfang_centipede\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
