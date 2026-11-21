"""``timing``: bus waveforms (SPI, I2C, UART, RS-485, CAN, single-wire) and protocol transactions, every number cited.

Model::

    kind: timing
    id: spi-timing
    title: SPI timing
    alt: One sentence.
    reads: Two or more sentences naming every signal.
    bus: spi                                    # spi, i2c, uart, rs485, can, single-wire, transaction or other
    mode: {cpol: 0, cpha: 0}                    # SPI only: the clock signal must idle at cpol
    refs:                                       # optional: names not here are looked up in docs/hardware.yml refs
      timing: {doc: ds, section: "7.6 Timing requirements", page: 9}
    signals:                                    # one lane each; the wave has one character per time slot
      - {id: cs, label: CS, wave: "1.0........1."}
      - {id: sck, label: SCK, wave: "0..pppppppp0.", clock: true}
      - {id: sdi, label: SDI, wave: "x..========x.", data: [A7, A6, A5, A4, A3, A2, A1, A0]}
    groups:                                     # optional brackets over slots, above the lanes
      - {from: 3, to: 11, label: "address byte"}
    params:                                     # every number of the figure: min, typ or max, unit and ref
      - {id: tcss, symbol: tCSS, label: CS low to the first SCK edge, min: 20, unit: ns, ref: timing}
    marks:                                      # a dimension arrow under a lane, from and to in slots
      - {param: tcss, signal: cs, from: 1, to: 3}
    notes:
      - {text: "Data is sampled on the rising edge.", ref: timing}   # a note with a number must cite it

Wave characters: ``0`` low, ``1`` high, ``l`` and ``h`` the same, ``p`` one clock period starting high, ``n`` one
starting low, ``z`` released (high impedance), ``x`` undefined, ``=`` a data or field slot (labelled from ``data``,
a string or ``{text, tone}``), ``.`` extends the previous slot (a ``p`` or ``n`` repeats), ``|`` a gap (time left out).
A number anywhere (a param, a group or a note) without a datasheet reference fails the build.
"""

from __future__ import annotations

from ..core import PROFILES, text_width, wrap
from ._cite import Citations, has_number
from ._common import Check, check_header, make_fig

REQUIRED = {"signals"}
ALLOWED = {"bus", "mode", "refs", "groups", "params", "marks", "notes", "slots"}
BUSES = ("spi", "i2c", "uart", "rs485", "can", "single-wire", "transaction", "other")
WAVE = set("01lhpnzx=.|")
LANE_H = 36.0
GAP = 12.0


def _segments(wave: str) -> list[dict]:
    """The wave as segments ``{c, a, b}``, ``a`` and ``b`` in slots. ``.`` extends the previous segment (after ``p`` or
    ``n`` it repeats the pulse); ``|`` is a slot of its own that carries the line on (``gap``) under a break mark."""
    segs: list[dict] = []
    for i, ch in enumerate(wave):
        if ch == "|":
            if segs:
                base = segs[-1]["c"] if segs[-1]["c"] != "gap" else segs[-1]["of"]
                segs.append({"c": "gap", "of": base, "a": i, "b": i + 1})
            continue
        if ch == ".":
            if not segs:
                continue
            if segs[-1]["c"] in "pn":
                segs.append({"c": segs[-1]["c"], "a": i, "b": i + 1})
            else:
                segs[-1]["b"] = i + 1
            continue
        segs.append({"c": {"h": "1", "l": "0"}.get(ch, ch), "a": i, "b": i + 1})
    return segs


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def value_text(p: dict) -> str:
    """``min 20 ns``, ``min 20 · max 50 ns``, ``typ 1.25 µs``."""
    parts = [f"{k} {_fmt(p[k])}" for k in ("min", "typ", "max") if p.get(k) not in (None, "")]
    return " · ".join(parts) + (f" {p['unit']}" if p.get("unit") else "")


def validate(model: dict, where: str, root=None) -> Citations:
    c = Check(where, model)
    check_header(c, model, "timing", REQUIRED, ALLOWED)
    cites = Citations(c, model, root)
    bus = model.get("bus", "other")
    if bus not in BUSES:
        c.bad(f"model.bus: one of {', '.join(BUSES)}")
    sigs = model.get("signals") or []
    if not isinstance(sigs, list) or not sigs:
        c.bad("signals: at least one signal")
        sigs = []
    ids: list[str] = []
    slots = 0
    clock_ids = []
    for i, s in enumerate(sigs):
        p = f"signals[{i}]"
        if not c.keys(s, p, {"id", "wave"}, {"label", "data", "tone", "clock"}):
            continue
        sid = str(s["id"])
        if sid in ids:
            c.bad(f"{p}.id: {sid!r} is listed twice")
        ids.append(sid)
        c.tone(s, p, default="blue")
        w = str(s["wave"]).replace(" ", "")
        bad = sorted(set(w) - WAVE)
        if bad:
            c.bad(f"{p}.wave: unknown character(s) {''.join(bad)!r} (allowed: 0 1 l h p n z x = . |)")
        if w[:1] in (".", "|"):
            c.bad(f"{p}.wave: must not start with '.' or '|'")
        slots = max(slots, len(w))
        need = w.count("=")
        data = s.get("data") or []
        if not isinstance(data, list):
            c.bad(f"{p}.data: a list")
            data = []
        if len(data) != need:
            c.bad(f"{p}.data: {len(data)} label(s) for {need} '=' slot(s)")
        for j, d in enumerate(data):
            if isinstance(d, dict):
                c.keys(d, f"{p}.data[{j}]", {"text"}, {"tone"})
                c.tone(d, f"{p}.data[{j}]", default="blue")
        if s.get("clock"):
            clock_ids.append((sid, w))
    n = model.get("slots")
    if n is not None:
        if not isinstance(n, int) or n < slots:
            c.bad(f"model.slots: at least the longest wave ({slots})")
    for sid, w in [(str(s.get("id")), str(s.get("wave", "")).replace(" ", "")) for s in sigs if isinstance(s, dict)]:
        if n is None and len(w) != slots:
            c.bad(f"signal {sid!r}: wave is {len(w)} slots, the longest is {slots}; give every wave the same length")
    mode = model.get("mode")
    if mode is not None:
        if bus != "spi":
            c.bad("model.mode: only for bus: spi")
        elif c.keys(mode, "mode", {"cpol", "cpha"}, set()):
            if mode["cpol"] not in (0, 1) or mode["cpha"] not in (0, 1):
                c.bad("mode: cpol and cpha are 0 or 1")
            elif not clock_ids:
                c.bad("mode: mark the clock signal with clock: true")
            else:
                for sid, w in clock_ids:
                    first = {"h": "1", "l": "0"}.get(w[:1], w[:1])
                    if first in "01" and int(first) != mode["cpol"]:
                        c.bad(f"signal {sid!r}: SPI mode with CPOL {mode['cpol']} idles "
                              f"{'high' if mode['cpol'] else 'low'}, the wave starts {first}")
    params: dict[str, dict] = {}
    for i, p in enumerate(model.get("params") or []):
        q = f"params[{i}]"
        if not c.keys(p, q, {"id", "symbol", "label", "unit", "ref"}, {"min", "typ", "max", "note"}):
            if isinstance(p, dict) and "ref" not in p:
                pass  # the missing ref is already listed
            continue
        if p["id"] in params:
            c.bad(f"{q}.id: {p['id']!r} is listed twice")
        params[str(p["id"])] = p
        vals = [p.get(k) for k in ("min", "typ", "max")]
        if all(v in (None, "") for v in vals):
            c.bad(f"{q}: give min, typ or max")
        for k in ("min", "typ", "max"):
            v = p.get(k)
            if v not in (None, "") and not isinstance(v, (int, float, str)) or isinstance(v, bool):
                c.bad(f"{q}.{k}: a number")
        nums = [p[k] for k in ("min", "max") if isinstance(p.get(k), (int, float)) and not isinstance(p.get(k), bool)]
        if len(nums) == 2 and nums[0] > nums[1]:
            c.bad(f"{q}: min is above max")
        cites.use(p.get("ref"), f"{q}.ref", f"{p.get('symbol')}")
    for i, m in enumerate(model.get("marks") or []):
        q = f"marks[{i}]"
        if not c.keys(m, q, {"param", "signal", "from", "to"}, set()):
            continue
        if str(m["param"]) not in params:
            c.bad(f"{q}.param: {m['param']!r} is not under params (every drawn interval names a cited value)")
        if str(m["signal"]) not in ids:
            c.bad(f"{q}.signal: unknown signal {m['signal']!r}")
        a, b = m["from"], m["to"]
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (a, b)):
            c.bad(f"{q}: from and to are slot positions (numbers)")
        elif not (0 <= a < b <= max(slots, n or 0)):
            c.bad(f"{q}: from and to must be inside the waves and from below to")
    for i, g in enumerate(model.get("groups") or []):
        q = f"groups[{i}]"
        if c.keys(g, q, {"from", "to", "label"}, {"ref", "tone"}):
            c.tone(g, q, default="slate")
            if not (isinstance(g["from"], (int, float)) and isinstance(g["to"], (int, float))
                    and 0 <= g["from"] < g["to"] <= max(slots, n or 0)):
                c.bad(f"{q}: from and to must be inside the waves and from below to")
            cites.text_needs_ref(g, q, ("label",))
    for i, nt in enumerate(model.get("notes") or []):
        q = f"notes[{i}]"
        if isinstance(nt, str):
            if has_number(nt):
                c.bad(f"{q}: a note with a number needs a ref ({{text: ..., ref: ...}})")
            continue
        if c.keys(nt, q, {"text"}, {"ref"}):
            cites.text_needs_ref(nt, q, ("text",))
    c.done()
    return cites


def _hatch(f, a: float, b: float, top: float, bot: float) -> None:
    """Diagonal hatching inside ``[a, b] x [top, bot]``, every 7 px."""
    h = bot - top
    x = a - h
    while x < b:
        x0, y0, x1, y1 = x, bot, x + h, top
        if x0 < a:
            y0 -= a - x0
            x0 = a
        if x1 > b:
            y1 += x1 - b
            x1 = b
        if x1 > x0:
            f.line([(x0, y0), (x1, y1)], color="rail", sw=1.0, layer="edge")
        x += 7


def build(model: dict, lock_dir, where: str = "model", root=None):
    cites = validate(model, where, root)
    prof = model.get("profile", "phone")
    model = dict(model, profile=prof)
    k = PROFILES[prof]
    sigs = model["signals"]
    slots = int(model.get("slots") or max(len(str(s["wave"]).replace(" ", "")) for s in sigs))
    params = {str(p["id"]): p for p in model.get("params") or []}
    sub = str(model.get("subtitle", "") or "")
    mode = model.get("mode")
    if mode:
        m = mode["cpol"] * 2 + mode["cpha"]
        sub = (sub + " " if sub else "") + f"SPI mode {m} (CPOL {mode['cpol']}, CPHA {mode['cpha']})."
    src = cites.sources_line()
    model = dict(model, subtitle=(sub + " " if sub else "") + src)
    names = [str(s.get("label", s["id"])) for s in sigs]
    f = make_fig(model, "timing", 640, names=names)
    for msg in cites.todo():
        f.problem(msg)
    W = f.body_w
    mono, small = k["mono"], k["small"]
    lab_w = max(text_width(nm, mono, 700, True) for nm in names) + 14
    x0, x1 = max(56.0, lab_w), W - 6
    sw = (x1 - x0) / slots

    def X(t: float) -> float:
        return x0 + t * sw

    if sw < 10:
        f.problem(f"{slots} slots leave {sw:.1f} px each; split the figure or use fewer slots (10 px at least)")
    y = 4.0
    # Groups: brackets above the lanes, packed into rows.
    groups = model.get("groups") or []
    rows: list[list[tuple[float, float]]] = []
    placed = []
    for g in groups:
        a, b = X(g["from"]), X(g["to"])
        lw = text_width(str(g["label"]), small, 600)
        lo, hi = min(a, (a + b) / 2 - lw / 2), max(b, (a + b) / 2 + lw / 2)
        if lo < 0 or hi > W:
            f.problem(f"group {g['label']!r} runs past the figure")
        r = next((i for i, row in enumerate(rows) if all(hi + 8 < s or lo - 8 > e for s, e in row)), None)
        if r is None:
            rows.append([])
            r = len(rows) - 1
        rows[r].append((lo, hi))
        placed.append((g, r))
    GH = small * 1.3 + 14
    for g, r in placed:
        gy = y + (len(rows) - 1 - r) * GH
        a, b = X(g["from"]), X(g["to"])
        tone = g.get("tone", "slate")
        f.text((a + b) / 2, gy + small * 0.95, str(g["label"]), size=small, weight=600, color=f"{tone}.text",
               anchor="middle")
        by = gy + small * 1.3 + 6
        f.line([(a + 1, by + 5), (a + 1, by), (b - 1, by), (b - 1, by + 5)], color=f"{tone}.strong", sw=1.4,
               layer="edge")
        f.nontext(f"{tone}.strong", ("canvas",), f"bracket {g['label']!r}")
    y += len(rows) * GH + (6 if rows else 0)
    grid_top = y
    marks_by: dict[str, list] = {}
    for m in model.get("marks") or []:
        marks_by.setdefault(str(m["signal"]), []).append(m)
    MH = small * 1.3 + 16
    lane_mid: dict[str, float] = {}
    lane_spans = []
    edge_x: list[float] = []
    for s in sigs:
        sid = str(s["id"])
        tone = s.get("tone", "blue")
        w = str(s["wave"]).replace(" ", "")
        hi_y, lo_y, mid = y + 5, y + LANE_H - 5, y + LANE_H / 2
        lane_mid[sid] = mid
        f.text(0, mid + mono * 0.36, str(s.get("label", sid)), size=mono, weight=700, mono=True)
        segs = _segments(w)
        data = list(s.get("data") or [])
        di = 0
        run: list[tuple[float, float]] = []  # the polyline of consecutive digital levels
        level = None

        def flush():
            nonlocal run
            if len(run) > 1:
                f.line(run, color="ink2", sw=2.0, layer="edge")
            run = []

        gaps = []
        for sg in segs:
            a, b, ch = X(sg["a"]), X(sg["b"]), sg["c"]
            if ch == "gap":
                gaps.append((a + b) / 2)
                of = sg["of"]
                if of in "01pn" and level in (0, 1):
                    ly = hi_y if level else lo_y
                    run = run + [(b, ly)] if run else [(a, ly), (b, ly)]
                    continue
                flush()
                if of == "=":
                    f.line([(a, hi_y), (b, hi_y)], color="ink2", sw=1.6, layer="edge")
                    f.line([(a, lo_y), (b, lo_y)], color="ink2", sw=1.6, layer="edge")
                elif of == "x":
                    f.rect(a, hi_y, b - a, lo_y - hi_y, fill="paper", stroke=None, rx=0, layer="region")
                    _hatch(f, a, b, hi_y, lo_y)
                else:
                    f.line([(a, mid), (b, mid)], color="rail", sw=2.0, layer="edge")
                continue
            if ch in "01pn":
                parts = ([(a, b, int(ch))] if ch in "01" else
                         [(a, (a + b) / 2, 1 if ch == "p" else 0), ((a + b) / 2, b, 0 if ch == "p" else 1)])
                for pa, pb, lv in parts:
                    ly = hi_y if lv else lo_y
                    if not run:
                        run = [(pa, ly)] if level is None or level == "other" else [(pa, mid), (pa, ly)]
                    elif level != lv:
                        run += [(pa, hi_y if level else lo_y), (pa, ly)]
                        edge_x.append(pa)
                    run.append((pb, ly))
                    level = lv
                continue
            flush()
            if level in (0, 1) and ch in "zx=":
                f.line([(a, hi_y if level else lo_y), (a, mid)], color="ink2", sw=2.0, layer="edge")
            level = "other"
            if ch == "z":
                f.line([(a, mid), (b, mid)], color="rail", sw=2.0, layer="edge")
                f.nontext("rail", ("canvas",), f"released line of {sid}")
            elif ch == "x":
                f.rect(a, hi_y, b - a, lo_y - hi_y, fill="paper", stroke=None, rx=0, layer="region")
                _hatch(f, a, b, hi_y, lo_y)
                f.line([(a, hi_y), (b, hi_y)], color="ink2", sw=1.6, layer="edge")
                f.line([(a, lo_y), (b, lo_y)], color="ink2", sw=1.6, layer="edge")
            elif ch == "=":
                d = data[di] if di < len(data) else ""
                di += 1
                txt = str(d.get("text") if isinstance(d, dict) else d)
                dt = (d.get("tone") if isinstance(d, dict) else None) or tone
                e = min(5.0, (b - a) / 4)
                f.path([("M", a, mid), ("L", a + e, hi_y), ("L", b - e, hi_y), ("L", b, mid), ("L", b - e, lo_y),
                        ("L", a + e, lo_y), ("Z",)], stroke=f"{dt}.strong", fill=f"{dt}.tint", sw=1.6, layer="node")
                f.nontext(f"{dt}.strong", ("canvas", f"{dt}.tint"), f"data slot {txt!r} of {sid}")
                size = small
                if text_width(txt, size, 600) > (b - a) - 2 * e - 2:
                    f.problem(f"data {txt!r} of {sid} does not fit its {sg['b'] - sg['a']} slot(s)")
                f.text((a + b) / 2, mid + size * 0.36, txt, size=size, weight=600, color=f"{dt}.text",
                       bg=f"{dt}.tint", anchor="middle")
        flush()
        for gx in gaps:
            if True:
                f.rect(gx - 4, y + 1, 8, LANE_H - 2, fill="canvas", stroke=None, rx=0, layer="label")
                for dx in (-4, 4):
                    f.line([(gx + dx - 3, y + LANE_H - 2), (gx + dx + 3, y + 2)], color="ink2", sw=1.4,
                           layer="label")
        lane_spans.append((y, y + LANE_H))
        y += LANE_H
        # Marks under this lane, packed into rows.
        mrows: list[list[tuple[float, float]]] = []
        mplaced = []
        for m in marks_by.get(sid, []):
            a, b = X(m["from"]), X(m["to"])
            lab = str(params[str(m["param"])]["symbol"])
            lw = text_width(lab, small, 700)
            beside = lw + 8 > b - a  # a label wider than its interval sits right of the arrow, not across the guides
            lo, hi = (a, b + 6 + lw) if beside else (a, b)
            if lo < 0 or hi > W:
                f.problem(f"mark {lab!r} runs past the figure")
            r = next((i for i, row in enumerate(mrows) if all(hi + 10 < s_ or lo - 10 > e_ for s_, e_ in row)), None)
            if r is None:
                mrows.append([])
                r = len(mrows) - 1
            mrows[r].append((lo, hi))
            mplaced.append((m, r, a, b, lab, beside))
        for m, r, a, b, lab, beside in mplaced:
            ry = y + 4 + r * MH
            ay = ry + small * 1.3 + 8
            for gx in (a, b):
                f.line([(gx, mid), (gx, ay + 4)], color="rail", sw=1.0, dash="3 3", layer="bg")
            if beside:
                f.text(b + 6, ay + small * 0.36, lab, size=small, weight=700, color="ink")
            else:
                f.text((a + b) / 2, ry + small * 0.95, lab, size=small, weight=700, color="ink", anchor="middle")
            if b - a >= 22:
                f.edge([(a + 1, ay), (b - 1, ay)], tone="ink2", arrow="both", sw=1.4)
            else:
                f.line([(a, ay), (b, ay)], color="ink2", sw=1.4, layer="edge")
                for gx in (a, b):
                    f.line([(gx, ay - 4), (gx, ay + 4)], color="ink2", sw=1.4, layer="edge")
                f.nontext("ink2", ("canvas",), f"interval {lab}")
        y += len(mrows) * MH + GAP
    # A faint slot grid behind the lanes.
    if slots <= 48:
        for i in range(slots + 1):
            f.line([(X(i), grid_top), (X(i), y - GAP)], color="hair", sw=1.0, layer="bg")
    # The values: one block per parameter, symbol and value, then what it is and where it comes from.
    ps = model.get("params") or []
    if ps:
        y += 4
        f.text(0, y + k["card_title"] * 0.85, "Timing values" if model.get("bus") != "transaction" else "Values",
               size=k["card_title"], weight=700)
        y += k["card_title"] * 1.3 + 8
        for p in ps:
            f.line([(0, y), (W, y)], color="hair", sw=1.0, layer="bg")
            y += 8
            sym = str(p["symbol"])
            val = value_text(p)
            f.text(0, y + mono * 0.85, sym, size=mono, weight=700, mono=True)
            vw = text_width(val, k["card_body"], 700)
            if text_width(sym, mono, 700, True) + vw + 16 > W:
                f.problem(f"param {sym!r}: symbol and value do not fit one line")
            f.text(W, y + k["card_body"] * 0.85, val, size=k["card_body"], weight=700, color="ink", anchor="end")
            y += max(mono, k["card_body"]) * 1.35
            ref = cites.refs.get(str(p["ref"]))
            text = str(p["label"]) + (f". {p['note']}" if p.get("note") else "")
            for ln in wrap(text, W, k["card_body"]):
                f.text(0, y + k["card_body"] * 0.85, ln, size=k["card_body"], color="ink2")
                y += k["card_body"] * 1.4
            if ref:
                f.text(0, y + small * 0.85, f"Datasheet {ref.long()}", size=small, color="muted")
                y += small * 1.4
            y += 4
        f.line([(0, y), (W, y)], color="hair", sw=1.0, layer="bg")
        f.twin = {"caption": str(model["title"]),
                  "head": ["Symbol", "Parameter", "Min", "Typ", "Max", "Unit", "Datasheet"],
                  "rows": [[str(p["symbol"]), str(p["label"]), _fmt(p.get("min", "")), _fmt(p.get("typ", "")),
                            _fmt(p.get("max", "")), str(p["unit"]),
                            cites.refs[str(p["ref"])].long() if str(p["ref"]) in cites.refs else ""]
                           for p in ps]}
    notes = model.get("notes") or []
    if notes:
        y += 14
        txt = " ".join(str(n["text"] if isinstance(n, dict) else n) for n in notes)
        f.note(0, y, W, txt, tone="slate", title="Notes")
    return f
