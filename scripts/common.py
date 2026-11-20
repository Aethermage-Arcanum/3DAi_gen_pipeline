"""Gemeinsame Helfer: Konfiguration laden/mergen, .env lesen, Kreatur-Ordner ↔ Kreatur-ID auflösen."""
import copy
import pathlib
import re
import tomllib

PIPELINE_DIR = pathlib.Path(__file__).resolve().parent.parent
ROOT_DIR = PIPELINE_DIR.parent
ENV_FILE = ROOT_DIR / ".env"
CREATURES_DIR = PIPELINE_DIR / "creatures"

# ----------------------------------------------------------------------------------- Kreatur-Ordner ↔ Kreatur-ID
# Seit 2026-11-20 (BACKLOG G7) tragen die Ordner eine laufende Nummer: creatures/01_chitin_crawler/.
# Die Kreatur-ID (`id` im Roster, `name` in creature.toml), der Exportname (ChitinCrawler.fbx) und alle Clip-/Unity-
# Namen bleiben OHNE Nummer. Nur hier wird zwischen Ordner und ID übersetzt – kein Skript baut den Pfad selbst.
_NUMBERED = re.compile(r"^(\d+)_(.+)$")


def folder_id(folder):
    """Ordnername → ID ohne Nummer ('01_chitin_crawler' → 'chitin_crawler'; ohne Nummer unverändert)."""
    name = pathlib.Path(folder).name
    m = _NUMBERED.match(name)
    return m.group(2) if m else name


def creature_dirs():
    """Alle Kreatur-Ordner (mit creature.toml), nach Nummer sortiert."""
    if not CREATURES_DIR.exists():
        return []
    return sorted(p.parent for p in CREATURES_DIR.glob("*/creature.toml"))


def creature_id(creature_dir):
    """ID einer Kreatur: `name` aus der creature.toml, sonst der Ordnername ohne Nummer."""
    creature_dir = pathlib.Path(creature_dir)
    toml = creature_dir / "creature.toml"
    if toml.exists():
        name = load_toml(toml).get("name")
        if name:
            return name
    return folder_id(creature_dir)


def export_name(creature_dir):
    """Exportname (FBX/GLB, Unity) aus der ID: chitin_crawler → ChitinCrawler. Nie aus dem Ordnernamen."""
    return "".join(p.capitalize() for p in creature_id(creature_dir).split("_"))


def find_creature(id_or_path, must_exist=True):
    """Kreatur-Ordner zu einer ID oder einem Pfad.

    Akzeptiert 'creatures/01_chitin_crawler', '01_chitin_crawler', 'chitin_crawler' und auch den alten Pfad
    'creatures/chitin_crawler' (vor der Nummerierung) – Treffer ist immer der nummerierte Ordner.
    """
    p = pathlib.Path(id_or_path)
    if p.is_dir() and (p / "creature.toml").exists():
        return p.resolve()
    numbered = bool(_NUMBERED.match(p.name))
    dirs = [d for d in CREATURES_DIR.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))] \
        if CREATURES_DIR.exists() else []
    hits = [d for d in dirs if (d.name == p.name if numbered else folder_id(d) == p.name)]
    if len(hits) == 1:
        return hits[0].resolve()
    if len(hits) > 1:
        raise SystemExit(f"Kreatur '{id_or_path}' ist mehrdeutig: {', '.join(d.name for d in hits)}")
    if must_exist:
        raise SystemExit(f"Kreatur '{id_or_path}' nicht gefunden (gesucht in {CREATURES_DIR}).")
    return None


def new_creature_dir(cid):
    """Ordner für eine neue Kreatur: nächste freie Nummer (wird nicht angelegt)."""
    nums = [int(m.group(1)) for d in CREATURES_DIR.iterdir() if d.is_dir() and (m := _NUMBERED.match(d.name))] \
        if CREATURES_DIR.exists() else []
    return CREATURES_DIR / f"{max(nums, default=0) + 1:02d}_{cid}"


def creature_dir_for(cid):
    """Vorhandener Ordner zu einer ID, sonst der künftige mit nächster Nummer (für make_roster/concept_crops)."""
    return find_creature(cid, must_exist=False) or new_creature_dir(cid)


def load_toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def deep_merge(base, override):
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_creature(creature_dir):
    """Liefert (Gesamt-Konfig, Bauplan, Stil) für einen Kreatur-Ordner."""
    creature_dir = pathlib.Path(creature_dir).resolve()
    creature = load_toml(creature_dir / "creature.toml")
    cfg = deep_merge(load_toml(PIPELINE_DIR / "pipeline.toml"), creature)
    bodyplans = load_toml(PIPELINE_DIR / "templates" / "bodyplans.toml")
    styles = load_toml(PIPELINE_DIR / "templates" / "styles.toml")
    bp_name, st_name = cfg["bodyplan"], cfg["style"]
    if bp_name not in bodyplans:
        raise SystemExit(f"Unbekannter Bauplan '{bp_name}'. Verfügbar: {', '.join(bodyplans)}")
    if st_name not in styles:
        raise SystemExit(f"Unbekannter Stil '{st_name}'. Verfügbar: {', '.join(styles)}")
    return cfg, bodyplans[bp_name], styles[st_name]


def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env
