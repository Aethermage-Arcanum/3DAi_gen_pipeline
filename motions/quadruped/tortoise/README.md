# Bewegungsmuster quadruped/tortoise – Schildkröte

Erstes Modell: **Shellback** (`creatures/11_shellback/`). Generator `tortoise_clips.py`, Werte `style.toml`,
Recherche und Herleitung `RESEARCH.md`. Clips heißen `Quadruped_Tortoise_<Clip>`.

```
python scripts/creature_pipeline.py creatures/11_shellback --stage motion   # Roh-GIFs rig/anim/raw/
python scripts/creature_pipeline.py creatures/11_shellback --stage full     # + Export, Gegentest, Fingerabdruck
```

## Entscheidungen des Nutzers (2026-11-23)
- **Attack2 = Panzer-Rammstoß** (Kopf eingezogen, Stachelpanzer voran; Vorbild Kommentkampf männlicher Landschildkröten).
- **Tempo lebhafter als echt:** Walk ≈ 0,7 Hz (42 Frames), Run ≈ 1,2 Hz (25 Frames). Echte Riesenschildkröten
  „pausieren fast bei jedem Schritt“ – im ARPG wirkte das eingefroren.
- **Kopf einziehen:** Der Kopf darf **halb** in den Panzer eintauchen (Mesh hat keinen Hohlraum; aus der Spielkamera
  verdeckt). Genutzt in Idle (einmal halb einziehen), Hit (Schreck) und Attack2 (Rammen).

## Was das Muster ausmacht
- **Panzer 100 % starr.** Der Rumpf bewegt sich nur als Ganzes (`shell()`: Root um einen Drehpunkt – Panzermitte, beim
  Kippen nach vorn die Hüfte). Hips/Spine_1/Chest werden nie gegeneinander gedreht. Voraussetzung im Rig:
  `rigid_shell = true` (siehe unten). Gemessen: Rücken und Flanke aus der Spielkamera in allen Clips Dehnung **1,00**.
- **Gang:** lateraler Viertakt, diagonal gekoppelt (Aufsetzen HL 0 · VL 0,40 · HR 0,5 · VR 0,90; Kit-Konvention
  `order = −Aufsetzzeit`), hoher Duty (Walk 0,78, Run 0,62, keine Schwebe). Fuß hebt flach und schwingt im Bogen nach
  außen (`swing_out`, gespreizte Beine). Kernunterschied zum Bären (lateral gekoppelt).
- **Lesbarkeit aus der Kamera = Panzer-Schaukeln:** Rollen ±3°, Gieren ±2,5° im Takt der Diagonalpaare (VL schwingt →
  linke Seite sinkt, linke Schulter geht vor), Heben 2× pro Zyklus, sackt 2–3 Frames nach dem Diagonal-Aufsetzen nach.
  Kopf vorgestreckt und tief, gleicht 70 % des Panzer-Gierens aus (ruhig), Hals schiebt im Takt leicht vor/zurück.
- **Stachelschwanz** starr in der Form (eigene Öffnung im Panzer), pendelt nur ±4° verzögert; beim Drehen nach außen.
- **Drehen:** Füße schieben tangential, **Kopf führt** (Mittel 31,5°), Panzer giert 6° in die Kurve – um die Hüfte, damit
  das innere Hinterbein nicht überstreckt –, rollt 1° zur Außenseite. 30 °/s.
- **Angriffe arbeiten mit dem ganzen Körper:** Reichweite kommt vor allem aus dem Körper-Ausfall, weil der modellierte
  Hals kurz ist und keine Hautreserve hat.

## Clips (Shellback, 30 fps)
| Clip | Dauer | Inhalt | Messwerte |
|---|---|---|---|
| Walk (Loop) | 1,4 s | diagonal gekoppelter Viertakt, Panzer schaukelt | Fußkontakt 0,0 mm, 0,143 m/s, Rumpf max. 1,5 cm abgesenkt |
| Run (Loop) | 0,83 s | hastiger Trab ohne Schwebe, Panzer 4 % tiefer, stärker schaukelnd | Fußkontakt 0,0 mm, 0,38 m/s |
| Idle (Loop) | 4,0 s | atmen, Kopf schaut rechts/links, zieht einmal halb ein, VR wird nachgesetzt | Standfüße 0,0 mm |
| Ready (Loop) | 1,8 s | Drohen: Panzer vorn 10° runter (wirkt als Hinterteil hoch), Kopf zurück + hoch, Maul weit offen, Wiegen | Füße 0,0 mm |
| TurnLeft / TurnRight (Loop) | 0,87 s | Drehen auf der Stelle, Kopf führt | ±30 °/s, Richtung gemessen ok (Kopf ±31,5° > Brust ±6°, gleiche Richtung) |
| Attack1 | 1,0 s | Schnappbiss: ausholen → Körper-Ausfall 0,16 L, Panzer kippt vorn 9° runter, Hals 0,085 L vor + Kopf nach vorn-oben, Maul schlägt zu (`hit` F12) → Zerren ±10° → zurück | Nase beim Treffer **22,7 cm vor der Ruhe-Nase**, 28,7 cm vor dem Panzer, Höhe 24 cm (Ruhe 26 cm) |
| Attack2 | 1,13 s | Panzer-Rammstoß: Kopf halb einziehen, ducken → Ausfall, vorn 13° aufbäumen (`hit` F16), Vorderfüße heben ab und setzen vorn auf, Hinterfüße treten nach → nachrutschen | **Root Motion 0,24 m** (Event `root_motion`), Panzerfront beim Treffer 18,4 cm vor der Ruhe, Höhe 30 cm |
| Hit | 0,47 s | Kopf zuckt halb ein, Panzer sackt ab, kippt zurück, rollt | kehrt zur Ruhe zurück |
| Death | 1,33 s | **Platzhalter** (Kopie Bär/Hirsch: zur Seite kippen). Nutzerregel: Death nicht anfassen. Schildkrötentypisch wäre „auf den Rücken“ – erst nach Freigabe. | |

Unity: Attack2 mit „Apply Root Motion“ (Root node = `Root`) oder per Code um `distance_m` aus dem Event versetzen.

## Rig-Optionen für Schildkröten (`rigging/quadruped_rig.py`, opt-in, nur Shellback eingeschaltet)
```toml
[quadruped.rig]
rigid_shell = true          # Panzer = Hauptkörper ohne Bein-/Hals-/Schwanz-Öffnungen → 100 % an shell_bone
shell_bone = "Spine_1"
shell_front = 0.3           # Halsöffnung: Anteil Schultergelenk → Kopfansatz (x)
shell_rim_front = 0.5       # Vorderbeine weich nur unter dieser Höhe (Anteil H) …
shell_rim_back = 0.42
shell_leg_radius = 0.22     # … und näher als das an der Beinkette (Anteil H)
shell_back = 0.19           # Schwanzöffnung (Anteil Länge vor der Schwanzspitze) …
shell_rim_tail = 0.45       # … unter dieser Höhe
shell_min_height = 0.18     # darunter nie Panzer (Krallen/Fersen am Boden)
shell_neck_free = true      # Halsöffnung + Kehle ohne Schulterblatt-/Bein-Gewichte (weich auslaufend)
shell_neck_free_width = 0.14
shell_blend_width = 0.12    # Übergang Panzer → Haut nach ABSTAND (Anteil H); ohne den Wert: shell_blend_rings Kanten-Ringe
knee_out = 0.07             # Hinterbein-Knie seitlich nach außen (Anteil H)
```
Warum (gemessen an der Shellback, sichtbare Flächen, `joint_densify_review.py visible`):
- Ohne `rigid_shell` griffen Schulterblatt, Oberarm, Oberschenkel, Hals und Schwanz in den Panzerrand.
- **Ring-Übergang (2 Kanten-Ringe) → Abstand:** Tripo-Low-Poly hat am Panzerrand Kanten von 0,5–1 cm neben langen; der
  Ring-Übergang war dort nur 1–2 cm breit → Dehnung bis 6,8 an Oberschenkel/Unterbein. Nach Abstand (7 cm): Walk 1,65,
  Run 1,78, Turn 1,6, Attack2 2,1.
- **Halsöffnung ohne Schulterblatt:** Hals schießt vor, Schulterblatt nicht → Riss am Halsansatz (4,6). Danach Hals 2,1.
  Harte Zonengrenze gab in der Lückenprüfung 5,8 cm (Kehle) → weich auslaufend (`shell_neck_free_soft`, Standard 0,06 H): 0,9 cm.
- **`knee_out`:** Die Hinterbeine sind als gerade Säule modelliert, Kette in Ruhe 0,96–0,98 gestreckt → jede
  Rumpfbewegung (Schaukeln, Ausfall, Drehen) zog den Rumpf nach unten (Drehen 11 cm, Rammstoß 24 cm). Mit Knie 4 cm
  außen: 0,89/0,92, IK beugt seitlich (Knie außen wie beim echten Tier).
- **Nicht genutzt:** `rigid_head_above` (würde die vorderen Panzerplatten mit dem Kopf nicken lassen), `joint_densify`
  (die Dehnung kam aus den Gewichten, nicht aus langen Kanten).

## Rest / Grenzen
- **Attack1 Kehle/Halsansatz** sichtbar bis 2,6 (Hals 2,1): Hals fährt 8,5 cm aus einem Mesh ohne Hautreserve. Liegt unter
  dem Kopf, aus der ARPG-Kamera großteils verdeckt (Prüfbild `temp/sh_a1_arpg_002.png`: gelb, keine Risse). Mehr Abhilfe
  nur über ein Modell mit sichtbarem Hals/Hautfalten.
- Die Seitenansicht der Vorschau (feste Kamera) schneidet im Attack1 den Kopf ab; ARPG-Ansicht zeigt ihn.
- Ready kippt den Panzer um die Hüfte (Hinterbeine haben trotz `knee_out` kaum Streckreserve zum echten „Hinterteil hoch“).
- Kit-Messwert `max_stretch` (alle Kanten, auch verdeckte) 2,8–7,1 – nur Info; maßgeblich sind die sichtbaren Flächen.

## Naturreferenzen
Siehe `RESEARCH.md` §3 (Biss Schnappschildkröte in Zeitlupe, Gang Aldabra-/Leopard-/Sternschildkröte; Schmidt et al. 2016,
Zani et al. 2005, Jayes & Alexander 1980, NC Wildlife). **Videos nicht selbst angesehen** (Agent kann keine Videos sehen) –
Werte sind Startwerte aus Literatur und Beschreibungen; der Nutzer sollte die Roh-GIFs gegen die Videos abnehmen.

## Varianten
Noch keine. Kandidaten (nur Werte): Landschildkröte = gleiche Kopplung, Walk langsamer (cycle_frames ↑), kein Schnappbiss
(Attack1 kürzer), Run entfällt.
