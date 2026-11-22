# Varianten-Baukasten – Arbeitsstand (WIP, Build-Agent)

Notizbuch für den Fall, dass das Token-Limit zuschlägt. Die Nutzer-Anleitung + Entwickler-Notiz steht in `VARIANTEN_BAUKASTEN.md`
(Teile A/B = M1, C/D = M2).

## M1: fertig, committet (87ff233)

## M2: fertig 2026-11-22, NICHT committet (Freigabe/Commit macht der Hauptchat)
- [x] Blender-Paket `procedural/variantkit_blender/` (Panel, Statur, Lagen per Geometry Nodes, Werkbank, Accessoires-Anzeige,
      Start-Skript + .cmd, headless `vk_headless.py -- bauen|bausteine|bild`)
- [x] Unity: VkCover, VkBlender („In Blender bauen“ im Hintergrund), VkTexBake (Atlas + Textur-Backen), Shader
      VariantLayers.cginc / VariantBake / VariantBaked, Fenster-Knopf + Fortschritt, Batch `-vkBlender` + Vergleich
- [x] Presets A B C E F G I, 15 neue Bausteintypen, Zonen `flanke_l/_r` neu (+ Kriterien `ueber`, `nicht_knochen`)
- [x] Varianten `rimehide_eisriese` (Fell) und `quillback_bear` (Stacheln + Gesichtsfell)
- [x] Selbstprüfung: alle 4 Varianten gebacken, Vorschau ↔ gebacken 0,4–1,9/255, Gegenprobe CreatureImporter identisch
- [x] Doku Teil C/D

## Hinweise für die nächste Session
- Batch immer mit **Unity 6000.3.28f1**. Hilfsskripte: `temp/vk2_work/run_batch.sh` (Ausgabe `temp/vk2_work/batch.log`).
- Blender 5.3: Modifier-Eingänge über `mod.properties.inputs.<Socket_n>.value` (nicht mehr `mod["Socket_n"]`), siehe
  `vk_nodes.set_mod_input`.
- Prüfbilder: `temp/vk2_shots/` (Unity), `temp/vk2_shots_blender/` (Blender), Panel-Screenshots `temp/vk2_work/gui_*.png`.
- Erzeuger-Skripte für Presets/Varianten (Platzhalter-Werte): `temp/vk2_work/make_presets.py`, `make_variants.py`.

## G14 Nachschwingen im Shader – FERTIG 2026-11-22, NICHT committet (Commit macht der Hauptchat)
Stand vor dem Limit-Reset: noch nichts gebaut (Arbeitsbaum war sauber). Neustart 2026-11-22.
**Plan / Entscheidungen**
- Beweglichkeit = vorhandenes `vk_h` (Blender GN, 0 Wurzel … 1 Spitze, Export `h` in `.bedeckung.json`) bzw. bei Accessoires
  `z / Höhe des Bausteins`. Neu: Vertex-Kanal **TEXCOORD1** = (h, weichheit [+2 = folgt Schwerkraft], Slot + Phase, Teil-Länge / L)
  in Vorschau-Mesh UND Spiel-Mesh; **TANGENT.xyz** = Teil-Achse (Wurzel → Spitze) nur für schwingende Teile (wird mitgeskinnt).
- Shader-Code in `Shaders/VariantSwing.cginc` (Layered, Baked, optional Creature/Standard Dangling). Biegung als Kreisbogen um die
  Wurzel → Länge bleibt gleich. Quellen: Trägheit (4 Slots: Hüfte, Brust, Kopf, Schwanz), Wackeln, Stöße (Zittern-Hülle).
- Laufzeit `VariantKit/Scripts/VariantSchwingen.cs`: Feder pro Slot, MaterialPropertyBlock, `VKStoss(string)` als AnimationEvent-Empfänger.
- `weichheit` ersetzt `schwingen` (Lagen) und `bewegung`/`schwingen.staerke` (Accessoires). Migration beim Laden (C# + Python).
- Gehänge: `auf`/`stelle` + Ausrichtung `unten`.
**Fortschritt**
- [x] Shader `VariantSwing.cginc`, Layered/Baked (vert), Komponente `VariantSchwingen.cs`, VkBuilder (TEXCOORD1, Tangente,
      `auf`/`stelle`, Ausrichtung `unten`), VkTexBake (Kanal ins Spiel-Mesh), VkBake (Komponente ins Prefab), VkImport (Events
      hit/slam → AnimationEvents „VKStoss“), VkSpec (Standards + Migration), VkDoc/vk_json (Migration), Blender `weichheit`,
      Fenster (Weichheit Lagen/Accessoires, `auf`/`stelle`, Vorschau mit Federn), Presets/Varianten: `bewegung`/`schwingen` entfernt,
      Gehänge in feucht/kueste → `unten`. C13: Schalter im Dangling-Shader + `VkDangleSwing.cs` (creature.toml-Flag).
- [x] Batch `VariantKit.VkSwingBatch.Run` (temp/g14_work/run_g14.sh) läuft: Testvariante temp/g14_work/g14_mossback_test.variant.json.
- [x] Feinabstimmung (Trägheit 1,5 · Fahrtwind 0,15 · Max 0,8 weich), Clip-Events-Fix (Clip-Namen „Basis|Take“), UV1 im
      Spiel-Mesh immer schreiben (fehlender Kanal = Zufallswerte → Slagback „explodierte“ mit Block).
- [x] GIFs `temp/g14_shots_final/*.gif` (+ Slagback/Cragplate), Übersicht `temp/g14_shots_final/G14_uebersicht.png`,
      C13 `temp/g14_c13/BogWarden_*.gif`. Kosten 3,5 µs/Gegner. Regression: Slagback/Cragplate pixelgleich zu M2,
      CreatureImporter-Gegenprobe identisch (Kopie gelöscht, Log `temp/g14_work/importer_check.log`).
- [x] Doku `VARIANTEN_BAUKASTEN.md` Teil E, `VARIANTEN_SPEC.md` 2.2/2.4/3.3 (weichheit statt schwingen/bewegung).
**Hinweise:** Batch `temp/g14_work/run_g14.sh <log> VariantKit.VkSwingBatch.Run …`, GIFs `python temp/g14_work/make_gifs.py <ordner>`.
C13 im echten Projekt: beim nächsten Öffnen importiert der CreatureImporter den Bog Warden, `VkDangleSwing` schaltet ein.
