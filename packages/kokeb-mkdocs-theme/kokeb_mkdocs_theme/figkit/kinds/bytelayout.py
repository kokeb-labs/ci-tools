"""``bytes``: the layout of a record in rows of bytes (fields as cards over their bytes), and optionally a ring of
slots under it.

Model::

    kind: bytes
    id: journal-layout
    title: ...
    alt: One sentence.
    reads: Two or more sentences.
    row_bytes: 8                # bytes per row
    size: 32                    # record size in bytes
    fields:
      - {at: 0, len: 2, name: magic, note: "0x4A4B", tone: slate}      # short: label on narrow cells
    ring:                       # optional
      title: "Ring of slots: the newest record is 5, the next append overwrites slot 6"
      slots: 8
      newest: 5
      next: 6
"""

from __future__ import annotations

from ..core import PROFILES
from ._common import Check, check_header, make_fig

REQUIRED = {"fields", "size"}
ALLOWED = {"row_bytes", "ring", "cell_width"}
ROWH = 82.0


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "bytes", REQUIRED, ALLOWED)
    size = model.get("size", 0)
    covered = [0] * (size if isinstance(size, int) and size > 0 else 0)
    for i, fld in enumerate(model.get("fields") or []):
        p = f"fields[{i}]"
        if not c.keys(fld, p, {"at", "len", "name"}, {"note", "tone", "short"}):
            continue
        c.tone(fld, p)
        if fld["at"] < 0 or fld["len"] < 1 or fld["at"] + fld["len"] > len(covered):
            c.bad(f"{p}: bytes {fld['at']}..{fld['at'] + fld['len'] - 1} are outside the {len(covered)} byte record")
            continue
        for b in range(fld["at"], fld["at"] + fld["len"]):
            covered[b] += 1
    for b, n in enumerate(covered):
        if n != 1:
            c.bad(f"byte {b} is covered by {n} fields (each byte belongs to exactly one field)")
            break
    rb = model.get("row_bytes", 8)
    if not isinstance(rb, int) or rb < 1 or (isinstance(size, int) and size % rb):
        c.bad("row_bytes: must divide size")
    ring = model.get("ring")
    if ring is not None and c.keys(ring, "ring", {"slots"}, {"title", "newest", "next"}):
        for key in ("newest", "next"):
            if key in ring and not 0 <= ring[key] < ring["slots"]:
                c.bad(f"ring.{key}: outside the slots")
    c.done()


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    k = PROFILES[model.get("profile", "detail")]
    rb = int(model.get("row_bytes", 8))
    size = int(model["size"])
    cell = float(model.get("cell_width", 100))
    x0 = 60.0
    ring_n = int((model.get("ring") or {}).get("slots", 0))
    width = int(max(x0 + rb * cell, ring_n * 118 + 16) + 64 + 16)
    f = make_fig(model, "bytes", width)
    for b in range(rb):
        f.text(x0 + b * cell + cell / 2, 10, str(b), size=k["small"], color="muted", anchor="middle")
    rows = size // rb
    for r in range(rows):
        f.text(x0 - 12, r * ROWH + 50, f"{r * rb}", size=k["small"], color="muted", anchor="end")
    for fld in sorted(model["fields"], key=lambda q: q["at"]):
        at, ln = fld["at"], fld["len"]
        tone = fld.get("tone", "slate")
        first = True
        while ln > 0:
            row, col = divmod(at, rb)
            take = min(ln, rb - col)
            w = take * cell - 6
            title = str(fld.get("short", fld["name"])) if take * cell <= 130 else str(fld["name"])
            note = [str(fld["note"])] if fld.get("note") and take * cell > 130 else []
            f.card(x0 + col * cell, 22 + row * ROWH, w, title if first else title + " (cont.)" if take * cell > 130 else title,
                   note, tone=tone, h=ROWH - 8, accent=True, center=True)
            first = False
            at, ln = at + take, ln - take
    ring = model.get("ring")
    if ring:
        y0 = 22 + rows * ROWH + 34
        if ring.get("title"):
            f.text(0, y0, str(ring["title"]), size=k["card_title"] - 1, weight=700, color="ink")
        n = int(ring["slots"])
        sw = min(118.0, (f.body_w - 16) / n)
        for i in range(n):
            tone = "green" if i == ring.get("newest") else "rose" if i == ring.get("next") else "slate"
            lab = "newest" if i == ring.get("newest") else "next write" if i == ring.get("next") else "older"
            f.card(8 + i * sw, y0 + 18, sw - 10, f"slot {i}", [lab], tone=tone, h=72, accent=tone != "slate", center=True)
        if "newest" in ring and "next" in ring and ring["next"] == ring["newest"] + 1:
            f.edge([(8 + ring["newest"] * sw + sw - 10 + 4, y0 + 54), (8 + ring["next"] * sw - 4, y0 + 54)], tone="green")
    f.twin = {"caption": f.title, "head": ["Bytes", "Field", "Note"],
              "rows": [[f"{q['at']}" if q["len"] == 1 else f"{q['at']}..{q['at'] + q['len'] - 1}", str(q["name"]),
                        str(q.get("note", ""))] for q in sorted(model["fields"], key=lambda q: q["at"])]}
    return f
