"""The chip-first README content of ``docs/hardware.yml``: what the chip is, what it does, where it is used, how
the driver covers it and what goes over its bus. All four keys are optional; each one switches on a figure and a
generated region (see ``docs/readme-chip-first.md`` in ci-tools)::

    overview:                               # the chip in one line, its headline numbers and where it sits
      summary: "a stepper motor controller and driver for two-phase motors"   # completes "The <chip> is ..."
      category: Stepper motor controller and driver                         # the hero's kicker
      ref: cover
      applications: [Robotics and industrial drives, {text: "3D printers", ref: cover}]
      applications_ref: apps                # optional: where the list comes from, when not from ref
      applications_inferred: "..."          # optional: the datasheet names no uses; say what they are inferred from
      inside: chip                          # optional: the "Inside the ..." heading (chip, module, device, sensor, part)
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
      kind: device                          # optional: device (a chip, module or instrument) or protocol
    capabilities:                           # what the chip does, one card each, and how the driver covers it
      - {id: motion, title: Ramp generator, icon: ramp, what: "Moves to a target with S-shaped ramps",
         status: supported, api: [MoveTo, SetRamp], registers: [RAMPMODE, {name: XTARGET, header: kXTarget}],
         docs: motion.md, tests: [tests/test_motion.cpp], ref: ramp}
    frames:                                 # what one bus transfer carries, bit by bit
      - id: spi
        title: SPI datagram
        bits: 40                            # 1 to 128
        bit_order: msb-first                # optional; lsb-first: a UART datagram, bit 0 sent first, bits [first, last]
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
#: The meanings for a protocol driver (``driver.kind: protocol``): there is no chip, and every supported function
#: names the host test that checks it (``tests``).
PROTOCOL_MEANINGS: dict[str, str] = {
    "supported": "the driver implements it and the named host test checks it",
    "guarded": "implemented, behind an explicit acknowledgement because a wrong value can do harm",
    "partial": "implemented in part; the coverage map says which part",
    "read-only": "the driver reads and reports it, and does not set it",
    "not-covered": "the protocol defines it and the driver leaves it out",
}
DRIVER_KINDS = ("device", "protocol")
INSIDE = ("chip", "module", "device", "sensor", "part")
#: Where a test named under ``tests`` is looked for.
TEST_DIRS = ("tests", "test")


def meaning(status: str, kind: str = "device") -> str:
    """What a status means, in the words of the driver's kind."""
    return PROTOCOL_MEANINGS[status] if kind == "protocol" else STATUSES[status][2]


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
    applications_ref: object = None  # the citation of the list, when it is not ``ref``
    applications_inferred: str = ""  # the datasheet names no uses: what the list is inferred from
    inside: str = ""  # the word of the "Inside the ..." heading

    @property
    def uses_ref(self):
        return self.applications_ref or self.ref


@dataclass
class Register:
    """A register behind a capability: the datasheet's mnemonic, and the header constant when the header spells it
    otherwise (the pill and the table show ``name``; the header check looks for ``header``)."""

    name: str
    header: str = ""

    def __str__(self) -> str:
        return self.name


@dataclass
class Capability:
    id: str
    title: str
    icon: str
    what: str
    status: str
    ref: object
    api: list[str] = field(default_factory=list)
    registers: list[Register] = field(default_factory=list)
    docs: str = ""
    note: str = ""
    unverified: str = ""
    tests: list[str] = field(default_factory=list)

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
    first: int = -1  # lsb-first frames: the datasheet's number of the field's first bit (sent first, drawn left)
    last: int = -1

    @property
    def width(self) -> int:
        return self.hi - self.lo + 1

    def shown(self) -> tuple[int, int]:
        """The bit numbers written at the field's left and right edges."""
        return (self.first, self.last) if self.first >= 0 else (self.hi, self.lo)


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
    lsb_first: bool = False  # sent byte by byte, each byte least significant bit first (a UART datagram)

    def row(self, label: str) -> FrameRow | None:
        return next((r for r in self.rows if r.label == label), None)


@dataclass
class ChipDoc:
    overview: Overview | None = None
    capabilities: list[Capability] = field(default_factory=list)
    frames: list[Frame] = field(default_factory=list)
    api_sources: list[str] = field(default_factory=list)
    register_sources: list[str] = field(default_factory=list)
    kind: str = "device"  # driver.kind: device or protocol


KEYS = {"overview", "driver", "capabilities", "frames"}
#: The longest frame the figure draws (a 72-bit TMCL UART datagram fits; the bit grid stays readable).
MAX_FRAME_BITS = 128
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
    if not keys(ctx, o, p, {"summary", "category", "ref", "applications", "applications_ref",
                            "applications_inferred", "specs", "system", "inside"}):
        return None
    summary, category = _text(ctx, o, "summary", p, True), _text(ctx, o, "category", p, True)
    if summary and summary.rstrip().endswith("."):
        ctx.bad(f"{p}.summary", "leave out the full stop: the README writes 'The <chip> is <summary>.'")
    ref = ctx.ref(o.get("ref"), f"{p}.ref")
    apps_ref = ctx.ref(o["applications_ref"], f"{p}.applications_ref") if o.get("applications_ref") is not None \
        else None
    inferred = _text(ctx, o, "applications_inferred", p)
    if (apps_ref or inferred) and not o.get("applications"):
        ctx.bad(f"{p}.applications", "missing: applications_ref and applications_inferred describe the list")
    inside = _text(ctx, o, "inside", p)
    if inside and inside not in INSIDE:
        ctx.bad(f"{p}.inside", f"{inside!r} is not one of {', '.join(INSIDE)}")
        inside = ""
    apps = [a for i, v in enumerate(_list(ctx, o.get("applications"), f"{p}.applications"))
            if (a := _item(ctx, keys, v, f"{p}.applications[{i}]", apps_ref or ref)) is not None]
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
    return Overview(summary, category, ref, apps, specs, system, apps_ref, inferred, inside)


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


def _registers(ctx, v, path: str) -> list[Register]:
    out: list[Register] = []
    for i, r in enumerate(_list(ctx, v, path)):
        if isinstance(r, (str, int, float)) and not isinstance(r, bool):
            out.append(Register(str(r)))
        elif isinstance(r, dict) and not set(r) - {"name", "header"} and r.get("name"):
            h = r.get("header")
            if h is not None and (not isinstance(h, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:]*", h)):
                ctx.bad(f"{path}[{i}].header", f"{h!r}: the constant's C++ name in the header")
                h = ""
            out.append(Register(str(r["name"]), str(h or "")))
        else:
            ctx.bad(f"{path}[{i}]", "a register is its datasheet name, or {name, header} when the header constant "
                    "is spelled otherwise")
    return out


def _test_text(root) -> str:
    out = []
    for d in TEST_DIRS:
        base = root / d
        if base.is_dir():
            for f in sorted(base.rglob("*")):
                if f.is_file() and f.suffix in (".cpp", ".cc", ".c", ".hpp", ".h", ".py"):
                    out.append(f.read_text(errors="replace"))
    return "\n".join(out)


def _capabilities(ctx, keys, root, caps, api_src: list[str], reg_src: list[str], kind: str = "device"
                  ) -> list[Capability]:
    from .icons import ICONS

    api_text = "\n".join((root / s).read_text(errors="replace") for s in api_src)
    reg_text = "\n".join((root / s).read_text(errors="replace") for s in reg_src)
    out: list[Capability] = []
    test_text = None
    for i, c in enumerate(_list(ctx, caps, "capabilities")):
        p = f"capabilities[{i}]"
        if not keys(ctx, c, p, {"id", "title", "icon", "what", "status", "api", "registers", "docs", "note", "ref",
                                "unverified", "tests"}):
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
        regs = _registers(ctx, c.get("registers"), f"{p}.registers")
        if status and status != "not-covered" and not api:
            ctx.bad(f"{p}.api", f"a {status} capability names the driver calls that cover it")
        for name in api:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:]*", name):
                ctx.bad(f"{p}.api", f"{name!r}: a C++ name, without parentheses")
            elif api_src and not re.search(rf"\b{re.escape(name.split('::')[-1])}\b", api_text):
                ctx.bad(f"{p}.api", f"{name!r} is not in {', '.join(api_src)}")
        for r in regs:
            name = r.header or r.name
            if reg_src and not re.search(rf"\b{re.escape(name.split('::')[-1])}\b", reg_text):
                what = f"{r.name!r} (header {r.header!r})" if r.header else repr(r.name)
                ctx.bad(f"{p}.registers", f"{what} is not in {', '.join(reg_src)}")
        tests = [str(x) for x in _list(ctx, c.get("tests"), f"{p}.tests")]
        for t in tests:
            if "/" in t or t.endswith((".cpp", ".cc", ".c", ".py")):
                if not (root / t).is_file():
                    ctx.bad(f"{p}.tests", f"no file {t}")
            else:
                if test_text is None:
                    test_text = _test_text(root)
                if t not in test_text:
                    ctx.bad(f"{p}.tests", f"no test named {t!r} under {' or '.join(d + '/' for d in TEST_DIRS)}")
        if kind == "protocol" and status == "supported" and not tests:
            ctx.bad(f"{p}.tests", "a supported capability of a protocol driver names the host test that checks it "
                    "(a test file such as tests/test_sdo.cpp, or a test case name)")
        docs = _text(ctx, c, "docs", p)
        if docs and not (root / "docs" / docs.split("#")[0]).is_file():
            ctx.bad(f"{p}.docs", f"no page docs/{docs.split('#')[0]}")
        ref = ctx.ref(c.get("ref"), f"{p}.ref")
        if cid and title and icon in ICONS and what and status in STATUSES and ref:
            out.append(Capability(cid, title, icon, what, status, ref, api, regs, docs, _text(ctx, c, "note", p),
                                  _text(ctx, c, "unverified", p), tests))
    return out


def _bits(ctx, v, path: str, width: int, ascending: bool = False) -> tuple[int, int] | None:
    """A field's bits: ``(high, low)``, or with ``ascending`` (an lsb-first frame) ``(first, last)``."""
    if isinstance(v, int) and not isinstance(v, bool):
        hi = lo = v
    elif isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in v):
        hi, lo = v
    else:
        ctx.bad(path, f"a bit (39) or a range [{'first, last' if ascending else 'high, low'}], not {v!r}")
        return None
    if ascending:
        if not (0 <= hi <= lo < width):
            ctx.bad(path, f"[{hi}, {lo}] is not a range inside 0 to {width - 1} (first bit first)")
            return None
        return hi, lo
    if not (0 <= lo <= hi < width):
        ctx.bad(path, f"[{hi}, {lo}] is not a range inside {width - 1} to 0 (high first)")
        return None
    return hi, lo


def _frames(ctx, keys, frames) -> list[Frame]:
    out: list[Frame] = []
    for i, f in enumerate(_list(ctx, frames, "frames")):
        p = f"frames[{i}]"
        if not keys(ctx, f, p, {"id", "title", "description", "bits", "ref", "rows", "decode", "waveform",
                                "bit_order"}):
            continue
        fid, title = _text(ctx, f, "id", p, True), _text(ctx, f, "title", p, True)
        if fid and not _SLUG.fullmatch(fid):
            ctx.bad(f"{p}.id", "lower-case letters, digits and hyphens: it names the figure")
        if fid and any(x.id == fid for x in out):
            ctx.bad(f"{p}.id", f"frame {fid!r} is listed twice")
        width = f.get("bits")
        if not isinstance(width, int) or isinstance(width, bool) or not 1 <= width <= MAX_FRAME_BITS:
            ctx.bad(f"{p}.bits", f"the frame length in bits, 1 to {MAX_FRAME_BITS}, not {width!r}")
            continue
        ref = ctx.ref(f.get("ref"), f"{p}.ref")
        order = _text(ctx, f, "bit_order", p) or "msb-first"
        if order not in ("msb-first", "lsb-first"):
            ctx.bad(f"{p}.bit_order", f"{order!r} is not msb-first or lsb-first")
            order = "msb-first"
        lsb = order == "lsb-first"
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
                b = _bits(ctx, fd.get("bits"), f"{fq}.bits", width, ascending=lsb)
                tone = _text(ctx, fd, "tone", fq) or "slate"
                if tone not in T.TONES:
                    ctx.bad(f"{fq}.tone", f"{tone!r} is not one of {', '.join(T.TONES)}")
                    tone = "slate"
                if name and b and lsb:
                    # Bit 0 is sent first and drawn on the left: the grid runs from width - 1 (left) to 0.
                    fields.append(Field(name, width - 1 - b[0], width - 1 - b[1], tone, _text(ctx, fd, "short", fq),
                                        b[0], b[1]))
                elif name and b:
                    fields.append(Field(name, b[0], b[1], tone, _text(ctx, fd, "short", fq)))
            # The fields of a row cover every bit once, in the order they are sent.
            nxt = width - 1
            for fd in fields:
                if fd.hi != nxt:
                    if lsb:
                        ctx.bad(f"{q}.fields", f"field {fd.name!r} starts at bit {fd.first}; the bit after the "
                                f"previous field is {width - 1 - nxt} (list the fields from bit 0 up to {width - 1}, "
                                "no gap, no overlap)")
                    else:
                        ctx.bad(f"{q}.fields", f"field {fd.name!r} starts at bit {fd.hi}; the bit after the previous "
                                f"field is {nxt} (list the fields from bit {width - 1} down to 0, no gap, no overlap)")
                    break
                nxt = fd.lo - 1
            else:
                if fields and nxt != -1:
                    ctx.bad(f"{q}.fields", f"bits {width - 1 - nxt} to {width - 1} are in no field" if lsb
                            else f"bits {nxt} to 0 are in no field")
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
            if wave and lsb:
                ctx.bad(f"{p}.waveform", "an SPI waveform needs an msb-first frame")
            out.append(Frame(fid, title, width, ref, rows, _text(ctx, f, "description", p), decode, wave, lsb))
    return out


def parse(ctx, keys, data: dict, root) -> ChipDoc:
    doc = ChipDoc()
    if data.get("overview") is not None:
        doc.overview = _overview(ctx, keys, data["overview"])
    drv = data.get("driver")
    if drv is not None and keys(ctx, drv, "driver", {"api", "registers", "kind"}):
        doc.api_sources = _sources(ctx, root, drv, "api")
        doc.register_sources = _sources(ctx, root, drv, "registers")
        kind = _text(ctx, drv, "kind", "driver") or "device"
        if kind not in DRIVER_KINDS:
            ctx.bad("driver.kind", f"{kind!r} is not one of {', '.join(DRIVER_KINDS)}")
            kind = "device"
        doc.kind = kind
    if data.get("capabilities") is not None:
        doc.capabilities = _capabilities(ctx, keys, root, data["capabilities"], doc.api_sources,
                                         doc.register_sources, doc.kind)
    if data.get("frames") is not None:
        doc.frames = _frames(ctx, keys, data["frames"])
    return doc
