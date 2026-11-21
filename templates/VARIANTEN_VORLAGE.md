# {{TITEL}} – Varianten zuerst (Schritt 0)

Stand {{DATUM}}. Vorbefüllt aus `creatures/roster.toml` (`varianten`, `base_look`) von
`python scripts/make_prompts.py {{ID}} --stage variants`. Diese Datei wird danach **nie überschrieben** – hier wird
von Hand weitergearbeitet. Vorlage: `templates/VARIANTEN_VORLAGE.md`.

Ablauf: **Nutzer legt 5–6 Varianten fest** (Grundform, Biome, Elite) → optional Varianten-Bogen in ChatGPT
(`prompts_varianten.md`) → Basis eindampfen → Unterschiede einsortieren → Ergebnis in `creatures/roster.toml`
eintragen (`varianten`, `base_look`) → Stufe 1 Design-Bild der **Basis** → Stufe 2 4 Ansichten → Prüfung A → Tripo
(erst `--dry-run`, dann nach OK).

Kurz erklärt – Varianten sind ein **Schichtmodell** (Nutzer 2026-11-21):
1. *Statur* = Standard-Statur der Kreatur plus Regler für Größe, Proportionen (länger, gestauchter) und Gewicht
   (dick/dünn).
2. *Bedeckung* = die Haupt-Oberfläche (Fell, Federn, Leder, Platten …) mit eigenen Einstellungen: Länge, Dichte,
   Form, Farbe.
3. *Accessoires* = Zusatzteile (Hörner, Schuppen, Pilze, Rücken-Aufsätze, Gehänge …): erst die **Körperstellen**
   wählen, dann die Einstellungen pro Accessoire. Per Blender Geometry Nodes mit Schiebereglern erzeugt und starr an
   den nächsten Knochen gehängt; Gehänge schwingen nach.
4. *Material/Textur-Ebenen* = färbt bzw. stilisiert alles Vorherige, auch mehrere Ebenen übereinander (Farbe,
   Muster, Glut, Frost, Nässe); Partikel (Funken, Sporen) in Unity.

*Eigene Basis* = die Silhouette weicht so stark ab, dass die Variante ein eigenes Tripo-Modell braucht.

## 1. Varianten-Entwurf

| # | Variante | Art | Biom | Kurzbeschreibung |
|---|---|---|---|---|
{{ENTWURF}}

**Nutzer: bestätigen / streichen / ersetzen / ergänzen** (pro Zeile).

## 2. Einsortier-Tabelle

> **Vorschlag Claude, Nutzer entscheidet.** Regel nach Schichten: größer/länger/gestauchter/dicker/dünner →
> 1 Statur · andere Haupt-Oberfläche (Fell ↔ Leder ↔ Platten) → 2 Bedeckung · Teile dazu/weg → 3 Accessoires
> (mit Körperstelle) · Farbe, Muster, Glut/Frost/Gift → 4 Material/Textur-Ebenen · starke Silhouetten-Abweichung →
> eigene Basis.

| Variante | 1 Statur-Regler | 2 Bedeckung (+ Einstellungen) | 3 Accessoires (Körperstelle + Einstellungen) | 4 Material/Textur-Ebenen | Eigene Basis? |
|---|---|---|---|---|---|
| … | … | … | … | … | … |

**Vorbefüllt aus `roster.toml`** (Feldansicht von `make_prompts.py`, Spalten = Feldnamen des Skripts). Von hier in
die Schichten-Tabelle oben übertragen.

> Notiz – Zuordnung der Skript-Felder zu den Schichten (Feldnamen bleiben): `size` + `slider` → 1 Statur ·
> `addons` → 3 Accessoires (bzw. 2 Bedeckung, wenn es die Haupt-Oberfläche ist, z. B. Platten am ganzen Körper) ·
> `tint` → 4 Material/Textur (Farbe) · `effect` → 4 Material/Textur (Glut, Frost …) bzw. Unity-Partikel ·
> `eigene_basis` → eigene Basis. Für Bedeckung und Körperstellen gibt es noch kein eigenes Feld.

| Variante | `tint` (→ 4) | `addons` (→ 3/2) | `size` + `slider` (→ 1) | `effect` (→ 4) | `eigene_basis` |
|---|---|---|---|---|---|
{{EINSORTIER}}

## 3. Basis-Kreatur

Was alle gemeinsam haben – nur das geht zu Tripo (P-Serie, Low-Poly):
- **Silhouette** (von schräg oben): …
- **Körperbau:** …
- **Gliedmaßen** (Anzahl, Form): …
- **Kopf-Grundform:** …
- **Schwanz:** …
- **Oberfläche:** „nackter“ Grundkörper, einheitlich neutral getönte glatte Haut – die Bedeckung (Schicht 2) und
  die Material-Ebenen (Schicht 4) kommen darüber. *(Vermutung Claude 2026-11-21, Nutzer bestätigt noch – BACKLOG
  G10/Q8.)*

Bewusst **NICHT** im Mesh (kommt als Bedeckung oder Accessoire): {{NICHT_IM_MESH}}.
Die Flächen, an denen Accessoires sitzen, bleiben **glatte Ansatzflächen**.

**Basis-Beschreibung** (`base_look` in `roster.toml`, Englisch, qualitativ, keine Zahlen – ersetzt `look` in
Stufe 1 und 2):

> {{BASIS}}

**Pose (CLAUDE.md 1a):** {{POSE}}. Alle Gliedmaßen in voller Länge sichtbar und frei – nie sitzend, hockend,
gefaltet oder untergeschlagen.

## 4. Offene Fragen an den Nutzer

1. …
