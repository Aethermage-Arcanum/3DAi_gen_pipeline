# Bewegungsmuster quadruped/bear (Bär)

Generator: `bear_clips.py` (eigener Code, nutzt `../quadruped_kit.py` nur lesend), Werte `style.toml`.
Erstes Modell: **Rimehide Bear** (`creatures/32_rimehide_bear/`, 2026-11-21) – die nackte Basis aller Bären-Varianten
(Eisriese, Mossback, Höhlenbär, Slagback, Cragplate, evtl. Quillback). Alle Varianten teilen Rig und Clips.
Andere Vierbeiner-Muster (wolf, deer, lizard …) bleiben unverändert – der Bär hat keine Zeile in ihrem Code geändert.

## Clips (Präfix `Quadruped_Bear_`)
| Clip | Dauer | Inhalt | Naturvorbild |
|---|---|---|---|
| Walk | 1,33 s, Loop | lateraler Viertakt, **Passgang-artig** (Vorderbein setzt 0,14 Zyklus nach dem gleichseitigen Hinterbein auf), immer 3 Füße am Boden; Schultergürtel rollt (7°) und giert (6°) deutlich stärker als das Becken → Buckel schaukelt; Rumpf schwankt zum Standbein; **Kopf tief**, pendelt 1× pro Zyklus seitlich (9°), verzögert gegen die Schultern; Pranken flach geschwungen, Sohle setzt ganz auf | Grizzly-Schritt (Shine 2016), „bear walking slow motion“ |
| Run | 0,67 s, Loop | schwerer Galopp (rotierend HL → HR → VR → VL), eine gesammelte Schwebe; Rücken rund beim Aufsetzen hinten (Kruppe hebt sich), Buckel schaukelt 7°, Körper rollt 3°; Kopf bleibt tief und ruhig | Grizzly-Angriff/-Sprint (Videos unten) |
| TurnLeft / TurnRight | 1,13 s, Loop | auf der Stelle drehen (32°/Zyklus); Becken und Brust biegen sich gegeneinander in die Kurve, **Kopf führt** (dreht zuerst und am weitesten) | – |
| Idle | 4,0 s, Loop | schwer atmen, Gewicht verlagern, Kopf senkt sich und **schnüffelt am Boden**, hebt sich, schaut rechts/links (Kopf führt, Hals folgt) | – |
| Ready | 2,0 s, Loop | **Drohen**: Gewicht nach vorn, Kopf tief und pendelnd, Kiefer klappt (Jaw-Popping), 1× Brüllen angedeutet, Vorderpranke **schlägt auf den Boden** (Event `slam`) | bear.org / NPS: Jaw-Popping, Huffing, Boden-Schlagen als Warnsignal |
| Attack1 | 1,2 s | **Prankenhieb** (rechte Pranke, `leg` in style.toml): Gewicht zur Gegenseite/nach hinten, Brust hebt sich (19°), Schultergürtel dreht weg, Pranke hoch (0,33 m) und nach außen → Rumpf verdreht sich zurück, Schulter rollt nach unten, Pranke fährt schräg von oben nach innen-vorn (Event `hit` Frame 15), schlägt auf, Kopf geht mit Maul auf in den Hieb → zurück | Brooks-Falls-Kämpfe (Pranken-Schläge) |
| Attack2 | 1,93 s | **Aufrichten + Doppelpranken-Slam**: kurz ducken → um die **Hüfte** aufrichten (Brust bis 66° hoch), Hüfte setzt sich nach hinten/unten auf die Hinterbeine, Pranken erhoben (bis 0,85 m), Brüllen → Körper fällt nach vorn, beide Pranken schlagen 12 % Körperlänge vor der Ruheposition auf (Event `hit` Frame 32), Aufprall federt durch Rumpf, Hals, Kopf → zurück | Braunbär richtet sich auf; Kampf „wie Boxer“ auf den Hinterbeinen |
| Hit | 0,53 s | Stoß zurück, Rumpf rollt weg, Kopf schlägt verzögert zur Seite, Maul kurz auf, gedämpftes Nachfedern | – |
| Death | 1,33 s | **Platzhalter** (Nutzerregel „Death-Clips nicht anfassen“): Kopie des Hirsch-Tods (zur Seite kippen) | – |

**Ganzkörper:** Kein Angriff bewegt nur ein Bein. Attack1: Rumpf hebt/verdreht/rollt, Gewicht verlagert, Kopf und Kiefer
gehen mit. Attack2: ganzer Körper kippt um die Hüfte, Rücken streckt sich, Hals gleicht aus, Aufprall federt durch.
Messwerte dazu in `clips_report.json` (`chest_pitch_max_deg`, `front_paw_max_up_m`).

## Naturreferenzen
**Videos kann der Build-Agent nicht ansehen** – die Werte stammen aus Studien/Texten und eigener Erfahrung mit
Bärenbewegung; die Videos sind zum Abgleich durch den Nutzer verlinkt.
- **Gangarten Grizzly** (Messung an 4 Grizzlys, 1,1–3,8 m/s): Schritt = Lateralsequenz mit 3 überlappenden Füßen
  (< 2 m/s), darüber **„running walk“ statt Trab** (Bären traben kaum), dann Kanter; Galopp vermutlich ab > 4 m/s.
  Hohe seitliche Kräfte (~14 % der Vertikalkraft) durch die nach innen gestellten Vorderbeine – passt zum seitlichen
  Schwanken im Walk. Langer, abfallender Rücken. Shine et al. 2015, *J Exp Biol* 218:3102 –
  [Hartpury-Eintrag](https://pure.hartpury.ac.uk/en/publications/grizzly-bear-ursus-arctos-horribilis-locomotion-gaits-and-ground-/) ·
  Dissertation Shine 2016 (Kap. 2, frei): [PDF Uni Idaho](https://objects.lib.uidaho.edu/etd/pdf/Shine_idaho_0089E_10943.pdf) ·
  Vorderbein als „Stütze“ in der Frontalebene: [Shine et al. 2017, J Exp Biol 220:1322 (PDF)](https://sites.usc.edu/mcgowanlab/files/2023/02/JEB_Shine_GB_IDA_2017.pdf)
- **Galopp/Angriff (Videos)**: [Grizzly rennt in Zeitlupe auf eine Wildkamera zu (Yukon Wildlife Cams, Bericht)](https://www.yahoo.com/news/grizzly-bear-trail-cam-appearance-170223253.html) ·
  [Grizzly jagt Wildpferde (Wildkamera)](https://a-z-animals.com/blog/watch-a-grizzly-chase-a-herd-of-wild-horses-in-stunning-footage/) ·
  [POV-Video: wie schnell ein Grizzly angreift](https://www.advnture.com/news/this-pov-video-shows-just-how-fast-a-grizzly-bear-can-really-attack)
- **Schritt (Video)**: [Grizzly geht auf die Kamera zu (Getty-Vorschau)](https://www.gettyimages.no/detail/video/shot-of-a-grizzly-bear-walking-toward-the-camera-through-stock-footage/697882520)
- **Aufrichten, Prankenhieb, Kampf auf den Hinterbeinen**: [Zwei Braunbären kämpfen an den Brooks Falls (Field & Stream)](https://www.fieldandstream.com/conservation/brown-bears-fight-brooks-falls/) ·
  [Grizzly-Kampf am Walkadaver, mit Zeitlupe (A-Z Animals)](https://a-z-animals.com/blog/watch-a-fierce-grizzly-battle-over-whale-carcass-feast/) ·
  [Braunbären-Spielkampf, Katmai (Getty-Vorschau)](https://www.gettyimages.dk/detail/video/alaska-katmai-national-park-two-brown-bears-play-stock-video-footage/1375-206)
- **Drohen** (Jaw-Popping, Huffing, Pranke auf den Boden schlagen, Kopf tief): [bear.org – Harmless Bluster](https://bear.org/?p=241) ·
  [BearSmart – Kommunikation](https://bearsmart.com/about-bears/communication) · [NPS – Bärenangriffe](https://nps.gov/articles/bearattacks.htm)
- Suchbegriffe zum Selbst-Ansehen: „grizzly bear walking slow motion“, „bear charge slow motion“, „brown bear standing
  fight Brooks Falls“, „polar bear walking side view“, „bear jaw popping ground slap“.

## Abgeleitete Werte (2026-11-21)
| Wert | Bär | zum Vergleich | Herleitung |
|---|---|---|---|
| Walk Fußfolge | Aufsetzen HL 0 · VL 0,14 · HR 0,5 · VR 0,64 | Wolf/Hirsch 0 · 0,25 · 0,5 · 0,75 | Lateralsequenz, beim schweren Bären nah am Passgang (Seiten-Paare fast gemeinsam) |
| Walk Stand | 68 % (3 Füße am Boden) | Wolf 62 % | Shine: Schritt = 3 überlappende Füße |
| Walk Takt | 40 Frames = 0,75 Schritte/s | Wolf 32 | schwerer, langsamer |
| Schultern rollen/gieren | 7° / 6° (Becken 4° / 4°) | Wolf 2,5° / 3,5° | rollende Schultern, Buckel schaukelt – aus der ARPG-Kamera gut sichtbar |
| seitlich schwanken | 1,4 % Länge | Wolf 0,8 % | hohe Seitenkräfte (Shine 2015) |
| Kopf | 10° tiefer, pendelt 9° seitlich | Wolf ruhig | typischer Bärenkopf-Schwung beim Gehen |
| Pranken | Hub vorn 12 %, hinten 8 %, Zehen 18° | Wolf 16/13 %, 32° | Sohlengänger, schlurfend; steifer Mittelfuß (IK-Steifigkeit Leg_3 0,8) |
| Run | 20 Frames, Stand 36 %, Rücken ±11°, Schaukeln 7°, Rollen 3° | Wolf 16 Frames, 30 %, ±13°, 6° | schwerer Galopp, weniger Schwebe |
| Attack2 | Brust bis 66° hoch, Pivot Hüfte, Hüfte 5 % zurück / 6 % tiefer | – | Bär setzt sich beim Aufrichten auf die Hinterbeine |

## Drehrichtung (gemessen, nicht angenommen)
`bear_clips.py` → `turn_check()`: Standfüße wandern relativ zum Körper im Uhrzeigersinn ⇒ Körper dreht links.
Ergebnis (Rimehide Bear): TurnLeft +32°/Zyklus, mittleres Gieren Kopf +31,7° > Hals +20,3° > Brust +8° (Becken −8° =
Körper biegt sich in die Kurve) → `turn_dir_ok: true`; TurnRight genau gespiegelt. Konvention wie wolf/deer
(`gait(turn=-turn)`).

## Statur ±20 % (Varianten-Baukasten)
- Alle Längen der Clips sind **relativ** (Körperlänge, Rumpfhöhe) und die Clips werden pro Rig gebacken → eine Variante
  mit anderer Statur, die durch die Pipeline läuft (eigenes Rig), bekommt automatisch passende Clips.
- **Bricht bei reinem Knochen-Skalieren zur Laufzeit** (gleiche Clips, Knochen in Unity skaliert):
  - Die Clips speichern Knochen-Drehungen + Root-Höhe. Werden nur die Beinknochen ±20 % skaliert, stimmt die Root-Höhe
    nicht mehr → Füße schweben (längere Beine) bzw. stecken im Boden (kürzere). Fußrutschen im Walk/Run, weil die
    Schrittlänge an die alte Beinlänge gekoppelt ist.
  - Die Hinterbeine stehen in Ruhe schon zu 97,5–98,4 % gestreckt (`QUAD_REST_STRETCH`) – Körper länger/Beine kürzer
    ⇒ überstreckt; `reach_fix` senkt beim Backen den Rumpf, das geht zur Laufzeit nicht.
  - Attack2 (Aufrichten um die Hüfte): Kopf/Pranken-Höhe skaliert mit, Fußkontakt der Hinterbeine bricht wie oben.
- **Test 2026-11-21** (Mesh gestaucht/gestreckt, Rig + Clips neu gebacken, `temp/br_statur_*`, nicht im Kreatur-Ordner):
  - Länge +20 % / Höhe −20 %: alle 10 Clips grün, Drehrichtung ok. Aber Dehnung im Walk/Run 4,2/4,8 an `Hips` schon in
    Frame 0 → das Rig liest den gestreckten Rumpf schlechter (Schwanz-/Becken-Erkennung, `tail_base = 0.6` ist auf
    diese Basis abgestimmt). Erster Lauf stürzte sogar ab (Stummelschwanz-Schnitt leer) → Rig-Fix: Lücken in der
    Schwanzkette werden jetzt fortlaufend gefüllt (Regression identisch).
  - Länge −20 % / Höhe +20 %: alles grün außer **Attack2** (IK-Fehler 2,5 cm: erhobene Pranken außer Reichweite, weil
    die Pranken-Hubhöhe relativ zur Rumpfhöhe gerechnet wird, die Beine aber nicht mitwachsen) → bei solchen Varianten
    `paw_raise` je Variante kleiner setzen (`[motion.attack2]` in der creature.toml).
  - **Empfehlung:** Statur-Varianten über den Baukasten als eigenes Mesh/Rig backen (ein Pipeline-Lauf ≈ 2 min) **oder**
    nur **uniform** skalieren (ganzes Objekt – dann bleibt alles stimmig). Für gemischte Proportionen zur Laufzeit
    bräuchte Unity eine Fuß-IK (z. B. Animation Rigging Two-Bone-IK) – nicht gebaut.

## Dehnung (nur Info, Rimehide Bear)
Siehe `creatures/32_rimehide_bear/README.md` (sichtbare Flächen aus der ARPG-Kamera je Bereich).
