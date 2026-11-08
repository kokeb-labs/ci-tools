#!/usr/bin/env python3
"""Fail if a workflow can be started by a privileged trigger the trigger policy does not allow.

A run started by workflow_dispatch, schedule, workflow_run, pull_request_target, issue_comment and the like runs in
the context of the default branch: it can write the Actions cache that later runs on main restore. Any step that
then runs code checked out by a computed ref could poison that cache (CodeQL
actions/cache-poisoning/poisonable-step). The workflows here therefore start only from push, pull_request,
merge_group and workflow_call; a manual run is a re-run. The one exception is release.yml, which must start from
the finished self-CI (workflow_run) and checks out only the commit that self-CI tested. docs/triggers.md has the
reasoning.

Usage: check_triggers.py FILE...   (workflow files)
"""

from __future__ import annotations

import os
import sys

import yaml

ALLOWED = {"push", "pull_request", "merge_group", "workflow_call"}
EXCEPTIONS = {"release.yml": {"workflow_run"}}


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


def main(paths: list[str]) -> int:
    bad = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        allowed = ALLOWED | EXCEPTIONS.get(os.path.basename(path), set())
        for trig in sorted(triggers(doc) - allowed):
            print(f"::error file={path}::trigger '{trig}' is not allowed (docs/triggers.md): "
                  "start from push, pull_request or workflow_call, and re-run instead of dispatching")
            bad += 1
    print(f"checked {len(paths)} file(s): {bad} disallowed trigger(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
