"""Freigabe einer Kreatur durch den Nutzer → sperrt sie gegen versehentliches Neu-Bauen.

  python scripts/approve.py creatures/<name> [--note "Text"]
  python scripts/approve.py creatures/<name> --revoke          Freigabe zurückziehen (Ordner approved/ löschen)

Legt creatures/<name>/approved/ an:
  approval.json        wann, welcher Git-Stand, Notiz
  manifest.json        Prüfsummen aller Dateien, die das Ergebnis bestimmen (scripts/build_info.py)
  fingerprint.json.gz  Knochen + verformtes Mesh aller Clips (Referenz für scripts/regression.py)
Nur der Nutzer gibt frei – Claude ruft das Skript erst nach ausdrücklichem OK auf.
"""
import argparse
import datetime
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_info  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("creature_dir")
    ap.add_argument("--note", default="")
    ap.add_argument("--revoke", action="store_true")
    a = ap.parse_args()
    c = pathlib.Path(a.creature_dir).resolve()
    dst = c / "approved"
    if a.revoke:
        shutil.rmtree(dst, ignore_errors=True)
        print(f"Freigabe von {c.name} zurückgezogen – die Pipeline darf sie wieder neu bauen.")
        return
    rig = c / "rig"
    man_p, fp_p = rig / "build_manifest.json", rig / "fingerprint.json.gz"
    if not (man_p.exists() and fp_p.exists()):
        raise SystemExit("Kein Bau-Nachweis/Fingerabdruck – erst python scripts/creature_pipeline.py " +
                         f"creatures/{c.name} (Stufe full) laufen lassen.")
    man = json.loads(man_p.read_text(encoding="utf-8"))
    ch = build_info.changed_files(man, c)
    if ch:
        raise SystemExit("Code hat sich seit dem letzten Bau geändert – Ergebnis wäre nicht reproduzierbar:\n  " +
                         "\n  ".join(ch) + f"\nErst neu bauen, ansehen, dann freigeben.")
    dst.mkdir(exist_ok=True)
    shutil.copy(man_p, dst / "manifest.json")
    shutil.copy(fp_p, dst / "fingerprint.json.gz")
    build_info.write(dst / "approval.json", {"date": datetime.date.today().isoformat(), "commit": build_info.git_commit(),
                                             "style": man["style"], "note": a.note})
    print(f"✓ {c.name} freigegeben und gesperrt ({man['style']}, {len(man['files'])} Abhängigkeiten).")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
