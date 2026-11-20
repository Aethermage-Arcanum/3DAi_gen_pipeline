# Reef Snapper (Vertebrates · Küste) – quadruped/lizard

Erstellt 2026-11-17 im autonomen Lauf.

```
python scripts/tripo_run.py creatures/08_reef_snapper --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/08_reef_snapper             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | ca. 4.200 (12 Brückenflächen zwischen den Vorderfüßen entfernt) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 30 (Vierbeiner-Standard) |
| UV | Tripo-UV (94 Inseln, 62 %, 0 % Überlappung) |
| Clips | 9, alle grün; Lücken max. 0,9 cm |

Besonderheiten (creature.toml `[quadruped.rig]`): Rückenkamm → `spine_top_pct = 65`; Vorderfüße unter der Brust verschmolzen → `cut_leg_bridges` + `exclusive_leg_pairs`.
