"""A figure drawn with the figkit API as it was before the figure kinds (palette 1). Its committed output
(``golden/legacy-fig.svg`` and ``.dark.svg``) was made by the code of ci-tools 1.21.0, so a test that rebuilds it
proves the old API still gives the same bytes."""

from kokeb_mkdocs_theme.figkit import Fig


def build():
    f = Fig("legacy-fig", "Legacy figure", alt="Two cards joined by an arrow, a region, a note and a chip row.",
            width=900, kicker="Fixture", subtitle="Drawn with the original figkit calls.",
            legend=[("blue", "a card"), ("~solid", "runs next"), ("~dashed", "passes files")])
    r = f.region(0, 0, 840, 230, "Region", tone="slate", sub="with a sub label")
    a = f.card(24, 56, 240, "First", ["one body line", "another body line"], tone="blue", accent=True, tag="tag")
    b = f.card(400, 56, 240, "Second", ["body"], tone="amber")
    c = f.card(24, 150, 240, "Third", [], tone="green", h=56, center=True, accent=True)
    f.connect(a, b, "right", "left", label="calls")
    f.connect(a, c, "bottom", "top", dashed=True)
    f.chips(400, 150, 400, ["alpha", "beta", "gamma"], tone="violet")
    f.note(0, 250, 840, "A note under the region with a sentence of text.", tone="brand", title="Note")
    f.step(700, 90, 1)
    return f
