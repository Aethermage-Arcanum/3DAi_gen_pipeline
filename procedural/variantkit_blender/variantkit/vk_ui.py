"""Panel „Variante“ in der Seitenleiste (N) des 3D-Fensters: Varianten-Datei laden/speichern, Statur, Bedeckungs-Lagen
(live per Geometry Nodes, auch während ein Clip läuft), Tris-Budget, Accessoires aus Unity anzeigen, Baustein-Werkbank."""
import os

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty,
                       StringProperty)

from . import vk_acc, vk_base, vk_cover, vk_json, vk_parts

WERKZEUG = "0.2.0"

# ------------------------------------------------------------------------------------------------ Zustand (Sitzung)
S = {"doc": None, "an": None, "arm": None, "ob": None, "acc": None, "pts": None, "acc_info": "", "acc_tris": 0,
     "loading": False, "pending": set(), "tris": {}, "teile": {}, "overlap": 0.0, "disk_rev": None}

# Statur-Regler: (Feld, Name, Typ, Regler-Min, Regler-Max, grün-Min, grün-Max, gelb-Min, gelb-Max) – wie Unity VkSpec
STATUR = [
    ("groesse", "Gesamtgröße", "G", 0.5, 2.0, 0.5, 2.0, 0.5, 2.0),
    ("koerper_laenge", "Körperlänge", "K", 0.8, 1.2, 0.9, 1.1, 0.8, 1.2),
    ("rumpf_hoehe", "Rumpfhöhe", "S", 0.6, 1.3, 0.75, 1.3, 0.6, 1.3),
    ("rumpf_dicke", "Rumpfdicke", "S", 0.8, 1.25, 0.8, 1.15, 0.8, 1.25),
    ("buckel", "Buckel", "S", 0.0, 1.6, 0.0, 1.6, 0.0, 1.6),
    ("glied_dicke", "Gliederdicke", "S", 0.8, 1.25, 0.8, 1.15, 0.8, 1.25),
    ("bein_laenge_vorn", "Beinlänge vorn", "K", 0.8, 1.2, 0.9, 1.1, 0.8, 1.2),
    ("bein_laenge_hinten", "Beinlänge hinten", "K", 0.8, 1.2, 0.9, 1.1, 0.8, 1.2),
    ("spur_breite", "Spurbreite", "K", 0.8, 1.25, 0.9, 1.1, 0.8, 1.25),
    ("pranken_vorn", "Pranken vorn", "K", 0.8, 1.5, 0.8, 1.3, 0.8, 1.5),
    ("pranken_hinten", "Pranken hinten", "K", 0.8, 1.5, 0.8, 1.3, 0.8, 1.5),
    ("hals_laenge", "Halslänge", "K", 0.7, 1.5, 0.8, 1.25, 0.7, 1.5),
    ("kopf_groesse", "Kopfgröße", "K", 0.7, 1.4, 0.7, 1.4, 0.7, 1.4),
    ("kopf_breite", "Kopfbreite", "S", 0.8, 1.5, 0.8, 1.5, 0.8, 1.5),
    ("schnauze_laenge", "Schnauzenlänge", "S", 0.8, 1.6, 0.8, 1.6, 0.8, 1.6),
    ("schwanz_laenge", "Schwanzlänge", "K", 0.5, 2.0, 0.5, 1.5, 0.5, 2.0),
    ("schwanz_dicke", "Schwanzdicke", "K", 0.6, 1.6, 0.6, 1.6, 0.6, 1.6),
]


def ampel(feld, v):
    r = next(x for x in STATUR if x[0] == feld)
    if r[5] - 1e-4 <= v <= r[6] + 1e-4:
        return 0
    if r[7] - 1e-4 <= v <= r[8] + 1e-4:
        return 1
    return 2


AMPEL_ICON = ["CHECKMARK", "INFO", "ERROR"]
AMPEL_TEXT = ["grün – Clips passen", "gelb – Clips mit Korrektur", "rot – eigener Clip-Satz nötig"]


# ------------------------------------------------------------------------------------------------ Hilfen
def _items_bases(self, context):
    return [(b["id"], f"{b['name']} ({os.path.basename(b['dir'])})", "") for b in vk_base.list_bases()] or [("-", "(keine Basis)", "")]


def _variant_files(base_id):
    try:
        info = vk_base.find_base(base_id)
    except Exception:
        return []
    d = os.path.join(info["dir"], "varianten")
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".variant.json")) if os.path.isdir(d) else []


_files_cache = []


def _items_files(self, context):
    global _files_cache
    files = _variant_files(context.scene.vk.basis)
    _files_cache = [(f, os.path.basename(f), f) for f in files] or [("-", "(keine Varianten-Datei)", "")]
    return _files_cache


_zone_items_cache = []


def _items_zones(self, context):
    global _zone_items_cache
    an = S.get("an")
    names = ["ganzer_koerper"] + (an.zones.names + an.zones.sammel_names if an else [])
    _zone_items_cache = [(z, z, "") for z in names]
    return _zone_items_cache


_clip_cache = []


def _items_clips(self, context):
    global _clip_cache
    _clip_cache = [("__ruhe__", "Ruhepose", "")] + [(a.name, a.name.replace("Quadruped_Bear_", "").replace("Quadruped_", ""), a.name)
                                                     for a in sorted(bpy.data.actions, key=lambda a: a.name) if a.name.startswith("Quadruped_")]
    return _clip_cache


_forms_cache = []


def _items_forms(self, context):
    global _forms_cache
    lib = vk_parts.read_lib(context.scene.vk.wb_typ) or {}
    _forms_cache = [(f, f, "") for f in lib.get("formen", {}).keys()] + [("__neu__", "(neue Form)", "")]
    return _forms_cache


def schedule(kind):
    if S["loading"]:
        return
    S["pending"].add(kind)
    if not bpy.app.timers.is_registered(_flush):
        bpy.app.timers.register(_flush, first_interval=0.06)


def _flush():
    kinds, S["pending"] = S["pending"], set()
    try:
        if S["doc"] is None or S["ob"] is None:
            return None
        if "statur" in kinds:
            vk_base.apply_statur(S["an"], S["arm"], S["ob"], S["doc"].resolved["statur"])
        if "maske" in kinds or "lagen" in kinds:
            lagen = [l for l in S["doc"].resolved["bedeckung"]["lagen"] if isinstance(l, dict) and l.get("an", True)][:2]
            S["overlap"] = vk_cover.update_masks(S["an"], S["ob"], lagen)
        if "lagen" in kinds or "maske" in kinds:
            vk_cover.sync_modifiers(S["an"], S["arm"], S["ob"], S["doc"], S["pts"])
            count()
    except Exception as ex:   # noqa
        bpy.context.scene.vk.status = f"Fehler: {ex}"
        import traceback
        traceback.print_exc()
    _redraw()
    return None


def count():
    try:
        ev = vk_cover.evaluate_parts(S["ob"], rest=False)
        S["tris"], S["teile"] = vk_cover.count_tris(ev)
    except Exception:
        S["tris"], S["teile"] = {}, {}


def _redraw():
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == "VIEW_3D":
                a.tag_redraw()


def _doc():
    return S["doc"]


def _lagen():
    d = _doc()
    return d.resolved["bedeckung"]["lagen"] if d else []


def _mark():
    if S["doc"] is not None and not S["loading"]:
        S["doc"].dirty = True


# ------------------------------------------------------------------------------------------------ Eigenschaften
def _upd_statur(self, context):
    if S["loading"] or S["doc"] is None:
        return
    st = S["doc"].resolved["statur"]
    for f, *_ in STATUR:
        st[f] = round(float(getattr(self, f)), 3)
    _mark()
    schedule("statur")


def _upd_masse(self, context):
    if S["loading"] or S["doc"] is None:
        return
    st = S["doc"].resolved["statur"]
    alt = (st["rumpf_dicke"] + st["glied_dicke"]) * 0.5
    d = self.masse - alt
    S["loading"] = True
    try:
        self.rumpf_dicke = min(max(st["rumpf_dicke"] + d, 0.8), 1.25)
        self.glied_dicke = min(max(st["glied_dicke"] + d, 0.8), 1.25)
    finally:
        S["loading"] = False
    _upd_statur(self, context)


class VKStatur(bpy.types.PropertyGroup):
    __annotations__ = {f: FloatProperty(name=n, min=a, max=b, default=1.0, precision=3, step=1, update=_upd_statur,
                                        description=f"{n} (Typ {t}); Regler bis zur gelben Zone (Entscheidung E3)")
                       for f, n, t, a, b, *_ in STATUR}
    __annotations__["masse"] = FloatProperty(name="Masse (Makro)", min=0.8, max=1.25, default=1.0, precision=3, update=_upd_masse,
                                             description="bewegt Rumpfdicke + Gliederdicke gemeinsam")


def _upd_haut(self, context):
    if S["loading"] or S["doc"] is None:
        return
    h = S["doc"].resolved["bedeckung"].setdefault("haut", {})
    h["typ"] = self.typ
    h["rauheit"] = round(self.rauheit, 3)
    _mark()


class VKHaut(bpy.types.PropertyGroup):
    typ: EnumProperty(name="Haut", items=[("glatt", "glatt", "nackte facettierte Haut"), ("leder", "Leder", "matt, Falten/Narben"),
                                           ("schuppen", "Schuppen", "Echsen-/Fischhaut")], update=_upd_haut)
    rauheit: FloatProperty(name="Rauheit", min=0, max=1, default=0.8, update=_upd_haut)


LAGE_FELDER_F = ["laenge", "laenge_zufall", "anlege_winkel", "richtung_zufall", "abstand_min", "weichheit", "breite", "kruemmung", "dicke",
                 "spitze", "groesse", "streckung", "schuppung", "woelbung", "groesse_zufall"]
LAGE_FELDER_I = ["anzahl", "kanten", "ecken"]
LAGE_FELDER_E = ["typ", "modus", "richtung", "form", "farbgruppe"]
LAGE_FELDER_B = ["accessoires_aussparen", "kiel"]
LAGE_ORDNUNG = ["id", "typ", "an", "modus", "anzahl", "laenge", "laenge_zufall", "laenge_nach_zone", "breite", "form", "kanten", "kruemmung",
                "kiel", "dicke", "spitze", "groesse", "groesse_zufall", "streckung", "ecken", "schuppung", "woelbung", "richtung",
                "anlege_winkel", "richtung_zufall", "abstand_min", "farbgruppe", "weichheit", "accessoires_aussparen", "seed", "weg_ab_lod", "maske"]


def _push_lage(self, kind):
    if S["loading"] or S["doc"] is None:
        return
    lagen = _lagen()
    i = self.index
    if i >= len(lagen):
        return
    l = lagen[i]
    old_typ = l.get("typ")
    if self.typ != old_typ:   # Typ gewechselt → Standardwerte des neuen Typs, Maske bleibt
        neu = vk_cover.neue_lage(self.typ, l.get("id") or f"{self.typ}_{i + 1}")
        neu["maske"] = l.get("maske", neu["maske"])
        neu["farbgruppe"] = l.get("farbgruppe", neu["farbgruppe"])
        l.clear()
        l.update(neu)
        fill_lage(self, l)
        _mark()
        schedule("lagen")
        return
    l["an"] = bool(self.an)
    for k in LAGE_FELDER_E:
        l[k] = getattr(self, k)
    for k in LAGE_FELDER_I:
        l[k] = int(getattr(self, k))
    for k in LAGE_FELDER_F:
        v = float(getattr(self, k))
        l[k] = round(v, 1 if k in ("anlege_winkel", "richtung_zufall") else 3)
    for k in LAGE_FELDER_B:
        l[k] = bool(getattr(self, k))
    l["seed"] = None if self.seed_auto else int(self.seed)
    mk = l.setdefault("maske", {})
    mk["zonen"] = [z for z in self.zonen.split(",") if z] or ["ganzer_koerper"]
    mk["ohne"] = [z for z in self.ohne.split(",") if z]
    mk["oben"] = round(self.oben, 3)
    mk["rand"] = round(self.rand, 3)
    mk["rauschen"] = round(self.rauschen, 3)
    l["laenge_nach_zone"] = {it.zone: round(it.faktor, 3) for it in self.laenge_zone}
    # nicht benutzte Felder des Typs nicht mitschreiben
    erlaubt = set(vk_cover.TYP_STD[self.typ]) | set(vk_cover.GEMEINSAM) | {"id", "typ", "an", "maske"}
    for k in list(l.keys()):
        if k not in erlaubt and k in (LAGE_FELDER_F + LAGE_FELDER_I + LAGE_FELDER_E + LAGE_FELDER_B):
            del l[k]
    ordered = {k: l[k] for k in LAGE_ORDNUNG if k in l}
    ordered.update({k: v for k, v in l.items() if k not in ordered})
    l.clear()
    l.update(ordered)
    _mark()
    schedule(kind)


def _upd_lage(self, context):
    _push_lage(self, "lagen")


def _upd_maske(self, context):
    _push_lage(self, "maske")


class VKZoneFaktor(bpy.types.PropertyGroup):
    zone: EnumProperty(name="Zone", items=_items_zones, update=lambda s, c: _upd_lz(s, c))
    faktor: FloatProperty(name="Faktor", min=0.2, max=3.0, default=1.3, update=lambda s, c: _upd_lz(s, c))


def _upd_lz(self, context):
    for lp in context.scene.vk.lagen:
        if any(it == self for it in lp.laenge_zone):
            _push_lage(lp, "maske")


class VKLage(bpy.types.PropertyGroup):
    index: IntProperty()
    an: BoolProperty(name="an", default=True, update=_upd_lage)
    typ: EnumProperty(name="Typ", items=[(t, t, "") for t in vk_cover.TYPEN], update=_upd_lage)
    modus: EnumProperty(name="Modus", items=[("geometrie", "Geometrie", "Teile am ganzen Maskenbereich"),
                                              ("silhouette", "Silhouette", "nur an Rückenlinie, Nacken, Schultern, Beinrändern (spart Tris)"),
                                              ("nur_shader", "nur Shader", "keine Geometrie (Strich nur in der Textur, später)")], update=_upd_maske)
    anzahl: IntProperty(name="Anzahl", min=0, max=1500, default=500, update=_upd_lage, description="Teile in der Maske – steuert direkt die Tris")
    laenge: FloatProperty(name="Länge", min=0.005, max=0.4, default=0.05, precision=3, step=0.1, update=_upd_lage, description="Anteil der Kreaturgröße")
    laenge_zufall: FloatProperty(name="Längen-Zufall", min=0, max=1, default=0.3, update=_upd_lage)
    richtung: EnumProperty(name="Richtung", items=[("knochen", "entlang Knochen", "wie Fell: nach hinten/unten"), ("hinten", "nach hinten", ""),
                                                    ("unten", "nach unten", ""), ("aussen", "senkrecht weg", "")], update=_upd_lage)
    anlege_winkel: FloatProperty(name="Anlege-Winkel", min=0, max=90, default=25, update=_upd_lage, description="0° liegt flach an, 90° steht ab")
    richtung_zufall: FloatProperty(name="Richtungs-Zufall", min=0, max=45, default=12, update=_upd_lage, description="Grad")
    abstand_min: FloatProperty(name="Abstand min.", min=0, max=0.1, default=0.015, precision=3, step=0.1, update=_upd_lage)
    farbgruppe: EnumProperty(name="Farbgruppe", items=[("bedeckung_1", "bedeckung_1", ""), ("bedeckung_2", "bedeckung_2", "")], update=_upd_lage)
    weichheit: FloatProperty(name="Weichheit", min=0, max=1, default=0.6, update=lambda s, c: _push_lage(s, "weich"),
                             description="Nachschwingen im Unity-Shader (G14): 0 = starr wie Felszacken, 1 = schwingendes Fell. Ändert die Geometrie nicht")
    accessoires_aussparen: BoolProperty(name="unter Accessoires aussparen", default=True, update=_upd_lage)
    kiel: BoolProperty(name="Kiel (Textur)", default=True, update=_upd_lage)
    seed_auto: BoolProperty(name="Seed automatisch", default=True, update=_upd_lage)
    seed: IntProperty(name="Seed", min=0, default=1, update=_upd_lage)
    breite: FloatProperty(name="Breite", min=0.2, max=1.0, default=0.45, update=_upd_lage, description="Breite relativ zur Länge")
    form: EnumProperty(name="Form", items=[(f, f, "") for f in vk_cover.FORMEN], update=_upd_lage)
    kanten: IntProperty(name="Kanten", min=3, max=5, default=3, update=_upd_lage)
    kruemmung: FloatProperty(name="Krümmung", min=0, max=1, default=0.3, update=_upd_lage)
    dicke: FloatProperty(name="Dicke", min=0.003, max=0.03, default=0.01, precision=3, step=0.05, update=_upd_lage, description="Anteil der Kreaturgröße")
    spitze: FloatProperty(name="Spitze", min=0, max=1, default=0.9, update=_upd_lage)
    groesse: FloatProperty(name="Größe", min=0.02, max=0.15, default=0.06, precision=3, step=0.1, update=_upd_lage)
    streckung: FloatProperty(name="Streckung", min=0.5, max=2, default=1.2, update=_upd_lage)
    ecken: IntProperty(name="Ecken", min=4, max=8, default=6, update=_upd_lage)
    schuppung: FloatProperty(name="Schuppung (Überlappung)", min=0, max=0.8, default=0.4, update=_upd_lage)
    woelbung: FloatProperty(name="Wölbung", min=0, max=1, default=0.3, update=_upd_lage)
    groesse_zufall: FloatProperty(name="Größen-Zufall", min=0, max=1, default=0.3, update=_upd_lage)
    zonen: StringProperty(name="Zonen", default="ganzer_koerper", update=_upd_maske)
    ohne: StringProperty(name="ohne", default="", update=_upd_maske)
    oben: FloatProperty(name="Oben (+) / Unterseite (−)", min=-1, max=1, default=0, update=_upd_maske)
    rand: FloatProperty(name="Rand", min=0, max=0.2, default=0.05, update=_upd_maske)
    rauschen: FloatProperty(name="Fleckiger Rand", min=0, max=1, default=0.2, update=_upd_maske)
    laenge_zone: CollectionProperty(type=VKZoneFaktor)
    offen: BoolProperty(default=True)


def _upd_wb(self, context):
    if S["loading"]:
        return
    try:
        fam = vk_parts.TYPEN[self.wb_typ][0]
        werte = {k: getattr(self.wb, k) for k, *_ in vk_parts.FAMILIEN[fam]}
        vk_parts.ensure_workbench(self.wb_typ, werte)
    except Exception as ex:
        self.status = f"Werkbank: {ex}"


def _wb_props():
    ann = {}
    seen = {}
    for fam, regs in vk_parts.FAMILIEN.items():
        for k, t, d, a, b, desc in regs:
            if k in seen:
                lo, hi = seen[k]
                seen[k] = (min(lo, a), max(hi, b))
            else:
                seen[k] = (a, b)
    for fam, regs in vk_parts.FAMILIEN.items():
        for k, t, d, a, b, desc in regs:
            if k in ann:
                continue
            lo, hi = seen[k]
            if t == "int":
                ann[k] = IntProperty(name=k, min=int(lo), max=int(hi), default=int(d), description=desc, update=lambda s, c: _upd_wb(c.scene.vk, c))
            else:
                ann[k] = FloatProperty(name=k, min=lo, max=hi, default=d, description=desc, update=lambda s, c: _upd_wb(c.scene.vk, c))
    return ann


class VKWerkbank(bpy.types.PropertyGroup):
    __annotations__ = _wb_props()


def _upd_wb_typ(self, context):
    _load_form(self)


def _upd_wb_form(self, context):
    _load_form(self)


def _load_form(vk):
    if S["loading"]:
        return
    try:
        form = vk.wb_form
    except Exception:
        form = "__neu__"
    werte = vk_parts.werte_fuer(vk.wb_typ, form if form != "__neu__" else "")
    S["loading"] = True
    try:
        for k, v in werte.items():
            if hasattr(vk.wb, k):
                setattr(vk.wb, k, v)
        if form != "__neu__":
            vk.wb_name = form
    finally:
        S["loading"] = False
    _upd_wb(vk, bpy.context)


def _upd_clip(self, context):
    arm = S.get("arm")
    if arm is None:
        return
    arm.animation_data_create()
    if self.clip == "__ruhe__":
        arm.animation_data.action = None
        for pb in arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.location = (0, 0, 0)
        return
    act = bpy.data.actions.get(self.clip)
    if act is None:
        return
    arm.animation_data.action = act
    try:
        if act.slots:
            arm.animation_data.action_slot = act.slots[0]
    except Exception:
        pass
    scn = context.scene
    scn.frame_start, scn.frame_end = int(act.frame_range[0]), int(act.frame_range[1])


class VKProps(bpy.types.PropertyGroup):
    basis: EnumProperty(name="Basis", items=_items_bases)
    datei: EnumProperty(name="Variante", items=_items_files)
    status: StringProperty(default="")
    statur: PointerProperty(type=VKStatur)
    haut: PointerProperty(type=VKHaut)
    lagen: CollectionProperty(type=VKLage)
    neu_typ: EnumProperty(name="neue Lage", items=[(t, t, "") for t in vk_cover.TYPEN])
    clip: EnumProperty(name="Clip", items=_items_clips, update=_upd_clip)
    zeige_acc: BoolProperty(name="Accessoires zeigen", default=True,
                            update=lambda s, c: setattr(bpy.data.objects[vk_acc.ACC_OBJ], "hide_viewport", not s.zeige_acc) if bpy.data.objects.get(vk_acc.ACC_OBJ) else None)
    wb_typ: EnumProperty(name="Typ", items=[(t, t, f"Familie {f}") for t, (f, _) in vk_parts.TYPEN.items()], update=_upd_wb_typ)
    wb_form: EnumProperty(name="Form", items=_items_forms, update=_upd_wb_form)
    wb_name: StringProperty(name="Name", default="neue_form")
    wb: PointerProperty(type=VKWerkbank)
    offen_statur: BoolProperty(default=True)
    offen_bedeckung: BoolProperty(default=True)
    offen_werkbank: BoolProperty(default=False)


# ------------------------------------------------------------------------------------------------ Laden / Füllen
def fill_lage(lp, l):
    S["loading"] = True
    try:
        lp.an = bool(l.get("an", True))
        lp.typ = l.get("typ", "fell") if l.get("typ") in vk_cover.TYPEN else "fell"
        for k in LAGE_FELDER_E[1:]:
            v = vk_cover.wert(l, k)
            if v is not None:
                try:
                    setattr(lp, k, v)
                except Exception:
                    pass
        for k in LAGE_FELDER_I + LAGE_FELDER_F:
            v = vk_cover.wert(l, k)
            if v is not None:
                try:
                    setattr(lp, k, v)
                except Exception:
                    pass
        for k in LAGE_FELDER_B:
            v = vk_cover.wert(l, k)
            if v is not None:
                setattr(lp, k, bool(v))
        lp.seed_auto = l.get("seed") is None
        lp.seed = int(l.get("seed") or 1)
        mk = l.get("maske") or {}
        lp.zonen = ",".join(mk.get("zonen") or ["ganzer_koerper"])
        lp.ohne = ",".join(mk.get("ohne") or [])
        lp.oben = float(mk.get("oben", 0) or 0)
        lp.rand = float(mk.get("rand", 0.05) or 0.05)
        lp.rauschen = float(mk.get("rauschen", 0.2) or 0)
        lp.laenge_zone.clear()
        for z, f in (l.get("laenge_nach_zone") or {}).items():
            it = lp.laenge_zone.add()
            try:
                it.zone = z
            except Exception:
                pass
            it.faktor = float(f)
    finally:
        S["loading"] = False


def fill_props(vk):
    d = S["doc"]
    S["loading"] = True
    try:
        st = d.resolved["statur"]
        for f, *_ in STATUR:
            setattr(vk.statur, f, float(st.get(f, 1.0)))
        vk.statur.masse = (st["rumpf_dicke"] + st["glied_dicke"]) * 0.5
        h = d.resolved["bedeckung"].get("haut", {})
        vk.haut.typ = h.get("typ", "glatt") if h.get("typ") in ("glatt", "leder", "schuppen") else "glatt"
        vk.haut.rauheit = float(h.get("rauheit", 0.8))
        vk.lagen.clear()
        for i, l in enumerate([x for x in d.resolved["bedeckung"]["lagen"] if isinstance(x, dict)][:2]):
            lp = vk.lagen.add()
            lp.index = i
            fill_lage(lp, l)
    finally:
        S["loading"] = False


def load_variant(path, vk):
    doc = vk_json.VariantDoc.load(path)
    info = vk_base.find_base(doc.resolved.get("basis") or vk.basis)
    arm, ob = vk_base.find_in_scene()
    if arm is None or ob is None or ob.get("vk_basis") != info["id"]:
        arm, ob = vk_base.load_into_scene(info)
    an = vk_base.Analysis(arm, ob)
    vk_cover.prepare_base(an, ob)
    S.update(doc=doc, an=an, arm=arm, ob=ob)
    coll = bpy.data.collections.get(vk_base.COLL_NAME)
    S["acc"], S["pts"], S["acc_info"], S["acc_tris"] = vk_acc.build(an, arm, doc, coll)
    fill_props(vk)
    S["loading"] = True
    try:
        vk.basis = info["id"]
        vk.datei = os.path.abspath(path)
    except Exception:
        pass
    finally:
        S["loading"] = False
    vk_base.apply_statur(an, arm, ob, doc.resolved["statur"])
    lagen = [l for l in doc.resolved["bedeckung"]["lagen"] if isinstance(l, dict) and l.get("an", True)][:2]
    S["overlap"] = vk_cover.update_masks(an, ob, lagen)
    vk_cover.sync_modifiers(an, arm, ob, doc, S["pts"])
    count()
    S["disk_rev"] = doc.loaded_revision
    return doc


# ------------------------------------------------------------------------------------------------ Operatoren
class VK_OT_laden(bpy.types.Operator):
    bl_idname = "vk.laden"
    bl_label = "Laden"
    bl_description = "Varianten-Datei laden (Basis-Kreatur samt Rig und Clips wird bei Bedarf geholt)"
    path: StringProperty(default="")

    def execute(self, context):
        vk = context.scene.vk
        p = self.path or vk.datei
        if not p or p == "-" or not os.path.exists(p):
            self.report({"ERROR"}, "Keine Varianten-Datei gewählt")
            return {"CANCELLED"}
        try:
            doc = load_variant(p, vk)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.report({"ERROR"}, f"Laden fehlgeschlagen: {ex}")
            return {"CANCELLED"}
        vk.status = f"Geladen: {os.path.basename(p)} (Revision {doc.loaded_revision})"
        if vk.clip == "":
            pass
        return {"FINISHED"}


class VK_OT_speichern(bpy.types.Operator):
    bl_idname = "vk.speichern"
    bl_label = "Speichern"
    bl_description = "Schreibt Statur und Bedeckung in die Varianten-Datei (nur Abweichungen vom Gruppen-Preset)"
    force: BoolProperty(default=False)

    def execute(self, context):
        d = S["doc"]
        if d is None:
            return {"CANCELLED"}
        err = d.save(force=self.force)
        vk = context.scene.vk
        if err:
            vk.status = err + " → „Überschreiben“ oder „Neu laden“"
            self.report({"WARNING"}, err)
            return {"CANCELLED"}
        S["disk_rev"] = d.loaded_revision
        vk.status = f"Gespeichert: {os.path.basename(d.path)} (Revision {d.loaded_revision})"
        return {"FINISHED"}


class VK_OT_lage_neu(bpy.types.Operator):
    bl_idname = "vk.lage_neu"
    bl_label = "Lage hinzufügen"
    bl_description = "Neue geometrische Lage (höchstens 2, Entscheidung E2)"

    def execute(self, context):
        d = S["doc"]
        vk = context.scene.vk
        lagen = _lagen()
        if d is None or len(lagen) >= 2:
            return {"CANCELLED"}
        n = 1
        while any(isinstance(l, dict) and l.get("id") == f"{vk.neu_typ}_{n}" for l in lagen):
            n += 1
        l = vk_cover.neue_lage(vk.neu_typ, f"{vk.neu_typ}_{n}")
        if len(lagen) == 1:
            l["farbgruppe"] = "bedeckung_2"
        lagen.append(l)
        lp = vk.lagen.add()
        lp.index = len(lagen) - 1
        fill_lage(lp, l)
        _mark()
        schedule("maske")
        return {"FINISHED"}


class VK_OT_lage_weg(bpy.types.Operator):
    bl_idname = "vk.lage_weg"
    bl_label = "Lage entfernen"
    index: IntProperty()

    def execute(self, context):
        lagen = _lagen()
        if self.index < len(lagen):
            lagen.pop(self.index)
        fill_props(context.scene.vk)
        _mark()
        schedule("maske")
        return {"FINISHED"}


class VK_OT_seed(bpy.types.Operator):
    bl_idname = "vk.seed"
    bl_label = "Neu würfeln"
    index: IntProperty()

    def execute(self, context):
        import random
        lp = context.scene.vk.lagen[self.index]
        S["loading"] = True
        lp.seed_auto = False
        S["loading"] = False
        lp.seed = random.randint(1, 99999)
        return {"FINISHED"}


class VK_OT_zone_toggle(bpy.types.Operator):
    bl_idname = "vk.zone_toggle"
    bl_label = "Zone"
    bl_options = {"INTERNAL"}
    index: IntProperty()
    feld: StringProperty()
    zone: StringProperty()

    def execute(self, context):
        lp = context.scene.vk.lagen[self.index]
        cur = [z for z in getattr(lp, self.feld).split(",") if z]
        if self.zone in cur:
            cur.remove(self.zone)
        else:
            cur.append(self.zone)
        setattr(lp, self.feld, ",".join(cur))
        return {"FINISHED"}


class VK_OT_zonen(bpy.types.Operator):
    bl_idname = "vk.zonen"
    bl_label = "Zonen wählen"
    bl_description = "Körperstellen (Andock-Zonen) und Sammelnamen an-/abwählen"
    index: IntProperty()
    feld: StringProperty(default="zonen")

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=520)

    def draw(self, context):
        lp = context.scene.vk.lagen[self.index]
        cur = [z for z in getattr(lp, self.feld).split(",") if z]
        an = S.get("an")
        lay = self.layout
        lay.label(text=f"{'Zonen' if self.feld == 'zonen' else 'ohne'} – Lage {self.index + 1}")
        for title, names in (("Zonen", ["ganzer_koerper"] + (an.zones.names if an else [])), ("Sammelnamen", an.zones.sammel_names if an else [])):
            lay.label(text=title)
            grid = lay.grid_flow(columns=4, even_columns=True)
            for z in names:
                op = grid.operator("vk.zone_toggle", text=z, depress=z in cur)
                op.index, op.feld, op.zone = self.index, self.feld, z

    def execute(self, context):
        return {"FINISHED"}


class VK_OT_lz_neu(bpy.types.Operator):
    bl_idname = "vk.lz_neu"
    bl_label = "Zone mit eigener Länge"
    index: IntProperty()

    def execute(self, context):
        lp = context.scene.vk.lagen[self.index]
        it = lp.laenge_zone.add()
        it.faktor = 1.3
        _push_lage(lp, "maske")
        return {"FINISHED"}


class VK_OT_lz_weg(bpy.types.Operator):
    bl_idname = "vk.lz_weg"
    bl_label = "entfernen"
    index: IntProperty()
    item: IntProperty()

    def execute(self, context):
        lp = context.scene.vk.lagen[self.index]
        lp.laenge_zone.remove(self.item)
        _push_lage(lp, "maske")
        return {"FINISHED"}


class VK_OT_statur_reset(bpy.types.Operator):
    bl_idname = "vk.statur_reset"
    bl_label = "1"
    bl_description = "Regler auf 1.0 (wie die Basis)"
    feld: StringProperty()

    def execute(self, context):
        setattr(context.scene.vk.statur, self.feld, 1.0)
        return {"FINISHED"}


class VK_OT_abspielen(bpy.types.Operator):
    bl_idname = "vk.abspielen"
    bl_label = "Abspielen / Anhalten"

    def execute(self, context):
        bpy.ops.screen.animation_play()
        return {"FINISHED"}


class VK_OT_arpg(bpy.types.Operator):
    bl_idname = "vk.arpg"
    bl_label = "ARPG-Ansicht"
    bl_description = "Blick schräg von oben wie im Spiel"

    def execute(self, context):
        import math
        from mathutils import Vector
        an = S.get("an")
        f = Vector(an.fwd) if an else Vector((1, 0, 0))
        l = Vector(an.left) if an else Vector((0, 1, 0))
        up = Vector((0, 0, 1))
        az, el = math.radians(35), math.radians(48)   # schräg von vorn-seitlich, 48° von oben (Spielkamera)
        eye = (f * math.cos(az) + l * math.sin(az)) * math.cos(el) + up * math.sin(el)
        areas = [context.area] if context.area and context.area.type == "VIEW_3D" else [a for a in context.screen.areas if a.type == "VIEW_3D"]
        for a in areas:
            r3d = a.spaces.active.region_3d
            r3d.view_rotation = (-eye).to_track_quat("-Z", "Y")
            r3d.view_location = (0, 0, 0.0)
            r3d.view_distance = 3.4 * (an.L if an else 1.0)
            r3d.view_perspective = "PERSP"
        return {"FINISHED"}


class VK_OT_acc_neu(bpy.types.Operator):
    bl_idname = "vk.acc_neu"
    bl_label = "Accessoires neu einlesen"
    bl_description = "Instanzen-Liste aus Unity neu lesen (Platzierung macht Unity)"

    def execute(self, context):
        if S["doc"] is None:
            return {"CANCELLED"}
        coll = bpy.data.collections.get(vk_base.COLL_NAME)
        S["acc"], S["pts"], S["acc_info"], S["acc_tris"] = vk_acc.build(S["an"], S["arm"], S["doc"], coll)
        schedule("lagen")
        return {"FINISHED"}


class VK_OT_export(bpy.types.Operator):
    bl_idname = "vk.export"
    bl_label = "Bedeckung für Unity exportieren"
    bl_description = "Schreibt output/varianten/<Name>/<Name>.bedeckung.json (dasselbe macht der Unity-Knopf „In Blender bauen“)"

    def execute(self, context):
        d = S["doc"]
        if d is None:
            return {"CANCELLED"}
        out = export_path(d)
        data = vk_cover.export_unity(S["an"], S["ob"], d, out, WERKZEUG)
        context.scene.vk.status = f"Exportiert: {os.path.basename(out)} ({data['tris']['gesamt']} Tris)"
        return {"FINISHED"}


def export_path(doc):
    cdir = vk_base.creature_dir_of_variant(doc.path)
    return os.path.join(cdir, "output", "varianten", doc.export_name, doc.export_name + ".bedeckung.json")


class VK_OT_form_speichern(bpy.types.Operator):
    bl_idname = "vk.form_speichern"
    bl_label = "Form speichern"
    bl_description = "Schreibt die Form in procedural/bausteine/<typ>.json (+ FBX/GLB). Unity nutzt sie beim nächsten Aufbau."

    def execute(self, context):
        vk = context.scene.vk
        ob = bpy.data.objects.get(vk_parts.WB_OBJ)
        if ob is None:
            _upd_wb(vk, context)
            ob = bpy.data.objects.get(vk_parts.WB_OBJ)
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in vk.wb_name.strip().lower()) or "form"
        fam = vk_parts.TYPEN[vk.wb_typ][0]
        werte = {k: getattr(vk.wb, k) for k, *_ in vk_parts.FAMILIEN[fam]}
        co, tri = vk_parts.evaluate_form(ob)
        f = vk_parts.save_form(vk.wb_typ, name, werte, co, tri)
        vk.status = f"Form gespeichert: {vk.wb_typ}/{name} ({f['tris']} Tris)"
        if S["doc"] is not None:
            bpy.ops.vk.acc_neu()
        return {"FINISHED"}


class VK_OT_werkbank(bpy.types.Operator):
    bl_idname = "vk.werkbank"
    bl_label = "Vorschau zeigen"

    def execute(self, context):
        _load_form(context.scene.vk)
        return {"FINISHED"}


class VK_OT_startformen(bpy.types.Operator):
    bl_idname = "vk.startformen"
    bl_label = "Fehlende Bausteintypen erzeugen"
    bl_description = "Legt für jeden Typ ohne Bibliothek die Startformen an (vorhandene bleiben unberührt)"

    def execute(self, context):
        done = vk_parts.generate_missing()
        context.scene.vk.status = "Erzeugt: " + (", ".join(done) if done else "nichts (alle vorhanden)")
        return {"FINISHED"}


# ------------------------------------------------------------------------------------------------ Panel
class VK_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Variante"
    bl_label = "Varianten-Baukasten"

    def draw(self, context):
        vk = context.scene.vk
        lay = self.layout
        col = lay.column(align=True)
        col.prop(vk, "basis")
        row = col.row(align=True)
        row.prop(vk, "datei", text="")
        row.operator("vk.laden", text="", icon="FILE_REFRESH")
        d = S["doc"]
        row = lay.row(align=True)
        row.operator("vk.laden", text="Laden" if d is None else "Neu laden", icon="IMPORT")
        if d is not None:
            row.operator("vk.speichern", text="Speichern *" if d.dirty else "Speichern", icon="FILE_TICK")
            if "geändert" in vk.status:
                op = row.operator("vk.speichern", text="Überschreiben", icon="ERROR")
                op.force = True
        if vk.status:
            lay.label(text=vk.status)
        if d is None:
            lay.label(text="Erst eine Varianten-Datei laden.", icon="INFO")
            return
        lay.label(text=f"{d.resolved.get('name', d.id)} · Gruppe {d.resolved.get('gruppe') or '–'} · {d.resolved.get('budget_klasse', 'normal')} · Rev. {d.loaded_revision}")
        # Vorschau
        box = lay.box()
        row = box.row(align=True)
        row.prop(vk, "clip", text="Clip")
        row.operator("vk.abspielen", text="", icon="PLAY")
        box.operator("vk.arpg", icon="VIEW_CAMERA")
        if bpy.data.objects.get(vk_acc.ACC_OBJ):
            row = box.row()
            row.prop(vk, "zeige_acc")
            row.operator("vk.acc_neu", text="", icon="FILE_REFRESH")
        box.label(text="Accessoires: " + (S["acc_info"] or "–"))
        self.draw_budget(lay, d)
        # Statur
        box = lay.box()
        box.prop(vk, "offen_statur", text="1 · Statur", icon="TRIA_DOWN" if vk.offen_statur else "TRIA_RIGHT", emboss=False)
        if vk.offen_statur:
            st = d.resolved["statur"]
            worst = max(ampel(f, st[f]) for f, *_ in STATUR)
            box.label(text="Statur-Ampel: " + AMPEL_TEXT[worst], icon=AMPEL_ICON[worst])
            box.prop(vk.statur, "masse", slider=True)
            for f, n, t, *_ in STATUR:
                row = box.row(align=True)
                row.label(text="", icon=AMPEL_ICON[ampel(f, st[f])])
                row.prop(vk.statur, f, text=f"{n} ({t})", slider=True)
                row.operator("vk.statur_reset", text="1").feld = f
            box.label(text="Knochen werden in der Vorschau nur skaliert (Füße können rutschen).", icon="INFO")
        # Bedeckung
        box = lay.box()
        box.prop(vk, "offen_bedeckung", text="2 · Bedeckung", icon="TRIA_DOWN" if vk.offen_bedeckung else "TRIA_RIGHT", emboss=False)
        if vk.offen_bedeckung:
            row = box.row()
            row.prop(vk.haut, "typ")
            row.prop(vk.haut, "rauheit")
            box.label(text="Haut wirkt nur im Unity-Shader (0 Tris).", icon="INFO")
            if S["overlap"] > 0.15:
                box.label(text=f"Lagen überlappen ({S['overlap'] * 100:.0f} %): Lage 1 hat Vorrang (E2).", icon="ERROR")
            for lp in vk.lagen:
                self.draw_lage(box, lp, d)
            if len(vk.lagen) < 2:
                row = box.row(align=True)
                row.prop(vk, "neu_typ", text="")
                row.operator("vk.lage_neu", icon="ADD")
            box.operator("vk.export", icon="EXPORT")
        # Werkbank
        box = lay.box()
        box.prop(vk, "offen_werkbank", text="3 · Baustein-Werkbank", icon="TRIA_DOWN" if vk.offen_werkbank else "TRIA_RIGHT", emboss=False)
        if vk.offen_werkbank:
            box.prop(vk, "wb_typ")
            box.prop(vk, "wb_form")
            fam = vk_parts.TYPEN[vk.wb_typ][0]
            lib = vk_parts.read_lib(vk.wb_typ) or {}
            fw = lib.get("formen", {}).get(vk.wb_form, {}).get("werte", {})
            if vk.wb_form != "__neu__" and fw and "familie" not in fw:
                box.label(text="M1-Form (bmesh): Speichern ersetzt sie durch die Werkbank-Fassung.", icon="INFO")
            col = box.column(align=True)
            for k, t, dflt, a, b, desc in vk_parts.FAMILIEN[fam]:
                col.prop(vk.wb, k, text=k.replace("_", " ").capitalize().replace("ue", "ü").replace("oe", "ö").replace("ae", "ä") if k != "seed" else "Seed (Zufall)",
                         slider=k != "seed")
            row = box.row(align=True)
            row.operator("vk.werkbank", icon="HIDE_OFF")
            row.prop(vk, "wb_name", text="")
            row.operator("vk.form_speichern", icon="FILE_TICK")
            box.operator("vk.startformen", icon="ADD")

    def draw_budget(self, lay, d):
        klasse = d.resolved.get("budget_klasse", "normal")
        cov = sum(S["tris"].values()) if S["tris"] else 0
        base = len(S["an"].tris) if S["an"] else 0
        acc = S["acc_tris"]
        bud_c, bud_t, bud_a = vk_cover.BUDGET_BEDECKUNG.get(klasse, 2000), vk_cover.BUDGET_GESAMT.get(klasse, 6000), vk_cover.BUDGET_ACC.get(klasse, 1500)
        box = lay.box()
        row = box.row()
        row.label(text=f"Bedeckung {cov:,} / {bud_c:,} Tris".replace(",", "."), icon="CHECKMARK" if cov <= bud_c else "ERROR")
        teile = ", ".join(f"L{k}: {v} Teile" for k, v in sorted(S["teile"].items()))
        if teile:
            row.label(text=teile)
        tot = base + cov + acc
        box.label(text=f"Gesamt {tot:,} / {bud_t:,} (Basis {base:,} + Acc. {acc:,} / {bud_a:,}) · {klasse}".replace(",", "."),
                  icon="CHECKMARK" if tot <= bud_t and acc <= bud_a else "ERROR")

    def draw_lage(self, box, lp, d):
        b = box.box()
        row = b.row(align=True)
        row.prop(lp, "offen", text="", icon="TRIA_DOWN" if lp.offen else "TRIA_RIGHT", emboss=False)
        row.prop(lp, "an", text="")
        tris = S["tris"].get(lp.index + 1, 0)
        row.label(text=f"Lage {lp.index + 1}: {lp.typ} · {tris} Tris")
        row.operator("vk.lage_weg", text="", icon="X").index = lp.index
        if not lp.offen:
            return
        L = S["an"].L if S["an"] else 1.0
        col = b.column(align=True)
        col.prop(lp, "typ")
        if lp.typ in ("fell", "federn"):
            col.prop(lp, "modus")
        col.prop(lp, "farbgruppe")
        col.prop(lp, "anzahl")
        if lp.typ == "platten":
            col.prop(lp, "groesse", text=f"Größe ({lp.groesse * L * 100:.1f} cm)", slider=True)
            col.prop(lp, "groesse_zufall", slider=True)
        else:
            col.prop(lp, "laenge", text=f"Länge ({lp.laenge * L * 100:.1f} cm)", slider=True)
        col.prop(lp, "laenge_zufall", slider=True)
        col.prop(lp, "abstand_min", text=f"Abstand min. ({lp.abstand_min * L * 100:.1f} cm)", slider=True)
        col = b.column(align=True)
        col.prop(lp, "richtung")
        col.prop(lp, "anlege_winkel", slider=True)
        col.prop(lp, "richtung_zufall", slider=True)
        col.prop(lp, "weichheit", slider=True, text="Weichheit (Nachschwingen in Unity)")
        col = b.column(align=True)
        if lp.typ == "fell":
            col.prop(lp, "form")
            col.prop(lp, "breite", slider=True)
            col.prop(lp, "kanten")
            col.prop(lp, "kruemmung", slider=True)
        elif lp.typ == "federn":
            col.prop(lp, "breite", slider=True)
            col.prop(lp, "kruemmung", slider=True)
            col.prop(lp, "kiel")
        elif lp.typ == "stacheln":
            col.prop(lp, "dicke", text=f"Dicke ({lp.dicke * L * 100:.1f} cm)", slider=True)
            col.prop(lp, "kanten")
            col.prop(lp, "spitze", slider=True)
            col.prop(lp, "kruemmung", slider=True)
        else:
            col.prop(lp, "dicke", text=f"Dicke ({lp.dicke * L * 100:.1f} cm)", slider=True)
            col.prop(lp, "ecken")
            col.prop(lp, "streckung", slider=True)
            col.prop(lp, "schuppung", slider=True)
            col.prop(lp, "woelbung", slider=True)
        b.prop(lp, "accessoires_aussparen")
        row = b.row(align=True)
        row.prop(lp, "seed_auto", text="Seed auto")
        sub = row.row(align=True)
        sub.enabled = not lp.seed_auto
        sub.prop(lp, "seed", text="")
        row.operator("vk.seed", text="", icon="FILE_REFRESH").index = lp.index
        # Maske
        mb = b.box()
        mb.label(text="Maske (wo die Lage wächst)")
        for feld, label in (("zonen", "Zonen"), ("ohne", "ohne")):
            row = mb.row(align=True)
            row.label(text=f"{label}: {getattr(lp, feld).replace(',', ', ') or '–'}")
            op = row.operator("vk.zonen", text="Wählen…")
            op.index, op.feld = lp.index, feld
        mb.prop(lp, "oben", slider=True)
        mb.prop(lp, "rauschen", slider=True)
        mb.label(text="Länge pro Zone (z. B. Nacken länger):")
        for k, it in enumerate(lp.laenge_zone):
            row = mb.row(align=True)
            row.prop(it, "zone", text="")
            row.prop(it, "faktor", slider=True)
            op = row.operator("vk.lz_weg", text="", icon="X")
            op.index, op.item = lp.index, k
        mb.operator("vk.lz_neu", icon="ADD").index = lp.index


CLASSES = [VKStatur, VKHaut, VKZoneFaktor, VKLage, VKWerkbank, VKProps, VK_OT_laden, VK_OT_speichern, VK_OT_lage_neu, VK_OT_lage_weg,
           VK_OT_seed, VK_OT_zone_toggle, VK_OT_zonen, VK_OT_lz_neu, VK_OT_lz_weg, VK_OT_statur_reset, VK_OT_abspielen, VK_OT_arpg,
           VK_OT_acc_neu, VK_OT_export, VK_OT_form_speichern, VK_OT_werkbank, VK_OT_startformen, VK_PT_panel]


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)
    bpy.types.Scene.vk = PointerProperty(type=VKProps)


def unregister():
    del bpy.types.Scene.vk
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
