"""Komplette Krabbler-Nachbearbeitung für eine Kreatur – kostenlos, lokal, wiederholbar.

  python scripts/crawler_pipeline.py creatures/chitin_crawler [--name ChitinCrawler] [--no-preview]

Schritte (alle per Blender headless):
  1. rigging/crawler_rig.py     Anatomie erkennen, Standard-Skelett, Gewichte   → rig/crawler_rigged.blend
  2. rigging/crawler_walk.py    prozeduraler Laufzyklus + Selbstprüfung         → rig/crawler_walk.blend
  3. rigging/render_anim.py     Vorschau (Seite/oben/ARPG) + GIF                 → rig/anim/
  4. rigging/export_unity.py    FBX + GLB für Unity/Blender                      → output/
  5. rigging/verify_export.py   Gegentest der Exporte                            → output/verify_*.json
Eingabe: raw/generate_model.glb (Tripo, nur Mesh + Textur). Einstellungen: rigging/crawler_defaults.toml,
überschreibbar in creature.toml unter [crawler.*].
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLENDER = r"D:\Blender\blender.exe"


def blender(args, label):
    print(f"→ {label}", flush=True)
    r = subprocess.run([BLENDER, "-b", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    keep = [l for l in r.stdout.splitlines() if l.startswith(("RIG_REPORT", "WALK_REPORT", "  FOOT", "EXPORT_OK",
                                                               "VERIFY", "Traceback", "Error"))]
    for l in keep:
        print("   ", l[:400])
    if r.returncode != 0 or any("Traceback" in l for l in r.stdout.splitlines() + r.stderr.splitlines()):
        print(r.stdout[-3000:], r.stderr[-2000:])
        raise SystemExit(f"Fehler in Schritt: {label}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("creature_dir")
    ap.add_argument("--name", default=None, help="Exportname (Standard: aus Ordnername)")
    ap.add_argument("--no-preview", action="store_true")
    a = ap.parse_args()
    c = pathlib.Path(a.creature_dir).resolve()
    name = a.name or "".join(p.capitalize() for p in c.name.split("_"))
    toml = str(c / "creature.toml")
    rig, out = c / "rig", c / "output"
    src = c / "raw" / "generate_model.glb"
    if not src.exists():
        raise SystemExit(f"{src} fehlt – erst scripts/tripo_run.py --steps generate laufen lassen.")
    R = ROOT / "rigging"
    blender(["--factory-startup", "-P", str(R / "crawler_rig.py"), "--", str(src), str(rig), toml], "Rig")
    blender([str(rig / "crawler_rigged.blend"), "-P", str(R / "crawler_walk.py"), "--", str(rig), toml], "Laufzyklus")
    if not a.no_preview:
        anim = rig / "anim"
        for p in anim.glob("*.png"):
            p.unlink()
        blender([str(rig / "crawler_walk.blend"), "-P", str(R / "render_anim.py"), "--", str(anim), "360"], "Vorschau")
        subprocess.run([sys.executable, str(R / "make_gif.py"), str(anim), "30"], check=True)
    blender([str(rig / "crawler_walk.blend"), "-P", str(R / "export_unity.py"), "--", str(out), name, toml], "Export")
    ok = True
    for ext in ("fbx", "glb"):
        f = out / f"{name}.{ext}"
        blender(["--factory-startup", "-P", str(R / "verify_export.py"), "--", str(f), str(out / f"verify_{ext}.json")],
                f"Gegentest {ext.upper()}")
        ok &= json.loads((out / f"verify_{ext}.json").read_text(encoding="utf-8"))["ok"]
    walk = json.loads((rig / "walk_report.json").read_text(encoding="utf-8"))
    ok &= walk["loop_ok"] and walk["foot_contact_ok"]
    print(f"\n{'✓ ALLES OK' if ok else '✗ PRÜFUNG FEHLGESCHLAGEN'}  ·  Unity-Laufgeschwindigkeit: "
          f"{walk['suggested_move_speed_mps']} m/s  ·  Ausgabe: {out}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
