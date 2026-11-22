# Varianten-Baukasten M1 – Arbeitsstand (WIP, Build-Agent)

Notizbuch für den Fall, dass das Token-Limit zuschlägt. Die Nutzer-Anleitung + Entwickler-Notiz steht in `VARIANTEN_BAUKASTEN.md`.

## Stand 2026-11-22: M1 fertig, nicht committet (Zwischenstand Commit 8eaf196)
- [x] Bausteine per Blender: `procedural/bausteine/make_bausteine.py` → `<typ>.fbx/.glb/.json` (basaltbrocken, steinplatte, felszacke, je 3 Formen, 14–40 Tris)
- [x] Zonen-Definition `rigging/quadruped_zonen.json`
- [x] Presets `templates/umgebungs_gruppen/lebensfeindlich.json` (H), `stein.json` (D)
- [x] Unity `Assets/Editor/VariantKit/*.cs` + `Assets/VariantKit/` (Shader, VariantStatur), eigene asmdefs
- [x] Varianten `creatures/32_rimehide_bear/varianten/slagback_bear|cragplate_bear.variant.json` (+ `.instanzen.json`), gebacken
- [x] Batch-Selbstprüfung `VariantKit.VkBatch.Run`, Bilder `temp/vk_shots/` (`*_vergleich.png`, `*_bewegung.png`)
- [x] Gegenprobe CreatureImporter in einer Projekt-Kopie: 14 Kreaturen, alle Clips bewegen sich, Bodenwerte identisch
- [x] Doku `docs/VARIANTEN_BAUKASTEN.md`

## Hinweise für die nächste Session
- Batch immer mit **Unity 6000.3.28f1** (Version des Projekts). Ein Lauf mit 15f1 hatte `ProjectVersion.txt` umgeschrieben
  (zurückgesetzt). Hilfsskript: `temp/vk_work/run_batch.sh`.
- Statur-Testvariante (starke Werte): `temp/vk_statur/statur_test.variant.json` (`-vkVariants <pfad>`).
- Sitz der Accessoires in Bewegung: ±2–5 cm an Buckel/Rücken/Unterarm (große, stark gebogene Dreiecke). Kandidaten für M2:
  feinere Haut unter den Andock-Zonen oder Bindung `haut` für große Platten.
