"""The application circuit figure: MCU, chip and the parts around them as a schematic, routed on a grid.

Placement follows how reference designs are drawn, so nobody positions a part by hand:

* The chip is a box in the middle. Supply pins point up, ground pins down; pins whose net reaches the MCU (directly
  or through one series part) face it on the left; every other pin faces right, in package-number order.
* The MCU stands on the left with each pin level with the chip pin it drives, so bus and GPIO wires run straight.
  Above each wire, in the port's colour, is the hook that drives it: the reader sees ``GpioSet(CtrlPin::Reset)``
  on the wire to RESET_N.
* A resistor from an MCU-side net to a supply is a pull-up: it stands above the wires, its supply on top; one to
  ground is a pull-down below them. A part between the MCU pin and the chip pin sits in the wire.
* A capacitor from a supply pin's net to ground is that pin's decoupling: it stands next to the pin, under the
  pin's supply symbol, with its own ground.
* Right-side pins each get a lane: a chain of two-pin parts runs out from the pin (a load, an LED and its resistor)
  and ends on a supply or ground symbol; further parts on the same net hang below the lane. Connectors and other
  ICs stand at the far right. A part no pattern places goes in a row under the circuit.
* Supplies and grounds are drawn as symbols at each place they are used, as on a datasheet; only a supply pin and
  its decoupling share one symbol.

Every other wire is routed by ``router.Grid``: orthogonal, never through a part or a label, crossings only at right
angles and junction dots where three wires meet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..figkit import Box, Fig, text_width
from . import symbols as S
from .common import UNVERIFIED_MARK, layout_problems, unverified_note
from .model import PIN_TYPES, Circuit, Hardware, Net
from .router import Grid, RouteError

G = S.G
HOOK_TONE = {"spi": "blue", "i2c": "blue", "uart": "blue", "gpio-out": "teal", "gpio-in": "amber", "irq": "amber",
             "other": "violet"}
HOOK_LABEL = {"blue": "bus hook (SPI, I2C, UART)", "teal": "GPIO output hook", "amber": "GPIO input hook",
              "violet": "other hook"}
HOOK_SIZE = 12
LANE_GAP = 3  # px between what one lane paints and the next


def _g(v: float) -> float:
    return math.ceil(v / G - 1e-9) * G


@dataclass
class CPin:
    """A pin of the chip in the circuit: package pins that share a name are one."""

    name: str
    numbers: list
    type: str
    net: Net | None
    hook: str
    side: str = "R"
    y: float = 0.0
    x: float = 0.0

    @property
    def tone(self) -> str:
        return PIN_TYPES[self.type][0]


@dataclass
class Plan:
    """Where every part goes, before anything is drawn."""

    left: list = field(default_factory=list)
    right: list = field(default_factory=list)
    top: list = field(default_factory=list)
    bottom: list = field(default_factory=list)
    series: dict = field(default_factory=dict)  # chip pin name -> part id
    pullups: list = field(default_factory=list)  # (part id, chip pin name, supply net, pin on net, pin on supply)
    pulldowns: list = field(default_factory=list)
    decaps: dict = field(default_factory=dict)  # chip pin name -> [(part id, pin on supply, pin on ground)]
    chains: dict = field(default_factory=dict)  # chip pin name -> [(part id, in pin, out pin)], end net
    chain_end: dict = field(default_factory=dict)
    shunts: dict = field(default_factory=dict)  # chip pin name -> [(part id, pin on net, other pin, other net)]
    hanging: dict = field(default_factory=dict)  # bottom chip pin name -> (part id, pin on net, other pin, net)
    far: list = field(default_factory=list)  # connectors and ICs
    loose: list = field(default_factory=list)  # parts no pattern placed


def circuit(hw: Hardware, circ: Circuit) -> Fig:
    """The figure ``chip-circuit-<id>``: laid out twice, first to measure, then on the final canvas."""
    probe = _draw(hw, circ, Fig("probe", "p", alt="p", width=4000), dy=0)
    dy = _g(-probe["min_y"] + 2 * G)
    width = max(760, int(_g(probe["max_x"] + 2 * G)) + 64)
    used_tones = probe["tones"]
    legend = [(t, HOOK_LABEL[t]) for t in ("blue", "teal", "amber", "violet") if t in used_tones]
    fig = Fig(
        f"chip-circuit-{circ.id}",
        f"{hw.chip}: {circ.title}",
        alt=f"Schematic of the {hw.chip} {circ.title.lower()}: " + _alt(hw, circ),
        width=width,
        kicker="Hardware",
        subtitle=(circ.description + " " if circ.description else "")
        + f"Above each MCU wire: the port hook that drives it. Datasheet: {circ.ref.short()}.",
        legend=legend,
    )
    info = _draw(hw, circ, fig, dy=dy)
    fig.doc = ("Reads: A schematic. The MCU is on the left, each of its pins level with the chip pin it connects to; "
               "above each wire is the hook of the driver's port that drives or reads it. Supply pins point up to "
               "their supply and decoupling, ground pins down. Pins on the right carry the loads and the pins tied "
               "to a supply or ground; a cross marks a pin left open. A dot is a junction; wires that cross without "
               "a dot are not connected.")
    unverified_note(fig, info["unverified"])
    fig.routing = info  # for the tests
    return fig


def _alt(hw: Hardware, circ: Circuit) -> str:
    parts = [p for p in circ.parts.values() if p.kind not in ("chip",)]
    kinds = []
    for p in parts:
        kinds.append(f"{p.id} {p.label or p.kind}{(' ' + p.value) if p.value else ''}")
    hooks = sorted({hw.hooks[h].call for q in hw.pins if (h := circ.hook_of(q)) and circ.net_of(circ.chip.id, q.name)})
    s = "the chip with " + ", ".join(kinds) if kinds else "the chip alone"
    if hooks:
        s += "; the MCU wires carry the port hooks " + ", ".join(hooks)
    return s + "."


# ---------------------------------------------------------------------------------------------------- planning


def _plan(hw: Hardware, circ: Circuit) -> tuple[Plan, dict[str, CPin]]:
    U = circ.chip
    plan = Plan()
    parts = circ.parts
    mcus = [p for p in parts.values() if p.kind == "mcu"]
    mcu = mcus[0] if mcus else None

    def nodes(net: Net, kind: str | None = None, exclude: str | None = None):
        return [(pid, pn) for pid, pn in net.nodes if (kind is None or parts[pid].kind == kind) and pid != exclude]

    def other(pid: str, pin: str) -> tuple[str, Net | None]:
        o = "2" if pin == "1" else "1"
        return o, circ.net_of(pid, o)

    cpins: dict[str, CPin] = {}
    for p in sorted(hw.pins, key=lambda q: (q.is_pad, int(q.number) if not q.is_pad else 0)):
        if p.name in cpins:
            cpins[p.name].numbers.append(p.number)
            continue
        cpins[p.name] = CPin(p.name, [p.number], p.type, circ.net_of(U.id, p.name), circ.hook_of(p))
    used: set[str] = {U.id} | ({mcu.id} if mcu else set())

    def reaches_mcu(net: Net | None):
        if net is None or mcu is None:
            return None
        if nodes(net, "mcu"):
            return ("direct", None)
        for pid, pn in net.nodes:
            part = parts[pid]
            if part.two_pin and pid not in used:
                _o, onet = other(pid, pn)
                if onet and onet.kind == "signal" and nodes(onet, "mcu") and not nodes(onet, "chip"):
                    return ("series", pid)
        return None

    for cp in cpins.values():
        if cp.type == "power":
            cp.side = "U"
        elif cp.type == "ground":
            cp.side = "D"
        elif cp.net is not None and cp.net.kind == "signal" and reaches_mcu(cp.net):
            cp.side = "L"
            how = reaches_mcu(cp.net)
            if how[0] == "series":
                plan.series[cp.name] = how[1]
                used.add(how[1])
        else:
            cp.side = "R"
    for cp in cpins.values():
        {"L": plan.left, "R": plan.right, "U": plan.top, "D": plan.bottom}[cp.side].append(cp)

    # Pull-ups and pull-downs on the MCU-side nets.
    for cp in plan.left:
        for pid, pn in cp.net.nodes:
            part = parts[pid]
            if pid in used or not part.two_pin:
                continue
            o, onet = other(pid, pn)
            if onet and onet.kind == "supply":
                plan.pullups.append((pid, cp.name, onet, pn, o))
                used.add(pid)
            elif onet and onet.kind == "ground":
                plan.pulldowns.append((pid, cp.name, onet, pn, o))
                used.add(pid)
    # Decoupling at the supply pins.
    for cp in plan.top:
        if cp.net is None or cp.net.kind != "supply":
            continue
        caps = []
        for pid, pn in cp.net.nodes:
            part = parts[pid]
            if pid in used or part.kind not in ("capacitor", "polarized-capacitor"):
                continue
            o, onet = other(pid, pn)
            if onet and onet.kind == "ground":
                caps.append((pid, pn, o))
                used.add(pid)
        plan.decaps[cp.name] = caps
    # Lanes on the right.
    for cp in plan.right:
        net = cp.net
        if net is None or net.kind != "signal":
            continue
        chain = []
        cur = net
        end = None
        while True:
            cand = [(pid, pn) for pid, pn in cur.nodes if parts[pid].two_pin and pid not in used]
            if not cand:
                break
            pid, pn = cand[0]
            o, onet = other(pid, pn)
            chain.append((pid, pn, o))
            used.add(pid)
            if onet is None:
                break
            if onet.kind in ("supply", "ground"):
                end = onet
                break
            further = [(q, n) for q, n in onet.nodes if parts[q].two_pin and q not in used]
            if nodes(onet, "chip") or len(further) != 1 or len(onet.nodes) != 2:
                end = onet
                break
            cur = onet
        plan.chains[cp.name] = chain
        plan.chain_end[cp.name] = end
        sh = []
        for pid, pn in net.nodes:
            part = parts[pid]
            if pid in used or not part.two_pin:
                continue
            o, onet = other(pid, pn)
            if onet and onet.kind in ("supply", "ground"):
                sh.append((pid, pn, o, onet))
                used.add(pid)
        plan.shunts[cp.name] = sh
    # A ground pin through one part to ground (a sense resistor) hangs below the chip.
    for cp in plan.bottom:
        if cp.net is None or cp.net.kind != "signal":
            continue
        for pid, pn in cp.net.nodes:
            part = parts[pid]
            if pid in used or not part.two_pin:
                continue
            o, onet = other(pid, pn)
            if onet and onet.kind == "ground":
                plan.hanging[cp.name] = (pid, pn, o, onet)
                used.add(pid)
                break
    for p in parts.values():
        if p.id in used:
            continue
        if p.kind in ("connector", "ic", "mcu"):
            plan.far.append(p)
        else:
            plan.loose.append(p)
        used.add(p.id)
    return plan, cpins


# ---------------------------------------------------------------------------------------------------- drawing


def _draw(hw: Hardware, circ: Circuit, fig: Fig, dy: float) -> dict:
    plan, cpins = _plan(hw, circ)
    parts = circ.parts
    U = circ.chip
    mcus = [p for p in parts.values() if p.kind == "mcu"]
    mcu = mcus[0] if mcus else None
    bodies: list[tuple[Box, str]] = []
    labels: list[Box] = []
    inks: list[tuple[Box, str]] = []  # every stroke of every symbol, for the text check
    terms: dict[str, list] = {}  # routing net -> [(x, y, side)]
    nc_points: list[tuple[float, float]] = []
    tones: set[str] = set()
    unverified = [f"{p.id}{(' ' + p.value) if p.value else ''}: {p.unverified}" for p in parts.values()
                  if p.unverified]
    unverified += [f"net {n.name}: {n.unverified}" for n in circ.nets if n.unverified]

    def term(net: str, pin) -> None:
        terms.setdefault(net, []).append(pin)

    # ---- chip geometry
    def nums(cp: CPin) -> str:
        return ", ".join(str(n) for n in cp.numbers)

    lname = max([text_width(cp.name, S.PIN_NAME, 400, True) for cp in plan.left] + [0])
    rname = max([text_width(cp.name, S.PIN_NAME, 400, True) for cp in plan.right] + [0])
    title_w = max(text_width(hw.chip, 15, 700), text_width(U.id, S.LABEL))
    pitch = 3 * G
    # Right lanes: room above and below each lane. A chain needs what its parts paint above the wire (the symbol
    # and its label) and below it, measured, plus a small gap.
    lane_up, lane_dn = {}, {}
    for cp in plan.right:
        up, dn = 1.5 * G, 1.5 * G
        chain = plan.chains.get(cp.name) or []
        end = plan.chain_end.get(cp.name)
        if chain:
            ext = [_extent(parts[pid]) for pid, *_r in chain]
            up = max(2.5 * G, max(a for a, _b in ext) + LANE_GAP)
            dn = max(dn, max(b for _a, b in ext) + LANE_GAP)
            if end is not None and end.kind == "ground":
                dn = max(dn, 3 * G)
            if end is not None and end.kind == "supply":
                up = max(up, 4 * G)
        if cp.net is not None and cp.net.kind == "ground":
            dn = max(dn, 3 * G)
        if cp.net is not None and cp.net.kind == "supply":
            up = max(up, 4 * G)
        if plan.shunts.get(cp.name):
            dn = max(dn, 10 * G)
        lane_up[cp.name], lane_dn[cp.name] = up, dn
    # Lanes of consecutive pins on one supply or ground net share a symbol: only the outer lane needs its room.
    for a, b in zip(plan.right, plan.right[1:]):
        if a.net is not None and b.net is a.net and a.net.kind in ("supply", "ground") and not plan.chains.get(a.name):
            if a.net.kind == "ground":
                lane_dn[a.name] = 1.5 * G
            else:
                lane_up[b.name] = 1.5 * G
    ry = []
    y = 0.0
    for k, cp in enumerate(plan.right):
        if k:
            prev = plan.right[k - 1]
            y += _g(max(pitch, lane_dn[prev.name] + lane_up[cp.name]))
        ry.append(y)
    right_span = (ry[-1] if ry else 0)
    left_span = (len(plan.left) - 1) * pitch if plan.left else 0
    top_pad = _g(max(2 * G, lane_up[plan.right[0].name] - 0.5 * G) if plan.right else 2 * G)
    if plan.top:
        top_pad = max(top_pad, 4 * G)  # under the names of the supply pins
    bot_pad = 4 * G if plan.bottom else 2 * G
    inner = max(right_span, left_span)
    H = _g(top_pad + inner + bot_pad + (lane_dn[plan.right[-1].name] - 1.5 * G if plan.right else 0))
    H = max(H, _g(10 * G))
    # Top and bottom pins: x offsets inside the chip.
    def cap_label_w(pid: str) -> float:
        part = parts[pid]
        note = UNVERIFIED_MARK if part.unverified else ""
        return max(text_width(pid, S.LABEL, 700), text_width(f"{part.value} {note}".strip(), S.LABEL))

    cap_off: dict[str, list[float]] = {}  # top pin -> x offset of each decoupling capacitor from the pin

    def tb_widths(cps, with_caps):
        """(room left of the pin, room right of it) for each top or bottom pin: its name is centred on the pin, its
        numbers run right of the stub, its decoupling capacitors stand further right."""
        ws = []
        for cp in cps:
            name_w = max(text_width(cp.name, S.PIN_NAME, 400, True),
                         text_width(cp.net.label or cp.net.name, S.LABEL, 700) if cp.net else 0)
            num_w = text_width(nums(cp), S.PIN_NUM) + 6
            left = _g(name_w / 2 + G)
            right = _g(max(name_w / 2, num_w) + G)
            if cp.side == "D" and plan.hanging.get(cp.name):
                right = max(right, 9 * G)
            if with_caps and plan.decaps.get(cp.name):
                offs, x = [], 0.0
                for k, (pid, _s, _g2) in enumerate(plan.decaps[cp.name]):
                    x = _g(max(6 * G, num_w + 15 + G)) if not k else \
                        _g(x + 15 + cap_label_w(plan.decaps[cp.name][k - 1][0]) + 2 * G)
                    offs.append(x)
                cap_off[cp.name] = offs
                right = max(right, _g(offs[-1] + 15 + cap_label_w(plan.decaps[cp.name][-1][0]) + 2 * G))
            ws.append((max(left, 2 * G), max(right, 2 * G)))
        return ws

    tw, bw = tb_widths(plan.top, True), tb_widths(plan.bottom, False)
    W = max(_g(lname + rname + title_w + 8 * G), _g(sum(a + b for a, b in tw) + 4 * G),
            _g(sum(a + b for a, b in bw) + 4 * G), 20 * G)

    # ---- horizontal geometry
    mcu_pins_r = []  # (chip pin, mcu pin name)
    if mcu:
        for cp in plan.left:
            via = plan.series.get(cp.name)
            net = cp.net
            if via:
                o = "2" if circ.net_of(via, "1") is net else "1"
                net = circ.net_of(via, o)
            mp = [pn for pid, pn in net.nodes if pid == mcu.id]
            mcu_pins_r.append((cp, mp[0] if mp else None))
    mlabels = {n: lab for n, lab in mcu.pins} if mcu else {}
    hooks_w = 0.0
    for cp, _mp in mcu_pins_r:
        if cp.hook:
            hooks_w = max(hooks_w, text_width(hw.hooks[cp.hook].call, HOOK_SIZE, 500, True))
    mcu_w = 0.0
    mcu_top, mcu_bot, mcu_extra = [], [], []
    if mcu:
        taken = {mp for _cp, mp in mcu_pins_r}
        for n, lab in mcu.pins:
            if n in taken:
                continue
            net = circ.net_of(mcu.id, n)
            if net is not None and net.kind == "supply":
                mcu_top.append(n)
            elif net is not None and net.kind == "ground":
                mcu_bot.append(n)
            elif net is not None:
                mcu_extra.append(n)
        mcu_w = max([text_width(lab, S.PIN_NAME, 400, True) for n, lab in mcu.pins if n not in mcu_top + mcu_bot]
                    + [0]) + text_width(mcu.label or "MCU", 15, 700) + 6 * G
        mcu_w = _g(max(mcu_w, 18 * G, (len(mcu_top) + 1) * 6 * G + text_width(mcu.label or "MCU", 15, 700)))
    series_w = 9 * G if plan.series else 0
    pull_w = len(plan.pullups + plan.pulldowns) * 8 * G
    chan = _g(G + hooks_w + 3 * G + series_w + pull_w + 3 * G) if mcu else 0
    mcu_x = 0.0
    chip_x = (_g(mcu_w + S.STUB + chan + S.STUB)) if mcu else _g(4 * G)
    chip_r = chip_x + W

    # ---- vertical geometry (chip top at ct)
    top_need = 0.0
    for cp in plan.top:
        top_need = max(top_need, 17.5 * G if plan.decaps.get(cp.name) else 7 * G)
    if plan.pullups:
        top_need = max(top_need, 13 * G - top_pad)
    ct = _g(top_need + 2 * G) + dy
    cb = ct + H
    # Left pins centred on the right span (or the body).
    l0 = ct + top_pad + _g(max(0, (inner - left_span) / 2) if plan.right else 0)
    for k, cp in enumerate(plan.left):
        cp.y = l0 + k * pitch
    for k, cp in enumerate(plan.right):
        cp.y = ct + top_pad + ry[k]
    for cps, ws in ((plan.top, tw), (plan.bottom, bw)):
        xx = chip_x + _g(2 * G + (W - sum(a + b for a, b in ws) - 4 * G) / 2)
        for cp, (a, b) in zip(cps, ws):
            cp.x = xx + a
            xx += a + b

    # ---- the chip
    sides = {"L": [], "R": [], "U": [], "D": []}
    pos = {}
    for cp in plan.left + plan.right:
        sides[cp.side].append(S.BoxPin(cp.name, cp.name, nums(cp), cp.tone))
        pos[(cp.side, cp.name)] = cp.y - ct
    for cp in plan.top + plan.bottom:
        sides[cp.side].append(S.BoxPin(cp.name, cp.name, nums(cp), cp.tone))
        pos[(cp.side, cp.name)] = cp.x - chip_x
    chip = S.box_symbol(fig, U.id, chip_x, ct, W, H, sides, hw.chip, U.id, fill="card", stroke="brand.strong",
                        title_tone="brand.text", positions=pos, mono=True)
    bodies.append((chip.body, f"the {hw.chip}"))
    inks.extend((b, f"the {hw.chip}") for b in chip.ink)
    labels += chip.labels
    placed_boxes = [(chip.body, 2.5)]

    # ---- the MCU
    mcu_p = None
    if mcu:
        ys = [cp.y for cp, _ in mcu_pins_r]
        y0 = (min(ys) if ys else ct + 2 * G) - 6 * G
        extra_y = (max(ys) if ys else ct) + 3 * G
        y1 = extra_y + len(mcu_extra) * pitch + 1 * G
        msides = {"R": [], "U": [], "D": []}
        mpos = {}
        for cp, mp in mcu_pins_r:
            if mp:
                msides["R"].append(S.BoxPin(mp, mlabels[mp], "", HOOK_TONE[hw.hooks[cp.hook].kind]
                                            if cp.hook else "slate"))
                mpos[("R", mp)] = cp.y - y0
        for k, n in enumerate(mcu_extra):
            msides["R"].append(S.BoxPin(n, mlabels[n], "", "slate"))
            mpos[("R", n)] = extra_y + k * pitch - y0
        for k, n in enumerate(mcu_top):
            msides["U"].append(S.BoxPin(n, mlabels[n], "", "rose"))
            mpos[("U", n)] = mcu_w - 3 * G - k * 6 * G
        for k, n in enumerate(mcu_bot):
            msides["D"].append(S.BoxPin(n, mlabels[n], "", "slate"))
            mpos[("D", n)] = mcu_w - 3 * G - k * 6 * G
        mcu_p = S.box_symbol(fig, mcu.id, mcu_x, _g(y0), mcu_w, _g(y1 - y0), msides, mcu.label or "MCU", mcu.id,
                             fill="paper", stroke="ink2", positions=mpos, mono=True, title_at="top")
        bodies.append((mcu_p.body, "the MCU"))
        inks.extend((b, "the MCU") for b in mcu_p.ink)
        labels += mcu_p.labels
        placed_boxes.append((mcu_p.body, 2.5))

    pins_of: dict[tuple[str, str], tuple] = {}
    for name, pin in chip.pins.items():
        pins_of[(U.id, name)] = pin
    if mcu_p:
        for name, pin in mcu_p.pins.items():
            pins_of[(mcu.id, name)] = pin

    small: list[tuple[Box, float]] = []  # bodies of small symbols, blocked with a small margin

    attached: list[tuple[float, float]] = []

    def attach_supply(net: Net, x: float, y: float, key: str):
        attached.append((x, y))
        s = S.supply(fig, x, y, net.label or net.name, sid=key)
        labels.extend(s.labels)
        inks.extend((b, f"the {net.label or net.name} supply") for b in s.ink)
        small.append((s.body, 0.5))
        return s

    def attach_ground(x: float, y: float, key: str):
        attached.append((x, y))
        g = S.ground(fig, x, y, sid=key)
        inks.extend((b, "a ground") for b in g.ink)
        small.append((g.body, 0.5))
        return g

    def place_two(pid: str, x: float, y: float, vertical: bool, first: str = "1"):
        """A two-pin part from (x, y), its pin ``first`` there (the symbol flips, so a diode keeps its polarity)."""
        part = parts[pid]
        note = UNVERIFIED_MARK if part.unverified else ""
        p = S.two_pin(fig, pid, part.kind, x, y, vertical, part.value, note, flip=first != "1")
        bodies.append((p.body, f"{pid}"))
        inks.extend((b, pid) for b in p.ink)
        labels.extend(p.labels)
        small.append((p.body, 0.75))
        for n, pin in p.pins.items():
            pins_of[(pid, n)] = pin
        return p

    def net_key(net: Net | None, cluster: str = "") -> str:
        return f"{net.name}#{cluster}" if net is not None and net.kind != "signal" else (net.name if net else "")

    # ---- supply pins, decoupling
    for cp in plan.top:
        x, ye = chip.pins[cp.name][0], chip.pins[cp.name][1]
        caps = plan.decaps.get(cp.name, [])
        if cp.net is None:
            nc_points.append((x, ye))
            continue
        if cp.net.kind != "supply":
            term(cp.net.name, chip.pins[cp.name])
            continue
        if not caps:
            attach_supply(cp.net, x, ye, f"sup-{cp.name}")
            term(net_key(cp.net, cp.name), chip.pins[cp.name])
            continue
        key = net_key(cp.net, cp.name)
        term(key, chip.pins[cp.name])
        s = attach_supply(cp.net, x, ct - 14 * G, f"sup-{cp.name}")
        term(key, s.pins["1"])
        for k, (pid, pin_s, pin_g) in enumerate(caps):
            cx = x + cap_off[cp.name][k]
            p = place_two(pid, cx, ct - 11 * G, True, first=pin_s)
            top_pin, bot_pin = p.pins[pin_s], p.pins[pin_g]
            term(key, top_pin)
            attach_ground(bot_pin[0], bot_pin[1], f"gnd-{pid}")
    for cp in plan.bottom:
        x, ye = chip.pins[cp.name][0], chip.pins[cp.name][1]
        if cp.net is None:
            nc_points.append((x, ye))
        elif cp.net.kind == "ground":
            attach_ground(x, ye, f"gnd-{cp.name}")
            term(net_key(cp.net, cp.name), chip.pins[cp.name])
        elif plan.hanging.get(cp.name):
            pid, pn, o, onet = plan.hanging[cp.name]
            p = place_two(pid, x, ye + 2 * G, True, first=pn)
            term(cp.net.name, chip.pins[cp.name])
            term(cp.net.name, p.pins[pn])
            attach_ground(p.pins[o][0], p.pins[o][1], f"gnd-{pid}")
        else:
            term(cp.net.name, chip.pins[cp.name])

    # ---- MCU power pins
    if mcu_p:
        for n in mcu_top:
            net = circ.net_of(mcu.id, n)
            pin = mcu_p.pins[n]
            attach_supply(net, pin[0], pin[1], f"sup-{mcu.id}-{n}")
            term(net_key(net, f"{mcu.id}.{n}"), pin)
        for n in mcu_bot:
            net = circ.net_of(mcu.id, n)
            pin = mcu_p.pins[n]
            attach_ground(pin[0], pin[1], f"gnd-{mcu.id}-{n}")
            term(net_key(net, f"{mcu.id}.{n}"), pin)

    # ---- MCU-side wires: hook labels, series parts, pull-ups and pull-downs
    hook_x = (mcu_w + S.STUB + G) if mcu else 0
    for cp, mp in mcu_pins_r:
        if cp.hook:
            hk = hw.hooks[cp.hook]
            tone = HOOK_TONE[hk.kind]
            tones.add(tone)
            labels.append(fig.text(hook_x, cp.y - 6, hk.call, size=HOOK_SIZE, weight=500, mono=True,
                                   color=f"{tone}.text"))
        if mp:
            term(circ.net_of(mcu.id, mp).name, pins_of[(mcu.id, mp)])
        term(cp.net.name, chip.pins[cp.name])
    sx = _g(hook_x + hooks_w + 2 * G)
    for cp, mp in mcu_pins_r:
        via = plan.series.get(cp.name)
        if not via:
            continue
        on_chip = "1" if circ.net_of(via, "1") is cp.net else "2"
        on_mcu = "2" if on_chip == "1" else "1"
        p = place_two(via, sx, cp.y, False, first=on_mcu)
        term(circ.net_of(via, on_mcu).name, p.pins[on_mcu])
        term(cp.net.name, p.pins[on_chip])
    px = _g(sx + series_w + 2 * G)
    top_left = min(cp.y for cp in plan.left) if plan.left else ct + 2 * G
    bot_left = max(cp.y for cp in plan.left) if plan.left else ct + 2 * G
    for k, (pid, cpn, onet, pn, o) in enumerate(plan.pullups):
        x = px + k * 8 * G
        p = place_two(pid, x, top_left - 9 * G, True, first=o)
        attach_supply(onet, x, top_left - 9 * G, f"sup-{pid}")
        term(cpins[cpn].net.name, p.pins[pn])
    for k, (pid, cpn, onet, pn, o) in enumerate(plan.pulldowns):
        x = px + (len(plan.pullups) + k) * 8 * G
        p = place_two(pid, x, bot_left + 3 * G, True, first=pn)
        attach_ground(x, bot_left + 9 * G, f"gnd-{pid}")
        term(cpins[cpn].net.name, p.pins[pn])

    # ---- right lanes
    x_end = chip_r + S.STUB
    max_sh = max([len(v) for v in plan.shunts.values()] + [0])
    sh_w = 0.0
    for v in plan.shunts.values():
        for pid, *_ in v:
            sh_w = max(sh_w, text_width(f"{pid}", S.LABEL, 700), text_width(parts[pid].value, S.LABEL))
    sh_pitch = _g(sh_w + 4 * G)
    chain_x0 = _g(x_end + 3 * G + max_sh * sh_pitch)
    col_w: dict[int, float] = {}
    for cp in plan.right:
        for k, (pid, *_r) in enumerate(plan.chains.get(cp.name) or []):
            part = parts[pid]
            lab = text_width(f"{pid}  {part.value}".strip(), S.LABEL, 600)
            col_w[k] = max(col_w.get(k, 0), _g(max(S.LEN + 4 * G, lab + 3 * G)))
    col_x = {}
    acc = chain_x0
    for k in sorted(col_w):
        col_x[k] = acc + _g((col_w[k] - S.LEN) / 2)
        acc += col_w[k]
    lane_end = acc
    run_start = None
    for idx, cp in enumerate(plan.right):
        pin = chip.pins[cp.name]
        net = cp.net
        if net is None:
            nc_points.append((pin[0], pin[1]))
            continue
        if net.kind in ("supply", "ground"):
            nxt = plan.right[idx + 1] if idx + 1 < len(plan.right) else None
            prv = plan.right[idx - 1] if idx else None
            if run_start is None or prv is None or prv.net is not net:
                run_start = cp
            key = net_key(net, f"run-{run_start.name}")
            term(key, pin)
            last = nxt is None or nxt.net is not net
            first = run_start is cp
            sx2 = x_end + 3 * G
            if net.kind == "ground" and last:
                g = attach_ground(sx2, cp.y + 2 * G, f"gnd-{cp.name}")
                term(key, g.pins["1"])
            if net.kind == "supply" and first:
                s = attach_supply(net, sx2, cp.y - 2 * G, f"sup-{cp.name}")
                term(key, s.pins["1"])
            continue
        term(net.name, pin)
        chain = plan.chains.get(cp.name) or []
        cur = net.name
        for k, (pid, pin_in, pin_out) in enumerate(chain):
            p = place_two(pid, col_x[k], cp.y, False, first=pin_in)
            term(cur, p.pins[pin_in])
            onet = circ.net_of(pid, pin_out)
            if onet is None:
                break
            if onet.kind == "signal":
                cur = onet.name
                term(cur, p.pins[pin_out])
        end = plan.chain_end.get(cp.name)
        if chain and end is not None and end.kind in ("supply", "ground"):
            last_pin = pins_of[(chain[-1][0], chain[-1][2])]
            ex = last_pin[0] + 3 * G
            key = net_key(end, f"end-{cp.name}")
            term(key, last_pin)
            if end.kind == "ground":
                g = attach_ground(ex, cp.y + G, f"gnd-end-{cp.name}")
                term(key, g.pins["1"])
            else:
                s = attach_supply(end, ex, cp.y - G, f"sup-end-{cp.name}")
                term(key, s.pins["1"])
        for k, (pid, pn, o, onet) in enumerate(plan.shunts.get(cp.name) or []):
            x = x_end + 3 * G + k * sh_pitch
            p = place_two(pid, x, cp.y + 2 * G, True, first=pn)
            term(net.name, p.pins[pn])
            if onet.kind == "ground":
                attach_ground(x, p.pins[o][1], f"gnd-{pid}")
            else:
                attach_supply(onet, x, p.pins[o][1], f"sup-{pid}")

    # ---- connectors and other ICs at the far right, loose parts in a row underneath
    fx = _g(max(lane_end, x_end + 6 * G) + 8 * G)
    fy = ct
    for part in plan.far:
        names = [lab for _n, lab in part.pins]
        w = _g(max(text_width(s, S.PIN_NAME, 400, True) for s in names) + max(text_width(part.label or part.id,
                                                                                         15, 700), 0) + 6 * G)
        h = _g(len(part.pins) * pitch + 6 * G)
        p = S.box_symbol(fig, part.id, fx, fy, w, h, {"L": [S.BoxPin(n, lab) for n, lab in part.pins]},
                         part.label or part.kind, part.id, fill="paper", stroke="ink2", mono=True, title_at="top",
                         positions={("L", n): 6 * G + k * pitch for k, (n, _l) in enumerate(part.pins)})
        bodies.append((p.body, part.id))
        inks.extend((b, part.id) for b in p.ink)
        labels.extend(p.labels)
        placed_boxes.append((p.body, 2.5))
        for n, pin in p.pins.items():
            pins_of[(part.id, n)] = pin
        fy = _g(fy + h + 6 * G)
    low = max([cb + 6 * G, fy] + [b.b for b, _n in bodies])
    lx = chip_x
    for part in plan.loose:
        if part.two_pin:
            place_two(part.id, lx, low + 4 * G, True)
            lx += _g(10 * G)
        else:
            continue
    # Nets for whatever is not placed by a pattern: every node not yet a terminal.
    have = {(round(p[0], 1), round(p[1], 1)) for pins in terms.values() for p in pins}
    have |= {(round(x, 1), round(y, 1)) for x, y in attached}
    for net in circ.nets:
        for pid, pn in net.nodes:
            if (pid, pn) not in pins_of:
                continue
            pin = pins_of[(pid, pn)]
            if (round(pin[0], 1), round(pin[1], 1)) in have:
                continue
            if net.kind == "signal":
                term(net.name, pin)
            else:
                # A supply or ground pin of a loose part or connector: its own symbol, a short wire away.
                side = pin[2]
                dx, dy2 = {"L": (2 * G, 0), "R": (-2 * G, 0), "U": (0, 2 * G), "D": (0, -2 * G)}[side]
                q = (pin[0] + dx, pin[1] + dy2)
                key = net_key(net, f"{pid}.{pn}")
                if net.kind == "ground":
                    g = attach_ground(q[0], q[1] + (0 if side in "UD" else G), f"gnd-{pid}-{pn}")
                    term(key, g.pins["1"])
                else:
                    s = attach_supply(net, q[0], q[1] - (0 if side in "UD" else G), f"sup-{pid}-{pn}")
                    term(key, s.pins["1"])
                term(key, pin)
            have.add((round(pin[0], 1), round(pin[1], 1)))

    for x, y in nc_points:
        inks.append((S.no_connect(fig, x, y), "a no-connect mark"))

    # ---- route
    max_x = max([b.r for b, _n in bodies] + [lb.r for lb in labels] + [lane_end])
    min_y = min([b.y for b, _n in bodies] + [lb.y for lb in labels] + [b.y for b, _m in small])
    max_y = max([b.b for b, _n in bodies] + [lb.b for lb in labels] + [b.b for b, _m in small])
    grid = Grid(0, 0, int(max_x // G) + 12, int((max_y + 12 * G) // G) + 1, G)
    for box, m in placed_boxes:
        grid.block_box(box.x, box.y, box.w, box.h, margin=0)
        grid.block_box(box.x - m * G + 1, box.y - m * G + 1, box.w + 2 * m * G - 2, box.h + 2 * m * G - 2)
    for box, m in small:
        grid.block_box(box.x - m * G, box.y - m * G, box.w + 2 * m * G, box.h + 2 * m * G)
    for lb in labels:
        grid.block_box(lb.x - 2, lb.y - 2, lb.w + 4, lb.h + 4)
    for x, y in nc_points:
        grid.add_terminal("~nc", grid.cell(x, y), None)
    problems = []
    for net, pins in terms.items():
        for x, y, side in pins:
            try:
                grid.add_terminal(net, grid.cell(x, y), side)
            except RouteError as e:
                problems.append(str(e))
    for x, y in attached:
        c = grid.cell(x, y)
        if c not in grid.terminals:
            grid.add_terminal("~symbol", c, None)
    order = sorted(terms, key=lambda n: (0 if "#" not in n else 1, -_span(terms[n]), n))
    # Short supply clusters first would block long signals; route signals first, longest first.
    for net in order:
        cells = []
        for x, y, _s in terms[net]:
            c = grid.cell(x, y)
            if c not in cells:
                cells.append(c)
        if len(cells) < 2:
            continue
        try:
            grid.route(net, cells)
        except RouteError as e:
            problems.append(str(e))
    wires = []
    for net in sorted(terms):
        for a, b in grid.segments(net):
            fig.line([a, b], color=S.WIRE, sw=1.5, layer="edge")
            wires.append((a, b))
        for x, y in grid.junctions(net):
            fig.circle(x, y, 3.2, fill=S.WIRE, layer="label")
    for p in problems:
        fig.problem(p)
    # Wires stop at pin ends: a wire must not cross into a symbol (the stubs belong to the symbols).
    layout_problems(fig, bodies, wires, inks)
    return {
        "min_y": min_y,
        "max_x": max_x,
        "tones": tones,
        "types": {cp.type for cp in cpins.values()},
        "unverified": unverified,
        "crossings": grid.crossings(),
        "grid": grid,
        "pins": pins_of,
        "plan": plan,
    }


def _extent(part) -> tuple[float, float]:
    """How far a two-pin part laid along a lane paints above and below its wire, its label included."""
    scratch = Fig("measure", "m", alt="m")
    p = S.two_pin(scratch, part.id, part.kind, 0, 0, False, part.value, UNVERIFIED_MARK if part.unverified else "")
    boxes = p.ink + p.labels
    return -min(b.y for b in boxes), max(b.b for b in boxes)


def _span(pins) -> float:
    xs = [p[0] for p in pins]
    ys = [p[1] for p in pins]
    return (max(xs) - min(xs)) + (max(ys) - min(ys))
