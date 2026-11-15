#!/usr/bin/env python3
"""Check a driver's declared C++ language standard against the organisation registry and against its own files.

    python3 check_standards.py --repo DIR [--standards standards.yml] [--today YYYY-MM-DD] [--require] [--base-ref REF] [--report out.json]
    python3 check_standards.py --registry          # validate standards.yml itself

A driver declares its language once, in the `language:` block of driver.yml:

    language:
      standard: 20               # the minimum ISO C++ standard (the floor); a consumer needs at least this
      profile: KB-CPP20          # a profile id of standards.yml
      profile_version: "1.0"     # the handbook release that defines the profile
      misra: "MISRA C++:2023"    # the MISRA edition the driver is analysed against
      compilers:                 # the oldest versions the driver promises to build with
        gcc: "10"
        clang: "13"
      tested: [20]               # every standard CI compiles the headers under (includes `standard`)
      effective_from: 2026-11-15 # the date this declaration took effect

Findings (LANG-nnn) are errors unless marked otherwise:

  001 note     no `language:` block: the registry default is assumed (error with --require)
  002         the block is malformed (missing key, wrong type, bad date)
  003         the profile is not in standards.yml
  004         the profile is retired (or its `supported_until` has passed)
  005 warning  the profile is in preview; 006 note: the profile is supported but a newer one is current
  007         `standard` differs from the profile's standard
  008         `profile_version` is not a handbook release of the profile
  009         `misra` is not an edition the profile allows
  010         a compiler key is unknown, or a floor is below the profile's floor
  011         `tested` does not include `standard`, names a standard that is not accepted, or is not a list of ints
  012         `effective_from` is in the future or before the profile's `since`
  040         the minimum standard was raised, or a tested standard dropped, against --base-ref, and CHANGELOG.md has no
              `### Breaking` entry (Unreleased, or the version section this change adds) (raising the minimum is a
              breaking change: a minor release before 1.0, a major release after)
  020         the build does not require the declared standard (no cxx_std_N in the CMake files)
  021         a file names another standard: cxx_std_N, CMAKE_CXX_STANDARD, `Standard: c++N` (clang-format) or a
              `__cplusplus ==` assertion differs from `standard`; `-std=c++N` or a `std:` workflow input is outside `tested`
  022         the CI standard matrix differs from `tested`
  030 warning  README: the C++ badge is missing; 031: the badge, prose in README.md and docs/ ("a C++20 compiler") or compiler floors
              ("GCC 10+") differ from the block

Exit status: 0 no error, 1 at least one error, 2 the registry or the declaration cannot be read.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
STATUSES = ("current", "supported", "preview", "retired")
BLOCK_KEYS = ("standard", "profile", "profile_version", "misra", "compilers", "tested", "effective_from")
SKIP_DIRS = {".git", ".venv", "venv", "site", "_site", "node_modules", "third_party", "__pycache__", ".driver-template"}
SKIP_PREFIXES = ("build", "cmake-build")
TEXT_SUFFIXES = {".cmake", ".txt", ".yml", ".yaml", ".sh", ".py", ".cpp", ".hpp", ".md", ""}
# __cplusplus values and the standard each stands for (GCC 11 to 13 report 202100 for C++23).
CPLUSPLUS_STD = {201402: 14, 201703: 17, 202002: 20, 202100: 23, 202302: 23}
PROSE_RE = re.compile(r"(?:\b(?:[Aa]|an|requires|needs|Header-only|ISO)\s+|brings the headers and )C\+\+(\d\d)\b|"
                      r"(?:^|(?<=\s))C\+\+(\d\d) (?:compiler|driver|library)\b")
README_FLOORS = {"gcc": r"GCC", "clang": r"Clang"}


@dataclasses.dataclass
class Finding:
    code: str
    message: str
    path: str = ""
    line: int = 0
    severity: str = "error"  # error | warning | note

    def text(self) -> str:
        where = f"{self.path}:{self.line}: " if self.path and self.line else f"{self.path}: " if self.path else ""
        return f"{self.severity}: {where}LANG-{self.code} {self.message}"


class Unreadable(Exception):
    pass


def version_key(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in str(v).split("."))
    except ValueError:
        raise Unreadable(f"{v!r} is not a dotted version number") from None


def load_registry(path: Path) -> dict:
    try:
        reg = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        raise Unreadable(f"{path}: {e}") from None
    problems = registry_problems(reg)
    if problems:
        raise Unreadable(f"{path}: " + "; ".join(problems))
    return reg


def registry_problems(reg: object) -> list[str]:
    """Rules that keep standards.yml itself coherent."""
    if not isinstance(reg, dict) or reg.get("schema") != 1:
        return ["schema must be 1"]
    bad: list[str] = []
    profiles = reg.get("profiles")
    keys = reg.get("compilers")
    if not isinstance(profiles, dict) or not profiles:
        return ["profiles is empty"]
    if not isinstance(keys, dict) or not keys:
        bad.append("compilers must list the compiler keys")
        keys = {}
    current = []
    for pid, p in profiles.items():
        if not isinstance(p, dict):
            bad.append(f"{pid}: not a mapping")
            continue
        for need in ("standard", "status", "misra", "cmake", "flag", "cplusplus", "compilers", "handbook_versions"):
            if need not in p:
                bad.append(f"{pid}: lacks {need}")
        if p.get("status") not in STATUSES:
            bad.append(f"{pid}: status must be one of {', '.join(STATUSES)}")
        if p.get("status") == "current":
            current.append(pid)
        if p.get("status") == "retired" and not p.get("retired_on"):
            bad.append(f"{pid}: a retired profile needs retired_on")
        if not re.fullmatch(r"KB-CPP\d\d", str(pid)) or str(p.get("standard")) != str(pid)[-2:]:
            bad.append(f"{pid}: the id must be KB-CPP<standard>")
        if p.get("flag") != f"c++{p.get('standard')}" or p.get("cmake", {}).get("feature") != f"cxx_std_{p.get('standard')}":
            bad.append(f"{pid}: flag and cmake.feature must be c++{p.get('standard')} and cxx_std_{p.get('standard')}")
        floors = p.get("compilers") or {}
        if set(floors) - set(keys):
            bad.append(f"{pid}: compiler keys not listed under compilers: {sorted(set(floors) - set(keys))}")
        for k, v in floors.items():
            if not isinstance(v, str):
                bad.append(f"{pid}: compilers.{k} must be a quoted string")
    if len(current) != 1:
        bad.append(f"exactly one profile must be current (found {current})")
    default = reg.get("default")
    if default not in profiles or profiles[default].get("status") != "current":
        bad.append("default must name the current profile")
    nxt = reg.get("next")
    if nxt is not None and (nxt not in profiles or profiles[nxt].get("status") != "preview"):
        bad.append("next must name a preview profile or be null")
    return bad


def effective_status(profile: dict, today: datetime.date) -> str:
    until = profile.get("supported_until")
    if profile["status"] in ("current", "supported") and until and parse_date(until) < today:
        return "retired"
    return profile["status"]


def parse_date(value: object) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        raise Unreadable(f"{value!r} is not a date (YYYY-MM-DD)") from None


class Check:
    def __init__(self, root: Path, reg: dict, today: datetime.date, require: bool):
        self.root = root
        self.reg = reg
        self.today = today
        self.require = require
        self.findings: list[Finding] = []
        self.block: dict = {}
        self.profile: dict = {}
        self.standard = 0
        self.tested: list[int] = []

    def add(self, code: str, message: str, path: str = "", line: int = 0, severity: str = "error") -> None:
        self.findings.append(Finding(code, message, path, line, severity))

    # -- the declaration -------------------------------------------------------------------------------------
    def read_block(self) -> bool:
        path = self.root / "driver.yml"
        if not path.is_file():
            return False  # a library or a repository without a manifest declares nothing
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            raise Unreadable(f"driver.yml is not valid YAML: {e}") from None
        block = doc.get("language") if isinstance(doc, dict) else None
        if block is None:
            default = self.reg["default"]
            self.add("001", f"driver.yml has no language block; {default} is assumed "
                     f"(add `language:` with standard {self.reg['profiles'][default]['standard']})",
                     "driver.yml", severity="error" if self.require else "note")
            return False
        if not isinstance(block, dict):
            self.add("002", "language must be a mapping", "driver.yml")
            return False
        self.block = block
        return True

    def shape(self) -> bool:
        b = self.block
        ok = True
        for k in BLOCK_KEYS:
            if k not in b:
                self.add("002", f"language.{k} is missing", "driver.yml")
                ok = False
        for k in set(b) - set(BLOCK_KEYS):
            self.add("002", f"language.{k} is not a known key (known: {', '.join(BLOCK_KEYS)})", "driver.yml")
            ok = False
        if not ok:
            return False
        if not isinstance(b["standard"], int) or isinstance(b["standard"], bool):
            self.add("002", "language.standard must be an integer such as 20", "driver.yml")
            ok = False
        for k in ("profile", "profile_version", "misra"):
            if not isinstance(b[k], str) or not b[k]:
                self.add("002", f"language.{k} must be a quoted, non-empty string", "driver.yml")
                ok = False
        comp = b["compilers"]
        if not isinstance(comp, dict) or not comp or any(not isinstance(v, str) for v in comp.values()):
            self.add("002", "language.compilers must map a compiler key to a quoted version string "
                     '(gcc: "10"; an unquoted 19.30 is read as a number)', "driver.yml")
            ok = False
        t = b["tested"]
        if not isinstance(t, list) or not t or any(not isinstance(x, int) or isinstance(x, bool) for x in t):
            self.add("011", "language.tested must be a list of integers such as [20]", "driver.yml")
            ok = False
        try:
            parse_date(b["effective_from"])
        except Unreadable as e:
            self.add("002", f"language.effective_from: {e}", "driver.yml")
            ok = False
        return ok

    def against_registry(self) -> None:
        b = self.block
        profiles = self.reg["profiles"]
        pid = b["profile"]
        if pid not in profiles:
            self.add("003", f"profile {pid} is not in standards.yml (known: {', '.join(profiles)})", "driver.yml")
            return
        p = self.profile = profiles[pid]
        status = effective_status(p, self.today)
        if status == "retired":
            self.add("004", f"profile {pid} is retired: move to {self.reg['default']} (docs/language-standards.md)",
                     "driver.yml")
        elif status == "preview":
            self.add("005", f"profile {pid} is a preview: its rules and compiler floors may still change",
                     "driver.yml", severity="warning")
        elif status == "supported":
            self.add("006", f"profile {pid} is supported; {self.reg['default']} is current", "driver.yml",
                     severity="note")
        if b["standard"] != p["standard"]:
            self.add("007", f"standard {b['standard']} differs from profile {pid} (C++{p['standard']})", "driver.yml")
        if str(b["profile_version"]) not in [str(v) for v in p["handbook_versions"]] and p["handbook_versions"]:
            self.add("008", f"profile_version {b['profile_version']!r} is not a handbook release of {pid} "
                     f"(known: {', '.join(map(str, p['handbook_versions']))})", "driver.yml")
        if b["misra"] not in p["misra"]:
            self.add("009", f"misra {b['misra']!r} is not allowed for {pid} (allowed: {', '.join(p['misra'])})",
                     "driver.yml")
        for key, ver in b["compilers"].items():
            if key not in self.reg["compilers"]:
                self.add("010", f"compiler {key!r} is not a known key ({', '.join(self.reg['compilers'])})", "driver.yml")
                continue
            floor = p["compilers"].get(key)
            try:
                if floor is not None and version_key(ver) < version_key(floor):
                    self.add("010", f"compilers.{key} {ver} is below the {pid} floor {floor}: the profile needs "
                             f"{key} {floor} or newer", "driver.yml")
            except Unreadable as e:
                self.add("002", f"language.compilers.{key}: {e}", "driver.yml")
        accepted = {int(q["standard"]) for q in profiles.values()
                    if effective_status(q, self.today) in ("current", "supported", "preview")}
        t = b["tested"]
        if b["standard"] not in t:
            self.add("011", f"tested {t} must include the declared standard {b['standard']}", "driver.yml")
        for s in t:
            if s not in accepted:
                self.add("011", f"tested names C++{s}, which no accepted profile has", "driver.yml")
            elif s < b["standard"]:
                self.add("011", f"tested names C++{s}, below the declared minimum {b['standard']}", "driver.yml")
        eff = parse_date(b["effective_from"])
        if eff > self.today:
            self.add("012", f"effective_from {eff} is in the future", "driver.yml")
        since = p.get("since")
        if since and eff < parse_date(since):
            self.add("012", f"effective_from {eff} is before profile {pid} existed ({since})", "driver.yml")

    # -- the files -------------------------------------------------------------------------------------------
    def files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(SKIP_PREFIXES))
            for name in sorted(filenames):
                p = Path(dirpath) / name
                if p.relative_to(self.root).as_posix() == "tools/check_language.py":
                    continue  # the template's own checker holds seeded wrong standards for its self-test
                if p.suffix in TEXT_SUFFIXES or name == "CMakeLists.txt" or name == ".clang-format":
                    yield p

    def lines(self, p: Path):
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        yield from enumerate(text.splitlines(), 1)

    def sites(self) -> None:
        std = self.standard = self.block["standard"]
        tested = self.tested = list(self.block["tested"])
        cmake_seen = False
        matrix: set[int] = set()
        matrix_at = ""
        for p in self.files():
            rel = p.relative_to(self.root).as_posix()
            is_cmake = p.name == "CMakeLists.txt" or p.suffix == ".cmake"
            is_workflow = rel.startswith(".github/workflows/") and p.suffix in (".yml", ".yaml")
            in_docs = rel.startswith("docs/") or p.suffix == ".md"
            for n, line in self.lines(p):
                code = line.split("#", 1)[0] if (is_cmake or is_workflow) else line
                if is_cmake:
                    for m in re.finditer(r"\bcxx_std_(\d\d)\b", code):
                        if rel in ("CMakeLists.txt",) or rel.startswith("cmake/"):
                            cmake_seen = cmake_seen or int(m.group(1)) == std
                        if int(m.group(1)) != std:
                            self.add("021", f"cxx_std_{m.group(1)} but language.standard is {std}", rel, n)
                    for m in re.finditer(r"\bCMAKE_CXX_STANDARD\s+(\d\d)\b", code):
                        cmake_seen = cmake_seen or (int(m.group(1)) == std and rel.count("/") == 0)
                        if int(m.group(1)) != std:
                            self.add("021", f"CMAKE_CXX_STANDARD {m.group(1)} but language.standard is {std}", rel, n)
                if p.name == ".clang-format":
                    m = re.match(r"\s*Standard:\s*c\+\+(\d\d)\b", line)
                    if m and int(m.group(1)) != std:
                        self.add("021", f"clang-format Standard c++{m.group(1)} but language.standard is {std}", rel, n)
                if not in_docs:
                    for m in re.finditer(r"__cplusplus\s*==\s*(\d{6})L", code):
                        found = CPLUSPLUS_STD.get(int(m.group(1)))
                        if found != std:
                            self.add("021", f"__cplusplus == {m.group(1)}L is "
                                     f"{'C++' + str(found) if found else 'no known standard'}, "
                                     f"language.standard is {std}", rel, n)
                    for m in re.finditer(r"(?<![\w-])-{1,2}std=(?:gnu|c)\+\+(\d\d)\b", code):
                        if int(m.group(1)) not in tested:
                            self.add("021", f"-std=c++{m.group(1)} is not in language.tested {tested}", rel, n)
                if is_workflow:
                    m = re.match(r"\s*(?:cppcheck_std|std|cxx_std|cpp_std)\s*:\s*[\"']?c?(?:\+\+)?(\d\d)[\"']?\s*$", code)
                    if m and int(m.group(1)) not in tested:
                        self.add("021", f"workflow standard {m.group(1)} is not in language.tested {tested}", rel, n)
                    m = re.match(r"\s*(?:std|cxx_std|cpp_std|standard)\s*:\s*\[([\d,\s]+)\]", code)
                    if m:
                        found = {int(x) for x in re.findall(r"\d+", m.group(1))}
                        matrix |= found
                        matrix_at = f"{rel}:{n}"
        if not cmake_seen and (self.root / "CMakeLists.txt").is_file():
            self.add("020", f"no cxx_std_{std} (or CMAKE_CXX_STANDARD {std}) in CMakeLists.txt or cmake/: the target "
                     "does not require the declared standard", "CMakeLists.txt")
        if matrix and matrix != set(tested):
            self.add("022", f"the CI standard matrix {sorted(matrix)} differs from language.tested {sorted(tested)}",
                     matrix_at.split(":")[0], int(matrix_at.split(":")[1]))
        self.readme()

    def prose_files(self):
        readme = self.root / "README.md"
        if readme.is_file():
            yield readme
        for p in sorted(self.root.rglob("*.md")):
            rel = p.relative_to(self.root).as_posix()
            if p == readme or any(part in SKIP_DIRS or part.startswith(SKIP_PREFIXES) for part in rel.split("/")[:-1]):
                continue
            if rel.startswith(("docs/adr/", ".claude/", ".github/")) or rel in ("CHANGELOG.md", "docs/changelog.md"):
                continue
            if rel.startswith(("docs/", "examples/")):
                yield p

    def readme(self) -> None:
        readme = self.root / "README.md"
        if readme.is_file() and not re.search(r"img\.shields\.io/badge/C%2B%2B-\d\d", readme.read_text(encoding="utf-8")):
            self.add("030", "no C++ standard badge (shields.io/badge/C%2B%2B-NN)", "README.md", severity="warning")
        std = self.standard
        for p in self.prose_files():
            rel = p.relative_to(self.root).as_posix()
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                for m in re.finditer(r"img\.shields\.io/badge/C%2B%2B-(\d\d)", line):
                    if int(m.group(1)) != std:
                        self.add("031", f"badge says C++{m.group(1)}, language.standard is {std}", rel, n)
                if "KB-CPP" not in line:  # a line about a profile's own rules keeps the profile's standard
                    for m in PROSE_RE.finditer(line):
                        found = int(m.group(1) or m.group(2))
                        if found != std:
                            self.add("031", f"text says C++{found}, language.standard is {std}", rel, n)
                for key, word in README_FLOORS.items():
                    for m in re.finditer(rf"\b{word} (\d+(?:\.\d+)*)\+", line):
                        have = self.block["compilers"].get(key)
                        if have is not None and version_key(m.group(1)) != version_key(have):
                            self.add("031", f"text says {word} {m.group(1)}+, language.compilers.{key} is {have}",
                                     rel, n)


def base_block(root: Path, ref: str) -> dict | None:
    """The language block of driver.yml at a git ref (None when the file or the block did not exist)."""
    done = subprocess.run(["git", "show", f"{ref}:driver.yml"], cwd=root, capture_output=True, text=True)
    if done.returncode != 0:
        return None
    try:
        doc = yaml.safe_load(done.stdout) or {}
    except yaml.YAMLError:
        return None
    block = doc.get("language") if isinstance(doc, dict) else None
    return block if isinstance(block, dict) else None


def breaking_recorded(root: Path) -> bool:
    """CHANGELOG.md has a `### Breaking` heading in Unreleased or in the top version section."""
    path = root / "CHANGELOG.md"
    if not path.is_file():
        return False
    sections = re.split(r"^## \[", path.read_text(encoding="utf-8"), flags=re.M)[1:]
    wanted = [sec for sec in sections if sec.startswith("Unreleased")]
    wanted += [sec for sec in sections if re.match(r"\d+\.\d+\.\d+\]", sec)][:1]
    return any(re.search(r"^### Breaking\b", sec, re.M) for sec in wanted)


def against_base(root: Path, block: dict, ref: str) -> list[Finding]:
    old = base_block(root, ref)
    if old is None or not isinstance(old.get("standard"), int):
        return []  # the block is new: nothing to compare
    raised = isinstance(block.get("standard"), int) and block["standard"] > old["standard"]
    dropped = sorted(set(old.get("tested") or []) - set(block.get("tested") or [])) \
        if isinstance(block.get("tested"), list) else []
    if (raised or dropped) and not breaking_recorded(root):
        what = f"raises language.standard from {old['standard']} to {block['standard']}" if raised \
            else f"drops {dropped} from language.tested"
        return [Finding("040", f"this change {what}: that is a breaking change for consumers; add a `### Breaking` "
                        "entry to CHANGELOG.md (a minor release before 1.0, a major release after)", "CHANGELOG.md")]
    return []


def run(root: Path, standards: Path, today: datetime.date, require: bool, base_ref: str | None = None) -> list[Finding]:
    reg = load_registry(standards)
    c = Check(root, reg, today, require)
    if c.read_block() and c.shape():
        c.against_registry()
        if c.profile:
            c.sites()
        if base_ref:
            c.findings += against_base(root, c.block, base_ref)
    return c.findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--standards", default=str(HERE / "standards.yml"))
    ap.add_argument("--today", default=None, help="YYYY-MM-DD (default: today)")
    ap.add_argument("--require", action="store_true", help="a missing language block is an error")
    ap.add_argument("--base-ref", default=None, help="a git ref (the pull request's base): compare with driver.yml there")
    ap.add_argument("--registry", action="store_true", help="only validate standards.yml")
    ap.add_argument("--report", default=None, help="write the findings as JSON")
    a = ap.parse_args(argv)
    try:
        today = parse_date(a.today) if a.today else datetime.date.today()
        if a.registry:
            load_registry(Path(a.standards))
            print("standards.yml is coherent")
            return 0
        findings = run(Path(a.repo).resolve(), Path(a.standards), today, a.require, a.base_ref)
    except Unreadable as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for f in findings:
        print(f.text())
        if os.environ.get("GITHUB_ACTIONS") and f.severity != "note":
            print(f"::{f.severity} file={f.path or 'driver.yml'}{',line=' + str(f.line) if f.line else ''}::"
                  f"LANG-{f.code} {f.message}")
    if a.report:
        Path(a.report).write_text(json.dumps([dataclasses.asdict(f) for f in findings], indent=2) + "\n")
    errors = [f for f in findings if f.severity == "error"]
    print(f"language standard: {len(errors)} error(s), {sum(f.severity == 'warning' for f in findings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
