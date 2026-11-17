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

Schwebeflug (Links 2026-11-17 gesammelt, Inhalt laut Quellenbeschreibung):
- Hornissen im Zeitlupen-Flug: https://thekidshouldseethis.com/post/hornet-flights-in-slow-motion
- Hornissen-Manöver an einer Futterstelle, 250–500 fps: https://www.dailymotion.com/video/x8d0egz
- Hornissen „stehen“ vor dem Flugloch eines Bienenstocks (Zeitlupe, NFB-Archiv): https://archives.nfb.ca/stockshot/50692/
- Asiatische Hornisse „hawking“ vor dem Bienenstock: https://www.eurekalert.org/multimedia/732906

Was wir daraus nehmen: Beim Schweben/Jagen steht die Wespe ruhig in der Luft, Beine hängen locker, Hinterleib leicht
nach unten; den Boden berührt sie **nie** – nur zum Landen streckt sie die Beine aus. Deshalb:
- `[hover] height = 0.18` (Wespe 1 m → Kern 18 cm höher als in der Tripo-Ruhepose; die hängenden Beine bleiben im
  Vorwärtsflug ≥ 11 cm über dem Boden – nah genug, um im ARPG Gegner am Boden zu stechen).
- `[hover] min_clearance = 0.03`: kein Mesh-Punkt kommt im Flug (alle Clips außer Death) näher als 3 cm an den Boden.
  Vorher schleifte der eingekrümmte Stachel in Ready (jeder Frame), Attack1 (Ausholen, Frame 7–10) und Hit (Frame 2–3)
  genau auf dem Boden. Selbstprüfung `clearance_ok` im Clip-Bericht.

## Bodenreferenz (2026-11-17, Meldung „Wespe sinkt 3,7 cm in den Boden“)
Boden = Unterkante der **Tripo-Ruhepose** (Bindepose: Beine hängen nach unten = „gelandet“). Das ist dieselbe Referenz
wie bei allen Skeletten (`GROUND` in jedem Baukasten). Der Unity-Viewer stellte dagegen die Pose auf den Boden, die
Unity nach dem Instantiieren zeigt – das ist der **erste Take im FBX (Attack1, Frame 0)** und bei der Wespe schon die
Schwebehöhe (+17,6 cm). Gemessen zur Ruhepose fliegt Walk 13,9–18,5 cm hoch, zur Schwebepose −3,7…+0,9 cm → daher
die „3,7 cm im Boden“. Viewer misst jetzt die Bindepose (`CreatureViewer.RestLowestPoint`); für laufende Kreaturen sind
beide Posen identisch (±0,0 cm), nur Flieger/Schweber (Wespe, Void) ändern sich.
