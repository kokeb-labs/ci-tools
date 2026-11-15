"""``seq``: a sequence diagram. Participants are cards in a row with a dashed lifeline under each; steps run top to
bottom: a call (solid arrow), a return (dashed arrow), a call to self (a small loop), a note over some participants,
and a numbered step disc.

Model::

    kind: seq
    id: bus-access
    title: ...
    alt: One sentence.
    reads: Two or more sentences naming every participant.
    participants:
      - {id: caller, label: Caller, tone: blue}
    steps:
      - {from: caller, to: handler, label: Read(reg)}                    # call
      - {from: handler, to: caller, label: value, return: true}          # return (dashed)
      - {from: handler, to: handler, label: lock bus}                    # self call
      - {note: "Both locks held", over: [handler, bus]}                  # note over one or more participants
"""

from __future__ import annotations

from ..core import PROFILES, text_width
from ._common import Check, check_header, make_fig

REQUIRED = {"participants", "steps"}
ALLOWED = {"min_gap"}
ROW = 44.0


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "seq", REQUIRED, ALLOWED)
    ids = []
    for i, p_ in enumerate(model.get("participants") or []):
        p = f"participants[{i}]"
        if c.keys(p_, p, {"id"}, {"label", "tone", "sub"}):
            c.tone(p_, p)
            ids.append(str(p_["id"]))
    if len(set(ids)) != len(ids):
        c.bad("participants: duplicate id")
    for i, s in enumerate(model.get("steps") or []):
        p = f"steps[{i}]"
        if "note" in s:
            if c.keys(s, p, {"note", "over"}, {"tone"}):
                for o in s["over"]:
                    if str(o) not in ids:
                        c.bad(f"{p}.over: unknown participant {o!r}")
        elif c.keys(s, p, {"from", "to", "label"}, {"return", "dashed", "tone"}):
            for end in ("from", "to"):
                if str(s[end]) not in ids:
                    c.bad(f"{p}.{end}: unknown participant {s[end]!r}")
    c.done()


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    k = PROFILES[model.get("profile", "detail")]
    parts = model["participants"]
    idx = {str(p["id"]): i for i, p in enumerate(parts)}
    n = len(parts)
    min_gap = float(model.get("min_gap", 170))
    # Column centres: gaps between neighbours grow until every label that spans them fits.
    gaps = [min_gap] * (n - 1)
    lbl_w = lambda s: text_width(str(s), k["edge_label"], 500) + 28  # noqa: E731
    for s in model["steps"]:
        if "note" in s:
            continue
        a, b = sorted((idx[str(s["from"])], idx[str(s["to"])]))
        if a == b:
            continue
        need = lbl_w(s["label"])
        have = sum(gaps[a:b])
        if need > have:
            for g in range(a, b):
                gaps[g] += (need - have) / (b - a)
    card_w = [max(130, text_width(str(p.get("label", p["id"])), k["card_title"], 700) + 2 * k["pad"] + 14) for p in parts]
    for i in range(n - 1):
        gaps[i] = max(gaps[i], (card_w[i] + card_w[i + 1]) / 2 + 16)
    cx = [card_w[0] / 2]
    for g in gaps:
        cx.append(cx[-1] + g)
    extra_r = 0.0
    for s in model["steps"]:  # a self call hangs to the right of its lifeline
        if "note" not in s and s["from"] == s["to"]:
            i = idx[str(s["from"])]
            extra_r = max(extra_r, 34 + lbl_w(s["label"]) - (cx[-1] - cx[i]) if i == n - 1 else 0)
    width = int(cx[-1] + card_w[-1] / 2 + max(0, extra_r) + 64 + 16)
    f = make_fig(model, "seq", width, names=[str(p.get("label", p["id"])) for p in parts])
    x0 = max(0.0, (f.body_w - (cx[-1] + card_w[-1] / 2)) / 2)
    head_h = 52
    steps = model["steps"]
    # Rows: a note is taller when it wraps; keep it to one line (short text) for now.
    y = head_h + 40
    ys = []
    for s in steps:
        ys.append(y)
        y += ROW + (8 if "note" in s else 0)
    bottom = y
    for i, p in enumerate(parts):
        f.line([(x0 + cx[i], head_h + 4), (x0 + cx[i], bottom - 10)], color="line", sw=1.2, dash="5 5", layer="bg")
        f.card(x0 + cx[i] - card_w[i] / 2, 0, card_w[i], str(p.get("label", p["id"])), tone=p.get("tone", "slate"),
               h=head_h, accent=True, center=True)
    f.nontext("line", ("canvas",), "lifeline")
    for s, yy in zip(steps, ys):
        if "note" in s:
            xs = [x0 + cx[idx[str(o)]] for o in s["over"]]
            lo, hi = min(xs) - 70, max(xs) + 70
            f.note(lo, yy - 16, hi - lo, str(s["note"]), tone=s.get("tone", "amber"))
            continue
        a, b = x0 + cx[idx[str(s["from"])]], x0 + cx[idx[str(s["to"])]]
        dashed = bool(s.get("return") or s.get("dashed"))
        tone = s.get("tone") or "rail"
        if a == b:
            pts = [(a + 4, yy - 8), (a + 34, yy - 8), (a + 34, yy + 8), (a + 4, yy + 8)]
            f.edge(pts, tone=tone, dashed=dashed)
            f.edge_label(a + 34 + 10 + lbl_w(s["label"]) / 2 - 14, yy, str(s["label"]))
        else:
            sg = 1 if b > a else -1
            f.edge([(a + sg * 4, yy), (b - sg * 4, yy)], tone=tone, dashed=dashed)
            f.edge_label((a + b) / 2, yy - 14, str(s["label"]))
    return f
