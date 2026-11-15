"""``matrix``: a grid of cells, as a status matrix or a heat map. Every cell carries text, and a status cell also a
glyph, so colour is never the only carrier. A table twin (``<id>.table.html``) is written from the same facts.

Model::

    kind: matrix
    id: port-capabilities
    title: ...
    alt: One sentence.
    reads: Two or more sentences.
    rows: [{id: i2c, label: I2C}]
    cols: [{id: host, label: Host}]
    cells:                      # status cell: native|adapted|fallback|planned|na, mapped by "statuses"
      - {row: i2c, col: host, status: ok, text: native, note: "400 kHz"}
      - {row: i2c, col: esp, value: 3, text: "3 ch"}        # heat cell: value is mapped onto the ramp
    heat: {min: 0, max: 8}      # optional: range of the ramp (default: the data's own range)
    statuses: {ok: native}      # optional: legend text of each status used (default: the status name)
"""

from __future__ import annotations

from ..core import PROFILES, text_width
from ._common import Check, check_header, make_fig

REQUIRED = {"rows", "cols", "cells"}
ALLOWED = {"heat", "statuses", "row_header", "cell_width"}
STATUS = ("ok", "warn", "fail", "na", "planned")
GLYPH = {"ok": "check", "warn": "bang", "fail": "cross", "na": "dash", "planned": "dots"}
CELL_H = 60.0


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "matrix", REQUIRED, ALLOWED)
    rows = [str(r["id"]) for r in model.get("rows") or [] if isinstance(r, dict) and "id" in r]
    cols = [str(r["id"]) for r in model.get("cols") or [] if isinstance(r, dict) and "id" in r]
    for key in ("rows", "cols"):
        for i, r in enumerate(model.get(key) or []):
            c.keys(r, f"{key}[{i}]", {"id"}, {"label"})
    seen = set()
    for i, cell in enumerate(model.get("cells") or []):
        p = f"cells[{i}]"
        if not c.keys(cell, p, {"row", "col"}, {"status", "value", "text", "note"}):
            continue
        if str(cell["row"]) not in rows:
            c.bad(f"{p}.row: unknown row {cell['row']!r}")
        if str(cell["col"]) not in cols:
            c.bad(f"{p}.col: unknown column {cell['col']!r}")
        if (cell["row"], cell["col"]) in seen:
            c.bad(f"{p}: duplicate cell")
        seen.add((cell["row"], cell["col"]))
        if ("status" in cell) == ("value" in cell):
            c.bad(f"{p}: give either status or value")
        if "status" in cell and cell["status"] not in STATUS:
            c.bad(f"{p}.status: one of {', '.join(STATUS)}")
        if "value" in cell and (not isinstance(cell["value"], (int, float)) or isinstance(cell["value"], bool)):
            c.bad(f"{p}.value: a number")
    c.done()


def _glyph(f, kind: str, cx: float, cy: float, tone: str) -> None:
    col = f"{tone}.strong"
    if kind == "check":
        f.path([("M", cx - 6, cy), ("L", cx - 2, cy + 5), ("L", cx + 7, cy - 6)], stroke=col, sw=2.4)
    elif kind == "cross":
        f.path([("M", cx - 5, cy - 5), ("L", cx + 5, cy + 5)], stroke=col, sw=2.4)
        f.path([("M", cx + 5, cy - 5), ("L", cx - 5, cy + 5)], stroke=col, sw=2.4)
    elif kind == "bang":
        f.path([("M", cx, cy - 7), ("L", cx, cy + 2)], stroke=col, sw=2.6)
        f.circle(cx, cy + 6, 1.6, fill=col, stroke=None)
    elif kind == "dash":
        f.path([("M", cx - 6, cy), ("L", cx + 6, cy)], stroke=col, sw=2.4)
    else:  # dots
        for dx in (-7, 0, 7):
            f.circle(cx + dx, cy, 1.9, fill=col, stroke=None)


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    k = PROFILES[model.get("profile", "detail")]
    rows, cols = model["rows"], model["cols"]
    cells = {(str(c["row"]), str(c["col"])): c for c in model["cells"]}
    vals = [c["value"] for c in model["cells"] if "value" in c]
    heat = model.get("heat") or {}
    lo, hi = heat.get("min", min(vals, default=0)), heat.get("max", max(vals, default=1))
    rh_w = max([text_width(str(r.get("label", r["id"])), k["card_body"], 700) for r in rows] + [90]) + 28
    cw = float(model.get("cell_width", 128))
    width = int(rh_w + len(cols) * cw + 64 + 16)
    f = make_fig(model, "matrix", width)
    x0 = max(0.0, (f.body_w - rh_w - len(cols) * cw) / 2)
    hdr = 40.0
    for j, col in enumerate(cols):
        f.text(x0 + rh_w + j * cw + cw / 2, hdr - 12, str(col.get("label", col["id"])), size=k["card_body"], weight=700,
               color="ink", anchor="middle")
    head, body = ["" ] + [str(c.get("label", c["id"])) for c in cols], []
    used = set()
    for i, r in enumerate(rows):
        y = hdr + i * CELL_H
        f.text(x0 + 4, y + CELL_H / 2 + 5, str(r.get("label", r["id"])), size=k["card_body"], weight=700, color="ink")
        row_out = [str(r.get("label", r["id"]))]
        for j, col in enumerate(cols):
            cell = cells.get((str(r["id"]), str(col["id"])))
            x = x0 + rh_w + j * cw
            if cell is None:
                f.rect(x + 3, y + 3, cw - 6, CELL_H - 6, fill="card", stroke="line", sw=1.0)
                f.nontext("line", ("canvas", "card"), "empty cell outline")
                row_out.append("")
                continue
            if "status" in cell:
                tone, glyph = cell["status"], GLYPH[cell["status"]]
                used.add(tone)
            else:
                step = 0 if hi == lo else min(4, int((cell["value"] - lo) / (hi - lo) * 5))
                tone, glyph = f"h{max(0, step)}", ""
            text = str(cell.get("text", cell.get("status", cell.get("value", ""))))
            if "status" in cell:
                f.rect(x + 3, y + 3, cw - 6, CELL_H - 6, fill=f"{tone}.tint", stroke=f"{tone}.strong", sw=1.4)
                f.nontext(f"{tone}.strong", ("canvas", f"{tone}.tint"), f"cell {r['id']}/{col['id']}")
            else:  # a heat cell is bounded by a neutral outline; its value is written in the cell
                f.rect(x + 3, y + 3, cw - 6, CELL_H - 6, fill=f"{tone}.tint", stroke="line", sw=1.4)
                f.nontext("line", ("canvas",), f"cell {r['id']}/{col['id']}")
            tw = text_width(text, k["card_body"], 600)
            if tw + (30 if glyph else 12) > cw - 6:
                f.problem(f"cell {r['id']}/{col['id']}: text {text!r} is wider than the cell")
            ty = y + CELL_H / 2 + (0 if not cell.get("note") else -3) + 5
            if glyph:
                gx = x + cw / 2 - tw / 2 - 12
                _glyph(f, glyph, gx, ty - 5, tone)
                f.text(x + cw / 2 + 10, ty, text, size=k["card_body"], weight=600, color=f"{tone}.text",
                       bg=f"{tone}.tint", anchor="middle")
            else:
                f.text(x + cw / 2, ty, text, size=k["card_body"], weight=600, color=f"{tone}.text",
                       bg=f"{tone}.tint", anchor="middle")
            if cell.get("note"):
                f.text(x + cw / 2, y + CELL_H - 9, str(cell["note"]), size=k["small"], color=f"{tone}.text",
                       bg=f"{tone}.tint", anchor="middle")
            row_out.append(text + (f" ({cell['note']})" if cell.get("note") else ""))
        body.append(row_out)
    f.twin = {"caption": f.title, "head": head, "rows": body}
    return f
