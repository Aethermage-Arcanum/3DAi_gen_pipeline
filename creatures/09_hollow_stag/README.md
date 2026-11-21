# Hollow Stag (Mammals · Highlands) – quadruped/deer

Erstellt 2026-11-17 im autonomen Lauf.

```
python scripts/tripo_run.py creatures/09_hollow_stag --steps generate   # 110 Credits, erledigt (raw/)
python scripts/creature_pipeline.py creatures/09_hollow_stag             # kostenlos
```

| Kennzahl | Wert |
|---|---|
| Dreiecke | ca. 4.300 (Tripo, aber 6.445 Vertices durch viele UV-Nähte) |
| Materialien / Draw Calls | 1 |
| Texturen | Farbe, Normal, ORM je 1024² |
| Knochen | 30 (Vierbeiner-Standard) |
| UV | Tripo-UV (1.146 Inseln – sehr zerstückelt, aber besser als Smart UV) |
| Clips | 9, alle grün; Lücken max. 0,5 cm |

Geweihstoß: Kopf tief, Nase runter (Geweih zeigt nach vorn), Vorschnellen. Dehnungs-Grenzen pro Clip mit Begründung in `motions/quadruped/deer/style.toml`.
Versuche mit exklusiven Beinpaaren / Brücken-Schnitt haben beim Hirsch die Dehnung nur verschoben → nicht aktiv.

**2026-11-17 – Nutzer-Feedback aus Unity behoben** (Optionen in `creature.toml [quadruped.rig]`):
- Vorderknie knickten nach innen: Die Vorderbeine stehen so eng, dass sie im Bauch-Messstreifen lagen → Beine als Bauch gelesen, alle Vordergelenke ~15 cm zu tief. Fix `adaptive_belly_strip`.
- Hinterbeine 2,4× so breit wie vorne (schon im Tripo-Modell, Ursache Referenzbild): Mesh-Korrektur `narrow_hind_legs = 0.8` (Hufe ±14,6 → ±7,7 cm, vorne ±6 cm).
- Geweih wackelte (hing am Hals-Knochen): `rigid_head_above` → Geweih starr am Kopf.
- Offen: Der alte Death-Clip hat jetzt 2,5 cm Lücke Hinterbein/Schwanzansatz (Grenze 1,5) – Death wird ohnehin neu gemacht. Alle anderen Clips ≤ 0,7 cm.

**2026-11-20 – C14 Geweih-Fix** („irgendwas hält das Geweih hinten fest“, Nutzer 2026-11-18/20):
- **Ursache (gemessen):** `rigid_head_above` in `rigging/quadruped_rig.py` machte nur Vertices über der Kopf-Oberkante
  **und vor der Schulter** (`x > x_sh`) starr am Kopf. Die hinteren Geweihsprossen ragen in der Draufsicht bis hinter die
  Schulterlinie → 144 Vertices der Sprossenspitzen hatten **0 % Kopf**, dafür Neck_1/Neck_2/Chest/Spine_1/Shoulder-Gewichte.
  Bei jeder Kopfbewegung blieben die Spitzen beim Körper → dünne, gestreckte Fläche nach hinten.
  Prüfbilder: `review/c14_antler_weights.png` (rot = Geweih mit Hals-/Rumpf-Gewicht, vorher/nachher),
  `review/c14_vorher_nachher.png` (Einzelbilder Attack/Ready/Turn/Walk aus den Roh-GIFs, vorher/nachher).
- **Fix (am Rig, Bewegung unverändert):** zwei Optionen in `creature.toml [quadruped.rig]`, nur für den Hirsch gesetzt:
  `rigid_head_connected = true` – starr am Kopf ist alles über der Kopf-Oberkante, das *innerhalb dieser Zone mit dem
  Schädel verbunden* ist (Rückenstacheln/Mähne liegen tiefer bzw. hängen nicht dran); `rigid_head_blend_rings = 2` –
  weicher Übergang Schädel→Nacken über 2 Kanten-Ringe *unter* der starren Zone (vorher Head 1,0 direkt neben Neck_2 1,0).
  Ohne die Optionen läuft der alte Code (alle anderen Vierbeiner: nachweislich identisch, s. u.).
- **Messwert** (`rigging/check_rigid_head.py`, größte Abweichung eines Geweih-Vertex von einer starren Kopfbewegung über
  alle Clips/Frames): **vorher 29,6 cm** (Geweihstoß), Ready 20,6, Turn 16,9, Idle 12,9, Walk 8,8 cm →
  **nachher 0,0 cm** in allen 9 Clips; Geweih-Vertices mit Fremd-Gewicht 144 → 0.
  Knochen-Bewegung identisch (Fingerabdruck: Knochen 0,0 mm/0,0°). Max. Dehnung Kopf/Hals: Attack 11,4 → 3,9,
  Ready 8,9 → 3,8, Turn 7,7 → 2,7. Nacken-Kanten: Idle 1,70 → 1,28, Turn 1,61 → 1,22 (Kantenlänge-Faktor).
- Regression: `scripts/regression.py --deep --creatures ravine_stalker,reef_snapper --against temp/c14_base` → beide identisch.
- Erneut prüfen: `& "D:\Blender\blender.exe" -b creatures/09_hollow_stag/rig/clips.blend -P rigging/check_rigid_head.py -- temp/rigid_head.json creatures/09_hollow_stag/creature.toml`
- Gilt automatisch auch für das spätere neue Hirsch-Modell (C12), da die Optionen in der `creature.toml` stehen.
- Neu gebaut (`--stage motion` → Roh-GIFs `rig/anim/raw/`, dann `--stage full`): alle 9 Clips ✓, Gegentest FBX/GLB ✓, Gelenk-Lücken max. 3,0 cm (Grenze 3,2, Schwanzstachel, unverändert). Death-Clip nicht angefasst (nur das Rig wirkt mit).

**2026-11-21 – C15 Dehnung am Hals aus der Spielkamera** (Nutzer: gemeldet war der **Hals**, nicht die Fußgelenke):
Gemessen nur auf den aus der Spielkamera sichtbaren Flächen (`rigging/joint_densify_review.py visible`,
`rigging/README.md` → „Gewichte nach Körperbereichen“).
- **Schlimmste sichtbare Stellen vorher:** Widerrist/Halsansatz oben im Geweihstoß **3,92** (29 Kanten > 1,5) und in
  Ready **3,60** (30); Kruppe/Schwanzansatz Run **2,99**, Attack 2,73; Rücken über dem Becken Attack 2,27; Hals unten
  (Brust) Run 2,17.
- **Ursachen (Fehlerklassen):** *Fremder Körperbereich* – beide Schulterblätter hatten 17–29 % auf dem Widerrist
  (halten ihn fest, während der Hals nach unten geht), die Oberschenkel bis 22 % auf der Kruppe (Abstands-Grenzen sind
  Anteile der Höhe, der Hirsch ist hoch → Bein-Gewichte reichen über den ganzen Rumpf). *Falscher Wirbelknochen* – der
  Hals steigt steil, der obere Halsknochen Neck_2 ist vom Widerrist so weit entfernt wie Neck_1 → 43 % Neck_2 am
  Widerrist. *Rig-Aufbau* – die Schwanzkette läuft im Zickzack durch die Hinterbeine (Mittelpunkt-Suche greift die weit
  hinten stehenden Beine): Tail_3/Tail_4 je 25 % auf der Kruppe.
- **Fix** (`creature.toml [quadruped.rig]`, Bewegung unverändert – Knochen 0,0 mm / 0,0°): `zone_lock = true`,
  `spine_chain_blend = 1.0`. Kein Gelenk-Verdichten (Widerrist-Kanten 3,5–4,2 cm lang, nach dem Fix aber ≤ 1,46) →
  Dreiecke unverändert.
- **Messwerte sichtbare Flächen, vorher → nachher** (max · Kanten > 1,5):
  Hals: Attack 3,92 · 29 → **1,40 · 0**, Ready 3,60 · 30 → **1,28 · 0**, Run 2,17 · 19 → 1,46 · 0, Walk 1,84 → 1,42,
  Turn 1,79/1,88 → 1,46/1,47 · Rücken: Attack 2,27 · 9 → 1,48 · 0, Run 1,80 → 1,26 · Schwanz/Kruppe: Run 2,99 · 9 →
  1,50 · 0, Attack 2,73 · 18 → 1,85 · 1, Idle 2,17 → 1,05 · Flanke ≤ 1,43, Schulter/Oberschenkel Attack 1,99 · 13 →
  1,62 · 2, Run 1,77 · 3 → 1,73 · 7. Anteil je Regel: `zone_lock` allein Hals Attack 3,92 → 2,16; `spine_chain_blend`
  allein nur 3,92 → 3,54; erst beide zusammen 1,40 (nach der Schulterblatt-Sperre bleibt Neck_2 die Ursache).
- **Rest:** Schwanzansatz im Geweihstoß 1,85 (Zickzack-Schwanzkette – Knochen umsetzen würde die Schwanzbewegung ändern,
  Entscheidung Nutzer); Unterbein/Hinterhufe unverändert (C12, tabu).
- Geweih weiterhin starr: `rigging/check_rigid_head.py` → 0,0 cm Abweichung in allen 9 Clips, 0 Geweih-Vertices mit
  Fremd-Gewicht. Neu gebaut (`--stage motion`, dann `--stage full`): alle 9 Clips ✓, Gegentest FBX/GLB ✓, 4.243 Tris,
  Gelenk-Lücken max 3,1 cm (vorher 3,05, Schwanzstachel). Die Gesamt-Dehnung im Clip-Bericht (Run 4,0, Attack 3,92)
  liegt jetzt am Hinterbein innen (Leg_BR_2, C12-Breitbeine, tabu) bzw. zwischen den Vorderbeinen (Leg_FR_1) – beides
  aus der Spielkamera verdeckt.
- Prüfbogen ARPG-Ansicht: `review/c15_hirsch_hals_vorher_nachher.png`, Geweihstoß über den ganzen Clip:
  `review/c15_hirsch_attack_dehnung_vorher_nachher.gif`. Roh-GIFs `rig/anim/raw/` (vorherige Fassung als Kopie in
  `temp/rd_before/09_hollow_stag/anim/`, nicht versioniert).
