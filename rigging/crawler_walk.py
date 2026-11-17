"""Prozeduraler Laufzyklus für das Standard-Krabbler-Skelett, gebacken als Action "Walk" (in place).

Aufruf:
  & "D:\\Blender\\blender.exe" -b <crawler_rigged.blend> -P rigging/crawler_walk.py -- <ausgabeordner> [<creature.toml>]
Ergebnis: <ausgabe>/crawler_walk.blend, walk_report.json, Vorschau-Frames walk_*.png

Gangart (Naturbeobachtung, siehe Monster-README): Laufbeine bilden zwei Gruppen, die sich abwechseln.
Gruppe A = linke Beine mit ungeradem Slot + rechte Beine mit geradem Slot (L1,R2,L3,R4), Gruppe B = Rest.
  - 8 Laufbeine → alternierender Vierfuß (Spinne)
  - 6 Laufbeine in Slots 1-3 oder 2-4 → Dreifuß-Gang (Ameise/Insekt): vorne+hinten einer Seite + Mitte der anderen
Nicht-Laufbeine (z. B. erhobene Taster) bewegen sich nur leicht tastend.
"""
import json
import math
import pathlib
import sys
import tomllib

import bpy
from mathutils import Euler, Quaternion, Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from crawler_rig import load_cfg  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
OUT = pathlib.Path(args[0]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
cfg = load_cfg(args[1] if len(args) > 1 else None)
W = cfg["walk"]
R = math.radians

arm = bpy.data.objects["Crawler_Rig"]
sc = bpy.context.scene
sc.render.fps = W["fps"]
N = W["cycle_frames"]
sc.frame_start, sc.frame_end = 0, N - 1


def ease(x):  # 0..1 → 0..1 weich
    return 0.5 - 0.5 * math.cos(math.pi * x)


def leg_phase(t, offset, duty):
    """t ∈ [0,1). Liefert (swing: bool, s ∈ [0,1] Fortschritt innerhalb Stand- bzw. Schwungphase)."""
    p = (t + offset) % 1.0
    if p < duty:
        return False, p / duty
    return True, (p - duty) / (1 - duty)


walking = [f"{s}{k}" for k in W["walking_slots"] for s in ("L", "R")]
feelers = [f"{s}{k}" for k in W["feeler_slots"] for s in ("L", "R")]
group_a = {leg for leg in walking if (leg[0] == "L") == (int(leg[1]) % 2 == 1)}

for pb in arm.pose.bones:
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = Euler((0, 0, 0))
    pb.location = Vector((0, 0, 0))

# ---- Bein-Achsen aus der Geometrie (Armature-Raum) → in Knochen-lokale Achsen umrechnen ----
# Gieren = um die Welt-Senkrechte (Füße bleiben auf gleicher Höhe),
# Heben = um die waagerechte Achse quer zum Bein, Vorzeichen so, dass die Spitze steigt.
UP = Vector((0, 0, 1))
leg_axes = {}
size = max(arm.dimensions)
for leg in walking + feelers:
    bones = {p: arm.data.bones[f"Leg_{leg}_{p}"] for p in ("Coxa", "Femur", "Tibia", "Tarsus")}
    root = bones["Coxa"].head_local
    tip = bones["Tarsus"].tail_local
    dir_h = Vector((tip.x - root.x, tip.y - root.y, 0))
    dir_h = dir_h.normalized() if dir_h.length > 1e-6 else Vector((0, 1, 0))
    lift_axis = UP.cross(dir_h).normalized()          # waagerecht, quer zum Bein
    # Vorzeichen: Drehung um +lift_axis soll die Spitze relativ zum Femur-Kopf anheben
    fh = bones["Femur"].head_local
    test = Quaternion(lift_axis, 0.2) @ (tip - fh)
    lift_sign = 1 if (test.z > (tip - fh).z) else -1
    # Gier-Vorzeichen: positive Drehung um UP soll die Spitze nach hinten (−X) bewegen
    yaw_test = Quaternion(UP, 0.2) @ (tip - root)
    back_sign = 1 if yaw_test.x < (tip - root).x else -1

    def local(bone, axis):
        return (bone.matrix_local.to_3x3().inverted() @ axis).normalized()

    # Schwenkwinkel so, dass JEDER Fuß dieselbe Strecke nach hinten schiebt (sonst rutschen Füße in Unity):
    # Fußweg in X bei Gieren ±A um die Hüfte: Δx = 2·r·|sin φ|·sin A
    h = Vector((tip.x - root.x, tip.y - root.y, 0))
    r, phi = h.length, math.atan2(h.y, h.x)
    target = W["stride"] * size
    ratio = target / max(1e-6, 2 * r * abs(math.sin(phi)))
    amp = math.asin(min(1.0, ratio))
    amp = min(amp, R(W["stride_max_deg"]))
    leg_axes[leg] = {
        "amp": amp,
        "coxa_yaw": local(bones["Coxa"], UP), "back_sign": back_sign,
        "femur_lift": local(bones["Femur"], lift_axis * lift_sign),
        "tibia_lift": local(bones["Tibia"], lift_axis * lift_sign),
    }
    for p in ("Coxa", "Femur", "Tibia"):
        arm.pose.bones[f"Leg_{leg}_{p}"].rotation_mode = "QUATERNION"
        arm.pose.bones[f"Leg_{leg}_{p}"].rotation_quaternion = Quaternion()

action = bpy.data.actions.new("Walk")
arm.animation_data_create()
arm.animation_data.action = action
size = max(arm.dimensions)  # grobe Größe für Wipp-Amplitude

# Vorlauf: Wie weit wandert die Fußspitze pro Standphase? → Laufgeschwindigkeit für Unity
stride_samples = {}
antenna_samples = {}
loop_samples = {}

for f in range(N + 1):
    t = (f % N) / N
    # ---- Beine ----
    for leg in walking:
        side = 1 if leg[0] == "L" else -1
        k = int(leg[1])
        # Wellenversatz innerhalb der Gruppe (vorne etwas früher) für natürlicheren Look
        offset = (0.0 if leg in group_a else 0.5) + W["wave_offset"] * (k - 2)
        swing, s = leg_phase(t, offset, W["duty"])
        A = leg_axes[leg]["amp"]
        # "back" = Bein nach hinten geschwenkt. Stand: vorne → hinten (Körper schiebt sich vor),
        # Schwung: angehoben schnell wieder nach vorne.
        back = (-A + 2 * A * s) if not swing else (A - 2 * A * ease(s))
        lift = R(W["lift_deg"]) * math.sin(math.pi * s) if swing else 0.0
        fold = R(W["tibia_fold_deg"]) * math.sin(math.pi * s) if swing else 0.0
        ax = leg_axes[leg]
        arm.pose.bones[f"Leg_{leg}_Coxa"].rotation_quaternion = Quaternion(ax["coxa_yaw"], ax["back_sign"] * back)
        arm.pose.bones[f"Leg_{leg}_Femur"].rotation_quaternion = Quaternion(ax["femur_lift"], lift)
        arm.pose.bones[f"Leg_{leg}_Tibia"].rotation_quaternion = Quaternion(ax["tibia_lift"], fold)
    for leg in feelers:
        side = 1 if leg[0] == "L" else -1
        ph = 2 * math.pi * (t * W["feeler_speed"] + (0.25 if side > 0 else 0.75))
        ax = leg_axes[leg]
        arm.pose.bones[f"Leg_{leg}_Coxa"].rotation_quaternion = Quaternion(ax["coxa_yaw"], R(W["feeler_deg"]) * math.sin(ph))
        arm.pose.bones[f"Leg_{leg}_Femur"].rotation_quaternion = Quaternion(
            ax["femur_lift"], R(W["feeler_deg"]) * 0.6 * (0.5 + 0.5 * math.cos(ph + 1)))
    # ---- Rumpf ----
    two = 2 * math.pi * 2 * t  # doppelte Frequenz: ein Wipper pro Schritt
    one = 2 * math.pi * t
    th = arm.pose.bones["Thorax"]
    th.location = Vector((0, 0, W["body_bob"] * size * math.sin(two)))
    th.rotation_euler = Euler((R(W["body_roll_deg"]) * math.sin(one), 0, R(W["body_sway_deg"]) * math.sin(one)))
    arm.pose.bones["Abdomen_1"].rotation_euler = Euler((R(W["abdomen_bob_deg"]) * math.sin(two - W["abdomen_lag"]), 0,
                                                       -R(W["abdomen_sway_deg"]) * math.sin(one - W["abdomen_lag"])))
    arm.pose.bones["Abdomen_2"].rotation_euler = Euler((0, 0, -R(W["abdomen_sway_deg"]) * 0.6 * math.sin(one - 2 * W["abdomen_lag"])))
    arm.pose.bones["Head"].rotation_euler = Euler((R(W["head_nod_deg"]) * math.sin(two + 0.5), 0,
                                                  -R(W["head_sway_deg"]) * math.sin(one + 0.3)))
    # Fühler stabilisieren: Kopf-/Körperdrehung (Armature-Raum) zum Großteil ausgleichen
    bpy.context.view_layer.update()
    q_head = arm.pose.bones["Head"].matrix.to_quaternion() @ arm.data.bones["Head"].matrix_local.to_quaternion().inverted()
    cancel = Quaternion().slerp(q_head.inverted(), W["antenna_stabilize"])
    for side, sign in (("L", 1), ("R", -1)):
        ph = 2 * math.pi * (t * W["antenna_speed"]) + (0 if sign > 0 else 1.7)
        own = Euler((R(W["antenna_deg"]) * math.sin(ph), 0,
                     sign * R(W["antenna_deg"]) * 0.7 * math.cos(ph + 0.8))).to_quaternion()  # ganzzahlige Frequenz = nahtlose Schleife
        bl = arm.data.bones[f"Antenna_{side}_1"].matrix_local.to_quaternion()
        pb = arm.pose.bones[f"Antenna_{side}_1"]
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (bl.inverted() @ cancel @ bl) @ own
        arm.pose.bones[f"Antenna_{side}_2"].rotation_euler = Euler((R(W["antenna_deg"]) * W["antenna_tip_factor"] * math.sin(ph - 0.9), 0, 0))
    # ---- Keyframes ----
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=f)
        if pb.name == "Thorax":
            pb.keyframe_insert("location", frame=f)

    # Fußspitzen-Position (Welt) mitschreiben + Phase merken
    bpy.context.view_layer.update()
    # Alle Knochenenden mitschreiben (Schleifenprüfung: Frame 0 == Frame N für JEDEN Knochen)
    if f in (0, N):
        loop_samples[f] = {pb.name: (arm.matrix_world @ pb.tail).copy() for pb in arm.pose.bones}
    # Fühlerspitzen relativ zum Kopf (Eigenbewegung) und in Welt (inkl. Kopf-/Körperbewegung)
    head_m = arm.matrix_world @ arm.pose.bones["Head"].matrix
    for side in ("L", "R"):
        tip_w = arm.matrix_world @ arm.pose.bones[f"Antenna_{side}_2"].tail
        antenna_samples.setdefault(side, []).append((tip_w.copy(), head_m.inverted() @ tip_w))
    for leg in walking:
        tip = arm.matrix_world @ arm.pose.bones[f"Leg_{leg}_Tarsus"].tail
        offset = (0.0 if leg in group_a else 0.5) + W["wave_offset"] * (int(leg[1]) - 2)
        swing, _ = leg_phase(t, offset, W["duty"])
        stride_samples.setdefault(leg, []).append((f, tip.copy(), swing))

# Lineare Interpolation → gleichmäßige Fußbewegung, keine Ease-Sprünge an Keys
for fc in action.fcurves if hasattr(action, "fcurves") else []:
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

# ---- Selbstprüfung ----
# Ruhe-Höhe der Fußspitzen (ohne Pose) als Bodenreferenz
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_euler, pb.location = Euler((0, 0, 0)), Vector((0, 0, 0))
    pb.rotation_quaternion = Quaternion()
bpy.context.view_layer.update()
rest_z = {leg: (arm.matrix_world @ arm.pose.bones[f"Leg_{leg}_Tarsus"].tail).z for leg in walking}
arm.animation_data.action = action
checks = {}
speeds = []
size_ref = size
for leg, samples in stride_samples.items():
    stance = [p for _, p, sw in samples if not sw]
    swing = [p for _, p, sw in samples if sw]
    xs = [p.x for p in stance]
    stride = max(xs) - min(xs) if xs else 0
    speeds.append(stride / (W["duty"] * N / W["fps"]))
    checks[leg] = {
        "stride_m": round(stride, 3),
        "stance_float_max_m": round(max(p.z for p in stance) - rest_z[leg], 4) if stance else None,  # >0 = schwebt
        "stance_sink_max_m": round(min(p.z for p in stance) - rest_z[leg], 4) if stance else None,   # <0 = im Boden
        "swing_lift_m": round(max(p.z for p in swing) - rest_z[leg], 3) if swing else None,
    }
tol = W["contact_tolerance"] * size_ref
contact_ok = all(abs(c["stance_float_max_m"]) <= tol and abs(c["stance_sink_max_m"]) <= tol for c in checks.values())
report = {
    "action": "Walk", "frames": N, "fps": W["fps"], "cycle_seconds": round(N / W["fps"], 3),
    "walking_legs": walking, "feelers": feelers,
    "group_A": sorted(group_a), "group_B": sorted(set(walking) - group_a),
    "legs": checks,
    "suggested_move_speed_mps": round(sum(speeds) / len(speeds), 3) if speeds else 0,
    "loop_ok": max((loop_samples[0][n] - loop_samples[N][n]).length for n in loop_samples[0]) < 1e-4,
    "loop_max_jump_m": round(max((loop_samples[0][n] - loop_samples[N][n]).length for n in loop_samples[0]), 5),
    "foot_contact_ok": contact_ok,
    # Fühler: max. Auslenkung der Spitze (Durchmesser der Bahn) und max. Geschwindigkeit
    "antenna": {side: {
        "range_world_m": round(max((a - b).length for a, _ in s for b, _ in s), 3),
        "range_vs_head_m": round(max((a - b).length for _, a in s for _, b in s), 3),
        "max_speed_mps": round(max((s[i + 1][0] - s[i][0]).length for i in range(len(s) - 1)) * W["fps"], 2),
    } for side, s in antenna_samples.items()},
    "contact_tolerance_m": round(tol, 4),
}
(OUT / "walk_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print("WALK_REPORT", json.dumps({k: v for k, v in report.items() if k != "legs"}, ensure_ascii=False))
for leg, c in checks.items():
    print("  FOOT", leg, c)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "crawler_walk.blend"))
print("WALK_OK")
