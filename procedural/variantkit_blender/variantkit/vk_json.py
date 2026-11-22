"""Varianten-Datei lesen/schreiben – Python-Gegenstück zu Unity `VkJson.cs` + `VkDoc.cs`.

Gleiche Regeln wie Unity (Spec 5.4 / 6.1), damit beide Programme dieselbe Datei abwechselnd schreiben können:
- Aufgelöste Fassung = Gruppen-Preset → Biom-Block → Datei (Objekte feldweise, Listen mit "id" je Eintrag).
- Gespeichert wird Kopf + volle Statur + nur die Abweichungen vom Preset.
- Schreiben: UTF-8, 2 Leerzeichen, "\n", Zahlen auf 3 Nachkommastellen, kleine flache Objekte in einer Zeile,
  atomar (temporäre Datei, dann umbenennen), Revisions-Schutz.
Keine Fremdbibliothek, nur die Python-Standardbibliothek.
"""
import copy
import hashlib
import json
import os

FORMAT_VERSION = 1

HEAD_ORDER = ["format", "format_version", "revision", "id", "name", "basis", "skelett", "muster", "art", "gruppe", "biom",
              "sonder", "budget_klasse", "seed", "freigegeben", "quelle", "statur", "bedeckung", "accessoires", "material",
              "effekte", "_gebaut"]

STATUR_FELDER = ["groesse", "koerper_laenge", "rumpf_hoehe", "rumpf_dicke", "buckel", "glied_dicke", "bein_laenge_vorn",
                 "bein_laenge_hinten", "spur_breite", "pranken_vorn", "pranken_hinten", "hals_laenge", "kopf_groesse",
                 "kopf_breite", "schnauze_laenge", "schwanz_laenge", "schwanz_dicke"]


# ------------------------------------------------------------------------------------------------ Schreiben
def _num(d):
    d = round(float(d), 3)
    if d == 0:
        return "0.0"
    s = f"{d:.3f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    return "0.0" if s == "-0.0" else s


def _q(s):
    out = ['"']
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _simple(v):
    return not isinstance(v, (dict, list))


def _w(sb, v, ind):
    if v is None:
        sb.append("null")
    elif isinstance(v, bool):
        sb.append("true" if v else "false")
    elif isinstance(v, str):
        sb.append(_q(v))
    elif isinstance(v, int):
        sb.append(str(v))
    elif isinstance(v, float):
        sb.append(_num(v))
    elif isinstance(v, list):
        if not v:
            sb.append("[]")
            return
        if all(_simple(x) for x in v):
            sb.append("[")
            for k, x in enumerate(v):
                if k:
                    sb.append(", ")
                _w(sb, x, ind)
            sb.append("]")
            return
        sb.append("[\n")
        for k, x in enumerate(v):
            sb.append(" " * ((ind + 1) * 2))
            _w(sb, x, ind + 1)
            sb.append(",\n" if k < len(v) - 1 else "\n")
        sb.append(" " * (ind * 2) + "]")
    elif isinstance(v, dict):
        if not v:
            sb.append("{}")
            return
        if ind > 0 and len(v) <= 8 and all(_simple(x) or (isinstance(x, list) and all(_simple(y) for y in x)) for x in v.values()):
            line = ["{ "]
            for k, (key, x) in enumerate(v.items()):
                if k:
                    line.append(", ")
                line.append(_q(key))
                line.append(": ")
                _w(line, x, ind)
            line.append(" }")
            s = "".join(line)
            if len(s) + ind * 2 < 150:
                sb.append(s)
                return
        sb.append("{\n")
        for c, (key, x) in enumerate(v.items()):
            sb.append(" " * ((ind + 1) * 2))
            sb.append(_q(key))
            sb.append(": ")
            _w(sb, x, ind + 1)
            sb.append(",\n" if c < len(v) - 1 else "\n")
        sb.append(" " * (ind * 2) + "}")
    else:
        sb.append(_q(str(v)))


def write(v):
    sb = []
    _w(sb, v, 0)
    sb.append("\n")
    return "".join(sb)


def write_file(path, obj):
    """Atomar schreiben (temporäre Datei, dann umbenennen)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(write(obj))
    os.replace(tmp, path)


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------ Merge / Diff (Spec 5.4)
NO_CHANGE = object()


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _id_list(v):
    return isinstance(v, list) and len(v) > 0 and all(isinstance(x, dict) and isinstance(x.get("id"), str) for x in v)


def merge(b, over):
    if isinstance(b, dict) and isinstance(over, dict):
        r = copy.deepcopy(b)
        for k, v in over.items():
            r[k] = merge(r[k], v) if k in r else copy.deepcopy(v)
        return r
    if isinstance(b, list) and isinstance(over, list) and (_id_list(b) or _id_list(over)) and all(isinstance(x, dict) for x in over):
        r = copy.deepcopy(b)
        for e in over:
            i = -1
            if isinstance(e.get("id"), str):
                for k, x in enumerate(r):
                    if isinstance(x, dict) and x.get("id") == e["id"]:
                        i = k
                        break
            if i >= 0:
                r[i] = merge(r[i], e)
            else:
                r.append(copy.deepcopy(e))
        return r
    return copy.deepcopy(over)


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    if _is_num(a) and _is_num(b):
        return abs(float(a) - float(b)) < 5e-4
    if isinstance(a, dict) and isinstance(b, dict):
        return len(a) == len(b) and all(k in b and same(v, b[k]) for k, v in a.items())
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if type(a) != type(b) and not (isinstance(a, str) and isinstance(b, str)):
        return False
    return a == b


def diff(resolved, b):
    if isinstance(resolved, dict) and isinstance(b, dict):
        r = {}
        for k, v in resolved.items():
            if k not in b:
                r[k] = copy.deepcopy(v)
                continue
            d = diff(v, b[k])
            if d is not NO_CHANGE:
                r[k] = d
        return NO_CHANGE if not r else r
    if isinstance(resolved, list) and isinstance(b, list) and (_id_list(resolved) or _id_list(b)):
        r = []
        for e in resolved:
            if not isinstance(e, dict):
                continue
            eid = e.get("id")
            be = next((x for x in b if isinstance(x, dict) and x.get("id") == eid), None)
            if be is None:
                r.append(copy.deepcopy(e))
                continue
            d = diff(e, be)
            if isinstance(d, dict):
                d = {"id": eid, **{k: v for k, v in d.items() if k != "id"}}
                r.append(d)
        for be in b:
            if isinstance(be, dict) and not any(isinstance(x, dict) and x.get("id") == be.get("id") for x in resolved):
                r.append({"id": be.get("id"), "an": False})
        return NO_CHANGE if not r else r
    return NO_CHANGE if same(resolved, b) else copy.deepcopy(resolved)


def fnv1a(s):
    h = 2166136261
    for byte in s.encode("utf-8"):
        h ^= byte
        h = (h * 16777619) & 0xFFFFFFFF
    return h & 0x7FFFFFFF


# ------------------------------------------------------------------------------------------------ Varianten-Datei
def pipeline_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


def preset_dir():
    return os.path.join(pipeline_root(), "templates", "umgebungs_gruppen")


WEICH_STD_ACC = {"moosfransen": 0.9, "tang": 0.9, "gehaenge": 0.9, "kette": 0.7, "barteln": 0.6, "grasbueschel": 0.5}


def migrate(o):
    """G14 (wie Unity VkSpec.Migrate): `schwingen` der Lagen und `bewegung`/`schwingen.staerke` der Accessoires gehen in
    `weichheit` auf. Die alten Felder hatten keine Wirkung: 0 / "starr" = Platzhalter -> Typ-Standard."""
    if not isinstance(o, dict):
        return
    bed = o.get("bedeckung")
    for l in (bed.get("lagen") or []) if isinstance(bed, dict) else []:
        if isinstance(l, dict) and "schwingen" in l:
            v = l.pop("schwingen")
            if _is_num(v) and v > 0 and "weichheit" not in l:
                l["weichheit"] = float(v)
    acc = o.get("accessoires")
    for a in acc if isinstance(acc, list) else []:
        if not isinstance(a, dict):
            continue
        b = a.pop("bewegung", None)
        sw = a.pop("schwingen", None)
        if b == "schwingt" and "weichheit" not in a:
            st = sw.get("staerke", 1.0) if isinstance(sw, dict) else (sw if _is_num(sw) else 1.0)
            a["weichheit"] = round(float(st) * WEICH_STD_ACC.get(a.get("typ"), 0.9), 3)
    bio = o.get("biome")
    for v in bio.values() if isinstance(bio, dict) else []:
        migrate(v)


def load_preset(gruppe, biom, format_v1=False):
    """Preset + Biom-Block. format_v1: die eingefrorene Fassung (templates/umgebungs_gruppen/_v1/), gegen die eine
    Varianten-Datei im Format 1 gespeichert wurde. Blender liest Material-Ebenen nicht; Unity stellt Format 1 auf 2 um
    (zwei Ebenen-Gruppen, VkSpec.MigrateMaterialV1). So bleibt eine alte Datei auch nach Speichern in Blender stimmig."""
    if not gruppe:
        return {}
    p = os.path.join(preset_dir(), gruppe + ".json")
    p1 = os.path.join(preset_dir(), "_v1", gruppe + ".json")
    if format_v1 and os.path.exists(p1):
        p = p1
    if not os.path.exists(p):
        return {}
    pr = read_file(p)
    r = {}
    for k in ("bedeckung", "accessoires", "material", "effekte"):
        if k in pr:
            r[k] = copy.deepcopy(pr[k])
    bb = (pr.get("biome") or {}).get(biom or "")
    if isinstance(bb, dict):
        r = merge(r, bb)
    migrate(r)
    return r


def _ordered(o):
    r = {}
    for k in HEAD_ORDER:
        if k in o:
            r[k] = o[k]
    for k, v in o.items():
        if k not in r:
            r[k] = v
    return r


class VariantDoc:
    """Eine Varianten-Datei (aufgelöste Fassung zum Bearbeiten, gespeichert wird nur die Anpassung)."""

    def __init__(self, path):
        self.path = path
        self.resolved = {}
        self.preset_resolved = {}
        self.loaded_revision = 0
        self.dirty = False

    @staticmethod
    def load(path):
        stored = read_file(path)
        migrate(stored)
        d = VariantDoc(path)
        d.preset_resolved = load_preset(stored.get("gruppe"), stored.get("biom"), int(stored.get("format_version", 1) or 1) < 2)
        d.resolved = merge(d.preset_resolved, stored)
        d.normalize()
        d.loaded_revision = int(stored.get("revision", 0) or 0)
        return d

    @property
    def id(self):
        return self.resolved.get("id", "variante")

    @property
    def export_name(self):
        return "".join(s[:1].upper() + s[1:] for s in self.id.split("_") if s)

    def normalize(self):
        R = self.resolved
        st = R.get("statur") if isinstance(R.get("statur"), dict) else {}
        R["statur"] = {f: float(st.get(f, 1.0)) for f in STATUR_FELDER}
        bed = R.setdefault("bedeckung", {})
        if not isinstance(bed, dict):
            bed = R["bedeckung"] = {}
        if "haut" not in bed:
            bed["haut"] = {"typ": "glatt", "rauheit": 0.8}
        if not isinstance(bed.get("lagen"), list):
            bed["lagen"] = []
        if not isinstance(R.get("accessoires"), list):
            R["accessoires"] = []
        mat = R.setdefault("material", {})
        mat.setdefault("stil", {})
        mat.setdefault("farbgruppen", {})
        fv = int(R.get("format_version", 1) or 1)
        keys = ("ebenen", "ebenen_accessoires") if fv >= 2 else ("ebenen",)   # Format 2: zweite Ebenen-Gruppe (Accessoires)
        for key in keys:
            if not isinstance(mat.get(key), list):
                mat[key] = []
            for n, e in enumerate([e for e in mat[key] if isinstance(e, dict)], 1):
                if not isinstance(e.get("id"), str):
                    ne = {"id": f"{e.get('typ', 'ebene')}#{n}"}
                    ne.update(e)
                    e.clear()
                    e.update(ne)
        R.setdefault("effekte", {})
        R.setdefault("_gebaut", None)
        self.resolved = _ordered(R)

    def stored(self):
        R = self.resolved
        d = diff(R, self.preset_resolved)
        d = d if isinstance(d, dict) else {}
        r = {}
        for k in HEAD_ORDER:
            if k == "statur":
                r[k] = copy.deepcopy(R["statur"])
                continue
            if k in ("bedeckung", "accessoires", "material", "effekte"):
                if k in d:
                    r[k] = d[k]
                continue
            if k in R:
                r[k] = copy.deepcopy(R[k])
        for k, v in R.items():
            if k not in r and k not in HEAD_ORDER:
                r[k] = copy.deepcopy(v)
        return r

    def save(self, force=False):
        """None = gespeichert, sonst Meldung (Datei ist neuer → nicht überschrieben)."""
        if os.path.exists(self.path) and not force:
            try:
                disk = int(read_file(self.path).get("revision", 0) or 0)
                if disk > self.loaded_revision:
                    return f"Datei wurde geändert (Revision {disk} > {self.loaded_revision}) – neu laden?"
            except Exception:
                pass
        self.resolved["revision"] = self.loaded_revision + 1
        write_file(self.path, self.stored())
        self.loaded_revision += 1
        self.dirty = False
        return None

    def disk_revision(self):
        try:
            return int(read_file(self.path).get("revision", 0) or 0)
        except Exception:
            return -1

    def entry_seed(self, entry, fallback_id):
        if entry and entry.get("seed") is not None:
            return int(entry["seed"])
        return fnv1a(f"{int(self.resolved.get('seed', 0) or 0)}:{(entry or {}).get('id', fallback_id) or fallback_id}")


def bedeckung_fingerprint(doc):
    """Kennung der Bedeckung, aus der gebaut wurde (Unity vergleicht damit, ob das Ergebnis noch aktuell ist)."""
    src = {"seed": int(doc.resolved.get("seed", 0) or 0), "bedeckung": doc.resolved.get("bedeckung", {})}
    return "sha1:" + hashlib.sha1(write(src).encode("utf-8")).hexdigest()
