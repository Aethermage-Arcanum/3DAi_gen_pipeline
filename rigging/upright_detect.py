"""Erkennung für das Skelett `upright` (aufrechter Zweibeiner mit langen Armen: Treant, Golem, Brute).
Reines numpy (läuft in Blender und außerhalb), wird nur von rigging/upright_rig.py benutzt.

Idee: Tripo baut solche Kreaturen meist als EIN zusammenhängendes Mesh (Rumpf, Arme und Beine verschmolzen).
Die Gliedmaßen findet man deshalb über waagerechte Schnitte durch das Mesh:
  - Schneidet man alles oberhalb einer Höhe z weg, zerfällt der Rest in Stücke (über Mesh-Kanten verbunden).
  - **Beine** = die Stücke, die den Boden berühren. Die höchste Schnitthöhe, bei der linkes und rechtes Bein noch
    getrennt sind, ist der **Schritt** (Beine laufen dort im Becken zusammen).
  - **Arme** = die beiden großen Stücke unterhalb des Schritts, die den Boden NICHT berühren (Hände hängen frei).
    Man schiebt den Schnitt pro Arm nach oben, bis der Arm mit dem Rumpf verschmilzt → **Achsel**.
  - Danach liegen die Gelenke an der echten Geometrie: Knie/Ellbogen = stärkste Biegung bzw. Engstelle der
    Mittellinie, Knöchel = wo die Wurzel-/Zehenspreizung beginnt, Handgelenk = wo die Finger zusammenlaufen.
  - **Krone** (Treant: Astkrone, Golem: Kristalle …) = wo der Rumpf-Querschnitt oberhalb der Schultern sprunghaft
    breiter wird.
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


def components_below(V, E, z_cut, sel=None):
    """Zusammenhängende Stücke aller (ausgewählten) Vertices unterhalb z_cut (Kanten mit beiden Enden darunter).
    → Label je Vertex (−1 = oberhalb/nicht gewählt)."""
    below = V[:, 2] < z_cut
    if sel is not None:
        below &= sel
    uf = UF(len(V))
    e = E[below[E[:, 0]] & below[E[:, 1]]]
    for a, b in e:
        uf.union(a, b)
    lab = uf.labels()
    lab[~below] = -1
    return lab


def slice_points(V, T, z):
    """Schnittpunkte der Dreiecke T mit der Ebene z (je geschnittene Kante ein Punkt)."""
    zt = V[T][:, :, 2]
    up = zt > z
    cross = T[up.any(1) & ~up.all(1)]
    pts = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        a, b = cross[:, i], cross[:, j]
        m = (V[a, 2] > z) != (V[b, 2] > z)
        a, b = a[m], b[m]
        s = (z - V[a, 2]) / (V[b, 2] - V[a, 2])
        pts.append(V[a] + s[:, None] * (V[b] - V[a]))
    return np.vstack(pts) if pts else np.zeros((0, 3))


def slice_contours(V, T, z, wid):
    """Geschlossene Schnittkurven der Ebene z: Schnittpunkte, die über dieselben Dreiecke verbunden sind, bilden eine
    Kurve (Finger, Beine … einzeln). → Liste von Punkt-Arrays."""
    zt = V[T][:, :, 2]
    up = zt > z
    cross = T[up.any(1) & ~up.all(1)]
    uf, key, pts = UF(3 * len(cross) + 1), {}, []
    for t in cross:
        ks = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = t[i], t[j]
            if (V[a, 2] > z) != (V[b, 2] > z):
                k = (min(wid[a], wid[b]), max(wid[a], wid[b]))
                if k not in key:
                    key[k] = len(pts)
                    s_ = (z - V[a, 2]) / (V[b, 2] - V[a, 2])
                    pts.append(V[a] + s_ * (V[b] - V[a]))
                ks.append(key[k])
        for k in ks[1:]:
            uf.union(ks[0], k)
    if not pts:
        return []
    lab = np.array([uf.find(i) for i in range(len(pts))])
    P = np.array(pts)
    return [P[lab == c] for c in np.unique(lab)]


def track(V, T, mask, z0, z1, step):
    """Mittellinie eines Körperteils (Vertex-Maske): Schwerpunkt der Schnittpunkte je Höhe, z0 → z1."""
    Tm = T[mask[T].all(1)]
    out = []
    for z in np.arange(z0, z1, step if z1 > z0 else -step):
        p = slice_points(V, Tm, z)
        if len(p) >= 3:
            c = p.mean(0)
            r = np.percentile(np.linalg.norm(p[:, :2] - c[:2], axis=1), 80)
            out.append([c[0], c[1], z, r])
    return np.array(out)


def smooth_track(tr, k=2):
    if len(tr) < 2 * k + 1:
        return tr
    out = tr.copy()
    for i in range(len(tr)):
        a, b = max(0, i - k), min(len(tr), i + k + 1)
        out[i, :2] = tr[a:b, :2].mean(0)
        out[i, 3] = tr[a:b, 3].mean()
    return out


def bend_point(tr, lo, hi, sign_dir=None):
    """Punkt der stärksten Abweichung von der Geraden Anfang→Ende im Bereich [lo, hi] (Anteil der Länge).
    sign_dir: nur Abweichung in diese Richtung zählen (z. B. Knie nach vorn)."""
    p0, p1 = tr[0, :3], tr[-1, :3]
    d = p1 - p0
    L = np.linalg.norm(d)
    best, bi = -1e9, None
    n = len(tr)
    for i in range(n):
        f = i / max(1, n - 1)
        if not lo <= f <= hi:
            continue
        t = np.clip((tr[i, :3] - p0) @ d / (L * L), 0, 1)
        off = tr[i, :3] - (p0 + t * d)
        dev = off @ sign_dir if sign_dir is not None else np.linalg.norm(off)
        if dev > best:
            best, bi = dev, i
    return bi, best


def geodesic(V, E, seeds, wid):
    """Kürzeste Wege über Mesh-Kanten (UV-Naht-Duplikate verbunden) von allen Seed-Vertices."""
    n = len(V)
    adj = [[] for _ in range(n)]
    L = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1)
    for (a, b), l in zip(E, L):
        adj[a].append((b, l))
        adj[b].append((a, l))
    grp = {}
    for i, w in enumerate(wid):
        grp.setdefault(w, []).append(i)
    for g in grp.values():
        for x in g[1:]:
            adj[g[0]].append((x, 0.0))
            adj[x].append((g[0], 0.0))
    dist = np.full(n, np.inf)
    h = []
    for s in np.where(seeds)[0]:
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
                dist[j] = nd
                heapq.heappush(h, (nd, j))
    return dist


def detect(V, T, part, MAIN, cfg):
    """→ dict mit allen Landmarken (Weltkoordinaten, Blender: vorn +X, links +Y, oben +Z)."""
    main = part == MAIN
    wid = weld(V)
    # Kanten aus Dreiecken + Naht-Duplikate (sonst zerfällt das Mesh an UV-Nähten in Stücke)
    E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    first, seam = {}, []
    for i, w in enumerate(wid):
        if w in first:
            seam.append((first[w], i))
        else:
            first[w] = i
    if seam:
        E = np.vstack([E, np.array(seam)])
    E = E[main[E[:, 0]] & main[E[:, 1]]]
    M = V[main]
    GROUND = float(V[:, 2].min())
    H = float(M[:, 2].max() - GROUND)
    step = cfg["cut_step"] * H
    ground_v = main & (V[:, 2] < GROUND + cfg["ground_band"] * H)
    y_mid = float(np.median(M[:, 1]))

    # ---------------------------------------------------------------- Beine + Schritt
    def ground_comps(z):
        lab = components_below(V, E, z, main)
        ids, cnt = np.unique(lab[ground_v], return_counts=True)
        keep = [(c, i) for i, c in zip(ids, cnt) if i >= 0]
        return lab, sorted(keep, reverse=True)

    z_crotch = None
    for z in np.arange(GROUND + cfg["crotch_search_top"] * H, GROUND + 0.05 * H, -step):
        lab, gc = ground_comps(z)
        tot = ground_v.sum()
        if len(gc) >= 2 and gc[1][0] >= cfg["leg_min_share"] * tot:
            ya = V[lab == gc[0][1], 1].mean()
            yb = V[lab == gc[1][1], 1].mean()
            if (ya - y_mid) * (yb - y_mid) < 0:
                z_crotch = float(z)
                break
    if z_crotch is None:
        raise SystemExit("upright_detect: keine zwei getrennten Beine gefunden (Schritt)")
    lab, gc = ground_comps(z_crotch)
    LEGS = {}
    for _, cid in gc[:2]:
        m = lab == cid
        side = "L" if V[m, 1].mean() > y_mid else "R"
        LEGS[side] = {"mask": m}

    # ---------------------------------------------------------------- Arme (frei hängende große Stücke) + Achsel
    lab = components_below(V, E, z_crotch, main)
    legs_ids = {lab[np.where(L_["mask"])[0][0]] for L_ in LEGS.values()}
    cand = []
    for cid in np.unique(lab[lab >= 0]):
        if cid in legs_ids:
            continue
        m = lab == cid
        span = V[m, 2].max() - V[m, 2].min()
        if span >= cfg["arm_min_span"] * H and m.sum() >= 10:
            cand.append((m.sum(), cid, V[m, 1].mean() - y_mid))
    cand.sort(reverse=True)
    ARMS = {}
    for n, cid, dy in cand:
        side = "L" if dy > 0 else "R"
        if side not in ARMS:
            m = lab == cid
            ARMS[side] = {"seed": int(np.where(m)[0][V[m, 2].argmin()])}
    for side, A in ARMS.items():
        z = z_crotch
        last = None
        while z < GROUND + H:
            lab = components_below(V, E, z, main)
            s = lab[A["seed"]]
            if any(lab[np.where(L_["mask"])[0][0]] == s for L_ in LEGS.values()):
                break
            last = (z, lab == s)
            z += step
        A["armpit"] = float(last[0])
        A["mask"] = last[1]
        A["tip"] = V[A["seed"]].copy()

    # ---------------------------------------------------------------- Rumpf-Mittellinie + Krone
    limb = np.zeros(len(V), bool)
    for X in list(LEGS.values()) + list(ARMS.values()):
        limb |= X["mask"]
    body = main & ~limb
    z_arm = min(A["armpit"] for A in ARMS.values()) if ARMS else z_crotch + 0.3 * H
    Tb = T[body[T].all(1)]
    trunk = []
    for z in np.arange(z_crotch, GROUND + H, step):
        p = slice_points(V, Tb, z)
        if len(p) < 3:
            continue
        # nur der Querschnitt um die bisherige Mitte (Äste/Strähnen außen ignorieren)
        c = trunk[-1][:2] if trunk else np.median(p[:, :2], 0)
        r0 = cfg["trunk_radius"] * H
        q = p[np.linalg.norm(p[:, :2] - c, axis=1) < max(r0, 1.5 * (trunk[-1][3] if trunk else r0))]
        if len(q) < 3:
            q = p
        cc = q.mean(0)
        w = np.ptp(p[:, 1])                     # volle Breite des Schnitts (inkl. Äste) für die Kronen-Erkennung
        trunk.append([cc[0], cc[1], z, np.percentile(np.linalg.norm(q[:, :2] - cc[:2], axis=1), 80), w])
    trunk = np.array(trunk)
    below_arm = trunk[(trunk[:, 2] > z_crotch) & (trunk[:, 2] < z_arm)]
    w_ref = float(np.median(below_arm[:, 4])) if len(below_arm) else float(np.median(trunk[:, 4]))
    z_crown = None
    if cfg.get("crown", True):
        for row in trunk:
            if row[2] > z_arm + cfg["crown_min_above_armpit"] * H and row[4] > cfg["crown_width_ratio"] * w_ref:
                z_crown = float(row[2])
                break
    z_top = GROUND + H
    return {"GROUND": GROUND, "H": H, "y_mid": y_mid, "E": E, "wid": wid, "main": main,
            "z_crotch": z_crotch, "z_armpit": z_arm, "z_crown": z_crown, "z_top": z_top,
            "LEGS": LEGS, "ARMS": ARMS, "trunk": trunk, "trunk_width": w_ref}
