# Alle ChatGPT-Prompts – zwei Stufen pro Kreatur

Seit 2026-11-18 (BACKLOG A10). Pro Kreatur:

1. **Stufe 1 – Design-Bild:** neuer ChatGPT-Chat → die genannten Bilder anhängen (Concept-Ausschnitt + Stil-Referenz) → Prompt 1 einfügen → **ein** Bild. **Du prüfst es gegen dein Concept** (Charakter, Körperbau, Anzahl Beine/Teile, Farben). Passt es nicht: neu generieren lassen oder `look` in `creatures/roster.toml` anpassen und `python scripts/make_roster.py` neu starten. Passt es: als `input/design.png` speichern.
2. **Stufe 2 – 4 Ansichten:** neuer ChatGPT-Chat → nur `input/design.png` anhängen → Prompt 2 einfügen → 4 Einzelbilder als `front.png`, `left.png`, `right.png`, `back.png` in denselben `input`-Ordner speichern.
3. **Claude prüft** die 4 Ansichten nach der Checkliste (`README.md`, Teil A), erst dann Tripo.

Kreaturen mit fertigem Tripo-Modell (markiert) brauchen das nur bei einem Neubau – ihre Bilder bleiben, wie sie sind.
**Ohne Concept** (markiert, Roster-Erweiterung 2026-11-18): Stufe 1 bekommt nur die Stil-Referenz und entwirft die Kreatur aus der Beschreibung – **das Design-Bild ist der Design-Entwurf**, du prüfst es (gefällt es dir?) und lässt es ggf. neu generieren.
Übersicht aller Concept-Ausschnitte: `creatures/concept_crops.png`.

| # | Kreatur | Tripo-Modell | design.png |
|---|---|---|---|
| 2 | [Spore Drone](#2-spore-drone) | – | – |
| 3 | [Needle Wasp](#3-needle-wasp) | ✅ vorhanden | – |
| 4 | [Broodling](#4-broodling) | ✅ vorhanden | – |
| 5 | [Reef Snapper](#5-reef-snapper) | ✅ vorhanden | – |
| 6 | [Shore Lurker](#6-shore-lurker) | – | – |
| 7 | [Shellback](#7-shellback) | ✅ vorhanden | – |
| 8 | [Eel Stalker](#8-eel-stalker) | ✅ vorhanden | – |
| 9 | [Ravine Stalker](#9-ravine-stalker) | ✅ vorhanden | – |
| 10 | [Stone Boar](#10-stone-boar) | – | – |
| 11 | [Hollow Stag](#11-hollow-stag) | ✅ vorhanden | – |
| 12 | [Rock Hyena](#12-rock-hyena) | – | – |
| 13 | [Sand Leviathan](#13-sand-leviathan) | ✅ vorhanden | – |
| 14 | [Dune Raptor](#14-dune-raptor) | ✅ vorhanden | – |
| 15 | [Glassback Colossus](#15-glassback-colossus) | – | – |
| 16 | [Scorpion Matriarch](#16-scorpion-matriarch) | ✅ vorhanden | – |
| 17 | [Frost Colossus](#17-frost-colossus) | ✅ vorhanden | – |
| 18 | [Flesh Titan](#18-flesh-titan) | – | – |
| 19 | [Void Manifestation](#19-void-manifestation) | ✅ vorhanden | – |
| 20 | [Void Harbinger](#20-void-harbinger) | – | – |
| 21 | [Reality Ripper](#21-reality-ripper) | ✅ vorhanden | ✅ |
| 22 | [Geode Golem](#22-geode-golem) | – | – |
| 23 | [Tomb Shroud](#23-tomb-shroud) | – | – |
| 24 | [Idol Eye](#24-idol-eye) | – | – |
| 25 | [Bonepicker Vulture](#25-bonepicker-vulture) | ✅ vorhanden | ✅ |
| 26 | [Cinder Wyvern](#26-cinder-wyvern) | ✅ vorhanden | ✅ |
| 27 | [Umbral Panther](#27-umbral-panther) | – | – |
| 28 | [Rimehide Bear](#28-rimehide-bear) | – | – |
| 29 | [Sporecap Mortar](#29-sporecap-mortar) | – | – |
| 30 | [Bog Ooze](#30-bog-ooze) | – | – |
| 31 | [Oasis Gulper](#31-oasis-gulper) | ✅ vorhanden | ✅ |
| 32 | [Quillback Burrower](#32-quillback-burrower) | – | – |
| 33 | [Ruin Howler](#33-ruin-howler) | ✅ vorhanden | ✅ |
| 34 | [Tallgrass Viper](#34-tallgrass-viper) | – | – |
| 35 | [Mound Queen](#35-mound-queen) | – | – |
| 36 | [Bog Warden](#36-bog-warden) | ✅ vorhanden | ✅ |
| 37 | [Gloomfang Centipede](#37-gloomfang-centipede) | ✅ vorhanden | ✅ |

## 2. Spore Drone

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\21_spore_drone\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\21_spore_drone\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Spore Drone". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A creepy forest beetle that carries a huge fungal growth on its back - slow, heavy-laden, like a walking mushroom colony. The body is a compact, rounded beetle with a glossy dark red-brown carapace marked with a few thin pale stripes. The head is small and low at the front, with short mandibles and two thin, curled orange antennae. On top of the back sits a big, lumpy cluster of round spore pods like a heap of puffball mushrooms, pale bone-white to creamy beige - it dominates the silhouette, especially from above. Six long, thin, spindly jointed legs lift the body high above the ground; they are olive-green near the body and fade to reddish-orange toward the pointed tips. Patches of mossy green fungal fuzz grow around the neck, the leg joints and the edges of the shell. Materials: hard lacquered chitin on body and legs, soft matte spongy surface on the spore pods. Palette: dark earthy red-brown, olive and moss green, with the pale spore cluster as the bright eye-catcher.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, all six legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, antennae forward and apart, mandibles closed. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\21_spore_drone\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 3. Needle Wasp

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\07_needle_wasp\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\07_needle_wasp\input\concept\neelde_wasp.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\07_needle_wasp\input\concept\style_B_stalk_wasp.png`

```text
Image 1 is my concept art of this creature: take its design, silhouette and colors; the description below adds the details. Image 1 is a concept sheet of this wasp: the big creature is the design, the small panels show details (head, stinger, wings, eggs) and views. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Needle Wasp". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A slender, aggressive forest wasp - clearly a wasp, not an ant - fast, nervous and dangerous. Its armor is dark indigo-violet with sharp, faceted plates on the head and thorax; the abdomen is banded in indigo and warm amber-orange. The head is long and wedge-shaped with bright orange eyes, a row of small fangs and a pair of big, curved, sickle-like orange mandibles; two long, thin, segmented antennae sweep back over the head. A narrow wasp waist connects the thorax to a long, pointed, armored abdomen with small serrated plates, ending in a long, sharp crimson needle stinger - the key feature, always clearly visible. A small cluster of round orange venom sacs bulges on the side of the thorax. Two pairs of large, translucent amber wings with fine darker veins spread out to the sides, clearly apart from the body. Six thin, delicate, fairly short brown-orange legs with pointed tips are held slightly tucked under the body like a hovering wasp. Materials: glossy hard chitin, thin glassy wings, a wet-looking stinger tip.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on its six legs with the body level, both pairs of wings spread out flat to the sides, stinger pointing straight back. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\07_needle_wasp\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 4. Broodling

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\10_broodling\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\10_broodling\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Broodling". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A small, unsettling forest spider that carries its own brood - a scuttling mother-creature bloated with eggs. The body is low and compact, with a reddish-brown, flesh-toned carapace made of overlapping, swollen plates. On its back sits a big, heaped cluster of round egg sacs, pale pink to creamy white, soft and slightly translucent-looking, with a single dark red spot on the largest egg. The head is small and tucked in at the front, with short fangs and a few small dark eyes. Eight jointed spider legs spread out around the body; they are dark reddish-brown with lighter, bony grey-white bands at the joints and dark pointed tips. Materials: glossy, slightly wet chitin on body and legs, soft fleshy membrane on the eggs. Palette: dark red-browns and raw flesh pink, with the pale egg cluster as the brightest shape.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, all eight legs spread evenly and symmetrically to both sides, none crossing, leg tips on the ground, fangs closed, abdomen fully visible. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\10_broodling\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 5. Reef Snapper

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\08_reef_snapper\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\08_reef_snapper\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Reef Snapper". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A low, long coastal lizard predator built for ambush and snapping - all jaws and spines. The body is long and close to the ground like a crocodile or monitor lizard, with four sturdy legs set out to the sides and a long, thick tail that tapers to a point. The head is the eye-catcher: a long, bony, pale grey-white skull-like snout with a reddish tip and huge jaws lined with rows of sharp white teeth. Small red eyes sit high on the head behind the snout. A row of jagged, fin-like spines runs from the back of the head along the spine down the tail, dark at the base with rust-orange edges. The hide is dark red-brown, covered with rough scales speckled in rust-orange and ember tones, slightly lighter on the belly. The feet end in short dark claws. Materials: rough, wet scales on the body, smooth bone on the head.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\08_reef_snapper\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 6. Shore Lurker

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\22_shore_lurker\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\22_shore_lurker\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Shore Lurker". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A hulking, low-slung coastal ambusher - heavy, brooding and patient, somewhere between a crocodile and a walrus-like brute. The body is broad and bulky with a deep chest and a powerful front, crouched close to the ground on four thick, muscular legs with wide clawed feet. The head is broad and flat with small amber eyes and a wide mouth; two long, curved, pale ivory tusks hang down from the lower jaw - its signature feature. A shaggy mane of long, quill-like spines grows from the back of the head along the neck and shoulders, pale bone-colored with rusty red tips. The hide is dark charcoal and slate-brown, mottled and wet-looking, with lighter bone-colored plates and ridges on the shoulders and legs. A short, thick tail trails behind. Materials: thick leathery hide, horn-like plates, smooth ivory tusks.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\22_shore_lurker\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 7. Shellback

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\11_shellback\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\11_shellback\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Shellback". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A heavy, armored coastal tortoise-beast - slow and stubborn, but with a snapping-turtle temper. Most of its body is covered by a big domed shell of rough, dark charcoal plates, edged with bands of bronze and tan, with a row of short, sharp spikes along the top ridge. The head is wide, flat and dark grey and pokes forward from under the shell, with several small orange eyes, two short horn spikes and a broad mouth full of jagged teeth. Four thick, stumpy legs, plated like the shell, end in large, heavy claws. The underside shows pale, ridged belly plates, and a short, stubby tail sticks out at the back. Materials: rough stony shell, leathery scaled skin, horn-like claws.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\11_shellback\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 8. Eel Stalker

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\03_eel_stalker\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\03_eel_stalker\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Eel Stalker". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A long, legless coastal eel-serpent - sinuous, slimy and predatory, always ready to strike. The body is long, smooth and muscular like a moray eel: thick behind the head and tapering into a thin tail, with a solid, heavy feel rather than a thin rope. Its skin is pale fleshy pink with darker red-brown bands and streaks along the back and flanks, lighter on the belly. The head is broad and dark grey, mottled with white, with round black eyes and a wide mouth full of long, thin fangs and a red throat. A crest of pale, bony spines with reddish tips runs over the head and down the neck like a frill. Ragged, soft skin flaps and barbels hang from under the jaw and throat. Materials: wet, glossy eel skin on the body, rougher armored skin on the head.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long on the ground with at most one gentle curve, not coiled, twisted or overlapping, head slightly raised and facing forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\03_eel_stalker\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 9. Ravine Stalker

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\02_ravine_stalker\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\02_ravine_stalker\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Ravine Stalker". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A lean, gaunt wolf-like highland predator - hungry, fast and menacing. The body is narrow and wiry with a deep chest, a tucked-in waist, visible ribs and long, thin legs. The hide is charcoal black, marbled with pale silver-grey streaks like veins in dark stone. The head is long and narrow with tall pointed ears, sharp yellow eyes and a snarling mouth with long fangs and a dark red inside. A ragged crest of pale, bony spikes and torn fur runs along the neck and back. The tail is long and thin, almost whip-like. The paws are dark with short claws. Materials: short, coarse fur over a stony, plated skin.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\02_ravine_stalker\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 10. Stone Boar

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\23_stone_boar\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\23_stone_boar\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Stone Boar". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A massive, hump-backed boar armored like a boulder - stubborn, heavy and built to charge. The body is bulky and front-heavy, with a huge raised hump over the shoulders, thick muscular forelegs and shorter hind legs. Its hide is dark slate-grey to purple-black and looks like cracked rock, with raw rust-red flesh showing between the stone plates on the flanks and belly. A thicket of pale bone shards and spikes sticks out of the hump and back. The head is low and heavy, with a big round amber eye and large, upward-curving ivory tusks, plus smaller tusks and horns around the snout. The short legs end in hard dark hooves. Materials: rough stone plates, coarse leathery skin, smooth bone tusks.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\23_stone_boar\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 11. Hollow Stag

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\09_hollow_stag\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\09_hollow_stag\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Hollow Stag". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A gaunt, haunted stag - eerie, silent and noble, like a deer that has been hollowed out. The body is tall and thin, with a long, slender neck, a narrow chest and long, thin legs ending in small dark hooves. Its hide is charcoal black with dark red, raw-looking streaks and patches on the neck, shoulders and flanks. The head is narrow and deer-like with small red eyes. Large, branching antlers rise high above the head, rust-brown to dark red with pale tips. A ragged tuft of pale grey, bone-like bristles and spines sticks up from the back above the shoulders and the hips. A short tail. Materials: thin, matte hide stretched over bones, hard antlers.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing calmly on all four long legs, every leg straight and vertical directly under the body like pillars, front and hind legs equally close together with the hooves about hip-width apart and parallel, hind legs not splayed or bowed outward, head held high facing forward, mouth closed, tail hanging short behind (never between the legs), the antlers rising freely above the head without touching the back or the neck. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\09_hollow_stag\input\design.png`

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

## 12. Rock Hyena

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\24_rock_hyena\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\24_rock_hyena\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Rock Hyena". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A hunched, hyena-like scavenger of the highlands - crooked, sly and aggressive. The silhouette is classic hyena: high, powerful shoulders and a back that slopes down clearly toward smaller hindquarters. The front legs are thick and strong, the hind legs shorter. The head is broad and dark grey, with a short, heavy muzzle, small red eyes, round ears and bared teeth. The body is mottled rust-orange and grey-brown, with patches of rough, rock-like skin as if it were partly turned to stone. A crest of short, stiff spikes and bristles runs along the neck and the top of the shoulders. A short, bushy tail. Materials: coarse, scruffy fur mixed with stony plates.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\24_rock_hyena\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 13. Sand Leviathan

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\12_sand_leviathan\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\12_sand_leviathan\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Sand Leviathan". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A huge, legless desert worm - ancient, crushing and terrifying, bursting out of the dunes. The body is long and thick and made of ribbed, ring-shaped segments, sandy beige and ochre with darker brown bands between the rings, tapering toward the tail end. Toward the head the segments become darker and rougher, rust-red and brown, with ragged armor plates. The head ends in a wide, round maw like a lamprey's: rings of long, inward-curving fangs around a dark red throat, framed by a ruff of hooked spines and tooth-like tendrils. The armored head behind the maw carries small dark eyes. Materials: tough, dry, ribbed hide on the body, bony armor on the head.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long on the ground in one gentle curve, not coiled or twisted, only the front part with the head raised a little, facing forward. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\12_sand_leviathan\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Sand Leviathan": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A huge, legless desert worm - ancient, crushing and terrifying, bursting out of the dunes. The body is long and thick and made of ribbed, ring-shaped segments, sandy beige and ochre with darker brown bands between the rings, tapering toward the tail end. Toward the head the segments become darker and rougher, rust-red and brown, with ragged armor plates. The head ends in a wide, round maw like a lamprey's: rings of long, inward-curving fangs around a dark red throat, framed by a ruff of hooked spines and tooth-like tendrils. The armored head behind the maw carries small dark eyes. Materials: tough, dry, ribbed hide on the body, bony armor on the head.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body stretched out long on the ground in one gentle curve, not coiled or twisted, only the front part with the head raised a little, facing forward.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 14. Dune Raptor

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\04_dune_raptor\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\04_dune_raptor\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Dune Raptor". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A fast, two-legged desert raptor - a lean, agile pack hunter that moves like a running bird. The body leans forward and is balanced by a long, stiff tail; it has NO wings and no arms. The two legs are long, slender and bird-like, with backward-bending ankles and three sharp claws on each foot. The head is long and narrow, with a toothy jaw and bright amber eyes. A short frill of dark, swept-back spines runs from the back of the head down the neck and along the back. The scaly hide is sandy ochre and khaki with darker brown mottling along the back, lighter on the belly, and the tail ends in a few small spikes. Materials: dry, fine scales and hard dark claws.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body leaning forward and level, both legs straight under the hips and slightly apart, tail extended straight back in line with the body (never hanging down between the legs), head forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\04_dune_raptor\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 15. Glassback Colossus

Artist B · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\25_glassback_colossus\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\25_glassback_colossus\input\concept\design_B.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Glassback Colossus". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A massive desert colossus - a hulking, ape-like brute armored in rock and crystal, slow but overwhelming. It stands on all fours on huge, long front arms and shorter, thick hind legs, with a broad, hunched upper body; it has no tail. The back, the shoulders and the forearms are covered with big, angular plates of glassy crystal in muted teal, jade and slate-green, like shards of dark glass growing out of the body. The chest and belly are bare, sandy-brown and ridged like cracked stone. The head sits low between the shoulders, framed by a spiky crystal crest, with small red eyes and a wide red mouth. The hands and feet are blocky and heavy, with dark knuckles. Materials: rough sandstone skin, smooth glassy crystal plates.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\25_glassback_colossus\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 16. Scorpion Matriarch

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\06_scorpion_matriarch\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\06_scorpion_matriarch\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Scorpion Matriarch". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A giant desert scorpion queen - huge, imperious and venomous. The body is low and wide, with a heavily armored, segmented back. Its chitin is glossy black-red with molten orange and ember-red highlights along the plate edges, like cooling lava. Two large, powerful pincers are held forward in front of the head. Exactly eight long, spiky, stilt-like walking legs carry the body, four on each side, with orange-red bands at the joints. A long, segmented tail rises from the rear and arches high over the back, ending in a big, curved, bright orange stinger. Materials: hard, polished chitin plates with sharp edges.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, the eight walking legs spread evenly to both sides with the tips on the ground, both pincers held forward and apart, tail arched up over the back without touching it. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\06_scorpion_matriarch\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 17. Frost Colossus

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\13_frost_colossus\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\13_frost_colossus\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Frost Colossus". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A huge gorilla-like ice beast - brutal, heavy and ancient, a walking glacier. It stands on all fours on its knuckles, with massive, long front arms, a broad chest and shoulders, and shorter, thick hind legs; like a gorilla it has no tail. Its body is dark steel-blue under thick armor of pale blue-white ice and frost plates on the shoulders, arms, back and legs. Jagged ice spikes and frozen crystal shards jut out of the shoulders, the back and the top of the head. The head is low and heavy, with a gaping, fanged mouth and small pale eyes deep under a frosty brow. Its fists and feet are huge and crusted with ice. Materials: rough frozen hide, cold translucent ice crystals, patches of frosted fur.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\13_frost_colossus\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 18. Flesh Titan

Artist B · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\26_flesh_titan\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\26_flesh_titan\input\concept\design_B.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Flesh Titan". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A hulking, two-legged abyssal flesh brute with a partly humanoid upper body - grotesque, enormous and unstoppable. Its body is raw red muscle without skin, with clearly sculpted chest, belly and arm muscles. Pale grey-white bone plates cover the shoulders, the forearms and the lower legs like natural armor. The head sits low between the shoulders under a bony, helmet-like grey hood with short horns, showing a wide, grinning mouth full of teeth. The arms are long and heavy and end in huge hands with long, curved, bone-white claws. It stands upright on two thick, armored legs. Materials: wet, glossy muscle tissue and hard, chalky bone.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: A-pose: standing straight, legs straight and slightly apart, arms angled down and away from the body, head forward. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\26_flesh_titan\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 19. Void Manifestation

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\05_void_manifestation\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\05_void_manifestation\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Void Manifestation". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A floating horror from the void - an alien, silent watcher that hovers above the ground. The core is a round body built around one huge eye: a dark, glossy black sphere framed by a vivid violet ring. Around the eye the body is dark purple-black, with short spiky appendages and small hooks forming a crown. Many long, squid-like tentacles grow from the underside and the sides; they are dark violet, thick and soft at the root and taper to thin tips, with lighter purple undersides. From above it reads as a dark eye-orb inside a wide ring of writhing tentacles. Materials: smooth, wet, rubbery skin and a glassy eye.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: floating level in the air, the eye facing forward, all tentacles hanging down and slightly spread, each one separate and only gently curved, not curled up or tangled. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\05_void_manifestation\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 20. Void Harbinger

Artist B · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\27_void_harbinger\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\27_void_harbinger\input\concept\design_B.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Void Harbinger". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A tall, partly humanoid void creature - a dark herald, spindly and unnatural. Instead of a head it has a large, dark, glossy orb framed by a vivid violet ring, sitting on top of a thin, black, spiky torso. Two long, thin arms with clawed fingers reach out from the shoulders. It stands upright on two long, thin, jointed legs. Behind its shoulders spread two large, tattered, bat-like wings with dark violet membranes, clearly separated from the body and the arms. The body is black with deep violet highlights and sharp thorn-like spikes on the shoulders, elbows and knees. Materials: hard, matte black chitin, thin leathery wing membranes and a glassy orb.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing upright on its two legs, legs straight and slightly apart, arms angled down and away from the body, both wings spread out symmetrically to the sides, free from the body and the arms. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\27_void_harbinger\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 21. Reality Ripper

Artist A · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\20_reality_ripper\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\20_reality_ripper\input\concept\design_A.png`  2. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is my concept art of this creature - a small, blurry crop: take the overall design, silhouette and colors from it, the details from the description; do not copy its blur. Recreate only the large creature in front; ignore the grey silhouettes, any text and the background of the concept. Image 2 is only an art-style reference: copy its rendering style, not the creatures in it.

Paint ONE clean, sharp, high-resolution design image of my creature "Reality Ripper". Stay true to the concept - same character, silhouette, body parts and colors - but redraw it cleanly with these details:

A mantis-like abyssal predator - a nightmare hunter that slices through reality. It walks on four long, jointed, spidery legs, and its two front limbs are huge raptorial blade arms with long, curved, scythe-like blades that rise and arch over its body. The blades are pale silver-grey with dark edges; the rest of the body is black-violet chitin with deep red highlights along the joints and plate edges. The head is small and pale, sitting at the front, with a single large orange-red eye and a jagged mouth. A few thin, whip-like feelers sweep back from the head. Materials: polished, sharp-edged chitin and metallic-looking blades.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, standing on its four walking legs spread evenly to both sides, the two blade arms raised and held forward at their full length, free from the legs and the head. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\20_reality_ripper\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Reality Ripper": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A mantis-like abyssal predator - a nightmare hunter that slices through reality. It walks on four long, jointed, spidery legs, and its two front limbs are huge raptorial blade arms with long, curved, scythe-like blades that rise and arch over its body. The blades are pale silver-grey with dark edges; the rest of the body is black-violet chitin with deep red highlights along the joints and plate edges. The head is small and pale, sitting at the front, with a single large orange-red eye and a jagged mouth. A few thin, whip-like feelers sweep back from the head. Materials: polished, sharp-edged chitin and metallic-looking blades.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body level, standing on its four walking legs spread evenly to both sides, the two blade arms raised and held forward at their full length, free from the legs and the head.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 22. Geode Golem

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Kristall, Rolle Nahkampf (Tank) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\28_geode_golem\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Geode Golem" - an original design with a bold silhouette that reads well from a top-down game camera:

A massive, slow golem of split rock, hollow like a geode - ancient, heavy and unstoppable. Its body is a hunched block of dark slate-grey stone with a broad, top-heavy chest and shoulders, a narrow waist and two short, thick, pillar-like legs. The head is small and sunk low between the shoulders: a blunt stone wedge with a deep brow and two narrow cyan crystal eyes. Its two arms are long and very heavy and end in huge, blocky stone fists. The back and shoulders are cracked open, and from the cracks burst large clusters of sharp, faceted crystals in icy cyan and pale violet - from above they form a jagged crystal crown that dominates the silhouette. Thin veins of the same crystal run through cracks in the arms and chest. The stone has flat, chiseled facets and chipped edges. Materials: rough matte rock and smooth, translucent-looking crystal. Palette: dark slate and charcoal stone with the cold crystal colors as the bright eye-catcher.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing upright on two legs, legs straight and slightly apart, both arms hanging down and angled away from the body so they touch neither the body nor the legs, head forward, mouth closed. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\28_geode_golem\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Geode Golem": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A massive, slow golem of split rock, hollow like a geode - ancient, heavy and unstoppable. Its body is a hunched block of dark slate-grey stone with a broad, top-heavy chest and shoulders, a narrow waist and two short, thick, pillar-like legs. The head is small and sunk low between the shoulders: a blunt stone wedge with a deep brow and two narrow cyan crystal eyes. Its two arms are long and very heavy and end in huge, blocky stone fists. The back and shoulders are cracked open, and from the cracks burst large clusters of sharp, faceted crystals in icy cyan and pale violet - from above they form a jagged crystal crown that dominates the silhouette. Thin veins of the same crystal run through cracks in the arms and chest. The stone has flat, chiseled facets and chipped edges. Materials: rough matte rock and smooth, translucent-looking crystal. Palette: dark slate and charcoal stone with the cold crystal colors as the bright eye-catcher.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing upright on two legs, legs straight and slightly apart, both arms hanging down and angled away from the body so they touch neither the body nor the legs, head forward, mouth closed.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 23. Tomb Shroud

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Krypta, Rolle Nahkampf (Assassine, Teleport) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\29_tomb_shroud\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Tomb Shroud" - an original design with a bold silhouette that reads well from a top-down game camera:

A silent crypt wraith - a hooded shroud that floats above the ground, mournful and menacing. It has no legs: the hunched, hooded upper body is wrapped in heavy, tattered grave cloth that hangs down and narrows into a ragged, pointed tail of cloth. Inside the deep hood there is only darkness and a pale, cracked bone mask with two hollow eye holes. Two long, thin, bony arms reach out from the cloth, each ending in a hand with long, hooked, bone-white claws. The cloth is thick and heavy, layered in folds, with torn edges and a few broad, dangling strips, and old rusted chains are wrapped around the chest. Colors: faded ash-grey and dusty bone-white cloth that darkens to deep charcoal at the hem, with a sickly pale green tint in the folds; mask and claws are old ivory. Materials: heavy, coarse burial linen, dry bone and corroded iron.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: floating upright above the ground, both arms held out and angled down away from the body, claws open and apart, the cloth tail hanging straight down without touching the ground. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\29_tomb_shroud\input\design.png`

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

## 24. Idol Eye

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Tempel/Ruinen, Rolle Fernkampf (Strahl) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\30_idol_eye\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Idol Eye" - an original design with a bold silhouette that reads well from a top-down game camera:

A floating temple guardian - an ancient stone idol that has cracked open to reveal a living eye. Its core is one huge, round eye with a gold-amber iris and a narrow dark pupil, wet and watchful. Around the eye a shell of thick, carved stone plates is spread open like the petals of a flower, leaving the eye free at the front. The plates are weathered sandstone with deep carved spiral patterns and inlaid bands of tarnished gold, and their outer rims end in short, blunt stone spikes. Below the eye hangs a heavy stone pendant like the chin of a broken idol. From above it reads as a round, ornamented stone disc with the eye looking out. Colors: warm ochre and sand-colored stone, moss-green weathering in the grooves, dull gold ornaments and the bright amber eye as the eye-catcher. Materials: carved, chipped stone, old gold and a glassy, wet eye.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: floating level above the ground, the eye facing forward, the stone plates spread open evenly and symmetrically around it, each plate separate. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\30_idol_eye\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Idol Eye": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A floating temple guardian - an ancient stone idol that has cracked open to reveal a living eye. Its core is one huge, round eye with a gold-amber iris and a narrow dark pupil, wet and watchful. Around the eye a shell of thick, carved stone plates is spread open like the petals of a flower, leaving the eye free at the front. The plates are weathered sandstone with deep carved spiral patterns and inlaid bands of tarnished gold, and their outer rims end in short, blunt stone spikes. Below the eye hangs a heavy stone pendant like the chin of a broken idol. From above it reads as a round, ornamented stone disc with the eye looking out. Colors: warm ochre and sand-colored stone, moss-green weathering in the grooves, dull gold ornaments and the bright amber eye as the eye-catcher. Materials: carved, chipped stone, old gold and a glassy, wet eye.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: floating level above the ground, the eye facing forward, the stone plates spread open evenly and symmetrically around it, each plate separate.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 25. Bonepicker Vulture

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Gras/Steppe, Rolle Schwarm (kreist, Sturzflug) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\15_bonepicker_vulture\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Bonepicker Vulture" - an original design with a bold silhouette that reads well from a top-down game camera:

A large, ragged steppe vulture - a patient scavenger that circles high and then dives. The body is heavy and hunched with a bulky chest and a thick ruff of bristling feathers around the base of the neck. The neck is long, bare and wrinkled, dull red, and carries a bald, bony head with a long, hooked, bone-white beak and small yellow eyes. Two very broad, long wings with deeply fingered, ragged tips form its signature silhouette; their upper side is dark umber brown with paler sand-colored edges and a row of stiff, sharp quill feathers along the front edge. A short, wide, fan-shaped tail sits at the back. Two strong, scaly grey legs end in big hooked talons. Materials: coarse, layered feathers shaped as clean faceted planes, leathery skin on head and neck, horn on beak and talons. Palette: dusty browns and sand with the raw red neck as the accent.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on its two legs, legs straight down and apart, body level, both wings spread out wide and symmetrically to the sides, fully open and free from the body and the legs, head forward, beak/mouth closed, tail extended straight back. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\15_bonepicker_vulture\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Bonepicker Vulture": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A large, ragged steppe vulture - a patient scavenger that circles high and then dives. The body is heavy and hunched with a bulky chest and a thick ruff of bristling feathers around the base of the neck. The neck is long, bare and wrinkled, dull red, and carries a bald, bony head with a long, hooked, bone-white beak and small yellow eyes. Two very broad, long wings with deeply fingered, ragged tips form its signature silhouette; their upper side is dark umber brown with paler sand-colored edges and a row of stiff, sharp quill feathers along the front edge. A short, wide, fan-shaped tail sits at the back. Two strong, scaly grey legs end in big hooked talons. Materials: coarse, layered feathers shaped as clean faceted planes, leathery skin on head and neck, horn on beak and talons. Palette: dusty browns and sand with the raw red neck as the accent.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on its two legs, legs straight down and apart, body level, both wings spread out wide and symmetrically to the sides, fully open and free from the body and the legs, head forward, beak/mouth closed, tail extended straight back.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 26. Cinder Wyvern

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Vulkan, Rolle Elite (landet zum Kämpfen, Feueratem) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\14_cinder_wyvern\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Cinder Wyvern" - an original design with a bold silhouette that reads well from a top-down game camera:

A fierce volcanic wyvern - a heavy, armored dragon-beast that lands to fight and breathes fire. It has two powerful hind legs with thick clawed feet and no front legs; its two huge wings grow from the shoulders and double as arms, with a hooked claw at each wing wrist. The wings are bat-like with thick, leathery membranes, ash-grey on top with charcoal edges and ember-orange veins. The body is muscular and barrel-chested, covered with overlapping basalt-black scales that break along the back into a ridge of jagged, rock-like plates. The head is long and wedge-shaped with a heavy jaw, rows of teeth and two backward-sweeping horns. A long, thick tail ends in a blunt, spiked club of volcanic rock. The cracks between the plates and the throat are painted in hot orange and red, without any glow. Materials: rough basalt-like scales, leathery wing skin and sharp horn. Palette: black and ash grey with molten orange accents.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on its two legs, legs straight down and apart, body level, both wings spread out wide and symmetrically to the sides, fully open and free from the body and the legs, head forward, beak/mouth closed, tail extended straight back. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\14_cinder_wyvern\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Cinder Wyvern": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A fierce volcanic wyvern - a heavy, armored dragon-beast that lands to fight and breathes fire. It has two powerful hind legs with thick clawed feet and no front legs; its two huge wings grow from the shoulders and double as arms, with a hooked claw at each wing wrist. The wings are bat-like with thick, leathery membranes, ash-grey on top with charcoal edges and ember-orange veins. The body is muscular and barrel-chested, covered with overlapping basalt-black scales that break along the back into a ridge of jagged, rock-like plates. The head is long and wedge-shaped with a heavy jaw, rows of teeth and two backward-sweeping horns. A long, thick tail ends in a blunt, spiked club of volcanic rock. The cracks between the plates and the throat are painted in hot orange and red, without any glow. Materials: rough basalt-like scales, leathery wing skin and sharp horn. Palette: black and ash grey with molten orange accents.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on its two legs, legs straight down and apart, body level, both wings spread out wide and symmetrically to the sides, fully open and free from the body and the legs, head forward, beak/mouth closed, tail extended straight back.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 27. Umbral Panther

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Dschungel, Rolle Nahkampf (Assassine, Sprung aus dem Hinterhalt) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\31_umbral_panther\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Umbral Panther" - an original design with a bold silhouette that reads well from a top-down game camera:

A sleek jungle panther built for ambush - silent, lithe and deadly. The body is long and low with powerful shoulders, a narrow waist and long legs with large, soft paws and hooked claws. The head is broad and flat with a short muzzle, tufted pointed ears, long sabre-like upper fangs and narrow, bright jade-green eyes. A ridge of dark, leaf-shaped bony plates runs down the spine from the neck to the base of the tail - from above it reads like a jagged line along the back. The tail is very long and heavy and ends in a thick, flat tuft. The fur is deep blue-black with darker rosette patterns and a teal sheen on top, lighter slate grey on the belly. Materials: short, sleek fur shaped as clean planes and smooth bone plates. Palette: near-black blues and deep teal, with the green eyes and the pale fangs as accents.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\31_umbral_panther\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Umbral Panther": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A sleek jungle panther built for ambush - silent, lithe and deadly. The body is long and low with powerful shoulders, a narrow waist and long legs with large, soft paws and hooked claws. The head is broad and flat with a short muzzle, tufted pointed ears, long sabre-like upper fangs and narrow, bright jade-green eyes. A ridge of dark, leaf-shaped bony plates runs down the spine from the neck to the base of the tail - from above it reads like a jagged line along the back. The tail is very long and heavy and ends in a thick, flat tuft. The fur is deep blue-black with darker rosette patterns and a teal sheen on top, lighter slate grey on the belly. Materials: short, sleek fur shaped as clean planes and smooth bone plates. Palette: near-black blues and deep teal, with the green eyes and the pale fangs as accents.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 28. Rimehide Bear

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Eis, Rolle Elite (Tank, richtet sich auf) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\32_rimehide_bear\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Rimehide Bear" - an original design with a bold silhouette that reads well from a top-down game camera:

A colossal glacier bear - a hulking, armored beast that rises on its hind legs to smash its prey. The body is massive and round-backed with a huge hump of muscle over the shoulders, a heavy head and four thick, pillar-like legs with wide paws and long black claws. Its fur is shaggy pale blue-grey and white, falling in heavy, faceted clumps on the shoulders, neck and legs. Thick slabs of clear blue glacier ice have frozen onto its back, shoulders and forearms like rough armor plates, with a ridge of jagged ice shards along the spine - from above the frozen armor dominates the silhouette. The head is broad with a short muzzle, small dark eyes under an icy brow and a mouth with heavy fangs. A short stub of a tail sits at the back. Materials: coarse, heavy fur, smooth translucent-looking ice and horn-black claws. Palette: cold whites and steel blues, with the dark mouth and claws as contrast.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\32_rimehide_bear\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Rimehide Bear": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A colossal glacier bear - a hulking, armored beast that rises on its hind legs to smash its prey. The body is massive and round-backed with a huge hump of muscle over the shoulders, a heavy head and four thick, pillar-like legs with wide paws and long black claws. Its fur is shaggy pale blue-grey and white, falling in heavy, faceted clumps on the shoulders, neck and legs. Thick slabs of clear blue glacier ice have frozen onto its back, shoulders and forearms like rough armor plates, with a ridge of jagged ice shards along the spine - from above the frozen armor dominates the silhouette. The head is broad with a short muzzle, small dark eyes under an icy brow and a mouth with heavy fangs. A short stub of a tail sits at the back. Materials: coarse, heavy fur, smooth translucent-looking ice and horn-black claws. Palette: cold whites and steel blues, with the dark mouth and claws as contrast.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 29. Sporecap Mortar

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Pilzwald, Rolle Fernkampf (stationär, Bogenschuss) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\33_sporecap_mortar\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Sporecap Mortar" - an original design with a bold silhouette that reads well from a top-down game camera:

A giant living mushroom turret that lobs spore bombs - rooted, bloated and poisonous. It stands on a thick, squat, fleshy stalk that spreads at the bottom into a wide base of gripping, root-like tendrils clamped to the ground. On top sits a huge, wide mushroom cap facing up, with a round, puckered opening in its center like the barrel of a mortar. The cap is deep violet with large pale lilac spots and a ring of short, thick, fleshy spikes along its rim. Under the cap grow thick, soft gills in pale cream, and a cluster of round, swollen spore sacs bulges from the side of the stalk like ripe fruit. The stalk is pale bone-white with violet veins. Materials: soft, matte, spongy mushroom flesh and slightly wet, glossy spore sacs. Palette: dark violet and bone white with sickly yellow-green tints on the sacs.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still and upright on its base, the base flat on the ground, the top facing up and forward, all flaps, petals or tendrils open, symmetric and apart from each other. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\33_sporecap_mortar\input\design.png`

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

## 30. Bog Ooze

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Sumpf, Rolle Schwarm (teilt sich beim Tod) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\34_bog_ooze\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Bog Ooze" - an original design with a bold silhouette that reads well from a top-down game camera:

A bubbling swamp ooze - a heaving blob of acidic sludge that splits apart when struck. Its body is a big, rounded, lumpy mound of thick, murky green-brown slime, wider at the bottom where it spreads over the ground. Inside the jelly the half-dissolved remains of its prey show as darker shapes: a few bones, a rusted helmet and a skull. The top is crowned by a few large bubbles and short, thick, drooping lumps. Two small, dark, sunken eye spots and a wide, toothless mouth slit sit at its front. Clumps of weed and pond scum cling to its surface. Materials: glossy, wet, jelly-like slime with a clear skin and murky depths. Palette: dark olive and bog brown with bright acid-green highlights on top.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: resting on the ground as one compact, evenly rounded mass, symmetric, not stretched, tilted or squashed, any short appendages separate and apart from each other. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\34_bog_ooze\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Bog Ooze": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A bubbling swamp ooze - a heaving blob of acidic sludge that splits apart when struck. Its body is a big, rounded, lumpy mound of thick, murky green-brown slime, wider at the bottom where it spreads over the ground. Inside the jelly the half-dissolved remains of its prey show as darker shapes: a few bones, a rusted helmet and a skull. The top is crowned by a few large bubbles and short, thick, drooping lumps. Two small, dark, sunken eye spots and a wide, toothless mouth slit sit at its front. Clumps of weed and pond scum cling to its surface. Materials: glossy, wet, jelly-like slime with a clear skin and murky depths. Palette: dark olive and bog brown with bright acid-green highlights on top.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: resting on the ground as one compact, evenly rounded mass, symmetric, not stretched, tilted or squashed, any short appendages separate and apart from each other.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 31. Oasis Gulper

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Oase, Rolle Nahkampf/Kontrolle (Zungenschlag zieht heran) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\16_oasis_gulper\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Oasis Gulper" - an original design with a bold silhouette that reads well from a top-down game camera:

A huge, bloated oasis toad - a lazy-looking ambusher that snaps prey from afar with its long tongue. The body is broad, round and squat, sitting low, with a wide, flat head that merges into the body without a neck. The mouth is enormous, a wide grinning slit across the whole front of the head, with a pale yellow throat pouch below. Two big, bulging amber eyes sit on top of the head. The front legs are short and sturdy, the hind legs big and powerful with long webbed feet. The back is covered with warty bumps, and a few small, flat lily pads and reeds grow from the skin like a living pond. The skin is turquoise and teal on top with dark spots, sandy yellow on the belly, with bold orange warning stripes along the sides. Materials: smooth, glossy, wet skin with rough warts. Palette: turquoise water colors with warm sand and orange accents.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours with straight, fully extended legs, the big hind legs stretched out and clearly visible at their full length, body lifted clear of the ground, feet flat on the ground, head forward, mouth closed. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\16_oasis_gulper\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Oasis Gulper": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A huge, bloated oasis toad - a lazy-looking ambusher that snaps prey from afar with its long tongue. The body is broad, round and squat, sitting low, with a wide, flat head that merges into the body without a neck. The mouth is enormous, a wide grinning slit across the whole front of the head, with a pale yellow throat pouch below. Two big, bulging amber eyes sit on top of the head. The front legs are short and sturdy, the hind legs big and powerful with long webbed feet. The back is covered with warty bumps, and a few small, flat lily pads and reeds grow from the skin like a living pond. The skin is turquoise and teal on top with dark spots, sandy yellow on the belly, with bold orange warning stripes along the sides. Materials: smooth, glossy, wet skin with rough warts. Palette: turquoise water colors with warm sand and orange accents.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing on all fours with straight, fully extended legs, the big hind legs stretched out and clearly visible at their full length, body lifted clear of the ground, feet flat on the ground, head forward, mouth closed.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 32. Quillback Burrower

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Stein, Rolle Fernkampf (gräbt sich ein, Stachel-Salve) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\35_quillback_burrower\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Quillback Burrower" - an original design with a bold silhouette that reads well from a top-down game camera:

A stocky, armored burrowing beast of the rocky badlands - it digs in, hides and fires its quills. The body is low, wide and muscular like a badger, with short, strong legs and huge, shovel-like front claws made for digging. The head is long and wedge-shaped with a blunt snout, small black eyes and a mouth with short, sharp teeth. Its back is covered by a dense mantle of long, thick, stone-grey quills that sweep backward from the neck to the tail and stand up into a bristling crest - from above it reads as a spiked dome. Flat, cracked plates of stone-colored hide protect the shoulders between the quills. The short tail bristles with quills as well. The fur on face, belly and legs is coarse and dark brown-grey, with a pale stripe running from the nose over the head. Materials: coarse fur, hard quills with pale tips and rough plated hide. Palette: dusty stone greys and dark browns with bone-white quill tips.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\35_quillback_burrower\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Quillback Burrower": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A stocky, armored burrowing beast of the rocky badlands - it digs in, hides and fires its quills. The body is low, wide and muscular like a badger, with short, strong legs and huge, shovel-like front claws made for digging. The head is long and wedge-shaped with a blunt snout, small black eyes and a mouth with short, sharp teeth. Its back is covered by a dense mantle of long, thick, stone-grey quills that sweep backward from the neck to the tail and stand up into a bristling crest - from above it reads as a spiked dome. Flat, cracked plates of stone-colored hide protect the shoulders between the quills. The short tail bristles with quills as well. The fur on face, belly and legs is coarse and dark brown-grey, with a pale stripe running from the nose over the head. Materials: coarse fur, hard quills with pale tips and rough plated hide. Palette: dusty stone greys and dark browns with bone-white quill tips.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing still, all four legs straight down under the body, front and hind legs equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back, no twisting.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at body height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 33. Ruin Howler

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Tempel/Ruinen, Rolle Schwarm/Fernkampf (Rudel, wirft Steine) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\17_ruin_howler\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Ruin Howler" - an original design with a bold silhouette that reads well from a top-down game camera:

A lanky, savage temple ape that lives in overgrown ruins - loud, agile and hurling chunks of stone. It walks on all fours on its long, powerful arms and shorter, bent legs, and has a long, thick tail. Its body is lean, with a hunched back and a broad chest. The head has a long, dog-like snout, a jaw full of long canine fangs and deep-set red eyes under a heavy brow; a mane of stiff, bristling hair frames the face and shoulders. Fragments of carved temple stone and tarnished gold rings are grown into the skin of its shoulders and forearms like trophies. The fur is dark rusty brown, lighter and sand-colored on the chest, and the bare face carries a vivid crimson and blue mask like a mandrill. Materials: coarse fur shaped as clean faceted clumps, bare leathery face, stone and old gold. Palette: rusty browns and sand with the vivid face as the eye-catcher.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing on all fours, the long front arms resting on the knuckles, arms and hind legs straight down and equally wide apart, head forward, mouth closed or only slightly open, tail extended straight back. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\17_ruin_howler\input\design.png`

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

## 34. Tallgrass Viper

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Gras/Steppe, Rolle Nahkampf (Hinterhalt, Schlag aus der S-Kurve) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\36_tallgrass_viper\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Tallgrass Viper" - an original design with a bold silhouette that reads well from a top-down game camera:

A long, sleek steppe viper that hides in the tall grass and strikes from an S-curve - fast and deadly. The body is long and muscular, thickest in the middle, and tapers to a thin tail that ends in a rattle of dry, horny segments. The head is a broad, flat triangle with two short, pointed horns above the eyes, narrow golden eyes with slit pupils and long fangs hidden in the closed mouth. Along the back runs a bold zigzag pattern of dark olive and black over straw-yellow scales that blends in with dry grass; the belly is pale cream with broad plate-like scales. A row of small, raised, keeled scales forms a low ridge along the spine. Materials: dry, matte, keeled scales, smooth belly plates and a horny rattle. Palette: straw yellow, olive and ochre with black zigzags.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long on the ground with at most one gentle curve, not coiled, twisted or overlapping, head slightly raised and facing forward, mouth closed or only slightly open. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\36_tallgrass_viper\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Tallgrass Viper": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A long, sleek steppe viper that hides in the tall grass and strikes from an S-curve - fast and deadly. The body is long and muscular, thickest in the middle, and tapers to a thin tail that ends in a rattle of dry, horny segments. The head is a broad, flat triangle with two short, pointed horns above the eyes, narrow golden eyes with slit pupils and long fangs hidden in the closed mouth. Along the back runs a bold zigzag pattern of dark olive and black over straw-yellow scales that blends in with dry grass; the belly is pale cream with broad plate-like scales. A row of small, raised, keeled scales forms a low ridge along the spine. Materials: dry, matte, keeled scales, smooth belly plates and a horny rattle. Palette: straw yellow, olive and ochre with black zigzags.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body stretched out long on the ground with at most one gentle curve, not coiled, twisted or overlapping, head slightly raised and facing forward, mouth closed or only slightly open.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 35. Mound Queen

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Dschungel, Rolle Boss (legt Brut) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\37_mound_queen\input`

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Mound Queen" - an original design with a bold silhouette that reads well from a top-down game camera:

An enormous termite-like queen of a jungle hive - a slow, bloated mother of the swarm that births her brood in battle. At the front sits a comparatively small, armored insect body with a heavy, plated head, a pair of large serrated mandibles and two thick, curved antennae. Six sturdy, jointed legs carry her, set wide to both sides of the front body. Behind them stretches a gigantic, swollen, segmented abdomen like a pale sac, ribbed with darker bands of chitin plates; it rests on the ground and drags behind her. Clusters of round, glossy eggs cling to the sides of the abdomen, and short chitin spikes line the bands on top. Head and legs are glossy dark amber-brown, the abdomen is pale ivory with a pinkish flesh tint and dark brown bands. Materials: polished chitin, soft stretched membrane and wet eggs. Palette: dark amber and brown with the huge pale abdomen as the dominant shape.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body level, all six legs spread evenly and symmetrically to both sides of the front body, none crossing, the huge abdomen stretched straight back behind the legs and resting on the ground, mandibles closed. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\37_mound_queen\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Mound Queen": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): An enormous termite-like queen of a jungle hive - a slow, bloated mother of the swarm that births her brood in battle. At the front sits a comparatively small, armored insect body with a heavy, plated head, a pair of large serrated mandibles and two thick, curved antennae. Six sturdy, jointed legs carry her, set wide to both sides of the front body. Behind them stretches a gigantic, swollen, segmented abdomen like a pale sac, ribbed with darker bands of chitin plates; it rests on the ground and drags behind her. Clusters of round, glossy eggs cling to the sides of the abdomen, and short chitin spikes line the bands on top. Head and legs are glossy dark amber-brown, the abdomen is pale ivory with a pinkish flesh tint and dark brown bands. Materials: polished chitin, soft stretched membrane and wet eggs. Palette: dark amber and brown with the huge pale abdomen as the dominant shape.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: body level, all six legs spread evenly and symmetrically to both sides of the front body, none crossing, the huge abdomen stretched straight back behind the legs and resting on the ground, mandibles closed.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly above body height, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 36. Bog Warden

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Sumpf, Rolle Elite (Tank, Wurzel-Slam) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\18_bog_warden\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Bog Warden" - an original design with a bold silhouette that reads well from a top-down game camera:

A hulking, ancient swamp tree that has torn itself from the mud - a slow, patient guardian that smashes the ground with its roots. Its body is a thick, gnarled, hunched trunk of dark, wet bark, standing on two short, massive legs of twisted roots that spread into claw-like root feet. Two very long, heavy arms of bent branches hang from the shoulders and end in big hands of knotted root-fingers. Where a head should be, a hollow in the trunk forms a face with a deep, dark mouth and two small eyes of pale amber fungus. Its crown is a broad, flat canopy of dead, crooked branches draped with thick strands of grey-green moss - from above it reads as a wide, ragged tree top. Shelf fungi, ivy and moss grow over the bark. Materials: rough, cracked bark, damp moss and soft fungus. Palette: dark brown-black bark, grey-green moss and pale amber accents.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: standing upright on two legs, legs straight and slightly apart, both arms hanging down and angled away from the body so they touch neither the body nor the legs, head forward, mouth closed. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\18_bog_warden\input\design.png`

```text
Image 1 is the approved, binding design of my creature "Bog Warden": keep its anatomy, shapes, colors, materials, style and the number of all parts exactly. Do not redesign, add or remove anything.

Description (also for the hidden sides): A hulking, ancient swamp tree that has torn itself from the mud - a slow, patient guardian that smashes the ground with its roots. Its body is a thick, gnarled, hunched trunk of dark, wet bark, standing on two short, massive legs of twisted roots that spread into claw-like root feet. Two very long, heavy arms of bent branches hang from the shoulders and end in big hands of knotted root-fingers. Where a head should be, a hollow in the trunk forms a face with a deep, dark mouth and two small eyes of pale amber fungus. Its crown is a broad, flat canopy of dead, crooked branches draped with thick strands of grey-green moss - from above it reads as a wide, ragged tree top. Shelf fungi, ivy and moss grow over the bark. Materials: rough, cracked bark, damp moss and soft fungus. Palette: dark brown-black bark, grey-green moss and pale amber accents.

Create 4 SEPARATE images (not a grid) of exactly this creature - one frozen 3D model, the camera circles around it:
1. front.png - facing the camera
2. left.png - its own left side, head to the LEFT image edge
3. right.png - its own right side, head to the RIGHT image edge
4. back.png - from directly behind

Rules for the 3D model:
- Same posture in all views, only the camera moves. Pose: standing upright on two legs, legs straight and slightly apart, both arms hanging down and angled away from the body so they touch neither the body nor the legs, head forward, mouth closed.
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera at chest height, very slightly from above, orthographic-like, no perspective distortion; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```

## 37. Gloomfang Centipede

**Ohne Concept** – Design-Entwurf aus der Beschreibung, Heimat-Biom Höhle, Rolle Nahkampf (schnell, Giftklauen) · Ordner `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\19_gloomfang_centipede\input` · **Tripo-Modell vorhanden – nur bei Neubau nötig**

### Stufe 1 – Design-Bild → `input/design.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\01_chitin_crawler\input\concept\2_style_lowpoly_insects_B.png`

```text
Image 1 is only an art-style reference: copy its rendering style, not the creatures in it.

There is no concept art for this creature yet: design it from the description below. Paint ONE clean, sharp, high-resolution design image of my creature "Gloomfang Centipede" - an original design with a bold silhouette that reads well from a top-down game camera:

A giant cave centipede - a fast, writhing hunter of the deep tunnels with venomous claws. The body is a long, flat chain of armored segments, each with a pair of long, jointed, sharp-tipped legs spread out to the sides, giving it a dense fringe of legs along its whole length. The head is flat and shield-shaped, with a pair of long, segmented antennae sweeping forward and a pair of huge, curved, pincer-like venom claws at the front. At the rear end, two long trailing legs point backward like a second pair of antennae. The armor plates are glossy dark maroon to black-red, each segment edged with a lighter rust-orange rim; the legs are pale amber with dark tips. Materials: polished, hard, segmented chitin. Palette: deep blood red and black, with the amber legs as a bright fringe.

Style: clean low-poly stylized game creature: faceted planar surfaces with crisp edges, simplified chunky shapes, bold readable silhouette that reads well from a top-down camera, strong color blocking with simple painted gradients per facet, colorful yet dark palette, gameplay-focused readability, rendered like a stylized low-poly 3D game asset.

Show the whole creature, uncropped, in a three-quarter view (from the front and a bit from the side) at body height. Pose: body stretched out long and straight on the ground, not coiled, all leg pairs spread evenly to both sides, none crossing, head slightly raised and facing forward, venom claws closed. All limbs clearly visible and apart from each other. Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching. Plain flat medium-grey (#9a9a9a) background, soft even lighting, no cast shadows, no glow, no smoke or particles, no text. One single square 1:1 image.
```

### Stufe 2 – 4 Ansichten → `front.png`, `left.png`, `right.png`, `back.png`

Anhängen: 1. `H:\AIProjects\3D AI\01_kreatur_pipeline\creatures\19_gloomfang_centipede\input\design.png`

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
- Every leg, arm, wing and tail is shown at its full length and clearly visible - extended, not folded, tucked under the body, sitting or crouching.
- Limbs and appendages stand free, touching neither each other nor the body; nothing hangs between the legs.
- Thin parts have visible thickness. Same number of parts as in the design, in every view.
- Whole creature centered and uncropped; camera slightly from above, orthographic-like, whole body length in frame; plain flat medium-grey (#9a9a9a) background, soft even light, no shadows, glow, particles or text; square 1:1.
```
