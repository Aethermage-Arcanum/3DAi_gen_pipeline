# Eel Stalker (Vertebrates · Küste) – legless/cobra

Erstes beinloses Modell. Erstellt 2026-11-17 im autonomen Lauf.

```
python scripts/tripo_run.py creatures/eel_stalker --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/eel_stalker             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 3.998 |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 17 (Root, 14 Wirbel, Kopf, Kiefer) |
| UV | Tripo-UV (163 Inseln, 57 % Abdeckung, 0 % Überlappung) – per Sichtprüfung statt Smart UV festgelegt |
| Clips | 9, alle grün (Dehnung max. 1,78, Bodenkontakt exakt, keine Lücken) |

Hinweis: Vorder-/Rückansicht der Referenzbilder waren nicht ganz stimmig (aufrecht vs. liegend). Tripo hat trotzdem einen sauberen Körper gebaut.
