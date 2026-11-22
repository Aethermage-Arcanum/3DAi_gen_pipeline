using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Eine Basis-Kreatur für den Baukasten: eigene Kopie der Pipeline-FBX unter Assets/VariantKit/Generated/Bases
    /// (unabhängig vom CreatureImporter), dazu die Analyse im Mesh-Raum: Körperachsen, Knochenlagen, Andock-Zonen,
    /// Farbgruppen der Basis (Krallen/Zähne, Nase/Maul, Augen).</summary>
    public class VkBase
    {
        public const string BasesDir = "Assets/VariantKit/Generated/Bases";

        public string id, name, creatureDir, fbxSource;
        public GameObject model;
        public SkinnedMeshRenderer smr;      // im Modell-Asset
        public Mesh mesh;                     // lesbare Basis
        public Texture2D color, normal;
        public List<AnimationClip> clips = new List<AnimationClip>();
        public float restMinY;                // tiefster Punkt der Bindepose im Raum des Modells (y)

        // ---- Analyse (Mesh-Raum = Raum des SkinnedMeshRenderers in der Bindepose)
        public Vector3[] verts, normals;
        public int[] tris;
        public BoneWeight[] weights;
        public string[] boneNames;
        public Dictionary<string, int> boneIndex = new Dictionary<string, int>();
        public Vector3[] boneHead, boneTail;
        public Vector3 up, fwd, left, origin;
        public float L;                       // Kreaturgröße = längste Kante des Begrenzungsrahmens (Mesh-Einheiten)
        public float meshToMeter = 1f;
        public float signedVolumeSign = 1f;   // Wicklung der Basis (für Bausteine)
        public float[] torsoTop, torsoBot; public float uMin, uMax; const int Bins = 48;
        public int[] lightGroup, darkGroup;
        public VkZones zones;

        public Vector3 Body(Vector3 p) { var d = p - origin; return new Vector3(Vector3.Dot(d, fwd), Vector3.Dot(d, up), Vector3.Dot(d, left)); }
        public Vector3 FromBody(Vector3 b) => origin + fwd * b.x + up * b.y + left * b.z;
        public Vector3 BodyDir(Vector3 d) => new Vector3(Vector3.Dot(d, fwd), Vector3.Dot(d, up), Vector3.Dot(d, left));
        public int Bone(string n) => boneIndex.TryGetValue(n, out var i) ? i : -1;

        public static string PipelineRoot => Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));

        // ------------------------------------------------------------------ Basen finden
        public class Info { public string id, name, dir, fbx, bodyplan; }

        public static List<Info> List()
        {
            var res = new List<Info>();
            var root = Path.Combine(PipelineRoot, "creatures");
            if (!Directory.Exists(root)) return res;
            foreach (var d in Directory.GetDirectories(root).OrderBy(x => x))
            {
                var toml = Path.Combine(d, "creature.toml");
                var outDir = Path.Combine(d, "output");
                if (!File.Exists(toml) || !Directory.Exists(outDir)) continue;
                var txt = File.ReadAllText(toml);
                var name = Regex.Match(txt, "^name\\s*=\\s*\"([^\"]+)\"", RegexOptions.Multiline).Groups[1].Value;
                var plan = Regex.Match(txt, "^bodyplan\\s*=\\s*\"([^\"]+)\"", RegexOptions.Multiline).Groups[1].Value;
                var fbx = Directory.GetFiles(outDir, "*.fbx").FirstOrDefault();
                if (fbx == null || plan != "quadruped") continue;   // Andock-Zonen gibt es bisher nur für den Vierbeiner
                res.Add(new Info { id = name, name = Path.GetFileNameWithoutExtension(fbx), dir = d, fbx = fbx, bodyplan = plan });
            }
            return res;
        }

        static readonly Dictionary<string, VkBase> cache = new Dictionary<string, VkBase>();

        static readonly HashSet<string> eventsChecked = new HashSet<string>();

        public static VkBase Load(string id, bool forceAnalyse = false)
        {
            var info = List().FirstOrDefault(i => i.id == id) ?? throw new Exception($"Basis-Kreatur '{id}' nicht gefunden (creatures/*/creature.toml name, bodyplan quadruped, output/*.fbx)");
            var dst = $"{BasesDir}/{info.name}/{info.name}.fbx";
            bool changed = Import(info, dst);
            if (!forceAnalyse && !changed && cache.TryGetValue(id, out var c) && c.model != null && c.mesh != null) return c;
            var b = new VkBase { id = id, name = info.name, creatureDir = info.dir, fbxSource = info.fbx };
            b.model = AssetDatabase.LoadAssetAtPath<GameObject>(dst);
            b.smr = b.model.GetComponentInChildren<SkinnedMeshRenderer>(true);
            b.mesh = b.smr.sharedMesh;
            if (!b.mesh.isReadable) throw new Exception($"{dst}: Mesh nicht lesbar (Import-Einstellung VkImport)");
            b.clips = AssetDatabase.LoadAllAssetsAtPath(dst).OfType<AnimationClip>().Where(a => !a.name.StartsWith("__preview__")).ToList();
            // G14: Clip-Events (hit/slam) fehlen noch in der Kopie (älterer Import) → einmal neu importieren
            var evPath = $"{BasesDir}/{info.name}/{info.name}_events.json";
            if (File.Exists(evPath) && !eventsChecked.Contains(dst) && Regex.IsMatch(File.ReadAllText(evPath), "\"(hit|slam)\"")
                && b.clips.All(c => AnimationUtility.GetAnimationEvents(c).Length == 0))
            {
                eventsChecked.Add(dst);
                AssetDatabase.ImportAsset(dst, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                b.model = AssetDatabase.LoadAssetAtPath<GameObject>(dst);
                b.smr = b.model.GetComponentInChildren<SkinnedMeshRenderer>(true);
                b.mesh = b.smr.sharedMesh;
                b.clips = AssetDatabase.LoadAllAssetsAtPath(dst).OfType<AnimationClip>().Where(a => !a.name.StartsWith("__preview__")).ToList();
                Debug.Log($"[VariantKit] {info.name}: Clip-Events nachgetragen ({b.clips.Sum(c => AnimationUtility.GetAnimationEvents(c).Length)} Stöße)");
            }
            var texDir = $"{BasesDir}/{info.name}/Textures";
            Texture2D Find(string p) => AssetDatabase.FindAssets("t:Texture2D", new[] { texDir })
                .Select(g => AssetDatabase.LoadAssetAtPath<Texture2D>(AssetDatabase.GUIDToAssetPath(g))).FirstOrDefault(t => t.name.StartsWith(p));
            b.color = Find("Color");
            b.normal = Find("Normal");
            b.Analyse();
            cache[id] = b;
            return b;
        }

        /// <summary>FBX kopieren (nur wenn neuer), importieren, eingebettete Texturen herausziehen. true = neu importiert.</summary>
        static bool Import(Info info, string dst)
        {
            var dir = Path.GetDirectoryName(dst);
            Directory.CreateDirectory(dir);
            bool copy = !File.Exists(dst) || new FileInfo(info.fbx).Length != new FileInfo(dst).Length ||
                        new FileInfo(info.fbx).LastWriteTimeUtc > new FileInfo(dst).LastWriteTimeUtc;
            var texDir = dir.Replace('\\', '/') + "/Textures";
            // G14: Clip-Events (hit/slam) neben die Kopie legen; VkImport schreibt sie in die Clips → bei Änderung neu importieren
            var evSrc = Path.Combine(Path.GetDirectoryName(info.fbx), Path.GetFileNameWithoutExtension(info.fbx) + "_events.json");
            var evDst = (Path.Combine(dir, Path.GetFileNameWithoutExtension(dst) + "_events.json")).Replace('\\', '/');
            if (File.Exists(evSrc) && (!File.Exists(evDst) || File.ReadAllText(evSrc) != File.ReadAllText(evDst)))
            {
                File.Copy(evSrc, evDst, true);
                AssetDatabase.ImportAsset(evDst, ImportAssetOptions.ForceSynchronousImport);
                if (!copy)
                {
                    AssetDatabase.ImportAsset(dst, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                    Debug.Log($"[VariantKit] {info.name}: Clip-Events (hit/slam) für das Nachschwingen übernommen → Basis-Kopie neu importiert");
                    return true;
                }
            }
            if (copy)
            {
                File.Copy(info.fbx, dst, true);
                if (AssetDatabase.IsValidFolder(texDir)) AssetDatabase.DeleteAsset(texDir);
                AssetDatabase.ImportAsset(dst, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            }
            if (!AssetDatabase.IsValidFolder(texDir) || AssetDatabase.FindAssets("t:Texture2D", new[] { texDir }).Length == 0)
            {
                Directory.CreateDirectory(texDir);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                var mi = (ModelImporter)AssetImporter.GetAtPath(dst);
                mi.ExtractTextures(texDir);
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
                copy = true;
            }
            return copy;
        }

        // ------------------------------------------------------------------ Analyse
        static readonly string[] Spine = { "Hips", "Spine_1", "Chest", "Neck_1", "Neck_2", "Head" };

        static string ChainChild(string bone)
        {
            switch (bone)
            {
                case "Hips": return "Spine_1";
                case "Spine_1": return "Chest";
                case "Chest": return "Neck_1";
                case "Neck_1": return "Neck_2";
                case "Neck_2": return "Head";
                case "Root": return "Hips";
            }
            var m = Regex.Match(bone, "^(Leg_[FB][LR]|Tail)_(\\d+)$");
            if (m.Success) return $"{m.Groups[1].Value}_{int.Parse(m.Groups[2].Value) + 1}";
            m = Regex.Match(bone, "^Shoulder_(F[LR])$");
            if (m.Success) return $"Leg_{m.Groups[1].Value}_1";
            return null;
        }

        public float Weight(int v, int bone)
        {
            var w = weights[v]; float s = 0;
            if (w.boneIndex0 == bone) s += w.weight0;
            if (w.boneIndex1 == bone) s += w.weight1;
            if (w.boneIndex2 == bone) s += w.weight2;
            if (w.boneIndex3 == bone) s += w.weight3;
            return s;
        }

        public float WeightSum(int v, IEnumerable<int> bones) { float s = 0; foreach (var b in bones) if (b >= 0) s += Weight(v, b); return s; }

        void Analyse()
        {
            verts = mesh.vertices;
            normals = mesh.normals;
            tris = mesh.triangles;
            weights = mesh.boneWeights;
            var bp = mesh.bindposes;
            boneNames = smr.bones.Select(t => t.name).ToArray();
            boneIndex.Clear();
            for (int i = 0; i < boneNames.Length; i++) boneIndex[boneNames[i]] = i;
            boneHead = bp.Select(m => m.inverse.MultiplyPoint3x4(Vector3.zero)).ToArray();

            // Achsen: oben aus der Lage des Renderers im Modell, vorn = Hüfte → Kopf, links = Seite von Leg_FL_1
            var toModel = model.transform.worldToLocalMatrix * smr.transform.localToWorldMatrix;
            up = toModel.inverse.MultiplyVector(Vector3.up).normalized;
            var f = boneHead[Bone("Head")] - boneHead[Bone("Hips")];
            fwd = (f - Vector3.Dot(f, up) * up).normalized;
            left = Vector3.Cross(up, fwd).normalized;
            int fl = Bone("Leg_FL_1");
            if (fl >= 0 && Vector3.Dot(boneHead[fl] - boneHead[Bone("Hips")], left) < 0) left = -left;
            var b0 = new Bounds(verts[0], Vector3.zero);
            foreach (var v in verts) b0.Encapsulate(v);
            origin = b0.center;
            float ex = verts.Max(v => Vector3.Dot(v, fwd)) - verts.Min(v => Vector3.Dot(v, fwd));
            float ey = verts.Max(v => Vector3.Dot(v, up)) - verts.Min(v => Vector3.Dot(v, up));
            float ez = verts.Max(v => Vector3.Dot(v, left)) - verts.Min(v => Vector3.Dot(v, left));
            L = Mathf.Max(ex, ey, ez);
            meshToMeter = toModel.MultiplyVector(fwd).magnitude;
            restMinY = verts.Min(v => toModel.MultiplyPoint3x4(v).y);

            // Knochen-Enden: Kettenkind, sonst Ausdehnung der Haut, die überwiegend an diesem Knochen hängt
            boneTail = new Vector3[boneNames.Length];
            for (int i = 0; i < boneNames.Length; i++)
            {
                var c = ChainChild(boneNames[i]);
                int ci = c == null ? -1 : Bone(c);
                if (ci >= 0) { boneTail[i] = boneHead[ci]; continue; }
                var own = Enumerable.Range(0, verts.Length).Where(v => Weight(v, i) > 0.5f).Select(v => verts[v]).ToList();
                if (own.Count == 0) { boneTail[i] = boneHead[i] + fwd * L * 0.02f; continue; }
                var cen = own.Aggregate(Vector3.zero, (a, x) => a + x) / own.Count;
                var dir = (cen - boneHead[i]).normalized;
                if (boneNames[i] == "Head" || boneNames[i] == "Jaw") dir = (dir + fwd).normalized;   // Kopf zeigt zur Schnauze
                float ext = own.Max(x => Vector3.Dot(x - boneHead[i], dir));
                boneTail[i] = boneHead[i] + dir * Mathf.Max(ext, L * 0.02f);
            }

            // Wicklung (Vorzeichen des Volumens), für die richtige Wicklung der Bausteine
            double vol = 0;
            for (int t = 0; t < tris.Length; t += 3) vol += Vector3.Dot(verts[tris[t]], Vector3.Cross(verts[tris[t + 1]], verts[tris[t + 2]]));
            signedVolumeSign = vol >= 0 ? 1f : -1f;

            // Rumpf-Querschnitt: oben/unten pro Abschnitt entlang der Körperachse (für Zonen „hoehe“ und Statur)
            var spineIdx = Spine.Select(Bone).Where(x => x >= 0).Concat(boneNames.Where(n => n.StartsWith("Tail")).Select(Bone)).ToList();
            var bodyV = Enumerable.Range(0, verts.Length).Select(v => Body(verts[v])).ToArray();
            uMin = bodyV.Min(p => p.x); uMax = bodyV.Max(p => p.x);
            torsoTop = Enumerable.Repeat(float.MinValue, Bins).ToArray();
            torsoBot = Enumerable.Repeat(float.MaxValue, Bins).ToArray();
            for (int v = 0; v < verts.Length; v++)
            {
                if (WeightSum(v, spineIdx) < 0.5f) continue;
                int k = UBin(bodyV[v].x);
                torsoTop[k] = Mathf.Max(torsoTop[k], bodyV[v].y);
                torsoBot[k] = Mathf.Min(torsoBot[k], bodyV[v].y);
            }
            FillBins(torsoTop); FillBins(torsoBot);

            // Farbgruppen der Basis: helle Pixel = haut, dunkle Pixel (Textur) = Krallen/Nase/Augen je nach Körperstelle
            lightGroup = new int[verts.Length];
            darkGroup = new int[verts.Length];
            int head = Bone("Head"), jaw = Bone("Jaw");
            var paws = boneNames.Where(n => Regex.IsMatch(n, "^Leg_[FB][LR]_[34]$")).Select(Bone).ToList();
            var comp = Components();
            var compSize = comp.GroupBy(c => c).ToDictionary(g => g.Key, g => g.Count());
            for (int v = 0; v < verts.Length; v++)
            {
                float wh = (head >= 0 ? Weight(v, head) : 0) + (jaw >= 0 ? Weight(v, jaw) : 0);
                bool small = compSize[comp[v]] < verts.Length * 0.05f;
                if (small && wh > 0.5f) { lightGroup[v] = darkGroup[v] = VkSpec.GruppeIndex("horn"); continue; }   // lose Fangzähne
                lightGroup[v] = 0;
                if (WeightSum(v, paws) > 0.3f) { darkGroup[v] = VkSpec.GruppeIndex("horn"); continue; }
                if (wh > 0.4f && head >= 0)
                {
                    float t = Along(verts[v], head);
                    var bp2 = Body(verts[v]); var hb = Body(boneHead[head]);
                    bool eye = t > 0.25f && t < 0.75f && bp2.y > hb.y - L * 0.02f && Mathf.Abs(bp2.z) > L * 0.02f && (jaw < 0 || Weight(v, jaw) < 0.3f);
                    darkGroup[v] = VkSpec.GruppeIndex(eye ? "augen" : "akzent");
                    continue;
                }
                darkGroup[v] = VkSpec.GruppeIndex("horn");
            }

            zones = new VkZones(this);
        }

        public int UBin(float u) => Mathf.Clamp((int)((u - uMin) / (uMax - uMin + 1e-6f) * Bins), 0, Bins - 1);
        public float TorsoTop(float u) => torsoTop[UBin(u)];
        public float TorsoBot(float u) => torsoBot[UBin(u)];

        static void FillBins(float[] a)
        {
            for (int pass = 0; pass < Bins; pass++)
                for (int i = 0; i < a.Length; i++)
                    if (a[i] == float.MinValue || a[i] == float.MaxValue)
                    {
                        if (i > 0 && a[i - 1] != float.MinValue && a[i - 1] != float.MaxValue) a[i] = a[i - 1];
                        else if (i < a.Length - 1 && a[i + 1] != float.MinValue && a[i + 1] != float.MaxValue) a[i] = a[i + 1];
                    }
            var c = (float[])a.Clone();
            for (int i = 0; i < a.Length; i++) a[i] = (c[Mathf.Max(0, i - 1)] + c[i] * 2 + c[Mathf.Min(a.Length - 1, i + 1)]) / 4f;
        }

        /// <summary>Lage eines Punkts entlang eines Knochens (0 = Ansatz, 1 = Ende).</summary>
        public float Along(Vector3 p, int bone)
        {
            var a = boneHead[bone]; var d = boneTail[bone] - a;
            return Vector3.Dot(p - a, d) / Mathf.Max(1e-8f, d.sqrMagnitude);
        }

        /// <summary>Punkt "Knochen:t" (Zonen-Datei) in Körperkoordinate u (vorn).</summary>
        public float BoneU(string spec)
        {
            var parts = spec.Split(':');
            int b = Bone(parts[0]);
            if (b < 0) return 0f;
            float t = parts.Length > 1 ? float.Parse(parts[1], System.Globalization.CultureInfo.InvariantCulture) : 0f;
            return Body(Vector3.LerpUnclamped(boneHead[b], boneTail[b], t)).x;
        }

        int[] Components()
        {
            var parent = Enumerable.Range(0, verts.Length).ToArray();
            int Find(int x) { while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; }
            for (int t = 0; t < tris.Length; t += 3)
            {
                int a = Find(tris[t]), b = Find(tris[t + 1]), c = Find(tris[t + 2]);
                parent[b] = a; parent[Find(c)] = a;
            }
            // gleiche Positionen (aufgetrennte UV-Nähte) zusammenlegen
            var byPos = new Dictionary<Vector3Int, int>();
            for (int v = 0; v < verts.Length; v++)
            {
                var k = Vector3Int.RoundToInt(verts[v] * (10000f / Mathf.Max(L, 1e-6f)));
                if (byPos.TryGetValue(k, out var o)) parent[Find(v)] = Find(o); else byPos[k] = v;
            }
            return Enumerable.Range(0, verts.Length).Select(Find).ToArray();
        }

        // ------------------------------------------------------------------ Strahl von oben (Rückenlinie)
        public bool RayDown(Vector3 bodyXZ, out int tri, out Vector3 bary, out Vector3 pos)
        {
            var o = FromBody(new Vector3(bodyXZ.x, TorsoTop(bodyXZ.x) + L, bodyXZ.z));
            return Ray(o, -up, verts, out tri, out bary, out pos);
        }

        public bool Ray(Vector3 o, Vector3 d, Vector3[] vs, out int tri, out Vector3 bary, out Vector3 pos)
        {
            tri = -1; bary = Vector3.zero; pos = Vector3.zero;
            float best = float.MaxValue;
            for (int t = 0; t < tris.Length; t += 3)
            {
                Vector3 a = vs[tris[t]], b = vs[tris[t + 1]], c = vs[tris[t + 2]];
                var e1 = b - a; var e2 = c - a; var p = Vector3.Cross(d, e2);
                float det = Vector3.Dot(e1, p);
                if (Mathf.Abs(det) < 1e-12f) continue;
                float inv = 1f / det; var s = o - a;
                float u = Vector3.Dot(s, p) * inv; if (u < 0 || u > 1) continue;
                var q = Vector3.Cross(s, e1);
                float w = Vector3.Dot(d, q) * inv; if (w < 0 || u + w > 1) continue;
                float dist = Vector3.Dot(e2, q) * inv;
                if (dist > 0 && dist < best) { best = dist; tri = t / 3; bary = new Vector3(1 - u - w, u, w); pos = o + d * dist; }
            }
            return tri >= 0;
        }
    }

    /// <summary>Andock-Zonen (rigging/quadruped_zonen.json) als weiche Masken pro Vertex.</summary>
    public class VkZones
    {
        readonly VkBase b;
        readonly JObj def, sammel;
        public readonly JObj rueckenlinie;
        readonly Dictionary<string, float[]> cache = new Dictionary<string, float[]>();
        public List<string> Names => def.Keys.ToList();
        public List<string> SammelNames => sammel.Keys.ToList();

        public static string DefPath(string skelett) => Path.Combine(VkBase.PipelineRoot, "rigging", $"{skelett}_zonen.json");

        public VkZones(VkBase b)
        {
            this.b = b;
            var j = Json.ParseObj(File.ReadAllText(DefPath("quadruped")));
            def = j.O("zonen"); sammel = j.O("sammel") ?? new JObj(); rueckenlinie = j.O("rueckenlinie");
        }

        static float Smooth(float e0, float e1, float x) { float t = Mathf.Clamp01((x - e0) / (e1 - e0)); return t * t * (3 - 2 * t); }
        static float Band(float lo, float hi, float x, float soft) => Smooth(lo - soft, lo + soft, x) * (1 - Smooth(hi - soft, hi + soft, x));

        /// <summary>Maske einer Zone oder eines Sammelnamens (0..1 pro Vertex).</summary>
        public float[] Mask(string name)
        {
            if (cache.TryGetValue(name, out var m)) return m;
            int n = b.verts.Length;
            m = new float[n];
            if (name == "ganzer_koerper") for (int i = 0; i < n; i++) m[i] = 1;
            else if (sammel.Has(name)) foreach (var s in sammel.Strs(name)) { var sm = Mask(s); for (int i = 0; i < n; i++) m[i] = Mathf.Max(m[i], sm[i]); }
            else if (def.Has(name)) Compute(def.O(name), m);
            else if (name == "rueckenlinie") { var r = Mask("ruecken_gesamt"); var nk = Mask("nacken"); for (int i = 0; i < n; i++) m[i] = Mathf.Max(r[i], nk[i]); }
            cache[name] = m;
            return m;
        }

        public float[] Mask(IEnumerable<string> zonen, IEnumerable<string> ohne)
        {
            int n = b.verts.Length;
            var m = new float[n];
            foreach (var z in zonen) { var zm = Mask(z); for (int i = 0; i < n; i++) m[i] = Mathf.Max(m[i], zm[i]); }
            foreach (var z in ohne ?? Enumerable.Empty<string>()) { var zm = Mask(z); for (int i = 0; i < n; i++) m[i] *= 1 - zm[i]; }
            return m;
        }

        void Compute(JObj z, float[] m)
        {
            var bones = z.Strs("knochen").Select(b.Bone).Where(x => x >= 0).ToList();
            float wmin = z.F("gewicht_min", 0.35f);
            int abB = z.S("abschnitt_knochen", null) is string ak ? b.Bone(ak) : (bones.Count > 0 ? bones[0] : -1);
            var ab = z.L("abschnitt") != null ? z.Vec("abschnitt", new[] { 0f, 1f }) : null;
            var ax = z.Strs("achse");
            float a0 = 0, a1 = 0;
            if (ax.Count == 2) { a0 = b.BoneU(ax[0]); a1 = b.BoneU(ax[1]); if (a0 > a1) (a0, a1) = (a1, a0); }
            var hh = z.L("hoehe") != null ? z.Vec("hoehe", new[] { 0f, 1f }) : null;
            string seite = z.S("seite", null);
            float sw = z.F("schwelle", 0f);
            float soft = b.L * 0.025f;
            // M2: nur oberhalb eines Knochenpunkts („ueber“), nicht an bestimmten Knochen („nicht_knochen“)
            var nk = z.Strs("nicht_knochen").Select(b.Bone).Where(x => x >= 0).ToList();
            float nw = z.F("nicht_gewicht", 0.5f);
            bool hasUeber = z.S("ueber", null) is string ue && b.Bone(ue.Split(':')[0]) >= 0;
            float yUeber = 0;
            if (hasUeber)
            {
                var parts = z.S("ueber", "").Split(':');
                int ub = b.Bone(parts[0]);
                float ut = parts.Length > 1 ? float.Parse(parts[1], System.Globalization.CultureInfo.InvariantCulture) : 0f;
                yUeber = b.Body(Vector3.LerpUnclamped(b.boneHead[ub], b.boneTail[ub], ut)).y;
            }
            for (int v = 0; v < m.Length; v++)
            {
                var p = b.verts[v]; var bp = b.Body(p); var nb = b.BodyDir(b.normals[v]);
                float r = 1;
                if (bones.Count > 0) r *= Smooth(wmin - 0.15f, wmin + 0.15f, b.WeightSum(v, bones));
                if (r <= 0) continue;
                if (ab != null && abB >= 0) r *= Band(ab[0], ab[1], b.Along(p, abB), 0.06f);
                if (ax.Count == 2) r *= Band(a0, a1, bp.x, soft);
                if (hh != null)
                {
                    float top = b.TorsoTop(bp.x), bot = b.TorsoBot(bp.x);
                    r *= Band(hh[0], hh[1], (bp.y - bot) / Mathf.Max(1e-6f, top - bot), 0.06f);
                }
                if (nk.Count > 0 && r > 0) r *= 1 - Smooth(nw - 0.15f, nw + 0.15f, b.WeightSum(v, nk));
                if (hasUeber && r > 0) r *= Smooth(yUeber - soft, yUeber + soft, bp.y);
                if (seite != null && r > 0)
                {
                    float side = bp.z >= 0 ? 1 : -1;
                    Vector3 dir;
                    switch (seite)
                    {
                        case "oben": dir = Vector3.up; break;
                        case "unten": dir = Vector3.down; break;
                        case "vorn": dir = Vector3.right; break;
                        case "hinten": dir = Vector3.left; break;
                        case "links": dir = new Vector3(0, 0, 1); break;
                        case "rechts": dir = new Vector3(0, 0, -1); break;
                        case "oben_vorn": dir = new Vector3(1, 1, 0).normalized; break;
                        case "aussen": dir = new Vector3(0, 0, side); break;
                        case "aussen_vorn": dir = new Vector3(1, 0, side).normalized; break;
                        default: dir = Vector3.up; break;
                    }
                    r *= Smooth(sw - 0.15f, sw + 0.15f, Vector3.Dot(nb, dir));
                    // links/rechts: nur die eigene Körperseite
                    if (seite == "links") r *= Smooth(-soft, soft, bp.z);
                    if (seite == "rechts") r *= Smooth(-soft, soft, -bp.z);
                }
                m[v] = r;
            }
        }
    }
}
