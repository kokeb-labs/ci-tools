"""Schematic symbols drawn on a figkit ``Fig``: resistor, capacitor, inductor, solenoid, diode, LED, crystal, fuse,
ground, supply, no-connect, and boxes with pins (the chip, an MCU, a connector).

Every symbol is placed with its pin ends on the routing grid (``G`` pixels) and returns a ``Placed``: the body box
the router must not enter, its pin ends (with the side the pin comes from) and the boxes of its labels. Two-pin
parts are ``LEN`` long from pin end to pin end, pin 1 at the top (vertical) or on the left (horizontal). The shapes
follow IEC 60617 (rectangular resistor), as most current datasheets draw them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..figkit import Box, text_width

G = 8  # routing grid, px
LEN = 6 * G  # a two-pin part, pin end to pin end
STUB = 3 * G  # pin length of a box symbol
PIN_PITCH = 3 * G
PART = "ink"  # stroke of part outlines
WIRE = "ink2"
SW = 1.6
LABEL = 12  # value labels
PIN_NAME = 12.5
PIN_NUM = 11


@dataclass
class Placed:
    id: str
    body: Box
    pins: dict = field(default_factory=dict)  # name -> (x, y, side the pin comes from: L R U D)
    labels: list = field(default_factory=list)  # Box
    ink: list = field(default_factory=list)  # Box: every stroke the symbol draws, for the layout check


def _frame(x: float, y: float, vertical: bool, flip: bool = False):
    """Local frame of a two-pin part: u runs from pin 1 to pin 2, v across. ``flip`` puts pin 1 at the far end."""
    if vertical:
        return (lambda u, v: (x + v, y + LEN - u)) if flip else (lambda u, v: (x + v, y + u))
    return (lambda u, v: (x + LEN - u, y - v)) if flip else (lambda u, v: (x + u, y - v))


def ink_box(pts, sw: float = SW) -> Box:
    """The box a stroke through ``pts`` paints: their bounding box grown by half the stroke width."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Box(min(xs) - sw / 2, min(ys) - sw / 2, max(xs) - min(xs) + sw, max(ys) - min(ys) + sw)


def _path(fig, ink: list, cmds, sw: float = SW, **kw) -> None:
    """``fig.path`` that records the stroke's box in ``ink`` (an arc's bulge is left to the part's body box)."""
    fig.path(cmds, sw=sw, **kw)
    pts = [c[1:3] if c[0] in ("M", "L") else c[2:4] for c in cmds if c[0] in ("M", "L", "A")]
    ink.append(ink_box(pts, sw))


def _poly(fig, T, ink: list, pts, close=False, fill=None, sw=SW, stroke=PART):
    cmds = [("M", *T(*pts[0]))] + [("L", *T(*p)) for p in pts[1:]]
    if close:
        cmds.append(("Z",))
    _path(fig, ink, cmds, stroke=stroke, fill=fill, sw=sw)


def two_pin(fig, pid: str, kind: str, x: float, y: float, vertical: bool, value: str = "", note: str = "",
            flip: bool = False) -> Placed:
    """A two-pin part from (x, y) down or to the right, pin 1 first (pin 2 first with ``flip``). Returns its body,
    pins and label boxes."""
    T = _frame(x, y, vertical, flip)
    ink: list[Box] = []
    L = LEN
    a, b = 13.0, L - 13.0  # body from a to b along the part
    half = 5.0  # half width of the body (across)
    if kind == "resistor":
        _poly(fig, T, ink, [(0, 0), (a, 0)])
        _poly(fig, T, ink, [(b, 0), (L, 0)])
        _poly(fig, T, ink, [(a, -half), (b, -half), (b, half), (a, half)], close=True, fill="card")
    elif kind == "fuse":
        _poly(fig, T, ink, [(0, 0), (L, 0)])
        _poly(fig, T, ink, [(a, -half), (b, -half), (b, half), (a, half)], close=True)
    elif kind in ("capacitor", "polarized-capacitor"):
        c0, c1 = L / 2 - 3.5, L / 2 + 3.5
        w = 10.0
        _poly(fig, T, ink, [(0, 0), (c0, 0)])
        _poly(fig, T, ink, [(c1, 0), (L, 0)])
        _poly(fig, T, ink, [(c0, -w), (c0, w)], sw=2.4)
        if kind == "polarized-capacitor":
            # Curved negative plate and a + by pin 1.
            p0, p1, p2 = T(c1 + 2.5, -w), T(c1, 0), T(c1 + 2.5, w)
            _path(fig, ink, [("M", *p0), ("A", 14, *p1, 0 if vertical else 1),
                             ("A", 14, *p2, 0 if vertical else 1)], stroke=PART, sw=2.4)
            px, py = T(c0 - 6, -9)
            _path(fig, ink, [("M", px - 3, py), ("L", px + 3, py), ("M", px, py - 3), ("L", px, py + 3)],
                  stroke=PART, sw=1.2)
        else:
            _poly(fig, T, ink, [(c1, -w), (c1, w)], sw=2.4)
        half = w
        a, b = c0 - 1, c1 + 1
    elif kind in ("inductor", "solenoid"):
        n, r = 4, 4.0
        a, b = L / 2 - n * r, L / 2 + n * r
        _poly(fig, T, ink, [(0, 0), (a, 0)])
        _poly(fig, T, ink, [(b, 0), (L, 0)])
        cmds = [("M", *T(a, 0))]
        for k in range(n):
            cmds.append(("A", r, *T(a + (k + 1) * 2 * r, 0), 1 if vertical else 0))
        _path(fig, ink, cmds, stroke=PART, sw=SW)
        half = r + 1
        if kind == "solenoid":
            # The plunger: a bar alongside the winding.
            _poly(fig, T, ink, [(a, 8.5), (b, 8.5)], sw=2.2)
            half = 10
    elif kind in ("diode", "led", "zener"):
        t0, t1, w = L / 2 - 6, L / 2 + 6, 7.0
        _poly(fig, T, ink, [(0, 0), (t0, 0)])
        _poly(fig, T, ink, [(t1, 0), (L, 0)])
        _poly(fig, T, ink, [(t0, -w), (t1, 0), (t0, w)], close=True, fill="card" if kind != "led" else None)
        if kind == "zener":
            _poly(fig, T, ink, [(t1 - 3, -w - 1), (t1, -w), (t1, w), (t1 + 3, w + 1)])
        else:
            _poly(fig, T, ink, [(t1, -w), (t1, w)])
        a, b, half = t0, t1, w
        if kind == "led":
            for off in (-2.0, 4.0):
                p0 = T(L / 2 + off - 1, w + 2)
                p1 = T(L / 2 + off + 4, w + 8)
                _path(fig, ink, [("M", *p0), ("L", *p1)], stroke=PART, sw=1.2)
                # Arrow head at p1, along (p1 - p0).
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                ln = (dx * dx + dy * dy) ** 0.5
                ux, uy = dx / ln, dy / ln
                hx, hy = p1[0] - ux * 4, p1[1] - uy * 4
                _path(fig, ink, [("M", *p1), ("L", hx - uy * 2.2, hy + ux * 2.2),
                                 ("L", hx + uy * 2.2, hy - ux * 2.2), ("Z",)], stroke=PART, fill=PART, sw=0.8)
            half = w + 9
    elif kind == "crystal":
        _poly(fig, T, ink, [(0, 0), (L / 2 - 8, 0)])
        _poly(fig, T, ink, [(L / 2 + 8, 0), (L, 0)])
        _poly(fig, T, ink, [(L / 2 - 8, -8), (L / 2 - 8, 8)], sw=2.0)
        _poly(fig, T, ink, [(L / 2 + 8, -8), (L / 2 + 8, 8)], sw=2.0)
        _poly(fig, T, ink, [(L / 2 - 4.5, -6), (L / 2 + 4.5, -6), (L / 2 + 4.5, 6), (L / 2 - 4.5, 6)], close=True,
              fill="card")
        a, b, half = L / 2 - 9, L / 2 + 9, 8
    else:
        raise ValueError(f"no symbol for {kind!r}")
    (bx0, by0), (bx1, by1) = T(a, -half), T(b, half)
    body = Box(min(bx0, bx1), min(by0, by1), abs(bx1 - bx0), abs(by1 - by0))
    p = Placed(pid, body, ink=ink + [body])
    if vertical:
        p.pins = {"1": (x, y, "D"), "2": (x, y + L, "U")}
    else:
        p.pins = {"1": (x, y, "R"), "2": (x + L, y, "L")}
    if flip:
        p.pins = {"1": p.pins["2"], "2": p.pins["1"]}
    # Designator and value: right of a vertical part, above a horizontal one.
    lines = [pid] + ([f"{value} {note}".strip()] if value or note else [])
    if vertical:
        lx = body.r + 5
        ly = y + L / 2 - (len(lines) - 1) * LABEL * 0.6 + LABEL * 0.35
        for k, s in enumerate(lines):
            p.labels.append(fig.text(lx, ly + k * LABEL * 1.2, s, size=LABEL, weight=700 if k == 0 else 400,
                                     color="ink" if k == 0 else "muted"))
    else:
        s = f"{pid}  {value}".strip() if value else pid
        if note:
            s += f"  {note}"
        p.labels.append(fig.text(x + L / 2, body.y - 5, s, size=LABEL, weight=600, color="ink2", anchor="middle"))
    return p


def ground(fig, x: float, y: float, sid: str = "gnd") -> Placed:
    """Ground: its pin at (x, y), the bars below."""
    ink: list[Box] = []
    _path(fig, ink, [("M", x, y), ("L", x, y + 8)], stroke=PART)
    for k, w in enumerate((8.0, 5.0, 2.0)):
        yy = y + 8 + k * 3.5
        _path(fig, ink, [("M", x - w, yy), ("L", x + w, yy)], stroke=PART)
    return Placed(sid, Box(x - 9, y + 1, 18, 17), {"1": (x, y, "D")}, ink=ink)


def supply(fig, x: float, y: float, label: str, sid: str = "vcc", tone: str = "rose") -> Placed:
    """A supply rail: its pin at (x, y), a bar above with the net name."""
    ink: list[Box] = []
    _path(fig, ink, [("M", x, y), ("L", x, y - 11)], stroke=PART)
    _path(fig, ink, [("M", x - 9, y - 11), ("L", x + 9, y - 11)], stroke=f"{tone}.strong", sw=2.4)
    lb = fig.text(x, y - 17, label, size=LABEL, weight=700, color=f"{tone}.text", anchor="middle")
    return Placed(sid, Box(x - 10, y - 13, 20, 12), {"1": (x, y, "U")}, [lb], ink)


def no_connect(fig, x: float, y: float) -> Box:
    """The cross on a pin left open; returns the box it paints."""
    ink: list[Box] = []
    for dx in (-1, 1):
        _path(fig, ink, [("M", x - 4, y - 4 * dx), ("L", x + 4, y + 4 * dx)], stroke="muted", sw=1.4)
    return ink[0]


@dataclass
class BoxPin:
    name: str  # node name in the circuit
    label: str  # text inside the box
    number: str = ""  # text by the stub (package pin numbers)
    tone: str = "slate"  # stub colour


def box_symbol(fig, sid: str, x: float, y: float, w: float, h: float, sides: dict, title: str, sub: str = "",
               fill: str = "card", stroke: str = PART, title_tone: str = "ink", positions: dict | None = None,
               mono: bool = False, title_at: str = "center") -> Placed:
    """A box with pins on its sides. ``sides`` maps L/R/U/D to ``BoxPin`` lists; ``positions`` gives each pin's
    offset along its side (from the top or the left edge); otherwise pins sit ``PIN_PITCH`` apart from 2G in."""
    fig.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=4)
    # The outline is ink (a text across it is a problem); the inside is the body's own.
    edges = [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x, y + h), (x + w, y + h)), ((x, y), (x, y + h))]
    p = Placed(sid, Box(x, y, w, h), ink=[ink_box(e, 1.8) for e in edges])
    for side, pins in sides.items():
        for k, bp in enumerate(pins):
            off = (positions or {}).get((side, bp.name), 2 * G + k * PIN_PITCH)
            if side == "L":
                px, py, ex, ey, came = x, y + off, x - STUB, y + off, "R"
            elif side == "R":
                px, py, ex, ey, came = x + w, y + off, x + w + STUB, y + off, "L"
            elif side == "U":
                px, py, ex, ey, came = x + off, y, x + off, y - STUB, "D"
            else:
                px, py, ex, ey, came = x + off, y + h, x + off, y + h + STUB, "U"
            _path(fig, p.ink, [("M", px, py), ("L", ex, ey)], stroke=f"{bp.tone}.strong", sw=2.2, cap="butt")
            p.pins[bp.name] = (ex, ey, came)
            # Name inside, number outside along the stub.
            size = PIN_NAME
            if side == "L":
                p.labels.append(fig.text(px + 6, py + size * 0.36, bp.label, size=size, mono=mono, color="ink",
                                         bg=fill))
                if bp.number:
                    p.labels.append(fig.text(px - 4, py - 4, bp.number, size=PIN_NUM, color="muted", anchor="end"))
            elif side == "R":
                p.labels.append(fig.text(px - 6, py + size * 0.36, bp.label, size=size, mono=mono, color="ink",
                                         bg=fill, anchor="end"))
                if bp.number:
                    p.labels.append(fig.text(px + 4, py - 4, bp.number, size=PIN_NUM, color="muted"))
            elif side == "U":
                p.labels.append(fig.text(px, py + 6 + size * 0.8, bp.label, size=size, mono=mono, color="ink",
                                         bg=fill, anchor="middle"))
                if bp.number:
                    p.labels.append(fig.text(px + 4, py - 6, bp.number, size=PIN_NUM, color="muted"))
            else:
                p.labels.append(fig.text(px, py - 7, bp.label, size=size, mono=mono, color="ink", bg=fill,
                                         anchor="middle"))
                if bp.number:
                    p.labels.append(fig.text(px + 4, py + 6 + PIN_NUM * 0.8, bp.number, size=PIN_NUM,
                                             color="muted"))
    if title:
        if title_at == "top":
            p.labels.append(fig.text(x + 12, y + 22, title, size=15, weight=700, color=title_tone, bg=fill))
            if sub:
                p.labels.append(fig.text(x + 12, y + 40, sub, size=LABEL, color="muted", bg=fill))
        elif title_at == "above":
            p.labels.append(fig.text(x, y - 8 - (14 if sub else 0), title, size=14, weight=700, color=title_tone))
            if sub:
                p.labels.append(fig.text(x, y - 8, sub, size=LABEL, color="muted"))
        else:
            cy = y + h / 2 - (8 if sub else 0) + 5
            p.labels.append(fig.text(x + w / 2, cy, title, size=15, weight=700, color=title_tone, bg=fill,
                                     anchor="middle"))
            if sub:
                p.labels.append(fig.text(x + w / 2, cy + 18, sub, size=LABEL, color="muted", bg=fill,
                                         anchor="middle"))
    return p


def label_width(s: str, size: float = PIN_NAME, mono: bool = False, weight: int = 400) -> float:
    return text_width(s, size, weight, mono)
