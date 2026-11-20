"""Bewegungsmuster winged/drake: schwerer Wyvern (Cinder Wyvern). Gehen, Rennen, Drehen, Idle, Drohen, Biss-Ausfall,
Schwanzkeulen-Hieb, Treffer, Tod (Platzhalter), Fliegen, Segeln, Abheben, Landen. Baukasten: ../winged_kit.py.

& "D:\\Blender\\blender.exe" -b <winged_rigged.blend> -P motions/winged/drake/drake_clips.py -- <ausgabe> [<creature.toml>]

Grundsätze (Regeln des Nutzers): Ganzkörper statt Einzelteil · Flügel, Schwanz und Rumpf-Haltung ABSOLUT (Tripo hat die
Flügel ungleich gestellt und den Schwanz seitlich gebogen) · Füße stehen (IK) · Überlappung: jedes Glied folgt dem
vorherigen verzögert (Federn, Wellen) · Schleifen periodisch (nahtlos) · Drehen: Rumpf biegt sich in die Kurve, Kopf führt.
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import winged_kit as K  # noqa: E402

K.init(HERE)
from winged_kit import (LEFT, UP, R, body, ease, ease_in, gait, ik_set, jaw, legs_tuck, neck, phase, posture,  # noqa: E402
                        rot, spring_curve, tail, tail_wave, wing, wing_blend)

ST, HGT = K.ST, K.HGT
STAND = ST["stand"]
SW = STAND["wing"]
TW = 2 * math.pi


def wings(P, PR=None):
    wing("L", P)
    wing("R", PR if PR is not None else P)


def add(P, **kw):
    """Flügel-Pose P mit Zuschlägen (Zahlen addiert, Listen elementweise)."""
    out = dict(P)
    for k, v in kw.items():
        if isinstance(v, (list, tuple)):
            base = out.get(k, [0.0] * len(v))
            out[k] = [a + b for a, b in zip(base, v)]
        else:
            out[k] = out.get(k, 0.0) + v
    return out


def neck_comp(rise_deg, k=0.8):
    """Hals hebt sich, wenn sich der Rumpf gegenüber dem Stand nach vorn neigt (Kopf bleibt etwa auf Blickhöhe)."""
    return R((STAND["rise_deg"] - rise_deg) * k)


def stand_pose(flex=0.0, side=0.0, twist=0.0):
    posture(STAND["rise_deg"], flex, side, twist)


# ---------------------------------------------------------------- Gehen / Rennen / Drehen
def locomotion(P, turn=0.0):
    """Komodowaran auf zwei Beinen: Becken giert mit dem Schwungbein, Gewicht pendelt übers Standbein, Rumpf biegt sich
    seitlich (Welle), der Kopf hält die Blickrichtung (Gegendrehung im Hals), der Schwanz schwingt als verzögerte
    S-Welle, die Flügel pendeln gegengleich zum Bein derselben Seite und wippen beim Aufsetzen. Drehen: Rumpf biegt sich
    in die Kurve, Kopf führt, Schwanz schleppt nach."""
    N, off, d = P["cycle_frames"], P["order"], P["duty"]
    sgn = (turn > 0) - (turn < 0)
    WP = P.get("wing", SW)

    def pose(f):
        t = (f % N) / N
        gait(t, P, off, turn=turn)
        c = TW * (t - d / 2)                                   # 0 = Mitte Standphase links
        bob = math.cos(2 * TW * (t - P["settle"] - 0.25))
        sway = math.cos(c - TW * 0.04)                         # +1 = über dem linken Fuß
        body(dz=P["bob"] * HGT * bob, dy=P["sway"] * HGT * sway, roll=-R(P["roll_deg"]) * sway)
        rot("Pelvis", UP, -R(P["hip_yaw_deg"]) * math.cos(TW * t))
        bend = R(P["bend_deg"]) * math.cos(TW * (t - 0.08)) + R(P.get("lead_deg", 0)) * sgn
        posture(P["rise_deg"], flex=R(1.5) * bob, side=bend)
        hl = R(P.get("head_lead_deg", 0)) * sgn
        neck(yaw=-P["head_counter"] * (bend - R(P.get("lead_deg", 0)) * sgn) + hl,
             pitch=R(2.0) * math.cos(2 * TW * (t - P["settle"] - 0.32)) - neck_comp(P["rise_deg"]))
        sw_ = P["wing_swing_deg"] * math.cos(TW * (t - 0.06))  # linker Flügel vor, wenn das linke Bein hinten ist
        lift = P["wing_lift_deg"] * math.cos(2 * TW * (t - P["settle"] - 0.1))
        tr = P.get("tail_trail_deg", 0) * sgn
        wings(add(WP, sweep=sw_ - 2 * sgn, elev=lift + 3 * sgn), add(WP, sweep=-sw_ + 2 * sgn, elev=lift - 3 * sgn))
        tail_wave(t, P["tail_yaw_deg"], 2.0, freq=1, lag=P["tail_lag"], yaw_bias=-tr)
    return {"N": N, "loop": True, "kind": "locomotion", "pose": pose, "duty": d, "turn": turn, "reach": "smooth",
            "swing": lambda s, f: phase((f % N) / N, off[s], d)[0]}


# ---------------------------------------------------------------- Idle / Ready
def clip_idle(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        br = math.sin(TW * 3 * t)
        body(dz=0.004 * HGT * br, dy=0.006 * HGT * math.sin(TW * t))
        stand_pose(flex=-R(P["breathe_deg"]) * br)
        look = R(P["look_deg"]) * math.sin(TW * t) * (0.7 + 0.3 * math.sin(TW * 2 * t + 1.0))
        neck(yaw=look, pitch=R(4) * math.sin(TW * 2 * t + 0.5), head_yaw=look * 0.3, head_pitch=-R(3) * br)
        jaw(2 + 2 * math.sin(TW * 3 * t - 0.5))
        sh = P["wing_shuffle"] * (math.sin(TW * t - 0.4) * 0.6 + 0.4 * math.sin(TW * 2 * t + 0.3))
        wings(add(SW, fold=sh, elev=2 * br), add(SW, fold=sh * 0.8, elev=2 * br))
        tail_wave(t, P["tail_deg"], 2.0, freq=1, lag=0.06, yaw_bias=-look * 0.4 * 57)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "symmetric": False}


def clip_ready(P):
    N = P["frames"]
    WR = P["wing"]

    def pose(f):
        t = f / N
        sw, br = math.sin(TW * t), math.sin(TW * 2 * t)
        body(dz=-P["crouch"] * HGT + 0.005 * HGT * br, dy=P["sway"] * HGT * sw, roll=-R(2) * sw)
        posture(P["rise_deg"], flex=R(2) * br, side=R(4) * math.sin(TW * (t - 0.05)))
        neck(pitch=R(P["neck_deg"]) + R(4) * br - neck_comp(P["rise_deg"], 0.5), yaw=-R(4) * math.sin(TW * (t - 0.05)), head_pitch=-R(10))
        jaw(P["jaw_deg"] * (0.75 + 0.25 * math.sin(TW * 2 * t - 0.8)))
        wings(add(WR, elev=3 * br, fold=0.04 * math.sin(TW * 2 * t + 0.4)))
        tail_wave(t, P["tail_deg"], 4.0, freq=2, lag=0.07, pitch_bias=-8)
    return {"N": N, "loop": True, "kind": "stand", "pose": pose, "reach": "smooth", "symmetric": True}


# ---------------------------------------------------------------- Angriffe
def curves(P, N, w, s_, settle=6):
    def wind(f):
        if f <= w:
            return ease(f / w)
        return max(0.0, 1 - (f - w) / (s_ - w)) if f <= s_ else 0.0

    def strike(f):
        if f <= w:
            return 0.0
        if f <= s_:
            return ease_in((f - w) / (s_ - w), 2.0)
        h = s_ + settle
        return 1.0 if f <= h else 1 - ease((f - h) / max(1, N - 3 - h))
    return wind, strike


def clip_attack1(P):
    """Biss-Ausfall (Waran/Krokodil): Ausholen = aufrichten, Hals zurück, Flügel hoch → Ausfall: Körper schießt nach vorn
    und kippt fast waagerecht, Hals streckt sich, Flügel schlagen nach vorn-unten (Schwung), Schwanz hebt sich als
    Gegengewicht, Maul reißt auf und schnappt beim Treffer zu → schwer zurück."""
    N, w, s_ = P["frames"], P["windup_end"], P["strike_end"]
    wind, strike = curves(P, N, w, s_)

    def sp(fn, fr=3.0, z=0.45, lag=0):
        return spring_curve(lambda f: fn(f - lag), N, fr, z)
    C = {
        "rise": sp(lambda f: STAND["rise_deg"] + (P["rise_back_deg"] - STAND["rise_deg"]) * wind(f)
                   + (P["rise_strike_deg"] - STAND["rise_deg"]) * strike(f), 3.5, 0.5),
        "dx": sp(lambda f: (-0.02 * wind(f) + P["lunge"] * strike(f)) * HGT, 3.0, 0.55),
        "dz": sp(lambda f: (0.01 * wind(f) - P["drop"] * strike(f)) * HGT, 3.0, 0.5),
        "neck": sp(lambda f: P["neck_back_deg"] * wind(f) + P["neck_strike_deg"] * strike(f), 3.2, 0.4, 1),
        "wk": sp(lambda f: strike(f), 3.6, 0.6, 0),
        "wu": sp(lambda f: wind(f), 3.0, 0.5, 1),
        "tail": sp(lambda f: -14 * strike(f) + 6 * wind(f), 2.2, 0.35, 3),
    }

    def jaw_at(f):
        hf = P["hit_frame"]
        if f < w:
            return 4 * wind(f)
        if f < hf - 1:
            return P["jaw_open_deg"] * ease((f - w) / max(1, hf - 2 - w))
        return P["jaw_open_deg"] * max(0.0, 1 - (f - hf + 1) / 2.0)

    def pose(f):
        body(dx=C["dx"][f], dz=C["dz"][f])
        posture(C["rise"][f])
        neck(pitch=R(C["neck"][f]) - neck_comp(C["rise"][f], 0.6), head_pitch=-R(C["neck"][f]) * 0.4)
        jaw(jaw_at(f))
        wp = wing_blend(wing_blend(SW, P["wing_up"], max(0.0, min(1.0, C["wu"][f]))), P["wing_strike"],
                        max(0.0, min(1.0, C["wk"][f])))
        wings(wp)
        tail_wave(f / N, 3, 0, freq=1, pitch_bias=C["tail"][f])
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "reach": "smooth", "symmetric": True,
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


def clip_attack2(P):
    """Schwanzkeulen-Hieb als Ganzkörper-Peitsche: Ausholen = Körper dreht nach links, Schwanz holt nach rechts aus →
    Schlag: Welle Becken → Rumpf → Schwanzwurzel → Keule (jedes Glied später, schneller), Körper wirbelt nach rechts herum,
    die Keule fegt hoch nach links vorn, Flügel spreizen zum Balancieren, Kopf bleibt auf das Ziel gerichtet → zurück."""
    N, w, s_ = P["frames"], P["windup_end"], P["strike_end"]
    wind, strike = curves(P, N, w, s_, settle=5)
    lag = P["chain_lag"]

    def sp(fn, fr, z, k=0.0):
        return spring_curve(lambda f: fn(f - k), N, fr, z)
    yaw = sp(lambda f: R(P["yaw_wind_deg"]) * wind(f) + R(P["yaw_strike_deg"]) * strike(f), 2.6, 0.55)
    bend = sp(lambda f: R(P["bend_wind_deg"]) * wind(f) + R(P["bend_strike_deg"]) * strike(f), 2.6, 0.5, lag)
    segs = [sp(lambda f: (P["tail_wind_deg"] * wind(f) + P["tail_strike_deg"] * strike(f)) / 6, 2.4, 0.35,
               (i + 2) * lag) for i in range(6)]
    lift = sp(lambda f: P["tail_lift_deg"] * strike(f), 2.2, 0.4, 3 * lag)
    wk = sp(lambda f: max(wind(f), strike(f)), 3.0, 0.5)

    def pose(f):
        body(yaw=yaw[f], roll=-0.25 * bend[f])
        posture(STAND["rise_deg"] - 8 * max(wind(f), strike(f)), side=bend[f])
        neck(yaw=-0.8 * (yaw[f] + bend[f]), pitch=R(6) * strike(f))
        jaw(10 * strike(f))
        wp = wing_blend(SW, P["wing"], max(0.0, min(1.0, wk[f])))
        wings(add(wp, sweep=8 * math.degrees(bend[f]) / 20), add(wp, sweep=-8 * math.degrees(bend[f]) / 20))
        tail([s[f] for s in segs], [lift[f] / 6] * 6)
    return {"N": N, "loop": False, "kind": "stand", "pose": pose, "reach": "smooth",
            "events": [{"frame": P["hit_frame"], "event": "hit"}]}


# ---------------------------------------------------------------- Hit / Death
def clip_hit(P):
    """Treffer: Ruck zurück, Flügel zucken hoch, Hals schnellt zurück, Schwanz peitscht nach – zurück in den Stand."""
    N = P["frames"]

    def k_at(f, lag=0.0):
        if f <= lag:
            return 0.0
        x = (f - lag) / (N - lag)
        return 0.0 if x >= 1 else math.sin(math.pi * min(1.0, x * 2.2)) * (1 - x) ** 1.5

    def pose(f):
        k, k1, k2, k3 = k_at(f), k_at(f, 1.5), k_at(f, 3), k_at(f, 4.5)
        body(dx=-P["jolt"] * HGT * k, roll=R(3) * k1)
        stand_pose(flex=-R(P["pitch_deg"]) * k1)
        neck(pitch=-R(14) * k2, yaw=R(8) * k2, head_pitch=-R(8) * k3)
        jaw(14 * k2)
        wings(add(SW, fold=-P["wing_flinch"] * k1, elev=12 * k1, bend=[0, 0, -10 * k3, -8 * k3, -6 * k3]))
        tail([6 * k3] * 6, [-3 * k2] * 6)
    return {"N": N, "loop": False, "kind": "stand_return", "pose": pose}


def clip_death(P):
    """PLATZHALTER – Death pausiert (Nutzer, 2026-11-17). Minimal: sackt ein, Flügel hängen. Keine Arbeit hineinstecken,
    bis der Nutzer Death-Clips freigibt."""
    N = P["frames"]

    def pose(f):
        k = ease(f / N)
        body(dz=-P["sag"] * HGT * k)
        posture(STAND["rise_deg"] + (P["rise_deg"] - STAND["rise_deg"]) * k)
        neck(pitch=R(20) * k)
        wings(wing_blend(SW, {"fold": 0.6, "elev": -25, "sweep": 0, "pitch": 60, "arm": 0}, k))
        tail()
    return {"N": N, "loop": False, "kind": "death", "pose": pose, "placeholder": "Death pausiert (Nutzer)",
            "events": [{"frame": N, "event": "dead"}]}


# ---------------------------------------------------------------- Fliegen
FLY = ST["fly"]


def flap_elev(p, P=FLY):
    """Flügelhöhe im Schlagzyklus p (0 = oben): Abschlag (down_share) kräftig, Aufschlag ruhiger."""
    p %= 1.0
    ds = P["down_share"]
    if p < ds:
        return P["elev_top"] + (P["elev_bottom"] - P["elev_top"]) * ease(p / ds)
    return P["elev_bottom"] + (P["elev_top"] - P["elev_bottom"]) * ease((p - ds) / (1 - ds))


def flap_wing(p, P=FLY, power=1.0):
    """Flügel-Pose im Schlagzyklus: Abschlag gestreckt, Aufschlag angewinkelt (Hand eingeklappt, Flughund), die äußeren
    Glieder folgen verzögert (Welle zur Spitze)."""
    ds = P["down_share"]
    q = p % 1.0
    up = math.sin(math.pi * (q - ds) / (1 - ds)) if q >= ds else 0.0
    lags = [0, 0, 0.4, 0.7, 1.0]
    E = [flap_elev(p - P["tip_lag"] * L_, P) for L_ in lags]
    top, bot = P["elev_top"], P["elev_bottom"]
    E = [(top + bot) / 2 + power * (e - (top + bot) / 2) for e in E]
    bends = [0.0] + [E[i - 1] - E[i] for i in range(1, 5)]
    pitch = P["pitch_down"] if q < ds else P["pitch_down"] + (P["pitch_up"] - P["pitch_down"]) * up
    return {"fold": P["fold_up"] * up - 0.8 * (1 - up) * power, "elev": E[0], "sweep": 4 * up - P.get("sweep", 0.0), "pitch": pitch,
            "arm": P.get("arm", 0.0), "bend": bends, "curl": [0, 0, 0, 0, 0]}


def fly_body(p, P=FLY):
    """Rumpf, Hals, Schwanz im Flug (ohne Höhe): Körper hebt sich im Abschlag, Kopf bleibt ruhig, Schwanz steuert."""
    ds = P["down_share"]
    bob = -math.cos(TW * (p - ds * 0.8))                       # +1 am Ende des Abschlags
    posture(P["rise_deg"], flex=R(P["body_pitch_deg"]) * math.sin(TW * (p - 0.15)))
    neck(pitch=-R(P["body_pitch_deg"]) * math.sin(TW * (p - 0.15)) - neck_comp(P["rise_deg"]), head_pitch=R(8))
    tail_wave(p, 3, P["tail_pitch_deg"], freq=1, lag=0.06)
    return bob


def clip_fly(P):
    N = P["cycle_frames"]

    def pose(f):
        p = (f % N) / N
        for s in ("L", "R"):
            ik_set(s, 0.0)
        bob = fly_body(p, P)
        body(dz=P["height"] * HGT + P["bob"] * HGT * bob)
        legs_tuck(P["leg_tuck"])
        wings(flap_wing(p, P))
    return {"N": N, "loop": True, "kind": "air", "pose": pose, "symmetric": True, "air_height_m": round(P["height"] * HGT, 3)}


def clip_glide(P):
    N = P["frames"]

    def pose(f):
        t = f / N
        for s in ("L", "R"):
            ik_set(s, 0.0)
        bank = R(P["bank_deg"]) * math.sin(TW * t)
        body(dz=P["height"] * HGT + 0.01 * HGT * math.sin(TW * 2 * t), roll=-bank, yaw=0.3 * bank * math.sin(TW * t))
        posture(P["rise_deg"], flex=R(1.5) * math.sin(TW * 2 * t))
        neck(yaw=bank * 0.8, pitch=-neck_comp(P["rise_deg"]), head_pitch=R(8), roll=bank * 0.5)
        legs_tuck(1.0)
        flex = 3 * math.sin(TW * 2 * t + 0.5)
        wings(add(P["wing"], elev=flex + math.degrees(bank) * 0.3), add(P["wing"], elev=flex - math.degrees(bank) * 0.3))
        tail([-P["tail_deg"] * math.sin(TW * t) / 6] * 6, [0.5 * math.sin(TW * 2 * t)] * 6)
    return {"N": N, "loop": True, "kind": "air", "pose": pose, "air_height_m": round(P["height"] * HGT, 3)}


def clip_takeoff(P):
    """Ducken (Flügel hoch an den Anfang des Abschlags) → Absprung, Beine strecken sich → zwei kräftige, schnelle
    Schläge (19 Frames) bis Flughöhe; Endpose = Fly Frame 0 (nahtloser Übergang)."""
    N, jf, lf = P["frames"], P["jump_frame"], P["liftoff_frame"]
    cyc = (N - jf) / 2.0
    top = flap_wing(0.0)

    def pose(f):
        if f <= jf:
            k = ease(f / jf)
            body(dz=-P["crouch"] * HGT * k)
            posture(STAND["rise_deg"] + 8 * k)
            neck(pitch=R(10) * k)
            wings(wing_blend(SW, top, k))
            tail(None, [-1.5 * k] * 6)
            return
        p = (f - jf) / cyc
        u = (f - jf) / (N - jf)
        if f <= lf:
            dz = -P["crouch"] * HGT * (1 - ease((f - jf) / (lf - jf))) + 0.02 * HGT * ease((f - jf) / (lf - jf))
        else:
            dz = 0.02 * HGT + (FLY["height"] * HGT - 0.02 * HGT) * ease((f - lf) / (N - lf))
        bob = fly_body(p) if u > 0.5 else 0.0
        if u <= 0.5:
            posture(STAND["rise_deg"] + 8 - (STAND["rise_deg"] + 8 - FLY["rise_deg"]) * ease(u * 2))
            neck(pitch=R(10) * (1 - u * 2) - neck_comp(FLY["rise_deg"]) * u * 2, head_pitch=R(8) * u * 2)
            tail(None, [-1.5 + 2 * u] * 6)
        body(dz=dz + FLY["bob"] * HGT * bob * ease((u - 0.5) * 2))
        k_ik = 1.0 if f <= lf else 1 - ease((f - lf) / 5)
        for s in ("L", "R"):
            ik_set(s, k_ik)
        legs_tuck(ease((f - lf) / 12) if f > lf else 0.0)
        wings(flap_wing(p, FLY, power=1.15))
    return {"N": N, "loop": False, "kind": "transition", "pose": pose, "symmetric": True,
            "ground": lambda f: ["L", "R"] if f <= lf else [],
            "events": [{"frame": jf, "event": "jump"}, {"frame": lf, "event": "liftoff"}]}


def clip_land(P):
    """Anflug (ein Schlag) → Bremsen: Flügel steil nach vorn gestellt, Körper richtet sich auf, Beine strecken sich nach
    vorn-unten → Aufsetzen (Event) → Einfedern → Flügel falten sich in die Standhaltung (Endpose = Stand)."""
    N, tf = P["frames"], P["touch_frame"]
    cyc = FLY["cycle_frames"]
    flare = {"fold": -0.3, "elev": 30, "sweep": 15, "pitch": 45, "arm": 15, "bend": [0, 0, 0, 0, 0], "curl": [0, 0, 0, 0, 0]}

    def pose(f):
        if f < tf:
            u = f / tf
            k_fl = ease((f - cyc * 0.6) / (tf - cyc * 0.6)) if f > cyc * 0.6 else 0.0
            if k_fl <= 0:
                bob = fly_body(f / cyc)
            else:                                                 # Flug-Haltung → Brems-Haltung
                bob = 0.0
                posture(FLY["rise_deg"] + (STAND["rise_deg"] + 14 - FLY["rise_deg"]) * k_fl)
                neck(pitch=-neck_comp(FLY["rise_deg"]) * (1 - k_fl) + R(8) * k_fl, head_pitch=R(8) * (1 - k_fl))
                tail(None, [-2 * k_fl] * 6)
            dz = FLY["height"] * HGT * (1 - ease(u)) + FLY["bob"] * HGT * bob * (1 - k_fl)
            body(dz=dz)
            k_ik = ease((f - (tf - 6)) / 6) if f > tf - 6 else 0.0
            for s in ("L", "R"):
                ik_set(s, k_ik)
            legs_tuck((1 - ease(u * 1.6)) * (1 - k_ik))
            wings(wing_blend(flap_wing(f / cyc), flare, k_fl))
            return
        u = (f - tf) / (N - tf)
        a = math.sin(math.pi * min(1.0, u * 2.0)) * (1 - u) ** 0.5
        body(dz=-P["absorb"] * HGT * a)
        posture(STAND["rise_deg"] + 14 * (1 - ease(u)) - 6 * a)
        neck(pitch=R(8) * (1 - ease(u)) + R(10) * a)
        tail(None, [-2 * (1 - ease(u)) + 1.5 * a] * 6)
        wings(wing_blend(flare, SW, ease(u * 1.3)))
    return {"N": N, "loop": False, "kind": "transition", "pose": pose, "symmetric": True,
            "ground": lambda f: ["L", "R"] if f >= tf else [],
            "events": [{"frame": tf, "event": "land"}]}


turn = R(ST["turn"]["turn_deg"])
K.bake({
    "Walk": locomotion(ST["walk"]),
    "Run": locomotion(ST["run"]),
    "TurnLeft": locomotion(ST["turn"], turn=turn),
    "TurnRight": locomotion(ST["turn"], turn=-turn),
    "Idle": clip_idle(ST["idle"]),
    "Ready": clip_ready(ST["ready"]),
    "Attack1": clip_attack1(ST["attack1"]),
    "Attack2": clip_attack2(ST["attack2"]),
    "Hit": clip_hit(ST["hit"]),
    "Death": clip_death(ST["death"]),
    "Fly": clip_fly(ST["fly"]),
    "Glide": clip_glide(ST["glide"]),
    "TakeOff": clip_takeoff(ST["takeoff"]),
    "Land": clip_land(ST["land"]),
})
