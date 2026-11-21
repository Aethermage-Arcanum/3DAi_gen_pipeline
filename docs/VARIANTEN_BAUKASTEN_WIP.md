# Varianten-Baukasten M1 – Arbeitsstand (WIP, Build-Agent)

Nur Notizbuch für den Fall, dass das Token-Limit zuschlägt. Die Nutzer-Anleitung steht in `VARIANTEN_BAUKASTEN.md`.

## Plan / Stand
- [ ] Bausteine per Blender: `procedural/bausteine/make_bausteine.py` → `<typ>.fbx/.glb/.json` (basaltbrocken, steinplatte, felszacke)
- [ ] Zonen-Definition `rigging/quadruped_zonen.json` (Unity rechnet die Zonen in M1 aus Gewichten + Lage)
- [ ] Presets `templates/umgebungs_gruppen/lebensfeindlich.json`, `stein.json`
- [ ] Unity: `Assets/Editor/VariantKit/*.cs` (Fenster, JSON, Platzierung, Builder, Backen, Batch), `Assets/VariantKit/` (Shader, Statur-Komponente)
- [ ] Varianten `creatures/32_rimehide_bear/varianten/slagback_bear.variant.json`, `cragplate_bear.variant.json`
- [ ] Batch-Selbstprüfung, Bilder `temp/vk_shots/`
- [ ] Gegenprobe CreatureImporter (Kopie unter `temp/vk_unitycopy`)
- [ ] Doku `docs/VARIANTEN_BAUKASTEN.md`

## Entscheidungen (Abweichungen von der Spec, begründet)
- JSON mit eigenem kleinem Parser/Schreiber in C# (kein Newtonsoft-Paket nötig, feste Feldreihenfolge, 3 Nachkommastellen).
- Zonen rechnet in M1 Unity (C#) aus Skin-Gewichten + Lage entlang der Wirbelsäule + Flächenrichtung; Definition als JSON statt TOML.
- Statur-S-Regler (Shape Keys) werden in M1 direkt beim Zusammenbau ins Mesh gerechnet (kein Blendshape nötig), K-Regler über
  Knochen-Skalierung mit Ausgleich am Kind (Komponente `VariantStatur`, LateUpdate) – auch im gebackenen Prefab.
- Material-Ebenen bleiben in M1 Shader-Parameter (Masken pro Vertex aus C#), kein Textur-Backen.
- Bausteine: zusätzlich zu FBX/GLB liegen die Meshes im `<typ>.json` (achsen-eindeutig), Unity liest das JSON.
