"""Colour tokens for figkit figures. Every colour has a light and a dark value.

A figure never writes a hex value. It names a token: a base token (``"ink"``, ``"card"``) or a tone part
(``"blue.tint"``, ``"amber.strong"``). The figure is laid out once and ``Fig.svg(theme)`` resolves the tokens for the
light or the dark theme, so the two renderings cannot drift apart.

A tone has four parts:

* ``strong`` - stripes, arrows, icons and the outline of an accented card;
* ``text``   - text written on the tone's tint;
* ``tint``   - fill of a region or an accented card;
* ``soft``   - outline of a region or a chip.

Every text / background pair used by a figure is checked against WCAG 2.x (at least 4.5:1) in both themes when the
figure is built, so a palette change that breaks contrast fails the build.
"""

from __future__ import annotations

#: Base tokens: name -> (light, dark).
BASE: dict[str, tuple[str, str]] = {
    "canvas": ("#FFFFFF", "#0E131A"),  # figure background
    "frame": ("#E2E7EE", "#283241"),  # figure outline
    "card": ("#FFFFFF", "#151C26"),  # card fill
    "paper": ("#F5F7FA", "#18202B"),  # quiet band
    "ink": ("#0E1726", "#E8EDF3"),  # primary text
    "ink2": ("#2B3442", "#D2DAE4"),  # body text
    "muted": ("#566070", "#9AA6B5"),  # secondary text (still >= 4.5:1 on card and paper)
    "line": ("#C9D1DB", "#3A4657"),  # card outline
    "hair": ("#E2E7EE", "#252F3C"),  # rules
    "rail": ("#8893A2", "#6C7889"),  # neutral arrows (never text)
    "on": ("#FFFFFF", "#0E131A"),  # text on a solid pill
}

#: Tones: name -> {"light": (strong, text, tint, soft), "dark": (strong, text, tint, soft)}.
TONES: dict[str, dict[str, tuple[str, str, str, str]]] = {
    # Kokeb copper on light, star gold on dark: the same pairing the site uses for links.
    "brand": {"light": ("#9A4A17", "#7A360E", "#FBEFE6", "#E9C3A6"), "dark": ("#F4B942", "#F8D27A", "#2A2113", "#6B5424")},
    "blue": {"light": ("#2563EB", "#1E429F", "#EAF2FF", "#BCD2F9"), "dark": ("#60A5FA", "#BFDBFE", "#13233A", "#2B4C78")},
    "teal": {"light": ("#0B7A72", "#0B5F59", "#E6F6F4", "#A6DCD5"), "dark": ("#2BB3A3", "#A7F3E6", "#0F2A28", "#215A54")},
    "violet": {"light": ("#7C3AED", "#5B21B6", "#F3EEFF", "#D5C5FA"), "dark": ("#A78BFA", "#DDD6FE", "#221A3A", "#4B3A82")},
    "amber": {"light": ("#C26A05", "#8A3C0B", "#FFF5E3", "#F1CF93"), "dark": ("#FBBF24", "#FDE68A", "#2C2310", "#6A5220")},
    "rose": {"light": ("#DB2752", "#9F1239", "#FFEEF2", "#F5BECB"), "dark": ("#FB7185", "#FECDD3", "#321820", "#6E3141")},
    "green": {"light": ("#15803D", "#14532D", "#EAF7EF", "#B2E2C2"), "dark": ("#4ADE80", "#BBF7D0", "#11281A", "#285A3A")},
    "slate": {"light": ("#64748B", "#334155", "#F1F4F8", "#CBD5E1"), "dark": ("#94A3B8", "#E2E8F0", "#1B232E", "#3A4656")},
    # Three more hues so each chip pin type has its own colour (hardware.model.PIN_TYPES): far enough from the tones
    # above, and from each other, in both themes. stone is a pale warm grey, for a pin that is not connected.
    "magenta": {"light": ("#A21CAF", "#86198F", "#FDF0FF", "#F0C6F7"), "dark": ("#F0ABFC", "#F5D0FE", "#2E1533", "#6B2E73")},
    "brown": {"light": ("#7C4A1E", "#6B3F17", "#F8F1EA", "#DCC3A8"), "dark": ("#D6A26B", "#F1D5B5", "#2A1F14", "#66492C")},
    "stone": {"light": ("#B5AFA9", "#57534E", "#F6F5F4", "#DDD9D5"), "dark": ("#57534E", "#D6D3D1", "#1F1D1B", "#3F3B37")},
}

PARTS = ("strong", "text", "tint", "soft")
THEMES = ("light", "dark")

#: Palette versions. ``1`` is the original palette: every figure written before palette 2 keeps it, so its bytes do not
#: change. ``2`` is the same palette with the failing non-text colours fixed (WCAG 2.x 1.4.11, 3:1 for the outline of a
#: card, an arrow and an accent stripe) plus the ``status`` and ``heat`` families. New figure kinds use palette 2; an
#: existing figure opts in with ``Fig(..., palette=2)``. Changing the default is a documented, versioned decision
#: (docs/figkit.md, "Palette versions").
DEFAULT_PALETTE = 1

#: Palette 2 overrides of base tokens: name -> (light, dark).
BASE2: dict[str, tuple[str, str]] = {
    "line": ("#738093", "#6C7889"),  # card outline: >= 3:1 on canvas, card and paper in both themes (was 1.54:1)
    "rail": ("#7C8798", "#6C7889"),  # neutral arrows: >= 3:1 on canvas, card and paper in both themes
}

#: Palette 2 additions and overrides of tones.
TONES2: dict[str, dict[str, tuple[str, str, str, str]]] = {
    "stone": {"light": ("#857F79", "#57534E", "#F6F5F4", "#DDD9D5"), "dark": ("#8C8780", "#D6D3D1", "#1F1D1B", "#3F3B37")},
    # Status family: the meaning is always also written as text and drawn as a glyph, never colour alone.
    "ok": TONES["green"],
    "warn": TONES["amber"],
    "fail": TONES["rose"],
    "na": {"light": ("#64748B", "#334155", "#F1F4F8", "#CBD5E1"), "dark": ("#94A3B8", "#E2E8F0", "#1B232E", "#3A4656")},
    "planned": TONES["violet"],
    # Heat ramp, step 0 (lowest) to 4: the fill is ``tint``, the text on it is ``text``, the outline is ``strong``.
    "h0": {"light": ("#2563EB", "#0E1726", "#EAF2FF", "#BCD2F9"), "dark": ("#60A5FA", "#E8EDF3", "#13233A", "#2B4C78")},
    "h1": {"light": ("#2563EB", "#0E1726", "#CFE0FB", "#BCD2F9"), "dark": ("#60A5FA", "#E8EDF3", "#1E3A63", "#2B4C78")},
    "h2": {"light": ("#1E429F", "#0E1726", "#9CC0F5", "#BCD2F9"), "dark": ("#93C5FD", "#E8EDF3", "#2F5FA6", "#2B4C78")},
    "h3": {"light": ("#1E429F", "#FFFFFF", "#3F73D8", "#BCD2F9"), "dark": ("#BFDBFE", "#0E131A", "#60A5FA", "#2B4C78")},
    "h4": {"light": ("#1E429F", "#FFFFFF", "#1E429F", "#BCD2F9"), "dark": ("#BFDBFE", "#0E131A", "#BFDBFE", "#2B4C78")},
}


def resolve(token: str, theme: str, palette: int = 1) -> str:
    """Hex value of ``token`` in ``theme`` and ``palette``; raises KeyError for an unknown token."""
    i = THEMES.index(theme)
    if palette >= 2 and token in BASE2:
        return BASE2[token][i]
    if token in BASE:
        return BASE[token][i]
    tone, _, part = token.partition(".")
    if palette >= 2 and tone in TONES2 and part in PARTS:
        return TONES2[tone][theme][PARTS.index(part)]
    if tone in TONES and part in PARTS:
        return TONES[tone][theme][PARTS.index(part)]
    raise KeyError(f"unknown colour token {token!r}")


def tokens(palette: int = 1) -> list[str]:
    """Every token name of a palette, sorted."""
    names = list(BASE)
    tones = dict(TONES)
    if palette >= 2:
        tones.update(TONES2)
    names += [f"{t}.{p}" for t in tones for p in PARTS]
    return sorted(set(names))


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(fg: str, bg: str) -> float:
    """WCAG 2.x contrast ratio between two hex colours."""
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)
