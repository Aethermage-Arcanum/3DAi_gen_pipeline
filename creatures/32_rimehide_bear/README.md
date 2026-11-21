# Rimehide Bear (32) – nackte Basis für die Bären-Varianten

```
python scripts/tripo_run.py creatures/32_rimehide_bear --steps generate   # 110 Credits – wartet auf OK des Nutzers
```

## Stand (2026-11-21)
- Basis-Bilder fertig, geprüft (Teil A), `--dry-run` ok → **wartet auf OK des Nutzers für den bezahlten Lauf** (110 Credits, Guthaben 155). Letzter Tripo-Lauf (BACKLOG G10).
- Varianten-Planung: `VARIANTEN.md` (BACKLOG Q8). Muster: `quadruped/bear`.

## Herkunft der Bilder
ChatGPT, vom Nutzer erstellt am 2026-11-20 („nackte“ Basis: facettiert, neutrale glatte Haut, ohne Eis/Fell). Originale bleiben in `input/` liegen, Kopien unter den Pipeline-Namen:

| Pipeline-Datei | Original | Inhalt |
|---|---|---|
| `design.png` | `Facettierter Eisbär mit Reißzähnen.png` | Design-Bild, 3/4-Ansicht |
| `front.png` | `Frontale Rimehide-Bär-Statue-1.png` | vorn |
| `left.png` | `Facettierter Rimehide-Bär im Seitenprofil-2.png` | Kopf im Bild **links** = eigene linke Körperseite |
| `right.png` | `Facettenbär im Seitenprofil-3.png` | Kopf im Bild **rechts** = eigene rechte Körperseite |
| `back.png` | `Facettierter Eisbär von hinten-4.png` | hinten |

Konvention left/right: `scripts/make_prompts.py` („left“ = its own left side, head to the LEFT image edge), so auch bei `14_cinder_wyvern/input/left.png`.
`input/Varianten/` = Varianten-Bilder des Nutzers, gehen nicht an Tripo.

## Prüfung Teil A (Referenzbilder, Claude 2026-11-21)
1. Reihenfolge/Blickrichtung ok (vorn, Kopf links, Kopf rechts, hinten), Kamera auf Augenhöhe. Die Seitenansichten sind leicht schräg (fernes Beinpaar sichtbar), kein Problem.
2. Haltung in allen vier Ansichten gleich: waagerechter Rücken mit Buckel, Kopf leicht gesenkt.
3. Nichts zwischen den Beinen: Stummelschwanz frei am Hinterteil.
4. Beine gerade nach unten, nicht gespreizt. Vorderbeine stehen **breiter als die Hinterbeine** (umgekehrt zum Hollow-Stag-Fehler) – gewollt, passt zum massigen Bären. Bei der Modellprüfung (Teil B, Fußabstand hinten/vorne) als bekannt werten.
5. Gliedmaßen frei, keine Berührungen untereinander.
6. Neutrale Pose, Maul zu. Kleine Säbel-Fangzähne ragen aus dem Oberkiefer (ins Mesh eingebaut, gewollt).
7. Teilezahl stimmt: 4 Beine, 1 Schwanz, 2 Ohren – in allen Ansichten und wie in `design.png`. Kleinigkeit: Krallenzahl schwankt (vorn 4, Seitenansicht 3) – egal für Tripo/Spielkamera.
8. Keine dünnen Teile (Flügel/Flossen).
9. Kein Glühen, neutraler grauer Hintergrund, keine Schrift.

**Ergebnis: freigegeben**, kein Grund, Bilder neu zu machen.

## Tripo-Einstellungen (Dry-Run 2026-11-21)
multiview-to-model, P-Serie `P2-20260801`, `face_limit` 4000, texture + PBR (`v3.5-20260815`, standard), delight, keine Quads. Nur Schritt `generate` (Tripo-Rig/Animation werden nicht genutzt).
