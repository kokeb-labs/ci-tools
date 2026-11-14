#!/usr/bin/env python3
"""Unit tests of the layering checker: its fixtures, the target graph, the symbol lint, the denylist and the poison
headers. PyYAML; the symbol test needs a C++ compiler and nm."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FIXTURE = os.path.join(REPO, "tests", "fixtures", "layering")
RULES = os.path.join(FIXTURE, "rules.yml")
sys.path.insert(0, HERE)

import layering  # noqa: E402


def cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(HERE, "layering.py"), *args], capture_output=True, text=True)


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class Fixtures(unittest.TestCase):
    def test_fixture_cases(self):
        r = cli("fixtures", "--dir", os.path.join(FIXTURE, "tests", "layering"), "--rules", RULES)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ok   good", r.stdout)

    def test_fixture_tree_is_clean(self):
        c, _ = layering.run_check(FIXTURE, RULES, "", "", ["tests/layering/**"])
        self.assertEqual(c.findings, [])

    def test_wrong_expectation_fails(self):
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(os.path.join(FIXTURE, "tests", "layering"), os.path.join(d, "f"))
            write(os.path.join(d, "f", "bad", "virtual-keyword", "expect.txt"), "LAY-001\n")
            r = cli("fixtures", "--dir", os.path.join(d, "f"), "--rules", RULES)
            self.assertEqual(r.returncode, 1)
            self.assertIn("FAIL bad/virtual-keyword", r.stdout)

    def test_empty_fixture_folder_warns(self):
        with tempfile.TemporaryDirectory() as d:
            r = cli("fixtures", "--dir", d, "--rules", RULES)
            self.assertEqual(r.returncode, 0)
            self.assertIn("::warning::", r.stdout)


class Graph(unittest.TestCase):
    DOT = '''digraph "g" {
subgraph clusterLegend {
  legendNode0 [ label = "Executable", shape = egg ];
  legendNode1 -> legendNode4 [ label = "Interface", style = dashed ];
}
    "node0" [ label = "fx_core", shape = octagon ];
    "node1" [ label = "fx_app", shape = octagon ];
    "node2" [ label = "fx_backend", shape = octagon ];
    "node0" -> "node1"  // fx_core -> fx_app
    "node1" -> "node2" [ style = dashed ] // fx_app -> fx_backend
    "node2" -> "node0" [ style = dotted ] // fx_backend -> fx_core
}
'''

    def test_layers_and_private_only(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "g.dot"), self.DOT)
            c = layering.Checker(FIXTURE, layering.Rules(RULES, FIXTURE), ["tests/layering/**"])
            c.check_targets(os.path.join(d, "g.dot"))
        msgs = sorted(f["message"] for f in c.findings)
        self.assertEqual([f["rule"] for f in c.findings], ["LAY-006"] * 2, msgs)
        self.assertIn("fx_core links fx_app (PUBLIC), a higher layer", msgs)
        self.assertIn("fx_app links fx_backend INTERFACE; it may be linked PRIVATE only", msgs)


class Symbols(unittest.TestCase):
    @unittest.skipUnless(shutil.which("c++") and shutil.which("nm"), "needs a C++ compiler and nm")
    def test_forbidden_symbol(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "lib", "core", "src", "use.cpp")
            write(src, 'extern "C" int xTaskCreate(void*);\nint f() { return xTaskCreate(nullptr); }\n')
            shutil.copy(RULES, os.path.join(d, "rules.yml"))
            obj = os.path.join(d, "build", "use.cpp.o")
            os.makedirs(os.path.dirname(obj))
            subprocess.run(["c++", "-c", src, "-o", obj], check=True)
            db = os.path.join(d, "build", "compile_commands.json")
            write(db, json.dumps([{"directory": d, "file": src, "output": obj, "command": f"c++ -c {src}"}]))
            c, n = layering.run_check(d, os.path.join(d, "rules.yml"), "", db, [], objects=os.path.join(d, "build"))
        self.assertEqual(n, 1)
        self.assertEqual([f["rule"] for f in c.findings], ["SYM-001"], c.findings)


class Misc(unittest.TestCase):
    def test_denylist_never_prints_the_name(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "lib", "core", "src", "a.cpp"), "// made for ACMEWIDGET\nint a;\n")
            deny = os.path.join(d, "deny.txt")
            write(deny, "acmewidget\n")
            r = cli("check", "--root", d, "--rules", RULES, "--denylist", deny)
        self.assertEqual(r.returncode, 1)
        self.assertIn("LAY-009", r.stdout)
        self.assertNotIn("acmewidget", r.stdout.lower())

    def test_poison_headers(self):
        with tempfile.TemporaryDirectory() as d:
            r = cli("poison", "--rules", RULES, "--out", d)
            self.assertEqual(r.returncode, 0, r.stdout)
            for h in ("FreeRTOS.h", "freertos/task.h", "esp_log.h"):
                with open(os.path.join(d, h), encoding="utf-8") as fh:
                    self.assertIn(layering.POISON_MARK, fh.read())

    def test_glob(self):
        self.assertTrue(layering.gmatch("lib/a/inc/x/y.hpp", ["lib/*/inc/**"]))
        self.assertFalse(layering.gmatch("lib/a/b/inc/y.hpp", ["lib/*/inc/**"]))
        self.assertTrue(layering.gmatch("a/b/CMakeLists.txt", ["**/CMakeLists.txt"]))
        self.assertTrue(layering.gmatch("CMakeLists.txt", ["**/CMakeLists.txt"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
