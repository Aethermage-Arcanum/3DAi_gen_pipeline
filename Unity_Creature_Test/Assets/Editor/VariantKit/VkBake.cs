using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Import-Einstellungen nur für die Basis-Kopien des Baukastens (Assets/VariantKit/Generated/Bases):
    /// Generic-Rig, Animation unkomprimiert, Mesh LESBAR (der Baukasten rechnet auf den Vertices). Der CreatureImporter
    /// (Assets/Creatures) bleibt davon unberührt.</summary>
    public class VkImport : AssetPostprocessor
    {
        bool Ours => assetPath.StartsWith(VkBase.BasesDir + "/") && assetPath.EndsWith(".fbx");

        void OnPreprocessModel()
        {
            if (!Ours) return;
            var mi = (ModelImporter)assetImporter;
            mi.animationType = ModelImporterAnimationType.Generic;
            mi.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            mi.importAnimation = true;
            mi.animationCompression = ModelImporterAnimationCompression.Off;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            mi.isReadable = true;
            mi.importCameras = false;
            mi.importLights = false;
        }

        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(VkBase.BasesDir + "/")) return;
            if (Path.GetFileName(assetPath).StartsWith("Normal")) ((TextureImporter)assetImporter).textureType = TextureImporterType.NormalMap;
        }
    }

    public class VkBakeResult
    {
        public string prefabPath, meshPath, materialPath, instancesPath;
        public int trisBase, trisAcc, tris, materials, bones, texSize;
        public List<string> textures = new List<string>();
        public VkSpec.Ampel staturAmpel, budgetAmpel;
        public List<string> warnings = new List<string>();
        public VkBuildResult build;
    }

    /// <summary>„Backen“ (Spec 6.3, Meilenstein 1 komplett in Unity): Prefab mit 1 SkinnedMeshRenderer (Körper +
    /// Accessoires mit Gewichten vom Ansatzpunkt) und 1 Material. Schreibt Instanzen-Liste und _gebaut in die Varianten-Datei.</summary>
    public static class VkBake
    {
        public const string BakedDir = "Assets/VariantKit/Baked";
        public const string ShaderName = "VariantKit/Layered";

        static T Store<T>(T obj, string path) where T : UnityEngine.Object
        {
            var existing = AssetDatabase.LoadAssetAtPath<T>(path);
            if (existing == null) { AssetDatabase.CreateAsset(obj, path); return obj; }
            EditorUtility.CopySerialized(obj, existing);
            existing.name = Path.GetFileNameWithoutExtension(path);
            EditorUtility.SetDirty(existing);
            return existing;
        }

        public static VkBakeResult Bake(VkBase b, VkDoc doc)
        {
            var res = VkBuilder.Build(b, doc);
            var r = new VkBakeResult { warnings = res.warnings, build = res };
            string name = doc.ExportName, dir = $"{BakedDir}/{name}";
            Directory.CreateDirectory(dir);
            AssetDatabase.Refresh();

            res.mesh.name = name;
            var mesh = Store(res.mesh, r.meshPath = $"{dir}/{name}_mesh.asset");
            var mat = new Material(Shader.Find(ShaderName)) { name = name };
            VkBuilder.ApplyMaterial(mat, b, doc, res);
            mat = Store(mat, r.materialPath = $"{dir}/{name}.mat");

            var root = new GameObject(name);
            var model = (GameObject)PrefabUtility.InstantiatePrefab(b.model);
            PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            model.name = b.name;
            model.transform.SetParent(root.transform, false);
            model.transform.localPosition = new Vector3(0, -b.restMinY, 0);
            var smr = model.GetComponentInChildren<SkinnedMeshRenderer>();
            var lb = smr.localBounds; lb.Expand(b.L * b.meshToMeter * 0.5f); smr.localBounds = lb;
            smr.sharedMesh = mesh;
            smr.sharedMaterials = new[] { mat };
            var st = model.AddComponent<VariantStatur>();
            VkBuilder.ConfigureStatur(st, b, doc.resolved.Obj("statur"), model);
            if (st.scales.Count + st.stretches.Count + st.offsets.Count == 0) UnityEngine.Object.DestroyImmediate(st);
            r.prefabPath = $"{dir}/{name}.prefab";
            r.bones = smr.bones.Length;
            PrefabUtility.SaveAsPrefabAsset(root, r.prefabPath);
            UnityEngine.Object.DestroyImmediate(root);

            // Kennzahlen + Budget (E5)
            r.trisBase = res.trisBase; r.trisAcc = res.trisAcc; r.tris = mesh.triangles.Length / 3;
            r.materials = 1;
            foreach (var t in new[] { b.color, b.normal }.Where(t => t != null)) { r.textures.Add($"{t.name} {t.width}²"); r.texSize = Mathf.Max(r.texSize, t.width); }
            var bud = VkSpec.BudgetFuer(doc.resolved.S("budget_klasse", "normal"));
            r.budgetAmpel = r.tris > bud.tris || r.trisAcc > bud.accessoires || r.texSize > bud.textur ? VkSpec.Ampel.Rot : VkSpec.Ampel.Gruen;
            r.staturAmpel = VkSpec.StaturAmpel(doc.resolved.Obj("statur"), out _);

            // Instanzen-Liste (abgeleitet, Spec 3.3) + _gebaut
            r.instancesPath = doc.InstancesPath;
            WriteInstances(b, doc, res, r.instancesPath);
            var parts = VkParts.Types().ToDictionary(t => t, t => Json.ParseObj(File.ReadAllText(Path.Combine(VkParts.Dir, t + ".json"))).S("version", "?"));
            doc.resolved["_gebaut"] = new JObj
            {
                ["quell_hash"] = doc.SourceHash(),
                ["datum"] = DateTime.Now.ToString("yyyy-MM-ddTHH:mm:ss"),
                ["werkzeuge"] = new JObj { ["unity_varianten"] = VkSpec.ToolVersion, ["bausteine"] = parts.Values.Distinct().FirstOrDefault() ?? "-", ["zonen"] = "1" },
                ["tris"] = new JObj { ["basis"] = (long)r.trisBase, ["bedeckung"] = 0L, ["accessoires"] = (long)r.trisAcc, ["gesamt"] = (long)r.tris },
                ["materialien"] = (long)r.materials,
                ["texturen"] = (long)r.texSize,
                ["statur_ampel"] = r.staturAmpel == VkSpec.Ampel.Gruen ? "gruen" : r.staturAmpel == VkSpec.Ampel.Gelb ? "gelb" : "rot",
                ["budget_ampel"] = r.budgetAmpel == VkSpec.Ampel.Gruen ? "gruen" : "rot",
                ["dateien"] = new List<object> { "Unity_Creature_Test/" + r.prefabPath },
            };
            var err = doc.Save();
            if (err != null) r.warnings.Add("Varianten-Datei nicht gespeichert: " + err);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"[VariantKit] GEBACKEN {name}: {r.tris} Tris (Basis {r.trisBase} + Accessoires {r.trisAcc}), 1 Material, " +
                      $"Texturen {string.Join(", ", r.textures)}, {r.bones} Knochen, Statur {r.staturAmpel}, Budget {r.budgetAmpel} → {r.prefabPath}");
            return r;
        }

        /// <summary>&lt;id&gt;.instanzen.json: Meter im Raum der Basis-FBX (x vorn, y links, z oben = Blender-Objektraum),
        /// Ursprung = Ursprung des Meshes. Matrix-Spalten = Baustein-Achsen (X Länge, Y Breite, Z Höhe) inkl. Größe.</summary>
        static void WriteInstances(VkBase b, VkDoc doc, VkBuildResult res, string path)
        {
            float s = b.meshToMeter;
            List<object> V(Vector3 v) => new List<object> { (double)Vector3.Dot(v, b.fwd) * s, (double)Vector3.Dot(v, b.left) * s, (double)Vector3.Dot(v, b.up) * s };
            var list = new List<object>();
            foreach (var i in res.instances)
            {
                var w = i.anchor;
                var anker = new JObj();
                void A(int bi, float wt) { if (wt > 0) anker[b.boneNames[bi]] = (double)wt; }
                A(w.boneIndex0, w.weight0); A(w.boneIndex1, w.weight1); A(w.boneIndex2, w.weight2); A(w.boneIndex3, w.weight3);
                list.Add(new JObj
                {
                    ["accessoire"] = i.acc, ["typ"] = i.typ, ["form"] = i.form, ["zone"] = i.zone, ["gespiegelt"] = i.mirrored,
                    ["position"] = V(i.m.GetColumn(3)), ["achse_x"] = V(i.m.GetColumn(0)), ["achse_y"] = V(i.m.GetColumn(1)), ["achse_z"] = V(i.m.GetColumn(2)),
                    ["ansatz"] = V(i.pos), ["bindung"] = i.bindung, ["anker_gewichte"] = anker, ["farbgruppe"] = i.farbgruppe, ["zufall"] = (double)i.rand,
                });
            }
            var o = new JObj
            {
                ["format"] = "kreatur_instanzen", ["format_version"] = 1L, ["variante"] = doc.Id, ["basis"] = b.id,
                ["quell_hash"] = doc.SourceHash(), ["werkzeug"] = VkSpec.ToolVersion,
                ["koordinaten"] = "Meter, Raum der Basis-FBX: x vorn, y links, z oben (wie Blender), Ursprung = Mesh-Ursprung",
                ["instanzen"] = list,
            };
            File.WriteAllText(path, Json.Write(o), new System.Text.UTF8Encoding(false));
        }
    }
}
