"""Prüft, ob der Kopf-Aufbau (Geweih, Hörner) starr mit dem Kopf-Knochen mitgeht (C14, Hollow Stag).

  & "D:\\Blender\\blender.exe" -b <clips.blend> -P rigging/check_rigid_head.py -- <ausgabe.json> [<creature.toml>]

Geweih = alle Vertices über der Kopf-Oberkante (höchster Punkt des Head-Knochens + rigid_head_above · Höhe), die über
diese Zone zusammenhängend mit dem Kopf verbunden sind (also auch Sprossen, die nach hinten über die Schulter ragen).
Messwerte:
  static_bad        Geweih-Vertices mit Gewicht auf einem anderen Knochen als Head (Ziel 0)
  above_not_head    ALLE Vertices über der Kopf-Oberkante (ohne Zusammenhang) mit Fremd-Gewicht (Info)
  max_dev_cm        größte Abweichung eines Geweih-Vertex von einer starren Kopfbewegung, über alle Clips/Frames (Ziel ≈ 0)
Nichts wird verändert – nur gelesen.
"""
import json
import pathlib
import sys
import tomllib

import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
OUT = pathlib.Path(a[0]).resolve()
margin = 0.02
if len(a) > 1:
    q = tomllib.loads(pathlib.Path(a[1]).read_text(encoding="utf-8")).get("quadruped", {}).get("rig", {})
    margin = q.get("rigid_head_above", margin)

sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = bpy.data.objects.get("Body_Mesh")
me = body.data
n = len(me.vertices)
co = np.zeros(n * 3)
me.vertices.foreach_get("co", co)
mw_b = np.array(body.matrix_world)
R = co.reshape(-1, 3) @ mw_b[:3, :3].T + mw_b[:3, 3]           # Ruhepose, Welt

ground, H = R[:, 2].min(), R[:, 2].max() - R[:, 2].min()
mw_a = np.array(arm.matrix_world)
hb = arm.data.bones["Head"]
hh = mw_a[:3, :3] @ np.array(hb.head_local) + mw_a[:3, 3]
ht = mw_a[:3, :3] @ np.array(hb.tail_local) + mw_a[:3, 3]
hb_top = max(hh[2], ht[2])
above = R[:, 2] > hb_top + margin * H

# Zusammenhang innerhalb der Zone über der Kopf-Oberkante (UV-Nähte: gleiche Position = verbunden)
par = np.arange(n)


def find(i):
    while par[i] != i:
        par[i] = par[par[i]]
        i = par[i]
    return i


key = {}
for i, p in enumerate(np.round(R, 5)):
    j = key.setdefault(tuple(p), i)
    if j != i:
        par[find(i)] = find(j)
for e in me.edges:
    u, v = e.vertices
    if above[u] and above[v]:
        par[find(u)] = find(v)
comp = np.array([find(i) for i in range(n)])
seed = above & (R[:, 0] >= hh[0])                                # über dem Schädel (vor dem Kopfansatz)
antler = above & np.isin(comp, np.unique(comp[seed]))

gi = {g.index: g.name for g in body.vertex_groups}
head_w = np.zeros(n)
other_w = np.zeros(n)
other_by = {}
for v in me.vertices:
    for g in v.groups:
        if gi[g.group] == "Head":
            head_w[v.index] = g.weight
        elif g.weight > 1e-4:
            other_w[v.index] += g.weight
            if antler[v.index]:
                other_by[gi[g.group]] = other_by.get(gi[g.group], 0) + 1
static_bad = antler & (other_w > 1e-4)
above_bad = above & (other_w > 1e-4)

# Abweichung von der starren Kopfbewegung
pb = arm.pose.bones["Head"]
inv_rest = np.linalg.inv(np.array(hb.matrix_local))
inv_a = np.linalg.inv(mw_a)
idx = np.where(antler)[0]
Ra = np.c_[R[idx], np.ones(len(idx))]
res = {"vertices": n, "antler_vertices": int(antler.sum()), "above_vertices": int(above.sum()),
       "antler_behind_shoulder": None, "static_bad": int(static_bad.sum()), "above_not_head": int(above_bad.sum()),
       "static_bad_bones": other_by, "clips": {}}
if "Leg_FL_1" in arm.data.bones:
    x_sh = (np.array(arm.data.bones["Leg_FL_1"].head_local)[0] + np.array(arm.data.bones["Leg_FR_1"].head_local)[0]) / 2
    res["antler_behind_shoulder"] = int((antler & (R[:, 0] <= x_sh)).sum())
buf = np.zeros(n * 3)
worst = (0.0, None, None)
for act in sorted(bpy.data.actions, key=lambda x: x.name):
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and act.slots:
        arm.animation_data.action_slot = act.slots[0]
    f0, f1 = (int(v) for v in act.frame_range)
    cmax, cf = 0.0, f0
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        ev = body.evaluated_get(dg)
        em = ev.to_mesh()
        em.vertices.foreach_get("co", buf)
        ev.to_mesh_clear()
        mwb = np.array(body.matrix_world)
        P = buf.reshape(-1, 3)[idx] @ mwb[:3, :3].T + mwb[:3, 3]
        T = mw_a @ np.array(pb.matrix) @ inv_rest @ inv_a        # starre Kopfbewegung in Weltkoordinaten
        E = (Ra @ T.T)[:, :3]
        d = np.linalg.norm(P - E, axis=1)
        if d.max() > cmax:
            cmax, cf = float(d.max()), f
        if d.max() > worst[0]:
            worst = (float(d.max()), act.name, f)
    res["clips"][act.name] = {"max_dev_cm": round(cmax * 100, 3), "frame": cf}
res["max_dev_cm"] = round(worst[0] * 100, 3)
res["worst"] = {"clip": worst[1], "frame": worst[2]}
res["ok"] = res["static_bad"] == 0 and res["max_dev_cm"] < 0.1
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"RIGID_HEAD {'OK' if res['ok'] else 'FEHLER'} · Geweih {res['antler_vertices']} Vertices "
      f"({res['antler_behind_shoulder']} hinter der Schulter) · Fremd-Gewicht {res['static_bad']} "
      f"{other_by} · max. Abweichung {res['max_dev_cm']} cm ({worst[1]} F{worst[2]})")
