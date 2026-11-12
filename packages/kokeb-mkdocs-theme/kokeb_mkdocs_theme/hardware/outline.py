"""The ``chip-outline`` figure: the package body from above, drawn to scale, with its pads, the dimension arrows
and a size label, from ``package.outline`` of ``docs/hardware.yml``.

It reuses the pinout's vocabulary (pads coloured by the pin's electrical type, pin 1 marked, pins numbered
counter-clockwise from it, the legend) and its checks: no two texts overlap and no dimension line runs through a
text or the body. What is to scale is the body (``length_mm`` down the left edge, ``width_mm`` across the top) and,
when the file gives it, the pitch and the height in a side view. The pads are drawn centred on each side at the
stated pitch, as a picture of where the pins are, not as the land pattern: the datasheet's recommended footprint is
the reference for a board. A leaded package (SOIC, TSSOP, SOT, QFP) shows its leads reaching out of the body; a
leadless one (QFN, DFN, LGA) shows its pads inside the edge.
"""

from __future__ import annotations

import math

from ..figkit import Box, Fig, text_width, wrap
from .common import layout_problems
from .model import PIN_TYPES, Hardware

NUM = 11.5  # size of a pad's pin number
DIM = 12.5  # size of a dimension label


def _mm(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".") if v != int(v) else f"{v:.1f}"


def size_text(hw: Hardware) -> str:
    """``2.0 x 2.0 x 0.75 mm`` (the height only when the file has it)."""
    o = hw.package.outline
    parts = [_mm(o.length_mm), _mm(o.width_mm)] + ([_mm(o.height_mm)] if o.height_mm else [])
    return " x ".join(parts) + " mm"


def _scale(o, n_max: int) -> float:
    """Pixels per millimetre: the body about 300 px across, larger when the pitch would leave pads too small to
    number (at most 560 px), never more than 160 px/mm."""
    s = 300 / max(o.length_mm, o.width_mm)
    s = max(s, 190 / min(o.length_mm, o.width_mm))
    if o.pitch_mm:
        s = max(s, 24 / o.pitch_mm)
    s = min(s, 560 / max(o.length_mm, o.width_mm), 160)
    return s


def outline(hw: Hardware) -> Fig:
    pk, o = hw.package, hw.package.outline
    by_num = {int(p.number): p for p in hw.pins if not p.is_pad}
    types = [t for t in PIN_TYPES if any(p.type == t for p in hw.pins)]
    sides = pk.sides
    s = _scale(o, max(len(v) for v in sides.values()))
    W, H = o.width_mm * s, o.length_mm * s
    leadless = pk.leadless
    count = {k: len(v) for k, v in sides.items()}
    # Pad spacing: the pitch, or an even share of the shortest edge that carries pins when none is given.
    if o.pitch_mm:
        step = o.pitch_mm * s
    else:
        step = min(34.0, min((W if k in ("top", "bottom") else H) * 0.8 / max(n, 1) for k, n in count.items() if n))
    pad_w = max(6.0, min(40.0, step * 0.55))
    pad_l = max(10.0, min(22.0, step * 0.7))
    out_l = 0.0 if leadless else pad_l  # how far a pad reaches outside the body

    # Where the annotations go: pitch on the left edge (pin 1's side), length on the right, width below.
    pitch_side = next((k for k in ("left", "top", "bottom", "right") if count.get(k, 0) >= 2), "") \
        if o.pitch_mm else ""
    lab_w = max(text_width(f"{_mm(v)} mm", DIM, 600) for v in (o.length_mm, o.width_mm, o.height_mm or 0.1))
    pitch_lab_w = text_width(f"pitch {_mm(o.pitch_mm)} mm", DIM, 600) if o.pitch_mm else 0
    ring = {k: out_l + 22.0 for k in ("left", "right", "top", "bottom")}  # distance of the next annotation
    left_room = ring["left"] + (30 + pitch_lab_w if pitch_side == "left" else 12) + 10
    right_room = ring["right"] + 30 + 8 + lab_w + (30 + pitch_lab_w if pitch_side == "right" else 0)
    # Text block to the right: the size label, the package line, the datasheet reference.
    label = size_text(hw)
    big = 22
    facts = [f"{pk.type}, {pk.pins} pins" + (" and an exposed pad" if pk.exposed_pad else ""),
             "Leads reach out of the body" if not pk.leadless else "Pads inside the body edge"]
    if o.pitch_mm:
        facts.append(f"Pitch {_mm(o.pitch_mm)} mm")
    if pk.variants:
        facts.append(f"{len(pk.variants)} other package" + ("s" if len(pk.variants) > 1 else "") + ": "
                     + ", ".join(v.type for v in pk.variants))
    lines = [ln for f in facts for ln in wrap(f, 290, 13.5)]
    col_w = max([text_width(label, big, 700), 220] + [text_width(ln, 13.5) for ln in lines])
    gap = 34
    total = left_room + W + right_room + gap + col_w
    width = max(760, math.ceil(total + 64))
    types_in = [(PIN_TYPES[t][0], PIN_TYPES[t][1]) for t in types]
    fig = Fig(
        "chip-outline",
        f"{hw.chip} package, {pk.type}",
        alt=f"Outline of the {hw.chip} in {pk.type} drawn to scale from above: body {size_text(hw)}"
        + (f", pitch {_mm(o.pitch_mm)} mm" if o.pitch_mm else "") + f", {pk.pins} pins"
        + (" and an exposed pad" if pk.exposed_pad else "") + ".",
        width=width,
        kicker="Hardware",
        subtitle="Package body from above, to scale, pin 1 marked; arrows give the datasheet's dimensions. The pads "
        "are centred on each side" + (" at the stated pitch" if o.pitch_mm else ", evenly spaced") + ": the land "
        "pattern is in the datasheet. "
        f"Datasheet: {o.ref.short()}.",
        legend=types_in,
    )
    bx = left_room + (fig.body_w - total) / 2 if fig.body_w > total else left_room
    by = 18.0
    bodies: list[tuple[Box, str]] = []
    wires: list[tuple[tuple, tuple]] = []
    cx, cy = bx + W / 2, by + H / 2
    body = fig.rect(bx, by, W, H, fill="paper", stroke="ink2", sw=2.0, rx=min(8, W / 20))
    bodies.append((body, "the package body"))

    # Exposed pad: shown, not sized (the datasheet's drawing gives its size).
    if pk.exposed_pad:
        ep = [p for p in hw.pins if p.is_pad][0]
        ew, eh = W * 0.4, H * 0.4
        fig.rect(cx - ew / 2, cy - eh / 2 + 18, ew, eh, fill="card", stroke=f"{ep.tone}.strong", sw=1.4, rx=6,
                 dash="5 4")

    # Pads, in the pinout's order: left top to bottom, bottom left to right, right bottom to top, top right to left.
    placed: dict[int, Box] = {}
    for side in ("left", "bottom", "right", "top"):
        nums = sides.get(side, [])
        order = nums if side in ("left", "bottom") else list(reversed(nums))
        for k, n in enumerate(order):
            p = by_num[n]
            off = (k - (len(order) - 1) / 2) * step
            if side in ("left", "right"):
                yy = cy + off
                x0 = (bx - out_l) if side == "left" else (bx + W - (0 if out_l else pad_l))
                box = fig.rect(x0, yy - pad_w / 2, pad_l, pad_w, fill=f"{p.tone}.tint", stroke=f"{p.tone}.strong",
                               sw=1.4, rx=2)
            else:
                xx = cx + off
                y0 = (by - out_l) if side == "top" else (by + H - (0 if out_l else pad_l))
                box = fig.rect(xx - pad_w / 2, y0, pad_w, pad_l, fill=f"{p.tone}.tint", stroke=f"{p.tone}.strong",
                               sw=1.4, rx=2)
            if min(box.w, box.h) >= NUM + 3 and max(box.w, box.h) >= NUM * 1.2 * len(str(n)) * 0.6 + 4:
                fig.text(box.cx, box.cy + NUM * 0.36, str(n), size=NUM, weight=700, color=f"{p.tone}.text",
                         bg=f"{p.tone}.tint", anchor="middle")
            placed[n] = box

    # Pin 1: a dot in the body corner nearest its pad.
    p1 = placed[1]
    dot = (bx + 14 if p1.cx < cx else bx + W - 14, by + 14 if p1.cy < cy else by + H - 14)
    fig.circle(dot[0], dot[1], 6, fill="ink2")

    # The chip's name and package inside the body, when it is wide enough for them clear of the pads.
    room = W - 2 * (pad_l + 12 if leadless else 12)
    for size, text in ((20, hw.chip), (16, hw.chip), (13, hw.chip)):
        if text_width(text, size, 700) <= room:
            fig.text(cx, cy - 8, text, size=size, weight=700, color="ink", bg="paper", anchor="middle")
            if text_width(pk.type, 13) <= room:
                fig.text(cx, cy + 14, pk.type, size=13, color="muted", bg="paper", anchor="middle")
            break

    # Dimension arrows.
    def arrow(p0, p1, tick: float = 7.0) -> None:
        fig.line([p0, p1], color="ink2", sw=1.2, layer="node")
        for a, b in ((p0, p1), (p1, p0)):
            dx, dy = b[0] - a[0], b[1] - a[1]
            d = math.hypot(dx, dy) or 1
            ux, uy = dx / d, dy / d
            fig.path([("M", *a), ("L", a[0] + ux * tick + uy * 3, a[1] + uy * tick - ux * 3),
                      ("L", a[0] + ux * tick - uy * 3, a[1] + uy * tick + ux * 3), ("Z",)], stroke=None,
                     fill="ink2")
        wires.append((p0, p1))

    def ext(p0, p1) -> None:
        fig.line([p0, p1], color="rail", sw=1.0, dash="3 3", layer="bg")
        wires.append((p0, p1))

    # Length (down the left edge, read on the right): extension lines from the body's top and bottom edges.
    xr = bx + W + ring["right"] + (30 + pitch_lab_w if pitch_side == "right" else 0)
    ext((bx + W + 4, by), (xr + 6, by))
    ext((bx + W + 4, by + H), (xr + 6, by + H))
    arrow((xr, by), (xr, by + H))
    fig.text(xr + 10, cy + DIM * 0.36, f"{_mm(o.length_mm)} mm", size=DIM, weight=600, color="ink2")
    # Width, below the body.
    yb = by + H + ring["bottom"] + (30 if pitch_side == "bottom" else 0)
    ext((bx, by + H + 4), (bx, yb + 6))
    ext((bx + W, by + H + 4), (bx + W, yb + 6))
    arrow((bx, yb), (bx + W, yb))
    fig.text(cx, yb + 18, f"{_mm(o.width_mm)} mm", size=DIM, weight=600, color="ink2", anchor="middle")
    bottom = yb + 24

    # Pitch, between the first two pads of the side that has them.
    if pitch_side:
        nums = sides[pitch_side]
        order = nums if pitch_side in ("left", "bottom") else list(reversed(nums))
        a, b = placed[order[0]], placed[order[1]]
        text = f"pitch {_mm(o.pitch_mm)} mm"
        if pitch_side in ("left", "right"):
            xd = (bx - ring["left"] - 14) if pitch_side == "left" else (bx + W + ring["right"] + 14)
            near = (a.x if pitch_side == "left" else a.r)
            ext((near + (-4 if pitch_side == "left" else 4), a.cy), (xd + (6 if pitch_side == "left" else -6), a.cy))
            ext((near + (-4 if pitch_side == "left" else 4), b.cy), (xd + (6 if pitch_side == "left" else -6), b.cy))
            arrow((xd, a.cy), (xd, b.cy), tick=min(7.0, step / 3))
            tx = xd - 10 if pitch_side == "left" else xd + 10
            fig.text(tx, (a.cy + b.cy) / 2 + DIM * 0.36, text, size=DIM, weight=600, color="ink2",
                     anchor="end" if pitch_side == "left" else "start")
        else:
            yd = (by - ring["top"] - 14) if pitch_side == "top" else (by + H + ring["bottom"] + 14)
            near = a.y if pitch_side == "top" else a.b
            ext((a.cx, near + (-4 if pitch_side == "top" else 4)), (a.cx, yd + (6 if pitch_side == "top" else -6)))
            ext((b.cx, near + (-4 if pitch_side == "top" else 4)), (b.cx, yd + (6 if pitch_side == "top" else -6)))
            arrow((a.cx, yd), (b.cx, yd), tick=min(7.0, step / 3))
            fig.text((a.cx + b.cx) / 2, yd + (-8 if pitch_side == "top" else 22), text, size=DIM, weight=600,
                     color="ink2", anchor="middle")
            bottom = max(bottom, yd + 26)

    # Side view: the body's thickness at the same scale, under the width arrow.
    if o.height_mm:
        hh = o.height_mm * s
        ys = bottom + 30
        fig.rect(bx, ys, W, hh, fill="paper", stroke="ink2", sw=2.0, rx=2)
        fig.line([(bx - 24, ys + hh), (bx + W + 24, ys + hh)], color="rail", sw=1.2, layer="bg")
        xh = bx + W + 30
        ext((bx + W + 4, ys), (xh + 6, ys))
        ext((bx + W + 4, ys + hh), (xh + 6, ys + hh))
        arrow((xh, ys), (xh, ys + hh), tick=min(7.0, hh / 3))
        fig.text(xh + 10, ys + hh / 2 + DIM * 0.36, f"{_mm(o.height_mm)} mm", size=DIM, weight=600, color="ink2")
        fig.text(bx - 14, ys + hh / 2 + DIM * 0.36, "Side view", size=DIM, color="muted", anchor="end")
        fig._grow(ys + hh + 6)

    # The size label and the facts beside the drawing.
    tx = bx + W + right_room + gap
    fig.text(tx, by + big, label, size=big, weight=700, color="ink")
    for k, text in enumerate(lines):
        fig.text(tx, by + big + 28 + k * 22, text, size=13.5, color="muted")

    fig.doc = (f"Reads: The {hw.chip} package seen from the top and, when the height is known, from the side, "
               f"drawn to scale: {label}. The arrows carry the datasheet's dimensions, the dot marks pin 1 and the "
               "pads are numbered counter-clockwise from it, coloured by the pin's electrical type (legend below). "
               "Pads sit centred on each side" + (" at the stated pitch" if o.pitch_mm else ", evenly spaced")
               + "; the datasheet's land pattern is the reference for a board.")
    layout_problems(fig, bodies, wires)
    fig.placed = placed
    return fig
