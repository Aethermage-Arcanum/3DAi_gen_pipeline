# Bewegungsmuster multileg/scorpion

Generator `scorpion_clips.py`, Werte `style.toml`. Erstes Modell: **Scorpion Matriarch** (2026-11-17), alle 9 Clips grün.

| Clip | Inhalt |
|---|---|
| Multileg_Scorpion_Walk / Run | alternierende Beingruppen (L1 R2 L3 R4 L5 gegen R1 L2 R3 L4 R5) mit kleiner Welle vorn → hinten, Scheren leicht erhoben, Schwanz pendelt |
| Multileg_Scorpion_TurnLeft/Right | auf der Stelle drehen |
| Multileg_Scorpion_Idle | Scheren öffnen/schließen abwechselnd, Schwanz pendelt |
| Multileg_Scorpion_Ready | Drohen: Körper hoch, Scheren gespreizt + erhoben, Schwanz gespannt über dem Rücken, Zittern |
| Multileg_Scorpion_Attack1 | Scheren packen zu, Stachel schnellt über den Kopf nach vorn (Event `hit` Frame 12) |
| Multileg_Scorpion_Hit | Ruck zurück |
| Multileg_Scorpion_Death | kippt auf den Rücken (Krabbler-Tod), Beine in der Luft, liegt am Boden |

## Naturreferenzen / Videos
„scorpion walking slow motion“ (Beinwechsel), „scorpion defensive posture“ (Scheren + Schwanz), „scorpion sting strike slow motion“.
Gangmuster wie bei Spinnentieren: alternierende Vierergruppen mit metachroner Welle (vgl. Ant/Spider-Variante im Crawler-Muster).

## Erkenntnisse
- Tripo erzeugte **5 statt 4 Beinpaare** (Fake it: Skelett nimmt beliebig viele). Das 5. Paar sitzt am Schwanzansatz und war mit Hüfte/Schwanz verschmolzen → Haupt-Ursache der Rest-Dehnung (Grenzen pro Clip mit Begründung in style.toml).
- Stich-Stärke: Krümmung entlang des Schwanzes + nur wenig Kippen an der Wurzel (Wurzel zieht am 5. Beinpaar).
