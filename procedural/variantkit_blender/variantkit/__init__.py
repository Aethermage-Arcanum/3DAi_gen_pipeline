"""Varianten-Baukasten – Blender-Teil (Meilenstein 2).

Panel „Variante“ in der Seitenleiste (N) des 3D-Fensters: Varianten-Datei laden/speichern, Statur, Bedeckungs-Lagen
(Fell, Federn, Stacheln, Platten per Geometry Nodes, live), Tris-Budget, Accessoires aus Unity anzeigen,
Baustein-Werkbank. Nur Blender + Python-Standardbibliothek + numpy (in Blender enthalten), kein Fremd-Plugin.
Kurzanleitung: docs/VARIANTEN_BAUKASTEN.md, Teil C.
"""
bl_info = {
    "name": "Varianten-Baukasten (Kreaturen)",
    "author": "3D-AI-Pipeline",
    "version": (0, 2, 0),
    "blender": (4, 2, 0),
    "location": "3D-Fenster › Seitenleiste (N) › Variante",
    "description": "Statur, Bedeckung (Geometry Nodes) und Baustein-Werkbank für Varianten-Dateien",
    "category": "Object",
}



def register():
    import importlib
    from . import vk_json, vk_nodes, vk_base, vk_cover, vk_parts, vk_acc, vk_ui
    for m in (vk_json, vk_nodes, vk_base, vk_cover, vk_parts, vk_acc, vk_ui):
        importlib.reload(m)   # erneutes Ausführen von vk_start.py lädt geänderten Code
    vk_ui.register()


def unregister():
    from . import vk_ui
    vk_ui.unregister()
