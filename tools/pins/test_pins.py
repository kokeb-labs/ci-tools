#!/usr/bin/env python3
"""Unit tests of the pin hygiene checker against a fake GitHub API and scratch git repositories. PyYAML."""

from __future__ import annotations

import argparse
import base64
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pins  # noqa: E402

REPO = "org-drivers/driver-abc"
SHA = "a" * 40
TAG_OBJ = "b" * 40


def b64(text: str) -> dict:
    return {"content": base64.b64encode(text.encode()).decode()}


class FakeApi:
    def __init__(self, **overrides):
        self.responses = {
            f"/repos/{REPO}": (200, {"private": False}),
            f"/repos/{REPO}/git/ref/tags/v1.2.0": (200, {"object": {"type": "tag", "sha": TAG_OBJ}}),
            f"/repos/{REPO}/git/tags/{TAG_OBJ}": (200, {"object": {"type": "commit", "sha": SHA}}),
            f"/repos/{REPO}/commits/{SHA}/check-runs?per_page=100&check_name=CI%20gate%20/%20gate":
                (200, {"check_runs": [{"name": "CI gate / gate", "conclusion": "failure", "started_at": "1"},
                                      {"name": "CI gate / gate", "conclusion": "success", "started_at": "2"}]}),
            f"/repos/{REPO}/contents/driver.yml?ref={SHA}":
                (200, b64("name: abc\nversion: 1.2.0\nmcus: [esp32]\nperipheral: rmt\nkb_core_min: 0.3.0\n")),
            f"/repos/{REPO}/contents/.kokeb/handbook.yml?ref={SHA}": (200, b64("level: high\n")),
        }
        self.responses.update(overrides)

    def get(self, path):
        return self.responses.get(path, (404, None))


def make_repo(d: str, lock_extra: str = "", gitmodules_extra: str = "", gitlink: str = SHA,
              tag: str = "v1.2.0", kind: str = "release") -> None:
    def git(*a):
        subprocess.run(["git", "-C", d, *a], check=True, capture_output=True)
    git("init", "-q")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    os.makedirs(os.path.join(d, "drivers"))
    with open(os.path.join(d, ".gitmodules"), "w") as fh:
        fh.write(f'[submodule "drivers/driver-abc"]\n\tpath = drivers/driver-abc\n'
                 f"\turl = https://github.com/{REPO}.git\n{gitmodules_extra}")
    with open(os.path.join(d, "drivers", "lock.yml"), "w") as fh:
        fh.write(f"drivers:\n  - name: abc\n    repo: {REPO}\n    tag: {tag}\n    commit: {SHA}\n    kind: {kind}\n"
                 + lock_extra)
    with open(os.path.join(d, "gates.cmake"), "w") as fh:
        fh.write('set(GATES\n  "abc:ESP32:rmt"  # comment "x:Y:z"\n)\n')
    with open(os.path.join(d, "version.cmake"), "w") as fh:
        fh.write("set(P_VERSION_MAJOR 0)\nset(P_VERSION_MINOR 4)\nset(P_VERSION_PATCH 1)\n")
    git("add", "-A")
    git("update-index", "--add", "--cacheinfo", f"160000,{gitlink},drivers/driver-abc")
    git("commit", "-q", "-m", "x")


def args(d: str, **kw) -> argparse.Namespace:
    base = dict(lock="drivers/lock.yml", root=d, gates="gates.cmake", version_file="version.cmake",
                required_check="CI gate / gate", tag_pattern=r"^v[0-9]+\.[0-9]+\.[0-9]+(-rc\.[0-9]+)?$",
                forbid_branch_entries="true", url_pattern=r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?(\.git)?$",
                handbook_levels="high safety", private_repos="false", release_lock="", ref="refs/heads/main")
    base.update(kw)
    return argparse.Namespace(**base)


class Pins(unittest.TestCase):
    def rules(self, api=None, repo_kw=None, **kw) -> list[str]:
        with tempfile.TemporaryDirectory() as d:
            make_repo(d, **(repo_kw or {}))
            findings, _, self.warnings = pins.check(args(d, **kw), api or FakeApi())
        return sorted(f["rule"] for f in findings)

    def test_clean_pin(self):
        self.assertEqual(self.rules(), [])

    def test_gitlink_and_lock_disagree(self):
        self.assertEqual(self.rules(repo_kw={"gitlink": "c" * 40}), ["PIN-002"])

    def test_extra_lock_entry_and_branch(self):
        extra = f"  - name: zzz\n    repo: org-drivers/driver-zzz\n    tag: v1.0.0\n    commit: {SHA}\n    kind: release\n"
        got = self.rules(repo_kw={"lock_extra": extra, "gitmodules_extra": "\tbranch = main\n"})
        self.assertIn("PIN-001", got)
        self.assertIn("PIN-011", got)

    def test_moved_tag_and_failed_gate(self):
        api = FakeApi(**{f"/repos/{REPO}/git/tags/{TAG_OBJ}": (200, {"object": {"type": "commit", "sha": "d" * 40}}),
                         f"/repos/{REPO}/commits/{SHA}/check-runs?per_page=100&check_name=CI%20gate%20/%20gate":
                             (200, {"check_runs": [{"name": "CI gate / gate", "conclusion": "failure"}]})})
        self.assertEqual(self.rules(api), ["PIN-003", "PIN-005"])

    def test_rc_tag_with_release_kind_and_bad_tag(self):
        self.assertIn("PIN-004", self.rules(repo_kw={"kind": "rc"}))
        self.assertIn("PIN-004", self.rules(repo_kw={"tag": "main"}))

    def test_driver_yml_mismatches(self):
        api = FakeApi(**{f"/repos/{REPO}/contents/driver.yml?ref={SHA}":
                         (200, b64("name: abd\nversion: 1.1.0\nmcus: [stm32]\nperipheral: tim\nkb_core_min: 0.5.0\n"))})
        self.assertEqual(self.rules(api), ["PIN-006", "PIN-006", "PIN-007", "PIN-007", "PIN-008"])

    def test_handbook_level_and_private(self):
        api = FakeApi(**{f"/repos/{REPO}/contents/.kokeb/handbook.yml?ref={SHA}": (200, b64("level: basic\n")),
                         f"/repos/{REPO}": (200, {"private": True})})
        self.assertEqual(self.rules(api), ["PIN-009", "PIN-013"])
        self.assertEqual(self.rules(api, private_repos="true"), ["PIN-009"])

    def test_unreadable_repository(self):
        self.assertEqual(self.rules(FakeApi(**{f"/repos/{REPO}": (404, None)})), ["PIN-013"])

    def test_url_pattern(self):
        self.assertEqual(self.rules(url_pattern=r"^https://example\.com/"), ["PIN-010"])

    def test_rc_in_final_release_warns(self):
        api = FakeApi(**{f"/repos/{REPO}/git/ref/tags/v1.2.0-rc.1": (200, {"object": {"type": "commit", "sha": SHA}})})
        self.assertEqual(self.rules(api, repo_kw={"tag": "v1.2.0-rc.1", "kind": "rc"}, ref="refs/tags/v0.4.1"), [])
        self.assertTrue(any("release candidate" in w for w in self.warnings))

    def test_parsers(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "v.txt")
            with open(p, "w") as fh:
                fh.write("# version\n1.4.2\n")
            self.assertEqual(pins.parse_version(p), "1.4.2")
        self.assertEqual(pins.repo_of_url("git@github.com:a/b.git"), "a/b")
        self.assertEqual(pins.repo_of_url("https://github.com/a/b"), "a/b")
        self.assertEqual(pins.repo_of_url("https://gitlab.com/a/b"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
