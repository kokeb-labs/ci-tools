"""``topology``: several devices on one host: a daisy chain or a shared (multi-drop) bus, every limit cited.

Model::

    kind: topology
    id: spi-chain
    title: SPI daisy chain
    alt: One sentence.
    reads: Two or more sentences naming the host and every device.
    style: chain                                 # chain: data passes through each device; bus: all on shared lines
    refs: {chain: {doc: ds, section: "4.3 Daisy chaining", page: 24}}
    host: {label: MCU, detail: SPI controller}
    nodes:                                       # two to four entries; {more: true} draws the devices left out
      - {label: TMC5160 1, detail: first in the chain}
      - {more: true, label: "…", detail: any number}
      - {label: TMC5160 N, detail: last}
    chain:                                       # style chain: the pin each device takes data on and passes it out of
      in: SDI
      out: SDO
      host_out: MOSI                             # the host pin that feeds the first device
      host_in: MISO                              # optional: the last device's output back to the host
    shared: [SCK, CSN]                           # lines every device and the host share (drawn as rails below)
    ends: {label: "120 Ω", ref: can}             # style bus, two rails: a terminator at each end
    pullups: {label: "pull-ups to VDD", ref: i2c}  # style bus: one resistor per rail at the far end
    facts:                                       # the limits, each with its datasheet reference
      - {text: "Up to 32 devices on one bus", ref: chain}

A node may carry ``address`` (``"0x40"``, ``ID 1``) with its ``ref``. A number in a fact, a note, an address, a
detail or a terminator label without a datasheet reference fails the build.
"""

from __future__ import annotations

from ..core import PROFILES, text_width, wrap
from ._cite import Citations, has_number
from ._common import Check, check_header, make_fig

REQUIRED = {"style", "host", "nodes"}
ALLOWED = {"refs", "chain", "shared", "ends", "pullups", "facts", "bus_label"}
RAIL_GAP = 30.0


def validate(model: dict, where: str, root=None) -> Citations:
    c = Check(where, model)
    check_header(c, model, "topology", REQUIRED, ALLOWED)
    cites = Citations(c, model, root)
    style = model.get("style")
    if style not in ("chain", "bus"):
        c.bad("model.style: chain or bus")
    h = model.get("host")
    if c.keys(h, "host", {"label"}, {"detail", "tone", "ref"}):
        c.tone(h, "host", default="blue")
        cites.text_needs_ref(h, "host", ("detail",))
    nodes = model.get("nodes") or []
    if not isinstance(nodes, list) or not 2 <= len(nodes) <= 4:
        c.bad("nodes: two to four entries (one may be {more: true})")
        nodes = nodes if isinstance(nodes, list) else []
    mores = 0
    for i, n in enumerate(nodes):
        p = f"nodes[{i}]"
        if not c.keys(n, p, set(), {"label", "detail", "address", "ref", "more", "tone"}):
            continue
        if n.get("more"):
            mores += 1
            if i in (0,):
                c.bad(f"{p}: the first device cannot be the left-out ones")
        elif not str(n.get("label") or "").strip():
            c.bad(f"{p}.label: must not be empty")
        c.tone(n, p, default="teal")
        if n.get("address") not in (None, ""):
            cites.use(n.get("ref"), f"{p}.ref", f"address {n.get('address')}")
        else:
            cites.text_needs_ref(n, p, ("detail",))
    if mores > 1:
        c.bad("nodes: at most one {more: true}")
    shared = model.get("shared") or []
    if not isinstance(shared, list) or not all(isinstance(s, str) and s.strip() for s in shared):
        c.bad("shared: a list of line names")
        shared = []
    if len(shared) > 4:
        c.bad("shared: at most four lines")
    if style == "chain":
        ch = model.get("chain")
        if c.keys(ch, "chain", {"in", "out", "host_out"}, {"host_in", "label", "ref"}):
            cites.text_needs_ref(ch, "chain", ("label",))
    elif model.get("chain") is not None:
        c.bad("chain: only for style: chain")
    if style == "bus" and not shared:
        c.bad("shared: a bus needs at least one line")
    for key in ("ends", "pullups"):
        e = model.get(key)
        if e is None:
            continue
        if style != "bus":
            c.bad(f"{key}: only for style: bus")
        if c.keys(e, key, {"label"}, {"ref"}):
            cites.text_needs_ref(e, key, ("label",))
    if model.get("ends") is not None and len(shared) != 2:
        c.bad("ends: terminators sit between two rails (a differential pair); shared needs exactly two lines")
    for i, ft in enumerate(model.get("facts") or []):
        q = f"facts[{i}]"
        if c.keys(ft, q, {"text"}, {"ref"}):
            cites.text_needs_ref(ft, q, ("text",))
    if model.get("bus_label") is not None and has_number(model.get("bus_label")):
        c.bad("bus_label: a number belongs in facts, with its ref")
    c.done()
    return cites


def build(model: dict, lock_dir, where: str = "model", root=None):
    """A vertical stack, so it reads on a phone: the host on top, the devices under it, the chain arrows between
    them (the return to the host up the left side) and the shared lines as rails on the right."""
    cites = validate(model, where, root)
    prof = model.get("profile", "phone")
    model = dict(model, profile=prof)
    k = PROFILES[prof]
    style = model["style"]
    host = model["host"]
    nodes = model["nodes"]
    shared = list(model.get("shared") or [])
    src = cites.sources_line()
    sub = str(model.get("subtitle", "") or "")
    model = dict(model, subtitle=(sub + " " if sub else "") + src)
    names = [str(host["label"])] + [str(n.get("label")) for n in nodes if not n.get("more")]
    f = make_fig(model, "topology", 640, names=names)
    for msg in cites.todo():
        f.problem(msg)
    W = f.body_w
    small, mono = k["small"], k["mono"]
    chain = model.get("chain") or {}
    ret = style == "chain" and bool(chain.get("host_in"))
    ns = len(shared)
    # Rails on the right: spaced so that their names, written above them, do not touch.
    rsp = max([text_width(s, small, 700) for s in shared] + [24]) + 12
    pu = model.get("pullups")
    ends = model.get("ends")
    rails_w = ns * rsp
    x_card = 30.0 if ret else 0.0
    stub = 26.0
    card_w = W - x_card - rails_w - stub - (8 if ends else 0)
    if card_w < 220:
        f.problem(f"the cards are {card_w:.0f} px wide; use fewer or shorter shared line names")
    top = 0.0
    if shared:
        top = small * 1.3 + 10 + (18 if ends else 0)  # the rail names (and a terminator above the host)
        if pu:
            top += 58  # the pull-up resistors and the supply bar above the host
    G = (mono * 1.4 + 26) if style == "chain" else 18.0

    def lines_of(item) -> list[str]:
        out = []
        if item.get("address") not in (None, ""):
            out.append(str(item["address"]))
        if item.get("detail"):
            out.append(str(item["detail"]))
        return out

    entries = [(host, True)] + [(nd, False) for nd in nodes]
    boxes = []
    y = top
    for item, is_host in entries:
        more = bool(item.get("more"))
        tone = item.get("tone", "blue" if is_host else "teal")
        b = f.card(x_card, y, card_w, str(item.get("label") or "…"), lines_of(item), tone=tone, accent=not more,
                   dashed=more)
        boxes.append((b, item, more))
        y = b.b + G
    host_box = boxes[0][0]
    bottom = boxes[-1][0].b
    ax = x_card + 44  # the chain arrows run down this line
    if style == "chain":
        prev, prev_more = host_box, False
        for i, (b, item, more) in enumerate(boxes[1:]):
            dashed = more or prev_more
            f.edge([(ax, prev.b + 3), (ax, b.y - 3)], tone="brand", dashed=dashed)
            src_pin = str(chain["host_out"]) if i == 0 else str(chain["out"])
            if not dashed:
                f.text(ax + 12, (prev.b + b.y) / 2 + mono * 0.36, f"{src_pin} → {chain['in']}", size=mono,
                       weight=600, mono=True, color="ink2")
            prev, prev_more = b, more
        if ret:
            last = boxes[-1][0]
            yb = last.b + 18
            f.edge([(ax, last.b + 3), (ax, yb), (8, yb), (8, host_box.cy), (x_card - 3, host_box.cy)], tone="brand")
            f.text(ax + 12, yb + mono * 0.36, f"{chain['out']} → {chain['host_in']}", size=mono, weight=600, mono=True,
                   color="ink2")
            bottom = yb + mono
        if chain.get("label"):
            bottom += 10
            for ln in wrap(str(chain["label"]), W, small):
                f.text(0, bottom + small * 1.1, ln, size=small, color="muted")
                bottom += small * 1.4
    if shared:
        rx0 = x_card + card_w + stub
        rx = [rx0 + rsp / 2 + i * rsp for i in range(ns)]
        cards = [(b, more) for b, _it, more in boxes]
        r_top = host_box.y + 8
        r_bot = cards[-1][0].b - 8
        if ends:
            r_top, r_bot = host_box.y - 10, cards[-1][0].b + 10
        if pu:
            r_top = host_box.y - 52
        for i, name in enumerate(shared):
            f.line([(rx[i], r_top), (rx[i], r_bot)], color="ink2", sw=2.2, layer="edge")
            f.nontext("ink2", ("canvas",), f"rail {name}")
            f.text(rx[i], r_top - 8 if not pu else r_top - 26, name, size=small, weight=700, color="ink",
                   anchor="middle")
            for j, (b, more) in enumerate(cards):
                sy = b.y + 16 + i * 10 if b.h > 40 + ns * 10 else b.cy
                f.line([(b.r, sy), (rx[i], sy)], color="ink2", sw=1.8, dash="5 4" if more else None, layer="edge")
                f.circle(rx[i], sy, 3.6, fill="ink2", layer="label")
        if ends and ns == 2:
            for ey, where_ in ((r_top + 2, "top"), (r_bot - 2, "bottom")):
                f.rect(rx[0] + 4, ey - 5, rx[1] - rx[0] - 8, 10, fill="amber.tint", stroke="amber.strong", sw=1.6,
                       rx=2, layer="label")
            f.nontext("amber.strong", ("canvas", "amber.tint"), "terminator")
            lab = f"{ends['label']} at both ends"
            f.text(W, max(bottom, r_bot) + small * 1.3 + 6, lab, size=small, weight=600, color="amber.text",
                   anchor="end")
            bottom = max(bottom, r_bot) + small * 1.3 + 12
        if pu:
            vy = r_top - 10
            f.line([(rx[0] - 10, vy), (rx[-1] + 10, vy)], color="ink2", sw=2.0, layer="edge")
            for i in range(ns):
                f.line([(rx[i], vy), (rx[i], r_top)], color="ink2", sw=1.6, layer="edge")
                f.rect(rx[i] - 4, r_top + 6, 8, 22, fill="amber.tint", stroke="amber.strong", sw=1.4, rx=2,
                       layer="label")
            f.nontext("amber.strong", ("canvas", "amber.tint"), "pull-up")
            for j, ln in enumerate(wrap(str(pu["label"]), rx0 - 24, small, 600)[:2]):
                f.text(rx0 - 14, vy - 2 + j * small * 1.3, ln, size=small, weight=600, color="amber.text",
                       anchor="end")
    facts = model.get("facts") or []
    if facts:
        y = bottom + 22
        lines = []
        for ft in facts:
            r = cites.refs.get(str(ft.get("ref"))) if ft.get("ref") else None
            lines.append(str(ft["text"]).rstrip(".") + (f" ({r.short()})" if r else "") + ".")
        f.note(0, y, W, " ".join(lines), tone="slate", title="Limits")
    return f
