"""The bus figure kinds: ``timing`` (waveforms and transactions) and ``topology`` (daisy chains and shared buses).

Their golden bytes are covered by ``test_figkit`` (every fixture model); these tests cover the citation rule (a number
without a datasheet reference fails), the schema, the phone width and the hardware.yml fallback.
"""

from __future__ import annotations

import copy
import pathlib
import sys
import tempfile
import unittest

import yaml

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from kokeb_mkdocs_theme.figkit import kinds  # noqa: E402
from kokeb_mkdocs_theme.figkit.kinds import ModelError, timing, topology  # noqa: E402

MODEL = HERE / "fixtures/figkit/model"
GOLDEN = HERE / "fixtures/figkit/golden"


def load(name: str) -> dict:
    return yaml.safe_load((MODEL / name).read_text(encoding="utf-8"))


def problems_of(fn, model, root=None) -> str:
    try:
        fn(model, "m", root=root)
    except ModelError as e:
        return str(e)
    return ""


class TimingTests(unittest.TestCase):
    def setUp(self):
        self.spi = load("i2c-timing.timing.yml")

    def test_fixtures_build_clean(self):
        for name in ("i2c-timing.timing.yml", "uart-frame.timing.yml"):
            fig = kinds.from_model(MODEL / name, lock_dir=GOLDEN)
            self.assertEqual(fig.problems(), [], name)
            self.assertEqual(fig.profile, "phone")

    def test_a_param_without_a_ref_fails(self):
        m = copy.deepcopy(self.spi)
        del m["params"][0]["ref"]
        self.assertIn("params[0]: missing 'ref'", problems_of(timing.validate, m))

    def test_an_unknown_ref_fails(self):
        m = copy.deepcopy(self.spi)
        m["params"][1]["ref"] = "nowhere"
        self.assertIn("unknown ref 'nowhere'", problems_of(timing.validate, m))

    def test_a_number_in_a_group_or_note_needs_a_ref(self):
        m = copy.deepcopy(self.spi)
        del m["groups"][0]["ref"]
        m["notes"] = ["Wait 5 ms after power-up."]
        p = problems_of(timing.validate, m)
        self.assertIn("groups[0].ref: no datasheet reference", p)
        self.assertIn("notes[0]: a note with a number needs a ref", p)

    def test_a_name_with_digits_is_not_a_number(self):
        m = copy.deepcopy(self.spi)
        m["groups"][1]["label"] = "ACK from XMPL100"
        self.assertEqual(problems_of(timing.validate, m), "")

    def test_marks_name_cited_params_and_known_signals(self):
        m = copy.deepcopy(self.spi)
        m["marks"].append({"param": "tlow", "signal": "nope", "from": 1, "to": 2})
        p = problems_of(timing.validate, m)
        self.assertIn("'tlow' is not under params", p)
        self.assertIn("unknown signal 'nope'", p)

    def test_wave_lengths_data_and_characters(self):
        m = copy.deepcopy(self.spi)
        m["signals"][0]["wave"] = "11nnk"
        m["signals"][1]["data"] = ["A6"]
        p = problems_of(timing.validate, m)
        self.assertIn("unknown character(s) 'k'", p)
        self.assertIn("give every wave the same length", p)
        self.assertIn("1 label(s) for 9 '=' slot(s)", p)

    def test_spi_mode_must_match_the_clock_idle_level(self):
        m = {"kind": "timing", "id": "t", "title": "T", "alt": "x" * 50, "bus": "spi", "mode": {"cpol": 1, "cpha": 1},
             "signals": [{"id": "sck", "wave": "0pp0", "clock": True}]}
        self.assertIn("idles high, the wave starts 0", problems_of(timing.validate, m))

    def test_the_value_text(self):
        self.assertEqual(timing.value_text({"min": 20, "unit": "ns"}), "min 20 ns")
        self.assertEqual(timing.value_text({"min": 0.6, "max": 50, "unit": "us"}), "min 0.6 · max 50 us")

    def test_gaps_are_slots_of_their_own(self):
        segs = timing._segments("1n|n1")
        self.assertEqual([s["c"] for s in segs], ["1", "n", "gap", "n", "1"])
        self.assertEqual(segs[2]["of"], "n")

    def test_table_twin_lists_every_param_with_its_section(self):
        fig = kinds.from_model(MODEL / "i2c-timing.timing.yml", lock_dir=GOLDEN)
        self.assertEqual([r[0] for r in fig.twin["rows"]], ["tHD;STA", "tSU;DAT", "fSCL"])
        self.assertTrue(all(r[-1] == "6.4 I2C timing, p. 9" for r in fig.twin["rows"]))

    def test_too_many_slots_is_a_problem(self):
        m = copy.deepcopy(load("uart-frame.timing.yml"))
        m["signals"][0]["wave"] = "1" * 80
        m["signals"][0]["data"] = []
        fig = timing.build(m, GOLDEN, "m")
        self.assertTrue(any("slots leave" in p for p in fig.problems()))


class TopologyTests(unittest.TestCase):
    def test_fixtures_build_clean_and_fit_a_phone(self):
        for name in ("spi-chain.topology.yml", "can-bus.topology.yml", "i2c-bus.topology.yml"):
            fig = kinds.from_model(MODEL / name, lock_dir=GOLDEN)
            self.assertEqual(fig.problems(), [], name)
            self.assertGreaterEqual(fig.min_text_px * 360 / fig.width, 7.8, name)

    def test_an_address_needs_a_ref(self):
        m = load("i2c-bus.topology.yml")
        del m["nodes"][0]["ref"]
        self.assertIn("nodes[0].ref: no datasheet reference", problems_of(topology.validate, m))

    def test_a_fact_with_a_number_needs_a_ref(self):
        m = load("can-bus.topology.yml")
        del m["facts"][0]["ref"]
        self.assertIn("facts[0].ref: no datasheet reference", problems_of(topology.validate, m))

    def test_terminators_need_a_pair(self):
        m = load("can-bus.topology.yml")
        m["shared"] = ["CANH", "CANL", "GND"]
        self.assertIn("shared needs exactly two lines", problems_of(topology.validate, m))

    def test_style_keys(self):
        m = load("spi-chain.topology.yml")
        m["style"] = "bus"
        self.assertIn("chain: only for style: chain", problems_of(topology.validate, m))
        m = load("spi-chain.topology.yml")
        del m["chain"]["in"]
        self.assertIn("chain: missing 'in'", problems_of(topology.validate, m))

    def test_node_count(self):
        m = load("spi-chain.topology.yml")
        m["nodes"] = m["nodes"][:1]
        self.assertIn("two to four entries", problems_of(topology.validate, m))


class CitationTests(unittest.TestCase):
    """A driver cites the sections its docs/hardware.yml already names; the document must be in datasheets.yml."""

    def repo(self) -> pathlib.Path:
        d = pathlib.Path(tempfile.mkdtemp())
        (d / "docs").mkdir()
        (d / "docs/datasheets.yml").write_text("---\ndocuments:\n  - {id: ds, title: Datasheet}\n")
        (d / "docs/hardware.yml").write_text(
            "---\nrefs:\n  spi: {doc: ds, section: \"6.2 SPI interface\", page: 8}\n"
            "  other: {doc: an, section: \"1 Intro\", page: 1}\n")
        return d

    def model(self, ref: str, refs=None) -> dict:
        m = {"kind": "timing", "id": "t", "title": "T", "alt": "x" * 50, "bus": "spi",
             "signals": [{"id": "cs", "wave": "10.1"}],
             "params": [{"id": "a", "symbol": "tA", "label": "A", "min": 1, "unit": "ns", "ref": ref}]}
        if refs:
            m["refs"] = refs
        return m

    def test_hardware_refs_are_the_fallback(self):
        root = self.repo()
        self.assertEqual(problems_of(timing.validate, self.model("spi"), root), "")
        cites = timing.validate(self.model("spi"), "m", root=root)
        self.assertEqual(cites.sources_line(), "Datasheet: 6.2 SPI interface, p. 8.")

    def test_a_document_not_in_datasheets_yml_fails(self):
        root = self.repo()
        p = problems_of(timing.validate, self.model("x", {"x": {"doc": "nope", "section": "1 A", "page": 2}}), root)
        self.assertIn("'nope' is not a document of docs/datasheets.yml", p)
        # A hardware.yml ref to an unknown document is not offered at all.
        self.assertIn("unknown ref 'other'", problems_of(timing.validate, self.model("other"), root))

    def test_a_page_must_be_a_printed_page_number(self):
        p = problems_of(timing.validate, self.model("x", {"x": {"doc": "ds", "section": "1 A", "page": "two"}}),
                        self.repo())
        self.assertIn("refs.x.page: the printed page number", p)


if __name__ == "__main__":
    unittest.main()
