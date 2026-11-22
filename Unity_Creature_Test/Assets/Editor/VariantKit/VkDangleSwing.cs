using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace VariantKit
{
    /// <summary>G14 / C13: schaltet im Shader „Creature/Standard Dangling“ den Schalter „Nachschwingen“ (Trägheit, Wackeln,
    /// Stöße aus VariantSwing.cginc) NUR für Kreaturen ein, deren creature.toml das ausdrücklich will:
    ///   [dangling]
    ///   nachschwingen = true          # Standard aus → Material und Bild bleiben exakt wie bisher
    ///   nachschwingen_laenge = 0.35   # Länge der hängenden Teile (m), Standard 0.3
    ///   nachschwingen_feder = 2       # welche Feder: 0 Hüfte, 1 Brust, 2 Kopf (Standard), 3 Schwanz
    /// Läuft nach jedem Import eines Kreatur-Materials (Assets/Creatures/&lt;Name&gt;/&lt;Name&gt;.mat) – der CreatureImporter bleibt
    /// unverändert. Die Laufzeit-Komponente hängt VariantSchwingen.AutoAttach beim Szenen-Start an.</summary>
    public class VkDangleSwing : AssetPostprocessor
    {
        const string Keyword = "_VK_NACHSCHWINGEN";

        static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] movedFrom)
        {
            var mats = imported.Where(p => Regex.IsMatch(p, @"^Assets/Creatures/([^/]+)/\1\.mat$")).ToList();
            if (mats.Count == 0) return;
            EditorApplication.delayCall += () => { foreach (var m in mats) Apply(m); };
        }

        public static bool Apply(string matPath)
        {
            var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if (mat == null || mat.shader == null || mat.shader.name != "Creature/Standard Dangling") return false;
            string name = Path.GetFileNameWithoutExtension(matPath);
            var cfg = Config(name);
            bool want = cfg.on;
            bool changed = mat.IsKeywordEnabled(Keyword) != want;
            if (want)
            {
                changed |= !Mathf.Approximately(mat.GetFloat("_VKDangleLen"), cfg.len) || !Mathf.Approximately(mat.GetFloat("_VKDangleSlot"), cfg.slot);
                if (changed)
                {
                    mat.EnableKeyword(Keyword);
                    mat.SetFloat("_VKNachschwingen", 1);
                    mat.SetFloat("_VKDangleLen", cfg.len);
                    mat.SetFloat("_VKDangleSlot", cfg.slot);
                }
            }
            else if (changed) { mat.DisableKeyword(Keyword); mat.SetFloat("_VKNachschwingen", 0); }
            if (changed)
            {
                EditorUtility.SetDirty(mat);
                AssetDatabase.SaveAssetIfDirty(mat);
                Debug.Log($"[VariantKit] {name}: Nachschwingen im Dangling-Shader {(want ? "AN" : "aus")} (creature.toml [dangling] nachschwingen)");
            }
            return want;
        }

        /// <summary>[dangling]-Abschnitt der creature.toml, deren output/&lt;Name&gt;.fbx zur Kreatur gehört.</summary>
        public static (bool on, float len, float slot) Config(string name)
        {
            // wie der CreatureImporter: -creaturesRoot (Projekt-Kopie für Tests), sonst ../creatures
            var args = System.Environment.GetCommandLineArgs();
            int ai = System.Array.IndexOf(args, "-creaturesRoot");
            var root = ai >= 0 && ai + 1 < args.Length ? args[ai + 1] : Path.Combine(VkBase.PipelineRoot, "creatures");
            if (!Directory.Exists(root)) return (false, 0.3f, 2);
            foreach (var d in Directory.GetDirectories(root))
            {
                if (!File.Exists(Path.Combine(d, "output", name + ".fbx"))) continue;
                var toml = Path.Combine(d, "creature.toml");
                if (!File.Exists(toml)) break;
                var txt = File.ReadAllText(toml);
                var sec = Regex.Match(txt, @"^\[dangling\]\s*$(.*?)(?=^\[|\z)", RegexOptions.Multiline | RegexOptions.Singleline);
                if (!sec.Success) break;
                var body = sec.Groups[1].Value;
                bool on = Regex.IsMatch(body, @"^\s*nachschwingen\s*=\s*true", RegexOptions.Multiline);
                float F(string key, float def)
                {
                    var m = Regex.Match(body, @"^\s*" + key + @"\s*=\s*([0-9.]+)", RegexOptions.Multiline);
                    return m.Success && float.TryParse(m.Groups[1].Value, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var v) ? v : def;
                }
                return (on, F("nachschwingen_laenge", 0.3f), F("nachschwingen_feder", 2));
            }
            return (false, 0.3f, 2);
        }
    }
}
