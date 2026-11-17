"""Selbstprüfung: Klaffen beim Animieren Lücken zwischen Mesh-Teilen auf (z. B. an den Knien)?

Misst Vertex-Paare aus VERSCHIEDENEN Teilen, die in Ruhe aneinanderliegen (< eps) und an
unterschiedlichen Knochen hängen. Für jedes Frame: wie weit gehen sie auseinander?

& "D:\\Blender\\blender.exe" -b <crawler_walk.blend> -P rigging/check_gaps.py -- <report.json> [eps] [threshold]
"""
import json
import sys

import bmesh
import bpy
from mathutils.kdtree import KDTree

a = sys.argv[sys.argv.index("--") + 1:]
OUT = a[0]
obj = next(o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers))
size = max(obj.dimensions)
EPS = float(a[1]) * size if len(a) > 1 else 0.006 * size
THR = float(a[2]) * size if len(a) > 2 else 0.006 * size   # ab hier sichtbare Lücke (≈ 6 mm bei 1 m)

me = obj.data
# Inseln
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
isl = [-1] * len(bm.verts)
k = 0
for v in bm.verts:
    if isl[v.index] >= 0:
        continue
    stack = [v]
    isl[v.index] = k
    while stack:
        x = stack.pop()
        for e in x.link_edges:
            y = e.other_vert(x)
            if isl[y.index] < 0:
                isl[y.index] = k
                stack.append(y)
    k += 1
bm.free()

names = {g.index: g.name for g in obj.vertex_groups}


def dominant(v):
    if not v.groups:
        return None
    g = max(v.groups, key=lambda g: g.weight)
    return names[g.group]


dom = [dominant(v) for v in me.vertices]
rest = [v.co.copy() for v in me.vertices]
kd = KDTree(len(rest))
for i, c in enumerate(rest):
    kd.insert(c, i)
kd.balance()
pairs = []
for i, c in enumerate(rest):
    for (p, j, d) in kd.find_range(c, EPS):
        if j > i and isl[i] != isl[j] and dom[i] != dom[j] and dom[i] and dom[j] \
                and (dom[i].startswith("Leg_") or dom[j].startswith("Leg_")):
            pairs.append((i, j, d))

sc = bpy.context.scene
worst = {}
max_open = 0.0
for f in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    m = ev.to_mesh()
    for i, j, d0 in pairs:
        opening = (m.vertices[i].co - m.vertices[j].co).length - d0
        key = " / ".join(sorted((dom[i], dom[j])))
        if opening > worst.get(key, (0,))[0]:
            worst[key] = (opening, f)
        max_open = max(max_open, opening)
    ev.to_mesh_clear()

bad = {k: v for k, v in worst.items() if v[0] > THR}
report = {"pairs_checked": len(pairs), "threshold_m": round(THR, 4),
          "max_opening_m": round(max_open, 4), "joints_over_threshold": len(bad),
          "worst": sorted([[k, round(v[0], 4), v[1]] for k, v in worst.items()], key=lambda x: -x[1])[:12],
          "ok": not bad}
open(OUT, "w", encoding="utf-8").write(json.dumps(report, indent=2, ensure_ascii=False))
print("GAPS", json.dumps({k: v for k, v in report.items() if k != "worst"}, ensure_ascii=False))
for w in report["worst"][:8]:
    print("  GAP", w)
