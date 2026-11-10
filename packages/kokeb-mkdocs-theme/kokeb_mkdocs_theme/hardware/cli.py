"""``kokeb-docs hardware``: check docs/hardware.yml, export a circuit, or draw the chip figures anywhere.

Usage (from anywhere in the repository)::

    kokeb-docs hardware --check                          validate the file and every circuit (CI)
    kokeb-docs hardware --list                           the figures and circuits it describes
    kokeb-docs hardware --kicad-netlist OUT.net [--circuit ID]
                                                         a circuit as a KiCad netlist (the first circuit by default)
    kokeb-docs hardware --svg DIR                        the chip figures, light and dark, into DIR

The figures themselves are built and drift-checked with the other figures by ``kokeb-docs figures``; ``--svg`` is
for a schematic wanted outside the site (a review, a board design note).
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from . import model, netlist, render


def check(root: pathlib.Path) -> list[str]:
    """Every problem of docs/hardware.yml: schema, references, hooks, circuits, and each figure's own checks."""
    try:
        hw = model.load(root)
    except model.HardwareError as e:
        return e.problems
    problems = []
    for c in hw.circuits:
        problems += netlist.check(hw, c)
    for fid in render.figure_ids(hw):
        problems += [f"{fid}: {p}" for p in render.build(hw, fid).problems()]
    return problems


def main(argv=None) -> int:
    from ..paths import repo_root

    ap = argparse.ArgumentParser(prog="kokeb-docs hardware", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate docs/hardware.yml (CI)")
    ap.add_argument("--list", action="store_true", help="list the figures and circuits")
    ap.add_argument("--kicad-netlist", metavar="OUT", help="write a circuit as a KiCad netlist")
    ap.add_argument("--circuit", metavar="ID", help="the circuit to export (default: the first)")
    ap.add_argument("--svg", metavar="DIR", help="write the chip figures, light and dark, into DIR")
    args = ap.parse_args(argv)
    root = repo_root()
    if not (root / model.SOURCE).is_file():
        print(f"[hardware] no {model.SOURCE} in {root}", file=sys.stderr)
        return 2
    if args.check:
        problems = check(root)
        for p in problems:
            print(f"[hardware] ERROR {p}", file=sys.stderr)
        if problems:
            return 1
        hw = model.load(root)
        print(f"[hardware] OK: {len(hw.pins)} pins, {len(hw.hooks)} hooks, {len(hw.blocks)} blocks, "
              f"{len(hw.circuits)} circuit(s)")
        return 0
    try:
        hw = model.load(root)
    except model.HardwareError as e:
        for p in e.problems:
            print(f"[hardware] ERROR {p}", file=sys.stderr)
        return 1
    if args.list:
        for fid in render.figure_ids(hw):
            print(fid)
        for c in hw.circuits:
            print(f"circuit {c.id}: {c.title} ({len(c.parts)} parts, {len(c.nets)} nets)")
        return 0
    if args.kicad_netlist:
        circ = hw.circuits[0] if hw.circuits and not args.circuit else next(
            (c for c in hw.circuits if c.id == args.circuit), None)
        if circ is None:
            print(f"[hardware] no circuit {args.circuit or ''!r} (have: {', '.join(c.id for c in hw.circuits)})",
                  file=sys.stderr)
            return 2
        problems = netlist.check(hw, circ)
        for p in problems:
            print(f"[hardware] ERROR {p}", file=sys.stderr)
        if problems:
            return 1
        out = pathlib.Path(args.kicad_netlist)
        out.write_text(netlist.kicad_netlist(hw, circ))
        print(f"  wrote {out} (circuit {circ.id}, {len(circ.parts)} parts, {len(circ.nets)} nets)")
        return 0
    if args.svg:
        d = pathlib.Path(args.svg)
        d.mkdir(parents=True, exist_ok=True)
        rc = 0
        for fid in render.figure_ids(hw):
            fig = render.build(hw, fid)
            for p in fig.problems():
                print(f"[hardware] ERROR {fid}: {p}", file=sys.stderr)
                rc = 1
            for theme in ("light", "dark"):
                path = d / (f"{fid}.svg" if theme == "light" else f"{fid}.dark.svg")
                path.write_text(fig.svg(theme))
                print(f"  wrote {path}")
        return rc
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
