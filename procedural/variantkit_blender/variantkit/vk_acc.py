"""Accessoires aus Unity in Blender anzeigen (nur lesen, Spec 6.3 / E6): <id>.instanzen.json → ein Mesh-Objekt mit den
Bausteinen an ihren Plätzen, Gewichte = Anker-Gewichte (läuft im Clip mit). Dazu eine Punktwolke „VK_Acc_Punkte“
(Ansatzpunkte + Radius), unter der die Bedeckung ausgespart wird (`accessoires_aussparen`)."""
import os

import bpy
import numpy as np

from . import vk_json

ACC_OBJ = "VK_Accessoires"
PTS_OBJ = "VK_Acc_Punkte"


def instances_path(doc):
    return os.path.join(os.path.dirname(doc.path), doc.id + ".instanzen.json")


def _lib(typ, cache):
    if typ not in cache:
        p = os.path.join(vk_json.pipeline_root(), "procedural", "bausteine", typ + ".json")
        cache[typ] = vk_json.read_file(p) if os.path.exists(p) else {"formen": {}}
    return cache[typ]


def _remove(name):
    ob = bpy.data.objects.get(name)
    if ob is not None:
        me = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


def build(an, arm, doc, coll):
    """→ (Objekt oder None, Punktwolke oder None, Info-Text, Tris)."""
    p = instances_path(doc)
    _remove(ACC_OBJ)
    _remove(PTS_OBJ)
    if not os.path.exists(p):
        return None, None, "keine Instanzen-Liste (in Unity „Backen“ oder „In Blender bauen“)", 0
    data = vk_json.read_file(p)
    inst = data.get("instanzen", [])
    fwd, left, up = an.fwd, an.left, an.up

    def to_mesh(v):   # Unity-Datei: x vorn, y links, z oben (Meter, Ursprung = Mesh-Ursprung)
        v = np.asarray(v, np.float64)
        return v[..., 0:1] * fwd + v[..., 1:2] * left + v[..., 2:3] * up

    cache = {}
    verts, faces, wts, mats = [], [], [], []
    anchors, radii = [], []
    for it in inst:
        f = _lib(it.get("typ", ""), cache).get("formen", {}).get(it.get("form", ""))
        if not f:
            continue
        fv = np.asarray(f["vertices"], np.float64)
        P = to_mesh(it["position"])
        AX, AY, AZ = to_mesh(it["achse_x"]), to_mesh(it["achse_y"]), to_mesh(it["achse_z"])
        wv = P + fv[:, 0:1] * AX + fv[:, 1:2] * AY + fv[:, 2:3] * AZ
        v0 = len(verts)
        verts.extend(wv.tolist())
        for t in f["dreiecke"]:
            faces.append((v0 + t[0], v0 + t[1], v0 + t[2]))
        wts.append((v0, len(fv), it.get("anker_gewichte", {})))
        anchors.append(to_mesh(it.get("ansatz", it["position"])).tolist())
        radii.append(0.5 * max(np.linalg.norm(AX), np.linalg.norm(AY)) * 0.9)
    if not verts:
        return None, None, "Instanzen-Liste leer", 0
    me = bpy.data.meshes.new(ACC_OBJ)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(ACC_OBJ, me)
    coll.objects.link(ob)
    ob.parent = arm
    groups = {}
    for v0, n, w in wts:
        for bone, wt in w.items():
            g = groups.get(bone) or ob.vertex_groups.new(name=bone)
            groups[bone] = g
            g.add(list(range(v0, v0 + n)), float(wt), "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    mat = bpy.data.materials.get("VK_accessoire") or bpy.data.materials.new("VK_accessoire")
    fg = doc.resolved.get("material", {}).get("farbgruppen", {}).get("accessoire_a", {})
    from .vk_cover import hex_rgb
    mat.diffuse_color = hex_rgb(fg.get("farbe", "#808084")) + (1.0,)
    me.materials.append(mat)
    for poly in me.polygons:
        poly.use_smooth = False
    ob.hide_select = True
    # Punktwolke zum Aussparen
    pm = bpy.data.meshes.new(PTS_OBJ)
    pm.from_pydata(anchors, [], [])
    a = pm.attributes.new("radius", "FLOAT", "POINT")
    a.data.foreach_set("value", np.asarray(radii, np.float32))
    po = bpy.data.objects.new(PTS_OBJ, pm)
    coll.objects.link(po)
    po.hide_viewport = True
    po.hide_render = True
    stale = data.get("quell_hash") and data.get("quell_hash") != _hash_hint(doc)
    info = f"{len(inst)} Teile aus {os.path.basename(p)}" + (" (Stand der letzten Unity-Platzierung)" if stale else "")
    return ob, po, info, len(faces)


def _hash_hint(doc):
    return None
