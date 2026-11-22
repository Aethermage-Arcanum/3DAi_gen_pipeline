"""Baustein-Werkbank (Spec 3.4): Form-Regler für die Accessoire-Bausteine über Geometry Nodes, live in Blender.

Sieben Familien (je ein Node-Baum mit Reglern), jeder Accessoire-Typ ist eine Familie mit eigenen Startwerten:
  zacke   – Kristall, Eiszacke, Felszacke, Dorn, Horn, Stoßzahn, Grabkralle, Seepocke
  platte  – Steinplatte, Eisplatte, Knochenplatte, Sinterplatte
  brocken – Basaltbrocken
  pilz    – Pilze (Gruppe aus 1–5 Pilzen)
  polster – Moospolster
  streifen– Grasbüschel, Moosfransen, Tang, Gehänge (dünn → doppelseitig)
  kette   – Kette
Die Bibliothek bleibt procedural/bausteine/<typ>.json (+ .fbx/.glb): Unity liest nur die JSON-Meshes (Achsen X vorn,
Y links, Z oben; Ursprung = Mitte der Unterseite; größte Ausdehnung 1.0). Speichern einer Form ersetzt nur diese Form.
"""
import json
import math
import os

import bpy
import numpy as np

from . import vk_json, vk_nodes

VERSION = "0.2.0"
LIB_VERSION = 2

# Familie → Regler: (Name, Art, Standard, Min, Max, Erklärung)
FAMILIEN = {
    "zacke": [
        ("kanten", "int", 5, 3, 8, "Anzahl Kanten (Querschnitt)"),
        ("segmente", "int", 2, 1, 6, "Abschnitte entlang der Höhe (mehr = runder gebogen)"),
        ("schlankheit", "float", 0.4, 0.1, 1.6, "Breite am Fuß im Verhältnis zur Höhe"),
        ("prisma", "float", 0.0, 0.0, 0.9, "gerader Schaft bis zu dieser Höhe, darüber Spitze (Kristall ≈ 0.5)"),
        ("spitze", "float", 1.0, 0.0, 1.0, "1 = spitz, kleiner = abgestumpft (Seepocke ≈ 0.4)"),
        ("spitze_versatz", "float", 0.1, 0.0, 0.6, "Spitze nach vorn versetzt (schief)"),
        ("kruemmung", "float", 0.0, 0.0, 1.0, "nach vorn gebogen (Horn, Kralle)"),
        ("drall", "float", 0.0, 0.0, 1.0, "Verdrehung um die eigene Achse (Horn)"),
        ("bruch", "float", 0.2, 0.0, 1.0, "unregelmäßige Facetten (Bruchkanten)"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
    "platte": [
        ("ecken", "int", 6, 4, 10, "Anzahl Ecken"),
        ("dicke", "float", 0.25, 0.03, 0.8, "Dicke im Verhältnis zum Durchmesser"),
        ("woelbung", "float", 0.12, 0.0, 0.6, "Mitte der Oberseite angehoben"),
        ("fase", "float", 0.12, 0.0, 0.45, "abgeschrägte Oberkante"),
        ("streckung", "float", 1.15, 0.5, 2.5, "Länge zu Breite"),
        ("bruch", "float", 0.2, 0.0, 1.0, "unregelmäßiger Rand"),
        ("rippen", "float", 0.0, 0.0, 1.0, "Rippen quer über die Oberseite (Knochenplatte)"),
        ("stufen", "int", 0, 0, 3, "Terrassen-Stufen am Rand (Sinterplatte)"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
    "brocken": [
        ("punkte", "int", 12, 6, 30, "Anzahl Eckpunkte (mehr = runder)"),
        ("blockig", "float", 0.7, 0.0, 1.0, "flache Oberseite, kantig"),
        ("dicke", "float", 0.65, 0.2, 1.2, "Höhe im Verhältnis zur Breite"),
        ("streckung", "float", 1.15, 0.5, 2.5, "Länge zu Breite"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
    "pilz": [
        ("pro_gruppe", "int", 3, 1, 5, "Pilze pro Gruppe"),
        ("stiel_hoehe", "float", 0.55, 0.1, 1.2, "Stielhöhe"),
        ("hut_breite", "float", 0.7, 0.2, 1.4, "Hutdurchmesser"),
        ("hut_form", "float", 0.4, 0.0, 1.0, "0 = flach, 1 = Glocke"),
        ("segmente", "int", 6, 4, 10, "Ecken von Stiel und Hut"),
        ("streuung", "float", 0.5, 0.0, 1.0, "wie weit die Pilze auseinanderstehen"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
    "polster": [
        ("ecken", "int", 9, 5, 16, "Ecken am Rand"),
        ("kuppel_hoehe", "float", 0.3, 0.05, 0.8, "Höhe der Kuppel"),
        ("rand_zacken", "float", 0.3, 0.0, 1.0, "unregelmäßiger, zackiger Rand"),
        ("zottel_rand", "int", 6, 0, 16, "kleine Zotteln am Rand"),
        ("rauheit", "float", 0.3, 0.0, 1.0, "buckelige Oberfläche"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
    "streifen": [
        ("anzahl", "int", 4, 1, 8, "Streifen/Blätter pro Teil"),
        ("breite", "float", 0.18, 0.03, 0.6, "Breite eines Streifens"),
        ("abschnitte", "int", 3, 1, 6, "Abschnitte entlang der Länge"),
        ("kruemmung", "float", 0.4, 0.0, 1.0, "biegt sich nach außen"),
        ("wellen", "float", 0.0, 0.0, 1.0, "seitliches Wellen (Tang)"),
        ("faecher", "float", 0.6, 0.0, 1.0, "wie weit die Streifen auseinanderfächern"),
        ("zacken", "float", 0.3, 0.0, 1.0, "gezackte Ränder"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
    "kette": [
        ("glieder", "int", 4, 2, 10, "Anzahl Glieder"),
        ("glied_dicke", "float", 0.12, 0.04, 0.3, "Dicke eines Glieds"),
        ("durchhang", "float", 0.3, 0.0, 1.0, "Kette biegt sich"),
        ("seed", "int", 1, 0, 9999, "Zufall"),
    ],
}

# Accessoire-Typ → (Familie, Startformen). Die drei M1-Typen behalten ihre bmesh-Formen, bis man sie hier neu speichert.
TYPEN = {
    "kristall": ("zacke", {"kristall_a": dict(kanten=6, segmente=2, schlankheit=0.42, prisma=0.55, spitze_versatz=0.05, bruch=0.25, seed=3),
                           "kristall_schlank": dict(kanten=5, segmente=2, schlankheit=0.28, prisma=0.65, spitze_versatz=0.08, bruch=0.2, seed=7),
                           "kristall_breit": dict(kanten=6, segmente=2, schlankheit=0.7, prisma=0.35, spitze_versatz=0.0, bruch=0.3, seed=11)}),
    "eiszacke": ("zacke", {"eiszacke_a": dict(kanten=5, segmente=3, schlankheit=0.32, prisma=0.3, kruemmung=0.25, bruch=0.25, seed=5),
                           "eiszacke_b": dict(kanten=4, segmente=3, schlankheit=0.26, prisma=0.2, kruemmung=0.4, bruch=0.2, seed=9)}),
    "felszacke": ("zacke", {}),
    "dorn": ("zacke", {"dorn_a": dict(kanten=4, segmente=2, schlankheit=0.3, kruemmung=0.35, bruch=0.1, seed=2),
                       "dorn_b": dict(kanten=3, segmente=2, schlankheit=0.25, kruemmung=0.6, bruch=0.05, seed=4)}),
    "horn": ("zacke", {"horn_a": dict(kanten=5, segmente=5, schlankheit=0.3, kruemmung=0.7, drall=0.2, bruch=0.05, spitze_versatz=0.0, seed=1),
                       "horn_b": dict(kanten=6, segmente=5, schlankheit=0.24, kruemmung=0.45, drall=0.5, bruch=0.05, spitze_versatz=0.0, seed=6)}),
    "seepocken": ("zacke", {"seepocke_a": dict(kanten=6, segmente=1, schlankheit=1.3, spitze=0.45, spitze_versatz=0.0, bruch=0.3, seed=8),
                            "seepocke_b": dict(kanten=5, segmente=1, schlankheit=1.0, spitze=0.35, spitze_versatz=0.05, bruch=0.35, seed=12)}),
    "eisplatte": ("platte", {"eisplatte_a": dict(ecken=6, dicke=0.3, woelbung=0.15, fase=0.2, streckung=1.2, bruch=0.35, seed=3),
                             "eisplatte_zackig": dict(ecken=7, dicke=0.35, woelbung=0.25, fase=0.3, streckung=1.1, bruch=0.6, seed=9)}),
    "knochenplatte": ("platte", {"knochen_a": dict(ecken=6, dicke=0.18, woelbung=0.15, fase=0.1, streckung=1.4, bruch=0.15, rippen=0.6, seed=2),
                                 "knochen_b": dict(ecken=5, dicke=0.22, woelbung=0.2, fase=0.12, streckung=1.1, bruch=0.2, rippen=0.4, seed=5)}),
    "sinterplatte": ("platte", {"sinter_a": dict(ecken=8, dicke=0.3, woelbung=0.05, fase=0.08, streckung=1.2, bruch=0.3, stufen=2, seed=4),
                                "sinter_b": dict(ecken=7, dicke=0.25, woelbung=0.1, fase=0.1, streckung=1.0, bruch=0.4, stufen=1, seed=10)}),
    "steinplatte": ("platte", {}),
    "basaltbrocken": ("brocken", {}),
    "pilze": ("pilz", {"pilze_a": dict(pro_gruppe=3, stiel_hoehe=0.55, hut_breite=0.7, hut_form=0.35, segmente=6, streuung=0.5, seed=3),
                       "pilze_glocke": dict(pro_gruppe=2, stiel_hoehe=0.7, hut_breite=0.55, hut_form=0.85, segmente=6, streuung=0.4, seed=8)}),
    "moospolster": ("polster", {"moos_a": dict(ecken=9, kuppel_hoehe=0.3, rand_zacken=0.35, zottel_rand=6, rauheit=0.35, seed=2),
                                "moos_flach": dict(ecken=10, kuppel_hoehe=0.18, rand_zacken=0.5, zottel_rand=8, rauheit=0.25, seed=5)}),
    "grasbueschel": ("streifen", {"gras_a": dict(anzahl=5, breite=0.14, abschnitte=2, kruemmung=0.45, faecher=0.7, zacken=0.2, seed=3)}),
    "moosfransen": ("streifen", {"fransen_a": dict(anzahl=4, breite=0.2, abschnitte=3, kruemmung=0.8, faecher=0.4, zacken=0.6, seed=4)}),
    "tang": ("streifen", {"tang_a": dict(anzahl=3, breite=0.22, abschnitte=4, kruemmung=0.6, wellen=0.7, faecher=0.5, zacken=0.1, seed=6)}),
    "gehaenge": ("streifen", {"ranke_a": dict(anzahl=2, breite=0.12, abschnitte=4, kruemmung=0.7, wellen=0.4, faecher=0.3, zacken=0.0, seed=7)}),
    "kette": ("kette", {"kette_a": dict(glieder=4, glied_dicke=0.12, durchhang=0.3, seed=1)}),
}


def lib_dir():
    return os.environ.get("VK_BAUSTEINE_DIR") or os.path.join(vk_json.pipeline_root(), "procedural", "bausteine")


def lib_path(typ):
    return os.path.join(lib_dir(), typ + ".json")


def read_lib(typ):
    p = lib_path(typ)
    return vk_json.read_file(p) if os.path.exists(p) else None


def defaults(familie):
    return {k: d for k, _t, d, _a, _b, _e in FAMILIEN[familie]}


def werte_fuer(typ, form):
    """Regler-Werte einer gespeicherten Form (oder Startwerte); M1-Formen ohne Familie werden sinngemäß übernommen."""
    fam = TYPEN[typ][0]
    w = defaults(fam)
    lib = read_lib(typ)
    src = (lib or {}).get("formen", {}).get(form, {}).get("werte") or TYPEN[typ][1].get(form) or {}
    for k, v in src.items():
        if k in w:
            w[k] = v
    if "kanten" in src and "ecken" in w:
        w["ecken"] = src["kanten"]
    if "ecken" in src and "punkte" in w:
        w["punkte"] = int(src["ecken"]) * 2
    return w


# ------------------------------------------------------------------------------------------------ Node-Bäume
def _deg(x):
    return x * math.pi / 180


def build_family(fam):
    name = f"VK_Baustein_{fam}"
    ng, B = vk_nodes.new_group(name)
    ins = {}
    for k, t, d, a, b, desc in FAMILIEN[fam]:
        ins[k] = B.input(k, t, d, a, b, desc)
    B.output("Geometry", "geo")
    geo = globals()["_fam_" + fam](B, ins)
    tri = B.node("GeometryNodeTriangulate", {"Mesh": geo})
    B.finish(B.out(B.node("GeometryNodeSetShadeSmooth", {"Mesh": B.out(tri), "Shade Smooth": False})))
    ng["vk_ids"] = json.dumps(B.ids)
    return ng, B.ids


def _jitter(B, geo, amount, seed, sel=None):
    rv = B.rnd(seed, (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0), "FLOAT_VECTOR")
    return B.set_pos(geo, offset=B.v("SCALE", rv, scale=amount), sel=sel)


def _del_bottom(B, geo):
    return B.delete(geo, B.cmp(B.sep(B.normal())[2], -0.9, "LESS_THAN", "FLOAT"), "FACE")


def _fam_zacke(B, i):
    r0 = B.m("MULTIPLY", i["schlankheit"], 0.5)
    c = B.cone(i["kanten"], r0, r0, 1.0, segs=i["segmente"], fill="TRIANGLE_FAN")
    c = _del_bottom(B, c)
    x, y, z = B.sep(B.pos())
    # Profil: bis „prisma“ voller Radius, darüber linear zur Spitze (1 − spitze)
    t = B.m("DIVIDE", B.m("MAXIMUM", B.m("SUBTRACT", z, i["prisma"]), 0.0), B.m("MAXIMUM", B.m("SUBTRACT", 1.0, i["prisma"]), 1e-3))
    top = B.m("SUBTRACT", 1.0, i["spitze"])
    f = B.m("ADD", 1.0, B.m("MULTIPLY", t, B.m("SUBTRACT", top, 1.0)))
    c = B.set_pos(c, position=B.xyz(B.m("MULTIPLY", x, f), B.m("MULTIPLY", y, f), z))
    # Drall um Z, Krümmung + Versatz nach vorn (X)
    x, y, z = B.sep(B.pos())
    vr = B.node("ShaderNodeVectorRotate", rotation_type="Z_AXIS")
    B.set(vr, "Vector", B.pos())
    B.set(vr, "Angle", B.m("MULTIPLY", B.m("MULTIPLY", i["drall"], math.pi), z))
    c = B.set_pos(c, position=B.out(vr))
    z2 = B.m("MULTIPLY", z, z)
    c = B.set_pos(c, offset=B.xyz(B.m("ADD", B.m("MULTIPLY", i["kruemmung"], B.m("MULTIPLY", z2, 0.7)), B.m("MULTIPLY", i["spitze_versatz"], z)),
                                  0.0, B.m("MULTIPLY", B.m("MULTIPLY", i["kruemmung"], z2), -0.25)))
    up = B.cmp(z, 0.02, "GREATER_THAN", "FLOAT")
    c = _jitter(B, c, B.m("MULTIPLY", i["bruch"], B.m("MULTIPLY", r0, 0.35)), i["seed"], up)
    return c


def _fam_platte(B, i):
    segs = B.m("ADD", i["stufen"], 1.0)
    c = B.cone(i["ecken"], B.m("MULTIPLY", 0.5, B.m("SUBTRACT", 1.0, i["fase"])), 0.5, i["dicke"], segs=segs, fill="TRIANGLE_FAN")
    c = _del_bottom(B, c)
    x, y, z = B.sep(B.pos())
    # Stufen: Zwischenringe nach innen (Terrassen)
    zr = B.m("DIVIDE", z, B.m("MAXIMUM", i["dicke"], 1e-4))
    inner = B.m("MULTIPLY", B.cmp(zr, 0.05, "GREATER_THAN", "FLOAT"), B.cmp(zr, 0.95, "LESS_THAN", "FLOAT"))
    sk = B.m("SUBTRACT", 1.0, B.m("MULTIPLY", inner, 0.12))
    c = B.set_pos(c, position=B.xyz(B.m("MULTIPLY", x, sk), B.m("MULTIPLY", y, sk), z))
    # unregelmäßiger Rand: radialer Zufall pro Winkel
    x, y, z = B.sep(B.pos())
    ang = B.m("ARCTAN2", y, x)
    aid = B.m("ROUND", B.m("MULTIPLY", ang, 20.0))
    rr = B.rnd(i["seed"], -1.0, 1.0, "FLOAT", ident=B.out(B.node("FunctionNodeFloatToInt", {"Float": aid})))
    rs = B.m("ADD", 1.0, B.m("MULTIPLY", rr, B.m("MULTIPLY", i["bruch"], 0.22)))
    c = B.set_pos(c, position=B.xyz(B.m("MULTIPLY", x, rs), B.m("MULTIPLY", y, rs), z))
    # Wölbung (Mitte oben), Rippen
    x, y, z = B.sep(B.pos())
    centre = B.m("LESS_THAN", B.v("LENGTH", B.xyz(x, y, 0.0)), 0.01)
    topv = B.cmp(zr, 0.99, "GREATER_THAN", "FLOAT")
    rip = B.m("MULTIPLY", B.m("MULTIPLY", i["rippen"], 0.06), B.m("COSINE", B.m("MULTIPLY", x, 4 * math.pi)))
    c = B.set_pos(c, offset=B.xyz(0.0, 0.0, B.m("ADD", B.m("MULTIPLY", centre, i["woelbung"]), B.m("MULTIPLY", topv, rip))))
    return _stretch(B, c, i["streckung"])


def _stretch(B, geo, s):
    x, y, z = B.sep(B.pos())
    return B.set_pos(geo, position=B.xyz(B.m("MULTIPLY", x, s), y, z))


def _fam_brocken(B, i):
    pts = B.node("GeometryNodePoints", {"Count": i["punkte"]})
    rv = B.rnd(i["seed"], (-1.0, -1.0, 0.0), (1.0, 1.0, 1.0), "FLOAT_VECTOR")
    sx, sy, sz = B.sep(rv)
    # Punkte auf einer gestauchten Halbkugel, Oberseite abgeflacht (blockig)
    zz = B.m("MULTIPLY", B.m("POWER", sz, B.m("SUBTRACT", 1.0, B.m("MULTIPLY", i["blockig"], 0.7))), i["dicke"])
    pos = B.xyz(B.m("MULTIPLY", sx, 0.5), B.m("MULTIPLY", sy, 0.45), zz)
    p = B.set_pos(B.out(pts), position=pos)
    # Fußring (flache Unterseite)
    circ = B.out(B.node("GeometryNodeMeshCircle", {"Vertices": 7, "Radius": 0.42}))
    hull = B.out(B.node("GeometryNodeConvexHull", {"Geometry": B.join(p, circ)}))
    return _stretch(B, hull, i["streckung"])


def _fam_pilz(B, i):
    seg = i["segmente"]
    stiel = B.cone(seg, 0.07, 0.09, i["stiel_hoehe"], fill="NONE")
    hut_h = B.m("ADD", 0.12, B.m("MULTIPLY", i["hut_form"], 0.4))
    hut = B.cone(seg, 0.0, B.m("MULTIPLY", i["hut_breite"], 0.5), hut_h, fill="TRIANGLE_FAN")
    hut = B.set_pos(hut, offset=B.xyz(0.0, 0.0, B.m("SUBTRACT", i["stiel_hoehe"], 0.02)))
    one = B.join(stiel, hut)
    pts = B.node("GeometryNodePoints", {"Count": i["pro_gruppe"]})
    rv = B.rnd(i["seed"], (-1.0, -1.0, 0.0), (1.0, 1.0, 0.0), "FLOAT_VECTOR")
    first = B.cmp(B.index(), 0, "EQUAL", "INT")
    pp = B.switch("VECTOR", first, B.v("SCALE", rv, scale=B.m("MULTIPLY", i["streuung"], B.m("MULTIPLY", i["hut_breite"], 0.8))), (0.0, 0.0, 0.0))
    p = B.set_pos(B.out(pts), position=pp)
    sc = B.switch("FLOAT", first, B.rnd(B.m("ADD", i["seed"], 5), 0.55, 0.85), 1.0)
    tilt = B.rnd(B.m("ADD", i["seed"], 9), (-0.25, -0.25, -3.14), (0.25, 0.25, 3.14), "FLOAT_VECTOR")
    e2r = B.node("FunctionNodeEulerToRotation", {"Euler": tilt})
    iop = B.node("GeometryNodeInstanceOnPoints")
    B.set(iop, "Points", p)
    B.set(iop, "Instance", one)
    B.set(iop, "Scale", B.xyz(sc, sc, sc))
    B.set(iop, "Rotation", B.out(e2r))
    return B.out(B.node("GeometryNodeRealizeInstances", {"Geometry": B.out(iop)}))


def _fam_polster(B, i):
    c = B.cone(i["ecken"], 0.22, 0.5, i["kuppel_hoehe"], segs=2, fill="TRIANGLE_FAN")
    c = _del_bottom(B, c)
    x, y, z = B.sep(B.pos())
    ang = B.m("ARCTAN2", y, x)
    rr = B.rnd(i["seed"], -1.0, 1.0, "FLOAT", ident=B.out(B.node("FunctionNodeFloatToInt", {"Float": B.m("ROUND", B.m("MULTIPLY", ang, 20.0))})))
    rs = B.m("ADD", 1.0, B.m("MULTIPLY", rr, B.m("MULTIPLY", i["rand_zacken"], 0.25)))
    c = B.set_pos(c, position=B.xyz(B.m("MULTIPLY", x, rs), B.m("MULTIPLY", y, rs), z))
    c = _jitter(B, c, B.m("MULTIPLY", i["rauheit"], 0.05), i["seed"], B.cmp(z, 0.01, "GREATER_THAN", "FLOAT"))
    # Zotteln am Rand: kleine dreikantige Spitzen schräg nach außen/unten
    circ = B.node("GeometryNodeMeshCircle", {"Vertices": B.m("MAXIMUM", i["zottel_rand"], 1.0), "Radius": 0.46})
    cpos = B.pos()
    outv = B.v("NORMALIZE", cpos)
    ax = B.node("FunctionNodeAxesToRotation", primary_axis="Z", secondary_axis="X")
    B.set(ax, "Primary Axis", B.v("NORMALIZE", B.v("ADD", outv, (0.0, 0.0, -0.35))))
    B.set(ax, "Secondary Axis", (0.0, 0.0, 1.0))
    z_cone = B.cone(3, 0.0, 0.05, 0.16)
    iop = B.node("GeometryNodeInstanceOnPoints")
    B.set(iop, "Points", B.out(circ))
    B.set(iop, "Instance", z_cone)
    B.set(iop, "Rotation", B.out(ax))
    B.set(iop, "Scale", B.xyz(1.0, 1.0, B.rnd(B.m("ADD", i["seed"], 3), 0.7, 1.3)))
    zot = B.out(B.node("GeometryNodeRealizeInstances", {"Geometry": B.out(iop)}))
    zot = B.set_pos(zot, offset=(0.0, 0.0, 0.03))
    zot = B.switch("GEOMETRY", B.cmp(i["zottel_rand"], 0, "GREATER_THAN", "INT"), None, zot)
    return B.join(c, zot)


def _fam_streifen(B, i):
    grid = B.node("GeometryNodeMeshGrid", {"Size X": i["breite"], "Size Y": 1.0, "Vertices X": 2,
                                          "Vertices Y": B.m("ADD", i["abschnitte"], 1.0)})
    g = B.transform(B.out(grid), t=(0, 0, 0.5), r=(math.pi / 2, 0, 0))   # steht entlang +Z, Fuß bei z = 0
    x, y, z = B.sep(B.pos())
    # zur Spitze schmaler + Zacken am Rand
    za = B.rnd(i["seed"], -1.0, 1.0, "FLOAT", ident=B.out(B.node("FunctionNodeFloatToInt", {"Float": B.m("ROUND", B.m("MULTIPLY", z, 50.0))})))
    w = B.m("MULTIPLY", B.m("SUBTRACT", 1.0, B.m("MULTIPLY", z, 0.8)), B.m("ADD", 1.0, B.m("MULTIPLY", za, B.m("MULTIPLY", i["zacken"], 0.5))))
    g = B.set_pos(g, position=B.xyz(B.m("MULTIPLY", x, w), y, z))
    x, y, z = B.sep(B.pos())
    bend = B.m("MULTIPLY", B.m("MULTIPLY", z, z), B.m("MULTIPLY", i["kruemmung"], 0.6))
    wave = B.m("MULTIPLY", B.m("SINE", B.m("MULTIPLY", z, 2.5 * math.pi)), B.m("MULTIPLY", i["wellen"], 0.12))
    g = B.set_pos(g, offset=B.xyz(wave, bend, B.m("MULTIPLY", bend, -0.3)))
    flip = B.out(B.node("GeometryNodeFlipFaces", {"Mesh": g}))
    blatt = B.join(g, flip)   # doppelseitig (dünn)
    pts = B.node("GeometryNodePoints", {"Count": i["anzahl"]})
    idx = B.index()
    spread = B.m("MULTIPLY", i["faecher"], 1.1)
    yaw = B.m("MULTIPLY", B.m("DIVIDE", idx, B.m("MAXIMUM", i["anzahl"], 1.0)), 2 * math.pi)
    rot = B.xyz(0.0, B.m("MULTIPLY", spread, 0.6), B.m("ADD", yaw, B.rnd(i["seed"], -0.4, 0.4)))
    pp = B.xyz(B.m("MULTIPLY", B.m("COSINE", yaw), B.m("MULTIPLY", i["faecher"], 0.12)),
               B.m("MULTIPLY", B.m("SINE", yaw), B.m("MULTIPLY", i["faecher"], 0.12)), 0.0)
    p = B.set_pos(B.out(pts), position=pp)
    iop = B.node("GeometryNodeInstanceOnPoints")
    B.set(iop, "Points", p)
    B.set(iop, "Instance", blatt)
    B.set(iop, "Rotation", B.out(B.node("FunctionNodeEulerToRotation", {"Euler": rot})))
    B.set(iop, "Scale", B.xyz(1.0, 1.0, B.rnd(B.m("ADD", i["seed"], 2), 0.7, 1.0)))
    return B.out(B.node("GeometryNodeRealizeInstances", {"Geometry": B.out(iop)}))


def _fam_kette(B, i):
    prof = B.node("GeometryNodeCurvePrimitiveCircle", {"Resolution": 3, "Radius": B.m("MULTIPLY", i["glied_dicke"], 0.6)})
    ring = B.node("GeometryNodeCurvePrimitiveCircle", {"Resolution": 4, "Radius": 0.5})
    c2m = B.node("GeometryNodeCurveToMesh")
    B.set(c2m, "Curve", B.out(ring))
    B.set(c2m, "Profile Curve", B.out(prof))
    link = B.transform(B.out(c2m), r=(math.pi / 2, 0, 0), s=(0.6, 1.0, 1.0))
    line = B.node("GeometryNodeMeshLine", {"Count": i["glieder"], "Start Location": (0, 0, 0.5), "Offset": (0, 0, 0.62)})
    idx = B.index()
    odd = B.m("MODULO", idx, 2.0)
    x, y, z = B.sep(B.pos())
    sag = B.m("MULTIPLY", B.m("MULTIPLY", z, z), B.m("MULTIPLY", i["durchhang"], 0.15))
    p = B.set_pos(B.out(line), offset=B.xyz(sag, 0.0, 0.0))
    iop = B.node("GeometryNodeInstanceOnPoints")
    B.set(iop, "Points", p)
    B.set(iop, "Instance", link)
    B.set(iop, "Rotation", B.out(B.node("FunctionNodeEulerToRotation", {"Euler": B.xyz(0.0, 0.0, B.m("MULTIPLY", odd, math.pi / 2))})))
    return B.out(B.node("GeometryNodeRealizeInstances", {"Geometry": B.out(iop)}))


# ------------------------------------------------------------------------------------------------ Werkbank-Objekt
WB_OBJ = "VK_Werkbank"


def ensure_workbench(typ, werte, location=(1.4, 0.0, 0.0)):
    fam = TYPEN[typ][0]
    ng = bpy.data.node_groups.get(f"VK_Baustein_{fam}")
    if ng is None or "vk_ids" not in ng:
        ng, ids = build_family(fam)
    ids = json.loads(ng["vk_ids"])
    ob = bpy.data.objects.get(WB_OBJ)
    if ob is None:
        me = bpy.data.meshes.new(WB_OBJ)
        ob = bpy.data.objects.new(WB_OBJ, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = location
        ob.scale = (0.4, 0.4, 0.4)
    mod = ob.modifiers.get("VK_Baustein") or ob.modifiers.new("VK_Baustein", "NODES")
    mod.node_group = ng
    for k, v in werte.items():
        if k in ids:
            t = next(t for kk, t, *_ in FAMILIEN[fam] if kk == k)
            vk_nodes.set_mod_input(mod, ids, k, int(v) if t == "int" else float(v))
    ob["vk_typ"] = typ
    ob.update_tag()
    return ob


def evaluate_form(ob):
    """Mesh der Werkbank auswerten und normieren (Ursprung Mitte Unterseite, größte Ausdehnung 1)."""
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        me.calc_loop_triangles()
        n = len(me.vertices)
        co = np.empty(n * 3, np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(n, 3).astype(np.float64)
        tri = np.empty(len(me.loop_triangles) * 3, np.int32)
        me.loop_triangles.foreach_get("vertices", tri)
        tri = tri.reshape(-1, 3)
    finally:
        ev.to_mesh_clear()
    used = np.unique(tri)
    remap = -np.ones(n, np.int64)
    remap[used] = np.arange(len(used))
    co = co[used]
    tri = remap[tri]
    mn, mx = co.min(0), co.max(0)
    cx, cy, z0 = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]
    ext = max(float((mx - mn).max()), 1e-6)
    co = (co - np.array([cx, cy, z0])) / ext
    return co, tri


def save_form(typ, form, werte, co, tri):
    """Eine Form in procedural/bausteine/<typ>.json schreiben (andere Formen bleiben), dann FBX/GLB neu."""
    fam = TYPEN[typ][0]
    lib = read_lib(typ) or {"format": "baustein_bibliothek", "version": VERSION, "typ": typ,
                            "koordinaten": "X vorn/Laenge, Y links/Breite, Z oben/Hoehe; Ursprung Mitte Unterseite; groesste Ausdehnung 1.0",
                            "formen": {}}
    lib["version"] = VERSION
    dims = (co.max(0) - co.min(0)).tolist()
    lib.setdefault("formen", {})[form] = {
        "werte": dict(familie=fam, **{k: (int(v) if isinstance(v, (bool, int)) or float(v).is_integer() and k in ("kanten", "segmente", "ecken", "stufen", "punkte", "pro_gruppe", "zottel_rand", "anzahl", "abschnitte", "glieder", "seed") else round(float(v), 4)) for k, v in werte.items()}),
        "tris": int(len(tri)),
        "masse": [round(float(d), 3) for d in dims],
        "vertices": [[round(float(c), 5) for c in v] for v in co],
        "dreiecke": [[int(a) for a in t] for t in tri],
    }
    os.makedirs(lib_dir(), exist_ok=True)
    with open(lib_path(typ), "w", encoding="utf-8", newline="\n") as f:
        json.dump(lib, f, ensure_ascii=False, indent=1)
    export_meshes(typ, lib)
    return lib["formen"][form]


def export_meshes(typ, lib):
    """Alle Formen eines Typs als FBX + GLB (für Menschen/andere Programme; Unity liest die JSON)."""
    scene = bpy.data.scenes.new("VK_Export")
    obs = []
    try:
        for k, (name, f) in enumerate(lib.get("formen", {}).items()):
            me = bpy.data.meshes.new(name)
            me.from_pydata([tuple(v) for v in f["vertices"]], [], [tuple(t) for t in f["dreiecke"]])
            me.update()
            ob = bpy.data.objects.new(name, me)
            ob.location.x = k * 1.5
            scene.collection.objects.link(ob)
            obs.append(ob)
        with bpy.context.temp_override(scene=scene):
            bpy.ops.export_scene.fbx(filepath=os.path.join(lib_dir(), f"{typ}.fbx"), use_selection=False, apply_unit_scale=True,
                                     object_types={"MESH"}, mesh_smooth_type="FACE", add_leaf_bones=False)
            bpy.ops.export_scene.gltf(filepath=os.path.join(lib_dir(), f"{typ}.glb"), export_format="GLB", use_selection=False,
                                      use_active_scene=True)
    finally:
        for o in obs:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(me)
        bpy.data.scenes.remove(scene)


def generate_missing(only=None, overwrite=False):
    """Startformen aller Typen erzeugen, deren Bibliothek fehlt (M1-Typen bleiben unberührt)."""
    done = []
    for typ, (fam, formen) in TYPEN.items():
        if only and typ != only:
            continue
        if not formen:
            continue
        if os.path.exists(lib_path(typ)) and not overwrite:
            continue
        for form, w in formen.items():
            werte = defaults(fam)
            werte.update(w)
            ob = ensure_workbench(typ, werte)
            co, tri = evaluate_form(ob)
            save_form(typ, form, werte, co, tri)
            print(f"[bausteine] {typ}/{form}: {len(tri)} Tris")
        done.append(typ)
    ob = bpy.data.objects.get(WB_OBJ)
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)
    return done
