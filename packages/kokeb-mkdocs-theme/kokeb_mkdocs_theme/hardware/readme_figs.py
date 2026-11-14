"""The chip-first README figures, drawn from the ``overview``, ``capabilities``, ``frames`` and ``circuits`` of
``docs/hardware.yml``. All use figkit's ``overview`` profile: they are read at README width (about 830 px), so no
text is under 11 px there, and each passes figkit's contrast, fit and overlap checks plus the chip figures' own
geometry checks (``common.layout_problems``).

* ``chip-hero``         the chip in its system: the host and its bus, the chip, what it drives and what it reads
                        back, and the headline numbers as tiles, each with its datasheet section;
* ``chip-capabilities`` what the chip does, one card per capability: an icon, a line, the driver's status and the
                        registers behind it (the function-to-register map);
* ``chip-frame-<id>``   one bus transfer bit by bit: the fields of each frame row, the bit numbers at the field
                        edges, an optional decode of one field and an optional SPI waveform in the same bit grid;
* ``chip-wiring-<id>``  a circuit reduced to what a reader wires by hand: every MCU signal to its chip pin with the
                        hook that drives it, the external blocks, then the supplies, the support parts and the unused
                        pins in words. The full schematic stays ``chip-circuit-<id>``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..figkit import Box, Fig, text_width, wrap
from ..figkit import theme as T
from . import icons
from .chipdoc import STATUSES, meaning
from .common import UNVERIFIED_MARK, layout_problems, unverified_note
from .model import PIN_TYPES, Hardware

W_FIG = 1200
STUB = 12  # length of the hero chip's pin stubs


def _short(r) -> str:
    """A citation short enough for a tile: ``28.1, p. 120``."""
    sec = r.section.split(" ")[0] if r.section[:1].isdigit() else r.section
    return f"{sec}, p. {r.page}"


def _graphic_contrast(fig: Fig, tone: str, what: str) -> None:
    """An icon or a pin stub is a graphic object: 3:1 against its fill in both themes (WCAG 1.4.11)."""
    for th in T.THEMES:
        c = T.contrast(T.resolve(f"{tone}.strong", th), T.resolve(f"{tone}.tint", th))
        if c < 3.0:
            fig.problem(f"{th}: {what} in tone {tone!r} is {c:.2f}:1 on its disc, needs 3:1")


def _text_on_bodies(fig: Fig, bodies: list[tuple[Box, str]]) -> None:
    """A text drawn on the canvas must not run onto a card or a box drawn under it (its contrast was checked
    against the canvas, and it reads as part of that box)."""
    for bb, _fg, bg, s, _z in fig._texts:
        if bg != "canvas" or not s.strip():
            continue
        for box, name in bodies:
            if bb.overlaps(box, margin=-1.0):
                fig.problem(f"text {s!r} runs onto {name}")


# ---------------------------------------------------------------------------------------------------- hero


def hero(hw: Hardware) -> Fig:
    ov = hw.doc.overview
    sy = ov.system
    pk = hw.package
    specs_alt = "; ".join(f"{s.value} {s.label}" for s in ov.specs)
    alt = f"Overview of the {hw.chip}, {ov.summary}."
    if sy:
        alt += f" A {sy.host} talks to it over {sy.bus}"
        if sy.drives:
            alt += "; it drives " + ", then ".join(d.label for d in sy.drives)
        if sy.senses:
            alt += "; it reads back " + ", ".join(s.label for s in sy.senses)
        alt += "."
    if specs_alt:
        alt += f" Headline figures: {specs_alt}."
    fig = Fig("chip-hero", hw.chip, alt=alt, width=W_FIG, profile="overview", kicker=ov.category,
              subtitle=("What talks to it, what it drives and what it reads back, " if sy else "")
              + f"with its headline numbers. Datasheet: {_short(ov.ref)}.")
    k = fig.k
    W = fig.body_w
    bodies: list[tuple[Box, str]] = []
    unverified = []
    CW, CH = 230, 210
    y0 = 8
    host_w = 210
    if sy:
        lw = text_width(sy.bus, k["edge_label"], 500) + 12
        g1 = max(120, math.ceil(lw + 56))
        cx0 = host_w + g1
    else:
        cx0 = W / 2 - CW / 2
    chip = _chip_body(fig, hw, cx0, y0, CW, CH)
    bodies.append((chip, "the chip"))
    ccy = chip.cy
    bottom = chip.b
    if sy:
        host_lines = ["your firmware and this driver"]
        hh = _measure_card(fig, host_w, sy.host, host_lines)
        host = fig.card(0, ccy - hh / 2, host_w, sy.host, host_lines, tone="blue", accent=True)
        fig.edge([(host.r + 4, ccy), (chip.x - STUB - 4, ccy)], tone="blue", label=sy.bus, arrow="both")
        bottom = max(bottom, host.b)
        if sy.drives:
            n = len(sy.drives)
            g2 = 60
            dw = min(260, math.floor((W - chip.r - STUB - n * g2) / n))
            x = chip.r + STUB + g2
            prev = chip
            for d in sy.drives:
                title = d.label + (UNVERIFIED_MARK if d.unverified else "")
                if d.unverified:
                    unverified.append(f"{d.label}: {d.unverified}")
                lines = [d.detail] if d.detail else []
                m = _measure_card(fig, dw, title, lines)
                box = fig.card(x, ccy - m / 2, dw, title, lines, tone="teal", accent=True)
                fig.edge([(prev.r + (STUB if prev is chip else 0) + 4, ccy), (box.x - 4, ccy)], tone="teal")
                bottom = max(bottom, box.b)
                prev = box
                x += dw + g2
        if sy.senses:
            sw_ = min(W, max(CW + 120, 360))
            lines = [s.label + (f" ({s.detail})" if s.detail else "") + (UNVERIFIED_MARK if s.unverified else "")
                     for s in sy.senses]
            unverified += [f"{s.label}: {s.unverified}" for s in sy.senses if s.unverified]
            sx = min(max(chip.cx - sw_ / 2, 0), W - sw_)
            box = fig.card(sx, bottom + 64, sw_, "Reads back", lines, tone="amber", accent=True)
            stub_b = STUB if hw.package.layout == "quad" else 0
            fig.edge([(chip.cx, box.y - 4), (chip.cx, chip.b + stub_b + 4)], tone="amber")
            bottom = box.b
    if ov.specs:
        n = len(ov.specs)
        gap = 16
        tw = (W - (n - 1) * gap) / n
        ty = bottom + 40
        # Tile height from the longest label.
        lab_lines = [wrap(s.label, tw - 32, k["card_body"]) for s in ov.specs]
        # The citation under each tile: a long section name wraps to a second line, then is ellipsised.
        cite_lines = [_lines(_short(s.ref), tw - 32, k["small"]) for s in ov.specs]
        nc = max(len(c) for c in cite_lines)
        th = (24 + 30 + 10 + max(len(ls) for ls in lab_lines) * k["card_body"] * 1.35 + 8 + k["small"]
              + (nc - 1) * k["small"] * 1.35 + 20)
        for i, s in enumerate(ov.specs):
            x = i * (tw + gap)
            fig.rect(x, ty, tw, th, fill="paper", stroke="line")
            val = s.value + (UNVERIFIED_MARK if s.unverified else "")
            if s.unverified:
                unverified.append(f"{s.value} {s.label}: {s.unverified}")
            size = 30
            while text_width(val, size, 700) > tw - 32 and size > 20:
                size -= 1
            if text_width(val, size, 700) > tw - 32:
                fig.problem(f"spec value {val!r} is wider than its tile")
            fig.text(x + 16, ty + 24 + size * 0.8, val, size=size, weight=700, color="ink", bg="paper")
            yy = ty + 24 + 30 + 10 + k["card_body"] * 0.8
            for ln in lab_lines[i]:
                fig.text(x + 16, yy, ln, size=k["card_body"], color="ink2", bg="paper")
                yy += k["card_body"] * 1.35
            for j, ln in enumerate(cite_lines[i]):
                fig.text(x + 16, ty + th - 18 - (len(cite_lines[i]) - 1 - j) * k["small"] * 1.35, ln, size=k["small"],
                         color="muted", bg="paper")
        bottom = ty + th
    fig._grow(bottom)
    unverified_note(fig, unverified)
    layout_problems(fig, bodies, [])
    fig.doc = (f"Reads: The {hw.chip} in the middle, drawn as its {pk.type} package. "
               + (f"On the left the {sy.host} that runs the driver, joined to it by {sy.bus}. " if sy else "")
               + ("To the right, what the chip drives, in the order the power flows. " if sy and sy.drives else "")
               + ("Below it, what the chip reads back. " if sy and sy.senses else "")
               + ("The tiles at the bottom are the headline numbers, each with the datasheet section and page it "
                  "comes from." if ov.specs else ""))
    return fig


def _measure_card(fig: Fig, w: float, title: str, lines: list[str]) -> float:
    scratch = Fig("scratch", "s", alt="s", width=W_FIG, profile=fig.profile)
    return scratch.card(0, 0, w, title, lines).h


def _chip_body(fig: Fig, hw: Hardware, x: float, y: float, w: float, h: float) -> Box:
    """The chip as a stylised package: pin stubs on the sides the package has, pin 1 dot, name and package."""
    pk = hw.package
    k = fig.k
    sides = ("left", "right") if pk.layout == "dual" else ("left", "right", "top", "bottom")
    per = {s: len(pk.sides.get(s, [])) for s in sides}
    stub, thick = STUB, 7
    for s in sides:
        n = min(per[s], 9)
        if not n:
            continue
        span = (h if s in ("left", "right") else w) - 40
        for i in range(n):
            t = 20 + (span * (i + 0.5) / n)
            if s == "left":
                fig.rect(x - stub, y + t - thick / 2, stub, thick, fill="slate.tint", stroke="slate.strong", sw=1.2,
                         rx=2)
            elif s == "right":
                fig.rect(x + w, y + t - thick / 2, stub, thick, fill="slate.tint", stroke="slate.strong", sw=1.2,
                         rx=2)
            elif s == "top":
                fig.rect(x + t - thick / 2, y - stub, thick, stub, fill="slate.tint", stroke="slate.strong", sw=1.2,
                         rx=2)
            else:
                fig.rect(x + t - thick / 2, y + h, thick, stub, fill="slate.tint", stroke="slate.strong", sw=1.2,
                         rx=2)
    body = fig.rect(x, y, w, h, fill="paper", stroke="ink2", sw=2.2, rx=10)
    fig.circle(x + 20, y + 20, 6, fill="ink2")
    size = 30
    while text_width(hw.chip, size, 700) > w - 30 and size > 22:
        size -= 1
    names = [hw.chip]
    if text_width(hw.chip, size, 700) > w - 30:
        # A long name wraps to two lines, a long package string too; what is still left over is ellipsised.
        size = 24
        names = _lines(hw.chip, w - 30, size, 700)
    pkg = _lines(pk.type, w - 30, k["card_body"])
    lh, ph = size * 1.15, k["card_body"] * 1.3
    cy = y + h / 2
    for t, ln in enumerate(names):  # the last name line sits where a one-line name does
        fig.text(x + w / 2, cy - 6 - (len(names) - 1 - t) * lh, ln, size=size, weight=700, color="ink", bg="paper",
                 anchor="middle")
    for t, ln in enumerate(pkg):
        fig.text(x + w / 2, cy + 24 + t * ph, ln, size=k["card_body"], color="muted", bg="paper", anchor="middle")
    pins = f"{pk.pins} pins" + (" + pad" if pk.exposed_pad else "")
    fig.text(x + w / 2, cy + 48 + (len(pkg) - 1) * ph, pins, size=k["small"], color="muted", bg="paper",
             anchor="middle")
    return body


# ---------------------------------------------------------------------------------------------------- capabilities


def capabilities(hw: Hardware) -> Fig:
    caps = hw.doc.capabilities
    kind = hw.doc.kind
    used = [s for s in STATUSES if any(c.status == s for c in caps)]
    of = "the protocol" if kind == "protocol" else "the chip"
    fig = Fig(
        "chip-capabilities",
        f"What the {hw.chip} does",
        alt=f"Capability map of the {hw.chip}: " + "; ".join(
            f"{c.title} ({STATUSES[c.status][1].lower()}): {c.what}" for c in caps) + ".",
        width=W_FIG,
        profile="overview",
        kicker="Capabilities",
        subtitle=f"One card per function of {of}, with how this driver covers it and the "
        + ("objects behind it." if kind == "protocol" else "registers behind it."),
        legend=[(STATUSES[s][0], f"{STATUSES[s][1]}: {meaning(s, kind)}") for s in used],
    )
    k = fig.k
    W = fig.body_w
    n = len(caps)
    cols = 1 if n == 1 else (2 if n <= 4 else 3)
    gap = 20
    cw = (W - (cols - 1) * gap) / cols
    pad = k["pad"]
    disc = 56
    inner = cw - 2 * pad
    title_w = inner - disc - 14

    def regs_of(c) -> list[str]:
        # The datasheet's names; a pill wider than the card is ellipsised (the coverage table has the full name).
        regs = [str(r) for r in c.registers]
        if len(regs) > 4:
            regs = regs[:3] + [f"+{len(c.registers) - 3} more"]
        return [_fit(r, inner - 16, k["pill"], 700) for r in regs]

    def measure(c) -> float:
        scratch = Fig("scratch", "s", alt="s", width=W_FIG, profile="overview")
        t_lines = wrap(c.title + (UNVERIFIED_MARK if c.unverified else ""), title_w, k["card_title"], 700)
        head = max(disc, len(t_lines) * k["card_title"] * 1.3)
        body = len(wrap(c.what, inner, k["card_body"])) * k["card_body"] * 1.45
        pills = [STATUSES[c.status][1]] + regs_of(c)
        ph = scratch.chips(0, 0, inner, pills)
        return pad + head + 12 + body + 12 + ph + pad

    rows = [caps[i:i + cols] for i in range(0, n, cols)]
    y = 0.0
    unverified = []
    for row in rows:
        h = max(measure(c) for c in row)
        for j, c in enumerate(row):
            x = j * (cw + gap)
            box = fig.rect(x, y, cw, h, fill="card", stroke="line")
            fig._cards.append((box, c.title))
            tone = c.tone
            # The icon says what the function is (one colour for all); the pill says how the driver covers it.
            itone = "slate" if c.status == "not-covered" else "brand"
            _graphic_contrast(fig, itone, "the icon")
            icons.draw(fig, c.icon, x + pad + disc / 2, y + pad + disc / 2, disc, itone)
            title = c.title + (UNVERIFIED_MARK if c.unverified else "")
            if c.unverified:
                unverified.append(f"{c.title}: {c.unverified}")
            t_lines = wrap(title, title_w, k["card_title"], 700)
            th = len(t_lines) * k["card_title"] * 1.3
            ty = y + pad + max(0.0, (disc - th) / 2) + k["card_title"] * 0.95
            for ln in t_lines:
                if text_width(ln, k["card_title"], 700) > title_w + 0.5:
                    fig.problem(f"capability title {ln!r} is wider than its card")
                fig.text(x + pad + disc + 14, ty, ln, size=k["card_title"], weight=700, color="ink", bg="card")
                ty += k["card_title"] * 1.3
            yy = y + pad + max(disc, th) + 12 + k["card_body"] * 0.85
            for ln in wrap(c.what, inner, k["card_body"]):
                fig.text(x + pad, yy, ln, size=k["card_body"], color="ink2", bg="card")
                yy += k["card_body"] * 1.45
            py = yy - k["card_body"] * 0.85 + 12 - k["card_body"] * 0.45 + 4
            # Status first (solid: it is the answer), then the registers (outline).
            sx = x + pad
            st = fig.pill(sx, py, STATUSES[c.status][1], tone=tone, solid=True)
            rest = regs_of(c)
            if rest:
                rx = st.r + 8
                ry = py
                for r in rest:
                    pw = fig.pill_width(r)
                    if rx + pw > x + cw - pad:
                        rx, ry = x + pad, ry + k["pill"] + 10 + 8
                    fig.pill(rx, ry, r, tone="slate")
                    rx += pw + 8
        y += h + gap
    fig._grow(y - gap)
    unverified_note(fig, unverified)
    layout_problems(fig, [], [])
    fig.doc = (f"Reads: Each card is one function of the {hw.chip}: an icon, its name and what it does for the "
               "application. The filled pill says how this driver covers it (legend below); the outlined pills are "
               + ("the protocol objects behind it" if kind == "protocol" else "the chip registers behind it")
               + ". The coverage table in the README gives the driver calls and the datasheet section of each card.")
    return fig


# ---------------------------------------------------------------------------------------------------- frames


def frame(hw: Hardware, fid: str) -> Fig:
    fr = next(f for f in hw.doc.frames if f.id == fid)
    rows_alt = "; ".join(
        f"{r.label}: " + ", ".join(f"{f.name} (bit {f.hi})" if f.width == 1 else f"{f.name} (bits {f.hi} to {f.lo})"
                                   for f in r.fields) for r in fr.rows)
    alt = f"{fr.title} of the {hw.chip}, {fr.bits} bits, most significant bit first. {rows_alt}."
    if fr.decode:
        alt += f" The {fr.decode.field} field of the {fr.decode.row} row: " + ", ".join(
            f"bit {b} {n}" for b, n in fr.decode.bits) + "."
    if fr.waveform:
        alt += f" Below, the SPI mode {fr.waveform.spi_mode} waveform of one transfer in the same bit grid."
    fig = Fig(f"chip-frame-{fr.id}", f"{hw.chip}: {fr.title}", alt=alt, width=W_FIG, profile="overview",
              kicker="On the bus",
              subtitle=(fr.description + " " if fr.description else "")
              + f"{fr.bits} bits, sent most significant bit first. Datasheet: {fr.ref.short()}.")
    k = fig.k
    W = fig.body_w
    bodies: list[tuple[Box, str]] = []
    lab = k["card_title"]
    lw = max([text_width(r.label, lab, 700) for r in fr.rows]
             + [text_width(r.sub, k["small"]) for r in fr.rows if r.sub]
             + ([text_width(ln.name, k["mono"], 700, True) for ln in fr.waveform.lanes]
                + [text_width(n, k["mono"], 700, True) for n in (fr.waveform.select, fr.waveform.clock)]
                if fr.waveform else []))
    LW = max(150, math.ceil(lw + 24))
    lead = 28  # room for the select line before the first bit and after the last
    x0, x1 = LW + lead, W - lead
    bw = (x1 - x0) / fr.bits

    def bx(bit: int) -> float:
        """Left edge of bit ``bit`` (bit width - 1 is the first one sent, drawn on the left)."""
        return x0 + (fr.bits - 1 - bit) * bw

    ns = k["small"]
    fig.text(x0, ns, "MSB, sent first", size=ns, color="muted")
    fig.text(x1, ns, "LSB, sent last", size=ns, color="muted", anchor="end")
    y = ns + 18
    RH = 46
    field_boxes = {}
    for r in fr.rows:
        fig.text(0, y + RH / 2 + (lab * 0.35 if not r.sub else -2), r.label, size=lab, weight=700)
        if r.sub:
            fig.text(0, y + RH / 2 + ns + 2, r.sub, size=ns, color="muted")
        for f in r.fields:
            fx, fw = bx(f.hi), f.width * bw
            box = fig.rect(fx, y, fw, RH, fill=f"{f.tone}.tint", stroke=f"{f.tone}.strong", sw=1.4, rx=6)
            bodies.append((box, f"field {f.name}"))
            field_boxes[(r.label, f.name)] = box
            name, size = f.name, k["card_body"]
            for cand, sz in ((f.name, k["card_body"]), (f.name, k["small"]), (f.short, k["card_body"]),
                             (f.short, k["small"])):
                if cand and text_width(cand, sz, 600) <= fw - 4:
                    name, size = cand, sz
                    break
            if text_width(name, size, 600) > fw - 4:
                fig.problem(f"field {f.name!r} of row {r.label!r} does not fit its {f.width} bit(s): give it a short "
                            "name (short:)")
            fig.text(fx + fw / 2, y + RH / 2 + size * 0.36, name, size=size, weight=600, color=f"{f.tone}.text",
                     bg=f"{f.tone}.tint", anchor="middle")
            # Bit numbers under the field: the high bit at its left edge, the low bit at its right edge.
            ny = y + RH + ns + 4
            if f.width == 1:
                fig.text(fx + fw / 2, ny, str(f.hi), size=ns, color="muted", anchor="middle")
            else:
                fig.text(fx + 2, ny, str(f.hi), size=ns, color="muted")
                fig.text(fx + fw - 2, ny, str(f.lo), size=ns, color="muted", anchor="end")
        y += RH + ns + 26
    if fr.waveform:
        y = _waveform(fig, fr, x0, x1, bx, bw, y + 8, LW)
    if fr.decode:
        y = _decode(fig, fr, y + 10, field_boxes)
    fig._grow(y)
    layout_problems(fig, bodies, [])
    fig.doc = (f"Reads: One {fr.title} of the {hw.chip}, {fr.bits} bits in a row from the most significant (left, sent "
               "first) to the least significant (right). Each row is one kind of frame; each coloured box a field, "
               "with its first and last bit number under it."
               + (" The waveform below draws the select, the clock and the data lines over the same bits."
                  if fr.waveform else "")
               + (f" The table at the bottom names each bit of the {fr.decode.field} field." if fr.decode else ""))
    return fig


def _waveform(fig: Fig, fr, x0: float, x1: float, bx, bw: float, y: float, LW: float) -> float:
    k = fig.k
    wv = fr.waveform
    cpol, cpha = wv.spi_mode >> 1, wv.spi_mode & 1
    LH, gap = 30, 16
    lane_y = y

    def label(name: str, yy: float) -> None:
        fig.text(0, yy + LH / 2 + k["mono"] * 0.36, name, size=k["mono"], weight=700, mono=True)

    hi_lo = lambda yy, v: yy + (4 if v else LH - 4)  # noqa: E731 - level -> y
    # Select: high, low for the whole frame, high again.
    label(wv.select, lane_y)
    sx0, sx1 = x0 - 20, x1 + 20
    fig.line([(LW, hi_lo(lane_y, 1)), (sx0, hi_lo(lane_y, 1)), (sx0, hi_lo(lane_y, 0)), (sx1, hi_lo(lane_y, 0)),
              (sx1, hi_lo(lane_y, 1)), (fig.body_w, hi_lo(lane_y, 1))], color="ink2", sw=2.0, layer="edge")
    lane_y += LH + gap
    # Clock: idles at CPOL; each bit has a first half and a second half level.
    label(wv.clock, lane_y)
    first = cpol ^ cpha
    pts = [(LW, hi_lo(lane_y, cpol)), (x0, hi_lo(lane_y, cpol))]
    level = cpol
    for i in range(fr.bits):
        a, m, b = x0 + i * bw, x0 + (i + 0.5) * bw, x0 + (i + 1) * bw
        for xx, v in ((a, first), (m, 1 - first)):
            if v != level:
                pts += [(xx, hi_lo(lane_y, level)), (xx, hi_lo(lane_y, v))]
                level = v
    if level != cpol:
        pts += [(x1, hi_lo(lane_y, level)), (x1, hi_lo(lane_y, cpol))]
    pts.append((fig.body_w, hi_lo(lane_y, cpol)))
    fig.line(pts, color="blue.strong", sw=2.0, layer="edge")
    lane_y += LH + gap
    for ln in wv.lanes:
        label(ln.name, lane_y)
        row = fr.row(ln.row) if ln.row else None
        mid = lane_y + LH / 2
        fig.line([(LW, mid), (x0, mid)], color="rail", sw=1.6, layer="edge")
        fig.line([(x1, mid), (fig.body_w, mid)], color="rail", sw=1.6, layer="edge")
        if row is None:
            fig.line([(x0, mid), (x1, mid)], color="rail", sw=1.6, dash="5 4", layer="edge")
        else:
            for f in row.fields:
                a, b = bx(f.hi), bx(f.hi) + f.width * bw
                s = min(5.0, (b - a) / 4)
                fig.path([("M", a, mid), ("L", a + s, lane_y + 3), ("L", b - s, lane_y + 3), ("L", b, mid),
                          ("L", b - s, lane_y + LH - 3), ("L", a + s, lane_y + LH - 3), ("Z",)],
                         stroke=f"{f.tone}.strong", fill=f"{f.tone}.tint", sw=1.4, layer="node")
                name = f.short or f.name
                if text_width(name, k["small"], 600) <= (b - a) - 2 * s - 6:
                    fig.text((a + b) / 2, mid + k["small"] * 0.36, name, size=k["small"], weight=600,
                             color=f"{f.tone}.text", bg=f"{f.tone}.tint", anchor="middle")
        lane_y += LH + gap
    edge = "rising" if cpol == cpha else "falling"
    other = "falling" if edge == "rising" else "rising"
    note = (f"SPI mode {wv.spi_mode}: {wv.clock} idles {'high' if cpol else 'low'}; the chip samples its input on "
            f"the {edge} edge and changes its output after the {other} edge. {wv.select} stays low for the whole "
            "frame.")
    yy = lane_y + 4
    for ln in wrap(note, fig.body_w, k["small"]):
        fig.text(0, yy + k["small"] * 0.8, ln, size=k["small"], color="muted")
        yy += k["small"] * 1.45
    return yy + 6


def _decode(fig: Fig, fr, y: float, field_boxes: dict) -> float:
    k = fig.k
    d = fr.decode
    W = fig.body_w
    for ln in wrap(f"{d.field}, one flag per bit (datasheet {_short(d.ref)})", W, k["card_title"], 700):
        fig.text(0, y + k["card_title"] * 0.85, ln, size=k["card_title"], weight=700)
        y += k["card_title"] * 1.3
    y += 12
    entry = max(text_width(n, k["mono"], 400, True) for _b, n in d.bits) + 56 + 28
    cols = max(1, min(4, int((W + 12) // (entry + 12))))
    cw = (W - (cols - 1) * 12) / cols
    rows = math.ceil(len(d.bits) / cols)
    RH = k["mono"] + 22
    for i, (b, n) in enumerate(d.bits):
        c, r = i // rows, i % rows
        x, yy = c * (cw + 12), y + r * (RH + 8)
        fig.rect(x, yy, cw, RH, fill="paper", stroke="line", rx=8)
        fig.pill(x + 8, yy + (RH - k["pill"] - 10) / 2, f"bit {b}", tone="slate", solid=True)
        fig.text(x + 8 + fig.pill_width(f"bit {b}") + 12, yy + RH / 2 + k["mono"] * 0.36, n, size=k["mono"],
                 mono=True, bg="paper")
    return y + rows * (RH + 8)


# ---------------------------------------------------------------------------------------------------- wiring


@dataclass
class _Row:
    """One wire of the wiring figure."""

    net: object
    near: str  # the pin label at the near end: the MCU's, or the intermediate part's
    far: str  # the pin at the far end: the chip's pin name, or the intermediate part's pin label
    hooks: list[str] = field(default_factory=list)  # driver calls shown under the wire
    via: str = ""  # a series part the wire goes through
    extra: list[str] = field(default_factory=list)  # other two-pin parts on the net
    chip_pin: str = ""  # the chip pin this wire ends on (empty for an MCU-to-part wire)


@dataclass
class _Between:
    """A part between the MCU and the chip (a buffer, a transceiver, a level shifter, a load switch): the wires
    from the MCU into it and the wires from it to the chip."""

    part: object
    into: list[_Row]
    out: list[_Row]


def _plan(hw: Hardware, c):
    """The wires of a circuit's wiring figure: MCU to chip (directly or through one series part), MCU to a part
    between them and that part to the chip, and the chip to the external blocks."""
    chip = c.chip
    host = next((p for p in c.parts.values() if p.kind == "mcu"), None)
    signal = [n for n in c.nets if n.kind not in ("supply", "ground")]
    pins_by_name: dict = {}
    for p in hw.pins:
        pins_by_name.setdefault(p.name, p)

    def on(n, pid: str) -> list[str]:
        return [pn for q, pn in n.nodes if q == pid]

    def other_net(pid: str, net):
        return next((m for m in signal if m is not net and on(m, pid)), None)

    def label(part, pn: str) -> str:
        return dict(part.pins).get(pn, pn)

    def hooks_of_chip(pn: str) -> list[str]:
        pin = pins_by_name.get(pn)
        return [hw.hooks[h].call for h in c.hooks_of(pin)] if pin else []

    def hooks_of_net(n) -> list[str]:
        return [hw.hooks[h].call for h in n.hooks] if n.hook_set else []

    direct: list[_Row] = []
    used_series: set[str] = set()
    used_nets: set[str] = set()
    if host:
        for n in signal:
            cp, mp = on(n, chip.id), on(n, host.id)
            if cp and mp:
                direct.append(_Row(n, label(host, mp[0]), cp[0], hooks_of_chip(cp[0]), chip_pin=cp[0]))
                used_nets.add(n.name)
            elif mp and not cp:
                # An MCU pin that reaches the chip through one series part (a resistor in a UART TX line).
                for pid, _pn in n.nodes:
                    m = other_net(pid, n) if c.parts[pid].two_pin else None
                    q = on(m, chip.id) if m else []
                    if q and not on(m, host.id):
                        direct.append(_Row(m, label(host, mp[0]), q[0], hooks_of_chip(q[0]), via=pid, chip_pin=q[0]))
                        used_series.add(pid)
                        used_nets.update((n.name, m.name))
                        break
    # Parts between the MCU and the chip.
    between: list[_Between] = []
    if host:
        for x in c.parts.values():
            if x.kind != "ic":
                continue
            into, out = [], []
            for n in signal:
                xp = on(n, x.id)
                if not xp or n.name in used_nets:
                    continue
                mp, cp = on(n, host.id), on(n, chip.id)
                if mp and not cp:
                    into.append(_Row(n, label(host, mp[0]), label(x, xp[0]), hooks_of_net(n)))
                elif cp and not mp:
                    out.append(_Row(n, label(x, xp[0]), cp[0], hooks_of_chip(cp[0]), chip_pin=cp[0]))
                elif not mp and not cp:
                    # Through one series part to the chip (a resistor at the first pixel) or from the MCU.
                    for pid, _pn in n.nodes:
                        m = other_net(pid, n) if c.parts[pid].two_pin else None
                        if m is None or on(m, x.id) or m.name in used_nets:
                            continue
                        q, mq = on(m, chip.id), on(m, host.id)
                        if q and not mq:
                            out.append(_Row(m, label(x, xp[0]), q[0], hooks_of_chip(q[0]), via=pid, chip_pin=q[0]))
                        elif mq and not q:
                            into.append(_Row(m, label(host, mq[0]), label(x, xp[0]), hooks_of_net(m), via=pid))
                        else:
                            continue
                        break
            if into and not out:
                # A load switch: the MCU enables it and it feeds a chip supply pin.
                for n in c.nets:
                    if n.kind == "supply" and on(n, x.id) and on(n, chip.id):
                        cp = sorted(set(on(n, chip.id)))[0]
                        out.append(_Row(n, label(x, on(n, x.id)[0]), cp, [], chip_pin=cp))
            if into and out:
                between.append(_Between(x, into, out))
                for r in into + out:
                    used_nets.add(r.net.name)
                    if r.via:
                        used_series.add(r.via)
    inter = {b.part.id for b in between}
    externals = [p for p in c.parts.values() if p.kind in ("ic", "connector") and p.id not in inter]
    right: dict[str, list[_Row]] = {e.id: [] for e in externals}
    for n in signal:
        if n.name in used_nets:
            continue
        cp = on(n, chip.id)
        ext = [(pid, pn) for pid, pn in n.nodes if pid in right]
        if cp and ext:
            pid, pn = ext[0]
            right[pid].append(_Row(n, label(c.parts[pid], pn), cp[0], chip_pin=cp[0]))
    rows = direct + [r for b in between for r in b.into + b.out] + [r for v in right.values() for r in v]
    for r in rows:
        if r.net.kind != "supply":
            r.extra = [pid for pid, _pn in r.net.nodes if c.parts[pid].two_pin and pid not in used_series]
    return host, direct, between, externals, right, pins_by_name


def reaches_chip(hw: Hardware, c) -> bool:
    """Whether an MCU signal of circuit ``c`` reaches the chip: the circuit then has a wiring figure."""
    host, direct, between, _e, _r, _p = _plan(hw, c)
    return bool(host and (direct or between))


def _fit(text: str, width: float, size: float, weight: int = 400, mono: bool = False) -> str:
    """``text``, ellipsised to ``width`` when it is wider."""
    if text_width(text, size, weight, mono) <= width:
        return text
    while text and text_width(text + "…", size, weight, mono) > width:
        text = text[:-1]
    return text.rstrip(" ,;-") + "…"


def _lines(text: str, width: float, size: float, weight: int = 400, most: int = 2) -> list[str]:
    """``text`` wrapped to ``width``, at most ``most`` lines, the last one ellipsised when more is left."""
    ls = wrap(text, width, size, weight)
    if len(ls) > most:
        ls = ls[:most - 1] + [_fit(" ".join(ls[most - 1:]), width, size, weight)]
    return [_fit(ln, width, size, weight) for ln in ls]


def wiring(hw: Hardware, cid: str) -> Fig:
    c = next(x for x in hw.circuits if x.id == cid)
    chip = c.chip
    host, left, between, externals, right, pins_by_name = _plan(hw, c)
    supplies = [n for n in c.nets if n.kind in ("supply", "ground")]
    nparts = {kind: 0 for kind in ("capacitor", "resistor")}
    other_passives = 0
    for p in c.parts.values():
        if p.two_pin:
            if p.kind in nparts:
                nparts[p.kind] += 1
            else:
                other_passives += 1

    def part_text(pid: str) -> str:
        return f"{pid} {c.parts[pid].value}".strip()

    def sub_lines(r: _Row) -> list[str]:
        bits = list(r.hooks)
        if r.via:
            bits.append(f"through {part_text(r.via)}")
        if r.extra:
            bits.append("+ " + ", ".join(part_text(x) for x in r.extra))
        return bits  # one line each under the wire

    def hook_text(r: _Row) -> str:
        return f" ({' and '.join(r.hooks)})" if r.hooks else ""

    mcu_name = (host.label or "MCU") if host else "MCU"
    alt_bits = [f"{mcu_name} {r.near} to {r.far}" + (f" through {part_text(r.via)}" if r.via else "") + hook_text(r)
                for r in left]
    for b in between:
        name = b.part.label or b.part.id
        alt_bits += [f"{mcu_name} {r.near} to {name} {r.far}" + (f" through {part_text(r.via)}" if r.via else "")
                     + hook_text(r) for r in b.into]
        alt_bits += [f"{name} {r.near} to {r.far}" + (f" through {part_text(r.via)}" if r.via else "")
                     + hook_text(r) for r in b.out]
    alt_bits += [f"{r.far} to {e.label or e.id} {r.near}" for e in externals for r in right[e.id]]
    alt = (f"Wiring of the {hw.chip} for the {c.title}: " + "; ".join(alt_bits)
           + ". Supplies, grounds and the support parts are listed under the drawing.")
    chip_rows = left + [r for b in between for r in b.out] + [r for v in right.values() for r in v]
    fig = Fig(f"chip-wiring-{c.id}", f"Wiring: {c.title}", alt=alt, width=W_FIG, profile="overview",
              kicker="Pins and wiring",
              subtitle="What you connect by hand, with the driver hook on each MCU wire. The full schematic, with "
              f"every part and value, is on the Hardware page. Datasheet: {c.ref.short()}.",
              legend=[(PIN_TYPES[t][0], PIN_TYPES[t][1]) for t in PIN_TYPES
                      if any(pins_by_name[r.chip_pin].type == t for r in chip_rows if r.chip_pin in pins_by_name)])
    k = fig.k
    W = fig.body_w
    mono = k["mono"]
    small = k["small"]
    all_rows = chip_rows + [r for b in between for r in b.into]
    subs = {id(r): sub_lines(r) for r in all_rows}
    # Row pitch: the net name above the wire, the hooks (and a series or extra part) under it, one line each.
    most = max([len(v) for v in subs.values()] + [1])
    RP = 64 + mono * 1.35 * (most - 1)
    pad = k["pad"]

    def tag_of(r: _Row) -> str:
        num = ", ".join(str(q.number) for q in hw.pin(r.chip_pin)) if r.chip_pin in pins_by_name else ""
        return r.net.name + (f"  pin {num}" if num else "")

    def span(rows: list[_Row]) -> float:
        """The room a wire's texts need between its two ends."""
        return max([text_width(s, mono, 400, True) for r in rows for s in subs[id(r)]]
                   + [text_width(tag_of(r), small, 600) for r in rows] + [80]) + 40

    mcu_rows = left + [r for b in between for r in b.into]
    host_lab_w = max([text_width(r.near, mono, 600, True) for r in mcu_rows] + [60])
    hw_w = max(200, math.ceil(host_lab_w + 2 * pad + 16))
    chip_lab_w = max([text_width(r.far, mono, 700, True) for r in chip_rows] + [60])
    has_right = any(right.values())
    chip_w = max(240, math.ceil(chip_lab_w * (2 if has_right else 1) + 2 * pad + (40 if has_right else 16)))
    gap_l = span(left) if left else 0
    if between:
        gap_a = span([r for b in between for r in b.into])
        gap_b = span([r for b in between for r in b.out])
        in_w = max(text_width(r.far, mono, 600, True) for b in between for r in b.into)
        out_w = max(text_width(r.near, mono, 600, True) for b in between for r in b.out)
        x_w = min(300, max(150, math.ceil(in_w + out_w + 2 * pad + 28)))
        mid = max(gap_l, gap_a + x_w + gap_b)
    else:
        gap_a = gap_b = x_w = 0
        mid = max(gap_l, 120)
    ext_w = 0
    gap_r = 0
    if has_right:
        ext_w = max([text_width(r.near, mono, 600, True) for v in right.values() for r in v]
                    + [text_width(e.label or e.id, k["card_title"], 700) * 0.6 for e in externals] + [120])
        ext_w = min(240, math.ceil(ext_w + 2 * pad + 16))
        gap_r = max([text_width(tag_of(r), small, 600) for v in right.values() for r in v] + [60]) + 40
    total = hw_w + mid + chip_w + (gap_r + ext_w if has_right else 0)
    if total > W:
        fig.problem(f"the wiring needs {total:.0f} px, the figure has {W:.0f}")
    x_host = max(0.0, (W - total) / 2)
    x_chip = x_host + hw_w + mid
    x_mid = x_host + hw_w + (mid - (gap_a + x_w + gap_b)) / 2 + gap_a  # the parts between, centred in the gap
    x_ext = x_chip + chip_w + gap_r
    head = k["card_title"] * 1.3 + pad + 18
    y0 = 0.0
    # Left column: the direct wires, then each part between with its name above it.
    y = y0 + head
    left_y = [y + (i + 0.5) * RP for i in range(len(left))]
    y += len(left) * RP
    groups = []
    for b in between:
        name_lines = _lines(b.part.label or b.part.id, x_w, small, 700)
        y += len(name_lines) * small * 1.3 + 10
        n = max(len(b.into), len(b.out))
        groups.append((b, name_lines, y, n))
        y += n * RP + 8
    n_right = sum(len(v) for v in right.values()) + max(0, len([e for e in externals if right[e.id]]) - 1)
    body_h = max(y - y0, head + max(n_right, 1 if not (left or between) else 0) * RP) + pad
    bodies = []
    # Chip card.
    cbox = fig.rect(x_chip, y0, chip_w, body_h, fill="paper", stroke="ink2", sw=2.2, rx=10)
    fig.text(x_chip + chip_w / 2, y0 + pad + k["card_title"] * 0.85, _fit(hw.chip, chip_w - 2 * pad,
             k["card_title"], 700), size=k["card_title"], weight=700, bg="paper", anchor="middle")
    fig.text(x_chip + chip_w / 2, y0 + pad + k["card_title"] * 0.85 + small * 1.4, chip.id, size=small,
             color="muted", bg="paper", anchor="middle")
    bodies.append((cbox, "the chip"))
    wires = []

    def stub(x: float, yy: float, pin_name: str, side: str) -> None:
        p = pins_by_name.get(pin_name)
        tone = p.tone if p else "slate"
        _graphic_contrast(fig, tone, f"the pin stub of {pin_name}")
        sx = x - 14 if side == "left" else x
        fig.rect(sx, yy - 6, 14, 12, fill=f"{tone}.tint", stroke=f"{tone}.strong", sw=1.4, rx=2, layer="label")

    def wire(a: tuple, b: tuple, r: _Row, color: str) -> None:
        fig.line([a, b], color=color, sw=2.2, layer="edge")
        wires.append((a, b))
        mx = (a[0] + b[0]) / 2
        fig.text(mx, a[1] - 10, tag_of(r), size=small, weight=600, color="ink2", anchor="middle")
        for j, s in enumerate(subs[id(r)]):
            fig.text(mx, a[1] + 10 + mono * 0.8 + j * mono * 1.35, s, size=mono, mono=True, color="muted",
                     anchor="middle")

    def chip_end(r: _Row, yy: float) -> str:
        fig.text(x_chip + pad + 4, yy + mono * 0.36, r.far, size=mono, weight=700, mono=True, bg="paper")
        stub(x_chip, yy, r.far, "left")
        p = pins_by_name.get(r.far)
        return f"{p.tone}.strong" if p else "ink2"

    def host_pin(r: _Row, yy: float) -> None:
        fig.text(x_host + hw_w - pad, yy + mono * 0.36, r.near, size=mono, weight=600, mono=True, color="blue.text",
                 bg="blue.tint", anchor="end")

    if host and (left or between):
        hbox = fig.rect(x_host, y0, hw_w, body_h, fill="blue.tint", stroke="blue.strong", sw=1.4)
        bodies.append((hbox, "the MCU"))
        fig.text(x_host + pad, y0 + pad + k["card_title"] * 0.85, _fit(mcu_name, hw_w - 2 * pad, k["card_title"], 700),
                 size=k["card_title"], weight=700, color="blue.text", bg="blue.tint")
        fig.text(x_host + pad, y0 + pad + k["card_title"] * 0.85 + small * 1.4, host.id, size=small,
                 color="blue.text", bg="blue.tint")
        for r, yy in zip(left, left_y):
            host_pin(r, yy)
            color = chip_end(r, yy)
            wire((x_host + hw_w, yy), (x_chip - 14, yy), r, color)
        for b, name_lines, top, n in groups:
            xbox = fig.rect(x_mid, top, x_w, n * RP, fill="violet.tint", stroke="violet.strong", sw=1.4)
            bodies.append((xbox, b.part.label or b.part.id))
            for t, ln in enumerate(name_lines):
                fig.text(x_mid, top - 10 - (len(name_lines) - 1 - t) * small * 1.3, ln, size=small, weight=700,
                         color="violet.text")
            for i, r in enumerate(b.into):
                yy = top + i * RP + RP / 2
                host_pin(r, yy)
                fig.text(x_mid + pad, yy + mono * 0.36, r.far, size=mono, weight=600, mono=True, color="violet.text",
                         bg="violet.tint")
                wire((x_host + hw_w, yy), (x_mid, yy), r, "ink2")
            for i, r in enumerate(b.out):
                yy = top + i * RP + RP / 2
                fig.text(x_mid + x_w - pad, yy + mono * 0.36, r.near, size=mono, weight=600, mono=True,
                         color="violet.text", bg="violet.tint", anchor="end")
                color = chip_end(r, yy)
                wire((x_mid + x_w, yy), (x_chip - 14, yy), r, color)
    yr = 0
    for e in externals:
        items = right[e.id]
        if not items:
            continue
        ey = y0 + head + yr * RP
        eh = len(items) * RP
        ebox = fig.rect(x_ext, ey, ext_w, eh, fill="teal.tint", stroke="teal.strong", sw=1.4)
        bodies.append((ebox, e.label or e.id))
        # The block's name above it, in the room the chip's header (or the blank row before it) leaves.
        for t, ln in enumerate(e_lines := _lines(e.label or e.id, ext_w, small, 700)):
            fig.text(x_ext, ey - 10 - (len(e_lines) - 1 - t) * small * 1.3, ln, size=small, weight=700,
                     color="teal.text")
        for i, r in enumerate(items):
            yy = ey + i * RP + RP / 2
            fig.text(x_chip + chip_w - pad - 4, yy + mono * 0.36, r.far, size=mono, weight=700, mono=True, bg="paper",
                     anchor="end")
            stub(x_chip + chip_w, yy, r.far, "right")
            fig.text(x_ext + pad, yy + mono * 0.36, r.near, size=mono, weight=600, mono=True, color="teal.text",
                     bg="teal.tint")
            p = pins_by_name.get(r.far)
            a, b = (x_chip + chip_w + 14, yy), (x_ext, yy)
            fig.line([a, b], color=f"{p.tone}.strong" if p else "ink2", sw=2.2, layer="edge")
            wires.append((a, b))
            fig.text((a[0] + b[0]) / 2, yy - 10, tag_of(r), size=small, weight=600, color="ink2", anchor="middle")
        yr += len(items) + 1
    y = y0 + body_h + 28
    # Supplies, support parts and unused pins, in words.
    lines = []
    for n in supplies:
        on_chip = sorted({pn for pid, pn in n.nodes if pid == chip.id})
        others = [f"{pid}.{pn}" for pid, pn in n.nodes if pid != chip.id and not c.parts[pid].two_pin]
        if on_chip:
            lines.append(f"{n.name}: {', '.join(on_chip)}" + (f"; also {', '.join(others)}" if others else ""))
        else:
            # A supply that reaches no chip pin (a switched battery rail of the load): name what it feeds.
            fed = others or sorted({pid for pid, _pn in n.nodes})
            lines.append(f"{n.name} (no {hw.chip} pin): {', '.join(fed)}")
    if lines:
        box = fig.note(0, y, W, " · ".join(lines), tone="rose", title="Supplies and ground")
        y = box.b + 14
    count = []
    if nparts["capacitor"]:
        count.append(f"{nparts['capacitor']} capacitor{'s' if nparts['capacitor'] > 1 else ''}")
    if nparts["resistor"]:
        count.append(f"{nparts['resistor']} resistor{'s' if nparts['resistor'] > 1 else ''}")
    if other_passives:
        count.append(f"{other_passives} other part{'s' if other_passives > 1 else ''}")
    unused = sorted({pn for pid, pn in c.unused if pid == chip.id}, key=lambda s: (len(s), s))
    words = []
    if count:
        words.append(f"Support parts: {', '.join(count)} around the supplies (values in the full schematic).")
    if unused and len(unused) <= 16:
        words.append(f"Not wired in this circuit ({len(unused)}): {', '.join(unused)}.")
    elif unused:
        words.append(f"{len(unused)} pins are not drawn in this circuit; the full schematic lists them.")
    if words:
        box = fig.note(0, y, W, " ".join(words), tone="slate", title="Also on the board")
        y = box.b
    fig._grow(y)
    unverified_note(fig, [f"net {n.name}: {n.unverified}" for n in c.nets if n.unverified]
                    + [f"{p.id}: {p.unverified}" for p in c.parts.values() if p.unverified])
    layout_problems(fig, bodies, wires)
    _text_on_bodies(fig, bodies)
    names = ", ".join(b.part.label or b.part.id for b in between)
    fig.doc = (f"Reads: The {host.label if host else 'host'} on the left, the {hw.chip}"
               + (f" on the right of the parts between them ({names})" if between else " in the middle")
               + (", the blocks it drives on the right" if has_right else "")
               + ". Each wire to the chip is coloured by the chip pin's electrical type and carries the net name and "
               "the chip pin number above it and, under it, the driver hooks that use it (and any part on the net). "
               "The boxes underneath list the supplies, the support parts and the pins this circuit leaves "
               "unconnected.")
    return fig
