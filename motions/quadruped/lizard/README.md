# Bewegungsmuster quadruped/lizard (Echse/Waran)

Generator: `lizard_clips.py` (eigener Code, nutzt `../quadruped_kit.py`), Werte `style.toml`. Erstes Modell: **Reef Snapper** (2026-11-17).

## Was dieses Muster ausmacht
- **Gang = Diagonal-Trab mit stehender S-Welle**: Schulter- und Beckengürtel gieren gegenläufig, die Krümmung ist am größten, wenn ein Vorderbein aufsetzt; der Schwanz setzt die Welle verzögert fort. Kopf bleibt ruhiger als die Schultern.
- **Run = schneller Trab** (Warane rennen im Trab, nicht im Galopp) mit größerer Welle (vorher: kopierter Wolfsgalopp).
- **Ready = Drohgebärde**: Rumpf seitlich gebogen (Profil zeigen), Hals hoch, Maul weit auf, Fauch-Stöße mit kleinem Schein-Vorstoß, Schwanz zur Seite gespannt und peitschend.
- **Attack1 = Schnappbiss**: Kopf + Hals holen zur Seite aus, Körper schnellt vor, Kopf schwingt von der Seite zur Mitte, zuschnappen (Event `hit` Frame 14), dann zurückreißen (Komodo „slashing bite“), Schwanz schwingt gegen.
- Death unverändert (Nutzer-Anweisung).

## Naturreferenzen
- Ritter 1992, *Lateral bending during lizard locomotion*, J Exp Biol 173:1 – stehende Welle bei langsamem Tempo, laufende Welle bei schnellem: [jeb.173.1.1 (PDF)](https://cob.silverchair.com/jeb/article-pdf/173/1/1/3285742/jexbio_173_1_1.pdf)
- Savannenwaran + Teju per Röntgen-Bewegungsanalyse (XROMM), *Sci Rep* 2020: Vorderfuß setzt etwa bei maximaler seitlicher Krümmung auf – [s41598-020-64140-y](https://www.nature.com/articles/s41598-020-64140-y)
- Ritter 1996 (Varanus salvator, Epaxialmuskeln): [J Exp Biol 198:2477](https://cob.silverchair.com/jeb/article/198/12/2477/7086/Epaxial-muscle-function-during-locomotion-in-a)
- Komodo-Biss (Kopf dreht beim Biss von seitlich zur Mitte und zieht nach hinten): D'Amore et al. 2011 – [PMC3197624](https://pmc.ncbi.nlm.nih.gov/articles/PMC3197624); Schlaggeschwindigkeit Varanus ≈ 1 m/s: [Whitford et al. 2022 (PDF)](https://biomechanics.ucr.edu/Whitford%20et%20al%202022%20BJLS.pdf)
- Videos (Stock-Vorschau): [Komodowaran geht (Storyblocks)](https://www.storyblocks.com/video/stock/komodo-dragon-walks-by-4k-a3v0u02) · [Komodowaran geht, Zeitlupe (iStock)](https://www.istockphoto.com/dk/videos/komodo-dragon) · Suchbegriffe „komodo dragon walking slow motion“, „monitor lizard threat display hiss“, „crocodile high walk“.

## Abgeleitete Werte (2026-11-17)
| Wert | vorher | jetzt | Herleitung |
|---|---|---|---|
| Rumpfwelle | `spine_side 10°` gleich auf 3 Wirbel → Körper drehte als Block um die Hüfte | Schulter ±9°, Becken ±8° gegenläufig, Welle läuft 5 % nach hinten | Ritter 1992, XROMM 2020 (Krümmung max. beim Aufsetzen vorn) |
| Schwanz | eigene Welle 14° | `follow` der Beckendrehung, 8 % Verzögerung/Glied, ×1,3 | Welle setzt sich in den Schwanz fort |
| Run | Wolfsgalopp (Kopie) | Trab 18 Frames, Welle ±13°/±12° | Warane rennen im Trab |
| Fußbahn/Rumpfhöhe | wie Wolf (Ruck, Knicke) | `gait_smooth`, `reach_smooth` | siehe wolf/README |
| Ready | Maul 13° (wegen Mundwinkel-Dehnung verkleinert), Kopf leicht hoch, sonst starr | Maul 34° + 10° Fauchen, Hals 26° hoch, Rumpfbogen ±22°, Schwanz peitscht 18°, Schein-Vorstoß 2,5 % | Waran-Drohgebärde; Dehnung nur Info |
| Attack1 | Kopf dreht 18° nur am Kopf, Vorstoß 8 % | Kopf + Hals + Rumpf schwingen 32° von der Seite zur Mitte, Vorstoß 12 %, Zurückreißen, Schwanz gegen | Komodo-Biss |

## Offen
- Ready/Attack sind aus der ARPG-Kamera jetzt deutlich größer; ob es „bedrohlich genug“ ist, muss der Nutzer in Unity beurteilen.

## Bodenkontakt
Vorher bis −1,9 cm (Attack1, Unterarm/Sohle unter dem Boden). Jetzt `feet_on_ground` (siehe wolf/README) → alle Clips außer Death ≤ 2 mm. Death unverändert (−1,5 cm).
