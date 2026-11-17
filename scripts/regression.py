"""Regressionstest: Hat sich eine freigegebene Kreatur verändert, weil gemeinsamer Code geändert wurde?

  python scripts/regression.py                      schnell (Sekunden): welche Abhängigkeiten freigegebener Kreaturen
                                                    haben sich seit der Freigabe geändert?
  python scripts/regression.py --deep               betroffene Kreaturen in temp/regression/ neu bauen und ihren
                                                    Fingerabdruck mit der Freigabe vergleichen (Minuten)
  python scripts/regression.py --deep --all         alle freigegebenen, egal ob betroffen
  python scripts/regression.py --deep --creatures a,b --against temp/base
                                                    beliebige Kreaturen gegen einen eigenen Vergleichsstand
                                                    (<against>/<name>/rig/fingerprint.json.gz), z. B. vor/nach Umbau
  python scripts/regression.py --compare A.json.gz B.json.gz

Gleicher Fingerabdruck = Knochen und verformtes Mesh sind in jedem Clip an jedem geprüften Frame gleich (±0,1 mm).
Ist eine geänderte Datei harmlos (Fingerabdruck gleich), wird der Freigabe-Nachweis auf den neuen Stand gesetzt.
Exit-Code 1 = Änderung gefunden → Ursache beheben oder Kreatur bewusst neu freigeben lassen.
"""
import argparse
import concurrent.futures as cf
import datetime
import gzip
import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_info  # noqa: E402

TOL_POS = 1e-4      # m
TOL_ROT = 1e-3      # Quaternion-Komponente


def load_fp(p):
    p = pathlib.Path(p)
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == ".gz" else raw)


def compare(a, b):
    """→ (gleich?, Liste lesbarer Unterschiede pro Clip)"""
    diffs = []
    if a["bones"] != b["bones"]:
        diffs.append(f"Skelett anders: {len(a['bones'])} → {len(b['bones'])} Knochen")
        return False, diffs
    if a["verts_total"] != b["verts_total"]:
        diffs.append(f"Mesh anders: {a['verts_total']} → {b['verts_total']} Vertices")
        return False, diffs
    for clip in sorted(set(a["clips"]) | set(b["clips"])):
        if clip not in a["clips"] or clip not in b["clips"]:
            diffs.append(f"{clip}: {'neu' if clip not in a['clips'] else 'fehlt'}")
            continue
        ca, cb = a["clips"][clip], b["clips"][clip]
        if set(ca) != set(cb):
            diffs.append(f"{clip}: Länge {max(map(int, ca))} → {max(map(int, cb))} Frames")
            continue
        dv = dp = dr = 0.0
        worst = None
        for f in ca:
            for va, vb in zip(ca[f]["verts"], cb[f]["verts"]):
                d = math.dist(va, vb)
                if d > dv:
                    dv, worst = d, f
            for ba, bb in zip(ca[f]["bones"], cb[f]["bones"]):
                dp = max(dp, math.dist(ba[:3], bb[:3]))
                qa, qb = ba[3:], bb[3:]
                dr = max(dr, min(max(abs(x - y) for x, y in zip(qa, qb)), max(abs(x + y) for x, y in zip(qa, qb))))
        if dv > TOL_POS or dp > TOL_POS or dr > TOL_ROT:
            diffs.append(f"{clip}: Mesh weicht bis {dv * 1000:.1f} mm ab (Frame {worst}), Knochen {dp * 1000:.1f} mm / "
                         f"{math.degrees(2 * math.asin(min(1, dr))):.1f}°")
    return not diffs, diffs


def approved_creatures():
    return sorted(p.parent.parent for p in ROOT.glob("creatures/*/approved/approval.json"))


def rebuild(c, work):
    log = work.parent / f"{c.name}.log"
    work.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "w", encoding="utf-8") as fh:
        rc = subprocess.call([sys.executable, str(ROOT / "scripts" / "creature_pipeline.py"), str(c), "--stage", "check",
                              "--work", str(work)], stdout=fh, stderr=subprocess.STDOUT)
    return rc, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--creatures", default=None, help="Komma-Liste statt der freigegebenen")
    ap.add_argument("--against", default=None, help="Vergleichsordner statt approved/")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--compare", nargs=2, default=None)
    ap.add_argument("--rename", default=None, help="nur mit --compare: ALT=NEU, Clip-Präfix im ersten Abdruck umbenennen "
                                                   "(z. B. Crawler_Ant_=Hexapod_Ant_ nach einer Umbenennung)")
    a = ap.parse_args()

    if a.compare:
        ref = load_fp(a.compare[0])
        if a.rename:
            old, new = a.rename.split("=")
            ref["clips"] = {k.replace(old, new, 1): v for k, v in ref["clips"].items()}
        same, diffs = compare(ref, load_fp(a.compare[1]))
        print("✓ gleich" if same else "✗ verschieden\n  " + "\n  ".join(diffs))
        sys.exit(0 if same else 1)

    if a.creatures:
        todo = {ROOT / "creatures" / n: ["(manuell gewählt)"] for n in a.creatures.split(",")}
    else:
        todo = {}
        for c in approved_creatures():
            man = json.loads((c / "approved" / "manifest.json").read_text(encoding="utf-8"))
            ch = build_info.changed_files(man, c)
            print(f"{'⚠' if ch else '✓'} {c.name:22} " + (f"{len(ch)} geänderte Abhängigkeit(en): {', '.join(ch)}" if ch
                                                          else "unverändert seit Freigabe"))
            if ch or a.all:
                todo[c] = ch
        if not approved_creatures():
            print("Keine freigegebenen Kreaturen (creatures/*/approved/).")
    if not todo:
        return
    if not a.deep:
        print("\n→ Betroffene prüfen: python scripts/regression.py --deep   (vor jedem Commit an gemeinsamem Code!)")
        sys.exit(1)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / "temp" / "regression" / stamp
    print(f"\nNeu bauen in {run_dir} ({len(todo)} Kreatur(en), {a.jobs} parallel) …", flush=True)
    if not (ROOT / "uv" / "textures" / "uv_checker.png").exists():   # einmal vorab, sonst schreiben parallele Bauten gleichzeitig
        subprocess.run([sys.executable, str(ROOT / "uv" / "biome_textures.py"), str(ROOT / "uv" / "textures")], check=True)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(rebuild, c, run_dir / c.name): c for c in todo}
        results = {futs[f]: f.result() for f in cf.as_completed(futs)}
    bad = False
    for c in sorted(todo):
        rc, log = results[c]
        if rc != 0:
            print(f"✗ {c.name:22} Bau fehlgeschlagen – {log}")
            bad = True
            continue
        new = load_fp(run_dir / c.name / "rig" / "fingerprint.json.gz")
        ref_p = (pathlib.Path(a.against).resolve() / c.name / "rig" / "fingerprint.json.gz") if a.against \
            else c / "approved" / "fingerprint.json.gz"
        same, diffs = compare(load_fp(ref_p), new)
        print(f"{'✓' if same else '✗'} {c.name:22} {'identisch' if same else 'VERÄNDERT'}")
        for d in diffs:
            print("     ", d)
        bad |= not same
        if same and not a.against and todo[c]:      # harmlose Änderung → Nachweis auf neuen Stand setzen
            man_p = c / "approved" / "manifest.json"
            old = json.loads(man_p.read_text(encoding="utf-8"))
            now = build_info.manifest(c, old.get("style"))
            now["rechecked"] = old.get("rechecked", []) + [{"date": stamp, "commit": now["commit"], "changed": todo[c]}]
            build_info.write(man_p, now)
            print("       Nachweis aktualisiert (Änderung betrifft diese Kreatur nicht)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
