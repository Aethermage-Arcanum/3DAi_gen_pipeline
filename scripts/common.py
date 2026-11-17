"""Gemeinsame Helfer: Konfiguration laden/mergen, .env lesen."""
import copy
import pathlib
import tomllib

PIPELINE_DIR = pathlib.Path(__file__).resolve().parent.parent
ROOT_DIR = PIPELINE_DIR.parent
ENV_FILE = ROOT_DIR / ".env"


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
