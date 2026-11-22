"""Varianten-Baukasten – Blender headless (für den Unity-Knopf „In Blender bauen“ und für Skripte).

  & "D:\\Blender\\blender.exe" -b --factory-startup -P procedural/variantkit_blender/vk_headless.py -- <Befehl> [Optionen]

Befehle:
  bauen      --variante <pfad.variant.json> [--out <datei.bedeckung.json>] [--glb]
             Baut die Bedeckungs-Lagen auf der Basis in Ruhepose und schreibt <ExportName>.bedeckung.json
             (Standard: creatures/<NN>/output/varianten/<ExportName>/). Unity importiert die Datei automatisch.
  bausteine  [--typ <typ>] [--ueberschreiben]
             Startformen der Baustein-Bibliothek erzeugen (nur fehlende Typen, außer --ueberschreiben).
  bild       --variante <pfad> --out <ordner> [--clip Walk --bild 15]
             Prüfbild aus Blender (Statur + Bedeckung + Accessoires), ARPG-Ansicht.

Ausgabe-Zeilen für Unity: „VK_FORTSCHRITT <0..1> <Text>“, „VK_FERTIG <Pfad>“, „VK_FEHLER <Text>“ (Exit-Code 1).
"""
import math
import os
import sys
import time
import traceback

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from variantkit import vk_acc, vk_base, vk_cover, vk_json, vk_parts, vk_ui  # noqa: E402


def progress(f, text):
    print(f"VK_FORTSCHRITT {f:.2f} {text}", flush=True)


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def setup(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    doc = vk_json.VariantDoc.load(path)
    progress(0.1, "Basis laden")
    info = vk_base.find_base(doc.resolved.get("basis"))
    arm, ob = vk_base.load_into_scene(info)
    progress(0.25, "Analyse + Zonen")
    an = vk_base.Analysis(arm, ob)
    vk_cover.prepare_base(an, ob)
    coll = bpy.data.collections.get(vk_base.COLL_NAME)
    acc, pts, acc_info, acc_tris = vk_acc.build(an, arm, doc, coll)
    return doc, an, arm, ob, acc, pts, acc_info, acc_tris


def cmd_bauen(argv):
    t0 = time.time()
    path = os.path.abspath(arg(argv, "--variante"))
    doc, an, arm, ob, acc, pts, acc_info, acc_tris = setup(path)
    progress(0.4, "Masken")
    lagen = [l for l in doc.resolved["bedeckung"].get("lagen", []) if isinstance(l, dict) and l.get("an", True)][:2]
    overlap = vk_cover.update_masks(an, ob, lagen)
    progress(0.55, f"Lagen bauen ({len(lagen)})")
    vk_cover.sync_modifiers(an, arm, ob, doc, pts)
    out = arg(argv, "--out") or vk_ui.export_path(doc)
    progress(0.75, "Export")
    data = vk_cover.export_unity(an, ob, doc, out, vk_ui.WERKZEUG)
    if "--glb" in argv:
        progress(0.9, "GLB")
        vk_cover.export_glb(ob, arm, os.path.splitext(out)[0].replace(".bedeckung", "") + "_bedeckung.glb")
    klasse = doc.resolved.get("budget_klasse", "normal")
    bud = vk_cover.BUDGET_BEDECKUNG.get(klasse, 2000)
    print(f"VK_INFO Bedeckung {data['tris']['gesamt']} Tris (Budget {klasse} {bud}), {len(data['teile'])} Teile, "
          f"Überlappung {overlap * 100:.0f} %, Accessoires: {acc_info}, {time.time() - t0:.1f} s", flush=True)
    progress(1.0, "fertig")
    print(f"VK_FERTIG {out}", flush=True)


def cmd_bausteine(argv):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    done = vk_parts.generate_missing(only=arg(argv, "--typ"), overwrite="--ueberschreiben" in argv)
    print("VK_FERTIG " + ", ".join(done), flush=True)


def cmd_bild(argv):
    path = os.path.abspath(arg(argv, "--variante"))
    outdir = os.path.abspath(arg(argv, "--out", "."))
    doc, an, arm, ob, acc, pts, acc_info, acc_tris = setup(path)
    vk_base.apply_statur(an, arm, ob, doc.resolved["statur"])
    lagen = [l for l in doc.resolved["bedeckung"].get("lagen", []) if isinstance(l, dict) and l.get("an", True)][:2]
    vk_cover.update_masks(an, ob, lagen)
    vk_cover.sync_modifiers(an, arm, ob, doc, pts)
    scn = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    scn.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engines else engines[0]
    scn.render.resolution_x = scn.render.resolution_y = 768
    cam = bpy.data.objects.new("VK_Kamera", bpy.data.cameras.new("VK_Kamera"))
    scn.collection.objects.link(cam)
    scn.camera = cam
    sun = bpy.data.objects.new("VK_Sonne", bpy.data.lights.new("VK_Sonne", "SUN"))
    scn.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(40), 0, math.radians(30))
    sun.data.energy = 3.0
    w = bpy.data.worlds.new("VK_Welt")
    w.color = (0.4, 0.4, 0.42)
    scn.world = w
    from mathutils import Vector
    f = Vector(an.fwd)
    yaw = math.atan2(f.y, f.x)
    clip = arg(argv, "--clip")
    frame = int(arg(argv, "--bild", "0"))
    arm.animation_data_create()
    if clip:
        act = bpy.data.actions.get(f"Quadruped_Bear_{clip}") or bpy.data.actions.get(clip)
        arm.animation_data.action = act
        try:
            arm.animation_data.action_slot = act.slots[0]
        except Exception:
            pass
    else:
        arm.animation_data.action = None
    scn.frame_set(frame)
    for tag, az, el in (("arpg", 150, 50), ("seite", 90, 5)):
        a = yaw + math.radians(az)
        d = Vector((math.cos(math.radians(el)) * math.cos(a), math.cos(math.radians(el)) * math.sin(a), math.sin(math.radians(el))))
        cam.location = Vector((0, 0, 0.0)) + d * 3.2
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        scn.render.filepath = os.path.join(outdir, f"{doc.export_name}_blender_{tag}_{clip or 'ruhe'}{frame}.png")
        bpy.ops.render.render(write_still=True)
    print(f"VK_FERTIG {outdir}", flush=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cmd = argv[0] if argv else "bauen"
    try:
        {"bauen": cmd_bauen, "bausteine": cmd_bausteine, "bild": cmd_bild}[cmd](argv)
    except SystemExit:
        raise
    except Exception as ex:
        traceback.print_exc()
        print(f"VK_FEHLER {type(ex).__name__}: {ex}", flush=True)
        sys.exit(1)


main()
