#!/usr/bin/env python3
"""``kokeb-docs figkit``: the figure kit's own commands.

    kokeb-docs figkit kinds                      the figure kinds and what each needs
    kokeb-docs figkit new --kind K --id ID [--page PAGE] [--title T]
                                                 scaffold docs/model/ID.K.yml (and an embed marker in PAGE)
    kokeb-docs figkit layout [ID ...] [--check]  run Graphviz `dot` (the only command that does) and write the
                                                 layout locks docs/diagrams/ID.layout.json; --check only reports
                                                 where the installed dot would change a committed lock (exit 0)
    kokeb-docs figkit font [ID ...]              write the font subsets of figures that say `font: embed`
    kokeb-docs figkit css [OUT]                  the shared style sheet for adaptive SVGs inlined in a page

Rendering (``kokeb-docs figures``) never runs Graphviz and never needs fonttools: it reads what these commands wrote.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from . import adaptive, build, fontsubset, layered
from .kinds import KINDS, LAYOUT_KINDS, module

SKELETONS = {
    "state": """states:
  - {id: Idle, tone: slate}
  - {id: Busy, tone: blue}
transitions:
  - {from: "[*]", to: Idle}
  - {from: Idle, to: Busy, label: start}
  - {from: Busy, to: Idle, label: done}
""",
    "graph": """direction: TB
nodes:
  - {id: top, tone: blue, lines: [what it is]}
  - {id: bottom, tone: teal, lines: [what it is]}
edges:
  - {from: top, to: bottom}
""",
    "seq": """participants:
  - {id: caller, label: Caller, tone: blue}
  - {id: callee, label: Callee, tone: green}
steps:
  - {from: caller, to: callee, label: request}
  - {from: callee, to: caller, label: reply, return: true}
""",
    "timeline": """axis: {unit: ms, min: 0, max: 10, ticks: [0, 5, 10]}
lanes:
  - {id: a, label: Lane A, tone: blue}
spans:
  - {lane: a, from: 1, to: 6, label: work, tone: blue}
deadlines:
  - {at: 8, label: deadline}
""",
    "matrix": """rows: [{id: r1, label: Row 1}]
cols: [{id: c1, label: Column 1}, {id: c2, label: Column 2}]
cells:
  - {row: r1, col: c1, status: ok, text: yes}
  - {row: r1, col: c2, status: planned, text: planned}
""",
    "bytes": """row_bytes: 4
size: 8
fields:
  - {at: 0, len: 2, name: magic, note: "0x4A4B", tone: slate}
  - {at: 2, len: 2, name: length, tone: blue}
  - {at: 4, len: 4, name: payload, tone: green}
""",
    "timing": """bus: spi
mode: {cpol: 0, cpha: 0}
refs:
  timing: {doc: ds, section: "TODO the datasheet's timing section", page: 1}
signals:
  - {id: cs, label: CS, wave: "10......1"}
  - {id: sck, label: SCK, wave: "0.pppppp0", clock: true}
  - {id: sdi, label: SDI, wave: "x.======x", data: [D5, D4, D3, D2, D1, D0]}
params:
  - {id: tcss, symbol: tCSS, label: CS low to the first SCK edge, min: 1, unit: ns, ref: timing}
marks:
  - {param: tcss, signal: cs, from: 1, to: 2}
""",
    "topology": """style: bus
refs:
  bus: {doc: ds, section: "TODO the datasheet's section on several devices", page: 1}
host: {label: MCU, detail: bus controller}
nodes:
  - {label: Device A, address: "0x40", ref: bus}
  - {label: Device B, address: "0x41", ref: bus}
shared: [SDA, SCL]
facts:
  - {text: "Up to 2 devices on one bus", ref: bus}
""",
    "pipeline": """columns:
  - id: inputs
    title: Inputs
    tone: blue
    items:
      - {id: source, title: source, lines: [what goes in]}
  - id: outputs
    title: Outputs
    tone: green
    items:
      - {id: result, title: result, lines: [what comes out]}
links:
  - {from: source, to: result, label: builds}
""",
}


def cmd_kinds(_args) -> int:
    for name in KINDS:
        doc = (module(name).__doc__ or "").strip().splitlines()[0]
        print(f"{name:9s} {doc}{'  [layout lock]' if name in LAYOUT_KINDS else ''}")
    return 0


def cmd_new(args) -> int:
    if args.kind not in KINDS:
        print(f"[figkit] unknown kind {args.kind!r}; kinds: {', '.join(KINDS)}", file=sys.stderr)
        return 2
    if not args.id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in args.id):
        print("[figkit] --id: lower case letters, digits and '-' only", file=sys.stderr)
        return 2
    root = build.ROOT
    path = root / "docs/model" / f"{args.id}.{args.kind}.yml"
    if path.exists() or (build.FIG_DIR / f"{args.id}.py").exists():
        print(f"[figkit] {args.id!r} already exists", file=sys.stderr)
        return 1
    title = args.title or args.id.replace("-", " ").capitalize()
    head = (f"---\n# Model of the figure {args.id!r}. Edit this file; `kokeb-docs figures` draws it. Never edit the SVGs.\n"
            f"# Kind {args.kind}: see `kokeb-docs figkit kinds` and docs/figkit.md.\n"
            f"kind: {args.kind}\nid: {args.id}\ntitle: {title}\n"
            "alt: TODO one sentence, 40 to 300 characters, saying what the figure shows\n"
            "reads: >-\n  TODO two or more sentences that name every state, participant, lane or column and say what\n"
            "  the figure tells the reader.\n"
            f"print: landscape\nsources:\n  - docs/model/{args.id}.{args.kind}.yml\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(head + SKELETONS[args.kind], encoding="utf-8")
    print(f"wrote {path.relative_to(root)}")
    marker = f"<!-- figure: {args.id} -->\n<!-- /figure -->\n"
    if args.page:
        page = pathlib.Path(args.page)
        page = page if page.is_absolute() else root / page
        with page.open("a", encoding="utf-8") as fh:
            fh.write("\n" + marker)
        print(f"added the embed marker to {args.page}")
    else:
        print("embed it in a page with:\n" + marker, end="")
    steps = ["edit the model (alt and reads first)"]
    if args.kind in LAYOUT_KINDS:
        steps.append(f"kokeb-docs figkit layout {args.id}      # once; commit docs/diagrams/{args.id}.layout.json")
    steps += ["kokeb-docs figures", "kokeb-docs figures --lint", "kokeb-docs check"]
    print("next:\n  " + "\n  ".join(steps))
    return 0


def _ids(args) -> list[str]:
    known = build.fig_ids()
    bad = [i for i in args.ids if i not in known]
    if bad:
        raise SystemExit(f"[figkit] unknown figure(s): {', '.join(bad)}")
    return args.ids or known


def cmd_layout(args) -> int:
    ids = _ids(args)
    mode = "compare" if args.check else "refresh"
    with layered.layout_mode(mode, ids if args.ids else None) as m:
        for fid in ids:
            fig, _ = build.load(fid)
            fig.problems()
    changed = [d for d in m.diffs]
    for fid, what in changed:
        print(f"[figkit] {fid}: {what}")
    if not changed:
        print(f"[figkit] layout: {len(ids)} figure(s), nothing to change (dot {layered.dot_version()})")
    return 0


def cmd_font(args) -> int:
    n = 0
    for fid in _ids(args):
        fig, _ = build.load(fid)
        if fig.font:
            print(f"[figkit] {fid}: font subset {fontsubset.write_lock(build.DIAGRAMS, fid, fig.svg('light'))}")
            n += 1
    if not n:
        print("[figkit] no figure asks for font: embed")
    return 0


def cmd_css(args) -> int:
    css = adaptive.adaptive_css()
    if args.out:
        pathlib.Path(args.out).write_text(css, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(css, end="")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kokeb-docs figkit", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("kinds").set_defaults(fn=cmd_kinds)
    p = sub.add_parser("new")
    p.add_argument("--kind", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--title")
    p.add_argument("--page")
    p.set_defaults(fn=cmd_new)
    p = sub.add_parser("layout")
    p.add_argument("ids", nargs="*")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_layout)
    p = sub.add_parser("font")
    p.add_argument("ids", nargs="*")
    p.set_defaults(fn=cmd_font)
    p = sub.add_parser("css")
    p.add_argument("out", nargs="?")
    p.set_defaults(fn=cmd_css)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
