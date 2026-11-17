using System.Collections.Generic;
using UnityEngine;

/// <summary>Liste aller importierten Kreaturen mit ihren Clips. Wird vom Menü "Kreaturen" automatisch erzeugt
/// (Editor/CreatureImporter.cs) – nicht von Hand pflegen.</summary>
public class CreatureCatalog : ScriptableObject
{
    [System.Serializable]
    public class Clip
    {
        public string label;          // kurzer Name, z. B. "Walk"
        public AnimationClip clip;
        public bool loop;             // laut Pipeline (clips_report.json) ein Schleifen-Clip
    }

    [System.Serializable]
    public class Entry
    {
        public string name;           // z. B. "RavineStalker"
        public string style;          // z. B. "Quadruped_Wolf"
        public GameObject model;
        public List<Clip> clips = new List<Clip>();
        public int triangles;
        public int bones;
        public int materials;
    }

    public List<Entry> entries = new List<Entry>();
}
