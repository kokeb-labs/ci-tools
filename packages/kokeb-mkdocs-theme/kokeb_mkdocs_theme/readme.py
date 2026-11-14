#!/usr/bin/env python3
"""``kokeb-docs readme``: keep a driver README chip-first, or move an older one to that layout.

A driver README opens with the chip, not with the software: what the chip is, what it does, where it is used, what
is inside it and how it is wired, then the shortest working code and how the driver covers each function. Every
part of that opening is drawn or generated from ``docs/hardware.yml`` (see ``docs/readme-chip-first.md``)::

    # <Chip> Driver
    <!-- generated: chip-summary -->      the chip in one sentence, with its citation
    (one line on the driver, badges, the documentation link)
    <!-- figure: chip-hero -->            the chip in its system and its headline numbers
    ## What it does                       <!-- figure: chip-capabilities -->
    ## Where it is used                   <!-- generated: chip-uses -->
    ## Inside the chip                    <!-- figure: chip-blocks -->       ("Inside the module" for a module)
    ## Pins and wiring                    <!-- figure: chip-pinout -->, <!-- figure: chip-wiring-<id> -->
    ## Quick start                        <!-- generated: quickstart-code --> (compiled by the host CI)
    ## Driver coverage                    <!-- generated: chip-coverage -->
    ## Documentation                      the page table
    (then, in any order: Datasheet, Try it on your PC, Add it to your project, Tests and quality, License)

Every figure in the README is a chip figure (``chip-*``): the software layering belongs on the architecture page.

Usage (from anywhere in the repository)::

    kokeb-docs readme --check      fail when README.md breaks the layout (run by kokeb-docs check once
                                   docs/hardware.yml has an overview)
    kokeb-docs readme --migrate    rewrite a template README into the layout; then run kokeb-docs figures and
                                   kokeb-docs gen, and read the result: the old chip paragraph lands under
                                   "Driver coverage" for you to trim
"""

from __future__ import annotations

import argparse
import re
import sys

from .paths import repo_root

#: The opening sections, in order: (heading, accepted heading pattern, markers the section must hold).
SECTIONS = [
    ("What it does", r"What it does", ["figure: chip-capabilities"]),
    ("Where it is used", r"Where it is used", ["generated: chip-uses"]),
    ("Inside the chip", r"Inside the (?:chip|module|device|sensor)", ["figure: chip-blocks"]),
    ("Pins and wiring", r"Pins and wiring", ["figure: chip-pinout", "figure: chip-wiring-"]),
    ("Quick start", r"Quick start", ["generated: quickstart-code"]),
    ("Driver coverage", r"Driver coverage", ["generated: chip-coverage"]),
    ("Documentation", r"Documentation", []),
]
TAIL = ["Datasheet", "Try it on your PC", "Add it to your project", "Tests and quality", "License"]

_FENCE = re.compile(r"^\s*(```|~~~)")
_FIGURE = re.compile(r"<!-- figure: (?P<id>[a-z0-9-]+) -->")
_OPEN = re.compile(r"^<!-- (?:(?P<kind>figure|generated): (?P<name>[a-z0-9-]+)|scaffold:(?P<sc>[a-z0-9-]+)) -->\s*$")


def _sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """The lines before the first ``## `` heading, and each ``## `` section as (heading, lines), outside fences."""
    pre: list[str] = []
    secs: list[tuple[str, list[str]]] = []
    fence = False
    for line in text.split("\n"):
        if _FENCE.match(line):
            fence = not fence
        if not fence and line.startswith("## "):
            secs.append((line[3:].strip(), []))
            continue
        (secs[-1][1] if secs else pre).append(line)
    return pre, secs


def check(text: str, hw=None) -> list[str]:
    """Every way ``text`` (a README) breaks the chip-first layout."""
    bad = []
    lines = text.split("\n")
    if not lines or not lines[0].startswith("# "):
        bad.append("line 1 is not the title (# <Chip> Driver)")
    pre, secs = _sections(text)
    pre_text = "\n".join(pre)
    first = next((ln for ln in pre[1:] if ln.strip()), "")
    if first.strip() != "<!-- generated: chip-summary -->":
        bad.append("the first thing under the title is not <!-- generated: chip-summary --> (what the chip is)")
    if "<!-- figure: chip-hero -->" not in pre_text:
        bad.append("no <!-- figure: chip-hero --> before the first section")
    heads = [h for h, _ in secs]
    for i, (name, pattern, markers) in enumerate(SECTIONS):
        if i >= len(heads) or not re.fullmatch(pattern, heads[i]):
            got = heads[i] if i < len(heads) else "nothing"
            bad.append(f"section {i + 1} is {got!r}, the layout needs {name!r} there "
                       f"(order: {', '.join(s[0] for s in SECTIONS)})")
            continue
        body = "\n".join(secs[i][1])
        for m in markers:
            if f"<!-- {m}" not in body:
                bad.append(f"section {name!r} has no <!-- {m}{'<id>' if m.endswith('-') else ''} -->")
    for m in _FIGURE.finditer(text):
        if not m.group("id").startswith("chip-"):
            bad.append(f"figure {m.group('id')!r} in the README: only chip figures (chip-*) belong there; the "
                       "software layering is on the architecture page")
    return bad


# ---------------------------------------------------------------------------------------------------- migrate


def _blocks(lines: list[str]) -> list[list[str]]:
    """Split a section into blocks: a marker pair (figure, generated, scaffold) with its body, a fenced code block,
    or a paragraph; blank lines separate blocks and are dropped."""
    out: list[list[str]] = []
    cur: list[str] = []
    i = 0

    def flush():
        nonlocal cur
        if cur:
            out.append(cur)
            cur = []

    while i < len(lines):
        ln = lines[i]
        m = _OPEN.match(ln)
        if m and not cur:
            end = "<!-- /figure -->" if m.group("kind") == "figure" else (
                "<!-- /generated -->" if m.group("kind") == "generated" else f"<!-- /scaffold:{m.group('sc')} -->")
            j = i
            while j < len(lines) and lines[j].strip() != end:
                j += 1
            out.append(lines[i:j + 1])
            i = j + 1
            continue
        if _FENCE.match(ln):
            j = i + 1
            while j < len(lines) and not _FENCE.match(lines[j]):
                j += 1
            cur += lines[i:j + 1]
            i = j + 1
            continue
        if not ln.strip():
            flush()
        else:
            cur.append(ln)
        i += 1
    flush()
    return out


def _wrap(para: str) -> list[str]:
    import textwrap

    return textwrap.wrap(para, 120, break_long_words=False, break_on_hyphens=False)


def _text_of(block: list[str]) -> str:
    """The first line of a block that is not a marker (a scaffold block wraps a paragraph)."""
    return next((x for x in block if not x.startswith("<!--")), "")


def _name(block: list[str]) -> str:
    m = _OPEN.match(block[0]) if block else None
    if not m:
        return ""
    return f"{m.group('kind')}:{m.group('name')}" if m.group("kind") else f"scaffold:{m.group('sc')}"


def _join(blocks: list[list[str]]) -> list[str]:
    out: list[str] = []
    for b in blocks:
        out += b + [""]
    return out


def migrate(text: str, hw) -> str:
    """``text`` (a README made by the driver template) in the chip-first layout. Nothing is lost: a block the
    layout has no place for keeps its section, after the opening ones. A README already in the layout is returned
    unchanged."""
    if not check(text, hw):
        return text
    pre, secs = _sections(text)
    title = pre[0]
    pre_blocks = _blocks(pre[1:])
    keep_pre, intro = [], []
    for b in pre_blocks:
        n = _name(b)
        if n.startswith("figure:") and not n.startswith("figure:chip-"):
            continue  # the software layering figure leaves the README
        if n in ("generated:chip-summary", "figure:chip-hero"):
            continue
        if not n and not b[0].startswith(("[![", "**Documentation", "C++20", "<!--", ">")):
            # The old chip-and-driver paragraph: the chip half is now chip-summary and the hero; keep the driver
            # half ("This driver ...") for the coverage section.
            para = " ".join(x.strip() for x in b)
            k = para.find("This driver")
            if k > 0:
                para = para[k:]
            intro.append(_wrap(para))
            continue
        keep_pre.append(b)
    by = {h: _blocks(body) for h, body in secs}
    order = [h for h, _ in secs]
    used: set[str] = set()

    def take(heading: str) -> list[list[str]]:
        used.add(heading)
        return by.get(heading, [])

    glance = take("At a glance")
    glance_table, pins_blocks, inside, card = [], [], [], []
    for b in glance:
        n = _name(b)
        if n == "figure:chip-blocks":
            inside.append(b)
        elif n in ("figure:chip-pinout", "figure:chip-outline", "generated:chip-card"):
            (card if n == "generated:chip-card" else pins_blocks).append(b)
        elif n.startswith("figure:") and not n.startswith("figure:chip-"):
            continue
        else:
            # The chip row of the old glance table: the hero and the chip card say it now.
            glance_table.append([x for x in b if not x.startswith("| **Chip** |")])
    use = take("Use it on your MCU")
    # Everything before "**2." (the wiring step: its table and notes) moves to "Pins and wiring".
    split = next((i for i, b in enumerate(use) if _text_of(b).startswith("**2.")), len(use))
    wiring, quick = use[:split], use[split:]
    # "1. Wire it" becomes a pointer to the section above; the table itself moves there.
    wiring = [b for b in wiring if not _text_of(b).startswith("**1. Wire it**")]
    quick = [["**1. Wire it** as in [Pins and wiring](#pins-and-wiring)."]] + quick
    features = take("What it does")
    circuits = [c.id for c in hw.circuits if any(p.kind == "mcu" for p in c.parts.values())] if hw else []
    frames = [f.id for f in hw.doc.frames] if hw and hw.doc else []

    def fig(fid: str) -> list[str]:
        return [f"<!-- figure: {fid} -->", "<!-- /figure -->"]

    def gen(name: str) -> list[str]:
        return [f"<!-- generated: {name} -->", "<!-- /generated -->"]

    out = [title, "", *gen("chip-summary"), ""] + _join(keep_pre) + fig("chip-hero") + [""]
    out += ["## What it does", ""] + _join([fig("chip-capabilities")])
    out += ["## Where it is used", ""] + _join([gen("chip-uses")])
    inside_name = "Inside the chip"
    if hw and hw.package.type.lower().startswith(("module", "jst", "connector")):
        inside_name = "Inside the module"
    out += [f"## {inside_name}", ""] + _join(inside or [fig("chip-blocks")])
    pins = [b for b in pins_blocks if _name(b) == "figure:chip-pinout"] or [fig("chip-pinout")]
    pins += [fig(f"chip-wiring-{circuits[0]}")] if circuits else []
    pins += wiring + [fig(f"chip-frame-{f}") for f in frames]
    pins += [b for b in pins_blocks if _name(b) == "figure:chip-outline"] + card
    out += ["## Pins and wiring", ""] + _join(pins)
    out += ["## Quick start", ""] + _join(quick)
    cov = [gen("chip-coverage")]
    if intro or glance_table or features:
        cov += intro + glance_table + features
    out += ["## Driver coverage", ""] + _join(cov)
    out += ["## Documentation", ""] + _join(take("Documentation"))
    for h in TAIL[:]:
        if h in by and h not in used:
            out += [f"## {h}", ""] + _join(take(h))
    for h in order:
        if h not in used and h not in [s[0] for s in SECTIONS]:
            out += [f"## {h}", ""] + _join(take(h))
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kokeb-docs readme", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="fail when README.md is not chip-first")
    g.add_argument("--migrate", action="store_true", help="rewrite README.md into the chip-first layout")
    args = ap.parse_args(argv)
    root = repo_root()
    path = root / "README.md"
    if not path.is_file():
        print(f"[readme] no README.md in {root}", file=sys.stderr)
        return 2
    hw = None
    if (root / "docs/hardware.yml").is_file():
        from .hardware import model

        try:
            hw = model.load(root)
        except model.HardwareError as e:
            for p in e.problems:
                print(f"[readme] ERROR {p}", file=sys.stderr)
            return 1
    text = path.read_text()
    if args.migrate:
        new = migrate(text, hw)
        if new != text:
            path.write_text(new)
            print("  wrote README.md (now run kokeb-docs figures && kokeb-docs gen, then read it)")
        return 0
    bad = check(text, hw)
    for b in bad:
        print(f"[readme] ERROR README.md: {b}", file=sys.stderr)
    if bad:
        return 1
    print("[readme] OK: README.md is chip-first")
    return 0


if __name__ == "__main__":
    sys.exit(main())
