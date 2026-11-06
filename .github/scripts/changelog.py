#!/usr/bin/env python3
"""CHANGELOG.md drives the releases of this repository (docs/VERSIONING.md).

A pull request that should be released moves the entries under ``## [Unreleased]`` to a new
``## [X.Y.Z] - YYYY-MM-DD`` section (``changelog.py bump patch``). When it merges, release.yml tags that version,
publishes the section as the release notes and moves the major tag. A pull request without a new section is merged
without a release; its entries wait under Unreleased for the next one.

Commands:

  bump patch|minor|major [--date YYYY-MM-DD]
      Move the Unreleased entries to the next version's section (local helper for contributors).
  check --base-ref <git ref>
      Pull request check (needs the tags fetched). A new, untagged version section must be the next patch, minor or major after the base branch's top
      version, dated, not empty, with nothing left under Unreleased; a "### Breaking" heading needs a major bump.
  release [--version X.Y.Z] --notes <file>
      Print ``version=X.Y.Z`` (or ``version=``) for the top version section, or for the named one, and write its body
      to <file> (release.yml).
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys

HEAD_RE = re.compile(r"^## \[(?P<name>[^\]]+)\](?P<rest>[^\n]*)$", re.M)
VER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
DATE_RE = re.compile(r"^ - \d{4}-\d{2}-\d{2}$")


def sections(text: str) -> list[tuple[str, str, str]]:
    """(name, rest of heading line, body) for every ``## [name]`` section, in file order."""
    heads = list(HEAD_RE.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((m.group("name"), m.group("rest"), text[m.end():end]))
    return out


def has_entries(body: str) -> bool:
    return any(line.lstrip().startswith(("- ", "* ")) or (line.strip() and not line.startswith("#"))
               for line in body.splitlines())


def has_breaking(body: str) -> bool:
    return bool(re.search(r"^### Breaking\b", body, re.M))


def top_version(text: str) -> tuple[str, str, str] | None:
    for name, rest, body in sections(text):
        if VER_RE.match(name):
            return name, rest, body
    return None


def unreleased(text: str) -> str:
    for name, _rest, body in sections(text):
        if name == "Unreleased":
            return body
    return ""


def parse(v: str) -> tuple[int, int, int]:
    m = VER_RE.match(v)
    if not m:
        raise ValueError(v)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def next_versions(v: str) -> dict[str, str]:
    a, b, c = parse(v)
    return {"patch": f"{a}.{b}.{c + 1}", "minor": f"{a}.{b + 1}.0", "major": f"{a + 1}.0.0"}


def breaking_allowed(text: str, base_text: str | None) -> bool:
    """A breaking change is recorded under Unreleased, or in a version section new in this pull request."""
    if has_breaking(unreleased(text)):
        return True
    top = top_version(text)
    base_top = top_version(base_text or "")
    return bool(top and base_top and top[0] != base_top[0] and has_breaking(top[2]))


def cmd_bump(path: str, level: str, date: str) -> int:
    text = open(path, encoding="utf-8").read()
    top = top_version(text)
    if not top:
        print("no released version in the changelog; write the first section by hand", file=sys.stderr)
        return 1
    body = unreleased(text)
    if not has_entries(body):
        print("nothing under ## [Unreleased] to release", file=sys.stderr)
        return 1
    if has_breaking(body) and level != "major":
        print("Unreleased has ### Breaking: only a major bump is allowed", file=sys.stderr)
        return 1
    new = next_versions(top[0])[level]
    heads = list(HEAD_RE.finditer(text))
    i = next(k for k, h in enumerate(heads) if h.group("name") == "Unreleased")
    start, end = heads[i].end(), heads[i + 1].start() if i + 1 < len(heads) else len(text)
    text = f"{text[:start]}\n\n## [{new}] - {date}\n\n{body.strip()}\n\n{text[end:]}"
    open(path, "w", encoding="utf-8").write(text)
    print(new)
    return 0


def tagged(version: str) -> bool:
    r = subprocess.run(["git", "tag", "-l", f"v{version}"], capture_output=True, text=True)
    return bool(r.stdout.strip())


def check(text: str, base_text: str | None, is_tagged=tagged) -> list[str]:
    errors = []
    top = top_version(text)
    base_top = top_version(base_text or "")
    if not top or (base_top and top[0] == base_top[0]) or is_tagged(top[0]):
        return errors  # no new release in this pull request (an already released version is only recorded)
    name, rest, body = top
    if base_top:
        allowed = next_versions(base_top[0])
        if name not in allowed.values():
            errors.append(f"[{name}] must follow [{base_top[0]}] by one step: one of {', '.join(allowed.values())}")
        elif has_breaking(body) and name != allowed["major"]:
            errors.append(f"[{name}] has ### Breaking: it must be the major release {allowed['major']}")
    if not DATE_RE.match(rest):
        errors.append(f"[{name}] needs a date: '## [{name}] - YYYY-MM-DD'")
    if not has_entries(body):
        errors.append(f"[{name}] has no entries")
    if has_entries(unreleased(text)):
        errors.append(f"entries are left under [Unreleased] next to the new [{name}]: move them into it")
    return errors


def git_show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--changelog", default="CHANGELOG.md")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bump")
    b.add_argument("level", choices=["patch", "minor", "major"])
    b.add_argument("--date", default=datetime.date.today().isoformat())
    c = sub.add_parser("check")
    c.add_argument("--base-ref", required=True)
    r = sub.add_parser("release")
    r.add_argument("--notes", required=True)
    r.add_argument("--version", default="")
    args = ap.parse_args()

    if args.cmd == "bump":
        return cmd_bump(args.changelog, args.level, args.date)
    text = open(args.changelog, encoding="utf-8").read()
    if args.cmd == "check":
        errors = check(text, git_show(args.base_ref, args.changelog))
        for e in errors:
            print(f"::error file={args.changelog}::{e}")
        if not errors:
            top = top_version(text)
            print(f"changelog ok (top version {top[0] if top else 'none'})")
        return 1 if errors else 0
    if args.version:
        found = next(((n, r, b) for n, r, b in sections(text) if n == args.version), None)
    else:
        found = top_version(text)
    print(f"version={found[0] if found else ''}")
    if found:
        open(args.notes, "w", encoding="utf-8").write(found[2].strip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
