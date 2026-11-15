"""``pipeline``: columns of stages, left to right, with arrows between stages of neighbouring columns.

Model::

    kind: pipeline
    id: board-to-code
    title: ...
    alt: One sentence.
    reads: Two or more sentences naming every column.
    columns:
      - id: inputs
        title: Inputs
        tone: blue
        items:
          - {id: board, title: board.yml, lines: ["pins, buses"], tag: input}
    links:
      - {from: board, to: check, label: read, dashed: false}
"""

from __future__ import annotations

from ..core import PROFILES, card_size
from ._common import Check, check_header, make_fig

REQUIRED = {"columns"}
ALLOWED = {"links", "column_width", "gap"}


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "pipeline", REQUIRED, ALLOWED)
    ids = []
    for i, col in enumerate(model.get("columns") or []):
        p = f"columns[{i}]"
        if c.keys(col, p, {"id", "title", "items"}, {"tone", "sub"}):
            c.tone(col, p)
            for j, it in enumerate(col["items"] or []):
                q = f"{p}.items[{j}]"
                if c.keys(it, q, {"id", "title"}, {"lines", "tag", "tone", "mono"}):
                    ids.append(str(it["id"]))
    if len(set(ids)) != len(ids):
        c.bad("items: duplicate id")
    cols = {str(it["id"]): ci for ci, col in enumerate(model.get("columns") or []) for it in col.get("items", [])}
    for i, l in enumerate(model.get("links") or []):
        p = f"links[{i}]"
        if c.keys(l, p, {"from", "to"}, {"label", "dashed"}):
            for end in ("from", "to"):
                if str(l[end]) not in cols:
                    c.bad(f"{p}.{end}: unknown item {l[end]!r}")
    c.done()


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    k = PROFILES[model.get("profile", "detail")]
    cols = model["columns"]
    n = len(cols)
    gap = int(model.get("gap", 64))
    cw = int(model.get("column_width", 230))
    width = n * cw + (n - 1) * gap + 64
    f = make_fig(model, "pipeline", width, names=[str(c["title"]) for c in cols])
    x0 = (f.body_w - (n * cw + (n - 1) * gap)) / 2
    head = k["region"] + 40
    boxes = {}
    ymax = 0.0
    for ci, col in enumerate(cols):
        x = x0 + ci * (cw + gap)
        tone = col.get("tone", "slate")
        y = head
        heights = []
        for it in col["items"]:
            heights.append(card_size(k, cw - 24, str(it["title"]), [str(v) for v in it.get("lines", [])],
                                     mono=bool(it.get("mono")), tag=str(it.get("tag", "") or "")))
        total = head + sum(heights) + 16 * (len(heights) - 1) + 20
        ymax = max(ymax, total)
        for it, h in zip(col["items"], heights):
            boxes[str(it["id"])] = (ci, x + 12, y, cw - 24, h, it, tone)
            y += h + 16
    for ci, col in enumerate(cols):
        x = x0 + ci * (cw + gap)
        f.region(x, 0, cw, ymax, str(col["title"]), tone=col.get("tone", "slate"), sub=str(col.get("sub", "") or ""))
    placed = {}
    for iid, (ci, x, y, w, h, it, tone) in boxes.items():
        placed[iid] = f.card(x, y + 0, w, str(it["title"]), [str(v) for v in it.get("lines", [])],
                             tone=it.get("tone", tone), h=h, mono=bool(it.get("mono")), tag=str(it.get("tag", "") or ""),
                             accent=False)
    out_n: dict[str, int] = {}
    in_n: dict[str, int] = {}
    for l in model.get("links") or []:
        out_n[str(l["from"])] = out_n.get(str(l["from"]), 0) + 1
        in_n[str(l["to"])] = in_n.get(str(l["to"]), 0) + 1
    out_i: dict[str, int] = {}
    in_i: dict[str, int] = {}
    for l in model.get("links") or []:
        a, b = str(l["from"]), str(l["to"])
        ba, bb = placed[a], placed[b]
        forward = boxes[a][0] < boxes[b][0]
        ia = out_i.get(a, 0)
        out_i[a] = ia + 1
        ib = in_i.get(b, 0)
        in_i[b] = ib + 1
        ta = (ia + 1) / (out_n[a] + 1)
        tb = (ib + 1) / (in_n[b] + 1)
        if boxes[a][0] == boxes[b][0]:
            f.connect(ba, bb, "bottom" if ba.y < bb.y else "top", "top" if ba.y < bb.y else "bottom", dashed=bool(l.get("dashed")), tone="rail")
            continue
        sa, sb = ("right", "left") if forward else ("left", "right")
        f.connect(ba, bb, sa, sb, at=ta, bt=tb, dashed=bool(l.get("dashed")), tone="rail", label=str(l.get("label", "") or ""))
    return f
