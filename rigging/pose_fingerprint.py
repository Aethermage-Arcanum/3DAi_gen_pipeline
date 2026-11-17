"""Fingerabdruck aller Clips: Knochen-Posen + verformtes Mesh an festen Frames → JSON.
Zwei Fingerabdrücke vergleicht scripts/regression.py. Gleich = die Kreatur sieht exakt gleich aus.

& "D:\\Blender\\blender.exe" -b <clips.blend> -P rigging/pose_fingerprint.py -- <ausgabe.json> [frame_schritt]
"""
import json
import pathlib
import sys

import bpy

a = sys.argv[sys.argv.index("--") + 1:]
OUT = pathlib.Path(a[0]).resolve()
STEP = int(a[1]) if len(a) > 1 else 1      # jeden Frame: grobe Schritte verpassen schnelle Zyklen (Flügelschlag = 4 Frames)
MAX_VERTS = 250                       # Stichprobe – reicht, um Gewichts-/Mesh-Änderungen zu sehen

sc = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = bpy.data.objects.get("Body_Mesh") or next(o for o in bpy.data.objects if o.type == "MESH" and
                                                 any(m.type == "ARMATURE" for m in o.modifiers))
n = len(body.data.vertices)
idx = list(range(0, n, max(1, n // MAX_VERTS)))
r5 = lambda v: [round(x, 5) for x in v]  # noqa: E731

res = {"bones": [b.name for b in arm.pose.bones], "verts_total": n, "verts_sampled": len(idx), "clips": {}}
for act in sorted(bpy.data.actions, key=lambda x: x.name):
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and act.slots:
        arm.animation_data.action_slot = act.slots[0]
    f0, f1 = (int(v) for v in act.frame_range)
    frames = sorted(set(list(range(f0, f1 + 1, STEP)) + [f1]))
    clip = {}
    for f in frames:
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        me = body.evaluated_get(dg).to_mesh()
        mw = body.matrix_world
        verts = [r5(mw @ me.vertices[i].co) for i in idx]
        body.evaluated_get(dg).to_mesh_clear()
        bones = [r5(pb.matrix.translation) + r5(pb.matrix.to_quaternion()) for pb in arm.pose.bones]
        clip[str(f)] = {"bones": bones, "verts": verts}
    res["clips"][act.name] = clip
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, separators=(",", ":")), encoding="utf-8")
print("FINGERPRINT_OK", len(res["clips"]), "clips", len(idx), "verts")
