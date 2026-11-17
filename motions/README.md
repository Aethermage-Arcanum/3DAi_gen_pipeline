# Bewegungsmuster (Motion Styles)

**Struktur:** Skelett → Bewegungsmuster → Clips

```
motions/
  <skelett>/                 z. B. crawler, quadruped, legless, flyer
    <muster>/                z. B. ant, crab · wolf, leopard, deer, badger · viper, cobra, centipede
      style.toml             alle Parameter (Slider) des Musters + dokumentierte Varianten
      *.py                   Generator der Clips dieses Musters
      README.md              Naturreferenzen + was dieses Muster ausmacht
```

- **Skelett** = Knochen-Standard eines Bauplans (gleiche Knochennamen für alle Monster dieses Bauplans).
- **Bewegungsmuster** = *wie* sich ein Tiertyp bewegt und kämpft. Hier liegen alle Clips (Walk, Run, Idle, Attack …).
- **Clips** werden pro Monster aus Muster + Monster-Geometrie **gebacken** und heißen `<Skelett>_<Muster>_<Clip>`, z. B. `Crawler_Ant_Walk`. In Unity teilen sich alle Monster mit gleichem Skelett und Muster denselben Animator-Aufbau.

## Variante oder eigenes Muster?
- **Variante** (nur Variablen): Das Tier bewegt sich nach denselben Regeln, nur mit anderen Werten, etwa Beinzahl, Tempo, Schrittlänge, Haltung oder Ausschlag. → als `[variants.<name>]` in der `style.toml` des Musters dokumentieren.
  Beispiel: **Spinne** ist eine Variante von **Ant**. Mit 8 statt 6 Laufbeinen entsteht aus derselben Gruppenregel automatisch der alternierende Vierfuß-Gang, und die Taster entfallen.
- **Eigenes Muster**: Das Grundverhalten ist anders, also Laufrichtung, Bein-Koordination, Haltung oder vor allem **Angriffsmechanik**. Dann reicht eine Variable nicht.
  Beispiel: **Crab** läuft seitwärts. Die Beine der führenden und der nachziehenden Seite haben verschiedene Schrittfolgen (Winkerkrabbe: führend 2-4-3-5, nachziehend 2-5-3-4, im Mittel ≈ alternierender Vierfuß). Die Scheren werden beim Laufen vom Boden gehalten, und Angriffe kommen aus den Scheren statt aus dem Maul. → eigenes Muster `crawler/crab`.

## Geplante Muster (Beispiele; gebaut: ant, crab)
| Skelett | Muster | Kern-Unterschied |
|---|---|---|
| crawler | **ant** ✅ | Dreifuß/Vierfuß vorwärts, Biss mit Mandibeln, Hinterleib für Stich/Säure. Varianten: spider, beetle, scorpion (?) |
| crawler | **crab** ✅ (validiert) | Seitwärtsgang per Fuß-IK, eigene Schrittfolge je Seite, Scheren-Angriffe, Scheren beim Laufen erhoben |
| quadruped | wolf | Trab/Galopp, Biss nach Anlauf, Rudel-Haltung |
| quadruped | leopard | Schleichen, geduckt, Sprung-Angriff (Pounce), Prankenhieb |
| quadruped | deer | Passgang/Sprünge, Geweih-Stoß, Fluchtverhalten |
| quadruped | badger | niedrig, watschelnd, Grab-/Krallenangriff, stur |
| legless | viper | seitliches Schlängeln, Schlag aus der S-Kurve |
| legless | cobra | aufgerichteter Vorderkörper, Schild spreizen, Biss von oben |
| legless | centipede | viele Beine in Wellen (metachronal), eigentlich eher ein Krabbler-Grenzfall |

## Regeln (gelten für jedes Muster)
1. **Naturbeobachtung zuerst:** Pro Muster und pro Clip Referenzen suchen und im README des Musters verlinken.
2. **Fake it:** Es muss aus der Top-down-Kamera gut aussehen, nicht biologisch exakt sein.
3. **Selbstprüfung pro Clip:** Füße rutschen/schweben nicht (wo sie stehen sollen), Schleife nahtlos, keine Gelenk-Lücken, Gegentest nach Export.

## Baukasten
`crawler/crawler_kit.py` enthält alles, was die Krabbler-Muster gemeinsam nutzen: Bein-Achsen, Gieren/Heben/Falten, Planar- und Fuß-IK, Fühler-Stabilisierung, Boden-Begrenzung, gemeinsamer Tod, Backen + Selbstprüfung. Ein neues Muster definiert nur noch seine Clips.
