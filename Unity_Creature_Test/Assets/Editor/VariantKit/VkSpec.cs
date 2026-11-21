using System.Collections.Generic;
using System.Linq;

namespace VariantKit
{
    /// <summary>Feste Werte aus docs/VARIANTEN_SPEC.md (Regler, Bereiche, Ampel-Zonen, Standardwerte, Budget).
    /// Eine Stelle für alles, damit Fenster, Builder und Batch dieselben Zahlen benutzen.</summary>
    public static class VkSpec
    {
        public const string ToolVersion = "0.1.0";
        public const int FormatVersion = 1;

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
        public static readonly string[] Ausrichtungen = { "normale", "oben", "hinten", "aussen", "knochen" };
        public static readonly string[] Bindungen = { "anker", "knochen", "haut" };

        public class TypStd { public string[] zonen; public string verteilung; public int anzahl; public float groesse; }

        public static readonly Dictionary<string, TypStd> AccTypen = new Dictionary<string, TypStd>
        {
            ["basaltbrocken"] = new TypStd { zonen = new[] { "buckel", "ruecken_mitte", "kruppe", "schulter_l" }, verteilung = "cluster", anzahl = 1, groesse = 0.13f },
            ["steinplatte"] = new TypStd { zonen = new[] { "stirn", "schulter_l", "unterarm_l", "oberschenkel_l", "ruecken_mitte" }, verteilung = "streuen", anzahl = 2, groesse = 0.12f },
            ["felszacke"] = new TypStd { zonen = new[] { "rueckenlinie" }, verteilung = "reihe", anzahl = 11, groesse = 0.10f },
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
                ["abstand_min"] = 0.02, ["ausrichtung"] = "normale", ["neigung"] = 0.0, ["drehung_zufall"] = 180.0,
                ["kipp_zufall"] = 10.0, ["einsinken"] = 0.25, ["bindung"] = "anker", ["bewegung"] = "starr",
                ["farbgruppe"] = "accessoire_a", ["farb_zufall"] = 0.0, ["weg_ab_lod"] = null, ["seed"] = null,
            };
            return o;
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
        public const int MaxEbenen = 8;

        /// <summary>Neue Ebene mit Standardwerten (Spec 4.3).</summary>
        public static JObj NeueEbene(string id, string typ)
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
            e["maske"] = new JObj { ["zonen"] = new List<object> { "ganzer_koerper" } };
            return e;
        }

        public static readonly Dictionary<string, (string farbe, float intensitaet)> Elemente = new Dictionary<string, (string, float)>
        {
            ["glut"] = ("#FF6A10", 4f), ["frost"] = ("#8FD8FF", 1.5f), ["gift"] = ("#9BFF3A", 2f), ["arkan"] = ("#7A6CFF", 2.5f),
            ["blitz"] = ("#E8F4FF", 5f), ["heilig"] = ("#FFE08A", 2.5f), ["keins"] = ("#404040", 0f),
        };

        // ------------------------------------------------------------------ Budget (Spec 6.4, E5)
        public class Budget { public int tris, accessoires, textur, materialien; }

        public static Budget BudgetFuer(string klasse)
        {
            switch (klasse)
            {
                case "elite": return new Budget { tris = 9000, accessoires = 2500, textur = 1024, materialien = 2 };
                case "boss": return new Budget { tris = 15000, accessoires = 4000, textur = 2048, materialien = 3 };
                default: return new Budget { tris = 6000, accessoires = 1500, textur = 1024, materialien = 2 };
            }
        }

        public static readonly string[] GruppenAchse = { "gemaessigt", "feucht", "sand", "stein", "kalt", "kueste", "geologisch", "lebensfeindlich", "aussergewoehnlich" };
        public static readonly string[] GruppenBuchstabe = { "A", "B", "C", "D", "E", "F", "G", "H", "I" };
    }
}
