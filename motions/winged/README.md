# Skelett `winged` – Zweibeiner mit Flügeln

Wyvern/Drachen (Muster **drake**) und große Vögel (Muster **bird**). Eigenes Rig (`rigging/winged_rig.py`) und eigener
Baukasten (`winged_kit.py`), kein Import aus anderen Skeletten.

## Knochen (36, Unity „Generic“, feste Namen)
```
Root
└ Pelvis → Spine_1 → Spine_2 → Chest
     Chest → Neck_1 → Neck_2 → Neck_3 → Head → Jaw          (Vogel: Jaw = Unterschnabel)
     Chest → Clavicle_{L,R} → UpperArm → Forearm → Hand → Finger_1 → Finger_2
Pelvis → Tail_1 … Tail_6                                      (Vogel: kurzer Steuerfeder-Fächer)
Pelvis → Thigh_{L,R} → Shin → Foot → Toe                      (digitigrad: Foot = Lauf, Toe = Zehen + Hinterzehe)
```
Drache: Finger_1/2 = Flügelfinger bis zur Spitze, die Haut dazwischen hängt per Gewicht an Arm, Hand und Fingern.
Vogel: Hand + Finger tragen die Handschwingen (Federspitzen, doppelseitig).

## Baukasten (`winged_kit.py`)
- **Beine:** IK-Kette Thigh+Shin+Foot auf den Fußballen, Zehen folgen dem Boden-Ziel (`gait`, `set_foot`, `reach_fix`).
  In der Luft IK ausblenden (`ik_set(s, 0)`) und Beine anziehen (`legs_tuck`).
- **Flügel ABSOLUT** (`wing(s, P)`): Grundform = Gelenkwinkel des Modells (links/rechts gemittelt, sonst reißt die
  Haut, die Tripo zwischen den Knochen aufgespannt hat), dann Richtung + Ebene jedes Knochens aus wenigen Parametern:
  `fold` (falten/spreizen), `arm` (Flügel in seiner Ebene drehen), `elev` (heben), `sweep` (fegen), `pitch`
  (Anstellwinkel), `bend`/`twist`/`curl` je Glied. Beide Flügel sind spiegelgleich, egal wie schief Tripo sie gestellt hat.
  Bezug ist die Brust in der Standhaltung des Musters (neigt sich der Körper, gehen die Flügel mit).
- **Schwanz ABSOLUT** (`tail`, `tail_wave`): Richtung je Glied vom Becken aus, die Tripo-Krümmung zählt nicht.
- **Rumpf** `posture(rise_deg)` absolut (Neigung Becken → Brust über der Waagerechten), `spine`, `body`, `neck`, `jaw`.
- **bake()**: Keyframes + Selbstprüfung: Fußkontakt, Rutschen, Schleife nahtlos, Drehrichtung (Rumpf UND Kopf führen),
  Boden-Durchdringung, Flügel-Symmetrie (Spitzen gespiegelt), Dehnung (nur Info).
  Clip-Arten: `locomotion`, `stand`, `stand_return`, `air` (Flug, Füße frei), `transition` (Abheben/Landen/Sprung:
  `ground(f)` sagt, wann die Füße stehen), `death`.

## Muster
| Muster | Kreatur | Kern |
|---|---|---|
| [drake](drake/README.md) | 14 Cinder Wyvern | zweibeinig, Flügel erhoben, Biss-Ausfall, Schwanzkeule, Flughund-Flügelschlag |
| [bird](bird/README.md) | 15 Bonepicker Vulture | Watscheln + beidbeiniges Hüpfen, Hacken, Sprung-Krallenhieb, Ruderflug, Thermik |

Clips (beide): Walk, Run, Idle, Ready, TurnLeft, TurnRight, Attack1, Attack2, Hit, Death (Platzhalter), Fly, Glide,
TakeOff, Land. Präfix `Winged_Drake_` / `Winged_Bird_`. Fly/Glide schweben auf `height` × Körperhöhe über dem Boden.

## Prüfbilder
`rigging/winged_review.py` (Kopie von upright_review mit winged-Farben): `rig` = Skelett + Gewichte vorn/seitlich/oben,
`strip` = Einzelbilder eines Clips (ARPG/Seite/vorn).
