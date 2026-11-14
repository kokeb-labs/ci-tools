"""The chip-first README content of ``docs/hardware.yml``: what the chip is, what it does, where it is used, how
the driver covers it and what goes over its bus. All four keys are optional; each one switches on a figure and a
generated region (see ``docs/readme-chip-first.md`` in ci-tools)::

    overview:                               # the chip in one line, its headline numbers and where it sits
      summary: "a stepper motor controller and driver for two-phase motors"   # completes "The <chip> is ..."
      category: Stepper motor controller and driver                         # the hero's kicker
      ref: cover
      applications: [Robotics and industrial drives, {text: "3D printers", ref: cover}]
      specs:                                # 2 to 6 headline numbers, one tile each
        - {value: "10 to 55 V", label: motor supply, ref: electrical}
      system:                               # the hero: host -> chip -> what it drives, and what it reads back
        host: MCU
        bus: SPI or UART
        drives: [{label: "8 MOSFETs", detail: "two full bridges", ref: sample}]
        senses: [{label: Encoder, ref: encoder}]
    driver:                                 # headers the capability names are checked against
      api: [inc/x.hpp]
      registers: [inc/x_registers.hpp]
    capabilities:                           # what the chip does, one card each, and how the driver covers it
      - {id: motion, title: Ramp generator, icon: ramp, what: "Moves to a target with S-shaped ramps",
         status: supported, api: [MoveTo, SetRamp], registers: [RAMPMODE, XTARGET], docs: motion.md, ref: ramp}
    frames:                                 # what one bus transfer carries, bit by bit
      - id: spi
        title: SPI datagram
        bits: 40
        ref: spi
        rows:
          - {label: Write, fields: [{name: W, bits: 39}, {name: address, bits: [38, 32]}, {name: data, bits: [31, 0]}]}
        decode: {row: Reply, field: status, ref: status, bits: [{bit: 7, name: status_stop_r}]}
        waveform: {spi_mode: 3, select: CSN, clock: SCK, lanes: [{name: SDI, row: Write}, {name: SDO, row: Reply}]}

Every fact cites the datasheet like the rest of the file, and the names a capability gives are checked against the
driver's headers, so the coverage table cannot name an API or a register that does not exist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..figkit import theme as T

#: Capability status -> (tone, label in the figure and the coverage table, meaning).
STATUSES: dict[str, tuple[str, str, str]] = {
    "supported": ("green", "Supported", "the driver covers it and a host test checks it"),
    "guarded": ("amber", "Guarded", "covered, behind an explicit acknowledgement because a wrong value can do harm"),
    "partial": ("blue", "Partial", "covered in part; the coverage map says which part"),
    "read-only": ("teal", "Read only", "the driver reads and reports it, and does not set it"),
    "not-covered": ("slate", "Not covered", "the chip has it and the driver leaves it alone"),
}


@dataclass
class Item:
    """A thing with a label, an optional detail and a citation (an application, a block of the hero)."""

    label: str
    ref: object
    detail: str = ""
    unverified: str = ""


@dataclass
class Spec:
    value: str
    label: str
    ref: object
    unverified: str = ""


@dataclass
class System:
    host: str
    bus: str
    drives: list[Item] = field(default_factory=list)
    senses: list[Item] = field(default_factory=list)


@dataclass
class Overview:
    summary: str
    category: str
    ref: object
    applications: list[Item] = field(default_factory=list)
    specs: list[Spec] = field(default_factory=list)
    system: System | None = None


@dataclass
class Capability:
    id: str
    title: str
    icon: str
    what: str
    status: str
    ref: object
    api: list[str] = field(default_factory=list)
    registers: list[str] = field(default_factory=list)
    docs: str = ""
    note: str = ""
    unverified: str = ""

    @property
    def tone(self) -> str:
        return STATUSES[self.status][0]


@dataclass
class Field:
    name: str
    hi: int
    lo: int
    tone: str = "slate"
    short: str = ""

    @property
    def width(self) -> int:
        return self.hi - self.lo + 1


@dataclass
class FrameRow:
    label: str
    fields: list[Field]
    sub: str = ""


@dataclass
class Decode:
    row: str
    field: str
    bits: list[tuple[int, str]]
    ref: object


@dataclass
class Lane:
    name: str
    row: str  # the row whose fields this data line carries; "" for a line held idle


@dataclass
class Waveform:
    spi_mode: int
    select: str
    clock: str
    lanes: list[Lane]


@dataclass
class Frame:
    id: str
    title: str
    bits: int
    ref: object
    rows: list[FrameRow]
    description: str = ""
    decode: Decode | None = None
    waveform: Waveform | None = None

    def row(self, label: str) -> FrameRow | None:
        return next((r for r in self.rows if r.label == label), None)


@dataclass
class ChipDoc:
    overview: Overview | None = None
    capabilities: list[Capability] = field(default_factory=list)
    frames: list[Frame] = field(default_factory=list)
    api_sources: list[str] = field(default_factory=list)
    register_sources: list[str] = field(default_factory=list)


KEYS = {"overview", "driver", "capabilities", "frames"}
_SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")


def _text(ctx, d: dict, key: str, path: str, required: bool = False) -> str:
    v = d.get(key)
    if v is None or v == "":
        if required:
            ctx.bad(f"{path}.{key}", "missing")
        return ""
    if not isinstance(v, (str, int, float)) or isinstance(v, bool):
        ctx.bad(f"{path}.{key}", f"must be text, not {type(v).__name__}")
        return ""
    return str(v)


def _list(ctx, v, path: str) -> list:
    if v is None:
        return []
    if not isinstance(v, list):
        ctx.bad(path, f"must be a list, not {type(v).__name__}")
        return []
    return v


def _item(ctx, keys, v, path: str, default_ref) -> Item | None:
    if isinstance(v, str):
        if default_ref is None:
            ctx.bad(path, "a plain entry needs a ref on its parent; write {label, ref}")
            return None
        return Item(v, default_ref)
    if not keys(ctx, v, path, {"label", "text", "detail", "ref", "unverified"}):
        return None
    label = _text(ctx, v, "label", path) or _text(ctx, v, "text", path)
    if not label:
        ctx.bad(f"{path}.label", "missing")
        return None
    ref = ctx.ref(v.get("ref"), f"{path}.ref", default_ref)
    return Item(label, ref, _text(ctx, v, "detail", path), _text(ctx, v, "unverified", path))


def _overview(ctx, keys, o) -> Overview | None:
    p = "overview"
    if not keys(ctx, o, p, {"summary", "category", "ref", "applications", "specs", "system"}):
        return None
    summary, category = _text(ctx, o, "summary", p, True), _text(ctx, o, "category", p, True)
    if summary and summary.rstrip().endswith("."):
        ctx.bad(f"{p}.summary", "leave out the full stop: the README writes 'The <chip> is <summary>.'")
    ref = ctx.ref(o.get("ref"), f"{p}.ref")
    apps = [a for i, v in enumerate(_list(ctx, o.get("applications"), f"{p}.applications"))
            if (a := _item(ctx, keys, v, f"{p}.applications[{i}]", ref)) is not None]
    specs: list[Spec] = []
    for i, s in enumerate(_list(ctx, o.get("specs"), f"{p}.specs")):
        q = f"{p}.specs[{i}]"
        if not keys(ctx, s, q, {"value", "label", "ref", "unverified"}):
            continue
        value, label = _text(ctx, s, "value", q, True), _text(ctx, s, "label", q, True)
        r = ctx.ref(s.get("ref"), f"{q}.ref")
        if value and label and r:
            specs.append(Spec(value, label, r, _text(ctx, s, "unverified", q)))
    if len(specs) > 6:
        ctx.bad(f"{p}.specs", f"{len(specs)} specs: the hero has room for six; keep the ones a buyer compares")
    system = None
    sy = o.get("system")
    if sy is not None and keys(ctx, sy, f"{p}.system", {"host", "bus", "drives", "senses"}):
        bus = _text(ctx, sy, "bus", f"{p}.system", True)
        drives = [a for i, v in enumerate(_list(ctx, sy.get("drives"), f"{p}.system.drives"))
                  if (a := _item(ctx, keys, v, f"{p}.system.drives[{i}]", ref)) is not None]
        senses = [a for i, v in enumerate(_list(ctx, sy.get("senses"), f"{p}.system.senses"))
                  if (a := _item(ctx, keys, v, f"{p}.system.senses[{i}]", ref)) is not None]
        if len(drives) > 3:
            ctx.bad(f"{p}.system.drives", "at most three steps from the chip to the load")
        system = System(_text(ctx, sy, "host", f"{p}.system") or "MCU", bus, drives, senses)
    if not (summary and category and ref):
        return None
    return Overview(summary, category, ref, apps, specs, system)


def _sources(ctx, root, d, key: str) -> list[str]:
    out = []
    for i, s in enumerate(_list(ctx, d.get(key), f"driver.{key}")):
        if not isinstance(s, str):
            ctx.bad(f"driver.{key}[{i}]", "must be a path")
            continue
        if not (root / s).is_file():
            ctx.bad(f"driver.{key}[{i}]", f"no file {s}")
            continue
        out.append(s)
    return out


def _capabilities(ctx, keys, root, caps, api_src: list[str], reg_src: list[str]) -> list[Capability]:
    from .icons import ICONS

    api_text = "\n".join((root / s).read_text(errors="replace") for s in api_src)
    reg_text = "\n".join((root / s).read_text(errors="replace") for s in reg_src)
    out: list[Capability] = []
    for i, c in enumerate(_list(ctx, caps, "capabilities")):
        p = f"capabilities[{i}]"
        if not keys(ctx, c, p, {"id", "title", "icon", "what", "status", "api", "registers", "docs", "note", "ref",
                                "unverified"}):
            continue
        cid, title = _text(ctx, c, "id", p, True), _text(ctx, c, "title", p, True)
        icon, what = _text(ctx, c, "icon", p, True), _text(ctx, c, "what", p, True)
        status = _text(ctx, c, "status", p, True)
        if cid and not _SLUG.fullmatch(cid):
            ctx.bad(f"{p}.id", "lower-case letters, digits and hyphens")
        if cid and any(x.id == cid for x in out):
            ctx.bad(f"{p}.id", f"capability {cid!r} is listed twice")
        if icon and icon not in ICONS:
            ctx.bad(f"{p}.icon", f"{icon!r} is not one of {', '.join(sorted(ICONS))}")
        if status and status not in STATUSES:
            ctx.bad(f"{p}.status", f"{status!r} is not one of {', '.join(STATUSES)}")
        if what and len(what) > 110:
            ctx.bad(f"{p}.what", f"{len(what)} characters: one short sentence (110 at most) fits a card")
        api = [str(x) for x in _list(ctx, c.get("api"), f"{p}.api")]
        regs = [str(x) for x in _list(ctx, c.get("registers"), f"{p}.registers")]
        if status and status != "not-covered" and not api:
            ctx.bad(f"{p}.api", f"a {status} capability names the driver calls that cover it")
        for name in api:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:]*", name):
                ctx.bad(f"{p}.api", f"{name!r}: a C++ name, without parentheses")
            elif api_src and not re.search(rf"\b{re.escape(name.split('::')[-1])}\b", api_text):
                ctx.bad(f"{p}.api", f"{name!r} is not in {', '.join(api_src)}")
        for name in regs:
            if reg_src and not re.search(rf"\b{re.escape(name)}\b", reg_text):
                ctx.bad(f"{p}.registers", f"{name!r} is not in {', '.join(reg_src)}")
        docs = _text(ctx, c, "docs", p)
        if docs and not (root / "docs" / docs.split("#")[0]).is_file():
            ctx.bad(f"{p}.docs", f"no page docs/{docs.split('#')[0]}")
        ref = ctx.ref(c.get("ref"), f"{p}.ref")
        if cid and title and icon in ICONS and what and status in STATUSES and ref:
            out.append(Capability(cid, title, icon, what, status, ref, api, regs, docs, _text(ctx, c, "note", p),
                                  _text(ctx, c, "unverified", p)))
    return out


def _bits(ctx, v, path: str, width: int) -> tuple[int, int] | None:
    if isinstance(v, int) and not isinstance(v, bool):
        hi = lo = v
    elif isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in v):
        hi, lo = v
    else:
        ctx.bad(path, f"a bit (39) or a range [high, low], not {v!r}")
        return None
    if not (0 <= lo <= hi < width):
        ctx.bad(path, f"[{hi}, {lo}] is not a range inside {width - 1} to 0 (high first)")
        return None
    return hi, lo


def _frames(ctx, keys, frames) -> list[Frame]:
    out: list[Frame] = []
    for i, f in enumerate(_list(ctx, frames, "frames")):
        p = f"frames[{i}]"
        if not keys(ctx, f, p, {"id", "title", "description", "bits", "ref", "rows", "decode", "waveform"}):
            continue
        fid, title = _text(ctx, f, "id", p, True), _text(ctx, f, "title", p, True)
        if fid and not _SLUG.fullmatch(fid):
            ctx.bad(f"{p}.id", "lower-case letters, digits and hyphens: it names the figure")
        if fid and any(x.id == fid for x in out):
            ctx.bad(f"{p}.id", f"frame {fid!r} is listed twice")
        width = f.get("bits")
        if not isinstance(width, int) or isinstance(width, bool) or not 1 <= width <= 64:
            ctx.bad(f"{p}.bits", f"the frame length in bits, 1 to 64, not {width!r}")
            continue
        ref = ctx.ref(f.get("ref"), f"{p}.ref")
        rows: list[FrameRow] = []
        for j, r in enumerate(_list(ctx, f.get("rows"), f"{p}.rows")):
            q = f"{p}.rows[{j}]"
            if not keys(ctx, r, q, {"label", "sub", "fields"}):
                continue
            label = _text(ctx, r, "label", q, True)
            fields: list[Field] = []
            for k, fd in enumerate(_list(ctx, r.get("fields"), f"{q}.fields")):
                fq = f"{q}.fields[{k}]"
                if not keys(ctx, fd, fq, {"name", "bits", "tone", "short"}):
                    continue
                name = _text(ctx, fd, "name", fq, True)
                b = _bits(ctx, fd.get("bits"), f"{fq}.bits", width)
                tone = _text(ctx, fd, "tone", fq) or "slate"
                if tone not in T.TONES:
                    ctx.bad(f"{fq}.tone", f"{tone!r} is not one of {', '.join(T.TONES)}")
                    tone = "slate"
                if name and b:
                    fields.append(Field(name, b[0], b[1], tone, _text(ctx, fd, "short", fq)))
            # The fields of a row cover every bit once, most significant first.
            nxt = width - 1
            for fd in fields:
                if fd.hi != nxt:
                    ctx.bad(f"{q}.fields", f"field {fd.name!r} starts at bit {fd.hi}; the bit after the previous "
                            f"field is {nxt} (list the fields from bit {width - 1} down to 0, no gap, no overlap)")
                    break
                nxt = fd.lo - 1
            else:
                if fields and nxt != -1:
                    ctx.bad(f"{q}.fields", f"bits {nxt} to 0 are in no field")
            if label and any(x.label == label for x in rows):
                ctx.bad(f"{q}.label", f"row {label!r} is listed twice")
            if label and fields:
                rows.append(FrameRow(label, fields, _text(ctx, r, "sub", q)))
        if not rows:
            ctx.bad(f"{p}.rows", "a frame has at least one row")
        decode = None
        d = f.get("decode")
        if d is not None and keys(ctx, d, f"{p}.decode", {"row", "field", "bits", "ref"}):
            rl, fn = _text(ctx, d, "row", f"{p}.decode", True), _text(ctx, d, "field", f"{p}.decode", True)
            row = next((r for r in rows if r.label == rl), None)
            fd = next((x for x in row.fields if x.name == fn), None) if row else None
            if rl and row is None:
                ctx.bad(f"{p}.decode.row", f"no row {rl!r}")
            elif fn and fd is None:
                ctx.bad(f"{p}.decode.field", f"row {rl!r} has no field {fn!r}")
            bits: list[tuple[int, str]] = []
            for k, b in enumerate(_list(ctx, d.get("bits"), f"{p}.decode.bits")):
                bq = f"{p}.decode.bits[{k}]"
                if not keys(ctx, b, bq, {"bit", "name"}):
                    continue
                n, name = b.get("bit"), _text(ctx, b, "name", bq, True)
                if fd and (not isinstance(n, int) or not 0 <= n < fd.width):
                    ctx.bad(f"{bq}.bit", f"{n!r} is not a bit of the {fd.width}-bit field (0 to {fd.width - 1})")
                    continue
                if name:
                    bits.append((int(n), name))
            if fd and sorted(b for b, _ in bits) != list(range(fd.width)):
                ctx.bad(f"{p}.decode.bits", f"name each of the {fd.width} bits of {fn!r} once")
            dref = ctx.ref(d.get("ref"), f"{p}.decode.ref", ref)
            if fd:
                decode = Decode(rl, fn, sorted(bits, reverse=True), dref)
        wave = None
        w = f.get("waveform")
        if w is not None and keys(ctx, w, f"{p}.waveform", {"spi_mode", "select", "clock", "lanes"}):
            mode = w.get("spi_mode")
            if mode not in (0, 1, 2, 3):
                ctx.bad(f"{p}.waveform.spi_mode", f"0, 1, 2 or 3 (CPOL * 2 + CPHA), not {mode!r}")
            lanes = []
            for k, ln in enumerate(_list(ctx, w.get("lanes"), f"{p}.waveform.lanes")):
                lq = f"{p}.waveform.lanes[{k}]"
                if not keys(ctx, ln, lq, {"name", "row"}):
                    continue
                name, rl = _text(ctx, ln, "name", lq, True), _text(ctx, ln, "row", lq)
                if rl and not any(r.label == rl for r in rows):
                    ctx.bad(f"{lq}.row", f"no row {rl!r}")
                if name:
                    lanes.append(Lane(name, rl))
            sel, clk = _text(ctx, w, "select", f"{p}.waveform", True), _text(ctx, w, "clock", f"{p}.waveform", True)
            if mode in (0, 1, 2, 3) and sel and clk:
                wave = Waveform(int(mode), sel, clk, lanes)
        if fid and title and ref and rows:
            out.append(Frame(fid, title, width, ref, rows, _text(ctx, f, "description", p), decode, wave))
    return out


def parse(ctx, keys, data: dict, root) -> ChipDoc:
    doc = ChipDoc()
    if data.get("overview") is not None:
        doc.overview = _overview(ctx, keys, data["overview"])
    drv = data.get("driver")
    if drv is not None and keys(ctx, drv, "driver", {"api", "registers"}):
        doc.api_sources = _sources(ctx, root, drv, "api")
        doc.register_sources = _sources(ctx, root, drv, "registers")
    if data.get("capabilities") is not None:
        doc.capabilities = _capabilities(ctx, keys, root, data["capabilities"], doc.api_sources,
                                         doc.register_sources)
    if data.get("frames") is not None:
        doc.frames = _frames(ctx, keys, data["frames"])
    return doc
