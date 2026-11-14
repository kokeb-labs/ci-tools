#!/usr/bin/env python3
"""Unit tests of ru-mutation's listing, operators and report. PyYAML for the equivalents file."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FIXTURE = os.path.join(REPO, "tests", "fixtures", "mutation")
sys.path.insert(0, HERE)


def jload(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def jdump(obj, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()

import mutate  # noqa: E402


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(HERE, "mutate.py"), *args], capture_output=True, text=True)


class Operators(unittest.TestCase):
    def test_selftest(self):
        self.assertEqual(cli("selftest").returncode, 0)

    def test_mask_keeps_length_and_lines(self):
        src = '#define A(x) \\\n  ((x) < 1)\nint f() { return 1 /* < */ < 2; }  // a < b\nconst char* s = "a < b";\n'
        m = mutate.mask(src)
        self.assertEqual(len(m), len(src))
        self.assertEqual(m.count("\n"), src.count("\n"))
        ops = [op for line in m.split("\n") for op, *_ in mutate.candidates(line)]
        self.assertEqual(sorted(ops), ["const", "const", "ror-lt"])

    def test_generated_ids_are_stable(self):
        a = mutate.generate(FIXTURE, ["src"])
        b = mutate.generate(FIXTURE, ["src"])
        self.assertEqual([m["id"] for m in a], [m["id"] for m in b])
        self.assertEqual(len({m["id"] for m in a}), len(a))


class Listing(unittest.TestCase):
    def test_catalogue_with_equivalents(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "m.json")
            r = cli("list", "--root", FIXTURE, "--catalogue", "tools/mutants/*.txt", "--paths", "src include",
                    "--equivalents", os.path.join(FIXTURE, "equivalent-mutants.yml"), "--out", out)
            self.assertEqual(r.returncode, 0, r.stdout)
            doc = jload(out)
            self.assertEqual(doc["mode"], "catalogue")
            eq = {m["id"]: m["equivalent"] for m in doc["mutants"] if m["equivalent"]}
            self.assertEqual(list(eq), ["clamp-low-equal"])
            first = next(m for m in doc["mutants"] if m["id"] == "clamp-low")
            self.assertEqual((first["file"], first["line"]), ("src/limits.cpp", 6))

    def test_stale_equivalent_fails(self):
        with tempfile.TemporaryDirectory() as d:
            eq = os.path.join(d, "eq.yml")
            with open(eq, "w") as fh:
                fh.write("gone-mutant: it was removed\n")
            r = cli("list", "--root", FIXTURE, "--paths", "src", "--equivalents", eq, "--out",
                    os.path.join(d, "m.json"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("gone-mutant", r.stdout)

    def test_max_is_a_stable_sample(self):
        with tempfile.TemporaryDirectory() as d:
            ids = []
            for i in range(2):
                out = os.path.join(d, f"m{i}.json")
                cli("list", "--root", FIXTURE, "--mode", "generated", "--paths", "src", "--max", "3", "--out", out)
                ids.append(sorted(m["id"] for m in jload(out)["mutants"]))
            self.assertEqual(len(ids[0]), 3)
            self.assertEqual(ids[0], ids[1])


class Report(unittest.TestCase):
    def report(self, statuses: dict[str, str], level: str, threshold: str = "") -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as d:
            mutants = [{"id": k, "file": "src/a.cpp", "line": 1, "column": 1, "operator": "ror-lt", "old": "<",
                        "new": "<=", "what": "w", "equivalent": "", "source": "generated"} for k in statuses]
            jdump({"mode": "generated", "mutants": mutants}, os.path.join(d, "m.json"))
            jdump({"results": [{"id": k, "status": v, "note": ""} for k, v in statuses.items() if v != "missing"]},
                  os.path.join(d, "r.json"))
            gh = os.path.join(d, "out.txt")
            r = cli("report", "--root", d, "--mutants", os.path.join(d, "m.json"), "--results",
                    os.path.join(d, "r.json"), "--level", level, "--threshold", threshold, "--report-dir",
                    os.path.join(d, "rep"), "--github-output", gh)
            mte = jload(os.path.join(d, "rep", "mutation-report.json"))
            self.assertEqual(mte["schemaVersion"], "2")
            return r.returncode, text(gh)

    def test_levels(self):
        four_one = {"a": "killed", "b": "killed", "c": "killed", "d": "killed", "e": "survived"}
        self.assertEqual(self.report(four_one, "standard")[0], 0)  # 80 %
        rc, out = self.report(four_one, "high")
        self.assertEqual(rc, 1)
        self.assertIn("kill_rate=80.0", out)
        self.assertEqual(self.report(four_one, "high", "75")[0], 0)

    def test_compile_errors_are_not_scored_but_missing_fails(self):
        rc, out = self.report({"a": "killed", "b": "compile_error"}, "high")
        self.assertEqual(rc, 0)
        self.assertIn("kill_rate=100.0", out)
        self.assertEqual(self.report({"a": "killed", "b": "missing"}, "standard")[0], 1)
        self.assertEqual(self.report({"a": "killed", "b": "broken"}, "high")[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
