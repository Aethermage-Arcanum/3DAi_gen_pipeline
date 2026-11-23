using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Selbstprüfung „Haut/Bedeckung“ und „Accessoire-Ebene pro Eintrag“ (Nutzer 2026-11-23), headless:
    ///   Shots: ARPG- + Seitenbild jeder Variante (-vkVariants "a;b", -vkShots ordner [-vkBase ordner = Vergleich mit Stand vorher])
    ///   Test:  -vkVariants "a;b" -vkKoerper "ebene_a;ebene_b" -vkAccEb "ebene_a;ebene_b" -vkEintrag "eintrag_a;eintrag_b" -vkShots ordner
    ///          Körper-Ebene nur „Bedeckung“ (bzw. nur „Haut“), Accessoire-Ebene nur für 1 Eintrag, Wirkungsbilder + Zahlen,
    ///          dazu Vorschau ↔ gebacken (Textur-Backen in einen temporären Asset-Ordner, danach gelöscht).
    /// Lädt die Dateien nur, speichert nichts.</summary>
    public static class VkUiBatch
    {
        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }
        static List<string> ListArg(string n) => (Arg(n) ?? "").Split(';').Where(s => s.Length > 0).ToList();

        public static void Shots()
        {
            try
            {
                var outDir = Arg("-vkShots"); Directory.CreateDirectory(outDir);
                var baseDir = Arg("-vkBase");
                var rep = new List<string>();
                VkLayerBatch.Scene();
                foreach (var f in ListArg("-vkVariants"))
                {
                    var d = VkDoc.Load(f);
                    var b = VkBase.Load(d.resolved.S("basis", ""));
                    var r = VkBuilder.Build(b, d);
                    foreach (var (tag, view) in new[] { ("arpg", VkBatch.ViewArpg), ("seite", VkBatch.ViewSide) })
                    {
                        var p = Path.Combine(outDir, $"{d.ExportName}_{tag}.png");
                        VkLayerBatch.Shot(b, d, r, p, view);
                        var q = baseDir != null ? Path.Combine(baseDir, Path.GetFileName(p)) : null;
                        if (q != null && File.Exists(q))
                        {
                            var (mean, max, n8) = PixDiff(q, p);
                            rep.Add($"{d.ExportName} {tag}: vorher↔nachher mittlere Abweichung {mean:0.000} (0..255), max {max}, Pixel > 8: {n8}");
                        }
                    }
                    UnityEngine.Object.DestroyImmediate(r.mesh);
                }
                if (rep.Count > 0) File.WriteAllLines(Path.Combine(outDir, "vergleich_vorher.txt"), rep);
                foreach (var l in rep) Debug.Log("[VariantKit] UI-SHOTS " + l);
                Debug.Log("[VariantKit] UI-SHOTS OK → " + outDir);
                EditorApplication.Exit(0);
            }
            catch (Exception ex) { Debug.LogError("[VariantKit] FEHLER " + ex); EditorApplication.Exit(1); }
        }

        public static void Test()
        {
            const string tmpAssets = "Assets/VariantKit/_ui_tmp";
            try
            {
                var outDir = Arg("-vkShots"); Directory.CreateDirectory(outDir);
                var files = ListArg("-vkVariants"); var kl = ListArg("-vkKoerper"); var al = ListArg("-vkAccEb"); var el = ListArg("-vkEintrag");
                var rep = new List<string>();
                VkLayerBatch.Scene();
                for (int i = 0; i < files.Count; i++)
                {
                    string f = files[i], kId = kl[i], aId = al[i], eId = el[i];
                    var d0 = VkDoc.Load(f);
                    var b = VkBase.Load(d0.resolved.S("basis", ""));
                    string n = d0.ExportName;
                    string P(string t) => Path.Combine(outDir, $"{n}_{t}.png");
                    JObj Find(JObj R, string liste, string id) => R.Obj("material").List(liste).OfType<JObj>().FirstOrDefault(e => e.S("id", "") == id);
                    void NurEintrag(JObj R)
                    {
                        var e = Find(R, "ebenen_accessoires", aId);
                        var all = VkSpec.AlleEintraege(R);
                        e["ziel"] = "alle";
                        foreach (var a in all) if (a.S("id", "") != eId) VkSpec.SetZielEintrag(e, a, false, all);   // wie die Häkchen im Fenster
                    }
                    void Shot(string tag, Action<JObj> edit)
                    {
                        var d = VkDoc.Load(f); edit(d.resolved);
                        var r = VkBuilder.Build(b, d);
                        VkLayerBatch.Shot(b, d, r, P(tag), VkBatch.ViewArpg);
                        UnityEngine.Object.DestroyImmediate(r.mesh);
                    }
                    var cls = Classes(b, f, eId, P("klassen"));
                    var lagen = VkSpec.AktiveLagen(d0.resolved).Select((l, k) => VkSpec.LageId(l, k)).ToList();
                    rep.Add($"{n}: Körper-Ebene {kId}, Accessoire-Ebene {aId}, Eintrag {eId}; Lagen [{string.Join(", ", lagen)}]; " +
                            $"Klassen-Pixel Haut {cls.Count(c => c == 1)}, Bedeckung {cls.Count(c => c == 4)}, Eintrag {cls.Count(c => c == 2)}, andere Accessoires {cls.Count(c => c == 3)}");
                    Shot("standard", R => { });
                    Shot("k_aus", R => Find(R, "ebenen", kId)["an"] = false);
                    Shot("k_nur_bedeckung", R => Find(R, "ebenen", kId).Obj("maske")["haut"] = false);
                    Shot("k_nur_haut", R => Find(R, "ebenen", kId).Obj("maske")["bedeckung"] = false);
                    Shot("a_aus", R => Find(R, "ebenen_accessoires", aId)["an"] = false);
                    Shot("a_nur_eintrag", NurEintrag);
                    string Z(string a, string bb) => $"Haut {Diff(P(a), P(bb), cls, 1):0.00} · Bedeckung {Diff(P(a), P(bb), cls, 4):0.00} · Eintrag {Diff(P(a), P(bb), cls, 2):0.00} · andere Acc. {Diff(P(a), P(bb), cls, 3):0.00}";
                    rep.Add($"  Wirkung {kId} Standard (Haut+Bedeckung): {Z("standard", "k_aus")}");
                    rep.Add($"  Wirkung {kId} nur Bedeckung:             {Z("k_nur_bedeckung", "k_aus")}");
                    rep.Add($"  Wirkung {kId} nur Haut:                  {Z("k_nur_haut", "k_aus")}");
                    rep.Add($"  Wirkung {aId} alle (Standard):           {Z("standard", "a_aus")}");
                    rep.Add($"  Wirkung {aId} nur {eId}:  {Z("a_nur_eintrag", "a_aus")}");
                    { var dz = VkDoc.Load(f); NurEintrag(dz.resolved); rep.Add($"    Ziel nach den Häkchen: {Json.Write(Find(dz.resolved, "ebenen_accessoires", aId)["ziel"]).Replace("\n", " ")}"); }
                    var wa = Path.Combine(outDir, $"{n}_w_k.png"); var wb = Path.Combine(outDir, $"{n}_w_a.png");
                    DiffImage(P("k_nur_bedeckung"), P("k_aus"), wa);
                    DiffImage(P("a_nur_eintrag"), P("a_aus"), wb);
                    SideBySide(wa, wb, Path.Combine(outDir, $"PRUEF_{n}.png"));
                    // Vorschau ↔ gebacken mit beiden Änderungen
                    {
                        var d = VkDoc.Load(f); Find(d.resolved, "ebenen", kId).Obj("maske")["haut"] = false; NurEintrag(d.resolved);
                        var r = VkBuilder.Build(b, d);
                        VkLayerBatch.Shot(b, d, r, P("beides_vorschau"), VkBatch.ViewArpg);
                        var tb = VkTexBake.Bake(b, d, r, null, tmpAssets, n, 1024);
                        ShotWith(b, d, tb.mesh, tb.material, P("beides_gebacken"), VkBatch.ViewArpg);
                        rep.Add($"  Vorschau ↔ gebacken (beide Änderungen): {VkBatch.ImageDiff(P("beides_vorschau"), P("beides_gebacken")):0.00}");
                        UnityEngine.Object.DestroyImmediate(r.mesh); UnityEngine.Object.DestroyImmediate(tb.mesh); UnityEngine.Object.DestroyImmediate(tb.material);
                        AssetDatabase.DeleteAsset(tmpAssets);
                    }
                }
                File.WriteAllLines(Path.Combine(outDir, "pruefung_ui.txt"), rep);
                foreach (var l in rep) Debug.Log("[VariantKit] UI-TEST " + l);
                Debug.Log("[VariantKit] UI-TEST OK → " + outDir);
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[VariantKit] FEHLER " + ex);
                if (AssetDatabase.IsValidFolder(tmpAssets)) AssetDatabase.DeleteAsset(tmpAssets);
                EditorApplication.Exit(1);
            }
        }

        /// <summary>Pixel-Klassen (ARPG): 0 Hintergrund/Boden, 1 Haut (Basis), 2 der gewählte Eintrag, 3 andere Accessoires, 4 Bedeckung.</summary>
        static int[] Classes(VkBase b, string f, string eintrag, string p)
        {
            var d = VkDoc.Load(f);
            foreach (var k in new[] { "ebenen", "ebenen_accessoires" }) foreach (JObj e in d.resolved.Obj("material").List(k).OfType<JObj>()) e["an"] = false;
            foreach (JObj a in d.resolved.List("accessoires").OfType<JObj>()) a["farbgruppe"] = a.S("id", "") == eintrag ? "accessoire_a" : "accessoire_b";
            var r = VkBuilder.Build(b, d);
            VkLayerBatch.Shot(b, d, r, p, VkBatch.ViewArpg, null, 0, 640, mat =>
            {
                for (int g = 0; g < 9; g++)
                {
                    var c = g == 3 ? new Vector4(1, 0, 0, 0) : g == 4 || g == 5 ? new Vector4(0, 0, 1, 0) : g == 1 || g == 2 ? new Vector4(0, 1, 0, 0) : new Vector4(1, 1, 0, 0);   // Haut gelb (Boden bleibt grau)
                    mat.SetVector($"_G{g}C", c); mat.SetVector($"_G{g}D", c);
                    mat.SetVector($"_G{g}P", new Vector4(0.9f, 0, 0, 0)); mat.SetVector($"_G{g}Q", Vector4.zero);
                }
            });
            UnityEngine.Object.DestroyImmediate(r.mesh);
            var px = Load(p); var bg = px[0];
            var cls = new int[px.Length];
            for (int i = 0; i < px.Length; i++)
            {
                var c = px[i];
                if (Math.Abs(c.r - bg.r) + Math.Abs(c.g - bg.g) + Math.Abs(c.b - bg.b) <= 6) continue;
                int mx = Math.Max(c.r, Math.Max(c.g, c.b)), mn = Math.Min(c.r, Math.Min(c.g, c.b));
                cls[i] = mx - mn < 40 ? 0 : c.b == mx ? 3 : c.r > mx * 0.6f && c.g > mx * 0.6f ? 1 : c.r == mx ? 2 : 4;
            }
            return cls;
        }

        static Color32[] Load(string p)
        {
            var t = new Texture2D(2, 2); t.LoadImage(File.ReadAllBytes(p));
            var px = t.GetPixels32(); UnityEngine.Object.DestroyImmediate(t); return px;
        }

        static float Diff(string a, string b, int[] cls, int k)
        {
            var pa = Load(a); var pb = Load(b);
            double s = 0; long n = 0;
            for (int i = 0; i < Math.Min(pa.Length, Math.Min(pb.Length, cls.Length)); i++)
            {
                if (cls[i] != k) continue;
                s += (Math.Abs(pa[i].r - pb[i].r) + Math.Abs(pa[i].g - pb[i].g) + Math.Abs(pa[i].b - pb[i].b)) / 3.0; n++;
            }
            return n > 0 ? (float)(s / n) : 0;
        }

        /// <summary>Ganzes Bild: mittlere Abweichung, größte Abweichung eines Kanals, Pixel mit Abweichung &gt; 8.</summary>
        static (float, int, int) PixDiff(string a, string b)
        {
            var pa = Load(a); var pb = Load(b);
            double s = 0; int mx = 0, n8 = 0;
            for (int i = 0; i < Math.Min(pa.Length, pb.Length); i++)
            {
                int d = Math.Max(Math.Abs(pa[i].r - pb[i].r), Math.Max(Math.Abs(pa[i].g - pb[i].g), Math.Abs(pa[i].b - pb[i].b)));
                s += (Math.Abs(pa[i].r - pb[i].r) + Math.Abs(pa[i].g - pb[i].g) + Math.Abs(pa[i].b - pb[i].b)) / 3.0;
                mx = Math.Max(mx, d); if (d > 8) n8++;
            }
            return ((float)(s / Math.Max(1, pa.Length)), mx, n8);
        }

        /// <summary>Wirkungsbild wie temp/mg_pruefung: Abweichung × 4 in Rot über dem abgedunkelten Bild a.</summary>
        static void DiffImage(string a, string b, string outPath)
        {
            var pa = Load(a); var pb = Load(b);
            int w = (int)Math.Sqrt(pa.Length);
            var o = new Color32[pa.Length];
            for (int i = 0; i < pa.Length; i++)
            {
                int d = (Math.Abs(pa[i].r - pb[i].r) + Math.Abs(pa[i].g - pb[i].g) + Math.Abs(pa[i].b - pb[i].b)) / 3;
                byte gray = (byte)((pa[i].r + pa[i].g + pa[i].b) / 3 * 0.45f);
                o[i] = d > 2 ? new Color32((byte)Math.Min(255, 60 + d * 4), (byte)(gray / 2), (byte)(gray / 2), 255) : new Color32(gray, gray, gray, 255);
            }
            var t = new Texture2D(w, w, TextureFormat.RGBA32, false); t.SetPixels32(o); t.Apply();
            File.WriteAllBytes(outPath, t.EncodeToPNG()); UnityEngine.Object.DestroyImmediate(t);
        }

        static void SideBySide(string a, string b, string outPath)
        {
            var pa = Load(a); var pb = Load(b);
            int w = (int)Math.Sqrt(pa.Length), gap = 8;
            var t = new Texture2D(w * 2 + gap, w, TextureFormat.RGBA32, false);
            var o = new Color32[(w * 2 + gap) * w];
            for (int i = 0; i < o.Length; i++) o[i] = new Color32(255, 255, 255, 255);
            for (int y = 0; y < w; y++) for (int x = 0; x < w; x++) { o[y * (w * 2 + gap) + x] = pa[y * w + x]; o[y * (w * 2 + gap) + w + gap + x] = pb[y * w + x]; }
            t.SetPixels32(o); t.Apply();
            File.WriteAllBytes(outPath, t.EncodeToPNG()); UnityEngine.Object.DestroyImmediate(t);
        }

        /// <summary>Wie VkLayerBatch.Shot, aber mit fertigem Mesh + Material (gebackenes Spiel-Mesh, Shader VariantKit/Baked).</summary>
        static void ShotWith(VkBase b, VkDoc doc, Mesh mesh, Material mat, string path, Vector2 view, int size = 640)
        {
            var cam = Camera.main;
            var inst = (GameObject)UnityEngine.Object.Instantiate(b.model);
            inst.transform.position = new Vector3(0, -b.restMinY, 0);
            var smr = inst.GetComponentInChildren<SkinnedMeshRenderer>();
            smr.sharedMesh = mesh; smr.sharedMaterials = new[] { mat };
            var lb = b.smr.localBounds; lb.Expand(b.L * b.meshToMeter * 0.6f); smr.localBounds = lb;
            var st = inst.AddComponent<VariantStatur>();
            VkBuilder.ConfigureStatur(st, b, doc.resolved.Obj("statur"), inst);
            VkBuilder.RestPose(inst);
            st.Apply();
            Shader.SetGlobalFloat("_VKUseTime", 1f); Shader.SetGlobalFloat("_VKTime", 0f);
            var mb = new Mesh(); smr.BakeMesh(mb, true);
            var bb = new Bounds(smr.transform.TransformPoint(mb.vertices[0]), Vector3.zero);
            foreach (var v in mb.vertices) bb.Encapsulate(smr.transform.TransformPoint(v));
            UnityEngine.Object.DestroyImmediate(mb);
            float ext = Mathf.Max(bb.size.x, bb.size.y, bb.size.z);
            var rt = new RenderTexture(size, size, 24) { antiAliasing = 4 };
            cam.targetTexture = rt;
            VkBatch.Pose(view, bb.center, ext * 2.3f, out var pos, out var rot);
            cam.transform.SetPositionAndRotation(pos, rot);
            cam.nearClipPlane = ext * 0.02f;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, size, size), 0, 0); tex.Apply();
            File.WriteAllBytes(path, tex.EncodeToPNG());
            RenderTexture.active = null; cam.targetTexture = null;
            Shader.SetGlobalFloat("_VKUseTime", 0f);
            UnityEngine.Object.DestroyImmediate(tex); UnityEngine.Object.DestroyImmediate(inst);
            rt.Release();
        }
    }
}
