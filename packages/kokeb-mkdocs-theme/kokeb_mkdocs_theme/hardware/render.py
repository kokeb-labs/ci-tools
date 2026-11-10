"""The chip figures drawn from ``docs/hardware.yml``: the package pinout, the block diagram and one application
circuit per ``circuits`` entry. Each is a figkit ``Fig``, so it renders light and dark from one layout, passes
figkit's checks (contrast, fit, overlaps) and is drift-checked by ``kokeb-docs figures --check`` like every other
figure. On top of figkit's checks each figure checks its own geometry (``layout_problems``): no two texts overlap,
no wire runs through a part body or a text, every pin sits on the side the package puts it.

Figure ids: ``chip-pinout``, ``chip-blocks`` and ``chip-circuit-<id>``.
"""

from __future__ import annotations

import math

from ..figkit import Box, Fig, text_width
from .model import PIN_TYPES, Hardware, Pin

MONO = True
UNVERIFIED_MARK = "*"


def figure_ids(hw: Hardware) -> list[str]:
    ids = ["chip-pinout"]
    if hw.blocks:
        ids.append("chip-blocks")
    ids += [f"chip-circuit-{c.id}" for c in hw.circuits]
    return ids


def build(hw: Hardware, fid: str) -> Fig:
    if fid == "chip-pinout":
        return pinout(hw)
    if fid == "chip-blocks":
        return blocks(hw)
    if fid.startswith("chip-circuit-"):
        from .circuit import circuit

        cid = fid[len("chip-circuit-"):]
        for c in hw.circuits:
            if c.id == cid:
                return circuit(hw, c)
    raise KeyError(fid)


def _pins_label(pins: list[Pin]) -> str:
    return ", ".join(str(p.number) for p in pins)


def _hook_call(hw: Hardware, pin: Pin) -> str:
    return hw.hooks[pin.hook].call if pin.hook else ""


def unverified_note(fig: Fig, items: list[str], y: float | None = None) -> None:
    """A footnote line under the figure for facts not confirmed in the datasheet."""
    if not items:
        return
    from ..figkit import wrap

    y = (fig._maxy + 22) if y is None else y
    text = f"{UNVERIFIED_MARK} Not confirmed in the datasheet: " + "; ".join(items) + "."
    for k, line in enumerate(wrap(text, fig.body_w, 12.5)):
        fig.text(0, y + k * 18, line, size=12.5, color="muted")


def layout_problems(fig: Fig, bodies: list[tuple[Box, str]], wires: list[tuple[tuple, tuple]],
                    skip_text: set[int] | None = None) -> None:
    """Geometry checks every chip figure runs: texts that overlap, wires through bodies or texts."""
    texts = [(bb, s) for k, (bb, _fg, _bg, s, _z) in enumerate(fig._texts) if s.strip()]
    for i in range(len(texts)):
        a, sa = texts[i]
        for j in range(i + 1, len(texts)):
            b, sb = texts[j]
            if a.overlaps(b, margin=-1.0):
                fig.problem(f"text {sa!r} overlaps text {sb!r}")
    for (x0, y0), (x1, y1) in wires:
        seg = Box(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
        for box, name in bodies:
            inner = Box(box.x + 1, box.y + 1, box.w - 2, box.h - 2)
            if _seg_hits(seg, inner):
                fig.problem(f"a wire runs through {name}")
        for bb, s in texts:
            inner = Box(bb.x + 1, bb.y + 1, bb.w - 2, bb.h - 2)
            if _seg_hits(seg, inner):
                fig.problem(f"a wire crosses the text {s!r}")


def _seg_hits(seg: Box, box: Box) -> bool:
    # An axis-aligned segment (a box of zero width or height) against a box, strictly inside.
    return seg.x < box.r and seg.r > box.x and seg.y < box.b and seg.b > box.y if seg.w and seg.h else (
        box.x < seg.r and seg.x < box.r and box.y < seg.b and seg.y < box.b
        if (seg.w or seg.h) else False)


# ---------------------------------------------------------------------------------------------------- pinout

PAD_L, PAD_W = 30, 20  # pad length (out from the body) and width
PITCH = 34


def pinout(hw: Hardware) -> Fig:
    pk = hw.package
    types = [t for t in PIN_TYPES if any(p.type == t for p in hw.pins)]
    legend = [(PIN_TYPES[t][0], PIN_TYPES[t][1]) for t in types]
    by_num = {int(p.number): p for p in hw.pins if not p.is_pad}
    unverified = [f"pin {p.number} {p.name}: {p.unverified}" for p in hw.pins if p.unverified]

    def name_of(p: Pin) -> str:
        return p.name + (UNVERIFIED_MARK if p.unverified else "")

    name_size, hook_size, num_size = 14, 12, 11.5
    name_w = max(text_width(name_of(p), name_size, 700, MONO) for p in hw.pins)
    hook_w = max([text_width(_hook_call(hw, p), hook_size, 400, MONO) for p in hw.pins] + [0])
    side_w = name_w + (hook_w + 18 if hook_w else 0) + 14
    sides = pk.sides
    bodies: list[tuple[Box, str]] = []
    texts_rot = pk.layout == "quad"
    nl = max(len(sides.get("left", [])), len(sides.get("right", [])))
    nt = max(len(sides.get("top", [])), len(sides.get("bottom", [])))
    bh = max(nl * PITCH + 2 * 22, 200)
    bw = max(nt * PITCH + 2 * 22, 260) if texts_rot else 260
    if texts_rot:
        bh = bw = max(bh, bw)
    # As wide as the drawing needs (a small package shown at page width keeps its text large), at least 760.
    width = max(760, math.ceil(bw + 2 * (PAD_L + 10 + side_w) + 2 * 32 + 48))
    fig = Fig(
        "chip-pinout",
        f"{hw.chip} pinout, {pk.type}",
        alt=f"Pinout of the {hw.chip} in {pk.type}, top view: {pk.pins} pins"
        + (" and an exposed pad" if pk.exposed_pad else "")
        + ", each with its name, its electrical type as a colour and the driver hook that uses it.",
        width=width,
        kicker="Hardware",
        subtitle=f"Top view, pin 1 marked. Colour is the pin's electrical type; the mono text outside is the port "
        f"hook the driver uses for it. Datasheet: {pk.ref.short()}.",
        legend=legend,
    )
    W = fig.body_w
    bx = W / 2 - bw / 2
    top_room = (side_w + PAD_L + 10) if texts_rot else 20
    by = top_room
    body = fig.rect(bx, by, bw, bh, fill="paper", stroke="ink2", sw=2.0, rx=8)
    bodies.append((body, "the package body"))
    # Pin 1: a notch on a dual package, a chamfer dot on a quad one; always a dot by pin 1.
    if pk.layout == "dual":
        fig.path([("M", bx + bw / 2 - 16, by), ("A", 16, bx + bw / 2 + 16, by, 0)], stroke="ink2", fill="card",
                 sw=2.0)
    fig.circle(bx + 20, by + 20, 6, fill="ink2")
    cx, cy = bx + bw / 2, by + bh / 2
    fig.text(cx, cy - 10, hw.chip, size=20, weight=700, color="ink", bg="paper", anchor="middle")
    fig.text(cx, cy + 14, f"{pk.type}, top view", size=13, color="muted", bg="paper", anchor="middle")
    if pk.exposed_pad:
        ep = [p for p in hw.pins if p.is_pad][0]
        s = min(bw, bh) * 0.42
        epy = cy + 30
        if epy + s / 2 > by + bh - 16:
            s = (by + bh - 16 - epy) * 2
        fig.rect(cx - s / 2, epy, s, max(s / 2, 36), fill="card", stroke=f"{ep.tone}.strong", sw=1.4, rx=6,
                 dash="5 4")
        fig.text(cx, epy + max(s / 2, 36) / 2 + 5, f"EP: {name_of(ep)}", size=12.5, weight=700,
                 color=f"{ep.tone}.text", bg="card", anchor="middle")

    def pad(p: Pin, side: str, k: int, count: int) -> None:
        if side in ("left", "right"):
            span = bh
            off = (span - count * PITCH) / 2 + PITCH * (k + 0.5)
            yy = by + off
            if side == "left":
                box = fig.rect(bx - PAD_L, yy - PAD_W / 2, PAD_L, PAD_W, fill=f"{p.tone}.tint",
                               stroke=f"{p.tone}.strong", sw=1.4, rx=3)
                fig.text(bx - PAD_L / 2, yy + num_size * 0.36, str(p.number), size=num_size, weight=700,
                         color=f"{p.tone}.text", bg=f"{p.tone}.tint", anchor="middle")
                nx = bx - PAD_L - 10
                fig.text(nx, yy + name_size * 0.36, name_of(p), size=name_size, weight=700, mono=MONO,
                         anchor="end")
                if p.hook:
                    fig.text(nx - name_w - 18, yy + hook_size * 0.36, _hook_call(hw, p), size=hook_size, mono=MONO,
                             color="muted", anchor="end")
            else:
                box = fig.rect(bx + bw, yy - PAD_W / 2, PAD_L, PAD_W, fill=f"{p.tone}.tint",
                               stroke=f"{p.tone}.strong", sw=1.4, rx=3)
                fig.text(bx + bw + PAD_L / 2, yy + num_size * 0.36, str(p.number), size=num_size, weight=700,
                         color=f"{p.tone}.text", bg=f"{p.tone}.tint", anchor="middle")
                nx = bx + bw + PAD_L + 10
                fig.text(nx, yy + name_size * 0.36, name_of(p), size=name_size, weight=700, mono=MONO)
                if p.hook:
                    fig.text(nx + name_w + 18, yy + hook_size * 0.36, _hook_call(hw, p), size=hook_size, mono=MONO,
                             color="muted")
        else:
            off = (bw - count * PITCH) / 2 + PITCH * (k + 0.5)
            xx = bx + off
            if side == "bottom":
                box = fig.rect(xx - PAD_W / 2, by + bh, PAD_W, PAD_L, fill=f"{p.tone}.tint",
                               stroke=f"{p.tone}.strong", sw=1.4, rx=3)
                fig.text(xx + num_size * 0.36, by + bh + PAD_L / 2, str(p.number), size=num_size, weight=700,
                         color=f"{p.tone}.text", bg=f"{p.tone}.tint", anchor="middle", rotate=-90)
                ny = by + bh + PAD_L + 10
                fig.text(xx + name_size * 0.36, ny, name_of(p), size=name_size, weight=700, mono=MONO,
                         anchor="end", rotate=-90)
                if p.hook:
                    fig.text(xx + hook_size * 0.36, ny + name_w + 18, _hook_call(hw, p), size=hook_size, mono=MONO,
                             color="muted", anchor="end", rotate=-90)
            else:
                box = fig.rect(xx - PAD_W / 2, by - PAD_L, PAD_W, PAD_L, fill=f"{p.tone}.tint",
                               stroke=f"{p.tone}.strong", sw=1.4, rx=3)
                fig.text(xx + num_size * 0.36, by - PAD_L / 2, str(p.number), size=num_size, weight=700,
                         color=f"{p.tone}.text", bg=f"{p.tone}.tint", anchor="middle", rotate=-90)
                ny = by - PAD_L - 10
                fig.text(xx + name_size * 0.36, ny, name_of(p), size=name_size, weight=700, mono=MONO,
                         rotate=-90)
                if p.hook:
                    fig.text(xx + hook_size * 0.36, ny - name_w - 18, _hook_call(hw, p), size=hook_size, mono=MONO,
                             color="muted", rotate=-90)
        placed[int(p.number)] = (side, box)

    placed: dict[int, tuple[str, Box]] = {}
    for side in ("left", "bottom", "right", "top"):
        nums = sides.get(side, [])
        order = nums if side in ("left", "bottom") else list(reversed(nums))
        # Left: top to bottom; bottom: left to right; right: bottom to top; top: right to left (counter-clockwise).
        for k, n in enumerate(order):
            pad(by_num[n], side, k, len(nums))
    if texts_rot:
        fig._grow(by + bh + PAD_L + side_w + 10)
    unverified_note(fig, unverified)
    fig.doc = (f"Reads: The {hw.chip} seen from the top, in its {pk.type} package. Pin 1 is marked by the dot; "
               "the numbers run counter-clockwise from it. Each pad is coloured by the pin's electrical type (legend "
               "below). Next to it is the pin's name and, in mono, the hook of the driver's port that drives or "
               "reads it; a pin without a hook is not used by the driver."
               + (" The dashed square is the exposed pad." if pk.exposed_pad else ""))
    _check_pinout(fig, hw, placed, body)
    layout_problems(fig, bodies, [])
    fig.placed = placed  # for the tests
    return fig


def _check_pinout(fig: Fig, hw: Hardware, placed: dict, body: Box) -> None:
    for side, nums in hw.package.sides.items():
        for n in nums:
            got, box = placed.get(n, (None, None))
            if got != side:
                fig.problem(f"pin {n} is drawn on the {got} side, the package has it on the {side}")
                continue
            ok = {
                "left": box.r <= body.x + 0.5,
                "right": box.x >= body.r - 0.5,
                "top": box.b <= body.y + 0.5,
                "bottom": box.y >= body.b - 0.5,
            }[side]
            if not ok:
                fig.problem(f"pin {n} is not outside the {side} edge of the body")


# ---------------------------------------------------------------------------------------------------- blocks


def blocks(hw: Hardware) -> Fig:
    from .router import RouteError
    from .symbols import G

    fig = Fig(
        "chip-blocks",
        f"Inside the {hw.chip}",
        alt=f"Block diagram of the {hw.chip}: its function blocks, how they connect and which package pins reach "
        "each block.",
        width=1200,
        kicker="Hardware",
        subtitle="Function blocks and their links, from the datasheet's block diagram"
        + (f" ({hw.blocks_ref.short()})" if hw.blocks_ref else "")
        + ". Pins on the edge carry their package number.",
        legend=[(PIN_TYPES[t][0], PIN_TYPES[t][1]) for t in PIN_TYPES
                if any(p.type == t for b in hw.blocks for n in b.pins for p in hw.pin(n))]
        + [("~solid", "signal or data between blocks")],
    )
    W = fig.body_w
    cols = max(b.at[0] for b in hw.blocks) + 1
    rows = max(b.at[1] for b in hw.blocks) + 1
    # Pins: which side of the chip each block's pins leave by.
    side_of = {}
    for b in hw.blocks:
        side_of[b.id] = b.side or ("left" if (b.at[0] + 0.5) <= cols / 2 else "right")

    def pin_text(name: str) -> str:
        ps = hw.pin(name)
        mark = UNVERIFIED_MARK if any(p.unverified for p in ps) else ""
        return f"{name}{mark}  {_pins_label(ps)}"

    lsz = 12.5
    left_w = max([text_width(pin_text(n), lsz, 600, MONO) for b in hw.blocks if side_of[b.id] == "left"
                  for n in b.pins] + [0])
    right_w = max([text_width(pin_text(n), lsz, 600, MONO) for b in hw.blocks if side_of[b.id] == "right"
                   for n in b.pins] + [0])
    lm = math.ceil((left_w + 26) / G) * G
    rm = math.ceil((right_w + 26) / G) * G
    rx0, rx1 = lm, math.floor((W - rm) / G) * G
    # Columns far enough apart for the label of a link between them.
    lab = max([text_width(ln.label, fig.k["edge_label"], 500) for ln in hw.links] + [0])
    gap_x = max(7 * G, math.ceil((lab + 12 + 5 * G) / G) * G)
    gap_y = max(6 * G, 6 * G)
    inner_x0, inner_x1 = rx0 + 5 * G, rx1 - 5 * G
    col_w = math.floor(((inner_x1 - inner_x0) - (cols - 1) * gap_x) / cols / G) * G
    # Card heights: measured on a scratch figure, then one height per row, tall enough for the block's pins.
    scratch = Fig("scratch", "s", alt="s", width=1200)
    row_h = [6 * G] * rows
    for b in hw.blocks:
        lines = [b.detail] if b.detail else []
        h = scratch.card(0, 0, col_w, b.label + (UNVERIFIED_MARK if b.unverified else ""), lines, tone=b.tone).h
        h = max(h, len(b.pins) * 3 * G + G)
        row_h[b.at[1]] = max(row_h[b.at[1]], math.ceil(h / G) * G)
    hts = {b.id: row_h[b.at[1]] for b in hw.blocks}
    top = fig.region_inner_top(0) + 2 * G
    top = math.ceil(top / G) * G
    row_y = []
    y = top
    for h in row_h:
        row_y.append(y)
        y += h + gap_y
    rb = y - gap_y + 4 * G
    fig.region(rx0, 0, rx1 - rx0, rb, hw.chip + (UNVERIFIED_MARK if hw.blocks_unverified else ""), tone="slate",
               sub=hw.package.type)
    boxes: dict[str, Box] = {}
    for b in hw.blocks:
        x = inner_x0 + b.at[0] * (col_w + gap_x)
        yb = row_y[b.at[1]] + (row_h[b.at[1]] - hts[b.id]) / 2
        yb = math.floor(yb / G) * G
        lines = [b.detail] if b.detail else []
        boxes[b.id] = fig.card(x, yb, col_w, b.label + (UNVERIFIED_MARK if b.unverified else ""), lines,
                               tone=b.tone, h=hts[b.id], accent=True)
    # Routing grid over the whole body.
    from .router import Grid

    grid = Grid(0, 0, int(W // G) + 1, int((rb + 4 * G) // G) + 1, G)
    for bx in boxes.values():
        grid.block_box(bx.x, bx.y, bx.w, bx.h, margin=1)
    # Pin pads on the region edges, in block order, near their block's middle.
    pin_ends = []  # (block id, pin name, edge point, port side)
    for side in ("left", "right"):
        group = [b for b in sorted(hw.blocks, key=lambda b: (b.at[1], b.at[0])) if side_of[b.id] == side]
        last = top - 3 * G
        for b in group:
            n = len(b.pins)
            if not n:
                continue
            bx = boxes[b.id]
            start = math.floor((bx.cy - (n - 1) * 3 * G / 2) / G) * G
            start = max(start, last + 3 * G)
            for k, name in enumerate(b.pins):
                yy = start + k * 3 * G
                last = yy
                tone = hw.pin(name)[0].tone
                ex = rx0 if side == "left" else rx1
                fig.rect(ex - 7, yy - 7, 14, 14, fill=f"{tone}.tint", stroke=f"{tone}.strong", sw=1.4, rx=3)
                if side == "left":
                    fig.text(ex - 14, yy + lsz * 0.36, pin_text(name), size=lsz, weight=600, mono=MONO, anchor="end")
                else:
                    fig.text(ex + 14, yy + lsz * 0.36, pin_text(name), size=lsz, weight=600, mono=MONO)
                pin_ends.append((b.id, name, (ex + (7 if side == "left" else -7), yy), side, tone))
    # Ports on block sides. A pin enters level with its pad. A link leaves and enters at the same height (or the
    # same x, between stacked blocks) when the two sides overlap, so it runs straight; ports on one side stay 3G
    # apart.
    def port(bid: str, side: str, v: float):
        bx = boxes[bid]
        if side == "left":
            return ((math.floor((bx.x - 2 * G) / G) * G, v), "R", (bx.x, v))
        if side == "right":
            return ((math.ceil((bx.r + 2 * G) / G) * G, v), "L", (bx.r, v))
        if side == "top":
            return ((v, math.floor((bx.y - 2 * G) / G) * G), "D", (v, bx.y))
        return ((v, math.ceil((bx.b + 2 * G) / G) * G), "U", (v, bx.b))

    def span(bid: str, side: str) -> list[int]:
        bx = boxes[bid]
        lo, hi = (bx.y, bx.b) if side in ("left", "right") else (bx.x, bx.r)
        return list(range(math.ceil((lo + G) / G) * G, math.floor((hi - G) / G) * G + 1, G))

    used_at: dict[tuple[str, str], list[float]] = {}
    where: dict = {}
    for k, (bid, name, pt, side, tone) in enumerate(pin_ends):
        sp = span(bid, side)
        v = min(max(pt[1], sp[0]), sp[-1])
        where[("pin", k, 1)] = port(bid, side, v)
        used_at.setdefault((bid, side), []).append(v)

    def free(bid: str, side: str, v: float) -> bool:
        return all(abs(v - u) >= 3 * G for u in used_at.get((bid, side), []))

    def centre(bid: str, side: str) -> float:
        bx = boxes[bid]
        return bx.cy if side in ("left", "right") else bx.cx

    for i, ln in enumerate(hw.links):
        a, b = boxes[ln.src], boxes[ln.dst]
        dx, dy = b.cx - a.cx, b.cy - a.cy
        if abs(dx) >= abs(dy) and not (a.x < b.cx < a.r):
            sa, sb = ("right", "left") if dx > 0 else ("left", "right")
        else:
            sa, sb = ("bottom", "top") if dy > 0 else ("top", "bottom")
        both = [v for v in span(ln.src, sa) if v in set(span(ln.dst, sb)) and free(ln.src, sa, v)
                and free(ln.dst, sb, v)]
        mid = (centre(ln.src, sa) + centre(ln.dst, sb)) / 2
        if both:
            va = vb = min(both, key=lambda v: (abs(v - mid), v))
        else:
            ca = [v for v in span(ln.src, sa) if free(ln.src, sa, v)] or span(ln.src, sa)
            cb = [v for v in span(ln.dst, sb) if free(ln.dst, sb, v)] or span(ln.dst, sb)
            va = min(ca, key=lambda v: (abs(v - centre(ln.src, sa)), v))
            vb = min(cb, key=lambda v: (abs(v - centre(ln.dst, sb)), v))
        where[("link", i, 0)] = port(ln.src, sa, va)
        where[("link", i, 1)] = port(ln.dst, sb, vb)
        used_at.setdefault((ln.src, sa), []).append(va)
        used_at.setdefault((ln.dst, sb), []).append(vb)
    wires = []
    # Every port is a terminal before anything is routed, so no wire runs through a port drawn later.
    pin_cells, link_cells = [], []
    for k, (bid, name, pt, side, tone) in enumerate(pin_ends):
        (px, py), pside, edge = where[("pin", k, 1)]
        s = grid.cell(pt[0] + (G - 7 if side == "left" else 7 - G), pt[1])
        e = grid.cell(px, py)
        grid.add_terminal(f"pin:{k}", s, "L" if side == "left" else "R")
        grid.add_terminal(f"pin:{k}", e, pside)
        pin_cells.append((s, e))
    for i, ln in enumerate(hw.links):
        (p0, s0, e0), (p1, s1, e1) = where[("link", i, 0)], where[("link", i, 1)]
        a, b = grid.cell(*p0), grid.cell(*p1)
        grid.add_terminal(f"link:{i}", a, s0)
        grid.add_terminal(f"link:{i}", b, s1)
        link_cells.append((a, b))
    # Pins first: short and fixed.
    for k, (bid, name, pt, side, tone) in enumerate(pin_ends):
        (px, py), pside, edge = where[("pin", k, 1)]
        s, e = pin_cells[k]
        try:
            grid.route(f"pin:{k}", [e, s])
        except RouteError as ex:
            fig.problem(str(ex))
            continue
        pts = _dedupe([pt] + _corners(grid, f"pin:{k}", s, e) + [edge])
        fig.line(pts, color=f"{tone}.strong", sw=1.8, layer="edge")
        fig.circle(edge[0], edge[1], 3, fill=f"{tone}.strong", layer="label")
        wires += list(zip(pts, pts[1:]))
    paths = []
    for i, ln in enumerate(hw.links):
        (p0, s0, e0), (p1, s1, e1) = where[("link", i, 0)], where[("link", i, 1)]
        a, b = link_cells[i]
        try:
            grid.route(f"link:{i}", [b, a])
        except RouteError as ex:
            fig.problem(str(ex))
            continue
        # Pull the arrow ends 4 px off the cards, as figkit's connect() does.
        paths.append((ln, _inset(_dedupe([e0] + _corners(grid, f"link:{i}", a, b) + [e1]), 4)))
    taken = list(boxes.values())
    for ln, pts in paths:
        fig.edge(pts, tone="rail", arrow="both" if ln.both else "end")
        if ln.label:
            text = ln.label + (UNVERIFIED_MARK if ln.unverified else "")
            box = _label_spot(fig, pts, text, taken)
            taken.append(box)
    fig._grow(rb)
    unverified_note(fig, ([f"the diagram: {hw.blocks_unverified}"] if hw.blocks_unverified else [])
                    + [f"{b.label}: {b.unverified}" for b in hw.blocks if b.unverified]
                    + [f"link {ln.src} to {ln.dst}: {ln.unverified}" for ln in hw.links if ln.unverified]
                    + [f"pin {p.name}: {p.unverified}" for p in hw.pins if p.unverified
                       and any(p.name in b.pins for b in hw.blocks)])
    layout_problems(fig, [(bx, f"block {bid!r}") for bid, bx in boxes.items()], wires)
    fig.doc = (f"Reads: The {hw.chip}'s function blocks inside its outline. Arrows between blocks carry signals or "
               "data in the direction they point (both ways where they have two heads). The package pins stand on "
               "the left and right edges with their numbers, each wired to the block it reaches.")
    return fig


def _label_spot(fig: Fig, pts, text: str, taken: list[Box]) -> Box:
    """Put an edge label on the middle of a segment of its edge, longest segment first, where it covers no card and
    no other label; the middle of the longest segment when no place is free (figkit then reports it)."""
    size = fig.k["edge_label"]
    w, h = text_width(text, size, 500) + 12, size + 8
    segs = sorted(zip(pts, pts[1:]), key=lambda s: -(abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1])))
    for frac in (0.5, 0.3, 0.7):
        for (x0, y0), (x1, y1) in segs:
            cx, cy = x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac
            box = Box(cx - w / 2 - 4, cy - h / 2 - 4, w + 8, h + 8)
            if not any(box.overlaps(t) for t in taken):
                return fig.edge_label(cx, cy, text)
    (x0, y0), (x1, y1) = segs[0]
    return fig.edge_label((x0 + x1) / 2, (y0 + y1) / 2, text)


def _corners(grid, net: str, a, b) -> list[tuple[float, float]]:
    """The corner points of the single wire of ``net`` from cell ``a`` to cell ``b``."""
    from .router import DIRS

    path = [a]
    seen = {a}
    c = a
    while c != b:
        nxt = None
        for d in sorted(grid.arms.get(c, {}).get(net, set())):
            n = (c[0] + DIRS[d][0], c[1] + DIRS[d][1])
            if n not in seen:
                nxt = n
                break
        if nxt is None:
            break
        path.append(nxt)
        seen.add(nxt)
        c = nxt
    pts = [grid.xy(path[0])]
    for k in range(1, len(path) - 1):
        p, q, r = path[k - 1], path[k], path[k + 1]
        if (q[0] - p[0], q[1] - p[1]) != (r[0] - q[0], r[1] - q[1]):
            pts.append(grid.xy(q))
    pts.append(grid.xy(path[-1]))
    return pts


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or (abs(out[-1][0] - p[0]) > 0.01 or abs(out[-1][1] - p[1]) > 0.01):
            out.append(p)
    # Drop middle points that lie on a straight run.
    k = 1
    while k < len(out) - 1:
        (x0, y0), (x1, y1), (x2, y2) = out[k - 1], out[k], out[k + 1]
        if (abs(x0 - x1) < 0.01 and abs(x1 - x2) < 0.01) or (abs(y0 - y1) < 0.01 and abs(y1 - y2) < 0.01):
            out.pop(k)
        else:
            k += 1
    return out


def _inset(pts, d: float):
    def move(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(dx, dy) or 1
        return (p[0] + dx / ln * d, p[1] + dy / ln * d)

    if len(pts) < 2:
        return pts
    pts = list(pts)
    pts[0] = move(pts[0], pts[1])
    pts[-1] = move(pts[-1], pts[-2])
    return pts
