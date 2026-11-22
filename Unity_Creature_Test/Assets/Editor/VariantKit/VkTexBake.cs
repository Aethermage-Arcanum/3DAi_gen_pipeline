using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace VariantKit
{
    /// <summary>Textur-Backen (Spec 4.1, E5): gemeinsames UV-Atlas (Basis-UV verkleinert + Kacheln für alle Teile), dann rendert
    /// „Hidden/VariantKit/Bake“ den Ebenen-Stapel im UV-Raum → Albedo, Maske, (Leuchten), (Normal), je 1024². Danach braucht die
    /// Variante nur noch „VariantKit/Baked“: 1 Material, feste Kosten.</summary>
    public static class VkTexBake
    {
        public const string BakeShader = "Hidden/VariantKit/Bake";
        public const string GameShader = "VariantKit/Baked";
        public const float BaseScale = 0.8f;    // Basis-UV belegt 80 % × 80 % (oben links), Teile die L-förmige Rest-Fläche

        public class Result
        {
            public Mesh mesh;                  // Spiel-Mesh: UV0 = Atlas, keine Hilfskanäle
            public Material material;
            public List<string> textures = new List<string>();
            public int size;
            public bool emission, normal;
            public float atlasFill;            // Anteil der Teil-Fläche, der belegt ist
            public float partTexel;            // mittlere Kachelgröße eines Teil-Dreiecks (Pixel)
        }

        // ------------------------------------------------------------------ Atlas
        /// <summary>Kopie des Varianten-Meshes mit getrennten Teil-Dreiecken und Atlas-UV in TEXCOORD7 (für den Bake-Shader).</summary>
        public static Mesh AtlasMesh(Mesh src, int nBase, int size, out float fill, out float meanTexel)
        {
            var V = new List<Vector3>(); src.GetVertices(V);
            var Nn = new List<Vector3>(); src.GetNormals(Nn);
            var Tg = new List<Vector4>(); src.GetTangents(Tg); if (Tg.Count != V.Count) Tg = Enumerable.Repeat(new Vector4(1, 0, 0, 1), V.Count).ToList();
            var BW = src.boneWeights.ToList();
            var uvs = new List<Vector4>[7];
            for (int c = 0; c < 7; c++) { uvs[c] = new List<Vector4>(); src.GetUVs(c, uvs[c]); if (uvs[c].Count != V.Count) uvs[c] = Enumerable.Repeat(Vector4.zero, V.Count).ToList(); }
            var T = src.triangles;
            var atlas = Enumerable.Repeat(new Vector4(-1, -1, 0, 0), V.Count).ToList();
            for (int v = 0; v < nBase; v++) { var u = uvs[0][v]; atlas[v] = new Vector4(u.x * BaseScale, 1 - BaseScale + u.y * BaseScale, 0, 0); }
            // Teil-Dreiecke: jedes bekommt eigene Vertices
            var partTris = new List<int>();
            for (int t = 0; t < T.Length / 3; t++) if (T[t * 3] >= nBase || T[t * 3 + 1] >= nBase || T[t * 3 + 2] >= nBase) partTris.Add(t);
            var newT = (int[])T.Clone();
            foreach (var t in partTris)
                for (int kk = 0; kk < 3; kk++)
                {
                    int ov = T[t * 3 + kk];
                    V.Add(V[ov]); Nn.Add(Nn[ov]); Tg.Add(Tg[ov]); BW.Add(BW[ov]);
                    for (int c = 0; c < 7; c++) uvs[c].Add(uvs[c][ov]);
                    atlas.Add(Vector4.zero);
                    newT[t * 3 + kk] = V.Count - 1;
                }
            // Kacheln: Dreiecke paarweise in Quadrate, Größe ∝ √Fläche, Regalpacken in die L-Fläche
            float px = 1f / size;
            var areas = partTris.Select(t => Vector3.Cross(V[newT[t * 3 + 1]] - V[newT[t * 3]], V[newT[t * 3 + 2]] - V[newT[t * 3]]).magnitude * 0.5f).ToList();
            var order = Enumerable.Range(0, partTris.Count).OrderByDescending(i => areas[i]).ToList();
            var pairs = new List<(int a, int b, float area)>();
            for (int i = 0; i < order.Count; i += 2)
                pairs.Add((order[i], i + 1 < order.Count ? order[i + 1] : -1, Mathf.Max(areas[order[i]], i + 1 < order.Count ? areas[order[i + 1]] : 0)));
            var regions = new[] { new Rect(BaseScale, 0, 1 - BaseScale, 1), new Rect(0, 0, BaseScale, 1 - BaseScale) };
            // Skalierung k (Pixel pro √Fläche) per Halbierung so groß wie möglich
            float k = 0; List<Rect> cells = null;
            float kLo = 0.0f, kHi = 1e7f;
            for (int it = 0; it < 30; it++)
            {
                float km = (kLo + kHi) * 0.5f;
                var c = Pack(pairs.Select(pp => Mathf.Clamp(Mathf.Ceil(km * Mathf.Sqrt(pp.area)) + 4, 6, size * 0.12f)).ToList(), regions, size);
                if (c != null) { kLo = km; cells = c; k = km; } else kHi = km;
            }
            if (cells == null) cells = Pack(pairs.Select(_ => 6f).ToList(), regions, size) ?? throw new Exception("Atlas: zu viele Teile für die Texturgröße");
            float used = 0, tex = 0;
            for (int i = 0; i < pairs.Count; i++)
            {
                var r = cells[i];
                used += r.width * r.height;
                tex += r.width;
                float pad = 1.6f * px;
                var a = new Vector2(r.xMin + pad, r.yMin + pad); var bR = new Vector2(r.xMax - pad * 2.2f, r.yMin + pad); var cT = new Vector2(r.xMin + pad, r.yMax - pad * 2.2f);
                SetTri(partTris[pairs[i].a], newT, atlas, a, bR, cT);
                if (pairs[i].b >= 0)
                {
                    var a2 = new Vector2(r.xMax - pad, r.yMax - pad); var b2 = new Vector2(r.xMin + pad * 2.2f, r.yMax - pad); var c2 = new Vector2(r.xMax - pad, r.yMin + pad * 2.2f);
                    SetTri(partTris[pairs[i].b], newT, atlas, a2, b2, c2);
                }
            }
            fill = used / regions.Sum(r => r.width * r.height);
            meanTexel = pairs.Count > 0 ? tex / pairs.Count * size : 0;
            var m = new Mesh { name = src.name + "_atlas", indexFormat = V.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
            m.SetVertices(V);
            m.SetNormals(Nn);
            m.SetTangents(Tg);
            for (int c = 0; c < 7; c++) m.SetUVs(c, uvs[c]);
            m.SetUVs(7, atlas);
            m.SetTriangles(newT, 0);
            m.boneWeights = BW.ToArray();
            m.bindposes = src.bindposes;
            m.RecalculateBounds();
            return m;
        }

        static void SetTri(int t, int[] T, List<Vector4> atlas, Vector2 a, Vector2 b, Vector2 c)
        {
            atlas[T[t * 3]] = a; atlas[T[t * 3 + 1]] = b; atlas[T[t * 3 + 2]] = c;
        }

        /// <summary>Regalpacken quadratischer Kacheln (Seitenlänge in Pixeln) in Rechtecke (UV). null = passt nicht.</summary>
        static List<Rect> Pack(List<float> sizesPx, Rect[] regions, int size)
        {
            var res = new Rect[sizesPx.Count];
            int ri = 0; float x = 0, y = 0, shelf = 0;
            var order = Enumerable.Range(0, sizesPx.Count).OrderByDescending(i => sizesPx[i]).ToList();
            foreach (var i in order)
            {
                float s = sizesPx[i] / size;
                while (true)
                {
                    if (ri >= regions.Length) return null;
                    var R = regions[ri];
                    if (x + s > R.width + 1e-6f) { x = 0; y += shelf; shelf = 0; }
                    if (y + s > R.height + 1e-6f || s > R.width) { ri++; x = 0; y = 0; shelf = 0; continue; }
                    res[i] = new Rect(R.xMin + x, R.yMin + y, s, s);
                    x += s; shelf = Mathf.Max(shelf, s);
                    break;
                }
            }
            return res.ToList();
        }

        // ------------------------------------------------------------------ Backen
        public static Result Bake(VkBase b, VkDoc doc, VkBuildResult res, Material preview, string dir, string name, int size)
        {
            var r = new Result { size = size };
            int nb = b.verts.Length;
            var atlasMesh = AtlasMesh(res.mesh, nb, size, out r.atlasFill, out r.partTexel);
            var bakeMat = new Material(Shader.Find(BakeShader)) { hideFlags = HideFlags.HideAndDontSave };
            VkBuilder.ApplyMaterial(bakeMat, b, doc, res);
            bool linear = QualitySettings.activeColorSpace == ColorSpace.Linear;
            var M = doc.resolved.Obj("material");
            bool anyEmission = M.Obj("farbgruppen").Select(kv => kv.Value as JObj).Any(o => o != null && o.F("leuchten", 0) > 0.001f)
                               || res.AlleEbenen.Any(e => e.S("typ", "") == "risse" && e.F("intensitaet", 0) > 0.001f);
            r.emission = anyEmission;
            r.normal = M.Obj("stil").F("facetten", 1f) < 0.99f && b.normal != null;
            var outs = new List<(int pass, string suffix, bool srgb)> { (0, "Albedo", true), (1, "Maske", false) };
            if (r.emission) outs.Add((2, "Leuchten", true));
            if (r.normal) outs.Add((3, "Normal", false));
            Texture2D cover = null;
            var tex = new Dictionary<string, Texture2D>();
            foreach (var (pass, suffix, srgb) in outs)
            {
                var rt = RenderTexture.GetTemporary(new RenderTextureDescriptor(size, size, RenderTextureFormat.ARGB32, 0) { sRGB = srgb && linear });
                bakeMat.SetFloat("_VKBakeOut", pass);
                var cb = new CommandBuffer { name = "VK Bake " + suffix };
                cb.SetRenderTarget(rt);
                cb.ClearRenderTarget(false, true, new Color(0, 0, 0, 0));
                cb.DrawMesh(atlasMesh, Matrix4x4.identity, bakeMat, 0, 0);
                Graphics.ExecuteCommandBuffer(cb);
                cb.Release();
                var prev = RenderTexture.active;
                RenderTexture.active = rt;
                var t = new Texture2D(size, size, TextureFormat.RGBA32, false, !(srgb && linear));
                t.ReadPixels(new Rect(0, 0, size, size), 0, 0);
                t.Apply();
                RenderTexture.active = prev;
                RenderTexture.ReleaseTemporary(rt);
                if (pass == 0) cover = t;
                tex[suffix] = t;
            }
            // Ränder auffüllen (Dilatation), damit Mip-Maps/Filter keine schwarzen Nähte zeigen
            var mask = cover.GetPixels32().Select(c => c.a > 127).ToArray();
            foreach (var kv in tex) Dilate(kv.Value, mask, 8, kv.Key == "Normal" ? new Color32(128, 128, 255, 255) : new Color32(0, 0, 0, 255));
            Directory.CreateDirectory(dir);
            var paths = new Dictionary<string, string>();
            foreach (var kv in tex)
            {
                var p = $"{dir}/{name}_{kv.Key}.png";
                File.WriteAllBytes(p, kv.Value.EncodeToPNG());
                paths[kv.Key] = p;
                r.textures.Add(p);
                UnityEngine.Object.DestroyImmediate(kv.Value);
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach (var kv in paths)
            {
                var ti = (TextureImporter)AssetImporter.GetAtPath(kv.Value);
                ti.textureType = kv.Key == "Normal" ? TextureImporterType.NormalMap : TextureImporterType.Default;
                ti.sRGBTexture = kv.Key == "Albedo" || kv.Key == "Leuchten";
                ti.maxTextureSize = size;
                ti.textureCompression = TextureImporterCompression.CompressedHQ;
                ti.mipmapEnabled = true;
                ti.SaveAndReimport();
            }
            // Spiel-Mesh: Atlas-UV + G14-Nachschwingen (TEXCOORD1, Teil-Achse in der Tangente schwingender Teile)
            var gm = new Mesh { name = name, indexFormat = atlasMesh.indexFormat };
            var v = new List<Vector3>(); atlasMesh.GetVertices(v); gm.SetVertices(v);
            var uvA = new List<Vector4>(); atlasMesh.GetUVs(7, uvA);
            gm.SetUVs(0, uvA.Select(x => new Vector2(x.x, x.y)).ToList());
            gm.SetTriangles(atlasMesh.triangles, 0);
            gm.boneWeights = atlasMesh.boneWeights;
            gm.bindposes = atlasMesh.bindposes;
            var n = new List<Vector3>(); atlasMesh.GetNormals(n); gm.SetNormals(n);
            gm.RecalculateTangents();
            var sw = new List<Vector4>(); atlasMesh.GetUVs(1, sw);
            if (sw.Count != v.Count) sw = Enumerable.Repeat(Vector4.zero, v.Count).ToList();
            gm.SetUVs(1, sw);   // immer schreiben: fehlt der Kanal, liefert die GPU Zufallswerte statt 0
            if (sw.Any(x => x.y > 0))
            {
                var tgA = new List<Vector4>(); atlasMesh.GetTangents(tgA);
                var tgG = new List<Vector4>(); gm.GetTangents(tgG);
                for (int i = 0; i < sw.Count; i++) if (sw[i].y > 0) tgG[i] = tgA[i];
                gm.SetTangents(tgG);
            }
            // Rim pro Vertex (Körper- und Accessoire-Rim getrennt; Stärke × Maske steht in Maske A)
            var grpA = new List<Vector4>(); atlasMesh.GetUVs(2, grpA);
            var rimCol = grpA.Count == v.Count ? VkBuilder.RimColors(grpA, doc, res) : null;
            if (rimCol != null) gm.colors = rimCol;
            gm.RecalculateBounds();
            r.mesh = gm;
            UnityEngine.Object.DestroyImmediate(atlasMesh);
            UnityEngine.Object.DestroyImmediate(bakeMat);
            // Material
            var mat = new Material(Shader.Find(GameShader)) { name = name };
            mat.SetTexture("_MainTex", AssetDatabase.LoadAssetAtPath<Texture2D>(paths["Albedo"]));
            mat.SetTexture("_MaskTex", AssetDatabase.LoadAssetAtPath<Texture2D>(paths["Maske"]));
            if (r.emission) mat.SetTexture("_EmissionTex", AssetDatabase.LoadAssetAtPath<Texture2D>(paths["Leuchten"]));
            if (r.normal) mat.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>(paths["Normal"]));
            mat.SetFloat("_Facetten", M.Obj("stil").F("facetten", 1f));
            // Puls: ein Wert pro Material (erste pulsierende Risse-Ebene, Körper vor Accessoires)
            var puls = res.AlleEbenen.FirstOrDefault(e => e.S("typ", "") == "risse" && e.F("puls_staerke", 0) > 0.001f && e.F("puls_frequenz", 0) > 0.001f);
            mat.SetFloat("_PulsFreq", puls?.F("puls_frequenz", 0) ?? 0);
            mat.SetFloat("_PulsStaerke", puls?.F("puls_staerke", 0) ?? 0);
            mat.SetFloat("_RimAn", rimCol != null ? 1 : 0);
            r.material = mat;
            return r;
        }

        static void Dilate(Texture2D t, bool[] filled, int iterations, Color32 empty)
        {
            int w = t.width, h = t.height;
            var px = t.GetPixels32();
            var f = (bool[])filled.Clone();
            for (int i = 0; i < px.Length; i++) if (!f[i]) px[i] = empty;
            for (int it = 0; it < iterations; it++)
            {
                var nf = (bool[])f.Clone();
                var np = (Color32[])px.Clone();
                for (int y = 0; y < h; y++)
                    for (int x = 0; x < w; x++)
                    {
                        int i = y * w + x;
                        if (f[i]) continue;
                        int r = 0, g = 0, bl = 0, a = 0, n = 0;
                        for (int dy = -1; dy <= 1; dy++)
                            for (int dx = -1; dx <= 1; dx++)
                            {
                                int xx = x + dx, yy = y + dy;
                                if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
                                int j = yy * w + xx;
                                if (!f[j]) continue;
                                r += px[j].r; g += px[j].g; bl += px[j].b; a += px[j].a; n++;
                            }
                        if (n == 0) continue;
                        np[i] = new Color32((byte)(r / n), (byte)(g / n), (byte)(bl / n), (byte)(a / n));
                        nf[i] = true;
                    }
                f = nf; px = np;
            }
            t.SetPixels32(px);
            t.Apply();
        }
    }
}
