using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

/// <summary>Test-Viewer: Kreatur per Dropdown wählen, Clip per Button (oder Taste 1–9), Auto-Loop, Tempo, Zeitleiste.
/// Kamera: rechte Maustaste ziehen = drehen, Mausrad = Zoom. Bedienung bewusst mit IMGUI – keine Zusatzpakete nötig.</summary>
public class CreatureViewer : MonoBehaviour
{
    public CreatureCatalog catalog;
    public string startClip = "Walk";
    public bool autoLoop = true;
    [Range(0.05f, 3f)] public float speed = 1f;

    // Kamera-Voreinstellungen (Grad): ARPG = schräg von oben wie im Spiel
    public static readonly Vector2 ViewArpg = new Vector2(150f, 50f);
    public static readonly Vector2 ViewSide = new Vector2(90f, 5f);
    public static readonly Vector2 ViewFront = new Vector2(180f, 10f);
    public static readonly Vector2 ViewTop = new Vector2(180f, 89f);

    int creature = -1, clipIdx = -1;
    GameObject inst;
    PlayableGraph graph;
    AnimationPlayableOutput output;
    AnimationClipPlayable playable;
    float time;
    bool playing = true, dropdownOpen;
    Vector2 dropScroll;

    Camera cam;
    Vector3 focus;
    float dist = 2.5f, size = 1f;
    Vector2 view = ViewArpg;

    CreatureCatalog.Entry Cur => creature >= 0 ? catalog.entries[creature] : null;
    CreatureCatalog.Clip CurClip => Cur != null && clipIdx >= 0 && clipIdx < Cur.clips.Count ? Cur.clips[clipIdx] : null;

    void Start()
    {
        cam = Camera.main;
        if (catalog != null && catalog.entries.Count > 0) Select(0);
    }

    void OnDestroy()
    {
        if (graph.IsValid()) graph.Destroy();
    }

    void Select(int i)
    {
        if (inst != null) Destroy(inst);
        if (graph.IsValid()) graph.Destroy();
        creature = i;
        var e = Cur;
        inst = Instantiate(e.model, Vector3.zero, Quaternion.identity);
        inst.name = e.name;
        PlaceOnGround(inst);
        var animator = inst.GetComponent<Animator>();
        if (animator == null) animator = inst.AddComponent<Animator>();
        animator.applyRootMotion = false;
        animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;     // auch rechnen, wenn das Modell gerade nicht im Bild ist
        graph = PlayableGraph.Create("CreatureViewer");
        graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);       // Zeit steuern wir selbst (Tempo, Loop, Zeitleiste)
        output = AnimationPlayableOutput.Create(graph, "Anim", animator);

        var b = Bounds(inst);
        focus = b.center;
        size = Mathf.Max(b.size.x, b.size.y, b.size.z);
        dist = size * 2.2f;
        int w = e.clips.FindIndex(c => c.label == startClip);
        PlayClip(w >= 0 ? w : 0);
    }

    void PlayClip(int i)
    {
        if (Cur == null || i < 0 || i >= Cur.clips.Count) return;
        if (playable.IsValid()) playable.Destroy();
        clipIdx = i;
        playable = AnimationClipPlayable.Create(graph, CurClip.clip);
        playable.SetApplyFootIK(false);
        output.SetSourcePlayable(playable);
        time = 0f;
        playing = true;
        Sample();
    }

    void Update()
    {
        var c = CurClip;
        if (c == null || !graph.IsValid()) return;
        float len = Mathf.Max(c.clip.length, 1e-4f);
        if (playing)
        {
            time += Time.deltaTime * speed;
            if (time > len)
            {
                if (autoLoop) time %= len;
                else { time = len; playing = false; }
            }
        }
        Sample();
    }

    void Sample()
    {
        if (!playable.IsValid()) return;
        playable.SetTime(time);
        graph.Evaluate(0f);
    }

    void LateUpdate()
    {
        if (cam == null) return;
        Pose(view, focus, dist, out var pos, out var rot);
        cam.transform.SetPositionAndRotation(pos, rot);
        cam.nearClipPlane = size * 0.01f;
    }

    /// <summary>Kamera-Position aus Blickwinkel (x = Azimut um die Hochachse, y = Höhe) – auch für Editor-Screenshots.</summary>
    public static void Pose(Vector2 v, Vector3 focus, float dist, out Vector3 pos, out Quaternion rot)
    {
        rot = Quaternion.Euler(v.y, v.x, 0f);
        pos = focus - rot * Vector3.forward * dist;
    }

    /// <summary>Der Modell-Ursprung liegt in der Körpermitte → so weit anheben, dass die Ruhepose auf dem Boden (y = 0) steht.
    /// Ruhepose = Bindepose (das Tripo-Modell, wie es gerigt wurde) – genau die Bodenreferenz, gegen die die Pipeline in
    /// Blender jeden Clip prüft. NICHT die Pose, die Unity nach dem Instantiieren zeigt: das ist der erste Take im FBX
    /// (Attack1, Frame 0) und bei Fliegern/Schwebern schon die Schwebehöhe (Wespe +17,6 cm, Void +5,9 cm) → die Schwebe-
    /// höhe landete auf dem Boden und der Flug "sank ein". Bei laufenden Kreaturen sind beide Posen gleich (±0,0 cm).
    /// Gemessen am echten Mesh, nicht an Renderer.bounds (bei animierten Modellen absichtlich zu groß).</summary>
    public static void PlaceOnGround(GameObject go)
    {
        go.transform.position = Vector3.zero;
        float minY = RestLowestPoint(go);
        go.transform.position = new Vector3(0f, -minY, 0f);
    }

    /// <summary>Tiefster Punkt der Bindepose: Mesh-Ecken (liegen im Raum des Renderers zum Bindezeitpunkt) ohne Skinning.</summary>
    public static float RestLowestPoint(GameObject go)
    {
        float minY = float.MaxValue;
        foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>())
            if (smr.sharedMesh != null)
                foreach (var v in smr.sharedMesh.vertices) minY = Mathf.Min(minY, smr.transform.TransformPoint(v).y);
        foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            if (mf.sharedMesh != null)
                foreach (var v in mf.sharedMesh.vertices) minY = Mathf.Min(minY, mf.transform.TransformPoint(v).y);
        return minY == float.MaxValue ? LowestPoint(go) : minY;
    }

    public static float LowestPoint(GameObject go)
    {
        float minY = float.MaxValue;
        var tmp = new Mesh();
        foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>())
        {
            smr.BakeMesh(tmp, true);                              // Ecken im Raum des Renderers (inkl. Skalierung)
            var t = smr.transform;
            foreach (var v in tmp.vertices) minY = Mathf.Min(minY, (t.position + t.rotation * v).y);
        }
        foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            if (mf.sharedMesh != null)
                foreach (var v in mf.sharedMesh.vertices) minY = Mathf.Min(minY, mf.transform.TransformPoint(v).y);
        if (Application.isPlaying) Destroy(tmp); else DestroyImmediate(tmp);
        return minY == float.MaxValue ? Bounds(go).min.y : minY;
    }

    public static Bounds Bounds(GameObject go)
    {
        var rs = go.GetComponentsInChildren<Renderer>();
        var b = rs.Length > 0 ? rs[0].bounds : new Bounds(go.transform.position, Vector3.one);
        foreach (var r in rs) b.Encapsulate(r.bounds);
        return b;
    }

    // ------------------------------------------------------------------ Bedienung
    void OnGUI()
    {
        if (catalog == null || catalog.entries.Count == 0)
        {
            GUI.Label(new Rect(10, 10, 600, 40), "Keine Kreaturen – Menü Kreaturen › Alle importieren + Szene bauen");
            return;
        }
        float s = Mathf.Max(1f, Screen.height / 900f);
        GUI.matrix = Matrix4x4.Scale(new Vector3(s, s, 1));
        HandleMouse(s);
        GUILayout.BeginArea(new Rect(10, 10, 330, Screen.height / s - 20), GUI.skin.box);

        GUILayout.Label("<b>Kreatur</b>", Rich());
        if (GUILayout.Button((Cur != null ? Cur.name : "–") + "   ▼")) dropdownOpen = !dropdownOpen;
        if (dropdownOpen)
        {
            dropScroll = GUILayout.BeginScrollView(dropScroll, GUILayout.MaxHeight(260));
            for (int i = 0; i < catalog.entries.Count; i++)
            {
                if (GUILayout.Toggle(i == creature, catalog.entries[i].name, "Button") && i != creature)
                {
                    Select(i);
                    dropdownOpen = false;
                }
            }
            GUILayout.EndScrollView();
        }
        var e = Cur;
        GUILayout.Label($"{e.style}\n{e.triangles} Tris · {e.bones} Knochen · {e.materials} Material(ien) · {e.clips.Count} Clips");

        GUILayout.Space(6);
        GUILayout.Label("<b>Animation</b>  (Tasten 1–9)", Rich());
        var labels = e.clips.ConvertAll(c => c.label).ToArray();
        int sel = GUILayout.SelectionGrid(clipIdx, labels, 3);
        if (sel != clipIdx) PlayClip(sel);

        var c = CurClip;
        if (c != null)
        {
            float len = c.clip.length, fps = c.clip.frameRate;
            GUILayout.Space(6);
            autoLoop = GUILayout.Toggle(autoLoop, " Auto-Loop" + (c.loop ? "" : "   (Clip ist eigentlich einmalig)"));
            GUILayout.Label($"Tempo  {speed:0.00}×");
            speed = GUILayout.HorizontalSlider(speed, 0.05f, 3f);
            GUILayout.BeginHorizontal();
            foreach (var p in new[] { 0.1f, 0.25f, 0.5f, 1f, 2f })
                if (GUILayout.Button(p + "×")) speed = p;
            GUILayout.EndHorizontal();

            GUILayout.Space(6);
            GUILayout.Label($"Zeit  {time:0.00} / {len:0.00} s   ·   Frame {Mathf.RoundToInt(time * fps)} / {Mathf.RoundToInt(len * fps)}");
            float t = GUILayout.HorizontalSlider(time, 0f, len);
            if (!Mathf.Approximately(t, time)) { time = t; playing = false; Sample(); }
            GUILayout.BeginHorizontal();
            if (GUILayout.Button(playing ? "❚❚ Pause" : "▶ Abspielen"))
            {
                if (!playing && time >= len) time = 0f;
                playing = !playing;
            }
            if (GUILayout.Button("|◀ Neustart")) { time = 0f; playing = true; }
            if (GUILayout.Button("◀ Frame")) { playing = false; time = Mathf.Max(0, time - 1f / fps); Sample(); }
            if (GUILayout.Button("Frame ▶")) { playing = false; time = Mathf.Min(len, time + 1f / fps); Sample(); }
            GUILayout.EndHorizontal();
        }

        GUILayout.Space(6);
        GUILayout.Label("<b>Kamera</b>  (rechte Maus = drehen, Rad = Zoom)", Rich());
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("ARPG")) view = ViewArpg;
        if (GUILayout.Button("Seite")) view = ViewSide;
        if (GUILayout.Button("Vorne")) view = ViewFront;
        if (GUILayout.Button("Oben")) view = ViewTop;
        GUILayout.EndHorizontal();
        GUILayout.EndArea();
    }

    void HandleMouse(float s)
    {
        var ev = Event.current;
        if (ev.type == EventType.MouseDrag && ev.button == 1)
        {
            view.x += ev.delta.x * 0.4f;
            view.y = Mathf.Clamp(view.y + ev.delta.y * 0.3f, -5f, 89.5f);
            ev.Use();
        }
        else if (ev.type == EventType.ScrollWheel && ev.mousePosition.x * s > 350 * s)
        {
            dist = Mathf.Clamp(dist * (1f + ev.delta.y * 0.05f), size * 0.5f, size * 10f);
            ev.Use();
        }
        else if (ev.type == EventType.KeyDown && ev.keyCode >= KeyCode.Alpha1 && ev.keyCode <= KeyCode.Alpha9)
        {
            PlayClip(ev.keyCode - KeyCode.Alpha1);
            ev.Use();
        }
    }

    static GUIStyle rich;
    static GUIStyle Rich()
    {
        if (rich == null) rich = new GUIStyle(GUI.skin.label) { richText = true };
        return rich;
    }
}
