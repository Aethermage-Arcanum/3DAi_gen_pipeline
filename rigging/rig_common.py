"""Gemeinsame Rig-Bausteine für alle Skelette außer crawler/quadruped (die haben ihre eigenen, validierten Versionen).

- load_mesh(src)               glTF laden, zusammenführen, Transformationen anwenden → (obj, V, part, MAIN)
- seg_dist(P, a, b)            Abstand Punkte → Knochen-Strecke
- skin(obj, V, part, MAIN, bones, names, allow, cfg)
                               Gewichte: 1/Abstand^falloff + Masken, Glätten über Kanten UND über Doppel-Vertices
                               (Tripo trennt an UV-Nähten – ohne Angleichen reißt das Mesh), max. 4 Einflüsse
- build_armature(name, bones, order)   Edit-Bones anlegen (bones: Name → (Kopf, Schwanz, Eltern))
- finish(obj, arm, out, blend_name, report, bones, order, V)   Modifier, Flat Shading, speichern, Debug-Daten
"""
import json

import bpy
import numpy as np
from mathutils import Vector


def load_mesh(src):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(src))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in bpy.data.objects:
        o.select_set(o in meshes)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "Body_Mesh"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return (obj,) + arrays(obj)


def delete_faces(obj, face_mask):
    """Flächen löschen (z. B. Tripo-Hautbrücken zwischen Beinen), lose Vertices mit entfernen."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if face_mask[f.index]], context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def arrays(obj):
    """(V, part, MAIN) für das aktuelle Mesh: Positionen, Teil-Nummer je Vertex, größtes Teil."""
    me = obj.data
    V = np.array([v.co[:] for v in me.vertices])
    N = len(V)
    parent = np.arange(N)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    key = {}
    for i, co in enumerate(np.round(V, 5)):
        j = key.setdefault(tuple(co), i)
        if j != i:
            parent[find(i)] = find(j)
    for e in me.edges:
        parent[find(e.vertices[0])] = find(e.vertices[1])
    part = np.array([find(i) for i in range(N)])
    ids, counts = np.unique(part, return_counts=True)
    return V, part, ids[np.argmax(counts)]


def seg_dist(P, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(1e-12, ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def skin(obj, V, part, MAIN, bones, names, allow, cfg):
    me = obj.data
    N = len(V)
    Dm = np.stack([seg_dist(V, bones[n][0], bones[n][1]) for n in names], 1)
    W = np.where(allow, 1.0 / (Dm + 1e-4) ** cfg["falloff"], 0.0)
    empty = W.sum(1) == 0
    W[empty] = 1.0 / (Dm[empty] + 1e-4) ** cfg["falloff"]
    W /= W.sum(1, keepdims=True)
    E = np.array([e.vertices[:] for e in me.edges])
    groups = {}
    for i, co in enumerate(np.round(V, 5)):
        groups.setdefault(tuple(co), []).append(i)
    weld = [g for g in groups.values() if len(g) > 1]
    if weld:
        E = np.vstack([E] + [np.array([[g[0], x] for x in g[1:]]) for g in weld])
    for _ in range(cfg["smooth_iterations"]):
        acc, cnt = np.zeros_like(W), np.zeros(N)
        np.add.at(acc, E[:, 0], W[E[:, 1]])
        np.add.at(acc, E[:, 1], W[E[:, 0]])
        np.add.at(cnt, E[:, 0], 1)
        np.add.at(cnt, E[:, 1], 1)
        sm = np.where(cnt[:, None] > 0, acc / np.maximum(cnt, 1)[:, None], W)
        W = (1 - cfg["smooth_factor"]) * W + cfg["smooth_factor"] * sm
        W = np.where(allow | empty[:, None], W, 0.0)
        W /= np.maximum(W.sum(1, keepdims=True), 1e-12)
    for g in weld:
        W[g] = W[g].mean(0)
    top = np.argsort(-W, 1)[:, :4]
    for n in names:
        obj.vertex_groups.new(name=n)
    for i in range(N):
        ws = W[i, top[i]]
        ws = ws / ws.sum()
        for j, w in zip(top[i], ws):
            if w > 1e-3:
                obj.vertex_groups[names[j]].add([i], float(w), "REPLACE")
    return W


def build_armature(name, bones, order, H):
    data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for n in order:
        hd, tl, _ = bones[n]
        eb = data.edit_bones.new(n)
        eb.head, eb.tail = Vector(hd), Vector(tl)
        if (eb.tail - eb.head).length < 1e-4:
            eb.tail = eb.head + Vector((0, 0, 0.01 * H))
        eb.roll = 0.0
    for n in order:
        p = bones[n][2]
        if p:
            data.edit_bones[n].parent = data.edit_bones[p]
            data.edit_bones[n].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def finish(obj, arm, out, blend_name, report, bones, order, V, tracks=None):
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    obj.parent = arm
    for p in obj.data.polygons:
        p.use_smooth = False
    bpy.ops.wm.save_as_mainfile(filepath=str(out / blend_name))
    (out / "rig_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    sample = V[::max(1, len(V) // 4000)]
    (out / "rig_debug.json").write_text(json.dumps({
        "verts": np.round(sample, 4).tolist(),
        "bones": {n: [np.round(np.asarray(bones[n][0], float), 4).tolist(),
                      np.round(np.asarray(bones[n][1], float), 4).tolist()] for n in order},
        "tracks": tracks or {}}), encoding="utf-8")
    print("RIG_OK", json.dumps(report, ensure_ascii=False))
