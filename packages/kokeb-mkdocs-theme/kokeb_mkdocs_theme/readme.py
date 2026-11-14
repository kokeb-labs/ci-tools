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
    ## Inside the chip                    <!-- figure: chip-blocks -->       (module, device, sensor or part:
                                                                              overview.inside chooses)
    ## Pins and wiring                    <!-- figure: chip-pinout -->, <!-- figure: chip-wiring-<id> -->
    ## Quick start                        <!-- generated: quickstart-code --> (compiled by the host CI)
    ## Driver coverage                    <!-- generated: chip-coverage -->
    ## Documentation                      the page table
    (then, in any order: Datasheet, Try it on your PC, Add it to your project, Tests and quality, License)

Every figure in the README is a chip figure (``chip-*``): the software layering belongs on the architecture page.

The documentation site's home page (``docs/index.md``) follows the same order under its hero::

    <div class="kb-hero" markdown> ... # <Chip> Driver ... </div>
    <!-- generated: chip-summary -->      then <!-- figure: chip-hero -->
    ## What it does, ## Where it is used, ## Inside the chip, ## Pins and wiring (as above, every wiring figure,
    the chip card, a pointer to the Hardware page), ## Quick start (optional), ## Driver coverage
    (then the other sections of the home page: What you get, Datasheet, Where to go next)

Usage (from anywhere in the repository)::

    kokeb-docs readme --check      fail when README.md breaks the layout (run by kokeb-docs check once
                                   docs/hardware.yml has an overview)
    kokeb-docs readme --migrate    rewrite a template README into the layout; then run kokeb-docs figures and
                                   kokeb-docs gen, and read the result: the old chip paragraph lands under
                                   "Driver coverage" for you to trim
    kokeb-docs readme --site --check|--migrate
                                   the same for docs/index.md (kokeb-docs check runs --site --check once the page
                                   has a <!-- generated: chip-summary --> region)
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
    ("Inside the chip", r"Inside the (?:chip|module|device|sensor|part)", ["figure: chip-blocks"]),
    ("Pins and wiring", r"Pins and wiring", ["figure: chip-pinout", "figure: chip-wiring-"]),
    ("Quick start", r"Quick start", ["generated: quickstart-code"]),
    ("Driver coverage", r"Driver coverage", ["generated: chip-coverage"]),
    ("Documentation", r"Documentation", []),
]
TAIL = ["Datasheet", "Try it on your PC", "Add it to your project", "Tests and quality", "License"]
#: Headings an older README used for its quick start (wire it, write the port, the code).
QUICK = ("Use it on your MCU", "In 30 seconds", "Quick start", "Quickstart", "Get started")

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
    bad += _check_sections(secs, _sections_for(hw))
    bad += _only_chip_figures(text, "the README")
    return bad


def _inside(hw) -> str:
    ov = hw.doc.overview if hw is not None and hw.doc else None
    return ov.inside if ov is not None and ov.inside else ""


def _has_wiring(hw) -> bool:
    """Whether the chip has a wiring figure (an MCU signal reaches it in some circuit); True when unknown."""
    if hw is None:
        return True
    from .hardware import render

    return any(i.startswith("chip-wiring-") for i in render.figure_ids(hw))


def _sections_for(hw, site: bool = False) -> list[tuple[str, str, list[str]]]:
    """The opening sections a README (or, with ``site``, the home page) of ``hw`` must have, in order."""
    out = []
    for name, pattern, markers in SECTIONS:
        if name.startswith("Inside") and _inside(hw):
            name = pattern = f"Inside the {_inside(hw)}"
        if name == "Pins and wiring" and not _has_wiring(hw):
            markers = [m for m in markers if m != "figure: chip-wiring-"]
        if site and name == "Quick start":
            continue  # the site has its own Quickstart page; the section is optional on the home page
        if site and name == "Documentation":
            break  # the site's navigation is the page table
        out.append((name, pattern, markers))
    return out


def _check_sections(secs, layout, optional_quick: bool = False) -> list[str]:
    bad = []
    heads = [h for h, _ in secs]
    i = 0
    for k, (name, pattern, markers) in enumerate(layout):
        # On the home page an optional Quick start may sit before Driver coverage.
        if optional_quick and name == "Driver coverage" and i < len(heads) and re.fullmatch(r"Quick start", heads[i]):
            i += 1
        if i >= len(heads) or not re.fullmatch(pattern, heads[i]):
            got = heads[i] if i < len(heads) else "nothing"
            bad.append(f"section {k + 1} is {got!r}, the layout needs {name!r} there "
                       f"(order: {', '.join(s[0] for s in layout)})")
            i += 1
            continue
        body = "\n".join(secs[i][1])
        for m in markers:
            if f"<!-- {m}" not in body:
                bad.append(f"section {name!r} has no <!-- {m}{'<id>' if m.endswith('-') else ''} -->")
        i += 1
    return bad


def _only_chip_figures(text: str, where: str) -> list[str]:
    return [f"figure {m.group('id')!r} in {where}: only chip figures (chip-*) belong there; the software layering "
            "is on the architecture page" for m in _FIGURE.finditer(text) if not m.group("id").startswith("chip-")]


# ---------------------------------------------------------------------------------------------------- migrate


def _wiring_ids(hw) -> list[str]:
    """The circuits that have a wiring figure."""
    if hw is None:
        return []
    from .hardware import render

    return [i[len("chip-wiring-"):] for i in render.figure_ids(hw) if i.startswith("chip-wiring-")]


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
    quick_head = next((h for h in order if h in QUICK), None)
    if quick_head is None:
        # A quick start under a heading of its own: the section that holds the compiled snippet or the wiring step.
        quick_head = next((h for h, body in secs if h not in [s[0] for s in SECTIONS] + TAIL
                           and ("<!-- generated: quickstart-code -->" in body or any(
                               ln.startswith("**1. Wire it**") for ln in body))), None)
    use = take(quick_head) if quick_head else []
    # Everything before "**2." (the wiring step: its table and notes) moves to "Pins and wiring".
    split = next((i for i, b in enumerate(use) if _text_of(b).startswith("**2.")), len(use))
    wiring, quick = use[:split], use[split:]
    # "1. Wire it" becomes a pointer to the section above; the table itself moves there.
    wiring = [b for b in wiring if not _text_of(b).startswith("**1. Wire it**")]
    quick = [["**1. Wire it** as in [Pins and wiring](#pins-and-wiring)."]] + quick
    features = take("What it does")
    circuits = _wiring_ids(hw)
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
    if _inside(hw):
        inside_name = f"Inside the {_inside(hw)}"
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
    # The rest (Datasheet, Try it on your PC, ..., and any section the layout does not know) keeps its order.
    for h in order:
        if h not in used and h not in [s[0] for s in SECTIONS]:
            out += [f"## {h}", ""] + _join(take(h))
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------------------------------- site home

SITE = "docs/index.md"
_DIV_OPEN = re.compile(r"<div\b")
_DIV_CLOSE = re.compile(r"</div>")


def _front(text: str) -> tuple[list[str], list[str]]:
    """The front matter lines (with their ``---`` fences) and the rest."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                return lines[:j + 1], lines[j + 1:]
    return [], lines


def _div_end(lines: list[str], i: int) -> int:
    """The index of the line closing the ``<div`` opened on line ``i``."""
    depth = 0
    for j in range(i, len(lines)):
        depth += len(_DIV_OPEN.findall(lines[j])) - len(_DIV_CLOSE.findall(lines[j]))
        if depth <= 0:
            return j
    return len(lines) - 1


def _hero(pre: list[str]) -> tuple[int, int] | None:
    """Where the home page's hero ``<div class="kb-hero" ...>`` starts and ends in ``pre``."""
    for i, ln in enumerate(pre):
        if ln.startswith('<div class="kb-hero"'):
            return i, _div_end(pre, i)
    return None


def check_site(text: str, hw=None) -> list[str]:
    """Every way ``text`` (``docs/index.md``) breaks the chip-first home page layout."""
    bad = []
    _fm, body = _front(text)
    pre, secs = _sections("\n".join(body))
    hero = _hero(pre)
    if hero is None:
        bad.append('no hero (<div class="kb-hero" markdown> with the # title) before the first section')
        after = pre
    else:
        if not any(ln.startswith("# ") for ln in pre[hero[0]:hero[1] + 1]):
            bad.append("the hero has no # title")
        after = pre[hero[1] + 1:]
    first = next((ln for ln in after if ln.strip()), "")
    if first.strip() != "<!-- generated: chip-summary -->":
        bad.append("the first thing under the hero is not <!-- generated: chip-summary --> (what the chip is)")
    if "<!-- figure: chip-hero -->" not in "\n".join(after):
        bad.append("no <!-- figure: chip-hero --> before the first section")
    bad += _check_sections(secs, _sections_for(hw, site=True), optional_quick=True)
    opening = "\n".join(body).split("\n## Driver coverage", 1)[0]
    bad += _only_chip_figures(opening, "the opening of the home page")
    return bad


def _site_blocks(lines: list[str]) -> list[list[str]]:
    """Like ``_blocks``, but a ``<div ...>`` (a chip card) is one block, blank lines inside it included."""
    out: list[list[str]] = []
    i = 0
    buf: list[str] = []
    while i < len(lines):
        if lines[i].startswith("<div"):
            out += _blocks(buf)
            buf = []
            j = _div_end(lines, i)
            out.append(lines[i:j + 1])
            i = j + 1
            continue
        buf.append(lines[i])
        i += 1
    return out + _blocks(buf)


def migrate_site(text: str, hw, root=None, readme_text: str = "") -> str:
    """``text`` (``docs/index.md``) in the chip-first home page layout. The hero, the other blocks and the other
    sections are kept: the paragraph under the hero moves under Driver coverage, the chip card under Pins and
    wiring. A page already in the layout is returned unchanged."""
    if not check_site(text, hw):
        return text
    fm, body = _front(text)
    pre, secs = _sections("\n".join(body))
    hero = _hero(pre)
    head = pre[:hero[1] + 1] if hero else []
    # A chip summary inside the hero moves under it (the hero says what the driver is; the summary the chip).
    if "<!-- generated: chip-summary -->" in head:
        i = head.index("<!-- generated: chip-summary -->")
        j = next((k for k in range(i, len(head)) if head[k].strip() == "<!-- /generated -->"), i)
        head = head[:i] + head[j + 1:]
        while i < len(head) and i > 0 and not head[i].strip() and not head[i - 1].strip():
            del head[i]
    rest = pre[hero[1] + 1:] if hero else pre
    keep, intro, card = [], [], []
    for b in _site_blocks(rest):
        n = _name(b)
        if n in ("generated:chip-summary", "figure:chip-hero") or (n.startswith("figure:")
                                                                   and not n.startswith("figure:chip-")):
            continue
        if b[0].startswith('<div class="kb-chip'):
            card.append(b)
        elif not n and not b[0].startswith(("<", "!!!", "|", "-", "*", "[")):
            intro.append(b)
        else:
            keep.append(b)
    by = {h: _blocks(body_) for h, body_ in secs}
    order = [h for h, _ in secs]
    used: set[str] = set()

    def take(h: str) -> list[list[str]]:
        used.add(h)
        return by.get(h, [])

    def fig(fid: str) -> list[str]:
        return [f"<!-- figure: {fid} -->", "<!-- /figure -->"]

    def gen(name: str) -> list[str]:
        return [f"<!-- generated: {name} -->", "<!-- /generated -->"]

    def has(page: str) -> bool:
        return root is not None and (root / "docs" / page).is_file()

    old = {h: take(h) for h in order if re.fullmatch(r"What it does|Where it is used|Inside the \w+|Pins and wiring|"
                                                       r"Quick start|Driver coverage", h)}

    def section(pattern: str, default: list[list[str]], marker: str) -> list[list[str]]:
        got = next((v for h, v in old.items() if re.fullmatch(pattern, h)), None)
        if got and any(_name(b) == marker for b in got):
            return got
        return default + (got or [])

    inside = next((h for h in old if h.startswith("Inside the ")), None)
    inside_name = f"Inside the {_inside(hw)}" if _inside(hw) else inside or "Inside the chip"
    if not inside and not _inside(hw) and hw and hw.package.type.lower().startswith(("module", "jst", "connector")):
        inside_name = "Inside the module"
    out = fm + head + [""] + gen("chip-summary") + [""] + _join(keep) + fig("chip-hero") + [""]
    out += ["## What it does", ""] + _join(section("What it does", [fig("chip-capabilities")],
                                                  "figure:chip-capabilities"))
    out += ["## Where it is used", ""] + _join(section("Where it is used", [gen("chip-uses")], "generated:chip-uses"))
    out += [f"## {inside_name}", ""] + _join(section(r"Inside the \w+", [fig("chip-blocks")], "figure:chip-blocks"))
    pins = old.get("Pins and wiring")
    if not pins:
        from .hardware import render

        ids = render.figure_ids(hw) if hw else []
        pins = [fig("chip-pinout")] + [fig(i) for i in ids if i.startswith("chip-wiring-")]
        pins += [fig(i) for i in ids if i == "chip-outline"] + [fig(i) for i in ids if i.startswith("chip-frame-")]
        pins += card
        if has("hardware.md"):
            pins.append(["Every pin, the reference circuits, the bus settings, the timing and the power: "
                         "[Hardware](hardware.md)."])
    else:
        pins = pins + card
    out += ["## Pins and wiring", ""] + _join(pins)
    quick = old.get("Quick start")
    if quick is None and "<!-- generated: quickstart-code -->" in readme_text:
        lead = "Wire the chip as above, write the port for your MCU" + (
            " ([Porting](porting.md))" if has("porting.md") else "") + ", then:"
        quick = [[lead], gen("quickstart-code")]
        if has("quickstart.md"):
            quick.append(["Every step, with the port and what to check when it does not work: "
                          "[Quickstart](quickstart.md)."])
    if quick:
        out += ["## Quick start", ""] + _join(quick)
    cov = section("Driver coverage", [gen("chip-coverage")], "generated:chip-coverage")
    out += ["## Driver coverage", ""] + _join(cov + [_wrap(" ".join(x.strip() for x in b)) for b in intro])
    for h in order:
        if h not in used:
            out += [f"## {h}", ""] + _join(take(h))
    while out and not out[-1].strip():
        out.pop()
    text = "\n".join(out) + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kokeb-docs readme", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="fail when README.md is not chip-first")
    g.add_argument("--migrate", action="store_true", help="rewrite README.md into the chip-first layout")
    ap.add_argument("--site", action="store_true", help=f"work on {SITE} (the site's home page) instead")
    args = ap.parse_args(argv)
    root = repo_root()
    name = SITE if args.site else "README.md"
    path = root / name
    if not path.is_file():
        print(f"[readme] no {name} in {root}", file=sys.stderr)
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
        if args.site:
            readme = root / "README.md"
            new = migrate_site(text, hw, root, readme.read_text() if readme.is_file() else "")
        else:
            new = migrate(text, hw)
        if new != text:
            path.write_text(new)
            print(f"  wrote {name} (now run kokeb-docs figures && kokeb-docs gen, then read it)")
        return 0
    bad = check_site(text, hw) if args.site else check(text, hw)
    for b in bad:
        print(f"[readme] ERROR {name}: {b}", file=sys.stderr)
    if bad:
        return 1
    print(f"[readme] OK: {name} is chip-first")
    return 0


if __name__ == "__main__":
    sys.exit(main())
