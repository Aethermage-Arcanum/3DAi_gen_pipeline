"""Erkennung der Anatomie eines Krabbler-Meshes (Spinne/Insekt), das aus vielen Einzelteilen (Inseln) besteht.

Konvention nach dem Import: oben = +Z, Kopf = +X (Tripo-GLB). Wird von octopod_rig.py importiert.

Ergebnis: dict mit
  islands   – Liste der Inseln (Vertex-Indizes, Schwerpunkt, Bounding-Box)
  legs      – Liste von Beinen: Insel-Kette Fuß→Körper, Gelenkpunkte Körper→Fuß, Seite, Slot
  body      – Insel-Indizes des Rumpfs (inkl. Kopf)
  head      – Insel-Indizes des Kopfs, antennae/mandibles – Ketten
  spine     – Punkte Hinterleib-Ende → Kopf-Spitze
"""
from collections import deque

import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree


def _islands(bm):
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop()
            comp.append(a.index)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index)
                    stack.append(b)
        out.append(comp)
    return out


def detect(obj, cfg):
    # Ein-Mesh-Fallback (seit 2026-11-21, Broodling): Tripo liefert neuere Spinnen als EIN zusammenhängendes Mesh.
    # Dann gibt es keine Inseln pro Beinsegment → Beine über Oberflächen-Wege finden (detect_single).
    # Greift nur, wenn das verschweißte Mesh aus höchstens single_mesh_max_parts Teilen besteht (oder per
    # creature.toml [octopod.detect] single_mesh = true erzwungen). Mehrteilige Meshes (Chitin Crawler) → alter Weg.
    mode = cfg.get("single_mesh", False)
    if mode is True or (mode == "auto" and _welded_parts(obj) <= cfg.get("single_mesh_max_parts", 3)):
        return detect_single(obj, cfg)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.verts.ensure_lookup_table()
    co = [v.co.copy() for v in bm.verts]
    bm.free()

    zs = [c.z for c in co]
    zmin, zmax = min(zs), max(zs)
    size = max(max(c.x for c in co) - min(c.x for c in co), max(c.y for c in co) - min(c.y for c in co))
    eps = cfg["contact_eps"] * size

    isl_verts = _islands_from_coords(obj)
    owner = {}
    for i, vs in enumerate(isl_verts):
        for v in vs:
            owner[v] = i
    islands = []
    for i, vs in enumerate(isl_verts):
        pts = [co[v] for v in vs]
        c = sum(pts, Vector()) / len(pts)
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        islands.append({"i": i, "verts": vs, "center": c, "min": mn, "max": mx})

    # ---- Nachbarschaft zwischen Inseln: kleinster Vertex-Abstand je Inselpaar ----
    kd = KDTree(len(co))
    for i, c in enumerate(co):
        kd.insert(c, i)
    kd.balance()
    best = {}      # (a,b) -> kleinster Abstand
    contacts = {}  # (a,b) -> Kontaktpunkte (alle Paare unter eps bzw. der nächste)
    for vi, c in enumerate(co):
        a = owner[vi]
        for (p, vj, d) in kd.find_n(c, cfg["neighbors"]):
            b = owner[vj]
            if b == a:
                continue
            key = (min(a, b), max(a, b))
            if d < best.get(key, (1e9,))[0]:
                best[key] = (d, (c + p) / 2)
            if d < eps:
                contacts.setdefault(key, []).append((c + p) / 2)
    for key, (d, mp) in best.items():
        contacts.setdefault(key, [mp])

    # Minimaler Spannbaum (Kruskal): jede Insel hängt am nächstgelegenen Nachbarn – Lücken egal
    parent_uf = list(range(len(islands)))

    def find(x):
        while parent_uf[x] != x:
            parent_uf[x] = parent_uf[parent_uf[x]]
            x = parent_uf[x]
        return x

    adj = {i: set() for i in range(len(islands))}
    for (a, b), (d, _) in sorted(best.items(), key=lambda kv: kv[1][0]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent_uf[ra] = rb
            adj[a].add(b)
            adj[b].add(a)

    def contact_point(a, b):
        pts = contacts.get((min(a, b), max(a, b)))
        if not pts:  # kein direkter Kontakt: nächste Punkte der Bounding-Boxen
            return (islands[a]["center"] + islands[b]["center"]) / 2
        return sum(pts, Vector()) / len(pts)

    # ---- Rumpf: Inseln, die die Mittellinie (y≈0) berühren ----
    mid = cfg["midline_tol"] * size
    body = {isl["i"] for isl in islands if isl["min"].y <= mid and isl["max"].y >= -mid}

    # ---- Füße: Inseln mit Bodenkontakt, nicht Rumpf ----
    ground = zmin + cfg["ground_tol"] * (zmax - zmin)
    feet = [isl["i"] for isl in islands if isl["min"].z <= ground and isl["i"] not in body]

    debug = []

    def path_to_body(f, body_set):
        prev = {f: None}
        q = deque([f])
        hit = None
        while q:
            a = q.popleft()
            if a in body_set:
                hit = a
                break
            for b in adj[a]:
                if b not in prev:
                    prev[b] = a
                    q.append(b)
        if hit is None:
            return None
        out, a = [], hit
        while a is not None:
            out.append(a)
            a = prev[a]
        return out  # Rumpf-Insel, ..., Fuß

    # Echte Fußspitzen: Fuß-Inseln, die nicht auf dem Weg einer anderen Fuß-Insel liegen
    paths = {f: path_to_body(f, body) for f in feet}
    tips = [f for f in feet if paths[f] and not any(f in paths[g][:-1] for g in feet if g != f and paths[g])]
    # Verbindungsteile, die von mehreren Beinen geteilt werden → zum Rumpf (Gelenkring/Seitenplatte)
    usage = {}
    for f in tips:
        for i in paths[f][1:]:
            usage[i] = usage.get(i, 0) + 1
    hubs = {i for i, n in usage.items() if n > 1}
    if hubs:
        debug.append(f"geteilte Verbindungsteile → Rumpf: {sorted(hubs)}")
    body_core = set(body)
    body = body | hubs
    feet = tips

    # ---- Bein-Ketten: kürzester Weg Fuß → Rumpf im Spannbaum ----
    legs = []
    used = set()
    for f in feet:
        prev = {f: None}
        q = deque([f])
        hit = None
        while q:
            a = q.popleft()
            if a in body:
                hit = a
                break
            for b in adj[a]:
                if b not in prev:
                    prev[b] = a
                    q.append(b)
        fc = islands[f]["center"]
        if hit is None:
            debug.append(f"foot {f} at {tuple(round(x, 2) for x in fc)}: kein Weg zum Rumpf")
            continue
        path = []
        a = hit
        while a is not None:
            path.append(a)
            a = prev[a]
        # path: Rumpf-Insel, Bein-Inseln..., Fuß
        chain = [p for p in path if p not in body]
        if not chain or used & set(chain):
            debug.append(f"foot {f} at {tuple(round(x, 2) for x in fc)}: Kette {chain} überschneidet "
                         f"bereits benutzte Teile {sorted(used & set(chain))}")
            continue
        used |= set(chain)
        # Gelenkpunkte: Körper-Kontakt, Kontakte zwischen Segmenten, Fußspitze
        joints = [contact_point(path[0], chain[0])]
        for a, b in zip(chain, chain[1:]):
            joints.append(contact_point(a, b))
        fpts = [co[v] for v in islands[chain[-1]]["verts"]]
        far = max(fpts, key=lambda p: (p - joints[-1]).length)  # Spitze = weitester Punkt vom letzten Gelenk
        joints.append(far)
        side = "L" if islands[chain[0]]["center"].y > 0 else "R"   # +Y = links (Kopf +X, oben +Z)
        legs.append({"islands": chain, "joints": joints, "side": side, "body_island": path[0]})

    # Slots: pro Seite von vorne (+X) nach hinten nummerieren
    for side in ("L", "R"):
        s = sorted([l for l in legs if l["side"] == side], key=lambda l: -l["joints"][0].x)
        for k, l in enumerate(s, 1):
            l["slot"] = k

    # Inseln, die an Beinketten hängen, aber nicht im Pfad liegen (z. B. Gelenkkappen) → nächstes Bein
    leg_of = {i: n for n, l in enumerate(legs) for i in l["islands"]}
    rest = [isl["i"] for isl in islands if isl["i"] not in body and isl["i"] not in leg_of]

    # ---- Kopf, Fühler, Mandibeln (vorne, nicht Bein) ----
    xs = [c.x for c in co]
    xmax = max(xs)
    head_x = xmax - cfg["head_fraction"] * (xmax - min(xs))
    appendages = [i for i in rest if islands[i]["center"].x > head_x]
    antennae = [i for i in appendages if islands[i]["center"].z > islands[i]["center"].z * 0 + (zmin + zmax) / 2]
    mandibles = [i for i in appendages if i not in antennae]
    others = [i for i in rest if i not in appendages]

    # ---- Wirbelsäule: Rumpf-Inseln entlang X ----
    body_pts = [co[v] for i in body for v in islands[i]["verts"]]
    bx = sorted(p.x for p in body_pts)
    spine = {"x_min": bx[0], "x_max": bx[-1],
             "z_mid": sum(p.z for p in body_pts) / len(body_pts)}

    debug.append(f"feet: {len(feet)} Inseln mit Bodenkontakt: " +
                 ", ".join(f"{f}@{tuple(round(x, 2) for x in islands[f]['center'])}" for f in feet))
    return {"debug": debug, "islands": islands, "adj": adj, "legs": legs, "body": sorted(body),
            "body_core": sorted(body_core), "antennae": antennae,
            "mandibles": mandibles, "others": others, "ground_z": zmin, "size": size, "spine": spine,
            "contact_point": contact_point, "coords": co}


def _islands_from_coords(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    out = _islands(bm)
    bm.free()
    return out


# ====================================================================== Ein-Mesh-Erkennung (seit 2026-11-21)
# Für Spinnen aus EINEM zusammenhängenden Tripo-Mesh (10_broodling). Eigene Kopie des Oberflächen-Weg-Ansatzes aus
# multileg_rig.py (kein Import: "kein Skelett hängt am Baukasten eines anderen"). Liefert dieselbe Struktur wie
# detect(): Pseudo-Inseln = 1 Rumpf-Insel + 1 Insel pro Bein, Gelenkkette = Bein-Mittellinie Wurzel → Spitze.
def _weld(obj):
    import numpy as np
    n = len(obj.data.vertices)
    V = np.empty(n * 3)
    obj.data.vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    M = np.array(obj.matrix_world)
    V = V @ M[:3, :3].T + M[:3, 3]
    key, rep = {}, np.empty(n, int)
    for i, c in enumerate(np.round(V, 5)):                 # UV-Nähte trennen Vertices → nach Position verschweißen
        rep[i] = key.setdefault((float(c[0]), float(c[1]), float(c[2])), i)
    E = np.empty(len(obj.data.edges) * 2, int)
    obj.data.edges.foreach_get("vertices", E)
    E = rep[E.reshape(-1, 2)]
    return V, rep, E[E[:, 0] != E[:, 1]]


def _welded_parts(obj):
    V, rep, E = _weld(obj)
    par = {int(r): int(r) for r in set(rep.tolist())}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b in E:
        ra, rb = find(int(a)), find(int(b))
        if ra != rb:
            par[ra] = rb
    return len({find(x) for x in par})


def _wall_thickness(obj, V):
    """Wand-Dicke je Vertex (Shape Diameter Function): Strahlen ins Innere (5er-Kegel, 25°) bis zur Gegenseite,
    Median. Beine ≈ 0,04, Rumpf ≈ 0,2–0,4 (Anteil Größe) → trennt Bein und Rumpf auch bei EINEM Mesh."""
    import math
    import numpy as np
    from mathutils.bvhtree import BVHTree
    me = obj.data
    bvh = BVHTree.FromPolygons([Vector(p) for p in V], [tuple(pl.vertices) for pl in me.polygons])
    m3 = obj.matrix_world.to_3x3()
    tan = math.tan(math.radians(25))
    out = np.zeros(len(V))
    for i, v in enumerate(me.vertices):
        n = (m3 @ v.normal).normalized()
        t = n.orthogonal().normalized()
        b = n.cross(t)
        p = Vector(V[i])
        ds = []
        for u, w in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            d = (-n + (t * u + b * w) * tan).normalized()
            h = bvh.ray_cast(p + d * 1e-4, d)
            if h[0] is not None:
                ds.append(h[3])
        out[i] = float(np.median(ds)) if ds else 0.0
    return out


def detect_single(obj, cfg):
    import heapq
    import numpy as np
    V, rep, E = _weld(obj)
    N = len(V)
    co = [Vector(p) for p in V]
    zmin, zmax = float(V[:, 2].min()), float(V[:, 2].max())
    H = zmax - zmin
    size = float(max(np.ptp(V[:, 0]), np.ptp(V[:, 1])))
    reps = np.unique(rep)
    adj = {int(r): [] for r in reps}
    for a, b in E:
        w = float(np.linalg.norm(V[a] - V[b]))
        adj[int(a)].append((int(b), w))
        adj[int(b)].append((int(a), w))
    debug = [f"Ein-Mesh-Erkennung: {N} Vertices, {len(reps)} verschweißt"]
    SDF = _wall_thickness(obj, V)
    sdf_r = cfg["sm_sdf_radius"] * size

    # Körpermitte: iterativ zum dichtesten Bereich, dann auf die Mittelebene (Eierhaufen o. ä. ist asymmetrisch)
    c = np.median(V, 0)
    for rad in (0.35, 0.25, 0.18, 0.12):
        sel = V[np.linalg.norm(V - c, axis=1) < rad * size]
        if len(sel) > 20:
            c = sel.mean(0)
    c[1] = 0.0
    src = int(reps[np.argmin(np.linalg.norm(V[reps] - c, axis=1))])
    dist, prev, pq = {src: 0.0}, {}, [(0.0, src)]
    while pq:
        dd, u = heapq.heappop(pq)
        if dd > dist.get(u, 1e18):
            continue
        for v, w in adj[u]:
            nd = dd + w
            if nd < dist.get(v, 1e18):
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd, v))

    # Extremitäten = lokale Maxima der Oberflächen-Entfernung zur Mitte (k-Ring)
    ext = []
    for u in reps:
        u = int(u)
        g = dist.get(u)
        if g is None or g < cfg["sm_ext_min"] * size:
            continue
        nb, fr = {u}, [u]
        for _ in range(4):
            nf = []
            for x in fr:
                for y, _w in adj[x]:
                    if y not in nb:
                        nb.add(y)
                        nf.append(y)
            fr = nf
        if all(dist.get(y, 0.0) <= g for y in nb):
            ext.append((g, u))
    ext.sort(reverse=True)
    keep = []
    for g, u in ext:
        if all(np.linalg.norm(V[u] - V[k]) > 0.06 * size for _, k in keep):
            keep.append((g, u))
    # Fußspitzen: Extremitäten nahe am Boden (auch leicht angehobene Beine) und seitlich der Mitte
    band = zmin + cfg["sm_tip_band"] * H
    tips = [u for g, u in keep if V[u, 2] <= band and abs(V[u, 1]) > cfg["sm_tip_min_side"] * size]
    other_ext = [u for g, u in keep if u not in tips]
    by_side = {"L": [u for u in tips if V[u, 1] > 0], "R": [u for u in tips if V[u, 1] < 0]}
    for s in by_side:                                       # höchstens 4 je Seite: die bodennächsten
        by_side[s] = sorted(by_side[s], key=lambda u: V[u, 2])[:4]
    debug.append("Extremitäten ohne Bodenkontakt (kein Bein): " +
                 ", ".join(str(tuple(round(float(x), 2) for x in V[u])) for u in other_ext))

    def surface_path(u):
        p = [u]
        while p[-1] in prev:
            p.append(prev[p[-1]])
        return p                                            # Spitze → Mitte

    cap = cfg["sm_thick_cap"] * size
    slab = cfg["sm_slab"] * size

    def section(i_pt, d):
        """Querschnitt am Punkt: zusammenhängender Teil des Mesh in einer dünnen Scheibe senkrecht zu d.
        → (Schwerpunkt, Radius p90). Der Radius springt am Übergang Bein → Rumpf."""
        p = V[i_pt]
        rel = V[reps] - p
        along = rel @ d
        near = np.linalg.norm(rel, axis=1) < cap
        S = {int(r) for r in reps[(np.abs(along) < slab) & near]}
        S.add(i_pt)
        comp, fr = {i_pt}, [i_pt]
        while fr:
            nf = []
            for x in fr:
                for y, _w in adj[x]:
                    if y in S and y not in comp:
                        comp.add(y)
                        nf.append(y)
            fr = nf
        P = V[list(comp)]
        ctr = P.mean(0)
        q = P - ctr
        q = q - np.outer(q @ d, d)
        return ctr, float(np.percentile(np.linalg.norm(q, axis=1), 90)), len(comp)

    legs = []
    for side in ("L", "R"):
        for tip in by_side[side]:
            path = surface_path(tip)
            P = V[path]
            n = len(P)
            ctrs, rads = [], []
            for i in range(n):
                d = P[max(0, i - 2)] - P[min(n - 1, i + 2)]     # Richtung Mitte → Spitze
                d = d / (np.linalg.norm(d) or 1.0)
                ctr, r, _ = section(path[i], d)
                ctrs.append(ctr)
                rads.append(r)
            rads = np.array(rads)
            arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
            # Wurzel = wo die Wand-Dicke (SDF, Median der Umgebung) vom dünnen Bein auf Rumpf-Dicke springt.
            # (Der Querschnitt allein ist bei Low-Poly-Beinen mit dicken Gelenkknubbeln zu verrauscht.)
            sdf_path = np.array([float(np.median(SDF[reps][np.linalg.norm(V[reps] - p, axis=1) < sdf_r]))
                                 for p in P])
            base = float(np.median(sdf_path[arc <= 0.45 * arc[-1]]))
            thr = max(cfg["sm_root_sdf"] * size, cfg["sm_root_ratio"] * base)
            root_i = n - 1
            for i in range(n):
                if arc[i] > cfg["sm_root_min_arc"] * arc[-1] and sdf_path[i] > thr:
                    root_i = i
                    break
            C = np.array(ctrs[:root_i + 1])                     # Mittellinie Spitze → Wurzel
            C[0] = V[tip]
            C = C[::-1]                                         # gleichmäßig neu abtasten (Wurzel → Spitze)
            seg = np.linalg.norm(np.diff(C, axis=0), axis=1)
            s_ = np.concatenate([[0], np.cumsum(seg)])
            t_ = np.linspace(0, s_[-1], cfg["sm_leg_points"])
            joints = [Vector([float(np.interp(x, s_, C[:, k])) for k in range(3)]) for x in t_]
            legs.append({"tip": tip, "joints": joints, "side": side,
                         "reach": cfg["sm_leg_capture"] * float(np.percentile(rads[:root_i + 1], 90)),
                         "tip_lift": float(V[tip, 2] - zmin), "root_rad": float(sdf_path[root_i]), "leg_rad": base,
                         "profile": [(round(float(a_), 3), round(float(r_), 3)) for a_, r_ in zip(arc, sdf_path)]})
    for side in ("L", "R"):
        for k, l in enumerate(sorted([l for l in legs if l["side"] == side], key=lambda l: -l["joints"][0].x), 1):
            l["slot"] = k
    # Symmetrie: Körper und Beine sind spiegelgleich (nur Aufsätze wie der Eierhaufen nicht) → Gelenkketten der
    # Beinpaare mitteln, sonst laufen linke und rechte Seite ungleich.
    if cfg.get("sm_symmetrize", True):
        for k in range(1, 5):
            pair = {l["side"]: l for l in legs if l["slot"] == k}
            if len(pair) == 2:
                for a_, b_ in zip(pair["L"]["joints"], pair["R"]["joints"]):
                    m_ = Vector(((a_.x + b_.x) / 2, (a_.y - b_.y) / 2, (a_.z + b_.z) / 2))
                    a_[:] = m_
                    b_[:] = (m_.x, -m_.y, m_.z)
    for l in legs:
        # Bein-Vertices: von der Spitze aus über die Oberfläche wachsen, nur jenseits der Wurzel-Ebene und
        # nahe an der Mittellinie (sonst würde Rumpf-Haut mitgenommen)
        joints, tip = l["joints"], l["tip"]
        root, nrm = np.array(joints[0][:]), np.array((joints[1] - joints[0]).normalized()[:])
        Cj = np.array([j[:] for j in joints])
        dl = np.full(len(reps), 1e9)
        Q = V[reps]
        for a, b in zip(Cj[:-1], Cj[1:]):
            ab = b - a
            tt = np.clip(((Q - a) @ ab) / max(1e-12, ab @ ab), 0, 1)
            dl = np.minimum(dl, np.linalg.norm(Q - (a + tt[:, None] * ab), axis=1))
        thin = SDF[reps] < cfg["sm_leg_max_sdf"] * size          # Rumpf/Kopf sind dick → nie Bein-Haut
        okv = {int(r) for r in reps[((Q - root) @ nrm > 0) & (dl < l["reach"]) & thin]}
        grown, fr = {tip}, [tip]
        while fr:
            nf = []
            for x in fr:
                for y, _w in adj[x]:
                    if y in okv and y not in grown:
                        grown.add(y)
                        nf.append(y)
            fr = nf
        l["set"] = grown
        l["knee_z"] = float(max(j.z for j in joints))
    # Überschneidungen (zwei Beine wachsen in dieselbe Haut): Vertex zum näheren Bein
    owner = {}
    for k, l in enumerate(legs):
        for u in l["set"]:
            owner.setdefault(u, []).append(k)
    for u, ks in owner.items():
        if len(ks) > 1:
            best = min(ks, key=lambda k: min((Vector(V[u]) - j).length for j in legs[k]["joints"]))
            for k in ks:
                if k != best:
                    legs[k]["set"].discard(u)

    # Pseudo-Inseln (Original-Vertex-Indizes): 0 = Rumpf, 1.. = Beine
    leg_of = {}
    for k, l in enumerate(legs, 1):
        for u in l["set"]:
            leg_of[u] = k

    # Von Tripo verschmolzene Stellen (Bein berührt Eierhaufen/Kopf oder ein anderes Bein): Flächen, die ein Bein
    # weit weg von seiner Wurzel mit dem Rumpf oder einem anderen Bein verbinden, sind keine echte Haut → löschen
    # und neu erkennen (sonst zieht das Bein die Rumpf-Haut mit: Dehnung ×5–7). Vorbild: multileg cut_fused_limbs.
    if cfg.get("sm_cut_fused", True) and not cfg.get("_sm_cut_done"):
        far = {}
        for k, l in enumerate(legs, 1):
            Cj = np.array([j[:] for j in l["joints"]])
            seg = np.linalg.norm(np.diff(Cj, axis=0), axis=1)
            cum = np.concatenate([[0], np.cumsum(seg)])
            us = np.array(sorted(l["set"]))
            if not len(us):
                continue
            Q = V[us]
            best_d, best_s = np.full(len(us), 1e9), np.zeros(len(us))
            for i, (a, b) in enumerate(zip(Cj[:-1], Cj[1:])):
                ab = b - a
                tt = np.clip(((Q - a) @ ab) / max(1e-12, ab @ ab), 0, 1)
                dd = np.linalg.norm(Q - (a + tt[:, None] * ab), axis=1)
                upd = dd < best_d
                best_d[upd], best_s[upd] = dd[upd], (cum[i] + tt * seg[i])[upd] / cum[-1]
            for u, s_ in zip(us, best_s):
                far[int(u)] = s_ > cfg["sm_fuse_min_frac"]
        cut = []
        for pl in obj.data.polygons:
            own = {leg_of.get(int(rep[v]), 0) for v in pl.vertices}
            if len(own) < 2:
                continue
            if len(own - {0}) >= 2 or any(far.get(int(rep[v]), False) for v in pl.vertices):
                cut.append(pl.index)
        n_mixed = sum(1 for pl in obj.data.polygons if len({leg_of.get(int(rep[v]), 0) for v in pl.vertices}) > 1)
        debug.append(f"Flächen zwischen Bein und Rumpf/Bein: {n_mixed}, davon verschmolzen (gelöscht): {len(cut)}")
        if cut:
            import bmesh as _bm
            bm = _bm.new()
            bm.from_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            _bm.ops.delete(bm, geom=[bm.faces[i] for i in cut], context="FACES")
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()
            again = detect_single(obj, dict(cfg, _sm_cut_done=True))
            again["debug"].insert(1, f"verschmolzene Stellen getrennt: {len(cut)} Flächen gelöscht "
                                     f"(Bein ↔ Rumpf jenseits {cfg['sm_fuse_min_frac']:.0%} der Beinlänge, Bein ↔ Bein)")
            again["fused_faces_cut"] = len(cut)
            return again
    isl_verts = [[] for _ in range(len(legs) + 1)]
    for v in range(N):
        isl_verts[leg_of.get(int(rep[v]), 0)].append(v)
    islands = []
    for i, vs in enumerate(isl_verts):
        pts = V[vs]
        islands.append({"i": i, "verts": vs, "center": Vector(pts.mean(0)), "min": Vector(pts.min(0)),
                        "max": Vector(pts.max(0))})
    out_legs = []
    for k, l in enumerate(legs, 1):
        out_legs.append({"islands": [k], "joints": l["joints"], "side": l["side"], "slot": l["slot"], "body_island": 0})
        debug.append(f"Bein {l['side']}{l['slot']}: Wurzel {tuple(round(x, 3) for x in l['joints'][0])}, "
                     f"Spitze {tuple(round(x, 3) for x in l['joints'][-1])}, Spitze über Boden "
                     f"{l['tip_lift'] / H * 100:.1f} % der Höhe, Knie z {l['knee_z']:.3f}, "
                     f"Wanddicke Bein {l['leg_rad']:.3f} / Wurzel {l['root_rad']:.3f}, {len(isl_verts[k])} Vertices; "
                     f"Wanddicke (Weg, SDF) Spitze→Mitte: {l['profile']}")
    body_pts = V[isl_verts[0]]
    spine = {"x_min": float(body_pts[:, 0].min()), "x_max": float(body_pts[:, 0].max()),
             "z_mid": float(body_pts[:, 2].mean())}

    def contact_point(a, b):
        return (islands[a]["center"] + islands[b]["center"]) / 2

    return {"debug": debug, "islands": islands, "adj": {0: set(range(1, len(islands)))}, "legs": out_legs,
            "body": [0], "body_core": [0], "antennae": [], "mandibles": [], "others": [], "ground_z": zmin,
            "size": size, "spine": spine, "contact_point": contact_point, "coords": co, "single_mesh": True}
