"""``docs/hardware.yml``: the one description of a chip's hardware, loaded and checked.

The file says what the package looks like, what every pin is and which hook of the driver's port drives it, what
blocks the chip has inside, and one or more reference circuits. Every fact carries a citation of the datasheet
(``ref``). The pin table, the three figures and the netlist export are all drawn from it, so they cannot disagree.

``load()`` returns a ``Hardware`` or raises ``HardwareError`` with every problem found, each prefixed by the path of
the offending value (``pins[3].type``), so one run lists everything to fix.

Schema (version 1), in the order the file is usually written::

    schema: 1
    chip: XMPL100                         # the part, as the docs name it
    documents:                            # optional when docs/datasheets.yml lists the documents
      - {id: ds, name: "XMPL100-DS Rev. A"}
    refs:                                 # named citations, used as ref: <key>
      pinout: {doc: ds, section: "3 Pin configuration", page: 3}
    package:
      type: SOIC-8                        # the datasheet's package name
      pins: 8                             # numbered pins, the exposed pad not counted
      layout: dual                        # optional: dual | quad, guessed from type
      sides: {left: [1, 2, 3], right: [4, 5]}   # optional, for packages the layout does not describe
      ref: pinout
      outline:                            # optional: the body, from the package outline drawing
        {length_mm: 4.9, width_mm: 3.9, height_mm: 1.75, pitch_mm: 1.27, ref: outline}
                                          # height_ref / pitch_ref: when a value is cited elsewhere than ref
      variants:                           # optional: the other packages the chip is sold in
        - {id: dfn, type: DFN-8, pins: 8, size: "3.0 x 3.0 x 0.8 mm", ordering: "-DFN", note: "...", ref: order}
    supply:                               # optional: the supply range(s), for the README chip card
      - {name: VDD, min_v: 1.8, max_v: 3.6, ref: electrical}
    hooks:                                # the port hooks a pin can map to
      - {id: transfer, call: "Transfer()", kind: spi, source: inc/x_spi_interface.hpp, symbol: Transfer}
    pins:
      - {number: 1, name: CS_N, type: bus, domain: VDD, function: "SPI chip select, active low",
         hook: transfer, unused: "-", ref: pinout}
    block_diagram:
      ref: blocks
      unverified: "..."                   # optional, for the whole diagram
      blocks:
        - {id: spi, label: SPI interface, detail: "mode 0 or 3", at: [0, 0], pins: [CS_N, SCLK]}
      links:
        - {from: spi, to: regs, label: frames, both: true}
    circuits:
      - id: typical
        title: Typical application
        ref: app
        parts:
          - {id: U1, kind: chip}
          - {id: U2, kind: mcu, label: MCU, pins: [{name: SCK, label: SPI SCK}, VDD, GND]}
          - {id: C1, kind: capacitor, value: 100 nF}
        nets:
          - {name: "+3V3", kind: supply, nodes: [U1.VDD, U2.VDD, C1.1]}
          - {name: SCK, nodes: [U1.SCLK, U2.SCK], hook: transfer}   # optional hook: replaces the pin's hook in this
                                                                 # circuit only; hook: null shows no hook; a list
                                                                 # ([write, read]) shows each, for a shared
                                                                 # half-duplex wire; an MCU net that reaches the
                                                                 # chip through a part (a transceiver) may name one
          - {name: GND, kind: ground, nodes: [U1.GND, U2.GND, C1.2]}
        unused: [U1.NC]
    overview: ...                         # optional, the chip-first README content: see ``chipdoc``
    driver: ...
    capabilities: ...
    frames: ...

Any pin, block, link, part or net may carry ``unverified: <why>``: the fact could not be confirmed in the datasheet.
The table and the figures mark it, so a guess never reads as a fact.
"""

from __future__ import annotations

import math
import pathlib
import re
from dataclasses import dataclass, field

import yaml

from ..figkit import theme as T

SOURCE = "docs/hardware.yml"
SCHEMA_VERSION = 1

#: Electrical type of a pin -> (figkit tone, label in the legend and the table).
PIN_TYPES: dict[str, tuple[str, str]] = {
    "power": ("rose", "power"),
    "ground": ("slate", "ground"),
    "bus": ("blue", "bus"),
    "digital-in": ("teal", "digital in"),
    "digital-out": ("green", "digital out"),
    "digital-io": ("violet", "digital in/out"),
    "open-drain": ("amber", "open drain"),
    "analog": ("magenta", "analog"),
    "power-out": ("brown", "power output"),
    "nc": ("stone", "not connected"),
}
HOOK_KINDS = ("spi", "i2c", "uart", "gpio-out", "gpio-in", "irq", "other")
NET_KINDS = ("signal", "supply", "ground")
#: Part kinds -> their pin names (None: the part lists its pins; "chip": the documented chip's pins).
TWO_PIN = {
    "resistor": ("1", "2"),
    "capacitor": ("1", "2"),
    "polarized-capacitor": ("1", "2"),
    "inductor": ("1", "2"),
    "solenoid": ("1", "2"),
    "diode": ("1", "2"),
    "zener": ("1", "2"),
    "led": ("1", "2"),
    "crystal": ("1", "2"),
    "fuse": ("1", "2"),
}
PIN_ALIASES = {"A": "1", "K": "2", "+": "1", "-": "2"}
PART_KINDS = (*TWO_PIN, "chip", "mcu", "ic", "connector")
LAYOUTS = ("dual", "quad")
# Packages whose pads lie under the body or flush with its edge (no leads reaching out): the outline figure draws
# their pads inside the body, and a leaded package's outside it.
_LEADLESS = re.compile(r"^[A-Z]{0,3}(?:QFN|MLF|LGA|LFCSP|DFN|SON|BGA|CSP)")
# Package names: a vendor prefix (Infineon's PG-DSO-36, P-DSO-20), then up to three letters of variant (thin,
# shrink, heat-sink, very thin: TSSOP, HTSSOP, TSDSO, HVQFN, WQFN, LQFP) before the family.
_VENDOR = re.compile(r"^(?:PG|P)-")
_DUAL = re.compile(r"^[A-Z]{0,3}(?:SOIC|SOP|DSO|DIP|SON|DFN|SOT|SO)")
_QUAD = re.compile(r"^[A-Z]{0,3}(?:QFN|QFP|MLF|LGA|LFCSP)")


class HardwareError(Exception):
    """Every problem found in docs/hardware.yml."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("\n".join(problems))


@dataclass(frozen=True)
class Ref:
    doc: str
    section: str
    page: int

    def short(self) -> str:
        return f"{self.section}, p. {self.page}"


@dataclass
class Hook:
    id: str
    call: str
    kind: str
    source: str = ""
    symbol: str = ""


@dataclass
class Pin:
    number: int | str
    name: str
    type: str
    domain: str
    function: str
    ref: Ref
    hook: str = ""
    unused: str = ""
    unverified: str = ""

    @property
    def tone(self) -> str:
        return PIN_TYPES[self.type][0]

    @property
    def is_pad(self) -> bool:
        return self.number == "EP"


@dataclass
class Outline:
    """The package body from the datasheet's package outline drawing. ``length_mm`` is the body edge pin 1 lies
    along (the left edge of the drawing), ``width_mm`` the other; ``height_mm`` and ``pitch_mm`` are optional."""

    length_mm: float
    width_mm: float
    ref: Ref
    height_mm: float | None = None
    pitch_mm: float | None = None
    height_ref: Ref | None = None  # when the height comes from another place than the drawing (a table)
    pitch_ref: Ref | None = None

    def ref_of(self, what: str) -> Ref:
        return (self.height_ref if what == "height" else self.pitch_ref) or self.ref


@dataclass
class Variant:
    """Another package the chip is sold in (the datasheet's ordering information)."""

    id: str
    type: str
    ref: Ref
    pins: int | None = None
    size: str = ""
    ordering: str = ""
    note: str = ""


@dataclass
class Supply:
    """One supply range of the chip, as the electrical characteristics give it."""

    min_v: float
    max_v: float
    ref: Ref
    name: str = ""


@dataclass
class Package:
    type: str
    pins: int
    layout: str
    sides: dict[str, list]
    ref: Ref
    exposed_pad: bool = False
    outline: Outline | None = None
    variants: list[Variant] = field(default_factory=list)

    @property
    def leadless(self) -> bool:
        return bool(_LEADLESS.match(_VENDOR.sub("", self.type.upper().replace(" ", ""))))


@dataclass
class Block:
    id: str
    label: str
    at: tuple[int, int]
    ref: Ref
    detail: str = ""
    pins: list[str] = field(default_factory=list)
    tone: str = "brand"
    side: str = ""
    unverified: str = ""


@dataclass
class Link:
    src: str
    dst: str
    label: str = ""
    both: bool = False
    unverified: str = ""


@dataclass
class Part:
    id: str
    kind: str
    ref: Ref
    value: str = ""
    label: str = ""
    pins: list[tuple[str, str]] = field(default_factory=list)  # (name, label)
    unverified: str = ""

    @property
    def two_pin(self) -> bool:
        return self.kind in TWO_PIN


@dataclass
class Net:
    name: str
    kind: str
    nodes: list[tuple[str, str]]  # (part id, pin name as written, aliases resolved)
    ref: Ref
    label: str = ""
    unverified: str = ""
    hook_set: bool = False  # the net carries its own ``hook`` key, which then replaces the chip pin's hook here
    hooks: list[str] = field(default_factory=list)  # those hook ids, in order; empty for null (no hook shown)

    @property
    def hook(self) -> str:
        """The first hook id of the net's own ``hook`` key ("" when there is none)."""
        return self.hooks[0] if self.hooks else ""


@dataclass
class Circuit:
    id: str
    title: str
    ref: Ref
    parts: dict[str, Part]
    nets: list[Net]
    unused: list[tuple[str, str]]
    description: str = ""

    @property
    def chip(self) -> Part:
        return next(p for p in self.parts.values() if p.kind == "chip")

    def net_of(self, part: str, pin: str) -> Net | None:
        for n in self.nets:
            if (part, pin) in n.nodes:
                return n
        return None

    def hook_of(self, pin: Pin) -> str:
        """The hook id the chip ``pin`` shows in this circuit: its net's ``hook`` override when there is one (empty
        for "no hook"), else the pin's own hook."""
        hs = self.hooks_of(pin)
        return hs[0] if hs else ""

    def hooks_of(self, pin: Pin) -> list[str]:
        """Every hook id the chip ``pin`` shows in this circuit: its net's ``hook`` (one or a list) when the net sets
        it, else the pin's own hook."""
        n = self.net_of(self.chip.id, pin.name)
        if n is not None and n.hook_set:
            return list(n.hooks)
        return [pin.hook] if pin.hook else []


@dataclass
class Hardware:
    chip: str
    package: Package
    hooks: dict[str, Hook]
    pins: list[Pin]
    blocks: list[Block]
    links: list[Link]
    blocks_ref: Ref | None
    circuits: list[Circuit]
    documents: dict[str, dict]
    source: str = SOURCE
    blocks_unverified: str = ""
    supply: list[Supply] = field(default_factory=list)
    #: The chip-first README content (``overview``, ``driver``, ``capabilities``, ``frames``), see ``chipdoc``.
    doc: object = None

    def pin(self, key: str | int) -> list[Pin]:
        """Pins named ``key`` (several for a repeated name such as GND), or the pin numbered ``key``."""
        named = [p for p in self.pins if p.name == key]
        if named:
            return named
        return [p for p in self.pins if str(p.number) == str(key)]

    @property
    def numbered(self) -> list[Pin]:
        return sorted((p for p in self.pins if not p.is_pad), key=lambda p: int(p.number))


# ---------------------------------------------------------------------------------------------------- loading


class _Ctx:
    def __init__(self, refs: dict, docs: dict):
        self.problems: list[str] = []
        self.refs = refs
        self.docs = docs

    def bad(self, path: str, msg: str) -> None:
        self.problems.append(f"{SOURCE}: {path}: {msg}")

    def need(self, d: dict, key: str, path: str, kind=str):
        v = d.get(key) if isinstance(d, dict) else None
        if v is None or v == "" or v == []:
            self.bad(f"{path}.{key}", "missing")
            return None
        if kind is str and not isinstance(v, (str, int, float)):
            self.bad(f"{path}.{key}", f"must be text, not {type(v).__name__}")
            return None
        if kind is not str and not isinstance(v, kind):
            self.bad(f"{path}.{key}", f"must be a {kind.__name__}, not {type(v).__name__}")
            return None
        return str(v) if kind is str else v

    def ref(self, v, path: str, default: Ref | None = None) -> Ref | None:
        if v is None:
            if default is None:
                self.bad(path, "missing: every fact cites the datasheet (ref: a key of refs, or {doc, section, page})")
            return default
        if isinstance(v, str):
            if v not in self.refs:
                self.bad(path, f"unknown citation {v!r} (refs: {', '.join(sorted(self.refs)) or 'none'})")
                return default
            return self.refs[v]
        if isinstance(v, dict):
            return self.inline_ref(v, path)
        self.bad(path, "must be a key of refs or {doc, section, page}")
        return default

    def inline_ref(self, v: dict, path: str) -> Ref | None:
        unknown = set(v) - {"doc", "section", "page"}
        if unknown:
            self.bad(path, f"unknown key(s) {', '.join(sorted(unknown))}")
        doc, section, page = v.get("doc"), v.get("section"), v.get("page")
        ok = True
        if doc not in self.docs:
            self.bad(f"{path}.doc", f"unknown document {doc!r} (known: {', '.join(sorted(self.docs)) or 'none'})")
            ok = False
        if not section:
            self.bad(f"{path}.section", "missing")
            ok = False
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            self.bad(f"{path}.page", f"must be a page number, not {page!r}")
            ok = False
        return Ref(str(doc), str(section), int(page)) if ok else None


def _keys(ctx: _Ctx, d, path: str, allowed: set[str]) -> bool:
    if not isinstance(d, dict):
        ctx.bad(path, f"must be a mapping, not {type(d).__name__}")
        return False
    extra = set(d) - allowed
    if extra:
        ctx.bad(path, f"unknown key(s) {', '.join(sorted(map(str, extra)))} (allowed: {', '.join(sorted(allowed))})")
    return True


def _number(ctx: _Ctx, d: dict, key: str, path: str, required: bool = False) -> float | None:
    """A positive, finite number (millimetres or volts), or None when absent and optional."""
    v = d.get(key)
    if v is None:
        if required:
            ctx.bad(f"{path}.{key}", "missing")
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
        ctx.bad(f"{path}.{key}", f"must be a positive number, not {v!r}")
        return None
    return float(v)


def _outline(ctx: _Ctx, o, package: Package) -> Outline | None:
    p = "package.outline"
    if not _keys(ctx, o, p, {"length_mm", "width_mm", "height_mm", "pitch_mm", "ref", "height_ref",
                                  "pitch_ref"}):
        return None
    length, width = _number(ctx, o, "length_mm", p, True), _number(ctx, o, "width_mm", p, True)
    height, pitch = _number(ctx, o, "height_mm", p), _number(ctx, o, "pitch_mm", p)
    ref = ctx.ref(o.get("ref"), f"{p}.ref")
    if None in (length, width, ref):
        return None
    if pitch is not None and pitch >= min(length, width):
        ctx.bad(f"{p}.pitch_mm", f"{pitch} mm is not smaller than the body ({length} x {width} mm)")
    if pitch is not None:
        for side, nums in package.sides.items():
            span = (len(nums) - 1) * pitch
            edge = length if side in ("left", "right") else width
            if span > edge + 1e-9:
                ctx.bad(f"{p}.pitch_mm", f"the {len(nums)} pins of the {side} side span {span:.2f} mm, more than "
                        f"the {edge} mm edge (length_mm is the left edge, width_mm the top edge)")
    href = ctx.ref(o["height_ref"], f"{p}.height_ref") if o.get("height_ref") is not None else None
    pref = ctx.ref(o["pitch_ref"], f"{p}.pitch_ref") if o.get("pitch_ref") is not None else None
    return Outline(length, width, ref, height, pitch, href, pref)


def _variants(ctx: _Ctx, vs) -> list[Variant]:
    out: list[Variant] = []
    if not isinstance(vs, list):
        ctx.bad("package.variants", "must be a list")
        return out
    for i, v in enumerate(vs):
        p = f"package.variants[{i}]"
        if not _keys(ctx, v, p, {"id", "type", "pins", "size", "ordering", "note", "ref"}):
            continue
        vid, vtype = ctx.need(v, "id", p), ctx.need(v, "type", p)
        if vid and any(x.id == vid for x in out):
            ctx.bad(f"{p}.id", f"variant {vid!r} is listed twice")
        pins = v.get("pins")
        if pins is not None and (isinstance(pins, bool) or not isinstance(pins, int) or pins < 1):
            ctx.bad(f"{p}.pins", f"must be a pin count, not {pins!r}")
            pins = None
        for k in ("size", "ordering", "note"):
            if v.get(k) is not None and not isinstance(v[k], (str, int, float)):
                ctx.bad(f"{p}.{k}", f"must be text, not {type(v[k]).__name__}")
        ref = ctx.ref(v.get("ref"), f"{p}.ref")
        if vid and vtype and ref:
            out.append(Variant(vid, vtype, ref, pins, str(v.get("size") or ""), str(v.get("ordering") or ""),
                               str(v.get("note") or "")))
    return out


def _supply(ctx: _Ctx, ss) -> list[Supply]:
    out: list[Supply] = []
    if not isinstance(ss, list):
        ctx.bad("supply", "must be a list of {name, min_v, max_v, ref}")
        return out
    for i, s in enumerate(ss):
        p = f"supply[{i}]"
        if not _keys(ctx, s, p, {"name", "min_v", "max_v", "ref"}):
            continue
        lo, hi = _number(ctx, s, "min_v", p, True), _number(ctx, s, "max_v", p, True)
        if lo is not None and hi is not None and lo > hi:
            ctx.bad(f"{p}.min_v", f"{lo} V is above max_v ({hi} V)")
        ref = ctx.ref(s.get("ref"), f"{p}.ref")
        if lo is not None and hi is not None and ref:
            out.append(Supply(lo, hi, ref, str(s.get("name") or "")))
    return out


def _documents(root: pathlib.Path, data: dict, ctx: _Ctx) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    ds = root / "docs/datasheets.yml"
    if ds.is_file():
        for d in (yaml.safe_load(ds.read_text()) or {}).get("documents") or []:
            if isinstance(d, dict) and d.get("id"):
                docs[str(d["id"])] = {
                    "name": f"{d.get('vendor', '')} {d.get('number', '')} {d.get('revision', '')}".strip(),
                    "pdf": d.get("pdf") or "",
                    "page_offset": int(d.get("page_offset") or 0),
                }
    for i, d in enumerate(data.get("documents") or []):
        p = f"documents[{i}]"
        if not _keys(ctx, d, p, {"id", "name", "pdf", "page_offset"}):
            continue
        did, name = ctx.need(d, "id", p), ctx.need(d, "name", p)
        if did and name:
            if did in docs:
                ctx.bad(f"{p}.id", f"document {did!r} is also in docs/datasheets.yml; list it once")
            docs[did] = {"name": name, "pdf": d.get("pdf") or "", "page_offset": int(d.get("page_offset") or 0)}
    return docs


def _guess_layout(ptype: str) -> str:
    t = _VENDOR.sub("", ptype.upper().replace(" ", ""))
    if _QUAD.match(t):
        return "quad"
    if _DUAL.match(t):
        return "dual"
    return ""


def _sides(layout: str, n: int) -> dict[str, list[int]]:
    """Pin numbers per side, in the order they are drawn: left top to bottom, bottom left to right, right bottom to
    top, top right to left (counter-clockwise from pin 1, seen from the top)."""
    if layout == "dual":
        h = n // 2
        return {"left": list(range(1, h + 1)), "right": list(range(h + 1, n + 1))}
    q = n // 4
    return {
        "left": list(range(1, q + 1)),
        "bottom": list(range(q + 1, 2 * q + 1)),
        "right": list(range(2 * q + 1, 3 * q + 1)),
        "top": list(range(3 * q + 1, n + 1)),
    }


def load(root: pathlib.Path | None = None, path: pathlib.Path | None = None) -> Hardware:
    """Load and check ``docs/hardware.yml`` of the repository at ``root``."""
    if root is None:
        from ..paths import repo_root

        root = repo_root()
    path = path or root / SOURCE
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise HardwareError([f"{SOURCE}: not valid YAML: {e}"]) from e
    return parse(data, root)


def parse(data, root: pathlib.Path) -> Hardware:
    ctx = _Ctx({}, {})
    if not _keys(ctx, data, "(top)", {"schema", "chip", "documents", "refs", "package", "hooks", "pins",
                                      "block_diagram", "circuits", "supply", "overview", "driver",
                                      "capabilities", "frames"}):
        raise HardwareError(ctx.problems)
    if data.get("schema") != SCHEMA_VERSION:
        ctx.bad("schema", f"must be {SCHEMA_VERSION}, not {data.get('schema')!r}")
    chip = ctx.need(data, "chip", "(top)") or "?"
    ctx.docs = _documents(root, data, ctx)
    if not ctx.docs:
        ctx.bad("documents", "no documents: list them here or in docs/datasheets.yml")
    refs = data.get("refs") or {}
    if not isinstance(refs, dict):
        ctx.bad("refs", "must be a mapping of name to {doc, section, page}")
        refs = {}
    for k, v in refs.items():
        r = ctx.inline_ref(v, f"refs.{k}") if isinstance(v, dict) else ctx.bad(f"refs.{k}", "must be {doc, section, page}")
        if r:
            ctx.refs[str(k)] = r

    # Package
    pk = data.get("package") or {}
    package = None
    if _keys(ctx, pk, "package", {"type", "pins", "layout", "sides", "exposed_pad", "ref",
                                   "outline", "variants"}):
        ptype = ctx.need(pk, "type", "package") or "?"
        n = pk.get("pins")
        if not isinstance(n, int) or n < 1:
            ctx.bad("package.pins", f"must be the number of pins, not {n!r}")
            n = 0
        layout = pk.get("layout") or _guess_layout(ptype)
        if layout not in LAYOUTS:
            ctx.bad("package.layout", f"{layout or '(not guessed from ' + ptype + ')'} is not one of {', '.join(LAYOUTS)}")
            layout = "dual"
        sides = pk.get("sides")
        if sides is None:
            if layout == "dual" and n % 2:
                ctx.bad("package.pins", "a dual package has an even pin count; give package.sides")
            if layout == "quad" and n % 4:
                ctx.bad("package.pins", "a quad package has a pin count divisible by 4; give package.sides")
            sides = _sides(layout, n)
        else:
            allowed = {"left", "right"} if layout == "dual" else {"left", "bottom", "right", "top"}
            if _keys(ctx, sides, "package.sides", allowed):
                listed = [x for v in sides.values() for x in (v or [])]
                if sorted(listed) != list(range(1, n + 1)):
                    ctx.bad("package.sides", f"must list pins 1 to {n} once each")
            sides = {k: list(sides.get(k) or []) for k in allowed} if isinstance(sides, dict) else _sides(layout, n)
        package = Package(ptype, n, layout, sides, ctx.ref(pk.get("ref"), "package.ref") or Ref("?", "?", 1),
                          bool(pk.get("exposed_pad")))
        if pk.get("outline") is not None:
            package.outline = _outline(ctx, pk["outline"], package)
        if pk.get("variants") is not None:
            package.variants = _variants(ctx, pk["variants"])

    supply = _supply(ctx, data["supply"]) if data.get("supply") is not None else []

    # Hooks
    hooks: dict[str, Hook] = {}
    for i, h in enumerate(data.get("hooks") or []):
        p = f"hooks[{i}]"
        if not _keys(ctx, h, p, {"id", "call", "kind", "source", "symbol"}):
            continue
        hid, call, kind = ctx.need(h, "id", p), ctx.need(h, "call", p), ctx.need(h, "kind", p)
        if kind and kind not in HOOK_KINDS:
            ctx.bad(f"{p}.kind", f"{kind!r} is not one of {', '.join(HOOK_KINDS)}")
        if hid in hooks:
            ctx.bad(f"{p}.id", f"hook {hid!r} is listed twice")
        src, sym = str(h.get("source") or ""), str(h.get("symbol") or "")
        if sym and not src:
            ctx.bad(f"{p}.symbol", "needs source: the file the symbol is declared in")
        if src:
            f = root / src
            if not f.is_file():
                ctx.bad(f"{p}.source", f"no file {src}")
            elif sym and not re.search(rf"\b{re.escape(sym)}\b", f.read_text(errors="replace")):
                ctx.bad(f"{p}.symbol", f"{sym!r} does not appear in {src}: the hook no longer exists in the port")
        if hid and call:
            hooks[hid] = Hook(hid, call, kind or "other", src, sym)

    # Pins
    pins: list[Pin] = []
    seen: dict[str, int] = {}
    for i, d in enumerate(data.get("pins") or []):
        p = f"pins[{i}]"
        if not _keys(ctx, d, p, {"number", "name", "type", "domain", "function", "hook", "unused", "ref",
                                 "unverified"}):
            continue
        num = d.get("number")
        if num != "EP" and (not isinstance(num, int) or isinstance(num, bool)):
            ctx.bad(f"{p}.number", f"must be a pin number or EP (the exposed pad), not {num!r}")
            continue
        if str(num) in seen:
            ctx.bad(f"{p}.number", f"pin {num} is listed twice (also pins[{seen[str(num)]}])")
        seen[str(num)] = i
        if package and num != "EP" and not 1 <= num <= package.pins:
            ctx.bad(f"{p}.number", f"pin {num} is outside 1 to {package.pins}")
        name = ctx.need(d, "name", p) or "?"
        ptype = ctx.need(d, "type", p) or "nc"
        if ptype not in PIN_TYPES:
            ctx.bad(f"{p}.type", f"{ptype!r} is not one of {', '.join(PIN_TYPES)}")
            ptype = "nc"
        hook = str(d.get("hook") or "")
        if hook and hook not in hooks:
            ctx.bad(f"{p}.hook", f"{hook!r} is not a hook listed under hooks ({', '.join(hooks) or 'none'})")
        domain = str(d.get("domain") or "")
        if not domain and ptype not in ("ground", "nc"):
            ctx.bad(f"{p}.domain", "missing: the supply that sets this pin's levels (the pin's own name for a supply)")
        function = ctx.need(d, "function", p) or ""
        pins.append(Pin(num, name, ptype, domain, function, ctx.ref(d.get("ref"), f"{p}.ref") or Ref("?", "?", 1),
                        hook, str(d.get("unused") or ""), str(d.get("unverified") or "")))
    if package:
        missing = [n for n in range(1, package.pins + 1) if str(n) not in seen]
        if missing:
            ctx.bad("pins", f"no entry for pin(s) {', '.join(map(str, missing))}")
        if package.exposed_pad and "EP" not in seen:
            ctx.bad("pins", "package.exposed_pad is set but no pin has number EP")
        if not package.exposed_pad and "EP" in seen:
            ctx.bad("package.exposed_pad", "a pin has number EP: set exposed_pad: true")
    names = {p.name for p in pins}

    # Block diagram
    bd = data.get("block_diagram") or {}
    blocks: list[Block] = []
    links: list[Link] = []
    blocks_ref = None
    blocks_unverified = ""
    if bd and _keys(ctx, bd, "block_diagram", {"ref", "blocks", "links", "unverified"}):
        blocks_unverified = str(bd.get("unverified") or "")
        blocks_ref = ctx.ref(bd.get("ref"), "block_diagram.ref")
        cells = {}
        for i, b in enumerate(bd.get("blocks") or []):
            p = f"block_diagram.blocks[{i}]"
            if not _keys(ctx, b, p, {"id", "label", "detail", "at", "pins", "tone", "side", "ref", "unverified"}):
                continue
            bid, label = ctx.need(b, "id", p), ctx.need(b, "label", p)
            at = b.get("at")
            if not (isinstance(at, list) and len(at) == 2 and all(isinstance(x, int) and x >= 0 for x in at)):
                ctx.bad(f"{p}.at", f"must be [column, row], not {at!r}")
                at = [0, i]
            if tuple(at) in cells:
                ctx.bad(f"{p}.at", f"cell {at} is taken by block {cells[tuple(at)]!r}")
            cells[tuple(at)] = bid
            bpins = [str(x) for x in (b.get("pins") or [])]
            for x in bpins:
                if x not in names:
                    ctx.bad(f"{p}.pins", f"no pin named {x!r}")
            tone = str(b.get("tone") or "brand")
            if tone not in T.TONES:
                ctx.bad(f"{p}.tone", f"{tone!r} is not one of {', '.join(T.TONES)}")
                tone = "brand"
            side = str(b.get("side") or "")
            if side not in ("", "left", "right"):
                ctx.bad(f"{p}.side", "must be left or right")
            if any(x.id == bid for x in blocks):
                ctx.bad(f"{p}.id", f"block {bid!r} is listed twice")
            blocks.append(Block(bid or "?", label or "?", (at[0], at[1]),
                                ctx.ref(b.get("ref"), f"{p}.ref", blocks_ref) or Ref("?", "?", 1),
                                str(b.get("detail") or ""), bpins, tone, side, str(b.get("unverified") or "")))
        ids = {b.id for b in blocks}
        for i, ln in enumerate(bd.get("links") or []):
            p = f"block_diagram.links[{i}]"
            if not _keys(ctx, ln, p, {"from", "to", "label", "both", "unverified"}):
                continue
            a, b = ctx.need(ln, "from", p), ctx.need(ln, "to", p)
            for k, v in (("from", a), ("to", b)):
                if v and v not in ids:
                    ctx.bad(f"{p}.{k}", f"no block {v!r}")
            links.append(Link(a or "?", b or "?", str(ln.get("label") or ""), bool(ln.get("both")),
                              str(ln.get("unverified") or "")))

    # Circuits
    circuits: list[Circuit] = []
    for ci, c in enumerate(data.get("circuits") or []):
        circ = _circuit(ctx, c, f"circuits[{ci}]", pins, hooks)
        if circ:
            if any(x.id == circ.id for x in circuits):
                ctx.bad(f"circuits[{ci}].id", f"circuit {circ.id!r} is listed twice")
            circuits.append(circ)

    from . import chipdoc

    doc = chipdoc.parse(ctx, _keys, data, root)

    if ctx.problems:
        raise HardwareError(ctx.problems)
    return Hardware(chip, package, hooks, pins, blocks, links, blocks_ref, circuits, ctx.docs,
                    blocks_unverified=blocks_unverified, supply=supply, doc=doc)


def _circuit(ctx: _Ctx, c, path: str, chip_pins: list[Pin], hooks: dict[str, Hook]) -> Circuit | None:
    if not _keys(ctx, c, path, {"id", "title", "description", "ref", "parts", "nets", "unused"}):
        return None
    cid = ctx.need(c, "id", path) or "?"
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", cid):
        ctx.bad(f"{path}.id", "lower-case letters, digits and hyphens: it names the figure")
    title = ctx.need(c, "title", path) or "?"
    cref = ctx.ref(c.get("ref"), f"{path}.ref") or Ref("?", "?", 1)
    parts: dict[str, Part] = {}
    for i, d in enumerate(c.get("parts") or []):
        p = f"{path}.parts[{i}]"
        if not _keys(ctx, d, p, {"id", "kind", "value", "label", "pins", "ref", "unverified"}):
            continue
        pid, kind = ctx.need(d, "id", p), ctx.need(d, "kind", p)
        if not pid or not kind:
            continue
        if kind not in PART_KINDS:
            ctx.bad(f"{p}.kind", f"{kind!r} is not one of {', '.join(PART_KINDS)}")
            continue
        if pid in parts:
            ctx.bad(f"{p}.id", f"part {pid!r} is listed twice")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", pid):
            ctx.bad(f"{p}.id", f"{pid!r}: a designator is a letter then letters, digits or _")
        plist: list[tuple[str, str]] = []
        if kind == "chip":
            # Pins that share a name (GND on several package pins) are one node of the circuit.
            plist = [(n, n) for n in dict.fromkeys(x.name for x in chip_pins)]
        elif kind in TWO_PIN:
            plist = [(x, x) for x in TWO_PIN[kind]]
        else:
            for j, q in enumerate(d.get("pins") or []):
                if isinstance(q, (str, int)):
                    plist.append((str(q), str(q)))
                elif isinstance(q, dict) and q.get("name") is not None:
                    plist.append((str(q["name"]), str(q.get("label") or q["name"])))
                else:
                    ctx.bad(f"{p}.pins[{j}]", "a pin is a name or {name, label}")
            if not plist:
                ctx.bad(f"{p}.pins", f"a {kind} lists its pins")
            if len({n for n, _ in plist}) != len(plist):
                ctx.bad(f"{p}.pins", "a pin name is listed twice")
        if kind != "chip" and d.get("pins") and kind in TWO_PIN:
            ctx.bad(f"{p}.pins", f"a {kind} has pins 1 and 2 (or {', '.join(PIN_ALIASES)}); do not list them")
        parts[pid] = Part(pid, kind, ctx.ref(d.get("ref"), f"{p}.ref", cref) or cref, str(d.get("value") or ""),
                          str(d.get("label") or ""), plist, str(d.get("unverified") or ""))
    chips = [x for x in parts.values() if x.kind == "chip"]
    if len(chips) != 1:
        ctx.bad(f"{path}.parts", f"needs exactly one part of kind chip (the documented chip), found {len(chips)}")

    def node(s, p: str) -> tuple[str, str] | None:
        if not isinstance(s, str) or "." not in s:
            ctx.bad(p, f"a node is PART.PIN, not {s!r}")
            return None
        pid, pin = s.split(".", 1)
        part = parts.get(pid)
        if part is None:
            ctx.bad(p, f"{s}: no part {pid!r}")
            return None
        if part.two_pin:
            pin = PIN_ALIASES.get(pin, pin)
        names = [n for n, _ in part.pins]
        if part.kind == "chip" and pin not in names:
            by_num = [x.name for x in chip_pins if str(x.number) == pin]
            if by_num:
                pin = by_num[0]
        if pin not in names:
            ctx.bad(p, f"{s}: {pid} has no pin {pin!r}")
            return None
        return (pid, pin)

    nets: list[Net] = []
    where: dict[tuple[str, str], str] = {}
    for i, d in enumerate(c.get("nets") or []):
        p = f"{path}.nets[{i}]"
        if not _keys(ctx, d, p, {"name", "kind", "label", "nodes", "ref", "unverified", "hook"}):
            continue
        name = ctx.need(d, "name", p) or "?"
        kind = str(d.get("kind") or "signal")
        if kind not in NET_KINDS:
            ctx.bad(f"{p}.kind", f"{kind!r} is not one of {', '.join(NET_KINDS)}")
        nodes = []
        for j, s in enumerate(d.get("nodes") or []):
            nd = node(s, f"{p}.nodes[{j}]")
            if nd is None:
                continue
            if nd in where:
                ctx.bad(f"{p}.nodes[{j}]", f"{s} is already on net {where[nd]!r}")
                continue
            where[nd] = name
            nodes.append(nd)
        # A net of the chip's repeated pin name counts each package pin as a node.
        count = sum(len([x for x in chip_pins if x.name == pn]) if parts[pid].kind == "chip" else 1
                    for pid, pn in nodes)
        if count < 2:
            ctx.bad(f"{p}.nodes", f"net {name!r} has {count} node(s); a net joins at least two")
        if any(x.name == name for x in nets):
            ctx.bad(f"{p}.name", f"net {name!r} is listed twice")
        hook_set = "hook" in d
        raw = d.get("hook")
        if isinstance(raw, list):
            net_hooks = [str(x) for x in raw if x]
            if len(net_hooks) != len(raw) or len(set(net_hooks)) != len(net_hooks):
                ctx.bad(f"{p}.hook", "a list of distinct hook ids")
        else:
            net_hooks = [str(raw)] if raw else []
        if hook_set and net_hooks:
            for h in net_hooks:
                if h not in hooks:
                    ctx.bad(f"{p}.hook", f"{h!r} is not a hook listed under hooks ({', '.join(hooks) or 'none'})")
            if not any(parts[pid].kind in ("chip", "mcu") for pid, _pn in nodes):
                ctx.bad(f"{p}.hook", f"net {name!r} has no chip or MCU pin, so no wire of it shows a hook")
        nets.append(Net(name, kind, nodes, ctx.ref(d.get("ref"), f"{p}.ref", cref) or cref,
                        str(d.get("label") or ""), str(d.get("unverified") or ""), hook_set, net_hooks))
    unused = []
    for j, s in enumerate(c.get("unused") or []):
        nd = node(s, f"{path}.unused[{j}]")
        if nd:
            if nd in where:
                ctx.bad(f"{path}.unused[{j}]", f"{s} is marked unused but is on net {where[nd]!r}")
            unused.append(nd)
    # Every pin is used or explicitly unused.
    for part in parts.values():
        for pn, _ in part.pins:
            if (part.id, pn) in where or (part.id, pn) in unused:
                continue
            if part.kind == "chip" and all(x.type == "nc" for x in chip_pins if x.name == pn):
                continue
            ctx.bad(f"{path}", f"{part.id}.{pn} is on no net: connect it or list it under unused")
    return Circuit(cid, title, cref, parts, nets, unused, str(c.get("description") or ""))
