"""``state``: a state machine. States are cards, transitions are orthogonal arrows with labels, a self transition is a
loop on the side of its card, ``[*]`` is the initial (filled disc) or final (ringed disc) pseudo state.

Model::

    kind: state
    id: handler-health
    title: Handler lifecycle and health
    alt: One sentence saying what the figure shows.
    reads: Two or more sentences naming every state and the calls that move between them.
    direction: TB                       # or LR
    states:
      - {id: Unknown, tone: slate}       # label, note (one line under the name) are optional
    transitions:
      - {from: "[*]", to: Unknown, label: ctor}
      - {from: Unknown, to: Starting, label: Start()}   # dashed: true, tone: rose are optional
"""

from __future__ import annotations

import math

from ..core import PROFILES, card_size, text_width
from ._common import Check, check_header, layered_layout, make_fig, route_edges
from .. import layered

REQUIRED = {"states", "transitions"}
ALLOWED = {"direction"}
DISC = 22


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "state", REQUIRED, ALLOWED)
    if model.get("direction", "TB") not in ("TB", "LR"):
        c.bad("model.direction: TB or LR")
    ids = []
    for i, s in enumerate(model.get("states") or []):
        p = f"states[{i}]"
        if c.keys(s, p, {"id"}, {"label", "tone", "note"}):
            c.tone(s, p)
            ids.append(str(s["id"]))
    if len(set(ids)) != len(ids):
        c.bad(f"states: duplicate id(s) {sorted({i for i in ids if ids.count(i) > 1})}")
    for i, t in enumerate(model.get("transitions") or []):
        p = f"transitions[{i}]"
        if c.keys(t, p, {"from", "to"}, {"label", "dashed", "tone"}):
            for end in ("from", "to"):
                if str(t[end]) not in ids and str(t[end]) != "[*]":
                    c.bad(f"{p}.{end}: unknown state {t[end]!r}")
            if str(t["from"]) == "[*]" and str(t["to"]) == "[*]":
                c.bad(f"{p}: [*] to [*]")
            if "tone" in t:
                c.tone(t, p)
    c.done()


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    fid = model["id"]
    prof = model.get("profile", "detail")
    k = PROFILES[prof]
    direction = model.get("direction", "TB")
    states = {str(s["id"]): s for s in model["states"]}
    trans = []
    init_n = fin_n = 0
    for t in model["transitions"]:
        a, b = str(t["from"]), str(t["to"])
        if a == "[*]":
            a = f"@start{init_n}"
            init_n += 1
        if b == "[*]":
            b = f"@end{fin_n}"
            fin_n += 1
        trans.append({"from": a, "to": b, "label": str(t.get("label", "") or ""), "dashed": bool(t.get("dashed")),
                      "tone": t.get("tone")})
    loop_room = {}
    for t in trans:
        if t["from"] == t["to"]:
            lw = text_width(t["label"], k["edge_label"], 500) + 12 if t["label"] else 0
            loop_room[t["from"]] = max(loop_room.get(t["from"], 0), layered.LOOP_OUT + layered.LOOP_LABEL_GAP + lw + 10)
    nodes = []
    for sid, s in states.items():
        title = str(s.get("label", sid))
        note = [str(s["note"])] if s.get("note") else []
        w = max(150, math.ceil(text_width(title, k["card_title"], 700) + 2 * k["pad"] + 6 + 8))
        h = max(52, card_size(k, w, title, note))
        nodes.append({"id": sid, "w": w, "h": h, "room": math.ceil(loop_room.get(sid, 0))})
    for t in trans:
        for key in ("from", "to"):
            if t[key].startswith("@") and not any(n["id"] == t[key] for n in nodes):
                nodes.append({"id": t[key], "w": DISC, "h": DISC})
    lock, cards, rlist = layered_layout(fid, prof, nodes, trans, direction, lock_dir)
    lw_, lh_ = lock["size"]
    f = make_fig(model, "state", max(640, int(lw_ + 64 + 16 + 100)), names=[str(s.get("label", i)) for i, s in states.items()])
    ox = max(0.0, (f.body_w - lw_) / 2)
    routes = route_edges(fid, prof, lock, cards, rlist, trans, f.problem)
    for sid, s in states.items():
        x, y, w, h = cards[sid]
        title = str(s.get("label", sid))
        note = [str(s["note"])] if s.get("note") else []
        f.card(x + ox, y, w, title, note, tone=s.get("tone", "slate"), h=h, accent=True, center=True)
    for nid, (x, y, w, h) in cards.items():
        if nid.startswith("@start"):
            f.circle(x + ox + w / 2, y + h / 2, w / 2, fill="ink2", stroke=None)
        elif nid.startswith("@end"):
            f.circle(x + ox + w / 2, y + h / 2, w / 2 - 1, fill="canvas", stroke="ink2", sw=2)
            f.circle(x + ox + w / 2, y + h / 2, w / 2 - 6, fill="ink2", stroke=None)
    for t, r in zip(trans, routes):
        pts = [(px + ox, py) for px, py in r.points]
        f.edge(pts, tone=t["tone"] or "rail", dashed=t["dashed"])
        if t["label"] and r.label_at:
            f.edge_label(r.label_at[0] + ox, r.label_at[1], t["label"])
    return f
