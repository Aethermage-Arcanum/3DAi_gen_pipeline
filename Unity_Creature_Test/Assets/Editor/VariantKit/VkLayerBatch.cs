using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Selbstprüfung der zwei Ebenen-Gruppen (Körper-Ebenen ↔ Accessoire-Ebenen), Unity 6000.3.28f1 headless:
    ///   -executeMethod VariantKit.VkLayerBatch.Diagnose -vkVariants "a;b" -vkShots &lt;ordner&gt;
    ///       baut jede Variante mit abgewandelten Masken (Zonen leer, „ohne“ alles …) und misst pro Körper-Ebene die Wirkung
    ///       auf Basis-Vertices und auf jeden Accessoire-Eintrag.
    ///   -executeMethod VariantKit.VkLayerBatch.Migrate -vkVariants "a;b"
    ///       lädt Dateien (Format 1 wird umgestellt), druckt das Ergebnis und speichert sie im Format 2.
    ///   -executeMethod VariantKit.VkLayerBatch.Run -vkVariants "&lt;variante für Test a&gt;" -vkTest &lt;testvariante&gt; -vkShots &lt;ordner&gt;
    ///       (a) alle Körper-Ebenen auf „nirgends“ → Accessoires pixelgleich; (b) jede Ebene wirkt nur auf ihr Ziel
    ///       (Differenzbilder pro Ebene, nach Pixel-Klassen Körper / Platten / Kristalle).</summary>
    public static class VkLayerBatch
    {
        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        static List<string> Files() => (Arg("-vkVariants") ?? "").Split(';').Where(s => s.Length > 0).ToList();

        // ------------------------------------------------------------------ Diagnose
        public static void Diagnose()
        {
            try
            {
                var outDir = Arg("-vkShots") ?? Path.Combine(VkBase.PipelineRoot, "temp", "mg_diag");
                Directory.CreateDirectory(outDir);
                var lines = new List<string>();
                Scene();
                foreach (var f in Files())
                {
                    var doc0 = VkDoc.Load(f);
                    var b = VkBase.Load(doc0.resolved.S("basis", ""));
                    foreach (var fall in new[] { "original", "zonen_leer", "ohne_ganzer_koerper", "ohne_alle_zonen", "alle_ebenen_aus" })
                    {
                        var doc = VkDoc.Load(f);
                        foreach (JObj e in doc.resolved.Obj("material").List("ebenen").OfType<JObj>())
                        {
                            var mk = e.Obj("maske");
                            if (fall == "zonen_leer") mk["zonen"] = new List<object>();
                            if (fall == "ohne_ganzer_koerper") mk["ohne"] = new List<object> { "ganzer_koerper" };
                            if (fall == "ohne_alle_zonen") mk["ohne"] = b.zones.Names.Cast<object>().ToList();
                            if (fall == "alle_ebenen_aus") e["an"] = false;
                        }
                        var r = VkBuilder.Build(b, doc);
                        lines.Add($"== {doc.Id} · {fall}");
                        lines.AddRange(Measure(b, r));
                        Shot(b, doc, r, Path.Combine(outDir, $"{doc.ExportName}_{fall}.png"), VkBatch.ViewArpg);
                        UnityEngine.Object.DestroyImmediate(r.mesh);
                    }
                }
                File.WriteAllLines(Path.Combine(outDir, "diagnose.txt"), lines);
                foreach (var l in lines) Debug.Log("[VariantKit] DIAG " + l);
                Debug.Log("[VariantKit] DIAGNOSE OK → " + outDir);
                EditorApplication.Exit(0);
            }
            catch (Exception ex) { Debug.LogError("[VariantKit] FEHLER " + ex); EditorApplication.Exit(1); }
        }

        /// <summary>Wirkung jeder Körper-Ebene: Masken-Kanal (TEXCOORD5/6) × Farbgruppen-Bit × „kein Accessoire“ (TEXCOORD2.w),
        /// Mittel und Maximum über die Basis-Vertices und je Accessoire-Eintrag.</summary>
        static List<string> Measure(VkBase b, VkBuildResult r)
        {
            var res = new List<string>();
            var m0 = new List<Vector4>(); r.mesh.GetUVs(5, m0);
            var m1 = new List<Vector4>(); r.mesh.GetUVs(6, m1);
            var g = new List<Vector4>(); r.mesh.GetUVs(2, g);
            int nb = b.verts.Length;
            for (int li = 0; li < r.ebenen.Count; li++)
            {
                var e = r.ebenen[li];
                var gr = (e.O("maske") ?? new JObj()).Strs("gruppen");
                int bits = 0; if (gr.Count == 0) bits = 511; else foreach (var x in gr) bits |= 1 << VkSpec.GruppeIndex(x);
                float M(int v) { var a = li < 4 ? m0[v] : m1[v]; return g[v].w < -0.5f ? 0 : a[li % 4]; }
                bool Hit(int v) { int gi = (int)Mathf.Round(g[v].x); return ((bits >> gi) & 1) == 1; }
                float bmax = 0, bsum = 0; int bn = 0;
                for (int v = 0; v < nb; v++) { float m = Hit(v) ? M(v) : 0; bmax = Mathf.Max(bmax, m); bsum += m; bn++; }
                var acc = new List<string>();
                foreach (var grp in r.instances.Where(i => !i.cover && i.vCount > 0).GroupBy(i => i.acc))
                {
                    float s = 0, mx = 0; int n = 0;
                    foreach (var inst in grp) for (int k = 0; k < inst.vCount; k++) { int v = inst.vStart + k; float m = Hit(v) ? M(v) : 0; s += m; mx = Mathf.Max(mx, m); n++; }
                    acc.Add($"{grp.Key}[{grp.First().farbgruppe}] mittel {s / Math.Max(1, n):0.00} max {mx:0.00}");
                }
                res.Add($"  Körper-Ebene {e.S("id", "?")} ({e.S("typ", "?")}, gruppen {(gr.Count == 0 ? "alle" : string.Join("+", gr))}): Basis max {bmax:0.00} mittel {bsum / Math.Max(1, bn):0.00} | " + string.Join(" · ", acc));
            }
            if (r.ebenen.Count == 0) res.Add("  (keine aktive Körper-Ebene)");
            foreach (var e in r.ebenenAcc)
                res.Add($"  Accessoire-Ebene {e.S("id", "?")} ({e.S("typ", "?")}) → {VkSpec.ZielText(e)}");
            return res;
        }

        // ------------------------------------------------------------------ Migration (Datei lesen + im Format 2 speichern)
        public static void Migrate()
        {
            try
            {
                foreach (var f in Files())
                {
                    long fv = Json.ParseObj(File.ReadAllText(f)).I("format_version", 1);
                    var doc = VkDoc.Load(f);
                    var m = doc.resolved.Obj("material");
                    Debug.Log($"[VariantKit] MIGRATION {Path.GetFileName(f)}: Format {fv} → {VkSpec.FormatVersion}, " +
                              $"Körper-Ebenen [{string.Join(", ", m.List("ebenen").OfType<JObj>().Select(e => e.S("id", "?") + (e.B("an", true) ? "" : " (aus)")))}], " +
                              $"Accessoire-Ebenen [{string.Join(", ", m.List("ebenen_accessoires").OfType<JObj>().Select(e => $"{e.S("id", "?")}{(e.B("an", true) ? "" : " (aus)")} → {VkSpec.ZielText(e)}"))}]" +
                              (doc.migratedFrom > 0 ? $", neu angelegt: {doc.migratedAccLayers}" : ""));
                    if (Environment.GetCommandLineArgs().Contains("-vkSave"))
                    {
                        var err = doc.Save();
                        Debug.Log($"[VariantKit] GESPEICHERT {f}: {err ?? "ok"}");
                    }
                }
                EditorApplication.Exit(0);
            }
            catch (Exception ex) { Debug.LogError("[VariantKit] FEHLER " + ex); EditorApplication.Exit(1); }
        }

        // ------------------------------------------------------------------ Selbstprüfung (a) + (b)
        public static void Run()
        {
            try
            {
                var outDir = Arg("-vkShots") ?? Path.Combine(VkBase.PipelineRoot, "temp", "mg_pruefung");
                Directory.CreateDirectory(outDir);
                var report = new List<string>();
                Scene();
                // (a) Körper-Ebenen auf „nirgends“: Accessoires (und Körper) müssen aussehen wie ganz ohne Körper-Ebenen
                foreach (var f in Files())
                {
                    var docA = VkDoc.Load(f);
                    var b = VkBase.Load(docA.resolved.S("basis", ""));
                    string n = docA.ExportName;
                    // Klassen-Maske (Accessoire-Pixel)
                    var cls = ClassMask(b, f, outDir, n);
                    void Variant(string tag, Action<JObj> edit)
                    {
                        var d = VkDoc.Load(f); edit(d.resolved.Obj("material"));
                        var r = VkBuilder.Build(b, d);
                        Shot(b, d, r, Path.Combine(outDir, $"{n}_a_{tag}.png"), VkBatch.ViewArpg);
                        UnityEngine.Object.DestroyImmediate(r.mesh);
                    }
                    Variant("original", m => { });
                    Variant("koerper_nirgends", m => { foreach (JObj e in m.List("ebenen").OfType<JObj>()) e.Obj("maske")["zonen"] = new List<object>(); });
                    Variant("koerper_ohne_alles", m => { foreach (JObj e in m.List("ebenen").OfType<JObj>()) e.Obj("maske")["ohne"] = new List<object> { "ganzer_koerper" }; });
                    Variant("koerper_aus", m => { foreach (JObj e in m.List("ebenen").OfType<JObj>()) e["an"] = false; });
                    Variant("accessoire_ebenen_aus", m => { foreach (JObj e in m.List("ebenen_accessoires").OfType<JObj>()) e["an"] = false; });
                    Variant("alles_aus", m => { foreach (var k in new[] { "ebenen", "ebenen_accessoires" }) foreach (JObj e in m.List(k).OfType<JObj>()) e["an"] = false; });
                    string P(string t) => Path.Combine(outDir, $"{n}_a_{t}.png");
                    report.Add($"(a) {n}: Klassen-Pixel Körper {cls.Count(c => c == 1)}, Accessoires {cls.Count(c => c >= 2)}");
                    report.Add($"    Körper-Ebenen auf Zonen [] (nirgends) ↔ Körper-Ebenen aus: ganzes Bild {Diff(P("koerper_nirgends"), P("koerper_aus"), null, -1):0.00}");
                    report.Add($"    Körper-Ebenen „ohne ganzer_koerper“ ↔ Körper-Ebenen aus: ganzes Bild {Diff(P("koerper_ohne_alles"), P("koerper_aus"), null, -1):0.00}");
                    report.Add($"    Körper-Ebenen an ↔ aus (Accessoire-Ebenen aus): Accessoire-Pixel {Diff(P("accessoire_ebenen_aus"), P("alles_aus"), cls, AlleAcc):0.00} · Körper-Pixel {Diff(P("accessoire_ebenen_aus"), P("alles_aus"), cls, 1):0.00}");
                    report.Add($"    Accessoire-Ebenen an ↔ aus (Körper-Ebenen aus): Accessoire-Pixel {Diff(P("koerper_aus"), P("alles_aus"), cls, AlleAcc):0.00} · Körper-Pixel {Diff(P("koerper_aus"), P("alles_aus"), cls, 1):0.00}");
                    DiffImage(P("accessoire_ebenen_aus"), P("alles_aus"), Path.Combine(outDir, $"{n}_a_wirkung_koerper_ebenen.png"));
                    DiffImage(P("koerper_aus"), P("alles_aus"), Path.Combine(outDir, $"{n}_a_wirkung_accessoire_ebenen.png"));
                }
                // (b) Testvariante: matte Platten-Ebene, leuchtende Kristall-Ebene, Körper-Ebene Glutrisse
                var tf = Arg("-vkTest");
                if (tf != null)
                {
                    var doc = VkDoc.Load(tf);
                    var b = VkBase.Load(doc.resolved.S("basis", ""));
                    string n = doc.ExportName;
                    var cls = ClassMask(b, tf, outDir, n);
                    var r0 = VkBuilder.Build(b, doc);
                    report.Add($"(b) {n}: Einträge {string.Join(", ", r0.accIds.Select((id, i) => $"{i}={id}"))}");
                    foreach (var e in r0.ebenenAcc) report.Add($"    Accessoire-Ebene {e.S("id", "?")} → {VkSpec.ZielText(e)}, Bits {VkBuilder.AccBits(e, doc.resolved, r0)}");
                    Shot(b, doc, r0, Path.Combine(outDir, $"{n}_b_alle.png"), VkBatch.ViewArpg);
                    Shot(b, doc, r0, Path.Combine(outDir, $"{n}_b_alle_seite.png"), new Vector2(120f, 22f));
                    UnityEngine.Object.DestroyImmediate(r0.mesh);
                    report.Add($"    Klassen-Pixel: Körper {cls.Count(c => c == 1)}, Platten (accessoire_a) {cls.Count(c => c == 2)}, Kristalle (accessoire_b) {cls.Count(c => c == 3)}");
                    foreach (var (liste, id) in new[] { ("ebenen", "glut_risse"), ("ebenen_accessoires", "platten_matt"), ("ebenen_accessoires", "kristall_leuchten") })
                    {
                        var d = VkDoc.Load(tf);
                        foreach (JObj e in d.resolved.Obj("material").List(liste).OfType<JObj>()) if (e.S("id", "") == id) e["an"] = false;
                        var r = VkBuilder.Build(b, d);
                        var p = Path.Combine(outDir, $"{n}_b_ohne_{id}.png");
                        Shot(b, d, r, p, VkBatch.ViewArpg);
                        UnityEngine.Object.DestroyImmediate(r.mesh);
                        var all = Path.Combine(outDir, $"{n}_b_alle.png");
                        report.Add($"    Ebene {id} an↔aus: Körper {Diff(all, p, cls, 1):0.00} · Platten {Diff(all, p, cls, 2):0.00} · Kristalle {Diff(all, p, cls, 3):0.00}  (mittlere Abweichung 0..255)");
                        DiffImage(all, p, Path.Combine(outDir, $"{n}_b_wirkung_{id}.png"));
                    }
                }
                File.WriteAllLines(Path.Combine(outDir, "pruefung_ebenen.txt"), report);
                foreach (var l in report) Debug.Log("[VariantKit] EBENEN " + l);
                Debug.Log("[VariantKit] EBENEN-PRUEFUNG OK → " + outDir);
                EditorApplication.Exit(0);
            }
            catch (Exception ex) { Debug.LogError("[VariantKit] FEHLER " + ex); EditorApplication.Exit(1); }
        }

        /// <summary>Pixel-Klassen in der ARPG-Ansicht: 0 Hintergrund, 1 Körper, 2 accessoire_a, 3 accessoire_b, 4 accessoire_c.
        /// Ohne Ebenen gerendert, Körper grau, Accessoire-Gruppen in reinen Farben (rot/blau/grün) → Klasse aus dem Farbton.</summary>
        static int[] ClassMask(VkBase b, string f, string outDir, string n)
        {
            var d = VkDoc.Load(f);
            foreach (var k in new[] { "ebenen", "ebenen_accessoires" }) foreach (JObj e in d.resolved.Obj("material").List(k).OfType<JObj>()) e["an"] = false;
            var r = VkBuilder.Build(b, d);
            var p = Path.Combine(outDir, $"{n}_klassen.png");
            Shot(b, d, r, p, VkBatch.ViewArpg, null, 0, 640, mat =>
            {
                for (int g = 0; g < 9; g++)
                {
                    var c = g == 3 ? new Vector4(1, 0, 0, 0) : g == 4 ? new Vector4(0, 0, 1, 0) : g == 5 ? new Vector4(0, 1, 0, 0) : new Vector4(0.55f, 0.55f, 0.55f, 0);
                    mat.SetVector($"_G{g}C", c); mat.SetVector($"_G{g}D", c);
                    mat.SetVector($"_G{g}P", new Vector4(0.9f, 0, 0, 0)); mat.SetVector($"_G{g}Q", Vector4.zero);
                }
            });
            UnityEngine.Object.DestroyImmediate(r.mesh);
            var t = new Texture2D(2, 2); t.LoadImage(File.ReadAllBytes(p));
            var px = t.GetPixels32(); var bg = px[0];
            var cls = new int[px.Length];
            for (int i = 0; i < px.Length; i++)
            {
                var c = px[i];
                if (Math.Abs(c.r - bg.r) + Math.Abs(c.g - bg.g) + Math.Abs(c.b - bg.b) <= 6) { cls[i] = 0; continue; }
                int mx = Math.Max(c.r, Math.Max(c.g, c.b)), mn = Math.Min(c.r, Math.Min(c.g, c.b));
                if (mx - mn < 40) cls[i] = 1;
                else if (c.r == mx) cls[i] = 2;
                else if (c.b == mx) cls[i] = 3;
                else cls[i] = 4;
            }
            UnityEngine.Object.DestroyImmediate(t);
            return cls;
        }

        /// <summary>Mittlere Abweichung (0..255) zwischen zwei Bildern, nur auf Pixeln der Klasse (AlleAcc = alle Accessoire-Klassen,
        /// −1 = alle Nicht-Hintergrund-Pixel beider Bilder).</summary>
        static float Diff(string a, string bPath, int[] cls, int klasse)
        {
            if (klasse < 0 || cls == null) return VkBatch.ImageDiff(a, bPath);
            var ta = new Texture2D(2, 2); ta.LoadImage(File.ReadAllBytes(a));
            var tb = new Texture2D(2, 2); tb.LoadImage(File.ReadAllBytes(bPath));
            var pa = ta.GetPixels32(); var pb = tb.GetPixels32();
            double sum = 0; long n = 0;
            for (int i = 0; i < Math.Min(pa.Length, Math.Min(pb.Length, cls.Length)); i++)
            {
                bool inK = klasse == AlleAcc ? cls[i] >= 2 : cls[i] == klasse;
                if (!inK) continue;
                sum += (Math.Abs(pa[i].r - pb[i].r) + Math.Abs(pa[i].g - pb[i].g) + Math.Abs(pa[i].b - pb[i].b)) / 3.0;
                n++;
            }
            UnityEngine.Object.DestroyImmediate(ta); UnityEngine.Object.DestroyImmediate(tb);
            return n > 0 ? (float)(sum / n) : 0;
        }
        const int AlleAcc = 9;   // Klasse „alle Accessoire-Pixel“

        /// <summary>Differenzbild: Abweichung × 4 in Rot über dem abgedunkelten Bild a.</summary>
        static void DiffImage(string a, string bPath, string outPath)
        {
            var ta = new Texture2D(2, 2); ta.LoadImage(File.ReadAllBytes(a));
            var tb = new Texture2D(2, 2); tb.LoadImage(File.ReadAllBytes(bPath));
            var pa = ta.GetPixels32(); var pb = tb.GetPixels32();
            var o = new Color32[pa.Length];
            for (int i = 0; i < pa.Length; i++)
            {
                int d = (Math.Abs(pa[i].r - pb[i].r) + Math.Abs(pa[i].g - pb[i].g) + Math.Abs(pa[i].b - pb[i].b)) / 3;
                byte gray = (byte)((pa[i].r + pa[i].g + pa[i].b) / 3 * 0.45f);
                o[i] = d > 2 ? new Color32((byte)Math.Min(255, 60 + d * 4), (byte)(gray / 2), (byte)(gray / 2), 255) : new Color32(gray, gray, gray, 255);
            }
            var t = new Texture2D(ta.width, ta.height, TextureFormat.RGBA32, false);
            t.SetPixels32(o); t.Apply();
            File.WriteAllBytes(outPath, t.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(ta); UnityEngine.Object.DestroyImmediate(tb); UnityEngine.Object.DestroyImmediate(t);
        }

        // ------------------------------------------------------------------ Bilder (Vorschau-Shader, ARPG-Kamera)
        /// <summary>Leere Prüf-Szene (einmal zu Beginn, bevor Basis/Meshes geladen werden – NewScene räumt ungenutzte Assets weg).</summary>
        public static void Scene()
        {
            EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f);
            foreach (var l in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None)) l.intensity = 1.2f;
            var cam = Camera.main;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.5f, 0.5f, 0.52f);
            cam.fieldOfView = 30f;
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.transform.localScale = Vector3.one * 10f;
            var gm = new Material(Shader.Find("Standard")) { color = new Color(0.30f, 0.30f, 0.31f) };
            ground.GetComponent<Renderer>().sharedMaterial = gm;
        }

        public static void Shot(VkBase b, VkDoc doc, VkBuildResult pv, string path, Vector2 view, string clip = null, float t = 0, int size = 640, Action<Material> tweak = null)
        {
            var cam = Camera.main;
            var mat = new Material(Shader.Find(VkBake.ShaderName));
            VkBuilder.ApplyMaterial(mat, b, doc, pv);
            tweak?.Invoke(mat);
            var inst = (GameObject)UnityEngine.Object.Instantiate(b.model);
            inst.transform.position = new Vector3(0, -b.restMinY, 0);
            var smr = inst.GetComponentInChildren<SkinnedMeshRenderer>();
            smr.sharedMesh = pv.mesh; smr.sharedMaterials = new[] { mat };
            var lb = b.smr.localBounds; lb.Expand(b.L * b.meshToMeter * 0.6f); smr.localBounds = lb;
            var st = inst.AddComponent<VariantStatur>();
            VkBuilder.ConfigureStatur(st, b, doc.resolved.Obj("statur"), inst);
            if (clip == null) VkBuilder.RestPose(inst); else { var c = VkBatch.Clip(b, clip); c.SampleAnimation(inst, c.length * t); }
            st.Apply();
            Shader.SetGlobalFloat("_VKUseTime", 1f);
            Shader.SetGlobalFloat("_VKTime", t * 2f);
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
            tex.ReadPixels(new Rect(0, 0, size, size), 0, 0);
            tex.Apply();
            File.WriteAllBytes(path, tex.EncodeToPNG());
            RenderTexture.active = null;
            cam.targetTexture = null;
            Shader.SetGlobalFloat("_VKUseTime", 0f);
            UnityEngine.Object.DestroyImmediate(tex);
            UnityEngine.Object.DestroyImmediate(inst);
            UnityEngine.Object.DestroyImmediate(mat);
            rt.Release();
        }
    }
}
