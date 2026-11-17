"""Modellprüfung: rohes Tripo-Modell (vor dem Rig) vermessen und auffällige Stellen melden.

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ AUTOMATISCHE MESSUNG = NUR FRÜHWARNSYSTEM. Eine individuelle Sichtprüfung des Modells (Bilder ansehen,    ║
║ gegen Concept und Referenzbilder vergleichen) durch den Agenten ist IMMER zusätzlich notwendig.            ║
║ Ein Ergebnis ohne Befund ist KEINE Freigabe – es heißt nur, dass diese Messungen nichts gefunden haben.   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════╝

Aufruf:
  python scripts/model_check.py creatures/<name>         → creatures/<name>/review/model_check.json + model_check.png
  python scripts/model_check.py --all                    → alle Kreaturen mit raw/generate_model.glb + Übersichtstabelle

Messungen (erwartete Werte aus creature.toml: [motion] style → Skelett; Schwellen in scripts/model_check.toml,
pro Kreatur überschreibbar unter [model_check], einzelne Befunde mit Begründung freigebbar unter [model_check.freigabe]):
  offene_flaechen  einseitige Flächen (Strahl nach hinten trifft nichts) – Bereiche, Flächen, Lage   (Needle Wasp)
  fussgruppen      Zahl der Fuß-Gruppen am Boden gegen die Beinzahl des Skeletts, Kontakte in der Mitte (Skorpion)
  fussbreite       seitlicher Abstand vorderes/hinteres Fußpaar, Verhältnis hinten/vorne              (Hollow Stag)
  haengende_teile  Teile unter der Bauchlinie zwischen den Beinen nahe der Körpermitte                (Dune Raptor)
  mittellinie      seitlicher Versatz der Körpermitte, bei Schlangen auch Verdrehung des Querschnitts (Eel Stalker)
  symmetrie        Anteil Vertices ohne Spiegel-Partner (links/rechts)
  boden            Schwerpunkt über der Standfläche der Füße
  dreiecke         gegen [tripo] face_limit
  mesh_teile       Anzahl zusammenhängender Teile, lose schwebende Teile
Blender-Teil: rigging/model_check_blender.py (Geometrie + Strahltest exportieren, Ansichten rendern).
"""
import argparse
import datetime
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import tomllib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from common import deep_merge, load_toml  # noqa: E402

BLENDER = r"D:\Blender\blender.exe"
BLENDER_PART = ROOT / "rigging" / "model_check_blender.py"

HINWEIS = ("Automatische Messung = nur Frühwarnsystem. Eine individuelle Sichtprüfung des Modells (Bilder ansehen, "
           "gegen Concept und Referenzbilder vergleichen) durch den Agenten ist IMMER zusätzlich notwendig.")
ERGEBNIS_LEER = "keine automatischen Auffälligkeiten – Sichtprüfung trotzdem erforderlich (keine Freigabe)"

TITEL = {
    "offene_flaechen": "Einseitige/offene Flächen",
    "fussgruppen": "Fuß-Gruppen am Boden",
    "fussbreite": "Fußabstand hinten/vorne",
    "haengende_teile": "Hängende Teile zwischen den Beinen",
    "mittellinie": "Krümmung/Verdrehung der Mittellinie",
    "symmetrie": "Symmetrie links/rechts",
    "boden": "Schwerpunkt über den Füßen",
    "dreiecke": "Dreiecke",
    "mesh_teile": "Mesh-Teile",
}


# ----------------------------------------------------------------------------------------------- Konfiguration
def resolve_config(creature_dir):
    c = pathlib.Path(creature_dir).resolve()
    ct = load_toml(c / "creature.toml")
    full = deep_merge(load_toml(ROOT / "pipeline.toml"), ct)
    style = ct.get("motion", {}).get("style", "")
    skel, _, muster = style.partition("/")
    base = load_toml(ROOT / "scripts" / "model_check.toml")
    skel_tab = base.pop("skelett", {})
    cfg = deep_merge(base, skel_tab.get(skel, {}))
    if skel == "hexapod":
        slots = ct.get("motion", {}).get("legs", {}).get("walking_slots")
        if slots:
            cfg["fussgruppen"]["erwartet"] = 2 * len(slots)
    own = ct.get("model_check", {})
    freigabe = own.get("freigabe", {})
    cfg = deep_merge(cfg, {k: v for k, v in own.items() if k != "freigabe"})
    facing = own.get("facing") or ct.get("flyer", {}).get("facing") or ct.get("floater", {}).get("facing") or "+x"
    bad = {k: v for k, v in freigabe.items() if not (isinstance(v, str) and v.strip())}
    if bad:
        raise SystemExit(f"[model_check.freigabe] braucht eine Begründung als Text, nicht {bad} – z. B. "
                         f'haengende_teile = "Tentakel hängen gewollt unter dem Körper"')
    unknown = set(freigabe) - set(TITEL)
    if unknown:
        raise SystemExit(f"[model_check.freigabe] unbekannte Prüfung(en) {sorted(unknown)}. Erlaubt: {sorted(TITEL)}")
    meta = {"kreatur": c.name, "skelett": skel or "?", "muster": muster or "?", "facing": facing,
            "face_limit": full.get("tripo", {}).get("face_limit")}
    return cfg, freigabe, meta


# ----------------------------------------------------------------------------------------------- Geometrie-Helfer
class UnionFind:
    def __init__(self, n):
        self.p = np.arange(n)

    def find(self, i):
        p = self.p
        while p[i] != i:
            p[i] = p[p[i]]
            i = p[i]
        return i

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)

    def labels(self):
        return np.array([self.find(i) for i in range(len(self.p))])


def close_pairs(P, eps, chunk=400):
    """Indexpaare (i<j) mit Abstand < eps (ohne scipy, blockweise)."""
    out = []
    for s in range(0, len(P), chunk):
        d = np.linalg.norm(P[s:s + chunk, None] - P[None], axis=2)
        i, j = np.where(d < eps)
        i = i + s
        keep = i < j
        out.append(np.c_[i[keep], j[keep]])
    return np.concatenate(out) if out else np.zeros((0, 2), int)


def nearest_dist(A, B, chunk=300):
    out = np.empty(len(A))
    for s in range(0, len(A), chunk):
        out[s:s + chunk] = np.linalg.norm(A[s:s + chunk, None] - B[None], axis=2).min(1)
    return out


def convex_hull(P):
    P = sorted(set(map(tuple, np.round(P, 6))))
    if len(P) < 3:
        return np.array(P)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return np.array(lo[:-1] + hi[:-1])


def dist_outside(hull, q):
    """0 wenn q im (konvexen, gegen den Uhrzeigersinn) Polygon liegt, sonst Abstand zum Rand."""
    def seg(a, b):
        ab = b - a
        t = np.clip((q - a) @ ab / max(ab @ ab, 1e-12), 0, 1)
        return np.linalg.norm(q - (a + t * ab))
    if len(hull) == 1:
        return float(np.linalg.norm(q - hull[0]))
    if len(hull) == 2:
        return float(seg(hull[0], hull[1]))
    inside = all((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= 0
                 for a, b in zip(hull, np.roll(hull, -1, 0)))
    return 0.0 if inside else float(min(seg(a, b) for a, b in zip(hull, np.roll(hull, -1, 0))))


# ----------------------------------------------------------------------------------------------- Messungen
class Model:
    def __init__(self, npz):
        d = np.load(npz)
        self.V = d["V"]
        self.tris, self.tri_poly, self.edges = d["tris"], d["tri_poly"], d["edges"]
        self.part, self.poly_open, self.back_dist = d["part"], d["poly_open"], d["back_dist"]
        self.n_polys, self.n_objects, self.n_materials = int(d["n_polys"]), int(d["n_objects"]), int(d["n_materials"])
        V = self.V
        self.mn, self.mx = V.min(0), V.max(0)
        self.ext = self.mx - self.mn
        self.size = float(self.ext.max())
        self.H, self.L = float(self.ext[2]), float(self.ext[0])
        self.ground = float(self.mn[2])
        self.mid = float((self.mn[1] + self.mx[1]) / 2)
        _, wid = np.unique(np.round(V, 5), axis=0, return_inverse=True)
        self.wid = wid.ravel()
        a = V[self.tris]
        self.tri_area = 0.5 * np.linalg.norm(np.cross(a[:, 1] - a[:, 0], a[:, 2] - a[:, 0]), axis=1)
        self.tri_center = a.mean(1)
        self.poly_area = np.bincount(self.tri_poly, self.tri_area, minlength=self.n_polys)

    def polys_of_verts(self, vmask):
        """Flächen, die mindestens einen markierten Vertex haben."""
        return sorted(set(self.tri_poly[vmask[self.tris].any(1)].tolist()))

    def r3(self, p):
        return [round(float(x), 3) for x in p]


def m_open_faces(M, c):
    op = M.poly_open
    tri_open = op[M.tri_poly]
    uf = UnionFind(M.n_polys)
    edge_owner = {}
    for t, p in zip(M.tris[tri_open], M.tri_poly[tri_open]):
        for k in range(3):
            e = tuple(sorted((M.wid[t[k]], M.wid[t[(k + 1) % 3]])))
            if e in edge_owner:
                uf.union(int(p), edge_owner[e])
            else:
                edge_owner[e] = int(p)
    regs = {}
    for p in np.where(op)[0]:
        regs.setdefault(uf.find(int(p)), []).append(int(p))
    min_a = c["min_bereich"] * M.size ** 2
    poly_center = np.zeros((M.n_polys, 3))
    np.add.at(poly_center, M.tri_poly, M.tri_center * M.tri_area[:, None])
    poly_center /= np.maximum(M.poly_area, 1e-12)[:, None]
    big = []
    for fs in regs.values():
        a = M.poly_area[fs].sum()
        if a >= min_a:
            ctr = (poly_center[fs] * M.poly_area[fs, None]).sum(0) / a
            bd = np.minimum(M.back_dist[fs], 9.0)
            big.append({"flaechen": len(fs), "flaeche_anteil": round(float(a / M.size ** 2), 4),
                        "mitte": M.r3(ctr), "lage": describe(M, ctr),
                        "abstand_dahinter_median": None if np.median(bd) >= 9 else round(float(np.median(bd)), 3),
                        "warnung": bool(a >= c["warn_bereich"] * M.size ** 2), "_polys": fs})
    big.sort(key=lambda r: -r["flaeche_anteil"])
    warn_regs = [r for r in big if r["warnung"]]
    small = [r for r in big if not r["warnung"]]
    n_warn = sum(r["flaechen"] for r in warn_regs)
    warn = len(warn_regs) > c["max_bereiche"]
    text = (f"{len(warn_regs)} Bereich(e) mit {n_warn} einseitigen Flächen ({', '.join(r['lage'] for r in warn_regs[:4])})"
            if warn_regs else "keine großen einseitigen Bereiche")
    if small:
        text += (f"; {len(small)} kleine(r) Bereich(e) unter {c['warn_bereich']} ({sum(r['flaechen'] for r in small)} Fl., "
                 f"{', '.join(r['lage'] for r in small[:3])}) – nur Info, ansehen")
    text += f"; gesamt {int(op.sum())} Flächen mit freier Rückseite inkl. Splitter"
    return {"warn": warn, "text": text,
            "werte": {"bereiche_warnung": len(warn_regs), "flaechen_warnung": n_warn,
                      "bereiche_klein": len(small), "flaechen_gesamt_inkl_splitter": int(op.sum()),
                      "liste": [{k: v for k, v in r.items() if k != "_polys"} for r in big]},
            "_polys": [p for r in warn_regs for p in r["_polys"]],
            "_marks": [{"typ": "punkt", "p": r["mitte"], "label": f"{r['flaechen']} F."} for r in warn_regs]}


def describe(M, p):
    """Grobe Lage in Worten (vorn/hinten, links/rechts, oben/unten)."""
    rel = (np.asarray(p) - M.mn) / np.maximum(M.ext, 1e-9)
    x = "vorn" if rel[0] > 0.66 else "hinten" if rel[0] < 0.33 else "Mitte"
    y = "links" if p[1] > M.mid + 0.08 * M.ext[1] else "rechts" if p[1] < M.mid - 0.08 * M.ext[1] else "mittig"
    z = "oben" if rel[2] > 0.66 else "unten" if rel[2] < 0.33 else "halbhoch"
    return f"{x}/{y}/{z}"


def foot_groups(M, c):
    V = M.V
    S = np.where(V[:, 2] < M.ground + c["bein_band"] * M.H)[0]
    if len(S) == 0:
        return [], {}
    idx = -np.ones(len(V), int)
    idx[S] = np.arange(len(S))
    uf = UnionFind(len(S))
    e = M.edges[(idx[M.edges[:, 0]] >= 0) & (idx[M.edges[:, 1]] >= 0)]
    for a, b in idx[e]:
        uf.union(a, b)
    for a, b in close_pairs(V[S], c["verschmelzen"] * M.size):
        uf.union(a, b)
    lab = uf.labels()
    is_ground = V[S, 2] < M.ground + c["boden_band"] * M.H
    groups = []
    for l in np.unique(lab[is_ground]):
        g = S[(lab == l) & is_ground]
        q = V[g]
        y = float(q[:, 1].mean())
        side = "links" if y > M.mid + c["mitte"] * M.size else "rechts" if y < M.mid - c["mitte"] * M.size else "mitte"
        groups.append({"x": float(q[:, 0].mean()), "y": y, "z": float(q[:, 2].min()), "seite": side,
                       "vertices": len(g), "_verts": g, "_leg": S[lab == l]})
    groups.sort(key=lambda g: -g["x"])
    for i, g in enumerate(groups, 1):
        g["nr"] = i
    # Paare: links ↔ gespiegelt nächstes rechts
    L = [g for g in groups if g["seite"] == "links"]
    R = [g for g in groups if g["seite"] == "rechts"]
    cand = sorted((np.hypot(a["x"] - b["x"], (a["y"] - M.mid) + (b["y"] - M.mid)), ia, ib)
                  for ia, a in enumerate(L) for ib, b in enumerate(R))
    used_l, used_r, pairs = set(), set(), []
    for d, ia, ib in cand:
        if ia in used_l or ib in used_r or d > 0.1 * M.size:
            continue
        used_l.add(ia)
        used_r.add(ib)
        a, b = L[ia], R[ib]
        pairs.append({"links": a["nr"], "rechts": b["nr"], "x": (a["x"] + b["x"]) / 2, "breite": a["y"] - b["y"]})
    pairs.sort(key=lambda p: -p["x"])
    return groups, {"paare": pairs, "ohne_partner": [g["nr"] for i, g in enumerate(L) if i not in used_l]
                    + [g["nr"] for i, g in enumerate(R) if i not in used_r],
                    "mitte": [g["nr"] for g in groups if g["seite"] == "mitte"]}


def m_feet(M, c, groups, info):
    exp = c["erwartet"]
    lo, hi = (exp, exp) if isinstance(exp, int) else (int(exp[0]), int(exp[1]))
    n = len(groups)
    probs = []
    if hi > 0 and not lo <= n <= hi:
        probs.append(f"{n} statt {lo if lo == hi else f'{lo}–{hi}'} erwartet")
    if hi > 0 and info.get("mitte"):
        probs.append(f"Bodenkontakt in der Körpermitte (Nr. {', '.join(map(str, info['mitte']))})")
    if hi > 0 and info.get("ohne_partner"):
        probs.append(f"ohne Gegenstück auf der anderen Seite (Nr. {', '.join(map(str, info['ohne_partner']))})")
    werte = {"gefunden": n, "erwartet": exp, "paare": len(info.get("paare", [])),
             "mitte": info.get("mitte", []), "ohne_partner": info.get("ohne_partner", []),
             "gruppen": [{"nr": g["nr"], "x": round(g["x"], 3), "y": round(g["y"], 3), "seite": g["seite"],
                          "vertices": g["vertices"]} for g in groups]}
    text = f"{n} Bodenkontakt-Gruppe(n), {len(info.get('paare', []))} Paar(e)"
    if hi <= 0:
        return {"warn": False, "info_only": True, "text": text + " (keine Erwartung für dieses Skelett)", "werte": werte}
    bad_nr = set(info.get("mitte", [])) | set(info.get("ohne_partner", []))
    if not lo <= n <= hi:
        bad_nr = {g["nr"] for g in groups}
    return {"warn": bool(probs), "text": text + (": " + "; ".join(probs) if probs else f" – passt zu {exp}"),
            "werte": werte, "_bad_nr": sorted(bad_nr)}


def m_width(M, c, info, groups):
    pairs = info.get("paare", [])
    if len(pairs) < 2:
        return {"skip": f"nur {len(pairs)} Fußpaar(e) – kein Vergleich vorn/hinten möglich"}
    front, hind = pairs[0], pairs[-1]
    ratio = hind["breite"] / max(front["breite"], 1e-9)
    warn = not c["min_verhaeltnis"] <= ratio <= c["max_verhaeltnis"]
    byn = {g["nr"]: g for g in groups}
    lines = [{"typ": "linie", "a": [byn[p["links"]]["x"], byn[p["links"]]["y"], M.ground],
              "b": [byn[p["rechts"]]["x"], byn[p["rechts"]]["y"], M.ground], "label": f"{name} {p['breite']:.2f}"}
             for p, name in ((front, "vorn"), (hind, "hinten"))]
    return {"warn": warn, "text": f"vorn {front['breite']:.3f}, hinten {hind['breite']:.3f} → hinten/vorne {ratio:.2f}× "
                                  f"(erlaubt {c['min_verhaeltnis']}–{c['max_verhaeltnis']})",
            "werte": {"vorn": round(front["breite"], 4), "hinten": round(hind["breite"], 4), "verhaeltnis": round(ratio, 2)},
            "_marks": lines}


def m_hanging(M, c, info, groups):
    pairs = info.get("paare", [])
    if not pairs:
        return {"skip": "kein Fußpaar gefunden – Bauchbereich unbekannt"}
    V = M.V
    xs = [p["x"] for p in pairs]
    if max(xs) - min(xs) < 0.1 * M.L:
        x0, x1 = min(xs) - c["zweibeiner_rand"] * M.L, max(xs) + c["zweibeiner_rand"] * M.L
    else:
        x0, x1 = min(xs), max(xs)
    hw = c["korridor"] * min(p["breite"] for p in pairs) / 2
    m = (V[:, 0] >= x0) & (V[:, 0] <= x1) & (np.abs(V[:, 1] - M.mid) < hw)
    for g in groups:                       # Füße/Zehen/Krallen selbst zählen nicht – Kontakte in der Mitte schon
        if g["seite"] != "mitte":
            m[g["_leg"]] = False
    if m.sum() < 10:
        return {"skip": "zu wenige Vertices im Prüfstreifen"}
    zrel = (V[:, 2] - M.ground) / M.H
    bins = np.linspace(x0, x1, int(c["abschnitte"]) + 1)
    lows = [zrel[m & (V[:, 0] >= a) & (V[:, 0] < b)].min() for a, b in zip(bins[:-1], bins[1:])
            if (m & (V[:, 0] >= a) & (V[:, 0] < b)).any()]
    belly = float(np.median(lows))
    lowest = float(zrel[m].min())
    drop = belly - lowest
    hang = m & (zrel < belly - c["max_absenkung"])
    warn = bool(hang.any())
    marks = [{"typ": "bauchlinie", "x0": x0, "x1": x1, "z": M.ground + belly * M.H, "hw": hw, "y": M.mid}]
    if warn:
        p = V[hang][np.argmin(zrel[hang])]
        marks.append({"typ": "punkt", "p": M.r3(p), "label": f"hängt {drop * 100:.0f}% H"})
    return {"warn": warn,
            "text": (f"Teil hängt {drop:.2f}×Höhe unter die Bauchlinie (Bauch {belly:.2f}, tiefster Punkt {lowest:.2f} "
                     f"über Boden, {int(hang.sum())} Vertices)" if warn else
                     f"nichts hängt (tiefster Punkt {drop:.2f}×Höhe unter Bauchlinie {belly:.2f}, erlaubt {c['max_absenkung']})"),
            "werte": {"bauchlinie_hoehe": round(belly, 3), "tiefster_punkt_hoehe": round(lowest, 3),
                      "absenkung": round(drop, 3), "vertices_haengend": int(hang.sum()),
                      "streifen_x": [round(x0, 3), round(x1, 3)], "streifen_halbbreite": round(hw, 3)},
            "_polys": M.polys_of_verts(hang), "_marks": marks}


def centerline(M, n, minv=12):
    V = M.V
    bins = np.linspace(M.mn[0], M.mx[0], int(n) + 1)
    C = []
    for a, b in zip(bins[:-1], bins[1:]):
        q = V[(V[:, 0] >= a) & (V[:, 0] < b)]
        if len(q) >= minv:
            C.append([(a + b) / 2, (q[:, 1].min() + q[:, 1].max()) / 2, (q[:, 2].min() + q[:, 2].max()) / 2])
    return np.array(C)


def m_midline(M, c):
    C = centerline(M, c["abschnitte"])
    if len(C) < 3:
        return {"skip": "zu wenige Querschnitte"}
    off = np.abs(C[:, 1] - M.mid) / M.L
    warn = bool(off.max() > c["max_versatz"])
    werte = {"max_versatz": round(float(off.max()), 3), "querschnitte": len(C)}
    text = f"Mittellinie seitlich max. {off.max():.3f}×Länge versetzt (erlaubt {c['max_versatz']})"
    if c["drehung_pruefen"]:
        rolls = []
        for i in range(len(C)):
            if C[i, 0] > M.mx[0] - c["kopf_auslassen"] * M.L:
                continue
            t = C[min(i + 1, len(C) - 1)] - C[max(i - 1, 0)]
            t /= np.linalg.norm(t)
            q = M.V[np.abs((M.V - C[i]) @ t) < M.L / c["abschnitte"]] - C[i]
            if len(q) < 12:
                continue
            side = np.cross([0, 0, 1], t)
            side /= np.linalg.norm(side)
            up = np.cross(t, side)
            w, vec = np.linalg.eigh(np.cov(np.c_[q @ side, q @ up].T))
            if np.sqrt(w[1] / max(w[0], 1e-12)) < 1.2:          # fast rund → Drehung nicht bestimmbar
                continue
            ang = (np.degrees(np.arctan2(vec[0, 1], vec[1, 1])) + 90) % 180 - 90
            rolls.append(float(ang))
        if rolls:
            rmax = float(np.max(np.abs(rolls)))
            werte.update({"max_drehung_grad": round(rmax, 1), "drehung_spanne_grad": round(max(rolls) - min(rolls), 1)})
            text += f"; Querschnitt bis {rmax:.0f}° gedreht (Spanne {max(rolls) - min(rolls):.0f}°, erlaubt {c['max_drehung']}°)"
            warn = warn or rmax > c["max_drehung"]
    col = "rot" if warn else "ok"
    return {"warn": warn, "text": text, "werte": werte,
            "_marks": [{"typ": "mittellinie", "pts": C.tolist(), "mid": M.mid, "farbe": col}]}


def m_symmetry(M, c):
    Mi = M.V.copy()
    Mi[:, 1] = 2 * M.mid - Mi[:, 1]
    d = nearest_dist(Mi, M.V) / M.size
    bad = d > c["toleranz"]
    frac = float(bad.mean())
    warn = frac > c["max_anteil"]
    return {"warn": warn, "text": f"{frac * 100:.1f} % der Vertices ohne Spiegel-Partner (erlaubt {c['max_anteil'] * 100:.0f} %)",
            "werte": {"anteil_unsymmetrisch": round(frac, 3)}, "_polys": M.polys_of_verts(bad) if warn else []}


def m_ground(M, c, groups):
    w = M.tri_area
    com = (M.tri_center * w[:, None]).sum(0) / w.sum()
    if not groups:
        return {"warn": True, "text": "keine Füße am Boden gefunden", "werte": {"schwerpunkt": M.r3(com)}}
    pts = np.concatenate([M.V[g["_verts"], :2] for g in groups])
    hull = convex_hull(pts)
    out = dist_outside(hull, com[:2]) / M.L
    warn = out > c["rand"]
    return {"warn": warn,
            "text": ("Schwerpunkt liegt über der Standfläche" if out == 0 else
                     f"Schwerpunkt {out:.3f}×Länge außerhalb der Standfläche (erlaubt {c['rand']})"),
            "werte": {"schwerpunkt": M.r3(com), "ausserhalb": round(out, 3), "tiefster_punkt_z": round(M.ground, 3)},
            "_marks": [{"typ": "standflaeche", "hull": hull.tolist(), "z": M.ground, "com": com.tolist(),
                        "farbe": "rot" if warn else "ok"}]}


def m_tris(M, c, face_limit):
    n = len(M.tris)
    if not face_limit:
        return {"warn": False, "info_only": True, "text": f"{n} Dreiecke (kein face_limit bekannt)", "werte": {"dreiecke": n}}
    warn = n > c["max_faktor"] * face_limit
    return {"warn": warn, "text": f"{n} Dreiecke bei face_limit {face_limit} ({n / face_limit:.2f}×, erlaubt {c['max_faktor']}×)",
            "werte": {"dreiecke": n, "face_limit": face_limit}}


def m_parts(M, c):
    ids, counts = np.unique(M.part, return_counts=True)
    main = ids[np.argmax(counts)]
    loose = []
    for p, n in zip(ids, counts):
        if p == main:
            continue
        mine = M.part == p
        d = nearest_dist(M.V[mine], M.V[~mine]).min() / M.size
        if d > c["lose_abstand"]:
            loose.append({"vertices": int(n), "abstand": round(float(d), 3), "mitte": M.r3(M.V[mine].mean(0)),
                          "_mask": mine})
    vm = np.zeros(len(M.V), bool)
    for lp in loose:
        vm |= lp["_mask"]
    return {"warn": bool(loose),
            "text": f"{len(ids)} zusammenhängende Teile, {M.n_objects} Mesh-Objekt(e), {M.n_materials} Material(ien)"
                    + (f"; {len(loose)} lose schwebende(s) Teil(e)" if loose else ""),
            "werte": {"teile": int(len(ids)), "mesh_objekte": M.n_objects, "materialien": M.n_materials,
                      "lose": [{k: v for k, v in lp.items() if k != "_mask"} for lp in loose]},
            "_polys": M.polys_of_verts(vm)}


def analyse(M, cfg, meta):
    res = {}

    def run(key, fn, *a):
        if not cfg[key].get("aktiv", True):
            res[key] = {"skip": f"für Skelett '{meta['skelett']}' nicht vorgesehen"}
            return
        res[key] = fn(M, cfg[key], *a)

    run("offene_flaechen", m_open_faces)
    groups, info = foot_groups(M, cfg["fussgruppen"])
    run("fussgruppen", m_feet, groups, info)
    run("fussbreite", m_width, info, groups)
    run("haengende_teile", m_hanging, info, groups)
    run("mittellinie", m_midline)
    run("symmetrie", m_symmetry)
    run("boden", m_ground, groups)
    run("dreiecke", m_tris, meta["face_limit"])
    run("mesh_teile", m_parts)
    return res, groups


# ----------------------------------------------------------------------------------------------- Bild
FARBE = {"rot": (230, 20, 20), "orange": (255, 140, 0), "ok": (40, 200, 90), "info": (90, 170, 255),
         "gelb": (255, 220, 40), "weiss": (255, 255, 255)}


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def label(dr, xy, txt, col, f):
    """Text mit dunklem Hintergrund (lesbar auf jedem Modell)."""
    x, y = xy
    dr.rectangle([x - 2, y - 1, x + dr.textlength(txt, font=f) + 2, y + 17], fill=(0, 0, 0))
    dr.text((x, y), txt, fill=col, font=f)


def project(view, p):
    c, r, u = (np.asarray(view[k]) for k in ("center", "right", "up"))
    s, res = view["ortho_scale"], view["res"]
    d = np.asarray(p, float) - c
    return (res / 2 + d @ r / s * res, res / 2 - d @ u / s * res)


def compose(outdir, views, befunde, groups, meta, M, out_png):
    order = ["vorn", "seite", "oben", "unten"]
    res = views["vorn"]["res"]
    tiles = {}
    for name in order:
        im = Image.open(outdir / f"view_{name}.png").convert("RGB")
        dr = ImageDraw.Draw(im)
        vw = views[name]
        f = font(15)

        def P(p):
            return project(vw, p)

        def status_col(key):
            b = befunde.get(key, {})
            return FARBE["orange"] if b.get("status") == "freigegeben" else FARBE["rot"] if b.get("status") == "WARNUNG" else FARBE["ok"]

        # Boden
        if name in ("vorn", "seite"):
            y = P([M.mn[0], M.mn[1], M.ground])[1]
            dr.line([(0, y), (res, y)], fill=(200, 200, 200), width=1)
        # Fuß-Gruppen
        fb = befunde.get("fussgruppen", {})
        bad = set(fb.get("_bad_nr", []))
        if groups and name in ("unten", "vorn", "seite"):
            for g in groups:
                x, y = P([g["x"], g["y"], g["z"]])
                col = (FARBE["orange"] if fb.get("status") == "freigegeben" else FARBE["rot"]) if g["nr"] in bad else FARBE["ok"]
                if fb.get("status") in ("info", "nicht geprüft"):
                    col = FARBE["info"]
                dr.ellipse([x - 9, y - 9, x + 9, y + 9], outline=col, width=3)
                if name == "unten":
                    label(dr, (x + 11, y - 8), str(g["nr"]), col, f)
        for key, b in befunde.items():
            for mk in b.get("_marks", []):
                col = status_col(key)
                t = mk["typ"]
                if t == "punkt" and b.get("status") in ("WARNUNG", "freigegeben"):
                    x, y = P(mk["p"])
                    dr.ellipse([x - 16, y - 16, x + 16, y + 16], outline=col, width=3)
                    if name in ("seite", "unten"):
                        label(dr, (x + 18, y - 8), mk["label"], col, f)
                elif t == "linie" and name == "unten":
                    a, bb = P(mk["a"]), P(mk["b"])
                    dr.line([a, bb], fill=col, width=3)
                    top = a if a[1] < bb[1] else bb
                    label(dr, (top[0] - 30, top[1] - 34), mk["label"], col, f)
                elif t == "bauchlinie" and name in ("seite", "vorn"):
                    if name == "seite":
                        a, bb = P([mk["x0"], mk["y"], mk["z"]]), P([mk["x1"], mk["y"], mk["z"]])
                    else:
                        a, bb = P([mk["x1"], mk["y"] - mk["hw"], mk["z"]]), P([mk["x1"], mk["y"] + mk["hw"], mk["z"]])
                    dr.line([a, bb], fill=FARBE["gelb"], width=2)
                    if name == "seite":
                        label(dr, (bb[0] + 4, bb[1] - 8), "Bauchlinie", FARBE["gelb"], f)
                elif t == "bauchlinie" and name == "unten":
                    a = P([mk["x0"], mk["y"] - mk["hw"], M.ground])
                    bb = P([mk["x1"], mk["y"] + mk["hw"], M.ground])
                    dr.rectangle([min(a[0], bb[0]), min(a[1], bb[1]), max(a[0], bb[0]), max(a[1], bb[1])],
                                 outline=FARBE["gelb"], width=1)
                elif t == "mittellinie" and name in ("oben", "unten"):
                    pts = [P(p) for p in mk["pts"]]
                    a = P([M.mn[0], mk["mid"], 0])
                    bb = P([M.mx[0], mk["mid"], 0])
                    dr.line([(a[0], a[1]), (bb[0], bb[1])], fill=(200, 200, 200), width=1)
                    dr.line(pts, fill=col if b.get("status") != "ok" else FARBE["info"], width=3)
                elif t == "standflaeche" and name == "unten":
                    h = [P([x, y, mk["z"]]) for x, y in mk["hull"]]
                    if len(h) >= 2:
                        dr.line(h + [h[0]], fill=col if b.get("status") != "ok" else FARBE["info"], width=1)
                    x, y = P(mk["com"])
                    dr.line([(x - 8, y), (x + 8, y)], fill=col, width=3)
                    dr.line([(x, y - 8), (x, y + 8)], fill=col, width=3)
        lab = {"vorn": "VORN (Kopf zur Kamera)", "seite": "SEITE (Kopf rechts)", "oben": "OBEN (Kopf rechts)",
               "unten": "UNTEN (Kopf rechts) · ○ Füße · + Schwerpunkt"}[name]
        dr.rectangle([0, 0, res, 22], fill=(0, 0, 0))
        dr.text((6, 3), lab, fill=(255, 255, 255), font=f)
        tiles[name] = im

    # Kopf
    lines = []
    for key, b in befunde.items():
        st = b["status"]
        col = {"WARNUNG": FARBE["rot"], "freigegeben": FARBE["orange"], "ok": FARBE["ok"]}.get(st, (170, 170, 170))
        txt = f"{st:<13} {TITEL[key]}: {b.get('text', '')}"
        if st == "freigegeben":
            txt += f"  [Begründung: {b['begruendung']}]"
        lines.append((txt, col))
    head_h = 120 + 22 * len(lines)
    W = res * 2
    img = Image.new("RGB", (W, head_h + res * 2 + 80), (25, 25, 28))
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 78], fill=(150, 0, 0))
    dr.text((12, 8), "NUR FRÜHWARNSYSTEM – Sichtprüfung durch den Agenten IMMER zusätzlich notwendig!", fill=(255, 255, 255), font=font(24))
    dr.text((12, 44), "Bilder ansehen, gegen Concept und Referenzbilder vergleichen. Kein Befund ≠ Freigabe.",
            fill=(255, 230, 230), font=font(18))
    n_warn = sum(1 for b in befunde.values() if b["status"] == "WARNUNG")
    erg = f"{n_warn} automatische Auffälligkeit(en) – Sichtprüfung erforderlich" if n_warn else ERGEBNIS_LEER
    dr.text((12, 88), f"{meta['kreatur']}  ·  Skelett {meta['skelett']}/{meta['muster']}  ·  {erg}",
            fill=FARBE["rot"] if n_warn else (230, 230, 230), font=font(18))
    y = 116
    for txt, col in lines:
        while dr.textlength(txt, font=font(14)) > W - 24 and len(txt) > 20:
            txt = txt[:-4] + "…"
        dr.text((12, y), txt, fill=col, font=font(14))
        y += 22
    for i, name in enumerate(order):
        img.paste(tiles[name], ((i % 2) * res, head_h + (i // 2) * res))
    dr.text((12, head_h + 2 * res + 8), "rot = Auffälligkeit · orange = per creature.toml mit Begründung freigegeben · "
            "grün/blau = gemessen, unauffällig · gelb = Bauchlinie/Prüfstreifen", fill=(220, 220, 220), font=font(15))
    for i, line in enumerate(textwrap.wrap(HINWEIS, 125)):
        dr.text((12, head_h + 2 * res + 32 + 18 * i), line, fill=(255, 120, 120), font=font(14))
    img.save(out_png)


# ----------------------------------------------------------------------------------------------- Ablauf
def blender(args):
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", str(BLENDER_PART), "--", *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or "Traceback" in r.stdout + r.stderr or "MODELCHECK_" not in r.stdout:
        print(r.stdout[-3000:], r.stderr[-2000:])
        raise SystemExit("Fehler im Blender-Teil (rigging/model_check_blender.py)")


def check(creature_dir, quiet=False):
    c = pathlib.Path(creature_dir).resolve()
    src = c / "raw" / "generate_model.glb"
    if not src.exists():
        raise SystemExit(f"{src} fehlt – erst scripts/tripo_run.py --steps generate laufen lassen.")
    cfg, freigabe, meta = resolve_config(c)
    review = c / "review"
    review.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="model_check_"))
    try:
        blender(["export", src, tmp / "geo.npz", meta["facing"]])
        M = Model(tmp / "geo.npz")
        raw, groups = analyse(M, cfg, meta)

        befunde, red, orange = {}, [], []
        for key, b in raw.items():
            if "skip" in b:
                befunde[key] = {"status": "nicht geprüft", "text": b["skip"]}
                continue
            st = "info" if b.get("info_only") else "WARNUNG" if b["warn"] else "ok"
            if st == "WARNUNG" and key in freigabe:
                st = "freigegeben"
            out = {"status": st, "text": b["text"], "werte": b.get("werte", {})}
            if key in freigabe:
                out["begruendung"] = freigabe[key]
            for k in ("_marks", "_bad_nr"):
                if k in b:
                    out[k] = b[k]
            befunde[key] = out
            if st == "WARNUNG":
                red += b.get("_polys", [])
            elif st == "freigegeben":
                orange += b.get("_polys", [])
        marks = {"rot": sorted(set(red)), "orange": sorted(set(orange) - set(red)), "res": cfg["bild"]["aufloesung"]}
        (tmp / "marks.json").write_text(json.dumps(marks), encoding="utf-8")
        blender(["render", src, tmp / "views", meta["facing"], tmp / "marks.json"])
        views = json.loads((tmp / "views" / "views.json").read_text(encoding="utf-8"))
        compose(tmp / "views", views, befunde, groups, meta, M, review / "model_check.png")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_warn = sum(1 for b in befunde.values() if b["status"] == "WARNUNG")
    report = {
        "hinweis": HINWEIS,
        "ergebnis": (f"{n_warn} automatische Auffälligkeit(en) – Sichtprüfung erforderlich" if n_warn else ERGEBNIS_LEER),
        "ist_freigabe": False,
        "kreatur": meta["kreatur"], "modell": str(src.relative_to(ROOT)).replace("\\", "/"),
        "skelett": meta["skelett"], "muster": meta["muster"], "facing": meta["facing"],
        "datum": datetime.date.today().isoformat(),
        "kennzahlen": {"dreiecke": len(M.tris), "vertices": len(M.V), "mesh_teile": int(len(np.unique(M.part))),
                       "mesh_objekte": M.n_objects, "materialien": M.n_materials,
                       "masse_modell_einheiten": [round(float(x), 3) for x in M.ext],
                       "tiefster_punkt_z": round(M.ground, 3),
                       "anmerkung": "Tripo liefert zentriert und auf Größe 1 normiert; die Pipeline stellt den tiefsten Punkt auf den Boden."},
        "befunde": {k: {kk: vv for kk, vv in b.items() if not kk.startswith("_")} for k, b in befunde.items()},
        "bild": "model_check.png",
        "konfig": cfg, "freigabe": freigabe,
    }
    (review / "model_check.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if not quiet:
        print(f"\nModellprüfung {meta['kreatur']} (Skelett {meta['skelett']}/{meta['muster']})")
        for key, b in befunde.items():
            line = f"  {b['status']:<13} {TITEL[key]}: {b['text']}"
            if "begruendung" in b and b["status"] == "freigegeben":
                line += f"  [Begründung: {b['begruendung']}]"
            print(line)
        print(f"\n  Ergebnis: {report['ergebnis']}")
        print(f"  Bericht: {review / 'model_check.json'}\n  Prüfbild: {review / 'model_check.png'}")
        print_hinweis()
    return report


def print_hinweis():
    """Steht IMMER am Ende jeder Konsolenausgabe – auch wenn alles grün ist (Anweisung des Nutzers)."""
    bar = "!" * 100
    body = textwrap.wrap(HINWEIS + " Ein Ergebnis ohne Befund ist KEINE Freigabe.", 94)
    print("\n" + bar + "\n" + "\n".join(f"!! {line}" for line in body) + "\n" + bar)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description="Modellprüfung (nur Frühwarnsystem – Sichtprüfung bleibt Pflicht)")
    ap.add_argument("creature_dir", nargs="?")
    ap.add_argument("--all", action="store_true", help="alle Kreaturen mit raw/generate_model.glb prüfen + Tabelle")
    a = ap.parse_args()
    if a.all:
        dirs = sorted(p.parent.parent for p in (ROOT / "creatures").glob("*/raw/generate_model.glb"))
        reps = []
        for d in dirs:
            print(f"→ {d.name}", flush=True)
            reps.append(check(d, quiet=True))
        keys = list(TITEL)
        short = {"WARNUNG": "WARN", "ok": "ok", "freigegeben": "frei", "info": "info", "nicht geprüft": "–"}
        print("\n" + "Kreatur".ljust(20) + "".join(k[:10].ljust(11) for k in keys))
        for r in reps:
            print(r["kreatur"][:19].ljust(20) + "".join(short[r["befunde"][k]["status"]].ljust(11) for k in keys))
        print("\nDetails: creatures/<name>/review/model_check.json + model_check.png")
        print_hinweis()
    elif a.creature_dir:
        check(a.creature_dir)
    else:
        ap.error("creatures/<name> oder --all angeben")


if __name__ == "__main__":
    main()
