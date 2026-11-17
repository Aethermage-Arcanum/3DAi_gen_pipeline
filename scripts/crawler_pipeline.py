"""Komplette Krabbler-Nachbearbeitung für eine Kreatur – kostenlos, lokal, wiederholbar.

  python scripts/crawler_pipeline.py creatures/chitin_crawler [--name ChitinCrawler] [--no-preview]

Schritte (alle per Blender headless):
  0. uv/uv_check.py                             UV-Prüfung, Biom-Testtexturen            → uv/model_uv.glb
  1. rigging/crawler_rig.py                     Anatomie erkennen, Standard-Skelett, Gewichte → rig/crawler_rigged.blend
  2. motions/<skelett>/<muster>/*_clips.py      alle Clips des Bewegungsmusters + Selbstprüfung → rig/crawler_clips.blend
  3. rigging/check_gaps.py                      Gelenk-Lücken in allen Clips                → rig/gap_report.json
  4. rigging/render_anim.py + make_gif.py       Vorschau-GIF pro Clip                       → rig/anim/<Clip>.gif
  5. rigging/export_unity.py                    FBX + GLB mit allen Clips                    → output/
  6. rigging/verify_export.py                   Gegentest der Exporte                        → output/verify_*.json
Eingabe: raw/generate_model.glb (Tripo, nur Mesh + Textur).
Einstellungen: rigging/crawler_defaults.toml (Rig) · motions/<skelett>/<muster>/style.toml (Bewegung),
pro Kreatur überschreibbar in creature.toml unter [crawler.*] bzw. [motion.*].
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


def blender(args, label, show=("CLIP ", "EXPORT_OK", "GAPS", "VERIFY", "Traceback", "Error")):
    print(f"→ {label}", flush=True)
    r = subprocess.run([BLENDER, "-b", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    for l in r.stdout.splitlines():
        if l.startswith(show):
            print("   ", l[:260])
    if r.returncode != 0 or "Traceback" in r.stdout + r.stderr:
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
    style = tomllib.loads((c / "creature.toml").read_text(encoding="utf-8")).get("motion", {}).get("style", "crawler/ant")
    skel, muster = style.split("/")
    clips_script = ROOT / "motions" / skel / muster / f"{muster}_clips.py"
    rig, out = c / "rig", c / "output"
    src = c / "raw" / "generate_model.glb"
    if not src.exists():
        raise SystemExit(f"{src} fehlt – erst scripts/tripo_run.py --steps generate laufen lassen.")
    R = ROOT / "rigging"
    # 0. UV-Prüfung direkt nach Tripo (Tripo-UV vs. Smart UV, Biom-Testtexturen)
    uvdir = c / "uv"
    if not (ROOT / "uv" / "textures" / "uv_checker.png").exists():
        subprocess.run([sys.executable, str(ROOT / "uv" / "biome_textures.py"), str(ROOT / "uv" / "textures")], check=True)
    blender(["--factory-startup", "-P", str(ROOT / "uv" / "uv_check.py"), "--", str(src), str(uvdir), toml],
            "UV-Prüfung", show=("UV_TRIPO", "UV_SMART", "UV_CHOSEN", "Traceback", "Error"))
    uvrep = json.loads((uvdir / "uv_report.json").read_text(encoding="utf-8"))
    subprocess.run([sys.executable, "-c", (
        "import sys;from PIL import Image;d=sys.argv[1];L=sys.argv[2:];"
        "I=[[Image.open(f'{d}/uv_{l}_{v}.png').convert('RGB').resize((360,360)) for v in ('arpg','side')] for l in L];"
        "s=Image.new('RGB',(360*len(L),720));[ (s.paste(a,(i*360,0)),s.paste(b,(i*360,360))) for i,(a,b) in enumerate(I)];"
        "s.save(f'{d}/uv_preview.png')"), str(uvdir)] + [r.split("_")[1] for r in uvrep["renders"][::2]], check=True)
    src = uvdir / "model_uv.glb"
    blender(["--factory-startup", "-P", str(R / "crawler_rig.py"), "--", str(src), str(rig), toml], "Rig")
    blender([str(rig / "crawler_rigged.blend"), "-P", str(clips_script), "--", str(rig), toml], f"Clips ({style})")
    clips_blend = rig / "crawler_clips.blend"
    gcfg = tomllib.loads((R / "crawler_defaults.toml").read_text(encoding="utf-8")).get("gaps", {})
    blender([str(clips_blend), "-P", str(R / "check_gaps.py"), "--", str(rig / "gap_report.json"),
             str(gcfg.get("pair_eps", 0.015)), str(gcfg.get("max_opening", 0.015))], "Lückenprüfung (alle Clips)")
    report = json.loads((rig / "clips_report.json").read_text(encoding="utf-8"))
    if not a.no_preview:
        anim = rig / "anim"
        shutil.rmtree(anim, ignore_errors=True)
        for clip in report["clips"]:
            d = anim / clip
            blender([str(clips_blend), "-P", str(R / "render_anim.py"), "--", str(d), "300", clip, "arpg,side"],
                    f"Vorschau {clip}", show=("Traceback", "Error"))
            subprocess.run([sys.executable, str(R / "make_gif.py"), str(d), "30", clip], check=True,
                           capture_output=True)
            shutil.copy(d / f"{clip}.gif", anim / f"{clip}.gif")
            shutil.rmtree(d)
    blender([str(clips_blend), "-P", str(R / "export_unity.py"), "--", str(out), name, toml], "Export")
    shutil.copy(rig / "events.json", out / f"{name}_events.json")
    ok = report["all_ok"]
    for ext in ("fbx", "glb"):
        f = out / f"{name}.{ext}"
        blender(["--factory-startup", "-P", str(R / "verify_export.py"), "--", str(f), str(out / f"verify_{ext}.json")],
                f"Gegentest {ext.upper()}")
        v = json.loads((out / f"verify_{ext}.json").read_text(encoding="utf-8"))
        ok &= v["ok"] and len(v["actions"]) >= len(report["clips"])
    gaps = json.loads((rig / "gap_report.json").read_text(encoding="utf-8"))
    ok &= gaps["ok"]
    print("\nClip-Übersicht:")
    for clip, r in report["clips"].items():
        extra = r.get("move_speed_mps") and f"{r['move_speed_mps']} m/s" or \
            r.get("turn_speed_deg_s") and f"{r['turn_speed_deg_s']} °/s" or ""
        print(f"  {'✓' if r['ok'] else '✗'} {clip:24} {r['seconds']:>5} s  {'Loop' if r['loop'] else '    '}  {extra}")
    print(f"Gelenk-Lücken: max {gaps['max_opening_m'] * 100:.1f} cm (Grenze {gaps['threshold_m'] * 100:.1f} cm)")
    u = uvrep[uvrep["chosen"].split("_")[0]]
    print(f"UV: {uvrep['chosen']} · {u['islands']} Inseln · Abdeckung {u['coverage']:.0%} · Überlappung "
          f"{u['overlap']:.1%} · Dichte-Ausreißer {u['density_outlier_fraction']:.1%} · Winkel {u['angle_distortion_deg']}°"
          + (f" · ⚠ {', '.join(uvrep['warnings'])}" if uvrep["warnings"] else ""))
    print(f"\n{'✓ ALLES OK' if ok else '✗ PRÜFUNG FEHLGESCHLAGEN'}  ·  Ausgabe: {out}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
