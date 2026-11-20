# Recherche: Tripo-Kosten und Alternativen (Image-to-3D)

Stand: 2026-11-20. Reine Web- und Code-Recherche, nichts gebaut, nichts bezahlt.
Wechselkurs-Annahme: 1 USD ≈ 0,90 € (nicht geprüft, grobe Annahme). Preise der Anbieter sind in USD, soweit nicht anders genannt.

Vertrauensstufen: **[offiziell]** = Doku des Anbieters, **[Reseller]** = Drittanbieter-Plattform (Preis kann Aufschlag enthalten), **[Blog/Hersteller]** = Vergleich von Anbieter oder Aggregator (befangen oder widersprüchlich).

## Teil 1 – Was wir bei Tripo bezahlen

**Gebuchte Optionen** (`pipeline.toml` Abschnitt `[tripo]`, ausgeführt von `scripts/tripo_run.py`):
- Endpunkt `POST /v3/generation/multiview-to-model` (4 Ansichten front/left/back/right; bei einem Bild `image-to-model`).
- Modell `P2-20260801` (P-Serie, Low-Poly), `face_limit = 4000`, `quad = false` (Dreiecke).
- `texture = true`, `pbr = true` (BaseColor, Metallic, Roughness, Normal), `texture_quality = "standard"`, `texture_version = "v3.5-20260815"`, `delight = true`, `auto_size = false`, Seeds zufällig. `export_uv` bleibt Standard (true).
- Ergebnis laut `raw/tripo_state.json`: `generate_model.glb` (Mesh + UVs + PBR-Texturen im GLB) und `generate_rendered_image.webp` (Vorschau). `credits_consumed` steht bei **allen** geprüften Kreaturen (Beispiel Broodling) auf **110,0**.
- Rig und Animation (Tripo) sind in der Config noch vorhanden, werden laut Projektregel nicht genutzt und würden extra kosten (Auto-Rig 25 Credits, Rig-Check kostenlos).

**Zusammensetzung der 110 Credits:** Tripo veröffentlicht keine Einzelpreise pro Parameter, die Doku-Seiten nennen keine Tabelle ([Billing-Doku](https://developers.tripo3d.com/en/docs/billing.md), [P-Multiview-Doku](https://developers.tripo3d.com/en/docs/generation-multiview-to-model/p.md): „Different task types consume different numbers of credits“). Die plausibelste Aufschlüsselung stammt vom Reseller 3D AI Studio für die Schwester-Version P1 [Reseller]: Multiview-Basis 80 + Textur standard 20 = 100; dazu kommt vermutlich PBR mit ca. 10 = **110**. Das passt exakt zu unseren gemessenen 110. Die Aufschlüsselung ist **Schätzung**, nur die Summe ist gemessen. Quelle: [3D AI Studio P1](https://www.3daistudio.com/Platform/API/Documentation/3d-generation/tripo-p1). Der Tripo-eigene Blog nennt für H-Serie niedrigere Werte (Multiview 20–30, Textur 10–30) – das gilt nicht für P-Serie ([Tripo Developer-Seite](https://developers.tripo3d.ai/)). `texture_quality = detailed` würde laut Reseller ca. +20 bis +60 kosten, `extreme` (8K) mehr.

**Preis pro Credit:** Die Tripo-Developer-Seite sagt **„1 credit = $0.01 USD“** ([developers.tripo3d.ai](https://developers.tripo3d.ai/)); Aufladung in 100er-Einheiten, laut Ankündigung ([Blog](https://www.tripo3d.ai/blog/announcement-tripo-openapi-platform-payment-system)) ebenfalls $0,01/Credit. AWS-Marketplace-Enterprise: 500.000 Credits für 4.500 $ (= $0,009/Credit) ([Listing](https://aws.amazon.com/marketplace/pp/prodview-hwlbvx7vubh7c)). Chinesische Plattform: 1 Credit = ¥0,07 (≈ $0,01).
Web-App-Credits (Subscription, z. B. 1000 Credits = 10 $) sind **nicht** dasselbe wie API-Credits laut Tripo-Hilfe.

**Stimmt „110 Credits = 1,10 €“?** Fast: **110 Credits = 1,10 USD ≈ 1,00 €** (bei 0,90 €/$). Die Zahl stimmt, nur die Währung ist Dollar. Mit Mengenrabatt (Enterprise) wäre es etwas weniger. Fehlgeschlagene Läufe und Wiederholungen (neuer Seed) kosten zusätzlich.

## Teil 2 – Vergleichstabelle (Multiview-Bild → texturiertes Low-Poly-Mesh, ca. 4.000 Faces)

| Dienst | €/Modell (ca.) | Multiview | Low-Poly steuerbar | PBR / UV | API | Kommerzielle Lizenz |
|---|---|---|---|---|---|---|
| **Tripo P2** (heute) | **~1,00** (110 Cr à $0,01) | ja, 2–4 | ja, direkt: `face_limit` 48–50.000, optional Quads | PBR ja; UV-Export ja, Qualität bei uns durch `uv/`-Prüfung | ja | ja über API/Bezahlkonto (Lizenztext prüfen) |
| **Meshy 6 / 7.1** | ~0,60–0,70 (30 Cr Textur + 5 Remesh = 35 Cr; Pro-Plan $20 = 1000 Cr ⇒ $0,02/Cr ⇒ ~$0,70) | ja, 1–4 Bilder | ja, `target_polycount` 100–300.000, Tri oder Quad (nur mit `should_remesh`) | PBR optional (`enable_pbr`), 2K/4K/8K | ja (Credits im Abo) | bezahlte Pläne ja, Free-Plan nein (Free-Modelle CC BY; prüfen) |
| **Hyper3D Rodin Gen-2/2.5** | ~0,36 (fal: $0,40; Extreme-High $0,80; HighPack $0,80 extra) | ja, bis 5 Bilder (Reseller: +5 Cr) | ja, Quad-Presets bis „extra-low“ = 4.000 Faces | PBR ja; UV laut Ufo3D-Test bei Rodin V2 unbrauchbar (nur Einzelbild getestet) | ja (fal, Runware; offiziell nur Business-Plan $120/Monat) | widersprüchlich: nur Business-Plan klar; unklar |
| **Tencent Hunyuan3D v3 / 3.5 Cloud** | ~0,34–0,38 (fal/WaveSpeed $0,375–0,38; 3D AI Studio: Pro 60 + PBR 20 + Multiview 20 = 100 Cr) | ja (nur Pro-Edition) | ja, aber **Mindestwert 40.000** Faces; Low-Poly-Modus (Tri/Quad) | PBR ja; UV laut Ufo3D nicht brauchbar | ja | ja, Cloud-API laut Tencent-AGB (prüfen) |
| **Hunyuan3D 2.0/2.1 lokal** | 0 | 2.0: ja (mv-turbo); 2.1: Einzelbild | nein (danach Decimate) | 2.1 PBR; 2.0 nur RGB | lokal | **Community-Lizenz schließt EU, UK, Südkorea aus** – für uns ungeeignet |
| **TRELLIS.2 (Microsoft, lokal)** | 0 (Strom) | nur Einzelbild bestätigt | nein, Tri-Mesh hochauflösend, braucht Retopo/Decimate | PBR ja; UV nicht spielfertig | lokal/ComfyUI | MIT (laut Beschreibungen; Repo prüfen) |
| **Pixal3D (Tencent ARC, lokal)** | 0 | Einzelbild | nein | PBR-GLB | lokal, `--low_vram` | unbekannt/prüfen, wegen Tencent evtl. EU-Klausel |
| **Stability SF3D / SPAR3D** | 0 (lokal) | nein, Einzelbild | nein | UV-entfaltet, einfache Materialien | lokal / Stability-API | Community-Lizenz: frei bis 1 Mio. $ Jahresumsatz, darüber Enterprise |
| **3D AI Studio** (Aggregator) | je Modell, z. B. Tripo/Rodin/Hunyuan ~0,25–0,95 je nach Paket | je Modell | je Modell | je Modell | ja | je Modell |
| **CSM** | unklar (Maker $20/Monat, Credits nicht ermittelt) | ja | eher Remesh | PBR ja | ja | nicht geklärt; CSM laut Costbench seit 01/2026 bei Google |
| **Sudo AI** | nicht ermittelt (keine Treffer) | – | – | – | – | – |
| **Kaedim** (Mensch im Loop) | ca. 20 $ bis 60 $ pro Modell (Indie $400/Monat für 20 Credits; Quellen widersprüchlich) | ja | saubere Topologie durch Künstler | ja | ja | ja |

### Unabhängige Tests und Stimmen
- [Ufo3D-Test](https://ufo3d.com/ai-3d-model-generators-tested/) (Rucksack, 4 Fotos): Meshy 7 > Hunyuan 3D V3 > Tripo V3.1 bei Oberflächendetail. **Keines** der Ergebnisse hatte nutzbare UVs oder Edge-Flow; Handmodell hatte weniger Polygone und saubere UVs. Testet aber hochdetailliert, **nicht Low-Poly/Kreaturen**.
- [Meshy-Blog „Best AI 3D Agent“](https://www.meshy.ai/blog/best-ai-3d-agent) (Hersteller, befangen): Hi3D und Tripo liefern sauberere Low-Poly-Topologie/UVs als Meshy, Rodin schwach für Game-Pipeline.
- [Kenerate-Review](https://kenerateai.com/blogs/tripo-vs-meshy-vs-rodin): Tripo rangiert bei nacktem Mesh vorne (Meshy-6-Test); Meshy besser bei smarter Topologie, Auto-Rig.
- [Medium-Vergleich](https://medium.com/ideas-with-wings/best-ai-3d-model-generators-in-2026-tripo-ai-vs-meshy-rodin-kaedim-and-more-7eea7b05eb11) und [Preisvergleich 3D AI Studio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/ai-3d-generator-pricing-compared) (Stand 1.11.2026, Aggregator, eigenes Interesse): Meshy 6 $0,60 (Pro-Plan), Rodin $0,50 (Creator-Plan), Hunyuan $0,38, Hitem3D $0,80.
- Fazit: **Es gibt keinen unabhängigen Test für stilisierte Low-Poly-Kreaturen.** Aussagen zu Stärken/Schwächen bei Kreaturen sind aus Quellen nicht belegbar; nur ein eigener Testlauf klärt das.

### Weitere Quellen
- Meshy-Preise (offiziell): [docs.meshy.ai/api/pricing](https://docs.meshy.ai/api/pricing.md); Multi-Image-API: [docs](https://docs.meshy.ai/en/api/multi-image-to-3d.md). Hinweis: Meshy-Changelog meldet ab 30.11.2026 Änderungen (T1-Requests werden abgelehnt), meshy-7 läuft Ende 2026 aus.
- Rodin: [Runware Polygon-Budget](https://runware.ai/docs/models/hyper3d-rodin-gen-2/guides/topology-and-polygon-budget), [fal.ai Rodin](https://fal.ai/models/fal-ai/hyper3d/rodin/v2.5)
- Hunyuan: [Tencent Cloud Credits](https://www.tencentcloud.com/document/product/1284/75281), [3D AI Studio Hunyuan 3.5](https://www.3daistudio.com/Platform/API/Hunyuan3D35), [HF-Lizenz 2.1](https://huggingface.co/tencent/Hunyuan3D-2.1), [README (VRAM)](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2.1/main/README.md)
- TRELLIS.2: [Low-VRAM-Guide](https://trellis2.app/blog/trellis-2-low-vram), [ComfyUI-Nativ](https://blog.comfy.org/p/trellis2-and-pixal3d-are-now-native), [Vergleich Meshy](https://www.meshy.ai/vi/compare/meshy-vs-trellis-2) (Hersteller)
- Pixal3D: [Bericht](https://www.creativeainews.com/blog/pixal3d-pixel-aligned-image-to-3d-tencent-2026/)
- Stability: [SPAR3D](https://stability.ai/news/stable-point-aware-3d), [SF3D](https://huggingface.co/stabilityai/stable-fast-3d)
- CSM/Kaedim: [Costbench CSM](https://www.costbench.com/software/ai-3d-generation/csm/), [Costbench Kaedim](https://www.costbench.com/software/ai-3d-generation/kaedim/), [Kaedim Plans](https://kaedim3d.com/plans)
- Tripo-Preisseite selbst und Credit-Hilfe lieferten HTTP 403 (nicht abrufbar). Preise daher aus Developer-Seite und Reseller.

## Teil 3 – Einordnung

**Tripo preislich:** ca. 1 $ pro Modell, bei 50–100 Basis-Monstern **50–110 $**. Das ist gegenüber der Arbeit (Rig, Animation, Prüfung) vernachlässigbar. Preislich ist Tripo etwas teurer als Meshy/Rodin/Hunyuan (ca. 0,35–0,70 $), aber nicht um einen Faktor, der zählt.

**Tripo qualitativ:** Für unseren Zweck der klare Vorteil: P-Serie erzeugt **direkt** Low-Poly (`face_limit` 4.000) mit sauberer Topologie, Multiview-Eingabe, UV und PBR in einem Schritt. Meshy kann das auch (Remesh `target_polycount`), Rodin ebenfalls (Quad-Preset „extra-low“), Hunyuan-Cloud nicht unter 40.000 Faces. Unabhängige Tests zeigen: generative UVs und Edge-Flow sind bei allen Diensten schwach (unsere eigene UV-Prüfung bleibt deshalb nötig).

**Lohnt ein Test anderer Dienste?** Ja, ein kleiner, begrenzter Test:
1. **Meshy 7.1 Multi-Image** (1–4 Bilder, `target_polycount = 4000`, `should_remesh`, `enable_pbr`): ~35 Credits ≈ 0,70 $ pro Modell, günstiger, gleiches Bildset. Beim Plan Pro ($20, 1000 Credits) reichen die Credits für ca. 28 Modelle, also Testlauf mit 3–4 Kreaturen ≈ 3 $. Frage: gleich gute Silhouette bei 4.000 Faces, bessere UVs/Textur?
2. **Rodin Gen-2.5 via fal.ai** (Quad „extra-low“ 4.000, bis 5 Bilder): ca. 0,40–0,80 $ pro Modell, ohne Abo über fal bezahlbar. Frage: Mesh-Qualität an Gliedmaßen, Quads sind riggingfreundlich.
Testkreaturen: dieselben 4 Ansichten wie bei bereits gebauten Monstern (z. B. Wolf/Quadruped, Needle Wasp, Broodling), damit direkt vergleichbar. Gesamtkosten ca. **5–8 $** für beide Dienste, je 3 Kreaturen.

**Lokal und kostenlos auf 8 GB VRAM?** Brauchbar für **Prototypen**, nicht als Ersatz:
- TRELLIS.2: läuft laut Community mit 8 GB im Low-VRAM-Modus bei 512³ (Spitze ca. 6,2–7,8 GB), MIT-Lizenz. Aber: nur Einzelbild (Multiview nicht bestätigt), Ergebnis hochauflösendes Dreiecksnetz, braucht Decimate/Retopo/UV-Neubau; kein Low-Poly-Stil direkt.
- Hunyuan3D lokal: offiziell 10 GB (Form) / 21 GB (Textur) / 29 GB gesamt; **Lizenz schließt die EU aus** – für uns gesperrt, unabhängig von der Hardware.
- SF3D/SPAR3D: laufen mit ~7 GB, Einzelbild, UV-entfaltet, Qualität für Kreaturen ungetestet, Umsatzgrenze 1 Mio. $.
Ein lokales Testen von TRELLIS.2 lohnt nur als Experiment (Aufwand: Installation, Retopo-Schritt); kein belegter Qualitätsgewinn gegenüber 1 $ Tripo.

**Hochrechnung 100 Monster** (ohne Fehl- und Wiederholungsläufe; mit 30 % Wiederholungen ca. +30 %):

| Dienst | pro Modell | 100 Modelle |
|---|---|---|
| **Tripo P2** (110 Cr) | ~1,00 € | **~100 €** (mit Wiederholungen ~130 €) |
| **Meshy 7.1** (35 Cr, Pro-Plan $0,02/Cr) | ~0,63 € | ~63 € (≈ 3.500 Credits ⇒ Premium-Plan $40/3000 + Reste; real ca. 65–75 $) |
| **Rodin Gen-2.5 (fal)** | ~0,36 € | ~36 € (Multi-Image evtl. +5 Cr; Extreme-High verdoppelt) |
| **Hunyuan3D Cloud v3** | ~0,34 € | ~34 € (aber Low-Poly erst nach eigenem Decimate) |

Die Differenz zwischen Tripo und dem günstigsten Dienst beträgt ca. 65 € bei 100 Monstern. Das ist weniger wert als eine Stunde Nacharbeit; **Qualität und Rig-Tauglichkeit entscheiden, nicht der Preis.**

## Empfehlung
1. **Bei Tripo P2 bleiben.** Preis (~1 $/Modell) und Funktionsumfang (direkt Low-Poly, Multiview, PBR, UV) passen; kein Grund zu wechseln.
2. **Korrektur für den Nutzer:** 110 Credits = 1,10 **Dollar** (≈ 1,00 €), nicht Euro; 100 Monster ≈ 100–130 €.
3. **Kleiner Gegentest** mit Meshy 7.1 (Multi-Image, 4.000 Faces) und optional Rodin Gen-2.5 über fal.ai: je 3 bereits vorhandene Kreaturen, Kosten gesamt ca. 5–8 $. Bewertung nach unserer bestehenden Checkliste (Silhouette, Gliedmaßen, UV-Prüfung `uv/`, Tris, Rig-Tauglichkeit).
4. **Lokale Modelle** nur als Experiment (TRELLIS.2), Hunyuan lokal wegen EU-Ausschluss nicht verwenden.
5. Offen und vor einer Entscheidung zu klären: exakte Credit-Aufschlüsselung bei Tripo (kleiner bezahlter Mini-Test mit `texture_quality`/`pbr`-Varianten oder `/v3/account/usage` auswerten), Lizenztexte (Tripo, Meshy, Rodin) im Original lesen.
