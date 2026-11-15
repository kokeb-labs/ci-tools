"""``graph``: a layered graph of cards and arrows (layers, zones, components). Same layout machinery as ``state``.

Model::

    kind: graph
    id: layers-zones
    title: Include zones
    alt: One sentence.
    reads: Two or more sentences.
    direction: TB            # or LR
    reduce: true             # optional: drop an arrow implied by a longer path (the rule it shows still holds)
    node_width: 190          # optional
    nodes:
      - {id: utils, label: utils, tone: blue, lines: ["2 path globs"], tag: sdk, accent: true}
    edges:
      - {from: rtos, to: utils, label: may include, dashed: false}
"""

from __future__ import annotations

import math

from .. import layered
from ..core import PROFILES, card_size, text_width
from ._common import Check, check_header, layered_layout, make_fig, route_edges

REQUIRED = {"nodes", "edges"}
ALLOWED = {"direction", "reduce", "node_width", "same_rank"}


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "graph", REQUIRED, ALLOWED)
    if model.get("direction", "TB") not in ("TB", "LR"):
        c.bad("model.direction: TB or LR")
    ids = []
    for i, n in enumerate(model.get("nodes") or []):
        p = f"nodes[{i}]"
        if c.keys(n, p, {"id"}, {"label", "tone", "lines", "tag", "accent", "sub"}):
            c.tone(n, p)
            ids.append(str(n["id"]))
            if not isinstance(n.get("lines", []), list):
                c.bad(f"{p}.lines: must be a list")
    if len(set(ids)) != len(ids):
        c.bad("nodes: duplicate id")
    for i, e in enumerate(model.get("edges") or []):
        p = f"edges[{i}]"
        if c.keys(e, p, {"from", "to"}, {"label", "dashed", "tone"}):
            for end in ("from", "to"):
                if str(e[end]) not in ids:
                    c.bad(f"{p}.{end}: unknown node {e[end]!r}")
    for g in model.get("same_rank", []) or []:
        for n in g:
            if str(n) not in ids:
                c.bad(f"same_rank: unknown node {n!r}")
    c.done()


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    fid, prof = model["id"], model.get("profile", "detail")
    k = PROFILES[prof]
    direction = model.get("direction", "TB")
    edges = [(str(e["from"]), str(e["to"])) for e in model["edges"]]
    meta = {(str(e["from"]), str(e["to"])): e for e in model["edges"]}
    if model.get("reduce"):
        keep = set(layered.transitive_reduction(sorted(set(edges))))
        edges = [e for e in edges if e in keep]
    trans = []
    for a, b in edges:
        e = meta[(a, b)]
        trans.append({"from": a, "to": b, "label": str(e.get("label", "") or ""), "dashed": bool(e.get("dashed")),
                      "tone": e.get("tone")})
    nw = int(model.get("node_width", 190))
    nodes = []
    for n in model["nodes"]:
        title = str(n.get("label", n["id"]))
        tag = str(n.get("tag", "") or "")
        lines = [str(x) for x in n.get("lines", [])]
        w = max(nw, math.ceil(text_width(title, k["card_title"], 700) + 2 * k["pad"] + 6 + (text_width(tag, k["pill"], 700) + 24 if tag else 0)))
        h = card_size(k, w, title, lines, sub=str(n.get("sub", "") or ""), tag=tag)
        lw = max([text_width(t["label"], k["edge_label"], 500) + 12 for t in trans if t["from"] == t["to"] == str(n["id"]) and t["label"]], default=0)
        nodes.append({"id": str(n["id"]), "w": w, "h": h, "room": math.ceil(layered.LOOP_OUT + 18 + lw) if any(t["from"] == t["to"] == str(n["id"]) for t in trans) else 0})
    lock, cards, rlist = layered_layout(fid, prof, nodes, trans, direction, lock_dir, model.get("same_rank") or ())
    f = make_fig(model, "graph", max(640, int(lock["size"][0] + 64 + 16 + 100)))
    ox = max(0.0, (f.body_w - lock["size"][0]) / 2)
    routes = route_edges(fid, prof, lock, cards, rlist, trans, f.problem)
    for n in model["nodes"]:
        x, y, w, h = cards[str(n["id"])]
        f.card(x + ox, y, w, str(n.get("label", n["id"])), [str(v) for v in n.get("lines", [])], tone=n.get("tone", "slate"),
               h=h, sub=str(n.get("sub", "") or ""), tag=str(n.get("tag", "") or ""), accent=bool(n.get("accent")))
    for t, r in zip(trans, routes):
        f.edge([(px + ox, py) for px, py in r.points], tone=t["tone"] or "rail", dashed=t["dashed"])
        if t["label"] and r.label_at:
            f.edge_label(r.label_at[0] + ox, r.label_at[1], t["label"])
    return f
