# UV-Prüfung (Schritt 0 der Pipeline, direkt nach Tripo)

`uv_check.py` misst Tripos UV-Map und eine Blender-**Smart-UV**-Alternative (kostenlos, lokal), wählt die bessere und rendert eine Sichtprüfung mit Test-Texturen. Ausgabe pro Kreatur in `creatures/<NN_name>/uv/`:
- `model_uv.glb`: Modell mit finaler UV, die Eingabe für das Rig
- `uv_report.json`: Kennzahlen beider UV-Varianten + Entscheidung
- `uv_preview.png`: **Prüfblatt** (`uv_sheet.py`), Tripo-UV und Smart UV untereinander:
  - **Inseln eingefärbt** (schräg + Seite): jede UV-Insel eine Farbe, also siehst du, welcher Körperteil an einem Stück liegt und wo zerschnitten wird
  - **Kopf-Nahaufnahme** mit Inseln + Nähten: Werden Augen, Kiefer, Fühlerbasis sauber getrennt?
  - **Nähte (gelb) auf der Original-Textur**: Gute Nähte laufen an Segmentkanten und Unterseiten, schlechte quer über Platten oder über den Kopf (oben sichtbar)
  - **Texel-Dichte** als Heatmap: grün = gleich scharf, blau = unschärfer, rot = schärfer als der Durchschnitt
  - **2D-Layout in denselben Inselfarben** über der Textur: Welcher Texturfleck gehört zu welchem Körperteil?
  - unten: gewählte UV mit Schachbrett + 1–2 Biom-Texturen
- `insp_<tripo|smart>_*.png`: die Einzelbilder des Prüfblatts
- `uv_layout_tripo.png` / `uv_layout_smart.png`: UV-Raum (grün = belegt, rot = Überlappung)

## Kennzahlen
| Kennzahl | Bedeutung | Grenze (`uv_defaults.toml`) |
|---|---|---|
| islands | Anzahl UV-Inseln (= Nähte); weniger ist besser | – |
| coverage | genutzter Anteil des UV-Raums (mehr = bessere Texturauflösung) | ≥ 45 % |
| overlap | überlappende UV-Fläche (Textur doppelt benutzt) | ≤ 2 % |
| density_outlier_fraction | Fläche mit Texturdichte außerhalb ×0,5…×2 (gezogen/gestaucht) | ≤ 10 % |
| angle_distortion_deg | mittlere Winkelverzerrung 3D → UV | ≤ 8° |
| parts / uv_islands | Körperteile (zusammenhängende Geometrie) / UV-Inseln | – |
| parts_in_one_island | Anteil der Körperteile, die als **ein** Stück in der UV liegen | – |
| big_parts_split_mean | in wie viele Inseln die größeren Teile im Schnitt zerschnitten sind | – |
| seam_length_per_size | Nahtlänge in Körpergrößen (jede Naht = möglicher sichtbarer Textur-Sprung) | – |
| seams_on_top_fraction | Anteil der Nähte auf nach oben zeigenden Flächen (in der Top-down-Kamera sichtbar) | – |
| part_density_min_max / head_density | Texturschärfe pro Körperteil relativ zum Mittel (Kopf: Augen!) | – |
| error_score | Gesamtwert (kleiner = besser) inkl. Naht-Strafe (`seam_weight`), Basis der Auto-Entscheidung | – |

`mode = "auto"`: Smart UV wird nur genommen, wenn ihr Fehlerwert < 80 % des Tripo-Werts ist. Dann werden **alle Texturen per Cycles-Bake übertragen**: Farbe und ORM über Emission, die Normal Map per „selected to active“ (der Tangentenraum hängt an der UV).

## Test-Texturen (`biome_textures.py` → `textures/`)
Kachelbar, düster-gemalt, Paletten aus den Biom-Concepts: **forest, coast, highlands, desert, snow, abyss**, dazu ein UV-Schachbrett mit Feldnamen und Richtungspfeil. Pro Lauf werden nur 1–2 Biome gerendert (`[preview] test_biomes`).

## Ergebnis Chitin Crawler (2026-11-17)
| | Tripo-UV | Smart UV (gepackt) |
|---|---|---|
| Inseln | 78 (eine pro Mesh-Teil) | 595 |
| Abdeckung | 61 % | 31 % |
| Überlappung | 0 % | 0 % |
| Dichte-Ausreißer | 1,2 % | 0 % |
| Winkelverzerrung | 6,8° | 5,5° |
| Körperteile in 1 Insel | 22 % | 0 % |
| große Teile zerschnitten in Ø | 6,3 Inseln | 51,6 Inseln |
| Nahtlänge | 16,7× Größe (39 % oben sichtbar) | 61,9× Größe |
| Dichte pro Teil | 0,88–2,12× (Kopf 1,6×) | 0,98–1,02× |
| Fehlerwert ohne / mit Naht-Strafe | **0,72** / **1,05** | 0,73 / 1,97 |

→ **Tripo-UV behalten.** Tripos P-Serie trennt Segmente überwiegend an ihren Kanten, und die Augen sind eigene kleine Inseln. Der Kopf bekommt 1,6× Texturschärfe, was für Augen gut ist. Schwachstelle: eine Naht läuft längs über die Kopfmitte (in der Kopf-Nahaufnahme sichtbar). Smart UV zerhackt jedes Teil in rund 50 Schnipsel und ist nur bei der Dichte gleichmäßiger.
**Lehre:** Die reine Flächenmessung hielt beide für gleichwertig (0,72 zu 0,73). Erst Inselfarben + Nähte zeigen den echten Unterschied, deshalb zählt die Nahtlänge jetzt im Fehlerwert mit. Der Wechsel-Pfad (Rebake) wurde erzwungen getestet, die übertragene Textur ist optisch identisch.

## Stolperfalle (behoben)
Flat Shading vor dem glTF-Export trennt jedes Dreieck in eigene Vertices → das Rig erkennt dann keine Anatomie mehr. Deshalb wird vor dem Export die Original-Schattierung wiederhergestellt, und die Vertex-Zahl wird nach dem Export gegengeprüft.

## Tripo-Alternative
Tripo hat einen eigenen UV-Endpunkt (`/v3/mesh-uv`, kostet Credits). Nicht nötig, solange Tripo-UV die Grenzwerte einhält.
