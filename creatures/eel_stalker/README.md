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
| Clips | 9, alle grün (Bodenkontakt exakt, keine Lücken, Schleifen nahtlos; Dehnung nur Info, max. 3,4 an Hals-Stachelansätzen) |

Hinweis: Vorder-/Rückansicht der Referenzbilder waren nicht ganz stimmig (aufrecht vs. liegend). Tripo hat trotzdem einen sauberen Körper gebaut.

## Umbau Bewegung 2026-11-17 (Nutzer-Feedback Unity)
Befund: Das Tripo-Modell ist in Ruhe fest verbogen – Draufsicht S-Kurve (Wirbel-Gieren −44° … +45°), Vorderkörper
bis +54° aufgerichtet (Kopfansatz 23 cm hoch), Bauch wellt sich 0–9 cm über dem Boden (Schwanzspitze schwebt),
Kopf −26° geneigt. Die alten Clips addierten nur auf diese Form → Körper wirkte eingefroren, Kopf starr.
Jetzt geben alle Clips außer Death die Körperform **absolut** vor (`legless_kit.shape`), Details und Naturreferenzen
in `motions/legless/cobra/README.md`. Vorher/Nachher-Kontaktblätter: `temp/review/eel_<clip>.png` (nicht versioniert).
Offen: Kopf-Hautlappen sollen nachschwingen (eigener Baustein „frei hängende Teile“ geplant); Death unverändert (alt).
