#!/usr/bin/env python3
"""Fail if a workflow can be started by a privileged trigger the trigger policy does not allow.

A run started by workflow_dispatch, schedule, workflow_run, pull_request_target, issue_comment and the like runs in
the context of the default branch: it can write the Actions cache that later runs on main restore. Any step that
then runs code checked out by a computed ref could poison that cache (CodeQL
actions/cache-poisoning/poisonable-step). The workflows here therefore start only from push, pull_request,
merge_group and workflow_call; a manual run is a re-run. The one exception is release.yml, which must start from
the finished self-CI (workflow_run) and checks out only the commit that self-CI tested. docs/triggers.md has the
reasoning.

One narrow exception: a file named weekly-floor-compilers.yml (the scheduled caller of ru-floor-compilers.yml in a
driver) may use `schedule` and `workflow_dispatch`, and only while it is nothing but that call: no steps, no secrets,
`contents: read` and nothing more, and the reusable it calls. The reusable ru-floor-compilers.yml, when present among
the files, must have no cache or restore step, no checkout `ref:`, no secrets and every action pinned by a 40-hex
commit SHA. Any other scheduled workflow still fails.

Usage: check_triggers.py FILE...   (workflow files)
"""

from __future__ import annotations

import os
import re
import sys

import yaml

ALLOWED = {"push", "pull_request", "merge_group", "workflow_call"}
EXCEPTIONS = {"release.yml": {"workflow_run"}}
SCHEDULED_CALLER = "weekly-floor-compilers.yml"
FLOOR_REUSABLE = "ru-floor-compilers.yml"
SHA = re.compile(r"@[0-9a-f]{40}\b")


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


def scheduled_caller_problems(doc: dict) -> list[str]:
    """Why a file that uses `schedule` is not the narrow floor-compiler caller (empty when it is)."""
    out: list[str] = []
    if doc.get("permissions") not in ({}, {"contents": "read"}):
        out.append("top-level permissions must be {} or contents: read only")
    jobs = doc.get("jobs") or {}
    if not jobs:
        out.append("no jobs")
    for name, job in jobs.items():
        uses = str(job.get("uses", ""))
        if not re.search(rf"/{re.escape(FLOOR_REUSABLE)}@\S+$", uses) and uses != f"./.github/workflows/{FLOOR_REUSABLE}":
            out.append(f"job {name} must only call {FLOOR_REUSABLE}")
        if "steps" in job or "secrets" in job:
            out.append(f"job {name} has steps or secrets")
        if job.get("permissions") != {"contents": "read"}:
            out.append(f"job {name} permissions must be exactly contents: read")
    return out


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


def main(paths: list[str]) -> int:
    bad = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        base = os.path.basename(path)
        allowed = ALLOWED | EXCEPTIONS.get(base, set())
        if base == SCHEDULED_CALLER:
            allowed |= {"schedule", "workflow_dispatch"}
            for why in scheduled_caller_problems(doc):
                print(f"::error file={path}::{why} (docs/triggers.md, the floor-compiler exception)")
                bad += 1
        if base == FLOOR_REUSABLE:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for why in floor_reusable_problems(text, doc):
                print(f"::error file={path}::{why} (docs/triggers.md, the floor-compiler exception)")
                bad += 1
        for trig in sorted(triggers(doc) - allowed):
            print(f"::error file={path}::trigger '{trig}' is not allowed (docs/triggers.md): "
                  "start from push, pull_request or workflow_call, and re-run instead of dispatching")
            bad += 1
    print(f"checked {len(paths)} file(s): {bad} disallowed trigger(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
