using System;
using UnityEngine;

/// <summary>Varianten-Baukasten G14 „Nachschwingen im Shader“ (Foliage-Trick): Fell, Federn, Fransen, Tang und Ketten
/// schwingen beim Anlaufen, Bremsen, Drehen und bei Treffern gedämpft nach – ohne Physik und ohne Zusatz-Knochen.
/// Pro Gegner 4 kleine Federn (Ansatz-Knochen Hüfte, Brust, Kopf, Schwanz). Jede misst die Geschwindigkeit ihres Knochens
/// und schwingt der Änderung hinterher. Ergebnis = 4 Vektoren per MaterialPropertyBlock an den Shader
/// (VariantSwing.cginc). Wie stark ein Vertex mitgeht, steht im Mesh: Beweglichkeit (Wurzel 0 … Spitze 1) × Weichheit der
/// Lage bzw. des Accessoires. Ohne diese Komponente (oder mit <see cref="an"/> = false) bleibt das Mesh exakt starr.
/// Stöße: <see cref="VKStoss"/> ist Empfänger der Clip-Events (hit, slam – im Baukasten aus &lt;Name&gt;_events.json in die
/// Clips der Basis-Kopie geschrieben), <see cref="Treffer"/> für Treffer aus einer Richtung (Spiel-Code).
/// Kosten: 4 Transform-Positionen + ~60 Rechenschritte + 1 SetPropertyBlock pro Gegner und Frame.</summary>
[DisallowMultipleComponent, DefaultExecutionOrder(100)]
public class VariantSchwingen : MonoBehaviour
{
    public const int Slots = 4;
    public static readonly string[] SlotNamen = { "Hüfte", "Brust", "Kopf", "Schwanz" };

    [Tooltip("Ansatz-Knochen der 4 Federn (Hüfte, Brust, Kopf, Schwanz). Leer = Feder des Rumpfs (Slot 0) übernimmt.")]
    public Transform[] ansatz = new Transform[Slots];
    [Tooltip("Renderer mit Material „VariantKit/Layered“ oder „VariantKit/Baked“ (leer = alle darunter)")]
    public Renderer[] ziele;
    [Tooltip("Kreaturgröße in Metern bei Skalierung 1 (Teil-Längen im Mesh sind Anteile davon)")]
    public float groesse = 1.5f;
    public bool an = true;

    [Header("Trägheit (Anlaufen, Bremsen, Drehen)")]
    [Range(0, 3)] public float traegheit = 1.5f;
    [Tooltip("Eigenfrequenz der Feder (Hz): klein = träge, groß = zappelig")]
    [Range(0.3f, 5)] public float frequenz = 1.6f;
    [Tooltip("Dämpfung: 0,1 schwingt lange nach, 1 kommt ohne Überschwingen zur Ruhe")]
    [Range(0.05f, 1)] public float daempfung = 0.2f;
    [Tooltip("Fahrtwind: Spitzen zeigen beim Laufen nach hinten (rad pro m/s)")]
    [Range(0, 0.3f)] public float fahrtwind = 0.15f;
    [Range(0.1f, 1.4f)] public float maxAusschlag = 0.8f;

    [Header("Wackeln (Wind/Rauschen)")]
    [Range(0, 0.4f)] public float wackeln = 0.04f;
    [Range(0, 5)] public float wackelTempo = 1.1f;

    [Header("Stöße (Clip-Events hit/slam, Treffer)")]
    [Range(0, 3)] public float stoss = 1f;
    [Range(0, 0.4f)] public float zittern = 0.15f;
    [Header("Gehänge")]
    [Tooltip("Wie stark Fransen/Tang/Ketten der Schwerkraft folgen, wenn sich der Körper neigt")]
    [Range(0, 1)] public float schwerkraft = 0.7f;

    [Header("Vorschau / Prüfbilder")]
    [Tooltip("true = Step(dt) wird von außen aufgerufen (Editor-Fenster, Batch); sonst in LateUpdate")]
    public bool manuell;
    [Tooltip("zusätzliche Geschwindigkeit (Welt, m/s) – z. B. Laufband in der Vorschau, wo das Modell nicht wandert")]
    public Vector3 zusatzGeschwindigkeit;

    // Zustand pro Feder
    readonly Vector3[] pPrev = new Vector3[Slots], vPrev = new Vector3[Slots], X = new Vector3[Slots], V = new Vector3[Slots];
    bool init;
    float shake, tempo;
    MaterialPropertyBlock mpb;
    static readonly int idS0 = Shader.PropertyToID("_VKS0"), idS1 = Shader.PropertyToID("_VKS1"), idS2 = Shader.PropertyToID("_VKS2"),
        idS3 = Shader.PropertyToID("_VKS3"), idSwing = Shader.PropertyToID("_VKSwing"), idSwingB = Shader.PropertyToID("_VKSwingB");

    public Vector3 Auslenkung(int slot) => Soft(X[slot]);   // wie an den Shader gegeben
    public float Tempo => tempo;

    void OnEnable() { init = false; if (ziele == null || ziele.Length == 0) ziele = GetComponentsInChildren<Renderer>(true); }

    void OnDisable() => Clear();

    void LateUpdate() { if (!manuell) Step(Time.deltaTime); }

    /// <summary>Alle Federn zurücksetzen (z. B. nach Teleport / Spawnen aus dem Pool).</summary>
    public void Zuruecksetzen() => init = false;

    /// <summary>Eine Zeitscheibe rechnen und an den Shader geben.</summary>
    public void Step(float dt)
    {
        if (!an) { Clear(); return; }
        if (dt <= 0) { Apply(); return; }
        dt = Mathf.Min(dt, 0.1f);
        var root = ansatz.Length > 0 && ansatz[0] != null ? ansatz[0] : transform;
        if (!init)
        {
            for (int i = 0; i < Slots; i++) { pPrev[i] = Pos(i, root); vPrev[i] = zusatzGeschwindigkeit; X[i] = V[i] = Vector3.zero; }
            init = true;
        }
        float w = 2 * Mathf.PI * frequenz, z = daempfung;
        float kick = traegheit / Mathf.Max(0.05f, 0.4f * groesse * transform.lossyScale.x);   // Pendel: θ'' = −a / ℓ (ℓ ≈ 0,4 × Größe)
        int sub = Mathf.Clamp(Mathf.CeilToInt(dt * 120f), 1, 8);
        float h = dt / sub;
        for (int i = 0; i < Slots; i++)
        {
            var p = Pos(i, root);
            var v = (p - pPrev[i]) / dt + zusatzGeschwindigkeit;
            var dv = v - vPrev[i];
            if (dv.sqrMagnitude > 900f) dv = Vector3.zero;       // Teleport
            pPrev[i] = p; vPrev[i] = v;
            if (i == 0) tempo = new Vector2(v.x, v.z).magnitude;
            V[i] -= dv * kick;
            var target = new Vector3(-v.x, 0, -v.z) * fahrtwind;
            for (int s = 0; s < sub; s++)
            {
                V[i] += (w * w * (target - X[i]) - 2 * z * w * V[i]) * h;
                X[i] += V[i] * h;
            }
            float m = X[i].magnitude;
            if (m > 1.5f * maxAusschlag) { X[i] *= 1.5f * maxAusschlag / m; V[i] *= 0.5f; }
        }
        shake *= Mathf.Exp(-dt * 5f);
        Apply();
    }

    Vector3 Pos(int i, Transform root) => (i < ansatz.Length && ansatz[i] != null ? ansatz[i] : root).position;

    /// <summary>Empfänger der Clip-Events (Funktion „VKStoss“, Text = Event aus &lt;Name&gt;_events.json).</summary>
    public void VKStoss(string art) => Stoss(art);

    /// <summary>Stoß: „slam“ (Spitzen fliegen nach unten), „hit“ (Schlag nach vorn, Spitzen schnellen nach vorn),
    /// „getroffen“ (von vorn getroffen). Andere Events (footstep, dead) wirken nicht.</summary>
    public void Stoss(string art, float staerke = 1f)
    {
        var fwd = Vorn();
        switch (art)
        {
            case "slam": Kick(Vector3.down * 3.5f + fwd * 3.5f, staerke, 1f); break;
            case "hit": Kick(fwd * 4.0f + Vector3.down * 1.0f, staerke, 0.8f); break;
            case "getroffen": Kick(-fwd * 3.5f, staerke, 1f); break;
        }
    }

    /// <summary>Treffer aus einer Richtung (Welt, zeigt vom Angreifer zum Gegner).</summary>
    public void Treffer(Vector3 richtung, float staerke = 1f) => Kick(richtung.normalized * 3.5f, staerke, 1f);

    void Kick(Vector3 dir, float staerke, float zitter)
    {
        if (!an) return;
        float k = stoss * staerke;
        for (int i = 0; i < Slots; i++) V[i] += dir * k * (i == 2 ? 1.2f : 1f);
        shake = Mathf.Max(shake, Mathf.Clamp01(zitter * k));
    }

    Vector3 Vorn()
    {
        if (ansatz.Length > 2 && ansatz[0] != null && ansatz[2] != null)
        {
            var f = ansatz[2].position - ansatz[0].position; f.y = 0;
            if (f.sqrMagnitude > 1e-6f) return f.normalized;
        }
        return transform.forward;
    }

    void Apply()
    {
        if (mpb == null) mpb = new MaterialPropertyBlock();
        // weiche Begrenzung (tanh): große Ausschläge laufen sanft in maxAusschlag statt hart abzuschneiden
        mpb.SetVector(idS0, Soft(X[0])); mpb.SetVector(idS1, Soft(X[1])); mpb.SetVector(idS2, Soft(X[2])); mpb.SetVector(idS3, Soft(X[3]));
        mpb.SetVector(idSwing, new Vector4(shake, tempo, groesse * transform.lossyScale.x, 1));
        mpb.SetVector(idSwingB, new Vector4(wackeln, wackelTempo, zittern * stoss, schwerkraft));
        if (ziele == null) return;
        foreach (var r in ziele) if (r != null) r.SetPropertyBlock(mpb);
    }

    Vector4 Soft(Vector3 x)
    {
        float m = x.magnitude;
        if (m < 1e-6f) return Vector4.zero;
        float e = Mathf.Exp(-2f * m / maxAusschlag);
        return x * (maxAusschlag * (1 - e) / (1 + e) / m);
    }

    void Clear()
    {
        if (ziele == null) return;
        foreach (var r in ziele) if (r != null) r.SetPropertyBlock(null);
    }

    /// <summary>Slot eines Knochens nach Namen (Standard-Vierbeiner; andere Skelette fallen auf Slot 0 zurück).</summary>
    public static int SlotFuer(string knochen)
    {
        if (string.IsNullOrEmpty(knochen)) return 0;
        if (knochen.StartsWith("Tail")) return 3;
        if (knochen == "Head" || knochen == "Jaw" || knochen == "Neck_2" || knochen.StartsWith("Ear") || knochen.StartsWith("Crown")) return 2;
        if (knochen == "Chest" || knochen == "Neck_1" || knochen.StartsWith("Leg_F") || knochen.StartsWith("Arm")) return 1;
        return 0;
    }

    /// <summary>Standard-Knochen der 4 Slots.</summary>
    public static readonly string[][] SlotKnochen =
    {
        new[] { "Hips", "Pelvis", "Spine_1", "Root" },
        new[] { "Chest", "Spine_2", "Neck_1" },
        new[] { "Head", "Neck_2", "Crown" },
        new[] { "Tail_3", "Tail_2", "Tail_1" },
    };

    /// <summary>C13: Kreaturen mit „Creature/Standard Dangling“ + Schalter Nachschwingen (z. B. Bog Warden) bekommen die
    /// Komponente beim Szenen-Start automatisch (CreatureViewer-Szene). Gebackene Varianten haben sie schon im Prefab.</summary>
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void AutoAttach()
    {
        foreach (var r in FindObjectsByType<SkinnedMeshRenderer>(FindObjectsSortMode.None))
        {
            var m = r.sharedMaterial;
            if (m == null || !m.IsKeywordEnabled("_VK_NACHSCHWINGEN") || r.GetComponentInParent<VariantSchwingen>() != null) continue;
            var anim = r.GetComponentInParent<Animator>();
            var go = anim != null ? anim.gameObject : r.transform.root.gameObject;
            var sw = go.AddComponent<VariantSchwingen>();
            sw.Binden();
            sw.groesse = Mathf.Max(0.3f, r.bounds.size.magnitude / Mathf.Max(1e-4f, go.transform.lossyScale.x) * 0.6f);
        }
    }

    /// <summary>Ansatz-Knochen nach Namen suchen (beim Backen bzw. in der Vorschau).</summary>
    public void Binden()
    {
        var all = GetComponentsInChildren<Transform>(true);
        ansatz = new Transform[Slots];
        for (int i = 0; i < Slots; i++)
            foreach (var n in SlotKnochen[i])
            {
                var t = Array.Find(all, x => x.name == n);
                if (t != null) { ansatz[i] = t; break; }
            }
        ziele = GetComponentsInChildren<Renderer>(true);
        init = false;
    }
}
