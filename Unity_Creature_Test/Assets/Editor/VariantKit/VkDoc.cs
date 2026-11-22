using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace VariantKit
{
    /// <summary>Eine Varianten-Datei (creatures/&lt;NN_name&gt;/varianten/&lt;id&gt;.variant.json) – die einzige Quelle der Wahrheit.
    /// Gespeichert wird Kopf + Statur (alle 17) + nur die Abweichungen vom Gruppen-Preset (Spec 5.4).
    /// Bearbeitet wird immer die aufgelöste Fassung (Preset → Biom-Block → Datei).</summary>
    public class VkDoc
    {
        public string path;          // absolut
        public JObj resolved;        // aufgelöste Fassung (wird im Fenster bearbeitet)
        public JObj presetResolved;  // Preset + Biom-Block (Vergleichsbasis beim Speichern)
        public long loadedRevision;
        public bool dirty;

        public static readonly string[] HeadOrder = { "format", "format_version", "revision", "id", "name", "basis", "skelett", "muster",
            "art", "gruppe", "biom", "sonder", "budget_klasse", "seed", "freigegeben", "quelle", "statur", "bedeckung", "accessoires",
            "material", "effekte", "_gebaut" };

        public static string PresetDir => Path.Combine(VkBase.PipelineRoot, "templates", "umgebungs_gruppen");
        public static string PresetPath(string gruppe) => Path.Combine(PresetDir, gruppe + ".json");
        public static string VariantDir(string creatureDir) => Path.Combine(creatureDir, "varianten");

        public string Id => resolved.S("id", "variante");
        public string ExportName => string.Concat(Id.Split('_').Where(s => s.Length > 0).Select(s => char.ToUpperInvariant(s[0]) + s.Substring(1)));
        public string InstancesPath => Path.Combine(Path.GetDirectoryName(path), Id + ".instanzen.json");

        public static List<string> Presets() => Directory.Exists(PresetDir)
            ? Directory.GetFiles(PresetDir, "*.json").Select(Path.GetFileNameWithoutExtension).OrderBy(x => x).ToList()
            : new List<string>();

        public static JObj LoadPreset(string gruppe, string biom)
        {
            if (string.IsNullOrEmpty(gruppe) || !File.Exists(PresetPath(gruppe))) return new JObj();
            var p = Json.ParseObj(File.ReadAllText(PresetPath(gruppe)));
            var r = new JObj();
            foreach (var k in new[] { "bedeckung", "accessoires", "material", "effekte" }) if (p.Has(k)) r[k] = Json.Clone(p[k]);
            var bb = p.O("biome")?.O(biom ?? "");
            if (bb != null) r = (JObj)Json.Merge(r, bb);
            VkSpec.Migrate(r);   // G14: schwingen/bewegung → weichheit
            return r;
        }

        public static VkDoc Load(string path)
        {
            var stored = Json.ParseObj(File.ReadAllText(path));
            VkSpec.Migrate(stored);   // G14: schwingen/bewegung → weichheit
            var d = new VkDoc { path = path };
            d.presetResolved = LoadPreset(stored.S("gruppe", null), stored.S("biom", null));
            d.resolved = (JObj)Json.Merge(d.presetResolved, stored);
            d.Normalize();
            d.loadedRevision = stored.I("revision", 0);
            return d;
        }

        /// <summary>Neue Variante auf einer Basis (Kopf, Statur 1.0, Preset der Gruppe).</summary>
        public static VkDoc New(VkBase.Info basis, string id, string name, string gruppe, string biom, int seed)
        {
            var d = new VkDoc { path = Path.Combine(VariantDir(basis.dir), id + ".variant.json"), dirty = true };
            d.presetResolved = LoadPreset(gruppe, biom);
            var head = new JObj
            {
                ["format"] = "kreatur_variante", ["format_version"] = (long)VkSpec.FormatVersion, ["revision"] = 0L, ["id"] = id, ["name"] = name,
                ["basis"] = basis.id, ["skelett"] = "quadruped", ["muster"] = "quadruped/" + basis.id.Split('_').Last(),
                ["art"] = "biom", ["gruppe"] = gruppe, ["biom"] = biom, ["sonder"] = null, ["budget_klasse"] = "normal", ["seed"] = (long)seed,
                ["freigegeben"] = false, ["quelle"] = new JObj { ["bild"] = null, ["roster"] = name },
            };
            d.resolved = (JObj)Json.Merge(d.presetResolved, head);
            d.Normalize();
            return d;
        }

        /// <summary>Gruppe/Biom wechseln: Anpassung behalten, Preset tauschen.</summary>
        public void ChangePreset(string gruppe, string biom)
        {
            var own = Stored();
            own["gruppe"] = gruppe; own["biom"] = biom;
            presetResolved = LoadPreset(gruppe, biom);
            resolved = (JObj)Json.Merge(presetResolved, own);
            Normalize();
            dirty = true;
        }

        /// <summary>Fehlende Pflichtfelder ergänzen (alle 17 Statur-Regler, Material-Blöcke, Listen).</summary>
        public void Normalize()
        {
            var st = resolved.Obj("statur");
            var full = new JObj();
            foreach (var r in VkSpec.Statur) full[r.feld] = st.Has(r.feld) ? st[r.feld] : 1.0;
            resolved["statur"] = full;
            var bed = resolved.Obj("bedeckung");
            if (!bed.Has("haut")) bed["haut"] = new JObj { ["typ"] = "glatt", ["rauheit"] = 0.8 };
            bed.List("lagen");
            resolved.List("accessoires");
            var mat = resolved.Obj("material");
            mat.Obj("stil");
            mat.Obj("farbgruppen");
            mat.List("ebenen");
            int n = 0;
            foreach (JObj e in mat.List("ebenen").OfType<JObj>()) { n++; if (!(e["id"] is string)) e.Insert(0, "id", $"{e.S("typ", "ebene")}#{n}"); }
            if (!resolved.Has("effekte")) resolved["effekte"] = new JObj();
            if (!resolved.Has("_gebaut")) resolved["_gebaut"] = null;
            Order(resolved);
        }

        static void Order(JObj o)
        {
            int i = 0;
            foreach (var k in HeadOrder) if (o.Has(k)) o.Insert(i++, k, o[k]);
        }

        /// <summary>Gespeicherte Fassung = Kopf + volle Statur + Abweichungen vom Preset.</summary>
        public JObj Stored()
        {
            var r = new JObj();
            var diff = Json.Diff(resolved, presetResolved) as JObj ?? new JObj();
            foreach (var k in HeadOrder)
            {
                if (k == "statur") { r[k] = Json.Clone(resolved["statur"]); continue; }
                if (k == "bedeckung" || k == "accessoires" || k == "material" || k == "effekte")
                {
                    if (diff.Has(k)) r[k] = diff[k];
                    continue;
                }
                if (resolved.Has(k)) r[k] = Json.Clone(resolved[k]);
            }
            foreach (var p in resolved) if (!r.Has(p.Key) && !HeadOrder.Contains(p.Key)) r[p.Key] = Json.Clone(p.Value);
            return r;
        }

        /// <summary>Speichern (atomar). Ist die Datei inzwischen neuer (anderes Programm), wird NICHT überschrieben.</summary>
        public string Save(bool force = false)
        {
            if (File.Exists(path) && !force)
            {
                try
                {
                    long disk = Json.ParseObj(File.ReadAllText(path)).I("revision", 0);
                    if (disk > loadedRevision) return $"Datei wurde geändert (Revision {disk} > {loadedRevision}) – neu laden?";
                }
                catch (Exception) { /* unlesbar → überschreiben */ }
            }
            resolved["revision"] = loadedRevision + 1;
            var stored = Stored();
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var tmp = path + ".tmp";
            File.WriteAllText(tmp, Json.Write(stored), new UTF8Encoding(false));
            if (File.Exists(path)) File.Delete(path);
            File.Move(tmp, path);
            loadedRevision += 1;
            dirty = false;
            return null;
        }

        /// <summary>Hash der Quelle ohne _gebaut (Spec 6.2 quell_hash).</summary>
        public string SourceHash()
        {
            var s = Stored();
            s.Remove("_gebaut");
            s.Remove("revision");
            using (var sha = SHA1.Create())
                return "sha1:" + BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(Json.Write(s)))).Replace("-", "").ToLowerInvariant();
        }

        public int EntrySeed(JObj entry, string fallbackId)
        {
            if (entry?["seed"] != null) return entry.I("seed", 0);
            return Json.Fnv1a($"{resolved.I("seed", 0)}:{entry?.S("id", fallbackId) ?? fallbackId}");
        }
    }
}
