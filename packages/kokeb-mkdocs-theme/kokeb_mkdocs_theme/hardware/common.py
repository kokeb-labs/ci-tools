"""Helpers every chip figure shares: the mark and footnote for unconfirmed facts, and the layout checks.

Kept apart from ``render`` (pinout, blocks) and ``circuit`` so neither imports the other.
"""

from __future__ import annotations

from ..figkit import Box, Fig, wrap

UNVERIFIED_MARK = "*"


def unverified_note(fig: Fig, items: list[str], y: float | None = None) -> None:
    """A footnote line under the figure for facts not confirmed in the datasheet."""
    if not items:
        return
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
