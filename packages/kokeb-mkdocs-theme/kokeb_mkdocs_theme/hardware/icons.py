"""Line icons for the capability map and the hero, drawn here from simple strokes (no icon font, no copied art).

Each icon is a list of strokes on a 24 x 24 grid: ``("p", [(x, y), ...], closed)`` a polyline, ``("c", cx, cy, r)``
a circle, ``("d", cx, cy, r)`` a filled dot and ``("a", x0, y0, r, x1, y1, sweep)`` an arc of at most half a circle.
``draw()`` puts one on a tinted disc in a figkit figure, in the tone's strong colour, so it follows the theme and
reads at 3:1 or better against its disc in both themes (a graphic object, WCAG 1.4.11).

Pick the icon that says what the capability does to the outside world; a chip-specific picture is not needed.
"""

from __future__ import annotations

import math

from ..figkit import Box, Fig


def _sine(x0: float, x1: float, y: float, amp: float, periods: float = 1.0, n: int = 24) -> list:
    return [(x0 + (x1 - x0) * k / n, y - amp * math.sin(2 * math.pi * periods * k / n)) for k in range(n + 1)]


ICONS: dict[str, list[tuple]] = {
    # Motion and motors
    "motion": [("a", 12, 5, 7, 19, 12, 1), ("a", 19, 12, 7, 12, 19, 1), ("a", 12, 19, 7, 5, 12, 1),
               ("p", [(2.5, 9.5), (5, 12.5), (7.8, 9.8)], False)],
    "ramp": [("p", [(3, 4), (3, 20), (21, 20)], False), ("p", [(5, 18), (9, 8), (15, 8), (19, 18)], False)],
    "steps": [("p", [(3, 20), (3, 16), (8, 16), (8, 12), (13, 12), (13, 8), (18, 8), (18, 4), (21, 4)], False)],
    "home": [("p", [(3, 11), (12, 4), (21, 11)], False), ("p", [(6, 9), (6, 20), (18, 20), (18, 9)], False),
             ("p", [(10, 20), (10, 14), (14, 14), (14, 20)], False)],
    "load": [("a", 9, 8, 3, 15, 8, 1), ("p", [(7.5, 9), (16.5, 9), (20, 20), (4, 20)], True)],
    "stop": [("c", 12, 12, 9), ("p", [(8.5, 8.5), (15.5, 8.5), (15.5, 15.5), (8.5, 15.5)], True)],
    "encoder": [("c", 12, 12, 8.5), ("d", 12, 12, 2)]
    + [("p", [(12 + 5.5 * math.cos(a), 12 + 5.5 * math.sin(a)), (12 + 8.5 * math.cos(a), 12 + 8.5 * math.sin(a))],
        False) for a in [k * math.pi / 4 for k in range(8)]],
    # Electrical
    "current": [("p", [(3, 12), (21, 12)], False), ("p", _sine(3, 21, 12, 6), False)],
    "analog": [("p", [(3, 4), (3, 20), (21, 20)], False), ("p", _sine(5, 21, 12, 5, 1.0), False)],
    "chopper": [("p", [(3, 17), (3, 7), (8, 7), (8, 17), (13, 17), (13, 7), (18, 7), (18, 17), (21, 17)], False)],
    "power": [("p", [(13.5, 3), (6, 13.5), (11.5, 13.5), (10.5, 21), (18, 10.5), (12.5, 10.5)], True)],
    "coil": [("p", [(2, 14), (4, 14)], False), ("a", 4, 14, 2.5, 9, 14, 1), ("a", 9, 14, 2.5, 14, 14, 1),
             ("a", 14, 14, 2.5, 19, 14, 1), ("p", [(19, 14), (22, 14)], False)],
    "switch": [("p", [(2, 15), (7, 15)], False), ("d", 7, 15, 1.6), ("p", [(7, 15), (16, 8)], False),
               ("d", 17, 15, 1.6), ("p", [(17, 15), (22, 15)], False)],
    "light": [("c", 12, 10, 6), ("p", [(9.5, 17.5), (14.5, 17.5)], False), ("p", [(10.5, 20.5), (13.5, 20.5)], False)],
    "gate": [("p", [(3, 12), (9, 12)], False), ("p", [(9, 6), (9, 18)], False), ("p", [(12, 6), (12, 18)], False),
             ("p", [(12, 8), (20, 8), (20, 3)], False), ("p", [(12, 16), (20, 16), (20, 21)], False)],
    # Sensing and diagnostics
    "gauge": [("a", 4, 16, 8, 20, 16, 1), ("p", [(12, 16), (16.5, 10)], False), ("d", 12, 16, 1.8),
              ("p", [(3, 19.5), (21, 19.5)], False)],
    "temperature": [("p", [(10, 15), (10, 5), (14, 5), (14, 15)], False), ("c", 12, 17.5, 3.5),
                    ("p", [(16.5, 8), (19, 8)], False), ("p", [(16.5, 11), (19, 11)], False)],
    "axes": [("p", [(6, 18), (6, 4)], False), ("p", [(3.5, 6.5), (6, 4), (8.5, 6.5)], False),
             ("p", [(6, 18), (20, 18)], False), ("p", [(17.5, 15.5), (20, 18), (17.5, 20.5)], False),
             ("p", [(6, 18), (15, 9)], False), ("p", [(11.5, 9), (15, 9), (15, 12.5)], False)],
    "flow": [("p", [(3, 7), (19, 7)], False), ("p", [(16.5, 4.5), (19, 7), (16.5, 9.5)], False),
             ("p", [(5, 12), (21, 12)], False), ("p", [(18.5, 9.5), (21, 12), (18.5, 14.5)], False),
             ("p", [(3, 17), (19, 17)], False), ("p", [(16.5, 14.5), (19, 17), (16.5, 19.5)], False)],
    "alert": [("p", [(12, 3.5), (21.5, 20), (2.5, 20)], True), ("p", [(12, 9.5), (12, 14)], False),
              ("d", 12, 17, 1.4)],
    "shield": [("p", [(12, 3), (19.5, 6), (19.5, 12), (12, 21), (4.5, 12), (4.5, 6)], True),
               ("p", [(8.5, 12), (11, 14.5), (15.5, 9.5)], False)],
    "check": [("c", 12, 12, 9), ("p", [(7.5, 12.5), (10.5, 15.5), (16.5, 9)], False)],
    "clock": [("c", 12, 12, 9), ("p", [(12, 7), (12, 12), (15.5, 14)], False)],
    # Data and interfaces
    "bus": [("p", [(3, 9), (8, 9), (8, 15), (3, 15)], True), ("p", [(16, 9), (21, 9), (21, 15), (16, 15)], True),
            ("p", [(8, 11), (16, 11)], False), ("p", [(8, 13), (16, 13)], False)],
    "chain": [("p", [(2, 9), (7, 9), (7, 15), (2, 15)], True),
              ("p", [(9.5, 9), (14.5, 9), (14.5, 15), (9.5, 15)], True),
              ("p", [(17, 9), (22, 9), (22, 15), (17, 15)], True), ("p", [(7, 12), (9.5, 12)], False),
              ("p", [(14.5, 12), (17, 12)], False)],
    "memory": [("p", [(7, 6), (17, 6), (17, 18), (7, 18)], True)]
    + [("p", [(4, y), (7, y)], False) for y in (9, 12, 15)] + [("p", [(17, y), (20, y)], False) for y in (9, 12, 15)],
    "table": [("p", [(4, 5), (20, 5), (20, 19), (4, 19)], True), ("p", [(4, 10), (20, 10)], False),
              ("p", [(4, 14.5), (20, 14.5)], False), ("p", [(10, 5), (10, 19)], False)],
    "settings": [("p", [(4, 7), (20, 7)], False), ("c", 9, 7, 2.2), ("p", [(4, 12), (20, 12)], False),
                 ("c", 15, 12, 2.2), ("p", [(4, 17), (20, 17)], False), ("c", 7.5, 17, 2.2)],
    "key": [("c", 8, 12, 4), ("p", [(12, 12), (21, 12)], False), ("p", [(17.5, 12), (17.5, 15)], False),
            ("p", [(20.5, 12), (20.5, 15.5)], False)],
    "lock": [("p", [(6, 11), (18, 11), (18, 20), (6, 20)], True), ("p", [(8.5, 11), (8.5, 8)], False),
             ("a", 8.5, 8, 3.5, 15.5, 8, 1), ("p", [(15.5, 8), (15.5, 11)], False), ("d", 12, 15.5, 1.5)],
    "tag": [("p", [(4, 4), (12, 4), (20, 12), (12, 20), (4, 12)], True), ("d", 8.5, 8.5, 1.6)],
    "sleep": [("a", 14, 4, 8, 14, 20, 0), ("a", 14, 20, 6.5, 14, 4, 1)],
}


def draw(fig: Fig, name: str, cx: float, cy: float, d: float, tone: str, on: str = "card") -> Box:
    """Icon ``name`` centred on (cx, cy) on a disc ``d`` px across, in ``tone``; ``on`` is the paint under the disc."""
    fig.circle(cx, cy, d / 2, fill=f"{tone}.tint", stroke=f"{tone}.soft", sw=1.2, layer="label")
    s = d * 0.62 / 24
    x0, y0 = cx - 12 * s, cy - 12 * s
    sw = max(1.6, d / 22)
    col = f"{tone}.strong"

    def P(x, y):
        return (x0 + x * s, y0 + y * s)

    for st in ICONS[name]:
        kind = st[0]
        if kind == "p":
            pts = [P(*q) for q in st[1]]
            cmds = [("M", *pts[0])] + [("L", *q) for q in pts[1:]] + ([("Z",)] if st[2] else [])
            fig.path(cmds, stroke=col, sw=sw, layer="label")
        elif kind == "c":
            fig.circle(*P(st[1], st[2]), st[3] * s, fill=None, stroke=col, sw=sw, layer="label")
        elif kind == "d":
            fig.circle(*P(st[1], st[2]), st[3] * s, fill=col, layer="label")
        elif kind == "a":
            a, b = P(st[1], st[2]), P(st[4], st[5])
            fig.path([("M", *a), ("A", st[3] * s, *b, st[6])], stroke=col, sw=sw, layer="label")
    return Box(cx - d / 2, cy - d / 2, d, d)
