// Varianten-Baukasten, Schicht 4 „Material-Ebenen“ (docs/VARIANTEN_SPEC.md 4.1–4.3) – EIN Material pro Variante.
// Built-in Render Pipeline (wie das Testprojekt), Surface-Shader, kein Plugin.
//   Farbgruppen (haut, accessoire_a, horn, akzent, augen …): Farbe, Farbe 2 + Farb-Zufall pro Teil, Rauheit, Detail
//     (wie stark die Tripo-Textur durchscheint), Helligkeits-Zufall pro Facette, Leuchten, Glasig (falsche Transparenz).
//   Ebenen (max. 8, Reihenfolge = Liste): verlauf, muster, risse (Glut/Frost … mit Emission + Puls), ueberzug, naesse, rim.
//   Masken: Zonen pro Vertex (aus C#, TEXCOORD5/6), Gruppen-Filter, „oben“ und „rauschen“ pro Pixel.
// Vertex-Daten (VkBuilder.Combine):
//   TEXCOORD2 = (Gruppe hell, Gruppe dunkel | Farb-Zufall Teil, Zufall pro Teil, 1 = Basis / 0 = Accessoire)
//   TEXCOORD3 = Ruhe-Position im Körperraum / Kreaturgröße (x vorn, y oben, z links), w = Höhe im Teil 0..1 (Ansatz → Spitze)
//   TEXCOORD4 = Ruhe-Normale im Körperraum
//   TEXCOORD1 + TANGENT = Nachschwingen (G14, VariantSwing.cginc): Beweglichkeit, Weichheit, Slot/Phase, Länge, Teil-Achse
// Alle Muster hängen an der RUHE-Position → sie kleben beim Laufen am Körper. Facetten-Look über Flächen-Ableitungen.
// Kosten: Editor-Vorschau darf teuer sein. Das gebackene Prefab nutzt seit M2 Texturen + „VariantKit/Baked“.
// Die Rechnung der Ebenen steht in VariantLayers.cginc (gleich für Vorschau und Textur-Backen).
Shader "VariantKit/Layered"
{
    Properties
    {
        _MainTex ("Farbtextur (Basis)", 2D) = "white" {}
        [Normal] _BumpMap ("Normal-Map (Basis)", 2D) = "bump" {}
        _Facetten ("Facetten (0 weich … 1 flach)", Range(0,1)) = 1
        _DarkThreshold ("Dunkel-Schwelle Textur (Krallen/Nase/Augen)", Range(0,1)) = 0.3
        _VKBounds ("Körpermaße (minY, maxY, minX, maxX)", Vector) = (-0.4,0.4,-0.5,0.5)
        [Header(Gruppe 0 haut)] _G0C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G0D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G0P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G0Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 1 bedeckung_1)] _G1C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G1D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G1P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G1Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 2 bedeckung_2)] _G2C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G2D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G2P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G2Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 3 accessoire_a)] _G3C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G3D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G3P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G3Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 4 accessoire_b)] _G4C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G4D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G4P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G4Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 5 accessoire_c)] _G5C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G5D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G5P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G5Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 6 horn)] _G6C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G6D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G6P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G6Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 7 akzent)] _G7C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G7D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G7P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G7Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Gruppe 8 augen)] _G8C ("Farbe (rgb) + Leuchten (a)", Vector) = (0.6,0.6,0.6,0)
        _G8D ("Farbe 2 (rgb) + Farb-Zufall (a)", Vector) = (0.6,0.6,0.6,0)
        _G8P ("Rauheit, Detail, Helligkeit-Zufall, Verlauf", Vector) = (0.8,0.5,0.08,0)
        _G8Q ("Glasig", Vector) = (0,0,0,0)
        [Header(Ebene 0)] _L0T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L0C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L0D ("Farbe B", Vector) = (0,0,0,0)
        _L0A ("Werte A", Vector) = (0,0,0,0)
        _L0B ("Werte B", Vector) = (0,0,0,0)
        _L0M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 1)] _L1T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L1C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L1D ("Farbe B", Vector) = (0,0,0,0)
        _L1A ("Werte A", Vector) = (0,0,0,0)
        _L1B ("Werte B", Vector) = (0,0,0,0)
        _L1M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 2)] _L2T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L2C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L2D ("Farbe B", Vector) = (0,0,0,0)
        _L2A ("Werte A", Vector) = (0,0,0,0)
        _L2B ("Werte B", Vector) = (0,0,0,0)
        _L2M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 3)] _L3T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L3C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L3D ("Farbe B", Vector) = (0,0,0,0)
        _L3A ("Werte A", Vector) = (0,0,0,0)
        _L3B ("Werte B", Vector) = (0,0,0,0)
        _L3M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 4)] _L4T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L4C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L4D ("Farbe B", Vector) = (0,0,0,0)
        _L4A ("Werte A", Vector) = (0,0,0,0)
        _L4B ("Werte B", Vector) = (0,0,0,0)
        _L4M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 5)] _L5T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L5C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L5D ("Farbe B", Vector) = (0,0,0,0)
        _L5A ("Werte A", Vector) = (0,0,0,0)
        _L5B ("Werte B", Vector) = (0,0,0,0)
        _L5M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 6)] _L6T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L6C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L6D ("Farbe B", Vector) = (0,0,0,0)
        _L6A ("Werte A", Vector) = (0,0,0,0)
        _L6B ("Werte B", Vector) = (0,0,0,0)
        _L6M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
        [Header(Ebene 7)] _L7T ("Typ, Art/Mischung, Richtung, -", Vector) = (0,0,0,0)
        _L7C ("Farbe + Intensitaet", Vector) = (0,0,0,0)
        _L7D ("Farbe B", Vector) = (0,0,0,0)
        _L7A ("Werte A", Vector) = (0,0,0,0)
        _L7B ("Werte B", Vector) = (0,0,0,0)
        _L7M ("Staerke, Gruppen-Bits, oben, rauschen", Vector) = (0,0,0,0)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 300

        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows vertex:vert addshadow
        #pragma target 4.0
        #include "VariantLayers.cginc"
        #include "VariantSwing.cginc"

        float _VKTime, _VKUseTime;   // feste Zeit für Prüfbilder/Fenster (global)

        struct appdata_vk
        {
            float4 vertex : POSITION;
            float3 normal : NORMAL;
            float4 tangent : TANGENT;
            float4 texcoord : TEXCOORD0;
            float4 texcoord1 : TEXCOORD1;
            float4 texcoord2 : TEXCOORD2;
            float4 texcoord3 : TEXCOORD3;
            float4 texcoord4 : TEXCOORD4;
            float4 texcoord5 : TEXCOORD5;
            float4 texcoord6 : TEXCOORD6;
            UNITY_VERTEX_INPUT_INSTANCE_ID
        };

        struct Input
        {
            float2 uv_MainTex;
            float3 worldPos;
            float3 worldNormal; INTERNAL_DATA
            float4 grp;
            float4 rest;
            float3 rnrm;
            float4 m0;
            float4 m1;
            float swf;          // 1 = schwingendes Teil (Normal-Map aus, Tangente = Teil-Achse)
        };

        void vert(inout appdata_vk v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.grp = v.texcoord2;
            o.rest = v.texcoord3;
            o.rnrm = v.texcoord4.xyz;
            o.m0 = v.texcoord5;
            o.m1 = v.texcoord6;
            o.swf = step(1e-4, v.texcoord1.y);
            v.vertex.xyz += VKSwingOffsetOS(v.vertex.xyz, v.tangent, v.texcoord1, lerp(_Time.y, _VKTime, _VKUseTime));
        }

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            // Normalen: weich (Tripo-Normal-Map) ↔ facettiert (Flächen-Ableitung)
            float3 wT = WorldNormalVector(IN, float3(1, 0, 0));
            float3 wB = WorldNormalVector(IN, float3(0, 1, 0));
            float3 wN = WorldNormalVector(IN, float3(0, 0, 1));
            float3 flatN = normalize(cross(ddy(IN.worldPos), ddx(IN.worldPos)));
            flatN *= sign(dot(flatN, wN) + 1e-5);
            float3 rn = normalize(IN.rnrm + 1e-5);
            float3 restFlat = normalize(cross(ddy(IN.rest.xyz), ddx(IN.rest.xyz)) + 1e-7);
            restFlat *= sign(dot(restFlat, rn) + 1e-5);

            VKIn vi;
            vi.uv = IN.uv_MainTex; vi.grp = IN.grp; vi.rest = IN.rest; vi.rnrm = IN.rnrm; vi.m0 = IN.m0; vi.m1 = IN.m1;
            vi.restFlat = restFlat;
            vi.edgeTerm = saturate((1 - dot(flatN, wN)) * 6);
            vi.t = lerp(_Time.y, _VKTime, _VKUseTime);
            VKOut r = VKEval(vi);

            float3 nDetail = normalize(r.nTS.x * wT + r.nTS.y * wB + r.nTS.z * wN);
            float3 nW = normalize(lerp(nDetail, flatN, max(_Facetten, IN.swf)));
            float3 V = normalize(_WorldSpaceCameraPos - IN.worldPos);
            float fres = pow(1 - saturate(dot(V, nW)), 3);
            float3 col = r.col + r.glasig * fres * 0.5;
            float3 emis = r.emis + r.rimC.rgb * r.rimC.a * pow(1 - saturate(dot(V, nW)), lerp(6, 1.5, r.rimBreite)) * r.rimMask;
            o.Albedo = saturate(col);
            o.Normal = normalize(float3(dot(nW, wT), dot(nW, wB), dot(nW, wN)));
            o.Metallic = 0;
            o.Smoothness = saturate(1 - r.rough);
            o.Emission = VKCompressEmission(emis);
            o.Alpha = 1;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
