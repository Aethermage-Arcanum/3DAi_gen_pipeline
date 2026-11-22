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
// Alle Muster hängen an der RUHE-Position → sie kleben beim Laufen am Körper. Facetten-Look über Flächen-Ableitungen.
// Kosten: Editor-Vorschau darf teuer sein. Im Spiel später gebackene Texturen + einfacher Shader (Meilenstein 2);
// in M1 läuft dieser Shader auch im gebackenen Prefab (1 Material, 1 Draw Call, aber mehr Rechenarbeit pro Pixel).
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

        sampler2D _MainTex;
        sampler2D _BumpMap;
        half _Facetten, _DarkThreshold;
        float4 _VKBounds;
        float _VKTime, _VKUseTime;   // feste Zeit für Prüfbilder/Fenster (global)

        #define GDECL(n) float4 _G##n##C, _G##n##D, _G##n##P, _G##n##Q;
        GDECL(0) GDECL(1) GDECL(2) GDECL(3) GDECL(4) GDECL(5) GDECL(6) GDECL(7) GDECL(8)
        #define LDECL(n) float4 _L##n##T, _L##n##C, _L##n##D, _L##n##A, _L##n##B, _L##n##M;
        LDECL(0) LDECL(1) LDECL(2) LDECL(3) LDECL(4) LDECL(5) LDECL(6) LDECL(7)

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
        };

        void vert(inout appdata_vk v, out Input o)
        {
            UNITY_INITIALIZE_OUTPUT(Input, o);
            o.grp = v.texcoord2;
            o.rest = v.texcoord3;
            o.rnrm = v.texcoord4.xyz;
            o.m0 = v.texcoord5;
            o.m1 = v.texcoord6;
        }

        // ---------------------------------------------------------------- Rauschen (Ruhe-Raum)
        float hash13(float3 p) { p = frac(p * 0.1031); p += dot(p, p.zyx + 31.32); return frac((p.x + p.y) * p.z); }
        float3 hash33(float3 p) { p = frac(p * float3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return frac((p.xxy + p.yxx) * p.zyx); }
        float vnoise(float3 p)
        {
            float3 i = floor(p), f = frac(p); f = f * f * (3 - 2 * f);
            return lerp(lerp(lerp(hash13(i), hash13(i + float3(1,0,0)), f.x), lerp(hash13(i + float3(0,1,0)), hash13(i + float3(1,1,0)), f.x), f.y),
                        lerp(lerp(hash13(i + float3(0,0,1)), hash13(i + float3(1,0,1)), f.x), lerp(hash13(i + float3(0,1,1)), hash13(i + float3(1,1,1)), f.x), f.y), f.z);
        }
        float fbm(float3 p) { return vnoise(p) * 0.5 + vnoise(p * 2.03 + 7.1) * 0.3 + vnoise(p * 4.07 + 3.3) * 0.2; }
        // Voronoi: x = Abstand zur nächsten Zellmitte, y = Abstand zur Zellgrenze (≈ (F2-F1)/2)
        float2 voronoi(float3 p)
        {
            float3 i = floor(p), f = frac(p);
            float d1 = 8, d2 = 8; float3 c1 = 0, c2 = 0;
            for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++)
            {
                float3 g = float3(x, y, z); float3 o = hash33(i + g); float3 r = g + o - f; float d = dot(r, r);
                if (d < d1) { d2 = d1; c2 = c1; d1 = d; c1 = r; } else if (d < d2) { d2 = d; c2 = r; }
            }
            float edge = dot(0.5 * (c1 + c2), normalize(c2 - c1));
            return float2(sqrt(d1), abs(edge));
        }
        float3 overlay3(float3 a, float3 b) { return lerp(2 * a * b, 1 - 2 * (1 - a) * (1 - b), step(0.5, a)); }
        float3 mixmode(float3 col, float3 c, float m, float mode)
        {
            if (mode < 0.5) return col * lerp(1, c, m);
            if (mode < 1.5) return lerp(col, overlay3(col, c), m);
            return lerp(col, c, m);
        }

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float4 GC[9] = { _G0C, _G1C, _G2C, _G3C, _G4C, _G5C, _G6C, _G7C, _G8C };
            float4 GD[9] = { _G0D, _G1D, _G2D, _G3D, _G4D, _G5D, _G6D, _G7D, _G8D };
            float4 GP[9] = { _G0P, _G1P, _G2P, _G3P, _G4P, _G5P, _G6P, _G7P, _G8P };
            float4 GQ[9] = { _G0Q, _G1Q, _G2Q, _G3Q, _G4Q, _G5Q, _G6Q, _G7Q, _G8Q };
            float4 LT[8] = { _L0T, _L1T, _L2T, _L3T, _L4T, _L5T, _L6T, _L7T };
            float4 LC[8] = { _L0C, _L1C, _L2C, _L3C, _L4C, _L5C, _L6C, _L7C };
            float4 LD[8] = { _L0D, _L1D, _L2D, _L3D, _L4D, _L5D, _L6D, _L7D };
            float4 LA[8] = { _L0A, _L1A, _L2A, _L3A, _L4A, _L5A, _L6A, _L7A };
            float4 LB[8] = { _L0B, _L1B, _L2B, _L3B, _L4B, _L5B, _L6B, _L7B };
            float4 LM[8] = { _L0M, _L1M, _L2M, _L3M, _L4M, _L5M, _L6M, _L7M };
            float LMask[8] = { IN.m0.x, IN.m0.y, IN.m0.z, IN.m0.w, IN.m1.x, IN.m1.y, IN.m1.z, IN.m1.w };

            float isBase = step(0.5, IN.grp.w);
            float3 p = IN.rest.xyz;
            float3 rn = normalize(IN.rnrm + 1e-5);
            float3 tex = tex2D(_MainTex, IN.uv_MainTex).rgb;
            float lum = dot(tex, float3(0.299, 0.587, 0.114));
            float dark = isBase * step(lum, _DarkThreshold);
            int g = (int)round(lerp(IN.grp.x, IN.grp.y, dark));
            g = clamp(g, 0, 8);

            // Normalen: weich (Tripo-Normal-Map) ↔ facettiert (Flächen-Ableitung)
            float3 wT = WorldNormalVector(IN, float3(1, 0, 0));
            float3 wB = WorldNormalVector(IN, float3(0, 1, 0));
            float3 wN = WorldNormalVector(IN, float3(0, 0, 1));
            float3 nTS = lerp(float3(0, 0, 1), UnpackNormal(tex2D(_BumpMap, IN.uv_MainTex)), isBase);
            float3 nDetail = normalize(nTS.x * wT + nTS.y * wB + nTS.z * wN);
            float3 flatN = normalize(cross(ddy(IN.worldPos), ddx(IN.worldPos)));
            flatN *= sign(dot(flatN, wN) + 1e-5);
            float3 nW = normalize(lerp(nDetail, flatN, _Facetten));
            float3 V = normalize(_WorldSpaceCameraPos - IN.worldPos);
            float edgeTerm = saturate((1 - dot(flatN, wN)) * 6);   // Kanten/Facettenwechsel (für Überzug „kanten“)

            // ---- Farbgruppe
            float4 C = GC[g], D = GD[g], P = GP[g], Q = GQ[g];
            float3 col = C.rgb;
            float fz = max(IN.grp.y * (1 - isBase), D.a);
            float r1 = IN.grp.z, r2 = frac(r1 * 7.31 + 0.37);
            float mixv = (1 - isBase) * (r1 < fz ? 0.85 + 0.15 * r2 : r2 * 0.18 * step(0.001, fz));
            col = lerp(C.rgb, D.rgb, mixv);
            col = lerp(col, lerp(C.rgb, D.rgb, IN.rest.w), P.w * (1 - isBase));
            float texRef = lerp(0.85, 0.12, dark);
            col *= lerp(1, saturate(lum / texRef), P.y * isBase);   // nur Helligkeit der Tripo-Textur, Farbton kommt aus der Gruppe
            float3 restFlat = normalize(cross(ddy(p), ddx(p)) + 1e-7);
            float fh = hash13(floor(restFlat * 37.0 + 50.0) + floor(p * 9.0) * 0.0 + r1 * 13.0);
            col *= 1 + (fh - 0.5) * 2 * P.z;
            float rough = P.x;
            float3 emis = C.rgb * C.a;
            float fres = pow(1 - saturate(dot(V, nW)), 3);
            col += Q.x * fres * 0.5; rough = lerp(rough, 0.1, Q.x * 0.5);

            float t = lerp(_Time.y, _VKTime, _VKUseTime);
            float up01 = rn.y * 0.5 + 0.5;

            // ---- Ebenen
            [loop] for (int i = 0; i < 8; i++)
            {
                float typ = LT[i].x;
                if (typ < 0.5) continue;
                float4 M = LM[i];
                float m = LMask[i] * M.x;
                m *= fmod(floor(M.y / exp2((float)g) + 1e-3), 2.0);
                if (M.z > 0) m *= lerp(1, smoothstep(0.45, 0.85, up01), M.z);
                if (M.z < 0) m *= lerp(1, smoothstep(0.45, 0.85, 1 - up01), -M.z);
                if (M.w > 0) m *= saturate(1 - M.w + M.w * 2.2 * fbm(p * 14 + i * 3.1));
                if (m <= 0.001) continue;
                float4 A = LA[i], B = LB[i], LCi = LC[i];
                if (typ < 1.5)            // verlauf
                {
                    float ty = LT[i].z < 0.5 ? (p.y - _VKBounds.x) / max(1e-4, _VKBounds.y - _VKBounds.x)
                             : LT[i].z < 1.5 ? (p.x - _VKBounds.z) / max(1e-4, _VKBounds.w - _VKBounds.z) : IN.rest.w;
                    float tt = smoothstep(A.x - A.y * 0.5 - 1e-3, A.x + A.y * 0.5 + 1e-3, ty);
                    col = mixmode(col, lerp(LD[i].rgb, LCi.rgb, tt), m, LT[i].y);
                }
                else if (typ < 2.5)       // muster
                {
                    float3 q = p / max(0.005, A.x) + B.x;
                    float art = LT[i].z, v = 0;
                    float warp = fbm(q * 0.7) * A.w * 4;
                    float coord = LT[i].w < 0.5 ? q.y : q.x;
                    if (art < 0.5) v = smoothstep(0.1, -0.1, sin((coord + warp) * 3.14159) + (1 - 2 * A.y));
                    else if (art < 1.5) v = smoothstep(1 - A.y - 0.06, 1 - A.y + 0.06, fbm(q + warp * 0.3));
                    else if (art < 2.5) v = 1 - smoothstep(A.y * 0.45, A.y * 0.45 + 0.08, voronoi(q).x);
                    else if (art < 3.5) v = smoothstep(0.1, -0.1, sin((length(q.xz) + warp) * 3.14159) + (1 - 2 * A.y));
                    else if (art < 4.5) v = smoothstep(0.2, -0.2, sin((q.x + q.y * 0.5 + warp * 2) * 3.14159) + (1 - 2 * A.y));
                    else v = 1 - smoothstep(0.02, 0.06 + A.y * 0.05, voronoi(q).y);
                    col = mixmode(col, LCi.rgb, v * A.z * m, LT[i].y);
                }
                else if (typ < 3.5)       // risse / adern / zellfugen
                {
                    float freq = lerp(4, 16, A.y);
                    float3 q = p * freq + B.z;
                    float art = LT[i].y;
                    float wL = max(A.x, 0.0005);
                    float ln = 0, e = 1, gate = 1;
                    if (art < 0.5 || art > 2.5)      // risse (+ Runen = Risse)
                    {
                        e = voronoi(q + fbm(q * 0.8) * 0.6).y / freq;
                        ln = 1 - smoothstep(wL * 0.5, wL, e);
                        float2 v2 = voronoi(q * 2.3 + 11.0);
                        float e2 = v2.y / (freq * 2.3);
                        ln = max(ln, (1 - smoothstep(wL * 0.3, wL * 0.6, e2)) * A.z * step(0.55, hash13(floor(q * 2.3 + 11.0))));
                        gate = smoothstep(0.54, 0.66, fbm(q * 0.4 + 5.0)); ln *= gate;
                    }
                    else if (art < 1.5)              // adern
                    {
                        float n = fbm(q * 0.7 + fbm(q * 0.35) * A.z * 2);
                        e = abs(n - 0.5) / freq;
                        ln = 1 - smoothstep(wL * 0.4, wL, e);
                    }
                    else                              // zellfugen (große Zellen, alle Fugen)
                    {
                        e = voronoi(q * 0.35).y / (freq * 0.35);
                        gate = smoothstep(0.4, 0.55, fbm(q * 0.3 + 2.0)); ln = (1 - smoothstep(wL * 0.4, wL, e)) * gate;
                    }
                    float halo = (1 - smoothstep(0, wL * 2.5, e)) * A.w * gate;
                    float baseGlow = A.w * (1 - isBase) * (1 - smoothstep(0.0, 0.35, IN.rest.w));   // Glut am Ansatz der Teile (Fugen)
                    float puls = 1 - B.y * 0.5 + B.y * 0.5 * sin(6.28318 * B.x * t);
                    col = lerp(col, LCi.rgb * 0.55 + 0.08, saturate(ln) * m);
                    emis += LCi.rgb * LCi.a * (ln + halo * 0.5 + baseGlow) * m * puls;
                    rough = lerp(rough, 1, ln * m);
                }
                else if (typ < 4.5)       // ueberzug
                {
                    float n = fbm(p / max(0.005, A.z) + B.x);
                    float cov = smoothstep(1 - A.x - 0.12, 1 - A.x + 0.12, n * 0.85 + edgeTerm * A.y * 0.6 + 0.05);
                    col = lerp(col, LCi.rgb, cov * m);
                    rough = lerp(rough, A.w, cov * m);
                }
                else if (typ < 5.5)       // naesse
                {
                    col *= 1 - A.z * A.x * m;
                    rough = lerp(rough, 1 - A.y, A.x * m);
                }
                else                      // rim (bleibt live)
                {
                    emis += LCi.rgb * LCi.a * pow(1 - saturate(dot(V, nW)), lerp(6, 1.5, A.x)) * m;
                }
            }

            // Leuchten ohne Bloom/HDR-Tonemapping: Farbton erhalten statt nach Gelb/Weiß auszubrennen
            float em = max(emis.r, max(emis.g, emis.b));
            emis *= (1 - exp(-em * 0.8)) * 1.25 / max(em, 1e-4);
            o.Albedo = saturate(col);
            o.Normal = normalize(float3(dot(nW, wT), dot(nW, wB), dot(nW, wN)));
            o.Metallic = 0;
            o.Smoothness = saturate(1 - rough);
            o.Emission = emis;
            o.Alpha = 1;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
