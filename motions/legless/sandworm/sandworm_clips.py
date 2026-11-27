"""Bewegungsmuster legless/sandworm: Wurm-Kriechen (Peristaltik + Wiegen), Sand-Pflügen, Drehen, Idle, Ready,
Vorstoß-Biss, Body Slam, Treffer, Eingraben (Burrow), Auftauchen (Emerge), Death-Platzhalter.
Gemeinsame Bausteine: ../legless_kit.py (opt-in: Ring-Skalierung, Stacheln ohne Bodenkontakt, Abtauchen).

& "D:\\Blender\\blender.exe" -b <legless_rigged.blend> -P motions/legless/sandworm/sandworm_clips.py -- <ausgabe> [<creature.toml>]

Eigener Clip-Code (Ideen aus cobra kopiert, nicht importiert). Körperform über K.shape, Grundlinie = gerade Liege-Haltung
des Modells (siehe REST_P). Peristaltik über die
Ring-Knochen ([legless] ring_bones): dick + kurz (verankert) bzw. dünn + lang (streckt vor); dabei rückt die Wirbelkette
entsprechend zusammen (Location-Versatz der Folge-Wirbel), damit zwischen den Ringen nichts aufreißt.
Burrow/Emerge folgen einem Pfad durch einen festen Eintritts-/Austrittspunkt („follow the leader“ wie die Sandboa).
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import legless_kit as K  # noqa: E402

K.init(HERE)
from mathutils import Vector  # noqa: E402

from legless_kit import FWD, R, ease, interp, mix  # noqa: E402

ST = K.ST
TAU = 2 * math.pi
NS = K.NSEG
S = K.seg_s()                                   # Bogenlänge je Wirbel (0 Schwanz … 1 Kopfansatz)
INFO = K.abs_info()
LENS = INFO["len"][:NS]
HEAD_S = INFO["len"][NS] / INFO["spine_len"]    # Kopf-Länge in Bogenlängen-Einheiten (Nase bei 1 + HEAD_S)
CUM = [0.0]
for _l in LENS:
    CUM.append(CUM[-1] + _l / INFO["spine_len"])
RINGS = [f"Ring_{i + 1:02d}" for i in range(NS)] if "Ring_01" in K.PB else []
BODY = ST["body"]
TENV = [interp(BODY["thick_envelope"], s) for s in S]
REST_Z = [K.DB[n].head_local.z for n in K.SPINE] + [K.DB["Head"].head_local.z, K.DB["Head"].tail_local.z]
REST_X = [K.DB[n].head_local.x for n in K.SPINE] + [K.DB["Head"].head_local.x, K.DB["Head"].tail_local.x]
CUMH = CUM + [1.0 + HEAD_S]


def mean_yaw(yaw):
    return sum(y * l for y, l in zip(yaw, LENS)) / sum(LENS)


def ramp(s, a, b):
    return interp([(a, 0.0), (b, 1.0)], s)


def thick_wave(t, amp, waves):
    """Verdickungswelle, läuft Kopf → Schwanz (retrograd wie beim Regenwurm). + = dick + kurz."""
    return [amp * e * math.sin(TAU * (t + waves * s)) for s, e in zip(S, TENV)]


# Grundlinie = Ruhe-Richtung der Wirbel. Der Wurm liegt im Modell gerade, aber die Mittellinie steigt zum dicken
# Vorderkörper an (Bauch flach am Boden, Körper wird dicker). Pitch/Yaw-Profile sind Abweichungen von dieser geraden
# Liege-Haltung; flach = wie modelliert (nicht waagerechte Mittellinie, sonst sticht der Bauch in den Boden).
REST_P = [math.degrees(INFO["yp"][n][1]) for n in K.SPINE]
REST_Y = [math.degrees(INFO["yp"][n][0]) for n in K.SPINE]


def build(yaw, pitch, hy, hp, a=None, jaw=0.0, roll=0.0):
    """Form (Abweichung von der geraden Liege-Haltung) + Ring-Dicke + Kiefer-Pumpen + Kopf-Rollen (Root unberührt)."""
    K.shape([y + r for y, r in zip(yaw, REST_Y)], [p + r for p, r in zip(pitch, REST_P)], hy, hp,
            neck=BODY.get("neck", 2))
    if a and RINGS:
        kl = BODY["len_coupling"]
        for i, n in enumerate(K.SPINE):
            sy = 1.0 - kl * a[i]
            K.PB[RINGS[i]].scale = Vector((1.0 + a[i], sy, 1.0 + a[i]))
            nxt = K.SPINE[i + 1] if i + 1 < NS else "Head"       # Folge-Wirbel rückt nach (kein Spalt in der Furche)
            K.PB[nxt].location = K.PB[nxt].location + Vector((0.0, -LENS[i] * (1.0 - sy), 0.0))
    jaw_total = BODY.get("jaw_rest_deg", 0.0) + jaw
    if jaw_total:
        K.jaw(jaw_total)
    if roll:
        K.rot("Head", FWD, R(roll))


def chain_at(e):
    """Weltposition der Mittellinie bei Bogenlänge e (0 Schwanzspitze, 1 Kopfansatz, 1 + HEAD_S Nase);
    außerhalb wird entlang des ersten bzw. letzten Knochens verlängert."""
    pts = K.chain_points() + [K.head_tip()]
    if e <= 0:
        d = (pts[1] - pts[0]) / max(1e-9, CUMH[1])
        return pts[0] + d * e
    for j in range(len(CUMH) - 1):
        if e <= CUMH[j + 1] or j == len(CUMH) - 2:
            u = (e - CUMH[j]) / max(1e-9, CUMH[j + 1] - CUMH[j])
            return pts[j] + (pts[j + 1] - pts[j]) * u
    return pts[-1]


def rest_z_at(e):
    e = max(0.0, min(1.0 + HEAD_S, e))
    for j in range(len(CUMH) - 1):
        if e <= CUMH[j + 1]:
            u = (e - CUMH[j]) / max(1e-9, CUMH[j + 1] - CUMH[j])
            return REST_Z[j] + (REST_Z[j + 1] - REST_Z[j]) * u
    return REST_Z[-1]


def pin(e, target):
    """Root so verschieben, dass die Mittellinie bei Bogenlänge e auf target (Welt) liegt."""
    off = target - chain_at(e)
    K.move("Root", Vector((off.x, off.y, off.z)))


def ground_behind(xlim):
    """Bodenkontakt nur für den Körper hinter dem Loch (x < xlim); liegt dort nichts, bleibt die Höhe."""
    P = K.body_world()
    if K.BODY_IDX is not None:
        P = P[K.BODY_IDX]
    P = P[P[:, 0] < xlim]
    if len(P) >= 8:
        K.move("Root", Vector((0, 0, K.GROUND - float(P[:, 2].min()))))


# ---------------------------------------------------------------- Fortbewegung (Wurm-Kriechen / Sand-Pflügen)
def crawl(P, turn=0.0):
    """turn: +1 links, -1 rechts, 0 geradeaus. Kurve = flacher Bogen über den ganzen Körper, Panzer + Kopf führen."""
    N = P["cycle_frames"]
    ps = P.get("peristalsis_scale", 1.0) if turn else 1.0
    meas = {"yaw": []}

    def pose(f):
        t = (f % N) / N
        a = thick_wave(t, P["thick"] * ps, P["thick_waves"])
        pitch = [interp(P["pitch"], s) - P["hump_deg"] * ps * e * math.cos(TAU * (t + P["thick_waves"] * s))
                 for s, e in zip(S, TENV)]
        env = [interp(P["sway_envelope"], s) for s in S]
        yaw = [P["sway_deg"] * e * math.sin(TAU * (t + P["sway_waves"] * s)) for s, e in zip(S, env)]
        hy = P["sway_deg"] * env[-1] * math.sin(TAU * (t + P["sway_waves"]) + R(P["head_lead_deg"]))
        if turn:
            for i, s in enumerate(S):
                yaw[i] += turn * (P["arc_deg"] * (s - 0.5) + P["lead_deg"] * ramp(s, 0.7, 1.0))
            hy += turn * (P["arc_deg"] * 0.5 + P["lead_deg"] + P["head_lead_deg"])
        m = mean_yaw(yaw)                       # mittlere Körperrichtung = Blickrichtung des Objekts
        yaw = [y - m for y in yaw]
        hp = P["head_pitch"] + P["head_bob_deg"] * math.sin(TAU * 2 * t)
        jaw = P["jaw_pump_deg"] * (0.5 - 0.5 * math.cos(TAU * 2 * t))
        build(yaw, pitch, hy - m, hp, a, jaw)
        surge = P["surge"] * K.SIZE * (math.sin(TAU * t) + 0.25 * math.sin(TAU * 2 * t))   # Ruck-Gleiten
        K.place(K.REST_MID + Vector((surge, 0, 0)))
        K.ground("contact")
        d = K.heading()
        meas["yaw"].append(math.degrees(math.atan2(d.y, d.x)))

    def measure():
        if not turn:
            return {"move_speed_mps": round(P["move_body_per_cycle"] * K.SIZE / (N / K.FPS), 3)}
        hm = sum(meas["yaw"]) / len(meas["yaw"])
        return {"turn_speed_deg_s": P["turn_speed_deg_s"], "head_yaw_mean_deg": round(hm, 1),
                "turn_direction": "links" if hm > 0 else "rechts", "turn_dir_ok": hm * turn > 5}
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "measure": measure}


# ---------------------------------------------------------------- Stand-Haltungen
def pitch_list(pts):
    return [interp(pts, s) for s in S]


def ready_params(t):
    Q = ST["ready"]
    sway = math.sin(TAU * t)
    br = math.sin(TAU * 2 * t)
    pitch = [v + Q["bob_deg"] * br * ramp(s, 0.55, 0.75) for v, s in zip(pitch_list(Q["pitch"]), S)]
    yaw = [Q["sway_deg"] * sway * ramp(s, 0.5, 0.8) for s in S]
    return {"yaw": yaw, "pitch": pitch, "hy": 0.0, "hp": Q["head_pitch"],
            "a": thick_wave(t, Q["thick"], Q["thick_waves"]),
            "jaw": Q["jaw_pump_deg"] * (0.5 - 0.5 * math.cos(TAU * Q["pumps"] * t)), "roll": 0.0, "slide": 0.0}


def idle_params(t):
    Q = ST["idle"]
    br = math.sin(TAU * Q["breaths"] * t)
    sniff = sum(math.exp(-((t - c) / 0.06) ** 2) for c in Q["sniff_at"])
    look = Q["look_deg"] * math.sin(TAU * t)
    a = [x + Q["breath"] * br * e for x, e in zip(thick_wave(t, Q["thick"], Q["thick_waves"]), TENV)]
    pitch = [v + Q["sniff_raise_deg"] * sniff * ramp(s, 0.6, 1.0) for v, s in zip(pitch_list(Q["pitch"]), S)]
    yaw = [look * 0.4 * ramp(s, 0.55, 1.0) for s in S]
    return {"yaw": yaw, "pitch": pitch, "hy": look, "hp": Q["head_pitch"] + 4 * sniff,
            "a": a, "jaw": Q["jaw_pump_deg"] * (0.5 - 0.5 * math.cos(TAU * 3 * t)), "roll": 0.0, "slide": 0.0}


def mixp(p, q, k):
    out = {}
    for key in p:
        if isinstance(p[key], list):
            out[key] = [mix(x, y, k) for x, y in zip(p[key], q[key])]
        else:
            out[key] = mix(p[key], q[key], k)
    return out


def apply(p):
    build(p["yaw"], p["pitch"], p["hy"], p["hp"], p["a"], p["jaw"], p["roll"])


REAR = ST["idle"]["anchor_hi"]                  # Schwerpunkt dieses hinteren Bereichs bleibt bei Stand-Clips liegen
K.reset()
apply(idle_params(0.0))
K.place(K.REST_MID)
ANCHOR = K.centroid(0.0, REAR)
K.reset()


def pose_stand(p):
    apply(p)
    K.place(ANCHOR + Vector((p["slide"] * K.SIZE, 0, 0)), 0.0, REAR)
    K.ground("contact")


def clip_idle(P):
    N = P["frames"]
    return {"N": N, "loop": True, "kind": "stand", "grounded": True, "pose": lambda f: pose_stand(idle_params(f / N))}


def clip_ready(P):
    N = P["frames"]
    return {"N": N, "loop": True, "kind": "stand", "grounded": True, "pose": lambda f: pose_stand(ready_params(f / N))}


def variant(base, V):
    """Haltung aus base + Abweichungen V (pitch-Profil, head_pitch, front_thick, slide)."""
    p = dict(base)
    p["pitch"] = pitch_list(V["pitch"])
    p["hp"] = V["head_pitch"]
    p["slide"] = V["slide"]
    p["a"] = [x + V["front_thick"] * e * ramp(s, 0.3, 0.55) for x, e, s in zip(base["a"], TENV, S)]
    p["yaw"] = [0.0] * NS
    p["jaw"] = 0.0
    return p


def attack_measure(meas, hit_key="hit"):
    def measure():
        st, h = meas["start"], meas[hit_key]
        front = meas["front_x"]
        return {"hit_reach_m": round(h.x - st.x, 3), "hit_reach_body_frac": round((h.x - st.x) / K.SIZE, 2),
                "hit_tip_height_m": round(h.z - K.GROUND, 3),
                "hit_ahead_of_body_m": round(h.x - front, 3),
                "hit_in_front_ok": h.x - st.x > 0.05 * K.SIZE and h.x - front > 0.02 * K.SIZE
                and h.z - K.GROUND < 0.2 * K.SIZE}
    return measure


def track(meas, f, hit_frame):
    tip = K.head_tip()
    if f == 0:
        meas["start"] = tip.copy()
    if f == hit_frame:
        meas["hit"] = tip.copy()
        pts = K.chain_points()                 # vorderster Punkt des Rumpfs (Kopfansatz) beim Treffer
        meas["front_x"] = max(p.x for p in pts)


def clip_attack1(P):
    """Ready → Stauchen (Ziehharmonika, höher aufgerichtet, zurück) → explosives Strecken mit Vorstoß, Kopf fällt
    nach vorn-unten aufs Ziel (hit) → Raspeln (Kopf rollt, Rumpf ruckt nach) → zurück in Ready."""
    N, w, s_, r_, hf = P["frames"], P["windup_end"], P["strike_end"], P["rasp_end"], P["hit_frame"]
    base = ready_params(0.0)
    W, X = variant(base, P["windup"]), variant(base, P["strike"])
    meas = {}

    def pose(f):
        if f <= w:
            p = mixp(base, W, ease(f / w))
        elif f <= s_:
            p = mixp(W, X, ((f - w) / (s_ - w)) ** 1.5)                  # beschleunigt bis zum Kontakt
            p["jaw"] = P["jaw_bite_deg"] * (f - w) / (s_ - w)
        elif f <= r_:
            u = (f - s_) / (r_ - s_)
            p = dict(X)
            p["roll"] = P["rasp_roll_deg"] * math.sin(TAU * 2 * u)
            p["slide"] = X["slide"] + P["rasp_tug"] * abs(math.sin(math.pi * P["rasp_tugs"] * u))
            p["jaw"] = P["jaw_bite_deg"] * (0.6 + 0.4 * math.cos(TAU * 2 * u))
        else:
            u = (f - r_) / (N - r_)
            y = 1 - (1 - u) ** 2.5
            p = mixp(dict(X, jaw=P["jaw_bite_deg"]), base, y)
        pose_stand(p)
        track(meas, f, hf)
    return {"N": N, "loop": False, "kind": "stand", "grounded": True, "returns_to_start": True, "pose": pose,
            "measure": attack_measure(meas), "events": [{"frame": hf, "event": "hit"}]}


def clip_attack2(P):
    """Body Slam: Vorderkörper steil hoch (staucht sich), kurz halten, kracht mit dem vorderen Drittel vor dem
    Körper auf den Boden (hit), Ringe quetschen breit, Nachfedern, zurück in Ready."""
    N, re, he, imp, se = P["frames"], P["rise_end"], P["hold_end"], P["impact_frame"], P["settle_end"]
    base = ready_params(0.0)
    U, D = variant(base, P["rise"]), variant(base, P["slam"])
    meas = {}

    def pose(f):
        if f <= re:
            p = mixp(base, U, ease(f / re))
            p["jaw"] = 6 * ease(f / re)
        elif f <= he:
            p = dict(U, jaw=6.0)
            p["pitch"] = [v + 2 * math.sin(math.pi * (f - re) / (he - re)) * ramp(s, 0.5, 0.8) for v, s in zip(U["pitch"], S)]
        elif f <= imp:
            p = mixp(dict(U, jaw=6.0), D, ((f - he) / (imp - he)) ** 2)    # fällt beschleunigt (Gewicht)
        elif f <= se:
            u = (f - imp) / (se - imp)
            p = dict(D)
            sq = P["impact_squash"] * math.exp(-4 * u)                        # Aufprall: Ringe vorn quetschen breit
            p["a"] = [x + sq * e * ramp(s, 0.35, 0.6) for x, e, s in zip(D["a"], TENV, S)]
            bounce = P["bounce_deg"] * math.sin(math.pi * min(1.0, u / 0.6)) * (1 if u < 0.6 else 0)
            p["pitch"] = [v + bounce * ramp(s, 0.55, 0.85) for v, s in zip(D["pitch"], S)]
        else:
            p = mixp(D, base, ease((f - se) / (N - se)))
        pose_stand(p)
        track(meas, f, imp)
    return {"N": N, "loop": False, "kind": "stand", "grounded": True, "returns_to_start": True, "pose": pose,
            "measure": attack_measure(meas), "events": [{"frame": imp, "event": "hit"}]}


def clip_hit(P):
    """Treffer aus Ready: Vorderkörper zuckt zurück, eine Stauchwelle (dick + kurz) läuft Kopf → Schwanz, Körper
    rutscht etwas zurück, dann zurück in Ready."""
    N = P["frames"]
    base = ready_params(0.0)

    def pose(f):
        x = f / N
        e = math.sin(0.5 * math.pi * min(1.0, x / P["peak"])) * (1 - ease((x - P["peak"]) / (1 - P["peak"]))
                                                                  if x > P["peak"] else 1.0)
        c = 1.0 - x / P["ripple_end"]
        p = dict(base)
        p["pitch"] = [v + P["recoil_deg"] * e * ramp(s, 0.5, 0.8) for v, s in zip(base["pitch"], S)]
        p["hp"] = base["hp"] + P["head_snap_deg"] * e
        p["yaw"] = [P["jolt_deg"] * e * ramp(s, 0.45, 0.85) for s in S]
        p["hy"] = P["jolt_deg"] * e * 1.3
        sq = P["squash"] * (1 if x < P["ripple_end"] else 0) * min(1.0, x / 0.08)
        p["a"] = [a + sq * te * math.exp(-((s - c) / 0.12) ** 2) for a, te, s in zip(base["a"], TENV, S)]
        p["slide"] = -P["slide"] * e
        pose_stand(p)
    return {"N": N, "loop": False, "kind": "stand", "grounded": True, "returns_to_start": True, "pose": pose}


# ---------------------------------------------------------------- Eingraben / Auftauchen (Pfad durch festes Loch)
def hole_pitch(e, below_deg, above, window, side):
    """Neigung je Wirbel: hinter dem Loch (s < e) below_deg, vor dem Loch above (Wert oder Liste), weich über window.
    side = 0: Biegung liegt ganz vor dem Loch (Burrow: unter dem Boden), 1: ganz dahinter (Emerge: unter dem Boden)."""
    out = []
    for i, s in enumerate(S):
        w = ease((s - e) / window + side)                    # 0 = hinter dem Loch, 1 = davor
        av = above[i] if isinstance(above, list) else above
        out.append(mix(below_deg if not callable(below_deg) else below_deg(s), av, w))
    return out


def clip_burrow(P):
    """Liegen → Kopf neigt sich nach unten → bohrt sich am festen Eintrittspunkt E (Kopfansatz in Ruhe) in den Boden;
    jeder Wirbel taucht genau dort ab (Pfad: waagerecht bis E, dahinter dive_deg schräg nach unten). Schub-Peristaltik,
    zum Schluss ein Peitschenschlag der Schwanzspitze, am Ende ganz unter dem Boden."""
    N, te, de = P["frames"], P["tilt_end"], P["dive_end"]
    K.reset()
    E = chain_at(1.0)                                         # Ruhe: Root = 0 → Kopfansatz in Ruhe
    K.reset()
    dive, win = P["dive_deg"], P["bend_window"]

    def pose(f):
        if f <= te:
            k, e = ease(f / te), 1.0
        else:
            u = min(1.0, (f - te) / (de - te))
            u = u + 0.03 * math.sin(TAU * P["pushes"] * u)    # ruckweises Schieben
            k, e = 1.0, mix(1.0, P["end_e"], u)
            if f > de:
                e = P["end_e"]
        pitch = [mix(0.0, v, k) for v in hole_pitch(e, 0.0, -dive, win, 0.0)]
        hw = ease((1.0 + HEAD_S / 2 - e) / win + 0.5) if f > te else 1.0
        hp = -dive * k * hw                                   # Kopf folgt dem Pfad
        x = f / N
        yaw = [0.0] * NS
        if x > P["whip_start"]:                              # Peitschenschlag der Schwanzspitze (noch über dem Boden)
            v = (x - P["whip_start"]) / (1 - P["whip_start"])
            yaw = [P["whip_deg"] * math.sin(TAU * 1.5 * v) * (1 - v) * (1 - ramp(s, 0.0, 0.35)) for s in S]
        a = thick_wave(P["pushes"] * x, P["thick"] * k, P["thick_waves"])
        build(yaw, pitch, 0.0, hp, a, 4 * (0.5 - 0.5 * math.cos(TAU * P["pushes"] * x)))
        pin(e, Vector((E.x, E.y, chain_at(e).z)))
        ground_behind(E.x - 0.04 * K.SIZE)

    return {"N": N, "loop": False, "kind": "stand", "grounded": False, "pose": pose,
            "below_ground": {"entry": (E.x, E.y), "dir": (1.0, 0.0), "margin": 0.06 * K.SIZE},
            "measure": lambda: {"entry_point_x_m": round(E.x, 3), "root_motion_m": round(K.PB["Root"].location.length, 3)},
            "events": [{"frame": te, "event": "sand_burst"}, {"frame": N, "event": "burrowed"}]}


def clip_emerge(P):
    """Unter dem Boden → Kopf bricht steil (rise_deg) am Loch X durch, vorderes ~45 % schießt hoch, Maul zum Himmel,
    Hochpunkt halten → Vorderkörper kippt mit Gewicht nach vorn und kracht flach auf den Boden, federt nach →
    der Rest zieht aus dem Loch und der Körper geht in die Ready-Haltung (letzter Frame = Ready Frame 0).
    Das Loch X = Lage der Schwanzspitze in der End-Haltung (Ready)."""
    N, re, he, imp, be = P["frames"], P["rise_end"], P["hold_end"], P["impact_frame"], P["bounce_end"]
    K.reset()
    fin = ready_params(0.0)
    pose_stand(fin)
    X = chain_at(0.0)
    dz_ready = X.z - rest_z_at(0.0)
    K.reset()
    rise, win, e_top = P["rise_deg"], P["bend_window"], P["rise_e"]
    flat = [0.0] * NS
    meas = {"peak": -1.0}

    def pose(f):
        jaw, a, hy, yaw = 0.0, None, 0.0, [0.0] * NS
        dz = 0.0
        if f <= re:                                          # Durchbruch, schnell und abbremsend
            u = f / re
            e = mix(1.0 + HEAD_S + P["start_depth"], e_top, 1 - (1 - u) ** 2)   # Nase startet unter dem Boden
            pitch = [rise] * NS
            hp = rise + P["head_sky_deg"] * u                # Kopf setzt die steile Linie fort, Maul zum Himmel
            jaw = 8 * u
        elif f <= he:                                        # Hochpunkt halten, Maul pumpt
            e = e_top
            pitch = [rise] * NS
            hp = rise + P["head_sky_deg"]
            jaw = 8 + 4 * math.sin(math.pi * (f - re) / (he - re))
        elif f <= imp:                                       # kippt beschleunigt nach vorn
            x = ((f - he) / (imp - he)) ** 2
            e = e_top
            pitch = hole_pitch(e, rise, [mix(rise, v, x) for v in flat], win, 1.0)
            hp = mix(rise + P["head_sky_deg"], -6, x)
            jaw = mix(8, 4, x)
        elif f <= be:                                        # Aufprall + Nachfedern
            u = (f - imp) / (be - imp)
            e = e_top
            b = P["bounce_deg"] * math.sin(math.pi * u) * (1 - u)
            pitch = hole_pitch(e, rise, [b * ramp(s, 0.6, 0.9) for s in S], win, 1.0)
            hp = -6 + b
            sq = 0.12 * math.exp(-4 * u)
            a = [sq * te_ * ramp(s, e_top, e_top + 0.15) for te_, s in zip(TENV, S)]
            jaw = 4
        else:                                                # Rest zieht aus dem Loch, Vorderkörper → Ready
            v = ease((f - be) / (N - be))
            e = mix(e_top, 0.0, v)
            pitch = hole_pitch(e, rise * (1 - v), [mix(0.0, r_, v) for r_ in fin["pitch"]], win, 1.0)
            hp = mix(-6, fin["hp"], v)
            a = [x * v for x in fin["a"]]
            yaw = [y * v for y in fin["yaw"]]
            jaw = mix(4, fin["jaw"], v)
            hy = fin["hy"] * v
            dz = dz_ready * v
        build(yaw, pitch, hy, hp, a, jaw)
        pin(e, Vector((X.x, X.y, rest_z_at(e) + dz)))
        h = K.head_tip().z - K.GROUND
        if h > meas["peak"]:
            meas["peak"], meas["peak_frame"] = h, f
        if f == imp:
            meas["impact_tip_h"] = h
        if f == N:
            meas["end"] = {n: (K.PB[n].rotation_quaternion.copy(), K.PB[n].location.copy(), K.PB[n].scale.copy())
                           for n in K.PB.keys()}

    def measure():
        K.reset()
        pose_stand(fin)
        ok = all((K.PB[n].rotation_quaternion - q).magnitude < 1e-4 and (K.PB[n].location - l).length < 1e-4
                 and (K.PB[n].scale - sc_).length < 1e-4 for n, (q, l, sc_) in meas["end"].items())
        return {"exit_point_x_m": round(X.x, 3), "peak_head_height_m": round(meas["peak"], 3),
                "peak_frame": meas["peak_frame"], "impact_head_height_m": round(meas["impact_tip_h"], 3),
                "ends_in_ready_ok": ok}
    return {"N": N, "loop": False, "kind": "stand", "grounded": False, "pose": pose,
            "below_ground": {"entry": (X.x, X.y), "dir": (-1.0, 0.0), "margin": 0.08 * K.SIZE},
            "measure": measure,
            "events": [{"frame": 1, "event": "sand_burst"}, {"frame": imp, "event": "land"},
                       {"frame": N, "event": "emerged"}]}


def clip_death(P):
    """PLATZHALTER (Death-Clips gesperrt, Nutzer 2026-11-17): liegt gerade und still."""
    def pose(f):
        build([0.0] * NS, [0.0] * NS, 0.0, 0.0)
        K.place(K.REST_MID)
        K.ground("contact")
    return {"N": P["frames"], "loop": False, "kind": "death", "grounded": True, "pose": pose,
            "events": [{"frame": P["frames"], "event": "dead"}]}


K.bake({
    "Walk": crawl(ST["walk"]),
    "Run": crawl(ST["run"]),
    "TurnLeft": crawl(ST["turn"], turn=1.0),
    "TurnRight": crawl(ST["turn"], turn=-1.0),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Attack2": clip_attack2(ST["attack2"]),
    "Hit": clip_hit(ST["hit"]),
    "Burrow": clip_burrow(ST["burrow"]),
    "Emerge": clip_emerge(ST["emerge"]),
    "Death": clip_death(ST["death"]),
})
