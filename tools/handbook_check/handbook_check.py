#!/usr/bin/env python3
"""Check a repository against the Kokeb Labs handbook rules that a script can decide.

The repository declares what it is in `.kokeb/handbook.yml`:

    handbook: "1.0"      # the handbook release it follows
    kind: driver         # driver | library | hal | firmware | tooling | docs | template
    level: high          # standard | high | safety
    waivers:             # optional
      - rule: KB-DOC-004
        reason: Doxygen comments for the v2 register API land with #41.
        approved_by: "@N3b3x"
        until: 2027-01-31

Each check below belongs to one handbook rule and runs only when that rule applies to the repository's kind and
level. A finding is an error, unless the rule is still `proposed` and its `enforce_from` date is ahead (then a
warning), or a valid waiver covers the rule (then a notice). Rule titles, levels, scope and dates come from
rules.json, a snapshot of the handbook exported by its own tooling.

Usage: handbook_check.py [--repo .] [--rules rules.json] [--today YYYY-MM-DD] [--report report.json]
Exit status: 1 when there is an error, 2 when the declaration cannot be read, 0 otherwise.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
HANDBOOK_URL = "https://kokeb-labs.github.io/handbook/rules"
KINDS = ("driver", "library", "hal", "firmware", "tooling", "docs", "template")
LEVELS = ("standard", "high", "safety")
TARGET_KINDS = {"driver", "library", "hal", "firmware", "template"}  # code that runs on a microcontroller

# ADR-0017: the target library subset.
DRIVER_HEADERS = {"cstdint", "cstddef", "array", "algorithm", "type_traits", "concepts", "limits", "cmath", "cstring",
                  "span", "utility", "optional", "bit", "cstdarg"}
BANNED_HEADERS = {"string", "vector", "map", "set", "unordered_map", "unordered_set", "list", "deque", "memory",
                  "functional", "iostream", "istream", "ostream", "sstream", "fstream", "thread", "mutex",
                  "condition_variable", "future", "regex", "filesystem", "locale", "exception", "stdexcept",
                  "typeinfo", "any"}
# ADR-0011: what the root of a driver (or a template that generates one) may hold.
ROOT_FILES = {"README.md", "LICENSE", "CHANGELOG.md", "CMakeLists.txt", "AGENTS.md", "CLAUDE.md", ".gitignore",
              ".gitmodules", "driver.yml"}
ROOT_DIRS = {".github", ".claude", ".kokeb", "_config", "cmake", "docs", "examples", "inc", "src", "tests", "tools",
             "third_party"}
BUSES = {"spi", "i2c", "uart", "adc", "pio", "gpio", "can", "canopen", "modbus", "onewire", "none"}
SOURCE_SUFFIXES = {".h", ".hpp", ".hh", ".ipp", ".inl", ".c", ".cc", ".cpp", ".cxx"}


@dataclasses.dataclass
class Finding:
    rule: str
    check: str
    message: str
    path: str = ""
    line: int = 0
    severity: str = "error"  # error | warning | notice, decided by rule status, date and waivers


class Repo:
    def __init__(self, root: pathlib.Path, rules: dict, today: datetime.date):
        self.root = root
        self.rules = rules
        self.today = today
        self.findings: list[Finding] = []
        self.declaration: dict = {}
        self.kind = ""
        self.level = "standard"
        self.waivers: dict[str, dict] = {}

    # -- helpers -----------------------------------------------------------------------------------------------
    def tracked(self) -> list[str]:
        r = subprocess.run(["git", "-C", str(self.root), "ls-files"], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.split()
        return [str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts]

    def applies(self, rule_id: str) -> bool:
        r = self.rules.get(rule_id)
        if r is None:
            return False
        if r["status"] == "retired":
            return False
        profiles = r.get("profiles") or ["all"]
        if profiles != ["all"] and self.kind not in profiles:
            return False
        return LEVELS.index(self.level) >= LEVELS.index(r.get("from_level") or "standard")

    def add(self, rule: str, check: str, message: str, path: str = "", line: int = 0) -> None:
        if self.applies(rule):
            self.findings.append(Finding(rule, check, message, path, line))

    # -- the declaration -----------------------------------------------------------------------------------------
    def load_declaration(self) -> str:
        """"ok", "missing" (reported as a finding) or "invalid" (cannot continue)."""
        path = self.root / ".kokeb/handbook.yml"
        if not path.is_file():
            # KB-REPO-002 applies to every kind, so report it even though the kind is unknown.
            self.kind = "template" if (self.root / "tools/scaffold.py").exists() else "driver"
            self.findings.append(Finding("KB-REPO-002", "handbook-declaration",
                                         ".kokeb/handbook.yml is missing: declare the handbook version, kind and level",
                                         ".kokeb/handbook.yml"))
            return "missing"
        try:
            d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            print(f"::error file=.kokeb/handbook.yml::not valid YAML: {e}")
            return "invalid"
        self.declaration = d
        where = ".kokeb/handbook.yml"
        problems = []
        extra = set(d) - {"handbook", "kind", "level", "waivers", "notes"}
        if extra:
            problems.append(f"unknown keys {sorted(extra)}")
        if not re.fullmatch(r"\d+\.\d+", str(d.get("handbook", ""))):
            problems.append('`handbook` must be a release such as "1.0"')
        if d.get("kind") not in KINDS:
            problems.append(f"`kind` must be one of {', '.join(KINDS)}")
        if d.get("level", "standard") not in LEVELS:
            problems.append(f"`level` must be one of {', '.join(LEVELS)}")
        self.kind = d.get("kind") if d.get("kind") in KINDS else "driver"
        self.level = d.get("level", "standard") if d.get("level", "standard") in LEVELS else "standard"
        for p in problems:
            self.findings.append(Finding("KB-REPO-002", "handbook-declaration", p, where))
        self.check_waivers(d.get("waivers") or [])
        return "ok"

    def check_waivers(self, waivers) -> None:
        where = ".kokeb/handbook.yml"
        if not isinstance(waivers, list):
            self.add("KB-REPO-003", "waivers", "`waivers` must be a list", where)
            return
        for i, w in enumerate(waivers, 1):
            if not isinstance(w, dict):
                self.add("KB-REPO-003", "waivers", f"waiver {i} is not a mapping", where)
                continue
            rule = str(w.get("rule", ""))
            missing = [k for k in ("rule", "reason", "approved_by", "until") if not str(w.get(k, "")).strip()]
            if missing:
                self.add("KB-REPO-003", "waivers", f"waiver {i} ({rule or '?'}) lacks {', '.join(missing)}", where)
                continue
            if rule not in self.rules:
                self.add("KB-REPO-003", "waivers", f"waiver {i} names {rule}, which is not a handbook rule", where)
                continue
            try:
                until = datetime.date.fromisoformat(str(w["until"]))
            except ValueError:
                self.add("KB-REPO-003", "waivers", f"waiver for {rule}: `until` must be YYYY-MM-DD", where)
                continue
            if until < self.today:
                self.add("KB-REPO-003", "waivers", f"the waiver for {rule} expired on {until}", where)
                continue
            if (until - self.today).days <= 30:
                print(f"::warning file={where}::the waiver for {rule} expires on {until}")
            self.waivers[rule] = {"until": until, "reason": str(w["reason"]).strip()}

    # -- the checks ----------------------------------------------------------------------------------------------
    def check_root_layout(self, files: list[str]) -> None:
        """What is committed at the root: build folders and local checkouts are not the repository's layout."""
        if self.kind not in ("driver", "template"):
            return
        entries: dict[str, bool] = {}
        for f in files:
            top, sep, _ = f.partition("/")
            entries[top] = entries.get(top, False) or bool(sep)
        for name, is_dir in sorted(entries.items()):
            if (self.root / name).is_symlink():
                self.add("KB-REPO-005", "repo-layout", f"{name}: a symlink at the root", name)
            elif is_dir and name not in ROOT_DIRS:
                self.add("KB-REPO-005", "repo-layout", f"{name}/ is not an allowed root folder", name)
            elif not is_dir and name not in ROOT_FILES:
                self.add("KB-REPO-005", "repo-layout",
                         f"{name} is not an allowed root file (tool configuration goes in _config/)", name)

    def chip(self) -> tuple[str, str, pathlib.Path | None]:
        """(name, version) from cmake/<chip>_build_settings.cmake."""
        for p in sorted((self.root / "cmake").glob("*_build_settings.cmake")):
            text = p.read_text(encoding="utf-8")
            name = re.search(r'set\(\s*\w+_TARGET_NAME\s+"([^"]+)"', text)
            ver = [re.search(rf"set\(\s*\w+_VERSION_{k}\s+(\d+)\s*\)", text) for k in ("MAJOR", "MINOR", "PATCH")]
            if name and all(ver):
                return name.group(1), ".".join(m.group(1) for m in ver), p
        return "", "", None

    def check_driver_manifest(self) -> None:
        if self.kind not in ("driver", "template"):
            return
        path = self.root / "driver.yml"
        if not path.is_file():
            self.add("KB-REPO-018", "driver-manifest", "driver.yml is missing", "driver.yml")
            return
        try:
            d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            self.add("KB-REPO-018", "driver-manifest", f"driver.yml is not valid YAML: {e}", "driver.yml")
            return
        need = ("name", "version", "bus", "mcus", "peripheral", "kb_core_min")
        missing = [k for k in need if k not in d]
        if missing:
            self.add("KB-REPO-018", "driver-manifest", f"driver.yml lacks {', '.join(missing)}", "driver.yml")
        name, version, settings = self.chip()
        if settings is not None:
            rel = str(settings.relative_to(self.root))
            if d.get("name") != name:
                self.add("KB-REPO-018", "driver-manifest",
                         f"driver.yml name {d.get('name')!r} differs from {rel} ({name!r})", "driver.yml")
            if str(d.get("version")) != version:
                self.add("KB-REPO-018", "driver-manifest",
                         f"driver.yml version {d.get('version')!r} differs from {rel} ({version})", "driver.yml")
        bus = d.get("bus")
        if not isinstance(bus, list) or not bus or not set(bus) <= BUSES:
            self.add("KB-REPO-018", "driver-manifest", f"driver.yml bus must be a list from {sorted(BUSES)}", "driver.yml")
        mcus = d.get("mcus")
        if not isinstance(mcus, list) or not mcus:
            self.add("KB-REPO-018", "driver-manifest", "driver.yml mcus must be a list: [any] or the families", "driver.yml")
        kb = d.get("kb_core_min")
        if kb is not None and not re.fullmatch(r"\d+\.\d+\.\d+", str(kb)):
            self.add("KB-REPO-018", "driver-manifest", "driver.yml kb_core_min must be X.Y.Z or null", "driver.yml")

    def check_cmake(self, files: list[str]) -> None:
        if self.kind not in TARGET_KINDS:
            return
        for f in files:
            if not (f.endswith("CMakeLists.txt") or f.endswith(".cmake")) or f.startswith(("tests/", "examples/")):
                continue
            for n, line in enumerate((self.root / f).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                code = line.split("#", 1)[0]
                if re.search(r"\bfile\s*\(\s*GLOB", code, re.I):
                    self.add("KB-BLD-002", "forbidden-patterns/cmake-glob",
                             "file(GLOB) collects sources; list them explicitly", f, n)
                if re.search(r"CMAKE_CXX_EXTENSIONS\s+ON", code):
                    self.add("KB-CPP-001", "forbidden-patterns/cmake-cxx-standard", "compiler extensions are on", f, n)
        if self.kind in ("driver", "library", "template"):
            texts = [(self.root / f).read_text(encoding="utf-8", errors="replace") for f in files
                     if (f == "CMakeLists.txt" or (f.startswith("cmake/") and f.endswith(".cmake")))]
            if texts and not any(re.search(r"cxx_std_20|CMAKE_CXX_STANDARD\s+20", t) for t in texts):
                self.add("KB-CPP-001", "forbidden-patterns/cmake-cxx-standard",
                         "the library target does not require C++20 (target_compile_features ... cxx_std_20)",
                         "CMakeLists.txt")

    def check_sources(self, files: list[str]) -> None:
        if self.kind not in TARGET_KINDS:
            return
        dirs = ("inc/", "src/", "include/", "lib/")
        for f in files:
            if not f.startswith(dirs) or pathlib.PurePosixPath(f).suffix not in SOURCE_SUFFIXES:
                continue
            text = (self.root / f).read_text(encoding="utf-8", errors="replace")
            for n, line in enumerate(text.splitlines(), 1):
                inc = re.match(r"\s*#\s*include\s*<([^>]+)>", line)
                if inc:
                    h = inc.group(1).strip()
                    if self.kind in ("driver", "template") and h not in DRIVER_HEADERS:
                        self.add("KB-CPP-012", "include-allowlist/driver",
                                 f"<{h}> is not in the driver's target library subset (ADR-0017)", f, n)
                    elif h in BANNED_HEADERS:
                        self.add("KB-CPP-012", "include-allowlist/target",
                                 f"<{h}> allocates, throws or needs an OS (ADR-0017)", f, n)
            code = strip_comments_and_strings(text)
            for n, line in enumerate(code.splitlines(), 1):
                if line.lstrip().startswith("#"):
                    continue
                for pat, msg in HEAP:
                    if pat.search(line):
                        self.add("KB-CPP-003", "forbidden-patterns/heap", msg, f, n)
                # `delete p` frees heap memory; `= delete` removes a function and is fine.
                for m in re.finditer(r"\bdelete\b", line):
                    if not re.search(r"=\s*$", line[:m.start()]):
                        self.add("KB-CPP-003", "forbidden-patterns/heap",
                                 "operator delete: there is no heap to return to", f, n)
                for pat, msg in EXCEPTIONS_RTTI:
                    if pat.search(line):
                        self.add("KB-CPP-002", "forbidden-patterns/exceptions-rtti", msg, f, n)
                if self.kind in ("driver", "template") and re.search(r"\bvirtual\b", line):
                    self.add("KB-ARCH-011", "forbidden-patterns/virtual-outside-interfaces",
                             "a driver has no virtual functions; ports use CRTP (ADR-0016)", f, n)

    def check_tracked(self, files: list[str]) -> None:
        for f in files:
            name = pathlib.PurePosixPath(f).name
            if name == "sdkconfig":
                self.add("KB-REPO-016", "tracked-files/sdkconfig",
                         "the generated sdkconfig is committed; keep settings in sdkconfig.defaults (ADR-0018)", f)
            if f.lower().endswith(".pdf") and f.startswith("docs/"):
                self.add("KB-DOC-035", "tracked-files/datasheets",
                         "a PDF is committed; reference datasheets by revision in docs/datasheets.yml (ADR-0019)", f)

    # -- result ----------------------------------------------------------------------------------------------------
    def settle(self) -> None:
        for f in self.findings:
            r = self.rules.get(f.rule, {})
            if f.rule in self.waivers:
                w = self.waivers[f.rule]
                f.severity = "notice"
                f.message += f" [waived until {w['until']}: {w['reason']}]"
            elif r.get("status") == "proposed" and r.get("enforce_from") and \
                    datetime.date.fromisoformat(r["enforce_from"]) > self.today:
                f.severity = "warning"
                f.message += f" [fails CI from {r['enforce_from']}]"
            elif r.get("level") != "must":
                f.severity = "warning"


HEAP = [
    (re.compile(r"(?<![\w:])new\b(?!\s*\()"), "operator new allocates from the heap"),
    (re.compile(r"\b(?:std::)?(?:malloc|calloc|realloc|free|aligned_alloc|strdup)\s*\("), "a C heap function"),
    (re.compile(r"\bstd::(?:make_unique|make_shared|allocate_shared)\b"), "a heap-owning smart pointer"),
]
EXCEPTIONS_RTTI = [
    (re.compile(r"\bthrow\b"), "throw: errors are values (Result<T>), not exceptions"),
    (re.compile(r"\btry\s*\{"), "try: no exceptions in target code"),
    (re.compile(r"\bcatch\s*\("), "catch: no exceptions in target code"),
    (re.compile(r"\btypeid\s*\("), "typeid needs RTTI"),
    (re.compile(r"\bdynamic_cast\s*<"), "dynamic_cast needs RTTI"),
]


def strip_comments_and_strings(text: str) -> str:
    """Blank out comments, string and character literals, keeping every newline so line numbers stay right."""
    out, i, n = [], 0, len(text)
    while i < n:
        c, nxt = text[i], text[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c == "/" and nxt == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j]))
            i = j
        elif c == "R" and nxt == '"':
            m = re.match(r'R"([^(\s]*)\(', text[i:])
            if m:
                end = text.find(f'){m.group(1)}"', i)
                j = n if end < 0 else end + len(m.group(1)) + 2
                out.append(re.sub(r"[^\n]", " ", text[i:j]))
                i = j
            else:
                out.append(c)
                i += 1
        elif c in "\"'":
            # A digit separator (1'000) is not a character literal.
            if c == "'" and i > 0 and text[i - 1].isalnum():
                out.append(c)
                i += 1
                continue
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(c + " " * max(0, j - i - 2) + (c if j - i >= 2 else ""))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--rules", default=str(HERE / "rules.json"))
    ap.add_argument("--today", default="")
    ap.add_argument("--report", default="")
    a = ap.parse_args()
    root = pathlib.Path(a.repo).resolve()
    rules = json.loads(pathlib.Path(a.rules).read_text(encoding="utf-8"))["rules"]
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
    repo = Repo(root, rules, today)
    if repo.load_declaration() == "invalid":
        return 2
    files = repo.tracked()
    repo.check_root_layout(files)
    repo.check_driver_manifest()
    repo.check_cmake(files)
    repo.check_sources(files)
    repo.check_tracked(files)
    repo.settle()

    order = {"error": 0, "warning": 1, "notice": 2}
    repo.findings.sort(key=lambda f: (order[f.severity], f.rule, f.path, f.line))
    for f in repo.findings:
        r = rules.get(f.rule, {})
        url = f"{HANDBOOK_URL}/{r.get('area', '')}/#{f.rule.lower()}"
        loc = f" file={f.path}" + (f",line={f.line}" if f.line else "") if f.path else ""
        print(f"::{f.severity}{loc}::{f.rule} {r.get('title', '')}: {f.message} ({url})")
    errors = sum(f.severity == "error" for f in repo.findings)
    warnings = sum(f.severity == "warning" for f in repo.findings)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    lines = [f"### Handbook check: {repo.kind}, {repo.level} level, handbook {repo.declaration.get('handbook', '?')}",
             "", f"{errors} error(s), {warnings} warning(s), {len(repo.waivers)} waiver(s).", ""]
    if repo.findings:
        lines += ["| | Rule | Where | Finding |", "| --- | --- | --- | --- |"]
        for f in repo.findings[:200]:
            where = f"`{f.path}:{f.line}`" if f.line else (f"`{f.path}`" if f.path else "")
            lines.append(f"| {f.severity} | [{f.rule}]({HANDBOOK_URL}/{rules.get(f.rule, {}).get('area', '')}/"
                         f"#{f.rule.lower()}) | {where} | {f.message} |")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))
    if a.report:
        pathlib.Path(a.report).write_text(json.dumps([dataclasses.asdict(f) for f in repo.findings], indent=1),
                                          encoding="utf-8")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"errors={errors}\nwarnings={warnings}\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
