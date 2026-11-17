# Autonomer Auftrag (2026-11-17, Nutzer mehrere Stunden abwesend)

**Auftrag:** Die Kreaturen aus ROADMAP_20_KREATUREN.md §7 in dieser Reihenfolge gründlich durch die Pipeline bringen:
1. Ravine Stalker (quadruped/wolf)
2. Eel Stalker (legless/cobra)
3. Dune Raptor (biped_raptor/raptor)
4. Void Manifestation (floater/tentacle)
5. Scorpion Matriarch (crawler + Schwanz/scorpion)
6. Needle Wasp (crawler + Flügel/wasp)
7. ~~Flesh Titan~~ → **übersprungen**, macht der Nutzer zusammen mit Claude
8. Reef Snapper (quadruped/lizard)
9. Hollow Stag (quadruped/deer)

**Regeln vom Nutzer:**
- Zeit nehmen, nacheinander, **immer selbst prüfen** (Messwerte + Renders), iterieren.
- **So viel Aufwand wie möglich nach Blender verlagern** (eigenes Rig + prozedurale Animation; Tripo nur Mesh + Textur).
- **Tripo-Budget: max. 1.500 Credits gesamt** (inkl. Neu-Generierungen). Vor jedem bezahlten Lauf `--dry-run`, Guthaben mitprotokollieren. Ist das Budget erreicht → stoppen.
- **Nach jeder fertigen Kreatur committen UND auf GitHub pushen** (origin/main).
- Naturbeobachtung zuerst: Videos/Referenzen zum Vorbild (`[motion] vorbild` in creature.toml) suchen und im README des Musters verlinken.
- Struktur Skelett → Bewegungsmuster → Clips beibehalten (motions/<skelett>/<muster>/), MVP-Umfang wie Ant (9 Clips).
- Alle 20 Minuten Wecker: bei Stillstand weitermachen.
- **Zum Abschluss jeder Kreatur ein GIF (Walk oder Attack) per SendUserFile an den Nutzer schicken.**

## Fortschritt (wird laufend aktualisiert)
| # | Kreatur | Tripo | UV | Rig | Clips | Export | Push | Credits |
|---|---|---|---|---|---|---|---|---|
| 1 | Ravine Stalker | ✅ | ✅ Tripo-UV | ✅ quadruped (30 Kn.) | ✅ 9/9 wolf | ✅ | ✅ | 110 |
| 2 | Eel Stalker | ✅ | ✅ Tripo-UV (manuell) | ✅ legless (17 Kn.) | ✅ 9/9 cobra | ✅ | ✅ | 110 |
| 3 | Dune Raptor | ✅ | ✅ Tripo-UV | ✅ biped_raptor (26 Kn.) | ✅ 9/9 raptor | ✅ | ✅ | 110 |
| 4 | Void Manifestation | ✅ | ✅ Tripo-UV | ✅ floater (19 Tentakel) | ✅ 9/9 tentacle | ✅ | ✅ | 110 |
| 5 | Scorpion Matriarch | ✅ | ✅ Tripo-UV | ✅ multileg (59 Kn., 5 Beinpaare) | ✅ 9/9 scorpion | ✅ | ✅ | 110 |
| 6 | Needle Wasp | ✅ | ✅ Tripo-UV | ✅ flyer (13 Ketten) | ✅ 9/9 wasp | ✅ | ✅ | 110 |
| 8 | Reef Snapper | ✅ | ✅ Tripo-UV | ✅ quadruped (Brücke getrennt) | ✅ 9/9 lizard | ✅ | ✅ | 110 |
| 9 | Hollow Stag | ✅ | | | | | | 110 |

Ausgegebene Credits gesamt: 880 / 1.500 (Guthaben 1.475)
