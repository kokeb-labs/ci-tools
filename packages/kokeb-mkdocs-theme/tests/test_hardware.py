"""Chip hardware diagrams: the docs/hardware.yml schema, the layout invariants of the three figures, the router,
the pin table and the KiCad netlist export."""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

from kokeb_mkdocs_theme.hardware import model, netlist, render
from kokeb_mkdocs_theme.hardware.router import Grid, RouteError

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parents[2] / "templates/mkdocs-site"


def base() -> dict:
    """The template site's XMPL100 description, as data."""
    return yaml.safe_load((TEMPLATE / "docs/hardware.yml").read_text())


def parse(data: dict, root: pathlib.Path | None = None) -> model.Hardware:
    return model.parse(data, root or TEMPLATE)


def problems(data: dict, root: pathlib.Path | None = None) -> list[str]:
    try:
        parse(data, root)
    except model.HardwareError as e:
        return e.problems
    return []


def quad() -> dict:
    """A fictional 16-pin QFN with an exposed pad, every pin on one net or unused."""
    pins = [{"number": n, "name": f"P{n}", "type": "digital-io", "domain": "VDD", "function": "I/O", "ref": "p"}
            for n in range(1, 17)]
    pins[0].update(name="VDD", type="power")
    pins[8].update(name="GND", type="ground")
    pins.append({"number": "EP", "name": "GND", "type": "ground", "function": "Exposed pad", "ref": "p"})
    return {
        "schema": 1, "chip": "QX16", "documents": [{"id": "d", "name": "QX16 data sheet"}],
        "refs": {"p": {"doc": "d", "section": "4 Pins", "page": 4}},
        "package": {"type": "QFN-16", "pins": 16, "exposed_pad": True, "ref": "p"},
        "hooks": [], "pins": pins,
    }


class SchemaTest(unittest.TestCase):
    def test_template_is_valid(self):
        hw = parse(base())
        self.assertEqual(hw.chip, "XMPL100")
        self.assertEqual(hw.package.layout, "dual")
        self.assertEqual(hw.package.sides, {"left": [1, 2, 3, 4], "right": [5, 6, 7, 8]})
        self.assertEqual(len(hw.pins), 8)
        self.assertEqual(hw.pin("RESET_N")[0].hook, "reset")
        self.assertEqual(hw.pins[0].ref.page, 8)  # the spi citation

    def test_layout_is_guessed_from_the_package(self):
        hw = parse(quad())
        self.assertEqual(hw.package.layout, "quad")
        self.assertEqual(hw.package.sides["bottom"], [5, 6, 7, 8])
        self.assertEqual(hw.package.sides["top"], [13, 14, 15, 16])

    def test_each_pin_number_once(self):
        d = base()
        d["pins"][1]["number"] = 1
        p = problems(d)
        self.assertTrue(any("pin 1 is listed twice" in x for x in p), p)
        self.assertTrue(any("no entry for pin(s) 2" in x for x in p), p)

    def test_pin_outside_the_package(self):
        d = base()
        d["pins"][0]["number"] = 9
        self.assertTrue(any("outside 1 to 8" in x for x in problems(d)))

    def test_unknown_type_hook_and_citation(self):
        d = base()
        d["pins"][0]["type"] = "gpio"
        d["pins"][1]["hook"] = "spi_transfer"
        d["pins"][2]["ref"] = "nowhere"
        p = problems(d)
        self.assertTrue(any("pins[0].type" in x for x in p), p)
        self.assertTrue(any("pins[1].hook" in x and "not a hook listed" in x for x in p), p)
        self.assertTrue(any("pins[2].ref" in x and "unknown citation" in x for x in p), p)

    def test_every_fact_cites_the_datasheet(self):
        d = base()
        del d["pins"][3]["ref"]
        d["refs"]["spi"]["page"] = 0
        d["refs"]["alert"]["doc"] = "other"
        p = problems(d)
        self.assertTrue(any("pins[3].ref: missing" in x for x in p), p)
        self.assertTrue(any("refs.spi.page" in x for x in p), p)
        self.assertTrue(any("refs.alert.doc" in x and "unknown document" in x for x in p), p)

    def test_unknown_keys_are_reported_with_their_path(self):
        d = base()
        d["pins"][0]["colour"] = "red"
        d["package"]["pitch"] = 1.27
        p = problems(d)
        self.assertTrue(any("pins[0]: unknown key(s) colour" in x for x in p), p)
        self.assertTrue(any("package: unknown key(s) pitch" in x for x in p), p)

    def test_hook_symbol_must_exist_in_its_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "inc").mkdir()
            (root / "inc/port.hpp").write_text("bool Transfer(const uint8_t*, uint8_t*, size_t) noexcept;\n")
            d = base()
            d["hooks"][0].update(source="inc/port.hpp", symbol="Transfer")
            self.assertEqual(problems(d, root), [])
            d["hooks"][0]["symbol"] = "TransferFrame"
            self.assertTrue(any("does not appear in inc/port.hpp" in x for x in problems(d, root)))
            d["hooks"][0]["source"] = "inc/missing.hpp"
            self.assertTrue(any("no file inc/missing.hpp" in x for x in problems(d, root)))

    def test_documents_come_from_datasheets_yml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/datasheets.yml").write_text(yaml.safe_dump({"documents": [
                {"id": "ds", "vendor": "Example", "number": "XMPL100-DS", "revision": "A", "pdf": "https://e/x.pdf"}]}))
            d = base()
            del d["documents"]
            hw = parse(d, root)
            self.assertEqual(hw.documents["ds"]["pdf"], "https://e/x.pdf")
            d["documents"] = [{"id": "ds", "name": "again"}]
            self.assertTrue(any("also in docs/datasheets.yml" in x for x in problems(d, root)))

    def test_circuit_endpoints_exist(self):
        d = base()
        nets = d["circuits"][0]["nets"]
        nets[2]["nodes"].append("U9.X")
        nets[3]["nodes"].append("U2.NOPE")
        nets[4]["nodes"].append("C1.3")
        p = problems(d)
        self.assertTrue(any("U9.X: no part 'U9'" in x for x in p), p)
        self.assertTrue(any("U2 has no pin 'NOPE'" in x for x in p), p)
        self.assertTrue(any("C1 has no pin '3'" in x for x in p), p)

    def test_every_net_has_two_nodes_and_every_pin_is_used(self):
        d = base()
        c = d["circuits"][0]
        c["nets"] = [n for n in c["nets"] if n["name"] != "RESET_N"]
        c["nets"].append({"name": "LONELY", "nodes": ["U2.RST"]})
        p = problems(d)
        self.assertTrue(any("net 'LONELY' has 1 node(s)" in x for x in p), p)
        self.assertTrue(any("U1.RESET_N is on no net" in x for x in p), p)
        # Marked unused, the chip pin is fine.
        c["nets"] = c["nets"][:-1]
        c["unused"] = ["U1.RESET_N", "U2.RST"]
        self.assertEqual(problems(d), [])

    def test_a_pin_is_on_one_net(self):
        d = base()
        d["circuits"][0]["nets"][2]["nodes"].append("U1.SDI")
        self.assertTrue(any("U1.SDI is already on net" in x for x in problems(d)))

    def test_unused_pin_cannot_be_connected(self):
        d = base()
        d["circuits"][0]["unused"] = ["U1.SCLK"]
        self.assertTrue(any("marked unused but is on net 'SCLK'" in x for x in problems(d)))

    def test_one_chip_per_circuit_and_pin_aliases(self):
        d = base()
        d["circuits"][0]["parts"].append({"id": "U3", "kind": "chip"})
        self.assertTrue(any("exactly one part of kind chip" in x for x in problems(d)))
        d = base()
        d["circuits"][0]["parts"].append({"id": "D1", "kind": "led"})
        d["circuits"][0]["nets"][0]["nodes"].append("D1.A")
        d["circuits"][0]["nets"][1]["nodes"].append("D1.K")
        hw = parse(d)
        self.assertEqual(hw.circuits[0].net_of("D1", "1").name, "+3V3")
        self.assertEqual(hw.circuits[0].net_of("D1", "2").name, "GND")

    def test_block_diagram_references(self):
        d = base()
        d["block_diagram"]["blocks"][0]["pins"].append("MISO")
        d["block_diagram"]["blocks"][1]["at"] = [0, 0]
        d["block_diagram"]["links"].append({"from": "spi", "to": "dsp"})
        p = problems(d)
        self.assertTrue(any("no pin named 'MISO'" in x for x in p), p)
        self.assertTrue(any("cell [0, 0] is taken" in x for x in p), p)
        self.assertTrue(any("no block 'dsp'" in x for x in p), p)


class PinoutTest(unittest.TestCase):
    def check_sides(self, hw):
        fig = render.pinout(hw)
        self.assertEqual(fig.problems(), [])
        for side, nums in hw.package.sides.items():
            for n in nums:
                self.assertEqual(fig.placed[n][0], side, f"pin {n}")
        return fig

    def test_dual_pins_in_datasheet_order(self):
        hw = parse(base())
        fig = self.check_sides(hw)
        left = [fig.placed[n][1].cy for n in hw.package.sides["left"]]
        right = [fig.placed[n][1].cy for n in hw.package.sides["right"]]
        self.assertEqual(left, sorted(left))  # 1 to 4, top to bottom
        self.assertEqual(right, sorted(right, reverse=True))  # 5 to 8, bottom to top

    def test_quad_pins_counter_clockwise(self):
        hw = parse(quad())
        fig = self.check_sides(hw)
        bottom = [fig.placed[n][1].cx for n in hw.package.sides["bottom"]]
        top = [fig.placed[n][1].cx for n in hw.package.sides["top"]]
        self.assertEqual(bottom, sorted(bottom))  # left to right
        self.assertEqual(top, sorted(top, reverse=True))  # right to left
        self.assertIn("EP: GND", fig.svg("light"))

    def test_explicit_sides(self):
        d = quad()
        d["package"] = {"type": "SOT-23-5", "pins": 5, "sides": {"left": [1, 2, 3], "right": [4, 5]}, "ref": "p"}
        d["pins"] = [p for p in d["pins"] if p["number"] != "EP" and p["number"] <= 5]
        self.check_sides(parse(d))

    def test_unverified_pins_are_marked(self):
        d = base()
        d["pins"][2]["unverified"] = "polarity not given"
        svg = render.pinout(parse(d)).svg("light")
        self.assertIn("ALERT*", svg)
        self.assertIn("Not confirmed in the datasheet: pin 3 ALERT: polarity not given", svg)


class FiguresTest(unittest.TestCase):
    def test_every_figure_is_clean_and_deterministic(self):
        hw = parse(base())
        self.assertEqual(render.figure_ids(hw), ["chip-pinout", "chip-blocks", "chip-circuit-typical"])
        for fid in render.figure_ids(hw):
            a, b = render.build(hw, fid), render.build(parse(base()), fid)
            self.assertEqual(a.problems(), [], fid)
            for theme in ("light", "dark"):
                self.assertEqual(a.svg(theme), b.svg(theme), f"{fid} {theme}")
            self.assertTrue(a.doc.startswith("Reads:"), fid)

    def test_overlapping_text_is_a_problem(self):
        from kokeb_mkdocs_theme.figkit import Fig

        f = Fig("t", "t", alt="t")
        f.text(0, 20, "one label")
        f.text(10, 22, "another label")
        render.layout_problems(f, [], [])
        self.assertTrue(any("overlaps text" in p for p in f.problems()))

    def test_circuit_places_parts_by_role(self):
        hw = parse(base())
        fig = render.build(hw, "chip-circuit-typical")
        plan = fig.routing["plan"]
        self.assertEqual([c.name for c in plan.left], ["CS_N", "SDO", "ALERT", "SDI", "SCLK", "RESET_N"])
        self.assertEqual([c.name for c in plan.top], ["VDD"])
        self.assertEqual([c.name for c in plan.bottom], ["GND"])
        self.assertEqual([p[0] for p in plan.pullups], ["R1"])
        self.assertEqual([p[0] for p in plan.decaps["VDD"]], ["C1"])
        pins = fig.routing["pins"]
        # The MCU pin is level with the chip pin it drives: a straight wire.
        self.assertEqual(pins[("U2", "RST")][1], pins[("U1", "RESET_N")][1])
        self.assertEqual(fig.routing["crossings"], 2)  # R1's drop crosses CS_N and SDO
        svg = fig.svg("light")
        self.assertIn("GpioSet(CtrlPin::Reset)", svg)
        self.assertIn("Transfer()", svg)

    def test_loads_lanes_and_polarity(self):
        d = base()
        c = d["circuits"][0]
        c["nets"] = [n for n in c["nets"] if n["name"] not in ("ALERT",)]
        c["parts"] = [p for p in c["parts"] if p["id"] != "R1"]
        c["parts"].append({"id": "R2", "kind": "resistor", "value": "1 kΩ"})
        c["parts"].append({"id": "D1", "kind": "led"})
        c["nets"][0]["nodes"].remove("R1.1")
        c["nets"].append({"name": "ALERT", "nodes": ["U1.ALERT", "R2.1"]})
        c["nets"].append({"name": "LED_A", "nodes": ["R2.2", "D1.A"]})
        c["nets"][1]["nodes"].append("D1.K")
        c["parts"][1]["pins"] = [p for p in c["parts"][1]["pins"] if not (isinstance(p, dict) and p["name"] == "IRQ")]
        hw = parse(d)
        fig = render.build(hw, "chip-circuit-typical")
        self.assertEqual(fig.problems(), [])
        plan = fig.routing["plan"]
        self.assertEqual([x[0] for x in plan.chains["ALERT"]], ["R2", "D1"])
        pins = fig.routing["pins"]
        # The chain runs right from the pin; the LED's anode faces the resistor.
        self.assertLess(pins[("R2", "1")][0], pins[("R2", "2")][0])
        self.assertLess(pins[("D1", "1")][0], pins[("D1", "2")][0])
        self.assertEqual(pins[("D1", "1")][1], pins[("U1", "ALERT")][1])


class RouterTest(unittest.TestCase):
    def test_route_avoids_blocks_and_crosses_at_right_angles(self):
        g = Grid(0, 0, 30, 30, 8)
        g.block_box(80, 40, 40, 160)
        a, b = g.cell(40, 120), g.cell(200, 120)
        g.add_terminal("A", a, "L")
        g.add_terminal("A", b, "R")
        g.route("A", [a, b])
        c, d = g.cell(160, 16), g.cell(160, 224)
        g.add_terminal("B", c, "U")
        g.add_terminal("B", d, "D")
        g.route("B", [c, d])
        for cell, nets in g.arms.items():
            if nets.get("A") or nets.get("B"):
                self.assertNotIn(cell, g.blocked)
            if len([n for n, arms in nets.items() if arms]) > 1:
                arms = [nets[n] for n in nets]
                self.assertIn({"L", "R"}, arms)
                self.assertIn({"U", "D"}, arms)
        self.assertEqual(g.crossings(), 1)

    def test_tree_gets_a_junction_and_no_four_way(self):
        g = Grid(0, 0, 20, 20, 8)
        cells = [g.cell(16, 80), g.cell(144, 80), g.cell(80, 16), g.cell(80, 144)]
        for c, side in zip(cells, "LRUD"):
            g.add_terminal("N", c, side)
        g.route("N", cells)
        for c, nets in g.arms.items():
            self.assertLessEqual(len(nets.get("N", ())), 3)
        self.assertGreaterEqual(len(g.junctions("N")), 2)
        # Every run of the net is straight and joins cells that are neighbours on the grid.
        for (x0, y0), (x1, y1) in g.segments("N"):
            self.assertTrue(x0 == x1 or y0 == y1)

    def test_no_route_is_an_error(self):
        g = Grid(0, 0, 10, 10, 8)
        g.block_box(30, 0, 8, 80)
        a, b = g.cell(8, 40), g.cell(64, 40)
        g.add_terminal("A", a, None)
        g.add_terminal("A", b, None)
        with self.assertRaises(RouteError):
            g.route("A", [a, b])

    def test_off_grid_point_is_an_error(self):
        with self.assertRaises(RouteError):
            Grid(0, 0, 10, 10, 8).cell(3, 8)


class NetlistTest(unittest.TestCase):
    def test_export_is_deterministic_and_complete(self):
        hw = parse(base())
        c = hw.circuits[0]
        a = netlist.kicad_netlist(hw, c)
        self.assertEqual(a, netlist.kicad_netlist(parse(base()), parse(base()).circuits[0]))
        self.assertEqual(a.count("("), a.count(")"))
        self.assertTrue(a.startswith('(export (version "E")'))
        self.assertNotRegex(a, r"\(date|tstamp \"[0-9a-f]")
        names = re.findall(r'\(net \(code "\d+"\) \(name "([^"]+)"\)', a)
        self.assertEqual(names, sorted(n.name for n in c.nets))
        self.assertIn('(node (ref "U1") (pin "7") (pinfunction "RESET_N") (pintype "input"))', a)
        self.assertIn('(libsource (lib "Device") (part "C") (description "capacitor"))', a)
        self.assertIn('(pin (num "3") (name "ALERT") (type "open_collector"))', a)
        self.assertEqual(netlist.check(hw, c), [])

    def test_repeated_pin_names_and_open_pins(self):
        d = quad()
        d["circuits"] = [{
            "id": "min", "title": "Minimal", "ref": "p",
            "parts": [{"id": "U1", "kind": "chip"}, {"id": "C1", "kind": "capacitor", "value": "1 µF"}],
            "nets": [{"name": "VDD", "kind": "supply", "nodes": ["U1.VDD", "C1.1"]},
                     {"name": "GND", "kind": "ground", "nodes": ["U1.GND", "C1.2"]}],
            "unused": [f"U1.P{n}" for n in range(2, 17) if n != 9],
        }]
        hw = parse(d)
        out = netlist.kicad_netlist(hw, hw.circuits[0])
        gnd = out[out.index('(name "GND")'):]
        gnd = gnd[:gnd.index("\n    )")]
        self.assertIn('(pin "9")', gnd)
        self.assertIn('(pin "EP")', gnd)
        self.assertIn('unconnected-(U1-P2-Pad2)', out)
        self.assertEqual(render.build(hw, "chip-circuit-min").problems(), [])


class TemplateSiteTest(unittest.TestCase):
    """The commands, run on a copy of the template site the way CI runs them."""

    def run_cli(self, cwd, *args):
        env = dict(os.environ, NO_MKDOCS_2_WARNING="1")
        env.pop("KOKEB_DOCS_ROOT", None)
        env.pop("KOKEB_DOCS_CONFIG", None)
        return subprocess.run([sys.executable, "-m", "kokeb_mkdocs_theme.cli", *args], cwd=cwd, env=env,
                              capture_output=True, text=True)

    def test_check_covers_hardware_figures_and_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = pathlib.Path(tmp) / "site"
            shutil.copytree(TEMPLATE, site)
            r = self.run_cli(site, "check")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("[hardware] OK", r.stdout)
            # A change to the file makes the committed figures and table stale.
            y = site / "docs/hardware.yml"
            y.write_text(y.read_text().replace("Supply, 1.8 V to 3.6 V", "Supply, 1.7 V to 3.6 V"))
            r = self.run_cli(site, "check")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("generated region is stale", r.stderr)
            # An invalid file stops the check before anything is drawn.
            y.write_text(y.read_text().replace("hook: reset", "hook: nreset"))
            r = self.run_cli(site, "check")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("pins[6].hook", r.stderr)

    def test_netlist_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = pathlib.Path(tmp) / "site"
            shutil.copytree(TEMPLATE, site)
            out = pathlib.Path(tmp) / "x.net"
            r = self.run_cli(site, "hardware", "--kicad-netlist", str(out), "--circuit", "typical")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('(comp (ref "R1")', out.read_text())
            r = self.run_cli(site, "hardware", "--kicad-netlist", str(out), "--circuit", "nope")
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
