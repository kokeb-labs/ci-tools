#!/usr/bin/env python3
"""Pin hygiene: every submodule is pinned to the commit of a release or release-candidate tag whose CI gate passed,
and the lock file says exactly that. Standard library plus PyYAML.

  pins.py --lock FILE [--root DIR] [--gates FILE] [--version-file FILE] [--required-check NAME]
          [--tag-pattern REGEX] [--forbid-branch-entries true|false] [--url-pattern REGEX]
          [--handbook-levels "high safety"] [--private-repos true|false] [--release-lock FILE] [--ref REF]
          [--report-dir DIR] [--summary FILE] [--github-output FILE] [--enforce true|false]

The GitHub API is read with the token in GITHUB_TOKEN (the workflow's built-in token; there is no other credential)
at GITHUB_API_URL. Checks, by id:

  PIN-001  the lock has exactly one entry per submodule, and none without a submodule
  PIN-002  the gitlink commit equals the lock entry's commit
  PIN-003  the lock entry's tag exists and points at that commit (annotated tags dereferenced)
  PIN-004  the tag matches --tag-pattern and the entry's kind agrees (rc for -rc.N, else release); an rc pin in a
           final release of this repository (--ref refs/tags/vX.Y.Z) is a warning
  PIN-005  the required check (--required-check, e.g. "CI gate / gate") concluded success on that commit
  PIN-006  driver.yml at the commit: name equals the lock name, version equals the tag without v and -rc.N
  PIN-007  driver.yml mcus and peripheral equal the gate table (--gates: "<name>:<MCU>:<peripheral>" strings; no
           entry means mcus [any] and peripheral null)
  PIN-008  driver.yml kb_core_min is null or not above this repository's version (--version-file)
  PIN-009  .kokeb/handbook.yml at the commit declares one of --handbook-levels (skipped when empty)
  PIN-010  the .gitmodules URL matches --url-pattern, and a checked-out submodule's working tree is clean
  PIN-011  .gitmodules has no branch = entry (--forbid-branch-entries)
  PIN-012  --release-lock (at a release): its pins equal the lock's, and the commit it records is this tree's HEAD
  PIN-013  the repository is readable with the built-in token, and is public unless --private-repos true

A finding is one line "PIN-NNN name: message"; the step summary gets a table of every pin; the report directory gets
pins.json and pins.sarif. Exit 1 on any finding (with --enforce true).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

import yaml

RULES = {
    "PIN-001": "one lock entry per submodule",
    "PIN-002": "gitlink equals the lock commit",
    "PIN-003": "the tag points at the commit",
    "PIN-004": "release or release-candidate tag, kind agrees",
    "PIN-005": "the required check passed on the commit",
    "PIN-006": "driver.yml name and version match",
    "PIN-007": "driver.yml mcus and peripheral match the gate table",
    "PIN-008": "kb_core_min is not above this version",
    "PIN-009": "handbook level",
    "PIN-010": "submodule URL and clean working tree",
    "PIN-011": "no branch entries",
    "PIN-012": "release lock complete and matching",
    "PIN-013": "repository readable and public",
}


class Api:
    """The GitHub REST API with the built-in token. get() returns (status, parsed JSON or None)."""

    def __init__(self, token: str, base: str):
        self.token, self.base = token, base.rstrip("/")
        self.cache: dict[str, tuple[int, object]] = {}

    def get(self, path: str) -> tuple[int, object]:
        if path in self.cache:
            return self.cache[path]
        req = urllib.request.Request(self.base + path, headers={
            "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ci-tools-pin-hygiene", **({"Authorization": f"Bearer {self.token}"} if self.token else {})})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    out = (r.status, json.loads(r.read().decode() or "null"))
                    break
            except urllib.error.HTTPError as e:
                out = (e.code, None)
                if e.code < 500:
                    break
            except (urllib.error.URLError, TimeoutError):
                out = (0, None)
        self.cache[path] = out
        return out


# ------------------------------------------------------------------------------------------------------- local tree

def git(root: str, *args: str) -> str:
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=False).stdout


def gitlinks(root: str) -> dict[str, str]:
    """path -> commit of every gitlink (mode 160000) in the index."""
    out = {}
    for line in git(root, "ls-files", "-s").splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) >= 2 and parts[0] == "160000":
            out[path] = parts[1]
    return out


def gitmodules(root: str) -> dict[str, dict]:
    """name -> {path, url, branch?} from .gitmodules."""
    path = os.path.join(root, ".gitmodules")
    if not os.path.isfile(path):
        return {}
    mods: dict[str, dict] = {}
    for line in git(root, "config", "-f", ".gitmodules", "--list").splitlines():
        key, _, value = line.partition("=")
        m = re.match(r"^submodule\.(.+)\.([^.]+)$", key)
        if m:
            mods.setdefault(m.group(1), {})[m.group(2)] = value
    return mods


def repo_of_url(url: str) -> str:
    m = re.match(r"^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else ""


def parse_gates(path: str) -> dict[str, list[tuple[str, str]]]:
    """name -> [(MCU, peripheral)] from every "<name>:<MCU>:<peripheral>" string of a CMake (or any text) file."""
    gates: dict[str, list[tuple[str, str]]] = {}
    if not path:
        return gates
    with open(path, encoding="utf-8") as fh:
        text = re.sub(r"#[^\n]*", "", fh.read())
    for name, mcu, periph in re.findall(r'"([A-Za-z0-9_]+):([A-Za-z0-9_]+):([A-Za-z0-9_]*)"', text):
        gates.setdefault(name, []).append((mcu, periph))
    return gates


def parse_version(path: str) -> str:
    """X.Y.Z from set(*_VERSION_MAJOR n) ... in a CMake file, set(*_VERSION "x.y.z"), VERSION x.y.z or a bare line."""
    if not path:
        return ""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    parts = {}
    for k in ("MAJOR", "MINOR", "PATCH"):
        m = re.search(rf"set\(\s*\w*VERSION_{k}\s+(\d+)\s*\)", text)
        if m:
            parts[k] = m.group(1)
    if len(parts) == 3:
        return f"{parts['MAJOR']}.{parts['MINOR']}.{parts['PATCH']}"
    m = re.search(r"(?<![\w.])(\d+\.\d+\.\d+)(?![\w.])", text)
    return m.group(1) if m else ""


def vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v.split("-")[0])[:3])


# ------------------------------------------------------------------------------------------------------------ check

def check(a, api: Api) -> tuple[list[dict], list[dict], list[str]]:
    findings: list[dict] = []
    warnings: list[str] = []
    rows: list[dict] = []

    def add(rule: str, name: str, msg: str):
        findings.append({"rule": rule, "name": name, "message": msg})

    root = a.root
    with open(os.path.join(root, a.lock), encoding="utf-8") as fh:
        lock = yaml.safe_load(fh) or {}
    entries = lock.get("drivers") if isinstance(lock, dict) else None
    if entries is None:
        entries = []
    if not isinstance(entries, list):
        add("PIN-001", "-", f"{a.lock}: `drivers` must be a list")
        entries = []
    links = gitlinks(root)
    mods = gitmodules(root)
    by_path = {m.get("path", ""): (n, m) for n, m in mods.items()}
    gates = parse_gates(os.path.join(root, a.gates) if a.gates else "")
    version = parse_version(os.path.join(root, a.version_file) if a.version_file else "")
    tag_rx = re.compile(a.tag_pattern)
    url_rx = re.compile(a.url_pattern) if a.url_pattern else None
    final_release = bool(re.match(r"^refs/tags/v\d+\.\d+\.\d+$", a.ref or ""))
    levels = set(a.handbook_levels.split())

    if a.forbid_branch_entries == "true":
        for n, m in sorted(mods.items()):
            if "branch" in m:
                add("PIN-011", n, f".gitmodules: submodule {n} has `branch = {m['branch']}`; pins never follow a branch")
    for n, m in sorted(mods.items()):
        if url_rx and not url_rx.match(m.get("url", "")):
            add("PIN-010", n, f".gitmodules: URL {m.get('url', '')} does not match {a.url_pattern}")
        if m.get("path") not in links:
            add("PIN-001", n, f".gitmodules lists {m.get('path')}, but the tree has no gitlink there")

    seen_paths = set()
    names = [str((e or {}).get("name", "")) for e in entries]
    for dup in sorted({x for x in names if names.count(x) > 1}):
        add("PIN-001", dup, f"{a.lock}: {dup} has more than one entry")
    for e in entries:
        e = e or {}
        name, repo, tag = str(e.get("name", "")), str(e.get("repo", "")), str(e.get("tag", ""))
        commit, kind = str(e.get("commit", "")), str(e.get("kind", ""))
        row = {"name": name, "repo": repo, "tag": tag, "commit": commit, "kind": kind, "path": "", "gate": "-",
               "ok": True}
        rows.append(row)
        missing = [k for k in ("name", "repo", "tag", "commit", "kind") if not e.get(k)]
        if missing:
            add("PIN-001", name or "-", f"{a.lock}: entry lacks {', '.join(missing)}")
            continue
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            add("PIN-002", name, f"commit {commit} is not a full 40-hex SHA")
        paths = [p for p, (_, m) in by_path.items() if repo_of_url(m.get("url", "")).lower() == repo.lower()]
        if len(paths) != 1:
            add("PIN-001", name, f"no submodule has the URL of {repo}" if not paths else
                f"{len(paths)} submodules point at {repo}")
        else:
            path = paths[0]
            row["path"] = path
            seen_paths.add(path)
            if links.get(path) != commit:
                add("PIN-002", name, f"the gitlink {path} is {links.get(path, 'missing')}, the lock says {commit}")
            sub = os.path.join(root, path)
            if os.path.exists(os.path.join(sub, ".git")):
                dirty = git(sub, "status", "--porcelain")
                if dirty.strip():
                    add("PIN-010", name, f"the working tree of {path} is not clean")
        if not tag_rx.match(tag):
            add("PIN-004", name, f"tag {tag} is not a release or release-candidate tag ({a.tag_pattern})")
        want_kind = "rc" if re.search(r"-rc\.\d+$", tag) else "release"
        if kind != want_kind:
            add("PIN-004", name, f"kind is {kind}, the tag {tag} makes it {want_kind}")
        if want_kind == "rc" and final_release:
            warnings.append(f"PIN-004 {name}: a final release pins the release candidate {tag}")

        status, info = api.get(f"/repos/{repo}")
        if status != 200:
            add("PIN-013", name, f"cannot read {repo} with the workflow's built-in token (HTTP {status}); a pin must "
                                 "be readable by everyone who rebuilds this tree")
            row["ok"] = False
            continue
        if isinstance(info, dict) and info.get("private") and a.private_repos != "true":
            add("PIN-013", name, f"{repo} is private; set private_repos: true to allow private pins")
        status, ref = api.get(f"/repos/{repo}/git/ref/tags/{urllib.parse.quote(tag)}")
        tag_commit = ""
        if status == 200 and isinstance(ref, dict):
            obj = ref.get("object") or {}
            for _ in range(5):  # annotated tag (or a tag of a tag) -> commit
                if obj.get("type") != "tag":
                    break
                st, t = api.get(f"/repos/{repo}/git/tags/{obj.get('sha')}")
                obj = (t or {}).get("object") or {} if st == 200 else {}
            tag_commit = obj.get("sha", "") if obj.get("type") == "commit" else ""
        if not tag_commit:
            add("PIN-003", name, f"tag {tag} does not exist in {repo}")
        elif tag_commit != commit:
            add("PIN-003", name, f"tag {tag} points at {tag_commit}, the lock says {commit} (a moved tag?)")
        if a.required_check:
            status, runs = api.get(f"/repos/{repo}/commits/{commit}/check-runs?per_page=100&check_name="
                                   + urllib.parse.quote(a.required_check))
            matching = [r for r in ((runs or {}).get("check_runs") or []) if r.get("name") == a.required_check]
            if status != 200:
                add("PIN-005", name, f"cannot read the checks of {commit[:12]} (HTTP {status})")
            elif not matching:
                add("PIN-005", name, f"no '{a.required_check}' check ran on {commit[:12]}")
            else:
                latest = max(matching, key=lambda r: r.get("started_at") or "")
                if latest.get("conclusion") != "success":
                    add("PIN-005", name, f"'{a.required_check}' on {commit[:12]} concluded "
                                         f"{latest.get('conclusion') or latest.get('status')}")
        meta = read_yaml(api, repo, "driver.yml", commit)
        if meta is None:
            add("PIN-006", name, f"driver.yml is missing at {commit[:12]}")
        else:
            if str(meta.get("name")) != name:
                add("PIN-006", name, f"driver.yml name is {meta.get('name')}, the lock says {name}")
            want = re.sub(r"^v", "", re.sub(r"-rc\.\d+$", "", tag))
            if str(meta.get("version")) != want:
                add("PIN-006", name, f"driver.yml version is {meta.get('version')}, the tag {tag} makes it {want}")
            mcus = sorted(str(x).lower() for x in (meta.get("mcus") or ["any"]))
            periph = meta.get("peripheral")
            gate = gates.get(name)
            if gate:
                row["gate"] = ", ".join(f"{m}:{p}" for m, p in gate)
                g_mcus = sorted({m.lower() for m, _ in gate})
                g_periph = {p for _, p in gate}
                if mcus != g_mcus:
                    add("PIN-007", name, f"driver.yml mcus {mcus} differ from the gate table {g_mcus}")
                if len(g_periph) != 1 or str(periph or "") != next(iter(g_periph)):
                    add("PIN-007", name, f"driver.yml peripheral {periph} differs from the gate table "
                                         f"{sorted(g_periph)}")
            elif a.gates and (mcus != ["any"] or periph not in (None, "", "null")):
                add("PIN-007", name, f"driver.yml needs mcus {mcus} and peripheral {periph}, but the gate table "
                                     "has no entry for it")
            kmin = meta.get("kb_core_min")
            if kmin not in (None, "", "null") and version:
                if vtuple(str(kmin)) > vtuple(version):
                    add("PIN-008", name, f"kb_core_min {kmin} is above this version {version}")
        if levels:
            hb = read_yaml(api, repo, ".kokeb/handbook.yml", commit)
            lvl = str((hb or {}).get("level", ""))
            if lvl not in levels:
                add("PIN-009", name, f".kokeb/handbook.yml level is {lvl or 'missing'}, needs one of "
                                     f"{', '.join(sorted(levels))}")

    for path in sorted(set(links) - seen_paths):
        n = by_path.get(path, (path, {}))[0]
        add("PIN-001", n, f"the submodule {path} has no entry in {a.lock}")

    if a.release_lock:
        check_release_lock(a, entries, add)
    bad = {f["name"] for f in findings}
    for r in rows:
        r["ok"] = r["ok"] and r["name"] not in bad
    return findings, rows, warnings


def read_yaml(api: Api, repo: str, path: str, ref: str):
    status, data = api.get(f"/repos/{repo}/contents/{path}?ref={ref}")
    if status != 200 or not isinstance(data, dict) or "content" not in data:
        return None
    try:
        doc = yaml.safe_load(base64.b64decode(data["content"]).decode("utf-8"))
    except (ValueError, yaml.YAMLError):
        return None
    return doc if isinstance(doc, dict) else None


def check_release_lock(a, entries, add) -> None:
    path = os.path.join(a.root, a.release_lock)
    if not os.path.isfile(path):
        add("PIN-012", "-", f"the release lock {a.release_lock} does not exist")
        return
    with open(path, encoding="utf-8") as fh:
        rel = yaml.safe_load(fh) or {}
    keys = ("name", "repo", "tag", "commit", "kind")
    want = sorted(tuple(str((e or {}).get(k, "")) for k in keys) for e in entries)
    got = sorted(tuple(str((e or {}).get(k, "")) for k in keys) for e in (rel.get("drivers") or []))
    if want != got:
        add("PIN-012", "-", f"the pins of {a.release_lock} differ from {a.lock}")
    head = git(a.root, "rev-parse", "HEAD").strip()
    own = [v.get("commit") for v in rel.values() if isinstance(v, dict) and "commit" in v]
    if not own:
        add("PIN-012", "-", f"{a.release_lock} records no commit of this repository")
    elif head and own[0] != head:
        add("PIN-012", "-", f"{a.release_lock} records commit {own[0]}, the tree is {head}")


# ----------------------------------------------------------------------------------------------------------- output

def lock_line(root: str, lock: str, name: str) -> int:
    try:
        with open(os.path.join(root, lock), encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if re.search(rf"name:\s*{re.escape(name)}\b", line):
                    return n
    except OSError:
        pass
    return 1


def sarif(findings: list[dict], lock_path: str, root: str, lock: str) -> dict:
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "ci-tools pin hygiene", "informationUri":
                                "https://github.com/kokeb-labs/ci-tools/blob/main/docs/ru-pin-hygiene.md",
                                "rules": [{"id": k, "shortDescription": {"text": v}} for k, v in RULES.items()]}},
            "results": [{
                "ruleId": f["rule"], "level": "error", "message": {"text": f"{f['name']}: {f['message']}"},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": lock_path},
                                                    "region": {"startLine": lock_line(root, lock, f["name"])}}}],
            } for f in findings],
        }],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lock", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--gates", default="")
    ap.add_argument("--version-file", default="")
    ap.add_argument("--required-check", default="CI gate / gate")
    ap.add_argument("--tag-pattern", default=r"^v[0-9]+\.[0-9]+\.[0-9]+(-rc\.[0-9]+)?$")
    ap.add_argument("--forbid-branch-entries", default="true", choices=["true", "false"])
    ap.add_argument("--url-pattern", default=r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?(\.git)?$")
    ap.add_argument("--handbook-levels", default="")
    ap.add_argument("--private-repos", default="false", choices=["true", "false"])
    ap.add_argument("--release-lock", default="")
    ap.add_argument("--ref", default=os.environ.get("GITHUB_REF", ""))
    ap.add_argument("--report-dir", default="")
    ap.add_argument("--summary")
    ap.add_argument("--github-output")
    ap.add_argument("--enforce", default="true", choices=["true", "false"])
    a = ap.parse_args()
    for label, rx in (("tag_pattern", a.tag_pattern), ("url_pattern", a.url_pattern)):
        try:
            re.compile(rx)
        except re.error as e:
            print(f"::error::{label} is not a regular expression: {e}")
            return 1
    for label, p in (("lock_file", a.lock), ("gates_file", a.gates), ("version_file", a.version_file)):
        if p and not os.path.isfile(os.path.join(a.root, p)):
            print(f"::error::{label} {p} does not exist")
            return 1
    api = Api(os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    findings, rows, warnings = check(a, api)
    lock_path = os.path.normpath(os.path.join(a.root, a.lock))
    level = "error" if a.enforce == "true" else "warning"
    for f in findings:
        line = lock_line(a.root, a.lock, f["name"])
        print(f"::{level} file={lock_path},line={line},title={f['rule']}::{f['rule']} {f['name']}: {f['message']}")
    for w in warnings:
        print(f"::warning file={lock_path}::{w}")
    table = ["### Pin hygiene", "", f"{len(rows)} pin(s) in `{lock_path}`, {len(findings)} finding(s).", ""]
    if rows:
        table += ["| Pin | Repository | Tag | Commit | Kind | Gate | Result |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for r in rows:
            table.append(f"| `{r['name']}` | {r['repo']} | `{r['tag']}` | `{r['commit'][:12]}` | {r['kind']} | "
                         f"{r['gate']} | {'pass' if r['ok'] else '**fail**'} |")
        table.append("")
    if findings:
        table += ["| Rule | Pin | Finding |", "| --- | --- | --- |"]
        table += [f"| {f['rule']} | `{f['name']}` | {f['message']} |" for f in findings]
        table.append("")
    text = "\n".join(table) + "\n"
    print(text)
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(text)
    if a.report_dir:
        os.makedirs(a.report_dir, exist_ok=True)
        with open(os.path.join(a.report_dir, "pins.json"), "w", encoding="utf-8") as fh:
            json.dump({"pins": rows, "findings": findings, "warnings": warnings}, fh, indent=2)
        with open(os.path.join(a.report_dir, "pins.sarif"), "w", encoding="utf-8") as fh:
            json.dump(sarif(findings, lock_path, a.root, a.lock), fh, indent=2)
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"pins={len(rows)}\nfindings={len(findings)}\n")
            fh.write(f"rules={json.dumps(sorted({f['rule'] for f in findings}))}\n")
    return 1 if (findings and a.enforce == "true") else 0


if __name__ == "__main__":
    sys.exit(main())
