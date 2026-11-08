#!/usr/bin/env python3
"""Fail if a step of ru-repo-checks.yml differs from the step of the single workflow it copies.

ru-repo-checks runs, as steps of one job, what dco.yml, org-standard-check.yml, ru-markdown-lint.yml,
ru-handbook-check.yml, ru-template-drift.yml, ru-cpp-analysis.yml and ru-yaml-lint.yml each run in a job of their
own. Its scripts and pinned actions are copies, so a fix to one of those workflows must reach ru-repo-checks too.
This compares each copied step's `run:` (or github-script `script:`) and `uses:` with its source, and fails on any
difference. The `if:`, `env:` and `with:` of a step may differ: inputs have prefixed names there.

Usage: check_repo_checks.py [--workflows .github/workflows]
"""

from __future__ import annotations

import argparse
import os
import sys

import yaml

# step id in ru-repo-checks.yml -> (source workflow, job id, step index in that job)
COPIES = {
    "dco": ("dco.yml", "dco", 0),
    "checkout": ("org-standard-check.yml", "check", 0),
    "org_standard": ("org-standard-check.yml", "check", 1),
    "markdown_run": ("ru-markdown-lint.yml", "markdownlint", 1),
    "markdown": ("ru-markdown-lint.yml", "markdownlint", 2),
    "handbook_checkout": ("ru-handbook-check.yml", "check", 1),
    "handbook_install": ("ru-handbook-check.yml", "check", 2),
    "handbook": ("ru-handbook-check.yml", "check", 3),
    "drift_checkout": ("ru-template-drift.yml", "drift", 1),
    "drift": ("ru-template-drift.yml", "drift", 2),
    "cppcheck_install": ("ru-cpp-analysis.yml", "cppcheck", 1),
    "cppcheck": ("ru-cpp-analysis.yml", "cppcheck", 2),
    "cppcheck_upload": ("ru-cpp-analysis.yml", "cppcheck", 3),
    "cppcheck_strict": ("ru-cpp-analysis.yml", "cppcheck", 4),
    "yaml_install": ("ru-yaml-lint.yml", "yamllint", 1),
    "yaml": ("ru-yaml-lint.yml", "yamllint", 2),
}
TARGET = "ru-repo-checks.yml"


def body(step: dict) -> dict:
    out = {"uses": step.get("uses"), "run": step.get("run")}
    if str(step.get("uses", "")).startswith("actions/github-script@"):
        out["script"] = (step.get("with") or {}).get("script")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workflows", default=".github/workflows")
    args = ap.parse_args()

    def load(name: str) -> dict:
        with open(os.path.join(args.workflows, name), encoding="utf-8") as fh:
            return yaml.safe_load(fh)

    target = load(TARGET)
    steps = {s.get("id"): s for job in target["jobs"].values() for s in job.get("steps") or [] if s.get("id")}
    errors = []
    for sid, (src, job, idx) in COPIES.items():
        mine = steps.get(sid)
        if mine is None:
            errors.append(f"{TARGET} has no step with id '{sid}' (the copy of {src} {job} step {idx + 1})")
            continue
        theirs = load(src)["jobs"][job]["steps"][idx]
        a, b = body(mine), body(theirs)
        for key in a:
            if a[key] != b[key]:
                errors.append(f"{TARGET} step '{sid}': its {key} differs from {src} (job {job}, step {idx + 1}); "
                              "update both")
    for e in errors:
        print(f"::error file={args.workflows}/{TARGET}::{e}")
    if not errors:
        print(f"{TARGET}: all {len(COPIES)} copied steps match their single workflows")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
