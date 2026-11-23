using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Ein platziertes Accessoire-Teil (Eintrag der Instanzen-Liste, Spec 3.3).</summary>
    public class VkInstance
    {
        public string acc, typ, form, zone, farbgruppe;
        public Matrix4x4 m;          // Baustein-Raum → Mesh-Raum (inkl. Größe, Streckung, ggf. gespiegelt)
        public bool mirrored;
        public int tri; public Vector3 bary; public Vector3 pos, nrm;
        public BoneWeight anchor;
        public string bindung;
        public float rand, farbZufall, size;
        public float[] layerMask;    // Masken der Körper-Ebenen am Ansatzpunkt (nur Bedeckung; Accessoires: 0)
        public int accIndex = -1;    // Nummer des Accessoire-Eintrags (Ziel der Accessoire-Ebenen), -1 = Bedeckung
        public int vStart, vCount;   // Bereich im kombinierten Mesh
        // M2: Teil der Bedeckung (Geometrie aus Blender statt Baustein-Bibliothek)
        public bool cover; public int lage;
        public Vector3[] cv;         // Vertices im Mesh-Raum (inkl. Statur-Versatz)
        public Vector3[] cb;         // dieselben im Körperraum / L (Ruhe, für Muster)
        public float[] ch;           // Höhe im Teil 0..1
        public int[] ct;             // Dreiecke (lokal)
        // G14 Nachschwingen (TEXCOORD1 + TANGENT, VariantSwing.cginc)
        public float weich;          // Weichheit der Lage / des Accessoires (0 = starr)
        public bool grav;            // Gehänge: folgt der Schwerkraft
        public int slot;             // Feder 0 Hüfte · 1 Brust · 2 Kopf · 3 Schwanz (aus dem Ansatz-Knochen)
        public Vector3 axis;         // Wurzel → Spitze (Mesh-Raum)
        public float lenRel;         // Länge Wurzel → Spitze / Kreaturgröße
        public int Tris => cover ? ct.Length / 3 : VkParts.Get(typ).First(f => f.name == form).tris;
    }

    /// <summary>Baustein-Bibliothek: procedural/bausteine/&lt;typ&gt;.json (Meshes in Blender-Koordinaten X vorn, Y links, Z oben).</summary>
    public static class VkParts
    {
        public class Form { public string name; public Vector3[] v; public int[] t; public float height; public int tris; }
        static readonly Dictionary<string, List<Form>> cache = new Dictionary<string, List<Form>>();
        static readonly Dictionary<string, DateTime> stamp = new Dictionary<string, DateTime>();

        public static string Dir => Path.Combine(VkBase.PipelineRoot, "procedural", "bausteine");
        public static List<string> Types() => Directory.Exists(Dir) ? Directory.GetFiles(Dir, "*.json").Select(Path.GetFileNameWithoutExtension).OrderBy(x => x).ToList() : new List<string>();

        public static List<Form> Get(string typ)
        {
            var p = Path.Combine(Dir, typ + ".json");
            if (!File.Exists(p)) return new List<Form>();
            var t = File.GetLastWriteTimeUtc(p);
            if (cache.TryGetValue(typ, out var c) && stamp[typ] == t) return c;
            var j = Json.ParseObj(File.ReadAllText(p));
            var res = new List<Form>();
            foreach (var kv in j.O("formen"))
            {
                var f = (JObj)kv.Value;
                var vs = f.L("vertices").Select(x => { var a = ((List<object>)x).Select(n => Json.ToF(n, 0)).ToArray(); return new Vector3(a[0], a[1], a[2]); }).ToArray();
                var ts = f.L("dreiecke").SelectMany(x => ((List<object>)x).Select(n => (int)Json.ToF(n, 0))).ToArray();
                res.Add(new Form { name = kv.Key, v = vs, t = ts, height = vs.Max(x => x.z), tris = ts.Length / 3 });
            }
            cache[typ] = res; stamp[typ] = t;
            return res;
        }
    }

    public class VkBuildResult
    {
        public Mesh mesh;
        public List<VkInstance> instances = new List<VkInstance>();
        public int trisBase, trisAcc;
        public List<string> warnings = new List<string>();
        public Dictionary<string, int> trisPerAcc = new Dictionary<string, int>();
        public Vector3[] dv; public Vector3[] dn;  // verformte Basis (Mesh-Raum)
        public int trisCover; public VkCover cover; public bool coverFresh, coverWanted;
        public Dictionary<int, int> trisCoverLage = new Dictionary<int, int>();
        public List<JObj> ebenen = new List<JObj>();      // Körper-Ebenen (aktiv, höchstens 8)
        public List<JObj> ebenenAcc = new List<JObj>();   // Accessoire-Ebenen (aktiv, höchstens 4)
        public List<string> accIds = new List<string>();  // aktive Accessoire-Einträge, Index = Eintrags-Nummer im Shader
        public int[] ebenenAuf = new int[0];              // pro Körper-Ebene: 1 = Haut, 2 = Lage 1, 4 = Lage 2 (VkSpec.AufBits)
        public IEnumerable<JObj> AlleEbenen => ebenen.Concat(ebenenAcc);
    }

    /// <summary>Baut aus Basis + Varianten-Datei das kombinierte Mesh (1 SkinnedMesh: Körper + Accessoires mit Gewichten
    /// des Ansatzpunkts) und stellt Material + Statur ein. Dieselbe Rechnung für Live-Vorschau und Backen.</summary>
    public static class VkBuilder
    {
        static float Smooth(float e0, float e1, float x) { float t = Mathf.Clamp01((x - e0) / (e1 - e0)); return t * t * (3 - 2 * t); }

        public static VkBuildResult Build(VkBase b, VkDoc doc)
        {
            var r = new VkBuildResult();
            var R = doc.resolved;
            ApplyShape(b, R.Obj("statur"), out r.dv);
            r.dn = FaceAwareNormals(b, r.dv);
            r.ebenen = R.Obj("material").List("ebenen").OfType<JObj>().Where(e => e.B("an", true)).Take(VkSpec.MaxEbenen).ToList();
            r.ebenenAcc = R.Obj("material").List("ebenen_accessoires").OfType<JObj>().Where(e => e.B("an", true)).Take(VkSpec.MaxAccEbenen).ToList();
            r.accIds = VkSpec.AktiveAccessoires(R).Select(a => a.S("id", "")).ToList();
            if (r.accIds.Count > VkSpec.MaxAccEintraege && r.ebenenAcc.Any(e => !VkSpec.ZielAlle(e)))
                r.warnings.Add($"Mehr als {VkSpec.MaxAccEintraege} Accessoire-Einträge: Einträge ab Nr. {VkSpec.MaxAccEintraege + 1} erreicht nur eine Accessoire-Ebene mit Ziel „alle“.");
            // Körper-Ebenen: Zonen-Maske pro Vertex. Fehlt „zonen“ → ganzer Körper (Standard); eine LEERE Liste heißt „nirgends“
            // (bis Format 1 galt leer als ganzer Körper – „alle Zonen abwählen“ wirkte deshalb nicht).
            var layerMasks = r.ebenen.Select(e =>
            {
                var m = e.O("maske") ?? new JObj();
                var z = m.L("zonen") == null ? new List<string> { "ganzer_koerper" } : m.Strs("zonen");
                return b.zones.Mask(z, m.Strs("ohne"));
            }).ToList();
            // Haut / Bedeckung (Nutzer 2026-11-23): wirkt die Ebene auf das Basis-Mesh und auf welche Lagen? Wird unten direkt in die
            // Vertex-Masken TEXCOORD5/6 eingerechnet (Basis × Haut-Bit, Bedeckungs-Teil × Bit seiner Lage) → Vorschau-Shader,
            // Textur-Backen und Spiel-Shader brauchen keine Änderung und sehen gleich aus.
            var lagenIds = VkSpec.AktiveLagen(R).Select((l, k) => VkSpec.LageId(l, k)).ToList();
            r.ebenenAuf = r.ebenen.Select(e => VkSpec.AufBits(e, lagenIds)).ToArray();
            // Accessoires mit `auf` (sitzen auf einem anderen Accessoire) nach den übrigen platzieren
            foreach (JObj acc in R.List("accessoires").OfType<JObj>().OrderBy(x => x["auf"] is string ? 1 : 0))
            {
                if (!acc.B("an", true)) continue;
                try { Place(b, doc, acc, r, layerMasks); }
                catch (Exception ex) { r.warnings.Add($"{acc.S("id", "?")}: {ex.Message}"); }
            }
            AddCover(b, doc, r);
            r.mesh = Combine(b, r, layerMasks);
            r.trisBase = b.tris.Length / 3;
            r.trisAcc = r.instances.Where(i => !i.cover).Sum(i => i.vCount > 0 ? i.Tris : 0);
            r.trisCover = r.instances.Where(i => i.cover).Sum(i => i.Tris);
            foreach (var g in r.instances.Where(i => i.cover).GroupBy(i => i.lage)) r.trisCoverLage[g.Key] = g.Sum(i => i.Tris);
            foreach (var g in r.instances.Where(i => !i.cover).GroupBy(i => i.acc))
                r.trisPerAcc[g.Key] = g.Sum(i => i.Tris);
            return r;
        }

        // ------------------------------------------------------------------ Schicht 2: Bedeckung aus Blender (M2)
        /// <summary>Teile der Bedeckung (Blender-Ergebnis) als Instanzen anhängen. Statur S: Versatz des Ansatzpunkts.</summary>
        static void AddCover(VkBase b, VkDoc doc, VkBuildResult r)
        {
            r.coverWanted = VkCover.HasLayers(doc);
            if (!r.coverWanted) return;
            VkCover c;
            try { c = VkCover.Get(b, doc); }
            catch (Exception ex) { r.warnings.Add("Bedeckung unlesbar: " + ex.Message); return; }
            r.cover = c;
            if (c == null) { r.warnings.Add("Bedeckung noch nicht gebaut – Knopf „In Blender bauen“."); return; }
            r.coverFresh = c.Fresh(doc);
            if (!r.coverFresh) r.warnings.Add("Bedeckung veraltet (Lagen geändert) – „In Blender bauen“.");
            // gleiche Zählung wie der Blender-Export: aktive Lagen, höchstens 2, Lage = Index + 1
            var lagen = doc.resolved.Obj("bedeckung").List("lagen").OfType<JObj>().Where(l => l.B("an", true)).Take(2).ToList();
            foreach (var p in c.parts)
            {
                Vector3 d = Lerp3(r.dv, p.tri, b.tris, p.bary) - Lerp3(b.verts, p.tri, b.tris, p.bary);
                var cv = new Vector3[p.nv]; var cb = new Vector3[p.nv]; var ch = new float[p.nv];
                for (int k = 0; k < p.nv; k++)
                {
                    cb[k] = c.body[p.v0 + k];
                    cv[k] = b.FromBody(cb[k] * b.L) + d;
                    ch[k] = c.h[p.v0 + k];
                }
                var ct = new List<int>();
                for (int k = 0; k < c.tris.Length; k += 3)
                    if (c.tris[k] >= p.v0 && c.tris[k] < p.v0 + p.nv) { ct.Add(c.tris[k] - p.v0); ct.Add(c.tris[k + 1] - p.v0); ct.Add(c.tris[k + 2] - p.v0); }
                var lage = p.lage - 1 < lagen.Count ? lagen[p.lage - 1] : null;
                // Achse: Mittel der Wurzel-Vertices → Mittel der Spitzen-Vertices
                Vector3 root = Vector3.zero, tip = Vector3.zero; float nr = 0, nt = 0, hmax = ch.Length > 0 ? ch.Max() : 1;
                for (int k = 0; k < p.nv; k++)
                {
                    if (ch[k] <= 0.02f) { root += cv[k]; nr++; }
                    if (ch[k] >= hmax - 0.02f) { tip += cv[k]; nt++; }
                }
                var axis = nr > 0 && nt > 0 ? tip / nt - root / nr : b.up;
                r.instances.Add(new VkInstance
                {
                    acc = "bedeckung_" + p.lage, typ = "bedeckung", form = "", zone = "", cover = true, lage = p.lage,
                    cv = cv, cb = cb, ch = ch, ct = ct.ToArray(), tri = p.tri, bary = p.bary,
                    pos = Lerp3(r.dv, p.tri, b.tris, p.bary), anchor = p.weights, bindung = "anker", rand = p.rand,
                    farbgruppe = p.farbgruppe, farbZufall = 0, size = 0.05f,
                    weich = lage != null ? VkSpec.WeichheitLage(lage) : 0, slot = SlotOf(b, p.weights),
                    axis = axis.sqrMagnitude > 1e-12f ? axis.normalized : b.up, lenRel = axis.magnitude / Mathf.Max(1e-6f, b.L * Mathf.Max(1e-3f, hmax)),
                });
            }
        }

        // ------------------------------------------------------------------ Statur Typ S (Formziele) direkt ins Mesh
        /// <summary>Formziele prozedural (Spec 1.1): Verschiebung mit weicher Maske. Kein Blendshape nötig, kostet zur
        /// Laufzeit nichts. Formeln: Faktor 1 = Basis.</summary>
        public static void ApplyShape(VkBase b, JObj st, out Vector3[] dv)
        {
            int n = b.verts.Length;
            dv = (Vector3[])b.verts.Clone();
            float rh = st.F("rumpf_hoehe", 1), rd = st.F("rumpf_dicke", 1), bu = st.F("buckel", 1), gd = st.F("glied_dicke", 1),
                  kb = st.F("kopf_breite", 1), sl = st.F("schnauze_laenge", 1);
            if (Mathf.Approximately(rh, 1) && Mathf.Approximately(rd, 1) && Mathf.Approximately(bu, 1) && Mathf.Approximately(gd, 1)
                && Mathf.Approximately(kb, 1) && Mathf.Approximately(sl, 1)) return;
            var torso = new[] { "Hips", "Spine_1", "Chest", "Neck_1" }.Select(b.Bone).Where(i => i >= 0).ToList();
            var legs = b.boneNames.Where(x => System.Text.RegularExpressions.Regex.IsMatch(x, "^Leg_[FB][LR]_[123]$")).Select(b.Bone).ToList();
            int head = b.Bone("Head"), jaw = b.Bone("Jaw");
            var hump = b.zones.Mask("buckel");
            float headLen = head >= 0 ? (b.boneTail[head] - b.boneHead[head]).magnitude : 0;
            var hb = head >= 0 ? b.Body(b.boneHead[head]) : Vector3.zero;
            for (int v = 0; v < n; v++)
            {
                var p = b.verts[v]; var bp = b.Body(p);
                var d = Vector3.zero;   // Versatz in Körperkoordinaten
                float wt = Smooth(0.3f, 0.85f, b.WeightSum(v, torso));
                if (wt > 0)
                {
                    float top = b.TorsoTop(bp.x), bot = b.TorsoBot(bp.x), cy = (top + bot) * 0.5f;
                    d.y += (rh - 1) * (bp.y - cy) * wt;
                    d.y += (rd - 1) * (bp.y - cy) * wt * 0.6f;
                    d.z += (rd - 1) * bp.z * wt;
                }
                d.y += (bu - 1) * 0.07f * b.L * hump[v];
                if (gd != 1)
                {
                    int best = -1; float bw = 0;
                    foreach (var l in legs) { float w = b.Weight(v, l); if (w > bw) { bw = w; best = l; } }
                    float wl = b.WeightSum(v, legs);
                    if (best >= 0 && wl > 0)
                    {
                        float t = Mathf.Clamp01(b.Along(p, best));
                        var axisP = Vector3.Lerp(b.boneHead[best], b.boneTail[best], t);
                        var off = b.BodyDir(p - axisP);
                        var dir = b.BodyDir(b.boneTail[best] - b.boneHead[best]).normalized;
                        off -= Vector3.Dot(off, dir) * dir;
                        d += (gd - 1) * off * Smooth(0.2f, 0.8f, wl);
                    }
                }
                if (head >= 0)
                {
                    float wh = b.Weight(v, head) + (jaw >= 0 ? b.Weight(v, jaw) : 0);
                    if (wh > 0)
                    {
                        d.z += (kb - 1) * bp.z * wh;
                        d.y -= (kb - 1) * 0.3f * (bp.y - hb.y) * wh;
                        float t = b.Along(p, head);
                        d.x += (sl - 1) * Mathf.Max(0, t - 0.6f) * headLen * wh;
                    }
                }
                dv[v] = p + b.fwd * d.x + b.up * d.y + b.left * d.z;
            }
        }

        static Vector3[] FaceAwareNormals(VkBase b, Vector3[] dv)
        {
            var m = new Mesh { vertices = dv, triangles = b.tris };
            m.RecalculateNormals();
            var n = m.normals;
            UnityEngine.Object.DestroyImmediate(m);
            // Richtung an den importierten Normalen ausrichten (Wicklung)
            for (int i = 0; i < n.Length; i++) if (Vector3.Dot(n[i], b.normals[i]) < 0) n[i] = -n[i];
            return n;
        }

        // ------------------------------------------------------------------ Schicht 3: Platzierung (Unity, Spec 3.3)
        public struct Cand { public int tri; public Vector3 bary, pos, nrm; public float mask; }

        static Vector3 Lerp3(Vector3[] a, int t, int[] tris, Vector3 w) => a[tris[t * 3]] * w.x + a[tris[t * 3 + 1]] * w.y + a[tris[t * 3 + 2]] * w.z;

        static Vector3 FaceN(VkBase b, Vector3[] dv, Vector3[] dn, int t)
        {
            Vector3 a = dv[b.tris[t * 3]], c1 = dv[b.tris[t * 3 + 1]], c2 = dv[b.tris[t * 3 + 2]];
            var n = Vector3.Cross(c1 - a, c2 - a).normalized;
            var avg = dn[b.tris[t * 3]] + dn[b.tris[t * 3 + 1]] + dn[b.tris[t * 3 + 2]];
            return Vector3.Dot(n, avg) < 0 ? -n : n;
        }

        static List<Cand> Sample(VkBase b, VkBuildResult r, float[] mask, int count, System.Random rnd)
        {
            int nt = b.tris.Length / 3;
            var cdf = new double[nt]; double acc = 0;
            for (int t = 0; t < nt; t++)
            {
                float m = (mask[b.tris[t * 3]] + mask[b.tris[t * 3 + 1]] + mask[b.tris[t * 3 + 2]]) / 3f;
                if (m > 0.35f)
                {
                    Vector3 a = r.dv[b.tris[t * 3]], c1 = r.dv[b.tris[t * 3 + 1]], c2 = r.dv[b.tris[t * 3 + 2]];
                    acc += Vector3.Cross(c1 - a, c2 - a).magnitude * 0.5 * m * m;
                }
                cdf[t] = acc;
            }
            var res = new List<Cand>();
            if (acc <= 0) return res;
            for (int k = 0; k < count; k++)
            {
                double x = rnd.NextDouble() * acc;
                int t = Array.BinarySearch(cdf, x); if (t < 0) t = ~t; t = Mathf.Clamp(t, 0, nt - 1);
                float u = (float)rnd.NextDouble(), v = (float)rnd.NextDouble();
                if (u + v > 1) { u = 1 - u; v = 1 - v; }
                var w = new Vector3(1 - u - v, u, v);
                float mm = mask[b.tris[t * 3]] * w.x + mask[b.tris[t * 3 + 1]] * w.y + mask[b.tris[t * 3 + 2]] * w.z;
                res.Add(new Cand { tri = t, bary = w, pos = Lerp3(r.dv, t, b.tris, w), nrm = FaceN(b, r.dv, r.dn, t), mask = mm });
            }
            return res;
        }

        static List<Cand> Scatter(List<Cand> cands, int n, float dmin)
        {
            var res = new List<Cand>();
            foreach (var c in cands)
            {
                if (res.Count >= n) break;
                if (res.All(o => (o.pos - c.pos).magnitude >= dmin)) res.Add(c);
            }
            return res;
        }

        /// <summary>Nächster Punkt auf der (verformten) Haut, optional nur Dreiecke mit Maske.</summary>
        public static Cand Closest(VkBase b, Vector3[] dv, Vector3[] dn, Vector3 p, float[] mask = null)
        {
            var best = new Cand { tri = -1 }; float bd = float.MaxValue;
            for (int t = 0; t < b.tris.Length / 3; t++)
            {
                if (mask != null && Mathf.Max(mask[b.tris[t * 3]], mask[b.tris[t * 3 + 1]], mask[b.tris[t * 3 + 2]]) < 0.05f) continue;
                Vector3 a = dv[b.tris[t * 3]], c1 = dv[b.tris[t * 3 + 1]], c2 = dv[b.tris[t * 3 + 2]];
                var q = ClosestOnTri(p, a, c1, c2, out var w);
                float d = (q - p).sqrMagnitude;
                if (d < bd) { bd = d; best = new Cand { tri = t, bary = w, pos = q, nrm = FaceN(b, dv, dn, t) }; }
            }
            return best;
        }

        static Vector3 ClosestOnTri(Vector3 p, Vector3 a, Vector3 b, Vector3 c, out Vector3 bary)
        {
            // Ericson, Real-Time Collision Detection 5.1.5
            var ab = b - a; var ac = c - a; var ap = p - a;
            float d1 = Vector3.Dot(ab, ap), d2 = Vector3.Dot(ac, ap);
            if (d1 <= 0 && d2 <= 0) { bary = new Vector3(1, 0, 0); return a; }
            var bp = p - b; float d3 = Vector3.Dot(ab, bp), d4 = Vector3.Dot(ac, bp);
            if (d3 >= 0 && d4 <= d3) { bary = new Vector3(0, 1, 0); return b; }
            float vc = d1 * d4 - d3 * d2;
            if (vc <= 0 && d1 >= 0 && d3 <= 0) { float v = d1 / (d1 - d3); bary = new Vector3(1 - v, v, 0); return a + v * ab; }
            var cp = p - c; float d5 = Vector3.Dot(ab, cp), d6 = Vector3.Dot(ac, cp);
            if (d6 >= 0 && d5 <= d6) { bary = new Vector3(0, 0, 1); return c; }
            float vb = d5 * d2 - d1 * d6;
            if (vb <= 0 && d2 >= 0 && d6 <= 0) { float w = d2 / (d2 - d6); bary = new Vector3(1 - w, 0, w); return a + w * ac; }
            float va = d3 * d6 - d5 * d4;
            if (va <= 0 && (d4 - d3) >= 0 && (d5 - d6) >= 0) { float w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); bary = new Vector3(0, 1 - w, w); return b + w * (c - b); }
            float den = 1f / (va + vb + vc); float vv = vb * den, ww = vc * den;
            bary = new Vector3(1 - vv - ww, vv, ww);
            return a + ab * vv + ac * ww;
        }

        public static BoneWeight Blend(VkBase b, int tri, Vector3 bary, string bindung)
        {
            var acc = new Dictionary<int, float>();
            void Add(int bi, float w) { if (w <= 0) return; acc.TryGetValue(bi, out var o); acc[bi] = o + w; }
            for (int k = 0; k < 3; k++)
            {
                var bw = b.weights[b.tris[tri * 3 + k]]; float f = bary[k];
                Add(bw.boneIndex0, bw.weight0 * f); Add(bw.boneIndex1, bw.weight1 * f); Add(bw.boneIndex2, bw.weight2 * f); Add(bw.boneIndex3, bw.weight3 * f);
            }
            var top = acc.OrderByDescending(kv => kv.Value).Take(bindung == "knochen" ? 1 : 4).ToList();
            float s = top.Sum(kv => kv.Value);
            var r = new BoneWeight();
            for (int i = 0; i < top.Count; i++)
            {
                float w = top[i].Value / s;
                switch (i)
                {
                    case 0: r.boneIndex0 = top[i].Key; r.weight0 = w; break;
                    case 1: r.boneIndex1 = top[i].Key; r.weight1 = w; break;
                    case 2: r.boneIndex2 = top[i].Key; r.weight2 = w; break;
                    case 3: r.boneIndex3 = top[i].Key; r.weight3 = w; break;
                }
            }
            return r;
        }

        static void Place(VkBase b, VkDoc doc, JObj a, VkBuildResult r, List<float[]> layerMasks)
        {
            string id = a.S("id", "acc"), typ = a.S("typ", "");
            var forms = VkParts.Get(typ);
            if (forms.Count == 0) { r.warnings.Add($"{id}: keine Bausteine für Typ '{typ}' (procedural/bausteine/{typ}.json)"); return; }
            var want = a.Strs("formen");
            var use = want.Count > 0 ? forms.Where(f => want.Contains(f.name)).ToList() : forms;
            if (use.Count == 0) use = forms;
            var rnd = new System.Random(doc.EntrySeed(a, id));
            string vert = a.S("verteilung", "streuen");
            int anzahl = Mathf.Max(0, a.I("anzahl", 1)), teile = Mathf.Max(1, a.I("teile", 4));
            float L = b.L, size = a.F("groesse", 0.1f) * L, gz = a.F("groesse_zufall", 0.3f);
            float dmin = Mathf.Max(a.F("abstand_min", 0.02f) * L, 0f);
            var zonen = a.Strs("zonen"); if (zonen.Count == 0) zonen.Add("buckel");
            bool spiegeln = a.B("spiegeln", true);
            var points = new List<(Cand c, string zone, float sizeF)>();
            var parentOf = new Dictionary<int, VkInstance>();   // `auf`: Punkt sitzt auf diesem Teil (erbt dessen Gewichte)
            string auf = a["auf"] as string;
            var gv = a.Vec("groesse_verlauf", new[] { 1f, 1f, 1f });
            float Verlauf(float t) => t < 0.5f ? Mathf.Lerp(gv[0], gv[1], t * 2) : Mathf.Lerp(gv[1], gv[2], t * 2 - 1);

            if (!string.IsNullOrEmpty(auf))
            {
                // Spec 3.3 `auf` + `stelle`: auf einem anderen Accessoire sitzen (oben) oder an seinem unteren Rand hängen
                var parents = r.instances.Where(i => !i.cover && i.acc == auf).ToList();
                if (parents.Count == 0) { r.warnings.Add($"{id}: auf '{auf}' – kein solches Accessoire (oder es ist aus)"); return; }
                spiegeln = false;   // die Eltern sind schon gespiegelt
                string stelle = a.S("stelle", "oben");
                foreach (var pi in parents)
                {
                    var pf = VkParts.Get(pi.typ).FirstOrDefault(f => f.name == pi.form);
                    if (pf == null) continue;
                    var pc = pi.m.MultiplyPoint3x4(new Vector3(0, 0, pf.height * 0.5f));
                    var pu = ((Vector3)pi.m.GetColumn(2)).normalized;
                    float rmax = pf.v.Max(v => new Vector2(v.x, v.y).magnitude);
                    var cands = new List<Cand>();
                    foreach (var v in pf.v)
                    {
                        float rr = new Vector2(v.x, v.y).magnitude;
                        bool ok = stelle == "rand_unten" ? v.z <= pf.height * 0.35f && rr >= rmax * 0.55f : v.z >= pf.height * 0.55f;
                        if (!ok) continue;
                        var wp = pi.m.MultiplyPoint3x4(v);
                        var outw = wp - pc; outw -= Vector3.Dot(outw, pu) * pu;
                        var n = stelle == "rand_unten" ? (outw.sqrMagnitude > 1e-12f ? outw.normalized : pu) : pu;
                        // am Rand unten: nur Stellen, deren Außenseite nicht nach oben zeigt (sonst hängt die Franse über dem Rücken)
                        if (stelle == "rand_unten" && Vector3.Dot(n, b.up) > 0.2f) continue;
                        cands.Add(new Cand { tri = pi.tri, bary = pi.bary, pos = wp, nrm = n, mask = 1 });
                    }
                    foreach (var c in Scatter(cands.OrderBy(_ => rnd.Next()).ToList(), anzahl, Mathf.Max(dmin, size * 0.5f)))
                    {
                        parentOf[points.Count] = pi;
                        points.Add((c, pi.zone, 1));
                    }
                }
            }
            else if (vert == "reihe")
            {
                var rl = b.zones.rueckenlinie;
                float u0 = b.BoneU(rl.S("von", "Head:0.25")), u1 = b.BoneU(rl.S("bis", "Tail_1:0.8"));
                float von = a.F("von", 0.1f), bis = a.F("bis", 0.8f);
                int reihen = Mathf.Clamp(a.I("reihen", 1), 1, 2);
                var st = a.Vec("streckung", new[] { 1f, 1f, 1f });
                float off = reihen == 2 ? size * 0.42f * st[1] + dmin * 0.5f : 0;
                for (int k = 0; k < anzahl; k++)
                {
                    float t = anzahl <= 1 ? 0.5f : (float)k / (anzahl - 1);
                    float pt = Mathf.Lerp(von, bis, t);
                    float side = reihen == 2 ? (k % 2 == 0 ? 1 : -1) : 0;
                    var q = new Vector3(Mathf.Lerp(u0, u1, pt), 0, side * off);
                    if (b.RayDown(q, out int tri, out var bary, out _))
                    {
                        var c = new Cand { tri = tri, bary = bary, pos = Lerp3(r.dv, tri, b.tris, bary), nrm = FaceN(b, r.dv, r.dn, tri), mask = 1 };
                        points.Add((c, "rueckenlinie", Verlauf(t)));
                    }
                }
            }
            else if (vert == "cluster" || vert == "kranz")
            {
                var mask = b.zones.Mask(zonen, null);
                var cands = Sample(b, r, mask, 600, rnd);
                if (cands.Count == 0) { r.warnings.Add($"{id}: Zone(n) {string.Join(",", zonen)} leer"); return; }
                string zl = string.Join("+", zonen);
                if (vert == "cluster")
                {
                    float rad = size * (0.45f + 0.28f * Mathf.Sqrt(teile));
                    var centers = Scatter(cands.OrderByDescending(c => c.mask).Take(Mathf.Max(30, cands.Count / 3)).OrderBy(_ => rnd.Next()).ToList(), anzahl, rad * 1.6f);
                    foreach (var cen in centers)
                    {
                        float spacing = Mathf.Max(dmin, size * 0.5f);
                        List<Cand> got = null;
                        for (int tries = 0; tries < 4; tries++, spacing *= 0.8f)
                        {
                            got = Scatter(cands.Where(c => (c.pos - cen.pos).magnitude < rad * (1 + tries * 0.25f))
                                .OrderBy(c => (c.pos - cen.pos).magnitude + (float)rnd.NextDouble() * rad * 0.5f).ToList(), teile, spacing);
                            if (got.Count >= teile) break;
                        }
                        foreach (var g in got) points.Add((g, zl, 1));
                    }
                }
                else
                {
                    var cen = cands.Aggregate(Vector3.zero, (s, c) => s + c.pos) / cands.Count;
                    var nrm = cands.Aggregate(Vector3.zero, (s, c) => s + c.nrm).normalized;
                    var tx = Vector3.Cross(nrm, b.left).normalized; if (tx.sqrMagnitude < 0.1f) tx = b.fwd;
                    var ty = Vector3.Cross(nrm, tx);
                    float rad = cands.Max(c => (c.pos - cen).magnitude) * 0.7f;
                    for (int k = 0; k < anzahl; k++)
                    {
                        float ang = k * Mathf.PI * 2 / anzahl;
                        var target = cen + (tx * Mathf.Cos(ang) + ty * Mathf.Sin(ang)) * rad;
                        var c = cands.OrderBy(x => (x.pos - target).sqrMagnitude).First();
                        points.Add((c, zl, Verlauf((float)k / Mathf.Max(1, anzahl - 1))));
                    }
                }
            }
            else
            {
                foreach (var z in zonen)
                {
                    if (spiegeln && z.EndsWith("_r") && zonen.Contains(z.Substring(0, z.Length - 2) + "_l")) continue;
                    var mask = b.zones.Mask(new[] { z }, null);
                    var cands = Sample(b, r, mask, 400, rnd);
                    if (cands.Count == 0) { r.warnings.Add($"{id}: Zone {z} leer"); continue; }
                    if (vert == "einzeln")
                    {
                        float ws = cands.Sum(c => c.mask);
                        var cen = cands.Aggregate(Vector3.zero, (s, c) => s + c.pos * c.mask) / Mathf.Max(1e-6f, ws);
                        var first = cands.OrderBy(c => (c.pos - cen).sqrMagnitude).First();
                        points.Add((first, z, 1));
                        if (anzahl > 1)
                            foreach (var c in Scatter(cands.OrderBy(_ => rnd.Next()).Where(c => (c.pos - first.pos).magnitude > size).ToList(), anzahl - 1, Mathf.Max(dmin, size * 0.8f)))
                                points.Add((c, z, 1));
                    }
                    else
                        foreach (var c in Scatter(cands.OrderByDescending(c => c.mask * (0.6f + 0.4f * (float)rnd.NextDouble())).ToList(), anzahl, Mathf.Max(dmin, size * 0.75f)))
                            points.Add((c, z, 1));
                }
            }

            // ---- Ausrichtung + Transformation
            var str = a.Vec("streckung", new[] { 1f, 1f, 1f });
            string aus = a.S("ausrichtung", "normale"), bind = a.S("bindung", "anker");
            float neig = a.F("neigung", 0) * Mathf.Deg2Rad, dreh = a.F("drehung_zufall", 180), kipp = a.F("kipp_zufall", 10), eins = a.F("einsinken", 0.25f);
            float asym = a.F("asymmetrie", 0.2f);
            float hand = Mathf.Sign(Vector3.Dot(Vector3.Cross(b.up, b.fwd), b.left));
            bool clusterMirror = spiegeln && (vert == "cluster" || vert == "kranz") && zonen.All(z => z.EndsWith("_l"));
            int count = 0;
            float weich = VkSpec.WeichheitAcc(a);
            bool grav = VkSpec.Haengt(typ);
            for (int pIdx = 0; pIdx < points.Count; pIdx++)
            {
                var (c, zone, sizeF) = points[pIdx];
                parentOf.TryGetValue(pIdx, out var parent);
                var form = use[rnd.Next(use.Count)];
                float sF = sizeF * Mathf.Lerp(1 - gz * 0.5f, 1 + gz * 0.5f, (float)rnd.NextDouble());
                float s = size * sF;
                Vector3 U;
                var bc = b.Body(c.pos);
                switch (aus)
                {
                    case "oben": U = b.up; break;
                    case "hinten": U = -b.fwd; break;
                    case "unten":   // Gehänge: hängt nach unten, leicht von der Haut weg geneigt
                        {
                            var nh = c.nrm - Vector3.Dot(c.nrm, b.up) * b.up;
                            U = (-b.up + 0.3f * (nh.sqrMagnitude > 1e-8f ? nh.normalized : Vector3.zero)).normalized;
                            break;
                        }
                    case "aussen": U = Mathf.Abs(bc.z) < L * 0.02f ? c.nrm : (b.left * Mathf.Sign(bc.z) + c.nrm).normalized; break;
                    default: U = c.nrm; break;
                }
                Vector3 F = b.fwd;
                if (aus == "knochen")
                {
                    var w = Blend(b, c.tri, c.bary, "knochen");
                    F = b.boneTail[w.boneIndex0] - b.boneHead[w.boneIndex0];
                }
                F -= Vector3.Dot(F, U) * U;
                if (F.sqrMagnitude < 1e-8f) { F = b.up - Vector3.Dot(b.up, U) * U; }
                F.Normalize();
                // Neigung (− = nach hinten), Kippen (zufällig), Drehung um die eigene Achse
                if (neig != 0) { var U2 = U * Mathf.Cos(neig) + F * Mathf.Sin(neig); F = F * Mathf.Cos(neig) - U * Mathf.Sin(neig); U = U2; }
                float th = (float)rnd.NextDouble() * Mathf.PI * 2, kp = (float)rnd.NextDouble() * kipp * Mathf.Deg2Rad;
                var W0 = Vector3.Cross(U, F) * hand;
                var T = F * Mathf.Cos(th) + W0 * Mathf.Sin(th);
                U = (U * Mathf.Cos(kp) + T * Mathf.Sin(kp)).normalized;
                F = (F - Vector3.Dot(F, U) * U).normalized;
                float dr = ((float)rnd.NextDouble() * 2 - 1) * dreh * Mathf.Deg2Rad;
                var Wd = Vector3.Cross(U, F) * hand;
                F = (F * Mathf.Cos(dr) + Wd * Mathf.Sin(dr)).normalized;
                var W = Vector3.Cross(U, F) * hand;
                var pos = c.pos - U * (eins * form.height * s * str[2]);
                var m = new Matrix4x4();
                m.SetColumn(0, F * (s * str[0])); m.SetColumn(1, W * (s * str[1])); m.SetColumn(2, U * (s * str[2]));
                m.SetColumn(3, new Vector4(pos.x, pos.y, pos.z, 1));
                float rnd1 = (float)rnd.NextDouble();
                var anchorW = parent != null ? parent.anchor : Blend(b, c.tri, c.bary, bind);
                float lenRel = form.height * s * str[2] / L;
                var inst = new VkInstance
                {
                    acc = id, typ = typ, form = form.name, zone = zone, m = m, tri = c.tri, bary = c.bary, pos = c.pos, nrm = c.nrm,
                    anchor = anchorW, bindung = parent != null ? "anker" : bind, rand = rnd1, size = s / L,
                    farbgruppe = a.S("farbgruppe", "accessoire_a"), farbZufall = a.F("farb_zufall", 0),
                    weich = weich, grav = grav, slot = SlotOf(b, anchorW), axis = U, lenRel = lenRel,
                };
                r.instances.Add(inst);
                count++;
                bool mirror = spiegeln && (clusterMirror || (zone.EndsWith("_l") && vert != "reihe"));
                if (mirror)
                {
                    var mir = Matrix4x4.identity;
                    var lft = b.left;
                    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) mir[i, j] = (i == j ? 1 : 0) - 2 * lft[i] * lft[j];
                    var o = b.origin;
                    var M = Matrix4x4.Translate(o) * mir * Matrix4x4.Translate(-o);
                    var mp = M.MultiplyPoint3x4(c.pos);
                    string rz = zone.EndsWith("_l") ? zone.Substring(0, zone.Length - 2) + "_r" : zone;
                    var snap = Closest(b, r.dv, r.dn, mp, b.zones.Mask(new[] { rz }, null));
                    if (snap.tri < 0) snap = Closest(b, r.dv, r.dn, mp);
                    float af = 1 + asym * ((float)rnd.NextDouble() - 0.5f) * 0.4f;
                    var mm = M * m;
                    var sc = Matrix4x4.Translate(snap.pos) * Matrix4x4.Scale(Vector3.one * af) * Matrix4x4.Translate(-mp);
                    r.instances.Add(new VkInstance
                    {
                        acc = id, typ = typ, form = form.name, zone = rz, m = sc * mm, mirrored = true, tri = snap.tri, bary = snap.bary,
                        pos = snap.pos, nrm = snap.nrm, anchor = Blend(b, snap.tri, snap.bary, bind), bindung = bind, rand = rnd1, size = s * af / L,
                        farbgruppe = inst.farbgruppe, farbZufall = inst.farbZufall,
                        weich = weich, grav = grav, slot = SlotOf(b, Blend(b, snap.tri, snap.bary, bind)),
                        axis = ((Vector3)(sc * mm).GetColumn(2)).normalized, lenRel = lenRel * af,
                    });
                }
            }
            if (count == 0) r.warnings.Add($"{id}: kein Teil platziert");
        }

        // ------------------------------------------------------------------ Zusammenführen zu 1 Mesh
        static Mesh Combine(VkBase b, VkBuildResult r, List<float[]> layerMasks)
        {
            int nb = b.verts.Length;
            var V = new List<Vector3>(r.dv);
            var UV0 = new List<Vector2>(b.mesh.uv.Length == nb ? b.mesh.uv : new Vector2[nb]);
            var G = new List<Vector4>(); var P = new List<Vector4>(); var N = new List<Vector4>();
            var M0 = new List<Vector4>(); var M1 = new List<Vector4>();
            var SW = new List<Vector4>(new Vector4[nb]);   // G14: TEXCOORD1 (Basis = 0, starr)
            var BW = new List<BoneWeight>(b.weights);
            var T = new List<int>();
            for (int sm = 0; sm < b.mesh.subMeshCount; sm++) T.AddRange(b.mesh.GetTriangles(sm));
            float L = b.L;
            Vector4 Masks(int v, int off, Func<int, int, float> f) => new Vector4(f(off, v), f(off + 1, v), f(off + 2, v), f(off + 3, v));
            float LM(int li, int v) => li < layerMasks.Count && (r.ebenenAuf[li] & 1) != 0 ? layerMasks[li][v] : 0;   // Haut-Bit
            for (int v = 0; v < nb; v++)
            {
                G.Add(new Vector4(b.lightGroup[v], b.darkGroup[v], 0, 1));
                var bp = b.Body(b.verts[v]) / L;
                P.Add(new Vector4(bp.x, bp.y, bp.z, 0));
                var bn = b.BodyDir(b.normals[v]);
                N.Add(new Vector4(bn.x, bn.y, bn.z, 0));
                M0.Add(Masks(v, 0, LM)); M1.Add(Masks(v, 4, LM));
            }
            // Haut-Bindung: Dreiecke in der Nähe vorsortieren
            foreach (var inst in r.instances)
            {
                if (inst.cover) { AddCoverPart(b, inst, layerMasks, r.ebenenAuf, V, UV0, G, P, N, M0, M1, BW, T); for (int k = 0; k < inst.cv.Length; k++) SW.Add(Swing(inst, inst.ch[k])); continue; }
                var form = VkParts.Get(inst.typ).First(f => f.name == inst.form);
                inst.vStart = V.Count; inst.vCount = form.v.Length;
                int g = VkSpec.GruppeIndex(inst.farbgruppe);
                // Accessoires: KEINE Körper-Masken (Körper-Ebenen wirken nie auf Accessoires). Stattdessen die Eintrags-Nummer in
                // TEXCOORD2.w = −(1 + n) → die Accessoire-Ebenen wählen ihr Ziel über eine Bit-Tabelle (Material, _A#M.y).
                inst.layerMask = new float[8];
                inst.accIndex = r.accIds.IndexOf(inst.acc);
                float accW = -(1 + Mathf.Max(0, inst.accIndex));
                float[] near = null;
                if (inst.bindung == "haut")
                {
                    near = new float[nb];
                    float rad = inst.size * L * 1.5f;
                    for (int v = 0; v < nb; v++) near[v] = (r.dv[v] - inst.pos).magnitude < rad ? 1 : 0;
                }
                foreach (var pv in form.v)
                {
                    var wp = inst.m.MultiplyPoint3x4(pv);
                    V.Add(wp);
                    UV0.Add(new Vector2(pv.x * 0.5f + 0.5f, pv.y * 0.5f + 0.5f));
                    G.Add(new Vector4(g, inst.farbZufall, inst.rand, accW));
                    var bp = b.Body(wp) / L;
                    P.Add(new Vector4(bp.x, bp.y, bp.z, Mathf.Clamp01(pv.z / Mathf.Max(1e-6f, form.height))));
                    SW.Add(Swing(inst, Mathf.Clamp01(pv.z / Mathf.Max(1e-6f, form.height))));
                    N.Add(Vector4.zero);   // unten nach dem Normalen-Rechnen gesetzt
                    M0.Add(Vector4.zero); M1.Add(Vector4.zero);
                    if (near != null)
                    {
                        var c = Closest(b, r.dv, r.dn, wp, near);
                        BW.Add(c.tri >= 0 ? Blend(b, c.tri, c.bary, "haut") : inst.anchor);
                    }
                    else BW.Add(inst.anchor);
                }
                // Wicklung wie die Basis: Vorzeichen des Volumens relativ zum Teil-Mittelpunkt vergleichen
                var cen = inst.m.MultiplyPoint3x4(new Vector3(0, 0, form.height * 0.5f));
                double vol = 0;
                for (int k = 0; k < form.t.Length; k += 3)
                    vol += Vector3.Dot(V[inst.vStart + form.t[k]] - cen, Vector3.Cross(V[inst.vStart + form.t[k + 1]] - cen, V[inst.vStart + form.t[k + 2]] - cen));
                bool flip = Math.Sign(vol) != Math.Sign(b.signedVolumeSign);
                for (int k = 0; k < form.t.Length; k += 3)
                {
                    T.Add(inst.vStart + form.t[k]);
                    T.Add(inst.vStart + form.t[k + (flip ? 2 : 1)]);
                    T.Add(inst.vStart + form.t[k + (flip ? 1 : 2)]);
                }
            }
            var mesh = new Mesh { name = "VariantMesh", indexFormat = V.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16 };
            mesh.SetVertices(V);
            mesh.SetUVs(0, UV0);
            mesh.SetTriangles(T, 0);
            mesh.boneWeights = BW.ToArray();
            mesh.bindposes = b.mesh.bindposes;
            mesh.RecalculateNormals();
            var nn = mesh.normals;
            for (int v = 0; v < nb; v++) if (Vector3.Dot(nn[v], b.normals[v]) < 0) nn[v] = -nn[v];
            mesh.normals = nn;
            for (int v = nb; v < V.Count; v++) { var bn = b.BodyDir(nn[v]); N[v] = new Vector4(bn.x, bn.y, bn.z, 0); }
            mesh.SetUVs(2, G); mesh.SetUVs(3, P); mesh.SetUVs(4, N); mesh.SetUVs(5, M0); mesh.SetUVs(6, M1);
            mesh.SetUVs(1, SW);
            mesh.RecalculateTangents();
            // G14: schwingende Teile tragen ihre Achse (Wurzel → Spitze) in der Tangente – das Skinning dreht sie mit
            var tg = mesh.tangents;
            foreach (var inst in r.instances)
            {
                if (inst.weich <= 0 || inst.vCount <= 0) continue;
                var ax = new Vector4(inst.axis.x, inst.axis.y, inst.axis.z, 1);
                for (int k = 0; k < inst.vCount; k++) tg[inst.vStart + k] = ax;
            }
            mesh.tangents = tg;
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>TEXCOORD1 eines Teil-Vertex: (Beweglichkeit h, Weichheit [+2 Schwerkraft], Slot + Phase, Länge / L).</summary>
        static Vector4 Swing(VkInstance inst, float h)
        {
            if (inst.weich <= 0) return new Vector4(h, 0, 0, 0);
            return new Vector4(Mathf.Clamp01(h), inst.weich + (inst.grav ? 2 : 0), inst.slot + Mathf.Clamp(inst.rand, 0, 0.999f), inst.lenRel);
        }

        /// <summary>Feder-Slot aus dem stärksten Knochen des Ansatzes (VariantSchwingen.SlotFuer).</summary>
        static int SlotOf(VkBase b, BoneWeight w)
        {
            int bi = w.boneIndex0; float bw = w.weight0;
            if (w.weight1 > bw) { bi = w.boneIndex1; bw = w.weight1; }
            if (w.weight2 > bw) { bi = w.boneIndex2; bw = w.weight2; }
            if (w.weight3 > bw) { bi = w.boneIndex3; }
            return bi >= 0 && bi < b.boneNames.Length ? VariantSchwingen.SlotFuer(b.boneNames[bi]) : 0;
        }

        static void AddCoverPart(VkBase b, VkInstance inst, List<float[]> layerMasks, int[] auf, List<Vector3> V, List<Vector2> UV0, List<Vector4> G,
            List<Vector4> P, List<Vector4> N, List<Vector4> M0, List<Vector4> M1, List<BoneWeight> BW, List<int> T)
        {
            inst.vStart = V.Count; inst.vCount = inst.cv.Length;
            int g = VkSpec.GruppeIndex(inst.farbgruppe);
            var am = new float[8];
            // Zonen-Maske am Ansatzpunkt (von der Basis, unabhängig vom Haut-Bit) × Bit der eigenen Lage (2 = Lage 1, 4 = Lage 2)
            int lageBit = 2 << Mathf.Clamp(inst.lage - 1, 0, 1);
            for (int li = 0; li < 8; li++)
                am[li] = li < layerMasks.Count && (auf[li] & lageBit) != 0 ? layerMasks[li][b.tris[inst.tri * 3]] * inst.bary.x + layerMasks[li][b.tris[inst.tri * 3 + 1]] * inst.bary.y + layerMasks[li][b.tris[inst.tri * 3 + 2]] * inst.bary.z : 0;
            inst.layerMask = am;
            for (int k = 0; k < inst.cv.Length; k++)
            {
                V.Add(inst.cv[k]);
                UV0.Add(Vector2.zero);
                G.Add(new Vector4(g, 0, inst.rand, 0));
                P.Add(new Vector4(inst.cb[k].x, inst.cb[k].y, inst.cb[k].z, inst.ch[k]));
                N.Add(Vector4.zero);
                M0.Add(new Vector4(am[0], am[1], am[2], am[3])); M1.Add(new Vector4(am[4], am[5], am[6], am[7]));
                BW.Add(inst.anchor);
            }
            // Wicklung wie die Basis (Blender und Unity spiegeln die Achsen): Vorzeichen des Volumens um den Ansatz prüfen
            var cen = inst.pos;
            double vol = 0;
            for (int k = 0; k < inst.ct.Length; k += 3)
                vol += Vector3.Dot(V[inst.vStart + inst.ct[k]] - cen, Vector3.Cross(V[inst.vStart + inst.ct[k + 1]] - cen, V[inst.vStart + inst.ct[k + 2]] - cen));
            bool flip = Math.Sign(vol) != Math.Sign(b.signedVolumeSign) && Math.Abs(vol) > 1e-12;
            for (int k = 0; k < inst.ct.Length; k += 3)
            {
                T.Add(inst.vStart + inst.ct[k]);
                T.Add(inst.vStart + inst.ct[k + (flip ? 2 : 1)]);
                T.Add(inst.vStart + inst.ct[k + (flip ? 1 : 2)]);
            }
        }

        // ------------------------------------------------------------------ Material (Schicht 4)
        public static Color Hex(string h, Color def)
        {
            if (string.IsNullOrEmpty(h)) return def;
            return ColorUtility.TryParseHtmlString(h, out var c) ? c : def;
        }

        /// <summary>Hex-Farben sind sRGB; im Linear-Farbraum (z. B. später URP) umrechnen, damit die Farbe stimmt.</summary>
        static Vector4 Lin(Color c, float a) { if (QualitySettings.activeColorSpace == ColorSpace.Linear) c = c.linear; return new Vector4(c.r, c.g, c.b, a); }

        static int Idx(string v, params string[] opts) { int i = Array.IndexOf(opts, v); return i < 0 ? 0 : i; }

        public static void ApplyMaterial(Material mat, VkBase b, VkDoc doc, VkBuildResult res)
        {
            var M = doc.resolved.Obj("material");
            mat.SetTexture("_MainTex", b.color);
            if (b.normal != null) mat.SetTexture("_BumpMap", b.normal);
            mat.SetFloat("_Facetten", M.Obj("stil").F("facetten", 1f));
            var fg = M.Obj("farbgruppen");
            var haut = doc.resolved.Obj("bedeckung").O("haut");
            for (int g = 0; g < VkSpec.Gruppen.Length; g++)
            {
                var name = VkSpec.Gruppen[g];
                var o = fg.O(name) ?? new JObj();
                var c = Hex(o.S("farbe", VkSpec.GruppenStdFarbe[name]), Color.gray);
                var c2 = Hex(o.S("farbe_2", null), c);
                float rauh = o.F("rauheit", name == "haut" && haut != null ? haut.F("rauheit", 0.8f) : 0.8f);
                mat.SetVector($"_G{g}C", Lin(c, o.F("leuchten", 0)));
                mat.SetVector($"_G{g}D", Lin(c2, o.F("farb_zufall", 0)));
                mat.SetVector($"_G{g}P", new Vector4(rauh, o.F("detail", 0.5f), o.F("helligkeit_zufall", 0.08f), o.S("verlauf", "keiner") == "ansatz_spitze" ? 1 : 0));
                mat.SetVector($"_G{g}Q", new Vector4(o.F("glasig", 0), 0, 0, 0));
            }
            // Körpermaße (für Verläufe) in Körper/L
            float L = b.L;
            var bys = b.verts.Select(v => b.Body(v) / L).ToArray();
            mat.SetVector("_VKBounds", new Vector4(bys.Min(v => v.y), bys.Max(v => v.y), bys.Min(v => v.x), bys.Max(v => v.x)));
            // Körper-Ebenen (_L0.._L7): Zonen-Maske pro Vertex (TEXCOORD5/6) × Farbgruppen-Bits (nur Körper-Gruppen wirken)
            for (int i = 0; i < VkSpec.MaxEbenen; i++)
            {
                var P = new Vector4[5]; var MM = Vector4.zero;
                if (i < res.ebenen.Count)
                {
                    var e = res.ebenen[i];
                    var mk = e.O("maske") ?? new JObj();
                    int bits = 0;
                    var gr = mk.Strs("gruppen");
                    if (gr.Count == 0) bits = 511; else foreach (var g in gr) bits |= 1 << VkSpec.GruppeIndex(g);
                    MM = new Vector4(e.F("staerke", 1), bits, mk.F("oben", 0), mk.F("rauschen", 0.2f));
                    P = LayerParams(e, doc, i);
                }
                SetLayer(mat, "L", i, P, MM);
            }
            // Accessoire-Ebenen (_A0.._A3): Ziel als Bit-Tabelle über die Eintrags-Nummer (−1 = alle), oben/rauschen pro Pixel
            for (int j = 0; j < VkSpec.MaxAccEbenen; j++)
            {
                var P = new Vector4[5]; var MM = Vector4.zero;
                if (j < res.ebenenAcc.Count)
                {
                    var e = res.ebenenAcc[j];
                    var mk = e.O("maske") ?? new JObj();
                    MM = new Vector4(e.F("staerke", 1), AccBits(e, doc.resolved, res), mk.F("oben", 0), mk.F("rauschen", 0f));
                    P = LayerParams(e, doc, j);
                }
                SetLayer(mat, "A", j, P, MM);
            }
        }

        /// <summary>Bit-Tabelle einer Accessoire-Ebene: −1 = alle Accessoires, sonst Bit n gesetzt = Eintrag n (res.accIds) getroffen.</summary>
        public static float AccBits(JObj e, JObj resolved, VkBuildResult res)
        {
            if (VkSpec.ZielAlle(e)) return -1;
            var accs = VkSpec.AktiveAccessoires(resolved);
            int bits = 0;
            for (int n = 0; n < Mathf.Min(res.accIds.Count, VkSpec.MaxAccEintraege); n++)
            {
                var a = accs.FirstOrDefault(x => x.S("id", "") == res.accIds[n]);
                if (a != null && VkSpec.ZielTrifft(e, a)) bits |= 1 << n;
            }
            return bits;
        }

        static void SetLayer(Material mat, string pre, int i, Vector4[] P, Vector4 M)
        {
            mat.SetVector($"_{pre}{i}T", P[0]); mat.SetVector($"_{pre}{i}C", P[1]); mat.SetVector($"_{pre}{i}D", P[2]);
            mat.SetVector($"_{pre}{i}A", P[3]); mat.SetVector($"_{pre}{i}B", P[4]); mat.SetVector($"_{pre}{i}M", M);
        }

        /// <summary>Werte einer Ebene (gleich für Körper- und Accessoire-Ebenen): T Typ/Art, C Farbe + Intensität, D Farbe B,
        /// A/B Werte. Der Seed hängt an der id → eine Accessoire-Ebene mit derselben id hat dasselbe Muster wie die Körper-Ebene.</summary>
        static Vector4[] LayerParams(JObj e, VkDoc doc, int i)
        {
            var T = Vector4.zero; var C = Vector4.zero; var C2 = Vector4.zero; var A = Vector4.zero; var B = Vector4.zero;
            string typ = e.S("typ", "");
            float seedOff = (Json.Fnv1a($"{doc.resolved.I("seed", 0)}:{e.S("id", typ + "#" + i)}") % 997) * 0.173f;
            if (e["seed"] != null) seedOff = (e.I("seed", 0) % 997) * 0.173f;
            switch (typ)
            {
                case "verlauf":
                    T = new Vector4(1, Idx(e.S("mischung", "ueberlagern"), "multiplizieren", "ueberlagern", "ersetzen"), Idx(e.S("richtung", "oben_unten"), "oben_unten", "vorn_hinten", "ansatz_spitze"), 0);
                    var ca = Hex(e.S("farbe_a", "#FFFFFF"), Color.white); var cb = Hex(e.S("farbe_b", "#808080"), Color.gray);
                    C = Lin(ca, 0); C2 = Lin(cb, 0);
                    A = new Vector4(e.F("mitte", 0.5f), e.F("weichheit", 0.5f), 0, 0);
                    break;
                case "muster":
                    T = new Vector4(2, Idx(e.S("mischung", "ueberlagern"), "multiplizieren", "ueberlagern", "ersetzen"),
                        Idx(e.S("art", "flecken"), "streifen", "flecken", "tupfen", "ringe", "marmor", "zellen"), Idx(e.S("richtung", "quer"), "quer", "laengs", "knochen"));
                    var cm = Hex(e.S("farbe", "#404040"), Color.gray); C = Lin(cm, 0);
                    A = new Vector4(e.F("skala", 0.08f), e.F("dichte", 0.5f), e.F("kontrast", 0.7f), e.F("verzerrung", 0.3f));
                    B = new Vector4(seedOff, 0, 0, 0);
                    break;
                case "risse":
                    var el = VkSpec.Elemente.TryGetValue(e.S("element", "glut"), out var ev) ? ev : ("#FF6A10", 4f);
                    var cr = Hex(e.S("farbe", el.Item1), Color.red);
                    T = new Vector4(3, Idx(e.S("art", "risse"), "risse", "adern", "zellfugen", "runen"), 0, 0);
                    C = Lin(cr, e.F("intensitaet", el.Item2));
                    A = new Vector4(e.F("breite", 0.005f), e.F("dichte", 0.4f), e.F("verzweigung", 0.5f), e.F("hof", 0.3f));
                    B = new Vector4(e.F("puls_frequenz", 0), e.F("puls_staerke", 0), seedOff, 0);
                    break;
                case "ueberzug":
                    var cu = Hex(e.S("farbe", "#A89A88"), Color.gray);
                    T = new Vector4(4, Idx(e.S("art", "staub"), "schmutz", "frost", "asche", "schleim", "staub", "moos"), 0, 0);
                    C = Lin(cu, 0);
                    A = new Vector4(e.F("menge", 0.3f), e.F("kanten", 0.4f), e.F("rauschen_skala", 0.08f), e.F("rauheit", 1f));
                    B = new Vector4(seedOff, 0, 0, 0);
                    break;
                case "naesse":
                    T = new Vector4(5, 0, 0, 0);
                    A = new Vector4(e.F("menge", 0.5f), e.F("glanz", 0.8f), e.F("abdunkeln", 0.3f), 0);
                    break;
                case "rim":
                    var ci = Hex(e.S("farbe", "#FFD080"), Color.white);
                    T = new Vector4(6, 0, 0, 0);
                    C = Lin(ci, e.F("intensitaet", 1.5f));
                    A = new Vector4(e.F("breite", 0.35f), 0, 0, 0);
                    break;
            }
            return new[] { T, C, C2, A, B };
        }

        /// <summary>Rim pro Vertex für das Spiel-Mesh (rgb = Farbe linear wie im Material, a = Breite): Körper-Vertices die
        /// Körper-Rim-Ebene, Accessoire-Vertices die letzte Accessoire-Rim-Ebene, die ihren Eintrag trifft. null = kein Rim.</summary>
        public static Color[] RimColors(List<Vector4> grp, VkDoc doc, VkBuildResult res)
        {
            var bodyRim = res.ebenen.LastOrDefault(e => e.S("typ", "") == "rim");
            var accRims = res.ebenenAcc.Where(e => e.S("typ", "") == "rim").ToList();
            if (bodyRim == null && accRims.Count == 0) return null;
            Color RC(JObj e) { var c = LayerParams(e, doc, 0)[1]; return new Color(c.x, c.y, c.z, e.F("breite", 0.35f)); }
            var bodyC = bodyRim != null ? RC(bodyRim) : new Color(0, 0, 0, 0.35f);
            var accC = new Dictionary<int, Color>();
            var accs = VkSpec.AktiveAccessoires(doc.resolved);
            for (int n = 0; n < res.accIds.Count; n++)
            {
                var a = accs.FirstOrDefault(x => x.S("id", "") == res.accIds[n]);
                var hit = accRims.LastOrDefault(e => (VkSpec.ZielAlle(e) || (n < VkSpec.MaxAccEintraege && a != null && VkSpec.ZielTrifft(e, a))));
                accC[n] = hit != null ? RC(hit) : new Color(0, 0, 0, 0.35f);
            }
            var col = new Color[grp.Count];
            for (int v = 0; v < grp.Count; v++)
            {
                float w = grp[v].w;
                col[v] = w < -0.5f && accC.TryGetValue(Mathf.RoundToInt(-w - 1), out var c) ? c : w < -0.5f ? new Color(0, 0, 0, 0.35f) : bodyC;
            }
            return col;
        }

        // ------------------------------------------------------------------ Statur Typ K/G (Knochen) → VariantStatur
        public static void ConfigureStatur(VariantStatur comp, VkBase b, JObj st, GameObject modelInstance)
        {
            comp.scales.Clear(); comp.stretches.Clear(); comp.offsets.Clear();
            var map = modelInstance.GetComponentsInChildren<Transform>(true).GroupBy(t => t.name).ToDictionary(g => g.Key, g => g.First());
            float g0 = st.F("groesse", 1), bv = st.F("bein_laenge_vorn", 1), bh = st.F("bein_laenge_hinten", 1), pv = st.F("pranken_vorn", 1),
                  ph = st.F("pranken_hinten", 1), kg = st.F("kopf_groesse", 1), sl = st.F("schwanz_laenge", 1), sd = st.F("schwanz_dicke", 1),
                  kl = st.F("koerper_laenge", 1), hl = st.F("hals_laenge", 1), sp = st.F("spur_breite", 1);
            // absolute Größenfaktoren pro Knochen (gleichmäßig), lokal = eigener / Eltern-Faktor (Ausgleich am Kind)
            var own = new Dictionary<string, float> { ["Root"] = g0 };
            foreach (var side in new[] { "FL", "FR" }) { for (int k = 1; k <= 3; k++) own[$"Leg_{side}_{k}"] = bv; own[$"Leg_{side}_4"] = pv; }
            foreach (var side in new[] { "BL", "BR" }) { for (int k = 1; k <= 3; k++) own[$"Leg_{side}_{k}"] = bh; own[$"Leg_{side}_4"] = ph; }
            own["Head"] = kg;
            for (int k = 1; k <= 4; k++) own[$"Tail_{k}"] = sl;
            float Abs(Transform t)
            {
                if (t == null || t == modelInstance.transform) return 1;
                float parent = Abs(t.parent);
                if (t.name == "Root") return own["Root"];
                return own.TryGetValue(t.name, out var f) ? g0 * f : parent;
            }
            foreach (var t in map.Values)
            {
                if (!b.boneIndex.ContainsKey(t.name)) continue;
                float local = Abs(t) / Abs(t.parent);
                var ls = Vector3.one * local;
                if (t.name == "Tail_1" && !Mathf.Approximately(sd, 1))
                {
                    var c = map.TryGetValue("Tail_2", out var c2) ? c2.localPosition.normalized : Vector3.up;
                    var ax = new Vector3(Mathf.Abs(c.x), Mathf.Abs(c.y), Mathf.Abs(c.z));
                    ls = Vector3.Scale(ls, new Vector3(ax.x > 0.7f ? 1 : sd, ax.y > 0.7f ? 1 : sd, ax.z > 0.7f ? 1 : sd));
                }
                if ((ls - Vector3.one).sqrMagnitude > 1e-8f) comp.scales.Add(new VariantStatur.BoneScale { bone = t.name, localScale = ls });
            }
            // Rumpf/Hals länger: Kinder entlang der Knochenachse verschieben (ohne dicker zu werden)
            void Stretch(string parent, float f)
            {
                if (Mathf.Approximately(f, 1) || !map.TryGetValue(parent, out var p)) return;
                var cc = map.TryGetValue(ChainChild(parent) ?? "", out var cct) ? cct : null;
                if (cc == null) return;
                var axis = cc.localPosition.normalized;
                foreach (Transform ch in p) if (b.boneIndex.ContainsKey(ch.name))
                        comp.stretches.Add(new VariantStatur.BoneStretch { bone = ch.name, parentAxis = axis, factor = f });
            }
            Stretch("Spine_1", kl); Stretch("Chest", kl); Stretch("Neck_1", hl); Stretch("Neck_2", hl);
            // Spurbreite + Bodenhöhe (Modell-Raum)
            var toModel = b.model.transform.worldToLocalMatrix * b.smr.transform.localToWorldMatrix;
            var leftM = toModel.MultiplyVector(b.left).normalized;
            var upM = toModel.MultiplyVector(b.up).normalized;
            float m2m = b.meshToMeter;
            if (!Mathf.Approximately(sp, 1))
                foreach (var (bone, sign) in new[] { ("Shoulder_FL", 1f), ("Shoulder_FR", -1f), ("Leg_BL_1", 1f), ("Leg_BR_1", -1f) })
                {
                    int bi = b.Bone(bone); if (bi < 0) continue;
                    float half = Mathf.Abs(b.Body(b.boneHead[bi]).z) * m2m;
                    comp.offsets.Add(new VariantStatur.BoneOffset { bone = bone, modelOffset = leftM * sign * (sp - 1) * half * g0 });
                }
            float ground = b.verts.Min(v => b.Body(v).y);
            float H(string bone) { int bi = b.Bone(bone); return bi < 0 ? 0 : (b.Body(b.boneHead[bi]).y - ground) * m2m; }
            float lift = 0.5f * ((bv - 1) * H("Leg_FL_1") + (pv - 1) * H("Leg_FL_4") * 0.6f + (bh - 1) * H("Leg_BL_1") + (ph - 1) * H("Leg_BL_4") * 0.6f) * g0;
            if (Mathf.Abs(lift) > 1e-5f) comp.offsets.Add(new VariantStatur.BoneOffset { bone = "Hips", modelOffset = upM * lift });
            comp.Bind();
        }

        static string ChainChild(string bone)
        {
            switch (bone) { case "Spine_1": return "Chest"; case "Chest": return "Neck_1"; case "Neck_1": return "Neck_2"; case "Neck_2": return "Head"; }
            return null;
        }

        // ------------------------------------------------------------------ Ruhepose (Bindepose) auf eine Instanz legen
        public static void RestPose(GameObject inst)
        {
            var smr = inst.GetComponentInChildren<SkinnedMeshRenderer>();
            var bp = smr.sharedMesh.bindposes;
            var l2w = smr.transform.localToWorldMatrix;
            int Depth(Transform t) { int d = 0; while (t != null) { d++; t = t.parent; } return d; }
            foreach (var bt in smr.bones) if (bt != null) bt.localScale = Vector3.one;   // Bindepose hat keine Statur-Skalierung (sonst hängt das Ergebnis vom Vorzustand ab)
            foreach (int i in Enumerable.Range(0, smr.bones.Length).OrderBy(i => Depth(smr.bones[i])))   // Eltern zuerst
            {
                var m = l2w * bp[i].inverse;
                smr.bones[i].SetPositionAndRotation(m.GetColumn(3), m.rotation);
            }
        }
    }
}
