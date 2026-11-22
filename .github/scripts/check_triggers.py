#!/usr/bin/env python3
"""Fail if a workflow can be started by a privileged trigger the trigger policy does not allow.

A run started by workflow_dispatch, schedule, workflow_run, pull_request_target, issue_comment and the like runs in
the context of the default branch: it can write the Actions cache that later runs on main restore. Any step that
then runs code checked out by a computed ref could poison that cache (CodeQL
actions/cache-poisoning/poisonable-step). The workflows here therefore start only from push, pull_request,
merge_group and workflow_call; a manual run is a re-run. The one exception is release.yml, which must start from
the finished self-CI (workflow_run) and checks out only the commit that self-CI tested. docs/triggers.md has the
reasoning.

Two narrow exceptions, each a file name that may use `schedule` and `workflow_dispatch` only while it is nothing but
a call of one reusable workflow: no steps, no secrets, no `ref:` input and exactly the permissions named here.

* weekly-floor-compilers.yml, the scheduled caller of ru-floor-compilers.yml in a driver: `contents: read` and nothing
  more. The reusable ru-floor-compilers.yml, when present among the files, must have no cache or restore step, no
  checkout `ref:`, no secrets and every action pinned by a 40-hex commit SHA.
* weekly-vulnerabilities.yml, the scheduled caller of ci-vulnerabilities.yml in a library: top-level `permissions: {}`,
  and for the called job exactly `contents: write` and `issues: write`. It calls a local reusable
  (`./.github/workflows/ci-vulnerabilities.yml`) or one pinned by a 40-hex commit SHA. The reusable
  ci-vulnerabilities.yml, when present among the files, must have no cache or restore step and no `cache:` input
  other than false, no checkout `ref:`, no secrets, every action pinned by a 40-hex commit SHA, a default-branch guard
  (`github.ref` against the repository's default branch) on every job that has `contents: write`, and `cache: false`
  on a call of ci-docs.yml that refreshes the vulnerability data.

Any other scheduled workflow still fails.

Usage: check_triggers.py FILE...   (workflow files)
"""

from __future__ import annotations

import os
import re
import sys

import yaml

ALLOWED = {"push", "pull_request", "merge_group", "workflow_call"}
EXCEPTIONS = {"release.yml": {"workflow_run"}}
SHA = re.compile(r"@[0-9a-f]{40}\b")
FLOOR_CALLER = "weekly-floor-compilers.yml"
FLOOR_REUSABLE = "ru-floor-compilers.yml"
VULN_CALLER = "weekly-vulnerabilities.yml"
VULN_REUSABLE = "ci-vulnerabilities.yml"
# caller file name -> (reusable it may call, top-level permissions it may have, permissions of the called job,
#                      whether a tag such as @v1 may pin a remote reusable)
SCHEDULED_CALLERS = {
    FLOOR_CALLER: (FLOOR_REUSABLE, ({}, {"contents": "read"}), {"contents": "read"}, True),
    VULN_CALLER: (VULN_REUSABLE, ({},), {"contents": "write", "issues": "write"}, False),
}
EXCEPTION_NOTE = {
    FLOOR_CALLER: "docs/triggers.md, the floor-compiler exception",
    VULN_CALLER: "docs/triggers.md, the vulnerability-scan exception",
    FLOOR_REUSABLE: "docs/triggers.md, the floor-compiler exception",
    VULN_REUSABLE: "docs/triggers.md, the vulnerability-scan exception",
}


def triggers(doc: dict) -> set[str]:
    # PyYAML reads the key `on` as the boolean True.
    on = doc.get("on", doc.get(True))
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    if isinstance(on, dict):
        return set(on)
    return set()


def scheduled_caller_problems(doc: dict, name: str = FLOOR_CALLER) -> list[str]:
    """Why a file that uses `schedule` is not the narrow caller its name allows (empty when it is)."""
    reusable, top_perms, job_perms, tag_ok = SCHEDULED_CALLERS[name]
    out: list[str] = []
    if doc.get("permissions") not in top_perms:
        out.append("top-level permissions must be " + " or ".join(
            "{}" if not p else "{" + ", ".join(f"{k}: {v}" for k, v in p.items()) + "}" for p in top_perms) + " only")
    jobs = doc.get("jobs") or {}
    if not jobs:
        out.append("no jobs")
    for job_name, job in jobs.items():
        uses = str(job.get("uses", ""))
        local = uses == f"./.github/workflows/{reusable}"
        remote = re.search(rf"^[^./@\s][^@\s]*/{re.escape(reusable)}@(\S+)$", uses)
        if remote and not tag_ok and not re.fullmatch(r"[0-9a-f]{40}", remote.group(1)):
            out.append(f"job {job_name}: the reusable {reusable} must be local or pinned by a 40-hex commit SHA")
        elif not local and not remote:
            out.append(f"job {job_name} must only call {reusable}")
        if "steps" in job or "secrets" in job:
            out.append(f"job {job_name} has steps or secrets")
        if "ref" in (job.get("with") or {}):
            out.append(f"job {job_name} passes a ref")
        if job.get("permissions") != job_perms:
            out.append(f"job {job_name} permissions must be exactly "
                       + ", ".join(f"{k}: {v}" for k, v in job_perms.items()))
    return out


def _steps_and_calls(doc: dict):
    for job_name, job in (doc.get("jobs") or {}).items():
        for step in job.get("steps") or []:
            yield job_name, step.get("uses"), step.get("with")
        if job.get("uses"):
            yield job_name, job["uses"], job.get("with")


def floor_reusable_problems(text: str, doc: dict) -> list[str]:
    """Why the reusable floor workflow may not run from a schedule (empty when it may)."""
    out: list[str] = []
    for job_name, job in (doc.get("jobs") or {}).items():
        for step in job.get("steps") or []:
            uses = str(step.get("uses", ""))
            if uses and not uses.startswith("./") and not SHA.search(uses):
                out.append(f"job {job_name}: action {uses} is not pinned by a commit SHA")
            if re.search(r"(^|/)(cache|restore)(/|@|$)", uses.split("@")[0]) or "cache" in uses.split("@")[0]:
                out.append(f"job {job_name}: {uses} is a cache step")
            if "ref" in (step.get("with") or {}):
                out.append(f"job {job_name}: checkout with a computed ref")
    if "secrets" in text.lower().replace("secrets: {}", ""):
        out.append("mentions secrets")
    return out


def _false(value) -> bool:
    return value is False or str(value).strip().lower() == "false"


def vuln_reusable_problems(text: str, doc: dict) -> list[str]:
    """Why the reusable vulnerability scan may not run from a schedule (empty when it may)."""
    out: list[str] = []
    for job_name, uses, with_ in _steps_and_calls(doc):
        uses = str(uses or "")
        with_ = with_ or {}
        if uses and not uses.startswith("./") and not SHA.search(uses):
            out.append(f"job {job_name}: action {uses} is not pinned by a commit SHA")
        if "cache" in uses.split("@")[0] or re.search(r"(^|/)restore(/|@|$)", uses.split("@")[0]):
            out.append(f"job {job_name}: {uses} is a cache step")
        for key in with_:
            if key.startswith("cache") and not (key == "cache" and _false(with_[key])):
                out.append(f"job {job_name}: `{key}:` input (use cache: false)")
        if "ref" in with_:
            out.append(f"job {job_name}: checkout with a computed ref")
        if uses.endswith("ci-docs.yml") and not _false(with_.get("cache")) and (
                str(with_.get("refresh_vulnerabilities", "")).strip().lower() not in ("", "false")):
            out.append(f"job {job_name}: a call of ci-docs.yml that refreshes the vulnerability data must pass "
                       "cache: false")
    for job_name, job in (doc.get("jobs") or {}).items():
        perms = job.get("permissions")
        if isinstance(perms, dict) and perms.get("contents") == "write":
            cond = str(job.get("if", ""))
            if "github.ref" not in cond or "default_branch" not in cond:
                out.append(f"job {job_name} has contents: write but no default-branch guard "
                           "(if: github.ref == format('refs/heads/{0}', github.event.repository.default_branch))")
    if re.search(r"\bsecrets\s*:", text) and not re.search(r"\bsecrets\s*:\s*\{\}", text):
        out.append("mentions secrets")
    return out


def main(paths: list[str]) -> int:
    bad = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        base = os.path.basename(path)
        allowed = ALLOWED | EXCEPTIONS.get(base, set())
        if base in SCHEDULED_CALLERS:
            allowed |= {"schedule", "workflow_dispatch"}
            for why in scheduled_caller_problems(doc, base):
                print(f"::error file={path}::{why} ({EXCEPTION_NOTE[base]})")
                bad += 1
        checker = {FLOOR_REUSABLE: floor_reusable_problems, VULN_REUSABLE: vuln_reusable_problems}.get(base)
        if checker:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for why in checker(text, doc):
                print(f"::error file={path}::{why} ({EXCEPTION_NOTE[base]})")
                bad += 1
        for trig in sorted(triggers(doc) - allowed):
            print(f"::error file={path}::trigger '{trig}' is not allowed (docs/triggers.md): "
                  "start from push, pull_request or workflow_call, and re-run instead of dispatching")
            bad += 1
    print(f"checked {len(paths)} file(s): {bad} disallowed trigger(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
