"""Bau-Nachweis einer Kreatur: welche Dateien (Skripte, Konfigs, Tripo-Mesh) ihr Ergebnis bestimmen + deren Prüfsummen.

Wird von creature_pipeline.py (schreibt build_manifest.json), approve.py (Freigabe) und regression.py
(Prüfung freigegebener Kreaturen) benutzt. Die Abhängigkeiten werden automatisch gefunden:
ausgehend vom Rig-Skript, Clip-Skript und der style.toml werden alle lokalen Imports und alle im Code
genannten Dateinamen (*.py / *.toml) eingesammelt – so fällt jede Änderung an gemeinsamem Code auf.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import tomllib

from common import creature_id

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {"creatures", "temp", "Unity", "__pycache__", ".git", "demo_output"}
_IMPORT = re.compile(r"^\s*(?:from|import)\s+(\w+)", re.M)
_LITERAL = re.compile(r"[\"'/](\w+\.(?:py|toml))[\"']")


def _index():
    idx = {}
    for p in ROOT.rglob("*"):
        if p.suffix in (".py", ".toml") and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS):
            idx.setdefault(p.name, []).append(p)
    return idx


def style_of(creature_dir, override=None):
    ct = tomllib.loads((creature_dir / "creature.toml").read_text(encoding="utf-8"))
    return override or ct.get("motion", {}).get("style", "hexapod/ant")


def dependencies(creature_dir, style=None):
    """Alle Dateien, die das Ergebnis dieser Kreatur bestimmen (Pfade relativ zum Pipeline-Ordner bzw. zur Kreatur)."""
    creature_dir = pathlib.Path(creature_dir).resolve()
    skel, muster = style_of(creature_dir, style).split("/")
    idx = _index()
    seeds = [ROOT / "scripts" / "creature_pipeline.py", ROOT / "rigging" / f"{skel}_rig.py",
             ROOT / "motions" / skel / muster / f"{muster}_clips.py", ROOT / "motions" / skel / muster / "style.toml"]
    seen, todo = set(), [s for s in seeds if s.exists()]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        if f.suffix != ".py":
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        names = {m + ".py" for m in _IMPORT.findall(txt)} | set(_LITERAL.findall(txt))
        for n in names:
            hits = idx.get(n, [])
            if len(hits) == 1:                    # mehrdeutige Namen (style.toml, README …) nur über Seeds
                todo.append(hits[0])
    files = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in seen)
    files += [f"@creature/{n}" for n in ("creature.toml", "raw/generate_model.glb") if (creature_dir / n).exists()]
    return files


def _path(rel, creature_dir):
    return (pathlib.Path(creature_dir) / rel[len("@creature/"):]) if rel.startswith("@creature/") else ROOT / rel


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:16]


def git_commit():
    try:
        c = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout.strip())
        return c + ("+uncommitted" if dirty else "")
    except OSError:
        return "?"


def manifest(creature_dir, style=None):
    creature_dir = pathlib.Path(creature_dir).resolve()
    deps = dependencies(creature_dir, style)
    return {"creature": creature_id(creature_dir), "style": style_of(creature_dir, style), "commit": git_commit(),
            "files": {d: sha(_path(d, creature_dir)) for d in deps}}


def changed_files(old, creature_dir):
    """Vergleicht einen gespeicherten Bau-Nachweis mit dem aktuellen Stand → Liste geänderter/neuer/fehlender Dateien."""
    now = manifest(creature_dir, old.get("style"))["files"]
    out = []
    for f in sorted(set(now) | set(old["files"])):
        if f not in now:
            out.append(f"{f} (entfernt)")
        elif f not in old["files"]:
            out.append(f"{f} (neu)")
        elif now[f] != old["files"][f]:
            out.append(f)
    return out


def write(path, data):
    pathlib.Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    import sys
    for d in dependencies(pathlib.Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None):
        print(d)
