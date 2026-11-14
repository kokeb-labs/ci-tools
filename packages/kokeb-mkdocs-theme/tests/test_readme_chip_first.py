"""The chip-first README: the overview, capabilities and frames of docs/hardware.yml, their figures and regions, and
``kokeb-docs readme --check|--migrate``."""

from __future__ import annotations

import copy
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

from kokeb_mkdocs_theme import readme
from kokeb_mkdocs_theme.figkit import READ_WIDTH
from kokeb_mkdocs_theme.hardware import icons, model, render

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parents[2] / "templates/mkdocs-site"
FIXTURE = HERE / "fixtures/readme-chip-first"

# The regions a driver repository generates itself (tools/docs/generators/), stubbed for the template site.
STUB_GENERATOR = '''
def quickstart():
    return "```cpp\\nint main() { return 0; }\\n```\\n"


def card():
    return "| Document | Revision |\\n| --- | --- |\\n| XMPL100-DS | A |\\n"


REGIONS = {"quickstart-code": quickstart, "datasheet-card": card}
'''


def data() -> dict:
    return yaml.safe_load((FIXTURE / "hardware.yml").read_text())


def site_root(tmp: str) -> pathlib.Path:
    """A copy of the template site with the fixture's hardware description, headers and stub generators."""
    site = pathlib.Path(tmp) / "site"
    shutil.copytree(TEMPLATE, site)
    shutil.copy(FIXTURE / "hardware.yml", site / "docs/hardware.yml")
    shutil.copytree(FIXTURE / "inc", site / "inc")
    gen = site / "tools/docs/generators"
    gen.mkdir(parents=True)
    (gen / "stub.py").write_text(STUB_GENERATOR)
    return site


def parse(d: dict, root: pathlib.Path) -> model.Hardware:
    return model.parse(d, root)


def problems(d: dict, root: pathlib.Path) -> list[str]:
    try:
        parse(d, root)
    except model.HardwareError as e:
        return e.problems
    return []


class SchemaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = site_root(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fixture_is_valid(self):
        hw = parse(data(), self.root)
        self.assertEqual(hw.doc.overview.category, "Digital temperature sensor")
        self.assertEqual(len(hw.doc.capabilities), 6)
        self.assertEqual([f.id for f in hw.doc.frames], ["spi"])
        self.assertEqual(hw.doc.frames[0].waveform.spi_mode, 0)

    def test_without_the_keys_nothing_changes(self):
        d = data()
        for k in ("overview", "driver", "capabilities", "frames"):
            d.pop(k)
        hw = parse(d, self.root)
        ids = render.figure_ids(hw)
        self.assertFalse([i for i in ids if i.startswith(("chip-hero", "chip-capabilities", "chip-frame",
                                                          "chip-wiring"))], ids)

    def test_names_are_checked_against_the_headers(self):
        d = data()
        d["capabilities"][0]["api"].append("ReadHumidity")
        d["capabilities"][0]["registers"].append("HUMIDITY")
        p = problems(d, self.root)
        self.assertTrue(any("capabilities[0].api" in x and "ReadHumidity" in x for x in p), p)
        self.assertTrue(any("capabilities[0].registers" in x and "HUMIDITY" in x for x in p), p)

    def test_capability_values(self):
        d = data()
        d["capabilities"][1].update(icon="rocket", status="maybe")
        d["capabilities"][2]["docs"] = "nowhere.md"
        d["capabilities"][3]["api"] = []
        d["capabilities"][4]["id"] = d["capabilities"][5]["id"]
        p = "\n".join(problems(d, self.root))
        for want in ("capabilities[1].icon", "capabilities[1].status", "capabilities[2].docs",
                     "capabilities[3].api", "is listed twice"):
            self.assertIn(want, p)

    def test_overview_values(self):
        d = data()
        d["overview"]["summary"] += "."
        d["overview"]["specs"] += copy.deepcopy(d["overview"]["specs"])
        d["overview"]["applications"][0] = {"label": "Ovens", "ref": "nope"}
        p = "\n".join(problems(d, self.root))
        for want in ("overview.summary", "overview.specs: 8 specs", "overview.applications[0].ref"):
            self.assertIn(want, p)

    def test_frame_fields_cover_every_bit_once(self):
        d = data()
        fr = d["frames"][0]
        fr["rows"][0]["fields"][1]["bits"] = [13, 8]  # gap at bit 14
        fr["rows"][1]["fields"][2]["bits"] = [8, 0]  # overlap at bit 8
        fr["rows"][2]["fields"].pop()  # bits 7 to 0 in no field
        p = "\n".join(problems(d, self.root))
        self.assertIn("rows[0].fields: field 'address' starts at bit 13", p)
        self.assertIn("rows[1].fields: field 'any value' starts at bit 8", p)
        self.assertIn("rows[2].fields: bits 7 to 0 are in no field", p)

    def test_decode_and_waveform(self):
        d = data()
        fr = d["frames"][0]
        fr["decode"] = {"row": "Reply", "field": "register data", "bits": [{"bit": b, "name": f"b{b}"}
                                                                           for b in range(7)]}
        fr["waveform"]["spi_mode"] = 4
        fr["waveform"]["lanes"].append({"name": "SDX", "row": "Nope"})
        p = "\n".join(problems(d, self.root))
        self.assertIn("frames[0].decode.bits: name each of the 8 bits", p)
        self.assertIn("frames[0].waveform.spi_mode", p)
        self.assertIn("frames[0].waveform.lanes[2].row: no row 'Nope'", p)


class FiguresTest(unittest.TestCase):
    def test_figures_are_clean_readable_and_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site_root(tmp)
            hw = parse(data(), root)
            ids = render.figure_ids(hw)
            for fid in ("chip-hero", "chip-capabilities", "chip-frame-spi", "chip-wiring-typical"):
                self.assertIn(fid, ids)
                a, b = render.build(hw, fid), render.build(parse(data(), root), fid)
                self.assertEqual(a.problems(), [], fid)
                self.assertEqual(a.profile, "overview", fid)
                self.assertGreaterEqual(a.min_text_px * min(1.0, READ_WIDTH / a.width), 11, fid)
                self.assertTrue(a.doc.startswith("Reads:"), fid)
                self.assertTrue(a.alt.strip(), fid)
                for theme in ("light", "dark"):
                    self.assertEqual(a.svg(theme), b.svg(theme), f"{fid} {theme}")
                    self.assertIn("<title", a.svg(theme))

    def test_alt_text_carries_the_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            hw = parse(data(), site_root(tmp))
            hero = render.build(hw, "chip-hero")
            self.assertIn("-40 to +125 °C measurement range", hero.alt)
            frame = render.build(hw, "chip-frame-spi")
            self.assertIn("address (bits 14 to 8)", frame.alt)
            wiring = render.build(hw, "chip-wiring-typical")
            self.assertIn("SPI SCK to SCLK (Transfer())", wiring.alt)

    def test_a_field_too_narrow_for_its_name_is_a_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = data()
            d["frames"][0]["rows"][0]["fields"][0]["name"] = "read not write"
            fig = render.build(parse(d, site_root(tmp)), "chip-frame-spi")
            self.assertTrue(any("give it a short name" in p for p in fig.problems()), fig.problems())

    def test_series_part_reaches_the_chip(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = data()
            c = d["circuits"][0]
            c["parts"].append({"id": "R2", "kind": "resistor", "value": "33 Ω"})
            nets = {n["name"]: n for n in c["nets"]}
            nets["SDI"]["nodes"] = ["U1.SDI", "R2.2"]
            c["nets"].append({"name": "MOSI", "nodes": ["R2.1", "U2.MOSI"]})
            fig = render.build(parse(d, site_root(tmp)), "chip-wiring-typical")
            self.assertEqual(fig.problems(), [])
            self.assertIn("SPI MOSI to SDI through R2 33 Ω", fig.alt)

    def test_icons_read_on_their_disc(self):
        from kokeb_mkdocs_theme.figkit import Fig

        fig = Fig("icons", "Icons", alt="Every icon.", profile="overview")
        for k, name in enumerate(sorted(icons.ICONS)):
            icons.draw(fig, name, 40 + (k % 10) * 80, 40 + (k // 10) * 80, 56, "brand")
        self.assertEqual(fig.problems(), [])
        for theme in ("light", "dark"):
            fig.svg(theme)


class RegionsTest(unittest.TestCase):
    def test_regions_are_written_and_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = site_root(tmp)
            shutil.copy(FIXTURE / "README.md.fixture", site / "README.md")
            for cmd in ("figures", "gen"):
                r = run_cli(site, cmd)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            text = (site / "README.md").read_text()
            self.assertIn("The **XMPL100** is a digital temperature sensor", text)
            self.assertIn("(1 Features, p. 1).", text)
            self.assertIn("- Thermal protection of power stages", text)
            self.assertIn("| [Alert window](docs/hardware.md) |", text)
            self.assertIn("`SetAlertThresholdsC`, `ReadStatus` | `ALERT_HIGH`, `ALERT_LOW`, `STATUS` | Supported |",
                          text)
            self.assertIn("docs/diagrams/chip-hero.dark.svg", text)
            for line in text.split("\n"):
                if not line.startswith(("|", "<", "  ", "[![")):
                    self.assertLessEqual(len(line), 120, line)
            r = run_cli(site, "check")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("[readme] OK", r.stdout)
            # A capability's line changes: the coverage table and the figure are stale.
            y = site / "docs/hardware.yml"
            y.write_text(y.read_text().replace("Protects each result", "Guards each result"))
            r = run_cli(site, "check")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("stale", r.stderr)


def run_cli(cwd, *args):
    env = dict(os.environ, NO_MKDOCS_2_WARNING="1")
    env.pop("KOKEB_DOCS_ROOT", None)
    env.pop("KOKEB_DOCS_CONFIG", None)
    return subprocess.run([sys.executable, "-m", "kokeb_mkdocs_theme.cli", *args], cwd=cwd, env=env,
                          capture_output=True, text=True)


class ReadmeTest(unittest.TestCase):
    def test_layout_rules(self):
        good = (FIXTURE / "README.md.fixture").read_text()
        self.assertEqual(readme.check(good), [])
        layered = good.replace("<!-- figure: chip-hero -->", "<!-- figure: driver-layers -->\n<!-- /figure -->\n\n"
                               "<!-- figure: chip-hero -->")
        self.assertTrue(any("driver-layers" in p for p in readme.check(layered)))
        swapped = good.replace("## What it does", "## X").replace("## Where it is used", "## What it does") \
            .replace("## X", "## Where it is used")
        self.assertTrue(any("section 1 is 'Where it is used'" in p for p in readme.check(swapped)))
        late = good.replace("<!-- generated: chip-summary -->\n<!-- /generated -->\n\n", "")
        self.assertTrue(any("chip-summary" in p for p in readme.check(late)))
        no_wiring = good.replace("<!-- figure: chip-wiring-typical -->\n<!-- /figure -->\n", "")
        self.assertTrue(any("chip-wiring-" in p for p in readme.check(no_wiring)))
        module = good.replace("## Inside the chip", "## Inside the module")
        self.assertEqual(readme.check(module), [])

    def test_migrate_keeps_everything_but_the_layering(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = site_root(tmp)
            old = (FIXTURE / "README.old.fixture").read_text()
            (site / "README.md").write_text(old)
            r = run_cli(site, "readme", "--check")
            self.assertEqual(r.returncode, 1)
            r = run_cli(site, "readme", "--migrate")
            self.assertEqual(r.returncode, 0, r.stderr)
            for cmd in ("figures", "gen"):
                r = run_cli(site, cmd)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            new = (site / "README.md").read_text()
            self.assertEqual(readme.check(new), [])
            self.assertNotIn("driver-layers", new)
            self.assertNotIn("| **Chip** |", new)
            # Every other line of the old README is still there: generated bodies are refilled and the old chip
            # paragraph is re-wrapped from "This driver" on, so those are compared apart.
            inside, intro = False, False
            for line in old.split("\n"):
                if line.startswith(("<!-- generated:", "<!-- figure:")):
                    inside = True
                if inside:
                    inside = not line.startswith(("<!-- /generated", "<!-- /figure"))
                    continue
                intro = line.startswith("The XMPL100 measures") or (intro and bool(line.strip()))
                # The headings of the sections the layout retires (At a glance, Use it on your MCU, the old
                # What it does) go; their content is checked line by line like the rest.
                if intro or not line.strip() or line.startswith(("| **Chip** |", "**1. Wire it**", "## ")):
                    continue
                self.assertIn(line, new)
            self.assertIn("This driver starts it safely, reads it continuously or on demand", new)
            r = run_cli(site, "check")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # Migrating twice changes nothing.
            self.assertEqual(readme.migrate(new, model.load(site)), new)


if __name__ == "__main__":
    unittest.main()
