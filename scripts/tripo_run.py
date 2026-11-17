"""Tripo-Schritt der Pipeline: Bilder → Mesh+Textur → Rig-Check → Rig → Animation.

Aufruf:
  python scripts/tripo_run.py creatures/spinne_01               # alle Schritte
  python scripts/tripo_run.py creatures/spinne_01 --dry-run     # nur zeigen, was passieren würde (kostenlos)
  python scripts/tripo_run.py creatures/spinne_01 --steps rig,animate
  python scripts/tripo_run.py creatures/spinne_01 --force generate   # Schritt trotz Ergebnis neu ausführen

Bereits erfolgreiche Schritte mit gleichen Einstellungen werden übersprungen (keine doppelten Kosten).
Zustand + Task-IDs: <kreatur>/raw/tripo_state.json. Downloads: <kreatur>/raw/.
"""
import argparse
import hashlib
import json
import pathlib
import sys
import time
import urllib.parse

import requests

from common import load_creature, load_env

# .ai = internationale Plattform (Keys von platform.tripo3d.ai). Die Doku zeigt .com – das ist
# die China-Plattform und lehnt unsere Keys mit 401 ab.
API = "https://openapi.tripo3d.ai/v3"
STEPS = ["generate", "rig_check", "rig", "animate"]
VIEW_ORDER = ["front", "left", "back", "right"]
IMG_EXT = [".png", ".jpg", ".jpeg", ".webp"]
FAIL = {"failed", "cancelled", "banned", "expired"}
# Tripo-Laufzyklen je Rig-Typ (Stand 11/2026). Preset muss zum Skelett passen!
WALK_PRESETS = {
    "biped": "preset:walk", "quadruped": "preset:quadruped:walk", "hexapod": "preset:hexapod:walk",
    "octopod": "preset:octopod:walk", "serpentine": "preset:serpentine:march", "aquatic": "preset:aquatic:march",
}


class Tripo:
    def __init__(self, key):
        self.s = requests.Session()
        # User-Agent nötig, sonst blockt Cloudflare (Fehler 1010)
        self.s.headers.update({"Authorization": f"Bearer {key}", "User-Agent": "pipeline-client/1.0"})

    def _check(self, r):
        try:
            j = r.json()
        except ValueError:
            raise SystemExit(f"HTTP {r.status_code}: {r.text[:300]}")
        if r.status_code >= 400 or j.get("code") != 0:
            raise SystemExit(f"Tripo-Fehler HTTP {r.status_code}: {json.dumps(j, ensure_ascii=False)[:500]}")
        return j["data"]

    def balance(self):
        return self._check(self.s.get(f"{API}/account/balance", timeout=30))

    def upload(self, path):
        with open(path, "rb") as f:
            return self._check(self.s.post(f"{API}/files", files={"file": (path.name, f)}, timeout=120))["file_token"]

    def post(self, endpoint, body):
        return self._check(self.s.post(f"{API}{endpoint}", json=body, timeout=60))["task_id"]

    def wait(self, task_id, label, timeout=1800):
        t0, last = time.time(), None
        while True:
            d = self._check(self.s.get(f"{API}/tasks/{task_id}", timeout=30))
            st, pr = d.get("status"), d.get("progress")
            if (st, pr) != last:
                print(f"  [{label}] {st} {pr if pr is not None else ''}".rstrip(), flush=True)
                last = (st, pr)
            if st == "success":
                return d
            if st in FAIL:
                raise SystemExit(f"Task {label} endete mit Status '{st}': {json.dumps(d, ensure_ascii=False)[:500]}")
            if time.time() - t0 > timeout:
                raise SystemExit(f"Timeout bei {label} (Task {task_id}) – später mit gleichem Befehl erneut versuchen.")
            time.sleep(5)


def fingerprint(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]


def find_images(input_dir, views):
    found = {}
    for v in views:
        for ext in IMG_EXT:
            p = input_dir / f"{v}{ext}"
            if p.exists():
                found[v] = p
                break
    return found


def download_outputs(sess, output, raw_dir, prefix):
    saved = []
    for k, v in (output or {}).items():
        if isinstance(v, str) and v.startswith("http"):
            ext = pathlib.Path(urllib.parse.urlparse(v).path).suffix or ".bin"
            dst = raw_dir / f"{prefix}_{k.removesuffix('_url')}{ext}"
            r = sess.get(v, timeout=300)
            r.raise_for_status()
            dst.write_bytes(r.content)
            saved.append(dst.name)
    return saved


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("creature_dir")
    ap.add_argument("--steps", default=",".join(STEPS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", default="", help="Kommagetrennte Schritte, die neu laufen sollen")
    a = ap.parse_args()

    cdir = pathlib.Path(a.creature_dir).resolve()
    cfg, bp, _ = load_creature(cdir)
    steps = [s for s in a.steps.split(",") if s]
    force = {s for s in a.force.split(",") if s}
    for s in steps + list(force):
        if s not in STEPS:
            raise SystemExit(f"Unbekannter Schritt '{s}'. Erlaubt: {', '.join(STEPS)}")

    raw = cdir / "raw"
    raw.mkdir(exist_ok=True)
    state_file = raw / "tripo_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}

    def save():
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    def invalidate_after(step):
        for s in STEPS[STEPS.index(step) + 1:]:
            if s in state:
                print(f"  → Ergebnis von '{s}' ist jetzt veraltet und wird verworfen.")
                state.pop(s)

    def should_run(step, params):
        fp = fingerprint(params)
        prev = state.get(step)
        if prev and prev.get("fingerprint") == fp and step not in force:
            print(f"✓ {step}: schon erledigt (Task {prev['task_id']}), übersprungen.")
            return None
        if prev and step not in force:
            raise SystemExit(f"'{step}' wurde mit ANDEREN Einstellungen schon ausgeführt. "
                             f"Zum Neu-Ausführen (kostet Credits): --force {step}")
        return fp

    # ---------- Parameter vorbereiten ----------
    images = find_images(cdir / "input", VIEW_ORDER)
    if "front" not in images:
        raise SystemExit(f"Kein front-Bild gefunden in {cdir / 'input'} (front.png/.jpg/.webp).")
    t = dict(cfg["tripo"])
    for seed in ("model_seed", "texture_seed"):
        if not t.get(seed):
            t.pop(seed, None)
    img_sig = {v: hashlib.sha1(p.read_bytes()).hexdigest()[:12] for v, p in images.items()}
    gen_params = {"tripo": t, "images": img_sig}

    print(f"Kreatur: {cfg['name']}  ·  Bauplan: {cfg['bodyplan']}  ·  Bilder: {', '.join(images)}")
    if a.dry_run:
        mode = "multiview-to-model" if len(images) > 1 else "image-to-model"
        print(f"[dry-run] generate → POST /generation/{mode} mit {json.dumps(t, ensure_ascii=False)}")
        print(f"[dry-run] rig_check (kostenlos) → rig mit {json.dumps(cfg['rig'], ensure_ascii=False)}")
        used = state.get("rig", {}).get("rig_type", bp["rig_type"])
        print(f"[dry-run] animate → {cfg['animate']['presets']} (auto = {WALK_PRESETS.get(used) or 'keins'}, Rig-Typ {used})")
        print("[dry-run] Status:", {s: ("erledigt" if s in state else "offen") for s in STEPS})
        return

    key = load_env().get("TRIPO_API_KEY")
    if not key:
        raise SystemExit("TRIPO_API_KEY fehlt in .env")
    api = Tripo(key)
    bal0 = api.balance()["balance"]
    print(f"Guthaben vorher: {bal0} Credits")

    # ---------- 1. generate ----------
    if "generate" in steps and (fp := should_run("generate", gen_params)):
        invalidate_after("generate")
        tokens = {v: api.upload(p) for v, p in images.items()}
        print(f"  Hochgeladen: {', '.join(tokens)}")
        if len(tokens) > 1:
            body = dict(t, inputs=[{v: tokens[v]} for v in VIEW_ORDER if v in tokens])
            tid = api.post("/generation/multiview-to-model", body)
        else:
            body = dict(t, input=tokens["front"])
            tid = api.post("/generation/image-to-model", body)
        d = api.wait(tid, "generate")
        files = download_outputs(api.s, d.get("output"), raw, "generate")
        state["generate"] = {"task_id": tid, "fingerprint": fp, "credits": d.get("credits_consumed"), "files": files}
        save()
        print(f"  Gespeichert: {', '.join(files)}  ·  Credits: {d.get('credits_consumed')}")

    gen_id = state.get("generate", {}).get("task_id")

    # ---------- 2. rig_check (kostenlos) ----------
    if "rig_check" in steps and gen_id and (fp := should_run("rig_check", {"input": gen_id})):
        tid = api.post("/animations/rig-check", {"input": gen_id})
        out = api.wait(tid, "rig_check").get("output", {})
        state["rig_check"] = {"task_id": tid, "fingerprint": fp, **out}
        save()
        print(f"  Riggbar: {out.get('riggable')}  ·  empfohlener Typ: {out.get('rig_type')}")

    # ---------- 3. rig ----------
    if "rig" in steps and gen_id:
        rc = state.get("rig_check", {})
        if rc and not rc.get("riggable"):
            raise SystemExit("Rig-Check sagt: nicht riggbar. Bild/Pose verbessern und neu generieren.")
        rig_type = cfg["rig"]["rig_type"]
        if rig_type == "auto":
            # Bauplan = Entscheidung des Nutzers. Weicht der Rig-Check ab, VOR dem Bezahlen stoppen.
            rig_type = bp["rig_type"]
            if rc.get("rig_type") and rc["rig_type"] != rig_type:
                raise SystemExit(
                    f"STOPP: Rig-Check erkennt '{rc['rig_type']}', Bauplan sagt '{rig_type}'. "
                    f"Das Modell passt vermutlich nicht zum Bauplan (z. B. falsche Beinzahl). "
                    f"Modell prüfen, dann entweder neu generieren oder in creature.toml "
                    f"[rig] rig_type = \"{rc['rig_type']}\" setzen.")
        body = {"input": gen_id, "model": cfg["rig"]["model"], "rig_type": rig_type,
                "out_format": cfg["rig"]["out_format"]}
        if fp := should_run("rig", body):
            invalidate_after("rig")
            tid = api.post("/animations/rig", body)
            d = api.wait(tid, "rig")
            files = download_outputs(api.s, d.get("output"), raw, "rig")
            state["rig"] = {"task_id": tid, "fingerprint": fp, "rig_type": rig_type,
                            "credits": d.get("credits_consumed"), "files": files}
            save()
            print(f"  Gespeichert: {', '.join(files)}  ·  Credits: {d.get('credits_consumed')}")

    # ---------- 4. animate ----------
    rig_id = state.get("rig", {}).get("task_id")
    if "animate" in steps and rig_id:
        presets = cfg["animate"]["presets"]
        if presets == "auto":
            # Preset muss zum TATSÄCHLICHEN Rig-Typ passen, nicht zum Bauplan
            used = state["rig"].get("rig_type", bp["rig_type"])
            walk = WALK_PRESETS.get(used, "")
            presets = [walk] if walk else []
        if not presets:
            print("– animate: keine Presets für diesen Bauplan, übersprungen.")
        else:
            body = {"input": rig_id, "out_format": cfg["animate"]["out_format"],
                    "animate_in_place": cfg["animate"]["animate_in_place"]}
            body.update({"animation": presets[0]} if len(presets) == 1 else {"animations": presets[:5]})
            if fp := should_run("animate", body):
                tid = api.post("/animations/retarget", body)
                d = api.wait(tid, "animate")
                files = download_outputs(api.s, d.get("output"), raw, "animate")
                state["animate"] = {"task_id": tid, "fingerprint": fp, "presets": presets,
                                    "credits": d.get("credits_consumed"), "files": files}
                save()
                print(f"  Gespeichert: {', '.join(files)}  ·  Credits: {d.get('credits_consumed')}")

    bal1 = api.balance()["balance"]
    print(f"Guthaben nachher: {bal1} Credits (verbraucht: {round(float(bal0) - float(bal1), 2)})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
