// Varianten-Baukasten G14 – Nachschwingen der Bedeckung im Shader („Foliage-Trick“). Gemeinsam für „VariantKit/Layered“
// (Vorschau), „VariantKit/Baked“ (Spiel) und optional „Creature/Standard Dangling“ (Schalter, C13).
// Keine Physik, keine Zusatz-Knochen: die Laufzeit-Komponente VariantSchwingen rechnet pro Gegner 4 kleine Federn
// (Hüfte, Brust, Kopf, Schwanz) und gibt sie per MaterialPropertyBlock an den Shader. Ohne Komponente sind alle Werte 0 →
// das Mesh ist exakt wie vorher (starr).
//
// Vertex-Daten (VkBuilder.Combine, VkTexBake):
//   TEXCOORD1 = (h, weichheit [+2 = folgt der Schwerkraft], Slot + Phase, Teil-Länge / Kreaturgröße)
//     h          0 = Wurzel … 1 = Spitze (Blender: Attribut vk_h, Accessoires: Höhe im Baustein)
//     weichheit  0 = starr … 1 = schwingt voll (Regler pro Lage / Accessoire)
//     Slot       0 Hüfte · 1 Brust · 2 Kopf · 3 Schwanz (welche Feder das Teil antreibt), Nachkomma = Phase pro Teil
//   TANGENT.xyz = Achse des Teils (Wurzel → Spitze) im Mesh-Raum, wird vom Skinning mitgedreht
// Biegung: Kreisbogen um die Wurzel mit Spitzen-Winkel |D| → das Teil biegt sich, ohne länger zu werden.
#ifndef VARIANT_SWING_INCLUDED
#define VARIANT_SWING_INCLUDED

// pro Renderer (MaterialPropertyBlock, VariantSchwingen)
float4 _VKS0, _VKS1, _VKS2, _VKS3;   // Auslenkung der Federn (Welt, Radiant ≈ Spitzen-Winkel), w frei
float4 _VKSwing;                     // x Stoß-Hülle 0..1 · y Tempo (m/s) · z Kreaturgröße (m) · w An (0/1)
float4 _VKSwingB;                    // x Wackeln (rad) · y Wackel-Tempo (Hz) · z Zittern bei Stößen (rad) · w Schwerkraft-Folgen

float3 VKSlotVec(float slot)
{
    return slot < 0.5 ? _VKS0.xyz : (slot < 1.5 ? _VKS1.xyz : (slot < 2.5 ? _VKS2.xyz : _VKS3.xyz));
}

// Auslenkung der drei Quellen (Trägheit, Wackeln, Stoß-Zittern) als Spitzen-Winkel-Vektor in Welt-Richtung
float3 VKSwingDeflect(float slot, float phase, float h, float t)
{
    float3 D = VKSlotVec(slot);
    float a = t * _VKSwingB.y * 6.2831853 + phase * 6.2831853 - h * 1.2;     // Welle läuft zur Spitze
    float3 wob = float3(0.7 * sin(a) + 0.3 * sin(a * 2.31 + 1.3),
                        0.35 * sin(a * 1.37 + 2.1),
                        0.7 * sin(a * 0.83 + 2.4) + 0.3 * sin(a * 1.91 + 0.4));
    D += wob * (_VKSwingB.x * (1 + 0.35 * _VKSwing.y));                    // Wackeln, beim Laufen etwas mehr
    float b = t * 56.5 + phase * 19.5;                                     // ≈ 9 Hz Zittern nach einem Stoß
    D += float3(sin(b), 0.6 * sin(b * 1.13 + 1.7), sin(b * 0.91 + 0.6)) * (_VKSwingB.z * _VKSwing.x);
    return D;
}

// Versatz eines Vertex im Objektraum (nach dem Skinning). sw = TEXCOORD1, tangentOS = TANGENT.
float3 VKSwingOffsetOS(float3 posOS, float4 tangentOS, float4 sw, float t)
{
    float grav = step(1.5, sw.y);
    float weich = sw.y - 2.0 * grav;
    float h = sw.x;
    if (weich * h * _VKSwing.w < 1e-5) return float3(0, 0, 0);
    float3 axis = normalize(mul((float3x3)unity_ObjectToWorld, tangentOS.xyz) + float3(0, 1e-6, 0));
    float len = max(sw.w * _VKSwing.z, 1e-4);
    float3 D = VKSwingDeflect(floor(sw.z), frac(sw.z), h, t);
    float3 down = float3(0, -1, 0);
    D += grav * _VKSwingB.w * (down - axis * dot(axis, down));             // Gehänge zieht es nach unten
    D *= weich;
    D -= axis * dot(D, axis);                                              // nur quer zur Achse biegen
    float th = length(D);
    if (th < 1e-5) return float3(0, 0, 0);
    float3 dir = D / th;
    th = min(th, 1.4);
    float r = len / th;                                                    // Biege-Radius
    float phi = th * h;
    float3 offW = dir * (r * (1 - cos(phi))) + axis * (r * sin(phi) - h * len);
    return mul((float3x3)unity_WorldToObject, offW * _VKSwing.w);
}

// Für „Creature/Standard Dangling“ (C13): dort gibt es nur Gewicht (Vertex-Farbe R) und Phase (G), keine Achse/Länge.
// Die Teile hängen (Moos, Lappen) → Achse ≈ Welt-unten, Versatz waagerecht, Länge _VKDangleLen (m).
float3 VKSwingDangleOffsetWS(float w, float phase, float slot, float len, float t)
{
    if (w * _VKSwing.w < 1e-5) return float3(0, 0, 0);
    float3 D = VKSwingDeflect(slot, phase, w, t);
    D.y = 0;
    float th = min(length(D), 1.2);
    if (th < 1e-5) return float3(0, 0, 0);
    float3 dir = D / max(length(D), 1e-6);
    float r = len / th, phi = th * w;
    return (dir * (r * (1 - cos(phi))) + float3(0, 1, 0) * (w * len - r * sin(phi))) * _VKSwing.w;
}

#endif
