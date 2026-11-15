#!/usr/bin/env python3
"""Unit tests of the language standard checker: the registry, the declaration and the files. PyYAML."""

from __future__ import annotations

import contextlib
import copy
import datetime
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_standards as cs  # noqa: E402

TODAY = datetime.date(2026, 11, 20)
STANDARDS = Path(HERE) / "standards.yml"

DRIVER_YML = """name: abc
version: 0.1.0
bus: [spi]
language:
  standard: 20
  profile: KB-CPP20
  profile_version: "1.0"
  misra: "MISRA C++:2023"
  compilers:
    gcc: "10"
    clang: "13"
  tested: [20]
  effective_from: 2026-11-15
"""
FILES = {
    "CMakeLists.txt": "add_library(abc INTERFACE)\ntarget_compile_features(abc INTERFACE cxx_std_20)\n",
    "tests/CMakeLists.txt": "target_compile_features(t PRIVATE cxx_std_20)\n"
                            'file(WRITE x "static_assert(__cplusplus == 202002L);")\n',
    "_config/.clang-format": "BasedOnStyle: Google\nStandard: c++20\n",
    "tools/preflight.sh": "cppcheck --std=c++20 x\nclang-tidy y -- -std=c++20\n",
    ".github/workflows/ci-repo-checks.yml": 'jobs:\n  a:\n    with:\n      cppcheck_std: "c++20"\n',
    "README.md": "# Abc\n\n[![C++20](https://img.shields.io/badge/C%2B%2B-20-informational)](docs/i.md)\n\n"
                 "Header-only C++20. You need a C++20 compiler (GCC 10+, Clang 13+ or MSVC 2022).\n",
}


class Case(unittest.TestCase):
    def tree(self, driver: str = DRIVER_YML, **files: str | None) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        merged = {**FILES, **{k.replace("__", "/").replace("_dot_", "."): v for k, v in files.items()}}
        (root / "driver.yml").write_text(driver, encoding="utf-8")
        for rel, text in merged.items():
            if text is None:
                continue
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return root

    def run_check(self, root: Path, standards: Path = STANDARDS, require: bool = False) -> list[cs.Finding]:
        return cs.run(root, standards, TODAY, require)

    def codes(self, findings, severity: str | None = None) -> list[str]:
        return sorted(f.code for f in findings if severity is None or f.severity == severity)

    def edit(self, **changes) -> str:
        doc = yaml.safe_load(DRIVER_YML)
        for k, v in changes.items():
            if v is None:
                doc["language"].pop(k)
            else:
                doc["language"][k] = v
        return yaml.safe_dump(doc, sort_keys=False)

    def registry(self, edit) -> Path:
        reg = copy.deepcopy(yaml.safe_load(STANDARDS.read_text()))
        edit(reg)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "standards.yml"
        p.write_text(yaml.safe_dump(reg, sort_keys=False))
        return p


class Registry(Case):
    def test_shipped_registry_is_coherent(self):
        self.assertEqual(cs.registry_problems(yaml.safe_load(STANDARDS.read_text())), [])

    def test_two_current_profiles(self):
        reg = yaml.safe_load(STANDARDS.read_text())
        reg["profiles"]["KB-CPP23"]["status"] = "current"
        self.assertTrue(any("exactly one" in p for p in cs.registry_problems(reg)))

    def test_default_must_be_current(self):
        reg = yaml.safe_load(STANDARDS.read_text())
        reg["default"] = "KB-CPP23"
        self.assertTrue(any("default" in p for p in cs.registry_problems(reg)))

    def test_retired_needs_a_date(self):
        reg = yaml.safe_load(STANDARDS.read_text())
        del reg["profiles"]["KB-CPP17"]["retired_on"]
        self.assertTrue(any("retired_on" in p for p in cs.registry_problems(reg)))

    def test_id_must_match_standard(self):
        reg = yaml.safe_load(STANDARDS.read_text())
        reg["profiles"]["KB-CPP20"]["standard"] = 23
        self.assertTrue(any("KB-CPP<standard>" in p for p in cs.registry_problems(reg)))

    def test_unlisted_compiler_key(self):
        reg = yaml.safe_load(STANDARDS.read_text())
        reg["profiles"]["KB-CPP20"]["compilers"]["icc"] = "19"
        self.assertTrue(any("icc" in p for p in cs.registry_problems(reg)))

    def test_next_must_be_preview(self):
        reg = yaml.safe_load(STANDARDS.read_text())
        reg["next"] = "KB-CPP20"
        self.assertTrue(any("next" in p for p in cs.registry_problems(reg)))


class Declaration(Case):
    def test_good_driver_passes(self):
        self.assertEqual(self.codes(self.run_check(self.tree()), "error"), [])

    def test_missing_block_is_a_note_and_an_error_when_required(self):
        root = self.tree(driver="name: abc\n")
        self.assertEqual(self.codes(self.run_check(root)), ["001"])
        self.assertEqual(self.codes(self.run_check(root), "error"), [])
        self.assertEqual(self.codes(self.run_check(root, require=True), "error"), ["001"])

    def test_no_driver_yml_declares_nothing(self):
        root = self.tree()
        (root / "driver.yml").unlink()
        self.assertEqual(self.run_check(root), [])

    def test_unknown_profile(self):
        f = self.run_check(self.tree(self.edit(profile="KB-CPP26")))
        self.assertEqual(self.codes(f, "error"), ["003"])

    def test_retired_profile(self):
        f = self.run_check(self.tree(self.edit(standard=17, profile="KB-CPP17", tested=[17])))
        self.assertIn("004", self.codes(f, "error"))

    def test_supported_until_passed_counts_as_retired(self):
        std = self.registry(lambda r: r["profiles"]["KB-CPP20"].update(status="supported", supported_until="2026-11-19"))
        std = self.registry_fix_default(std)
        f = self.run_check(self.tree(), std)
        self.assertIn("004", self.codes(f, "error"))

    def registry_fix_default(self, path: Path) -> Path:
        reg = yaml.safe_load(path.read_text())
        reg["profiles"]["KB-CPP23"]["status"] = "current"
        reg["default"] = "KB-CPP23"
        reg["next"] = None
        path.write_text(yaml.safe_dump(reg, sort_keys=False))
        return path

    def test_supported_profile_is_a_note(self):
        std = self.registry_fix_default(self.registry(lambda r: r["profiles"]["KB-CPP20"].update(status="supported")))
        f = self.run_check(self.tree(), std)
        self.assertEqual(self.codes(f), ["006"])

    def preview_tree(self) -> Path:
        readme = FILES["README.md"].replace("-20-", "-23-").replace("C++20", "C++23").replace("GCC 10", "GCC 13") \
            .replace("Clang 13", "Clang 17")
        return self.tree(self.edit(standard=23, profile="KB-CPP23", tested=[23], profile_version="1.0",
                                   compilers={"gcc": "13", "clang": "17"}),
                         **{"CMakeLists.txt": "target_compile_features(abc INTERFACE cxx_std_23)\n",
                            "tests/CMakeLists.txt": "target_compile_features(t PRIVATE cxx_std_23)\n",
                            "_config/.clang-format": "Standard: c++23\n",
                            "tools/preflight.sh": "cppcheck --std=c++23 x\n",
                            ".github/workflows/ci-repo-checks.yml": None,
                            "README.md": readme})

    def test_preview_profile_is_a_warning(self):
        std = self.registry(lambda r: r["profiles"]["KB-CPP23"].update(handbook_versions=["1.0"]))
        f = self.run_check(self.preview_tree(), std)
        self.assertEqual(self.codes(f), ["005"])
        self.assertEqual(self.codes(f, "error"), [])

    def test_standard_differs_from_profile(self):
        f = self.run_check(self.tree(self.edit(standard=23, tested=[23])))
        self.assertIn("007", self.codes(f, "error"))

    def test_unknown_profile_version(self):
        self.assertIn("008", self.codes(self.run_check(self.tree(self.edit(profile_version="9.9"))), "error"))

    def test_misra_edition(self):
        self.assertIn("009", self.codes(self.run_check(self.tree(self.edit(misra="MISRA C++:2008"))), "error"))

    def test_compiler_below_floor_and_unknown_key(self):
        f = self.run_check(self.tree(self.edit(compilers={"gcc": "9", "clang": "13", "icc": "19"})))
        self.assertEqual(self.codes(f, "error").count("010"), 2)

    def test_compiler_version_must_be_a_string(self):
        f = self.run_check(self.tree(self.edit(compilers={"gcc": 10, "clang": "13"})))
        self.assertEqual(self.codes(f, "error"), ["002"])

    def test_compare_is_numeric(self):
        f = self.run_check(self.tree(self.edit(compilers={"gcc": "10", "msvc": "19.4"})))
        self.assertIn("010", self.codes(f, "error"))
        f = self.run_check(self.tree(self.edit(compilers={"gcc": "10", "msvc": "19.100"})))
        self.assertNotIn("010", self.codes(f, "error"))

    def test_missing_and_extra_keys(self):
        self.assertEqual(self.codes(self.run_check(self.tree(self.edit(misra=None))), "error"), ["002"])
        doc = yaml.safe_load(DRIVER_YML)
        doc["language"]["colour"] = "red"
        self.assertEqual(self.codes(self.run_check(self.tree(yaml.safe_dump(doc))), "error"), ["002"])

    def test_tested_rules(self):
        self.assertIn("011", self.codes(self.run_check(self.tree(self.edit(tested=[23]))), "error"))
        self.assertIn("011", self.codes(self.run_check(self.tree(self.edit(tested=[20, 26]))), "error"))
        self.assertIn("011", self.codes(self.run_check(self.tree(self.edit(tested=[20, 17]))), "error"))
        self.assertIn("011", self.codes(self.run_check(self.tree(self.edit(tested="20"))), "error"))

    def test_effective_from(self):
        self.assertIn("012", self.codes(self.run_check(self.tree(self.edit(effective_from=datetime.date(2027, 1, 1)))),
                                        "error"))
        self.assertIn("012", self.codes(self.run_check(self.tree(self.edit(effective_from=datetime.date(2026, 1, 1)))),
                                        "error"))
        self.assertIn("002", self.codes(self.run_check(self.tree(self.edit(effective_from="soon"))), "error"))


class Files(Case):
    def assertOnly(self, findings, code: str, path: str):
        errors = [f for f in findings if f.severity == "error"]
        self.assertEqual([(f.code, f.path) for f in errors], [(code, path)])

    def test_cmake_names_another_standard(self):
        f = self.run_check(self.tree(tests__CMakeLists_dot_txt="target_compile_features(t PRIVATE cxx_std_23)\n"))
        self.assertOnly(f, "021", "tests/CMakeLists.txt")

    def test_library_target_does_not_require_the_standard(self):
        f = self.run_check(self.tree(CMakeLists_dot_txt="add_library(abc INTERFACE)\n"))
        self.assertOnly(f, "020", "CMakeLists.txt")

    def test_cmake_comment_is_not_code(self):
        root = self.tree(CMakeLists_dot_txt="# was cxx_std_17\ntarget_compile_features(abc INTERFACE cxx_std_20)\n")
        self.assertEqual(self.codes(self.run_check(root), "error"), [])

    def test_clang_format(self):
        root = self.tree()
        self.assertEqual(self.codes(self.run_check(root), "error"), [])
        (root / "_config/.clang-format").write_text("Standard: c++17\n")
        self.assertOnly(self.run_check(root), "021", "_config/.clang-format")

    def test_cplusplus_assertion(self):
        f = self.run_check(self.tree(tests__CMakeLists_dot_txt='target_compile_features(t PRIVATE cxx_std_20)\n'
                                     'static_assert(__cplusplus == 201703L);\n'))
        self.assertOnly(f, "021", "tests/CMakeLists.txt")

    def test_std_flag_must_be_tested(self):
        f = self.run_check(self.tree(tools__preflight_dot_sh="cppcheck --std=c++17 x\n"))
        self.assertOnly(f, "021", "tools/preflight.sh")
        root = self.tree(self.edit(tested=[20, 23]), tools__preflight_dot_sh="cppcheck --std=c++23 x\n")
        self.assertEqual(self.codes(self.run_check(root), "error"), [])

    def test_workflow_input(self):
        wf = 'jobs:\n  a:\n    with:\n      cppcheck_std: "c++17"\n'
        root = self.tree()
        (root / ".github/workflows/ci-repo-checks.yml").write_text(wf)
        self.assertOnly(self.run_check(root), "021", ".github/workflows/ci-repo-checks.yml")

    def test_ci_matrix_equals_tested(self):
        root = self.tree(self.edit(tested=[20, 23], compilers={"gcc": "10", "clang": "13"}))
        (root / ".github/workflows/ci-std.yml").write_text("jobs:\n  a:\n    strategy:\n      matrix:\n"
                                                           "        std: [20]\n")
        self.assertOnly(self.run_check(root), "022", ".github/workflows/ci-std.yml")
        (root / ".github/workflows/ci-std.yml").write_text("jobs:\n  a:\n    strategy:\n      matrix:\n"
                                                           "        std: [20, 23]\n")
        self.assertEqual(self.codes(self.run_check(root), "error"), [])

    def test_readme_badge_text_and_floors(self):
        base = FILES["README.md"]
        self.assertOnly(self.run_check(self.tree(README_dot_md=base.replace("-20-", "-17-"))), "031", "README.md")
        self.assertOnly(self.run_check(self.tree(README_dot_md=base.replace("a C++20 compiler", "a C++17 compiler"))),
                        "031", "README.md")
        self.assertOnly(self.run_check(self.tree(README_dot_md=base.replace("GCC 10+", "GCC 11+"))), "031", "README.md")
        f = self.run_check(self.tree(README_dot_md="# Abc\n"))
        self.assertEqual(self.codes(f), ["030"])

    def test_build_directories_and_third_party_are_skipped(self):
        root = self.tree(**{"build__CMakeLists_dot_txt": "cxx_std_17\n", "third_party__x__CMakeLists_dot_txt": "cxx_std_11\n"})
        self.assertEqual(self.codes(self.run_check(root), "error"), [])


class Command(Case):
    def test_exit_status(self):
        good, bad = self.tree(), self.tree(self.edit(profile="KB-CPP26"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cs.main(["--repo", str(good), "--today", "2026-11-20"]), 0)
            self.assertEqual(cs.main(["--repo", str(bad), "--today", "2026-11-20"]), 1)
            self.assertEqual(cs.main(["--repo", str(good), "--standards", "/nonexistent.yml"]), 2)
            self.assertEqual(cs.main(["--registry"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
