"""Schicht 2 „Bedeckung“: Lagen (Fell, Federn, Stacheln, Platten) per Geometry Nodes (Spec 2.1–2.5, E2, E5).

Aufbau in Blender (live, auch während ein Clip läuft):
  Basis-Mesh (Shape Keys = Statur S) → [VK_Lage_1] → [VK_Lage_2] → Armature
Jeder Lagen-Modifier verteilt Punkte auf der RUHE-Form der Haut (Attribut vk_rest → Statur ändert die Verteilung
nicht), setzt pro Punkt ein kleines Teil (Zottel, Feder, Stachel, Platte) und hängt es an die verformte Haut
(vk_pdef/vk_ndef). Die Teile erben die Vertex-Gruppen (= Skin-Gewichte) ihres Ansatzpunkts → sie laufen mit der Haut
mit und verformen sich nicht (alle Punkte eines Teils haben dieselben Gewichte).

Python rechnet pro Lage nur die Masken (Zonen, „oben“, fleckiger Rand, Silhouette, Lage-1-Vorrang) und den
Längenfaktor pro Zone als Vertex-Attribute; alles andere rechnet der Node-Baum.
Export für Unity: <ExportName>.bedeckung.json (Körperraum, Gewichte nach Knochennamen) – siehe export_unity().
"""
import json
import math
import os

import bpy
import numpy as np
from mathutils import noise, Vector

from . import vk_json, vk_nodes

GROUP = "VK_Bedeckung"
GROUP_VERSION = 5
TYPEN = ["fell", "federn", "stacheln", "platten"]
FORMEN = ["spitz", "rund", "zackig", "buschel"]
RICHTUNGEN = ["knochen", "hinten", "unten", "aussen"]
MODI = ["geometrie", "silhouette", "nur_shader"]
SILHOUETTE_ZONEN = ["ruecken_gesamt", "schultern", "oberschenkel", "unterarme", "schwanz", "kopf_oben"]

# Standardwerte pro Typ (Spec 2.2 / 2.4)
GEMEINSAM = {"laenge_zufall": 0.3, "laenge_nach_zone": {}, "richtung": "knochen", "richtung_zufall": 12.0,
             "farbgruppe": "bedeckung_1", "accessoires_aussparen": True, "seed": None, "weg_ab_lod": 2}
TYP_STD = {
    "fell": {"anzahl": 500, "laenge": 0.05, "anlege_winkel": 25.0, "abstand_min": 0.015, "breite": 0.45, "form": "spitz",
             "kanten": 3, "kruemmung": 0.3, "modus": "geometrie", "weichheit": 0.6},
    "federn": {"anzahl": 300, "laenge": 0.06, "anlege_winkel": 15.0, "abstand_min": 0.02, "breite": 0.35, "kruemmung": 0.4,
               "kiel": True, "modus": "geometrie", "weichheit": 0.4},
    "stacheln": {"anzahl": 250, "laenge": 0.10, "anlege_winkel": 35.0, "abstand_min": 0.02, "dicke": 0.01, "kanten": 4,
                 "spitze": 0.9, "kruemmung": 0.1, "weichheit": 0.1},
    "platten": {"anzahl": 60, "laenge": 0.06, "anlege_winkel": 10.0, "abstand_min": 0.03, "groesse": 0.06, "dicke": 0.01,
                "streckung": 1.2, "ecken": 6, "schuppung": 0.4, "woelbung": 0.3, "groesse_zufall": 0.3, "weichheit": 0.0},
}
# G14: `weichheit` (Nachschwingen im Unity-Shader) steht pro Typ in TYP_STD; sie ändert die Geometrie nicht. Die
# Beweglichkeit pro Vertex ist das Attribut `vk_h` (Wurzel 0 … Spitze 1), exportiert als "h" in <Name>.bedeckung.json.
TRIS_PRO_TEIL = {"fell": lambda l: {"spitz": 1, "rund": 3, "zackig": 2, "buschel": 3}.get(l.get("form", "spitz"), 1) * int(l.get("kanten", 3)),
                 "federn": lambda l: 4, "stacheln": lambda l: int(l.get("kanten", 4)) + (int(l.get("kanten", 4)) if float(l.get("spitze", 0.9)) < 0.99 else 0),
                 "platten": lambda l: 3 * int(l.get("ecken", 6))}
BUDGET_BEDECKUNG = {"normal": 2000, "elite": 3000, "boss": 5000}
BUDGET_GESAMT = {"normal": 6000, "elite": 9000, "boss": 15000}
BUDGET_ACC = {"normal": 1500, "elite": 2500, "boss": 4000}


def neue_lage(typ, lage_id):
    d = {"id": lage_id, "typ": typ, "an": True}
    d.update(TYP_STD[typ])
    d.update(GEMEINSAM)
    d["farbgruppe"] = "bedeckung_1"
    d["maske"] = {"zonen": ["ganzer_koerper"], "ohne": [], "oben": 0.0, "rand": 0.05, "rauschen": 0.2}
    return d


def wert(lage, key):
    if key in lage and lage[key] is not None:
        return lage[key]
    t = TYP_STD.get(lage.get("typ", "fell"), {})
    if key in t:
        return t[key]
    return GEMEINSAM.get(key)


# ------------------------------------------------------------------------------------------------ Node-Baum
def build_group():
    ng = bpy.data.node_groups.get(GROUP)
    if ng is not None and ng.get("vk_version") == GROUP_VERSION:
        return ng, json.loads(ng["vk_ids"])
    ng, B = vk_nodes.new_group(GROUP)
    G = B.input("Geometry", "geo")
    lage = B.input("Lage", "int", 1, 1, 2)
    typ = B.input("Typ", "int", 0, 0, 3, "0 Fell, 1 Federn, 2 Stacheln, 3 Platten")
    anzahl = B.input("Anzahl", "int", 500, 0, 1500)
    laenge = B.input("Laenge", "float", 0.05, 0.0, 2.0, "Meter")
    l_zuf = B.input("Laenge Zufall", "float", 0.3, 0.0, 1.0)
    breite = B.input("Breite", "float", 0.45, 0.05, 2.0)
    dicke = B.input("Dicke", "float", 0.01, 0.0, 1.0, "Meter")
    kanten = B.input("Kanten", "int", 3, 3, 8)
    form = B.input("Form", "int", 0, 0, 3)
    kruemm = B.input("Kruemmung", "float", 0.3, 0.0, 1.0)
    spitze = B.input("Spitze", "float", 0.9, 0.0, 1.0)
    richtung = B.input("Richtung", "int", 0, 0, 3)
    anlege = B.input("Anlege Winkel", "float", 25.0, 0.0, 90.0)
    r_zuf = B.input("Richtung Zufall", "float", 12.0, 0.0, 45.0)
    abstand = B.input("Abstand Min", "float", 0.015, 0.0, 1.0)
    seed = B.input("Seed", "int", 0)
    groesse = B.input("Groesse", "float", 0.06, 0.0, 2.0)
    streck = B.input("Streckung", "float", 1.2, 0.3, 3.0)
    woelb = B.input("Woelbung", "float", 0.3, 0.0, 1.0)
    g_zuf = B.input("Groesse Zufall", "float", 0.3, 0.0, 1.0)
    schupp = B.input("Schuppung", "float", 0.4, 0.0, 0.9)
    vorn = B.input("Vorn", "vec", (1, 0, 0))
    oben = B.input("Oben", "vec", (0, 0, 1))
    acc_obj = B.input("Aussparen", "obj")
    material = B.input("Material", "mat")
    mname = B.input("Maske", "str", "vk_maske_1")
    lname = B.input("Laengen Attribut", "str", "vk_laenge_1")
    B.output("Geometry", "geo")

    deg = math.pi / 180.0
    # ---- verformte Lage merken, Verteilung auf der Ruhe-Form
    G1 = B.store(G, "vk_pdef", B.pos(), "FLOAT_VECTOR")
    G1 = B.store(G1, "vk_ndef", B.normal(), "FLOAT_VECTOR")
    Grest = B.set_pos(G1, position=B.attr("vk_rest", "FLOAT_VECTOR"))
    is_base = B.cmp(B.attr("vk_lage", "INT"), 0, "EQUAL", "INT")
    mask = B.attr(mname, "FLOAT")
    fa = B.out(B.node("GeometryNodeInputMeshFaceArea"))
    stat = B.node("GeometryNodeAttributeStatistic", data_type="FLOAT", domain="FACE")
    B.set(stat, "Geometry", Grest)
    B.set(stat, "Selection", is_base)
    B.set(stat, "Attribute", B.m("MULTIPLY", fa, mask))
    stat2 = B.node("GeometryNodeAttributeStatistic", data_type="FLOAT", domain="FACE")
    B.set(stat2, "Geometry", Grest)
    B.set(stat2, "Selection", is_base)
    B.set(stat2, "Attribute", fa)
    # winzige Masken nicht mit riesiger Dichte füllen (Poisson prüft Dichte × Gesamtfläche Kandidaten)
    area = B.m("MAXIMUM", B.out(stat, "Sum"), B.m("MULTIPLY", B.out(stat2, "Sum"), 0.01))
    dens = B.m("DIVIDE", anzahl, area)
    is_plate = B.cmp(typ, 3, "EQUAL", "INT")
    plate_d = B.m("MULTIPLY", groesse, B.m("SUBTRACT", 1.0, schupp))
    dist = B.switch("FLOAT", is_plate, abstand, B.m("MAXIMUM", abstand, plate_d))
    dp = B.node("GeometryNodeDistributePointsOnFaces", distribute_method="POISSON")
    B.set(dp, "Mesh", Grest)
    B.set(dp, "Selection", is_base)
    B.set(dp, "Distance Min", dist)
    B.set(dp, "Density Max", dens)
    B.set(dp, "Density Factor", mask)
    B.set(dp, "Seed", seed)
    P = B.out(dp, "Points")

    # ---- unter Accessoires aussparen (Punktwolke mit Attribut "radius")
    acc = B.out(B.node("GeometryNodeObjectInfo", {"Object": acc_obj}, transform_space="RELATIVE"), "Geometry")
    near = B.node("GeometryNodeSampleNearest", domain="POINT")
    B.set(near, "Geometry", acc)
    B.set(near, "Sample Position", B.pos())
    si_r = B.node("GeometryNodeSampleIndex", data_type="FLOAT", domain="POINT")
    B.set(si_r, "Geometry", acc)
    B.set(si_r, "Value", B.attr("radius", "FLOAT"))
    B.set(si_r, "Index", B.out(near))
    si_p = B.node("GeometryNodeSampleIndex", data_type="FLOAT_VECTOR", domain="POINT")
    B.set(si_p, "Geometry", acc)
    B.set(si_p, "Value", B.pos())
    B.set(si_p, "Index", B.out(near))
    dacc = B.v("DISTANCE", B.pos(), B.out(si_p))
    P = B.delete(P, B.cmp(dacc, B.out(si_r), "LESS_THAN", "FLOAT"))

    # ---- pro Punkt: Richtung, Länge, Größe
    n = B.v("NORMALIZE", B.attr("vk_ndef", "FLOAT_VECTOR"))
    pdef = B.attr("vk_pdef", "FLOAT_VECTOR")
    r1, r2, r3, r4 = (B.rnd(B.m("ADD", seed, k)) for k in (11, 23, 37, 51))
    neg_vorn = B.v("SCALE", vorn, scale=-1.0)
    neg_oben = B.v("SCALE", oben, scale=-1.0)
    t0 = B.index_switch("VECTOR", richtung, [B.attr("vk_strich", "FLOAT_VECTOR"), neg_vorn, neg_oben, neg_vorn])
    tp = B.v("SUBTRACT", t0, B.v("SCALE", n, scale=B.v("DOT_PRODUCT", t0, n)))
    fb = B.v("SUBTRACT", neg_vorn, B.v("SCALE", n, scale=B.v("DOT_PRODUCT", neg_vorn, n)))
    tlen = B.v("LENGTH", tp)
    t1 = B.v("NORMALIZE", B.switch("VECTOR", B.cmp(tlen, 0.15, "GREATER_THAN", "FLOAT"), fb, tp))
    ang = B.m("MULTIPLY", B.m("MULTIPLY", B.m("SUBTRACT", r1, 0.5), 2.0), B.m("MULTIPLY", r_zuf, deg))
    vr = B.node("ShaderNodeVectorRotate", rotation_type="AXIS_ANGLE")
    B.set(vr, "Vector", t1)
    B.set(vr, "Axis", n)
    B.set(vr, "Angle", ang)
    trot = B.out(vr)
    is_out = B.cmp(richtung, 3, "EQUAL", "INT")
    a_base = B.switch("FLOAT", is_out, B.m("MULTIPLY", anlege, deg), 80.0 * deg)
    a = B.m("ADD", a_base, B.m("MULTIPLY", B.m("SUBTRACT", r2, 0.5), B.m("MULTIPLY", r_zuf, deg)))
    d = B.v("NORMALIZE", B.v("ADD", B.v("SCALE", trot, scale=B.m("COSINE", a)), B.v("SCALE", n, scale=B.m("SINE", a))))
    sec = B.switch("VECTOR", is_out, n, trot)
    side_ok = B.v("NORMALIZE", B.v("CROSS_PRODUCT", sec, d))
    ax = B.node("FunctionNodeAxesToRotation", primary_axis="Z", secondary_axis="X")
    B.set(ax, "Primary Axis", d)
    B.set(ax, "Secondary Axis", side_ok)
    rot = B.out(ax)
    lenf = B.attr(lname, "FLOAT")
    ln = B.m("MULTIPLY", B.m("MULTIPLY", laenge, lenf), B.m("ADD", 1.0, B.m("MULTIPLY", B.m("MULTIPLY", B.m("SUBTRACT", r3, 0.5), 2.0), l_zuf)))
    sz = B.m("MULTIPLY", B.m("MULTIPLY", groesse, B.m("ADD", 1.0, B.m("MULTIPLY", B.m("MULTIPLY", B.m("SUBTRACT", r3, 0.5), 2.0), g_zuf))), lenf)
    wl = B.m("MULTIPLY", ln, breite)
    scale = B.index_switch("VECTOR", typ, [
        B.xyz(wl, B.m("MULTIPLY", wl, 0.4), ln),
        B.xyz(wl, B.m("MULTIPLY", ln, 0.08), ln),
        B.xyz(dicke, dicke, ln),
        B.xyz(sz, dicke, B.m("MULTIPLY", sz, streck)),
    ])
    _, sy, sz_len = B.sep(scale)
    # Ansatz leicht in die Haut (keine Lücke), Teil an die verformte Haut
    P = B.store(P, "vk_anker", B.pos(), "FLOAT_VECTOR")
    P = B.store(P, "vk_n", n, "FLOAT_VECTOR")
    P = B.store(P, "vk_len", sz_len, "FLOAT")
    P = B.store(P, "vk_rand", r4, "FLOAT")
    P = B.store(P, "vk_teil", B.index(), "INT")
    P = B.set_pos(P, position=B.v("SUBTRACT", pdef, B.v("SCALE", n, scale=B.m("MULTIPLY", sy, 0.35))))

    # ---- Teil-Meshes (Einheitsgröße: Ansatz z = 0, Spitze z = 1, Breite x ±0.5, Dicke y ±0.5)
    def up(mesh):   # Kegel-Knoten liegt schon von z = 0 (Ansatz) bis z = 1 (Spitze)
        return mesh
    spitz = up(B.cone(kanten, 0.0, 0.5))
    rund = up(B.cone(kanten, 0.22, 0.5, fill="TRIANGLE_FAN"))
    rund = B.delete(rund, B.cmp(B.sep(B.normal())[2], -0.9, "LESS_THAN", "FLOAT"), "FACE")
    zack = up(B.cone(kanten, 0.0, 0.5, segs=2))
    zx, zy, zz = B.sep(B.pos())
    mid = B.m("MULTIPLY", B.m("SUBTRACT", 1.0, B.m("ABSOLUTE", B.m("SUBTRACT", B.m("MULTIPLY", zz, 2.0), 1.0))), 0.45)
    zack = B.set_pos(zack, offset=B.xyz(B.m("MULTIPLY", zx, mid), 0.0, 0.0))
    b1 = B.transform(spitz, r=(0, 0.42, 0), s=(0.8, 1, 0.85))
    b2 = B.transform(spitz, r=(0, -0.42, 0), s=(0.8, 1, 0.85))
    busch = B.join(spitz, b1, b2)
    fell = B.index_switch("GEOMETRY", form, [spitz, rund, zack, busch])
    feder = up(B.cone(4, 0.0, 0.5))
    st_top = B.m("MULTIPLY", B.m("SUBTRACT", 1.0, spitze), 0.3)
    stachel = up(B.cone(kanten, st_top, 0.5, fill="TRIANGLE_FAN"))
    stachel = B.delete(stachel, B.cmp(B.sep(B.normal())[2], -0.9, "LESS_THAN", "FLOAT"), "FACE")
    pl = B.cone(kanten, 0.42, 0.5, fill="TRIANGLE_FAN")
    pl = B.delete(pl, B.cmp(B.sep(B.normal())[2], -0.9, "LESS_THAN", "FLOAT"), "FACE")
    px, py, pz = B.sep(B.pos())
    center = B.m("LESS_THAN", B.v("LENGTH", B.xyz(px, py, 0.0)), 0.01)
    pl = B.set_pos(pl, offset=B.xyz(0.0, 0.0, B.m("MULTIPLY", B.m("MULTIPLY", center, B.cmp(pz, 0.0, "GREATER_THAN", "FLOAT")), woelb)))
    pl = B.transform(pl, t=(0, 0, 0.5), r=(-math.pi / 2, 0, 0))
    part = B.index_switch("GEOMETRY", typ, [fell, feder, stachel, pl])
    part = B.store(part, "vk_h", B.m("MINIMUM", B.m("MAXIMUM", B.sep(B.pos())[2], 0.0), 1.0), "FLOAT")
    tri = B.node("GeometryNodeTriangulate")
    B.set(tri, "Mesh", part)
    part = B.out(tri)

    iop = B.node("GeometryNodeInstanceOnPoints")
    B.set(iop, "Points", P)
    B.set(iop, "Instance", part)
    B.set(iop, "Rotation", rot)
    B.set(iop, "Scale", scale)
    R = B.out(B.node("GeometryNodeRealizeInstances", {"Geometry": B.out(iop)}))
    # Krümmung: Spitze zur Haut hin (nach der Größe, damit sie in Metern wirkt)
    h = B.attr("vk_h", "FLOAT")
    bend = B.m("MULTIPLY", B.m("MULTIPLY", B.m("MULTIPLY", kruemm, 0.35), B.attr("vk_len", "FLOAT")), B.m("MULTIPLY", h, h))
    R = B.set_pos(R, offset=B.v("SCALE", B.attr("vk_n", "FLOAT_VECTOR"), scale=B.m("MULTIPLY", bend, -1.0)))
    R = B.store(R, "vk_lage", lage, "INT")
    sm = B.node("GeometryNodeSetMaterial")
    B.set(sm, "Geometry", R)
    B.set(sm, "Material", material)
    R = B.out(sm)
    ss = B.node("GeometryNodeSetShadeSmooth", {"Mesh": R, "Shade Smooth": False})
    R = B.out(ss)
    B.finish(B.join(G, R))
    ng["vk_version"] = GROUP_VERSION
    ng["vk_ids"] = json.dumps(B.ids)
    return ng, B.ids


# ------------------------------------------------------------------------------------------------ Masken (Python)
def _noise(p, scale):
    return np.array([noise.noise(Vector(x * scale)) * 0.5 + 0.5 for x in p])


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def lage_mask(an, lage):
    mk = lage.get("maske") or {}
    m = an.zones.combined(mk.get("zonen") or ["ganzer_koerper"], mk.get("ohne") or [])
    oben = float(mk.get("oben", 0.0) or 0.0)
    if abs(oben) > 1e-4:
        up01 = an.body_dir(an.normals)[:, 1] * 0.5 + 0.5
        if oben > 0:
            m = m * (1 + (_smooth(0.45, 0.85, up01) - 1) * oben)
        else:
            m = m * (1 + (_smooth(0.45, 0.85, 1 - up01) - 1) * -oben)
    r = float(mk.get("rauschen", 0.2) or 0.0)
    if r > 0:
        nz = _noise(an.body / an.L, 9.0)
        m = m * np.clip(1 - r + r * 2.2 * nz, 0, 1)
    if wert(lage, "modus") == "silhouette":
        m = m * an.zones.combined(SILHOUETTE_ZONEN)
    return np.clip(m, 0, 1)


def lage_laenge(an, lage):
    f = np.ones(len(an.verts))
    for z, fac in (lage.get("laenge_nach_zone") or {}).items():
        f += (float(fac) - 1.0) * an.zones.mask(z)
    return np.clip(f, 0.1, 5.0)


def write_attr(me, name, values, dtype="FLOAT"):
    a = me.attributes.get(name)
    if a is not None and (a.data_type != dtype or a.domain != "POINT"):
        me.attributes.remove(a)
        a = None
    if a is None:
        a = me.attributes.new(name, dtype, "POINT")
    if dtype == "FLOAT_VECTOR":
        a.data.foreach_set("vector", np.asarray(values, np.float32).ravel())
    elif dtype == "INT":
        a.data.foreach_set("value", np.asarray(values, np.int32).ravel())
    else:
        a.data.foreach_set("value", np.asarray(values, np.float32).ravel())


def prepare_base(an, ob):
    me = ob.data
    write_attr(me, "vk_rest", an.verts, "FLOAT_VECTOR")
    write_attr(me, "vk_strich", an.strich(), "FLOAT_VECTOR")
    write_attr(me, "vk_lage", np.zeros(len(an.verts)), "INT")


def update_masks(an, ob, lagen):
    """Masken + Längenfaktoren aller Lagen; Lage 2 weicht Lage 1 (E2: getrennte Bereiche). → Überlappung (Anteil)."""
    me = ob.data
    masks = []
    for i in range(2):
        m = lage_mask(an, lagen[i]) if i < len(lagen) else np.zeros(len(an.verts))
        masks.append(m)
    overlap = 0.0
    if len(lagen) > 1:
        v, t = an.verts, an.tris
        area = np.linalg.norm(np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]]), axis=1)
        a2 = (masks[1][t].mean(1) > 0.5)
        both = a2 & (masks[0][t].mean(1) > 0.5)
        overlap = float(area[both].sum() / max(area[a2].sum(), 1e-9))
        masks[1] = masks[1] * (1 - _smooth(0.3, 0.7, masks[0]))
    for i in range(2):
        write_attr(me, f"vk_maske_{i + 1}", masks[i])
        write_attr(me, f"vk_laenge_{i + 1}", lage_laenge(an, lagen[i]) if i < len(lagen) else np.ones(len(an.verts)))
    me.update()
    return overlap


# ------------------------------------------------------------------------------------------------ Modifier
def mod_name(i):
    return f"VK_Lage_{i + 1}"


def ensure_material(name, color=(0.8, 0.8, 0.8), color2=None):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        at = nt.nodes.new("ShaderNodeAttribute")
        at.attribute_name = "vk_h"
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.name = "VK_Mix"
        nt.links.new(at.outputs["Fac"], mix.inputs["Factor"])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.85
    mix = mat.node_tree.nodes.get("VK_Mix")
    c1 = tuple(color) + (1.0,)
    c2 = tuple(color2 or color) + (1.0,)
    for s in mix.inputs:
        if s.name == "A" and s.type == "RGBA":
            s.default_value = c1
        if s.name == "B" and s.type == "RGBA":
            s.default_value = c2
    mat.diffuse_color = c1
    return mat


def hex_rgb(h, default=(0.7, 0.7, 0.7)):
    try:
        h = h.lstrip("#")
        srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)
    except Exception:
        return default


def sync_modifiers(an, arm, ob, doc, acc_obj=None):
    """Modifier pro Lage anlegen/aktualisieren (vor dem Armature-Modifier). Gibt Infos pro Lage zurück."""
    ng, ids = build_group()
    lagen = [l for l in doc.resolved["bedeckung"].get("lagen", []) if isinstance(l, dict)][:2]
    aktive = [l for l in lagen if l.get("an", True)]
    fg = doc.resolved.get("material", {}).get("farbgruppen", {})
    L = an.L
    vorn = tuple(float(x) for x in an.fwd)
    oben = tuple(float(x) for x in an.up)
    for i in range(2):
        name = mod_name(i)
        mod = ob.modifiers.get(name)
        if i >= len(aktive):
            if mod is not None:
                ob.modifiers.remove(mod)
            continue
        l = aktive[i]
        if mod is None:
            mod = ob.modifiers.new(name, "NODES")
            mod.node_group = ng
            arm_idx = next((k for k, m in enumerate(ob.modifiers) if m.type == "ARMATURE"), len(ob.modifiers) - 1)
            ob.modifiers.move(len(ob.modifiers) - 1, min(i, arm_idx))
        if mod.node_group is not ng:
            mod.node_group = ng
        g = l.get("farbgruppe", "bedeckung_1")
        gc = fg.get(g, {})
        mat = ensure_material(f"VK_{g}", hex_rgb(gc.get("farbe", "#B0B0B0")), hex_rgb(gc.get("farbe_2") or gc.get("farbe", "#B0B0B0")))
        typ = l.get("typ", "fell")
        anz = int(wert(l, "anzahl") or 0)
        if wert(l, "modus") == "nur_shader":
            anz = 0
        seed = doc.entry_seed(l, l.get("id") or f"lage#{i + 1}")
        vals = {
            "Lage": i + 1, "Typ": TYPEN.index(typ) if typ in TYPEN else 0, "Anzahl": anz,
            "Laenge": float(wert(l, "laenge")) * L, "Laenge Zufall": float(wert(l, "laenge_zufall")),
            "Breite": float(wert(l, "breite") or 0.45), "Dicke": float(wert(l, "dicke") or 0.01) * L,
            "Kanten": int(wert(l, "ecken") if typ == "platten" else (wert(l, "kanten") or 3)),
            "Form": FORMEN.index(wert(l, "form")) if wert(l, "form") in FORMEN else 0,
            "Kruemmung": float(wert(l, "kruemmung") or 0.0), "Spitze": float(wert(l, "spitze") or 0.9),
            "Richtung": RICHTUNGEN.index(wert(l, "richtung")) if wert(l, "richtung") in RICHTUNGEN else 0,
            "Anlege Winkel": float(wert(l, "anlege_winkel")), "Richtung Zufall": float(wert(l, "richtung_zufall")),
            "Abstand Min": float(wert(l, "abstand_min")) * L, "Seed": int(seed % 100000),
            "Groesse": float(wert(l, "groesse") or 0.06) * L, "Streckung": float(wert(l, "streckung") or 1.2),
            "Woelbung": float(wert(l, "woelbung") or 0.3), "Groesse Zufall": float(wert(l, "groesse_zufall") or 0.3),
            "Schuppung": float(wert(l, "schuppung") or 0.4), "Vorn": vorn, "Oben": oben,
            "Maske": f"vk_maske_{i + 1}", "Laengen Attribut": f"vk_laenge_{i + 1}",
        }
        changed = False
        for k, v in vals.items():
            changed |= vk_nodes.set_mod_input(mod, ids, k, v)
        vk_nodes.set_mod_input(mod, ids, "Aussparen", acc_obj if (acc_obj is not None and wert(l, "accessoires_aussparen")) else None)
        vk_nodes.set_mod_input(mod, ids, "Material", mat)
        if mat.name not in [m.name for m in ob.data.materials if m]:
            ob.data.materials.append(mat)
        mod.show_viewport = True
    ob.update_tag()
    return aktive


# ------------------------------------------------------------------------------------------------ Zählen / Export
def evaluate_parts(ob, rest=True):
    """Ausgewertetes Mesh lesen (rest=True: Armature aus, Statur-Shape-Key 0) → dict mit Arrays."""
    arm_mods = [m for m in ob.modifiers if m.type == "ARMATURE"]
    old = [m.show_viewport for m in arm_mods]
    kb = ob.data.shape_keys.key_blocks.get("VK_Statur") if ob.data.shape_keys else None
    old_kb = kb.value if kb else None
    if rest:
        for m in arm_mods:
            m.show_viewport = False
        if kb:
            kb.value = 0.0
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        n = len(me.vertices)
        co = np.empty(n * 3, np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)

        def get(name, kind="value", dim=1, dt=np.float32):
            a = me.attributes.get(name)
            if a is None:
                return np.zeros((n, dim) if dim > 1 else n, dt)
            arr = np.empty(len(a.data) * dim, dt)
            a.data.foreach_get(kind, arr)
            return arr.reshape(-1, dim) if dim > 1 else arr
        lage = get("vk_lage", dt=np.int32)
        teil = get("vk_teil", dt=np.int32)
        h = get("vk_h")
        rand = get("vk_rand")
        anker = get("vk_anker", "vector", 3)
        me.calc_loop_triangles()
        tri = np.empty(len(me.loop_triangles) * 3, np.int32)
        me.loop_triangles.foreach_get("vertices", tri)
        tri = tri.reshape(-1, 3)
        part_v = np.nonzero(lage > 0)[0]
        groups = {}
        names = [g.name for g in ev.vertex_groups]
        first = {}
        for v in part_v:
            key = (int(lage[v]), int(teil[v]))
            if key not in first:
                first[key] = v
        for key, v in first.items():
            ws = sorted(((g.weight, names[g.group]) for g in me.vertices[v].groups if g.group < len(names) and g.weight > 1e-4), reverse=True)[:4]
            s = sum(w for w, _ in ws) or 1.0
            groups[key] = {nm: w / s for w, nm in ws}
        res = {"co": co, "lage": lage, "teil": teil, "h": h, "rand": rand, "anker": anker, "tri": tri, "gewichte": groups,
               "first": first, "n_base": int((lage == 0).sum())}
    finally:
        ev.to_mesh_clear()
        if rest:
            for m, s in zip(arm_mods, old):
                m.show_viewport = s
            if kb:
                kb.value = old_kb
    return res


def count_tris(ev):
    lage, tri = ev["lage"], ev["tri"]
    tl = lage[tri[:, 0]]
    teile = {}
    for (lg, _t) in ev["first"].keys():
        teile[lg] = teile.get(lg, 0) + 1
    return {1: int((tl == 1).sum()), 2: int((tl == 2).sum())}, teile


def export_unity(an, ob, doc, out_path, werkzeug):
    """<ExportName>.bedeckung.json für Unity: Körperraum (x vorn, y oben, z links) / Kreaturgröße, Gewichte nach Namen."""
    ev = evaluate_parts(ob, rest=True)
    lage, teil, tri = ev["lage"], ev["teil"], ev["tri"]
    keys = sorted(ev["first"].keys())
    lagen = [l for l in doc.resolved["bedeckung"].get("lagen", []) if isinstance(l, dict) and l.get("an", True)][:2]
    verts, hh, tris, teile = [], [], [], []
    for key in keys:
        vs = np.nonzero((lage == key[0]) & (teil == key[1]))[0]
        remap = {int(v): k for k, v in enumerate(vs)}
        t_sel = tri[np.isin(tri[:, 0], vs) & (lage[tri[:, 0]] == key[0])]
        t_sel = t_sel[np.all(np.isin(t_sel, vs), axis=1)]
        v0 = len(verts) // 3
        b = an.to_body(ev["co"][vs].astype(np.float64)) / an.L
        verts.extend(round(float(x), 5) for x in b.ravel())
        hh.extend(round(float(x), 3) for x in ev["h"][vs])
        for t in t_sel:
            tris.extend(v0 + remap[int(i)] for i in t)
        v1 = ev["first"][key]
        l = lagen[key[0] - 1] if key[0] - 1 < len(lagen) else {}
        teile.append({
            "lage": key[0], "farbgruppe": l.get("farbgruppe", f"bedeckung_{key[0]}"), "zufall": round(float(ev["rand"][v1]), 3),
            "anker": [round(float(x), 5) for x in (an.to_body(ev["anker"][v1].astype(np.float64)) / an.L)],
            "gewichte": {k: round(v, 4) for k, v in ev["gewichte"][key].items()}, "v0": v0, "nv": int(len(vs)),
        })
    cnt, _ = count_tris(ev)
    data = {
        "format": "kreatur_bedeckung", "format_version": 1, "variante": doc.id, "basis": doc.resolved.get("basis"),
        "werkzeug": werkzeug, "revision": doc.loaded_revision,
        "quelle": {"seed": int(doc.resolved.get("seed", 0) or 0), "bedeckung": doc.resolved.get("bedeckung", {})},
        "koordinaten": "Koerperraum / Kreaturgroesse: x vorn, y oben, z links; Ursprung = Mitte Begrenzungsrahmen der Basis",
        "kreaturgroesse_m": round(an.L, 5),
        "tris": {"lage_1": cnt[1], "lage_2": cnt[2], "gesamt": cnt[1] + cnt[2]},
        "teile": teile, "vertices": verts, "h": hh, "dreiecke": tris,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, out_path)
    return data


def export_glb(ob, arm, out_path):
    """Bedeckung + Basis als GLB (für Menschen / andere Programme; Unity liest die JSON-Datei)."""
    sel = [ob, arm]
    for o in bpy.context.view_layer.objects:
        o.select_set(o in sel)
    bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB", use_selection=True, export_apply=True,
                              export_animations=False, export_skins=True)
