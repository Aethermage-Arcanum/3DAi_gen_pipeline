# Hollow Stag (Mammals · Highlands) – quadruped/deer

Erstellt 2026-11-17 im autonomen Lauf.

```
python scripts/tripo_run.py creatures/hollow_stag --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/hollow_stag             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | ca. 4.300 (Tripo, aber 6.445 Vertices durch viele UV-Nähte) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 30 (Vierbeiner-Standard) |
| UV | Tripo-UV (1.146 Inseln – sehr zerstückelt, aber besser als Smart UV) |
| Clips | 9, alle grün; Lücken max. 0,5 cm |

Geweihstoß: Kopf tief, Nase runter (Geweih zeigt nach vorn), Vorschnellen. Dehnungs-Grenzen pro Clip mit Begründung in `motions/quadruped/deer/style.toml`.
Versuche mit exklusiven Beinpaaren / Brücken-Schnitt haben beim Hirsch die Dehnung nur verschoben → nicht aktiv.
