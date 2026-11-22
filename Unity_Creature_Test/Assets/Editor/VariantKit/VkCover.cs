using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Schicht 2 „Bedeckung“ (Spec 2.1–2.4): Ergebnis aus Blender (&lt;ExportName&gt;.bedeckung.json, gebaut von
    /// procedural/variantkit_blender, Knopf „In Blender bauen“). Unity rechnet die Lagen NICHT selbst (Spec 0.4) – es setzt nur
    /// die fertigen Teile auf die Basis: Koordinaten im Körperraum (achsen-unabhängig), Gewichte nach Knochennamen, Statur S
    /// über den Versatz des Ansatzpunkts (Teil wandert mit, verformt sich nicht).</summary>
    public class VkCover
    {
        public class Part
        {
            public int lage; public string farbgruppe; public float rand;
            public Vector3 anchorBody;       // Körperraum / L
            public int tri; public Vector3 bary;   // Ansatz auf der (unverformten) Basis
            public BoneWeight weights;
            public int v0, nv;
        }

        public string path;
        public DateTime stamp;
        public JObj quelle;
        public long revision;
        public string werkzeug;
        public Vector3[] body;      // Vertices im Körperraum / L (Ruhe, ohne Statur)
        public float[] h;           // 0 = Ansatz … 1 = Spitze
        public int[] tris;          // Indizes in body (global)
        public List<Part> parts = new List<Part>();
        public int trisTotal;
        public Dictionary<int, int> trisPerLage = new Dictionary<int, int>();

        static readonly Dictionary<string, VkCover> cache = new Dictionary<string, VkCover>();

        public static string PathFor(VkDoc doc)
        {
            var creatureDir = Path.GetDirectoryName(Path.GetDirectoryName(doc.path));
            return Path.Combine(creatureDir, "output", "varianten", doc.ExportName, doc.ExportName + ".bedeckung.json");
        }

        public static bool HasLayers(VkDoc doc) =>
            doc.resolved.Obj("bedeckung").List("lagen").OfType<JObj>().Any(l => l.B("an", true));

        /// <summary>Bedeckung der Variante laden (gecacht nach Datei-Zeitstempel). null = noch nie gebaut.</summary>
        public static VkCover Get(VkBase b, VkDoc doc)
        {
            var p = PathFor(doc);
            if (!File.Exists(p)) return null;
            var t = File.GetLastWriteTimeUtc(p);
            string key = b.id + "|" + p;
            if (cache.TryGetValue(key, out var c) && c.stamp == t) return c;
            c = Load(b, p);
            c.stamp = t;
            cache[key] = c;
            return c;
        }

        public static void Invalidate() => cache.Clear();

        /// <summary>Stimmt die gebaute Bedeckung noch mit der Varianten-Datei überein (Lagen + Seed)?</summary>
        public bool Fresh(VkDoc doc) =>
            quelle != null && Json.Same(quelle["bedeckung"], doc.resolved["bedeckung"]) && quelle.I("seed", -1) == doc.resolved.I("seed", 0);

        static VkCover Load(VkBase b, string path)
        {
            var j = Json.ParseObj(File.ReadAllText(path));
            var c = new VkCover { path = path, quelle = j.O("quelle"), revision = j.I("revision", 0), werkzeug = j.S("werkzeug", "?") };
            var vs = j.L("vertices") ?? new List<object>();
            c.body = new Vector3[vs.Count / 3];
            for (int i = 0; i < c.body.Length; i++)
                c.body[i] = new Vector3(Json.ToF(vs[i * 3], 0), Json.ToF(vs[i * 3 + 1], 0), Json.ToF(vs[i * 3 + 2], 0));
            c.h = (j.L("h") ?? new List<object>()).Select(x => Json.ToF(x, 0)).ToArray();
            if (c.h.Length != c.body.Length) c.h = new float[c.body.Length];
            c.tris = (j.L("dreiecke") ?? new List<object>()).Select(x => (int)Json.ToF(x, 0)).ToArray();
            c.trisTotal = c.tris.Length / 3;
            // Ansatzpunkte einmal auf die Basis (unverformt) legen → Statur-Versatz + Masken der Material-Ebenen
            foreach (JObj t in (j.L("teile") ?? new List<object>()).OfType<JObj>())
            {
                var a = t.Vec("anker", new[] { 0f, 0f, 0f });
                var part = new Part
                {
                    lage = t.I("lage", 1), farbgruppe = t.S("farbgruppe", "bedeckung_1"), rand = t.F("zufall", 0.5f),
                    anchorBody = new Vector3(a[0], a[1], a[2]), v0 = t.I("v0", 0), nv = t.I("nv", 0),
                };
                var cl = VkBuilder.Closest(b, b.verts, b.normals, b.FromBody(part.anchorBody * b.L));
                part.tri = Mathf.Max(0, cl.tri); part.bary = cl.tri >= 0 ? cl.bary : new Vector3(1, 0, 0);
                part.weights = Weights(b, t.O("gewichte"), part.tri, part.bary);
                c.parts.Add(part);
            }
            foreach (var part in c.parts)
            {
                int n = 0;
                for (int k = 0; k < c.tris.Length; k += 3) if (c.tris[k] >= part.v0 && c.tris[k] < part.v0 + part.nv) n++;
                c.trisPerLage.TryGetValue(part.lage, out var o); c.trisPerLage[part.lage] = o + n;
            }
            return c;
        }

        /// <summary>Gewichte nach Knochennamen (aus Blender, höchstens 4); fehlt ein Knochen → Gewichte der Haut am Ansatz.</summary>
        static BoneWeight Weights(VkBase b, JObj w, int tri, Vector3 bary)
        {
            var list = new List<(int bone, float w)>();
            if (w != null) foreach (var kv in w) { int bi = b.Bone(kv.Key); if (bi >= 0) list.Add((bi, Json.ToF(kv.Value, 0))); }
            if (list.Count == 0 || list.Sum(x => x.w) < 1e-4f) return VkBuilder.Blend(b, tri, bary, "anker");
            list = list.OrderByDescending(x => x.w).Take(4).ToList();
            float s = list.Sum(x => x.w);
            var r = new BoneWeight();
            for (int i = 0; i < list.Count; i++)
            {
                float v = list[i].w / s;
                switch (i)
                {
                    case 0: r.boneIndex0 = list[i].bone; r.weight0 = v; break;
                    case 1: r.boneIndex1 = list[i].bone; r.weight1 = v; break;
                    case 2: r.boneIndex2 = list[i].bone; r.weight2 = v; break;
                    case 3: r.boneIndex3 = list[i].bone; r.weight3 = v; break;
                }
            }
            return r;
        }
    }
}
