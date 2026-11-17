# Bewegungsmuster crawler/ant

Ameisen-/Insekten-Bewegung für das Krabbler-Skelett. Varianten (nur Variablen, siehe `style.toml`): **spider** (8 Laufbeine → alternierender Vierfuß), **beetle** (schwer, langsam).

Generator: `ant_clips.py` backt alle Clips auf ein gerigtes Modell und prüft jeden einzeln. Aufruf über `scripts/crawler_pipeline.py`.

## Clips (MVP) – Stand 2026-11-17, geprüft am Chitin Crawler
| Clip | Dauer | Loop | Inhalt | Selbstprüfung |
|---|---|---|---|---|
| Crawler_Ant_Walk | 0,67 s | ✓ | Dreifuß-Gang, Taster tasten, Rumpf wiegt | Bodenkontakt ≤ 6 mm, gleiche Schrittlänge, 0,28 m/s |
| Crawler_Ant_Run | 0,30 s | ✓ | gleicher Gang, schneller, längere Schritte | Bodenkontakt, 0,65 m/s |
| Crawler_Ant_TurnLeft/Right | 0,67 s | ✓ | eine Seite schiebt vor, andere zurück | Bodenkontakt, 34 °/s |
| Crawler_Ant_Idle | 2,0 s | ✓ | Hinterleib atmet, Kopf schaut, Fühler tasten | Füße stehen (≤ 5 mm) |
| Crawler_Ant_Ready | 1,0 s | ✓ | Drohhaltung: Kopf hoch, Hinterleib hoch, Taster erhoben, Zittern | Füße stehen |
| Crawler_Ant_Attack1 | 0,8 s | – | Biss: Ausholen (Telegraph) → Vorschnellen → zurück, Event `hit` @ Frame 12 | Füße stehen |
| Crawler_Ant_Hit | 0,27 s | – | Zurückzucken, kehrt exakt zur Ruhe zurück (additiv nutzbar) | Füße stehen, Rückkehr zur Ruhe |
| Crawler_Ant_Death | 1,2 s | – | Zucken → auf den Rücken kippen (Root-Drehung) → Beine einrollen → letztes Zucken | kein Teil im Boden |

Alle Clips zusätzlich: keine Gelenk-Lücke > 1,5 cm (`check_gaps.py`), Schleifen nahtlos für alle 43 Knochen.

## Naturreferenzen
- **Gang:** Ameisen-Dreifuß (vorne + hinten einer Seite mit der Mitte der anderen), Tempo über Schrittlänge + Frequenz:
  [J Exp Biol 1994](https://cob.silverchair.com/jeb/article-pdf/192/1/95/2854548/jexbio_192_1_95.pdf) · [Desert ants 2015](https://link.springer.com/article/10.1007/s00359-015-0999-2) · [ScienceDaily](https://sciencedaily.com/releases/2014/07/140701193249.htm)
- **Ready / Drohen:** Mandibeln öffnen als erstes Aggressionssignal, Hinterleib heben („gaster flagging“) als Warnhaltung:
  [AntWiki – Alarm Communication](https://antwiki.org/wiki/Alarm_Communication) · [Mandible opening response](https://ouci.dntb.gov.ua/works/4VLzwgW9) · [Ant Insights – Crematogaster](https://antinsights.substack.com/p/ant-spotlight-crematogaster-cerasi)
- **Death:** totes Insekt auf dem Rücken, Beine eingerollt. Das ist allgemeines Wissen: Ohne Muskel- bzw. Hydraulikspannung krümmen sich die Beine ein (bei Spinnen werden die Beine hydraulisch gestreckt).

## Erkenntnisse beim Bauen
- **Der Thorax trägt die Beine** (FK). Jede Thorax-Drehung oder -Verschiebung bewegt die Füße mit → in Stand-Clips max. ~1° drehen, sonst rutschen die Füße.
- **Eng anliegende Beinansätze** (beim Chitin Crawler L2/L3) begrenzen, wie weit Oberschenkel sich heben dürfen → Bewegung lieber über Unterschenkel und Hüftschwenk.
- **Große Ganzkörper-Bewegungen über den Root-Knochen** (z. B. Umkippen) erzeugen keine Lücken, weil sich alles gemeinsam bewegt.
- **Boden-Begrenzung:** `fold_ground_clamped` hebt das Knie automatisch, bis das Bein-Mesh auf dem Boden aufliegt. Für Fühler wird der Klappwinkel automatisch so gesucht, dass sie nicht im Boden stecken.
- Ready und Attack mussten für die Top-down-Kamera deutlich übertrieben werden, sonst sind sie nicht lesbar.

## Offen
- Mandibeln haben beim Chitin Crawler kein eigenes Mesh-Teil (Teil des Kopfes) → Mandibel-Knochen ohne Wirkung.
- Prio-2-Clips: Attack2 (Stich/Säure), HitHeavy, Knockdown + Strampeln + GetUp, Dodge, Spawn, Stun
- Nicht in Unity getestet.
