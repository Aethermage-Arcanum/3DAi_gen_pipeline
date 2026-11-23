using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Feste Werte aus docs/VARIANTEN_SPEC.md (Regler, Bereiche, Ampel-Zonen, Standardwerte, Budget).
    /// Eine Stelle für alles, damit Fenster, Builder und Batch dieselben Zahlen benutzen.</summary>
    public static class VkSpec
    {
        public const string ToolVersion = "0.4.0";   // 0.3.0 = G14 Nachschwingen (weichheit, TEXCOORD1), 0.4.0 = zwei Ebenen-Gruppen
        /// <summary>2 = Material-Ebenen in zwei Gruppen: „ebenen“ wirken nur auf Haut + Bedeckung, „ebenen_accessoires“ nur auf
        /// Accessoires (Format 1: eine Liste für alles, Accessoires bekamen die Maske ihres Ansatzpunkts).</summary>
        public const int FormatVersion = 2;

        // ------------------------------------------------------------------ Schicht 1: Statur (Spec 1.2 / 1.3)
        public enum Typ { G, K, S }

        public class Regler
        {
            public string feld, name; public Typ typ;
            public float min, max;          // Bereich laut Spec
            public float gruenMin, gruenMax; // 🟢 Clips teilen
            public float gelbMin, gelbMax;   // 🟡 Clips teilen + Korrektur → Regler-Grenze (E3)
            public string hinweis;
            public float SliderMin => System.Math.Max(min, gelbMin);
            public float SliderMax => System.Math.Min(max, gelbMax);
        }

        static Regler R(string f, string n, Typ t, float min, float max, float gMin, float gMax, float yMin, float yMax, string h = "")
            => new Regler { feld = f, name = n, typ = t, min = min, max = max, gruenMin = gMin, gruenMax = gMax, gelbMin = yMin, gelbMax = yMax, hinweis = h };

        public static readonly Regler[] Statur =
        {
            R("groesse", "Gesamtgröße", Typ.G, 0.5f, 2f, 0.5f, 2f, 0.5f, 2f, "Laufgeschwindigkeit im Spiel × Größe"),
            R("koerper_laenge", "Körperlänge", Typ.K, 0.8f, 1.4f, 0.9f, 1.1f, 0.8f, 1.2f, "Vorder-/Hinterfüße treten ineinander"),
            R("rumpf_hoehe", "Rumpfhöhe", Typ.S, 0.6f, 1.3f, 0.75f, 1.3f, 0.6f, 1.3f, "unter 0,75 schleift der Bauch"),
            R("rumpf_dicke", "Rumpfdicke", Typ.S, 0.8f, 1.3f, 0.8f, 1.15f, 0.8f, 1.25f, "Beine durchdringen Brust/Bauch"),
            R("buckel", "Buckel", Typ.S, 0f, 1.6f, 0f, 1.6f, 0f, 1.6f),
            R("glied_dicke", "Gliederdicke", Typ.S, 0.8f, 1.3f, 0.8f, 1.15f, 0.8f, 1.25f, "Beine durchdringen Brust/Bauch"),
            R("bein_laenge_vorn", "Beinlänge vorn", Typ.K, 0.6f, 1.3f, 0.9f, 1.1f, 0.8f, 1.2f, "Füße schweben/sinken ein"),
            R("bein_laenge_hinten", "Beinlänge hinten", Typ.K, 0.6f, 1.3f, 0.9f, 1.1f, 0.8f, 1.2f, "Füße schweben/sinken ein"),
            R("spur_breite", "Spurbreite", Typ.K, 0.8f, 1.6f, 0.9f, 1.1f, 0.8f, 1.25f, "Füße rutschen seitlich"),
            R("pranken_vorn", "Pranken vorn", Typ.K, 0.8f, 1.6f, 0.8f, 1.3f, 0.8f, 1.5f, "Pranken treffen sich"),
            R("pranken_hinten", "Pranken hinten", Typ.K, 0.8f, 1.5f, 0.8f, 1.3f, 0.8f, 1.5f, "Pranken treffen sich"),
            R("hals_laenge", "Halslänge", Typ.K, 0.7f, 1.5f, 0.8f, 1.25f, 0.7f, 1.5f, "Biss-Reichweite (Hitbox) ändert sich"),
            R("kopf_groesse", "Kopfgröße", Typ.K, 0.7f, 1.4f, 0.7f, 1.4f, 0.7f, 1.4f),
            R("kopf_breite", "Kopfbreite", Typ.S, 0.8f, 1.5f, 0.8f, 1.5f, 0.8f, 1.5f),
            R("schnauze_laenge", "Schnauzenlänge", Typ.S, 0.8f, 1.6f, 0.8f, 1.6f, 0.8f, 1.6f),
            R("schwanz_laenge", "Schwanzlänge", Typ.K, 0.5f, 2f, 0.5f, 1.5f, 0.5f, 2f, "über 1,5 wirkt der Stummel-Clip steif"),
            R("schwanz_dicke", "Schwanzdicke", Typ.K, 0.6f, 1.6f, 0.6f, 1.6f, 0.6f, 1.6f),
        };

        public enum Ampel { Gruen, Gelb, Rot }

        public static Ampel Zone(Regler r, float v)
        {
            if (v >= r.gruenMin - 1e-4f && v <= r.gruenMax + 1e-4f) return Ampel.Gruen;
            if (v >= r.gelbMin - 1e-4f && v <= r.gelbMax + 1e-4f) return Ampel.Gelb;
            return Ampel.Rot;
        }

        /// <summary>Statur-Ampel (schlechteste Farbe aller Regler, dazu der Unterschied Beinlänge vorn ↔ hinten).</summary>
        public static Ampel StaturAmpel(JObj statur, out List<string> gruende)
        {
            gruende = new List<string>();
            var worst = Ampel.Gruen;
            foreach (var r in Statur)
            {
                var z = Zone(r, statur.F(r.feld, 1f));
                if (z > Ampel.Gruen) gruende.Add($"{r.name} {statur.F(r.feld, 1f):0.00} ({(z == Ampel.Gelb ? "gelb" : "rot")})");
                if (z > worst) worst = z;
            }
            float v = statur.F("bein_laenge_vorn", 1f), h = statur.F("bein_laenge_hinten", 1f);
            float d = System.Math.Abs(v - h) / System.Math.Min(v, h);
            var dz = d <= 0.08f ? Ampel.Gruen : d <= 0.15f ? Ampel.Gelb : Ampel.Rot;
            if (dz > Ampel.Gruen) gruende.Add($"Beinlänge vorn↔hinten {d * 100:0} % ({(dz == Ampel.Gelb ? "gelb" : "rot")})");
            if (dz > worst) worst = dz;
            return worst;
        }

        // ------------------------------------------------------------------ Schicht 3: Accessoires (Spec 3.3 / 3.4)
        public static readonly string[] Verteilungen = { "einzeln", "streuen", "cluster", "reihe", "kranz" };
        public static readonly string[] Ausrichtungen = { "normale", "oben", "hinten", "aussen", "knochen", "unten" };
        public static readonly string[] Stellen = { "oben", "rand_unten" };
        public static readonly string[] Bindungen = { "anker", "knochen", "haut" };

        public class TypStd { public string[] zonen; public string verteilung; public int anzahl; public float groesse; }

        public static readonly Dictionary<string, TypStd> AccTypen = new Dictionary<string, TypStd>
        {
            ["basaltbrocken"] = new TypStd { zonen = new[] { "buckel", "ruecken_mitte", "kruppe", "schulter_l" }, verteilung = "cluster", anzahl = 1, groesse = 0.13f },
            ["steinplatte"] = new TypStd { zonen = new[] { "stirn", "schulter_l", "unterarm_l", "oberschenkel_l", "ruecken_mitte" }, verteilung = "streuen", anzahl = 2, groesse = 0.12f },
            ["felszacke"] = new TypStd { zonen = new[] { "rueckenlinie" }, verteilung = "reihe", anzahl = 11, groesse = 0.10f },
            // M2 (Spec 3.4 + 5.3), Startwerte – Formen kommen aus der Baustein-Werkbank (Blender)
            ["kristall"] = new TypStd { zonen = new[] { "buckel", "ruecken_mitte" }, verteilung = "cluster", anzahl = 1, groesse = 0.05f },
            ["eiszacke"] = new TypStd { zonen = new[] { "kopf_oben" }, verteilung = "kranz", anzahl = 7, groesse = 0.06f },
            ["dorn"] = new TypStd { zonen = new[] { "schulter_l", "nacken" }, verteilung = "streuen", anzahl = 3, groesse = 0.06f },
            ["horn"] = new TypStd { zonen = new[] { "kopf_oben" }, verteilung = "einzeln", anzahl = 1, groesse = 0.12f },
            ["eisplatte"] = new TypStd { zonen = new[] { "schulter_l", "unterarm_l", "oberschenkel_l" }, verteilung = "cluster", anzahl = 1, groesse = 0.12f },
            ["knochenplatte"] = new TypStd { zonen = new[] { "ruecken_mitte", "schulter_l" }, verteilung = "streuen", anzahl = 3, groesse = 0.08f },
            ["sinterplatte"] = new TypStd { zonen = new[] { "ruecken_mitte", "schulter_l" }, verteilung = "streuen", anzahl = 2, groesse = 0.12f },
            ["moospolster"] = new TypStd { zonen = new[] { "ruecken_gesamt", "schulter_l", "oberschenkel_l" }, verteilung = "streuen", anzahl = 2, groesse = 0.18f },
            ["pilze"] = new TypStd { zonen = new[] { "buckel", "schulter_l", "kruppe" }, verteilung = "cluster", anzahl = 1, groesse = 0.05f },
            ["grasbueschel"] = new TypStd { zonen = new[] { "ruecken_gesamt" }, verteilung = "streuen", anzahl = 4, groesse = 0.04f },
            ["moosfransen"] = new TypStd { zonen = new[] { "flanke_l" }, verteilung = "streuen", anzahl = 4, groesse = 0.08f },
            ["gehaenge"] = new TypStd { zonen = new[] { "flanke_l", "nacken" }, verteilung = "streuen", anzahl = 2, groesse = 0.10f },
            ["seepocken"] = new TypStd { zonen = new[] { "ruecken_gesamt", "flanke_l" }, verteilung = "cluster", anzahl = 2, groesse = 0.035f },
            ["tang"] = new TypStd { zonen = new[] { "flanke_l" }, verteilung = "streuen", anzahl = 3, groesse = 0.10f },
            ["kette"] = new TypStd { zonen = new[] { "flanke_l", "nacken" }, verteilung = "streuen", anzahl = 2, groesse = 0.12f },
        };

        /// <summary>Accessoire-Eintrag mit allen Standardwerten (Spec 3.3) für einen Typ.</summary>
        public static JObj NeuesAccessoire(string id, string typ)
        {
            AccTypen.TryGetValue(typ, out var t);
            t = t ?? new TypStd { zonen = new[] { "buckel" }, verteilung = "streuen", anzahl = 2, groesse = 0.1f };
            var o = new JObj
            {
                ["id"] = id, ["typ"] = typ, ["formen"] = new List<object>(), ["zonen"] = t.zonen.Take(1).Cast<object>().ToList(),
                ["spiegeln"] = true, ["asymmetrie"] = 0.2, ["verteilung"] = t.verteilung, ["anzahl"] = (long)t.anzahl, ["teile"] = 4L,
                ["von"] = 0.1, ["bis"] = 0.8, ["reihen"] = 1L, ["groesse"] = (double)t.groesse, ["groesse_zufall"] = 0.3,
                ["groesse_verlauf"] = new List<object> { 1.0, 1.0, 1.0 }, ["streckung"] = new List<object> { 1.0, 1.0, 1.0 },
                ["abstand_min"] = 0.02, ["ausrichtung"] = Haengt(typ) ? "unten" : "normale", ["neigung"] = 0.0, ["drehung_zufall"] = 180.0,
                ["kipp_zufall"] = 10.0, ["einsinken"] = 0.25, ["bindung"] = "anker", ["weichheit"] = (double)WeichStdAcc(typ),
                ["farbgruppe"] = "accessoire_a", ["farb_zufall"] = 0.0, ["weg_ab_lod"] = null, ["seed"] = null,
            };
            return o;
        }

        // ------------------------------------------------------------------ G14 Nachschwingen: weichheit (Spec 2.2, 3.3)
        /// <summary>Standard-Weichheit einer Lage: 0 = starr wie Felszacken, 1 = schwingendes Fell.</summary>
        public static float WeichStdLage(string typ)
        {
            switch (typ)
            {
                case "fell": return 0.6f;
                case "federn": return 0.4f;
                case "stacheln": return 0.1f;
                default: return 0f;   // platten
            }
        }

        /// <summary>Standard-Weichheit eines Accessoire-Typs (Gehänge schwingen, alles andere ist starr).</summary>
        public static float WeichStdAcc(string typ)
        {
            switch (typ)
            {
                case "moosfransen": case "tang": case "gehaenge": return 0.9f;
                case "kette": return 0.7f;
                case "barteln": return 0.6f;
                case "grasbueschel": return 0.5f;
                default: return 0f;
            }
        }

        /// <summary>Gehänge: hängen in der Ruhe nach unten (Ausrichtung „unten“) und folgen beim Neigen der Schwerkraft.</summary>
        public static bool Haengt(string typ) => typ == "moosfransen" || typ == "tang" || typ == "gehaenge" || typ == "kette";

        public static float WeichheitLage(JObj l) => Mathf.Clamp01(l.F("weichheit", WeichStdLage(l.S("typ", "fell"))));
        public static float WeichheitAcc(JObj a) => Mathf.Clamp01(a.F("weichheit", WeichStdAcc(a.S("typ", ""))));

        /// <summary>Migration alter Dateien (vor G14): `schwingen` der Lagen und `bewegung`/`schwingen.staerke` der Accessoires
        /// gehen in `weichheit` auf (ein Feld). Die alten Felder hatten noch keine Wirkung: 0/„starr“ war nur der
        /// Platzhalter → Typ-Standard; ein Wert &gt; 0 bzw. „schwingt“ wird übernommen. Gilt für Varianten-Dateien und Presets.</summary>
        public static void Migrate(JObj o)
        {
            if (o == null) return;
            foreach (JObj l in (o.O("bedeckung")?.L("lagen") ?? new List<object>()).OfType<JObj>())
            {
                if (!l.Has("schwingen")) continue;
                float v = l.F("schwingen", 0);
                l.Remove("schwingen");
                if (v > 0 && !l.Has("weichheit")) l["weichheit"] = (double)v;
            }
            foreach (JObj a in (o.L("accessoires") ?? new List<object>()).OfType<JObj>())
            {
                string b = a.Has("bewegung") ? a.S("bewegung", "starr") : null;
                var sw = a["schwingen"];
                a.Remove("bewegung"); a.Remove("schwingen");
                if (b == "schwingt" && !a.Has("weichheit"))
                {
                    float st = sw is JObj so ? so.F("staerke", 1f) : sw != null ? Json.ToF(sw, 1f) : 1f;
                    float std = WeichStdAcc(a.S("typ", ""));
                    a["weichheit"] = (double)Mathf.Round(st * (std > 0 ? std : 0.9f) * 1000f) / 1000.0;
                }
            }
            foreach (var kv in o.O("biome") ?? new JObj()) Migrate(kv.Value as JObj);
        }

        // ------------------------------------------------------------------ Schicht 4: Farbgruppen + Ebenen (Spec 4.2 / 4.3)
        public static readonly string[] Gruppen = { "haut", "bedeckung_1", "bedeckung_2", "accessoire_a", "accessoire_b", "accessoire_c", "horn", "akzent", "augen" };
        public static int GruppeIndex(string g) { int i = System.Array.IndexOf(Gruppen, g); return i < 0 ? 0 : i; }

        public static readonly Dictionary<string, string> GruppenStdFarbe = new Dictionary<string, string>
        {
            ["haut"] = "#9A9A9E", ["bedeckung_1"] = "#8A8A8E", ["bedeckung_2"] = "#7A7A7E", ["accessoire_a"] = "#808084",
            ["accessoire_b"] = "#707074", ["accessoire_c"] = "#606064", ["horn"] = "#2A2A2C", ["akzent"] = "#1E1E20", ["augen"] = "#202020",
        };

        public static readonly string[] EbenenTypen = { "verlauf", "muster", "risse", "ueberzug", "naesse", "rim" };
        public const int MaxEbenen = 8;          // Körper-Ebenen
        public const int MaxAccEbenen = 4;       // Accessoire-Ebenen (Shader-Slots _A0.._A3)
        public const int MaxAccEintraege = 24;   // gezielt ansprechbare Accessoire-Einträge (Bits im float); „alle“ gilt für jede Anzahl
        /// <summary>Farbgruppen, die zum Körper gehören (Körper-Ebenen filtern nur diese).</summary>
        public static readonly string[] KoerperGruppen = { "haut", "bedeckung_1", "bedeckung_2", "horn", "akzent", "augen" };

        /// <summary>Neue Ebene mit Standardwerten (Spec 4.3). acc = Accessoire-Ebene: Ziel „alle“, Maske ohne Zonen.</summary>
        public static JObj NeueEbene(string id, string typ, bool acc = false)
        {
            var e = new JObj { ["id"] = id, ["typ"] = typ, ["an"] = true };
            switch (typ)
            {
                case "verlauf":
                    e["richtung"] = "oben_unten"; e["farbe_a"] = "#FFFFFF"; e["farbe_b"] = "#808080"; e["mischung"] = "ueberlagern";
                    e["mitte"] = 0.5; e["weichheit"] = 0.5; break;
                case "muster":
                    e["art"] = "flecken"; e["farbe"] = "#404040"; e["skala"] = 0.08; e["dichte"] = 0.5; e["kontrast"] = 0.7;
                    e["richtung"] = "quer"; e["verzerrung"] = 0.3; e["mischung"] = "ueberlagern"; e["seed"] = null; break;
                case "risse":
                    e["element"] = "glut"; e["art"] = "risse"; e["farbe"] = "#FF6A10"; e["intensitaet"] = 4.0; e["breite"] = 0.005;
                    e["dichte"] = 0.4; e["verzweigung"] = 0.5; e["hof"] = 0.3; e["puls_frequenz"] = 0.0; e["puls_staerke"] = 0.0; e["seed"] = null; break;
                case "ueberzug":
                    e["art"] = "staub"; e["farbe"] = "#A89A88"; e["menge"] = 0.3; e["kanten"] = 0.4; e["rauschen_skala"] = 0.08;
                    e["rauheit"] = 1.0; e["seed"] = null; break;
                case "naesse":
                    e["menge"] = 0.5; e["glanz"] = 0.8; e["abdunkeln"] = 0.3; break;
                case "rim":
                    e["farbe"] = "#FFD080"; e["intensitaet"] = 1.5; e["breite"] = 0.35; break;
            }
            e["staerke"] = 1.0;
            if (acc) { e["ziel"] = "alle"; e["maske"] = new JObj { ["oben"] = 0.0, ["rauschen"] = 0.0 }; }
            else e["maske"] = new JObj { ["zonen"] = new List<object> { "ganzer_koerper" } };
            return e;
        }

        // ------------------------------------------------------------------ Accessoire-Ebenen: Ziel
        /// <summary>Ziel einer Accessoire-Ebene: "alle" oder { typen: [...], eintraege: [...] } (Vereinigung).</summary>
        public static bool ZielAlle(JObj e) => !(e["ziel"] is JObj) && e.S("ziel", "alle") == "alle";

        /// <summary>Aktive Accessoire-Einträge in der Reihenfolge der aufgelösten Liste (Index = Eintrags-Nummer im Shader).</summary>
        public static List<JObj> AktiveAccessoires(JObj resolved) =>
            (resolved.L("accessoires") ?? new List<object>()).OfType<JObj>().Where(a => a.B("an", true) && a["id"] is string).ToList();

        /// <summary>Trifft die Accessoire-Ebene diesen Eintrag?</summary>
        public static bool ZielTrifft(JObj e, JObj acc)
        {
            if (ZielAlle(e)) return true;
            var z = e["ziel"] as JObj;
            if (z == null) return false;
            return z.Strs("typen").Contains(acc.S("typ", "")) || z.Strs("eintraege").Contains(acc.S("id", ""));
        }

        /// <summary>Kurzer Text für das Fenster: „alle“, „Typen: kristall · Einträge: eis_kamm“, „– (keins)“.</summary>
        public static string ZielText(JObj e)
        {
            if (ZielAlle(e)) return "alle Accessoires";
            var z = e["ziel"] as JObj;
            var t = z?.Strs("typen") ?? new List<string>(); var n = z?.Strs("eintraege") ?? new List<string>();
            if (t.Count + n.Count == 0) return "– (keins: Ebene wirkt nirgends)";
            var parts = new List<string>();
            if (t.Count > 0) parts.Add("Typen: " + string.Join(", ", t));
            if (n.Count > 0) parts.Add("Einträge: " + string.Join(", ", n));
            return string.Join(" · ", parts);
        }

        /// <summary>Alle Accessoire-Einträge der Variante mit id (auch abgeschaltete) – die Zeilen der Häkchen-Liste.</summary>
        public static List<JObj> AlleEintraege(JObj resolved) =>
            (resolved.L("accessoires") ?? new List<object>()).OfType<JObj>().Where(a => a["id"] is string).ToList();

        /// <summary>Häkchen „Ebene wirkt auf diesen Eintrag“ setzen/entfernen. Aus „alle“ wird beim Abwählen die Liste aller
        /// übrigen Einträge; trifft die Ebene den Eintrag über seinen Typ, wird der Typ in seine übrigen Einträge aufgelöst.</summary>
        public static void SetZielEintrag(JObj e, JObj acc, bool on, List<JObj> alle)
        {
            if (ZielTrifft(e, acc) == on) return;
            string id = acc.S("id", ""), typ = acc.S("typ", "");
            if (ZielAlle(e))
            {
                e["ziel"] = new JObj { ["typen"] = new List<object>(), ["eintraege"] = alle.Where(a => a != acc).Select(a => (object)a.S("id", "")).Distinct().ToList() };
                return;
            }
            var z = e["ziel"] as JObj ?? new JObj();
            var t = z.Strs("typen"); var n = z.Strs("eintraege");
            if (on) { if (!n.Contains(id)) n.Add(id); }
            else
            {
                n.RemoveAll(x => x == id);
                if (t.Remove(typ))
                    foreach (var a in alle)
                        if (a != acc && a.S("typ", "") == typ && !n.Contains(a.S("id", ""))) n.Add(a.S("id", ""));
            }
            e["ziel"] = new JObj { ["typen"] = t.Cast<object>().ToList(), ["eintraege"] = n.Cast<object>().ToList() };
        }

        /// <summary>Nach dem Umbenennen eines Eintrags die Ziele der Accessoire-Ebenen nachziehen.</summary>
        public static void RenameZiel(JObj resolved, string alt, string neu)
        {
            foreach (JObj e in (resolved.O("material")?.L("ebenen_accessoires") ?? new List<object>()).OfType<JObj>())
                if (e["ziel"] is JObj z && z.L("eintraege") is List<object> l)
                    for (int i = 0; i < l.Count; i++) if (l[i] as string == alt) l[i] = neu;
        }

        // ------------------------------------------------------------------ Körper-Ebenen: Haut / Bedeckung (Nutzer 2026-11-23)
        // maske.haut      fehlt/true = wirkt auf die Haut (Basis-Mesh inkl. Krallen/Augen-Gruppen), false = nicht
        // maske.bedeckung fehlt/true = alle Bedeckungs-Lagen, false = keine, [lagen-ids] = nur diese Lagen
        // Standard = beide an (Haut und Bedeckung teilen sich die Ebene) – alte Dateien haben die Felder nicht → unverändert.

        /// <summary>Aktive Bedeckungs-Lagen in Blender-Reihenfolge (höchstens 2, Lage-Nummer im Mesh = Index + 1).</summary>
        public static List<JObj> AktiveLagen(JObj resolved) =>
            (resolved.O("bedeckung")?.L("lagen") ?? new List<object>()).OfType<JObj>().Where(l => l.B("an", true)).Take(2).ToList();
        public static string LageId(JObj lage, int index) => lage.S("id", $"lage_{index + 1}");

        public static bool AufHaut(JObj e) => (e.O("maske") ?? new JObj()).B("haut", true);

        /// <summary>Wirkt die Körper-Ebene auf diese Lage? lageId null = Lage ohne Eintrag in der Datei (nur true/false zählt).</summary>
        public static bool AufLage(JObj e, string lageId)
        {
            var v = e.O("maske")?["bedeckung"];
            if (v == null) return true;
            if (v is bool b) return b;
            if (v is List<object> l) return lageId != null && l.OfType<string>().Contains(lageId);
            return true;
        }

        /// <summary>Lagen-Auswahl schreiben: alle an → Feld weg (Standard), keine → false, sonst Liste der ids.</summary>
        public static void SetLagen(JObj mk, List<string> an, List<string> alle)
        {
            if (alle.Count > 0 && alle.All(an.Contains)) mk.Remove("bedeckung");
            else if (an.Count == 0) mk["bedeckung"] = false;
            else mk["bedeckung"] = an.Cast<object>().ToList();
        }

        /// <summary>Bits pro Körper-Ebene: 1 = Haut, 2 = Lage 1, 4 = Lage 2 (für VkBuilder.Combine).</summary>
        public static int AufBits(JObj e, List<string> lagenIds)
        {
            int bits = AufHaut(e) ? 1 : 0;
            for (int k = 0; k < 2; k++) if (AufLage(e, k < lagenIds.Count ? lagenIds[k] : null)) bits |= 2 << k;
            return bits;
        }

        /// <summary>Kurztext für die Ebenen-Zeile: "" (Standard), „nur Haut“, „nur Bedeckung“, „Haut + fell“, „nirgends“.</summary>
        public static string AufText(JObj e, List<string> lagenIds)
        {
            bool h = AufHaut(e);
            var on = lagenIds.Where(id => AufLage(e, id)).ToList();
            bool bedAlle = lagenIds.Count == 0 ? AufLage(e, null) : on.Count == lagenIds.Count;
            if (h && bedAlle) return "";
            if (!h && on.Count == 0 && !(lagenIds.Count == 0 && bedAlle)) return "nirgends";
            string bed = bedAlle ? "Bedeckung" : string.Join(" + ", on);
            if (!h) return "nur " + bed;
            return on.Count == 0 ? "nur Haut" : "Haut + " + bed;
        }

        // ------------------------------------------------------------------ Migration Format 1 → 2 (zwei Ebenen-Gruppen)
        /// <summary>Format 1 → 2 auf der AUFGELÖSTEN Fassung (Preset + Biom + Datei, alte Bedeutung). Bisher wirkte jede Ebene
        /// auch auf die Accessoires (Maske des Ansatzpunkts, nur durch die Farbgruppen gefiltert). Jetzt:
        ///  • jede alte Ebene bleibt Körper-Ebene (gleiche id), der Farbgruppen-Filter behält nur Körper-Gruppen. Hatte sie nur
        ///    Accessoire-Gruppen (z. B. „glut_fugen“ nur accessoire_a), wirkte sie nie auf den Körper → keine Körper-Ebene.
        ///  • wirkte sie sichtbar auf Accessoires, entsteht eine Accessoire-Ebene mit derselben id (→ gleicher Seed, gleiches
        ///    Muster) und denselben Werten. Ziel „alle“, wenn sie alle aktiven Einträge traf, sonst genau die getroffenen.
        ///    „Getroffen“ = Farbgruppe des Eintrags passt zum Filter und der Eintrag sitzt in einer Zone der Ebene (Sammelnamen
        ///    aufgelöst, „ohne“ abgezogen) – Näherung der alten Ansatzpunkt-Maske ohne deren weiche Ränder.
        /// Liefert die Zahl der angelegten Accessoire-Ebenen.</summary>
        public static int MigrateMaterialV1(JObj resolved)
        {
            var mat = resolved?.O("material");
            if (mat == null) { if (resolved != null) resolved["format_version"] = (long)FormatVersion; return 0; }
            var old = (mat.L("ebenen") ?? new List<object>()).OfType<JObj>().ToList();
            var accs = AktiveAccessoires(resolved);
            var byId = new Dictionary<string, JObj>();
            foreach (var a in accs) byId[a.S("id", "")] = a;
            var body = new List<object>(); var accL = new List<object>();
            int n = 0;
            foreach (var e in old)
            {
                n++;
                if (!(e["id"] is string)) e.Insert(0, "id", $"{e.S("typ", "ebene")}#{n}");
                var mk = e.O("maske") ?? new JObj();
                // Format 1: eine leere Zonen-Liste galt als ganzer Körper (Fehler, seit Format 2 heißt leer „nirgends“)
                if (mk.L("zonen") is List<object> zl0 && zl0.Count == 0) { mk = (JObj)Json.Clone(mk); mk["zonen"] = new List<object> { "ganzer_koerper" }; e["maske"] = mk; }
                var gr = mk.Strs("gruppen");
                bool alleGruppen = gr.Count == 0;
                var bodyGr = gr.Where(g => KoerperGruppen.Contains(g)).ToList();
                if (alleGruppen || bodyGr.Count > 0)
                {
                    var be = (JObj)Json.Clone(e);
                    if (!alleGruppen) be.Obj("maske")["gruppen"] = bodyGr.Cast<object>().ToList();
                    body.Add(be);
                }
                if (!e.B("an", true) || e.F("staerke", 1) <= 0.001f || accL.Count >= MaxAccEbenen) continue;
                var passend = accs.Where(a => alleGruppen || gr.Contains(a.S("farbgruppe", "accessoire_a"))).ToList();
                var hit = passend.Where(a => InZonen(a, mk, byId)).ToList();
                // Kein passendes Accessoire in der Variante (z. B. alle abgeschaltet): unbeschränkte Ebene trotzdem als „alle“
                // übernehmen – wirkt jetzt auf nichts (kein sichtbarer Unterschied) und gilt wie früher für später ergänzte Teile.
                bool unbeschraenkt = passend.Count == 0 && (alleGruppen || gr.Any(g => g.StartsWith("accessoire_"))) && (mk.Strs("zonen").Count == 0 || mk.Strs("zonen").Contains("ganzer_koerper")) && mk.Strs("ohne").Count == 0;
                if (hit.Count == 0 && !unbeschraenkt) continue;
                var ae = (JObj)Json.Clone(e);
                ae["maske"] = new JObj { ["oben"] = (double)mk.F("oben", 0), ["rauschen"] = (double)mk.F("rauschen", 0.2f) };
                if (hit.Count == accs.Count || unbeschraenkt) ae["ziel"] = "alle";
                else ae["ziel"] = new JObj { ["typen"] = new List<object>(), ["eintraege"] = hit.Select(a => (object)a.S("id", "")).ToList() };
                accL.Add(ae);
            }
            mat["ebenen"] = body;
            mat["ebenen_accessoires"] = accL;
            resolved["format_version"] = (long)FormatVersion;
            return accL.Count;
        }

        /// <summary>Sitzt der Eintrag (Format 1) in einer Zone der Ebene? Zonen-Namen über die Sammelnamen der Zonen-Definition
        /// aufgelöst; „auf“ (sitzt auf einem anderen Accessoire) nimmt die Zonen des Trägers, „spiegeln“ die Gegenseite.</summary>
        static bool InZonen(JObj acc, JObj mk, Dictionary<string, JObj> byId)
        {
            var zl = mk.Strs("zonen");
            if (zl.Count == 0) zl.Add("ganzer_koerper");   // Format 1: fehlend oder leer = ganzer Körper
            var ohne = Leaves(mk.Strs("ohne"));
            if (ohne.Contains("ganzer_koerper")) return false;
            var a = acc;
            for (int k = 0; k < 4 && a["auf"] is string auf && byId.TryGetValue(auf, out var t); k++) a = t;
            var ez = a.Strs("zonen");
            if (a.B("spiegeln", false)) ez = ez.Concat(ez.Where(z => z.EndsWith("_l")).Select(z => z.Substring(0, z.Length - 2) + "_r")).ToList();
            var el = Leaves(ez);
            el.ExceptWith(ohne);
            if (el.Count == 0) return false;
            if (zl.Contains("ganzer_koerper")) return true;
            return el.Overlaps(Leaves(zl));
        }

        static JObj zonenDef;
        /// <summary>Zonen-Namen in Einzelzonen auflösen (Sammelnamen aus rigging/quadruped_zonen.json, rueckenlinie).</summary>
        static HashSet<string> Leaves(IEnumerable<string> names)
        {
            if (zonenDef == null)
            {
                try { zonenDef = Json.ParseObj(System.IO.File.ReadAllText(VkZones.DefPath("quadruped"))); }
                catch (System.Exception) { zonenDef = new JObj(); }
            }
            var sammel = zonenDef.O("sammel") ?? new JObj();
            var res = new HashSet<string>();
            void Add(string nm, int depth)
            {
                if (depth > 6) return;
                if (nm == "rueckenlinie") { Add("ruecken_gesamt", depth + 1); Add("nacken", depth + 1); return; }
                if (sammel.Has(nm)) { foreach (var s2 in sammel.Strs(nm)) Add(s2, depth + 1); return; }
                res.Add(nm);
            }
            foreach (var nm in names ?? Enumerable.Empty<string>()) Add(nm, 0);
            return res;
        }

        public static readonly Dictionary<string, (string farbe, float intensitaet)> Elemente = new Dictionary<string, (string, float)>
        {
            ["glut"] = ("#FF6A10", 4f), ["frost"] = ("#8FD8FF", 1.5f), ["gift"] = ("#9BFF3A", 2f), ["arkan"] = ("#7A6CFF", 2.5f),
            ["blitz"] = ("#E8F4FF", 5f), ["heilig"] = ("#FFE08A", 2.5f), ["keins"] = ("#404040", 0f),
        };

        // ------------------------------------------------------------------ Budget (Spec 6.4, E5)
        public class Budget { public int tris, accessoires, bedeckung, textur, materialien; }

        public static Budget BudgetFuer(string klasse)
        {
            switch (klasse)
            {
                case "elite": return new Budget { tris = 9000, accessoires = 2500, bedeckung = 3000, textur = 1024, materialien = 2 };
                case "boss": return new Budget { tris = 15000, accessoires = 4000, bedeckung = 5000, textur = 2048, materialien = 3 };
                default: return new Budget { tris = 6000, accessoires = 1500, bedeckung = 2000, textur = 1024, materialien = 2 };
            }
        }

        public static readonly string[] GruppenAchse = { "gemaessigt", "feucht", "sand", "stein", "kalt", "kueste", "geologisch", "lebensfeindlich", "aussergewoehnlich" };
        public static readonly string[] GruppenBuchstabe = { "A", "B", "C", "D", "E", "F", "G", "H", "I" };
    }
}
