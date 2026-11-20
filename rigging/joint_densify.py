"""Allzweck-Baustein „Gelenk-Verdichtung“ (Backlog C9): mehr Vertices nur in einem Ring um stark beugende Gelenke.

Problem: Tripo-Low-Poly hat an Gelenken oft lange Dreiecke. Eine lange Kante, deren Enden an verschiedenen Knochen
hängen, kann beim Beugen nur gerade „abkürzen“ oder sich dehnen – die Haut knickt und streckt sich an EINER Kante.
Regel des Nutzers: Dehnung nie durch kleinere Bewegung lösen, sondern am Mesh (mehr Vertices am Gelenk).

Ablauf (wird vom Rig-Skript aufgerufen, Opt-in pro Kreatur über [joint_densify] in der creature.toml):
  1. densify()  NACH dem Skelett, VOR dem Gewichten: Kanten im Ring (Kugel um den Gelenkpunkt = Kopf des genannten
                Knochens) halbieren, bis sie kürzer als `target_edge` sind (höchstens `levels`-mal, höchstens
                `max_extra_tris` zusätzliche Dreiecke, die nächsten Kanten zuerst).
                - neue Vertices liegen GENAU auf der alten Kante (kein Glätten) → Facetten-Look bleibt
                - UVs, Ecken-Normalen, Material und Flat-Flag werden von bmesh mitinterpoliert bzw. übernommen
                - UV-Naht-Duplikate (gleiche Position, getrennte Kanten) werden immer gemeinsam geteilt →
                  die neuen Vertices liegen auf beiden Seiten an derselben Stelle, keine T-Stöße, kein Aufreißen
                - alte Vertices behalten ihre Nummer (neue hängen hinten an); das Rig gewichtet danach alle
                  Vertices ganz normal (seine Abstands-Gewichte liefern an den neuen Stützpunkten Zwischenwerte)
  2. soften()   NACH dem Gewichten, optional (`soft_iterations`, Standard 0 = aus): zusätzliches Glätten der Gewichte
                nur im Ring (zur Mitte hin stärker, am Ringrand 0), nur zwischen Knochen, die der Vertex schon hat, und
                dem Gelenk-Paar (Knochen + Eltern). Max. 4 Einflüsse, UV-Naht-Duplikate identisch. Gemessen an Wolf und
                Raptor (2026-11-20) wurde die Dehnung damit größer → aus; die weichen Übergänge der Rigs reichen.
  3. finish()   Bericht (zusätzliche Tris usw.) + <rig>/joint_densify.json (für rigging/joint_densify_review.py:
                Zuordnung alter Kanten → Kette neuer Vertices, damit die Dehnung vorher/nachher fair verglichen wird).

Ohne [joint_densify] gibt load_cfg() None zurück und das Rig-Skript ruft nichts davon auf → Mesh, Gewichte und Export
bleiben Bit für Bit gleich (Nachweis: scripts/regression.py --deep).

Einbau in ein Rig-Skript (bisher quadruped_rig.py und biped_raptor_rig.py):
    import joint_densify as JD
    JDS = JD.load_cfg(creature_toml)                      # None ohne Abschnitt
    ... Skelett (bones: Name → (Kopf, Schwanz, Eltern)) ...
    if JDS:
        JDS = JD.densify(obj, bones, JDS)                 # danach V, part, MAIN neu: rig_common.arrays(obj)
    ... Gewichte ...
    if JDS:
        JD.soften(obj, JDS)
        report["joint_densify"] = JD.finish(JDS, OUT)
"""
import fnmatch
import json
import pathlib
import tomllib

import bmesh
import numpy as np
from mathutils.kdtree import KDTree

HERE = pathlib.Path(__file__).resolve().parent


def load_cfg(creature_toml):
    """Standardwerte + [joint_densify] der Kreatur, oder None (kein Abschnitt → Baustein aus)."""
    if not creature_toml:
        return None
    ct = tomllib.loads(pathlib.Path(creature_toml).read_text(encoding="utf-8"))
    if "joint_densify" not in ct:
        return None
    cfg = tomllib.loads((HERE / "joint_densify_defaults.toml").read_text(encoding="utf-8"))
    own = dict(ct["joint_densify"])
    cfg["joint"] = own.pop("joint", [])
    cfg.update(own)
    if not cfg["joint"]:
        raise SystemExit("[joint_densify] braucht mindestens einen [[joint_densify.joint]] mit bones = [...]")
    return cfg


def _keys(P):
    return [tuple(k) for k in np.round(P, 5)]


def _joints(bones, cfg, size):
    out = []
    for spec in cfg["joint"]:
        pats = spec["bones"]
        hits = [n for n in bones if any(fnmatch.fnmatchcase(n, p) for p in pats)]
        if not hits:
            raise SystemExit(f"[joint_densify] kein Knochen passt zu {pats}")
        r = float(spec.get("radius", cfg["radius"])) * size
        for n in hits:
            b = bones[n]
            par = b[2] if len(b) > 2 else None
            p, t = np.asarray(b[0], float), np.asarray(b[1], float)
            # Gelenk-Ebene: senkrecht zur mittleren Richtung von Eltern- und Kind-Knochen (dort knickt die Haut)
            d = (t - p) / max(1e-9, np.linalg.norm(t - p))
            if par in bones:
                q = p - np.asarray(bones[par][0], float)
                if np.linalg.norm(q) > 1e-9:
                    d = d + q / np.linalg.norm(q)
            out.append({"bone": n, "parent": par, "p": p, "r": r, "axis": d / max(1e-9, np.linalg.norm(d))})
    return out


def _rel(P, joints):
    """Abstand zum nächsten Gelenk in Ringradien (0 = Gelenkpunkt, 1 = Ringrand) und Nummer dieses Gelenks."""
    R = np.stack([np.linalg.norm(P - j["p"], axis=1) / j["r"] for j in joints], 1)
    return R.min(1), R


def _priority(pa, pb, joints):
    """Rangfolge einer Kante (kleiner = zuerst teilen): Kanten, die die Gelenk-Ebene kreuzen oder ihr nahe liegen,
    vor Kanten, die nur längs des Glieds im Ring liegen. None = Kante liegt in keinem Ring."""
    best = None
    for j in joints:
        if min(np.linalg.norm(pa - j["p"]), np.linalg.norm(pb - j["p"]),
               np.linalg.norm((pa + pb) / 2 - j["p"])) >= j["r"]:
            continue
        sa, sb = float((pa - j["p"]) @ j["axis"]), float((pb - j["p"]) @ j["axis"])
        pr = 0.0 if sa * sb <= 0 else min(abs(sa), abs(sb)) / j["r"]
        best = pr if best is None else min(best, pr)
    return best


def _main_part(bm):
    """Vertices des größten zusammenhängenden Teils (verschweißt über gleiche Position, wie rig_common.arrays)."""
    n = len(bm.verts)
    par = np.arange(n)

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    first = {}
    for i, k in enumerate(_keys(np.array([v.co[:] for v in bm.verts]))):
        j = first.setdefault(k, i)
        if j != i:
            par[find(i)] = find(j)
    for e in bm.edges:
        par[find(e.verts[0].index)] = find(e.verts[1].index)
    root = np.array([find(i) for i in range(n)])
    ids, cnt = np.unique(root, return_counts=True)
    return root == ids[np.argmax(cnt)]


def densify(obj, bones, cfg):
    me = obj.data
    V0 = np.array([v.co[:] for v in me.vertices])
    N0 = len(V0)
    E0 = np.array([e.vertices[:] for e in me.edges])
    size = float((V0.max(0) - V0.min(0)).max())
    joints = _joints(bones, cfg, size)
    target = cfg["target_edge"] * size
    budget = int(cfg["max_extra_tris"])
    tris0 = sum(len(p.vertices) - 2 for p in me.polygons)

    bm = bmesh.new()
    bm.from_mesh(me)
    added, levels, split_total, hit_budget = 0, [], 0, False
    for _ in range(int(cfg["levels"])):
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        P = np.array([v.co[:] for v in bm.verts])
        main = _main_part(bm) if cfg["main_only"] else np.ones(len(P), bool)
        # Kandidaten: lange Kanten des Hauptkörpers, deren Mitte oder ein Ende im Ring liegt
        groups = {}
        for e in bm.edges:
            a, b = e.verts[0].index, e.verts[1].index
            if not (main[a] and main[b]) or e.calc_length() <= target:
                continue
            pr = _priority(P[a], P[b], joints)
            if pr is None:
                continue
            k = tuple(sorted(_keys(P[[a, b]])))          # UV-Naht-Duplikate teilen dieselbe Positions-Kante
            g = groups.setdefault(k, [pr, 0, []])
            g[0] = min(g[0], pr)
            g[1] += len(e.link_faces)                     # Halbieren einer Kante = +1 Dreieck je anliegender Fläche
            g[2].append(e)
        sel = []
        for prio, cost, es in sorted(groups.values(), key=lambda g: g[0]):   # an der Gelenk-Ebene zuerst
            if added + cost > budget:
                hit_budget = True
                continue
            added += cost
            sel += es
        if not sel:
            break
        nv = len(bm.verts)
        bmesh.ops.subdivide_edges(bm, edges=sel, cuts=1, use_grid_fill=True, smooth=0.0)
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        ngon = [f for f in bm.faces if len(f.verts) > 3 and any(v.index >= nv for v in f.verts)]
        if ngon:
            bmesh.ops.triangulate(bm, faces=ngon, quad_method="BEAUTY", ngon_method="BEAUTY")
        split_total += len(sel)
        levels.append(len(sel))
    bm.to_mesh(me)
    bm.free()
    me.update()

    V = np.array([v.co[:] for v in me.vertices])
    if not np.allclose(V[:N0], V0, atol=1e-9):
        raise SystemExit("joint_densify: alte Vertices haben sich verschoben/umnummeriert – Abbruch")
    tris1 = sum(len(p.vertices) - 2 for p in me.polygons)

    # Ketten: alte Kante (a, b) → alle neuen Vertices, die auf ihr liegen (sortiert), für den fairen Dehnungsvergleich
    chains = {}
    if len(V) > N0:
        kd = KDTree(len(V) - N0)
        for i in range(N0, len(V)):
            kd.insert(V[i], i)
        kd.balance()
        have = {tuple(sorted(e.vertices[:])) for e in me.edges}
        for ei, (a, b) in enumerate(E0):
            if (min(a, b), max(a, b)) in have:
                continue
            pa, pb = V[a], V[b]
            ab = pb - pa
            L2 = float(ab @ ab)
            if L2 < 1e-16:
                continue
            on = {}
            for co, i, _ in kd.find_range((pa + pb) / 2, 0.5 * np.sqrt(L2) * 1.001):
                t = float((np.asarray(co) - pa) @ ab / L2)
                if 1e-6 < t < 1 - 1e-6 and np.linalg.norm(np.asarray(co) - (pa + t * ab)) < 1e-6 * size:
                    on.setdefault(round(t, 6), i)
            if on:
                chains[int(ei)] = [int(a)] + [on[t] for t in sorted(on)] + [int(b)]

    rep = {"joints": [j["bone"] for j in joints], "radius_m": sorted({round(j["r"], 4) for j in joints}),
           "target_edge_m": round(target, 4), "levels": levels, "edges_split": split_total,
           "verts_before": N0, "verts_after": len(V), "tris_before": tris0, "tris_after": tris1,
           "extra_tris": tris1 - tris0, "max_extra_tris": budget, "budget_reached": hit_budget}
    print("RIG_JOINT_DENSIFY", json.dumps(rep, ensure_ascii=False))
    return {"cfg": cfg, "joints": joints, "size": size, "N0": N0, "E0": E0, "chains": chains, "report": rep}


def soften(obj, state):
    cfg = state["cfg"]
    n_it, k = int(cfg["soft_iterations"]), float(cfg["soft_factor"])
    if n_it <= 0:
        state["report"]["soft_vertices"] = 0
        return
    me = obj.data
    V = np.array([v.co[:] for v in me.vertices])
    N = len(V)
    names = [g.name for g in obj.vertex_groups]
    G = len(names)
    W = np.zeros((N, G))
    for v in me.vertices:
        for g in v.groups:
            W[v.index, g.group] = g.weight
    rel, R = _rel(V, state["joints"])
    t = np.clip((1.0 - rel) / 0.5, 0.0, 1.0)            # innere Ringhälfte voll, äußere Hälfte weich auf 0
    f = t * t * (3 - 2 * t)
    act = f > 0
    # erlaubte Knochen je Vertex: was er schon hat + Gelenk-Paar (Knochen, Eltern) jedes Rings, in dem er liegt
    gi = {n: i for i, n in enumerate(names)}
    allow = W > 1e-6
    for jn, j in enumerate(state["joints"]):
        inside = R[:, jn] < 1.0
        for n in (j["bone"], j["parent"]):
            if n in gi:
                allow[inside, gi[n]] = True
    E = np.array([e.vertices[:] for e in me.edges])
    groups = {}
    for i, kk in enumerate(_keys(V)):
        groups.setdefault(kk, []).append(i)
    weld = [g for g in groups.values() if len(g) > 1]
    if weld:
        E = np.vstack([E] + [np.array([[g[0], x] for x in g[1:]]) for g in weld])
    W0 = W.copy()
    for _ in range(n_it):
        acc, cnt = np.zeros_like(W), np.zeros(N)
        np.add.at(acc, E[:, 0], W[E[:, 1]])
        np.add.at(acc, E[:, 1], W[E[:, 0]])
        np.add.at(cnt, E[:, 0], 1)
        np.add.at(cnt, E[:, 1], 1)
        sm = np.where(cnt[:, None] > 0, acc / np.maximum(cnt, 1)[:, None], W)
        kf = (k * f)[:, None]
        W = np.where(act[:, None], (1 - kf) * W + kf * sm, W)
        W = np.where(allow | ~act[:, None], W, 0.0)
        W /= np.maximum(W.sum(1, keepdims=True), 1e-12)
    for g in weld:
        W[g] = W[g].mean(0)
    changed = np.where(np.abs(W - W0).max(1) > 1e-6)[0]
    for i in changed:
        top = np.argsort(-W[i])[:4]
        ws = W[i, top] / W[i, top].sum()
        for g in list(me.vertices[i].groups):
            obj.vertex_groups[g.group].remove([int(i)])
        for j, w in zip(top, ws):
            if w > 1e-3:
                obj.vertex_groups[names[j]].add([int(i)], float(w), "REPLACE")
    state["report"]["soft_vertices"] = int(len(changed))
    print(f"RIG_JOINT_DENSIFY weiche Gewichte: {len(changed)} Vertices im Ring, {n_it} Runden")


def finish(state, out_dir):
    data = {"base_verts": state["N0"], "base_edges": state["E0"].tolist(),
            "chains": {str(k): v for k, v in state["chains"].items()}, "report": state["report"]}
    (pathlib.Path(out_dir) / "joint_densify.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    return state["report"]
