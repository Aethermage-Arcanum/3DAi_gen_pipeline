using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>Varianten-Baukasten, Schicht 1 „Statur“ (Knochen-Regler, Typ K/G der Spec): skaliert/streckt Knochen NACH der
/// Animation (LateUpdate), damit die gemeinsamen Clips des Musters weiterlaufen. Die Formziele (Typ S: Rumpfdicke,
/// Buckel …) stecken schon fest im gebackenen Mesh und kosten hier nichts.
///   scales   = feste lokale Skalierung pro Knochen (gleichmäßig, mit Ausgleich am Kind → Kinder behalten ihre Größe)
///   stretches= Kind-Knochen entlang der Knochenachse des Elternteils verschieben (Hals/Rumpf länger, ohne dicker zu werden)
///   offsets  = Verschiebung im Raum des Modells (Spurbreite, Bodenhöhe der Hüfte)
/// Kosten: ein paar Dutzend Transform-Zugriffe pro Gegner und Frame. Exakt (Ruhepose eingebacken, Clips neu gebacken)
/// wird es erst mit dem Blender-Backen (Meilenstein 2) – bis dahin können die Füße bei geänderter Beinlänge leicht rutschen.</summary>
[ExecuteAlways, DisallowMultipleComponent]
public class VariantStatur : MonoBehaviour
{
    [Serializable] public struct BoneScale { public string bone; public Vector3 localScale; }
    [Serializable] public struct BoneStretch { public string bone; public Vector3 parentAxis; public float factor; }
    [Serializable] public struct BoneOffset { public string bone; public Vector3 modelOffset; }

    public List<BoneScale> scales = new List<BoneScale>();
    public List<BoneStretch> stretches = new List<BoneStretch>();
    public List<BoneOffset> offsets = new List<BoneOffset>();

    Transform[] sBones, tBones, oBones;
    // Schutz gegen Aufsummieren, wenn kein Animator schreibt (Editor, Pause): letzte geschriebene + Ausgangswerte
    readonly Dictionary<Transform, (Vector3 written, Vector3 source)> state = new Dictionary<Transform, (Vector3, Vector3)>();

    void OnEnable() { Bind(); }

    public void Bind()
    {
        var map = new Dictionary<string, Transform>();
        foreach (var t in GetComponentsInChildren<Transform>(true)) if (!map.ContainsKey(t.name)) map[t.name] = t;
        Transform Find(string n) => map.TryGetValue(n, out var t) ? t : null;
        sBones = scales.ConvertAll(s => Find(s.bone)).ToArray();
        tBones = stretches.ConvertAll(s => Find(s.bone)).ToArray();
        oBones = offsets.ConvertAll(s => Find(s.bone)).ToArray();
        state.Clear();
    }

    void LateUpdate() { Apply(); }

    public void Apply()
    {
        if (sBones == null || sBones.Length != scales.Count || tBones.Length != stretches.Count || oBones.Length != offsets.Count) Bind();
        for (int i = 0; i < scales.Count; i++)
            if (sBones[i] != null) sBones[i].localScale = scales[i].localScale;

        // lokale Positionen: Ausgangswert = was der Animator geschrieben hat (oder der zuletzt gemerkte, falls niemand schrieb)
        var touched = new Dictionary<Transform, Vector3>();
        Vector3 Src(Transform b)
        {
            if (touched.TryGetValue(b, out var cur)) return cur;
            var lp = b.localPosition;
            if (state.TryGetValue(b, out var s) && (lp - s.written).sqrMagnitude < 1e-12f) lp = s.source;
            state[b] = (Vector3.zero, lp);
            return lp;
        }
        for (int i = 0; i < stretches.Count; i++)
        {
            var b = tBones[i];
            if (b == null) continue;
            var lp = Src(b);
            var a = stretches[i].parentAxis;
            touched[b] = lp + (stretches[i].factor - 1f) * Vector3.Dot(lp, a) * a;
        }
        for (int i = 0; i < offsets.Count; i++)
        {
            var b = oBones[i];
            if (b == null || b.parent == null) continue;
            var lp = Src(b);
            var w = transform.TransformVector(offsets[i].modelOffset);
            touched[b] = lp + b.parent.InverseTransformVector(w);
        }
        foreach (var kv in touched)
        {
            kv.Key.localPosition = kv.Value;
            state[kv.Key] = (kv.Value, state[kv.Key].source);
        }
    }
}
