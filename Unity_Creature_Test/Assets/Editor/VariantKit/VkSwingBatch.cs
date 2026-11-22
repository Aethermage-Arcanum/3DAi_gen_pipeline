using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Debug = UnityEngine.Debug;

namespace VariantKit
{
    /// <summary>G14 Nachschwingen – Helfer (Vorschau-Fenster) und Selbstprüfung headless:
    ///   Unity.exe -batchmode -projectPath Unity_Creature_Test -executeMethod VariantKit.VkSwingBatch.Run -logFile log.txt
    ///     -vkVariants "a;b"   Varianten-Dateien (Standard: alle creatures/*/varianten)   -vkShots &lt;ordner&gt;   -vkBlender
    ///     -vkPerf             Kosten der Komponente messen (300 Gegner)
    /// Pro Variante: backen, dann zwei Bildfolgen in der ARPG-Ansicht, jedes Bild zweimal (ohne | mit Nachschwingen):
    ///   lauf    Idle → Walk → Run → Stopp → Idle (das Modell wandert wirklich, die Kamera folgt)
    ///   angriff Idle → Attack2 (Event hit) → Idle → Ready (Event slam) → Idle
    /// Ausgabe &lt;shots&gt;/&lt;Name&gt;_&lt;folge&gt;/ohne_000.png, mit_000.png, werte.json (Auslenkung pro Feder, Tempo).</summary>
    public static class VkSwingBatch
    {
        static string Arg(string name)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, name);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        // ------------------------------------------------------------------ Helfer (auch für das Fenster)
        public static Vector3 WorldForward(VkBase b, GameObject model)
        {
            Transform Find(string n) => model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == n);
            var hips = Find("Hips") ?? Find("Pelvis"); var head = Find("Head");
            if (hips != null && head != null)
            {
                var f = head.position - hips.position; f.y = 0;
                if (f.sqrMagnitude > 1e-8f) return f.normalized;
            }
            return model.transform.forward;
        }

        static readonly Dictionary<string, float> speedCache = new Dictionary<string, float>();

        /// <summary>Boden-Tempo eines Clips (m/s), der auf der Stelle läuft: Rückwärts-Geschwindigkeit der Füße, solange sie
        /// den Boden berühren. Pose des Modells bleibt erhalten.</summary>
        public static float GroundSpeed(VkBase b, AnimationClip c, GameObject model) => GroundSpeed(b.id, b.L * b.meshToMeter, c, model);

        public static float GroundSpeed(string id, float size, AnimationClip c, GameObject model)
        {
            string key = id + "|" + c.name;
            if (speedCache.TryGetValue(key, out var sp)) return sp;
            var all = model.GetComponentsInChildren<Transform>(true);
            var save = all.Select(t => (t.localPosition, t.localRotation, t.localScale)).ToArray();
            var feet = all.Where(t => Regex.IsMatch(t.name, "^Leg_[FB][LR]_\\d+$")).GroupBy(t => t.name.Substring(0, 6))
                .Select(g => g.OrderByDescending(t => int.Parse(t.name.Substring(7))).First()).ToList();
            if (feet.Count == 0) feet = all.Where(t => Regex.IsMatch(t.name, "^Foot_[LR]$")).ToList();   // Zweibeiner (upright)
            VkBuilder.RestPose(model);
            var fwd = model.transform.InverseTransformDirection(WorldForward(null, model));
            int N = 60;
            var pos = new Vector3[feet.Count, N + 1];
            for (int k = 0; k <= N; k++)
            {
                c.SampleAnimation(model, c.length * k / N);
                for (int f = 0; f < feet.Count; f++) pos[f, k] = model.transform.InverseTransformPoint(feet[f].position);
            }
            var vals = new List<float>();
            float dt = c.length / N;
            for (int f = 0; f < feet.Count; f++)
            {
                float minY = float.MaxValue;
                for (int k = 0; k <= N; k++) minY = Mathf.Min(minY, pos[f, k].y);
                for (int k = 0; k < N; k++)
                    if (pos[f, k].y < minY + 0.02f * size && pos[f, k + 1].y < minY + 0.02f * size)
                        vals.Add(-Vector3.Dot(pos[f, k + 1] - pos[f, k], fwd) / dt);
            }
            for (int i = 0; i < all.Length; i++) { all[i].localPosition = save[i].localPosition; all[i].localRotation = save[i].localRotation; all[i].localScale = save[i].localScale; }
            vals.Sort();
            sp = vals.Count > 0 ? Mathf.Max(0, vals[vals.Count / 2]) : 0;
            speedCache[key] = sp;
            return sp;
        }

        /// <summary>Clip-Events „VKStoss“ zwischen t0 (exklusiv) und t1 (inklusiv) auslösen; t1 &lt; t0 = Clip ist umgelaufen.</summary>
        public static void FireEvents(AnimationClip c, float t0, float t1, VariantSchwingen sw, bool log = false,
            Func<AnimationClip, IEnumerable<(float time, string art)>> source = null)
        {
            if (sw == null) return;
            var evs = source != null ? source(c) : AnimationUtility.GetAnimationEvents(c).Where(e => e.functionName == "VKStoss").Select(e => (e.time, e.stringParameter));
            foreach (var (time, art) in evs)
            {
                bool hit = t1 >= t0 ? time > t0 && time <= t1 : time > t0 || time <= t1;
                if (!hit) continue;
                sw.VKStoss(art);
                if (log) Debug.Log($"[VariantKit] G14 STOSS {art} aus Clip {c.name} bei {time:0.00} s");
            }
        }

        // ------------------------------------------------------------------ Bildfolgen
        struct Seg { public string clip; public float dur, speed, ramp, fade; public bool loop; }

        class Pose
        {
            public Transform[] t; public Vector3[] p; public Quaternion[] r;
            public Pose(Transform[] all) { t = all; p = new Vector3[all.Length]; r = new Quaternion[all.Length]; }
            public void Grab() { for (int i = 0; i < t.Length; i++) { p[i] = t[i].localPosition; r[i] = t[i].localRotation; } }
        }

        public static void Run()
        {
            try
            {
                var shots = Arg("-vkShots") ?? Path.Combine(VkBase.PipelineRoot, "temp", "g14_shots");
                Directory.CreateDirectory(shots);
                var files = Arg("-vkVariants")?.Split(';').Where(s => s.Length > 0).ToList()
                            ?? Directory.GetDirectories(Path.Combine(VkBase.PipelineRoot, "creatures"))
                                .Select(d => Path.Combine(d, "varianten")).Where(Directory.Exists)
                                .SelectMany(d => Directory.GetFiles(d, "*.variant.json")).ToList();
                var report = new JObj { ["datum"] = DateTime.Now.ToString("s"), ["varianten"] = new List<object>() };
                string perfPrefab = null;
                foreach (var f in files)
                {
                    var doc = VkDoc.Load(f);
                    var b = VkBase.Load(doc.resolved.S("basis", ""));
                    if (Environment.GetCommandLineArgs().Contains("-vkBlender") && VkCover.HasLayers(doc))
                    {
                        var pre = VkBuilder.Build(b, doc);
                        VkBake.WriteInstances(b, doc, pre, doc.InstancesPath);
                        UnityEngine.Object.DestroyImmediate(pre.mesh);
                        var job = VkBlenderJob.Start(doc.path);
                        bool ok = job.Wait();
                        VkCover.Invalidate();
                        Debug.Log($"[VariantKit] IN BLENDER BAUEN {doc.Id}: {(ok ? "ok" : "FEHLER " + job.error)} · {job.info}");
                        if (!ok) throw new Exception("In Blender bauen fehlgeschlagen: " + job.error);
                    }
                    var r = VkBake.Bake(b, doc);
                    var swingParts = r.build.instances.Where(i => i.weich > 0).ToList();
                    int swingVerts = swingParts.Sum(i => i.vCount);
                    var entry = new JObj
                    {
                        ["id"] = doc.Id, ["prefab"] = r.prefabPath, ["tris"] = (long)r.tris, ["warnungen"] = r.warnings.Cast<object>().ToList(),
                        ["schwingende_teile"] = (long)swingParts.Count, ["schwingende_vertices"] = (long)swingVerts,
                        ["vertices"] = (long)r.tex.mesh.vertexCount,
                    };
                    var wj = new JObj();
                    foreach (var g in swingParts.GroupBy(i => i.acc)) wj[g.Key] = (double)g.First().weich;
                    entry["weichheit"] = wj;
                    Debug.Log($"[VariantKit] G14 {doc.ExportName}: {swingParts.Count} schwingende Teile, {swingVerts}/{r.tex.mesh.vertexCount} Vertices · " +
                              string.Join(", ", swingParts.GroupBy(i => i.acc).Select(g => $"{g.Key} w={g.First().weich:0.00} slot={string.Join("/", g.Select(x => x.slot).Distinct())}")));
                    var seqs = new JObj();
                    foreach (var seq in new[] { "lauf", "angriff" }) seqs[seq] = Sequence(seq, b, doc, r, shots);
                    entry["folgen"] = seqs;
                    report.List("varianten").Add(entry);
                    if (perfPrefab == null && swingParts.Count > 0) perfPrefab = r.prefabPath;
                }
                if (Environment.GetCommandLineArgs().Contains("-vkPerf") && perfPrefab != null) report["kosten"] = Perf(perfPrefab);
                File.WriteAllText(Path.Combine(shots, "g14_pruefung.json"), Json.Write(report));
                Debug.Log("[VariantKit] G14 OK → " + shots);
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[VariantKit] FEHLER " + ex);
                EditorApplication.Exit(1);
            }
        }

        static List<Seg> Plan(string seq, VkBase b, GameObject model)
        {
            var walk = VkBatch.Clip(b, "Walk"); var run = VkBatch.Clip(b, "Run");
            float vw = GroundSpeed(b, walk, model), vr = GroundSpeed(b, run, model);
            Debug.Log($"[VariantKit] G14 Boden-Tempo {b.name}: Walk {vw:0.00} m/s, Run {vr:0.00} m/s · Clip-Events: " +
                      string.Join(", ", b.clips.Select(c => $"{c.name}={AnimationUtility.GetAnimationEvents(c).Length}")));
            if (seq == "lauf")
                return new List<Seg>
                {
                    new Seg { clip = "Idle", dur = 0.6f, loop = true },
                    new Seg { clip = "Walk", dur = 2.0f, speed = vw, ramp = 0.45f, fade = 0.25f, loop = true },
                    new Seg { clip = "Run", dur = 2.0f, speed = vr, ramp = 0.45f, fade = 0.25f, loop = true },
                    new Seg { clip = "Idle", dur = 2.2f, speed = 0, ramp = 0.3f, fade = 0.3f, loop = true },
                };
            var a2 = VkBatch.Clip(b, "Attack2"); var rd = VkBatch.Clip(b, "Ready");
            return new List<Seg>
            {
                new Seg { clip = "Idle", dur = 0.5f, loop = true },
                new Seg { clip = "Attack2", dur = a2.length, fade = 0.15f },
                new Seg { clip = "Idle", dur = 0.9f, fade = 0.25f, loop = true },
                new Seg { clip = "Ready", dur = rd.length, fade = 0.2f },
                new Seg { clip = "Idle", dur = 1.4f, fade = 0.25f, loop = true },
            };
        }

        static void Stage()
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
            ground.transform.localScale = Vector3.one * 20f;
            var gm = new Material(Shader.Find("Standard")) { color = new Color(0.30f, 0.30f, 0.31f) };
            ground.GetComponent<Renderer>().sharedMaterial = gm;
            // Bodenraster, damit man die Fortbewegung sieht
            var tex = new Texture2D(64, 64) { filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Repeat };
            for (int y = 0; y < 64; y++) for (int x = 0; x < 64; x++) tex.SetPixel(x, y, (x < 2 || y < 2) ? new Color(0.22f, 0.22f, 0.23f) : new Color(0.31f, 0.31f, 0.32f));
            tex.Apply();
            gm.mainTexture = tex; gm.mainTextureScale = new Vector2(100, 100);   // Kachel 2 m

        }

        static JObj Sequence(string seq, VkBase b, VkDoc doc, VkBakeResult r, string shotsRoot)
        {
            Stage();
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(r.prefabPath);
            var go = (GameObject)UnityEngine.Object.Instantiate(prefab);
            var model = go.transform.GetChild(0).gameObject;
            var smr = model.GetComponentInChildren<SkinnedMeshRenderer>();
            var st = model.GetComponent<VariantStatur>();
            var sw = model.GetComponent<VariantSchwingen>();
            var segs = Plan(seq, b, model);
            return Film($"{doc.ExportName}_{seq}", go, model, smr, st, sw, l => VkBatch.Clip(b, l), null, segs, shotsRoot);
        }

        /// <summary>Bildfolge (ohne | mit) für ein Modell: Clips nach Plan, Modell wandert, Kamera folgt in der ARPG-Ansicht.</summary>
        static JObj Film(string name, GameObject go, GameObject model, SkinnedMeshRenderer smr, VariantStatur st, VariantSchwingen sw,
            Func<string, AnimationClip> clipFn, Func<AnimationClip, IEnumerable<(float time, string art)>> eventsFn, List<Seg> segs, string shotsRoot)
        {
            bool swings = sw != null && sw.enabled;
            if (sw != null) { sw.manuell = true; sw.enabled = true; sw.Binden(); }
            var all = model.GetComponentsInChildren<Transform>(true);
            var pa = new Pose(all); var pb = new Pose(all);
            var cam = Camera.main;

            VkBuilder.RestPose(model);
            var mb = new Mesh(); smr.BakeMesh(mb, true);
            var bb = new Bounds(smr.transform.TransformPoint(mb.vertices[0]), Vector3.zero);
            foreach (var v in mb.vertices) bb.Encapsulate(smr.transform.TransformPoint(v));
            UnityEngine.Object.DestroyImmediate(mb);
            float ext = Mathf.Max(bb.size.x, bb.size.y, bb.size.z);
            var focusOff = bb.center - go.transform.position;
            // Laufrichtung quer zur ARPG-Kamera (im Spiel laufen Gegner in alle Richtungen) → das Nachziehen ist von der Seite zu sehen
            var fwd0 = WorldForward(null, model);
            var camRight = Quaternion.Euler(VkBatch.ViewArpg.y, VkBatch.ViewArpg.x, 0) * Vector3.right; camRight.y = 0; camRight.Normalize();
            go.transform.rotation = Quaternion.FromToRotation(fwd0, -camRight) * go.transform.rotation;
            focusOff = Quaternion.FromToRotation(fwd0, -camRight) * (bb.center - go.transform.position);
            var fwd = WorldForward(null, model);

            int W = 340, fps = 20;
            var rt = new RenderTexture(W, W, 24) { antiAliasing = 4 };
            cam.targetTexture = rt;
            var outDir = Path.Combine(shotsRoot, name);
            if (Directory.Exists(outDir)) Directory.Delete(outDir, true);
            Directory.CreateDirectory(outDir);
            Shader.SetGlobalFloat("_VKUseTime", 1f);
            var rp = new Texture2D(W, W, TextureFormat.RGB24, false);
            void Shot(string tag, int frame)
            {
                cam.Render();
                RenderTexture.active = rt;
                rp.ReadPixels(new Rect(0, 0, W, W), 0, 0);
                rp.Apply();
                File.WriteAllBytes(Path.Combine(outDir, $"{tag}_{frame:000}.png"), rp.EncodeToPNG());
            }

            float total = segs.Sum(s => s.dur), dt = 1f / fps, speed = 0, t = 0;
            var werte = new List<object>();
            int frame = 0, si = 0; float segStart = 0, startSpeed = 0;
            float prevClipT = -1;
            Vector3 camFocus = go.transform.position + focusOff;
            while (t < total - 1e-4f)
            {
                while (si < segs.Count - 1 && t >= segStart + segs[si].dur) { segStart += segs[si].dur; startSpeed = speed; si++; prevClipT = -1; }
                var s = segs[si];
                float lt = t - segStart;
                speed = s.ramp > 0 ? Mathf.Lerp(startSpeed, s.speed, Mathf.SmoothStep(0, 1, Mathf.Clamp01(lt / s.ramp))) : s.speed;
                // Pose: aktueller Clip, am Anfang aus dem vorigen überblendet
                var c = clipFn(s.clip);
                float ct = s.loop ? lt % c.length : Mathf.Min(lt, c.length);
                c.SampleAnimation(model, ct);
                if (si > 0 && s.fade > 0 && lt < s.fade)
                {
                    pb.Grab();
                    var ps = segs[si - 1]; var pc = clipFn(ps.clip);
                    float plt = t - (segStart - ps.dur);
                    pc.SampleAnimation(model, ps.loop ? plt % pc.length : Mathf.Min(plt, pc.length));
                    pa.Grab();
                    float w = Mathf.SmoothStep(0, 1, lt / s.fade);
                    for (int i = 0; i < all.Length; i++)
                    {
                        all[i].localPosition = Vector3.Lerp(pa.p[i], pb.p[i], w);
                        all[i].localRotation = Quaternion.Slerp(pa.r[i], pb.r[i], w);
                    }
                }
                if (st != null) st.Apply();
                go.transform.position += fwd * speed * dt;
                if (sw != null)
                {
                    if (prevClipT >= 0) FireEvents(c, prevClipT, ct, sw, true, eventsFn);
                    sw.Step(frame == 0 ? 0 : dt);
                }
                prevClipT = ct;
                Shader.SetGlobalFloat("_VKTime", t);
                camFocus = go.transform.position + focusOff;
                VkBatch.Pose(VkBatch.ViewArpg, camFocus, ext * 2.5f, out var cpos, out var crot);
                cam.transform.SetPositionAndRotation(cpos, crot);
                cam.nearClipPlane = ext * 0.02f;
                Shot("mit", frame);
                smr.SetPropertyBlock(null);   // gleiche Pose, ohne Nachschwingen
                Shot("ohne", frame);
                if (sw != null)
                    werte.Add(new JObj
                    {
                        ["t"] = (double)Math.Round(t, 3), ["clip"] = s.clip, ["tempo"] = (double)Math.Round(speed, 3),
                        ["huefte"] = (double)Math.Round(sw.Auslenkung(0).magnitude, 4), ["brust"] = (double)Math.Round(sw.Auslenkung(1).magnitude, 4),
                        ["kopf"] = (double)Math.Round(sw.Auslenkung(2).magnitude, 4), ["schwanz"] = (double)Math.Round(sw.Auslenkung(3).magnitude, 4),
                    });
                t += dt; frame++;
            }
            RenderTexture.active = null;
            cam.targetTexture = null;
            Shader.SetGlobalFloat("_VKUseTime", 0f);
            UnityEngine.Object.DestroyImmediate(rp);
            UnityEngine.Object.DestroyImmediate(go);
            var info = new JObj
            {
                ["bilder"] = (long)frame, ["fps"] = (long)fps, ["schwingt"] = swings, ["ordner"] = outDir,
                ["max_auslenkung_rad"] = werte.Count == 0 ? 0.0 : (double)werte.Cast<JObj>().Max(x => new[] { "huefte", "brust", "kopf", "schwanz" }.Max(k => x.F(k, 0))),
                ["werte"] = werte,
            };
            File.WriteAllText(Path.Combine(outDir, "werte.json"), Json.Write(info));
            Debug.Log($"[VariantKit] G14 FOLGE {name}: {frame} Bilder, schwingt={swings}, max. Auslenkung {Json.ToF(info["max_auslenkung_rad"], 0):0.000} rad");
            info.Remove("werte");
            return info;
        }

        // ------------------------------------------------------------------ C13: Bog Warden (Creature/Standard Dangling + Schalter)
        /// <summary>Unity.exe -batchmode -projectPath &lt;Kopie mit importierten Kreaturen&gt; -executeMethod VariantKit.VkSwingBatch.RunC13
        ///   -vkShots &lt;ordner&gt; [-vkCreature BogWarden]. Schaltet den Schalter per creature.toml ein (VkDangleSwing) und filmt
        /// Walk → Run → Stopp und Attack1/Attack2 (Events hit aus &lt;Name&gt;_events.json): links ohne, rechts mit Nachschwingen.</summary>
        public static void RunC13()
        {
            try
            {
                string name = Arg("-vkCreature") ?? "BogWarden";
                var shots = Arg("-vkShots") ?? Path.Combine(VkBase.PipelineRoot, "temp", "g14_c13");
                Directory.CreateDirectory(shots);
                string dir = $"Assets/Creatures/{name}", fbx = $"{dir}/{name}.fbx", matPath = $"{dir}/{name}.mat";
                bool on = VkDangleSwing.Apply(matPath);
                var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
                Debug.Log($"[VariantKit] C13 {name}: Schalter {(mat.IsKeywordEnabled("_VK_NACHSCHWINGEN") ? "AN" : "aus")} (creature.toml: {on}), Shader {mat.shader.name}, Länge {mat.GetFloat("_VKDangleLen")} m, Feder {mat.GetFloat("_VKDangleSlot")}");
                var clips = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<AnimationClip>().Where(a => !a.name.StartsWith("__preview__")).ToList();
                AnimationClip Clip(string l) => clips.FirstOrDefault(c => c.name.EndsWith("_" + l)) ?? clips.First();
                var ev = Json.ParseObj(File.ReadAllText($"{dir}/{name}_events.json"));
                float fpsE = ev.F("fps", 30);
                IEnumerable<(float, string)> Events(AnimationClip c)
                {
                    string cn = c.name.Contains("|") ? c.name.Substring(c.name.LastIndexOf('|') + 1) : c.name;
                    return (ev.O("clips")?.L(cn) ?? new List<object>()).OfType<JObj>().Where(e => e.S("event", "") == "hit" || e.S("event", "") == "slam")
                        .Select(e => (e.F("frame", 0) / fpsE, e.S("event", ""))).ToList();
                }
                var report = new JObj();
                foreach (var seq in new[] { "lauf", "angriff" })
                {
                    Stage();
                    var model = (GameObject)UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(fbx));
                    var go = new GameObject(name);
                    model.transform.SetParent(go.transform, false);
                    var smr = model.GetComponentInChildren<SkinnedMeshRenderer>();
                    smr.sharedMaterial = mat;
                    var lb = smr.localBounds; lb.Expand(lb.size.magnitude * 0.3f); smr.localBounds = lb;
                    var sw = model.AddComponent<VariantSchwingen>();
                    sw.Binden();
                    sw.groesse = Mathf.Max(smr.bounds.size.x, smr.bounds.size.y, smr.bounds.size.z);
                    // Boden: tiefster Punkt der Ruhepose auf y = 0
                    var mb = new Mesh(); smr.BakeMesh(mb, true);
                    float minY = mb.vertices.Min(v => smr.transform.TransformPoint(v).y);
                    UnityEngine.Object.DestroyImmediate(mb);
                    model.transform.position -= new Vector3(0, minY, 0);
                    float vw = GroundSpeed(name, sw.groesse, Clip("Walk"), model), vr = GroundSpeed(name, sw.groesse, Clip("Run"), model);
                    Debug.Log($"[VariantKit] C13 {name}: Größe {sw.groesse:0.00} m, Walk {vw:0.00} m/s, Run {vr:0.00} m/s, Federn {string.Join(", ", sw.ansatz.Select(t => t ? t.name : "-"))}");
                    var segs = seq == "lauf"
                        ? new List<Seg>
                        {
                            new Seg { clip = "Idle", dur = 0.6f, loop = true },
                            new Seg { clip = "Walk", dur = 2.0f, speed = vw, ramp = 0.45f, fade = 0.25f, loop = true },
                            new Seg { clip = "Run", dur = 2.0f, speed = vr, ramp = 0.45f, fade = 0.25f, loop = true },
                            new Seg { clip = "Idle", dur = 2.2f, speed = 0, ramp = 0.3f, fade = 0.3f, loop = true },
                        }
                        : new List<Seg>
                        {
                            new Seg { clip = "Idle", dur = 0.5f, loop = true },
                            new Seg { clip = "Attack1", dur = Clip("Attack1").length, fade = 0.15f },
                            new Seg { clip = "Idle", dur = 0.8f, fade = 0.25f, loop = true },
                            new Seg { clip = "Attack2", dur = Clip("Attack2").length, fade = 0.15f },
                            new Seg { clip = "Idle", dur = 1.4f, fade = 0.25f, loop = true },
                        };
                    report[seq] = Film($"{name}_{seq}", go, model, smr, null, sw, Clip, Events, segs, shots);
                }
                File.WriteAllText(Path.Combine(shots, "c13_pruefung.json"), Json.Write(report));
                Debug.Log("[VariantKit] C13 OK → " + shots);
                EditorApplication.Exit(0);
            }
            catch (Exception ex)
            {
                Debug.LogError("[VariantKit] FEHLER " + ex);
                EditorApplication.Exit(1);
            }
        }

        // ------------------------------------------------------------------ Kosten
        /// <summary>Zeit von VariantSchwingen.Step pro Gegner (300 Instanzen, je 200 Schritte), Editor-Mono.</summary>
        static JObj Perf(string prefabPath)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            int n = 300, steps = 200;
            var list = new List<VariantSchwingen>();
            for (int i = 0; i < n; i++)
            {
                var go = (GameObject)UnityEngine.Object.Instantiate(prefab, new Vector3(i % 20 * 3f, 0, i / 20 * 3f), Quaternion.identity);
                var sw = go.GetComponentInChildren<VariantSchwingen>();
                sw.manuell = true; sw.enabled = true; sw.Binden();
                list.Add(sw);
            }
            for (int k = 0; k < 20; k++) foreach (var sw in list) sw.Step(1f / 60f);
            var watch = Stopwatch.StartNew();
            for (int k = 0; k < steps; k++)
            {
                foreach (var sw in list)
                {
                    sw.transform.position += new Vector3(0.02f, 0, 0);   // wandert → echte Rechnung
                    sw.Step(1f / 60f);
                }
            }
            watch.Stop();
            var w2 = Stopwatch.StartNew();
            for (int k = 0; k < steps; k++) foreach (var sw in list) sw.transform.position += new Vector3(0.02f, 0, 0);
            w2.Stop();
            double ms = (watch.Elapsed.TotalMilliseconds - w2.Elapsed.TotalMilliseconds) / (n * (double)steps);
            Debug.Log($"[VariantKit] G14 KOSTEN VariantSchwingen.Step: {ms * 1000:0.0} µs pro Gegner und Frame ({n} Gegner × {steps} Schritte, Editor-Mono, ohne Rendering)");
            return new JObj { ["ms_pro_gegner"] = ms, ["gegner"] = (long)n, ["schritte"] = (long)steps, ["umgebung"] = "Editor-Batch (Mono), CPU-Seite inkl. SetPropertyBlock" };
        }
    }
}
