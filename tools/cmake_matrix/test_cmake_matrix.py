#!/usr/bin/env python3
"""Unit tests of ru-cmake-matrix's planner, entry runner (dry run) and report. Standard library only."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
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

import plan  # noqa: E402

ENV = {"MATRIX": "", "MATRIX_FROM": "", "MCUS": "", "RTOSES": "", "PRESETS": "", "MCU_TOOLCHAINS": "{}",
       "MCU_VARIABLE": "KB_MCU", "RTOS_VARIABLE": "KB_RTOS", "DEFAULT_TOOLCHAIN": "host-gcc", "BUILD_TYPE": "Debug",
       "SOURCE_DIR": ".", "BUILD_TARGET": "", "RUN_TESTS": "true"}


def run_plan(**kw):
    env = dict(ENV, **kw)
    return plan.plan(env)


class Plan(unittest.TestCase):
    def test_cross_product_names_and_args(self):
        out, errors = run_plan(MCUS="HOST ESP32", RTOSES="NONE FREERTOS",
                               MCU_TOOLCHAINS='{"ESP32*": "esp-idf:esp32s3", "HOST": "host-clang"}')
        self.assertEqual(errors, [])
        self.assertEqual(out["count"], 4)
        names = [e["name"] for e in out["runner"] + out["container"]]
        self.assertEqual(sorted(names), ["ESP32-FREERTOS", "ESP32-NONE", "HOST-FREERTOS", "HOST-NONE"])
        esp = next(e for e in out["container"] if e["name"] == "ESP32-FREERTOS")
        self.assertEqual((esp["toolchain"], esp["idf_target"], esp["test"]), ("esp-idf", "esp32s3", False))
        self.assertEqual(esp["cmake_args"], "-DKB_MCU=ESP32 -DKB_RTOS=FREERTOS")
        host = next(e for e in out["runner"] if e["name"] == "HOST-NONE")
        self.assertEqual((host["toolchain"], host["test"]), ("host-clang", True))

    def test_explicit_entries_and_defaults(self):
        m = json.dumps([{"name": "a"}, {"name": "m4", "toolchain": "arm-none-eabi", "cmake_args": "-DX=1"},
                        {"name": "notest", "test": False}])
        out, errors = run_plan(MATRIX=m, SOURCE_DIR="sub", BUILD_TARGET="lib")
        self.assertEqual(errors, [])
        a, m4, nt = out["runner"]
        self.assertEqual((a["toolchain"], a["source_dir"], a["target"], a["test"]), ("host-gcc", "sub", "lib", True))
        self.assertEqual((m4["core"], m4["test"], m4["cmake_args"]), ("cortex-m4f", False, "-DX=1"))
        self.assertFalse(nt["test"])

    def test_catalogue_pairs(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "compat.json")
            with open(p, "w") as fh:
                json.dump({"drivers": [{"configs": [{"mcu": "ESP32", "rtos": "FREERTOS"},
                                                    {"mcu": "HOST", "rtos": "NONE"}]},
                                       {"configs": [{"mcu": "ESP32", "rtos": "FREERTOS"}]}]}, fh)
            out, errors = run_plan(MATRIX_FROM=p, MCU_TOOLCHAINS='{"*": "host-gcc"}')
        self.assertEqual(errors, [])
        self.assertEqual([e["name"] for e in out["runner"]], ["ESP32-FREERTOS", "HOST-NONE"])

    def test_errors(self):
        cases = [
            ([{"name": "x", "colour": 1}], "unknown key"),
            ([{"name": "x"}, {"name": "x"}], "more than once"),
            ([{"name": "bad name"}], "name must be"),
            ([{"name": "x", "toolchain": "msvc"}], "is not one of"),
            ([{"name": "x", "toolchain": "arm-none-eabi", "core": "cortex-a53"}], "core"),
            ([{"name": "x", "toolchain": "arm-none-eabi", "test": True}], "needs a host toolchain"),
            ([{"name": "x", "mcu": "ES P32"}], "may hold only"),
        ]
        for matrix, needle in cases:
            _, errors = run_plan(MATRIX=json.dumps(matrix))
            self.assertTrue(any(needle in e for e in errors), (matrix, errors))
        _, errors = run_plan(MATRIX="{not json")
        self.assertIn("not JSON", errors[0])

    def test_call_id_is_stable(self):
        a, _ = run_plan(MCUS="A B")
        b, _ = run_plan(MCUS="A B")
        c, _ = run_plan(MCUS="A C")
        self.assertEqual(a["call_id"], b["call_id"])
        self.assertNotEqual(a["call_id"], c["call_id"])


class RunAndReport(unittest.TestCase):
    def test_dry_run_and_report(self):
        out, _ = run_plan(MATRIX=json.dumps([{"name": "a"}, {"name": "b", "toolchain": "arm-none-eabi"}]))
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, RUNNER_TEMP=d)
            r = subprocess.run([sys.executable, os.path.join(HERE, "run.py"), "--entry-json",
                                json.dumps(out["runner"][1]), "--out-dir", os.path.join(d, "res", "b"), "--dry-run"],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("-DCMAKE_TOOLCHAIN_FILE=", r.stdout)
            self.assertIn("-mcpu=cortex-m4", text(os.path.join(d, "cmake-matrix", "b", "toolchain-cortex-m4f.cmake")))
            gh = os.path.join(d, "gh.txt")
            r = subprocess.run([sys.executable, os.path.join(HERE, "report.py"), "--plan", json.dumps(out),
                                "--results", os.path.join(d, "res"), "--github-output", gh],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)  # "a" has no result
            out_text = text(gh)
            self.assertIn("passed=1", out_text)
            self.assertIn("failed=1", out_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
