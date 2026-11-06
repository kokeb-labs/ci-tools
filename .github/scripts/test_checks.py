#!/usr/bin/env python3
"""Tests for the self-CI check scripts. Run: python .github/scripts/test_checks.py"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script: str, *args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(HERE, script), *args],
                          cwd=cwd, capture_output=True, text=True)


README = textwrap.dedent("""\
    <!-- permissions-table:start -->
    | Workflow | Caller must grant |
    |---|---|
    | `ru-x.yml` | {row} |
    <!-- permissions-table:end -->
    """)

WORKFLOW = textwrap.dedent("""\
    on: {{ workflow_call: {{}} }}
    {top}jobs:
      a:
        runs-on: ubuntu-latest
        {perms}
        steps: [{{ run: "true" }}]
    """)


class PermissionsContract(unittest.TestCase):
    def check(self, row: str, perms: str, top: str = "permissions: {}\n", caller: str | None = None) -> subprocess.CompletedProcess:
        d = tempfile.mkdtemp()
        wf = os.path.join(d, "wf")
        os.makedirs(wf)
        with open(os.path.join(d, "README.md"), "w") as fh:
            fh.write(README.format(row=row))
        with open(os.path.join(wf, "ru-x.yml"), "w") as fh:
            fh.write(WORKFLOW.format(top=top, perms=perms))
        if caller is not None:
            with open(os.path.join(wf, "ci-x.yml"), "w") as fh:
                fh.write(caller)
        return run("check_permissions.py", "--readme", os.path.join(d, "README.md"), "--workflows", wf)

    def test_match_passes(self):
        r = self.check("`contents: read`", "permissions: { contents: read }")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_job_asks_more_than_documented_fails(self):
        r = self.check("`contents: read`", "permissions: { contents: read, pull-requests: write }")
        self.assertEqual(r.returncode, 1)
        self.assertIn("startup_failure", r.stdout)

    def test_documented_more_than_needed_fails(self):
        r = self.check("`contents: write`", "permissions: { contents: read }")
        self.assertEqual(r.returncode, 1)
        self.assertIn("shrink the row", r.stdout)

    def test_missing_job_permissions_fails(self):
        r = self.check("`contents: read`", "")
        self.assertEqual(r.returncode, 1)

    def test_top_level_permissions_fails(self):
        r = self.check("`contents: read`", "permissions: { contents: read }", top="permissions: { contents: read }\n")
        self.assertEqual(r.returncode, 1)

    def test_missing_top_level_permissions_fails(self):
        r = self.check("`contents: read`", "permissions: { contents: read }", top="")
        self.assertEqual(r.returncode, 1)
        self.assertIn("must be `{}`", r.stdout)

    def test_any_workflow_call_file_is_checked(self):
        d = tempfile.mkdtemp()
        wf = os.path.join(d, "wf")
        os.makedirs(wf)
        with open(os.path.join(d, "README.md"), "w") as fh:
            fh.write(README.format(row="`contents: read`").replace("ru-x.yml", "dco.yml"))
        with open(os.path.join(wf, "dco.yml"), "w") as fh:
            fh.write(WORKFLOW.format(top="permissions: {}\n", perms="permissions: { contents: write }"))
        r = run("check_permissions.py", "--readme", os.path.join(d, "README.md"), "--workflows", wf)
        self.assertEqual(r.returncode, 1)
        self.assertIn("dco.yml", r.stdout)

    def test_empty_permissions_is_none(self):
        r = self.check("none", "permissions: {}")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_local_caller_granting_too_little_fails(self):
        caller = "on: push\npermissions: { contents: read }\njobs:\n  c:\n    uses: ./.github/workflows/ru-x.yml\n"
        r = self.check("`contents: write`", "permissions: { contents: write }", caller=caller)
        self.assertEqual(r.returncode, 1)
        self.assertIn("grants", r.stdout)


class RunTails(unittest.TestCase):
    def check(self, script: str) -> subprocess.CompletedProcess:
        d = tempfile.mkdtemp()
        p = os.path.join(d, "w.yml")
        with open(p, "w") as fh:
            fh.write("jobs:\n  a:\n    steps:\n      - run: |\n" + textwrap.indent(script, " " * 10))
        return run("check_run_tails.py", p)

    def test_bare_and_list_at_end_fails(self):
        self.assertEqual(self.check('echo a\n[ -n "$X" ] && echo set\n').returncode, 1)

    def test_and_list_with_or_passes(self):
        self.assertEqual(self.check('[ -n "$X" ] && echo set || true\n').returncode, 0)

    def test_and_list_not_last_passes(self):
        self.assertEqual(self.check('[ -n "$X" ] && echo set\necho done\n').returncode, 0)

    def test_if_block_passes(self):
        self.assertEqual(self.check('if [ -n "$X" ]; then\n  echo set\nfi\n').returncode, 0)


def gate_script() -> str:
    import yaml
    path = os.path.join(HERE, "..", "workflows", "ru-ci-gate.yml")
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    for step in doc["jobs"]["gate"]["steps"]:
        if step.get("name") == "Evaluate needed jobs":
            return step["run"]
    raise AssertionError("gate step not found")


CALLER = textwrap.dedent("""\
    on: pull_request
    jobs:
      build: {runs-on: ubuntu-latest, steps: [{run: "true"}]}
      docs: {runs-on: ubuntu-latest, steps: [{run: "true"}]}
      ci-gate:
        needs: [build, docs]
        if: always()
        uses: kokeb-labs/ci-tools/.github/workflows/ru-ci-gate.yml@v1
    """)


class CiGate(unittest.TestCase):
    def gate(self, needs: dict, allow: str = "", caller: str | None = None) -> subprocess.CompletedProcess:
        import json
        d = tempfile.mkdtemp()
        env = {**os.environ, "NEEDS_JSON": json.dumps(needs), "ALLOW_SKIPPED": allow,
               "VERIFY_NEEDS": "true" if caller is not None else "false",
               "WORKFLOW_REF": "o/r/.github/workflows/ci.yml@refs/pull/1/merge",
               "GITHUB_REPOSITORY": "o/r", "GITHUB_STEP_SUMMARY": os.path.join(d, "summary.md")}
        if caller is not None:
            bindir = os.path.join(d, "bin")
            os.makedirs(bindir)
            with open(os.path.join(d, "caller.yml"), "w") as fh:
                fh.write(caller)
            with open(os.path.join(bindir, "gh"), "w") as fh:
                fh.write(f"#!/bin/sh\ncat '{os.path.join(d, 'caller.yml')}'\n")
            os.chmod(os.path.join(bindir, "gh"), 0o755)
            env["PATH"] = bindir + os.pathsep + env["PATH"]
        return subprocess.run(["bash", "-e", "-c", gate_script()], env=env, capture_output=True, text=True)

    def test_all_success_passes(self):
        r = self.gate({"build": {"result": "success"}, "docs": {"result": "success"}})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_failure_fails(self):
        r = self.gate({"build": {"result": "failure"}, "docs": {"result": "success"}})
        self.assertEqual(r.returncode, 1)
        self.assertIn("'build' finished with 'failure'", r.stdout)

    def test_cancelled_fails(self):
        self.assertEqual(self.gate({"build": {"result": "cancelled"}}).returncode, 1)

    def test_skip_not_allowed_fails(self):
        r = self.gate({"build": {"result": "success"}, "docs": {"result": "skipped"}})
        self.assertEqual(r.returncode, 1)

    def test_allowed_skip_passes(self):
        r = self.gate({"build": {"result": "success"}, "docs": {"result": "skipped"}}, allow="docs")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_unknown_allowed_job_fails(self):
        r = self.gate({"build": {"result": "success"}}, allow="dcos")
        self.assertEqual(r.returncode, 1)

    def test_empty_needs_fails(self):
        self.assertEqual(self.gate({}).returncode, 1)

    def test_caller_complete_passes(self):
        r = self.gate({"build": {"result": "success"}, "docs": {"result": "success"}}, caller=CALLER)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_caller_missing_need_fails(self):
        caller = CALLER.replace("needs: [build, docs]", "needs: [build]")
        r = self.gate({"build": {"result": "success"}}, caller=caller)
        self.assertEqual(r.returncode, 1)
        self.assertIn("does not list these jobs in needs: docs", r.stdout)

    def test_caller_without_always_fails(self):
        caller = CALLER.replace("    if: always()\n", "")
        r = self.gate({"build": {"result": "success"}, "docs": {"result": "success"}}, caller=caller)
        self.assertEqual(r.returncode, 1)
        self.assertIn("always()", r.stdout)



def _workflow(name: str) -> dict:
    import yaml
    with open(os.path.join(HERE, "..", "workflows", name), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


DCO_HARNESS = r"""
const fs = require("fs");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const out = { failed: null, errors: [], notices: [], info: [] };
const summary = { addHeading() { return this; }, addRaw() { return this; }, async write() { return this; } };
const core = {
  setFailed: (m) => { out.failed = m; }, error: (m) => out.errors.push(m),
  notice: (m) => out.notices.push(m), info: (m) => out.info.push(m), summary,
};
const github = { rest: { pulls: { listCommits: "listCommits" } }, paginate: async () => input.commits };
const context = { payload: input.payload, eventName: input.event, repo: { owner: "o", repo: "r" } };
Object.assign(process.env, input.env);
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
new AsyncFunction("require", "github", "context", "core", input.script)(require, github, context, core)
  .then(() => console.log(JSON.stringify(out)))
  .catch((e) => { console.error(e); process.exit(2); });
"""


def _commit(sha: str, message: str, name: str = "Ada Lovelace", email: str = "ada@example.org",
            login: str = "ada", user_type: str = "User", parents: int = 1) -> dict:
    return {"sha": sha * 40, "parents": [{}] * parents, "author": {"login": login, "type": user_type},
            "commit": {"message": message, "author": {"name": name, "email": email}}}


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class Dco(unittest.TestCase):
    def run_dco(self, commits, event="pull_request", allow_bots="true", skip_merges="true", count=None):
        import json
        step = _workflow("dco.yml")["jobs"]["dco"]["steps"][0]
        payload = {"pull_request": {"number": 1, "commits": len(commits) if count is None else count}}
        data = {"script": step["with"]["script"], "commits": commits, "event": event,
                "payload": payload if event.startswith("pull_request") else {},
                "env": {"ALLOW_BOTS": allow_bots, "SKIP_MERGE_COMMITS": skip_merges}}
        r = subprocess.run(["node", "-e", DCO_HARNESS], input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    SIGNED = "Fix it\n\nSigned-off-by: Ada Lovelace <ada@example.org>\n"

    def test_signed_off_by_author_passes(self):
        self.assertIsNone(self.run_dco([_commit("a", self.SIGNED)])["failed"])

    def test_case_and_spacing_do_not_matter(self):
        msg = "Fix\n\nsigned-off-by:   ada  lovelace <ADA@Example.org>\n"
        self.assertIsNone(self.run_dco([_commit("a", msg)])["failed"])

    def test_missing_sign_off_fails(self):
        out = self.run_dco([_commit("a", self.SIGNED), _commit("b", "Fix it\n")])
        self.assertIn("1 of 2", out["failed"])
        self.assertIn("no Signed-off-by line", out["errors"][0])

    def test_sign_off_by_someone_else_fails(self):
        msg = "Fix\n\nSigned-off-by: Bob <bob@example.org>\n"
        out = self.run_dco([_commit("a", msg)])
        self.assertIsNotNone(out["failed"])
        self.assertIn("author is ada lovelace <ada@example.org>", out["errors"][0])

    def test_other_email_fails(self):
        msg = "Fix\n\nSigned-off-by: Ada Lovelace <ada@other.example>\n"
        self.assertIsNotNone(self.run_dco([_commit("a", msg)])["failed"])

    def test_sign_off_in_the_body_text_does_not_count(self):
        msg = "Fix\n\nPlease add Signed-off-by: Ada Lovelace <ada@example.org> next time\n"
        self.assertIsNotNone(self.run_dco([_commit("a", msg)])["failed"])

    def test_bot_skipped_unless_disabled(self):
        bot = _commit("a", "Bump\n", name="dependabot[bot]", email="x@users.noreply.github.com",
                      login="dependabot[bot]", user_type="Bot")
        self.assertIsNone(self.run_dco([bot])["failed"])
        self.assertIsNotNone(self.run_dco([bot], allow_bots="false")["failed"])

    def test_merge_commit_skipped_unless_disabled(self):
        merge = _commit("a", "Merge main\n", parents=2)
        self.assertIsNone(self.run_dco([merge])["failed"])
        self.assertIsNotNone(self.run_dco([merge], skip_merges="false")["failed"])

    def test_no_pull_request_passes_with_notice(self):
        out = self.run_dco([], event="push")
        self.assertIsNone(out["failed"])
        self.assertTrue(out["notices"])

    def test_truncated_commit_list_fails(self):
        self.assertIn("250", self.run_dco([_commit("a", self.SIGNED)], count=300)["failed"])


MIT = """MIT License

Copyright (c) 2026 The Kokeb Labs Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class OrgStandard(unittest.TestCase):
    def check(self, files: dict[str, str], extra: str = "") -> subprocess.CompletedProcess:
        step = _workflow("org-standard-check.yml")["jobs"]["check"]["steps"][1]
        d = tempfile.mkdtemp()
        for name, body in files.items():
            os.makedirs(os.path.dirname(os.path.join(d, name)) or d, exist_ok=True)
            with open(os.path.join(d, name), "w") as fh:
                fh.write(body)
        env = {**os.environ, "EXTRA_FILES": extra, "GITHUB_STEP_SUMMARY": os.path.join(d, "summary.md")}
        return subprocess.run(["bash", "-e", "-c", step["run"]], cwd=d, env=env, capture_output=True, text=True)

    def standard(self, **override) -> dict[str, str]:
        files = {"README.md": "# x\n", "LICENSE": MIT, "CHANGELOG.md": "# Changelog\n", ".github/CODEOWNERS": "* @o\n"}
        files.update(override)
        return {k: v for k, v in files.items() if v is not None}

    def test_complete_repository_passes(self):
        r = self.check(self.standard())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_rewrapped_mit_passes(self):
        r = self.check(self.standard(LICENSE=" ".join(MIT.split())))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_missing_codeowners_fails(self):
        r = self.check(self.standard(**{".github/CODEOWNERS": None}))
        self.assertEqual(r.returncode, 1)
        self.assertIn(".github/CODEOWNERS is missing", r.stdout)

    def test_empty_changelog_fails(self):
        self.assertEqual(self.check(self.standard(**{"CHANGELOG.md": ""})).returncode, 1)

    def test_other_licence_fails(self):
        other = "Apache License\nVersion 2.0, January 2004\nCopyright (c) 2026 Someone\n"
        r = self.check(self.standard(LICENSE=other))
        self.assertEqual(r.returncode, 1)
        self.assertIn("not the MIT licence", r.stdout)

    def test_mit_without_copyright_line_fails(self):
        r = self.check(self.standard(LICENSE=MIT.replace("Copyright (c) 2026 The Kokeb Labs Authors\n", "")))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no 'Copyright", r.stdout)

    def test_extra_files_are_required(self):
        self.assertEqual(self.check(self.standard(), extra="SECURITY.md").returncode, 1)
        self.assertEqual(self.check(self.standard(**{"SECURITY.md": "x\n"}), extra="SECURITY.md").returncode, 0)


class ContractDiff(unittest.TestCase):
    BASE = textwrap.dedent("""\
        on:
          workflow_call:
            inputs:
              keep: {type: string, required: false, default: ""}
              gone: {type: boolean, required: false, default: false}
        jobs:
          a: {runs-on: ubuntu-latest, permissions: {contents: read}, steps: [{run: "true"}]}
        """)

    def check(self, new: str, changelog: str = "", base_changelog: str = "") -> subprocess.CompletedProcess:
        d = tempfile.mkdtemp()
        wf = os.path.join(d, ".github", "workflows")
        os.makedirs(wf)
        git = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True)
        git("init", "-q")
        with open(os.path.join(wf, "ru-x.yml"), "w") as fh:
            fh.write(self.BASE)
        with open(os.path.join(d, "CHANGELOG.md"), "w") as fh:
            fh.write(base_changelog)
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        with open(os.path.join(wf, "ru-x.yml"), "w") as fh:
            fh.write(new)
        with open(os.path.join(d, "CHANGELOG.md"), "w") as fh:
            fh.write(changelog)
        return run("check_contract.py", "--base-ref", "HEAD", cwd=d)

    def test_unchanged_passes(self):
        self.assertEqual(self.check(self.BASE).returncode, 0)

    def test_new_optional_input_passes(self):
        new = self.BASE.replace("      gone:", "      extra: {type: string, required: false, default: x}\n      gone:")
        self.assertEqual(self.check(new).returncode, 0)

    def test_removed_input_fails(self):
        new = "\n".join(l for l in self.BASE.splitlines() if "gone" not in l) + "\n"
        r = self.check(new)
        self.assertEqual(r.returncode, 1)
        self.assertIn("input `gone` removed", r.stdout)

    def test_widened_permissions_fail(self):
        r = self.check(self.BASE.replace("{contents: read}", "{contents: write}"))
        self.assertEqual(r.returncode, 1)

    def test_breaking_recorded_in_changelog_passes(self):
        log = "# Changelog\n\n## [Unreleased]\n\n### Breaking\n\n- removed gone\n\n## [1.0.0]\n"
        new = "\n".join(l for l in self.BASE.splitlines() if "gone" not in l) + "\n"
        self.assertEqual(self.check(new, log).returncode, 0)

    def test_breaking_in_the_new_major_section_passes(self):
        log = "# Changelog\n\n## [Unreleased]\n\n## [2.0.0] - 2026-11-06\n\n### Breaking\n\n- removed gone\n\n## [1.0.0]\n"
        new = "\n".join(l for l in self.BASE.splitlines() if "gone" not in l) + "\n"
        self.assertEqual(self.check(new, log, "# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n").returncode, 0)

    def test_breaking_under_released_section_does_not_count(self):
        log = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n## [1.0.0]\n\n### Breaking\n"
        new = "\n".join(l for l in self.BASE.splitlines() if "gone" not in l) + "\n"
        self.assertEqual(self.check(new, log, log).returncode, 1)


class ChangelogTest(unittest.TestCase):
    """changelog.py: the release a pull request asks for, and the bump helper."""

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import changelog as cl  # noqa: E402

    BASE = "# Changelog\n\n## [Unreleased]\n\n## [1.2.3] - 2026-01-01\n\n### Fixed\n\n- old\n"

    def chk(self, text, base):
        return self.cl.check(text, base, is_tagged=lambda v: False)

    def test_already_tagged_version_is_not_a_new_release(self):
        text = self.log("## [1.2.9] - 2026-11-06\n\n- x\n\n", "- pending\n\n")
        self.assertEqual(self.cl.check(text, self.BASE, is_tagged=lambda v: v == "1.2.9"), [])

    def log(self, new_section: str, unreleased: str = "") -> str:
        return f"# Changelog\n\n## [Unreleased]\n\n{unreleased}{new_section}## [1.2.3] - 2026-01-01\n\n### Fixed\n\n- old\n"

    def test_no_new_section_is_fine(self):
        self.assertEqual(self.chk(self.log("", "### Added\n\n- pending\n\n"), self.BASE), [])

    def test_next_patch_minor_major_pass(self):
        for v in ("1.2.4", "1.3.0", "2.0.0"):
            self.assertEqual(self.chk(self.log(f"## [{v}] - 2026-11-06\n\n### Fixed\n\n- x\n\n"), self.BASE), [], v)

    def test_skipped_version_fails(self):
        errs = self.chk(self.log("## [1.2.5] - 2026-11-06\n\n- x\n\n"), self.BASE)
        self.assertTrue(any("one step" in e for e in errs), errs)

    def test_breaking_needs_major(self):
        errs = self.chk(self.log("## [1.3.0] - 2026-11-06\n\n### Breaking\n\n- x\n\n"), self.BASE)
        self.assertTrue(any("major" in e for e in errs), errs)

    def test_needs_date_entries_and_empty_unreleased(self):
        errs = self.chk(self.log("## [1.2.4]\n\n### Fixed\n\n", "- left behind\n\n"), self.BASE)
        self.assertEqual(len(errs), 3, errs)

    def test_bump_moves_unreleased(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "CHANGELOG.md"
            p.write_text(self.log("", "### Fixed\n\n- new fix\n\n"))
            self.assertEqual(self.cl.cmd_bump(str(p), "patch", "2026-11-06"), 0)
            text = p.read_text()
            self.assertIn("## [Unreleased]\n\n## [1.2.4] - 2026-11-06\n\n### Fixed\n\n- new fix\n\n## [1.2.3]", text)
            self.assertEqual(self.chk(text, self.BASE), [])

    def test_release_notes_are_the_top_section(self):
        top = self.cl.top_version(self.log("## [1.2.4] - 2026-11-06\n\n### Fixed\n\n- x\n\n"))
        self.assertEqual(top[0], "1.2.4")
        self.assertIn("- x", top[2])


if __name__ == "__main__":
    unittest.main()
