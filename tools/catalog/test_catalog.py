#!/usr/bin/env python3
"""Unit tests of the catalogue generator, its schemas and the SBOMs, with a fake GitHub API. PyYAML, jsonschema."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import tempfile
import unittest

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import catalog  # noqa: E402

SHA = "a" * 40
DRIVER_YML = "name: abc\nversion: 1.2.0\nbus: [spi]\nmcus: [any]\nperipheral: null\nkb_core_min: null\n"


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class Tree:
    def __init__(self, driver_yml: str = DRIVER_YML, gates: str = "", tag: str = "v1.2.0"):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.root = self.tmp.name
        write(os.path.join(d, "lock.yml"), f"drivers:\n  - {{name: abc, repo: org/driver-abc, tag: {tag}, "
                                           f"commit: {SHA}, kind: {'rc' if '-rc' in tag else 'release'}}}\n")
        write(os.path.join(d, "gates.cmake"), f"set(G {gates})\n")
        write(os.path.join(d, "cmake", "p_version.cmake"),
              "set(P_VERSION_MAJOR 0)\nset(P_VERSION_MINOR 3)\nset(P_VERSION_PATCH 0)\n")
        write(os.path.join(d, "lib", "inc", "kb", "bindings", "abc.hpp"), "#pragma once\n")
        self.files = {f"/repos/org/driver-abc/contents/driver.yml?ref={SHA}": driver_yml,
                      f"/repos/org/driver-abc/contents/LICENSE?ref={SHA}": "MIT License\n\nPermission is hereby "
                                                                          "granted, free of charge, ..."}

    def api(self, path):
        if path in self.files:
            return 200, {"content": base64.b64encode(self.files[path].encode()).decode()}
        return 404, None

    def args(self, **kw):
        base = dict(root=self.root, lock="lock.yml", gates="gates.cmake", version_file="", results=[],
                    results_json="", binding_pattern="", schemas="")
        base.update(kw)
        return argparse.Namespace(**base)


class Build(unittest.TestCase):
    def setUp(self):
        self._api = catalog.api_get

    def tree(self, *a, **kw) -> Tree:
        t = Tree(*a, **kw)
        self.addCleanup(t.tmp.cleanup)
        return t

    def tearDown(self):
        catalog.api_get = self._api

    def build(self, tree: Tree, **kw):
        catalog.api_get = tree.api
        return catalog.build(tree.args(**kw))

    def test_entry_configs_and_binding(self):
        t = self.tree()
        results = json.dumps([{"name": "x", "mcu": "HOST", "rtos": "NONE", "status": "passed"},
                              {"mcu": "ESP32", "rtos": "FREERTOS", "result": "fail"},
                              {"driver": "other", "mcu": "STM32", "rtos": "NONE", "result": "pass"},
                              {"name": "no-mcu", "status": "passed"}])
        doc, errors, _ = self.build(t, results_json=results,
                                    binding_pattern="lib/inc/kb/bindings/{name}.hpp")
        self.assertEqual(errors, [])
        self.assertEqual(doc["kb_core"], "0.3.0")
        d = doc["drivers"][0]
        self.assertEqual(d["binding"], "kb/bindings/abc.hpp")
        self.assertEqual(d["configs"], [{"mcu": "ESP32", "rtos": "FREERTOS", "result": "fail"},
                                        {"mcu": "HOST", "rtos": "NONE", "result": "pass"}])

    def test_gate_disagreement_is_an_error_not_an_entry(self):
        t = self.tree(DRIVER_YML.replace("mcus: [any]", "mcus: [esp32]").replace("peripheral: null",
                                                                                   "peripheral: rmt"))
        doc, errors, _ = self.build(t)
        self.assertEqual(doc["drivers"], [])
        self.assertTrue(any("gate table has no entry" in e for e in errors), errors)
        t = self.tree(DRIVER_YML.replace("mcus: [any]", "mcus: [esp32]").replace("peripheral: null", "peripheral: rmt"),
                 gates='"abc:ESP32:rmt"')
        doc, errors, _ = self.build(t)
        self.assertEqual((errors, len(doc["drivers"])), ([], 1))

    def test_schema_and_version_errors(self):
        doc, errors, _ = self.build(self.tree(DRIVER_YML.replace("bus: [spi]", "bus: [carrier-pigeon]")))
        self.assertEqual(doc["drivers"], [])
        self.assertTrue(any("driver.yml" in e and "bus" in e for e in errors), errors)
        doc, errors, _ = self.build(self.tree(tag="v1.2.0-rc.1"))
        self.assertEqual(errors, [])  # the rc tag's version is 1.2.0
        doc, errors, _ = self.build(self.tree(DRIVER_YML.replace("1.2.0", "1.3.0")))
        self.assertTrue(any("not the tag's" in e for e in errors), errors)

    def test_unreadable_driver(self):
        t = self.tree()
        t.files.clear()
        _, errors, _ = self.build(t)
        self.assertTrue(any("not readable" in e for e in errors), errors)

    def test_check_compares_data(self):
        t = self.tree()
        catalog.api_get = t.api
        out = os.path.join(t.root, "gen", "compat.yml")
        doc, _, _ = catalog.build(t.args())
        write(os.path.join(t.root, "compat.yml"), "# hand comment\n" + yaml.safe_dump(doc))
        ns = t.args(out=out, check="compat.yml", summary=None, github_output=None)
        self.assertEqual(catalog.cmd_build(ns), 0)
        doc["kb_core"] = "9.9.9"
        write(os.path.join(t.root, "compat.yml"), yaml.safe_dump(doc))
        self.assertEqual(catalog.cmd_build(ns), 1)

    def test_output_is_deterministic(self):
        t = self.tree()
        a = catalog.dump(self.build(t)[0])
        b = catalog.dump(self.build(t)[0])
        self.assertEqual(a, b)
        self.assertNotRegex(a, r"\d{4}-\d{2}-\d{2}T")


class Sbom(unittest.TestCase):
    def test_both_formats(self):
        t = Tree()
        self.addCleanup(t.tmp.cleanup)
        old = catalog.api_get
        catalog.api_get = t.api
        try:
            doc, _, _ = catalog.build(t.args())
            cat = os.path.join(t.root, "compat.yml")
            write(cat, catalog.dump(doc))
            out = os.path.join(t.root, "sbom")
            ns = argparse.Namespace(root=t.root, catalog=cat, name="core", version="0.3.0", repo="org/core",
                                    out_dir=out)
            self.assertEqual(catalog.cmd_sbom(ns), 0)
            with open(os.path.join(out, "core-0.3.0.cdx.json"), encoding="utf-8") as fh:
                cdx = json.load(fh)
            with open(os.path.join(out, "core-0.3.0.spdx.json"), encoding="utf-8") as fh:
                spdx = json.load(fh)
        finally:
            catalog.api_get = old
        self.assertEqual(cdx["specVersion"], "1.6")
        self.assertEqual(cdx["components"][0]["purl"], "pkg:github/org/driver-abc@v1.2.0")
        self.assertEqual(cdx["components"][0]["licenses"], [{"license": {"id": "MIT"}}])
        self.assertEqual(spdx["spdxVersion"], "SPDX-2.3")
        self.assertEqual(len(spdx["relationships"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
