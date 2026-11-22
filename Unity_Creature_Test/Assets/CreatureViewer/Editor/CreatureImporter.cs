using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Playables;

/// <summary>
/// Holt alle fertigen Kreaturen aus der Pipeline (../creatures/*/output/*.fbx) ins Projekt, stellt den Import ein
/// (Generic-Rig, Schleifen laut Pipeline) und baut Katalog + Test-Szene neu.
///   Menü:      Kreaturen › Alle importieren + Szene bauen
///   Automatisch: beim Öffnen des Projekts, wenn eine Kreatur neu/geändert ist
///   Headless:  Unity.exe -batchmode -projectPath Unity -executeMethod CreatureImporter.Batch -quit
///              optional: -creaturesRoot <ordner mit Kreatur-Unterordnern>  -shotsDir <ordner für Prüfbilder>
/// Frei hängende Teile: liegt neben der FBX ein <Name>_dangling.json (rigging/export_unity.py, nur bei markiertem Mesh),
/// bekommt die Kreatur den Shader "Creature/Standard Dangling" (schwingt ohne Knochen), sonst den normalen Standard-Shader.
/// Alles unter Assets/Creatures und Assets/CreatureViewer/Generated ist erzeugt (nicht von Hand ändern, nicht versioniert).
/// </summary>
[InitializeOnLoad]
public static class CreatureImporter
{
    public const string CreaturesDir = "Assets/Creatures";
    public const string GenDir = "Assets/CreatureViewer/Generated";
    public const string CatalogPath = GenDir + "/CreatureCatalog.asset";
    public const string ScenePath = GenDir + "/CreatureViewer.unity";
    static readonly string[] Order = { "Walk", "Run", "Idle", "Ready", "TurnLeft", "TurnRight", "Attack1", "Hit", "Death" };

    public const string DangleShader = "Creature/Standard Dangling";

    static string PipelineRoot => Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));

    /// <summary>Wert eines Kommandozeilen-Arguments (-name wert) oder null.</summary>
    static string Arg(string name)
    {
        var a = Environment.GetCommandLineArgs();
        int i = Array.IndexOf(a, name);
        return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
    }

    /// <summary>Woher die Kreaturen kommen: Standard ../creatures, für Tests per -creaturesRoot umlenkbar.</summary>
    static string CreaturesSource => Arg("-creaturesRoot") ?? Path.Combine(PipelineRoot, "creatures");

    static CreatureImporter()
    {
        if (Application.isBatchMode) return;
        EditorApplication.delayCall += () =>
        {
            if (!File.Exists(ScenePath) || Sources().Any(s => NeedsCopy(s.fbx, Dest(s.name))))
            {
                Debug.Log("[Kreaturen] Neue/geänderte Kreaturen gefunden – importiere automatisch …");
                ImportAll();
            }
        };
    }

    [MenuItem("Kreaturen/Alle importieren + Szene bauen")]
    public static void ImportAllAndOpen()
    {
        ImportAll();
        EditorSceneManager.OpenScene(ScenePath);
    }

    /// <summary>Für die Kommandozeile: importieren, Szene bauen, Prüfbilder rendern, beenden.</summary>
    public static void Batch()
    {
        try
        {
            ImportAll();
            var shots = Arg("-shotsDir") ?? Path.Combine(PipelineRoot, "temp", "unity_shots");
            Screenshots(shots);
            DangleShots(shots);
            PlaybackSelfTest();
            EditorApplication.Exit(0);
        }
        catch (Exception ex)
        {
            Debug.LogError("[Kreaturen] FEHLER " + ex);
            EditorApplication.Exit(1);
        }
    }

    // ------------------------------------------------------------------ Quellen + Kopieren
    struct Source { public string name, fbx, report, events, dangling; }

    static IEnumerable<Source> Sources()
    {
        var dir = CreaturesSource;
        if (!Directory.Exists(dir)) yield break;
        foreach (var c in Directory.GetDirectories(dir).OrderBy(d => d))
        {
            var outDir = Path.Combine(c, "output");
            if (!Directory.Exists(outDir)) continue;
            foreach (var fbx in Directory.GetFiles(outDir, "*.fbx"))
            {
                var name = Path.GetFileNameWithoutExtension(fbx);
                yield return new Source
                {
                    name = name, fbx = fbx,
                    report = Path.Combine(c, "rig", "clips_report.json"),
                    events = Path.Combine(outDir, name + "_events.json"),
                    dangling = Path.Combine(outDir, name + "_dangling.json"),
                };
            }
        }
    }

    public static string GroundFile(string name) => $"{CreaturesDir}/{name}/{name}_ground.txt";

    static string Dest(string name) => $"{CreaturesDir}/{name}/{name}.fbx";

    static bool NeedsCopy(string src, string dst)
    {
        if (!File.Exists(dst)) return true;
        var a = new FileInfo(src); var b = new FileInfo(dst);
        return a.Length != b.Length || a.LastWriteTimeUtc > b.LastWriteTimeUtc;
    }

    public static void ImportAll()
    {
        Directory.CreateDirectory(CreaturesDir);
        Directory.CreateDirectory(GenDir);
        var sources = Sources().ToList();
        int copied = 0;
        foreach (var s in sources)
        {
            var dst = Dest(s.name);
            Directory.CreateDirectory(Path.GetDirectoryName(dst));
            // Berichte zuerst: der Import (OnPreprocessAnimation) liest daraus, welche Clips Schleifen sind
            if (File.Exists(s.report)) File.Copy(s.report, $"{CreaturesDir}/{s.name}/{s.name}_clips.json", true);
            if (File.Exists(s.events)) File.Copy(s.events, $"{CreaturesDir}/{s.name}/{s.name}_events.json", true);
            var dng = $"{CreaturesDir}/{s.name}/{s.name}_dangling.json";     // frei hängende Teile → Wabbel-Material
            if (File.Exists(s.dangling)) File.Copy(s.dangling, dng, true);
            else if (File.Exists(dng)) File.Delete(dng);
            if (NeedsCopy(s.fbx, dst))
            {
                File.Copy(s.fbx, dst, true);
                copied++;
                var texDir = $"{CreaturesDir}/{s.name}/Textures";        // neue FBX → Texturen neu herausziehen
                if (AssetDatabase.IsValidFolder(texDir)) AssetDatabase.DeleteAsset(texDir);
            }
        }
        // Kreaturen, die es in der Pipeline nicht mehr gibt, entfernen
        foreach (var d in Directory.GetDirectories(CreaturesDir))
            if (sources.All(s => s.name != Path.GetFileName(d))) AssetDatabase.DeleteAsset(d.Replace('\\', '/'));
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        // Bodenwert (Name_ground.txt) kommt aus dem Import; fehlt er (FBX vor dieser Version importiert) → Reimport erzwingen
        foreach (var s in sources)
            if (!File.Exists(GroundFile(s.name))) AssetDatabase.ImportAsset(Dest(s.name), ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
        // Texturen stecken in der FBX (Blender: embed_textures) → herausziehen, damit die Materialien sie benutzen
        foreach (var s in sources) EnsureMaterial(s.name);

        var cat = BuildCatalog(sources.Select(s => s.name));
        // Szene wird neu gebaut und geöffnet → vorher ungespeicherte Änderungen anderer Szenen sichern lassen
        if (Application.isBatchMode || EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) BuildScene(cat);
        else Debug.LogWarning("[Kreaturen] Katalog aktualisiert, Szene NICHT neu gebaut (abgebrochen).");
        Debug.Log($"[Kreaturen] OK: {cat.entries.Count} Kreaturen ({copied} neu/geändert kopiert) · " +
                  string.Join(", ", cat.entries.Select(e => $"{e.name}({e.clips.Count} Clips, {e.triangles} Tris)")));
    }

    /// <summary>Texturen aus der FBX holen (Blender schreibt sie ohne Dateiendung hinein → Endung nach Inhalt ergänzen)
    /// und EIN schlichtes Material pro Kreatur bauen (Standard-Shader: Farbe + Normal-Map), das die FBX-Materialien ersetzt.</summary>
    static void EnsureMaterial(string name)
    {
        var dst = Dest(name);
        var dir = $"{CreaturesDir}/{name}";
        var texDir = dir + "/Textures";
        var matPath = $"{dir}/{name}.mat";
        var danglePath = $"{dir}/{name}_dangling.json";
        var shader = Shader.Find(File.Exists(danglePath) ? DangleShader : "Standard");
        var existing = AssetDatabase.LoadAssetAtPath<Material>(matPath);
        if (existing != null && AssetDatabase.IsValidFolder(texDir)
            && AssetDatabase.FindAssets("t:Texture2D", new[] { texDir }).Length > 0)
        {
            // Texturen + Material schon da → nur Shader (Markierung neu/entfernt) und Wabbel-Startwerte nachziehen
            if (existing.shader != shader)
            {
                existing.shader = shader;
                if (existing.GetTexture("_BumpMap") != null) existing.EnableKeyword("_NORMALMAP");
            }
            ConfigureDangle(existing, danglePath, name);
            EditorUtility.SetDirty(existing);
            AssetDatabase.SaveAssets();
            return;
        }
        if (AssetDatabase.IsValidFolder(texDir)) AssetDatabase.DeleteAsset(texDir);
        Directory.CreateDirectory(texDir);
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        var mi = (ModelImporter)AssetImporter.GetAtPath(dst);
        if (!mi.ExtractTextures(texDir)) Debug.LogWarning($"[Kreaturen] {name}: keine eingebetteten Texturen gefunden");
        foreach (var f in Directory.GetFiles(texDir))
        {
            if (f.EndsWith(".meta") || Path.HasExtension(f)) continue;
            var head = new byte[2];
            using (var fs = File.OpenRead(f)) fs.Read(head, 0, 2);
            var ext = head[0] == 0xFF && head[1] == 0xD8 ? ".jpg" : ".png";
            if (File.Exists(f + ".meta")) File.Delete(f + ".meta");
            File.Move(f, f + ext);
        }
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        Texture2D Find(string prefix) => AssetDatabase.FindAssets("t:Texture2D", new[] { texDir })
            .Select(g => AssetDatabase.LoadAssetAtPath<Texture2D>(AssetDatabase.GUIDToAssetPath(g)))
            .FirstOrDefault(t => t.name.StartsWith(prefix));
        var color = Find("Color");
        var normal = Find("Normal");
        var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
        if (mat == null)
        {
            mat = new Material(shader);
            AssetDatabase.CreateAsset(mat, matPath);
        }
        else if (mat.shader != shader) mat.shader = shader;
        mat.SetTexture("_MainTex", color);
        if (normal != null)
        {
            mat.SetTexture("_BumpMap", normal);
            mat.EnableKeyword("_NORMALMAP");
        }
        mat.SetFloat("_Metallic", 0f);
        mat.SetFloat("_Glossiness", 0.2f);
        ConfigureDangle(mat, danglePath, name);
        EditorUtility.SetDirty(mat);
        foreach (var m in AssetDatabase.LoadAllAssetsAtPath(dst).OfType<Material>().Select(m => m.name).Distinct().ToList())
            mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), m), mat);
        mi.SaveAndReimport();
        Debug.Log($"[Kreaturen] {name}: Material ({mat.shader.name}) mit {(color ? color.name : "KEINER Farbtextur")}{(normal ? " + Normal-Map" : "")}");
    }

    /// <summary>Startwerte aus rigging/export_unity.py (Name_dangling.json).</summary>
    [Serializable]
    class DangleSettings { public float amplitude_m = 0.02f, frequency_hz = 0.7f, lag_rad = 1.5f, vertical = 0.3f; }

    /// <summary>Wabbel-Material: Startwerte aus der Pipeline setzen + prüfen, dass das Mesh die Markierung (Vertex-Farben)
    /// wirklich hat. Bei Kreaturen ohne Markierung (Standard-Shader) tut die Funktion nichts.</summary>
    static void ConfigureDangle(Material mat, string danglePath, string name)
    {
        if (mat.shader.name != DangleShader || !File.Exists(danglePath)) return;
        var d = JsonUtility.FromJson<DangleSettings>(File.ReadAllText(danglePath));
        mat.SetFloat("_DangleAmplitude", d.amplitude_m);
        mat.SetFloat("_DangleFrequency", d.frequency_hz);
        mat.SetFloat("_DangleLag", d.lag_rad);
        mat.SetFloat("_DangleVertical", d.vertical);
        var mesh = AssetDatabase.LoadAllAssetsAtPath(Dest(name)).OfType<Mesh>().FirstOrDefault();
        int marked = mesh != null ? mesh.colors32.Count(c => c.r > 1) : 0;
        if (marked == 0) Debug.LogWarning($"[Kreaturen] {name}: _dangling.json vorhanden, aber das Mesh hat keine markierten Vertex-Farben");
        Debug.Log($"[Kreaturen] DANGLE {name}: {marked}/{(mesh ? mesh.vertexCount : 0)} Vertices schwingen · " +
                  $"Ausschlag {d.amplitude_m * 100:0.0} cm · {d.frequency_hz} Hz");
    }

    /// <summary>Prüfbilder für frei hängende Teile: Shader-Zeit fest auf 4 Zeitpunkte (je eine Viertel-Schwingung),
    /// Nahaufnahme der markierten Teile aus 3 Richtungen. Die Pose bleibt gleich → alles, was sich zwischen den Bildern
    /// bewegt, kommt aus dem Shader. Dateien: Name_dangle_ansicht_t0..t3.png</summary>
    public static void DangleShots(string outDir)
    {
        var cat = AssetDatabase.LoadAssetAtPath<CreatureCatalog>(CatalogPath);
        var cam = Camera.main;
        var rt = new RenderTexture(512, 512, 24);
        cam.targetTexture = rt;
        foreach (var e in cat.entries)
        {
            var go = UnityEngine.Object.Instantiate(e.model);
            CreatureViewer.PlaceOnGround(go, e.restMinY);
            var smr = go.GetComponentInChildren<SkinnedMeshRenderer>();
            var mat = smr != null ? smr.sharedMaterial : null;
            if (mat == null || mat.shader.name != DangleShader) { UnityEngine.Object.DestroyImmediate(go); continue; }
            var idle = e.clips.FirstOrDefault(c => c.label == "Idle") ?? e.clips.FirstOrDefault();
            if (idle != null) idle.clip.SampleAnimation(go, 0f);
            // markierte Vertices (Vertex-Farbe R) in Weltkoordinaten → Bildausschnitt
            var baked = new Mesh();
            smr.BakeMesh(baked, true);
            var cols = smr.sharedMesh.colors32;
            var verts = baked.vertices;
            var tr = smr.transform;
            var pts = verts.Where((v, i) => i < cols.Length && cols[i].r > 25).Select(v => tr.position + tr.rotation * v).ToList();
            UnityEngine.Object.DestroyImmediate(baked);
            if (pts.Count == 0)
            {
                Debug.LogWarning($"[Kreaturen] DANGLE {e.name}: keine markierten Vertices");
                UnityEngine.Object.DestroyImmediate(go);
                continue;
            }
            var b = new Bounds(pts[0], Vector3.zero);
            foreach (var p in pts) b.Encapsulate(p);
            float ext = Mathf.Max(b.size.x, b.size.y, b.size.z);
            float f = Mathf.Max(0.01f, mat.GetFloat("_DangleFrequency"));
            Debug.Log($"[Kreaturen] DANGLE {e.name}: {pts.Count} markierte Vertices, Ausschnitt {ext:0.00} m, " +
                      $"Skalierung Renderer {tr.lossyScale}, Ausschlag {mat.GetFloat("_DangleAmplitude") * 100:0.0} cm");
            foreach (var (vn, v) in new[] { ("side", CreatureViewer.ViewSide), ("arpg", CreatureViewer.ViewArpg), ("below", new Vector2(150f, -25f)) })
            {
                CreatureViewer.Pose(v, b.center, ext * 2.6f, out var pos, out var rot);
                cam.transform.SetPositionAndRotation(pos, rot);
                cam.nearClipPlane = ext * 0.05f;
                for (int k = 0; k < 4; k++)
                {
                    Shader.SetGlobalFloat("_DangleUseTestTime", 1f);
                    Shader.SetGlobalFloat("_DangleTestTime", k / (4f * f));
                    cam.Render();
                    RenderTexture.active = rt;
                    var tex = new Texture2D(512, 512, TextureFormat.RGB24, false);
                    tex.ReadPixels(new Rect(0, 0, 512, 512), 0, 0);
                    tex.Apply();
                    File.WriteAllBytes(Path.Combine(outDir, $"{e.name}_dangle_{vn}_t{k}.png"), tex.EncodeToPNG());
                    UnityEngine.Object.DestroyImmediate(tex);
                }
            }
            Shader.SetGlobalFloat("_DangleUseTestTime", 0f);
            UnityEngine.Object.DestroyImmediate(go);
        }
        RenderTexture.active = null;
        cam.targetTexture = null;
    }

    // ------------------------------------------------------------------ Katalog + Szene
    public static string Short(string clipName)
    {
        var n = clipName.Substring(clipName.LastIndexOf('|') + 1);
        return n.Substring(n.LastIndexOf('_') + 1);
    }

    static string Style(string clipName)
    {
        var n = clipName.Substring(clipName.LastIndexOf('|') + 1);
        int i = n.LastIndexOf('_');
        return i > 0 ? n.Substring(0, i) : "";
    }

    /// <summary>Schleife laut Pipeline-Bericht ("loop": true/false beim Clip), sonst Standard nach Name.</summary>
    public static bool IsLoop(string reportText, string clipName)
    {
        var full = clipName.Substring(clipName.LastIndexOf('|') + 1);
        if (!string.IsNullOrEmpty(reportText))
        {
            int i = reportText.IndexOf("\"" + full + "\": {", StringComparison.Ordinal);
            if (i >= 0)
            {
                var m = Regex.Match(reportText.Substring(i), "\"loop\":\\s*(true|false)");
                if (m.Success) return m.Groups[1].Value == "true";
            }
        }
        var s = Short(clipName);
        return !(s.StartsWith("Attack") || s == "Hit" || s == "Death");
    }

    static CreatureCatalog BuildCatalog(IEnumerable<string> names)
    {
        var cat = AssetDatabase.LoadAssetAtPath<CreatureCatalog>(CatalogPath);
        if (cat == null)
        {
            cat = ScriptableObject.CreateInstance<CreatureCatalog>();
            AssetDatabase.CreateAsset(cat, CatalogPath);
        }
        cat.entries.Clear();
        foreach (var name in names)
        {
            var path = Dest(name);
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (model == null) { Debug.LogWarning($"[Kreaturen] {name}: Modell nicht importiert"); continue; }
            var report = File.Exists($"{CreaturesDir}/{name}/{name}_clips.json")
                ? File.ReadAllText($"{CreaturesDir}/{name}/{name}_clips.json") : "";
            var clips = AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__"))
                .OrderBy(c => { int i = Array.IndexOf(Order, Short(c.name)); return i < 0 ? 100 : i; })
                .ThenBy(c => Short(c.name)).ToList();
            var e = new CreatureCatalog.Entry { name = name, model = model, style = clips.Count > 0 ? Style(clips[0].name) : "" };
            foreach (var c in clips) e.clips.Add(new CreatureCatalog.Clip { label = Short(c.name), clip = c, loop = IsLoop(report, c.name) });
            foreach (var smr in model.GetComponentsInChildren<SkinnedMeshRenderer>(true))
            {
                if (smr.sharedMesh != null) e.triangles += smr.sharedMesh.triangles.Length / 3;
                e.bones = Mathf.Max(e.bones, smr.bones.Length);
                e.materials += smr.sharedMaterials.Length;
            }
            var gf = GroundFile(name);
            if (File.Exists(gf)) e.restMinY = float.Parse(File.ReadAllText(gf).Trim(), System.Globalization.CultureInfo.InvariantCulture);
            else Debug.LogWarning($"[Kreaturen] {name}: kein Bodenwert ({gf}) – Kreatur steht evtl. falsch auf dem Boden");
            cat.entries.Add(e);
        }
        EditorUtility.SetDirty(cat);
        AssetDatabase.SaveAssets();
        return cat;
    }

    static void BuildScene(CreatureCatalog cat)
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
        var matPath = GenDir + "/Boden.mat";
        var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
        if (mat == null)
        {
            mat = new Material(Shader.Find("Standard")) { color = new Color(0.22f, 0.22f, 0.23f) };
            AssetDatabase.CreateAsset(mat, matPath);
        }
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Boden";
        ground.transform.localScale = Vector3.one * 2f;
        ground.GetComponent<Renderer>().sharedMaterial = mat;
        var cam = Camera.main;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.32f, 0.33f, 0.35f);
        cam.fieldOfView = 35f;
        var viewer = new GameObject("Viewer").AddComponent<CreatureViewer>();
        viewer.catalog = cat;
        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
    }

    /// <summary>Prüft die Wiedergabe wie im Viewer (PlayableGraph, Zeit von Hand gesetzt): jeder Clip muss Knochen bewegen.</summary>
    static void PlaybackSelfTest()
    {
        var cat = AssetDatabase.LoadAssetAtPath<CreatureCatalog>(CatalogPath);
        int bad = 0;
        foreach (var e in cat.entries)
        {
            var go = UnityEngine.Object.Instantiate(e.model);
            var anim = go.GetComponent<Animator>() ?? go.AddComponent<Animator>();
            anim.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            var smr = go.GetComponentInChildren<SkinnedMeshRenderer>();
            var graph = UnityEngine.Playables.PlayableGraph.Create("Test");
            graph.SetTimeUpdateMode(UnityEngine.Playables.DirectorUpdateMode.Manual);
            var output = UnityEngine.Animations.AnimationPlayableOutput.Create(graph, "A", anim);
            var still = new List<string>();
            foreach (var c in e.clips)
            {
                var p = UnityEngine.Animations.AnimationClipPlayable.Create(graph, c.clip);
                output.SetSourcePlayable(p);
                float moved = 0f;
                var start = smr.bones.Select(b => b.position).ToArray();
                foreach (var t in new[] { 0.25f, 0.5f, 0.75f })
                {
                    p.SetTime(c.clip.length * t);
                    graph.Evaluate(0f);
                    p.SetTime(0);
                    moved = Mathf.Max(moved, smr.bones.Select((b, i) => (b.position - start[i]).magnitude).Max());
                    graph.Evaluate(0f);
                }
                if (moved < 1e-4f) still.Add(c.label);
                p.Destroy();
            }
            graph.Destroy();
            UnityEngine.Object.DestroyImmediate(go);
            bad += still.Count;
            Debug.Log($"[Kreaturen] PLAY {e.name}: " + (still.Count == 0 ? "alle Clips bewegen sich" : "KEINE Bewegung in " + string.Join(",", still)));
        }
        if (bad > 0) throw new Exception($"{bad} Clips ohne Bewegung");
    }

    // ------------------------------------------------------------------ Prüfbilder (headless)
    public static void Screenshots(string outDir)
    {
        Directory.CreateDirectory(outDir);
        EditorSceneManager.OpenScene(ScenePath);
        var cat = AssetDatabase.LoadAssetAtPath<CreatureCatalog>(CatalogPath);
        var cam = Camera.main;
        var rt = new RenderTexture(512, 512, 24);
        cam.targetTexture = rt;
        // arpg + side im Walk; top + back in der Ruhepose (Flügel ausgebreitet statt mitten im Schlag) – zeigen dünne
        // Teile wie Flügel von beiden Seiten, einseitige Flächen (Backface Culling) fallen so sofort auf
        var views = new[] { ("arpg", CreatureViewer.ViewArpg, false), ("side", CreatureViewer.ViewSide, false),
                            ("arpg_rest", CreatureViewer.ViewArpg, true), ("top", CreatureViewer.ViewTop, true),
                            ("back", new Vector2(330f, 45f), true) };
        foreach (var e in cat.entries)
        {
            var go = UnityEngine.Object.Instantiate(e.model);
            CreatureViewer.PlaceOnGround(go, e.restMinY);
            var walk = e.clips.FirstOrDefault(c => c.label == "Walk") ?? e.clips.FirstOrDefault();
            if (walk != null)
            {
                // Bodenkontakt im Walk: tiefster Punkt über den ganzen Zyklus (≈ 0 = Füße am Boden, > 0 = schwebt)
                float lo = float.MaxValue, hi = float.MinValue;
                for (int k = 0; k <= 20; k++)
                {
                    walk.clip.SampleAnimation(go, walk.clip.length * k / 20f);
                    float y = CreatureViewer.LowestPoint(go);
                    lo = Mathf.Min(lo, y); hi = Mathf.Max(hi, y);
                }
                Debug.Log($"[Kreaturen] GROUND {e.name}: tiefster Punkt im Walk {lo * 100:0.0} … {hi * 100:0.0} cm über dem Boden");
                walk.clip.SampleAnimation(go, walk.clip.length * 0.3f);
            }
            var b = CreatureViewer.Bounds(go);
            float size = Mathf.Max(b.size.x, b.size.y, b.size.z);
            var restGo = UnityEngine.Object.Instantiate(e.model);           // Ruhepose (ohne Clip) für top/back
            CreatureViewer.PlaceOnGround(restGo, e.restMinY);
            var rb = CreatureViewer.Bounds(restGo);
            foreach (var (vn, v, rest) in views)
            {
                go.SetActive(!rest);
                restGo.SetActive(rest);
                var focus = rest ? rb.center : b.center;
                CreatureViewer.Pose(v, focus, (rest ? Mathf.Max(rb.size.x, rb.size.y, rb.size.z) : size) * 2.2f, out var pos, out var rot);
                cam.transform.SetPositionAndRotation(pos, rot);
                cam.nearClipPlane = size * 0.01f;
                cam.Render();
                RenderTexture.active = rt;
                var tex = new Texture2D(512, 512, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, 512, 512), 0, 0);
                tex.Apply();
                File.WriteAllBytes(Path.Combine(outDir, $"{e.name}_{vn}.png"), tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex);
            }
            Debug.Log($"[Kreaturen] SHOT {e.name} size={size:0.00} center={b.center} clips={string.Join(",", e.clips.Select(c => c.label + (c.loop ? "(L)" : "")))}");
            UnityEngine.Object.DestroyImmediate(go);
            UnityEngine.Object.DestroyImmediate(restGo);
        }
        RenderTexture.active = null;
        cam.targetTexture = null;
    }
}

/// <summary>Import-Einstellungen für alles unter Assets/Creatures: Generic-Rig, Animationen ohne Kompression,
/// Schleifen laut Pipeline-Bericht.</summary>
public class CreatureImportSettings : AssetPostprocessor
{
    bool Ours => assetPath.StartsWith(CreatureImporter.CreaturesDir + "/") && assetPath.EndsWith(".fbx");

    void OnPreprocessModel()
    {
        if (!Ours) return;
        var mi = (ModelImporter)assetImporter;
        mi.animationType = ModelImporterAnimationType.Generic;
        mi.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
        mi.importAnimation = true;
        mi.animationCompression = ModelImporterAnimationCompression.Off;   // exakt wie in Blender gebacken
        mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
        mi.importCameras = false;
        mi.importLights = false;
    }

    // Version hochzählen = Unity importiert alle Kreatur-FBX einmal neu (z. B. wenn OnPostprocessModel sich ändert)
    public override uint GetVersion() => 2;

    /// <summary>Tiefster Punkt der Bindepose (Mesh-Ecken im Raum des Wurzelobjekts, ohne Skinning) → Name_ground.txt.
    /// Hier ist das Mesh noch lesbar; zur Laufzeit ist es das nicht (Read/Write bleibt aus: halber Speicher bei vielen Gegnern).</summary>
    void OnPostprocessModel(GameObject root)
    {
        if (!Ours) return;
        float minY = float.MaxValue;
        var toRoot = root.transform.worldToLocalMatrix;
        foreach (var smr in root.GetComponentsInChildren<SkinnedMeshRenderer>())
        {
            if (smr.sharedMesh == null) continue;
            var m = toRoot * smr.transform.localToWorldMatrix;
            foreach (var v in smr.sharedMesh.vertices) minY = Mathf.Min(minY, m.MultiplyPoint3x4(v).y);
        }
        foreach (var mf in root.GetComponentsInChildren<MeshFilter>())
        {
            if (mf.sharedMesh == null) continue;
            var m = toRoot * mf.transform.localToWorldMatrix;
            foreach (var v in mf.sharedMesh.vertices) minY = Mathf.Min(minY, m.MultiplyPoint3x4(v).y);
        }
        if (minY == float.MaxValue) minY = 0f;
        var file = Path.ChangeExtension(assetPath, null) + "_ground.txt";
        var text = minY.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        if (!File.Exists(file) || File.ReadAllText(file).Trim() != text) File.WriteAllText(file, text);
    }

    void OnPreprocessTexture()
    {
        if (!assetPath.StartsWith(CreatureImporter.CreaturesDir + "/")) return;
        if (Path.GetFileName(assetPath).StartsWith("Normal"))             // Tripo: NormalGL_* = OpenGL-Normal-Map (passt zu Unity)
            ((TextureImporter)assetImporter).textureType = TextureImporterType.NormalMap;
    }

    void OnPreprocessAnimation()
    {
        if (!Ours) return;
        var mi = (ModelImporter)assetImporter;
        var reportPath = Path.ChangeExtension(assetPath, null) + "_clips.json";
        var report = File.Exists(reportPath) ? File.ReadAllText(reportPath) : "";
        var clips = mi.defaultClipAnimations;
        foreach (var c in clips) c.loopTime = CreatureImporter.IsLoop(report, c.takeName);
        mi.clipAnimations = clips;
    }
}
