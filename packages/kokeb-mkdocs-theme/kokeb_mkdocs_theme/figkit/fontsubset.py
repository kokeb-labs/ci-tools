"""Embedded font subset for standalone SVGs (``font: embed`` in a model, or ``Fig(font="embed")``).

A standalone SVG opened from disk or used as an ``<img>`` cannot load the site's font, so it falls back to a system
font. With ``font: embed`` the file carries a subset of Inter (the glyphs of this figure only, the weight axis kept),
as a ``data:`` WOFF2 in an ``@font-face`` rule. Budget: 25 KB per figure (a typical figure needs 8 to 10 KB).

Same lock idea as the layout: ``kokeb-docs figkit font <id>`` makes the subset (it needs ``fonttools`` and ``brotli``,
the ``fonts`` extra of this package) and writes ``<id>.font.woff2`` and ``<id>.font.json`` (the glyphs and the hash)
next to the figure; a normal render only reads them, so it needs neither package, and the bytes do not depend on the
fonttools version. If the figure's text changes, the glyph list in the lock no longer matches and the render fails
with "font subset stale, run figkit font".

Licence: Inter is under the SIL Open Font License 1.1 (``theme/assets/kokeb/FONTS-LICENSE.txt``), which allows
embedding and subsetting; the file carries the copyright and licence line of the font as an XML comment.
Reproducible: the subset of a given source file, glyph set and fonttools version is byte for byte the same.
Monospace text (a card with ``mono``) is not embedded; it falls back to the system monospace font.
"""

from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import re

BUDGET_BYTES = 25 * 1024
SOURCE = pathlib.Path(__file__).resolve().parent.parent / "theme/assets/kokeb/inter-latin-wght-normal.woff2"
NOTICE = ("Inter subset, Copyright 2016 The Inter Project Authors (https://github.com/rsms/inter), "
          "SIL Open Font License 1.1 (https://openfontlicense.org)")


class FontStale(Exception):
    pass


def chars_of(svg: str) -> str:
    """The characters the figure's text needs, sorted, plus the space."""
    text = "".join(re.findall(r"<(?:text|title|desc)(?: [^>]*)?>([^<]*)<", svg))
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")
    return "".join(sorted(set(text) | {" "}))


def paths(lock_dir, fid: str):
    d = pathlib.Path(lock_dir)
    return d / f"{fid}.font.woff2", d / f"{fid}.font.json"


def make_subset(chars: str) -> bytes:
    try:
        import io

        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError as e:  # pragma: no cover
        raise SystemExit("figkit font needs fonttools and brotli: pip install 'kokeb-mkdocs-theme[fonts]'") from e
    font = TTFont(str(SOURCE))
    opt = subset.Options()
    opt.flavor = "woff2"
    opt.layout_features = ["kern"]
    opt.name_IDs = [0, 1, 2, 3, 4, 6]
    opt.notdef_outline = True
    opt.hinting = False
    opt.desubroutinize = True
    sub = subset.Subsetter(opt)
    sub.populate(text=chars)
    sub.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def write_lock(lock_dir, fid: str, svg: str) -> str:
    """(Re)make the subset for the glyphs of ``svg``. Returns what happened."""
    chars = chars_of(svg)
    wpath, jpath = paths(lock_dir, fid)
    if jpath.is_file() and json.loads(jpath.read_text()).get("chars") == chars and wpath.is_file():
        return "unchanged"
    data = make_subset(chars)
    if len(data) > BUDGET_BYTES:
        raise SystemExit(f"[figkit] {fid}: font subset is {len(data)} bytes, over the {BUDGET_BYTES} byte budget")
    pathlib.Path(lock_dir).mkdir(parents=True, exist_ok=True)
    wpath.write_bytes(data)
    import fontTools

    jpath.write_text(json.dumps({"chars": chars, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                                 "source": SOURCE.name, "fonttools": fontTools.version}, indent=1, sort_keys=True) + "\n")
    return "written"


def embed(svg: str, lock_dir, fid: str) -> str:
    """``svg`` with the subset as an ``@font-face`` rule. Raises ``FontStale`` when the lock is missing or old."""
    wpath, jpath = paths(lock_dir, fid)
    if not wpath.is_file() or not jpath.is_file():
        raise FontStale(f"{fid}: no font subset; run `kokeb-docs figkit font {fid}` and commit it")
    meta = json.loads(jpath.read_text())
    if meta["chars"] != chars_of(svg):
        raise FontStale(f"{fid}: font subset stale (the figure's text changed); run `kokeb-docs figkit font {fid}`")
    b64 = base64.b64encode(wpath.read_bytes()).decode()
    rule = ("@font-face{font-family:Inter;font-weight:100 900;font-style:normal;src:url(data:font/woff2;base64,"
            f"{b64}) format(\"woff2\")}}")
    comment = f"<!-- {NOTICE} -->\n"
    if "<style>" in svg:
        svg = svg.replace("<style>\n", f"<style>\n{rule}\n", 1)
    else:
        svg = re.sub(r"(<desc [^>]*>.*?</desc>\n)", lambda m: m.group(1) + f"<style>\n{rule}\n</style>\n", svg, count=1,
                     flags=re.S)
    return svg.replace("<svg ", comment + "<svg ", 1) if not svg.startswith("<!--") else svg
