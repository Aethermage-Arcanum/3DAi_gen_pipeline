"""Erkennung für das Skelett `winged` (Zweibeiner mit Flügeln: Wyvern/Drache, großer Vogel).
Reines numpy (läuft in Blender und außerhalb), wird nur von rigging/winged_rig.py benutzt. Kein Import aus anderen
Skeletten (Kapselung) – die Helfer (Schweißen, Komponenten, Geodäten) sind hier bewusst eigene Kopien.

Idee (Tripo liefert EIN zusammenhängendes Mesh, Flügel/Schwanz oft schief oder einseitig gestellt):
  - **Füße** = Vertices am Boden, in zwei Gruppen links/rechts (2-Means auf y). Ihre Mitte ist die Körper-Mittelebene.
  - **Beine** = die zwei Stücke, die den Boden berühren, wenn man das Mesh oberhalb einer Höhe abschneidet. Die höchste
    Höhe, bei der beide noch getrennt sind, ist der **Schritt**.
  - **Flügel** = je Seite das größte Stück jenseits einer Seitenebene (|y − Mitte| > wing_plane), das den Boden NICHT
    berührt und die Ebene hoch (Schulterhöhe) kreuzt. Ein seitlich gebogener Schwanz kreuzt sie tief → kein Flügel.
    Schulter = Kreuzungsstelle, nach innen versetzt · Handgelenk = höchster Punkt des Flügels (Kralle/Dorn am Bug) ·
    Spitze = weitester Punkt von der Schulter · Ellbogen = Anteil elbow_share auf dem kürzesten Weg Schulter → Handgelenk ·
    Hand/Finger = Weg Handgelenk → Spitze gedrittelt. Flügelebene (Normale der Oberseite) aus Spannweite × Profil.
  - **Kopf** = vorderster Punkt außerhalb der Flügel; **Schwanz** = hinterster. Hals und Schwanz folgen der echten,
    auch krummen Mittellinie: Schwerpunkte der Vertices gleichen Kanten-Abstands von der Spitze (Geodäten-Ringe).
"""
import heapq

import numpy as np


class UF:
    def __init__(self, n):
        self.p = np.arange(n)

    def find(self, i):
        p = self.p
        r = i
        while p[r] != r:
            r = p[r]
        while p[i] != r:
            p[i], i = r, p[i]
        return r

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb

    def labels(self):
        return np.array([self.find(i) for i in range(len(self.p))])


def weld(V):
    """Vertex → geschweißte Id (UV-Naht-Duplikate an gleicher Position = eine Id)."""
    key = {}
    return np.array([key.setdefault(tuple(c), len(key)) for c in np.round(V, 5)])


def weld_edges(E, wid):
    """Mesh-Kanten + Verbindungen zwischen UV-Naht-Duplikaten (Länge 0)."""
    grp = {}
    for i, w in enumerate(wid):
        grp.setdefault(w, []).append(i)
    extra = [(g[0], x) for g in grp.values() if len(g) > 1 for x in g[1:]]
    return np.vstack([E, np.array(extra, int).reshape(-1, 2)])


def components(n, Ew, sel):
    """Zusammenhängende Stücke der ausgewählten Vertices (Kanten mit beiden Enden ausgewählt). −1 = nicht gewählt."""
    uf = UF(n)
    for a, b in Ew[sel[Ew[:, 0]] & sel[Ew[:, 1]]]:
        uf.union(a, b)
    lab = uf.labels()
    lab[~sel] = -1
    return lab


def geodesic(V, Ew, seeds, allowed=None):
    """Kürzeste Wege über Mesh-Kanten (Ew inkl. Naht-Verbindungen) von allen Seed-Vertices; optional nur über `allowed`.
    → (Abstand, Vorgänger)."""
    n = len(V)
    adj = [[] for _ in range(n)]
    L = np.linalg.norm(V[Ew[:, 0]] - V[Ew[:, 1]], axis=1)
    for (a, b), l in zip(Ew, L):
        if allowed is not None and not (allowed[a] and allowed[b]):
            continue
        adj[a].append((b, l))
        adj[b].append((a, l))
    dist = np.full(n, np.inf)
    prev = np.full(n, -1)
    h = []
    for s in np.atleast_1d(seeds):
        dist[s] = 0.0
        h.append((0.0, int(s)))
    heapq.heapify(h)
    while h:
        d, i = heapq.heappop(h)
        if d > dist[i]:
            continue
        for j, l in adj[i]:
            nd = d + l
            if nd < dist[j]:
                dist[j], prev[j] = nd, i
                heapq.heappush(h, (nd, j))
    return dist, prev


def path_to(prev, i):
    out = [i]
    while prev[out[-1]] >= 0:
        out.append(prev[out[-1]])
    return out[::-1]


def resample(P, n):
    """Polylinie P (k×3) in n+1 gleich lange Abschnitte → (n+1)×3 Punkte."""
    P = np.asarray(P, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n + 1)
    return np.column_stack([np.interp(t, s, P[:, k]) for k in range(3)])


def smooth_line(P, k=2, keep_ends=True):
    P = np.asarray(P, float)
    out = P.copy()
    for i in range(len(P)):
        a, b = max(0, i - k), min(len(P), i + k + 1)
        out[i] = P[a:b].mean(0)
    if keep_ends and len(P):
        out[0], out[-1] = P[0], P[-1]
    return out


def bend_index(P, lo=0.2, hi=0.8):
    """Index der stärksten Abweichung von der Geraden Anfang→Ende im Bereich [lo, hi] (Anteil der Punkte)."""
    p0, p1 = P[0], P[-1]
    d = p1 - p0
    L2 = max(1e-12, d @ d)
    best, bi = -1.0, len(P) // 2
    for i in range(len(P)):
        f = i / max(1, len(P) - 1)
        if lo <= f <= hi:
            t = np.clip((P[i] - p0) @ d / L2, 0, 1)
            dev = np.linalg.norm(P[i] - (p0 + t * d))
            if dev > best:
                best, bi = dev, i
    return bi


def ring_centerline(V, dist, sel, step, stop):
    """Mittellinie eines Schlauchs (Hals, Schwanz): Schwerpunkt der Vertices je Abstands-Ring von der Spitze.
    stop(p, ring_vertices) → True beendet (Ansatz am Rumpf erreicht).
    → Punkte Spitze … Ansatz, Ring-Radien, erreichter Kanten-Abstand (Länge des Schlauchs über die Oberfläche)."""
    pts, rad, reach = [], [], [0.0]
    d = np.where(sel, dist, np.inf)
    k = 0
    while True:
        m = (d >= k * step) & (d < (k + 1) * step)
        if m.sum() < 3:
            if k * step > np.nanmax(np.where(np.isfinite(d), d, np.nan)):
                break
            k += 1
            continue
        c = V[m].mean(0)
        r = float(np.median(np.linalg.norm(V[m] - c, axis=1)))
        if stop(c, V[m]):
            break
        reach[0] = (k + 1) * step
        pts.append(c)
        rad.append(r)
        k += 1
        if k > 2000:
            break
    return np.array(pts), np.array(rad), reach[0]


def detect(V, T, E, part, MAIN, cfg):
    """→ dict mit allen Landmarken (Blender: vorn +X, links +Y, oben +Z)."""
    wid = weld(V)
    Ew = weld_edges(E, wid)
    n = len(V)
    main = part == MAIN
    G = float(V[main, 2].min())
    H = float(V[main, 2].max() - G)
    z = V[:, 2] - G
    out = {"GROUND": G, "H": H, "wid": wid, "Ew": Ew, "main": main}

    # ---------------------------------------------------------------- Füße (2 Gruppen am Boden)
    low = main & (z < cfg["ground_band"] * H)
    ys = V[low, 1]
    a, b = ys.min(), ys.max()
    for _ in range(20):
        m = np.abs(ys - a) < np.abs(ys - b)
        a, b = ys[m].mean(), ys[~m].mean()
    y_mid = (a + b) / 2
    out["y_mid"] = float(y_mid)
    lowi = np.where(low)[0]
    feet = {"L": lowi[V[lowi, 1] > y_mid], "R": lowi[V[lowi, 1] <= y_mid]}

    # ---------------------------------------------------------------- Beine + Schritt
    step = cfg["cut_step"] * H
    crotch, legmask = None, None
    for zc in np.arange(cfg["ground_band"] * H + step, cfg["crotch_search_top"] * H, step):
        lab = components(n, Ew, main & (z < zc))
        la, lb = lab[feet["L"]], lab[feet["R"]]
        ca = np.bincount(la[la >= 0]).argmax()
        cb = np.bincount(lb[lb >= 0]).argmax()
        if ca == cb:
            break
        crotch, legmask = zc, {"L": lab == ca, "R": lab == cb}
    if crotch is None:
        raise SystemExit("winged_detect: Beine nicht getrennt gefunden")
    out["z_crotch"] = G + crotch
    out["feet"] = feet
    out["LEGS"] = legmask

    # ---------------------------------------------------------------- Flügel
    side = main & (np.abs(V[:, 1] - y_mid) > cfg["wing_plane"] * H)
    lab = components(n, Ew, side)
    cross = np.zeros(n, bool)
    ee = Ew[side[Ew[:, 0]] != side[Ew[:, 1]]]
    cross[ee.ravel()] = True
    wings = {}
    for s, sg in (("L", 1), ("R", -1)):
        best = None
        for L_ in np.unique(lab[side]):
            m = lab == L_
            if np.sign(V[m, 1].mean() - y_mid) != sg or m.sum() < cfg["wing_min_verts"]:
                continue
            if z[m].min() < cfg["ground_band"] * H:                     # berührt den Boden → Bein/Fuß
                continue
            cr = m & cross
            if not cr.any() or z[cr].mean() < cfg["wing_cross_min"] * H:  # kreuzt tief → Schwanz
                continue
            if best is None or m.sum() > best.sum():
                best = m
        if best is None:
            raise SystemExit(f"winged_detect: Flügel {s} nicht gefunden")
        wings[s] = {"mask": best}
    # Schultergelenke symmetrisch: Tripo stellt Flügel oft ungleich (einer nach hinten gefegt → seine Kreuzungsstelle
    # liegt weiter hinten). Gelenk-x = vordere der beiden Kreuzungsstellen (+ shoulder_fwd), Höhe/Abstand = Mittel.
    Cs = {s: V[np.where(wings[s]["mask"] & cross)[0]].mean(0) for s in wings}
    z_sh = (Cs["L"][2] + Cs["R"][2]) / 2 - cfg["shoulder_down"] * H
    w_sh = max(0.0, (abs(Cs["L"][1] - y_mid) + abs(Cs["R"][1] - y_mid)) / 2 - cfg["shoulder_in"] * H)
    x_sh = max(Cs["L"][0], Cs["R"][0]) + cfg["shoulder_fwd"] * H          # der weniger nach hinten gefegte Flügel
    out["torso_x_at_shoulder"] = x_sh
    for s, sg in (("L", 1), ("R", -1)):
        m = wings[s]["mask"]
        cr = np.where(m & cross)[0]
        C = Cs[s]
        S = np.array([x_sh, y_mid + sg * w_sh, z_sh])
        idx = np.where(m)[0]
        tip = idx[np.argmax(np.linalg.norm(V[idx] - S, axis=1))]
        top = idx[np.argmax(V[idx, 2])]
        near = idx[np.linalg.norm(V[idx] - V[top], axis=1) < cfg["wrist_radius"] * H]
        wrist = V[near].mean(0)
        # Wege über den Flügel (Kreuzungsstelle → Handgelenk → Spitze)
        allowed = m | (np.linalg.norm(V - C, axis=1) < 0.05 * H)
        seed = cr[np.argmin(np.linalg.norm(V[cr] - C, axis=1))]
        d0, p0 = geodesic(V, Ew, seed, allowed)
        wv = near[np.argmin(np.linalg.norm(V[near] - wrist, axis=1))]
        arm_path = V[path_to(p0, wv)]
        d1, p1 = geodesic(V, Ew, wv, allowed)
        fin_path = V[path_to(p1, tip)]
        ap = smooth_line(resample(np.vstack([S, arm_path, wrist]), 24), 2)
        elbow = resample(ap, 100)[int(round(cfg["elbow_share"] * 100))]
        fp = smooth_line(resample(np.vstack([wrist, fin_path]), 24), 2)
        k1 = fp[int(round(cfg["hand_share"] * 24))]
        k2 = fp[int(round((cfg["hand_share"] + (1 - cfg["hand_share"]) / 2) * 24))]
        span = V[tip] - S
        span /= np.linalg.norm(span)
        # Profil: Flügel-Schwerpunkt relativ zur Bug-Linie (Schulter → Handgelenk → Spitze) = Richtung zur Hinterkante
        line = np.vstack([S, elbow, wrist, k1, k2, V[tip]])
        cen = V[m].mean(0)
        best_t, best_d = None, 1e9
        for i in range(len(line) - 1):
            a_, b_ = line[i], line[i + 1]
            t = np.clip((cen - a_) @ (b_ - a_) / max(1e-12, (b_ - a_) @ (b_ - a_)), 0, 1)
            q = a_ + t * (b_ - a_)
            if np.linalg.norm(cen - q) < best_d:
                best_d, best_t = np.linalg.norm(cen - q), q
        chord = cen - best_t
        chord -= (chord @ span) * span
        chord /= max(1e-9, np.linalg.norm(chord))
        normal = sg * np.cross(span, chord)
        normal /= np.linalg.norm(normal)
        wings[s].update({"cross": C, "shoulder": S, "elbow": elbow, "wrist": wrist, "k1": k1, "k2": k2,
                         "tip": V[tip].copy(), "normal": normal, "chord": chord, "span": span,
                         "arm_path": ap, "fin_path": fp})
    out["WINGS"] = wings

    # ---------------------------------------------------------------- Kopf + Schwanz (Mittellinien über Geodäten-Ringe)
    wing_any = wings["L"]["mask"] | wings["R"]["mask"]
    leg_any = legmask["L"] | legmask["R"]
    core = main & ~wing_any
    sh_c = (wings["L"]["shoulder"] + wings["R"]["shoulder"]) / 2
    hips = np.array([V[legmask[s] & (z > crotch - 3 * step)].mean(0) for s in ("L", "R")])
    pel = np.array([hips[:, 0].mean(), y_mid, G + crotch + cfg["hip_up"] * H])
    chest = np.array([sh_c[0] - cfg["chest_back"] * H, y_mid, sh_c[2] - cfg["chest_down"] * H])   # Schultern symmetrisch
    out["pelvis"], out["chest"] = pel, chest

    cidx = np.where(core & ~leg_any)[0]
    head_tip = cidx[np.argmax(V[cidx, 0])]
    tail_tip = cidx[np.argmin(V[cidx, 0])]
    rstep = cfg["ring_step"] * H
    dh, _ = geodesic(V, Ew, head_tip, core)
    # Hals endet, wo die Ring-Mitte die Brust erreicht (hinter der Schulterlinie bzw. nah an der Brust)
    neck_pts, neck_r, neck_geo = ring_centerline(
        V, dh, core, rstep,
        lambda c, R_: c[0] < chest[0] + cfg["neck_stop"] * H or np.linalg.norm(c - chest) < cfg["neck_stop"] * H
        or np.median(np.linalg.norm(R_ - c, axis=1)) > cfg["neck_r_max"] * H)
    dt, _ = geodesic(V, Ew, tail_tip, core & ~leg_any)
    tail_pts, tail_r, tail_geo = ring_centerline(
        V, dt, core & ~leg_any, rstep,
        lambda c, R_: c[0] > pel[0] - cfg["tail_stop"] * H or np.linalg.norm(c - pel) < cfg["tail_stop"] * H)
    neck_pts = smooth_line(smooth_line(neck_pts, 3), 3) if len(neck_pts) > 4 else neck_pts
    tail_pts = smooth_line(smooth_line(tail_pts, 3), 3) if len(tail_pts) > 4 else tail_pts
    out.update({"head_tip": V[head_tip].copy(), "tail_tip": V[tail_tip].copy(),
                "neck_line": neck_pts, "neck_r": neck_r, "neck_geo": neck_geo, "tail_geo": tail_geo, "tail_line": tail_pts, "tail_r": tail_r,
                "dist_head": dh, "dist_tail": dt, "core": core, "wing_any": wing_any, "leg_any": leg_any})
    return out
