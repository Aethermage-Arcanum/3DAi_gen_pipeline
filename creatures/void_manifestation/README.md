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
| Knochen | Root + Core + 19 Tentakel-Ketten (automatisch erkannt) |
| UV | Tripo-UV (149 Inseln, 59 %, 0 % Überlappung) |
| Clips | 9, alle grün (Dehnung max. ~1,7, schwebt immer, Tod liegt am Boden) |

Hinweis: Tripo lieferte das Modell nach −Y schauend → `[floater] facing = "-y"` in creature.toml. Das Auge-Leuchten kommt später als Emission/Shader (nicht in der Textur).
