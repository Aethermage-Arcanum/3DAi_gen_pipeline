"""Startet Blender mit dem Varianten-Panel (ohne Installation).

Doppelklick auf Varianten_Blender.cmd, oder:
  & "D:\Blender\blender.exe" --python procedural/variantkit_blender/vk_start.py [-- --variante <pfad.variant.json>]
Danach im 3D-Fenster die Taste N drücken → Reiter „Variante“.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import variantkit  # noqa: E402

try:
    variantkit.unregister()
except Exception:
    pass
variantkit.register()


def _start():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    scn = bpy.context.scene
    # leere Szene: Standard-Würfel, Licht und Kamera weg
    for name in ("Cube", "Light", "Camera"):
        ob = bpy.data.objects.get(name)
        if ob is not None:
            bpy.data.objects.remove(ob, do_unlink=True)
    path = argv[argv.index("--variante") + 1] if "--variante" in argv else None
    if path:
        bpy.ops.vk.laden(path=os.path.abspath(path))
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == "VIEW_3D":
                a.spaces.active.show_region_ui = True
                for r in a.regions:
                    if r.type == "UI":
                        try:
                            r.active_panel_category = "Variante"
                        except Exception:
                            pass
                if path:
                    with bpy.context.temp_override(window=w, area=a):
                        bpy.ops.vk.arpg()
    return None


if not bpy.app.background:
    bpy.app.timers.register(_start, first_interval=0.5)
print("[VariantKit] Panel „Variante“ geladen (3D-Fenster, Taste N).")
