"""Komplette Nachbearbeitung einer Kreatur nach Tripo – für jedes Skelett, ein Befehl, kostenlos, lokal.

  python scripts/creature_pipeline.py creatures/<name> [--name Export] [--no-preview] [--style skelett/muster]

Das Skelett kommt aus creature.toml [motion] style = "<skelett>/<muster>":
  crawler   → scripts/crawler_pipeline.py (bewährter Krabbler-Weg)
  sonst     → rigging/<skelett>_rig.py → motions/<skelett>/<muster>/<muster>_clips.py
Schritte: UV-Prüfung → Rig → Clips (+ Selbstprüfung) → Lückenprüfung → GIFs → Export FBX/GLB → Gegentest.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLENDER = r"D:\Blender\blender.exe"


def blender(args, label, show=("CLIP ", "EXPORT_OK", "GAPS", "VERIFY", "RIG_", "QUAD_", "Traceback", "Error")):
    print(f"→ {label}", flush=True)
    r = subprocess.run([BLENDER, "-b", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    for l in r.stdout.splitlines():
        if l.startswith(show):
            print("   ", l[:300])
    if r.returncode != 0 or "Traceback" in r.stdout + r.stderr:
        print(r.stdout[-3000:], r.stderr[-2000:])
        raise SystemExit(f"Fehler in Schritt: {label}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("creature_dir")
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--style", default=None)
    a = ap.parse_args()
    c = pathlib.Path(a.creature_dir).resolve()
    ct = tomllib.loads((c / "creature.toml").read_text(encoding="utf-8"))
    style = a.style or ct.get("motion", {}).get("style", "crawler/ant")
    skel, muster = style.split("/")
    if skel == "crawler":
        cmd = [sys.executable, str(ROOT / "scripts" / "crawler_pipeline.py"), str(c)] + \
              (["--name", a.name] if a.name else []) + (["--no-preview"] if a.no_preview else []) + \
              (["--style", a.style] if a.style else [])
        raise SystemExit(subprocess.call(cmd))
    name = a.name or "".join(p.capitalize() for p in c.name.split("_"))
    toml = str(c / "creature.toml")
    src = c / "raw" / "generate_model.glb"
    if not src.exists():
        raise SystemExit(f"{src} fehlt – erst scripts/tripo_run.py --steps generate laufen lassen.")
    rig_script = ROOT / "rigging" / f"{skel}_rig.py"
    clips_script = ROOT / "motions" / skel / muster / f"{muster}_clips.py"
    for f in (rig_script, clips_script):
        if not f.exists():
            raise SystemExit(f"{f} fehlt – Skelett/Muster noch nicht gebaut.")
    rig, out, uvdir = c / "rig", c / "output", c / "uv"
    R = ROOT / "rigging"
    # 1. UV-Prüfung
    if not (ROOT / "uv" / "textures" / "uv_checker.png").exists():
        subprocess.run([sys.executable, str(ROOT / "uv" / "biome_textures.py"), str(ROOT / "uv" / "textures")], check=True)
    blender(["--factory-startup", "-P", str(ROOT / "uv" / "uv_check.py"), "--", str(src), str(uvdir), toml],
            "UV-Prüfung", show=("UV_INSPECT", "UV_SCORE", "UV_CHOSEN", "Traceback", "Error"))
    subprocess.run([sys.executable, str(ROOT / "uv" / "uv_sheet.py"), str(uvdir)], check=True)
    uvrep = json.loads((uvdir / "uv_report.json").read_text(encoding="utf-8"))
    # 2. Rig + 3. Clips
    blender(["--factory-startup", "-P", str(rig_script), "--", str(uvdir / "model_uv.glb"), str(rig), toml], "Rig")
    if (R / "draw_rig.py").exists() and (rig / "rig_debug.json").exists():
        subprocess.run([sys.executable, str(R / "draw_rig.py"), str(rig)], check=True, capture_output=True)
    blender([str(rig / f"{skel}_rigged.blend"), "-P", str(clips_script), "--", str(rig), toml], f"Clips ({style})")
    clips_blend = rig / "clips.blend"
    report = json.loads((rig / "clips_report.json").read_text(encoding="utf-8"))
    # 4. Lückenprüfung (getrennte Teile, die in Ruhe aneinanderliegen)
    gcfg = tomllib.loads((R / "crawler_defaults.toml").read_text(encoding="utf-8")).get("gaps", {})
    blender([str(clips_blend), "-P", str(R / "check_gaps.py"), "--", str(rig / "gap_report.json"),
             str(gcfg.get("pair_eps", 0.015)), str(gcfg.get("max_opening", 0.015))], "Lückenprüfung")
    gaps = json.loads((rig / "gap_report.json").read_text(encoding="utf-8"))
    # 5. Vorschau-GIFs
    if not a.no_preview:
        anim = rig / "anim"
        shutil.rmtree(anim, ignore_errors=True)
        for clip in report["clips"]:
            d = anim / clip
            blender([str(clips_blend), "-P", str(R / "render_anim.py"), "--", str(d), "300", clip, "arpg,side"],
                    f"Vorschau {clip}", show=("Traceback", "Error"))
            subprocess.run([sys.executable, str(R / "make_gif.py"), str(d), "30", clip], check=True, capture_output=True)
            shutil.copy(d / f"{clip}.gif", anim / f"{clip}.gif")
            shutil.rmtree(d)
    # 6. Export + 7. Gegentest
    blender([str(clips_blend), "-P", str(R / "export_unity.py"), "--", str(out), name, toml], "Export")
    shutil.copy(rig / "events.json", out / f"{name}_events.json")
    ok = report["all_ok"] and gaps["ok"]
    for ext in ("fbx", "glb"):
        f = out / f"{name}.{ext}"
        blender(["--factory-startup", "-P", str(R / "verify_export.py"), "--", str(f), str(out / f"verify_{ext}.json")],
                f"Gegentest {ext.upper()}")
        v = json.loads((out / f"verify_{ext}.json").read_text(encoding="utf-8"))
        ok &= v["ok"] and len(v["actions"]) >= len(report["clips"])
    print("\nClip-Übersicht:")
    for clip, r in report["clips"].items():
        extra = r.get("move_speed_mps") and f"{r['move_speed_mps']} m/s" or \
            r.get("turn_speed_deg_s") and f"{r['turn_speed_deg_s']} °/s" or ""
        print(f"  {'✓' if r['ok'] else '✗'} {clip:28} {r['seconds']:>5} s  {'Loop' if r['loop'] else '    '}  "
              f"Dehnung {r.get('max_stretch', '-')}  {extra}")
    print(f"Gelenk-Lücken: max {gaps['max_opening_m'] * 100:.1f} cm (Grenze {gaps['threshold_m'] * 100:.1f} cm)")
    u = uvrep[uvrep["chosen"].split("_")[0]]
    print(f"UV: {uvrep['chosen']} · {u['islands']} Inseln · Abdeckung {u['coverage']:.0%} · Überlappung {u['overlap']:.1%}"
          + (f" · ⚠ {', '.join(uvrep['warnings'])}" if uvrep["warnings"] else ""))
    print(f"\n{'✓ ALLES OK' if ok else '✗ PRÜFUNG FEHLGESCHLAGEN'}  ·  Ausgabe: {out}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
