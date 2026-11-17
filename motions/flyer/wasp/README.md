# Bewegungsmuster flyer/wasp

Generator `wasp_clips.py`, Werte `style.toml`. Erstes Modell: **Needle Wasp** (2026-11-17), alle 9 Clips grün (Dehnung ≤ 1,28).

| Clip | Inhalt |
|---|---|
| Flyer_Wasp_Walk / Run | Vorwärtsflug: nach vorn geneigt, Flügelschlag, Beine schleppen nach, Hinterleib pumpt |
| Flyer_Wasp_TurnLeft/Right | Kurvenlage |
| Flyer_Wasp_Idle | Schwebeflug, Hinterleib pumpt, Fühler tasten |
| Flyer_Wasp_Ready | Hinterleib unter den Körper gekrümmt, Stachel nach unten/vorn |
| Flyer_Wasp_Attack1 | hochziehen → Sturzflug nach vorn-unten, Hinterleib schnellt vor (Event `hit` Frame 12) |
| Flyer_Wasp_Hit | wird zurückgeschleudert, Flügel stocken |
| Flyer_Wasp_Death | Flügel stoppen, trudelt ab, landet auf dem Rücken |

## Naturreferenzen / Videos
„wasp hovering slow motion“, „hornet sting slow motion“, „wasp flight high speed camera“. Echte Wespen schlagen ~200×/s –
im Spiel unsichtbar, deshalb verlangsamter Schlag + Bewegungsunschärfe per Shader.
