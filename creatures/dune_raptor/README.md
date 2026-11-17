# Dune Raptor (Beasts · Wüste) – biped_raptor/raptor

Erster Zweibeiner. Erstellt 2026-11-17 im autonomen Lauf. Version ohne Flügel (Elite-Variante mit Flügeln später).

```
python scripts/tripo_run.py creatures/dune_raptor --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/dune_raptor             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | ca. 4.180 (Tripo 4.294; entfernt: 45 Flächen Hautbrücke zwischen den Beinen + 65 Flächen Bauch-Lappen) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 26 (inkl. Arme, Kiefer, 4 Schwanzglieder) |
| UV | Tripo-UV (176 Inseln, 61 %, 0 % Überlappung) |
| Clips | 9, alle grün; Lücken max. 1,3 cm (Standardgrenze 1,5 cm) |

Hinweis: Die Referenzbilder vorn/hinten zeigten ihn aufrecht, seitlich waagerecht – Tripo hat sich an den Seiten orientiert, Ergebnis ist sauber.

**2026-11-17 – „zweiter Schwanz“ (vom Nutzer in Unity entdeckt):** Das Frontbild zeigte den Raptor aufrecht mit dem Schwanz zwischen den Beinen. Tripo hat daraus einen Hautstreifen unter dem Bauch gebaut, der an den Schienbeinen hing und mitschwang. Behoben im Rig (`[biped_raptor] cut_belly_flap = true`, löscht das schmale Band an der Mittellinie hinter der Hüfte unterhalb der Bauchlinie). Lehre für neue Referenzbilder: Front/Back in derselben (waagerechten) Haltung wie die Seiten, Schwanz nicht zwischen den Beinen.
