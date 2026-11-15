"""``timeline``: swim lanes against a time axis: spans (bars), events (marks) and deadline lines.

Model::

    kind: timeline
    id: transfer-deadline
    title: ...
    alt: One sentence.
    reads: Two or more sentences naming every lane.
    axis: {unit: us, min: 0, max: 100, ticks: [0, 25, 50, 75, 100]}
    lanes:
      - {id: cpu, label: CPU, tone: blue}
    spans:
      - {lane: cpu, from: 0, to: 20, label: prepare, tone: blue}       # status: ok|warn|fail|planned|na instead of tone
    events:
      - {lane: cpu, at: 50, label: start, tone: green}
    deadlines:
      - {at: 80, label: deadline}
"""

from __future__ import annotations

from ..core import PROFILES, text_width
from ._common import Check, check_header, make_fig

REQUIRED = {"axis", "lanes"}
ALLOWED = {"spans", "events", "deadlines"}
LANE_H = 64.0
LABEL_W = 120.0


def validate(model: dict, where: str) -> None:
    c = Check(where, model)
    check_header(c, model, "timeline", REQUIRED, ALLOWED)
    ax = model.get("axis") or {}
    c.keys(ax, "axis", {"min", "max"}, {"unit", "ticks"})
    if isinstance(ax.get("min"), (int, float)) and isinstance(ax.get("max"), (int, float)) and ax["max"] <= ax["min"]:
        c.bad("axis: max must be above min")
    lanes = []
    for i, l in enumerate(model.get("lanes") or []):
        p = f"lanes[{i}]"
        if c.keys(l, p, {"id"}, {"label", "tone"}):
            c.tone(l, p)
            lanes.append(str(l["id"]))
    for i, s in enumerate(model.get("spans") or []):
        p = f"spans[{i}]"
        if c.keys(s, p, {"lane", "from", "to", "label"}, {"tone", "status"}):
            if str(s["lane"]) not in lanes:
                c.bad(f"{p}.lane: unknown lane")
            elif s["to"] <= s["from"]:
                c.bad(f"{p}: to must be above from")
    for i, e in enumerate(model.get("events") or []):
        p = f"events[{i}]"
        if c.keys(e, p, {"lane", "at", "label"}, {"tone", "status"}) and str(e["lane"]) not in lanes:
            c.bad(f"{p}.lane: unknown lane")
    for i, d in enumerate(model.get("deadlines") or []):
        c.keys(d, f"deadlines[{i}]", {"at", "label"}, {"tone"})
    c.done()


def build(model: dict, lock_dir, where: str = "model"):
    validate(model, where)
    k = PROFILES[model.get("profile", "detail")]
    ax = model["axis"]
    lanes = model["lanes"]
    f = make_fig(model, "timeline", 1000, names=[str(l.get("label", l["id"])) for l in lanes])
    plot_x0, plot_x1 = LABEL_W + 16, f.body_w - 16
    t = lambda v: plot_x0 + (v - ax["min"]) / (ax["max"] - ax["min"]) * (plot_x1 - plot_x0)  # noqa: E731
    top = 36.0
    lane_y = {str(l["id"]): top + i * LANE_H for i, l in enumerate(lanes)}
    bottom = top + len(lanes) * LANE_H
    unit = str(ax.get("unit", "") or "")
    ticks = ax.get("ticks") or [ax["min"], ax["max"]]
    for v in ticks:
        f.line([(t(v), top - 6), (t(v), bottom)], color="hair", sw=1.0, layer="bg")
        f.text(t(v), top - 12, f"{v:g}", size=k["small"], color="muted", anchor="middle")
    if unit:
        f.text(plot_x1, bottom + 22, unit, size=k["small"], color="muted", anchor="end")
    for l in lanes:
        y = lane_y[str(l["id"])]
        tone = l.get("tone", "slate")
        f.rect(0, y + 2, plot_x1 + 16, LANE_H - 4, fill=f"{tone}.tint", stroke=f"{tone}.soft", layer="region", sw=1.0)
        f.text(12, y + LANE_H / 2 + 5, str(l.get("label", l["id"])), size=k["card_title"], weight=700,
               color=f"{tone}.text", bg=f"{tone}.tint")
    for s in model.get("spans") or []:
        y = lane_y[str(s["lane"])]
        tone = s.get("status") or s.get("tone") or "slate"
        x0, x1 = t(s["from"]), t(s["to"])
        w = x1 - x0
        f.rect(x0, y + 12, w, LANE_H - 24, fill=f"{tone}.tint", stroke=f"{tone}.strong", sw=1.4, layer="node")
        f.nontext(f"{tone}.strong", ("canvas", f"{tone}.tint"), f"span {s['label']!r}")
        lab = str(s["label"])
        if text_width(lab, k["card_body"], 600) + 12 > w:
            f.problem(f"span {lab!r} is {w:.0f} px wide, its label needs {text_width(lab, k['card_body'], 600) + 12:.0f}")
        f.text((x0 + x1) / 2, y + LANE_H / 2 + 4, lab, size=k["card_body"], weight=600, color=f"{tone}.text",
               bg=f"{tone}.tint", anchor="middle")
    for e in model.get("events") or []:
        y = lane_y[str(e["lane"])]
        tone = e.get("status") or e.get("tone") or "slate"
        x = t(e["at"])
        f.circle(x, y + LANE_H / 2, 7, fill=f"{tone}.strong", stroke="canvas", sw=2)
        f.nontext(f"{tone}.strong", ("canvas", f"{tone}.tint"), f"event {e['label']!r}")
        f.text(x, y + 14, str(e["label"]), size=k["small"], color=f"{tone}.text", bg=f"{tone}.tint", anchor="middle")
    for d in model.get("deadlines") or []:
        x = t(d["at"])
        tone = d.get("tone", "rose")
        f.line([(x, top - 6), (x, bottom + 4)], color=f"{tone}.strong", sw=2.0, dash="7 5", layer="edge")
        f.nontext(f"{tone}.strong", ("canvas",), f"deadline {d['label']!r}")
        f.text(x, bottom + 22, str(d["label"]), size=k["small"], weight=700, color=f"{tone}.text", anchor="middle")
    return f
