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
