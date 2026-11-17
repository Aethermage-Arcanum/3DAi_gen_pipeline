"""Komplette Nachbearbeitung einer Kreatur nach Tripo – für jedes Skelett, ein Befehl, kostenlos, lokal.

  python scripts/creature_pipeline.py creatures/<name> [--stage motion|full|check] [--style skelett/muster]
                                      [--work <ordner>] [--name Export] [--no-preview] [--unlock]

Stufen (siehe README "Zusammenarbeit"):
  motion  UV → Rig → Clips → Roh-GIFs in rig/anim/raw/   (keine Prüfung bremst, kein Export) → Nutzer beurteilt Bewegung
  full    UV → Rig → Clips → Lücken → GIFs in rig/anim/final/ → Export FBX/GLB → Gegentest → Fingerabdruck
  check   UV → Rig → Clips → Fingerabdruck   (für scripts/regression.py, nichts gerendert/exportiert)

Freigegebene Kreaturen (creatures/<name>/approved/) sind gesperrt: die Pipeline schreibt nichts in ihren
Ordner, außer mit --unlock. Mit --work <ordner> landen alle Ausgaben dort (die Kreatur bleibt unberührt).
Skelett/Muster aus creature.toml [motion] style = "<skelett>/<muster>":
  rigging/<skelett>_rig.py → motions/<skelett>/<muster>/<muster>_clips.py
"""
import argparse
import gzip
import json
import pathlib
import shutil
import subprocess
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_info  # noqa: E402

BLENDER = r"D:\Blender\blender.exe"


def blender(args, label, show=("CLIP ", "EXPORT_OK", "GAPS", "VERIFY", "RIG_", "QUAD_", "FINGERPRINT", "Traceback", "Error")):
    print(f"→ {label}", flush=True)
    r = subprocess.run([BLENDER, "-b", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    for l in r.stdout.splitlines():
        if l.startswith(show):
            print("   ", l[:300])
    if r.returncode != 0 or "Traceback" in r.stdout + r.stderr:
        print(r.stdout[-3000:], r.stderr[-2000:])
        raise SystemExit(f"Fehler in Schritt: {label}")
    return r.stdout


def render_gifs(clips_blend, clips, anim):
    R = ROOT / "rigging"
    shutil.rmtree(anim, ignore_errors=True)
    for clip in clips:
        d = anim / clip
        blender([str(clips_blend), "-P", str(R / "render_anim.py"), "--", str(d), "300", clip, "arpg,side"],
                f"Vorschau {clip}", show=("Traceback", "Error"))
        subprocess.run([sys.executable, str(R / "make_gif.py"), str(d), "30", clip], check=True, capture_output=True)
        shutil.copy(d / f"{clip}.gif", anim / f"{clip}.gif")
        shutil.rmtree(d)


def fingerprint(clips_blend, dest):
    tmp = dest.with_suffix("")                      # .json
    blender([str(clips_blend), "-P", str(ROOT / "rigging" / "pose_fingerprint.py"), "--", str(tmp)], "Fingerabdruck")
    dest.write_bytes(gzip.compress(tmp.read_bytes(), mtime=0))
    tmp.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("creature_dir")
    ap.add_argument("--stage", choices=("motion", "full", "check"), default="full")
    ap.add_argument("--style", default=None, help="anderes Muster testen → Ausgabe in style_tests/<muster>/")
    ap.add_argument("--work", default=None, help="alle Ausgaben in diesen Ordner statt in die Kreatur")
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--unlock", action="store_true", help="freigegebene Kreatur trotzdem neu bauen (überschreibt!)")
    a = ap.parse_args()
    c = pathlib.Path(a.creature_dir).resolve()
    ct = tomllib.loads((c / "creature.toml").read_text(encoding="utf-8"))
    own_style = ct.get("motion", {}).get("style", "hexapod/ant")
    style = a.style or own_style
    skel, muster = style.split("/")
    name = a.name or "".join(p.capitalize() for p in c.name.split("_"))

    # Ausgabeordner: Kreatur selbst, Stil-Test oder fremder Arbeitsordner
    base = pathlib.Path(a.work).resolve() if a.work else c
    uvdir, rig = base / "uv", base / "rig"
    clips_dir, out = rig, base / "output"
    if style != own_style:
        clips_dir = base / "style_tests" / muster
        out = clips_dir / "output"
        name = f"{name}_{muster.capitalize()}"
        if skel != own_style.split("/")[0]:            # fremdes Skelett → eigenes Rig im Testordner, Kreatur-Rig bleibt
            rig = clips_dir / "rig"
    if (c / "approved").exists() and not a.work and not a.unlock and style == own_style:
        raise SystemExit(f"{c.name} ist freigegeben (approved/) und damit gesperrt. Neu bauen nur mit --unlock "
                         f"(danach erneut freigeben) – oder mit --work <ordner> in einen Testordner.")

    toml = str(c / "creature.toml")
    src = c / "raw" / "generate_model.glb"
    if not src.exists():
        raise SystemExit(f"{src} fehlt – erst scripts/tripo_run.py --steps generate laufen lassen.")
    rig_script = ROOT / "rigging" / f"{skel}_rig.py"
    clips_script = ROOT / "motions" / skel / muster / f"{muster}_clips.py"
    for f in (rig_script, clips_script):
        if not f.exists():
            raise SystemExit(f"{f} fehlt – Skelett/Muster noch nicht gebaut.")
    R = ROOT / "rigging"
    for d in (uvdir, rig, clips_dir, out):
        d.mkdir(parents=True, exist_ok=True)

    # 1. UV-Prüfung
    if not (ROOT / "uv" / "textures" / "uv_checker.png").exists():
        subprocess.run([sys.executable, str(ROOT / "uv" / "biome_textures.py"), str(ROOT / "uv" / "textures")], check=True)
    blender(["--factory-startup", "-P", str(ROOT / "uv" / "uv_check.py"), "--", str(src), str(uvdir), toml],
            "UV-Prüfung", show=("UV_INSPECT", "UV_SCORE", "UV_CHOSEN", "Traceback", "Error"))
    if a.stage != "check":
        subprocess.run([sys.executable, str(ROOT / "uv" / "uv_sheet.py"), str(uvdir)], check=True)
    uvrep = json.loads((uvdir / "uv_report.json").read_text(encoding="utf-8"))
    # 2. Rig + 3. Clips
    blender(["--factory-startup", "-P", str(rig_script), "--", str(uvdir / "model_uv.glb"), str(rig), toml], "Rig")
    if a.stage != "check" and (R / "draw_rig.py").exists() and (rig / "rig_debug.json").exists():
        subprocess.run([sys.executable, str(R / "draw_rig.py"), str(rig)], check=True, capture_output=True)
    # 2b. Frei hängende Teile (nur mit [dangling] in der creature.toml): Markierung "_DANGLING" ins Mesh → Unity-Shader
    #     lässt sie ohne Knochen schwingen. Ohne Abschnitt bleibt das Rig-Blend unangetastet.
    if "dangling" in ct:
        blender([str(rig / f"{skel}_rigged.blend"), "-P", str(R / "dangling.py"), "--", toml, str(rig)]
                + ([] if a.stage == "check" else ["render"]), "Frei hängende Teile",
                show=("RIG_", "DANGLING", "Traceback", "Error"))
    blender([str(rig / f"{skel}_rigged.blend"), "-P", str(clips_script), "--", str(clips_dir), toml], f"Clips ({style})")
    clips_blend = next(p for p in (clips_dir / "clips.blend", clips_dir / f"{skel}_clips.blend") if p.exists())
    report = json.loads((clips_dir / "clips_report.json").read_text(encoding="utf-8"))
    build_info.write(clips_dir / "build_manifest.json", build_info.manifest(c, style))

    if a.stage == "check":
        fingerprint(clips_blend, clips_dir / "fingerprint.json.gz")
        print(f"\n✓ CHECK fertig · {clips_dir / 'fingerprint.json.gz'}")
        return
    if a.stage == "motion":
        if not a.no_preview:
            render_gifs(clips_blend, report["clips"], clips_dir / "anim" / "raw")
        print("\nRoh-Clips (Messwerte nur zur Info):")
        for clip, r in report["clips"].items():
            print(f"  {clip:30} {r['seconds']:>5} s  Dehnung {r.get('max_stretch', '-')}")
        print(f"\n✓ MOTION fertig – Roh-GIFs: {clips_dir / 'anim' / 'raw'}  → Bewegung vom Nutzer abnehmen lassen")
        return

    # 4. Lückenprüfung (getrennte Teile, die in Ruhe aneinanderliegen)
    gcfg = tomllib.loads((R / "gaps_defaults.toml").read_text(encoding="utf-8"))
    gcfg.update(ct.get("gaps", {}))                       # pro Kreatur überschreibbar (mit Begründung!)
    blender([str(clips_blend), "-P", str(R / "check_gaps.py"), "--", str(clips_dir / "gap_report.json"),
             str(gcfg.get("pair_eps", 0.015)), str(gcfg.get("max_opening", 0.015))], "Lückenprüfung")
    gaps = json.loads((clips_dir / "gap_report.json").read_text(encoding="utf-8"))
    # 5. Vorschau-GIFs (Endfassung; die Roh-Fassung aus --stage motion bleibt unberührt)
    if not a.no_preview:
        render_gifs(clips_blend, report["clips"], clips_dir / "anim" / "final")
    # 6. Export + 7. Gegentest + 8. Fingerabdruck
    blender([str(clips_blend), "-P", str(R / "export_unity.py"), "--", str(out), name, toml], "Export")
    shutil.copy(clips_dir / "events.json", out / f"{name}_events.json")
    ok = report["all_ok"] and gaps["ok"]
    for ext in ("fbx", "glb"):
        f = out / f"{name}.{ext}"
        blender(["--factory-startup", "-P", str(R / "verify_export.py"), "--", str(f), str(out / f"verify_{ext}.json")],
                f"Gegentest {ext.upper()}")
        v = json.loads((out / f"verify_{ext}.json").read_text(encoding="utf-8"))
        ok &= v["ok"] and len(v["actions"]) >= len(report["clips"])
    fingerprint(clips_blend, clips_dir / "fingerprint.json.gz")
    print("\nClip-Übersicht (Dehnung nur zur Info, bremst nichts):")
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
    print("Freigeben (sperrt die Kreatur): python scripts/approve.py " + str(c.relative_to(ROOT)).replace("\\", "/"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
