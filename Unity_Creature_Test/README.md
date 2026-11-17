# Unity-Testszene: Kreaturen-Viewer

Zeigt alle fertigen Kreaturen der Pipeline (`../creatures/*/output/*.fbx`) in Unity 6 (6000.3.15f1, Built-in Render Pipeline).

## Benutzen
1. Unity Hub → **Add project from disk** → diesen Ordner (`01_kreatur_pipeline/Unity_Creature_Test`) wählen, mit 6000.3.15f1 öffnen.
2. Beim Öffnen importiert das Projekt automatisch alle Kreaturen und öffnet die Szene `Assets/CreatureViewer/Generated/CreatureViewer.unity`.
   Neu exportierte/geänderte Kreaturen werden beim nächsten Öffnen erkannt – oder sofort über das Menü **Kreaturen › Alle importieren + Szene bauen**.
3. **Play** drücken. Links das Bedienfeld:
   - **Kreatur**: Dropdown – nach dem Wechsel läuft automatisch **Walk**
   - **Animation**: 9 Buttons (Walk, Run, Idle, Ready, TurnLeft, TurnRight, Attack1, Hit, Death) – auch Tasten **1–9**
   - **Auto-Loop** an/aus (aus = Clip läuft einmal und bleibt am Ende stehen)
   - **Tempo** 0,05–3× (Schnellwahl 0,1 / 0,25 / 0,5 / 1 / 2×)
   - **Zeitleiste** zum Scrubben, Pause, Neustart, Frame vor/zurück
   - **Kamera**: ARPG (schräg von oben wie im Spiel), Seite, Vorne, Oben · rechte Maustaste ziehen = drehen, Mausrad = Zoom

## Was beim Import passiert (`Assets/CreatureViewer/Editor/CreatureImporter.cs`)
- FBX + Clip-Bericht (welche Clips Schleifen sind) werden nach `Assets/Creatures/<Name>/` kopiert.
- Import als **Generic**-Rig, Animationen **unkomprimiert** (genau wie in Blender gebacken), Schleifen laut Pipeline.
- Die Texturen stecken in der FBX ohne Dateiendung → werden herausgezogen, Endung ergänzt, und es entsteht **ein** Material pro Kreatur (Standard-Shader, Farbe + Normal-Map).
- Kreaturen stehen auf dem Boden (Ursprung der Modelle liegt in der Körpermitte → wird beim Anzeigen angehoben).
- `Assets/Creatures` und `Assets/CreatureViewer/Generated` sind erzeugt und nicht versioniert.

## Frei hängende Teile (Lappen, Fühler) – Shader `Creature/Standard Dangling`
- Kreaturen, deren Mesh in der Pipeline markiert wurde (`[dangling]` in der creature.toml, siehe `../rigging/README.md`),
  liefern neben der FBX ein `<Name>_dangling.json`. Der Importer gibt ihnen dann automatisch statt „Standard“ den Shader
  `Assets/CreatureViewer/Shaders/CreatureDangling.shader`: gleicher Look (Farbe, Normal-Map, Glätte 0,2), aber markierte
  Vertices (Vertex-Farbe R = Gewicht, G = Phase) schwingen weich – ohne Knochen, zusätzlich zu jeder Animation, Schatten
  schwingen mit. Alle anderen Kreaturen bleiben beim normalen Standard-Shader.
- Material-Slider (Startwerte aus `_dangling.json`): **Ausschlag an der Spitze (m)**, **Tempo (Schwingungen/s)**,
  **Verzögerung Ansatz → Spitze**, **Anteil auf-ab**. Zum Ausprobieren im Play-Modus einfach am Material
  `Assets/Creatures/<Name>/<Name>.mat` ziehen (wird beim nächsten Import wieder auf die Pipeline-Werte gesetzt –
  dauerhaft ändern über `[dangling]` in der creature.toml).
- Kosten: kein zusätzlicher Draw Call, kein Knochen, ~20 Rechenschritte pro Vertex im Vertex-Shader.
- Prüfbilder (headless): `<Name>_dangle_<side|arpg|below>_t0..t3.png` – gleiche Pose, Shader-Zeit auf 4 Viertel-
  Schwingungen gesetzt (`Shader.SetGlobalFloat("_DangleTestTime")`); was sich zwischen den Bildern bewegt, kommt aus dem Shader.

## Headless (für Claude / Prüfung)
```
& "D:\Unity\6000.3.15f1\Editor\Unity.exe" -batchmode -projectPath "<pfad>\01_kreatur_pipeline\Unity_Creature_Test" -executeMethod CreatureImporter.Batch -logFile <log>
```
Optional `-creaturesRoot <ordner>` (andere Kreatur-Quelle, z. B. Testbauten aus `--work`) und `-shotsDir <ordner>`.
Für Prüfungen, während das Projekt beim Nutzer offen ist: Kopie neben dem Projekt anlegen (Assets ohne `Creatures*` und
`CreatureViewer/Generated*`, dazu Packages + ProjectSettings), dort laufen lassen, danach löschen.
Importiert, baut die Szene, rendert Prüfbilder nach `../temp/unity_shots/` (ARPG, Seite, Oben, schräg von hinten – Walk; Oben/Hinten zeigen einseitige Flächen wie Flügel) und prüft, dass sich in jedem Clip Knochen bewegen.
Stand 2026-11-17: 9 Kreaturen, 81 Clips, alle bewegen sich; Texturen + Bodenkontakt per Prüfbild kontrolliert.

## Bekannt / offen
- Built-in Render Pipeline (einfachster Weg für den Test). Falls das Spiel URP nutzt, Materialien später auf URP/Lit umstellen.
- Bedienung bewusst mit IMGUI (keine Zusatzpakete) – reicht für einen Test-Viewer.
