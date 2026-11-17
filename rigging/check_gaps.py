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


def mirror_limbs(a_, b_):
    """Linkes vs. rechtes Glied derselben Art (z. B. Leg_BL_2 / Leg_BR_2) dürfen auseinanderlaufen –
    wenn sie in Ruhe aneinanderliegen, ist das keine Gelenk-Lücke, sondern Beine im Gegentakt."""
    import re
    m1, m2 = re.match(r"(Leg_[A-Z]?)([LR])(.*)", a_), re.match(r"(Leg_[A-Z]?)([LR])(.*)", b_)
    if m1 and m2 and m1.group(1) == m2.group(1) and m1.group(2) != m2.group(2):
        return True
    # verschiedene Gliedmaßen (z. B. Leg_R4_* / Leg_R5_* beim Mehrbeiner) dürfen sich auch trennen
    limb = lambda n: n.rsplit("_", 1)[0] if re.match(r"(Leg_[LR]\d|Claw_[LR])_\d", n) else None  # noqa: E731
    return bool(limb(a_) and limb(b_) and limb(a_) != limb(b_))


for i, c in enumerate(rest):
    for (p, j, d) in kd.find_range(c, EPS):
        if j > i and isl[i] != isl[j] and dom[i] != dom[j] and dom[i] and dom[j] \
                and (dom[i].startswith("Leg_") or dom[j].startswith("Leg_")) and not mirror_limbs(dom[i], dom[j]):
            pairs.append((i, j, d))

sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
worst = {}
max_open = 0.0
per_clip = {}
# Alle Clips prüfen (jede Action des Rigs)
for act in [a_ for a_ in bpy.data.actions if a_.users or a_.use_fake_user]:
    arm.animation_data.action = act
    f0, f1 = (int(v) for v in act.frame_range)
    clip_max = 0.0
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(dg)
        m = ev.to_mesh()
        for i, j, d0 in pairs:
            opening = (m.vertices[i].co - m.vertices[j].co).length - d0
            key = f"{act.name}: " + " / ".join(sorted((dom[i], dom[j])))
            if opening > worst.get(key, (0,))[0]:
                worst[key] = (opening, f)
            clip_max = max(clip_max, opening)
        ev.to_mesh_clear()
    per_clip[act.name] = round(clip_max, 4)
    max_open = max(max_open, clip_max)

bad = {k: v for k, v in worst.items() if v[0] > THR}
report = {"pairs_checked": len(pairs), "threshold_m": round(THR, 4),
          "max_opening_m": round(max_open, 4), "joints_over_threshold": len(bad), "per_clip_max_m": per_clip,
          "worst": sorted([[k, round(v[0], 4), v[1]] for k, v in worst.items()], key=lambda x: -x[1])[:12],
          "ok": not bad}
open(OUT, "w", encoding="utf-8").write(json.dumps(report, indent=2, ensure_ascii=False))
print("GAPS", json.dumps({k: v for k, v in report.items() if k != "worst"}, ensure_ascii=False))
for w in report["worst"][:8]:
    print("  GAP", w)
