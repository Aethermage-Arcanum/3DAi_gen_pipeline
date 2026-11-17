"""Baut das Geometry-Nodes-System "Monster Anbauteile" (Stacheln + Panzerplatten) in Blender.

Wird von anderen Blender-Skripten importiert:  from addon_nodes import build_addon_group
Alle Regler erscheinen als normale Modifier-Slider am Objekt – ohne Plugin, für jeden editierbar.

Achsen-Konvention (wie Blender/Tripo-Import): Kopf zeigt nach -Y, oben ist +Z.
"""
import math
import bpy

GROUP_NAME = "Monster Anbauteile"

# (Name, Typ, Default, Min, Max, Beschreibung) – das sind die Slider.
SLIDERS = {
    "Stacheln": [
        ("Stacheln An", "BOOL", True, None, None, "Stacheln ein/aus"),
        ("Stachel Dichte", "FLOAT", 6.0, 0.0, 200.0, "Max. Stacheln pro m² (vor Masken)"),
        ("Stachel Abstand", "FLOAT", 0.18, 0.01, 2.0, "Mindestabstand zwischen Stacheln"),
        ("Stachel Länge", "FLOAT", 0.45, 0.01, 3.0, "Länge in m"),
        ("Stachel Breite", "FLOAT", 0.08, 0.005, 1.0, "Radius am Fuß in m"),
        ("Stachel Kanten", "INT", 4, 3, 12, "Facetten pro Stachel (Polygon-Kosten!)"),
        ("Stachel Neigung", "FLOAT", 0.6, -2.0, 2.0, "Neigung nach hinten (0 = senkrecht zur Haut)"),
        ("Stachel Zufall Größe", "FLOAT", 0.4, 0.0, 1.0, "Größenstreuung 0..1"),
        ("Stachel Abdeckung", "FLOAT", 0.4, 0.0, 1.0, "0 = nur ganz oben, 0.5 = obere Hälfte, 1 = überall"),
        ("Stachel Kammbreite", "FLOAT", 0.12, 0.0, 10.0, "Breite des Streifens entlang der Mittellinie (groß = überall)"),
        ("Stachel Seed", "INT", 1, 0, 100000, "Zufalls-Seed"),
    ],
    "Platten": [
        ("Platten An", "BOOL", False, None, None, "Panzerplatten ein/aus"),
        ("Platten Dichte", "FLOAT", 40.0, 0.0, 500.0, "Max. Platten pro m²"),
        ("Platten Abstand", "FLOAT", 0.16, 0.01, 2.0, "Mindestabstand zwischen Plattenmitten"),
        ("Platten Größe", "FLOAT", 0.13, 0.01, 2.0, "Radius in m"),
        ("Platten Streckung", "FLOAT", 1.4, 0.3, 4.0, "Länglich in Laufrichtung (1 = rund)"),
        ("Platten Dicke", "FLOAT", 0.035, 0.001, 0.5, "Dicke in m"),
        ("Platten Kanten", "INT", 6, 3, 12, "Facetten pro Platte"),
        ("Platten Schuppung", "FLOAT", 0.5, -2.0, 2.0, "Neigung nach hinten → Schuppen-Überlappung"),
        ("Platten Zufall Größe", "FLOAT", 0.25, 0.0, 1.0, "Größenstreuung 0..1"),
        ("Platten Abdeckung", "FLOAT", 0.45, 0.0, 1.0, "0 = nur ganz oben, 1 = überall"),
        ("Platten Seed", "INT", 7, 0, 100000, "Zufalls-Seed"),
    ],
    "Materialien": [
        ("Körper Material", "MATERIAL", None, None, None, ""),
        ("Stachel Material", "MATERIAL", None, None, None, ""),
        ("Platten Material", "MATERIAL", None, None, None, ""),
        ("Flat Shading", "BOOL", True, None, None, "Facettierter Low-Poly-Look"),
    ],
}

SOCKET_TYPES = {"FLOAT": "NodeSocketFloat", "INT": "NodeSocketInt", "BOOL": "NodeSocketBool",
                "MATERIAL": "NodeSocketMaterial"}


class G:
    """Kleiner Helfer, damit der Node-Aufbau lesbar bleibt."""

    def __init__(self, ng):
        self.ng, self.x = ng, 0

    def node(self, idname, **props):
        n = self.ng.nodes.new(idname)
        for k, v in props.items():
            setattr(n, k, v)
        n.location = (self.x, 0)
        self.x += 200
        return n

    def link(self, a, b):
        self.ng.links.new(a, b)

    def math(self, op, a, b=None):
        n = self.node("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.link(v, n.inputs[i])
        return n.outputs[0]

    def vmath(self, op, a, b=None, scale=None):
        n = self.node("ShaderNodeVectorMath", operation=op)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (tuple, list)):
                n.inputs[i].default_value = v
            else:
                self.link(v, n.inputs[i])
        if scale is not None:
            sock = n.inputs["Scale"]
            if isinstance(scale, (int, float)):
                sock.default_value = scale
            else:
                self.link(scale, sock)
        return n.outputs["Vector"]

    def map_range(self, value, fmin, fmax, tmin, tmax):
        n = self.node("ShaderNodeMapRange", clamp=True)
        for name, v in (("Value", value), ("From Min", fmin), ("From Max", fmax), ("To Min", tmin), ("To Max", tmax)):
            sock = n.inputs[name]
            if isinstance(v, (int, float)):
                sock.default_value = v
            else:
                self.link(v, sock)
        return n.outputs["Result"]

    def combine(self, x=0.0, y=0.0, z=0.0):
        n = self.node("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.link(v, n.inputs[i])
        return n.outputs[0]

    def random(self, vmin, vmax, seed):
        n = self.node("FunctionNodeRandomValue", data_type="FLOAT")
        n.inputs["Min"].default_value = vmin
        if isinstance(vmax, (int, float)):
            n.inputs["Max"].default_value = vmax
        else:
            self.link(vmax, n.inputs["Max"])
        self.link(seed, n.inputs["Seed"])
        return n.outputs["Value"]


def _coverage_mask(g, coverage):
    """1 auf Flächen, die genug nach oben zeigen. coverage 0 → nur Spitze, 0.5 → obere Hälfte, 1 → alles."""
    nz = g.node("ShaderNodeSeparateXYZ")
    g.link(g.node("GeometryNodeInputNormal").outputs["Normal"], nz.inputs[0])
    threshold = g.math("SUBTRACT", 1.0, g.math("MULTIPLY", coverage, 2.0))
    return g.map_range(nz.outputs["Z"], threshold, g.math("ADD", threshold, 0.25), 0.0, 1.0)


def _scatter(g, mesh, density, spacing, density_factor, seed):
    d = g.node("GeometryNodeDistributePointsOnFaces", distribute_method="POISSON")
    g.link(mesh, d.inputs["Mesh"])
    g.link(spacing, d.inputs["Distance Min"])
    g.link(density, d.inputs["Density Max"])
    g.link(density_factor, d.inputs["Density Factor"])
    g.link(seed, d.inputs["Seed"])
    return d


def _lean_rotation(g, normal, lean):
    """Richtung = Normale + Neigung nach hinten (+Y), daraus eine Rotation mit Z entlang der Richtung."""
    direction = g.vmath("NORMALIZE", g.vmath("ADD", normal, g.vmath("SCALE", (0, 1, 0), scale=lean)))
    al = g.node("FunctionNodeAlignRotationToVector", axis="Z")
    g.link(direction, al.inputs["Vector"])
    return al.outputs["Rotation"]


def build_addon_group():
    if GROUP_NAME in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[GROUP_NAME])
    ng = bpy.data.node_groups.new(GROUP_NAME, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    for panel_name, sliders in SLIDERS.items():
        panel = ng.interface.new_panel(panel_name)
        for name, typ, default, vmin, vmax, desc in sliders:
            s = ng.interface.new_socket(name, in_out="INPUT", socket_type=SOCKET_TYPES[typ], parent=panel)
            s.description = desc
            if default is not None:
                s.default_value = default
            if vmin is not None:
                s.min_value, s.max_value = vmin, vmax

    g = G(ng)
    gi = g.node("NodeGroupInput")
    go = g.node("NodeGroupOutput")
    I = gi.outputs
    body = I["Geometry"]

    # ---------------- Stacheln ----------------
    # Kamm-Maske: Abstand zur Mittellinie x=0 (Rückgrat). Später: Abstand zu den Wirbelsäulen-Knochen des Rigs.
    sx = g.node("ShaderNodeSeparateXYZ")
    g.link(g.node("GeometryNodeInputPosition").outputs["Position"], sx.inputs[0])
    absx = g.math("ABSOLUTE", sx.outputs["X"])
    ridge = g.map_range(absx, I["Stachel Kammbreite"], g.math("ADD", g.math("MULTIPLY", I["Stachel Kammbreite"], 1.5), 0.02), 1.0, 0.0)
    sp_mask = g.math("MULTIPLY", _coverage_mask(g, I["Stachel Abdeckung"]), ridge)

    sp_pts = _scatter(g, body, I["Stachel Dichte"], I["Stachel Abstand"], sp_mask, I["Stachel Seed"])
    cone = g.node("GeometryNodeMeshCone", fill_type="NONE")
    g.link(I["Stachel Kanten"], cone.inputs["Vertices"])
    cone.inputs["Radius Top"].default_value = 0.0
    cone.inputs["Radius Bottom"].default_value = 1.0
    cone.inputs["Depth"].default_value = 1.0
    cone_up = g.node("GeometryNodeTransform")  # Fußpunkt auf die Haut setzen
    g.link(cone.outputs["Mesh"], cone_up.inputs["Geometry"])
    cone_up.inputs["Translation"].default_value = (0, 0, 0.45)  # etwas in die Haut versenkt
    sp_rand = g.math("ADD", 1.0, g.random(0.0, I["Stachel Zufall Größe"], I["Stachel Seed"]))
    sp_rand = g.math("SUBTRACT", sp_rand, g.math("MULTIPLY", I["Stachel Zufall Größe"], 0.5))
    sp_scale = g.combine(g.math("MULTIPLY", I["Stachel Breite"], sp_rand),
                         g.math("MULTIPLY", I["Stachel Breite"], sp_rand),
                         g.math("MULTIPLY", I["Stachel Länge"], sp_rand))
    sp_inst = g.node("GeometryNodeInstanceOnPoints")
    g.link(sp_pts.outputs["Points"], sp_inst.inputs["Points"])
    g.link(cone_up.outputs["Geometry"], sp_inst.inputs["Instance"])
    g.link(_lean_rotation(g, sp_pts.outputs["Normal"], I["Stachel Neigung"]), sp_inst.inputs["Rotation"])
    g.link(sp_scale, sp_inst.inputs["Scale"])
    sp_real = g.node("GeometryNodeRealizeInstances")
    g.link(sp_inst.outputs["Instances"], sp_real.inputs["Geometry"])
    sp_mat = g.node("GeometryNodeSetMaterial")
    g.link(sp_real.outputs["Geometry"], sp_mat.inputs["Geometry"])
    g.link(I["Stachel Material"], sp_mat.inputs["Material"])
    sp_sw = g.node("GeometryNodeSwitch", input_type="GEOMETRY")
    g.link(I["Stacheln An"], sp_sw.inputs["Switch"])
    g.link(sp_mat.outputs["Geometry"], sp_sw.inputs["True"])

    # ---------------- Platten ----------------
    pl_pts = _scatter(g, body, I["Platten Dichte"], I["Platten Abstand"],
                      _coverage_mask(g, I["Platten Abdeckung"]), I["Platten Seed"])
    cyl = g.node("GeometryNodeMeshCylinder", fill_type="NGON")
    g.link(I["Platten Kanten"], cyl.inputs["Vertices"])
    cyl.inputs["Radius"].default_value = 1.0
    cyl.inputs["Depth"].default_value = 1.0
    cyl_up = g.node("GeometryNodeTransform")
    g.link(cyl.outputs["Mesh"], cyl_up.inputs["Geometry"])
    cyl_up.inputs["Translation"].default_value = (0, 0, 0.3)
    pl_rand = g.math("ADD", 1.0, g.random(0.0, I["Platten Zufall Größe"], I["Platten Seed"]))
    pl_rand = g.math("SUBTRACT", pl_rand, g.math("MULTIPLY", I["Platten Zufall Größe"], 0.5))
    pl_r = g.math("MULTIPLY", I["Platten Größe"], pl_rand)
    pl_scale = g.combine(pl_r, g.math("MULTIPLY", pl_r, I["Platten Streckung"]), I["Platten Dicke"])
    pl_inst = g.node("GeometryNodeInstanceOnPoints")
    g.link(pl_pts.outputs["Points"], pl_inst.inputs["Points"])
    g.link(cyl_up.outputs["Geometry"], pl_inst.inputs["Instance"])
    g.link(_lean_rotation(g, pl_pts.outputs["Normal"], I["Platten Schuppung"]), pl_inst.inputs["Rotation"])
    g.link(pl_scale, pl_inst.inputs["Scale"])
    pl_real = g.node("GeometryNodeRealizeInstances")
    g.link(pl_inst.outputs["Instances"], pl_real.inputs["Geometry"])
    pl_mat = g.node("GeometryNodeSetMaterial")
    g.link(pl_real.outputs["Geometry"], pl_mat.inputs["Geometry"])
    g.link(I["Platten Material"], pl_mat.inputs["Material"])
    pl_sw = g.node("GeometryNodeSwitch", input_type="GEOMETRY")
    g.link(I["Platten An"], pl_sw.inputs["Switch"])
    g.link(pl_mat.outputs["Geometry"], pl_sw.inputs["True"])

    # ---------------- Körper + Zusammenführen ----------------
    body_mat = g.node("GeometryNodeSetMaterial")
    g.link(body, body_mat.inputs["Geometry"])
    g.link(I["Körper Material"], body_mat.inputs["Material"])
    join = g.node("GeometryNodeJoinGeometry")
    for sock in (pl_sw.outputs[0], sp_sw.outputs[0], body_mat.outputs["Geometry"]):
        g.link(sock, join.inputs["Geometry"])
    shade = g.node("GeometryNodeSetShadeSmooth")
    g.link(join.outputs["Geometry"], shade.inputs["Mesh"])
    flat = g.node("FunctionNodeBooleanMath", operation="NOT")
    g.link(I["Flat Shading"], flat.inputs[0])
    g.link(flat.outputs[0], shade.inputs["Shade Smooth"])
    g.link(shade.outputs["Mesh"], go.inputs["Geometry"])
    return ng


def socket_ids(ng):
    """Name → Identifier, um Modifier-Werte per Name zu setzen."""
    return {it.name: it.identifier for it in ng.interface.items_tree
            if getattr(it, "item_type", "") == "SOCKET" and it.in_out == "INPUT"}


def set_input(mod, identifier, value):
    """Blender 5.x: mod.properties.inputs.<id>.value · ältere Versionen: mod[id]."""
    props = getattr(mod, "properties", None)
    if props is not None and hasattr(props, "inputs"):
        getattr(props.inputs, identifier).value = value
    else:
        mod[identifier] = value


def apply_settings(obj, mod, settings):
    ids = socket_ids(mod.node_group)
    for name, value in settings.items():
        if name not in ids:
            raise KeyError(f"Unbekannter Slider '{name}'. Verfügbar: {', '.join(ids)}")
        set_input(mod, ids[name], value)
    obj.update_tag()
