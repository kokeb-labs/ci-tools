"""Layered layout for the ``state`` and ``graph`` kinds: Graphviz as a build-time oracle, a committed lock, and
orthogonal routes drawn by figkit.

How the pieces fit:

* ``spec`` is what the layout depends on: the node sizes, the edges (in order), the direction, the spacing and the
  same-rank groups. Its SHA-256 is the *input hash*.
* ``kokeb-docs figkit layout`` is the only code that runs Graphviz ``dot``. It writes ``<id>.layout.json`` next to the
  figure: node boxes and the waypoints dot chose for each edge, as whole pixels, with the input hash. The lock records
  the dot version for the reader; nothing reads it back, so a Graphviz upgrade changes a figure only when somebody
  re-runs ``figkit layout`` and commits the new lock.
* A normal render (``kokeb-docs figures``) reads the lock. A missing lock or a different input hash is an error that
  says to run ``figkit layout``; dot is not called, so the bytes depend on Python and figkit only.
* ``route()`` turns the waypoints into orthogonal routes (vertical and horizontal runs with rounded corners) with a
  separate slot for every run in a gutter, spread ports on a card side, and a proper loop for a self-edge.

Internally the router works in ``(c, m)`` coordinates: ``m`` runs along the rank direction (down for ``TB``, right for
``LR``) and ``c`` across it. ``to_xy`` maps back.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import math
import pathlib
import re
import shutil
import subprocess
from dataclasses import dataclass, field

LOCK_VERSION = 1
BASE_GUTTER = 46.0  # smallest room between two ranks, px
LOOP_OUT = 26.0  # how far a self loop leaves its card, px
LOOP_LABEL_GAP = 8.0


class LayoutStale(Exception):
    """The layout lock is missing or was made from different inputs."""


# ---------------------------------------------------------------------------------------------------- the lock


def input_hash(spec: dict) -> str:
    return hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def lock_path(lock_dir: pathlib.Path, fid: str) -> pathlib.Path:
    return pathlib.Path(lock_dir) / f"{fid}.layout.json"


@dataclass
class _Mode:
    mode: str = "use"  # use | refresh | compare
    ids: set | None = None
    diffs: list = field(default_factory=list)


_MODE = _Mode()


@contextlib.contextmanager
def layout_mode(mode: str, ids=None):
    """``refresh``: run dot and write the locks (of ``ids``, or all); ``compare``: run dot and record where it would
    change a lock (``diffs()``); ``use`` (default): read the lock, never run dot."""
    global _MODE
    old, _MODE = _MODE, _Mode(mode, set(ids) if ids else None)
    try:
        yield _MODE
    finally:
        _MODE = old


def dot_path() -> str:
    exe = shutil.which("dot")
    if not exe:
        raise SystemExit("figkit layout: Graphviz `dot` is not installed (it is only needed to make or check a layout "
                         "lock, never to render)")
    return exe


def dot_version() -> str:
    out = subprocess.run([dot_path(), "-V"], capture_output=True, text=True, check=True)
    m = re.search(r"version (\d+(?:\.\d+)*)", out.stdout + out.stderr)
    return m.group(1) if m else "unknown"


def _dot_source(spec: dict, ranksep: float) -> str:
    rd = spec["direction"]
    lines = ["digraph G {", f"rankdir={rd}; splines=polyline; ranksep={ranksep / 72:.4f}; "
                            f"nodesep={spec['nodesep'] / 72:.4f};",
             'node [shape=box, fixedsize=true, label=""];']
    for n, (w, h) in spec["nodes"]:
        lines.append(f'"{n}" [width={w / 72:.4f}, height={h / 72:.4f}];')
    for a, b in spec["edges"]:
        lines.append(f'"{a}" -> "{b}";')
    for grp in spec.get("same_rank", []):
        lines.append("{rank=same; " + "; ".join(f'"{n}"' for n in grp) + "}")
    lines.append("}")
    return "\n".join(lines)


def _run_dot(spec: dict, ranksep: float) -> dict:
    out = subprocess.run([dot_path(), "-Tjson"], input=_dot_source(spec, ranksep), capture_output=True, text=True,
                         check=True).stdout
    g = json.loads(out)
    height = float(g["bb"].split(",")[3])
    width = float(g["bb"].split(",")[2])
    size = {n: (w, h) for n, (w, h) in spec["nodes"]}
    names = {i: o["name"] for i, o in enumerate(g["objects"])}
    nodes = {}
    for o in g["objects"]:
        if "pos" in o and o["name"] in size:
            cx, cy = (float(v) for v in o["pos"].split(","))
            w, h = size[o["name"]]
            nodes[o["name"]] = [round(cx - w / 2), round(height - cy - h / 2), w, h]
    edges = []
    for e in g.get("edges", []):
        raw = next((op["points"] for op in e.get("_draw_", []) if op["op"] == "b"), [])
        pts = raw[::3] if len(raw) % 3 == 1 else raw
        via = [[round(x), round(height - y)] for x, y in pts[1:-1]]
        edges.append({"from": names[e["tail"]], "to": names[e["head"]], "via": via})
    return {"nodes": nodes, "edges": edges, "size": [round(width), round(height)]}


def _ranks_of(nodes: dict, direction: str) -> list[list[str]]:
    """Nodes grouped by rank (equal centre on the rank axis), in rank order."""
    key = (lambda b: b[1] + b[3] / 2) if direction == "TB" else (lambda b: b[0] + b[2] / 2)
    groups: dict[int, list[str]] = {}
    for n, b in nodes.items():
        groups.setdefault(round(key(b)), []).append(n)
    return [sorted(groups[k]) for k in sorted(groups)]


def gutter_need(spec: dict, nodes: dict, label_h: dict) -> float:
    """Room the busiest gutter needs, given the ranks in ``nodes``: one slot per edge run, wider when labelled."""
    ranks = _ranks_of(nodes, spec["direction"])
    rank_of = {n: i for i, r in enumerate(ranks) for n in r}
    users: dict[int, list[float]] = {}  # gutter -> label heights of the runs there (0: none)
    for i, (a, b) in enumerate(spec["edges"]):
        if a == b or a not in rank_of or b not in rank_of:
            continue
        ra, rb = rank_of[a], rank_of[b]
        lo, hi = (ra, rb) if ra <= rb else (rb, ra)
        gutters = list(range(lo, hi)) if lo != hi else [lo - 1]
        first = gutters[0] if ra <= rb else gutters[-1]  # the label sits in the first gutter of the edge
        for g in gutters:
            users.setdefault(g, []).append(label_h.get(i, 0.0) if g == first else 0.0)
    need = BASE_GUTTER
    for g, hs in users.items():
        lab = [h for h in hs if h]
        need = max(need, len(lab) * (max(lab) + 8) + (len(hs) - len(lab) + 1) * 10 if lab else (len(hs) + 1) * 10)
    return math.ceil(need)


def make_lock(fid: str, spec: dict, label_h: dict) -> dict:
    """Run dot (twice: the second time with the gutters sized for the edge runs of the first) and return the lock."""
    sep = BASE_GUTTER
    res = _run_dot(spec, sep)
    for _ in range(4):  # the ranks can change when the gutters grow: size them until the busiest gutter fits
        need = float(gutter_need(spec, res["nodes"], label_h))
        if need <= sep:
            break
        sep = math.ceil(need * 1.05)
        res = _run_dot(spec, sep)
    return {
        "figkit_layout": LOCK_VERSION,
        "id": fid,
        "input": input_hash(spec),
        "engine": f"graphviz dot {dot_version()} (recorded for the reader; render never reads it)",
        "direction": spec["direction"],
        "size": res["size"],
        "nodes": res["nodes"],
        "edges": res["edges"],
    }


def dump_lock(lock: dict) -> str:
    return json.dumps(lock, indent=1, sort_keys=True) + "\n"


def get_layout(fid: str, spec: dict, label_h: dict, lock_dir) -> dict:
    """The layout lock of figure ``fid`` for ``spec``. Never runs dot unless ``layout_mode`` says so."""
    path = lock_path(lock_dir, fid)
    want = input_hash(spec)
    mode = _MODE.mode
    active = mode != "use" and (_MODE.ids is None or fid in _MODE.ids)
    if active:
        lock = make_lock(fid, spec, label_h)
        old = json.loads(path.read_text()) if path.is_file() else None
        if mode == "refresh":
            if old is None or dump_lock(old) != dump_lock(lock):
                path.parent.mkdir(parents=True, exist_ok=True)
                # Keep the recorded engine line when nothing but it differs, so a Graphviz patch level alone never
                # shows up as a diff.
                if old is not None and {k: v for k, v in old.items() if k != "engine"} == \
                        {k: v for k, v in lock.items() if k != "engine"}:
                    return old
                path.write_text(dump_lock(lock))
                _MODE.diffs.append((fid, "written"))
            return lock
        if old is None:
            _MODE.diffs.append((fid, "no lock"))
        elif {k: v for k, v in old.items() if k != "engine"} != {k: v for k, v in lock.items() if k != "engine"}:
            _MODE.diffs.append((fid, f"dot {dot_version()} would change the lock"))
        return old if old is not None else lock
    if not path.is_file():
        raise LayoutStale(f"{fid}: no layout lock at {path}; run `kokeb-docs figkit layout {fid}` and commit it")
    lock = json.loads(path.read_text())
    if lock.get("figkit_layout") != LOCK_VERSION or lock.get("input") != want:
        raise LayoutStale(f"{fid}: layout stale (the figure's nodes, edges or sizes changed since {path.name} was "
                          f"made); run `kokeb-docs figkit layout {fid}` and commit the lock")
    return lock


# ---------------------------------------------------------------------------------------------------- routing


@dataclass
class Route:
    points: list  # [(x, y)] in lock coordinates
    label_at: tuple | None = None  # centre of the label
    loop: bool = False


def _mk(direction: str):
    """(to_cm, to_xy) for a direction."""
    if direction == "TB":
        return (lambda x, y: (x, y)), (lambda c, m: (c, m))
    return (lambda x, y: (y, x)), (lambda c, m: (m, c))


def route(fid: str, lock: dict, cards: dict, edges: list[dict], label_size: dict, problem) -> list[Route]:
    """Routes for ``edges`` (dicts with ``from``, ``to`` in lock order) over ``cards`` ({id: (x, y, w, h)} drawn
    boxes). ``label_size`` maps an edge index to (w, h). ``problem(msg)`` reports what does not fit."""
    d = lock["direction"]
    to_cm, to_xy = _mk(d)

    lm = lambda i: label_size[i][1] if d == "TB" else label_size[i][0]  # noqa: E731

    def box(n):
        x, y, w, h = cards[n]
        c0, m0 = to_cm(x, y)
        c1, m1 = to_cm(x + w, y + h)
        return (min(c0, c1), min(m0, m1), max(c0, c1), max(m0, m1))  # c0, m0, c1, m1

    lock_nodes = lock["nodes"]
    ranks = _ranks_of(lock_nodes, d)
    rank_of = {n: i for i, r in enumerate(ranks) for n in r}
    rtop = [min(box(n)[1] for n in r) for r in ranks]
    rbot = [max(box(n)[3] for n in r) for r in ranks]
    rmid = [sum((box(n)[1] + box(n)[3]) / 2 for n in r) / len(r) for r in ranks]

    # 1. classify
    kind: dict[int, str] = {}
    for i, e in enumerate(edges):
        a, b = e["from"], e["to"]
        ra, rb = rank_of[a], rank_of[b]
        kind[i] = "loop" if a == b else "fwd" if rb > ra else "back" if rb < ra else "same"

    # 2. waypoints per edge: the cross coordinate in every rank strictly between
    def waypoints(i: int) -> list[float]:
        e = edges[i]
        ra, rb = rank_of[e["from"]], rank_of[e["to"]]
        lo, hi = min(ra, rb), max(ra, rb)
        via = [to_cm(x, y) for x, y in e.get("via", [])]
        if ra > rb:
            via = via[::-1]
        out = []
        ca, cb = (box(e["from"])[0] + box(e["from"])[2]) / 2, (box(e["to"])[0] + box(e["to"])[2]) / 2
        for k in range(lo + 1, hi):
            best = min(via, key=lambda p: abs(p[1] - rmid[k]), default=None)
            if best is not None and abs(best[1] - rmid[k]) < max(60, (rbot[k] - rtop[k])):
                out.append(best[0])
            else:
                out.append(ca + (cb - ca) * (k - lo) / (hi - lo))
        return out if ra < rb else out[::-1]

    # Lanes: where long edges cross a rank. Keep them off the cards and at least LANE px apart.
    LANE = 14.0
    raw_wp = {i: waypoints(i) for i in range(len(edges)) if kind[i] in ("fwd", "back")}
    for k in range(len(ranks)):
        items = []  # (c, edge index, position in that edge's waypoint list)
        for i, wp in raw_wp.items():
            ra, rb = rank_of[edges[i]["from"]], rank_of[edges[i]["to"]]
            lo, hi = min(ra, rb), max(ra, rb)
            if lo < k < hi:
                idx = k - lo - 1 if ra < rb else hi - k - 1
                items.append((wp[idx], i, idx))
        items.sort()
        spans = sorted((box(n)[0] - 10, box(n)[2] + 10) for n in ranks[k])
        placed = []
        for c, i, idx in items:
            for lo_c, hi_c in spans:
                if lo_c < c < hi_c:
                    c = lo_c if c - lo_c < hi_c - c else hi_c
            if placed and c < placed[-1] + LANE:
                c = placed[-1] + LANE
            placed.append(c)
            raw_wp[i][idx] = c
    waypoints = lambda i: raw_wp[i]  # noqa: E731

    # 3. ports: spread the edge ends along a card side, ordered by where the edge goes
    ends: dict[tuple, list] = {}  # (node, side) -> [(sort key, edge index, role)]

    def neighbour_c(i, role):
        e = edges[i]
        wp = waypoints(i) if kind[i] in ("fwd", "back") else []
        if kind[i] in ("fwd", "back"):
            if role == "tail":
                return wp[0] if wp else (box(e["to"])[0] + box(e["to"])[2]) / 2
            return wp[-1] if wp else (box(e["from"])[0] + box(e["from"])[2]) / 2
        other = e["to"] if role == "tail" else e["from"]
        return (box(other)[0] + box(other)[2]) / 2

    side_of: dict[tuple, str] = {}
    for i, e in enumerate(edges):
        k = kind[i]
        if k == "loop":
            continue
        if k == "fwd":
            tail_side, head_side = "m1", "m0"
        elif k == "back":
            tail_side, head_side = "m0", "m1"
        else:  # same rank
            a, b = box(e["from"]), box(e["to"])
            if _adjacent(e["from"], e["to"], ranks, rank_of, box):
                tail_side, head_side = ("c1", "c0") if a[2] <= b[0] else ("c0", "c1")
            else:
                tail_side = head_side = "m0"
        side_of[(i, "tail")], side_of[(i, "head")] = tail_side, head_side
        ends.setdefault((e["from"], tail_side), []).append((neighbour_c(i, "tail"), i, "tail"))
        ends.setdefault((e["to"], head_side), []).append((neighbour_c(i, "head"), i, "head"))
    port: dict[tuple, float] = {}  # (edge index, role) -> position along the side
    for (n, side), lst in sorted(ends.items()):
        b = box(n)
        lo, hi = (b[0], b[2]) if side.startswith("m") else (b[1], b[3])
        margin = min(14.0, (hi - lo) / 4)
        lo, hi = lo + margin, hi - margin
        lst.sort()
        for j, (_k, i, role) in enumerate(lst):
            port[(i, role)] = (lo + hi) / 2 if len(lst) == 1 else lo + (hi - lo) * j / (len(lst) - 1)

    # 4. gutter slots
    runs: dict[int, list[int]] = {}  # gutter index (between rank g and g+1) -> edge indices with a run there
    for i, e in enumerate(edges):
        ra, rb = rank_of[e["from"]], rank_of[e["to"]]
        if kind[i] in ("fwd", "back"):
            for g in range(min(ra, rb), max(ra, rb)):
                runs.setdefault(g, []).append(i)
        elif kind[i] == "same" and side_of[(i, "tail")] == "m0":
            runs.setdefault(ra - 1, []).append(i)
    slot_m: dict[tuple, float] = {}
    for g, lst in runs.items():
        lo = rbot[g] if g >= 0 else rtop[0] - 3 * BASE_GUTTER / 2
        hi = rtop[g + 1] if g + 1 < len(ranks) else rbot[g] + BASE_GUTTER
        lst.sort(key=lambda i: (port.get((i, "tail"), 0.0), i))
        first_of = lambda i: (g == (rank_of[edges[i]["from"]] - (1 if kind[i] == "back" else 0))) if kind[i] != "same" else True
        has_label = {i: (i in label_size and first_of(i)) for i in lst}
        lh = max([lm(i) for i in lst if has_label[i]], default=0)
        weights = [(lh + 8) if has_label[i] else 10 for i in lst]
        total = sum(weights) + 10
        scale = (hi - lo) / total
        if scale < 0.98:
            problem(f"gutter {g} between ranks is {hi - lo:.0f} px but its runs need {total:.0f} px; "
                    f"run `kokeb-docs figkit layout {fid}`")
        cum = 5.0
        for j, i in enumerate(lst):
            slot_m[(i, g)] = lo + scale * (cum + weights[j] / 2)
            cum += weights[j]

    # 5. build routes
    loops_on: dict[str, int] = {}
    out: list[Route] = []
    for i, e in enumerate(edges):
        a, b = e["from"], e["to"]
        ba, bb = box(a), box(b)
        k = kind[i]
        gap = 4.0
        lw, lh = label_size.get(i, (0, 0))
        if k == "loop":
            n = loops_on.get(a, 0)
            loops_on[a] = n + 1
            sgn = 1 if n % 2 == 0 else -1
            cside = ba[2] if sgn > 0 else ba[0]
            mid = (ba[1] + ba[3]) / 2
            dm = min((ba[3] - ba[1]) / 4, 12.0)
            cc = cside + sgn * LOOP_OUT
            pts_cm = [(cside + sgn * gap, mid - dm), (cc, mid - dm), (cc, mid + dm), (cside + sgn * gap, mid + dm)]
            lab = (cc + sgn * (LOOP_LABEL_GAP + lw / 2), mid) if lw else None
            out.append(Route([to_xy(c, m) for c, m in pts_cm], to_xy(*lab) if lab else None, True))
            continue
        cs, ce = port[(i, "tail")], port[(i, "head")]
        ts, te = side_of[(i, "tail")], side_of[(i, "head")]
        wp = waypoints(i) if k in ("fwd", "back") else []
        pts: list[tuple[float, float]] = []
        label_pos = None
        if k in ("fwd", "back"):
            sgn = 1 if k == "fwd" else -1
            ra, rb = rank_of[a], rank_of[b]
            start_m = (ba[3] + gap) if sgn > 0 else (ba[1] - gap)
            end_m = (bb[1] - gap) if sgn > 0 else (bb[3] + gap)
            cs_list = [cs] + wp + [ce]
            gl = list(range(ra, rb)) if sgn > 0 else list(range(ra - 1, rb - 1, -1))
            pts.append((cs, start_m))
            cur_c = cs
            for step, g in enumerate(gl):
                nxt = cs_list[step + 1]
                sm = slot_m[(i, g)]
                if abs(nxt - cur_c) > 0.5:
                    pts.append((cur_c, sm))
                    pts.append((nxt, sm))
                    if label_pos is None and lw:
                        label_pos = ((cur_c + nxt) / 2, sm) if abs(nxt - cur_c) >= lw * 0.6 + 8 else \
                            (max(cur_c, nxt) + 8 + lw / 2, sm)
                elif label_pos is None and lw:
                    label_pos = (cur_c + 8 + lw / 2, sm)
                cur_c = nxt
            pts.append((ce, end_m))
        else:  # same rank
            if ts.startswith("c"):  # side to side
                cstart = (ba[2] + gap) if ts == "c1" else (ba[0] - gap)
                cend = (bb[0] - gap) if te == "c0" else (bb[2] + gap)
                pm = port[(i, "tail")]
                pe = port[(i, "head")]
                if abs(pm - pe) < 0.5:
                    pts = [(cstart, pm), (cend, pe)]
                else:
                    cmid = (cstart + cend) / 2
                    pts = [(cstart, pm), (cmid, pm), (cmid, pe), (cend, pe)]
                label_pos = ((cstart + cend) / 2, (pm + pe) / 2 - lh / 2 - 4) if lw else None
            else:  # over the top
                sm = slot_m[(i, rank_of[a] - 1)]
                pts = [(cs, ba[1] - gap), (cs, sm), (ce, sm), (ce, bb[1] - gap)]
                label_pos = ((cs + ce) / 2, sm) if lw else None
        out.append(Route([to_xy(c, m) for c, m in pts], to_xy(*label_pos) if label_pos else None))
    return out


def _adjacent(a: str, b: str, ranks, rank_of, box) -> bool:
    """True when no other card of the rank lies between ``a`` and ``b``."""
    ba, bb = box(a), box(b)
    lo, hi = sorted((ba[0] + ba[2], bb[0] + bb[2]))
    for n in ranks[rank_of[a]]:
        if n in (a, b):
            continue
        bn = box(n)
        if lo < bn[0] + bn[2] < hi:
            return False
    return True


def transitive_reduction(edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Drop A->C when A->B->...->C exists, keeping the picture legible; the rule it shows still holds."""
    out: dict[str, set] = {}
    for a, b in edges:
        out.setdefault(a, set()).add(b)

    def reach(src, skip):
        seen, todo = set(), sorted(t for t in out.get(src, ()) if (src, t) != skip)
        while todo:
            n = todo.pop()
            if n not in seen:
                seen.add(n)
                todo += sorted(out.get(n, ()))
        return seen

    return [e for e in edges if e[1] not in reach(e[0], e)]
