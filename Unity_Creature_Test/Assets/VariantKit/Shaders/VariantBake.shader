// Varianten-Baukasten – Textur-Backen (Spec 4.1): rendert den Ebenen-Stapel im UV-Raum der Atlas-UV (TEXCOORD7).
// Gleiche Rechnung wie die Vorschau (VariantLayers.cginc), beide Ebenen-Gruppen. Ausgabe je nach _VKBakeOut:
//   0 Albedo (rgb, a = 1 = belegt)   1 Maske (R Rauheit, G Puls-Anteil, B Glasig, A Rim-Maske × Stärke / 4)
//   2 Leuchten (rgb komprimiert / 1.25)   3 Normal (Tangentenraum der Basis-UV, 0.5 + 0.5·n)
Shader "Hidden/VariantKit/Bake"
{
    Properties
    {
        _MainTex ("Farbtextur (Basis)", 2D) = "white" {}
        [Normal] _BumpMap ("Normal-Map (Basis)", 2D) = "bump" {}
    }
    SubShader
    {
        Cull Off ZWrite Off ZTest Always
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 4.0
            #include "UnityCG.cginc"
            #include "VariantLayers.cginc"

            float _VKBakeOut;

            struct appdata
            {
                float4 vertex : POSITION;
                float4 uv0 : TEXCOORD0;
                float4 grp : TEXCOORD2;
                float4 rest : TEXCOORD3;
                float4 rnrm : TEXCOORD4;
                float4 m0 : TEXCOORD5;
                float4 m1 : TEXCOORD6;
                float4 atlas : TEXCOORD7;
            };
            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float4 grp : TEXCOORD1;
                float4 rest : TEXCOORD2;
                float3 rnrm : TEXCOORD3;
                float4 m0 : TEXCOORD4;
                float4 m1 : TEXCOORD5;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = float4(v.atlas.x * 2 - 1, v.atlas.y * 2 - 1, 0.5, 1);
                #if UNITY_UV_STARTS_AT_TOP
                o.pos.y = -o.pos.y;
                #endif
                o.uv = v.uv0.xy; o.grp = v.grp; o.rest = v.rest; o.rnrm = v.rnrm.xyz; o.m0 = v.m0; o.m1 = v.m1;
                return o;
            }

            float4 frag(v2f i) : SV_Target
            {
                float3 rn = normalize(i.rnrm + 1e-5);
                float3 restFlat = normalize(cross(ddy(i.rest.xyz), ddx(i.rest.xyz)) + 1e-7);
                restFlat *= sign(dot(restFlat, rn) + 1e-5);
                VKIn vi;
                vi.uv = i.uv; vi.grp = i.grp; vi.rest = i.rest; vi.rnrm = i.rnrm; vi.m0 = i.m0; vi.m1 = i.m1;
                vi.restFlat = restFlat;
                vi.edgeTerm = saturate((1 - dot(restFlat, rn)) * 6);
                vi.t = 0;
                VKOut r = VKEval(vi);
                float3 eAll = r.emisConst + r.emisPuls;
                if (_VKBakeOut < 0.5) return float4(saturate(r.col), 1);
                if (_VKBakeOut < 1.5)
                {
                    float lp = dot(r.emisPuls, float3(0.3, 0.6, 0.1)), la = dot(eAll, float3(0.3, 0.6, 0.1));
                    // A = Rim-Maske × Stärke / 4 (Farbe + Breite stehen pro Vertex im Spiel-Mesh: Körper und Accessoires getrennt)
                    return float4(saturate(r.rough), saturate(lp / max(la, 1e-4)), saturate(r.glasig), saturate(r.rimMask * r.rimC.a * 0.25));
                }
                if (_VKBakeOut < 2.5) return float4(saturate(VKCompressEmission(eAll) / 1.25), 1);
                return float4(normalize(r.nTS) * 0.5 + 0.5, 1);
            }
            ENDCG
        }
    }
}
