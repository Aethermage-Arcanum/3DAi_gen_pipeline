// Varianten-Baukasten – gemeinsame Rechnung der Material-Ebenen (Spec 4.1–4.3).
// Wird vom Vorschau-Shader „VariantKit/Layered“ UND vom Textur-Backen „Hidden/VariantKit/Bake“ benutzt → die gebackenen
// Texturen sind genau das, was die Vorschau zeigt. Blickabhängiges (Glasig-Fresnel, Rim, Puls) rechnet der Aufrufer.
#ifndef VARIANT_LAYERS_INCLUDED
#define VARIANT_LAYERS_INCLUDED

sampler2D _MainTex;
sampler2D _BumpMap;
half _Facetten, _DarkThreshold;
float4 _VKBounds;

#define GDECL(n) float4 _G##n##C, _G##n##D, _G##n##P, _G##n##Q;
GDECL(0) GDECL(1) GDECL(2) GDECL(3) GDECL(4) GDECL(5) GDECL(6) GDECL(7) GDECL(8)
#define LDECL(n) float4 _L##n##T, _L##n##C, _L##n##D, _L##n##A, _L##n##B, _L##n##M;
LDECL(0) LDECL(1) LDECL(2) LDECL(3) LDECL(4) LDECL(5) LDECL(6) LDECL(7)

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

struct VKIn
{
    float2 uv;          // Basis-UV (Tripo-Textur)
    float4 grp;         // Gruppe hell, Gruppe dunkel | Farb-Zufall Teil, Zufall pro Teil, 1 = Basis / 0 = Teil
    float4 rest;        // Ruhe-Position im Körperraum / Kreaturgröße, w = Höhe im Teil (Ansatz → Spitze)
    float3 rnrm;        // Ruhe-Normale
    float4 m0, m1;      // Masken der 8 Ebenen
    float3 restFlat;    // Flächen-Normale (Ruhe-Raum, zur Ruhe-Normale ausgerichtet)
    float edgeTerm;     // Kanten/Facettenwechsel (für Überzug „kanten“)
    float t;            // Zeit (Puls)
};

struct VKOut
{
    float3 col;         // Albedo ohne blickabhängige Anteile
    float rough;
    float3 emis;        // Leuchten inkl. Puls zum Zeitpunkt t (Vorschau)
    float3 emisConst;   // Leuchten ohne Puls-Ebenen (Backen)
    float3 emisPuls;    // Puls-Ebenen bei voller Stärke (Backen)
    float glasig;
    float isBase;
    float3 nTS;         // Normal-Map (Tangentenraum, nur Basis)
    float rimMask; float4 rimC; float rimBreite;   // Rim bleibt live
    int g;
};

VKOut VKEval(VKIn IN)
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

    VKOut o;
    float isBase = step(0.5, IN.grp.w);
    o.isBase = isBase;
    float3 p = IN.rest.xyz;
    float3 rn = normalize(IN.rnrm + 1e-5);
    float3 tex = tex2D(_MainTex, IN.uv).rgb;
    float lum = dot(tex, float3(0.299, 0.587, 0.114));
    float dark = isBase * step(lum, _DarkThreshold);
    int g = (int)round(lerp(IN.grp.x, IN.grp.y, dark));
    g = clamp(g, 0, 8);
    o.g = g;
    o.nTS = lerp(float3(0, 0, 1), UnpackNormal(tex2D(_BumpMap, IN.uv)), isBase);

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
    float fh = hash13(floor(IN.restFlat * 37.0 + 50.0) + r1 * 13.0);
    col *= 1 + (fh - 0.5) * 2 * P.z;
    float rough = P.x;
    float3 emisC = C.rgb * C.a;
    float3 emisP = 0;
    float3 emisNow = 0;
    o.glasig = Q.x;
    rough = lerp(rough, 0.1, Q.x * 0.5);
    o.rimMask = 0; o.rimC = 0; o.rimBreite = 0.35;

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
            float puls = 1 - B.y * 0.5 + B.y * 0.5 * sin(6.28318 * B.x * IN.t);
            col = lerp(col, LCi.rgb * 0.55 + 0.08, saturate(ln) * m);
            float3 em = LCi.rgb * LCi.a * (ln + halo * 0.5 + baseGlow) * m;
            emisNow += em * puls;
            if (B.y > 0.001 && B.x > 0.001) emisP += em; else emisC += em;
            rough = lerp(rough, 1, ln * m);
        }
        else if (typ < 4.5)       // ueberzug
        {
            float n = fbm(p / max(0.005, A.z) + B.x);
            float cov = smoothstep(1 - A.x - 0.12, 1 - A.x + 0.12, n * 0.85 + IN.edgeTerm * A.y * 0.6 + 0.05);
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
            o.rimMask = m; o.rimC = LCi; o.rimBreite = A.x;
        }
    }
    o.col = col;
    o.rough = rough;
    o.emisConst = emisC;
    o.emisPuls = emisP;
    o.emis = C.rgb * C.a + emisNow;
    return o;
}

// Leuchten ohne Bloom/HDR-Tonemapping: Farbton erhalten statt nach Gelb/Weiß auszubrennen
float3 VKCompressEmission(float3 emis)
{
    float em = max(emis.r, max(emis.g, emis.b));
    return emis * (1 - exp(-em * 0.8)) * 1.25 / max(em, 1e-4);
}

#endif
