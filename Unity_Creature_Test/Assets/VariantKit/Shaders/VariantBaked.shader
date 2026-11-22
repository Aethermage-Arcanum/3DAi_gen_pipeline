// Varianten-Baukasten – Spiel-Shader der gebackenen Variante (Spec 4.1, E5): EIN Material, feste Kosten, egal wie viele
// Ebenen die Variante hatte. Texturen (je 1024²): Albedo, Maske (R Rauheit, G Puls-Anteil, B Glasig, A Rim-Maske),
// optional Leuchten und Normal. Rim: Stärke × Maske in Maske A, Farbe + Breite als Vertex-Farbe (Körper und Accessoires
// können verschiedene Rim-Ebenen haben). Live bleiben nur: Facetten-Look (Flächen-Ableitung), Glasig-Fresnel, Rim-Light, Puls und
// seit G14 das Nachschwingen der Bedeckung/Gehänge (VariantSwing.cginc, Werte per MaterialPropertyBlock von VariantSchwingen).
Shader "VariantKit/Baked"
{
    Properties
    {
        _MainTex ("Albedo", 2D) = "white" {}
        _MaskTex ("Maske (R Rauheit, G Puls, B Glasig, A Rim)", 2D) = "black" {}
        _EmissionTex ("Leuchten", 2D) = "black" {}
        [Normal] _BumpMap ("Normal", 2D) = "bump" {}
        _Facetten ("Facetten (0 weich … 1 flach)", Range(0,1)) = 1
        _EmissionScale ("Leuchten-Faktor", Float) = 1.25
        _PulsFreq ("Puls (Hz)", Float) = 0
        _PulsStaerke ("Puls-Stärke", Range(0,1)) = 0
        _RimAn ("Rim an (Farbe + Breite pro Vertex, Stärke in Maske A)", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows addshadow vertex:vert
        #pragma target 3.5
        sampler2D _MainTex, _MaskTex, _EmissionTex, _BumpMap;
        half _Facetten, _EmissionScale, _PulsFreq, _PulsStaerke, _RimAn;
        float _VKTime, _VKUseTime;
        #include "VariantSwing.cginc"
        struct Input { float2 uv_MainTex; float3 worldPos; float3 worldNormal; INTERNAL_DATA float swf; float4 rimV; };

        void vert(inout appdata_full v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.swf = step(1e-4, v.texcoord1.y);
            o.rimV = v.color;   // Rim pro Vertex (rgb Farbe, a Breite): Körper- und Accessoire-Rim getrennt
            v.vertex.xyz += VKSwingOffsetOS(v.vertex.xyz, v.tangent, v.texcoord1, lerp(_Time.y, _VKTime, _VKUseTime));
        }

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float4 m = tex2D(_MaskTex, IN.uv_MainTex);
            float3 wT = WorldNormalVector(IN, float3(1, 0, 0));
            float3 wB = WorldNormalVector(IN, float3(0, 1, 0));
            float3 wN = WorldNormalVector(IN, float3(0, 0, 1));
            float3 nTS = UnpackNormal(tex2D(_BumpMap, IN.uv_MainTex));
            float3 nDetail = normalize(nTS.x * wT + nTS.y * wB + nTS.z * wN);
            float3 flatN = normalize(cross(ddy(IN.worldPos), ddx(IN.worldPos)));
            flatN *= sign(dot(flatN, wN) + 1e-5);
            float3 nW = normalize(lerp(nDetail, flatN, max(_Facetten, IN.swf)));
            float3 V = normalize(_WorldSpaceCameraPos - IN.worldPos);
            float nv = 1 - saturate(dot(V, nW));
            float3 col = tex2D(_MainTex, IN.uv_MainTex).rgb + m.b * pow(nv, 3) * 0.5;
            float t = lerp(_Time.y, _VKTime, _VKUseTime);
            float puls = 1 - _PulsStaerke * 0.5 + _PulsStaerke * 0.5 * sin(6.28318 * _PulsFreq * t);
            float3 emis = tex2D(_EmissionTex, IN.uv_MainTex).rgb * _EmissionScale * lerp(1, puls, m.g);
            if (_RimAn > 0.5) emis += IN.rimV.rgb * (m.a * 4) * pow(nv, lerp(6, 1.5, IN.rimV.a));
            o.Albedo = saturate(col);
            o.Normal = normalize(float3(dot(nW, wT), dot(nW, wB), dot(nW, wN)));
            o.Metallic = 0;
            o.Smoothness = saturate(1 - m.r);
            o.Emission = emis;
            o.Alpha = 1;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
