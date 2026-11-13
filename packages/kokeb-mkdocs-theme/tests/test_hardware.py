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

from kokeb_mkdocs_theme.hardware import common, model, netlist, render
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
        common.layout_problems(f, [], [])
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


# A capacitor lane to a supply above a load between two chip pins: found by a driver, where the load's label was
# drawn on the capacitor's plates.
LANE_REPRO = """
schema: 1
chip: REPRO
documents: [{id: ds, name: Repro}]
refs: {p: {doc: ds, section: "1", page: 1}}
package: {type: SOIC-8, pins: 8, ref: p}
hooks: [{id: t, call: "Transfer()", kind: spi}]
pins:
  - {number: 1, name: SCK, type: bus, hook: t, domain: VM, function: x, ref: p}
  - {number: 2, name: GND, type: ground, domain: VM, function: x, ref: p}
  - {number: 3, name: NC1, type: nc, domain: VM, function: x, ref: p}
  - {number: 7, name: NC2, type: nc, domain: VM, function: x, ref: p}
  - {number: 5, name: OUTB, type: power-out, domain: VM, function: x, ref: p}
  - {number: 6, name: OUTA, type: power-out, domain: VM, function: x, ref: p}
  - {number: 4, name: VCP, type: analog, domain: VM, function: x, ref: p}
  - {number: 8, name: VM, type: power, domain: VM, function: x, ref: p}
circuits:
  - id: c
    title: Repro
    ref: p
    parts:
      - {id: U1, kind: chip}
      - {id: U2, kind: mcu, pins: [SCK, GND]}
      - {id: C1, kind: capacitor, value: 1 µF}
      - {id: L1, kind: solenoid}
    nets:
      - {name: VM, kind: supply, nodes: [U1.VM, C1.2]}
      - {name: GND, kind: ground, nodes: [U1.GND, U2.GND]}
      - {name: SCK, nodes: [U1.SCK, U2.SCK]}
      - {name: VCP, nodes: [U1.VCP, C1.1]}
      - {name: A, nodes: [U1.OUTA, L1.1]}
      - {name: B, nodes: [U1.OUTB, L1.2]}
"""


def crowded_links() -> dict:
    """Two links into the top of one block, one of them turning in from the side (a driver's 'supply faults' and
    'f_SYS' into its central logic)."""
    d = base()
    d["block_diagram"]["blocks"] = [
        {"id": "psu", "label": "Power supply", "at": [0, 1], "pins": ["VDD", "GND"],
         "detail": "undervoltage and overvoltage detection, " * 3},
        {"id": "pll", "label": "PLL", "detail": "with clock watchdog", "at": [1, 0], "side": "left"},
        {"id": "logic", "label": "Central logic", "at": [0, 2], "pins": ["CS_N", "SCLK", "RESET_N"],
         "detail": "states, faults, direct drive, " * 6},
        {"id": "ch", "label": "Channels", "at": [1, 2], "side": "right"},
        {"id": "out", "label": "Power stages", "at": [2, 2], "side": "right", "pins": ["ALERT"]},
    ]
    d["block_diagram"]["links"] = [{"from": "psu", "to": "logic", "label": "supply faults"},
                                   {"from": "pll", "to": "logic", "label": "f_SYS"},
                                   {"from": "logic", "to": "ch", "label": "setpoints"}]
    return d


class CircuitHookOverrideTest(unittest.TestCase):
    """A net's optional ``hook`` replaces the chip pin's hook in that circuit only."""

    @staticmethod
    def net(d: dict, name: str) -> dict:
        return next(n for n in d["circuits"][0]["nets"] if n["name"] == name)

    def render(self, d: dict):
        hw = parse(d)
        fig = render.build(hw, "chip-circuit-typical")
        self.assertEqual(fig.problems(), [])
        return hw, fig

    def test_absent_override_is_unchanged(self):
        hw, fig = self.render(base())
        self.assertFalse(any(n.hook_set for n in hw.circuits[0].nets))
        svg = fig.svg("light")
        self.assertIn("Transfer()", svg)
        self.assertIn("GpioSet(CtrlPin::Reset)", svg)
        self.assertIn("Transfer()", fig.alt)

    def test_override_replaces_the_hook_in_this_circuit_only(self):
        d = base()
        self.net(d, "RESET_N")["hook"] = "transfer"
        hw, fig = self.render(d)
        circ = hw.circuits[0]
        self.assertEqual(circ.hook_of(hw.pin("RESET_N")[0]), "transfer")
        self.assertEqual(hw.pin("RESET_N")[0].hook, "reset")  # the pin table keeps the pin's own hook
        for theme in ("light", "dark"):
            self.assertNotIn("GpioSet(CtrlPin::Reset)", fig.svg(theme))
        self.assertNotIn("GpioSet(CtrlPin::Reset)", fig.alt)
        self.assertIn("Transfer()", fig.alt)

    def test_null_and_empty_override_show_no_hook(self):
        for value in (None, ""):
            d = base()
            self.net(d, "SCLK")["hook"] = value
            self.net(d, "CS_N")["hook"] = value
            self.net(d, "SDI")["hook"] = value
            self.net(d, "SDO")["hook"] = value
            hw, fig = self.render(d)
            self.assertEqual(hw.circuits[0].hook_of(hw.pin("SCLK")[0]), "")
            self.assertNotIn("Transfer()", fig.svg("light"), value)
            self.assertNotIn("Transfer()", fig.svg("dark"), value)
            self.assertNotIn("Transfer()", fig.alt)
            self.assertIn("GpioSet(CtrlPin::Reset)", fig.alt)

    def test_override_must_name_a_listed_hook_and_a_net_with_the_chip(self):
        d = base()
        self.net(d, "SCLK")["hook"] = "nope"
        self.assertTrue(any("nets" in x and ".hook" in x and "not a hook listed" in x for x in problems(d)))
        d = base()
        d["circuits"][0]["nets"].append({"name": "X", "nodes": ["U2.GND", "C1.1"], "hook": "transfer"})
        self.assertTrue(any("no chip pin" in x for x in problems(d)), problems(d))


class LayoutRegressionTest(unittest.TestCase):
    def test_lane_label_clears_the_capacitor_above(self):
        from unittest import mock

        from kokeb_mkdocs_theme.hardware import circuit

        hw = parse(yaml.safe_load(LANE_REPRO))
        fig = render.build(hw, "chip-circuit-c")
        self.assertEqual(fig.problems(), [])
        pins = fig.routing["pins"]
        # L1's label sits below C1's lower plate, with room to spare.
        self.assertGreaterEqual(pins[("L1", "1")][1] - pins[("C1", "1")][1], 5 * 8)
        # With the old lane room (nothing measured) the label lands on the plates, and the check says so.
        with mock.patch.object(circuit, "_extent", lambda part: (0.0, 0.0)):
            old = render.build(parse(yaml.safe_load(LANE_REPRO)), "chip-circuit-c").problems()
        self.assertIn("text 'L1' overlaps the symbol of C1", old)

    def test_text_on_a_symbol_is_a_problem(self):
        from kokeb_mkdocs_theme.figkit import Fig
        from kokeb_mkdocs_theme.hardware import symbols

        f = Fig("t", "t", alt="t")
        p = symbols.two_pin(f, "C9", "capacitor", 40, 40, False, "1 µF")
        f.text(60, 52, "label")  # across the plates, below the wire
        common.layout_problems(f, [], [], [(b, "C9") for b in p.ink])
        self.assertIn("text 'label' overlaps the symbol of C9", f.problems())

    def test_links_into_one_face_spread_and_labels_stay_clear(self):
        from unittest import mock

        hw = parse(crowded_links())
        fig = render.build(hw, "chip-blocks")
        self.assertEqual(fig.problems(), [])
        ends = {(ln.src, ln.dst): pts[-1] for ln, pts in fig.links}
        # Both arrive on the top of the logic block, 5G apart rather than the 3G minimum.
        self.assertEqual(ends[("psu", "logic")][1], ends[("pll", "logic")][1])
        self.assertGreaterEqual(abs(ends[("psu", "logic")][0] - ends[("pll", "logic")][0]), 5 * 8)
        # f_SYS comes from the right, so it takes the port right of the other.
        self.assertGreater(ends[("pll", "logic")][0], ends[("psu", "logic")][0])

        def on_another_line(fig, pts, text, taken, lines):
            (x0, y0), (x1, y1) = lines[-1]
            return fig.edge_label((x0 + x1) / 2, (y0 + y1) / 2, text)

        with mock.patch.object(render, "_label_spot", on_another_line):
            bad = render.build(parse(crowded_links()), "chip-blocks").problems()
        self.assertTrue(any("runs through the label" in p for p in bad), bad)


class ColourTest(unittest.TestCase):
    @staticmethod
    def lab(hex_colour: str) -> tuple[float, float, float]:
        """CIE L*a*b* (D65) of a hex colour."""
        h = hex_colour.lstrip("#")
        rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)
        x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

        def f(t: float) -> float:
            return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

        return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))

    def test_pin_types_are_told_apart_in_both_themes(self):
        from kokeb_mkdocs_theme.figkit import theme

        tones = {t: tone for t, (tone, _label) in model.PIN_TYPES.items()}
        for th in theme.THEMES:
            labs = {t: self.lab(theme.resolve(f"{tone}.strong", th)) for t, tone in tones.items()}
            names = sorted(labs)
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    de = sum((p - q) ** 2 for p, q in zip(labs[a], labs[b])) ** 0.5
                    self.assertGreaterEqual(de, 25, f"{th}: {a} and {b} are only {de:.1f} apart (CIE76)")

    def test_every_tone_text_reads_on_its_tint(self):
        from kokeb_mkdocs_theme.figkit import MIN_CONTRAST, theme

        for tone in theme.TONES:
            for th in theme.THEMES:
                ratio = theme.contrast(theme.resolve(f"{tone}.text", th), theme.resolve(f"{tone}.tint", th))
                self.assertGreaterEqual(ratio, MIN_CONTRAST, f"{tone} {th}")


class PackageAndTitleTest(unittest.TestCase):
    def test_vendor_package_names_are_recognised(self):
        dual = ["PG-DSO-36", "PG-TSDSO-14", "P-DSO-20", "SOIC-8", "SO-8", "SSOP-24", "TSSOP-20", "HTSSOP-28",
                "DSO-14", "MSOP-10", "TDSON-8"]
        quad = ["PG-VQFN-48", "PG-TQFP-48", "QFN-16", "VQFN-32", "HVQFN-24", "TQFN-38", "WQFN-20", "QFP-44",
                "LQFP-64"]
        for t in dual:
            self.assertEqual(model._guess_layout(t), "dual", t)
        for t in quad:
            self.assertEqual(model._guess_layout(t), "quad", t)
        self.assertEqual(model._guess_layout("BGA-64"), "")
        d = base()
        d["package"]["type"] = "PG-DSO-8"
        self.assertEqual(parse(d).package.layout, "dual")

    def test_long_card_title_words_wrap_or_shrink(self):
        from kokeb_mkdocs_theme.figkit import Fig
        from kokeb_mkdocs_theme.figkit.core import fit_title

        self.assertEqual(fit_title("I2C-bus/SMBus interface", 80, 15, 13)[0], ["I2C-bus/", "SMBus", "interface"])
        self.assertEqual(fit_title("Two half-bridges", 80, 15, 13)[0], ["Two half-", "bridges"])
        # A word with no break in it shrinks before it fails.
        from kokeb_mkdocs_theme.figkit import text_width

        lines, size = fit_title("Watchdog", text_width("Watchdog", 15, 700) - 4, 15, 13)
        self.assertEqual((lines, 13 <= size < 15), (["Watchdog"], True))
        f = Fig("t", "t", alt="t")
        f.card(0, 0, 96, "I2C-bus/SMBus")
        f.card(200, 0, 96, "half-bridges")
        self.assertEqual(f.problems(), [])
        f.card(400, 0, 40, "Supercalifragilistic")
        self.assertTrue(any("wider than its card" in p for p in f.problems()))


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


FIXTURE = HERE / "fixtures/chip-outline"


def with_outline() -> dict:
    """The template's description with the package data of schema 1.16 (outline, variants, supply)."""
    return yaml.safe_load((FIXTURE / "hardware.yml").read_text())


class PackageDataTest(unittest.TestCase):
    """package.outline, package.variants and supply: optional, validated, drawn and put on the chip card."""

    def test_outline_variants_and_supply_load(self):
        hw = parse(with_outline())
        o = hw.package.outline
        self.assertEqual((o.length_mm, o.width_mm, o.height_mm, o.pitch_mm), (4.9, 3.9, 1.75, 1.27))
        self.assertEqual(o.ref_of("height").page, 5)
        self.assertEqual(o.ref_of("pitch").page, 24)  # the drawing's, as no pitch_ref is given
        self.assertEqual([v.id for v in hw.package.variants], ["dfn", "tssop"])
        self.assertEqual(hw.supply[0].max_v, 3.6)
        self.assertFalse(hw.package.leadless)
        self.assertTrue(parse(quad()).package.leadless)

    def test_a_chip_without_the_new_fields_is_unchanged(self):
        hw = parse(base())
        self.assertIsNone(hw.package.outline)
        self.assertEqual((hw.package.variants, hw.supply), ([], []))
        self.assertNotIn("chip-outline", render.figure_ids(hw))
        self.assertIn("chip-outline", render.figure_ids(parse(with_outline())))

    def test_numbers_must_be_positive(self):
        for key, bad in (("length_mm", 0), ("width_mm", -2), ("height_mm", "1.75"), ("pitch_mm", True)):
            d = with_outline()
            d["package"]["outline"][key] = bad
            self.assertTrue(any(f"package.outline.{key}" in x and "positive number" in x for x in problems(d)), key)
        d = with_outline()
        del d["package"]["outline"]["length_mm"]
        self.assertTrue(any("package.outline.length_mm: missing" in x for x in problems(d)))

    def test_refs_must_resolve(self):
        for path in (("outline", "ref"), ("outline", "height_ref"), ("variants", 0, "ref")):
            d = with_outline()
            node = d["package"]
            for k in path[:-1]:
                node = node[k]
            node[path[-1]] = "nowhere"
            self.assertTrue(any("unknown citation 'nowhere'" in x for x in problems(d)), path)
        d = with_outline()
        del d["package"]["outline"]["ref"]
        self.assertTrue(any("package.outline.ref" in x and "missing" in x for x in problems(d)))

    def test_variant_ids_are_unique_and_complete(self):
        d = with_outline()
        d["package"]["variants"][1]["id"] = "dfn"
        self.assertTrue(any("variant 'dfn' is listed twice" in x for x in problems(d)))
        d = with_outline()
        d["package"]["variants"][0]["pins"] = 0
        d["package"]["variants"][1]["colour"] = "red"
        p = problems(d)
        self.assertTrue(any("variants[0].pins" in x for x in p), p)
        self.assertTrue(any("variants[1]" in x and "colour" in x for x in p), p)
        d = with_outline()
        del d["package"]["variants"][0]["type"]
        self.assertTrue(any("variants[0].type: missing" in x for x in problems(d)))

    def test_pins_must_fit_the_body_and_supply_must_be_ordered(self):
        d = with_outline()
        d["package"]["outline"]["pitch_mm"] = 1.6  # 3 gaps of 1.6 mm on a 4.9 mm edge: 4.8 fits, so widen
        d["package"]["outline"]["length_mm"] = 3.0
        self.assertTrue(any("span 4.80 mm, more than the 3.0 mm edge" in x for x in problems(d)))
        d = with_outline()
        d["supply"][0].update(min_v=3.6, max_v=1.8)
        self.assertTrue(any("supply[0].min_v" in x for x in problems(d)))

    def test_outline_figure_for_a_leaded_package(self):
        hw = parse(with_outline())
        fig = render.build(hw, "chip-outline")
        self.assertEqual(fig.problems(), [])
        svg = fig.svg("light")
        for text in ("4.9 mm", "3.9 mm", "1.75 mm", "pitch 1.27 mm", "4.9 x 3.9 x 1.75 mm"):
            self.assertIn(text, svg)
        body = fig.placed  # leads reach out of the body: pad 1 lies left of pad 5, which lies right of the body
        self.assertLess(body[1].x, body[5].x)
        self.assertEqual([round(body[n].cy, 1) for n in (1, 2, 3, 4)], sorted(round(body[n].cy, 1) for n in range(1, 5)))
        self.assertEqual(svg, render.build(parse(with_outline()), "chip-outline").svg("light"))

    def test_outline_figure_for_a_leadless_package_and_partial_data(self):
        d = quad()
        d["package"]["outline"] = {"length_mm": 3.0, "width_mm": 3.0, "pitch_mm": 0.5, "ref": "p"}
        fig = render.build(parse(d), "chip-outline")
        self.assertEqual(fig.problems(), [])
        self.assertNotIn("Side view", fig.svg("light"))  # no height: no side view
        d["package"]["outline"] = {"length_mm": 3.0, "width_mm": 3.0, "ref": "p"}  # no pitch either
        fig = render.build(parse(d), "chip-outline")
        self.assertEqual(fig.problems(), [])
        self.assertNotIn("pitch", fig.svg("light"))

    def test_fine_pitch_gets_a_larger_drawing_not_overlaps(self):
        d = quad()
        d["package"]["outline"] = {"length_mm": 3.0, "width_mm": 3.0, "pitch_mm": 0.4, "ref": "p"}
        self.assertEqual(render.build(parse(d), "chip-outline").problems(), [])


class ChipCardTest(unittest.TestCase):
    """The README region and the figure, through the commands, on a copy of the template site."""

    run_cli = TemplateSiteTest.run_cli

    def site(self, tmp: str, outline: bool) -> pathlib.Path:
        site = pathlib.Path(tmp) / "site"
        shutil.copytree(TEMPLATE, site)
        if outline:
            shutil.copy(FIXTURE / "hardware.yml", site / "docs/hardware.yml")
        shutil.copy(FIXTURE / "README.md.fixture", site / "README.md")
        return site

    def test_card_and_figure_are_written_and_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.site(tmp, True)
            r = self.run_cli(site, "check")
            self.assertNotEqual(r.returncode, 0)  # figures and region not written yet
            for cmd in ("figures", "gen"):
                r = self.run_cli(site, cmd)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue((site / "docs/diagrams/chip-outline.svg").is_file())
            self.assertTrue((site / "docs/diagrams/chip-outline.dark.svg").is_file())
            readme = (site / "README.md").read_text()
            self.assertIn("docs/diagrams/chip-outline.dark.svg", readme)
            for row in ("| **Package** | SOIC-8 |", "| **Pins** | 8 |", "| **Body size** | 4.9 x 3.9 x 1.75 mm |",
                        "| **Pin pitch** | 1.27 mm |", "| **Supply VDD** | 1.8 V to 3.6 V |", "| `dfn` | DFN-8 | 8 |"):
                self.assertIn(row, readme)
            self.assertIn("height 5 Electrical characteristics, Table 4 Mechanical data, p. 5", readme)
            r = self.run_cli(site, "check")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # A change to the outline makes the card and the figure stale.
            y = site / "docs/hardware.yml"
            y.write_text(y.read_text().replace("pitch_mm: 1.27", "pitch_mm: 1.25"))
            r = self.run_cli(site, "check")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("stale", r.stderr)
            # An invalid outline stops the check at the validation.
            y.write_text(y.read_text().replace("length_mm: 4.9", "length_mm: -4.9"))
            r = self.run_cli(site, "check")
            self.assertIn("package.outline.length_mm", r.stderr)

    def test_a_chip_without_an_outline_still_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = self.site(tmp, False)
            readme = (site / "README.md").read_text().replace("<!-- figure: chip-outline -->\n<!-- /figure -->\n\n", "")
            (site / "README.md").write_text(readme)
            for cmd in ("figures", "gen"):
                r = self.run_cli(site, cmd)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            card = (site / "README.md").read_text()
            self.assertIn("| **Package** | SOIC-8 |", card)
            self.assertNotIn("Body size", card)
            self.assertNotIn("Pin pitch", card)
            self.assertNotIn("Also sold as", card)
            self.assertFalse((site / "docs/diagrams/chip-outline.svg").exists())
            r = self.run_cli(site, "check")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
