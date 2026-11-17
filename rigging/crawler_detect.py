"""Erkennung der Anatomie eines Krabbler-Meshes (Spinne/Insekt), das aus vielen Einzelteilen (Inseln) besteht.

Konvention nach dem Import: oben = +Z, Kopf = +X (Tripo-GLB). Wird von crawler_rig.py importiert.

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
