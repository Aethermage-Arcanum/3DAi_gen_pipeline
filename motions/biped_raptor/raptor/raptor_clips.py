"""Bewegungsmuster biped_raptor/raptor: Schritt, Laufvogel-Rennen, Drehen, Idle, Drohen, Stampf-Tritt,
Treffer, Tod. Nutzt den Beine-Baukasten ../biped_kit.py (Blender-IK für die Beine).

& "D:\\Blender\\blender.exe" -b <biped_raptor_rigged.blend> -P motions/biped_raptor/raptor/raptor_clips.py -- <ausgabe> [<creature.toml>]
"""
import math
import pathlib
import sys

import bpy
from mathutils import Quaternion, Vector

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import biped_kit as K  # noqa: E402

K.init(HERE)
from biped_kit import (FWD, LEFT, UP, R, body, ease, gait, head_stabilize, ik_off, jaw, neck_head,  # noqa: E402
                       phase, rot, set_foot, spine, spring_curve, tail, tail_wave)

ST, SIZE, HGT, LEGS = K.ST, K.SIZE, K.HGT, K.LEGS
ARMS = sorted({b.name[4] for b in K.DB if b.name.startswith("Arm_")})


def arms(up_deg=0.0, swing_deg=0.0, t=0.0, spread_deg=0.0):
    """Greifarme: up = nach vorn/oben anheben, swing = Pendeln im Gang, spread = Krallen auseinander."""
    for s in ARMS:
        sg = 1 if s == "L" else -1
        rot(f"Arm_{s}_1", LEFT, -R(up_deg) - R(swing_deg) * math.sin(2 * math.pi * t + (0 if s == "L" else math.pi)))
        rot(f"Arm_{s}_1", FWD, sg * R(spread_deg))
        rot(f"Arm_{s}_2", LEFT, -R(up_deg) * 0.6)


def arms_pose(up=0.0, spread=0.0, d1=0.0, d2=0.0, d3=0.0, alt=0.0):
    """Greifarme mit Nachschwingen: d1..d3 = zusätzliche Beugung je Glied (Grad, gegeneinander verzögert übergeben),
    alt = gegengleiches Pendeln links/rechts."""
    for s in ARMS:
        sg = 1 if s == "L" else -1
        rot(f"Arm_{s}_1", LEFT, -R(up + d1 + alt * sg))
        rot(f"Arm_{s}_1", FWD, sg * R(spread))
        rot(f"Arm_{s}_2", LEFT, -R(up * 0.6 + d2))
        rot(f"Arm_{s}_3", LEFT, -R(d3))


def locomotion(P, turn=0.0):
    """Ganzkörper-Gang (Strauß/Emu, Bishop 2021 Schwanz-Pendeln, Huhn/Wachtel Kopfstabilisierung):
    Becken giert (Hüfte des Schwungbeins geht mit vor) + verlagert das Gewicht seitlich über das Standbein,
    Brust dreht gegen (verzögert), Rumpf federt (Gehen: tiefster Punkt in der Doppelstütze; Rennen: in der
    Standmitte), Kopf hält Höhe + Blickrichtung im Raum, Schwanz pendelt als verzögerte Welle gegen das Becken,
    Arme baumeln verzögert. Alles periodisch → nahtlose Schleife."""
    N, off, d = P["cycle_frames"], P["order"], P["duty"]
    sgn = (turn > 0) - (turn < 0)
    bph = P.get("bob_phase", 0.05)
    tw = 2 * math.pi

    def bl(t, lag=0.0):                       # Federweg des Rumpfs (−1 = tiefster Punkt), verzögert um lag Zyklen
        return -math.cos(2 * tw * (t - bph - lag))

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=turn)
        c = tw * (t - d / 2)                  # 0 = Mitte der Standphase links
        body(dz=P.get("bob", 0) * HGT * bl(t), dy=P.get("sway", 0) * SIZE * math.cos(c - tw * 0.04),
             pitch=-R(P.get("lean_deg", 0)) + R(P.get("pitch_deg", 0)) * bl(t, 0.03))
        # Becken: Gieren (Schwungbein-Hüfte vor) + Rollen zum Standbein; Brust dreht verzögert dagegen
        yaw, roll = R(P.get("hip_yaw_deg", 0)), R(P.get("roll_deg", 0))
        rot("Hips", UP, yaw * math.cos(c + tw * 0.03))
        rot("Hips", FWD, -roll * math.cos(c))
        for n, lag in (("Spine_1", 0.04), ("Chest", 0.08)):
            rot(n, UP, -yaw * P.get("counter", 0.7) / 2 * math.cos(c - tw * lag))
            rot(n, FWD, roll * 0.4 * math.cos(c - tw * lag))
        rot("Chest", LEFT, -R(P.get("spine_bob_deg", 0)) * bl(t, 0.06))     # Brust nickt nach dem Aufsetzen nach
        if turn:                                                            # Körper biegt sich in die Kurve
            spine(side=R(P.get("bend_deg", 0)) * sgn)
            for n in ("Neck_1", "Neck_2"):
                rot(n, UP, R(P.get("head_lead_deg", 0)) * sgn / 2)
        # Hals hält die Kopfhöhe (Rumpf tief → Hals hoch), Kopf hält die Blickrichtung im Raum
        rot("Neck_1", LEFT, R(P.get("neck_level_deg", 0)) * bl(t, 0.02))
        head_stabilize(P.get("head_stabilize", 0),
                       target=Quaternion(UP, R(P.get("head_lead_deg", 0)) * sgn * 1.4) if turn else None)
        tail_wave(t, P.get("tail_yaw_deg", 0), P.get("tail_pitch_deg", 0), 1, 2, P.get("tail_lag", 0.07),
                  P.get("tail_lift_deg", 0),
                  yaw_phase=d / 2 - 0.25 + P.get("tail_yaw_phase", 0.5),
                  pitch_phase=2 * bph + 0.25 + P.get("tail_pitch_lag", 0.06))
        if turn:
            for i in range(1, 5):
                rot(f"Tail_{i}", UP, -R(P.get("tail_trail_deg", 0)) * sgn / 4 * (0.6 + 0.3 * i))
        ab = P.get("arm_bob_deg", 0)
        arms_pose(up=10, d1=ab * bl(t, 0.06), d2=ab * bl(t, 0.11), d3=ab * 1.3 * bl(t, 0.16),
                  alt=P.get("arm_swing_deg", 0) * math.sin(tw * (t - 0.08)))
        K.apply_toes()
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": P["duty"], "turn": turn,
            "max_stretch": P.get("max_stretch"),
            "swing": lambda leg, f: phase((f % N) / N, off[leg], P["duty"])[0]}


def clip_idle(P):
    N = P["frames"]
    looks = [(0.0, 0.0), (0.15, 1.0), (0.4, -0.6), (0.65, 0.3), (0.85, 0.0)]   # ruckartig + halten

    def look(t):
        for (t0, a0), (t1, a1) in zip(looks, looks[1:] + [(1.0, 0.0)]):
            if t0 <= t < t1:
                return a0 + (a1 - a0) * ease(min(1.0, (t - t0) / 0.05))
        return 0.0

    def pose(f):
        t = f / N
        sw, br = math.sin(2 * math.pi * t), math.sin(2 * math.pi * 3 * t)
        # Gewicht wandert langsam von Bein zu Bein, Atmen läuft verzögert von der Brust in den Hals
        body(dz=0.006 * HGT * br, dy=P.get("sway", 0) * SIZE * sw, roll=-R(P.get("roll_deg", 0)) * sw)
        rot("Hips", UP, R(P.get("hip_yaw_deg", 0)) * math.sin(2 * math.pi * (t - 0.03)))
        rot("Chest", LEFT, R(P["breathe_deg"]) * br)
        rot("Neck_1", LEFT, -R(P["breathe_deg"]) * 0.7 * math.sin(2 * math.pi * (3 * t - 0.1)))
        head_stabilize(P.get("head_stabilize", 0))
        a = look(t)
        neck_head(yaw=R(P["look_deg"]) * a)
        rot("Head", FWD, R(P.get("tilt_deg", 0)) * a)                   # Vogel: Kopf beim Hinsehen leicht schief
        tail_wave(t, P["tail_deg"], P.get("tail_pitch_deg", 0), 2, 3, 0.07)
        arms_pose(up=10 + 3 * br, d2=2 * math.sin(2 * math.pi * (3 * t - 0.1)),
                  d3=3 * math.sin(2 * math.pi * (3 * t - 0.2)))
    return {"N": N, "loop": True, "kind": "stand", "pose": pose}


def clip_ready(P):
    """Drohen mit dem ganzen Körper: tief geduckt, Gewicht pendelt von Bein zu Bein, Brust pumpt (Atem),
    Hals als gespannte S-Kurve, Kopf bleibt auf das Ziel gerichtet (gleicht den Körper aus), Schwanz peitscht
    langsam als Welle, Maul faucht stoßweise, Krallen erhoben."""
    N = P["frames"]

    def pose(f):
        t = f / N
        sw, br = math.sin(2 * math.pi * t), math.sin(2 * math.pi * 2 * t)
        tr = R(P["tremble_deg"]) * math.sin(2 * math.pi * 6 * t)
        body(dz=-P["crouch"] * HGT + 0.015 * HGT * br, dy=P.get("sway", 0) * SIZE * sw,
             pitch=-R(P.get("lean_deg", 6)) + tr * 0.3, roll=-R(P.get("roll_deg", 0)) * sw)
        yaw = R(P.get("hip_yaw_deg", 0))
        rot("Hips", UP, yaw * math.sin(2 * math.pi * (t - 0.05)))
        for n, lag in (("Spine_1", 0.08), ("Chest", 0.14)):
            rot(n, UP, -yaw * 0.6 * math.sin(2 * math.pi * (t - lag)))
        rot("Chest", LEFT, -R(P["breathe_deg"]) * br)
        rot("Neck_1", LEFT, R(P.get("neck_coil_deg", 0)))
        rot("Neck_2", LEFT, -R(P.get("neck_coil_deg", 0)) * 0.7
            - R(P["breathe_deg"]) * 0.5 * math.sin(2 * math.pi * (2 * t - 0.1)))
        head_stabilize(P.get("head_lock", 0), target=Quaternion(LEFT, R(P["head_down_deg"])))
        jaw(P["jaw_deg"] + P.get("hiss_deg", 0) * max(0.0, math.sin(2 * math.pi * 3 * t)))
        tail_wave(t, P.get("tail_lash_deg", 0), P.get("tail_pitch_deg", 0), 1, 2, 0.09, P["tail_lift_deg"])
        arms_pose(up=P["arms_up_deg"] + 4 * br, spread=10, d2=6 * math.sin(2 * math.pi * (2 * t - 0.15)),
                  d3=-8 + 6 * math.sin(2 * math.pi * (2 * t - 0.25)))
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "max_stretch": P.get("max_stretch")}


def clip_attack1(P):
    """Stampf-Tritt mit dem ganzen Körper (Sekretärvogel): Ausholen = Gewicht aufs Standbein, Rumpf richtet sich
    auf und lehnt zurück, Hals zieht zurück, Kopf bleibt aufs Ziel gerichtet, Arme spreizen zur Balance, Trittfuß
    hoch, Zehen eingerollt → Tritt in 2 Frames: Fuß stampft vor-unten, Rumpf stößt vor und sackt ein, Hals schnellt
    vor, Maul auf, Schwanz peitscht hoch → Nachfedern (gedämpfte Federn, Schwanzglieder zeitversetzt) → zurück."""
    N, w, s, h = P["frames"], P["windup_end"], P["strike_end"], P["hold_end"]
    kl = P["kick_leg"]
    ss = -1 if kl[1] == "L" else 1                 # Seite des Standbeins (+1 = links)

    def wind(f):
        if f <= w:
            return ease(f / w)
        return max(0.0, 1 - (f - w) / (s - w)) if f <= s else 0.0

    def strike(f):
        if f <= w:
            return 0.0
        if f <= s:
            return ((f - w) / (s - w)) ** 2
        return 1.0 if f <= h else 1 - ease((f - h) / (N - h))

    def sp(fn, fr=3.5, z=0.45):
        return spring_curve(fn, N, fr, z)

    C = {
        "dz": sp(lambda f: HGT * (P["rise"] * wind(f) - P["drop"] * strike(f))),
        "dx": sp(lambda f: SIZE * (-0.015 * wind(f) + P["lunge"] * strike(f))),
        "dy": sp(lambda f: ss * SIZE * P["shift"] * (wind(f) + 0.5 * strike(f)), 2.5),
        "pitch": sp(lambda f: R(P["lean_back_deg"]) * wind(f) - R(P["lunge_pitch_deg"]) * strike(f)),
        "roll": sp(lambda f: -ss * R(P["roll_deg"]) * (wind(f) + 0.5 * strike(f)), 2.5),
        "flex": sp(lambda f: -R(8) * wind(f) + R(5) * strike(f), 3.0),
        "neck": sp(lambda f: R(P["neck_back_deg"]) * wind(f) - R(P["neck_thrust_deg"]) * strike(f), 3.0, 0.4),
        "aim": sp(lambda f: R(P["head_aim_deg"]) * max(wind(f), strike(f)), 3.0, 0.5),
        "arms": sp(lambda f: P["arms_up_deg"] * wind(f) + 10 * strike(f), 2.8, 0.4),
        "arms2": sp(lambda f: -20 * wind(f) + 25 * strike(f), 2.4, 0.35),
        "jaw": sp(lambda f: P["jaw_deg"] * max(0.4 * wind(f), strike(f)), 5.0, 0.5),
    }
    # Schwanz = träge Kette: jedes Glied folgt der Rumpf-Neigung über eine immer langsamere Feder → bei schnellen
    # Wechseln bleibt die Spitze zurück und peitscht danach über (Follow-Through), in Ruhe folgt er dem Rumpf.
    pitch_t = lambda f: R(P["lean_back_deg"]) * wind(f) - R(P["lunge_pitch_deg"]) * strike(f)  # noqa: E731
    tails = [sp(pitch_t, 3.0 - 0.5 * i, 0.3) for i in range(1, 5)]
    tail_up = sp(lambda f: R(P["tail_up_deg"]) * (0.4 * wind(f) + strike(f)), 3.0, 0.5)

    def foot(f):
        """→ (vor 0..1, hoch 0..1, Zehen einrollen rad, Zehen folgen 0..1)"""
        if f <= w:                                       # Fuß hoch vor die Brust, Zehen eingerollt
            a = ease(f / w)
            return P["kick_cock"] * a, a, R(50) * a, 0.7 * a
        if f <= s:                                       # beschleunigt vor-unten, Zehen strecken sich zum Aufprall
            x = (f - w) / (s - w)
            x2 = x * x
            return P["kick_cock"] + (1 - P["kick_cock"]) * x2, 1 - x2, R(50) * (1 - x), 0.7 * (1 - x)
        if f <= h:
            return 1.0, 0.0, 0.0, 0.0
        x = ease((f - h) / (N - h))
        return 1 - x, 0.22 * K.bump(x), R(25) * K.bump(x), 0.5 * K.bump(x)

    def pose(f):
        fwd, up, curl, follow = foot(f)
        set_foot(kl, Vector((P["kick_reach"] * SIZE * fwd, 0, P["kick_height"] * HGT * up)), curl)
        K.foot_toes(kl, follow, curl)
        body(dz=C["dz"][f], dx=C["dx"][f], dy=C["dy"][f], pitch=C["pitch"][f], roll=C["roll"][f])
        spine(flex=C["flex"][f])
        for n in ("Neck_1", "Neck_2"):
            rot(n, LEFT, -C["neck"][f] / 2)
        head_stabilize(0.7, target=Quaternion(LEFT, C["aim"][f]))
        jaw(C["jaw"][f])
        prev = C["pitch"][f]
        for i, tc in enumerate(tails, 1):
            rot(f"Tail_{i}", LEFT, (prev - tc[f]) * P["tail_inertia"] + tail_up[f] / 4)
            prev = tc[f]
        arms_pose(up=C["arms"][f], spread=P["arms_spread_deg"] * wind(f) ** 0.7, d2=C["arms2"][f],
                  d3=C["arms2"][f] * 0.6)
        K.apply_toes()
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "planted": [l for l in LEGS if l != kl],
            "max_stretch": P.get("max_stretch"),
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_hit(P):
    """Treffer: Ruck zurück, danach laufen Brust, Hals, Kopf und Schwanz zeitversetzt nach (Follow-Through)."""
    N = P["frames"]

    def k_at(f, lag=0.0):
        if f <= lag:
            return 0.0
        x = (f - lag) / (N - lag)                   # gleiches Ende bei Frame N → Clip kehrt exakt in Ruhe zurück
        return 0.0 if x >= 1 else math.sin(math.pi * min(1.0, x * 2.5)) * (1 - x)

    def pose(f):
        k, k1, k2 = k_at(f), k_at(f, 1), k_at(f, 2)
        body(dx=-P["jolt"] * SIZE * k, roll=R(P["roll_deg"]) * k, pitch=R(6) * k)
        spine(flex=-R(8) * k1)
        neck_head(yaw=R(P["head_deg"]) * k1, pitch=R(10) * k1)
        rot("Head", UP, R(P["head_deg"]) * 0.4 * k2)
        jaw(14 * k1)
        for i in range(1, 5):
            rot(f"Tail_{i}", LEFT, R(16) * k_at(f, 0.5 * i) / 4)
            rot(f"Tail_{i}", UP, -R(10) * k_at(f, 0.5 * i) / 4)
        arms_pose(up=18 * k1, d2=12 * k2, d3=10 * k2)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    N, c0, c1, side = P["frames"], P["collapse_start"], P["collapse_end"], P["side"]
    feet = [K.REST[l]["ball"] for l in LEGS]
    piv = sum(feet, Vector()) / len(feet) + Vector((0, -side * 0.06 * SIZE, 0))
    h0 = K.DB["Root"].head_local

    def raw(f):
        k = ease((f - c0) / (c1 - c0)) if f >= c0 else 0.0
        jolt = math.sin(math.pi * min(1.0, f / max(1, c0))) if f < c0 else 0.0
        q = Quaternion(FWD, side * R(85) * k)
        rot("Root", FWD, side * R(85) * k)
        K.move("Root", (piv - h0) - q @ (piv - h0))
        for leg in LEGS:
            ik_off(leg, ease((k - 0.2) / 0.4))   # Beine geben erst nach, wenn der Körper halb gekippt ist (sonst schwebt er)
            rot(f"Leg_{leg}_1", LEFT, -R(P["legs_limp_deg"]) * k)
            rot(f"Leg_{leg}_2", LEFT, R(P["legs_limp_deg"]) * k)
        neck_head(pitch=-R(15) * k - R(8) * jolt)
        jaw(15 * k)
        tail(0, 0, 1, -15 * k)
        arms(up_deg=-10 * k)
        return k

    K.reset()
    raw(N)
    bpy.context.view_layer.update()
    drop = K.mesh_min_z() - K.GROUND

    def pose(f):
        k = raw(f)
        K.move("Root", Vector((0, 0, -drop * k)))
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "max_stretch": P.get("max_stretch"),
            "events": [{"frame": N, "event": "dead"}]}


turn = R(ST["turn"]["turn_deg"])
K.bake({
    "Walk": locomotion(ST["walk"]),
    "Run": locomotion(ST["run"]),
    "TurnLeft": locomotion(ST["turn"], turn=turn),
    "TurnRight": locomotion(ST["turn"], turn=-turn),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
})
