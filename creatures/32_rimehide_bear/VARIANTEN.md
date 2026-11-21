# Rimehide Bear – Varianten zuerst (Schritt 0)

Stand 2026-11-20. **Letzter Tripo-Lauf** (155 Credits = genau 1 Modell, kein zweiter Versuch).
Ziel: **ein** Grundkörper (massiger Vierbeiner mit Buckel, ohne Eis), aus dem möglichst viele Roster-Kreaturen als
Varianten entstehen. Skelett `quadruped`, neues Bewegungsmuster `quadruped/bear`.

Ablauf: **Nutzer legt die Varianten fest** → Basis eindampfen → Design-Bild → 4 Ansichten → Prüfung A → Tripo
(erst `--dry-run`, dann nach OK). `roster.toml` und Prompts werden erst danach angepasst.

Kurz erklärt – Varianten sind ein **Schichtmodell** (Nutzer 2026-11-21, am Beispiel Bär; Tabelle unten am
2026-11-21 danach umsortiert, Inhalt unverändert):
1. *Statur* = Standard-Statur plus Regler für Größe, Proportionen (länger, gestauchter) und Gewicht (dick/dünn).
2. *Bedeckung* = Haupt-Oberfläche (Fell, Federn, Leder, Platten …) mit eigenen Einstellungen: Länge, Dichte, Form,
   Farbe.
3. *Accessoires* = Zusatzteile (Hörner, Schuppen, Pilze, Rücken-Aufsätze, Gehänge …): erst die Körperstellen wählen,
   dann die Einstellungen pro Accessoire. Per Blender Geometry Nodes mit Schiebereglern, starr am nächsten Knochen.
4. *Material/Textur-Ebenen* = färbt bzw. stilisiert alles Vorherige, auch mehrere Ebenen übereinander (Farbe, Eis,
   Glut, Nässe); Partikel (Frost-Atem, Funken, Staub) in Unity.

## 1. Varianten-Entwurf

| # | Variante | Biom | Kurzbeschreibung |
|---|---|---|---|
| 1 | Rimehide Bear (Grundform) | Eis | Weiß-stahlblauer Gletscherbär, Eisplatten auf Rücken/Schultern/Unterarmen, Eissplitter-Kamm, Prankenhieb friert ein |
| 2 | Mossback Bear | Wald | Dunkelbraun-moosgrün, Moospolster und Pilze statt Eis, Gift |
| 3 | Cave Bear | Höhle | Schwarzbraun, Tropfstein-Platten und kleine Kristalle, Betäubung |
| 4 | Slagback Bear | Vulkan | Rußschwarz mit glühenden Rissen, Basaltplatten und Schlackebrocken, Feuer |
| 5 | Cragplate Bear | Stein | Steingrau-braun, Steinplatten und Felszacken, etwas größer, Stampfer betäubt |
| 6 | Elder Rimehide (Elite) | alle | 1,5× so groß, Krone aus Eiszacken, Schulterdornen, Brüllen + Doppelschlag aufgerichtet |
| 7 | *Quillback Burrower* (passt gut) | Stein | Dachs-artiger Gräber mit Stachelmantel. **Abweichung:** flacher und länger, kürzere Beine, große Grabkrallen, keilförmiger Kopf – über Proportions-Slider machbar |
| 8 | *Stone Boar* (Grenzfall) | Hochland | Buckel-Eber mit Steinplatten und Hauern. **Abweichung:** lange Schweine-Schnauze statt Bärenkopf, Hufe statt Pranken, Hinterbeine deutlich kürzer – Kopf und Füße passen nur mit neutralem Kopf |
| 9 | *Shore Lurker* (Grenzfall) | Küste | Krokodil-Walross-Lauerer mit Hauern und Stachelmähne. **Abweichung:** liegt flach am Boden, Beine seitlich gestellt, breiter flacher Kopf, dickerer Schwanz – Silhouette von oben klar anders, wahrscheinlich eigene Basis |

Hinweis zu 7–9: Als Variante würden sie den **Bären-Clip-Satz** teilen (Gang, Aufrichten, Prankenhieb). Ihre bisher
geplanten Muster (Dachs, Eber, Echse) entfielen dann oder bräuchten Zusatz-Clips auf demselben Rig.

**Nutzer: bestätigen / streichen / ersetzen / ergänzen** (pro Zeile)

## 2. Einsortier-Tabelle

> **Vorschlag Claude, Nutzer entscheidet.** Nur nach den 4 Schichten umsortiert (2026-11-21), nichts neu
> entschieden. Spalte 4 = bisherige Tönung + Shader/Partikel. Spalte 2: Die Bedeckung war bisher kein eigener Punkt;
> „?“ = bisheriger Eintrag, der eher Bedeckung als Accessoire sein könnte. Körperstelle „–“ = bisher nicht genannt.

| Variante | 1 Statur-Regler | 2 Bedeckung (+ Einstellungen) | 3 Accessoires (Körperstelle + Einstellungen) | 4 Material/Textur-Ebenen | Eigene Basis? |
|---|---|---|---|---|---|
| Rimehide Bear | – (Referenz 1,0) | wie Basis (Frage 5) | Eisplatten (Rücken, Schultern, Unterarme), Eissplitter-Kamm (–) | Weiß/Stahlblau · Eis halbtransparent · Partikel: Frost-Atem | nein |
| Mossback Bear | – | wie Basis (Frage 5) | Moospolster (–), Pilze (–) | Dunkelbraun/Moosgrün · Partikel: Gift-Sporen | nein |
| Cave Bear | etwas schwerer Kopf | wie Basis (Frage 5) | Tropfstein-Platten (–), kleine Kristalle (–) | Schwarzbraun · Kristall-Glimmen schwach | nein |
| Slagback Bear | – | wie Basis (Frage 5) | Basaltplatten (–), Schlackebrocken (–) | Rußschwarz · Glutrisse (Emission) · Partikel: Funken | nein |
| Cragplate Bear | Größe 1,05, Buckel höher | wie Basis (Frage 5) | Steinplatten (–), Felszacken (–) | Steingrau/Braun · Partikel: Staub beim Stampfen | nein |
| Elder Rimehide | Größe 1,5, Schultern breiter | wie Basis (Frage 5) | Eiszacken-Krone (Kopf), Schulterdornen (Schultern) | Biom-Farbe + Rim-Light · Frost-Aura | nein |
| Quillback Burrower | Beine kürzer, Körper länger/flacher, Vorderkrallen größer, Kopf spitzer | Stachelmantel? | Steinplatten (Schulter) | Steingrau/Dunkelbraun, heller Nasenstreifen · Partikel: Stachel-Salve, Erdbrocken beim Eingraben | eher nein |
| Stone Boar | Schnauze länger, Hinterbeine kürzer, Buckel höher | rostrote Haut? | Steinplatten (–), Knochenzacken (Buckel), **Hauer** (Maul) | Schiefergrau/Violettschwarz · Partikel: Staub beim Rammen | Grenzfall (Schnauze + Hufe) |
| Shore Lurker | Beine viel kürzer, Körper flacher, Kopf breiter, Schwanz länger | wie Basis (Frage 5) | Hauer (Maul), Stachelmähne (Nacken), Knochenplatten (–) | Anthrazit/Schiefer · nasser Glanz · Partikel: Tropfen | **wahrscheinlich ja** (liegende Haltung, seitliche Beine) |

## 3. Basis-Kreatur (Vorschlag)

Was alle gemeinsam haben – nur das geht zu Tripo (P-Serie, Low-Poly):
- **Silhouette:** massiger, vorderlastiger Vierbeiner mit hohem **Muskelbuckel über den Schultern**, runder Rücken,
  der nach hinten abfällt. Von oben: breite Schultern, schmalere Hüfte.
- **Körperbau:** tiefer Brustkorb, kräftiger kurzer Hals, Bauch frei vom Boden.
- **Gliedmaßen:** vier dicke, säulenartige Beine, vorn etwas kräftiger; breite Pranken mit kurzen, dunklen Krallen.
- **Kopf-Grundform:** breit und schwer, mittellange stumpfe Schnauze, kleine Augen, kleine runde Ohren, Maul mit
  sichtbaren Fängen (Ausprägung siehe Frage 1).
- **Schwanz:** kurzer Stummel (siehe Frage 2).
- **Oberfläche:** einheitliches, kurzes, grobes Fell bzw. Haut in neutralem Mittelgrau, damit Tönung greift.
  *(Nach dem Schichtmodell vermutlich „nackte“ neutrale Haut, Fell als eigene Schicht – siehe Frage 5.)*

Bewusst **NICHT** im Mesh: Eis, Stacheln, Platten, Moos, Pilze, Kristalle, Hauer, Mähne, zottelige Fellbüschel.
**Rücken und Schultern bleiben glatte Ansatzflächen** für die Anbauteile.

**Pose (Regeln CLAUDE.md 1a):** steht auf allen vier Beinen, alle Beine in voller Länge sichtbar, hüftbreit und
parallel, Hinterbeine nicht gespreizt, Beine berühren sich nicht; nicht aufgerichtet, nicht sitzend oder hockend;
Kopf gerade nach vorn, Schwanz gerade nach hinten, Körper symmetrisch und nicht verdreht.

## 4. Offene Fragen an den Nutzer

1. **Kopf:** eher klar Bär (kurze Schnauze, runde Ohren) oder neutraler (etwas längere, breite Schnauze), damit
   Eber und Lurker als Variante passen?
2. **Schwanz:** kurzer Bärenstummel oder ein mittellanger Schwanz, der sich per Slider verlängern lässt (Lurker,
   Burrower)?
3. **Größen-Slider:** welche Spanne? Vorschlag 0,8–1,5 (Jungtier bis Elite), Beinlänge ±25 %.
4. **Grenzfälle:** Sollen Quillback Burrower, Stone Boar und Shore Lurker wirklich auf diese Basis – und dann den
   Bären-Clip-Satz teilen statt eigener Muster (Dachs, Eber, Echse)?
5. **Oberfläche der Basis** (seit dem Schichtmodell 2026-11-21 nur noch eine Bestätigung): **Vermutung Claude:**
   Die Basis bleibt ein „nackter“ Grundkörper mit neutraler, glatter Haut; Fell (Bär, Burrower), Leder/Haut (Eber,
   Lurker) oder Platten sind eine eigene Schicht (Bedeckung) und kommen nicht ins Tripo-Mesh. Passt das?
   *(Bisherige Frage: Fell-Textur oder neutrale ledrige Haut als Basis?)*
