using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Selbstprüfung headless:
    ///   Unity.exe -batchmode -projectPath Unity_Creature_Test -executeMethod VariantKit.VkBatch.Run -logFile log.txt
    ///   optional: -vkVariants "pfad1;pfad2" (Standard: alle creatures/*/varianten/*.variant.json)  -vkShots &lt;ordner&gt;
    /// Backt jede Variante, rendert ARPG-Bilder (Ruhepose, Walk, Attack2, Seite) und misst, ob die Accessoires in der
    /// Bewegung schweben oder einsinken (Abstand Teil-Unterseite ↔ Haut entlang der Hautnormale, gegen die Ruhepose).</summary>
    public static class VkBatch
    {
        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        public static void Run()
        {
            try
            {
                var shots = Arg("-vkShots") ?? Path.Combine(VkBase.PipelineRoot, "temp", "vk_shots");
                Directory.CreateDirectory(shots);
                var files = Arg("-vkVariants")?.Split(';').Where(s => s.Length > 0).ToList()
                            ?? Directory.GetDirectories(Path.Combine(VkBase.PipelineRoot, "creatures"))
                                .Select(d => Path.Combine(d, "varianten")).Where(Directory.Exists)
                                .SelectMany(d => Directory.GetFiles(d, "*.variant.json")).ToList();
                var report = new JObj { ["datum"] = DateTime.Now.ToString("s"), ["varianten"] = new List<object>() };
                foreach (var f in files)
                {
                    var doc = VkDoc.Load(f);
                    var b = VkBase.Load(doc.resolved.S("basis", ""));
                    var r = VkBake.Bake(b, doc);
                    var entry = new JObj
                    {
                        ["id"] = doc.Id, ["prefab"] = r.prefabPath, ["tris"] = (long)r.tris, ["tris_basis"] = (long)r.trisBase, ["tris_accessoires"] = (long)r.trisAcc,
                        ["materialien"] = (long)r.materials, ["texturen"] = r.textures.Cast<object>().ToList(), ["knochen"] = (long)r.bones,
                        ["statur_ampel"] = r.staturAmpel.ToString(), ["budget_ampel"] = r.budgetAmpel.ToString(),
                        ["warnungen"] = r.warnings.Cast<object>().ToList(), ["teile"] = (long)r.build.instances.Count,
                    };
                    entry["sitz"] = Render(b, doc, r, shots);
                    VariantKitWindow.SmokeTest(f, Path.Combine(shots, doc.ExportName + "_fenster_walk.png"), "Walk", 0.4f);
                    report.List("varianten").Add(entry);
                }
                File.WriteAllText(Path.Combine(shots, "selbstpruefung.json"), Json.Write(report));
                Debug.Log("[VariantKit] SELBSTPRUEFUNG OK → " + shots);
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[VariantKit] FEHLER " + ex);
                EditorApplication.Exit(1);
            }
        }

        public static void Pose(Vector2 v, Vector3 focus, float dist, out Vector3 pos, out Quaternion rot)
        {
            rot = Quaternion.Euler(v.y, v.x, 0f);
            pos = focus - rot * Vector3.forward * dist;
        }

        public static readonly Vector2 ViewArpg = new Vector2(150f, 50f), ViewSide = new Vector2(90f, 5f), ViewFront = new Vector2(180f, 10f), ViewTop = new Vector2(180f, 89f);

        public static AnimationClip Clip(VkBase b, string label) => b.clips.FirstOrDefault(c => c.name.EndsWith("_" + label)) ?? b.clips.FirstOrDefault();

        static JObj Render(VkBase b, VkDoc doc, VkBakeResult r, string outDir)
        {
            EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;   // neutrales Umgebungslicht → Farben vergleichbar
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
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(r.prefabPath);
            var go = (GameObject)UnityEngine.Object.Instantiate(prefab);
            var model = go.transform.GetChild(0).gameObject;
            var smr = model.GetComponentInChildren<SkinnedMeshRenderer>();
            var st = model.GetComponent<VariantStatur>();
            int size = 768;
            var rt = new RenderTexture(size, size, 24) { antiAliasing = 4 };
            cam.targetTexture = rt;
            Shader.SetGlobalFloat("_VKUseTime", 1f);

            void SetPose(string clip, float t)
            {
                if (clip == null) VkBuilder.RestPose(model);
                else { var c = Clip(b, clip); c.SampleAnimation(model, c.length * t); }
                if (st != null) st.Apply();
                Shader.SetGlobalFloat("_VKTime", t * 2f);
            }
            SetPose(null, 0);
            var bounds = smr.bounds;
            var mb = new Mesh(); smr.BakeMesh(mb, true);
            var bb = new Bounds(smr.transform.TransformPoint(mb.vertices[0]), Vector3.zero);
            foreach (var v in mb.vertices) bb.Encapsulate(smr.transform.TransformPoint(v));
            UnityEngine.Object.DestroyImmediate(mb);
            float ext = Mathf.Max(bb.size.x, bb.size.y, bb.size.z);
            void Shot(string tag, Vector2 view, float zoom = 2.3f)
            {
                Pose(view, bb.center, ext * zoom, out var pos, out var rot);
                cam.transform.SetPositionAndRotation(pos, rot);
                cam.nearClipPlane = ext * 0.02f;
                cam.Render();
                RenderTexture.active = rt;
                var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, size, size), 0, 0);
                tex.Apply();
                File.WriteAllBytes(Path.Combine(outDir, $"{doc.ExportName}_{tag}.png"), tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex);
            }
            SetPose(null, 0); Shot("arpg_rest", ViewArpg); Shot("side_rest", ViewSide); Shot("front_rest", ViewFront); Shot("design_view", new Vector2(120f, 22f), 2.0f);
            foreach (var t in new[] { 0.15f, 0.4f, 0.65f }) { SetPose("Walk", t); Shot($"walk_{(int)(t * 100):00}", ViewArpg); }
            foreach (var t in new[] { 0.3f, 0.55f, 0.8f }) { SetPose("Attack2", t); Shot($"attack2_{(int)(t * 100):00}", ViewArpg); }
            SetPose("Attack2", 0.55f); Shot("attack2_55_side", ViewSide);
            RenderTexture.active = null;
            cam.targetTexture = null;
            Shader.SetGlobalFloat("_VKUseTime", 0f);

            var sitz = Seating(b, r.build, model, smr, st);
            UnityEngine.Object.DestroyImmediate(go);
            return sitz;
        }

        /// <summary>Sitz der Accessoires in der Bewegung: Unterseite jedes Teils gegen den nächsten Hautpunkt (Ruhepose),
        /// Abstand entlang der Hautnormale. Δ &gt; 0 = schwebt ab, Δ &lt; 0 = sinkt ein (cm, Welt).</summary>
        public static JObj Seating(VkBase b, VkBuildResult res, GameObject model, SkinnedMeshRenderer smr, VariantStatur st)
        {
            var mesh = smr.sharedMesh;
            var mv = mesh.vertices; var mw = mesh.boneWeights; var bp = mesh.bindposes;
            var probes = new List<(string acc, int pv, int tri, Vector3 bary, float d0)>();
            foreach (var inst in res.instances)
            {
                var form = VkParts.Get(inst.typ).First(f => f.name == inst.form);
                for (int k = 0; k < form.v.Length; k++)
                {
                    if (form.v[k].z > form.height * 0.3f) continue;
                    int pv = inst.vStart + k;
                    var c = VkBuilder.Closest(b, res.dv, res.dn, mv[pv]);
                    if (c.tri < 0) continue;
                    probes.Add((inst.acc, pv, c.tri, c.bary, Vector3.Dot(mv[pv] - c.pos, c.nrm)));
                }
            }
            var bones = smr.bones;
            Vector3 Skin(int v, Matrix4x4[] M)
            {
                var w = mw[v];
                return M[w.boneIndex0].MultiplyPoint3x4(mv[v]) * w.weight0 + M[w.boneIndex1].MultiplyPoint3x4(mv[v]) * w.weight1 +
                       M[w.boneIndex2].MultiplyPoint3x4(mv[v]) * w.weight2 + M[w.boneIndex3].MultiplyPoint3x4(mv[v]) * w.weight3;
            }
            var worst = new Dictionary<string, (float plus, float minus)>();
            float[] Dist(Matrix4x4[] M)
            {
                var res2 = new float[probes.Count];
                for (int q = 0; q < probes.Count; q++)
                {
                    var p = probes[q];
                    int t0 = b.tris[p.tri * 3], t1 = b.tris[p.tri * 3 + 1], t2 = b.tris[p.tri * 3 + 2];
                    Vector3 a = Skin(t0, M), bb = Skin(t1, M), cc = Skin(t2, M);
                    var sp = a * p.bary.x + bb * p.bary.y + cc * p.bary.z;
                    var n = Vector3.Cross(bb - a, cc - a).normalized;
                    var rest = Vector3.Cross(res.dv[t1] - res.dv[t0], res.dv[t2] - res.dv[t0]);
                    if (Vector3.Dot(rest, res.dn[t0] + res.dn[t1] + res.dn[t2]) < 0) n = -n;   // Normalen-Richtung wie in der Ruhe
                    res2[q] = Vector3.Dot(Skin(p.pv, M) - sp, n);
                }
                return res2;
            }
            Matrix4x4[] Mats()
            {
                if (st != null) st.Apply();
                var M = new Matrix4x4[bones.Length];
                for (int j = 0; j < bones.Length; j++) M[j] = bones[j].localToWorldMatrix * bp[j];
                return M;
            }
            VkBuilder.RestPose(model);
            var d0 = Dist(Mats());
            foreach (var clip in new[] { "Walk", "Run", "Attack1", "Attack2", "Idle", "TurnLeft" })
            {
                var c = Clip(b, clip);
                if (c == null || !c.name.EndsWith(clip)) continue;
                for (int k = 0; k <= 16; k++)
                {
                    c.SampleAnimation(model, c.length * k / 16f);
                    var d = Dist(Mats());
                    for (int q = 0; q < probes.Count; q++)
                    {
                        float delta = d[q] - d0[q];
                        worst.TryGetValue(probes[q].acc, out var wv);
                        worst[probes[q].acc] = (Mathf.Max(wv.plus, delta), Mathf.Min(wv.minus, delta));
                    }
                }
            }
            var o = new JObj();
            foreach (var kv in worst)
                o[kv.Key] = new JObj { ["schwebt_max_cm"] = (double)(kv.Value.plus * 100), ["sinkt_max_cm"] = (double)(-kv.Value.minus * 100) };
            Debug.Log("[VariantKit] SITZ " + string.Join(" · ", worst.Select(kv => $"{kv.Key}: +{kv.Value.plus * 100:0.0}/-{-kv.Value.minus * 100:0.0} cm")));
            return o;
        }
    }
}
