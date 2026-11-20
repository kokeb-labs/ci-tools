#!/usr/bin/env python3
"""Build and check the documentation figures.

A figure is a Python module ``docs/diagrams/figures/<id>.py``:

* ``data() -> dict`` (optional) extracts the facts the figure shows from the code, with a ``"sources"`` list naming
  the file (and symbol) each fact came from. The result is written to ``docs/diagrams/data/<id>.json``.
* ``build(data) -> figkit.Fig`` lays the figure out (``data`` is ``None`` when there is no ``data()``).
* ``SOURCES`` (optional) lists the files a hand-placed figure is drawn from.
* The module docstring's ``Reads:`` paragraph is the long description shown under the figure.

A figure can also be a model file ``docs/model/<id>.<kind>.yml`` (kinds: state, graph, seq, timeline, matrix, bytes,
pipeline; see ``kinds``), with no module: ``kokeb-docs figkit new`` writes one. A model figure is drawn with palette 2
(non-text contrast, print fit) and also gets ``<id>.adaptive.svg`` (one file for both themes), a table twin
``<id>.table.html`` when its kind has one, and a layout lock ``<id>.layout.json`` for the layered kinds (made by
``kokeb-docs figkit layout``; this build only reads it and never runs Graphviz).

A repository with ``docs/hardware.yml`` also gets the chip figures drawn from it, with no module to write:
``chip-pinout``, ``chip-blocks`` (when the file has a block diagram) and ``chip-circuit-<id>`` for each circuit
(see ``kokeb_mkdocs_theme.hardware``). They are built, embedded and checked exactly like the others.

Outputs, all committed: ``docs/diagrams/<id>.svg`` and ``<id>.dark.svg``, ``docs/diagrams/data/<id>.json``,
``docs/diagrams/figures.json`` (title, alt text, description and sources, read by the site hook) and the figure
catalogue ``docs/diagrams/index.md``. A page embeds a figure with a marker pair, which this script fills with a
``<picture>`` that works on GitHub (the site hook replaces it with a light / dark pair that follows the theme
toggle)::

    <!-- figure: board-overview -->
    <!-- /figure -->

The build fails on any figkit problem (contrast below 4.5:1 in either theme, content that does not fit, overlapping
cards, missing alt text), on an unknown figure in a marker, and on output that is not well-formed XML.

Usage (from anywhere in the repository; the root is the folder that holds the site's docs_dir, see paths.py)::

    kokeb-docs figures              # extract, render, write, fill embeds
    kokeb-docs figures some-id      # only some figures
    kokeb-docs figures --check      # CI: everything committed must equal a fresh build
    kokeb-docs figures --report     # contrast and smallest text per figure
    kokeb-docs figures --lint       # SVG, alt text, non-text contrast and print-fit findings (warnings for old figures)

A figure module imports figkit as ``from kokeb_mkdocs_theme.figkit import Fig`` (``from figkit import Fig`` keeps
working: the build registers the package under that name too).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import posixpath
import re
import sys
import textwrap
import xml.etree.ElementTree as ET

from .. import figkit
from ..paths import SKIP_DIRS, is_site_root, repo_root
from . import adaptive, fontsubset, layered, lint

ROOT = repo_root()
DIAGRAMS = ROOT / "docs/diagrams"
FIG_DIR = DIAGRAMS / "figures"
DATA_DIR = DIAGRAMS / "data"
INDEX = DIAGRAMS / "figures.json"
CATALOGUE = DIAGRAMS / "index.md"

FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,}).*?^(?P=indent)(?P=fence)[ \t]*$", re.M | re.S)


def outside_fences(text: str, fn) -> str:
    """Apply ``fn`` to the parts of ``text`` that are not fenced code blocks (examples of markers stay as they are)."""
    out, pos = [], 0
    for m in FENCE.finditer(text):
        out.append(fn(text[pos : m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(fn(text[pos:]))
    return "".join(out)


sys.modules.setdefault("figkit", figkit)
sys.path[:0] = [str(ROOT / "tools/docs"), str(FIG_DIR)]

MARKER = re.compile(r"(<!-- figure: (?P<id>[a-z0-9-]+) -->)(?P<body>.*?)(<!-- /figure -->)", re.S)


MODEL_DIR = ROOT / "docs/model"


def model_files() -> dict[str, pathlib.Path]:
    """Figure id -> model file for every ``docs/model/<id>.<kind>.yml`` whose kind is a figure kind."""
    from .kinds import KINDS

    out = {}
    if MODEL_DIR.is_dir():
        for p in sorted(MODEL_DIR.glob("*.yml")):
            stem, _, kind = p.name[: -len(".yml")].rpartition(".")
            if stem and kind in KINDS:
                out[stem] = p
    return out


HARDWARE = ROOT / "docs/hardware.yml"
_hw_cache: dict = {}


def _hardware():
    """The parsed docs/hardware.yml, or None when the repository has none."""
    if not HARDWARE.is_file():
        return None
    if "hw" not in _hw_cache:
        from ..hardware import model

        try:
            _hw_cache["hw"] = model.load(ROOT)
        except model.HardwareError as e:
            raise SystemExit("[figures] " + "\n[figures] ".join(e.problems)) from e
    return _hw_cache["hw"]


def hardware_ids() -> list[str]:
    hw = _hardware()
    if hw is None:
        return []
    from ..hardware import render

    return render.figure_ids(hw)


def fig_ids() -> list[str]:
    mods = sorted(p.stem for p in FIG_DIR.glob("*.py") if not p.stem.startswith("_")) if FIG_DIR.is_dir() else []
    hw = hardware_ids()
    models = model_files()
    clash = sorted(set(mods) & set(hw))
    both = sorted(set(mods) & set(models))
    if both:
        raise SystemExit(f"[figures] {', '.join(both)}: both a module and a model file in docs/model/; keep one")
    mods = sorted(set(mods) | set(models))
    if clash:
        raise SystemExit(f"[figures] {', '.join(clash)}: the id of a figure drawn from docs/hardware.yml; rename the "
                         "module")
    return sorted(mods + hw)


def load(fid: str):
    if fid in hardware_ids():
        from ..hardware import render

        hw = _hardware()
        fig = render.build(hw, fid)
        fig.source = "docs/hardware.yml"
        fig.sources = ["docs/hardware.yml"] + sorted({h.source for h in hw.hooks.values() if h.source})
        return fig, None
    if fid in model_files():
        from .kinds import from_model

        path = model_files()[fid]
        fig = from_model(path, lock_dir=DIAGRAMS)
        if fig.fid != fid:
            raise SystemExit(f"[figures] {path.relative_to(ROOT)} builds a figure with id {fig.fid!r}")
        fig.doc = ""
        fig.source = path.relative_to(ROOT).as_posix()
        fig.sources = sorted({fig.source, *_declared_sources(path)})
        return fig, None
    spec = importlib.util.spec_from_file_location(f"figure_{fid.replace('-', '_')}", FIG_DIR / f"{fid}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    data = mod.data() if hasattr(mod, "data") else None
    fig = mod.build(data)
    if fig.fid != fid:
        raise SystemExit(f"[figures] {fid}.py builds a figure with id {fig.fid!r}")
    fig.doc = (mod.__doc__ or "").strip()
    fig.source = f"docs/diagrams/figures/{fid}.py"
    sources = list(getattr(mod, "SOURCES", []))
    sources += [s for s in getattr(fig, "model_sources", []) if s not in sources]
    if data:
        sources += [s for s in data.get("sources", []) if s not in sources]
    fig.sources = sources
    return fig, data


def _declared_sources(path: pathlib.Path) -> list[str]:
    import yaml

    return [str(s) for s in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("sources", [])]


def description(fig) -> str:
    for para in fig.doc.split("\n\n"):
        if para.strip().startswith("Reads:"):
            return " ".join(para.strip()[len("Reads:") :].split())
    return fig.reads


def dump(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def svg_text(fig, theme: str) -> str:
    out = fig.svg(theme)
    ET.fromstring(out)  # well-formed, or raise
    if fig.font:
        out = fontsubset.embed(out, DIAGRAMS, fig.fid)
        ET.fromstring(out)
    return out


def adaptive_text(fig) -> str:
    out = adaptive.to_adaptive(fig.raw_svg(), fig.palette)
    ET.fromstring(out)
    if fig.font:
        out = fontsubset.embed(out, DIAGRAMS, fig.fid)
        ET.fromstring(out)
    return out


def twin_html(fig) -> str:
    """The table twin: the figure's facts as a ``<details>`` table, for assistive technology and for print."""
    from xml.sax.saxutils import escape

    t = fig.twin
    head = "".join(f"<th scope=\"col\">{escape(h)}</th>" for h in t["head"])
    rows = "".join("<tr>" + "".join((f"<th scope=\"row\">{escape(c)}</th>" if i == 0 else f"<td>{escape(c)}</td>")
                                    for i, c in enumerate(r)) + "</tr>\n" for r in t["rows"])
    return (f"<details>\n<summary>Table form of this figure</summary>\n<table>\n<caption>{escape(t['caption'])}</caption>\n"
            f"<thead><tr>{head}</tr></thead>\n<tbody>\n{rows}</tbody>\n</table>\n</details>\n")


def entry(fig) -> dict:
    out = {
        "title": fig.title,
        "alt": " ".join(fig.alt.split()),
        "description": description(fig),
        "profile": fig.profile,
        "width": fig.width,
        "source": fig.source,
        "sources": fig.sources,
    }
    if fig.kind or fig.adaptive:  # model figures only: the entries of every other figure stay as they were
        out.update(kind=fig.kind, palette=fig.palette, print=fig.print_mode or "", adaptive=fig.adaptive,
                   twin=fig.twin is not None, font=fig.font)
    return out


def _link(path: str) -> str:
    """Link from the catalogue to a repository file. A data file the site publishes (``docs/hardware.yml``) is linked
    within the site; anything else through the repository root, which the site hook sends to GitHub."""
    if path.startswith("docs/") and path.endswith((".yml", ".yaml")) and not path.startswith("docs/diagrams/"):
        return posixpath.relpath(path, "docs/diagrams")
    return f"../../{path}"


def catalogue(index: dict) -> str:
    lines = [
        "# Figures",
        "",
        "<!-- Written by kokeb-docs figures from docs/diagrams/figures/*.py. Do not edit by hand. -->",
        "",
        "Every figure on this site is drawn by a Python module from facts extracted from the code, so it is rebuilt,",
        "not redrawn, when the code changes. CI runs `kokeb-docs figures --check` and fails when a",
        "committed figure no longer matches the code. Each figure below lists the files it is drawn from.",
        "",
    ]
    for fid, e in index.items():
        embed = f"<!-- figure: {fid} -->{picture(fid, e, CATALOGUE)}<!-- /figure -->"
        lines += [f"## {e['title']}", "", embed, ""]
        what = "Hardware description" if e["source"].endswith(".yml") else "Figure module"
        lines += [f"{what}: [`{e['source']}`]({_link(e['source'])})", ""]
        if e["sources"]:
            lines += ["Drawn from:", ""]
            for s in e["sources"]:
                path = s.split(":", 1)[0]
                rest = s[len(path) :]
                # Symbol first: the link is one long unbreakable token, so it goes last (Markdown line-length lint).
                lines.append(f"- {f'`{rest[1:]}` in ' if rest else ''}[`{path}`]({_link(path)})")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def picture(fid: str, e: dict, md_path: pathlib.Path) -> str:
    rel = posixpath.relpath((DIAGRAMS / fid).as_posix(), md_path.parent.as_posix())
    alt = "\n    ".join(textwrap.wrap(e["alt"].replace('"', "&quot;"), 100, break_long_words=False))
    return (
        "\n<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{rel}.dark.svg">\n'
        f'  <img src="{rel}.svg"\n    alt="{alt}">\n'
        "</picture>\n"
    )


def markdown_files() -> list[pathlib.Path]:
    out = []
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel[:-1]):
            continue
        # A folder with its own mkdocs.yml or _config/mkdocs.yml (a template, a fixture) is another site with its own
        # figures.
        if any(is_site_root(ROOT.joinpath(*rel[:i])) for i in range(1, len(rel))):
            continue
        out.append(p)
    return out


def mermaid_fences(ban: bool = False) -> list[tuple[str, int]]:
    """Pages that hold a ``mermaid`` fence, and ``.mmd`` sources: ``[(path, count)]``.

    Without ``ban``: published pages under docs/ only (README files excluded). With ``ban`` (``--ban-mermaid``, or
    ``no_mermaid: true`` under ``extra:`` in the site configuration): every Markdown file of the repository, README
    files included, and every ``.mmd`` file (count 0): Mermaid is not rendered on phones and in mobile apps, so no
    figure may use it, not even as the source format.
    """
    out = []
    for p in markdown_files():
        rel = p.relative_to(ROOT)
        if not ban and (rel.parts[0] != "docs" or p.name.lower() == "readme.md"):
            continue
        n = len(re.findall(r"^[ \t]*(?:`{3,}|~{3,})[ \t]*mermaid\b", p.read_text(), re.M))
        if n:
            out.append((rel.as_posix(), n))
    if ban:
        for p in sorted(ROOT.rglob("*.mmd")):
            rel = p.relative_to(ROOT)
            if not any(part in SKIP_DIRS or part.startswith(".git") for part in rel.parts):
                out.append((rel.as_posix(), 0))
    return out


def fill_embeds(index: dict, write: bool) -> list[str]:
    """Fill (or with ``write=False`` check) every figure marker. Returns problems."""
    bad = []
    for p in markdown_files():
        # Scaffold blocks are text a generator pastes into pages of another repository, where the figure id names
        # another model: the marker stays empty here and is filled in the scaffolded page.
        if "scaffold" in p.relative_to(ROOT).parts[:-1]:
            continue
        text = p.read_text()
        if "<!-- figure:" not in text:
            continue

        def sub(m: re.Match) -> str:
            fid = m.group("id")
            if fid not in index:
                bad.append(f"{p.relative_to(ROOT)}: no figure {fid!r}")
                return m.group(0)
            return m.group(1) + picture(fid, index[fid], p) + m.group(4)

        new = outside_fences(text, lambda t: MARKER.sub(sub, t))
        if new != text:
            if write:
                p.write_text(new)
            else:
                bad.append(f"{p.relative_to(ROOT)}: figure embed is stale (run kokeb-docs figures)")
    return bad


LINTS: dict[str, list[tuple[str, str]]] = {}


def render_all(ids: list[str]) -> tuple[dict[pathlib.Path, str], dict, list[str]]:
    """Every output file and its content, the index, and the problems."""
    files: dict[pathlib.Path, str] = {}
    index: dict = json.loads(INDEX.read_text()) if INDEX.exists() and ids != fig_ids() else {}
    problems = []
    for fid in ids:
        try:
            fig, data = load(fid)
        except (layered.LayoutStale, fontsubset.FontStale) as e:
            problems.append(str(e))
            continue
        problems += [f"{fid}: {p}" for p in fig.problems()]
        if data is not None:
            files[DATA_DIR / f"{fid}.json"] = dump(data)
        mine: dict[str, str] = {}
        try:
            for theme in ("light", "dark"):
                name = f"{fid}.svg" if theme == "light" else f"{fid}.dark.svg"
                mine[name] = svg_text(fig, theme)
            if fig.adaptive:
                mine[f"{fid}.adaptive.svg"] = adaptive_text(fig)
        except ET.ParseError as e:
            problems.append(f"{fid}: SVG is not well-formed: {e}")
        except fontsubset.FontStale as e:
            problems.append(str(e))
        for name, text in mine.items():
            files[DIAGRAMS / name] = text
        if fig.twin is not None:
            files[DIAGRAMS / f"{fid}.table.html"] = twin_html(fig)
        if fig.palette >= 2:  # a palette 2 figure is held to the lints; older figures see them with --lint
            problems += [f"{fid}: {m}" for lv, m in lint.lint_fig(fig, mine, description(fig), advisories=False)
                         if lv == "error"]
        LINTS[fid] = lint.lint_fig(fig, mine, description(fig))
        index[fid] = entry(fig)
    index = {k: index[k] for k in sorted(index) if k in fig_ids()}
    files[INDEX] = dump(index)
    files[CATALOGUE] = catalogue(index)
    return files, index, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kokeb-docs figures", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="figure ids (default: all)")
    ap.add_argument("--check", action="store_true", help="fail if anything committed differs from a fresh build")
    ap.add_argument("--report", action="store_true", help="print contrast and smallest text per figure")
    ap.add_argument("--ban-mermaid", action="store_true",
                    help="with --lint: a mermaid fence in a published page (docs/) is an error, not a warning")
    ap.add_argument("--lint", action="store_true", help="SVG, alt text, non-text contrast and print-fit findings; "
                    "warnings for figures drawn before palette 2, errors (exit 1) for palette 2 figures and SVG defects")
    args = ap.parse_args(argv)

    known = fig_ids()
    unknown = [i for i in args.ids if i not in known]
    if unknown:
        print(f"[figures] unknown figure(s): {', '.join(unknown)}", file=sys.stderr)
        return 2
    ids = args.ids or known

    if args.report:
        for fid in ids:
            fig, _ = load(fid)
            c = fig.contrast_report()
            print(f"{fid:28s} {fig.profile:8s} min text {fig.min_text_px:5.1f} px "
                  f"({fig.min_display_px:5.1f} at README width)  contrast light {c['light']}:1 dark {c['dark']}:1")
        return 0

    files, index, problems = render_all(known if (args.check or args.lint) else ids)
    if args.lint:
        errors = 0
        for fid in ids:
            for lv, m in LINTS.get(fid, []):
                print(f"[figures] {lv.upper()} {fid}: {m}")
                errors += lv == "error"
        shown = {m for lst in LINTS.values() for _lv, m in lst}
        problems = [p for p in problems if p.split(": ", 1)[-1] not in shown]
        for page, n in mermaid_fences(args.ban_mermaid):
            level = "ERROR" if args.ban_mermaid else "WARN"
            what = f"{n} mermaid fence(s)" if n else "a Mermaid source"
            tail = ("Mermaid is banned (no phone rendering): redraw it as a figkit figure, docs/figkit.md"
                    if args.ban_mermaid else
                    "published pages use figkit figures (docs/figkit.md); Mermaid stays allowed in README files and "
                    "pull requests until the site sets no_mermaid")
            print(f"[figures] {level} {page}: {what}; {tail}")
            errors += bool(args.ban_mermaid)
        for p in problems:
            print(f"[figures] ERROR {p}", file=sys.stderr)
        print(f"[figures] lint: {errors + len(problems)} error(s) in {len(ids)} figure(s)")
        return 1 if errors or problems else 0
    hw = _hardware()
    if hw is not None:
        from ..hardware import render

        for cid in render.wiring_skipped(hw):
            print(f"[figures] note: circuit {cid!r} has an MCU but no MCU signal reaches the chip, so it has no "
                  f"chip-wiring-{cid} figure")

    if args.check:
        bad = list(problems)
        for path, content in files.items():
            if not path.exists() or path.read_text() != content:
                bad.append(f"{path.relative_to(ROOT)} is stale (run kokeb-docs figures)")
        expected = {p.name for p in files if p.parent == DIAGRAMS and p.suffix == ".svg"}
        for p in sorted(DIAGRAMS.glob("*.svg")):
            if p.name not in expected:
                bad.append(f"{p.relative_to(ROOT)} has no figure module")
        expected_data = {p.name for p in files if p.parent == DATA_DIR}
        for p in sorted(DATA_DIR.glob("*.json")) if DATA_DIR.exists() else []:
            if p.name not in expected_data:
                bad.append(f"{p.relative_to(ROOT)} has no figure module")
        known_ids = set(known)
        for pat in ("*.layout.json", "*.table.html", "*.font.woff2", "*.font.json"):
            for p in sorted(DIAGRAMS.glob(pat)):
                if p.name[: -len(pat) + 1] not in known_ids:
                    bad.append(f"{p.relative_to(ROOT)} has no figure module")
        bad += fill_embeds(index, write=False)
        for b in bad:
            print(f"[figures] ERROR {b}", file=sys.stderr)
        if bad:
            return 1
        print(f"[figures] OK: {len(known)} figure(s) current")
        return 0

    for p in problems:
        print(f"[figures] ERROR {p}", file=sys.stderr)
    if problems:
        return 1
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text() != content:
            path.write_text(content)
            print(f"  wrote {path.relative_to(ROOT)}")
    for b in fill_embeds(index, write=True):
        print(f"[figures] ERROR {b}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
