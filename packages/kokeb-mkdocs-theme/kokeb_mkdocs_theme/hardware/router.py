"""An orthogonal wire router for schematic figures: A* on a grid, one net at a time.

The rules are those of a hand-drawn schematic:

* A wire never enters a part body or a text label (the cells under them are blocked).
* Two nets never share a run of wire; they may cross at right angles, and a crossing is never a bend, a pin or a
  junction, so a crossing cannot be read as a connection.
* A net is a tree. Each terminal after the first is routed to the nearest point of the tree already drawn; where
  it lands on a wire it makes a T, drawn with a junction dot. No point joins more than three wires (no four-way
  junctions, which read ambiguously).
* Bends and crossings cost extra, so the shortest clean route wins; equal routes are broken by a fixed order, so the
  same input always gives the same wires.

Cells are ``(i, j)`` on a grid of ``step`` pixels whose cell (0, 0) is at body coordinates ``(x0, y0)``. Each cell
records, per net, its *arms*: the sides (``R``, ``D``, ``L``, ``U``) a wire leaves it by.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

DIRS = {"R": (1, 0), "D": (0, 1), "L": (-1, 0), "U": (0, -1)}
OPP = {"R": "L", "L": "R", "U": "D", "D": "U"}
ORDER = ("R", "D", "L", "U")

BEND = 4.0
CROSS = 8.0
HUG = 0.5  # running right next to another net's wire


class RouteError(Exception):
    pass


@dataclass
class Grid:
    x0: float
    y0: float
    cols: int
    rows: int
    step: float
    blocked: set = field(default_factory=set)
    arms: dict = field(default_factory=dict)  # cell -> {net: set(arms)}
    terminals: dict = field(default_factory=dict)  # cell -> net (pin ends: never crossed)
    pinside: dict = field(default_factory=dict)  # cell -> the side of a pin end that is the pin itself

    def cell(self, x: float, y: float) -> tuple[int, int]:
        i, j = round((x - self.x0) / self.step), round((y - self.y0) / self.step)
        if abs(self.x0 + i * self.step - x) > 0.01 or abs(self.y0 + j * self.step - y) > 0.01:
            raise RouteError(f"point ({x}, {y}) is not on the routing grid")
        return (i, j)

    def xy(self, c: tuple[int, int]) -> tuple[float, float]:
        return (self.x0 + c[0] * self.step, self.y0 + c[1] * self.step)

    def block_box(self, x: float, y: float, w: float, h: float, margin: int = 0) -> None:
        """Block every cell whose point lies inside the box (grown by ``margin`` cells)."""
        i0 = int((x - self.x0) // self.step) - margin
        i1 = int(-((-(x + w - self.x0)) // self.step)) + margin
        j0 = int((y - self.y0) // self.step) - margin
        j1 = int(-((-(y + h - self.y0)) // self.step)) + margin
        for i in range(max(i0, 0), min(i1, self.cols - 1) + 1):
            px = self.x0 + i * self.step
            if not (x - margin * self.step - 0.01 <= px <= x + w + margin * self.step + 0.01):
                continue
            for j in range(max(j0, 0), min(j1, self.rows - 1) + 1):
                py = self.y0 + j * self.step
                if y - margin * self.step - 0.01 <= py <= y + h + margin * self.step + 0.01:
                    self.blocked.add((i, j))

    def add_terminal(self, net: str, c: tuple[int, int], body_side: str | None) -> None:
        """A pin end: its arm toward the part body is the pin itself."""
        if c in self.terminals and self.terminals[c] != net:
            raise RouteError(f"two nets end at {self.xy(c)}")
        self.blocked.discard(c)
        self.terminals[c] = net
        self.arms.setdefault(c, {}).setdefault(net, set())
        if body_side:
            self.pinside[c] = body_side

    def _others(self, c, net):
        return {n: a for n, a in self.arms.get(c, {}).items() if n != net}

    def _straight(self, arms: set) -> str | None:
        if arms == {"L", "R"}:
            return "h"
        if arms == {"U", "D"}:
            return "v"
        return None

    # ------------------------------------------------------------------ one connection

    def _search(self, net: str, start: tuple[int, int], tree: set, bounds) -> list[tuple[int, int]] | None:
        ci0, cj0, ci1, cj1 = bounds
        ti0 = min(c[0] for c in tree)
        ti1 = max(c[0] for c in tree)
        tj0 = min(c[1] for c in tree)
        tj1 = max(c[1] for c in tree)

        def h(c):
            dx = ti0 - c[0] if c[0] < ti0 else (c[0] - ti1 if c[0] > ti1 else 0)
            dy = tj0 - c[1] if c[1] < tj0 else (c[1] - tj1 if c[1] > tj1 else 0)
            return dx + dy

        start_arms = self.arms.get(start, {}).get(net, set()) | ({self.pinside[start]} if start in self.pinside else set())
        seq = 0
        heap = [(h(start), 0.0, seq, start, "")]
        best = {(start, ""): 0.0}
        prev: dict = {}
        while heap:
            f, g, _s, c, d = heapq.heappop(heap)
            if d == "*":
                path = [c]
                key = (c, "*")
                while key in prev:
                    key = prev[key]
                    path.append(key[0])
                path.reverse()
                # Collapse the duplicated goal cell.
                return [p for k, p in enumerate(path) if k == 0 or p != path[k - 1]]
            if best.get((c, d), 1e18) < g:
                continue
            here_others = self._others(c, net) if c != start else {}
            for nd in ORDER:
                if d and nd == OPP[d]:
                    continue
                if c == start and nd in start_arms:
                    continue  # never leave a pin back into its body or along a wire it already has
                if here_others and d and nd != d:
                    continue  # never bend on a crossing
                dx, dy = DIRS[nd]
                n = (c[0] + dx, c[1] + dy)
                if not (ci0 <= n[0] <= ci1 and cj0 <= n[1] <= cj1):
                    continue
                cost = g + 1.0 + (BEND if d and nd != d else 0.0)
                if n in tree:
                    mine = self.arms.get(n, {}).get(net, set())
                    arm = OPP[nd]
                    pin = self.pinside.get(n)
                    if arm in mine or arm == pin or len(mine) + (1 if pin else 0) >= 3:
                        continue
                    if self._others(n, net):
                        continue
                    key = (n, "*")
                    if cost < best.get(key, 1e18):
                        best[key] = cost
                        prev[key] = (c, d)
                        seq += 1
                        heapq.heappush(heap, (cost, cost, seq, n, "*"))
                    continue
                if n in self.blocked:
                    continue
                if n in self.terminals and self.terminals[n] != net:
                    continue
                others = self._others(n, net)
                if self.arms.get(n, {}).get(net):
                    continue  # our own wire but not in this tree: cannot happen; be safe
                if others:
                    ok = True
                    for a in others.values():
                        st = self._straight(a)
                        if st is None or st == ("h" if nd in "LR" else "v"):
                            ok = False
                            break
                    if not ok:
                        continue
                    cost += CROSS
                else:
                    # Prefer a free lane over one hugging another net's wire.
                    for sd in (("U", "D") if nd in "LR" else ("L", "R")):
                        sx, sy = DIRS[sd]
                        m = (n[0] + sx, n[1] + sy)
                        if any(self._others(m, net).values()):
                            cost += HUG
                key = (n, nd)
                if cost < best.get(key, 1e18):
                    best[key] = cost
                    prev[key] = (c, d)
                    seq += 1
                    heapq.heappush(heap, (cost + h(n), cost, seq, n, nd))
        return None

    def connect(self, net: str, start: tuple[int, int], tree: set) -> list[tuple[int, int]]:
        """Route ``start`` to the nearest cell of ``tree`` and record the wire; returns its cells."""
        cells = [start, *tree]
        i0, i1 = min(c[0] for c in cells), max(c[0] for c in cells)
        j0, j1 = min(c[1] for c in cells), max(c[1] for c in cells)
        path = None
        for margin in (6, 16, None):
            if margin is None:
                bounds = (0, 0, self.cols - 1, self.rows - 1)
            else:
                bounds = (max(i0 - margin, 0), max(j0 - margin, 0), min(i1 + margin, self.cols - 1),
                          min(j1 + margin, self.rows - 1))
            path = self._search(net, start, tree, bounds)
            if path:
                break
        if not path:
            raise RouteError(f"net {net!r}: no route from {self.xy(start)} to the rest of the net")
        for a, b in zip(path, path[1:]):
            d = next(k for k, v in DIRS.items() if (a[0] + v[0], a[1] + v[1]) == b)
            self.arms.setdefault(a, {}).setdefault(net, set()).add(d)
            self.arms.setdefault(b, {}).setdefault(net, set()).add(OPP[d])
        return path

    def route(self, net: str, terminals: list[tuple[int, int]]) -> None:
        """Route a whole net: the first two terminals to each other, then each other terminal to the tree drawn so far.

        The tree starts as the first terminal plus any wire of the net already recorded (a pre-drawn stub).
        """
        tree = {c for c, nets in self.arms.items() if nets.get(net) and (c not in self.terminals or c == terminals[0])}
        tree |= {terminals[0]}
        todo = list(terminals[1:])
        first = True
        while todo:
            # The second terminal first (the net's main wire, pin to pin), then the nearest terminal, ties by the
            # order given: branches join the main wire instead of bending it.
            if not first:
                todo.sort(key=lambda c: min(abs(c[0] - t[0]) + abs(c[1] - t[1]) for t in tree))
            first = False
            s = todo.pop(0)
            if s in tree:
                continue
            path = self.connect(net, s, tree)
            tree |= set(path)

    # ------------------------------------------------------------------ output

    def segments(self, net: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        """Maximal straight runs of a net, in body coordinates, in a fixed order."""
        out = []
        for c in sorted(c for c, n in self.arms.items() if n.get(net)):
            a = self.arms[c][net]
            for d, back in (("R", "L"), ("D", "U")):
                if d in a and back not in a:
                    end = c
                    while d in self.arms.get(end, {}).get(net, set()):
                        end = (end[0] + DIRS[d][0], end[1] + DIRS[d][1])
                    out.append((self.xy(c), self.xy(end)))
        return out

    def junctions(self, net: str) -> list[tuple[float, float]]:
        """Points where three wires of the net meet (a pin counts as one), drawn as dots."""
        out = []
        for c in sorted(self.arms):
            n = len(self.arms[c].get(net, ())) + (1 if c in self.pinside and self.terminals.get(c) == net else 0)
            if n >= 3:
                out.append(self.xy(c))
        return out

    def crossings(self) -> int:
        return sum(1 for c, nets in self.arms.items() if len(nets) > 1)
