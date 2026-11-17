# Void Manifestation (Monstrosities · Abyss) – floater/tentacle

Erster Schweber. Erstellt 2026-11-17 im autonomen Lauf.

```
python scripts/tripo_run.py creatures/void_manifestation --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/void_manifestation             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | 4.022 |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 74 = Root + Core + 21 Tentakel-Ketten ab der echten Wurzel (automatisch erkannt; bis 2026-11-17: 46 / 19 Ketten) |
| UV | Tripo-UV (149 Inseln, 59 %, 0 % Überlappung) |
| Clips | 9, alle grün (Dehnung max. ~1,7, schwebt immer, Tod liegt am Boden) |

**2026-11-17 – Tentakel bis zur Wurzel wabbelig** (Nutzer-Meldung „nur die unteren Enden bewegen sich“): Ursache war das Rig –
die oberen 30–60 % jedes Tentakels lagen in der Kernkugel und hingen starr am Kern. Jetzt Wurzel-Verlängerung im Rig +
Wellen/Nachschwingen über die ganze Kette (Details: `motions/floater/tentacle/README.md`). Death unverändert.

Hinweis: Tripo lieferte das Modell nach −Y schauend → `[floater] facing = "-y"` in creature.toml. Das Auge-Leuchten kommt später als Emission/Shader (nicht in der Textur).
