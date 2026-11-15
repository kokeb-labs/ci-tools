"""Lints for figures: the SVG itself, the alt text and long description, and the print fit.

Text contrast (4.5:1), non-text contrast (3:1) and fit are checked while a figure is drawn (``Fig.problems()``,
``Fig.advisories()``). These lints look at the finished files and at the words:

SVG lint (``svg_lint``)
    well-formed; ``viewBox``; ``role="img"``; ``<title>`` and ``<desc>``; no script, no event handler attribute, no
    ``style=`` attribute; no external reference (every ``href`` and ``url()`` points inside the file); a ``<style>``
    element only in an adaptive or font-embedding file, with no ``@import``; a ``data:`` URL only as the font of an
    embedded subset; ids start with the figure id (palette 2); at most 60 KB (85 KB with an embedded font).

Alt lint (``alt_lint``)
    the alt text is one sentence of 40 to 300 characters, does not start with "image of", "diagram of" or "picture
    of", and differs from the title; the long description (``Reads:``) has at least two sentences, and every name the
    figure lists (states, participants, lanes, columns) appears in the alt or the description.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

MAX_BYTES = 60 * 1024
MAX_BYTES_FONT = 85 * 1024
_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")


def sentences(text: str) -> list[str]:
    return [s for s in _SENT.split(" ".join(text.split())) if s.strip()]


def svg_lint(svg: str, fid: str, adaptive: bool = False, font_embedded: bool = False, palette: int = 2) -> list[str]:
    out: list[str] = []
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        return [f"not well-formed XML: {e}"]
    if not root.tag.endswith("svg"):
        out.append("root element is not svg")
    if not root.get("viewBox"):
        out.append("no viewBox")
    if root.get("role") != "img":
        out.append('no role="img"')
    names = [el.tag.split("}")[-1] for el in root.iter()]
    for need in ("title", "desc"):
        if need not in names:
            out.append(f"no <{need}>")
    if "script" in names:
        out.append("contains <script>")
    if "foreignObject" in names:
        out.append("contains <foreignObject>")
    ids = []
    for el in root.iter():
        for k, v in el.attrib.items():
            key = k.split("}")[-1]
            if key.lower().startswith("on"):
                out.append(f"event handler attribute {key}")
            if key == "style":
                out.append(f"style= attribute on <{el.tag.split('}')[-1]}>")
            if key == "href" and not v.startswith("#"):
                out.append(f"external reference href={v[:40]!r}")
            if key == "id":
                ids.append(v)
    style_texts = [el.text or "" for el in root.iter() if el.tag.split("}")[-1] == "style"]
    if style_texts and not (adaptive or font_embedded):
        out.append("contains a <style> element (only an adaptive or font-embedding file may)")
    for css in style_texts:
        if "@import" in css:
            out.append("@import in <style>")
        for u in re.findall(r"url\(([^)]*)\)", css):
            if not u.startswith("data:font/woff2;base64,") or not font_embedded:
                out.append(f"external or data url in <style>: {u[:40]!r}")
    for u in re.findall(r"url\(([^)]*)\)", re.sub(r"<style>.*?</style>", "", svg, flags=re.S)):
        if not u.startswith("#"):
            out.append(f"external url() {u[:40]!r}")
    if "data:" in re.sub(r"<style>.*?</style>", "", svg, flags=re.S):
        out.append("data: URL outside <style>")
    if palette >= 2:
        for i in ids:
            if not i.startswith(fid + "-"):
                out.append(f"id {i!r} does not start with the figure id {fid!r}-")
    limit = MAX_BYTES_FONT if font_embedded else MAX_BYTES
    if len(svg.encode()) > limit:
        out.append(f"{len(svg.encode())} bytes, over the {limit} byte budget")
    return out


def alt_lint(alt: str, title: str, reads: str = "", names=()) -> list[str]:
    out = []
    a = " ".join(alt.split())
    if "TODO" in a or "TODO" in reads:
        out.append("alt text or Reads still contains TODO (written by `figkit new`)")
    if not 40 <= len(a) <= 300:
        out.append(f"alt text is {len(a)} characters, needs 40 to 300")
    if len(sentences(a)) != 1:
        out.append(f"alt text is {len(sentences(a))} sentences, needs exactly one")
    if re.match(r"(?i)\s*(image|diagram|picture|figure|graphic) of\b", a):
        out.append('alt text starts with "image of" or "diagram of"; say what it shows')
    if a.strip().rstrip(".").lower() == title.strip().rstrip(".").lower():
        out.append("alt text equals the title")
    if reads:
        if len(sentences(reads)) < 2:
            out.append("the Reads description needs at least two sentences")
        hay = (a + " " + reads).lower()
        for n in names:
            if str(n).lower() not in hay:
                out.append(f"neither the alt text nor the Reads description names {n!r}")
    else:
        out.append("no Reads description (the long description)")
    return out


def lint_fig(fig, files: dict[str, str], reads: str, advisories: bool = True) -> list[tuple[str, str]]:
    """Every finding for a figure as ``(level, message)``: ``error`` for a palette 2 figure (it fails the build) and
    for any SVG defect, ``warn`` for the rest of a palette 1 figure (the old figures keep building)."""
    res: list[tuple[str, str]] = []
    legacy = fig.palette < 2
    lvl = "warn" if legacy else "error"
    for name, svg in files.items():
        for m in svg_lint(svg, fig.fid, adaptive=name.endswith(".adaptive.svg"), font_embedded=bool(fig.font),
                          palette=fig.palette):
            res.append(("warn" if legacy and m.startswith("id ") else "error", f"{name}: {m}"))
    for m in alt_lint(fig.alt, fig.title, reads, fig.names):
        res.append((lvl, m))
    for m in fig.advisories() if advisories else []:
        res.append((lvl, m))
    return res
