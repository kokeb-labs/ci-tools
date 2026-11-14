"""Chip regions, generated from ``docs/hardware.yml`` (see ``kokeb_mkdocs_theme.hardware``).

* ``<!-- generated: chip-pins -->``: one row per package pin: number, name, electrical type and voltage domain,
  function, the driver hook that uses it, what to do with it when unused, and the datasheet section and page.
* ``<!-- generated: chip-parts -->``: the parts of each reference circuit, with their value and what they connect.
* ``<!-- generated: chip-card -->``: the chip at a glance for the README: package, pin count, body size, pitch,
  supply range and, for a chip sold in several packages, the variants, each with its datasheet citation. A row
  whose facts the file does not give is left out.

* ``<!-- generated: chip-summary -->``: the README's first line, "The <chip> is <overview.summary>", with its citation.
* ``<!-- generated: chip-uses -->``: where the chip is used, one bullet per ``overview.applications`` entry.
* ``<!-- generated: chip-coverage -->``: one row per ``capabilities`` entry: what the chip does, the driver calls
  and registers that cover it (checked against the headers named under ``driver``), the status and the citation.

The figures ``chip-pinout``, ``chip-outline``, ``chip-blocks``, ``chip-circuit-<id>``, ``chip-hero``,
``chip-capabilities``, ``chip-frame-<id>`` and ``chip-wiring-<id>`` come from the same file, so the table and
the figures cannot disagree. A file that fails validation stops the run with every problem listed.
"""

from __future__ import annotations

import re

from kokeb_mkdocs_theme.hardware import model
from kokeb_mkdocs_theme.hardware.model import PIN_TYPES, Ref
from kokeb_mkdocs_theme.paths import repo_root


def _cell(s: str) -> str:
    return " ".join(str(s).split()).replace("|", "\\|")


def _load():
    root = repo_root()
    if not (root / model.SOURCE).is_file():
        return None
    try:
        return model.load(root)
    except model.HardwareError as e:
        raise SystemExit("[gen] " + "\n[gen] ".join(e.problems)) from e


_NUMBER = re.compile(r"^\d+(?:\.\d+)*(?:\s+to\s+\d+(?:\.\d+)*)?(?=\s|$)")


def ref_text(hw: model.Hardware, r: Ref, short: bool = False) -> str:
    """``section, p. N``, the page linked to the PDF when the document has a stable link. ``short`` keeps only the
    section number (``6.2``) when the section starts with one, for a narrow table column."""
    d = hw.documents.get(r.doc, {})
    page = f"p. {r.page}"
    if d.get("pdf"):
        page = f"[{page}]({d['pdf']}#page={r.page + int(d.get('page_offset') or 0)})"
    section = r.section
    m = _NUMBER.match(section) if short else None
    if m:
        section = m.group(0)
    return f"{_cell(section)}, {page}"


def pins(page) -> str:
    hw = _load()
    if hw is None:
        return f"_No `{model.SOURCE}` in this repository._\n"
    with_unused = any(p.unused for p in hw.pins)
    head = ["Pin", "Name", "Type (domain)", "Function", "Driver hook"] + (["If unused"] if with_unused else [])
    head.append("Datasheet")
    rows = ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)]
    notes = []
    order = hw.numbered + [p for p in hw.pins if p.is_pad]
    for p in order:
        mark = ""
        if p.unverified:
            notes.append(f"pin {p.number} ({p.name}): {p.unverified}")
            mark = f" [^{len(notes)}]"
        hook = f"`{hw.hooks[p.hook].call}`" if p.hook else "-"
        kind = PIN_TYPES[p.type][1] + (f" ({_cell(p.domain)})" if p.domain and p.type != "ground" else "")
        cells = [str(p.number) if not p.is_pad else "EP", f"`{p.name}`{mark}", kind, _cell(p.function), hook]
        if with_unused:
            cells.append(_cell(p.unused or "-"))
        cells.append(ref_text(hw, p.ref, short=True))
        rows.append("| " + " | ".join(cells) + " |")
    out = [f"{hw.package.type}, {hw.package.pins} pins" + (" and an exposed pad" if hw.package.exposed_pad else "")
           + f" ({ref_text(hw, hw.package.ref)}).", "", *rows, ""]
    for k, n in enumerate(notes, 1):
        out.append(f"[^{k}]: Not confirmed in the datasheet: {_cell(n)}.")
    if notes:
        out.append("")
    out.append(f"Source of this table and of the chip figures: [`{model.SOURCE}`]({page.rel(model.SOURCE)}).")
    return "\n".join(out) + "\n"


def parts(page) -> str:
    hw = _load()
    if hw is None:
        return f"_No `{model.SOURCE}` in this repository._\n"
    out = []
    for c in hw.circuits:
        if len(hw.circuits) > 1:
            out += [f"**{_cell(c.title)}** (figure `chip-circuit-{c.id}`)", ""]
        out += ["| Part | Kind | Value | Connects | Datasheet |", "| --- | --- | --- | --- | --- |"]
        for p in c.parts.values():
            if p.kind == "chip":
                continue
            conns = []
            for n in c.nets:
                for pid, pin in n.nodes:
                    if pid == p.id:
                        conns.append(f"{pin}: {n.name}" if not p.two_pin else n.name)
            note = f" (not confirmed: {_cell(p.unverified)})" if p.unverified else ""
            label = p.label or p.kind.replace("-", " ")
            rows = f"| {p.id} | {_cell(label)} | {_cell(p.value or '-')}{note} | {_cell(', '.join(conns))} | " \
                   f"{ref_text(hw, p.ref, short=True)} |"
            out.append(rows)
        out.append("")
    out.append(f"Export a circuit for a schematic or PCB tool: `kokeb-docs hardware --kicad-netlist OUT.net "
               f"--circuit {hw.circuits[0].id if hw.circuits else 'ID'}`.")
    return "\n".join(out) + "\n"


def _mm(v: float) -> str:
    return f"{v:.1f}" if abs(v * 10 - round(v * 10)) < 1e-9 else f"{v:.3f}".rstrip("0")


def card(page) -> str:
    hw = _load()
    if hw is None:
        return f"_No `{model.SOURCE}` in this repository._\n"
    pk, o = hw.package, hw.package.outline
    rows = [("Package", f"{_cell(pk.type)}" + (", exposed pad" if pk.exposed_pad else ""), ref_text(hw, pk.ref, True)),
            ("Pins", str(pk.pins), ref_text(hw, pk.ref, True))]
    if o:
        dims = " x ".join(_mm(v) for v in (o.length_mm, o.width_mm, o.height_mm) if v)
        cite = ref_text(hw, o.ref, True)
        if o.height_mm and o.height_ref:
            cite += f"; height {ref_text(hw, o.height_ref)}"
        rows.append(("Body size", f"{dims} mm", cite))
        if o.pitch_mm:
            rows.append(("Pin pitch", f"{_mm(o.pitch_mm)} mm", ref_text(hw, o.ref_of("pitch"), True)))
    if pk.variants:
        rows.append(("Variants", ", ".join(f"`{_cell(v.id)}`" for v in pk.variants) + " (below)",
                     ref_text(hw, pk.variants[0].ref, True)))
    for s in hw.supply:
        rows.append((f"Supply {_cell(s.name)}".strip(), f"{_mm(s.min_v)} V to {_mm(s.max_v)} V", ref_text(hw, s.ref, True)))
    out = ["| | | Datasheet |", "| --- | --- | --- |"]
    out += [f"| **{k}** | {v} | {r} |" for k, v, r in rows]
    if pk.variants:
        out += ["", "Also sold as:", "",
                "| Variant | Package | Pins | Size | Ordering | Note | Datasheet |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
        for v in pk.variants:
            out.append(f"| `{_cell(v.id)}` | {_cell(v.type)} | {v.pins or '-'} | {_cell(v.size or '-')} | "
                       f"{_cell(v.ordering or '-')} | {_cell(v.note or '-')} | {ref_text(hw, v.ref, True)} |")
    more = f"; pins, circuits and the block diagram: [Hardware]({page.rel('docs/hardware.md')})" \
        if (repo_root() / "docs/hardware.md").is_file() else ""
    out += ["", f"From [`{model.SOURCE}`]({page.rel(model.SOURCE)}){more}."]
    return "\n".join(out) + "\n"


def _fill(text: str) -> str:
    """A paragraph wrapped at 120 columns (the Markdown line-length rule), never inside a word or a link."""
    import textwrap

    return textwrap.fill(" ".join(text.split()), 120, break_long_words=False, break_on_hyphens=False)


def _none(what: str) -> str:
    return f"_No `{what}` in `{model.SOURCE}`._\n"


def summary(page) -> str:
    hw = _load()
    if hw is None:
        return f"_No `{model.SOURCE}` in this repository._\n"
    ov = hw.doc.overview if hw.doc else None
    if ov is None:
        return _none("overview")
    return _fill(f"The **{hw.chip}** is {ov.summary} ({ref_text(hw, ov.ref)}).") + "\n"


def uses(page) -> str:
    hw = _load()
    if hw is None:
        return f"_No `{model.SOURCE}` in this repository._\n"
    ov = hw.doc.overview if hw.doc else None
    if ov is None or not ov.applications:
        return _none("overview.applications")
    out = []
    for a in ov.applications:
        cite = f" ({ref_text(hw, a.ref, True)})" if a.ref != ov.ref else ""
        mark = " (not confirmed in the datasheet)" if a.unverified else ""
        out.append(f"- {_cell(a.label)}" + (f": {_cell(a.detail)}" if a.detail else "") + cite + mark)
    out += ["", f"Uses named by the datasheet ({ref_text(hw, ov.ref)})."]
    return "\n".join(out) + "\n"


def coverage(page) -> str:
    from kokeb_mkdocs_theme.hardware.chipdoc import STATUSES

    hw = _load()
    if hw is None:
        return f"_No `{model.SOURCE}` in this repository._\n"
    caps = hw.doc.capabilities if hw.doc else []
    if not caps:
        return _none("capabilities")
    rows = ["| Capability | What the chip does | Driver API | Registers | Status | Datasheet |",
            "| --- | --- | --- | --- | --- | --- |"]
    for c in caps:
        name = _cell(c.title)
        doc, _, anchor = c.docs.partition("#")
        if doc and (repo_root() / "docs" / doc).is_file():
            name = f"[{name}]({page.rel('docs/' + doc)}{'#' + anchor if anchor else ''})"
        what = _cell(c.what) + (f" ({_cell(c.note)})" if c.note else "") + (
            f" (not confirmed in the datasheet: {_cell(c.unverified)})" if c.unverified else "")
        api = ", ".join(f"`{_cell(a)}`" for a in c.api) or "-"
        regs = ", ".join(f"`{_cell(r)}`" for r in c.registers) or "-"
        rows.append(f"| {name} | {what} | {api} | {regs} | {STATUSES[c.status][1]} | {ref_text(hw, c.ref, True)} |")
    used = [s for s in STATUSES if any(c.status == s for c in caps)]
    legend = "; ".join(f"**{STATUSES[s][1]}**: {STATUSES[s][2]}" for s in used)
    checked = []
    if hw.doc.api_sources:
        checked.append("every API name is in " + ", ".join(f"`{s}`" for s in hw.doc.api_sources))
    if hw.doc.register_sources:
        checked.append("every register in " + ", ".join(f"`{s}`" for s in hw.doc.register_sources))
    out = rows + ["", _fill(legend + "."), ""]
    tail = f"From [`{model.SOURCE}`]({page.rel(model.SOURCE)})"
    if checked:
        tail += "; `kokeb-docs hardware --check` confirms that " + " and ".join(checked)
    out.append(_fill(tail + "."))
    return "\n".join(out) + "\n"


REGIONS = {"chip-pins": pins, "chip-parts": parts, "chip-card": card, "chip-summary": summary, "chip-uses": uses,
           "chip-coverage": coverage}
