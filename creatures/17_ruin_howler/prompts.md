# Bildprompts: Ruin Howler

Bauplan: **Vierbeiner (Bestie, Wolf, Echse)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\17_ruin_howler\input`

**Kein Concept – das Design-Bild ist der Design-Entwurf.** Stufe 1 entwirft die Kreatur nur aus der Beschreibung (`look`) und der Stil-Referenz. **Prüfe es (du = Nutzer)** und lass es ggf. neu generieren – erst wenn es dir gefällt, wird es als `input/design.png` verbindlich. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Ruin Howler" - an original design with a bold silhouette that reads well from a top-down game camera:

A lanky, savage temple ape that lives in overgrown ruins - loud, agile and hurling chunks of stone. It walks on all fours on its long, powerful arms and shorter, bent legs, and has a long, thick tail. Its body is lean, with a hunched back and a broad chest. The head has a long, dog-like snout, a jaw full of long canine fangs and deep-set red eyes under a heavy brow; a mane of stiff, bristling hair frames the face and shoulders. Fragments of carved temple stone and tarnished gold rings are grown into the skin of its shoulders and forearms like trophies. The fur is dark rusty brown, lighter and sand-colored on the chest, and the bare face carries a vivid crimson and blue mask like a mandrill. Materials: coarse fur shaped as clean faceted clumps, bare leathery face, stone and old gold. Palette: rusty browns and sand with the vivid face as the eye-catcher.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Ist das dein Monster? Charakter, Silhouette von schräg oben, Anzahl der Beine/Teile, Farben, Stil (clean Low-Poly). Wenn nicht: im selben Chat neu generieren lassen („nochmal, aber …“) oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\17_ruin_howler\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\17_ruin_howler\input\design.png` (✅ liegt schon vor)

```text
Image 1 is the approved, binding design of my creature "Ruin Howler": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A lanky, savage temple ape that lives in overgrown ruins - loud, agile and hurling chunks of stone. It walks on all fours on its long, powerful arms and shorter, bent legs, and has a long, thick tail. Its body is lean, with a hunched back and a broad chest. The head has a long, dog-like snout, a jaw full of long canine fangs and deep-set red eyes under a heavy brow; a mane of stiff, bristling hair frames the face and shoulders. Fragments of carved temple stone and tarnished gold rings are grown into the skin of its shoulders and forearms like trophies. The fur is dark rusty brown, lighter and sand-colored on the chest, and the bare face carries a vivid crimson and blue mask like a mandrill. Materials: coarse fur shaped as clean faceted clumps, bare leathery face, stone and old gold. Palette: rusty browns and sand with the vivid face as the eye-catcher.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\17_ruin_howler\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
