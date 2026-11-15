"""Shared by the figure kinds: model checking, the figure header, and the layered layout step."""

from __future__ import annotations

from .. import layered
from ..core import PROFILES, Fig, card_size, text_width

#: Keys every model may carry.
COMMON = {"kind", "id", "title", "alt", "reads", "kicker", "subtitle", "width", "profile", "print", "legend",
          "sources", "font"}
TONES = ("brand", "blue", "teal", "violet", "amber", "rose", "green", "slate", "magenta", "brown", "stone", "ok",
         "warn", "fail", "na", "planned")


class ModelError(SystemExit):
    """A model file that does not follow its kind's schema. Raised with every problem found, one per line."""

    def __init__(self, where: str, problems: list[str]):
        super().__init__(f"[figkit] {where}: " + f"\n[figkit] {where}: ".join(problems))


class Check:
    """Collects schema problems of one model; ``done()`` raises when there are any."""

    def __init__(self, where: str, model):
        self.where, self.problems, self.model = where, [], model

    def bad(self, msg: str) -> None:
        self.problems.append(msg)

    def keys(self, obj, path: str, required: set, allowed: set) -> bool:
        if not isinstance(obj, dict):
            self.bad(f"{path}: must be a mapping")
            return False
        for k in sorted(required - set(obj)):
            self.bad(f"{path}: missing {k!r}")
        for k in sorted(set(obj) - allowed - required):
            self.bad(f"{path}: unknown key {k!r} (allowed: {', '.join(sorted(allowed | required))})")
        return not (required - set(obj))

    def tone(self, obj, path: str, key: str = "tone", default: str = "slate") -> str:
        t = obj.get(key, default)
        if t not in TONES:
            self.bad(f"{path}.{key}: unknown tone {t!r}")
            return default
        return t

    def text(self, obj, path: str, key: str, required: bool = False) -> str:
        v = obj.get(key, "")
        if v is None:
            v = ""
        if not isinstance(v, (str, int, float)) or isinstance(v, bool):
            self.bad(f"{path}.{key}: must be text")
            return ""
        if required and not str(v).strip():
            self.bad(f"{path}.{key}: must not be empty")
        return str(v)

    def done(self) -> None:
        if self.problems:
            raise ModelError(self.where, self.problems)


def check_header(c: Check, model: dict, kind: str, extra_required: set, extra_allowed: set) -> None:
    c.keys(model, "model", {"kind", "id", "title", "alt"} | extra_required, COMMON | extra_allowed)
    if model.get("kind") != kind:
        c.bad(f"model.kind: must be {kind!r}")
    fid = str(model.get("id", ""))
    if not fid or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in fid):
        c.bad("model.id: lower case letters, digits and '-' only")
    if model.get("print") not in (None, "portrait", "landscape"):
        c.bad("model.print: portrait or landscape")
    if model.get("font") not in (None, "", "embed"):
        c.bad("model.font: 'embed' or leave out")
    if model.get("profile", "detail") not in PROFILES:
        c.bad(f"model.profile: one of {', '.join(PROFILES)}")


def make_fig(model: dict, kind: str, width: int, names=(), default_print: str = "landscape", **kw) -> Fig:
    """The figure header of a model: title, alt, kicker, legend, print mode, palette 2, adaptive output."""
    legend = []
    for item in model.get("legend", []) or []:
        if isinstance(item, dict):
            legend.append((item["tone"], item["label"]))
        else:
            legend.append((item[0], item[1]))
    f = Fig(
        model["id"], model["title"], alt=" ".join(str(model["alt"]).split()),
        width=max(int(model.get("width", 0) or 0), int(width)), kicker=str(model.get("kicker", "") or ""),
        subtitle=str(model.get("subtitle", "") or ""), profile=model.get("profile", "detail"), legend=legend,
        palette=2, print_mode=model.get("print", default_print), adaptive=True, kind=kind,
        reads=" ".join(str(model.get("reads", "") or "").split()), names=list(names),
        font=model.get("font", "") or "", **kw,
    )
    return f


# ------------------------------------------------------------------------------------------ layered layout step


def label_box(k: dict, text: str) -> tuple[float, float]:
    return (round(text_width(text, k["edge_label"], 500)) + 12, k["edge_label"] + 8)


def layered_layout(fid: str, profile: str, nodes: list[dict], edges: list[dict], direction: str, lock_dir,
                   same_rank=(), nodesep: float = 56.0):
    """Lay out cards with the lock. ``nodes``: dicts with ``id``, ``w``, ``h`` (card size) and optional ``room``
    (extra room kept clear on each side, for a self loop). ``edges``: dicts with ``from``, ``to``, ``label``.

    Returns ``(lock, cards, rlist)`` with ``cards = {id: (x, y, w, h)}`` and ``rlist`` the edge list given to
    ``layered.route`` (so the caller can pair it with the routes).
    """
    k = PROFILES[profile]
    spec = {
        "direction": direction, "nodesep": nodesep,
        "nodes": [[n["id"], [n["w"] + 2 * n.get("room", 0), n["h"]]] for n in nodes],
        "edges": [[e["from"], e["to"]] for e in edges if e["from"] != e["to"]],
        "same_rank": [list(g) for g in same_rank],
    }
    label_h = {}
    j = 0
    for e in edges:
        if e["from"] == e["to"]:
            continue
        if e.get("label"):
            label_h[j] = label_box(k, e["label"])[1 if direction == "TB" else 0]
        j += 1
    lock = layered.get_layout(fid, spec, label_h, lock_dir)
    size = {n["id"]: (n["w"], n["h"], n.get("room", 0)) for n in nodes}
    cards = {}
    for nid, (x, y, w, h) in lock["nodes"].items():
        cw, ch, room = size[nid]
        cards[nid] = (x + (w - cw) / 2, y + (h - ch) / 2, cw, ch)
    by_pair: dict[tuple, list] = {}
    for le in lock["edges"]:  # dot may list edges in another order: match by (from, to), keeping order within a pair
        by_pair.setdefault((le["from"], le["to"]), []).append(le["via"])
    rlist = []
    for e in edges:
        if e["from"] == e["to"]:
            rlist.append({"from": e["from"], "to": e["to"], "via": []})
        else:
            pool = by_pair.get((e["from"], e["to"]))
            if not pool:
                raise layered.LayoutStale(f"{fid}: layout lock edges do not match the model; re-run figkit layout")
            rlist.append({"from": e["from"], "to": e["to"], "via": pool.pop(0)})
    return lock, cards, rlist


def route_edges(fid: str, profile: str, lock: dict, cards: dict, rlist: list[dict], edges: list[dict], problem):
    k = PROFILES[profile]
    lsz = {i: label_box(k, e["label"]) for i, e in enumerate(edges) if e.get("label")}
    return layered.route(fid, lock, cards, rlist, lsz, problem)


__all__ = ["Check", "ModelError", "card_size", "check_header", "layered_layout", "make_fig", "route_edges"]
