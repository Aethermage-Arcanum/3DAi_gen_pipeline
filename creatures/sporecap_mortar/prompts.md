# Bildprompts: Sporecap Mortar

Bauplan: **Stationär (Turm, Nest, Pflanze)** · Stil: **Artist B: Clean Low-Poly Stylized (Projekt-Standard)** · Ordner: `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sporecap_mortar\input`

**Kein Concept – das Design-Bild ist der Design-Entwurf.** Stufe 1 entwirft die Kreatur nur aus der Beschreibung (`look`) und der Stil-Referenz. **Prüfe es (du = Nutzer)** und lass es ggf. neu generieren – erst wenn es dir gefällt, wird es als `input/design.png` verbindlich. Stufe 2 macht daraus die 4 Ansichten für Tripo. Beschreibung ändern: `look` in `creatures/roster.toml` (oder `creature.toml`), dann `python scripts/make_prompts.py` erneut starten.

## Stufe 1 – Design-Bild → `input/design.png`

Neuer ChatGPT-Chat. **Anhängen, in dieser Reihenfolge:**

1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Sporecap Mortar" - an original design with a bold silhouette that reads well from a top-down game camera:

A giant living mushroom turret that lobs spore bombs - rooted, bloated and poisonous. It stands on a thick, squat, fleshy stalk that spreads at the bottom into a wide base of gripping, root-like tendrils clamped to the ground. On top sits a huge, wide mushroom cap facing up, with a round, puckered opening in its center like the barrel of a mortar. The cap is deep violet with large pale lilac spots and a ring of short, thick, fleshy spikes along its rim. Under the cap grow thick, soft gills in pale cream, and a cluster of round, swollen spore sacs bulges from the side of the stalk like ripe fruit. The stalk is pale bone-white with violet veins. Materials: soft, matte, spongy mushroom flesh and slightly wet, glossy spore sacs. Palette: dark violet and bone white with sickly yellow-green tints on the sacs.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still and upright on its base, the base flat on the ground, the top facing up and forward, all flaps, petals or tendrils open, symmetric and apart from each other. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

**Prüfen (du):** Ist das dein Monster? Charakter, Silhouette von schräg oben, Anzahl der Beine/Teile, Farben, Stil (clean Low-Poly). Wenn nicht: im selben Chat neu generieren lassen („nochmal, aber …“) oder `look` anpassen. Wenn ja: als PNG speichern unter
`H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sporecap_mortar\input\design.png`

## Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Neuer ChatGPT-Chat. **Anhängen:** 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sporecap_mortar\input\design.png` (noch nicht vorhanden – erst Stufe 1)

```text
Image 1 is the approved, binding design of my creature "Sporecap Mortar": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A giant living mushroom turret that lobs spore bombs - rooted, bloated and poisonous. It stands on a thick, squat, fleshy stalk that spreads at the bottom into a wide base of gripping, root-like tendrils clamped to the ground. On top sits a huge, wide mushroom cap facing up, with a round, puckered opening in its center like the barrel of a mortar. The cap is deep violet with large pale lilac spots and a ring of short, thick, fleshy spikes along its rim. Under the cap grow thick, soft gills in pale cream, and a cluster of round, swollen spore sacs bulges from the side of the stalk like ripe fruit. The stalk is pale bone-white with violet veins. Materials: soft, matte, spongy mushroom flesh and slightly wet, glossy spore sacs. Palette: dark violet and bone white with sickly yellow-green tints on the sacs.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still and upright on its base, the base flat on the ground, the top facing up and forward, all flaps, petals or tendrils open, symmetric and apart from each other.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above the top, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

Die Bilder nacheinander als `front.png`, `left.png`, `right.png`, `back.png` in `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sporecap_mortar\input` speichern. Macht ChatGPT doch ein Raster: „Bitte jede Ansicht als eigenes Bild“ nachschieben.

## Prüfung vor Tripo (Claude, Pflicht)

Claude prüft die 4 Ansichten nach der Checkliste in `README.md` („Prüfung von Referenzbild und Tripo-Modell“, Teil A): Reihenfolge/Blickrichtung, gleiche Haltung in allen Ansichten, nichts zwischen den Beinen, Beine vorn und hinten gleich breit, Gliedmaßen frei, gerade Grundpose, Teilezahl wie im Design, dünne Teile mit Volumen, kein Glühen. Bei einem Befund: Bild neu machen statt im Rig reparieren.
