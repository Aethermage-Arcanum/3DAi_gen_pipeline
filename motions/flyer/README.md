# Skelett flyer (fliegende Insekten/Kreaturen)

Rig: `rigging/flyer_rig.py` (= Schwebe-Rig `floater_rig.py`: Kern + automatisch erkannte Ketten; Werte `floater_defaults.toml`, pro Kreatur `[floater]`).
Baukasten: `motions/floater/floater_kit.py`. Muster: `wasp/`. Ein Befehl: `python scripts/creature_pipeline.py creatures/<name>`.

Die Ketten werden im Muster nach **Lage** zugeordnet: Hinterleib = am weitesten hinten · Beine = Spitze deutlich unter dem Kern ·
Fühler = vorn · Flügel = Rest (seitlich). Tripo zerlegt Flügel gern in mehrere Stücke – die schlagen gemeinsam.
Flügelschlag stark verlangsamt (4 Frames pro Schlag), die Unschärfe echter Insektenflügel kommt später per Shader („Fake it“).
