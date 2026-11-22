"""Kleiner Helfer, um Geometry-Nodes-Bäume per Python aufzubauen (lesbarer als nodes.new/links.new von Hand)."""
import bpy

SOCK = {"geo": "NodeSocketGeometry", "float": "NodeSocketFloat", "int": "NodeSocketInt", "bool": "NodeSocketBool",
        "vec": "NodeSocketVector", "obj": "NodeSocketObject", "mat": "NodeSocketMaterial", "str": "NodeSocketString"}


class NB:
    def __init__(self, ng):
        self.ng = ng
        self.N = ng.nodes
        self.Lk = ng.links
        self.gi = self.N.new("NodeGroupInput")
        self.go = self.N.new("NodeGroupOutput")
        self.ids = {}
        self._x = 0

    # ---- Schnittstelle
    def input(self, name, kind, default=None, mn=None, mx=None, desc=""):
        s = self.ng.interface.new_socket(name, in_out="INPUT", socket_type=SOCK[kind])
        if default is not None and hasattr(s, "default_value"):
            s.default_value = default
        if mn is not None and hasattr(s, "min_value"):
            s.min_value = mn
        if mx is not None and hasattr(s, "max_value"):
            s.max_value = mx
        if desc:
            s.description = desc
        self.ids[name] = s.identifier
        return self.gi.outputs[name]

    def output(self, name, kind):
        self.ng.interface.new_socket(name, in_out="OUTPUT", socket_type=SOCK[kind])
        return self.go.inputs[name]

    def g(self, name):
        return self.gi.outputs[name]

    # ---- Knoten
    def node(self, typ, ins=None, **props):
        nd = self.N.new(typ)
        nd.location = (self._x, 0)
        self._x += 40
        for k, v in props.items():
            setattr(nd, k, v)
        for key, val in (ins or {}).items():
            self.set(nd, key, val)
        return nd

    @staticmethod
    def sin(nd, key):
        if isinstance(key, int):
            return nd.inputs[key]
        for s in nd.inputs:
            if (s.name == key or s.identifier == key) and s.enabled:
                return s
        for s in nd.inputs:
            if s.name == key or s.identifier == key:
                return s
        raise KeyError(f"{nd.bl_idname}: Eingang '{key}' fehlt ({[s.name for s in nd.inputs]})")

    @staticmethod
    def out(nd, key=0):
        outs = [s for s in nd.outputs if s.enabled]
        if isinstance(key, int):
            return outs[key]
        for s in outs:
            if s.name == key:
                return s
        raise KeyError(f"{nd.bl_idname}: Ausgang '{key}' fehlt")

    def set(self, nd, key, val):
        s = self.sin(nd, key)
        if isinstance(val, bpy.types.NodeSocket):
            self.Lk.new(val, s)
        elif val is not None:
            s.default_value = val

    def link(self, a, b):
        self.Lk.new(a, b)

    # ---- Mathe
    def m(self, op, a, b=None, c=None):
        nd = self.node("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b, c)):
            if v is not None:
                self.set(nd, i, v)
        return nd.outputs[0]

    def v(self, op, a, b=None, c=None, scale=None):
        nd = self.node("ShaderNodeVectorMath", operation=op)
        for i, val in enumerate((a, b, c)):
            if val is not None:
                self.set(nd, i, val)
        if scale is not None:
            self.set(nd, 3, scale)
        return self.out(nd, 0)

    def xyz(self, x, y, z):
        return self.out(self.node("ShaderNodeCombineXYZ", {"X": x, "Y": y, "Z": z}))

    def sep(self, vec):
        nd = self.node("ShaderNodeSeparateXYZ", {"Vector": vec})
        return nd.outputs[0], nd.outputs[1], nd.outputs[2]

    def attr(self, name, dtype="FLOAT"):
        nd = self.node("GeometryNodeInputNamedAttribute", {"Name": name}, data_type=dtype)
        return self.out(nd, "Attribute")

    def store(self, geo, name, value, dtype="FLOAT", domain="POINT", sel=None):
        nd = self.node("GeometryNodeStoreNamedAttribute", data_type=dtype, domain=domain)
        self.set(nd, "Geometry", geo)
        self.set(nd, "Name", name)
        self.set(nd, "Value", value)
        if sel is not None:
            self.set(nd, "Selection", sel)
        return self.out(nd, "Geometry")

    def rnd(self, seed, mn=0.0, mx=1.0, dtype="FLOAT", ident=None):
        nd = self.node("FunctionNodeRandomValue", data_type=dtype)
        self.set(nd, "Min", mn)
        self.set(nd, "Max", mx)
        self.set(nd, "Seed", seed)
        if ident is not None:
            self.set(nd, "ID", ident)
        return self.out(nd, "Value")

    def cmp(self, a, b, op="EQUAL", dtype="INT"):
        nd = self.node("FunctionNodeCompare", data_type=dtype, operation=op)
        self.set(nd, "A", a)
        self.set(nd, "B", b)
        return self.out(nd, 0)

    def switch(self, kind, cond, false, true):
        nd = self.node("GeometryNodeSwitch", input_type=kind)
        self.set(nd, "Switch", cond)
        self.set(nd, "False", false)
        self.set(nd, "True", true)
        return self.out(nd, 0)

    def index_switch(self, kind, index, items):
        nd = self.node("GeometryNodeIndexSwitch", data_type=kind)
        while len([s for s in nd.inputs if s.identifier.startswith("Item_")]) < len(items):
            nd.index_switch_items.new()
        self.set(nd, "Index", index)
        for i, it in enumerate(items):
            self.set(nd, f"Item_{i}", it)
        return self.out(nd, 0)

    def pos(self):
        return self.out(self.node("GeometryNodeInputPosition"))

    def normal(self):
        return self.out(self.node("GeometryNodeInputNormal"))

    def index(self):
        return self.out(self.node("GeometryNodeInputIndex"))

    def join(self, *geos):
        nd = self.node("GeometryNodeJoinGeometry")
        for g in reversed(geos):
            self.link(g, nd.inputs[0])
        return self.out(nd)

    def set_pos(self, geo, position=None, offset=None, sel=None):
        nd = self.node("GeometryNodeSetPosition")
        self.set(nd, "Geometry", geo)
        if position is not None:
            self.set(nd, "Position", position)
        if offset is not None:
            self.set(nd, "Offset", offset)
        if sel is not None:
            self.set(nd, "Selection", sel)
        return self.out(nd)

    def transform(self, geo, t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1)):
        nd = self.node("GeometryNodeTransform")
        self.set(nd, "Geometry", geo)
        self.set(nd, "Translation", t)
        self.set(nd, "Rotation", r)
        self.set(nd, "Scale", s)
        return self.out(nd)

    def delete(self, geo, sel, domain="POINT"):
        nd = self.node("GeometryNodeDeleteGeometry", domain=domain)
        self.set(nd, "Geometry", geo)
        self.set(nd, "Selection", sel)
        return self.out(nd)

    def cone(self, verts, r_top, r_bot, depth=1.0, segs=1, fill="NONE"):
        nd = self.node("GeometryNodeMeshCone", {"Vertices": verts, "Side Segments": segs, "Radius Top": r_top,
                                                 "Radius Bottom": r_bot, "Depth": depth})
        try:
            nd.fill_type = fill
        except Exception:
            pass
        return self.out(nd, "Mesh")

    def finish(self, geo):
        self.link(geo, self.go.inputs[0])


def new_group(name):
    old = bpy.data.node_groups.get(name)
    if old is not None:
        bpy.data.node_groups.remove(old)
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    return ng, NB(ng)


def _mod_inputs(mod):
    props = getattr(mod, "properties", None)
    return props.inputs if props is not None and hasattr(props, "inputs") else None


def set_mod_input(mod, ng_ids, name, value):
    """Eingang eines Geometry-Nodes-Modifiers setzen (Blender 5: mod.properties.inputs.<Socket_n>, älter: mod[id])."""
    ident = ng_ids[name]
    inp = _mod_inputs(mod)
    if inp is not None:
        slot = getattr(inp, ident)
        try:
            cur = slot.value
        except Exception:
            cur = None
        try:
            if cur is not None and not isinstance(value, bpy.types.ID) and not isinstance(cur, bpy.types.ID):
                if hasattr(cur, "__len__") and not isinstance(cur, str):
                    if all(abs(a - b) < 1e-9 for a, b in zip(cur, value)):
                        return False
                elif cur == value:
                    return False
        except Exception:
            pass
        slot.value = value
        return True
    mod[ident] = value
    return True


def get_mod_input(mod, ng_ids, name):
    ident = ng_ids[name]
    inp = _mod_inputs(mod)
    if inp is not None:
        return getattr(inp, ident).value
    return mod[ident]
