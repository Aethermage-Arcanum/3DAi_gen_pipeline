# Alle ChatGPT-Prompts – zwei Stufen pro Kreatur

Seit 2026-11-18 (BACKLOG A10). Pro Kreatur:

1. **Stufe 1 – Design-Bild:** neuer ChatGPT-Chat → die genannten Bilder anhängen (Concept-Ausschnitt + Stil-Referenz) → Prompt 1 einfügen → **ein** Bild. **Du prüfst es gegen dein Concept** (Charakter, Körperbau, Anzahl Beine/Teile, Farben). Passt es nicht: neu generieren lassen oder `look` in `creatures/roster.toml` anpassen und `python scripts/make_roster.py` neu starten. Passt es: als `input/design.png` speichern.
2. **Stufe 2 – 4 Ansichten:** neuer ChatGPT-Chat → nur `input/design.png` anhängen → Prompt 2 einfügen → 4 Einzelbilder als `front.png`, `left.png`, `right.png`, `back.png` in denselben `input`-Ordner speichern.
3. **Claude prüft** die 4 Ansichten nach der Checkliste (`README.md`, Teil A), erst dann Tripo.

Kreaturen mit fertigem Tripo-Modell (markiert) brauchen das nur bei einem Neubau – ihre Bilder bleiben, wie sie sind.
Übersicht aller Concept-Ausschnitte: `creatures/concept_crops.png`.

| # | Kreatur | Tripo-Modell | design.png |
|---|---|---|---|
| 2 | [Spore Drone](#2-spore-drone) | – | – |
| 3 | [Needle Wasp](#3-needle-wasp) | ✅ vorhanden | – |
| 4 | [Broodling](#4-broodling) | – | – |
| 5 | [Reef Snapper](#5-reef-snapper) | ✅ vorhanden | – |
| 6 | [Shore Lurker](#6-shore-lurker) | – | – |
| 7 | [Shellback](#7-shellback) | – | – |
| 8 | [Eel Stalker](#8-eel-stalker) | ✅ vorhanden | – |
| 9 | [Ravine Stalker](#9-ravine-stalker) | ✅ vorhanden | – |
| 10 | [Stone Boar](#10-stone-boar) | – | – |
| 11 | [Hollow Stag](#11-hollow-stag) | ✅ vorhanden | – |
| 12 | [Rock Hyena](#12-rock-hyena) | – | – |
| 13 | [Sand Leviathan](#13-sand-leviathan) | – | – |
| 14 | [Dune Raptor](#14-dune-raptor) | ✅ vorhanden | – |
| 15 | [Glassback Colossus](#15-glassback-colossus) | – | – |
| 16 | [Scorpion Matriarch](#16-scorpion-matriarch) | ✅ vorhanden | – |
| 17 | [Frost Colossus](#17-frost-colossus) | – | – |
| 18 | [Flesh Titan](#18-flesh-titan) | – | – |
| 19 | [Void Manifestation](#19-void-manifestation) | ✅ vorhanden | – |
| 20 | [Void Harbinger](#20-void-harbinger) | – | – |
| 21 | [Reality Ripper](#21-reality-ripper) | – | – |

## 2. Spore Drone

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\spore_drone\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\spore_drone\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Spore Drone". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A creepy forest beetle that carries a huge fungal growth on its back - slow, heavy-laden, like a walking mushroom colony. The body is a compact, rounded beetle with a glossy dark red-brown carapace marked with a few thin pale stripes. The head is small and low at the front, with short mandibles and two thin, curled orange antennae. On top of the back sits a big, lumpy cluster of round spore pods like a heap of puffball mushrooms, pale bone-white to creamy beige - it dominates the silhouette, especially from above. Six long, thin, spindly jointed legs lift the body high above the ground; they are olive-green near the body and fade to reddish-orange toward the pointed tips. Patches of mossy green fungal fuzz grow around the neck, the leg joints and the edges of the shell. Materials: hard lacquered chitin on body and legs, soft matte spongy surface on the spore pods. Palette: dark earthy red-brown, olive and moss green, with the pale spore cluster as the bright eye-catcher.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, all six legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, antennae forward and apart, mandibles closed. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\spore_drone\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Spore Drone": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A creepy forest beetle that carries a huge fungal growth on its back - slow, heavy-laden, like a walking mushroom colony. The body is a compact, rounded beetle with a glossy dark red-brown carapace marked with a few thin pale stripes. The head is small and low at the front, with short mandibles and two thin, curled orange antennae. On top of the back sits a big, lumpy cluster of round spore pods like a heap of puffball mushrooms, pale bone-white to creamy beige - it dominates the silhouette, especially from above. Six long, thin, spindly jointed legs lift the body high above the ground; they are olive-green near the body and fade to reddish-orange toward the pointed tips. Patches of mossy green fungal fuzz grow around the neck, the leg joints and the edges of the shell. Materials: hard lacquered chitin on body and legs, soft matte spongy surface on the spore pods. Palette: dark earthy red-brown, olive and moss green, with the pale spore cluster as the bright eye-catcher.

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

## 3. Needle Wasp

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\needle_wasp\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\needle_wasp\input\concept\neelde_wasp.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\needle_wasp\input\concept\style_B_stalk_wasp.png`

```text
Image 1 is my concept art of this creature: take its design, silhouette and colors; the description below adds the details. Image 1 is a concept sheet of this wasp: the big creature is the design, the small panels show details (head, stinger, wings, eggs) and views. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Needle Wasp". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A slender, aggressive forest wasp - clearly a wasp, not an ant - fast, nervous and dangerous. Its armor is dark indigo-violet with sharp, faceted plates on the head and thorax; the abdomen is banded in indigo and warm amber-orange. The head is long and wedge-shaped with bright orange eyes, a row of small fangs and a pair of big, curved, sickle-like orange mandibles; two long, thin, segmented antennae sweep back over the head. A narrow wasp waist connects the thorax to a long, pointed, armored abdomen with small serrated plates, ending in a long, sharp crimson needle stinger - the key feature, always clearly visible. A small cluster of round orange venom sacs bulges on the side of the thorax. Two pairs of large, translucent amber wings with fine darker veins spread out to the sides, clearly apart from the body. Six thin, delicate, fairly short brown-orange legs with pointed tips are held slightly tucked under the body like a hovering wasp. Materials: glossy hard chitin, thin glassy wings, a wet-looking stinger tip.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on its six legs with the body level, both pairs of wings spread out flat to the sides, stinger pointing straight back. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\needle_wasp\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Needle Wasp": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A slender, aggressive forest wasp - clearly a wasp, not an ant - fast, nervous and dangerous. Its armor is dark indigo-violet with sharp, faceted plates on the head and thorax; the abdomen is banded in indigo and warm amber-orange. The head is long and wedge-shaped with bright orange eyes, a row of small fangs and a pair of big, curved, sickle-like orange mandibles; two long, thin, segmented antennae sweep back over the head. A narrow wasp waist connects the thorax to a long, pointed, armored abdomen with small serrated plates, ending in a long, sharp crimson needle stinger - the key feature, always clearly visible. A small cluster of round orange venom sacs bulges on the side of the thorax. Two pairs of large, translucent amber wings with fine darker veins spread out to the sides, clearly apart from the body. Six thin, delicate, fairly short brown-orange legs with pointed tips are held slightly tucked under the body like a hovering wasp. Materials: glossy hard chitin, thin glassy wings, a wet-looking stinger tip.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on its six legs with the body level, both pairs of wings spread out flat to the sides, stinger pointing straight back.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 4. Broodling

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\broodling\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\broodling\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Broodling". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A small, unsettling forest spider that carries its own brood - a scuttling mother-creature bloated with eggs. The body is low and compact, with a reddish-brown, flesh-toned carapace made of overlapping, swollen plates. On its back sits a big, heaped cluster of round egg sacs, pale pink to creamy white, soft and slightly translucent-looking, with a single dark red spot on the largest egg. The head is small and tucked in at the front, with short fangs and a few small dark eyes. Eight jointed spider legs spread out around the body; they are dark reddish-brown with lighter, bony grey-white bands at the joints and dark pointed tips. Materials: glossy, slightly wet chitin on body and legs, soft fleshy membrane on the eggs. Palette: dark red-browns and raw flesh pink, with the pale egg cluster as the brightest shape.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, all eight legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, fangs closed, abdomen fully visible. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\broodling\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Broodling": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A small, unsettling forest spider that carries its own brood - a scuttling mother-creature bloated with eggs. The body is low and compact, with a reddish-brown, flesh-toned carapace made of overlapping, swollen plates. On its back sits a big, heaped cluster of round egg sacs, pale pink to creamy white, soft and slightly translucent-looking, with a single dark red spot on the largest egg. The head is small and tucked in at the front, with short fangs and a few small dark eyes. Eight jointed spider legs spread out around the body; they are dark reddish-brown with lighter, bony grey-white bands at the joints and dark pointed tips. Materials: glossy, slightly wet chitin on body and legs, soft fleshy membrane on the eggs. Palette: dark red-browns and raw flesh pink, with the pale egg cluster as the brightest shape.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body level, all eight legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, fangs closed, abdomen fully visible.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 5. Reef Snapper

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\reef_snapper\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\reef_snapper\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Reef Snapper". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A low, long coastal lizard predator built for ambush and snapping - all jaws and spines. The body is long and close to the ground like a crocodile or monitor lizard, with four sturdy legs set out to the sides and a long, thick tail that tapers to a point. The head is the eye-catcher: a long, bony, pale grey-white skull-like snout with a reddish tip and huge jaws lined with rows of sharp white teeth. Small red eyes sit high on the head behind the snout. A row of jagged, fin-like spines runs from the back of the head along the spine down the tail, dark at the base with rust-orange edges. The hide is dark red-brown, covered with rough scales speckled in rust-orange and ember tones, slightly lighter on the belly. The feet end in short dark claws. Materials: rough, wet scales on the body, smooth bone on the head.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\reef_snapper\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Reef Snapper": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A low, long coastal lizard predator built for ambush and snapping - all jaws and spines. The body is long and close to the ground like a crocodile or monitor lizard, with four sturdy legs set out to the sides and a long, thick tail that tapers to a point. The head is the eye-catcher: a long, bony, pale grey-white skull-like snout with a reddish tip and huge jaws lined with rows of sharp white teeth. Small red eyes sit high on the head behind the snout. A row of jagged, fin-like spines runs from the back of the head along the spine down the tail, dark at the base with rust-orange edges. The hide is dark red-brown, covered with rough scales speckled in rust-orange and ember tones, slightly lighter on the belly. The feet end in short dark claws. Materials: rough, wet scales on the body, smooth bone on the head.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 6. Shore Lurker

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shore_lurker\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shore_lurker\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Shore Lurker". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A hulking, low-slung coastal ambusher - heavy, brooding and patient, somewhere between a crocodile and a walrus-like brute. The body is broad and bulky with a deep chest and a powerful front, crouched close to the ground on four thick, muscular legs with wide clawed feet. The head is broad and flat with small amber eyes and a wide mouth; two long, curved, pale ivory tusks hang down from the lower jaw - its signature feature. A shaggy mane of long, quill-like spines grows from the back of the head along the neck and shoulders, pale bone-colored with rusty red tips. The hide is dark charcoal and slate-brown, mottled and wet-looking, with lighter bone-colored plates and ridges on the shoulders and legs. A short, thick tail trails behind. Materials: thick leathery hide, horn-like plates, smooth ivory tusks.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shore_lurker\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Shore Lurker": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A hulking, low-slung coastal ambusher - heavy, brooding and patient, somewhere between a crocodile and a walrus-like brute. The body is broad and bulky with a deep chest and a powerful front, crouched close to the ground on four thick, muscular legs with wide clawed feet. The head is broad and flat with small amber eyes and a wide mouth; two long, curved, pale ivory tusks hang down from the lower jaw - its signature feature. A shaggy mane of long, quill-like spines grows from the back of the head along the neck and shoulders, pale bone-colored with rusty red tips. The hide is dark charcoal and slate-brown, mottled and wet-looking, with lighter bone-colored plates and ridges on the shoulders and legs. A short, thick tail trails behind. Materials: thick leathery hide, horn-like plates, smooth ivory tusks.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 7. Shellback

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shellback\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shellback\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Shellback". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A heavy, armored coastal tortoise-beast - slow and stubborn, but with a snapping-turtle temper. Most of its body is covered by a big domed shell of rough, dark charcoal plates, edged with bands of bronze and tan, with a row of short, sharp spikes along the top ridge. The head is wide, flat and dark grey and pokes forward from under the shell, with several small orange eyes, two short horn spikes and a broad mouth full of jagged teeth. Four thick, stumpy legs, plated like the shell, end in large, heavy claws. The underside shows pale, ridged belly plates, and a short, stubby tail sticks out at the back. Materials: rough stony shell, leathery scaled skin, horn-like claws.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\shellback\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Shellback": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A heavy, armored coastal tortoise-beast - slow and stubborn, but with a snapping-turtle temper. Most of its body is covered by a big domed shell of rough, dark charcoal plates, edged with bands of bronze and tan, with a row of short, sharp spikes along the top ridge. The head is wide, flat and dark grey and pokes forward from under the shell, with several small orange eyes, two short horn spikes and a broad mouth full of jagged teeth. Four thick, stumpy legs, plated like the shell, end in large, heavy claws. The underside shows pale, ridged belly plates, and a short, stubby tail sticks out at the back. Materials: rough stony shell, leathery scaled skin, horn-like claws.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 8. Eel Stalker

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\eel_stalker\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\eel_stalker\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Eel Stalker". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A long, legless coastal eel-serpent - sinuous, slimy and predatory, always ready to strike. The body is long, smooth and muscular like a moray eel: thick behind the head and tapering into a thin tail, with a solid, heavy feel rather than a thin rope. Its skin is pale fleshy pink with darker red-brown bands and streaks along the back and flanks, lighter on the belly. The head is broad and dark grey, mottled with white, with round black eyes and a wide mouth full of long, thin fangs and a red throat. A crest of pale, bony spines with reddish tips runs over the head and down the neck like a frill. Ragged, soft skin flaps and barbels hang from under the jaw and throat. Materials: wet, glossy eel skin on the body, rougher armored skin on the head.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long on the ground with at most one gentle curve, not coiled, twisted or overlapping, head slightly raised and facing forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\eel_stalker\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Eel Stalker": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A long, legless coastal eel-serpent - sinuous, slimy and predatory, always ready to strike. The body is long, smooth and muscular like a moray eel: thick behind the head and tapering into a thin tail, with a solid, heavy feel rather than a thin rope. Its skin is pale fleshy pink with darker red-brown bands and streaks along the back and flanks, lighter on the belly. The head is broad and dark grey, mottled with white, with round black eyes and a wide mouth full of long, thin fangs and a red throat. A crest of pale, bony spines with reddish tips runs over the head and down the neck like a frill. Ragged, soft skin flaps and barbels hang from under the jaw and throat. Materials: wet, glossy eel skin on the body, rougher armored skin on the head.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body stretched out long on the ground with at most one gentle curve, not coiled, twisted or overlapping, head slightly raised and facing forward, mouth closed or only slightly open.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 9. Ravine Stalker

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\ravine_stalker\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\ravine_stalker\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Ravine Stalker". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A lean, gaunt wolf-like highland predator - hungry, fast and menacing. The body is narrow and wiry with a deep chest, a tucked-in waist, visible ribs and long, thin legs. The hide is charcoal black, marbled with pale silver-grey streaks like veins in dark stone. The head is long and narrow with tall pointed ears, sharp yellow eyes and a snarling mouth with long fangs and a dark red inside. A ragged crest of pale, bony spikes and torn fur runs along the neck and back. The tail is long and thin, almost whip-like. The paws are dark with short claws. Materials: short, coarse fur over a stony, plated skin.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\ravine_stalker\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Ravine Stalker": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A lean, gaunt wolf-like highland predator - hungry, fast and menacing. The body is narrow and wiry with a deep chest, a tucked-in waist, visible ribs and long, thin legs. The hide is charcoal black, marbled with pale silver-grey streaks like veins in dark stone. The head is long and narrow with tall pointed ears, sharp yellow eyes and a snarling mouth with long fangs and a dark red inside. A ragged crest of pale, bony spikes and torn fur runs along the neck and back. The tail is long and thin, almost whip-like. The paws are dark with short claws. Materials: short, coarse fur over a stony, plated skin.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 10. Stone Boar

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\stone_boar\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\stone_boar\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Stone Boar". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A massive, hump-backed boar armored like a boulder - stubborn, heavy and built to charge. The body is bulky and front-heavy, with a huge raised hump over the shoulders, thick muscular forelegs and shorter hind legs. Its hide is dark slate-grey to purple-black and looks like cracked rock, with raw rust-red flesh showing between the stone plates on the flanks and belly. A thicket of pale bone shards and spikes sticks out of the hump and back. The head is low and heavy, with a big round amber eye and large, upward-curving ivory tusks, plus smaller tusks and horns around the snout. The short legs end in hard dark hooves. Materials: rough stone plates, coarse leathery skin, smooth bone tusks.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\stone_boar\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Stone Boar": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A massive, hump-backed boar armored like a boulder - stubborn, heavy and built to charge. The body is bulky and front-heavy, with a huge raised hump over the shoulders, thick muscular forelegs and shorter hind legs. Its hide is dark slate-grey to purple-black and looks like cracked rock, with raw rust-red flesh showing between the stone plates on the flanks and belly. A thicket of pale bone shards and spikes sticks out of the hump and back. The head is low and heavy, with a big round amber eye and large, upward-curving ivory tusks, plus smaller tusks and horns around the snout. The short legs end in hard dark hooves. Materials: rough stone plates, coarse leathery skin, smooth bone tusks.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 11. Hollow Stag

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Hollow Stag". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A gaunt, haunted stag - eerie, silent and noble, like a deer that has been hollowed out. The body is tall and thin, with a long, slender neck, a narrow chest and long, thin legs ending in small dark hooves. Its hide is charcoal black with dark red, raw-looking streaks and patches on the neck, shoulders and flanks. The head is narrow and deer-like with small red eyes. Large, branching antlers rise high above the head, rust-brown to dark red with pale tips. A ragged tuft of pale grey, bone-like bristles and spines sticks up from the back above the shoulders and the hips. A short tail. Materials: thin, matte hide stretched over bones, hard antlers.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\hollow_stag\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Hollow Stag": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A gaunt, haunted stag - eerie, silent and noble, like a deer that has been hollowed out. The body is tall and thin, with a long, slender neck, a narrow chest and long, thin legs ending in small dark hooves. Its hide is charcoal black with dark red, raw-looking streaks and patches on the neck, shoulders and flanks. The head is narrow and deer-like with small red eyes. Large, branching antlers rise high above the head, rust-brown to dark red with pale tips. A ragged tuft of pale grey, bone-like bristles and spines sticks up from the back above the shoulders and the hips. A short tail. Materials: thin, matte hide stretched over bones, hard antlers.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 12. Rock Hyena

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\rock_hyena\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\rock_hyena\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Rock Hyena". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A hunched, hyena-like scavenger of the highlands - crooked, sly and aggressive. The silhouette is classic hyena: high, powerful shoulders and a back that slopes down clearly toward smaller hindquarters. The front legs are thick and strong, the hind legs shorter. The head is broad and dark grey, with a short, heavy muzzle, small red eyes, round ears and bared teeth. The body is mottled rust-orange and grey-brown, with patches of rough, rock-like skin as if it were partly turned to stone. A crest of short, stiff spikes and bristles runs along the neck and the top of the shoulders. A short, bushy tail. Materials: coarse, scruffy fur mixed with stony plates.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\rock_hyena\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Rock Hyena": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A hunched, hyena-like scavenger of the highlands - crooked, sly and aggressive. The silhouette is classic hyena: high, powerful shoulders and a back that slopes down clearly toward smaller hindquarters. The front legs are thick and strong, the hind legs shorter. The head is broad and dark grey, with a short, heavy muzzle, small red eyes, round ears and bared teeth. The body is mottled rust-orange and grey-brown, with patches of rough, rock-like skin as if it were partly turned to stone. A crest of short, stiff spikes and bristles runs along the neck and the top of the shoulders. A short, bushy tail. Materials: coarse, scruffy fur mixed with stony plates.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 13. Sand Leviathan

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sand_leviathan\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sand_leviathan\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Sand Leviathan". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A huge, legless desert worm - ancient, crushing and terrifying, bursting out of the dunes. The body is long and thick and made of ribbed, ring-shaped segments, sandy beige and ochre with darker brown bands between the rings, tapering toward the tail end. Toward the head the segments become darker and rougher, rust-red and brown, with ragged armor plates. The head is a long, crocodile-like maw packed with jagged teeth, framed by rows of hooked spines and tooth-like tendrils around the jaws and throat. Small dark eyes sit on top of the head. Materials: tough, dry, ribbed hide on the body, bony armor on the head.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long on the ground in one gentle curve, not coiled or twisted, only the front part with the head raised a little, facing forward. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\sand_leviathan\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Sand Leviathan": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A huge, legless desert worm - ancient, crushing and terrifying, bursting out of the dunes. The body is long and thick and made of ribbed, ring-shaped segments, sandy beige and ochre with darker brown bands between the rings, tapering toward the tail end. Toward the head the segments become darker and rougher, rust-red and brown, with ragged armor plates. The head is a long, crocodile-like maw packed with jagged teeth, framed by rows of hooked spines and tooth-like tendrils around the jaws and throat. Small dark eyes sit on top of the head. Materials: tough, dry, ribbed hide on the body, bony armor on the head.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body stretched out long on the ground in one gentle curve, not coiled or twisted, only the front part with the head raised a little, facing forward.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 14. Dune Raptor

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\dune_raptor\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\dune_raptor\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Dune Raptor". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A fast, two-legged desert raptor - a lean, agile pack hunter that moves like a running bird. The body leans forward and is balanced by a long, stiff tail; it has NO wings and no arms. The two legs are long, slender and bird-like, with backward-bending ankles and three sharp claws on each foot. The head is long and narrow, with a toothy jaw and bright amber eyes. A short frill of dark, swept-back spines runs from the back of the head down the neck and along the back. The scaly hide is sandy ochre and khaki with darker brown mottling along the back, lighter on the belly, and the tail ends in a few small spikes. Materials: dry, fine scales and hard dark claws.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body leaning forward and level, both legs straight under the hips and slightly apart, tail extended straight back in line with the body (never hanging down between the legs), head forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\dune_raptor\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Dune Raptor": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A fast, two-legged desert raptor - a lean, agile pack hunter that moves like a running bird. The body leans forward and is balanced by a long, stiff tail; it has NO wings and no arms. The two legs are long, slender and bird-like, with backward-bending ankles and three sharp claws on each foot. The head is long and narrow, with a toothy jaw and bright amber eyes. A short frill of dark, swept-back spines runs from the back of the head down the neck and along the back. The scaly hide is sandy ochre and khaki with darker brown mottling along the back, lighter on the belly, and the tail ends in a few small spikes. Materials: dry, fine scales and hard dark claws.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body leaning forward and level, both legs straight under the hips and slightly apart, tail extended straight back in line with the body (never hanging down between the legs), head forward, mouth closed or only slightly open.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 15. Glassback Colossus

Artist B · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\glassback_colossus\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\glassback_colossus\input\concept\design_B.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Glassback Colossus". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A massive desert colossus - a hulking, ape-like brute armored in rock and crystal, slow but overwhelming. It stands on all fours on huge, long front arms and shorter, thick hind legs, with a broad, hunched upper body; it has no tail. The back, the shoulders and the forearms are covered with big, angular plates of glassy crystal in muted teal, jade and slate-green, like shards of dark glass growing out of the body. The chest and belly are bare, sandy-brown and ridged like cracked stone. The head sits low between the shoulders, framed by a spiky crystal crest, with small red eyes and a wide red mouth. The hands and feet are blocky and heavy, with dark knuckles. Materials: rough sandstone skin, smooth glassy crystal plates.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\glassback_colossus\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Glassback Colossus": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A massive desert colossus - a hulking, ape-like brute armored in rock and crystal, slow but overwhelming. It stands on all fours on huge, long front arms and shorter, thick hind legs, with a broad, hunched upper body; it has no tail. The back, the shoulders and the forearms are covered with big, angular plates of glassy crystal in muted teal, jade and slate-green, like shards of dark glass growing out of the body. The chest and belly are bare, sandy-brown and ridged like cracked stone. The head sits low between the shoulders, framed by a spiky crystal crest, with small red eyes and a wide red mouth. The hands and feet are blocky and heavy, with dark knuckles. Materials: rough sandstone skin, smooth glassy crystal plates.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 16. Scorpion Matriarch

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\scorpion_matriarch\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\scorpion_matriarch\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Scorpion Matriarch". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A giant desert scorpion queen - huge, imperious and venomous. The body is low and wide, with a heavily armored, segmented back. Its chitin is glossy black-red with molten orange and ember-red highlights along the plate edges, like cooling lava. Two large, powerful pincers are held forward in front of the head. Exactly eight long, spiky, stilt-like walking legs carry the body, four on each side, with orange-red bands at the joints. A long, segmented tail rises from the rear and arches high over the back, ending in a big, curved, bright orange stinger. Materials: hard, polished chitin plates with sharp edges.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, the eight walking legs spread evenly to both sides with the tips on the ground, both pincers held forward and apart, tail arched up over the back without touching it. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\scorpion_matriarch\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Scorpion Matriarch": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A giant desert scorpion queen - huge, imperious and venomous. The body is low and wide, with a heavily armored, segmented back. Its chitin is glossy black-red with molten orange and ember-red highlights along the plate edges, like cooling lava. Two large, powerful pincers are held forward in front of the head. Exactly eight long, spiky, stilt-like walking legs carry the body, four on each side, with orange-red bands at the joints. A long, segmented tail rises from the rear and arches high over the back, ending in a big, curved, bright orange stinger. Materials: hard, polished chitin plates with sharp edges.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body level, the eight walking legs spread evenly to both sides with the tips on the ground, both pincers held forward and apart, tail arched up over the back without touching it.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 17. Frost Colossus

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\frost_colossus\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\frost_colossus\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Frost Colossus". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A huge gorilla-like ice beast - brutal, heavy and ancient, a walking glacier. It stands on all fours on its knuckles, with massive, long front arms, a broad chest and shoulders, and shorter, thick hind legs; like a gorilla it has no tail. Its body is dark steel-blue under thick armor of pale blue-white ice and frost plates on the shoulders, arms, back and legs. Jagged ice spikes and frozen crystal shards jut out of the shoulders, the back and the top of the head. The head is low and heavy, with a gaping, fanged mouth and small pale eyes deep under a frosty brow. Its fists and feet are huge and crusted with ice. Materials: rough frozen hide, cold translucent ice crystals, patches of frosted fur.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\frost_colossus\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Frost Colossus": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A huge gorilla-like ice beast - brutal, heavy and ancient, a walking glacier. It stands on all fours on its knuckles, with massive, long front arms, a broad chest and shoulders, and shorter, thick hind legs; like a gorilla it has no tail. Its body is dark steel-blue under thick armor of pale blue-white ice and frost plates on the shoulders, arms, back and legs. Jagged ice spikes and frozen crystal shards jut out of the shoulders, the back and the top of the head. The head is low and heavy, with a gaping, fanged mouth and small pale eyes deep under a frosty brow. Its fists and feet are huge and crusted with ice. Materials: rough frozen hide, cold translucent ice crystals, patches of frosted fur.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 18. Flesh Titan

Artist B · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\flesh_titan\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\flesh_titan\input\concept\design_B.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Flesh Titan". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A hulking, two-legged abyssal flesh brute with a partly humanoid upper body - grotesque, enormous and unstoppable. Its body is raw red muscle without skin, with clearly sculpted chest, belly and arm muscles. Pale grey-white bone plates cover the shoulders, the forearms and the lower legs like natural armor. The head sits low between the shoulders under a bony, helmet-like grey hood with short horns, showing a wide, grinning mouth full of teeth. The arms are long and heavy and end in huge hands with long, curved, bone-white claws. It stands upright on two thick, armored legs. Materials: wet, glossy muscle tissue and hard, chalky bone.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: A-pose: standing straight, legs straight and slightly apart, arms angled down and away from the body, head forward. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\flesh_titan\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Flesh Titan": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A hulking, two-legged abyssal flesh brute with a partly humanoid upper body - grotesque, enormous and unstoppable. Its body is raw red muscle without skin, with clearly sculpted chest, belly and arm muscles. Pale grey-white bone plates cover the shoulders, the forearms and the lower legs like natural armor. The head sits low between the shoulders under a bony, helmet-like grey hood with short horns, showing a wide, grinning mouth full of teeth. The arms are long and heavy and end in huge hands with long, curved, bone-white claws. It stands upright on two thick, armored legs. Materials: wet, glossy muscle tissue and hard, chalky bone.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: A-pose: standing straight, legs straight and slightly apart, arms angled down and away from the body, head forward.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 19. Void Manifestation

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\void_manifestation\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\void_manifestation\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Void Manifestation". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A floating horror from the void - an alien, silent watcher that hovers above the ground. The core is a round body built around one huge eye: a dark, glossy black sphere framed by a vivid violet ring. Around the eye the body is dark purple-black, with short spiky appendages and small hooks forming a crown. Many long, squid-like tentacles grow from the underside and the sides; they are dark violet, thick and soft at the root and taper to thin tips, with lighter purple undersides. From above it reads as a dark eye-orb inside a wide ring of writhing tentacles. Materials: smooth, wet, rubbery skin and a glassy eye.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: floating level in the air, the eye facing forward, all tentacles hanging down and slightly spread, each one separate and only gently curved, not curled up or tangled. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\void_manifestation\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Void Manifestation": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A floating horror from the void - an alien, silent watcher that hovers above the ground. The core is a round body built around one huge eye: a dark, glossy black sphere framed by a vivid violet ring. Around the eye the body is dark purple-black, with short spiky appendages and small hooks forming a crown. Many long, squid-like tentacles grow from the underside and the sides; they are dark violet, thick and soft at the root and taper to thin tips, with lighter purple undersides. From above it reads as a dark eye-orb inside a wide ring of writhing tentacles. Materials: smooth, wet, rubbery skin and a glassy eye.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: floating level in the air, the eye facing forward, all tentacles hanging down and slightly spread, each one separate and only gently curved, not curled up or tangled.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 20. Void Harbinger

Artist B · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\void_harbinger\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\void_harbinger\input\concept\design_B.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Void Harbinger". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A tall, partly humanoid void creature - a dark herald, spindly and unnatural. Instead of a head it has a large, dark, glossy orb framed by a vivid violet ring, sitting on top of a thin, black, spiky torso. Two long, thin arms with clawed fingers reach out from the shoulders. It stands upright on two long, thin, jointed legs. Behind its shoulders spread two large, tattered, bat-like wings with dark violet membranes, clearly separated from the body and the arms. The body is black with deep violet highlights and sharp thorn-like spikes on the shoulders, elbows and knees. Materials: hard, matte black chitin, thin leathery wing membranes and a glassy orb.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing upright on its two legs, legs straight and slightly apart, arms angled down and away from the body, both wings spread out symmetrically to the sides, free from the body and the arms. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\void_harbinger\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Void Harbinger": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A tall, partly humanoid void creature - a dark herald, spindly and unnatural. Instead of a head it has a large, dark, glossy orb framed by a vivid violet ring, sitting on top of a thin, black, spiky torso. Two long, thin arms with clawed fingers reach out from the shoulders. It stands upright on two long, thin, jointed legs. Behind its shoulders spread two large, tattered, bat-like wings with dark violet membranes, clearly separated from the body and the arms. The body is black with deep violet highlights and sharp thorn-like spikes on the shoulders, elbows and knees. Materials: hard, matte black chitin, thin leathery wing membranes and a glassy orb.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing upright on its two legs, legs straight and slightly apart, arms angled down and away from the body, both wings spread out symmetrically to the sides, free from the body and the arms.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 21. Reality Ripper

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\reality_ripper\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\reality_ripper\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Reality Ripper". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A mantis-like abyssal predator - a nightmare hunter that slices through reality. It walks on four long, jointed, spidery legs, and its two front limbs are huge raptorial blade arms with long, curved, scythe-like blades that rise and arch over its body. The blades are pale silver-grey with dark edges; the rest of the body is black-violet chitin with deep red highlights along the joints and plate edges. The head is small and pale, sitting at the front, with a single large orange-red eye and a jagged mouth. A few thin, whip-like feelers sweep back from the head. Materials: polished, sharp-edged chitin and metallic-looking blades.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, standing on its four walking legs spread evenly to both sides, the two blade arms raised and folded in front of the body, free from the legs and the head. All limbs clearly visible and apart from each other. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\reality_ripper\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Reality Ripper": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A mantis-like abyssal predator - a nightmare hunter that slices through reality. It walks on four long, jointed, spidery legs, and its two front limbs are huge raptorial blade arms with long, curved, scythe-like blades that rise and arch over its body. The blades are pale silver-grey with dark edges; the rest of the body is black-violet chitin with deep red highlights along the joints and plate edges. The head is small and pale, sitting at the front, with a single large orange-red eye and a jagged mouth. A few thin, whip-like feelers sweep back from the head. Materials: polished, sharp-edged chitin and metallic-looking blades.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body level, standing on its four walking legs spread evenly to both sides, the two blade arms raised and folded in front of the body, free from the legs and the head.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```
