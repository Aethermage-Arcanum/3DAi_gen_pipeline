# Sandwurm – Arbeitsstand (Build-Agent, 2026-11-27)

Arbeitsdateien nur in `temp/sw_*` (Ausgangsstand Eel Stalker: `temp/sw_base/03_eel_stalker/`, Skripte: `temp/sw_scripts/`,
Testbauten: `temp/sw_work/`). Nichts committet.

## Erledigt
- Prüfung Teil B (Sichtprüfung `review/model_check.png`, `temp/sw_inspect/view_*.png`, Raster-Ansichten
  `temp/sw_inspect/grid_all.png`): bestanden, keine schweren Mängel. Bekannt: Bauchstacheln wie Stummelbeine, Maul offen.
- Ausgangsstand Eel Stalker gebaut (`temp/sw_base/03_eel_stalker/rig/fingerprint.json.gz`).
- Rig-Erweiterungen opt-in in `rigging/legless_rig.py` (joints, axial_weights/axial_blend, rigid_spikes,
  ground_ignore_spikes, ring_bones), Kreatur-Werte in `creatures/12_sand_leviathan/creature.toml` `[legless]`.
- Baukasten opt-in in `motions/legless/legless_kit.py` (`_NO_GROUND`, `key_scale`, `render_ground`, `below_ground`).
- `rigging/render_anim.py`: opt-in Boden auf `scene["ground_z"]`. `rigging/joint_densify_review.py`: Spine_NN/Ring_NN = Rumpf.
- Muster `motions/legless/sandworm/` (style.toml, sandworm_clips.py), 12 Clips.
- Dehnung: Panzer 4 Wirbel statt 3, breitere Übergänge zwischen Platten, Kopf-Knick auf 3 Wirbel verteilt,
  Loch-Biegung bei Burrow/Emerge unter den Boden gelegt → sichtbare Flächen max ≈ 2,0 (Turn-Flanke 2,3 an 3–5 Kanten).

- Kontaktbögen (Roh-GIFs) angesehen: `creatures/12_sand_leviathan/rig/anim/raw/sheet_*.png`; Emerge-Kopf (Maul zum Himmel)
  und Startlage (ganz unter dem Boden) sowie höherer Body Slam nachgebessert.
- Regression: Eel Stalker identisch (`temp/regression/20261127_113606`).
- `--stage motion` + `--stage full` in der Kreatur: ALLES OK, Export `creatures/12_sand_leviathan/output/`.
- READMEs: Muster, Kreatur (Kennzahlen, Messwerte), `motions/legless/README.md` (Opt-in-Erweiterungen).

## Offen
- Nutzer-Abnahme der Bewegung; Naturvideos gegenprüfen.
- Turn: 3–5 Kanten an der Bauchlinie am Panzerende bis 2,3 (Rücken ≤ 1,8). Emerge Rücken 2,0 an der Loch-Biegung.
- Burrow: sichtbarer Eintritt liegt ≈ 0,15 L vor dem nominellen Eintrittspunkt und wandert ≈ 7 cm zurück (Bauch taucht früher ab).
- Death nur Platzhalter (gesperrt). Nichts committet.
