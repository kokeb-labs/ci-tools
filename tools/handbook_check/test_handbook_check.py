#!/usr/bin/env python3
"""Tests for handbook_check.py: each check on a small repository built in a temporary folder."""

from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import handbook_check as hc  # noqa: E402

RULES = json.loads((HERE / "rules.json").read_text())["rules"]
TODAY = datetime.date(2026, 11, 7)
LATER = datetime.date(2027, 6, 1)  # after every enforce_from date in the snapshot

GOOD = {
    ".kokeb/handbook.yml": '---\nhandbook: "1.0"\nkind: driver\nlevel: high\n',
    "driver.yml": "---\nname: abc\nversion: 0.1.0\nbus: [spi]\nmcus: [any]\nperipheral: null\nkb_core_min: null\n",
    "CMakeLists.txt": "add_library(abc INTERFACE)\ntarget_compile_features(abc INTERFACE cxx_std_20)\n",
    "cmake/abc_build_settings.cmake": textwrap.dedent("""\
        set(ABC_TARGET_NAME "abc")
        set(ABC_VERSION_MAJOR 0)
        set(ABC_VERSION_MINOR 1)
        set(ABC_VERSION_PATCH 0)
        """),
    "inc/abc.hpp": textwrap.dedent("""\
        #pragma once
        #include <array>
        #include <cstdint>
        // A comment that says new, delete, throw and virtual is fine.
        namespace abc {
        class Abc {
         public:
          Abc(const Abc&) = delete;
          Abc& operator=(const Abc&) = delete;
          static constexpr std::uint32_t kBig = 1'000'000;
          const char* Name() const noexcept { return "new delete throw"; }
        };
        }  // namespace abc
        """),
    "README.md": "# abc\n", "LICENSE": "MIT\n", "CHANGELOG.md": "# Changelog\n",
}


def make(files: dict[str, str]) -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    return root


def run(files: dict[str, str], today=LATER) -> hc.Repo:
    root = make(files)
    repo = hc.Repo(root, RULES, today)
    repo.load_declaration()
    tracked = repo.tracked()
    repo.check_root_layout(tracked)
    repo.check_driver_manifest()
    repo.check_cmake(tracked)
    repo.check_sources(tracked)
    repo.check_tracked(tracked)
    repo.settle()
    return repo


def errors(repo: hc.Repo) -> list[tuple[str, str]]:
    return [(f.rule, f.message) for f in repo.findings if f.severity == "error"]


class HandbookCheckTest(unittest.TestCase):
    def test_good_driver_is_clean(self):
        self.assertEqual([(f.rule, f.message) for f in run(GOOD).findings], [])

    def test_heap_exceptions_rtti_virtual_in_code(self):
        bad = dict(GOOD)
        bad["src/abc.ipp"] = textwrap.dedent("""\
            void F() {
              int* p = new int(1);
              delete p;
              void* q = malloc(4);
              try { throw 1; } catch (...) {}
              auto& t = typeid(int);
            }
            struct B { virtual void G(); };
            """)
        rules = sorted({r for r, _ in errors(run(bad))})
        self.assertEqual(rules, ["KB-ARCH-011", "KB-CPP-002", "KB-CPP-003"])
        found = errors(run(bad))
        self.assertEqual(sum(r == "KB-CPP-003" for r, _ in found), 3)  # new, delete, malloc

    def test_placement_new_and_deleted_functions_are_fine(self):
        ok = dict(GOOD)
        ok["inc/abc.hpp"] = GOOD["inc/abc.hpp"] + "void H(void* b) = delete;\n"
        self.assertEqual(errors(run(ok)), [])

    def test_driver_includes_only_the_subset(self):
        bad = dict(GOOD)
        bad["inc/abc.hpp"] = GOOD["inc/abc.hpp"].replace("#include <array>", "#include <vector>\n#include <cstdio>")
        msgs = [m for r, m in errors(run(bad)) if r == "KB-CPP-012"]
        self.assertEqual(len(msgs), 2)

    def test_cmake_glob_and_missing_cxx20(self):
        bad = dict(GOOD)
        bad["CMakeLists.txt"] = "file(GLOB SRC src/*.cpp)\nadd_library(abc ${SRC})\n"
        rules = sorted(r for r, _ in errors(run(bad)))
        self.assertIn("KB-BLD-002", rules)
        self.assertIn("KB-CPP-001", rules)

    def test_glob_in_tests_is_allowed(self):
        ok = dict(GOOD)
        ok["tests/CMakeLists.txt"] = "file(GLOB T test_*.cpp)\n"
        self.assertEqual(errors(run(ok)), [])

    def test_manifest_must_match_build_settings(self):
        bad = dict(GOOD)
        bad["driver.yml"] = GOOD["driver.yml"].replace("0.1.0", "0.2.0").replace("[spi]", "[warp]")
        msgs = [m for r, m in errors(run(bad)) if r == "KB-REPO-018"]
        self.assertEqual(len(msgs), 2)

    def test_root_layout(self):
        bad = dict(GOOD)
        bad[".clang-format.bak"] = "x"
        bad["scripts/a.sh"] = "x"
        self.assertEqual(len([r for r, _ in errors(run(bad)) if r == "KB-REPO-005"]), 2)

    def test_untracked_root_entries_are_ignored(self):
        root = make(GOOD)
        (root / "build").mkdir()
        (root / "build" / "x.o").write_text("")
        repo = hc.Repo(root, RULES, LATER)
        repo.load_declaration()
        repo.check_root_layout(repo.tracked())
        self.assertEqual(repo.findings, [])

    def test_tracked_sdkconfig_and_pdf(self):
        bad = dict(GOOD)
        bad["examples/esp32/sdkconfig"] = "CONFIG_X=y\n"
        bad["docs/ds.pdf"] = "%PDF"
        rules = sorted(r for r, _ in errors(run(bad)))
        self.assertEqual(rules, ["KB-DOC-035", "KB-REPO-016"])

    def test_proposed_rule_warns_before_its_date(self):
        bad = dict(GOOD)
        bad["CMakeLists.txt"] = GOOD["CMakeLists.txt"] + "file(GLOB X src/*.cpp)\n"
        repo = run(bad, today=TODAY)
        glob = [f for f in repo.findings if f.rule == "KB-BLD-002"]
        self.assertEqual([f.severity for f in glob], ["warning"])

    def test_waiver_turns_an_error_into_a_notice_and_expires(self):
        bad = dict(GOOD)
        bad["CMakeLists.txt"] = GOOD["CMakeLists.txt"] + "file(GLOB X src/*.cpp)\n"
        waived = dict(bad)
        waived[".kokeb/handbook.yml"] = GOOD[".kokeb/handbook.yml"] + textwrap.dedent("""\
            waivers:
              - rule: KB-BLD-002
                reason: sources move to an explicit list in #12
                approved_by: "@N3b3x"
                until: 2027-12-31
            """)
        repo = run(waived)
        self.assertEqual([f.severity for f in repo.findings if f.rule == "KB-BLD-002"], ["notice"])
        expired = dict(waived)
        expired[".kokeb/handbook.yml"] = waived[".kokeb/handbook.yml"].replace("2027-12-31", "2027-01-01")
        rules = sorted(r for r, _ in errors(run(expired)))
        self.assertIn("KB-REPO-003", rules)
        self.assertIn("KB-BLD-002", rules)

    def test_declaration_is_checked(self):
        bad = dict(GOOD)
        bad[".kokeb/handbook.yml"] = '---\nhandbook: latest\nkind: gadget\nlevel: extreme\ncolour: red\n'
        msgs = [m for r, m in errors(run(bad)) if r == "KB-REPO-002"]
        self.assertEqual(len(msgs), 4)

    def test_rules_outside_the_level_do_not_apply(self):
        repo = hc.Repo(pathlib.Path("."), RULES, LATER)
        repo.kind, repo.level = "driver", "standard"
        self.assertFalse(repo.applies("KB-TST-004"))  # coverage floor: high and above
        repo.level = "high"
        self.assertTrue(repo.applies("KB-TST-004"))

    def test_stripping_keeps_lines_and_ignores_literals(self):
        src = 'a = "x // not a comment";  // new\n/* delete\n throw */ b = \'"\';\nc = 1\'000;\n'
        out = hc.strip_comments_and_strings(src)
        self.assertEqual(out.count("\n"), src.count("\n"))
        for word in ("new", "delete", "throw"):
            self.assertNotIn(word, out)
        self.assertIn("c = 1'000;", out)


if __name__ == "__main__":
    unittest.main()
