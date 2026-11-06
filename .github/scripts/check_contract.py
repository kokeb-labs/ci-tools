#!/usr/bin/env python3
"""Detect breaking changes to the reusable workflows' caller contract.

Compares every reusable workflow (a file with an `on: workflow_call`
trigger) in the working tree with the same file at a base git
ref (the pull request's base branch) and reports changes that break callers
pinned to the current major version:

  * a reusable workflow removed;
  * an input removed (callers passing it hit startup_failure);
  * an input's type changed;
  * an input made required, or a new input added as required without default;
  * an output removed;
  * a secret added as required, or a secret removed;
  * job permissions widened (callers granting the old set hit startup_failure).

Breaking changes are allowed only when CHANGELOG.md records them under a
"### Breaking" subsection, in the Unreleased section or in the version section
this pull request adds (which changelog.py then requires to be a major bump;
docs/VERSIONING.md). Without one this script fails and lists them.

Usage: check_contract.py --base-ref <git ref> [--workflows .github/workflows] [--changelog CHANGELOG.md]
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys

import yaml

LEVEL = {"none": 0, "read": 1, "write": 2}


def call_spec(doc: dict) -> dict:
    on = doc.get(True, doc.get("on")) or {}
    if not isinstance(on, dict):
        return {}
    return on.get("workflow_call") or {}


def call_spec_or_none(doc: dict) -> bool:
    """True when the workflow has an `on: workflow_call` trigger (with or without a body)."""
    on = doc.get(True, doc.get("on"))
    if isinstance(on, (dict, list)):
        return "workflow_call" in on
    return on == "workflow_call"


def job_permissions(doc: dict) -> dict[str, str] | None:
    """Union of declared permissions, or None if some job inherits the caller's token unchanged."""
    jobs = [j for j in (doc.get("jobs") or {}).values() if isinstance(j, dict)]
    if "permissions" not in doc and any("permissions" not in j for j in jobs):
        return None
    out: dict[str, str] = {}
    blocks = [doc.get("permissions")] + [j.get("permissions") for j in (doc.get("jobs") or {}).values()
                                         if isinstance(j, dict)]
    for block in blocks:
        if isinstance(block, dict):
            for scope, level in block.items():
                if LEVEL.get(level, 0) > LEVEL.get(out.get(scope, "none"), 0):
                    out[scope] = level
        elif block == "write-all":
            out["*"] = "write"
    return out


def breaking_changes(name: str, old: dict, new: dict) -> list[str]:
    out = []
    o, n = call_spec(old), call_spec(new)
    oi, ni = o.get("inputs") or {}, n.get("inputs") or {}
    for key, spec in oi.items():
        if key not in ni:
            out.append(f"{name}: input `{key}` removed (deprecate it instead: keep accepting it)")
            continue
        if (spec or {}).get("type") != (ni[key] or {}).get("type"):
            out.append(f"{name}: input `{key}` changed type {spec.get('type')} -> {ni[key].get('type')}")
        if not (spec or {}).get("required") and (ni[key] or {}).get("required"):
            out.append(f"{name}: input `{key}` became required")
    for key, spec in ni.items():
        if key not in oi and (spec or {}).get("required") and "default" not in (spec or {}):
            out.append(f"{name}: new required input `{key}` without a default")
    for key in (o.get("outputs") or {}):
        if key not in (n.get("outputs") or {}):
            out.append(f"{name}: output `{key}` removed")
    os_, ns = o.get("secrets") or {}, n.get("secrets") or {}
    for key in os_:
        if key not in ns:
            out.append(f"{name}: secret `{key}` removed")
    for key, spec in ns.items():
        if key not in os_ and (spec or {}).get("required"):
            out.append(f"{name}: new required secret `{key}`")
    op, np_ = job_permissions(old), job_permissions(new)
    if op is None or np_ is None:
        # A job without declared permissions takes whatever the caller grants,
        # so there is no fixed baseline to compare against.
        return out
    for scope, level in np_.items():
        if LEVEL[level] > LEVEL.get(op.get(scope, "none"), 0):
            out.append(f"{name}: needs `{scope}: {level}` (was `{op.get(scope, 'none')}`); "
                       "callers that grant the old set hit startup_failure")
    return out


def breaking_recorded(changelog: str, base_ref: str) -> bool:
    if not os.path.exists(changelog):
        return False
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from changelog import breaking_allowed  # noqa: E402  (sibling script)
    text = open(changelog, encoding="utf-8").read()
    return breaking_allowed(text, git_show(base_ref, changelog))


def git_show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-ref", required=True)
    ap.add_argument("--workflows", default=".github/workflows")
    ap.add_argument("--changelog", default="CHANGELOG.md")
    args = ap.parse_args()

    listing = subprocess.run(["git", "ls-tree", "--name-only", f"{args.base_ref}:{args.workflows}"],
                             capture_output=True, text=True)
    if listing.returncode != 0:
        print(f"::error::cannot list {args.workflows} at {args.base_ref}: {listing.stderr.strip()}")
        return 2
    base_names = {n for n in listing.stdout.split() if re.fullmatch(r".*\.ya?ml", n)
                  and call_spec_or_none(yaml.safe_load(git_show(args.base_ref, f"{args.workflows}/{n}") or "") or {})}
    head_names = set()
    for p in glob.glob(os.path.join(args.workflows, "*.y*ml")):
        with open(p, encoding="utf-8") as fh:
            if call_spec_or_none(yaml.safe_load(fh) or {}):
                head_names.add(os.path.basename(p))

    changes: list[str] = []
    for name in sorted(base_names - head_names):
        changes.append(f"{name}: reusable workflow removed")
    for name in sorted(base_names & head_names):
        old = yaml.safe_load(git_show(args.base_ref, f"{args.workflows}/{name}") or "") or {}
        with open(os.path.join(args.workflows, name), encoding="utf-8") as fh:
            new = yaml.safe_load(fh) or {}
        changes += breaking_changes(name, old, new)

    if not changes:
        print(f"no breaking contract changes against {args.base_ref}")
        return 0
    if breaking_recorded(args.changelog, args.base_ref):
        for c in changes:
            print(f"::warning::breaking (recorded in {args.changelog}): {c}")
        print("breaking changes are recorded under ### Breaking: the next release must be a major bump")
        return 0
    for c in changes:
        print(f"::error::breaking change: {c}")
    print(f"{len(changes)} breaking change(s). Either keep the contract compatible (deprecate instead of "
          f"removing), or record them under '### Breaking' in {args.changelog} "
          "so the next release is a major bump (see docs/VERSIONING.md).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
