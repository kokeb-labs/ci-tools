#!/usr/bin/env python3
"""The verdict of one ru-cmake-matrix call, from the result.json of every entry. Standard library only.

  report.py --plan PLAN_JSON --results DIR [--summary FILE] [--github-output FILE]

PLAN_JSON is the plan job's output (the entries that were to run). An entry without a result.json (its job was
cancelled or never started) counts as failed. Writes a table to the step summary and `results` (JSON list of
{name, toolchain, mcu, rtos, status, failed_step, seconds, tests}), `passed` and `failed` to the step outputs. Exit 1 when an
entry did not pass.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--summary")
    ap.add_argument("--github-output")
    a = ap.parse_args()
    planned = json.loads(a.plan)
    entries = (planned.get("runner") or []) + (planned.get("container") or [])
    found = {}
    for path in glob.glob(os.path.join(a.results, "**", "result.json"), recursive=True):
        with open(path, encoding="utf-8") as fh:
            r = json.load(fh)
        found[r.get("name")] = r
    rows = []
    for e in entries:
        r = found.get(e["name"]) or {"name": e["name"], "toolchain": e["toolchain"], "status": "missing",
                                     "failed_step": "no result (job cancelled or not started)", "tests": {}}
        r["mcu"], r["rtos"] = e.get("mcu", ""), e.get("rtos", "")
        rows.append(r)
    failed = [r for r in rows if r.get("status") != "passed"]
    lines = ["### CMake matrix", "", "| Configuration | Toolchain | Result | Failed step | Tests | Time |",
             "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        t = r.get("tests") or {}
        tests = f"{t.get('tests', 0) - t.get('failures', 0)}/{t.get('tests', 0)}" if t else "-"
        mark = "pass" if r.get("status") == "passed" else "**" + str(r.get("status")) + "**"
        lines.append(f"| `{r['name']}` | {r.get('toolchain', '')} | {mark} | {r.get('failed_step') or '-'} | "
                     f"{tests} | {r.get('seconds', '-')} s |")
    lines += ["", f"{len(rows) - len(failed)} of {len(rows)} configuration(s) passed."]
    text = "\n".join(lines) + "\n"
    print(text)
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(text)
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"results={json.dumps(rows, sort_keys=True)}\n")
            fh.write(f"passed={len(rows) - len(failed)}\nfailed={len(failed)}\n")
    for r in failed:
        print(f"::error::{r['name']}: {r.get('status')} at {r.get('failed_step') or '?'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
