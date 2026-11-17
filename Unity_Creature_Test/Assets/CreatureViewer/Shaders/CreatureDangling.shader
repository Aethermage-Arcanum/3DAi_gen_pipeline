// Standard-Look der Kreaturen (wie Unitys "Standard": Farbe + Normal-Map, Metallic/Glätte) PLUS frei hängende Teile:
// Vertices, die die Pipeline markiert hat (rigging/dangling.py → Vertex-Farbe R), schwingen weich – ohne Knochen.
//   Vertex-Farbe R = Gewicht   0 = starr (folgt nur dem Rig), 1 = schwingt voll; steigt vom Ansatz zur Spitze
//   Vertex-Farbe G = Phase     pro Teil (Lappen/Fühler) eigene Phase → nicht alle im Gleichtakt
// Bewegung: je Achse zwei überlagerte Sinuswellen mit krummen Frequenzverhältnissen (wirkt organisch, wiederholt sich
// kaum), Welle läuft vom Ansatz zur Spitze (_DangleLag). Versatz in Weltkoordinaten (Meter × Objekt-Skalierung),
// nach dem Skinning → funktioniert mit jeder Animation. Schatten schwingen mit (addshadow).
// Kosten: ~20 Rechenschritte pro Vertex im Vertex-Shader, kein zusätzlicher Draw Call, keine Knochen.
// Kreaturen ohne Markierung bekommen weiter den normalen Standard-Shader (CreatureImporter.EnsureMaterial).
Shader "Creature/Standard Dangling"
{
    Properties
    {
        _Color ("Farbe", Color) = (1,1,1,1)
        _MainTex ("Farbtextur", 2D) = "white" {}
        [Normal] _BumpMap ("Normal-Map", 2D) = "bump" {}
        _BumpScale ("Normal-Stärke", Float) = 1
        _Glossiness ("Glätte", Range(0,1)) = 0.2
        [Gamma] _Metallic ("Metallisch", Range(0,1)) = 0

        [Header(Frei haengende Teile)]
        _DangleAmplitude ("Ausschlag an der Spitze (m)", Range(0, 0.3)) = 0.02
        _DangleFrequency ("Tempo (Schwingungen pro s)", Range(0, 4)) = 0.7
        _DangleLag ("Verzoegerung Ansatz bis Spitze (rad)", Range(0, 6.3)) = 1.5
        _DangleVertical ("Anteil auf-ab", Range(0, 1)) = 0.3
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 300

        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows vertex:vert addshadow
        #pragma target 3.0

        sampler2D _MainTex;
        sampler2D _BumpMap;
        half _BumpScale;
        half _Glossiness;
        half _Metallic;
        fixed4 _Color;
        float _DangleAmplitude, _DangleFrequency, _DangleLag, _DangleVertical;
        // Nur für Prüfbilder: feste Zeit statt _Time (global gesetzt, sonst 0 → normale Zeit)
        float _DangleTestTime, _DangleUseTestTime;

        struct Input { float2 uv_MainTex; };

        void vert(inout appdata_full v)
        {
            float w = v.color.r;
            float t = lerp(_Time.y, _DangleTestTime, _DangleUseTestTime);
            float ph = v.color.g * 6.2831853 + w * _DangleLag;          // eigene Phase je Teil + Welle zur Spitze
            float a = t * _DangleFrequency * 6.2831853 - ph;
            float3 d;
            d.x = 0.75 * sin(a)               + 0.25 * sin(a * 2.13 + 1.7);
            d.z = 0.75 * sin(a * 0.81 + 2.4)  + 0.25 * sin(a * 1.87 + 0.6);
            d.y = _DangleVertical * (0.7 * sin(a * 1.31 + 4.1) + 0.3 * sin(a * 2.71));
            float scale = length(unity_ObjectToWorld._m00_m10_m20);       // Kreatur größer skaliert → Ausschlag mit
            float3 worldOffset = d * (_DangleAmplitude * scale * w);
            v.vertex.xyz += mul((float3x3)unity_WorldToObject, worldOffset);
        }

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            fixed4 c = tex2D(_MainTex, IN.uv_MainTex) * _Color;
            o.Albedo = c.rgb;
            o.Normal = UnpackScaleNormal(tex2D(_BumpMap, IN.uv_MainTex), _BumpScale);
            o.Metallic = _Metallic;
            o.Smoothness = _Glossiness;
            o.Alpha = 1;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
