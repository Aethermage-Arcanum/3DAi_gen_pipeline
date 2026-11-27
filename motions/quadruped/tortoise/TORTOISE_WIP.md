# Arbeitsstand Shellback / quadruped/tortoise (WIP, Bau-Agent)

Stand 2026-11-27 – falls das Limit zuschlägt, hier weitermachen.

## Erledigt
- Teil B Tripo-Modell: bestanden (temp/sh_inspect/, review/model_check.png). 4.344 Tris, 1 Material, 3 Teile (Hauptkörper + 2 kleine
  Teile, 34 Vertices = Augen), Symmetrie exakt, 4 Füße, keine Hautbrücken. Kein schwerer Mangel.
- Ausgangsstand VOR der Rig-Änderung: temp/sh_base/{02_ravine_stalker,08_reef_snapper,09_hollow_stag,32_rimehide_bear}/rig/fingerprint.json.gz (vollständig, 2026-11-23 09:35).
- rigging/quadruped_rig.py: neue opt-in-Optionen `rigid_shell` (+ shell_*), `knee_out`. Ohne Werte unverändert (Regression steht noch aus!).
- creature.toml Shellback: [quadruped.rig] mit rigid_shell, knee_out.
- motions/quadruped/tortoise/style.toml + tortoise_clips.py (alle 10 Clips backen, Drehrichtung gemessen ok).
- Prüfwerkzeuge (nur temp): temp/sh_scripts/weights_view.py + combine.py (Gewichte als Farben), vis_summary.py, lowshell.py.

## Messungen (temp/sh_c2, Rig temp/sh_rig2, shell_leg_radius 0.22)
- Panzer (Rücken/Flanke) sichtbar max 1,00 in allen Clips = 100 % starr.
- Dehnung sichtbar: Hals bis 4,6 (Attack1), Schulter/Oberschenkel bis 6,8 (Attack2), Unterbein bis 6,8 – alles an KURZEN Kanten
  (0,5–0,9 cm) am Rand des 2-Ring-Übergangs. → Plan: Übergang nach Abstand (Meter) statt Kanten-Ringen.
- 3 Panzer-Vertices fast am Boden bei x −0,29, y −0,13 (nur rechts?) → prüfen.

## Stand 2026-11-27 (später)
- Übergang nach Abstand (shell_blend_width 0.12), shell_min_height, shell_neck_free(+_width) eingebaut → sichtbare Dehnung
  Walk/Turn/Run ≤ 1,8, Attack1 Hals 2,1 / Kehle 2,7 (Rest), Panzer 1,00.
- --stage motion gelaufen, Kontaktbögen rig/anim/raw/*_bogen.png (Walk, Run, TurnLeft, Attack1, Attack2) angesehen: ok.
- Regression --deep gegen temp/sh_base: Wolf, Reef Snapper, Hirsch, Bär identisch.

- Halsöffnung weich auslaufend (shell_neck_free_soft) → Lückenprüfung 5,8 → 0,9 cm. Regression erneut identisch.
- --stage full: ✓ ALLES OK. READMEs (Muster, Kreatur), rigging/README.md, quadruped_defaults.toml ergänzt.

## Offen
- Abnahme durch den Nutzer (Roh-GIFs + Kontaktbögen rig/anim/raw/). Nicht committet (Zwischenstand b6f2c7b stammt nicht vom Agenten).
