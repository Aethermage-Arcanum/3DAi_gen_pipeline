using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace VariantKit
{
    /// <summary>Menü „Kreaturen › Varianten-Baukasten“: Varianten-Datei laden/anlegen/speichern, Statur, Material-Ebenen und
    /// Accessoires live einstellen (Vorschau mit laufendem Clip, ARPG-Kamera), Kennzahlen + Budget, „Backen“.</summary>
    public class VariantKitWindow : EditorWindow
    {
        [MenuItem("Kreaturen/Varianten-Baukasten")]
        public static void Open() => GetWindow<VariantKitWindow>("Varianten-Baukasten").minSize = new Vector2(460, 600);

        // ---- Zustand
        List<VkBase.Info> bases = new List<VkBase.Info>();
        int baseIdx;
        VkBase cur;
        List<string> files = new List<string>();
        int fileIdx;
        VkDoc doc;
        VkBuildResult res;
        string status = "", error;
        bool rebuild;
        double lastChange;

        // ---- Vorschau
        PreviewRenderUtility pru;
        GameObject inst, ground;
        Material mat;
        VariantStatur statur;
        VariantSchwingen schwingen;   // G14: Nachschwingen in der Vorschau (von Hand getaktet)
        bool swingOn = true;
        float swingTime = -1, swingClipT;
        int swingClip = -1;
        static readonly string[] ClipLabels = { "Ruhe", "Walk", "Idle", "Run", "Attack1", "Attack2" };
        int clipIdx = 1;
        float time, speed = 1f;
        bool playing = true;
        Vector2 view = VkBatch.ViewArpg;
        float zoom = 2.3f;
        double lastTick;

        // ---- Oberfläche
        Vector2 scroll;
        int tab;
        static readonly string[] Tabs = { "Statur", "Material", "Accessoires", "Datei & Kennzahlen" };
        readonly Dictionary<string, bool> fold = new Dictionary<string, bool>();
        string newId = "neue_variante", newName = "Neue Variante";
        int newPreset;
        string addAccTyp = "basaltbrocken";
        int addLayerTyp = 2, addAccLayerTyp = 3;
        VkBlenderJob job;          // „In Blender bauen“ (läuft im Hintergrund)

        void OnEnable()
        {
            bases = VkBase.List();
            EditorApplication.update += Tick;
            if (bases.Count > 0) SelectBase(Mathf.Clamp(baseIdx, 0, bases.Count - 1));
        }

        void OnDisable()
        {
            EditorApplication.update -= Tick;
            Cleanup();
        }

        void Cleanup()
        {
            if (inst != null) DestroyImmediate(inst);
            if (ground != null) DestroyImmediate(ground);
            if (mat != null) DestroyImmediate(mat);
            if (res?.mesh != null) DestroyImmediate(res.mesh);
            pru?.Cleanup();
            pru = null;
        }

        void Tick()
        {
            double now = EditorApplication.timeSinceStartup;
            float dt = (float)(now - lastTick);
            if (dt < 1f / 30f) return;
            lastTick = now;
            if (playing) time += Mathf.Min(dt, 0.1f) * speed;
            if (job != null && !job.done && job.Poll() && job.done) BlenderFinished();
            if (rebuild && now - lastChange > 0.12) Rebuild();
            Repaint();
        }

        // ------------------------------------------------------------------ Laden / Bauen
        void SelectBase(int i)
        {
            baseIdx = i;
            error = null;
            try
            {
                cur = VkBase.Load(bases[i].id);
                RefreshFiles();
                if (files.Count > 0) LoadFile(Mathf.Clamp(fileIdx, 0, files.Count - 1)); else { doc = null; SetupPreview(); }
            }
            catch (Exception ex) { error = ex.Message; Debug.LogException(ex); }
        }

        void RefreshFiles()
        {
            var dir = VkDoc.VariantDir(bases[baseIdx].dir);
            files = Directory.Exists(dir) ? Directory.GetFiles(dir, "*.variant.json").OrderBy(x => x).ToList() : new List<string>();
        }

        void LoadFile(int i)
        {
            fileIdx = i;
            try { doc = VkDoc.Load(files[i]); status = $"Geladen: {Path.GetFileName(files[i])} (Revision {doc.loadedRevision})"; }
            catch (Exception ex) { error = "Datei unlesbar: " + ex.Message; doc = null; }
            SetupPreview();
        }

        void SetupPreview()
        {
            Cleanup();
            if (cur == null) return;
            pru = new PreviewRenderUtility();
            pru.camera.fieldOfView = 30f;
            pru.camera.clearFlags = CameraClearFlags.SolidColor;
            pru.camera.backgroundColor = new Color(0.32f, 0.33f, 0.35f);
            pru.camera.farClipPlane = 100f;
            pru.lights[0].intensity = 1.25f;
            pru.lights[0].transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            pru.lights[1].intensity = 0.55f;
            pru.lights[1].transform.rotation = Quaternion.Euler(-20f, 160f, 0f);
            pru.ambientColor = new Color(0.38f, 0.38f, 0.38f);
            inst = Instantiate(cur.model);
            inst.hideFlags = HideFlags.HideAndDontSave;
            inst.transform.position = new Vector3(0, -cur.restMinY, 0);
            statur = inst.AddComponent<VariantStatur>();
            schwingen = inst.AddComponent<VariantSchwingen>();
            schwingen.manuell = true;
            pru.AddSingleGO(inst);
            ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.hideFlags = HideFlags.HideAndDontSave;
            ground.transform.localScale = Vector3.one * 0.6f;
            var gm = new Material(Shader.Find("Standard")) { color = new Color(0.26f, 0.26f, 0.27f), hideFlags = HideFlags.HideAndDontSave };
            ground.GetComponent<Renderer>().sharedMaterial = gm;
            pru.AddSingleGO(ground);
            var sh = Shader.Find(VkBake.ShaderName);
            if (sh == null)
            {
                Cleanup();
                // z. B. beim Editor-Start vor dem Import oder bei einem Syntaxfehler im Shader: verständlich melden statt Null-Exception.
                // Die Varianten-Datei bleibt geladen (Regler, Speichern), nur die Vorschau fehlt; „Neu laden“ versucht es erneut.
                error = $"Vorschau-Shader „{VkBake.ShaderName}“ nicht gefunden (noch nicht importiert oder Shader-Fehler, siehe Console). " +
                        "Die Datei ist geladen, nur die Vorschau fehlt. Nach dem Import „Laden“ drücken.";
                return;
            }
            mat = new Material(sh) { hideFlags = HideFlags.HideAndDontSave };
            Rebuild();
        }

        void Changed() { if (doc != null) doc.dirty = true; rebuild = true; lastChange = EditorApplication.timeSinceStartup; }

        void Rebuild()
        {
            rebuild = false;
            if (cur == null || inst == null || doc == null || mat == null) return;
            try
            {
                var old = res?.mesh;
                res = VkBuilder.Build(cur, doc);
                var smr = inst.GetComponentInChildren<SkinnedMeshRenderer>();
                smr.sharedMesh = res.mesh;
                VkBuilder.ApplyMaterial(mat, cur, doc, res);
                smr.sharedMaterials = new[] { mat };
                var lb = cur.smr.localBounds; lb.Expand(cur.L * cur.meshToMeter * 0.6f); smr.localBounds = lb;
                VkBuilder.ConfigureStatur(statur, cur, doc.resolved.Obj("statur"), inst);
                VkBake.ConfigureSchwingen(schwingen, cur, inst, true);
                schwingen.manuell = true;
                if (old != null) DestroyImmediate(old);
                error = null;
            }
            catch (Exception ex) { error = ex.Message; Debug.LogException(ex); }
        }

        // ------------------------------------------------------------------ Oberfläche
        void OnGUI()
        {
            if (bases.Count == 0)
            {
                EditorGUILayout.HelpBox("Keine Basis-Kreatur gefunden (creatures/*/creature.toml mit bodyplan \"quadruped\" und output/*.fbx).", MessageType.Warning);
                if (GUILayout.Button("Neu suchen")) OnEnable();
                return;
            }
            Header();
            if (error != null) EditorGUILayout.HelpBox(error, MessageType.Error);
            if (doc == null) { NewVariantBox(); return; }
            DrawPreview();
            tab = GUILayout.Toolbar(tab, Tabs);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            switch (tab)
            {
                case 0: StaturTab(); break;
                case 1: MaterialTab(); break;
                case 2: AccTab(); break;
                case 3: FileTab(); break;
            }
            EditorGUILayout.EndScrollView();
        }

        void Header()
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Basis", GUILayout.Width(50));
                int nb = EditorGUILayout.Popup(baseIdx, bases.Select(b => $"{b.name} ({Path.GetFileName(b.dir)})").ToArray());
                if (nb != baseIdx && ConfirmDiscard()) SelectBase(nb);
            }
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Variante", GUILayout.Width(50));
                if (files.Count > 0)
                {
                    int nf = EditorGUILayout.Popup(fileIdx, files.Select(f => Path.GetFileName(f) + (doc != null && doc.dirty && f == doc.path ? " *" : "")).ToArray());
                    if (nf != fileIdx && ConfirmDiscard()) LoadFile(nf);
                }
                else EditorGUILayout.LabelField("(noch keine Varianten-Datei)");
                if (GUILayout.Button("Laden", GUILayout.Width(52)) && files.Count > 0 && ConfirmDiscard()) { RefreshFiles(); LoadFile(Mathf.Min(fileIdx, files.Count - 1)); }
                if (GUILayout.Button("Neu", GUILayout.Width(40)) && ConfirmDiscard()) { doc = null; Cleanup(); }
                GUI.enabled = doc != null;
                if (GUILayout.Button(doc != null && doc.dirty ? "Speichern *" : "Speichern", GUILayout.Width(82))) Save();
                GUI.enabled = true;
            }
            if (doc != null)
            {
                using (new EditorGUILayout.HorizontalScope())
                {
                    var bud = VkSpec.BudgetFuer(doc.resolved.S("budget_klasse", "normal"));
                    int tris = res?.mesh != null ? res.mesh.triangles.Length / 3 : 0;
                    var a = VkSpec.StaturAmpel(doc.resolved.Obj("statur"), out _);
                    Lamp(a); GUILayout.Label("Statur", GUILayout.Width(40));
                    Lamp(tris > bud.tris || (res?.trisAcc ?? 0) > bud.accessoires || (res?.trisCover ?? 0) > bud.bedeckung ? VkSpec.Ampel.Rot : VkSpec.Ampel.Gruen);
                    GUILayout.Label($"Budget: {tris:N0} / {bud.tris:N0} Tris · 1 Material", GUILayout.ExpandWidth(true));
                    GUI.enabled = job == null || job.done;
                    GUI.backgroundColor = new Color(0.6f, 0.8f, 1f);
                    if (GUILayout.Button(new GUIContent("In Blender bauen", "Speichert die Datei, baut die Bedeckung (Fell, Stacheln, Platten) in Blender und lädt sie automatisch"), GUILayout.Width(118), GUILayout.Height(20))) BuildInBlender();
                    GUI.backgroundColor = new Color(1f, 0.85f, 0.5f);
                    if (GUILayout.Button("Backen", GUILayout.Width(70), GUILayout.Height(20))) Bake();
                    GUI.backgroundColor = Color.white;
                    GUI.enabled = true;
                }
                CoverStatus();
                if (!string.IsNullOrEmpty(status)) EditorGUILayout.LabelField(status, EditorStyles.miniLabel);
            }
        }

        void CoverStatus()
        {
            if (job != null && !job.done)
            {
                using (new EditorGUILayout.HorizontalScope())
                {
                    var r = GUILayoutUtility.GetRect(100, 18, GUILayout.ExpandWidth(true));
                    EditorGUI.ProgressBar(r, job.progress, $"Blender: {job.text} ({(DateTime.Now - job.started).TotalSeconds:0} s)");
                    if (GUILayout.Button("Abbrechen", GUILayout.Width(80))) { job.Cancel(); status = "Blender abgebrochen"; }
                }
                return;
            }
            if (job != null && job.done && !job.ok)
                EditorGUILayout.HelpBox("„In Blender bauen“ fehlgeschlagen: " + job.error + "\nLog: " + job.LogPath(), MessageType.Error);
            if (res == null || !res.coverWanted) return;
            if (res.cover == null) EditorGUILayout.HelpBox("Bedeckung noch nicht gebaut – „In Blender bauen“ drücken.", MessageType.Info);
            else if (!res.coverFresh) EditorGUILayout.HelpBox("Bedeckung veraltet (Lagen in der Datei geändert) – „In Blender bauen“.", MessageType.Warning);
            else EditorGUILayout.LabelField($"Bedeckung: {res.trisCover:N0} Tris ({string.Join(", ", res.trisCoverLage.Select(kv => $"Lage {kv.Key}: {kv.Value:N0}"))}) · aus Blender", EditorStyles.miniLabel);
        }

        /// <summary>„In Blender bauen“: Datei + Instanzen-Liste speichern → Blender headless baut die Bedeckung → Auto-Import.</summary>
        void BuildInBlender()
        {
            if (doc.dirty || !File.Exists(doc.path))
            {
                var err = doc.Save();
                if (err != null)
                {
                    if (!EditorUtility.DisplayDialog("Datei geändert", err + "\n\nTrotzdem überschreiben?", "Überschreiben", "Abbrechen")) return;
                    doc.Save(true);
                }
                RefreshFiles();
                fileIdx = Mathf.Max(0, files.IndexOf(doc.path));
            }
            try { if (res != null) VkBake.WriteInstances(cur, doc, res, doc.InstancesPath); }
            catch (Exception ex) { Debug.LogWarning("[VariantKit] Instanzen-Liste: " + ex.Message); }
            job = VkBlenderJob.Start(doc.path);
            status = job.done ? "Blender: " + job.error : "Blender baut die Bedeckung …";
        }

        void BlenderFinished()
        {
            if (job.ok)
            {
                VkCover.Invalidate();
                status = $"Bedeckung aus Blender geladen ({job.info})";
                Rebuild();
            }
            else status = "Blender-Fehler: " + job.error;
            Repaint();
        }

        bool ConfirmDiscard() => doc == null || !doc.dirty ||
            EditorUtility.DisplayDialog("Ungespeicherte Änderungen", $"{doc.Id} hat ungespeicherte Änderungen. Verwerfen?", "Verwerfen", "Abbrechen");

        void Save()
        {
            var err = doc.Save();
            if (err != null && EditorUtility.DisplayDialog("Datei geändert", err + "\n\nTrotzdem überschreiben?", "Überschreiben", "Abbrechen")) err = doc.Save(true);
            status = err ?? $"Gespeichert: {Path.GetFileName(doc.path)} (Revision {doc.loadedRevision})";
            RefreshFiles();
            fileIdx = Mathf.Max(0, files.IndexOf(doc.path));
        }

        void Bake()
        {
            try
            {
                EditorUtility.DisplayProgressBar("Backen", doc.Id, 0.5f);
                var r = VkBake.Bake(cur, doc);
                status = $"Gebacken: {r.prefabPath} · {r.tris} Tris · 1 Material" + (r.warnings.Count > 0 ? " · " + string.Join("; ", r.warnings) : "");
                EditorGUIUtility.PingObject(AssetDatabase.LoadAssetAtPath<GameObject>(r.prefabPath));
                RefreshFiles();
            }
            catch (Exception ex) { error = "Backen fehlgeschlagen: " + ex.Message; Debug.LogException(ex); }
            finally { EditorUtility.ClearProgressBar(); }
        }

        void NewVariantBox()
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Neue Variante anlegen", EditorStyles.boldLabel);
            newId = EditorGUILayout.TextField("ID (snake_case)", newId);
            newName = EditorGUILayout.TextField("Name", newName);
            var presets = VkDoc.Presets();
            presets.Insert(0, "(kein Preset)");
            newPreset = EditorGUILayout.Popup("Umgebungs-Gruppe", newPreset, presets.Select(PresetLabel).ToArray());
            if (GUILayout.Button("Anlegen"))
            {
                var id = new string(newId.ToLowerInvariant().Select(c => char.IsLetterOrDigit(c) ? c : '_').ToArray());
                string g = newPreset > 0 ? presets[newPreset] : null;
                doc = VkDoc.New(bases[baseIdx], id, newName, g, null, UnityEngine.Random.Range(1000, 99999));
                status = "Neu (noch nicht gespeichert): " + Path.GetFileName(doc.path);
                SetupPreview();
            }
        }

        static string PresetLabel(string g)
        {
            int i = Array.IndexOf(VkSpec.GruppenAchse, g);
            return i >= 0 ? $"{VkSpec.GruppenBuchstabe[i]} {g}" : g;
        }

        static void Lamp(VkSpec.Ampel a)
        {
            var c = a == VkSpec.Ampel.Gruen ? new Color(0.3f, 0.8f, 0.3f) : a == VkSpec.Ampel.Gelb ? new Color(0.95f, 0.8f, 0.2f) : new Color(0.9f, 0.3f, 0.25f);
            var r = GUILayoutUtility.GetRect(14, 14, GUILayout.Width(14));
            r.y += 2; r.height = 12; r.width = 12;
            EditorGUI.DrawRect(r, c);
        }

        // ------------------------------------------------------------------ Vorschau
        void DrawPreview()
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                clipIdx = GUILayout.Toolbar(clipIdx, ClipLabels);
                if (GUILayout.Button(playing ? "❚❚" : "▶", GUILayout.Width(28))) playing = !playing;
                speed = EditorGUILayout.Slider(speed, 0.1f, 2f, GUILayout.Width(120));
            }
            using (new EditorGUILayout.HorizontalScope())
            {
                GUILayout.Label("Kamera:", GUILayout.Width(52));
                if (GUILayout.Button("ARPG")) view = VkBatch.ViewArpg;
                if (GUILayout.Button("Seite")) view = VkBatch.ViewSide;
                if (GUILayout.Button("Vorn")) view = VkBatch.ViewFront;
                if (GUILayout.Button("Oben")) view = VkBatch.ViewTop;
                GUILayout.Label("Ziehen = drehen, Rad = Zoom", EditorStyles.miniLabel);
            }
            var rect = GUILayoutUtility.GetRect(200, 10000, 260, Mathf.Max(260, position.height * 0.42f));
            if (pru == null || inst == null) { EditorGUI.DrawRect(rect, Color.black); return; }
            var e = Event.current;
            if (rect.Contains(e.mousePosition))
            {
                if (e.type == EventType.MouseDrag) { view.x += e.delta.x * 0.5f; view.y = Mathf.Clamp(view.y + e.delta.y * 0.4f, -10f, 89f); e.Use(); }
                if (e.type == EventType.ScrollWheel) { zoom = Mathf.Clamp(zoom * (1 + e.delta.y * 0.04f), 0.8f, 6f); e.Use(); }
            }
            if (e.type != EventType.Repaint) return;
            // Pose
            if (clipIdx == 0) VkBuilder.RestPose(inst);
            else
            {
                var c = VkBatch.Clip(cur, ClipLabels[clipIdx]);
                if (c != null) c.SampleAnimation(inst, c.length > 0 ? time % c.length : 0);
            }
            statur.Apply();
            StepSwing();
            float size = cur.L * cur.meshToMeter;
            var focus = new Vector3(0, size * 0.38f, 0);
            VkBatch.Pose(view, focus, size * zoom, out var pos, out var rot);
            pru.camera.transform.SetPositionAndRotation(pos, rot);
            pru.camera.nearClipPlane = size * 0.02f;
            Shader.SetGlobalFloat("_VKUseTime", 1f);
            Shader.SetGlobalFloat("_VKTime", time);
            pru.BeginPreview(rect, GUIStyle.none);
            pru.Render(true);
            var tex = pru.EndPreview();
            Shader.SetGlobalFloat("_VKUseTime", 0f);
            GUI.DrawTexture(rect, tex, ScaleMode.StretchToFill, false);
            if (clipIdx != 0)
                GUI.Label(new Rect(rect.x + 6, rect.yMax - 20, rect.width, 18), "Live-Vorschau: Fußrutschen bei geänderter Statur ist normal (Clips werden erst beim Blender-Backen angepasst).", EditorStyles.whiteMiniLabel);
        }

        /// <summary>G14: Federn um die Zeit seit dem letzten Bild weiterrechnen. Das Vorschau-Modell läuft auf der Stelle →
        /// „Laufband“ = Tempo des Clips als Zusatz-Geschwindigkeit. Clip-Events (hit/slam) lösen den Stoß aus.</summary>
        void StepSwing()
        {
            if (schwingen == null) return;
            schwingen.an = swingOn;
            float dt = swingTime < 0 ? 0 : Mathf.Clamp(time - swingTime, 0, 0.1f);
            if (swingClip != clipIdx || time < swingTime) { schwingen.Zuruecksetzen(); dt = 0; swingClipT = -1; }
            swingTime = time; swingClip = clipIdx;
            var c = clipIdx == 0 ? null : VkBatch.Clip(cur, ClipLabels[clipIdx]);
            float speedC = c != null && (ClipLabels[clipIdx] == "Walk" || ClipLabels[clipIdx] == "Run") ? VkSwingBatch.GroundSpeed(cur, c, inst) : 0;
            schwingen.zusatzGeschwindigkeit = VkSwingBatch.WorldForward(cur, inst) * speedC;
            if (c != null && c.length > 0)
            {
                float tc = time % c.length;
                if (swingClipT >= 0) VkSwingBatch.FireEvents(c, swingClipT, tc, schwingen);
                swingClipT = tc;
            }
            schwingen.Step(dt);
        }

        // ------------------------------------------------------------------ Helfer für Felder (lesen/schreiben direkt in der aufgelösten Datei)
        bool Fold(string key, string label, bool def = false)
        {
            if (!fold.TryGetValue(key, out var v)) v = def;
            v = EditorGUILayout.Foldout(v, label, true);
            fold[key] = v;
            return v;
        }

        void F(JObj o, string k, string label, float min, float max, float def, string tip = null)
        {
            EditorGUI.BeginChangeCheck();
            float v = EditorGUILayout.Slider(new GUIContent(label, tip), o.F(k, def), min, max);
            if (EditorGUI.EndChangeCheck()) { o[k] = (double)Mathf.Round(v * 1000f) / 1000.0; Changed(); }
        }

        void I(JObj o, string k, string label, int min, int max, int def)
        {
            EditorGUI.BeginChangeCheck();
            int v = EditorGUILayout.IntSlider(label, o.I(k, def), min, max);
            if (EditorGUI.EndChangeCheck()) { o[k] = (long)v; Changed(); }
        }

        void T(JObj o, string k, string label, bool def)
        {
            EditorGUI.BeginChangeCheck();
            bool v = EditorGUILayout.Toggle(label, o.B(k, def));
            if (EditorGUI.EndChangeCheck()) { o[k] = v; Changed(); }
        }

        void P(JObj o, string k, string label, string[] opts, string def)
        {
            int i = Array.IndexOf(opts, o.S(k, def));
            EditorGUI.BeginChangeCheck();
            int n = EditorGUILayout.Popup(label, Mathf.Max(0, i), opts);
            if (EditorGUI.EndChangeCheck()) { o[k] = opts[n]; Changed(); }
        }

        void Col(JObj o, string k, string label, string def, bool optional = false)
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                bool has = o[k] is string;
                if (optional)
                {
                    EditorGUI.BeginChangeCheck();
                    has = EditorGUILayout.ToggleLeft(label, has, GUILayout.Width(EditorGUIUtility.labelWidth));
                    if (EditorGUI.EndChangeCheck()) { o[k] = has ? (object)def : null; Changed(); }
                    if (!has) return;
                }
                else EditorGUILayout.LabelField(label, GUILayout.Width(EditorGUIUtility.labelWidth));
                EditorGUI.BeginChangeCheck();
                var c = EditorGUILayout.ColorField(GUIContent.none, VkBuilder.Hex(o.S(k, def), Color.gray), true, false, false);
                if (EditorGUI.EndChangeCheck()) { o[k] = "#" + ColorUtility.ToHtmlStringRGB(c); Changed(); }
            }
        }

        void Vec3(JObj o, string k, string label, string[] names, float min, float max)
        {
            var v = o.Vec(k, new[] { 1f, 1f, 1f });
            EditorGUILayout.LabelField(label);
            EditorGUI.indentLevel++;
            EditorGUI.BeginChangeCheck();
            for (int i = 0; i < 3; i++) v[i] = EditorGUILayout.Slider(names[i], v[i], min, max);
            if (EditorGUI.EndChangeCheck()) { o.SetVec(k, v.Select(x => Mathf.Round(x * 1000) / 1000f).ToArray()); Changed(); }
            EditorGUI.indentLevel--;
        }

        /// <summary>Zonen-Liste mit Auswahlmenü (Andock-Zonen, Sammelnamen).</summary>
        void ZoneList(JObj o, string k, string label, bool withLine = false, bool layerZones = false)
        {
            var list = o.Strs(k);
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField(label, GUILayout.Width(EditorGUIUtility.labelWidth));
                string txt = list.Count > 0 ? string.Join(", ", list)
                           : layerZones ? (o.L(k) == null ? "ganzer_koerper (Standard)" : "– keine: Ebene wirkt nirgends") : "–";
                EditorGUILayout.LabelField(txt, EditorStyles.wordWrappedLabel);
                if (GUILayout.Button("Wählen…", GUILayout.Width(64)))
                {
                    var menu = new GenericMenu();
                    var all = new List<string> { "ganzer_koerper" };
                    if (withLine) all.Add("rueckenlinie");
                    all.AddRange(cur.zones.Names);
                    foreach (var z in all)
                        menu.AddItem(new GUIContent("Zonen/" + z), list.Contains(z), () => ToggleZone(o, k, z));
                    foreach (var z in cur.zones.SammelNames)
                        menu.AddItem(new GUIContent("Sammelnamen/" + z), list.Contains(z), () => ToggleZone(o, k, z));
                    menu.ShowAsContext();
                }
            }
        }

        void ToggleZone(JObj o, string k, string z)
        {
            var l = o.Strs(k);
            if (l.Contains(z)) l.Remove(z); else l.Add(z);
            o[k] = l.Cast<object>().ToList();
            Changed();
        }

        float Cm(float frac) => frac * cur.L * cur.meshToMeter * 100f;

        // ------------------------------------------------------------------ Tab Statur
        void StaturTab()
        {
            EditorGUILayout.HelpBox("Live-Vorschau: Die Knochen werden nur angenähert skaliert. Rutschen die Füße beim Laufen, ist das normal. " +
                                    "Die fertige Variante muss neu gebacken werden (Statur-Klasse, Blender-Backen in Meilenstein 2). " +
                                    "Regler sind auf die gelbe Zone begrenzt (Entscheidung E3).", MessageType.Info);
            var st = doc.resolved.Obj("statur");
            var a = VkSpec.StaturAmpel(st, out var why);
            using (new EditorGUILayout.HorizontalScope())
            {
                Lamp(a);
                EditorGUILayout.LabelField("Statur-Ampel: " + (a == VkSpec.Ampel.Gruen ? "grün – Clips passen" : a == VkSpec.Ampel.Gelb ? "gelb – Clips mit Korrektur" : "rot – eigener Clip-Satz nötig"));
            }
            foreach (var w in why) EditorGUILayout.LabelField("   • " + w, EditorStyles.miniLabel);
            EditorGUILayout.Space();
            // Makro „Masse“: Rumpf- und Gliederdicke gemeinsam
            float masse = (st.F("rumpf_dicke", 1) + st.F("glied_dicke", 1)) * 0.5f;
            EditorGUI.BeginChangeCheck();
            float nm = EditorGUILayout.Slider(new GUIContent("Masse (Makro)", "bewegt Rumpfdicke + Gliederdicke gemeinsam"), masse, 0.8f, 1.25f);
            if (EditorGUI.EndChangeCheck())
            {
                float d = nm - masse;
                st["rumpf_dicke"] = (double)Mathf.Clamp(st.F("rumpf_dicke", 1) + d, 0.8f, 1.25f);
                st["glied_dicke"] = (double)Mathf.Clamp(st.F("glied_dicke", 1) + d, 0.8f, 1.25f);
                Changed();
            }
            foreach (var r in VkSpec.Statur)
            {
                using (new EditorGUILayout.HorizontalScope())
                {
                    Lamp(VkSpec.Zone(r, st.F(r.feld, 1)));
                    EditorGUI.BeginChangeCheck();
                    float v = EditorGUILayout.Slider(new GUIContent($"{r.name} ({r.typ})", r.hinweis), st.F(r.feld, 1), r.SliderMin, r.SliderMax);
                    if (EditorGUI.EndChangeCheck())
                    {
                        // Beinlänge vorn ↔ hinten höchstens 15 % Unterschied (gelb)
                        if (r.feld.StartsWith("bein_laenge"))
                        {
                            float other = st.F(r.feld.EndsWith("vorn") ? "bein_laenge_hinten" : "bein_laenge_vorn", 1);
                            v = Mathf.Clamp(v, other / 1.15f, other * 1.15f);
                        }
                        st[r.feld] = (double)Mathf.Round(v * 1000) / 1000.0;
                        Changed();
                    }
                    if (GUILayout.Button("1", GUILayout.Width(20))) { st[r.feld] = 1.0; Changed(); }
                }
            }
        }

        // ------------------------------------------------------------------ Tab Material
        void MaterialTab()
        {
            var m = doc.resolved.Obj("material");
            F(m.Obj("stil"), "facetten", "Facetten (flach ↔ weich)", 0, 1, 1);
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Farbgruppen", EditorStyles.boldLabel);
            var fg = m.Obj("farbgruppen");
            foreach (var g in VkSpec.Gruppen)
            {
                var o = fg.O(g);
                using (new EditorGUILayout.HorizontalScope())
                {
                    var c = VkBuilder.Hex(o?.S("farbe", null) ?? VkSpec.GruppenStdFarbe[g], Color.gray);
                    EditorGUI.DrawRect(GUILayoutUtility.GetRect(14, 14, GUILayout.Width(14)), c);
                    if (!Fold("fg_" + g, g)) continue;
                }
                if (!fold["fg_" + g]) continue;
                o = fg.Obj(g);
                EditorGUI.indentLevel++;
                Col(o, "farbe", "Farbe", VkSpec.GruppenStdFarbe[g]);
                Col(o, "farbe_2", "Farbe 2", "#808080", true);
                F(o, "farb_zufall", "Farb-Zufall pro Teil", 0, 1, 0, "Anteil der Teile, die Farbe 2 bekommen");
                P(o, "verlauf", "Verlauf", new[] { "keiner", "ansatz_spitze" }, "keiner");
                F(o, "rauheit", "Rauheit (matt ↔ glänzend)", 0, 1, 0.8f);
                F(o, "detail", "Detail (Tripo-Textur)", 0, 1, 0.5f);
                F(o, "helligkeit_zufall", "Helligkeit pro Facette", 0, 0.3f, 0.08f);
                F(o, "leuchten", "Leuchten", 0, 8, 0);
                F(o, "glasig", "Glasig (falsche Transparenz)", 0, 1, 0);
                EditorGUI.indentLevel--;
            }
            EditorGUILayout.Space();
            if (doc.migratedFrom == 1)
                EditorGUILayout.HelpBox($"Datei im alten Format 1 geladen und umgestellt: Die bisherigen Ebenen sind jetzt Körper-Ebenen, " +
                    $"{doc.migratedAccLayers} Accessoire-Ebene(n) wurden aus Ebenen angelegt, die bisher auch auf die Accessoires wirkten. " +
                    "„Speichern“ schreibt Format 2.", MessageType.Info);
            // ---- Gruppe 1: Körper (Haut + Bedeckung)
            EditorGUILayout.LabelField($"Körper-Ebenen (max. {VkSpec.MaxEbenen}, empfohlen 3–5, oben = zuerst)", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("wirken auf Haut und/oder Bedeckung (Häkchen „wirkt auf“), gesteuert über die Zonen – nie auf Accessoires", EditorStyles.miniLabel);
            LayerList(m.List("ebenen"), false);
            EditorGUILayout.Space(8);
            // ---- Gruppe 2: Accessoires (immer obenauf)
            EditorGUILayout.LabelField($"Accessoire-Ebenen – liegen immer obenauf (max. {VkSpec.MaxAccEbenen}, empfohlen 1–3)", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("wirken nur auf Accessoires; Häkchen pro Eintrag (auch im Reiter Accessoires unter „Material“ – dieselben Daten)", EditorStyles.miniLabel);
            LayerList(m.List("ebenen_accessoires"), true);
            EditorGUILayout.HelpBox("„rand“ der Masken wirkt als fester weicher Übergang; Rim-Light und Puls bleiben zur Laufzeit live. " +
                                    "Rim höchstens 1× pro Gruppe, Puls: ein Wert pro Material (erste pulsierende Risse-Ebene).", MessageType.None);
        }

        /// <summary>Liste einer Ebenen-Gruppe mit an/aus, ▲ ▼ ✕ und „Ebene hinzufügen“.</summary>
        void LayerList(List<object> eb, bool acc)
        {
            string pre = acc ? "ea_" : "eb_";
            int max = acc ? VkSpec.MaxAccEbenen : VkSpec.MaxEbenen;
            if (eb.Count == 0) EditorGUILayout.LabelField("   (keine)", EditorStyles.miniLabel);
            for (int i = 0; i < eb.Count; i++)
            {
                if (!(eb[i] is JObj e)) continue;
                using (new EditorGUILayout.HorizontalScope())
                {
                    EditorGUI.BeginChangeCheck();
                    bool an = EditorGUILayout.Toggle(e.B("an", true), GUILayout.Width(16));
                    if (EditorGUI.EndChangeCheck()) { e["an"] = an; Changed(); }
                    string auf = acc ? "" : VkSpec.AufText(e, LagenIds());
                    string extra = acc ? "  → " + VkSpec.ZielText(e) : auf.Length > 0 ? "  → " + auf : "";
                    bool open = Fold(pre + e.S("id", i.ToString()), $"{e.S("id", "?")}  ({e.S("typ", "?")}){extra}");
                    if (GUILayout.Button("▲", GUILayout.Width(22)) && i > 0) { eb.RemoveAt(i); eb.Insert(i - 1, e); Changed(); GUIUtility.ExitGUI(); }
                    if (GUILayout.Button("▼", GUILayout.Width(22)) && i < eb.Count - 1) { eb.RemoveAt(i); eb.Insert(i + 1, e); Changed(); GUIUtility.ExitGUI(); }
                    if (GUILayout.Button("✕", GUILayout.Width(22))) { eb.RemoveAt(i); Changed(); GUIUtility.ExitGUI(); }
                    if (!open) continue;
                }
                EditorGUI.indentLevel++;
                LayerFields(e, acc);
                EditorGUI.indentLevel--;
                EditorGUILayout.Space(4);
            }
            if (eb.OfType<JObj>().Count(x => x.B("an", true)) > max)
                EditorGUILayout.HelpBox($"Mehr als {max} aktive Ebenen: nur die ersten {max} wirken.", MessageType.Warning);
            foreach (var t in new[] { "naesse", "rim" })
                if (eb.OfType<JObj>().Count(x => x.B("an", true) && x.S("typ", "") == t) > 1)
                    EditorGUILayout.HelpBox($"„{t}“ ist in dieser Gruppe mehrfach an – nur die letzte zählt (Spec 4.3: je 1×).", MessageType.Warning);
            using (new EditorGUILayout.HorizontalScope())
            {
                int sel = acc ? addAccLayerTyp : addLayerTyp;
                sel = EditorGUILayout.Popup(sel, VkSpec.EbenenTypen);
                if (acc) addAccLayerTyp = sel; else addLayerTyp = sel;
                GUI.enabled = eb.Count < max;
                if (GUILayout.Button(acc ? "Accessoire-Ebene hinzufügen" : "Ebene hinzufügen"))
                {
                    var typ = VkSpec.EbenenTypen[sel];
                    string baseId = acc ? $"acc_{typ}" : typ;
                    int n = 1; while (eb.OfType<JObj>().Any(x => x.S("id", "") == $"{baseId}_{n}")) n++;
                    eb.Add(VkSpec.NeueEbene($"{baseId}_{n}", typ, acc));
                    fold[$"{pre}{baseId}_{n}"] = true;
                    Changed();
                }
                GUI.enabled = true;
            }
        }

        /// <summary>„gilt für“ einer Accessoire-Ebene: Häkchen „alle“ + ein Häkchen pro Accessoire-Eintrag der Variante
        /// (Hauptbedienelement, Nutzer 2026-11-23). „Typen…“ bleibt als Komfort (ganzer Typ auf einmal).</summary>
        void ZielField(JObj e)
        {
            var all = VkSpec.AlleEintraege(doc.resolved);
            bool alle = VkSpec.ZielAlle(e);
            var z = e["ziel"] as JObj;
            var typen = z?.Strs("typen") ?? new List<string>();
            var eint = z?.Strs("eintraege") ?? new List<string>();
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("gilt für", GUILayout.Width(EditorGUIUtility.labelWidth));
                EditorGUI.BeginChangeCheck();
                bool na = EditorGUILayout.ToggleLeft(new GUIContent("alle Accessoires", "auch Einträge, die später dazukommen"), alle);
                if (EditorGUI.EndChangeCheck())
                {
                    e["ziel"] = na ? (object)"alle" : new JObj { ["typen"] = new List<object>(), ["eintraege"] = all.Select(a => (object)a.S("id", "")).Distinct().ToList() };
                    Changed();
                }
                if (GUILayout.Button(new GUIContent("Typen…", "ganzen Typ auf einmal an/aus (Komfort)"), GUILayout.Width(64)))
                {
                    var menu = new GenericMenu();
                    foreach (var t in all.Select(a => a.S("typ", "")).Where(t => t.Length > 0).Distinct().OrderBy(t => t))
                        menu.AddItem(new GUIContent(t), !alle && typen.Contains(t), () => ToggleZiel(e, "typen", t));
                    if (all.Count == 0) menu.AddDisabledItem(new GUIContent("(die Variante hat keine Accessoires)"));
                    menu.ShowAsContext();
                }
            }
            EditorGUI.indentLevel++;
            if (all.Count == 0) EditorGUILayout.LabelField("(die Variante hat keine Accessoires)", EditorStyles.miniLabel);
            foreach (var a in all)
            {
                string id = a.S("id", "");
                bool hit = VkSpec.ZielTrifft(e, a);
                string via = !alle && hit && !eint.Contains(id) ? "  · über Typ" : "";
                EditorGUI.BeginChangeCheck();
                bool n = EditorGUILayout.ToggleLeft($"{id}  ({a.S("typ", "?")}){(a.B("an", true) ? "" : " – aus")}{via}", hit);
                if (EditorGUI.EndChangeCheck()) { VkSpec.SetZielEintrag(e, a, n, all); Changed(); }
            }
            EditorGUI.indentLevel--;
            var accs = VkSpec.AktiveAccessoires(doc.resolved);
            if (!VkSpec.ZielAlle(e) && accs.All(a => !VkSpec.ZielTrifft(e, a)))
                EditorGUILayout.HelpBox("Diese Ebene trifft kein Accessoire der Variante.", MessageType.Warning);
            if (!VkSpec.ZielAlle(e) && accs.Count > VkSpec.MaxAccEintraege)
                EditorGUILayout.HelpBox($"Nur die ersten {VkSpec.MaxAccEintraege} Einträge lassen sich gezielt wählen, „alle“ gilt für jede Anzahl.", MessageType.Warning);
        }

        List<string> LagenIds() => VkSpec.AktiveLagen(doc.resolved).Select((l, k) => VkSpec.LageId(l, k)).ToList();

        /// <summary>„wirkt auf“ einer Körper-Ebene: Haut und Bedeckung getrennt (Standard: beide an). Bei 2 Lagen ein Häkchen pro Lage.</summary>
        void AufField(JObj e)
        {
            var mk = e.Obj("maske");
            var lagen = VkSpec.AktiveLagen(doc.resolved);
            var ids = LagenIds();
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField(new GUIContent("wirkt auf", "Haut = Grundkörper (Basis-Mesh); Bedeckung = Fell, Federn, Stacheln, Platten der Lagen"), GUILayout.Width(EditorGUIUtility.labelWidth));
                int il = EditorGUI.indentLevel; EditorGUI.indentLevel = 0;
                EditorGUI.BeginChangeCheck();
                bool h = EditorGUILayout.ToggleLeft("Haut", VkSpec.AufHaut(e), GUILayout.Width(60));
                if (EditorGUI.EndChangeCheck()) { if (h) mk.Remove("haut"); else mk["haut"] = false; Changed(); }
                if (lagen.Count <= 1)
                {
                    string lbl = lagen.Count == 0 ? "Bedeckung" : $"Bedeckung ({lagen[0].S("typ", "?")})";
                    bool cur = VkSpec.AufLage(e, ids.Count > 0 ? ids[0] : null);
                    EditorGUI.BeginChangeCheck();
                    bool nb = EditorGUILayout.ToggleLeft(lbl, cur);
                    if (EditorGUI.EndChangeCheck()) { if (nb) mk.Remove("bedeckung"); else mk["bedeckung"] = false; Changed(); }
                }
                else
                {
                    var on = ids.Where(id => VkSpec.AufLage(e, id)).ToList();
                    for (int k = 0; k < lagen.Count; k++)
                    {
                        EditorGUI.BeginChangeCheck();
                        bool nb = EditorGUILayout.ToggleLeft(new GUIContent($"{ids[k]} ({lagen[k].S("typ", "?")})", $"Bedeckungs-Lage {k + 1}"), on.Contains(ids[k]), GUILayout.MinWidth(80));
                        if (EditorGUI.EndChangeCheck())
                        {
                            if (nb) on.Add(ids[k]); else on.Remove(ids[k]);
                            VkSpec.SetLagen(mk, on, ids);
                            Changed();
                        }
                    }
                }
                EditorGUI.indentLevel = il;
            }
            if (lagen.Count == 0) EditorGUILayout.LabelField("   (die Variante hat keine Bedeckungs-Lage – „Bedeckung“ wirkt erst, wenn eine Lage dazukommt)", EditorStyles.wordWrappedMiniLabel);
            if (VkSpec.AufText(e, ids) == "nirgends") EditorGUILayout.HelpBox("Weder Haut noch Bedeckung gewählt: die Ebene wirkt nirgends.", MessageType.Warning);
        }

        void ToggleZiel(JObj e, string key, string val)
        {
            var z = e["ziel"] as JObj ?? new JObj { ["typen"] = new List<object>(), ["eintraege"] = new List<object>() };
            var l = z.Strs(key);
            if (l.Contains(val)) l.Remove(val); else l.Add(val);
            z[key] = l.Cast<object>().ToList();
            if (!z.Has("typen")) z["typen"] = new List<object>();
            if (!z.Has("eintraege")) z["eintraege"] = new List<object>();
            e["ziel"] = z;
            Changed();
        }

        void LayerFields(JObj e, bool acc = false, bool zielListe = true)
        {
            switch (e.S("typ", ""))
            {
                case "verlauf":
                    P(e, "richtung", "Richtung", new[] { "oben_unten", "vorn_hinten", "ansatz_spitze" }, "oben_unten");
                    Col(e, "farbe_a", "Farbe oben/vorn", "#FFFFFF"); Col(e, "farbe_b", "Farbe unten/hinten", "#808080");
                    P(e, "mischung", "Mischung", new[] { "multiplizieren", "ueberlagern", "ersetzen" }, "ueberlagern");
                    F(e, "mitte", "Mitte", 0, 1, 0.5f); F(e, "weichheit", "Weichheit", 0, 1, 0.5f);
                    break;
                case "muster":
                    P(e, "art", "Art", new[] { "streifen", "flecken", "tupfen", "ringe", "marmor", "zellen" }, "flecken");
                    Col(e, "farbe", "Farbe", "#404040");
                    F(e, "skala", "Skala", 0.01f, 0.5f, 0.08f); F(e, "dichte", "Dichte", 0, 1, 0.5f); F(e, "kontrast", "Kontrast", 0, 1, 0.7f);
                    P(e, "richtung", "Richtung", new[] { "quer", "laengs", "knochen" }, "quer");
                    F(e, "verzerrung", "Verzerrung", 0, 1, 0.3f);
                    P(e, "mischung", "Mischung", new[] { "multiplizieren", "ueberlagern", "ersetzen" }, "ueberlagern");
                    break;
                case "risse":
                    EditorGUI.BeginChangeCheck();
                    P(e, "element", "Element", VkSpec.Elemente.Keys.ToArray(), "glut");
                    if (EditorGUI.EndChangeCheck() && VkSpec.Elemente.TryGetValue(e.S("element", "glut"), out var el)) { e["farbe"] = el.farbe; e["intensitaet"] = (double)el.intensitaet; }
                    P(e, "art", "Art", new[] { "risse", "adern", "zellfugen", "runen" }, "risse");
                    Col(e, "farbe", "Farbe", "#FF6A10");
                    F(e, "intensitaet", "Leuchten", 0, 8, 4); F(e, "breite", "Breite", 0.001f, 0.02f, 0.005f);
                    F(e, "dichte", "Dichte", 0, 1, 0.4f); F(e, "verzweigung", "Verzweigung", 0, 1, 0.5f); F(e, "hof", "Glüh-Hof", 0, 1, 0.3f);
                    F(e, "puls_frequenz", "Puls (Hz)", 0, 2, 0); F(e, "puls_staerke", "Puls-Stärke", 0, 1, 0);
                    break;
                case "ueberzug":
                    P(e, "art", "Art", new[] { "schmutz", "frost", "asche", "schleim", "staub", "moos" }, "staub");
                    Col(e, "farbe", "Farbe", "#A89A88");
                    F(e, "menge", "Menge", 0, 1, 0.3f); F(e, "kanten", "an Kanten", 0, 1, 0.4f);
                    F(e, "rauschen_skala", "Fleck-Größe", 0.01f, 0.3f, 0.08f); F(e, "rauheit", "Rauheit", 0, 1, 1);
                    break;
                case "naesse":
                    F(e, "menge", "Menge", 0, 1, 0.5f); F(e, "glanz", "Glanz", 0, 1, 0.8f); F(e, "abdunkeln", "Abdunkeln", 0, 1, 0.3f);
                    break;
                case "rim":
                    Col(e, "farbe", "Farbe", "#FFD080"); F(e, "intensitaet", "Stärke", 0, 4, 1.5f); F(e, "breite", "Breite", 0, 1, 0.35f);
                    break;
            }
            F(e, "staerke", "Stärke der Ebene", 0, 1, 1);
            if (!(e["seed"] is null) || e.Has("seed"))
                using (new EditorGUILayout.HorizontalScope())
                {
                    EditorGUILayout.LabelField("Seed", e["seed"] == null ? "automatisch" : e.I("seed", 0).ToString());
                    if (GUILayout.Button("Neu würfeln", GUILayout.Width(90))) { e["seed"] = (long)UnityEngine.Random.Range(1, 99999); Changed(); }
                }
            var mk = e.Obj("maske");
            if (acc)
            {
                if (zielListe) ZielField(e);
                EditorGUILayout.LabelField("Maske innerhalb der Teile (Körper-Zonen gelten hier nicht)", EditorStyles.miniBoldLabel);
                F(mk, "oben", "Oben (+) / Unterseite (−)", -1, 1, 0);
                F(mk, "rauschen", "Fleckiger Rand", 0, 1, 0);
                return;
            }
            EditorGUILayout.LabelField("Maske (wo die Ebene auf dem Körper wirkt)", EditorStyles.miniBoldLabel);
            AufField(e);
            ZoneList(mk, "zonen", "Zonen", false, true);
            ZoneList(mk, "ohne", "ohne");
            F(mk, "oben", "Oben (+) / Unterseite (−)", -1, 1, 0);
            F(mk, "rauschen", "Fleckiger Rand", 0, 1, 0.2f);
            var gr = mk.Strs("gruppen");
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Farbgruppen", GUILayout.Width(EditorGUIUtility.labelWidth));
                EditorGUILayout.LabelField(gr.Count == 0 ? "alle (Körper)" : string.Join(", ", gr), EditorStyles.wordWrappedLabel);
                if (GUILayout.Button("Wählen…", GUILayout.Width(64)))
                {
                    var menu = new GenericMenu();
                    foreach (var g in VkSpec.KoerperGruppen)
                        menu.AddItem(new GUIContent(g), gr.Contains(g), () =>
                        {
                            var l = mk.Strs("gruppen");
                            if (l.Contains(g)) l.Remove(g); else l.Add(g);
                            if (l.Count == 0) mk.Remove("gruppen"); else mk["gruppen"] = l.Cast<object>().ToList();
                            Changed();
                        });
                    menu.ShowAsContext();
                }
            }
        }

        // ------------------------------------------------------------------ Tab Accessoires
        void AccTab()
        {
            var list = doc.resolved.List("accessoires");
            var types = VkParts.Types();
            SwingBox();
            EditorGUILayout.HelpBox("Ablauf: Körperstellen (Zonen) wählen → Typ → Einstellungen. Die Teile sitzen auf der Haut unter dem Ansatzpunkt " +
                                    "und bekommen dessen Gewichte (Bindung „anker“, E4). Größen sind Anteile der Kreaturgröße (cm in Klammern).", MessageType.None);
            for (int i = 0; i < list.Count; i++)
            {
                if (!(list[i] is JObj a)) continue;
                string id = a.S("id", "?");
                int tris = res != null && res.trisPerAcc.TryGetValue(id, out var t) ? t : 0;
                int cnt = res?.instances.Count(x => x.acc == id) ?? 0;
                using (new EditorGUILayout.HorizontalScope())
                {
                    EditorGUI.BeginChangeCheck();
                    bool an = EditorGUILayout.Toggle(a.B("an", true), GUILayout.Width(16));
                    if (EditorGUI.EndChangeCheck()) { a["an"] = an; Changed(); }
                    bool open = Fold("acc_" + id, $"{id}  ({a.S("typ", "?")}, {cnt} Teile, {tris} Tris)");
                    if (GUILayout.Button("✕", GUILayout.Width(22))) { list.RemoveAt(i); Changed(); GUIUtility.ExitGUI(); }
                    if (!open) continue;
                }
                EditorGUI.indentLevel++;
                AccFields(a, types);
                AccMaterialBox(a);
                EditorGUI.indentLevel--;
                EditorGUILayout.Space(4);
            }
            if (res != null) foreach (var w in res.warnings) EditorGUILayout.HelpBox(w, MessageType.Warning);
            using (new EditorGUILayout.HorizontalScope())
            {
                int ti = Mathf.Max(0, types.IndexOf(addAccTyp));
                ti = EditorGUILayout.Popup(ti, types.ToArray());
                if (types.Count > 0) addAccTyp = types[ti];
                if (GUILayout.Button("Accessoire hinzufügen") && types.Count > 0)
                {
                    int n = 1; while (list.OfType<JObj>().Any(x => x.S("id", "") == $"{addAccTyp}_{n}")) n++;
                    var a = VkSpec.NeuesAccessoire($"{addAccTyp}_{n}", addAccTyp);
                    list.Add(a);
                    fold[$"acc_{addAccTyp}_{n}"] = true;
                    Changed();
                }
            }
        }

        /// <summary>Aufklappbereich „Material“ an jedem Accessoire-Eintrag: die Accessoire-Ebenen mit Häkchen „wirkt auf diesen
        /// Eintrag“ und ihren Reglern. Dieselben Daten wie Reiter Material → Accessoire-Ebenen (material.ebenen_accessoires).</summary>
        void AccMaterialBox(JObj a)
        {
            string id = a.S("id", "?");
            var eb = doc.resolved.Obj("material").List("ebenen_accessoires");
            var layers = eb.OfType<JObj>().ToList();
            int hits = layers.Count(e => e.B("an", true) && VkSpec.ZielTrifft(e, a));
            if (!Fold("accmat_" + id, $"Material ({hits} von {layers.Count} Accessoire-Ebenen wirken hier)")) return;
            EditorGUI.indentLevel++;
            EditorGUILayout.LabelField("Häkchen = Ebene wirkt auf diesen Eintrag. Gleiche Ebenen wie im Reiter Material (Änderungen gelten dort mit).", EditorStyles.wordWrappedMiniLabel);
            var all = VkSpec.AlleEintraege(doc.resolved);
            foreach (var e in layers)
            {
                string eid = e.S("id", "?");
                bool open;
                using (new EditorGUILayout.HorizontalScope())
                {
                    int il = EditorGUI.indentLevel;
                    GUILayout.Space(il * 15);
                    EditorGUI.indentLevel = 0;
                    EditorGUI.BeginChangeCheck();
                    bool hit = EditorGUILayout.Toggle(VkSpec.ZielTrifft(e, a), GUILayout.Width(16));
                    if (EditorGUI.EndChangeCheck()) { VkSpec.SetZielEintrag(e, a, hit, all); Changed(); }
                    open = Fold($"accmat_{id}_{eid}", $"{eid}  ({e.S("typ", "?")}){(e.B("an", true) ? "" : " – Ebene aus")}  → {VkSpec.ZielText(e)}");
                    EditorGUI.indentLevel = il;
                }
                if (!open) continue;
                EditorGUI.indentLevel++;
                T(e, "an", "Ebene an", true);
                LayerFields(e, true, false);
                EditorGUI.indentLevel--;
                EditorGUILayout.Space(2);
            }
            if (layers.Count == 0) EditorGUILayout.LabelField("(noch keine Accessoire-Ebene)", EditorStyles.miniLabel);
            using (new EditorGUILayout.HorizontalScope())
            {
                addAccLayerTyp = EditorGUILayout.Popup(addAccLayerTyp, VkSpec.EbenenTypen);
                GUI.enabled = eb.Count < VkSpec.MaxAccEbenen;
                if (GUILayout.Button("neue Ebene nur für diesen Eintrag"))
                {
                    var typ = VkSpec.EbenenTypen[addAccLayerTyp];
                    int n = 1; while (eb.OfType<JObj>().Any(x => x.S("id", "") == $"acc_{typ}_{n}")) n++;
                    var ne = VkSpec.NeueEbene($"acc_{typ}_{n}", typ, true);
                    ne["ziel"] = new JObj { ["typen"] = new List<object>(), ["eintraege"] = new List<object> { id } };
                    eb.Add(ne);
                    fold[$"accmat_{id}_acc_{typ}_{n}"] = true;
                    Changed();
                }
                GUI.enabled = true;
            }
            EditorGUI.indentLevel--;
        }

        /// <summary>G14: Weichheit der Bedeckungs-Lagen (die Geometrie kommt aus Blender, die Weichheit wirkt sofort im Shader).</summary>
        void SwingBox()
        {
            if (!Fold("swing", "Nachschwingen (Weichheit, G14)", true)) return;
            EditorGUI.indentLevel++;
            using (new EditorGUILayout.HorizontalScope())
            {
                swingOn = EditorGUILayout.ToggleLeft("in der Vorschau an", swingOn, GUILayout.Width(150));
                if (GUILayout.Button("Stoß (slam)", GUILayout.Width(90)) && schwingen != null) schwingen.Stoss("slam");
                if (GUILayout.Button("Schlag (hit)", GUILayout.Width(90)) && schwingen != null) schwingen.Stoss("hit");
            }
            var lagen = doc.resolved.Obj("bedeckung").List("lagen").OfType<JObj>().Where(l => l.B("an", true)).Take(2).ToList();
            if (lagen.Count == 0) EditorGUILayout.LabelField("Keine Bedeckungs-Lage (Fell, Federn …) – Weichheit der Accessoires steht unten pro Eintrag.", EditorStyles.miniLabel);
            for (int i = 0; i < lagen.Count; i++)
            {
                string typ = lagen[i].S("typ", "fell");
                F(lagen[i], "weichheit", $"Lage {i + 1} ({typ})", 0, 1, VkSpec.WeichStdLage(typ), "0 = starr wie Felszacken … 1 = schwingendes Fell. Wirkt ohne „In Blender bauen“.");
            }
            EditorGUILayout.LabelField("Trägheit beim Anlaufen/Bremsen/Drehen, Wackeln und Stöße (Clip-Events hit/slam) rechnet die Komponente VariantSchwingen im Prefab.", EditorStyles.wordWrappedMiniLabel);
            EditorGUI.indentLevel--;
            EditorGUILayout.Space(4);
        }

        void AccFields(JObj a, List<string> types)
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUI.BeginChangeCheck();
                var id = EditorGUILayout.DelayedTextField("ID", a.S("id", ""));
                if (EditorGUI.EndChangeCheck() && id.Length > 0) { VkSpec.RenameZiel(doc.resolved, a.S("id", ""), id); a["id"] = id; Changed(); }
            }
            P(a, "typ", "Typ", types.ToArray(), types.FirstOrDefault());
            var forms = VkParts.Get(a.S("typ", "")).Select(f => f.name).ToList();
            var chosen = a.Strs("formen");
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Formen", GUILayout.Width(EditorGUIUtility.labelWidth));
                foreach (var f in forms)
                {
                    bool on = chosen.Count == 0 || chosen.Contains(f);
                    bool n = GUILayout.Toggle(on, f, "Button");
                    if (n != on)
                    {
                        var l = chosen.Count == 0 ? new List<string>(forms) : chosen;
                        if (n) l.Add(f); else l.Remove(f);
                        a["formen"] = l.Distinct().Cast<object>().ToList();
                        Changed();
                    }
                }
            }
            // Spec 3.3 `auf`/`stelle`: auf einem anderen Accessoire sitzen statt auf Zonen
            var others = doc.resolved.List("accessoires").OfType<JObj>().Select(x => x.S("id", "")).Where(x => x.Length > 0 && x != a.S("id", "")).ToList();
            {
                var opts = new List<string> { "(Zonen)" }; opts.AddRange(others);
                int ai = Mathf.Max(0, opts.IndexOf(a["auf"] as string ?? "(Zonen)"));
                EditorGUI.BeginChangeCheck();
                int na = EditorGUILayout.Popup(new GUIContent("Sitzt auf", "statt Zonen: auf einem anderen Accessoire (Fransen am Moospolster-Rand, Pilze auf Moos)"), ai, opts.ToArray());
                if (EditorGUI.EndChangeCheck()) { a["auf"] = na == 0 ? null : opts[na]; Changed(); }
            }
            if (a["auf"] is string) P(a, "stelle", "Stelle", VkSpec.Stellen, "oben");
            else ZoneList(a, "zonen", "Zonen", true);
            T(a, "spiegeln", "Spiegeln (_l → _r)", true);
            if (a.B("spiegeln", true)) F(a, "asymmetrie", "Asymmetrie", 0, 1, 0.2f);
            P(a, "verteilung", "Verteilung", VkSpec.Verteilungen, "streuen");
            string v = a.S("verteilung", "streuen");
            I(a, "anzahl", v == "cluster" ? "Anzahl Haufen" : v == "reihe" ? "Anzahl gesamt" : "Anzahl pro Zone", 1, 40, 1);
            if (v == "cluster") I(a, "teile", "Teile pro Haufen", 1, 16, 4);
            if (v == "reihe")
            {
                F(a, "von", "Rückenlinie von (Kopf)", 0, 1, 0.1f); F(a, "bis", "bis (Schwanz)", 0, 1, 0.8f);
                I(a, "reihen", "Reihen", 1, 2, 1);
            }
            F(a, "groesse", $"Größe ({Cm(a.F("groesse", 0.1f)):0} cm)", 0.01f, 0.4f, 0.1f);
            F(a, "groesse_zufall", "Größen-Zufall", 0, 1, 0.3f);
            if (v == "reihe" || v == "kranz") Vec3(a, "groesse_verlauf", "Größen-Verlauf", new[] { "Anfang", "Mitte", "Ende" }, 0.1f, 2f);
            Vec3(a, "streckung", "Streckung", new[] { "Länge", "Breite", "Höhe" }, 0.3f, 3f);
            F(a, "abstand_min", $"Abstand min. ({Cm(a.F("abstand_min", 0.02f)):0} cm)", 0, 0.2f, 0.02f);
            P(a, "ausrichtung", "Ausrichtung", VkSpec.Ausrichtungen, "normale");
            F(a, "neigung", "Neigung (− hinten / + vorn)", -90, 90, 0);
            F(a, "drehung_zufall", "Drehung Zufall (°)", 0, 180, 180);
            F(a, "kipp_zufall", "Kippen Zufall (°)", 0, 45, 10);
            F(a, "einsinken", "Einsinken (Anteil Höhe)", 0, 0.6f, 0.25f);
            P(a, "bindung", "Bindung", VkSpec.Bindungen, "anker");
            F(a, "weichheit", "Weichheit (Nachschwingen)", 0, 1, VkSpec.WeichStdAcc(a.S("typ", "")), "0 = starr … 1 = schwingt voll (Fransen, Tang, Ketten). Gehänge folgen zusätzlich der Schwerkraft.");
            P(a, "farbgruppe", "Farbgruppe", new[] { "accessoire_a", "accessoire_b", "accessoire_c", "horn" }, "accessoire_a");
            F(a, "farb_zufall", "Farb-Zufall", 0, 1, 0);
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Seed", a["seed"] == null ? $"automatisch ({doc.EntrySeed(a, a.S("id", ""))})" : a.I("seed", 0).ToString());
                if (GUILayout.Button("Neu würfeln", GUILayout.Width(90))) { a["seed"] = (long)UnityEngine.Random.Range(1, 99999); Changed(); }
                if (a["seed"] != null && GUILayout.Button("auto", GUILayout.Width(44))) { a["seed"] = null; Changed(); }
            }
        }

        // ------------------------------------------------------------------ Tab Datei & Kennzahlen
        void FileTab()
        {
            var R = doc.resolved;
            EditorGUILayout.LabelField("Datei", doc.path.Replace(VkBase.PipelineRoot, "…"), EditorStyles.wordWrappedLabel);
            EditorGUILayout.LabelField("Revision", doc.loadedRevision.ToString());
            EditorGUI.BeginChangeCheck();
            R["name"] = EditorGUILayout.TextField("Name", R.S("name", ""));
            if (EditorGUI.EndChangeCheck()) Changed();
            var presets = VkDoc.Presets(); presets.Insert(0, "(kein Preset)");
            int pi = Mathf.Max(0, presets.IndexOf(R.S("gruppe", "")));
            EditorGUI.BeginChangeCheck();
            int npi = EditorGUILayout.Popup("Umgebungs-Gruppe", pi, presets.Select(PresetLabel).ToArray());
            string biom = EditorGUILayout.DelayedTextField("Biom (im Preset)", R.S("biom", "") ?? "");
            if (EditorGUI.EndChangeCheck())
            {
                doc.ChangePreset(npi > 0 ? presets[npi] : null, string.IsNullOrEmpty(biom) ? null : biom);
                Changed();
            }
            P(R, "budget_klasse", "Budget-Klasse", new[] { "normal", "elite", "boss" }, "normal");
            P(R, "art", "Art", new[] { "grund", "biom", "elite", "sonder" }, "biom");
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUI.BeginChangeCheck();
                int s = EditorGUILayout.IntField("Seed der Variante", R.I("seed", 0));
                if (EditorGUI.EndChangeCheck()) { R["seed"] = (long)Mathf.Max(0, s); Changed(); }
                if (GUILayout.Button("Neu würfeln", GUILayout.Width(90))) { R["seed"] = (long)UnityEngine.Random.Range(1, 999999); Changed(); }
            }
            T(R, "freigegeben", "Freigegeben (Nutzer-Abnahme)", false);
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUI.BeginChangeCheck();
                var bp = EditorGUILayout.DelayedTextField(new GUIContent("Blender (Pfad)", "für „In Blender bauen“"), VkBlenderJob.BlenderPath);
                if (EditorGUI.EndChangeCheck()) VkBlenderJob.BlenderPath = bp;
                if (GUILayout.Button("…", GUILayout.Width(24)))
                {
                    var f = EditorUtility.OpenFilePanel("blender.exe wählen", Path.GetDirectoryName(VkBlenderJob.BlenderPath), "exe");
                    if (!string.IsNullOrEmpty(f)) VkBlenderJob.BlenderPath = f;
                }
            }

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Kennzahlen (Live)", EditorStyles.boldLabel);
            var bud = VkSpec.BudgetFuer(R.S("budget_klasse", "normal"));
            if (res?.mesh != null)
            {
                int tris = res.mesh.triangles.Length / 3;
                Row("Tris gesamt", $"{tris:N0} / {bud.tris:N0}", tris <= bud.tris);
                Row("  davon Basis", $"{res.trisBase:N0}", true);
                Row("  davon Bedeckung", res.coverWanted ? $"{res.trisCover:N0} / {bud.bedeckung:N0}" + (res.cover == null ? " (nicht gebaut)" : res.coverFresh ? "" : " (veraltet)") : "keine Lage", res.trisCover <= bud.bedeckung);
                Row("  davon Accessoires", $"{res.trisAcc:N0} / {bud.accessoires:N0} ({res.instances.Count} Teile)", res.trisAcc <= bud.accessoires);
                Row("Materialien / Draw Calls", "1", true);
                Row("Texturen (gebacken)", $"Albedo + Maske (+ Leuchten, + Normal bei Facetten < 1), je {bud.textur}²", true);
                Row("Knochen", $"{cur.boneNames.Length} (keine zusätzlichen)", true);
                Row("Vertices", $"{res.mesh.vertexCount:N0}", true);
            }
            var gb = R.O("_gebaut");
            EditorGUILayout.Space();
            if (gb == null) EditorGUILayout.HelpBox("Noch nie gebacken.", MessageType.Info);
            else
            {
                bool fresh = gb.S("quell_hash", "") == doc.SourceHash();
                EditorGUILayout.HelpBox((fresh ? "Gebacken und aktuell" : "Gebacken, aber VERALTET – neu backen") + $" ({gb.S("datum", "?")})\n" +
                                        string.Join("\n", gb.Strs("dateien")), fresh ? MessageType.Info : MessageType.Warning);
            }
            EditorGUILayout.HelpBox("Gespeichert werden Kopf, Statur und nur die Abweichungen vom Gruppen-Preset (templates/umgebungs_gruppen/). " +
                                    "„Backen“ schreibt Prefab + Mesh + Material nach Assets/VariantKit/Baked/<Name>/ und die Instanzen-Liste neben die Varianten-Datei.", MessageType.None);
        }

        /// <summary>Für die Selbstprüfung (Batch): gleiche Live-Vorschau wie im Fenster (Rebuild, Statur, Clip, Preview-Kamera)
        /// als Bild speichern, ohne GUI.</summary>
        public static void SmokeTest(string variantPath, string outPng, string clip, float t)
        {
            var w = CreateInstance<VariantKitWindow>();
            try
            {
                w.bases = VkBase.List();
                w.doc = VkDoc.Load(variantPath);
                w.baseIdx = w.bases.FindIndex(b => b.id == w.doc.resolved.S("basis", ""));
                w.cur = VkBase.Load(w.bases[w.baseIdx].id);
                w.SetupPreview();
                // Änderung wie mit einem Regler: Gesamtgröße + Beinlänge, dann neu bauen
                w.Rebuild();
                var c = VkBatch.Clip(w.cur, clip);
                c.SampleAnimation(w.inst, c.length * t);
                w.statur.Apply();
                // G14: Federn wie im Fenster takten (Laufband-Tempo des Clips, 10 Schritte bis zum Bild)
                w.clipIdx = Mathf.Max(0, Array.IndexOf(ClipLabels, clip));
                for (int k = 0; k <= 10; k++) { w.time = c.length * t - (10 - k) / 30f; w.StepSwing(); }
                c.SampleAnimation(w.inst, c.length * t);
                w.statur.Apply();
                float size = w.cur.L * w.cur.meshToMeter;
                VkBatch.Pose(VkBatch.ViewArpg, new Vector3(0, size * 0.38f, 0), size * 2.3f, out var pos, out var rot);
                w.pru.camera.transform.SetPositionAndRotation(pos, rot);
                w.pru.camera.nearClipPlane = size * 0.02f;
                w.pru.BeginStaticPreview(new Rect(0, 0, 512, 512));
                w.pru.Render(true);
                var tex = w.pru.EndStaticPreview();
                File.WriteAllBytes(outPng, tex.EncodeToPNG());
                Debug.Log($"[VariantKit] FENSTER-VORSCHAU {Path.GetFileName(outPng)}: {w.res.mesh.triangles.Length / 3} Tris, {w.res.instances.Count} Teile, Statur-Ops {w.statur.scales.Count}/{w.statur.stretches.Count}/{w.statur.offsets.Count}, " +
                          $"Nachschwingen: Laufband {w.schwingen.zusatzGeschwindigkeit.magnitude:0.00} m/s, Hüfte {w.schwingen.Auslenkung(0).magnitude:0.000} rad");
            }
            finally { w.Cleanup(); DestroyImmediate(w); }
        }

        static void Row(string label, string val, bool ok)
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                Lamp(ok ? VkSpec.Ampel.Gruen : VkSpec.Ampel.Rot);
                EditorGUILayout.LabelField(label, val);
            }
        }
    }
}
