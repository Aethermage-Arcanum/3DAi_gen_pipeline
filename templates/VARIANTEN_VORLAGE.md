# {{TITEL}} – Varianten zuerst (Schritt 0)

Stand {{DATUM}}. Vorbefüllt aus `creatures/roster.toml` (`varianten`, `base_look`) von
`python scripts/make_prompts.py {{ID}} --stage variants`. Diese Datei wird danach **nie überschrieben** – hier wird
von Hand weitergearbeitet. Vorlage: `templates/VARIANTEN_VORLAGE.md`.

Ablauf: **Nutzer legt 5–6 Varianten fest** (Grundform, Biome, Elite) → optional Varianten-Bogen in ChatGPT
(`prompts_varianten.md`) → Basis eindampfen → Unterschiede einsortieren → Ergebnis in `creatures/roster.toml`
eintragen (`varianten`, `base_look`) → Stufe 1 Design-Bild der **Basis** → Stufe 2 4 Ansichten → Prüfung A → Tripo
(erst `--dry-run`, dann nach OK).

Kurz erklärt: *Tönung* = nur Farbe ändern · *Anbauteile* = Zusatzteile (Platten, Stacheln, Moos …), per Blender
Geometry Nodes mit Schiebereglern erzeugt und starr an einen Knochen gehängt · *Proportions-Slider* = Teile dicker,
länger, größer ziehen · *Shader/Partikel* = Leuchten, Glut, Frost-Nebel in Unity · *eigene Basis* = die Silhouette
weicht so stark ab, dass die Variante ein eigenes Tripo-Modell braucht.

## 1. Varianten-Entwurf

| # | Variante | Art | Biom | Kurzbeschreibung |
|---|---|---|---|---|
{{ENTWURF}}

**Nutzer: bestätigen / streichen / ersetzen / ergänzen** (pro Zeile).

## 2. Einsortier-Tabelle

> **Vorschlag Claude, Nutzer entscheidet.** Regel: nur Farbe → Tönung · Teile dazu/weg → Anbauteile · dicker,
> größer, längere Hörner → Proportions-Slider · Glut/Frost/Gift → Shader/Partikel · starke Silhouetten-Abweichung
> → eigene Basis.

| Variante | Tönung | Anbauteile (Geometry Nodes) | Proportions-Slider | Shader/Partikel (Unity) | Eigene Basis nötig? |
|---|---|---|---|---|---|
{{EINSORTIER}}

## 3. Basis-Kreatur

Was alle gemeinsam haben – nur das geht zu Tripo (P-Serie, Low-Poly):
- **Silhouette** (von schräg oben): …
- **Körperbau:** …
- **Gliedmaßen** (Anzahl, Form): …
- **Kopf-Grundform:** …
- **Schwanz:** …
- **Oberfläche:** einheitlich und neutral getönt, damit die Tönung greift.

Bewusst **NICHT** im Mesh (kommt als Anbauteil): {{NICHT_IM_MESH}}.
Die Flächen, an denen Anbauteile sitzen, bleiben **glatte Ansatzflächen**.

**Basis-Beschreibung** (`base_look` in `roster.toml`, Englisch, qualitativ, keine Zahlen – ersetzt `look` in
Stufe 1 und 2):

> {{BASIS}}

**Pose (CLAUDE.md 1a):** {{POSE}}. Alle Gliedmaßen in voller Länge sichtbar und frei – nie sitzend, hockend,
gefaltet oder untergeschlagen.

## 4. Offene Fragen an den Nutzer

1. …
