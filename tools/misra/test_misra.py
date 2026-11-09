#!/usr/bin/env python3
"""Unit tests of misra.py: the licence gate, deviation records and markers, build flags, extraction coverage and the
level policy of the report. Run: python tools/misra/test_misra.py"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MISRA = os.path.join(HERE, "misra.py")

RECORDS = textwrap.dedent("""\
    deviations:
      - id: MD-CPP-003
        guideline: Rule 8.2.5
        scope: MCU port only.
        justification: Registers.
        mitigation: Accessors.
        approved_by: maintainer
        date: 2026-11-08
        review_by: 2027-11-08
      - id: MD-CPP-009
        guideline: Rule 6.7.2
        scope: Old.
        justification: Old.
        mitigation: Old.
        approved_by: maintainer
        date: 2025-01-01
        review_by: 2026-01-01
    """)

MATRIX = textwrap.dedent("""\
    guidelines:
      - {id: Rule 0.2.2, category: required, our_category: required, applies: yes,
         verification: [{by: compiler, how: x}]}
      - {id: Rule 8.2.5, category: required, our_category: required, applies: yes,
         verification: [{by: clang-tidy, how: x}]}
      - {id: Rule 6.5.1, category: advisory, our_category: advisory, applies: yes,
         verification: [{by: review, how: x}]}
    """)


def run(*args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, MISRA, *args], capture_output=True, text=True, cwd=cwd)


def git_repo(files: dict[str, str]) -> str:
    d = tempfile.mkdtemp()
    for path, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, path)) or d, exist_ok=True)
        with open(os.path.join(d, path), "w", encoding="utf-8") as fh:
            fh.write(text)
    subprocess.run(["git", "init", "-q", d], check=True)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    return d


def sarif(results: list[tuple[str, str, int, bool]]) -> dict:
    rules = sorted({(q, tag) for q, tag, _l, _d in results})
    return {"runs": [{"tool": {"driver": {"rules": [
        {"id": q, "properties": {"tags": [f"external/misra/id/{tag}"]}} for q, tag in rules]}},
        "results": [{"ruleId": q, "message": {"text": "m"}, "locations": [{"physicalLocation": {
            "artifactLocation": {"uri": "inc/a.hpp"}, "region": {"startLine": line}}}],
            **({"suppressions": [{"kind": "inSource"}]} if dev else {})} for q, _t, line, dev in results]}]}


class Licence(unittest.TestCase):
    def test_private_without_licence_is_refused(self):
        r = run("licence", "--private", "true", "--advanced-security", "false")
        self.assertEqual(r.returncode, 1)
        self.assertIn("private repository", r.stdout)

    def test_private_with_advanced_security_is_allowed(self):
        self.assertEqual(run("licence", "--private", "true", "--advanced-security", "true").returncode, 0)

    def test_public_needs_an_osi_licence(self):
        d = git_repo({"README.md": "x"})
        self.assertEqual(run("licence", "--private", "false", "--repo", d).returncode, 1)
        d = git_repo({"LICENSE": "MIT License\n\nCopyright (c) 2026 Kokeb Labs\n"})
        self.assertEqual(run("licence", "--private", "false", "--repo", d).returncode, 0)


    def test_private_open_source_prerelease_needs_an_osi_licence(self):
        d = git_repo({"README.md": "x"})
        args = ("licence", "--private", "true", "--open-source-prerelease", "true", "--repo", d)
        self.assertEqual(run(*args).returncode, 1)
        d = git_repo({"LICENSE": "MIT License\n\nCopyright (c) 2026 The x authors\n"})
        r = run("licence", "--private", "true", "--open-source-prerelease", "true", "--repo", d)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("open-source pre-release", r.stdout)


class Prepare(unittest.TestCase):
    def prepare(self, files: dict[str, str], today="2026-11-08"):
        d = git_repo({"records.yml": RECORDS, **files})
        out = os.path.join(d, "out")
        r = run("prepare", "--records", os.path.join(d, "records.yml"), "--paths", "inc", "--repo", d,
                "--coding-standards", os.path.join(d, "coding-standards.yml"), "--markers", out, "--today", today)
        with open(out, encoding="utf-8") as fh:
            return r, json.load(fh), d

    def test_records_become_code_identifiers(self):
        r, m, d = self.prepare({"inc/a.hpp": "int x;\n"}, today="2025-06-01")
        self.assertEqual(r.returncode, 0, r.stdout)
        with open(os.path.join(d, "coding-standards.yml"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("code-identifier: MD-CPP-003", text)
        self.assertIn("rule-id: RULE-8-2-5", text)
        self.assertIn("report-deviated-alerts: true", text)

    def test_lapsed_record_fails(self):
        r, m, _d = self.prepare({"inc/a.hpp": "int x;\n"})
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any("MD-CPP-009 lapsed" in e for e in m["errors"]))

    def test_markers_must_cite_known_records(self):
        r, m, _d = self.prepare({"inc/a.hpp": textwrap.dedent("""\
            int a;  // codeql::misra_deviation(MD-CPP-003)
            int b;  // codeql::misra_deviation(MD-CPP-123)
            int c;  // codeql::autosar_deviation(MD-CPP-003)
            int d;  // NOLINT(cppcoreguidelines-pro-type-reinterpret-cast)
            int e;  // NOLINT(cppcoreguidelines-pro-type-reinterpret-cast) MD-CPP-003
            // codeql::misra_deviation_next_line(MD-CPP-003)
            int f;  // see MD-CPP-003 in the middle: not a marker
            """)}, today="2025-06-01")
        self.assertEqual(r.returncode, 1)
        errors = sorted((e["line"], e["error"]) for e in m["marker_errors"])
        self.assertEqual([line for line, _ in errors], [2, 3, 4])
        self.assertEqual(sorted(mk["line"] for mk in m["markers"]), [1, 2, 3, 5, 6])

    def test_a_committed_coding_standards_file_fails(self):
        r, m, _d = self.prepare({"inc/a.hpp": "int x;\n", "coding-standards.yml": "deviations: []\n"},
                                today="2025-06-01")
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any("coding-standards.yml" in e for e in m["errors"]))


class Report(unittest.TestCase):
    def report(self, results, level, scopes=(), extraction_complete=True):
        d = tempfile.mkdtemp()
        cfg = os.path.join(d, "host")
        os.makedirs(cfg)
        canary = [("cpp/misra/unused-parameter-misra-cpp", "rule-0-2-2", 1, False)]
        s = sarif(results + canary)
        s["runs"][0]["results"][-1]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] = \
            ".ru-misra/ci-tools/tools/misra/canary/ru_misra_canary.cpp"
        for name, data in (("results.sarif", s), ("extraction.json", {"complete": extraction_complete}),
                           ("flags.json", {"complete": True}),
                           ("suppressions.json", {"#select": {"tuples": [
                               [{}, f"// lgtm[{q}]", f"lgtm[{q}]", {"label": "", "url": {
                                   "uri": f"file:{d}/inc/a.hpp", "startLine": line, "endLine": line}}]
                               for q, line in scopes]}})):
            with open(os.path.join(cfg, name), "w", encoding="utf-8") as fh:
                json.dump(data, fh)
        with open(os.path.join(d, "markers.json"), "w", encoding="utf-8") as fh:
            json.dump({"records": {}, "markers": [], "marker_errors": [], "errors": []}, fh)
        with open(os.path.join(d, "matrix.yml"), "w", encoding="utf-8") as fh:
            fh.write(MATRIX)
        out = os.path.join(d, "out")
        r = run("report", "--matrix", os.path.join(d, "matrix.yml"), "--markers", os.path.join(d, "markers.json"),
                "--config", f"host={cfg}", "--repo", d, "--paths", "inc", "--level", level,
                "--canary-expect", "cpp/misra/unused-parameter-misra-cpp", "--out-dir", out, "--github-output", "")
        with open(os.path.join(out, "misra-summary.json"), encoding="utf-8") as fh:
            return r, json.load(fh)

    def test_high_fails_required_and_warns_advisory(self):
        r, s = self.report([("q/adv", "rule-6-5-1", 3, False)], "high")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(s["warning_guidelines"], ["Rule 6.5.1"])
        r, s = self.report([("q/req", "rule-8-2-5", 3, False)], "high")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(s["failing_guidelines"], ["Rule 8.2.5"])

    def test_safety_fails_any_undeviated_finding(self):
        r, s = self.report([("q/adv", "rule-6-5-1", 3, False)], "safety")
        self.assertEqual(r.returncode, 1)

    def test_deviated_findings_pass_and_unused_markers_fail(self):
        r, s = self.report([("q/req", "rule-8-2-5", 3, True)], "safety", scopes=[("q/req", 3)])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(s["guidelines"]["Rule 8.2.5"]["status"], "deviated")
        r, s = self.report([("q/req", "rule-8-2-5", 3, True)], "safety", scopes=[("q/req", 3), ("q/req", 9)])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(s["suppression_errors"]), 1)

    def test_missing_canary_or_incomplete_extraction_fails(self):
        r, s = self.report([], "high", extraction_complete=False)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any("extraction" in p for p in s["problems"]))


class Extraction(unittest.TestCase):
    def test_every_unit_and_source_file_must_be_extracted(self):
        d = git_repo({"inc/a.hpp": "x", "inc/b.hpp": "y", "src/a.cpp": "z"})
        compdb = os.path.join(d, "cc.json")
        with open(compdb, "w", encoding="utf-8") as fh:
            json.dump([{"directory": d, "file": "src/a.cpp", "arguments": ["g++", "-c", "src/a.cpp"]}], fh)
        compiled = os.path.join(d, "compiled.json")
        with open(compiled, "w", encoding="utf-8") as fh:
            json.dump({"#select": {"tuples": [[os.path.join(d, "src/a.cpp"), "src/a.cpp", True],
                                              [os.path.join(d, "inc/a.hpp"), "inc/a.hpp", False]]}}, fh)
        diags = os.path.join(d, "diags.json")
        with open(diags, "w", encoding="utf-8") as fh:
            json.dump({"#select": {"tuples": []}}, fh)
        out = os.path.join(d, "ext.json")
        r = run("extraction", "--compdb", compdb, "--compiled", compiled, "--diagnostics", diags, "--repo", d,
                "--paths", "inc src", "--out", out)
        self.assertEqual(r.returncode, 1)
        with open(out, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["not_analysed"], ["inc/b.hpp"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
