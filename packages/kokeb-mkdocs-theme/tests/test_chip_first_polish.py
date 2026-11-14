"""The chip-first polish of 1.20: the home page layout (``readme --site``), the migration of unknown sections, parts
between the MCU and the chip in the wiring figure, several hooks on one wire, supplies that reach no chip pin, long
names in the figures, the applications citation, long frames, register aliases, protocol drivers and ``Inside the
part``."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest

from kokeb_mkdocs_theme import readme
from kokeb_mkdocs_theme.generators import hardware as gen_hw
from kokeb_mkdocs_theme.hardware import render

from test_readme_chip_first import FIXTURE, TEMPLATE, data, parse, problems, run_cli, site_root


def circuit(d: dict) -> dict:
    return d["circuits"][0]


def nets(d: dict) -> dict:
    return {n["name"]: n for n in circuit(d)["nets"]}


def texts(fig) -> list[str]:
    return [s for _bb, _fg, _bg, s, _z in fig._texts]


class Page:
    """The bit of a MkDocs page the generators use."""

    def rel(self, path: str) -> str:
        return path


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = site_root(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def hw(self, d: dict):
        return parse(d, self.root)

    def fig(self, d: dict, fid: str):
        f = render.build(self.hw(d), fid)
        self.assertEqual(f.problems(), [], fid)
        for theme in ("light", "dark"):
            f.svg(theme)
        return f


class WiringTest(Case):
    def test_a_buffer_between_mcu_and_chip(self):
        d = data()
        c = circuit(d)
        c["parts"].append({"id": "U3", "kind": "ic", "label": "Level shifter", "pins": ["A", "Y", "VCC", "GND"]})
        n = nets(d)
        n["SDI"]["nodes"] = ["U1.SDI", "U3.Y"]
        c["nets"].append({"name": "MOSI", "nodes": ["U2.MOSI", "U3.A"]})
        n["+3V3"]["nodes"].append("U3.VCC")
        n["GND"]["nodes"].append("U3.GND")
        fig = self.fig(d, "chip-wiring-typical")
        self.assertIn("MCU SPI MOSI to Level shifter A", fig.alt)
        self.assertIn("Level shifter Y to SDI (Transfer())", fig.alt)
        self.assertIn("Level shifter", texts(fig))

    def test_a_transceiver_with_a_series_resistor_and_more_mcu_wires(self):
        d = data()
        c = circuit(d)
        c["parts"] += [{"id": "U3", "kind": "ic", "label": "Transceiver", "pins": ["DI", "RO", "DE", "B"]},
                       {"id": "R2", "kind": "resistor", "value": "33 Ω"}]
        n = nets(d)
        n["SDI"]["nodes"] = ["U1.SDI", "R2.2"]
        n["SDO"]["nodes"] = ["U1.SDO", "U3.RO"]  # chip pin straight to the part
        c["nets"] += [{"name": "Bus", "nodes": ["R2.1", "U3.B"]},
                      {"name": "MOSI", "nodes": ["U2.MOSI", "U3.DI"], "hook": "transfer"},
                      {"name": "MISO", "nodes": ["U2.MISO", "U3.DE"]}]
        fig = self.fig(d, "chip-wiring-typical")
        self.assertIn("Transceiver B to SDI through R2 33 Ω", fig.alt)
        self.assertIn("MCU SPI MOSI to Transceiver DI (Transfer())", fig.alt)
        self.assertIn("MCU SPI MISO to Transceiver DE", fig.alt)

    def test_a_load_switch_feeds_the_chip_supply(self):
        d = data()
        c = circuit(d)
        c["parts"] += [{"id": "U3", "kind": "ic", "label": "Load switch", "pins": ["IN", "OUT", "EN"]},
                       {"id": "J1", "kind": "connector", "label": "3.3 V in", "pins": ["V", "G"]}]
        n = nets(d)
        n["+3V3"]["nodes"] = ["U1.VDD", "C1.1", "R1.1", "U3.OUT"]
        n["GND"]["nodes"].append("J1.G")
        c["nets"] += [{"name": "VIN", "kind": "supply", "nodes": ["J1.V", "U3.IN", "U2.VDD"]},
                      {"name": "PWR_EN", "nodes": ["U2.IRQ", "U3.EN"], "hook": "reset"}]
        n["ALERT"]["nodes"] = ["U1.ALERT", "R1.2"]
        fig = self.fig(d, "chip-wiring-typical")
        self.assertIn("MCU GPIO (IRQ) to Load switch EN (GpioSet(CtrlPin::Reset))", fig.alt)
        self.assertIn("Load switch OUT to VDD", fig.alt)

    def test_nothing_reaches_the_chip_no_figure(self):
        d = data()
        c = circuit(d)
        c["nets"] = [x for x in c["nets"] if x["name"] in ("+3V3", "GND", "ALERT")]
        nets(d)["ALERT"]["nodes"] = ["U1.ALERT", "R1.2"]
        c["unused"] = ["U1.SCLK", "U1.SDI", "U1.SDO", "U1.CS_N", "U1.RESET_N", "U2.SCK", "U2.MOSI", "U2.MISO",
                       "U2.CS", "U2.RST", "U2.IRQ"]
        hw = self.hw(d)
        self.assertNotIn("chip-wiring-typical", render.figure_ids(hw))
        self.assertEqual(render.wiring_skipped(hw), ["typical"])
        # The README then needs no wiring figure.
        good = (FIXTURE / "README.md.fixture").read_text().replace(
            "<!-- figure: chip-wiring-typical -->\n<!-- /figure -->\n", "")
        self.assertEqual(readme.check(good, hw), [])

    def test_two_hooks_on_one_wire(self):
        d = data()
        d["hooks"].append({"id": "read", "call": "Read()", "kind": "uart"})
        nets(d)["SDO"]["hook"] = ["transfer", "read"]
        fig = self.fig(d, "chip-wiring-typical")
        self.assertIn("SPI MISO to SDO (Transfer() and Read())", fig.alt)
        self.assertIn("Read()", texts(fig))
        d["circuits"][0]["nets"][4]["hook"] = ["transfer", "transfer"]
        self.assertTrue(any("distinct hook ids" in p for p in problems(d, self.root)))

    def test_a_supply_with_no_chip_pin_names_what_it_feeds(self):
        d = data()
        c = circuit(d)
        c["parts"] += [{"id": "C2", "kind": "capacitor", "value": "10 µF"},
                       {"id": "Q1", "kind": "ic", "label": "Battery switch", "pins": ["S", "D"]}]
        c["nets"].append({"name": "VBAT_SW", "kind": "supply", "nodes": ["Q1.D", "C2.1"]})
        c["unused"] = ["Q1.S"]
        nets(d)["GND"]["nodes"].append("C2.2")
        fig = self.fig(d, "chip-wiring-typical")
        joined = " ".join(texts(fig))
        self.assertIn("VBAT_SW (no XMPL100 pin): Q1.D", joined)
        self.assertNotIn("VBAT_SW: ·", joined)


class OverflowTest(Case):
    def test_long_names_wrap_or_ellipsise(self):
        d = data()
        d["chip"] = "XMPL100 temperature sensor (generic, any vendor)"
        d["package"]["type"] = "SOIC-8 narrow body, or a JST GH 8-pin connector on a module"
        d["refs"]["features"]["section"] = "Distinctive characteristics and electrical characteristics of the part"
        for s in d["overview"]["specs"]:
            s["ref"] = "features"
        d["capabilities"][0]["registers"] = ["TEMP_MSB_AND_LSB_AND_EVERYTHING_ELSE_IN_ONE_LONG_NAME"]
        with open(self.root / "inc/xmpl100_registers.hpp", "a") as f:
            f.write("\n// TEMP_MSB_AND_LSB_AND_EVERYTHING_ELSE_IN_ONE_LONG_NAME\n")
        for fid in ("chip-hero", "chip-capabilities", "chip-wiring-typical"):
            fig = self.fig(d, fid)
            self.assertTrue(any(t.endswith("…") for t in texts(fig)) or fid == "chip-hero", fid)


class UsesTest(Case):
    def test_applications_ref_and_inferred(self):
        d = data()
        d["refs"]["apps"] = {"doc": "ds", "section": "12 Applications", "page": 27}
        d["overview"]["applications_ref"] = "apps"
        self.copy_hw(d)
        out = gen_hw.uses(Page())
        self.assertIn("Uses named by the datasheet (12 Applications, p. 27).", out)
        self.assertNotIn("(12, p. 27)", out)  # the items share the footer's citation
        d["overview"]["applications_inferred"] = "from the functions in the features list"
        self.copy_hw(d)
        out = gen_hw.uses(Page())
        self.assertIn("Uses inferred, not named by the datasheet: from the functions in the features list", out)
        d["overview"].pop("applications")
        self.assertTrue(any("overview.applications: missing" in p for p in problems(d, self.root)))

    def copy_hw(self, d: dict):
        import yaml

        (self.root / "docs/hardware.yml").write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False))
        gen_hw.repo_root = lambda: self.root  # the generator reads the repository it runs in


class FramesAndRegistersTest(Case):
    def test_a_72_bit_frame(self):
        d = data()
        fr = d["frames"][0]
        fr["bits"] = 72
        names = ["address", "command", "type", "bank"]
        fields = [{"name": n, "bits": [71 - 8 * i, 64 - 8 * i], "tone": "blue"} for i, n in enumerate(names)]
        fields += [{"name": "value", "bits": [39, 8], "tone": "green"}, {"name": "checksum", "bits": [7, 0]}]
        fr["rows"] = [{"label": "Command", "fields": fields}]
        fr.pop("waveform")
        self.assertEqual(problems(d, self.root), [])
        self.assertIn("72 bits", self.fig(d, "chip-frame-spi").alt)
        fr["bits"] = 129
        self.assertTrue(any("1 to 128" in p for p in problems(d, self.root)))

    def test_a_register_with_a_header_alias(self):
        d = data()
        d["capabilities"][0]["registers"] = [{"name": "Temperature MSB", "header": "TEMP_MSB"}, "TEMP_LSB"]
        hw = self.hw(d)
        self.assertEqual(str(hw.doc.capabilities[0].registers[0]), "Temperature MSB")
        self.assertIn("Temperature MSB", texts(self.fig(d, "chip-capabilities")))
        d["capabilities"][0]["registers"][0]["header"] = "NOT_THERE"
        p = problems(d, self.root)
        self.assertTrue(any("'Temperature MSB' (header 'NOT_THERE') is not in" in x for x in p), p)
        d["capabilities"][0]["registers"][0] = {"name": "X", "nope": 1}
        self.assertTrue(any("capabilities[0].registers[0]" in x for x in problems(d, self.root)))


class ProtocolTest(Case):
    def test_protocol_drivers_name_their_tests_and_say_protocol(self):
        d = data()
        d["driver"]["kind"] = "protocol"
        p = problems(d, self.root)
        self.assertTrue(any("capabilities[0].tests" in x and "names the host test" in x for x in p), p)
        (self.root / "tests").mkdir(exist_ok=True)
        (self.root / "tests/test_measure.cpp").write_text('TEST_CASE("A reading comes back in degrees") {}\n')
        for c in d["capabilities"]:
            c["tests"] = ["tests/test_measure.cpp"]
        d["capabilities"][1]["tests"] = ["A reading comes back in degrees"]
        self.assertEqual(problems(d, self.root), [])
        fig = self.fig(d, "chip-capabilities")
        self.assertIn("the driver implements it and the named host test checks it", " ".join(texts(fig)))
        self.assertNotIn("the chip has it", " ".join(texts(fig)))
        d["capabilities"][2]["tests"] = ["No such test", "tests/none.cpp"]
        p = "\n".join(problems(d, self.root))
        self.assertIn("no test named 'No such test'", p)
        self.assertIn("no file tests/none.cpp", p)
        d["driver"]["kind"] = "service"
        self.assertTrue(any("driver.kind" in x for x in problems(d, self.root)))


class InsideTest(Case):
    def test_inside_the_part(self):
        d = data()
        d["overview"]["inside"] = "part"
        hw = self.hw(d)
        good = (FIXTURE / "README.md.fixture").read_text()
        self.assertTrue(any("'Inside the part'" in p for p in readme.check(good, hw)))
        self.assertEqual(readme.check(good.replace("## Inside the chip", "## Inside the part"), hw), [])
        self.assertEqual(readme.check(good.replace("## Inside the chip", "## Inside the part")), [])
        d["overview"]["inside"] = "box"
        self.assertTrue(any("overview.inside" in p for p in problems(d, self.root)))


class MigrateTest(Case):
    def test_a_quick_start_under_another_heading_and_unknown_sections_keep_their_place(self):
        old = (FIXTURE / "README.old.fixture").read_text()
        old = old.replace("## Use it on your MCU", "## In 30 seconds")
        old = old.replace("## Tests and quality", "## Hardware notes\n\nKeep the bus short.\n\n## Tests and quality")
        new = readme.migrate(old, self.hw(data()))
        heads = [ln for ln in new.split("\n") if ln.startswith("## ")]
        self.assertNotIn("## In 30 seconds", heads)
        self.assertEqual(heads.index("## Hardware notes") + 1, heads.index("## Tests and quality"))
        self.assertLess(heads.index("## Documentation"), heads.index("## Hardware notes"))
        quick = new.split("## Quick start", 1)[1].split("\n## ", 1)[0]
        self.assertIn("**1. Wire it** as in [Pins and wiring](#pins-and-wiring).", quick)
        pins = new.split("## Pins and wiring", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| MCU |", pins)  # the wiring table moved with the wiring
        self.assertEqual(readme.check(new, self.hw(data())), [])


class SiteTest(Case):
    def test_the_template_home_page_migrates_and_checks(self):
        shutil.copy(FIXTURE / "README.md.fixture", self.root / "README.md")
        page = self.root / "docs/index.md"
        old = page.read_text()
        self.assertTrue(readme.check_site(old, self.hw(data())))
        for args in (("readme", "--site", "--migrate"), ("figures",), ("gen",)):
            r = run_cli(self.root, *args)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        new = page.read_text()
        self.assertEqual(readme.check_site(new, self.hw(data())), [])
        heads = [ln for ln in new.split("\n") if ln.startswith("## ")]
        self.assertEqual(heads[:6], ["## What it does", "## Where it is used", "## Inside the chip",
                                     "## Pins and wiring", "## Quick start", "## Driver coverage"])
        self.assertIn("The **XMPL100** is a digital temperature sensor", new)
        self.assertIn("diagrams/chip-hero.svg", new)
        # The old paragraph under the hero lands under Driver coverage.
        first_para = next(b for b in old.split("</div>\n", 1)[1].split("\n\n") if b.strip())
        cov = new.split("## Driver coverage", 1)[1]
        self.assertIn(" ".join(first_para.split()[:6]), cov)
        r = run_cli(self.root, "check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("docs/index.md is chip-first", r.stdout)
        self.assertEqual(readme.migrate_site(new, self.hw(data()), self.root), new)

    def test_site_rules(self):
        hw = self.hw(data())
        good = ("---\nhide: [toc]\n---\n\n<div class=\"kb-hero\" markdown>\n# XMPL100 Driver\n</div>\n\n"
                "<!-- generated: chip-summary -->\n<!-- /generated -->\n\n<!-- figure: chip-hero -->\n<!-- /figure -->\n\n"
                "## What it does\n\n<!-- figure: chip-capabilities -->\n\n## Where it is used\n\n"
                "<!-- generated: chip-uses -->\n\n## Inside the chip\n\n<!-- figure: chip-blocks -->\n\n"
                "## Pins and wiring\n\n<!-- figure: chip-pinout -->\n<!-- figure: chip-wiring-typical -->\n\n"
                "## Driver coverage\n\n<!-- generated: chip-coverage -->\n\n## Where to go next\n")
        self.assertEqual(readme.check_site(good, hw), [])
        self.assertEqual(readme.check_site(good.replace("## Driver coverage", "## Quick start\n\nx\n\n"
                                                        "## Driver coverage"), hw), [])
        inside = good.replace("</div>\n\n<!-- generated: chip-summary -->\n<!-- /generated -->",
                              "<!-- generated: chip-summary -->\n<!-- /generated -->\n</div>")
        self.assertTrue(any("first thing under the hero" in p for p in readme.check_site(inside, hw)))
        fixed = readme.migrate_site(inside, hw, self.root)
        self.assertEqual(readme.check_site(fixed, hw), [])
        layered = good.replace("## What it does\n", "## What it does\n\n<!-- figure: driver-layers -->\n")
        self.assertTrue(any("driver-layers" in p for p in readme.check_site(layered, hw)))
        self.assertTrue(any("hero" in p for p in readme.check_site(good.replace('class="kb-hero"', 'class="x"'), hw)))


if __name__ == "__main__":
    unittest.main()
