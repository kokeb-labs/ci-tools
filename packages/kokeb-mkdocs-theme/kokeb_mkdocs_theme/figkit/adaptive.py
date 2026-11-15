"""One SVG for both themes: ``<id>.adaptive.svg``.

Colours move out of the attributes into classes (``fk-f-<token>`` for fill, ``fk-s-<token>`` for stroke) and a style
block defines every token as a custom property for the light and the dark theme. The theme is chosen, in order, by
``data-theme="light|dark"`` on the page's root element, Material's ``data-md-color-scheme`` (``slate`` is dark), and the
reader's ``prefers-color-scheme``. In forced-colors mode the figure uses the system colours.

Two forms:

* standalone (default): the style block is inside the SVG, so the file works as an ``<img>`` (there the operating
  system's preference decides) and when opened from disk;
* ``embed_style=False``: no style block, for an SVG inlined into a page whose CSP forbids inline style; the page links
  ``adaptive_css()`` (written as ``figures.css``) once.

The output has no ``style=`` attribute and no script.
"""

from __future__ import annotations

import re

from . import theme as T

_ATTR = re.compile(r'\s(fill|stroke)="§([^§]+)§"')
_TAG = re.compile(r"<(?!/)(?!\?)(?!!)([A-Za-z]+)([^>]*?)(/?)>")


def _cls(token: str) -> str:
    return token.replace(".", "-")


def _vars(theme: str, palette: int, tokens: list[str]) -> str:
    return "".join(f"--fk-{_cls(t)}:{T.resolve(t, theme, palette)};" for t in tokens)


def adaptive_css(tokens: list[str] | None = None, palette: int = 2, scope: str = ".fk") -> str:
    """The shared style sheet: tokens as custom properties, one class per token for fill and for stroke."""
    toks = tokens if tokens is not None else T.tokens(palette)
    light, dark = _vars("light", palette, toks), _vars("dark", palette, toks)
    out = [
        f"{scope}{{{light}}}",
        f"@media (prefers-color-scheme:dark){{{scope}{{{dark}}}}}",
        f':root[data-theme="dark"] {scope},[data-md-color-scheme="slate"] {scope}{{{dark}}}',
        f':root[data-theme="light"] {scope},[data-md-color-scheme="default"] {scope}{{{light}}}',
    ]
    for t in toks:
        c = _cls(t)
        out.append(f".fk-f-{c}{{fill:var(--fk-{c})}}.fk-s-{c}{{stroke:var(--fk-{c})}}")
    out.append("@media (forced-colors:active){.fk text{fill:CanvasText}.fk rect,.fk circle{fill:Canvas;stroke:CanvasText}"
               ".fk path{stroke:CanvasText}.fk marker path{fill:CanvasText;stroke:none}}")
    return "\n".join(out) + "\n"


def to_adaptive(raw: str, palette: int, embed_style: bool = True, extra_css: str = "") -> str:
    """Turn a figure's placeholder SVG (``Fig.raw_svg()``) into the adaptive SVG."""
    used: list[str] = []

    def retag(m: re.Match) -> str:
        name, attrs, close = m.groups()
        classes = []
        def take(am: re.Match) -> str:
            kind, tok = am.group(1), am.group(2)
            classes.append(f"fk-{'f' if kind == 'fill' else 's'}-{_cls(tok)}")
            if tok not in used:
                used.append(tok)
            return ""
        attrs = _ATTR.sub(take, attrs)
        if name == "svg":
            classes.insert(0, "fk")
        if not classes:
            return m.group(0)
        return f'<{name}{attrs} class="{" ".join(classes)}"{close}>'

    body = _TAG.sub(retag, raw)
    assert "§" not in body, "a colour placeholder was not turned into a class"
    if embed_style:
        css = adaptive_css(sorted(used), palette) + extra_css
        body = body.replace("<defs>", f"<style>\n{css}</style>\n<defs>", 1) if "<defs>" in body else \
            re.sub(r"(<desc [^>]*>.*?</desc>\n)", lambda m: m.group(1) + f"<style>\n{css}</style>\n", body, count=1, flags=re.S)
    return body
