"""Generated regions of this repository's documentation site, read from the reusable workflows themselves.

* ``workflow-catalogue``: every reusable workflow (a file with an ``on: workflow_call`` trigger) with its page, purpose
  (the purpose line of the page) and permissions.
* ``permissions-table``: the permissions each reusable workflow needs, per job and in total.
* ``inputs-<workflow>``: the inputs table of one workflow (``inputs-ru-ci-gate``, ...).
* ``jobs-<workflow>``: the jobs of one workflow with their permissions and step names.
* ``inputs-ensure-tools-directory``: the inputs and outputs of the composite action.

A workflow's YAML is the only source, so a page cannot drift from it: ``kokeb-docs gen --check`` fails CI when a
region differs from what the workflows give.
"""

from __future__ import annotations

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOWS = ROOT / ".github/workflows"
DOCS = ROOT / "docs"


def _load(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _is_reusable(doc: dict) -> bool:
    on = doc.get(True, doc.get("on"))
    if isinstance(on, (dict, list)):
        return "workflow_call" in on
    return on == "workflow_call"


def _workflows() -> list[pathlib.Path]:
    # ci-*.yml are this repository's own self-tests (called by ci-self.yml), not part of the catalogue.
    return [p for p in sorted(WORKFLOWS.glob("*.yml")) if _is_reusable(_load(p)) and not p.name.startswith("ci-")]


def _inputs(doc: dict) -> dict:
    on = doc.get(True, doc.get("on")) or {}
    return ((on.get("workflow_call") or {}).get("inputs")) or {}


def _cell(value) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _perms(job: dict) -> dict[str, str]:
    p = job.get("permissions")
    if isinstance(p, dict):
        return {k: v for k, v in p.items() if v != "none"}
    return {}


def _union(doc: dict) -> dict[str, str]:
    rank = {"read": 1, "write": 2}
    out: dict[str, str] = {}
    for job in (doc.get("jobs") or {}).values():
        for scope, level in _perms(job).items():
            if rank.get(level, 0) > rank.get(out.get(scope, ""), 0):
                out[scope] = level
    return out


def _fmt_perms(perms: dict[str, str]) -> str:
    return ", ".join(f"`{k}: {v}`" for k, v in sorted(perms.items())) or "none"


def _purpose(stem: str) -> str:
    page = DOCS / f"{stem}.md"
    if not page.exists():
        return ""
    lines = page.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            for nxt in lines[i + 1 :]:
                if nxt.strip():
                    para = []
                    for rest in lines[lines.index(nxt, i + 1) :]:
                        if not rest.strip():
                            break
                        para.append(rest.strip())
                    return " ".join(para)
            break
    return ""


def workflow_catalogue(page) -> str:
    rows = ["| Workflow | Purpose | Permissions |", "| --- | --- | --- |"]
    for wf in _workflows():
        doc = _load(wf)
        link = page.rel(f"docs/{wf.stem}.md")
        purpose = _purpose(wf.stem) or _cell(doc.get("name", ""))
        rows.append(f"| [`{wf.name}`]({link}) | {_cell(purpose)} | {_fmt_perms(_union(doc))} |")
    return "\n".join(rows) + "\n"


def permissions_table(page) -> str:
    rows = ["| Workflow | Caller grants | Job: permissions |", "| --- | --- | --- |"]
    for wf in _workflows():
        doc = _load(wf)
        jobs = "<br>".join(f"`{name}`: {_fmt_perms(_perms(job))}" for name, job in (doc.get("jobs") or {}).items())
        rows.append(f"| [`{wf.name}`]({page.rel(f'docs/{wf.stem}.md')}) | {_fmt_perms(_union(doc))} | {jobs} |")
    return "\n".join(rows) + "\n"


def _inputs_table(path: pathlib.Path) -> str:
    inputs = _inputs(_load(path))
    if not inputs:
        return "This workflow has no inputs.\n"
    rows = ["| Input | Type | Default | Description |", "| --- | --- | --- | --- |"]
    for name, spec in inputs.items():
        spec = spec or {}
        if spec.get("required"):
            default = "required"
        elif "default" in spec:
            d = spec["default"]
            d = ("true" if d else "false") if isinstance(d, bool) else str(d)
            d = " ".join(d.split())
            default = f"`{_cell(d)}`" if d else "empty"
        else:
            default = "empty"
        rows.append(f"| `{name}` | {spec.get('type', '')} | {default} | {_cell(spec.get('description', ''))} |")
    return "\n".join(rows) + "\n"


def _jobs_table(path: pathlib.Path) -> str:
    rows = ["| Job | Permissions | Steps |", "| --- | --- | --- |"]
    for name, job in (_load(path).get("jobs") or {}).items():
        if "uses" in job:
            steps = f"calls `{job['uses']}`"
        else:
            names = [s.get("name") or (f"`{s['uses'].split('@')[0]}`" if "uses" in s else "") for s in job.get("steps") or []]
            steps = "; ".join(_cell(n) for n in names if n)
        title = job.get("name")
        label = f"`{name}`" + (f" ({_cell(title)})" if title and "${{" not in str(title) else "")
        rows.append(f"| {label} | {_fmt_perms(_perms(job))} | {steps} |")
    return "\n".join(rows) + "\n"


def _action_inputs() -> str:
    doc = _load(ROOT / ".github/actions/ensure-tools-directory/action.yml")
    rows = ["| Input | Default | Description |", "| --- | --- | --- |"]
    for name, spec in (doc.get("inputs") or {}).items():
        spec = spec or {}
        d = " ".join(str(spec.get("default", "")).split())
        rows.append(f"| `{name}` | {f'`{_cell(d)}`' if d else 'empty'} | {_cell(spec.get('description', ''))} |")
    rows += ["", "| Output | Description |", "| --- | --- |"]
    for name, spec in (doc.get("outputs") or {}).items():
        rows.append(f"| `{name}` | {_cell((spec or {}).get('description', ''))} |")
    return "\n".join(rows) + "\n"


REGIONS = {"workflow-catalogue": workflow_catalogue, "permissions-table": permissions_table,
           "inputs-ensure-tools-directory": _action_inputs}
for _wf in _workflows():
    REGIONS[f"inputs-{_wf.stem}"] = (lambda p=_wf: _inputs_table(p))
    REGIONS[f"jobs-{_wf.stem}"] = (lambda p=_wf: _jobs_table(p))
