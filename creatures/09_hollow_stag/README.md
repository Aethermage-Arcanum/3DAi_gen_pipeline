# Hollow Stag (Mammals · Highlands) – quadruped/deer

Erstellt 2026-11-17 im autonomen Lauf.

```
python scripts/tripo_run.py creatures/09_hollow_stag --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/09_hollow_stag             # kostenlos
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

**2026-11-17 – Nutzer-Feedback aus Unity behoben** (Optionen in `creature.toml [quadruped.rig]`):
- Vorderknie knickten nach innen: Die Vorderbeine stehen so eng, dass sie im Bauch-Messstreifen lagen → Beine als Bauch gelesen, alle Vordergelenke ~15 cm zu tief. Fix `adaptive_belly_strip`.
- Hinterbeine 2,4× so breit wie vorne (schon im Tripo-Modell, Ursache Referenzbild): Mesh-Korrektur `narrow_hind_legs = 0.8` (Hufe ±14,6 → ±7,7 cm, vorne ±6 cm).
- Geweih wackelte (hing am Hals-Knochen): `rigid_head_above` → Geweih starr am Kopf.
- Offen: Der alte Death-Clip hat jetzt 2,5 cm Lücke Hinterbein/Schwanzansatz (Grenze 1,5) – Death wird ohnehin neu gemacht. Alle anderen Clips ≤ 0,7 cm.
