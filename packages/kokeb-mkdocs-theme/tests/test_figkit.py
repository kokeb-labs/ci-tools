"""Tests of figkit's figure kinds, layout lock, adaptive output, lints and palette 2.

Golden bytes: ``fixtures/figkit/golden/`` holds the committed output of every fixture model in ``fixtures/figkit/model/``
(light, dark, adaptive, table twin, layout lock). The tests rebuild them and compare bytes, so a change in figkit that
alters a figure shows up as a diff of a committed file. After a deliberate change run

    FIGKIT_UPDATE_GOLDEN=1 python -m unittest tests.test_figkit      (from packages/kokeb-mkdocs-theme)

and review the diff. The suite also runs on Linux in CI, so the same bytes are checked on macOS and Linux. Graphviz is
needed only by the tests that run ``figkit layout`` (they skip without ``dot``); no render test calls it.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import yaml

from kokeb_mkdocs_theme.figkit import adaptive, build, core, fontsubset, kinds, layered, lint
from kokeb_mkdocs_theme.figkit import theme as T

HERE = pathlib.Path(__file__).resolve().parent
FIX = HERE / "fixtures/figkit"
MODELS = sorted((FIX / "model").glob("*.yml"))
GOLDEN = FIX / "golden"
UPDATE = bool(os.environ.get("FIGKIT_UPDATE_GOLDEN"))
PKG = HERE.parent


def outputs(model_path: pathlib.Path, lock_dir: pathlib.Path) -> dict[str, str]:
    """Every file ``kokeb-docs figures`` writes for a model figure."""
    fig = kinds.from_model(model_path, lock_dir=lock_dir)
    assert fig.problems() == [], fig.problems()
    out = {
        f"{fig.fid}.svg": fig.svg("light"),
        f"{fig.fid}.dark.svg": fig.svg("dark"),
        f"{fig.fid}.adaptive.svg": adaptive.to_adaptive(fig.raw_svg(), fig.palette),
    }
    if fig.twin is not None:
        out[f"{fig.fid}.table.html"] = build.twin_html(fig)
    return out


def dot_available() -> bool:
    return shutil.which("dot") is not None


class NoGraphviz:
    """Context: any attempt to find or run Graphviz fails the test (render must never need it)."""

    def __enter__(self):
        self._which, self._run = shutil.which, subprocess.run

        def boom(*a, **k):
            raise AssertionError("render tried to run an external program (Graphviz)")

        shutil.which = lambda name, *a, **k: None if name == "dot" else self._which(name, *a, **k)
        subprocess.run = boom
        return self

    def __exit__(self, *exc):
        shutil.which, subprocess.run = self._which, self._run


class GoldenTests(unittest.TestCase):
    def test_golden_bytes(self):
        """Light, dark, adaptive and table twin of every fixture equal the committed files, byte for byte."""
        for path in MODELS:
            with self.subTest(model=path.name):
                if UPDATE:
                    with layered.layout_mode("refresh"):
                        kinds.from_model(path, lock_dir=GOLDEN)
                    for name, text in outputs(path, GOLDEN).items():
                        (GOLDEN / name).write_text(text, encoding="utf-8")
                    continue
                with NoGraphviz():
                    produced = outputs(path, GOLDEN)
                for name, text in produced.items():
                    self.assertTrue((GOLDEN / name).is_file(), f"missing golden file {name}")
                    self.assertEqual(text, (GOLDEN / name).read_text(encoding="utf-8"), name)

    def test_font_embed_golden(self):
        """A figure that asks for ``font: embed`` carries the committed subset; the render needs no fonttools."""
        path = FIX / "model/journal-layout.bytes.yml"
        model = yaml.safe_load(path.read_text())
        model["font"] = "embed"
        fig = kinds.from_model(model, lock_dir=GOLDEN)
        if UPDATE:
            fontsubset.write_lock(GOLDEN, fig.fid, fig.svg("light"))
            (GOLDEN / "journal-layout.font.svg").write_text(fontsubset.embed(fig.svg("light"), GOLDEN, fig.fid))
            return
        got = fontsubset.embed(fig.svg("light"), GOLDEN, fig.fid)
        self.assertEqual(got, (GOLDEN / "journal-layout.font.svg").read_text())
        ET.fromstring(got)
        self.assertEqual(lint.svg_lint(got, fig.fid, font_embedded=True), [])
        meta = json.loads((GOLDEN / "journal-layout.font.json").read_text())
        self.assertLess(meta["bytes"], fontsubset.BUDGET_BYTES)
        self.assertIn("SIL Open Font License", got)

    def test_font_stale(self):
        model = yaml.safe_load((FIX / "model/journal-layout.bytes.yml").read_text())
        model["font"] = "embed"
        model["title"] = "A title with new glyphs: ZQJX"
        fig = kinds.from_model(model, lock_dir=GOLDEN)
        with self.assertRaises(fontsubset.FontStale):
            fontsubset.embed(fig.svg("light"), GOLDEN, fig.fid)

    def test_legacy_figure_bytes_unchanged(self):
        """A figure drawn with the original API (palette 1) is byte for byte what ci-tools 1.21.0 produced."""
        spec = importlib.util.spec_from_file_location("legacy_fig", FIX / "legacy_fig.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fig = mod.build()
        self.assertEqual(fig.problems(), [])
        self.assertEqual(fig.palette, 1)
        self.assertEqual(fig.svg("light"), (GOLDEN / "legacy-fig.svg").read_text())
        self.assertEqual(fig.svg("dark"), (GOLDEN / "legacy-fig.dark.svg").read_text())

    def test_model_files_follow_the_yaml_lint_rules(self):
        """The repository's yamllint config wants ``---``, two space indents and no padding after a comma."""
        import re

        for path in list(MODELS) + sorted((HERE.parents[2] / "docs/model").glob("*.yml")):
            text = path.read_text()
            self.assertTrue(text.startswith("---\n"), path.name)
            self.assertIsNone(re.search(r",  +\S", text), f"{path.name}: padding after a comma")
            self.assertIsNone(re.search(r"^\t", text, re.M), path.name)

    def test_prototype_fixtures_present(self):
        """The three prototype figures are fixtures: the state machine, the zone graph and the byte layout."""
        ids = {yaml.safe_load(p.read_text())["id"] for p in MODELS}
        self.assertTrue({"handler-health", "layers-zones", "journal-layout"} <= ids)


class DeterminismTests(unittest.TestCase):
    SCRIPT = (
        "import hashlib,sys,pathlib,json\n"
        "sys.path.insert(0, sys.argv[3])\n"
        "from kokeb_mkdocs_theme.figkit import kinds, adaptive\n"
        "h=hashlib.sha256()\n"
        "for p in sorted(pathlib.Path(sys.argv[1]).glob('*.yml')):\n"
        "    f=kinds.from_model(p, lock_dir=sys.argv[2])\n"
        "    for s in (f.svg('light'), f.svg('dark'), adaptive.to_adaptive(f.raw_svg(), f.palette)):\n"
        "        h.update(s.encode())\n"
        "print(h.hexdigest())\n"
    )

    def run_once(self, seed: str) -> str:
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(PKG))
        r = subprocess.run([sys.executable, "-I", "-c", self.SCRIPT, str(FIX / "model"), str(GOLDEN), str(PKG)], env=env,
                           capture_output=True, text=True, cwd=tempfile.gettempdir())
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_two_runs_same_hash(self):
        """Two separate processes, with different string hash seeds, give the same bytes."""
        a, b, c = self.run_once("1"), self.run_once("2"), self.run_once("random")
        self.assertEqual(a, b)
        self.assertEqual(a, c)

    def test_same_process_twice(self):
        for path in MODELS:
            one = outputs(path, GOLDEN)
            two = outputs(path, GOLDEN)
            self.assertEqual(one, two, path.name)


class LayoutLockTests(unittest.TestCase):
    def model(self):
        return yaml.safe_load((FIX / "model/handler-health.state.yml").read_text())

    def test_render_never_runs_graphviz(self):
        with NoGraphviz():
            fig = kinds.from_model(self.model(), lock_dir=GOLDEN)
            self.assertEqual(fig.problems(), [])

    def test_missing_lock(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(layered.LayoutStale) as cm:
            kinds.from_model(self.model(), lock_dir=d)
        self.assertIn("figkit layout", str(cm.exception))

    def test_stale_lock_after_model_change(self):
        m = self.model()
        m["transitions"].append({"from": "Ready", "to": "Starting", "label": "restart"})
        with self.assertRaises(layered.LayoutStale) as cm:
            kinds.from_model(m, lock_dir=GOLDEN)
        self.assertIn("stale", str(cm.exception))

    def test_label_text_change_does_not_stale_unless_size_changes(self):
        """The lock depends on node sizes and edges, so a changed alt text or title keeps it."""
        m = self.model()
        m["title"] = "Another title"
        m["alt"] = m["alt"] + " Extra words."
        kinds.from_model(m, lock_dir=GOLDEN)

    def test_lock_has_input_hash_and_no_float_noise(self):
        lock = json.loads((GOLDEN / "handler-health.layout.json").read_text())
        self.assertEqual(len(lock["input"]), 64)
        for box in lock["nodes"].values():
            self.assertTrue(all(isinstance(v, int) for v in box), box)

    @unittest.skipUnless(dot_available(), "Graphviz dot is not installed")
    def test_layout_command_writes_a_lock_that_renders(self):
        with tempfile.TemporaryDirectory() as d:
            with layered.layout_mode("refresh"):
                kinds.from_model(self.model(), lock_dir=d)
            self.assertTrue((pathlib.Path(d) / "handler-health.layout.json").is_file())
            with NoGraphviz():
                fig = kinds.from_model(self.model(), lock_dir=d)
            self.assertEqual(fig.problems(), [])
            svg = fig.svg("light")
            ET.fromstring(svg)

    @unittest.skipUnless(dot_available(), "Graphviz dot is not installed")
    def test_compare_mode_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as d:
            with layered.layout_mode("compare") as m:
                kinds.from_model(self.model(), lock_dir=d)
            self.assertEqual(m.diffs, [("handler-health", "no lock")])
            self.assertEqual(list(pathlib.Path(d).iterdir()), [])


class KindTests(unittest.TestCase):
    def test_every_fixture_has_no_problems_and_lints_clean(self):
        for path in MODELS:
            with self.subTest(model=path.name):
                fig = kinds.from_model(path, lock_dir=GOLDEN)
                files = {k: v for k, v in outputs(path, GOLDEN).items() if k.endswith(".svg")}
                found = lint.lint_fig(fig, files, build.description(fig))
                self.assertEqual(found, [])
                self.assertEqual(fig.palette, 2)
                self.assertGreaterEqual(fig.print_pt(), core.MIN_PRINT_PT)

    def test_self_loop_is_a_loop_on_the_side(self):
        """The Starting self transition is drawn as an open loop on the right side of its card, with the label."""
        svg = (GOLDEN / "handler-health.svg").read_text()
        self.assertIn("next stage", svg)
        lock = json.loads((GOLDEN / "handler-health.layout.json").read_text())
        self.assertNotIn(["Starting", "Starting"], [[e["from"], e["to"]] for e in lock["edges"]])

    def test_routes_are_orthogonal(self):
        """Every straight piece of every route is horizontal or vertical (corners are small Q curves)."""
        import re

        svg = (GOLDEN / "handler-health.svg").read_text()
        paths = re.findall(r'<path d="(M[^"]+)" fill="none" stroke="#7C8798"', svg)
        self.assertGreaterEqual(len(paths), 10)
        for d in paths:
            prev = None
            for cmd, nums in re.findall(r"([MLQ])([-\d. ]+)", d):
                v = [float(x) for x in nums.split()]
                pt = (v[-2], v[-1])
                if cmd == "L" and prev is not None:
                    self.assertTrue(abs(pt[0] - prev[0]) < 0.11 or abs(pt[1] - prev[1]) < 0.11, (d, prev, pt))
                prev = pt

    def test_schema_errors_are_listed(self):
        m = yaml.safe_load((FIX / "model/handler-health.state.yml").read_text())
        m["states"][0]["tone"] = "purple"
        m["transitions"][0]["to"] = "Nowhere"
        m["unexpected"] = 1
        with self.assertRaises(SystemExit) as cm:
            kinds.from_model(m, lock_dir=GOLDEN)
        msg = str(cm.exception)
        self.assertIn("unknown tone 'purple'", msg)
        self.assertIn("unknown state 'Nowhere'", msg)
        self.assertIn("unknown key 'unexpected'", msg)

    def test_bytes_overlap_is_an_error(self):
        m = yaml.safe_load((FIX / "model/journal-layout.bytes.yml").read_text())
        m["fields"][1]["at"] = 1
        with self.assertRaises(SystemExit) as cm:
            kinds.from_model(m, lock_dir=GOLDEN)
        self.assertIn("covered by", str(cm.exception))

    def test_matrix_needs_status_or_value(self):
        m = yaml.safe_load((FIX / "model/port-capabilities.matrix.yml").read_text())
        m["cells"][0]["value"] = 3
        with self.assertRaises(SystemExit):
            kinds.from_model(m, lock_dir=GOLDEN)

    def test_status_cells_have_text_and_glyph(self):
        """Colour is never the only carrier: every status cell has its word and a drawn mark."""
        svg = (GOLDEN / "port-capabilities.svg").read_text()
        for word in ("native", "adapted", "planned", "n/a", "missing"):
            self.assertIn(f">{word}<", svg)
        self.assertGreaterEqual(svg.count("stroke-linecap"), 6)

    def test_table_twin(self):
        html = (GOLDEN / "port-capabilities.table.html").read_text()
        self.assertIn("<details>", html)
        self.assertIn("<th scope=\"row\">I2C</th>", html)
        self.assertIn("native (1 MHz)", html)

    def test_kinds_registry(self):
        self.assertEqual(set(kinds.KINDS), {"state", "graph", "seq", "timeline", "matrix", "bytes", "pipeline"})
        for name in kinds.KINDS:
            self.assertTrue(hasattr(kinds.module(name), "validate"))
        self.assertEqual({p.name.split(".")[-2] for p in MODELS}, set(kinds.KINDS))


class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.fig = kinds.from_model(FIX / "model/bus-access.seq.yml")
        self.svg = adaptive.to_adaptive(self.fig.raw_svg(), 2)

    def test_no_style_attribute_no_script_no_placeholder(self):
        self.assertNotIn(" style=", self.svg)
        self.assertNotIn("<script", self.svg)
        self.assertNotIn("§", self.svg)
        self.assertEqual(lint.svg_lint(self.svg, "bus-access", adaptive=True), [])

    def test_follows_page_theme(self):
        self.assertIn('prefers-color-scheme:dark', self.svg)
        self.assertIn(':root[data-theme="dark"]', self.svg)
        self.assertIn('[data-md-color-scheme="slate"]', self.svg)
        self.assertIn("forced-colors:active", self.svg)

    def test_tokens_match_both_themes(self):
        for th in T.THEMES:
            self.assertIn(f"--fk-ink:{T.resolve('ink', th, 2)}", self.svg)

    def test_inline_form_has_no_style_element(self):
        inline = adaptive.to_adaptive(self.fig.raw_svg(), 2, embed_style=False)
        self.assertNotIn("<style", inline)
        self.assertIn('class="fk"', inline)
        self.assertIn("--fk-ink:", adaptive.adaptive_css())

    def test_marker_ids_prefixed(self):
        self.assertIn('id="bus-access-arrow-', self.svg)


class PaletteTests(unittest.TestCase):
    def test_palette_1_is_unchanged(self):
        self.assertEqual(T.resolve("line", "light"), "#C9D1DB")
        self.assertEqual(T.resolve("line", "dark"), "#3A4657")
        self.assertEqual(T.resolve("stone.strong", "light"), "#B5AFA9")
        self.assertEqual(T.resolve("line", "light", 1), T.BASE["line"][0])

    def test_palette_2_non_text_contrast(self):
        """The fixed tokens reach 3:1 on every background they sit on, in both themes."""
        for th in T.THEMES:
            for tok in ("line", "rail"):
                for bg in ("canvas", "card", "paper"):
                    self.assertGreaterEqual(T.contrast(T.resolve(tok, th, 2), T.resolve(bg, th, 2)), 3.0, (th, tok, bg))
            for tone in list(T.TONES) + list(T.TONES2):
                if tone.startswith("h"):
                    continue
                strong = T.resolve(f"{tone}.strong", th, 2)
                self.assertGreaterEqual(T.contrast(strong, T.resolve("canvas", th, 2)), 3.0, (th, tone, "canvas"))
                self.assertGreaterEqual(T.contrast(strong, T.resolve(f"{tone}.tint", th, 2)), 3.0, (th, tone, "tint"))

    def test_palette_2_text_on_tint(self):
        for th in T.THEMES:
            for tone in list(T.TONES) + list(T.TONES2):
                self.assertGreaterEqual(
                    T.contrast(T.resolve(f"{tone}.text", th, 2), T.resolve(f"{tone}.tint", th, 2)), 4.5, (th, tone))

    def test_status_and_heat_tokens_exist(self):
        for name in ("ok", "warn", "fail", "na", "planned", "h0", "h1", "h2", "h3", "h4"):
            self.assertIn(f"{name}.tint", T.tokens(2))
            self.assertNotIn(f"{name}.tint", T.tokens(1))

    def test_palette_1_figure_does_not_fail_on_non_text_contrast(self):
        """An old figure keeps building; the finding is an advisory only."""
        f = core.Fig("old-card", "Old", alt="One card.", width=400)
        f.card(0, 0, 200, "Card", ["line"], tone="slate")
        self.assertEqual(f.problems(), [])
        self.assertTrue(any("outline of card" in a for a in f.advisories()))
        g = core.Fig("new-card", "New", alt="One card.", width=400, palette=2)
        g.card(0, 0, 200, "Card", ["line"], tone="slate")
        self.assertEqual(g.problems(), [])
        self.assertEqual(g.advisories(), [])

    def test_non_text_failure_fails_palette_2(self):
        g = core.Fig("bad-edge", "Bad", alt="An arrow.", width=400, palette=2)
        g.nontext("hair", ("canvas",), "decorative line that carries meaning")
        self.assertTrue(any("needs 3.0:1" in p for p in g.problems()))


class PrintFitTests(unittest.TestCase):
    def test_portrait_fails_where_landscape_passes(self):
        f = core.Fig("wide", "Wide", alt="Some text on a wide figure.", width=1200, print_mode="portrait")
        f.text(0, 20, "small text", size=13)
        self.assertAlmostEqual(f.print_pt(), 13 * 510 / 1200, places=1)
        self.assertTrue(any("print portrait" in a for a in f.advisories()))
        f.print_mode = "landscape"
        self.assertAlmostEqual(f.print_pt(), 13 * 757 / 1200, places=1)
        self.assertEqual([a for a in f.advisories() if "print" in a], [])

    def test_undeclared_print_is_not_checked(self):
        f = core.Fig("x", "X", alt="Text.", width=2000)
        f.text(0, 20, "tiny", size=12)
        self.assertEqual(f.advisories(), [])


class LintTests(unittest.TestCase):
    GOOD = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" role="img" aria-labelledby="f-t f-d">'
        '<title id="f-t">T</title><desc id="f-d">D</desc><rect id="f-r" width="1" height="1"/></svg>'
    )

    def test_good(self):
        self.assertEqual(lint.svg_lint(self.GOOD, "f"), [])

    def test_defects(self):
        cases = {
            "script": self.GOOD.replace("<rect", "<script>1</script><rect"),
            "event": self.GOOD.replace("<rect", '<rect onclick="x()"').replace("<rect onclick", "<rect onclick"),
            "style attr": self.GOOD.replace("<rect", '<rect style="fill:red"'),
            "external": self.GOOD.replace("<rect", '<image href="https://example.invalid/a.png"/><rect'),
            "no viewbox": self.GOOD.replace('viewBox="0 0 10 10" ', ""),
            "no role": self.GOOD.replace('role="img" ', ""),
            "no title": self.GOOD.replace('<title id="f-t">T</title>', ""),
            "bad id": self.GOOD.replace('id="f-r"', 'id="r"'),
            "style element": self.GOOD.replace("<rect", "<style>.a{}</style><rect"),
            "data url": self.GOOD.replace("<rect", '<rect fill="url(data:x)"'),
            "too big": self.GOOD.replace("<rect", "<!--" + "x" * 70000 + "--><rect"),
        }
        for name, svg in cases.items():
            with self.subTest(name):
                self.assertTrue(lint.svg_lint(svg, "f"), name)

    def test_alt_rules(self):
        ok = "Sequence of a bus read in which the caller asks the handler and the handler answers."
        reads = "The Caller asks. The Handler answers."
        self.assertEqual(lint.alt_lint(ok, "Bus read", reads, ["Caller", "Handler"]), [])
        self.assertTrue(lint.alt_lint("Too short.", "T", reads))
        self.assertTrue(lint.alt_lint("Diagram of a bus read in which the caller asks the handler.", "T", reads))
        self.assertTrue(lint.alt_lint(ok + " And a second sentence here.", "T", reads))
        self.assertTrue(lint.alt_lint(ok, ok.rstrip("."), reads))
        self.assertTrue(lint.alt_lint(ok, "T", "Only one sentence here."))
        self.assertTrue(lint.alt_lint(ok, "T", reads, ["Missing"]))
        self.assertTrue(lint.alt_lint("TODO " + ok, "T", reads))
        self.assertTrue(lint.alt_lint(ok, "T", ""))


class BuildFlowTests(unittest.TestCase):
    """``kokeb-docs figures`` and ``figkit`` in a scratch repository, with the committed locks as the layout."""

    def run_cli(self, root, *args):
        env = dict(os.environ, PYTHONPATH=str(PKG), KOKEB_DOCS_ROOT=str(root))
        return subprocess.run([sys.executable, "-m", "kokeb_mkdocs_theme.cli", *args], cwd=root, env=env,
                              capture_output=True, text=True)

    def make_repo(self):
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "mkdocs.yml").write_text("site_name: t\n")
        (d / "docs/model").mkdir(parents=True)
        (d / "docs/index.md").write_text("# t\n\n<!-- figure: bus-access -->\n<!-- /figure -->\n")
        for p in MODELS:
            shutil.copy(p, d / "docs/model" / p.name)
        (d / "docs/diagrams").mkdir()
        for p in GOLDEN.glob("*.layout.json"):
            shutil.copy(p, d / "docs/diagrams" / p.name)
        return d

    def test_write_then_check(self):
        d = self.make_repo()
        r = self.run_cli(d, "figures")
        self.assertEqual(r.returncode, 0, r.stderr)
        for name in ("bus-access.svg", "bus-access.dark.svg", "bus-access.adaptive.svg", "port-capabilities.table.html",
                     "figures.json", "index.md"):
            self.assertTrue((d / "docs/diagrams" / name).is_file(), name)
        r = self.run_cli(d, "figures", "--check")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("<picture>", (d / "docs/index.md").read_text())
        index = (d / "docs/diagrams/figures.json").read_text()
        self.assertNotIn(str(d), index)  # sources are repository paths, never absolute
        self.assertNotIn(str(d), (d / "docs/diagrams/index.md").read_text())
        # the output equals the golden files
        for p in GOLDEN.glob("*.svg"):
            out = d / "docs/diagrams" / p.name
            if out.is_file() and p.name != "journal-layout.font.svg":
                self.assertEqual(out.read_text(), p.read_text(), p.name)
        r = self.run_cli(d, "figures", "--lint")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_stale_layout_fails_the_check(self):
        d = self.make_repo()
        self.run_cli(d, "figures")
        model = d / "docs/model/handler-health.state.yml"
        model.write_text(model.read_text().replace("- {id: Unknown, tone: slate}",
                                                   "- {id: Unknown, tone: slate, note: a second line}"))
        r = self.run_cli(d, "figures", "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("layout stale", r.stderr)
        self.assertIn("figkit layout handler-health", r.stderr)

    def test_edited_svg_is_caught(self):
        d = self.make_repo()
        self.run_cli(d, "figures")
        svg = d / "docs/diagrams/bus-access.svg"
        svg.write_text(svg.read_text().replace("Caller", "Client", 1))
        r = self.run_cli(d, "figures", "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("bus-access.svg is stale", r.stderr)

    def test_new_scaffolds_each_kind(self):
        for kind in kinds.KINDS:
            with self.subTest(kind=kind):
                d = pathlib.Path(tempfile.mkdtemp())
                self.addCleanup(shutil.rmtree, d, True)
                (d / "mkdocs.yml").write_text("site_name: t\n")
                (d / "docs").mkdir()
                (d / "docs/page.md").write_text("# Page\n")
                r = self.run_cli(d, "figkit", "new", "--kind", kind, "--id", "demo", "--page", "docs/page.md")
                self.assertEqual(r.returncode, 0, r.stderr)
                model = d / "docs/model" / f"demo.{kind}.yml"
                self.assertTrue(model.is_file())
                self.assertTrue(model.read_text().startswith("---\n"))
                self.assertIn("<!-- figure: demo -->", (d / "docs/page.md").read_text())
                # the scaffold is a valid model: the schema accepts it; only the TODO text and (for layered
                # kinds) the missing lock stop the build, which is the point
                data = yaml.safe_load(model.read_text())
                kinds.module(kind).validate(data, str(model))
                r = self.run_cli(d, "figures")
                self.assertEqual(r.returncode, 1)
                self.assertTrue("TODO" in r.stderr or "layout" in r.stderr, r.stderr)
                again = self.run_cli(d, "figkit", "new", "--kind", kind, "--id", "demo")
                self.assertEqual(again.returncode, 1)

    @unittest.skipUnless(dot_available(), "Graphviz dot is not installed")
    def test_scaffold_to_green_with_layout_command(self):
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "mkdocs.yml").write_text("site_name: t\n")
        (d / "docs").mkdir()
        self.assertEqual(self.run_cli(d, "figkit", "new", "--kind", "state", "--id", "demo").returncode, 0)
        model = d / "docs/model/demo.state.yml"
        text = model.read_text()
        text = text.replace("alt: TODO one sentence, 40 to 300 characters, saying what the figure shows",
                            "alt: State machine of a worker that is Idle until it is started, then Busy until it is done.")
        text = text.replace("  TODO two or more sentences that name every state, participant, lane or column and say what\n"
                            "  the figure tells the reader.",
                            "  The worker starts Idle. A start moves it to Busy, and done returns it to Idle.")
        model.write_text(text)
        r = self.run_cli(d, "figkit", "layout")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((d / "docs/diagrams/demo.layout.json").is_file())
        r = self.run_cli(d, "figures")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.run_cli(d, "figures", "--check").returncode, 0)

    def test_mermaid_fences_are_reported_then_banned(self):
        d = self.make_repo()
        (d / "docs/page.md").write_text("# P\n\n```mermaid\nflowchart TD\n  A-->B\n```\n")
        (d / "README.md").write_text("# R\n\n```mermaid\nflowchart TD\n  A-->B\n```\n")
        self.run_cli(d, "figures")
        r = self.run_cli(d, "figures", "--lint")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("WARN docs/page.md: 1 mermaid fence", r.stdout)
        self.assertNotIn("README.md", r.stdout)  # allowed there
        r = self.run_cli(d, "figures", "--lint", "--ban-mermaid")
        self.assertEqual(r.returncode, 1)
        self.assertIn("ERROR docs/page.md", r.stdout)

    def test_render_time_budget(self):
        """Rendering every fixture (all three outputs each) stays far under the budget of 10 s (ADR 0001)."""
        import time

        t0 = time.perf_counter()
        for path in MODELS:
            outputs(path, GOLDEN)
        self.assertLess(time.perf_counter() - t0, 10.0)

    def test_existing_module_figures_are_unaffected(self):
        """A repository with only a module figure (no models, no locks) builds as before, with no new files."""
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "mkdocs.yml").write_text("site_name: t\n")
        (d / "docs/diagrams/figures").mkdir(parents=True)
        (d / "docs/diagrams/figures/old.py").write_text(
            '"""Old.\n\nReads: Two cards.\n"""\nfrom kokeb_mkdocs_theme.figkit import Fig\n\n\ndef build(_):\n'
            '    f = Fig("old", "Old", alt="Two cards joined by an arrow.", width=600)\n'
            '    a = f.card(0, 0, 200, "A", tone="blue", accent=True)\n    b = f.card(300, 0, 200, "B")\n'
            '    f.connect(a, b, "right", "left")\n    return f\n')
        self.assertEqual(self.run_cli(d, "figures").returncode, 0)
        names = sorted(p.name for p in (d / "docs/diagrams").iterdir() if p.is_file())
        self.assertEqual(names, ["figures.json", "index.md", "old.dark.svg", "old.svg"])
        entry = json.loads((d / "docs/diagrams/figures.json").read_text())["old"]
        self.assertEqual(sorted(entry), ["alt", "description", "profile", "source", "sources", "title", "width"])
        self.assertEqual(self.run_cli(d, "figures", "--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
