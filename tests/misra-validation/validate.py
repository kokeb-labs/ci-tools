#!/usr/bin/env python3
"""Tool-validation suite of the MISRA C++:2023 toolchain (docs/tool-validation/plan.md).

The compliance matrix claims that a tool decides a guideline: a compiler flag, a clang-tidy check, a CodeQL query.
Each claim is a requirement here (docs/tool-validation/plan.md, "Requirements"), and each requirement has test
cases: seeded violations in `bad*` files (true positives, with the edge cases the guideline targets), compliant
code in `ok*` files (true negatives, with near misses that must not be flagged), and the exact rule id the tool
must report: the warning option, the clang-tidy check name, or the CodeQL query id and its guideline tag.

A case is a directory under cases/ (or under codeql/<pack>/validation/ for the own profile) with a `case.yml`:

    guideline: Rule 0.2.2            # Dir 5.7.2, or KB-CPP-046 for an own-profile rule
    gcc:   {flag: unused-parameter}  # diagnostic names [-Wunused-parameter] (GCC [-Werror=...], Clang [-Werror,-W...])
    clang: {flag: unused-parameter}  # or message: <regex> (no option name), or error: <regex> (a hard error)
    clang-tidy: {check: readability-braces-around-statements, options: {}, config: {}, message: <regex>}
    codeql: {queries: [cpp/misra/unused-parameter-misra-cpp]}
    seeded: [...]                    # each violating form the bad files seed, edge cases included (one line each)
    near_misses: [...]               # each compliant form in the ok files that resembles a violation
    targets: [host, cortex-m]        # where the files must build and CodeQL must hold (default: both)
    compiles: false                  # bad files are hard errors by design (no CodeQL claim can be proven then)
    other_findings: [{query, why}]   # reviewed results of OTHER queries on ok files; why "misfire: ..." = false positive
    known_misses: [{query, why, kind: false-negative|false-positive, targets}]   # anomalies of the CLAIMED query

Files: `bad*` and `ok*` with .cpp (a translation unit) or .hpp/.ipp (compiled through a generated one-line unit).
Anything else in the directory (e.g. a .inc included by a bad file) is a support file.

Each seeded violation in a bad file ends its line with `// seeded` (`// seeded@-1` on the next line when the line
cannot end in a comment, e.g. one spliced by a backslash): every tool the case claims must report on that
line (a CodeQL claim: at least one of its queries). `// seeded: codeql` or `// seeded: gcc,clang-tidy` names the
tools that report there when the others report the same form on another marked line. So a bad file that seeds
three forms proves three detections, not one; a bad file without a marker is a malformed case.

Commands (each writes a results JSON; `record` turns them into requirements, traceability and the report):

    validate.py compilers [--gcc g++-14] [--clang clang++-18] [--arm arm-none-eabi-g++] --results F
    validate.py tidy [--clang-tidy clang-tidy] --results F
    validate.py build --side bad|ok --target host|cortex-m --cxx g++ [--out DIR]     the build CodeQL traces
    validate.py codeql --bad bad.sarif --ok ok.sarif --target host|cortex-m --results F
    validate.py record --results-dir DIR --matrix misra-cpp-2023.yml [--check] [--out DIR]
    validate.py local --codeql BIN --pack DIR [...]                                  everything, on this machine

`--only REGEX` (or VALIDATE_ONLY) selects cases by directory name. Exit status: 0 when every claim holds, 1 when
one fails, 2 on a malformed case.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOTS = [os.path.join(HERE, "cases")] + sorted(glob.glob(os.path.join(REPO, "codeql", "*", "validation")))
TOOLCHAIN = os.path.join(REPO, "tools", "misra", "toolchain.json")
RECORD = os.path.join(HERE, "validation-record.json")
ANOMALIES = os.path.join(HERE, "anomalies.yml")
SUPPORTED = os.path.join(HERE, "codeql-supported.json")
TRACE_DOC = os.path.join(REPO, "docs", "tool-validation", "traceability.md")

# The compile flags every compliant file must build with: the org warning set at the safety level. The
# compiler-decided guidelines of the matrix rely on exactly these (ru-misra checks the caller's build uses them).
ORG_FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wshadow", "-Wundef", "-Werror",
             "-fno-exceptions", "-fno-rtti"]
# The CodeQL databases are traced with the language flags the scans build with (-fno-exceptions changes what the
# extractor records, e.g. noexcept), warnings off so a bad file's diagnostics do not stop the trace.
CODEQL_FLAGS = ["-std=c++20", "-fno-exceptions", "-fno-rtti", "-w"]
TARGETS = ("host", "cortex-m")
NO_EH = ("-fno-exceptions", "-fno-rtti")
EH_RE = re.compile(r"\b(try|catch|throw|typeid|dynamic_cast)\b")
HEADER_EXT = (".hpp", ".ipp")
SOURCE_EXT = (".cpp",) + HEADER_EXT
TOOLS = ("gcc", "clang", "clang-tidy", "codeql")
SEEDED_RE = re.compile(r"//\s*seeded(?:@(-[1-9]))?(?::\s*([a-z-]+(?:\s*,\s*[a-z-]+)*))?\s*$")
# GCC prints some preprocessor errors without a column (`f.cpp:2: error: unterminated #if`).
DIAG_RE = re.compile(r"^(.*?):(\d+):(?:\d+:)? (?:fatal )?(?:warning|error): (.*)$", re.M)


def seeded_lines(path: str) -> dict[int, set[str] | None]:
    """The marked lines of a bad file: line -> the tools that must report there (None: every claimed tool)."""
    marks = {}
    with open(path, encoding="utf-8") as fh:
        for n, text in enumerate(fh, 1):
            m = SEEDED_RE.search(text.rstrip("\n"))
            if m:
                tools = {t.strip() for t in m.group(2).split(",")} if m.group(2) else None
                if tools and tools - set(TOOLS):
                    raise CaseError(f"{rel(path)}:{n}: unknown tool in the seeded marker: {sorted(tools - set(TOOLS))}")
                # `// seeded@-1`: the violation is reported on the line above, which cannot end in a comment
                # (a line spliced by a backslash).
                marks[n + int(m.group(1) or 0)] = tools
    return marks


def lines_for(marks: dict[int, set[str] | None], tool: str) -> list[int]:
    """The marked lines a tool must report on (the cross GCC is held to the gcc markers)."""
    tool = "gcc" if tool == "gcc-arm" else tool
    return sorted(n for n, tools in marks.items() if tools is None or tool in tools)


def diag_lines(out: str, path: str, match) -> set[int]:
    """Lines of `path` where a diagnostic whose text satisfies `match` is reported."""
    return {int(m.group(2)) for m in DIAG_RE.finditer(out)
            if os.path.abspath(m.group(1)) == os.path.abspath(path) and match(m.group(3))}
CASE_KEYS = {"guideline", "gcc", "clang", "clang-tidy", "codeql", "other_findings", "compiles", "notes",
             "known_misses", "targets", "seeded", "near_misses"}


def load_toolchain() -> dict:
    with open(TOOLCHAIN, encoding="utf-8") as fh:
        return json.load(fh)


CORTEX_FLAGS = load_toolchain()["cortex_m"]["flags"].split()
ONLY = os.environ.get("VALIDATE_ONLY", "")


class CaseError(Exception):
    pass


def guideline_slug(gid: str) -> str:
    """Rule 8.2.5 -> rule-8-2-5 (the tag in a CodeQL query's metadata); KB-CPP-046 -> kb-cpp-046."""
    m = re.fullmatch(r"(Rule|Dir) (\d+(?:\.\d+)+)", gid)
    if m:
        return f"{m.group(1).lower()}-{m.group(2).replace('.', '-')}"
    return gid.lower()


def rel(path: str) -> str:
    return os.path.relpath(path, REPO).replace(os.sep, "/")


def load_cases(only: str | None = None) -> list[dict]:
    only = ONLY if only is None else only
    cases = []
    for root in ROOTS:
        for path in sorted(glob.glob(os.path.join(root, "*", "case.yml"))):
            d = os.path.dirname(path)
            if only and not re.search(only, os.path.basename(d)):
                continue
            with open(path, encoding="utf-8") as fh:
                spec = yaml.safe_load(fh) or {}
            if "guideline" not in spec:
                raise CaseError(f"{rel(path)}: no guideline")
            unknown = set(spec) - CASE_KEYS
            if unknown:
                raise CaseError(f"{rel(path)}: unknown keys {sorted(unknown)}")
            files = sorted(os.listdir(d))
            spec["name"] = rel(d)
            spec["dir"] = d
            spec["bad"] = [os.path.join(d, f) for f in files if f.startswith("bad") and f.endswith(SOURCE_EXT)]
            spec["ok"] = [os.path.join(d, f) for f in files if f.startswith("ok") and f.endswith(SOURCE_EXT)]
            spec["targets"] = spec.get("targets") or list(TARGETS)
            if set(spec["targets"]) - set(TARGETS):
                raise CaseError(f"{rel(path)}: targets must be among {TARGETS}")
            if not spec["bad"] or not spec["ok"]:
                raise CaseError(f"{rel(path)}: needs at least one bad* and one ok* .cpp/.hpp/.ipp file")
            if not any(t in spec for t in TOOLS):
                raise CaseError(f"{rel(path)}: names no tool")
            spec["marks"] = {f: seeded_lines(f) for f in spec["bad"]}
            for f, marks in spec["marks"].items():
                if not marks:
                    raise CaseError(f"{rel(f)}: no `// seeded` marker: mark the line of each seeded violation")
                for tools in marks.values():
                    if tools and not tools & set(spec) - {"other_findings"}:
                        raise CaseError(f"{rel(f)}: a seeded marker names {sorted(tools)}, which the case does "
                                        "not claim")
            for m in spec.get("known_misses") or []:
                m.setdefault("tool", "codeql")
                m.setdefault("kind", "false-negative")
                if m["kind"] not in ("false-negative", "false-positive"):
                    raise CaseError(f"{rel(path)}: known_misses kind must be false-negative or false-positive")
            cases.append(spec)
    return cases


def tu_for(path: str, tmp: str) -> str:
    """The file to hand to the compiler: a header goes through a one-line translation unit."""
    if path.endswith(HEADER_EXT):
        # One unit per call: jobs for several compilers compile the same header in parallel.
        fd, tu = tempfile.mkstemp(prefix=re.sub(r"[^A-Za-z0-9]+", "_", rel(path)) + "_", suffix=".cpp", dir=tmp)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(f'#include "{os.path.abspath(path)}"\n')
        return tu
    return path


def compile_one(cxx: str, path: str, flags: list[str], tmp: str) -> tuple[int, str]:
    tu = tu_for(path, tmp)
    lang = ["-x", "c++"] if path.endswith(".ipp") else []
    # LC_ALL=C: ASCII quotes in diagnostics, whatever the runner's locale (GCC quotes with U+2018/U+2019 in UTF-8).
    r = subprocess.run([cxx, *flags, "-I", os.path.dirname(path), *lang, "-c", tu, "-o", os.devnull],
                       capture_output=True, text=True, env={**os.environ, "LC_ALL": "C"})
    return r.returncode, r.stdout + r.stderr


def compiler_matcher(spec: dict):
    """A test of one diagnostic's text for the claim, and the claim's name."""
    if "flag" in spec:
        flag = re.escape(spec["flag"])
        return (lambda t: re.search(rf"\[(?:-Werror,)?-W(?:error=)?{flag}\]", t) is not None), f"-W{spec['flag']}"
    if "message" in spec:
        return (lambda t: re.search(spec["message"], t) is not None), f"message /{spec['message']}/"
    if "error" in spec:
        return (lambda t: re.search(spec["error"], t) is not None), f"error /{spec['error']}/"
    raise CaseError("a compiler entry needs flag, message or error")


def compiler_claim_holds(spec: dict, rc: int, out: str, path: str, lines: list[int]) -> tuple[bool, str]:
    """The claim holds on a bad file when the diagnostic is reported on every marked line (an error claim also
    needs the compile to fail)."""
    match, what = compiler_matcher(spec)
    if "error" in spec and rc == 0:
        return False, what
    missing = sorted(set(lines) - diag_lines(out, path, match))
    if missing:
        return False, f"{what} on line(s) {', '.join(map(str, missing))}"
    return True, what


def cmd_compilers(args) -> int:
    """The compiler-warning claims, with the host GCC and Clang and with the cross GCC; and every ok file builds
    cleanly with the org flags on every compiler of its targets (a compliant example that warns proves nothing)."""
    cases = load_cases()
    compilers = [("gcc", args.gcc, [], "host"), ("clang", args.clang, [], "host")]
    if args.arm:
        compilers.append(("gcc-arm", args.arm, CORTEX_FLAGS, "cortex-m"))
    jobs = []
    for c in cases:
        for tool, cxx, extra, target in compilers:
            if target not in c["targets"]:
                continue
            for f in c["ok"]:
                jobs.append((c, tool, cxx, extra, f, "ok"))
            claim = c.get("gcc" if tool == "gcc-arm" else tool)
            if claim:
                for f in c["bad"]:
                    jobs.append((c, tool, cxx, extra, f, "bad"))
    with tempfile.TemporaryDirectory() as tmp, cf.ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        outs = list(ex.map(lambda j: compile_one(j[2], j[4], ORG_FLAGS + j[3], tmp), jobs))
    per = {}
    for (c, tool, _cxx, extra, f, side), (rc, out) in zip(jobs, outs):
        claim = c.get("gcc" if tool == "gcc-arm" else tool)
        e = per.setdefault((c["name"], tool), {
            "case": c["name"], "guideline": c["guideline"], "tool": tool, "claimed": bool(claim),
            "id": compiler_matcher(claim)[1] if claim else "", "target": "cortex-m" if extra else "host",
            "proven": False, "problems": [], "files": []})
        e["files"].append(rel(f))
        if side == "ok":
            if rc != 0 or out.strip():
                e["problems"].append(f"{rel(f)} must build cleanly with {' '.join(ORG_FLAGS + extra)}:\n"
                                     f"{out.strip()}")
        else:
            ok, what = compiler_claim_holds(claim, rc, out, f, lines_for(c["marks"][f], tool))
            if not ok:
                e["problems"].append(f"{rel(f)}: expected {what}, got:\n{out.strip() or '(no output)'}")
    results = list(per.values())
    for e in results:
        e["proven"] = e["claimed"] and not e["problems"]
    return finish(results, [e for e in results if e["problems"]], args.results, "compilers")


def tidy_config(spec: dict) -> str:
    opts = spec.get("options") or {}
    cfg = {"Checks": f"-*,{spec['check']}", "WarningsAsErrors": "", "HeaderFilterRegex": ".*",
           **(spec.get("config") or {}),
           "CheckOptions": {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in opts.items()}}
    return json.dumps(cfg)


def darwin_sysroot() -> list[str]:
    """The PyPI clang-tidy does not find the macOS SDK on its own (local runs only; CI is Linux)."""
    if platform.system() != "Darwin":
        return []
    sdk = subprocess.run(["xcrun", "--show-sdk-path"], capture_output=True, text=True).stdout.strip()
    return ["-isysroot", sdk, "-isystem", f"{sdk}/usr/include/c++/v1"] if sdk else []


def tidy_one(binary: str, spec: dict, path: str) -> tuple[dict[str, set[int]], str]:
    lang = "c++-header" if path.endswith(HEADER_EXT) else "c++"
    r = subprocess.run([binary, "--quiet", f"--config={tidy_config(spec)}", path, "--", "-x", lang,
                        *[f for f in ORG_FLAGS if f != "-Werror"], *darwin_sysroot(), "-I", os.path.dirname(path)],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    checks: dict[str, set[int]] = {}
    for m in re.finditer(r"^([^\n:]+):(\d+):\d+: (?:warning|error): (.*?) \[([^\]\n]+)\]$", out, re.M):
        # A claim with `message` counts only the diagnostics whose text matches: the check reports more than the
        # guideline covers (ru-misra applies the same filter).
        if spec.get("message") and not re.search(spec["message"], m.group(3)):
            continue
        if os.path.abspath(m.group(1)) == os.path.abspath(path):
            for x in m.group(4).split(","):
                checks.setdefault(x.strip(), set()).add(int(m.group(2)))
    return checks, out


def cmd_tidy(args) -> int:
    cases = [c for c in load_cases() if "clang-tidy" in c]
    jobs = [(c, f, side) for c in cases for side in ("bad", "ok") for f in c[side]]
    with cf.ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        outs = list(ex.map(lambda j: tidy_one(args.clang_tidy, j[0]["clang-tidy"], j[1]), jobs))
    per = {}
    for (c, f, side), (checks, out) in zip(jobs, outs):
        check = c["clang-tidy"]["check"]
        e = per.setdefault(c["name"], {"case": c["name"], "guideline": c["guideline"], "tool": "clang-tidy",
                                       "claimed": True, "id": check, "target": "host", "proven": False,
                                       "problems": [], "files": []})
        e["files"].append(rel(f))
        if side == "bad":
            missing = sorted(set(lines_for(c["marks"][f], "clang-tidy")) - checks.get(check, set()))
            if missing:
                e["problems"].append(f"{rel(f)}: expected [{check}] on line(s) {', '.join(map(str, missing))}, "
                                     f"got:\n{out.strip() or '(no output)'}")
        if side == "ok" and check in checks:
            e["problems"].append(f"{rel(f)}: [{check}] reported on compliant code:\n{out.strip()}")
    results = list(per.values())
    by_name = {c["name"]: c for c in cases}
    for e in results:
        a = next((m for m in by_name[e["case"]].get("known_misses") or []
                  if m["tool"] == "clang-tidy" and m["query"] == e["id"]), None)
        if a:
            # A recorded anomaly of the check: reported, not failed, as long as it is what the log says.
            fn = any("expected [" in p for p in e["problems"])
            fp = any("reported on compliant code" in p for p in e["problems"])
            observed = "false-negative" if fn else "false-positive" if fp else ""
            e["anomaly"] = {"kind": a["kind"], "why": a.get("why", "")}
            if observed != a["kind"]:
                e["problems"] = [f"recorded {a['kind']} of {e['id']} no longer occurs: remove it from known_misses "
                                 "and from the anomaly log"] if not observed else [
                                 f"recorded as {a['kind']} but observed {observed}", *e["problems"]]
            else:
                e["problems"] = []
        e["proven"] = not e["problems"] and not a
    return finish(results, [e for e in results if e["problems"]], args.results, "clang-tidy")


def cmd_handbook(args) -> int:
    """The handbook checker's unit tests for the checks the matrix names; one result per claim."""
    with open(args.matrix, encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)["guidelines"]
    test_file = os.path.join(REPO, "tools", "handbook_check", "test_handbook_check.py")
    outcome = {}
    for check, test in HANDBOOK_TESTS.items():
        r = subprocess.run([sys.executable, test_file, "-k", test], capture_output=True, text=True)
        outcome[check] = (r.returncode == 0 and "OK" in r.stderr, r.stderr[-2000:], f"{rel(test_file)}::{test}")
    # The handbook's source checks (checks/source_checks.py) are validated by their own selftest, which seeds a break
    # of every check and confirms it is reported; the checks it documents count as validated when it passes.
    src = os.path.join(args.handbook, "checks", "source_checks.py") if args.handbook else ""
    if src and os.path.isfile(src):
        r = subprocess.run([sys.executable, src, "selftest"], capture_output=True, text=True)
        with open(src, encoding="utf-8") as fh:
            documented = set(re.findall(r"^  ([a-z0-9-]+(?:/[a-z0-9-]+)?)\s{2,}", fh.read(), re.M))
        for check in documented:
            outcome.setdefault(check, (r.returncode == 0, (r.stdout + r.stderr)[-2000:],
                                       "handbook checks/source_checks.py selftest"))
    results = []
    for g in matrix:
        for v in g["verification"]:
            if v["by"] == "handbook-check" and not v.get("partial"):
                check = v["how"].split(" ")[0]
                ok, out, test = outcome.get(check, (False, f"no test validates the check {check}", "none"))
                results.append({"case": test,
                                "guideline": g["id"], "tool": "handbook-check", "claimed": True, "id": check,
                                "target": "host", "proven": ok, "problems": [] if ok else [out]})
    return finish(results, [r for r in results if r["problems"]], args.results, "handbook-check")


def cmd_build(args) -> int:
    """Compile every file of one side for one target, for CodeQL to trace. A file that does not compile fails."""
    cases = [c for c in load_cases() if "codeql" in c and c.get("compiles", True) and args.target in c["targets"]]
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    flags = CODEQL_FLAGS + (CORTEX_FLAGS if args.target == "cortex-m" else [])
    files = [f for c in cases for f in c[args.side]]
    bad = 0
    for f in files:
        # Sequential and in the open: the CodeQL tracer follows each compiler process. A file that exercises
        # exceptions or RTTI (cases of the exception guidelines) cannot build with -fno-exceptions -fno-rtti;
        # every other file is traced with them, as the scans build.
        with open(f, encoding="utf-8") as fh:
            needs_eh = EH_RE.search(fh.read()) is not None
        rc, text = compile_one(args.cxx, f, [x for x in flags if x not in NO_EH] if needs_eh else flags, out)
        if rc != 0:
            bad += 1
            print(f"::error file={rel(f)}::does not compile for the {args.target} CodeQL database:\n{text}")
    print(f"compiled {len(files) - bad}/{len(files)} {args.side} file(s) of {len(cases)} case(s) for {args.target}")
    return 1 if bad else 0


def sarif_results(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        sarif = json.load(fh)
    out = []
    for run in sarif.get("runs", []):
        rules = {}
        for comp in [run["tool"]["driver"], *run["tool"].get("extensions", [])]:
            for r in comp.get("rules", []):
                tags = (r.get("properties") or {}).get("tags", [])
                rules[r["id"]] = next((t.split("/")[-1] for t in tags if re.match(r"external/\w+/id/", t)), "")
        for res in run.get("results", []):
            rid = res.get("ruleId") or ""
            loc = (res.get("locations") or [{}])[0].get("physicalLocation", {})
            out.append({"query": rid, "tag": rules.get(rid, ""),
                        "file": loc.get("artifactLocation", {}).get("uri", "").lstrip("./"),
                        # A result about a whole file (no region, e.g. a header without a guard) is on line 1.
                        "line": loc.get("region", {}).get("startLine", 0) or 1,
                        "message": (res.get("message") or {}).get("text", "")})
    return out


def cmd_codeql(args) -> int:
    cases = [c for c in load_cases() if "codeql" in c and args.target in c["targets"]]

    def by_file(results):
        d = {}
        for r in results:
            d.setdefault(r["file"], []).append(r)
        return d

    bad_f, ok_f = by_file(sarif_results(args.bad)), by_file(sarif_results(args.ok))

    def lookup(d, f):
        k = rel(f)
        return next((v for p, v in d.items() if p == k or p.endswith("/" + k)), [])

    results, failures = [], []
    for c in cases:
        queries = (c["codeql"] or {}).get("queries") or []
        if not queries:
            raise CaseError(f"{c['name']}: codeql needs queries")
        tag = guideline_slug(c["guideline"])
        allowed = {o["query"]: o.get("why", "") for o in c.get("other_findings") or []}
        anomalies = {m["query"]: m for m in c.get("known_misses") or []
                     if m["tool"] == "codeql" and args.target in (m.get("targets") or TARGETS)}
        for q in queries:
            e = {"case": c["name"], "guideline": c["guideline"], "tool": "codeql", "claimed": True, "id": q,
                 "target": args.target, "proven": False, "problems": [], "fn": [], "fp": [],
                 "files": [rel(f) for f in c["bad"] + c["ok"]]}
            if not c.get("compiles", True):
                if anomalies.get(q, {}).get("kind") == "false-negative":
                    e["fn"].append("not exercisable: the seeded forms are compile errors")
                else:
                    e["problems"].append("bad files do not compile, so CodeQL cannot be shown to detect them")
            else:
                # Every marked line is reported by some claimed query, and each claimed query reports a marked
                # line somewhere in the case (so each claim is exercised). Extra results in a bad file are not
                # failures: a bad file may break other guidelines on the way.
                own = 0
                for f in c["bad"]:
                    results_f = lookup(bad_f, f)
                    hits = [r for r in results_f if r["query"] == q]
                    if any(r["tag"] != tag for r in hits):
                        e["problems"].append(f"{rel(f)}: {q} is tagged {hits[0]['tag'] or 'nothing'}, not {tag}")
                    want = lines_for(c["marks"][f], "codeql")
                    own += len({r["line"] for r in hits} & set(want))
                    claimed_lines = {r["line"] for r in results_f if r["query"] in queries}
                    for n in want:
                        if n not in claimed_lines:
                            e["fn"].append(f"{rel(f)}:{n}: seeded, but no claimed query reports this line (got "
                                           f"{sorted({r['query'] for r in results_f if r['line'] == n}) or 'none'})")
                if not own:
                    e["fn"].append(f"{q} reports no marked line of any bad file (got "
                                   f"{sorted({r['query'] for f in c['bad'] for r in lookup(bad_f, f)}) or 'none'})")
            for f in c["ok"]:
                e["fp"] += [f"{rel(f)}:{r['line']}: {r['message']}" for r in lookup(ok_f, f) if r["query"] == q]
            a = anomalies.get(q)
            if a:
                # A recorded anomaly of the claimed query: reported, not failed, as long as it is what the log says.
                observed = "false-negative" if e["fn"] else "false-positive" if e["fp"] else ""
                e["anomaly"] = {"kind": a["kind"], "why": a.get("why", "")}
                if observed != a["kind"]:
                    if not observed:
                        e["problems"].append(f"recorded {a['kind']} of {q} no longer occurs: remove it from "
                                             "known_misses and from the anomaly log (the requirement then passes)")
                    elif observed:
                        e["problems"].append(f"recorded as {a['kind']} but observed {observed}")
            else:
                e["problems"] += e["fn"] + [f"{q} reported on compliant code: {x}" for x in e["fp"]]
            e["proven"] = not e["problems"] and not a
            results.append(e)
            if e["problems"]:
                failures.append(e)
        if args.no_others:
            continue
        # Every other query's result on an ok file must be reviewed and listed in other_findings.
        seen = set()
        for f in c["ok"]:
            for r in lookup(ok_f, f):
                if r["query"] in queries:
                    continue
                seen.add(r["query"])
                if r["query"] not in allowed:
                    failures.append({"case": c["name"], "guideline": c["guideline"], "tool": "codeql",
                                     "id": r["query"], "target": args.target, "problems": [
                                         f"{rel(f)}:{r['line']}: unreviewed result of {r['query']} on compliant "
                                         f"code ({r['message']}); fix the snippet or list it in other_findings"]})
        for q in sorted(set(allowed) - seen):
            print(f"::notice::{c['name']}: other_findings lists {q}, which reported nothing on {args.target}")
    return finish(results, failures, args.results, f"codeql-{args.target}")


def finish(results, failures, path, label) -> int:
    for f in failures:
        print(f"::error::{label}: {f['case']} ({f['guideline']}, {f['id']}):")
        for p in f["problems"]:
            print("    " + p.replace("\n", "\n    "))
    proven = sum(1 for r in results if r.get("proven"))
    anomalies = sum(1 for r in results if r.get("anomaly"))
    claimed = sum(1 for r in results if r.get("claimed", True))
    print(f"{label}: {proven}/{claimed} claim(s) proven, {anomalies} recorded anomaly(ies), "
          f"{len(failures)} failure(s)")
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"tool": label, "results": results, "failures": failures}, fh, indent=1)
    return 1 if failures else 0


# --- record: requirements, traceability, anomaly log, report ---------------------------------------------------


def suite_digest() -> str:
    """SHA-256 over everything that defines the validation: the cases, the own queries, this script, the pins."""
    h = hashlib.sha256()
    files = [TOOLCHAIN, os.path.abspath(__file__), SUPPORTED, ANOMALIES]
    for root in ROOTS + sorted(glob.glob(os.path.join(REPO, "codeql", "*", "rules"))):
        files += sorted(p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True) if os.path.isfile(p))
    for p in sorted(set(files)):
        h.update(rel(p).encode() + b"\0")
        with open(p, "rb") as fh:
            h.update(hashlib.sha256(fh.read()).digest())
    return h.hexdigest()


def file_sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


TOOL_CODE = {"gcc": "GCC", "clang": "CLANG", "gcc-arm": "GCCARM", "clang-tidy": "TIDY", "codeql": "CQL",
             "handbook-check": "HBC"}
# The handbook checker's own unit tests are its validation: the test that seeds each check the matrix names.
HANDBOOK_TESTS = {"forbidden-patterns/exceptions-rtti": "test_heap_exceptions_rtti_virtual_in_code"}


def build_requirements(matrix: list[dict], supported: dict, cases: list[dict]) -> list[dict]:
    """Every claim "tool X decides guideline G with rule id R" (the matrix's non-partial compiler and clang-tidy
    entries, every default-suite query of the MISRA pack for an applicable guideline, every own-profile query)."""
    reqs = []
    by_g: dict[str, list[dict]] = {}
    for c in cases:
        by_g.setdefault(c["guideline"], []).append(c)

    def add(tool, gid, rid, source, claim):
        reqs.append({"tool": tool, "guideline": gid, "rule_id": rid, "source": source, "claim": claim})

    for g in matrix:
        gid = g["id"]
        decided = {v["by"]: v["how"] for v in g["verification"] if not v.get("partial")}
        cs = by_g.get(gid, [])
        if "compiler" in decided:
            claimed = sorted({(t, compiler_claim_holds(c[t], 0, "")[1]) for c in cs for t in ("gcc", "clang") if t in c})
            for t, rid in claimed or [("gcc", "(no case)")]:
                add(t, gid, rid, "matrix", decided["compiler"])
                if t == "gcc":
                    add("gcc-arm", gid, rid, "matrix", decided["compiler"] + " (cross GCC)")
        if "clang-tidy" in decided:
            for check in sorted({c["clang-tidy"]["check"] for c in cs if "clang-tidy" in c}) or ["(no case)"]:
                add("clang-tidy", gid, check, "matrix", decided["clang-tidy"])
        if "handbook-check" in decided:
            check = decided["handbook-check"].split(" ")[0]
            add("handbook-check", gid, check, "matrix", decided["handbook-check"])
        if g["applies"] is True:
            for q in supported.get(gid, []):
                add("codeql", gid, q, "misra-pack", f"default-suite query of the pinned pack for {gid}")
    for c in cases:
        if not re.fullmatch(r"(Rule|Dir) .*", c["guideline"]):
            for q in (c.get("codeql") or {}).get("queries", []):
                if not any(r["rule_id"] == q for r in reqs):
                    add("codeql", c["guideline"], q, "kokeb-profile", f"own-profile query for {c['guideline']}")
    counters: dict[str, int] = {}
    for r in reqs:
        base = f"TV-{TOOL_CODE[r['tool']]}-{guideline_slug(r['guideline']).upper()}"
        counters[base] = counters.get(base, 0) + 1
        r["id"] = f"{base}-{counters[base]:02d}"
    return reqs


def load_results(results_dir: str) -> tuple[list[dict], dict, list[str]]:
    """Every test result, the tool versions, and the failures that belong to no requirement (unreviewed
    results of other queries on compliant code)."""
    results, versions, other = [], {}, []
    for p in sorted(glob.glob(os.path.join(results_dir, "**", "results-*.json"), recursive=True)):
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        results += data["results"]
        keys = {(r["case"], r["id"], r.get("target")) for r in data["results"]}
        other += [f"{f['case']}: {pr}" for f in data["failures"] if (f["case"], f["id"], f.get("target")) not in keys
                  for pr in f["problems"]]
    for p in sorted(glob.glob(os.path.join(results_dir, "**", "versions*.json"), recursive=True)):
        with open(p, encoding="utf-8") as fh:
            for k, v in json.load(fh).items():
                if v != "not installed":
                    versions[k] = v
    return results, versions, other


def anomaly_entries(cases: list[dict]) -> list[dict]:
    """What the cases record: anomalies of a claimed query, and misfires of other queries on compliant code."""
    out = []
    for c in cases:
        for m in c.get("known_misses") or []:
            out.append({"case": c["name"], "tool": m["tool"], "rule_id": m["query"], "kind": m["kind"],
                        "description": " ".join(str(m.get("why", "")).split())})
        for o in c.get("other_findings") or []:
            why = " ".join(str(o.get("why", "")).split())
            if why.lower().startswith("misfire"):
                out.append({"case": c["name"], "tool": "codeql", "rule_id": o["query"], "kind": "false-positive",
                            "description": re.sub(r"^misfire:\s*", "", why, flags=re.I)})
    return out


def cmd_record(args) -> int:
    with open(args.matrix, encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)["guidelines"]
    with open(SUPPORTED, encoding="utf-8") as fh:
        sup = json.load(fh)
    supported = {g: [q["id"] for q in qs if not q["audit"]] for g, qs in sup["guidelines"].items()}
    cases = load_cases("")
    reqs = build_requirements(matrix, supported, cases)
    results, versions, other_failures = load_results(args.results_dir)
    with open(ANOMALIES, encoding="utf-8") as fh:
        log = yaml.safe_load(fh) or {}
    logged = {(a["case"], a["rule_id"], a["kind"]): a for a in log.get("anomalies", [])}
    problems = list(other_failures)

    # The anomaly log and the cases must agree, entry for entry, and every entry needs a disposition.
    recorded = anomaly_entries(cases)
    for a in recorded:
        k = (a["case"], a["rule_id"], a["kind"])
        if k not in logged:
            problems.append(f"anomaly not in the log: {a['case']} {a['rule_id']} {a['kind']} (add it to anomalies.yml)")
        elif not str(logged[k].get("disposition", "")).strip():
            problems.append(f"anomaly {logged[k]['id']} has no disposition")
    for k, a in logged.items():
        if not any((r["case"], r["rule_id"], r["kind"]) == k for r in recorded):
            problems.append(f"anomaly {a['id']} ({a['case']} {a['rule_id']}) is no longer recorded by its case: "
                            "close it in the log")

    # Every case states what it seeds and which near misses it holds, so a reviewer can judge the test's strength.
    for c in cases:
        for key in ("seeded", "near_misses"):
            if not c.get(key):
                problems.append(f"{c['name']}: case.yml lists no {key}")
    targets_of = {c["name"]: c["targets"] for c in cases}
    for r in reqs:
        runs = [x for x in results if x["tool"] == r["tool"] and x["id"] == r["rule_id"]
                and x["guideline"] == r["guideline"] and x.get("claimed", True)]
        r["tests"] = sorted({x["case"] for x in runs})
        r["runs"] = sorted({f"{x['case']}@{x.get('target', 'host')}" for x in runs})
        r["anomalies"] = sorted({logged[(x["case"], r["rule_id"], x["anomaly"]["kind"])]["id"] for x in runs
                                 if x.get("anomaly") and (x["case"], r["rule_id"], x["anomaly"]["kind"]) in logged})
        failed = [x for x in runs if x.get("problems")]
        if r["tool"] == "codeql":
            # CodeQL must hold on every target each of its cases is written for.
            want = {f"{c}@{t}" for c in r["tests"] for t in targets_of.get(c, TARGETS)}
            missing_runs = sorted(want - set(r["runs"]))
        else:
            missing_runs = []
        if not runs:
            r["status"] = "no test"
        elif failed or missing_runs:
            r["status"] = "fail"
            r["detail"] = [p for x in failed for p in x["problems"]][:5] + [f"not run: {m}" for m in missing_runs]
        elif any((x.get("anomaly") or {}).get("kind") == "false-negative" for x in runs) or not any(
                x.get("proven") for x in runs):
            # A recorded false negative makes the rule id partial: it does not decide the guideline, even if
            # other cases pass. A recorded false positive is noise for review, not a gap: the requirement passes.
            r["status"] = "anomaly"
        else:
            r["status"] = "pass"
        if r["source"] == "matrix" and r["status"] != "pass":
            problems.append(f"{r['id']}: the matrix says {r['tool']} decides {r['guideline']}, but its validation "
                            f"is '{r['status']}'")
        if r["source"] != "matrix" and r["status"] in ("fail", "no test"):
            problems.append(f"{r['id']}: {r['rule_id']} for {r['guideline']} has validation status '{r['status']}'")

    # The guideline -> tool mapping the handbook matrix uses, with what the suite proves.
    mapping = []
    for g in matrix:
        tools = {}
        for r in reqs:
            if r["guideline"] == g["id"]:
                tools.setdefault(r["tool"], []).append(r["status"])
        mapping.append({"guideline": g["id"], "matrix": sorted({(v["by"] + (" (partial)" if v.get("partial") else ""))
                                                               for v in g["verification"]}),
                        "validated": {t: ("pass" if all(s == "pass" for s in ss) else
                                          "anomaly" if all(s in ("pass", "anomaly") for s in ss) else "fail")
                                      for t, ss in sorted(tools.items())}})
    counts: dict[str, dict[str, int]] = {}
    for r in reqs:
        counts.setdefault(r["tool"], {}).setdefault(r["status"], 0)
        counts[r["tool"]][r["status"]] += 1
    record = {
        "schema": 1,
        "toolchain_sha256": file_sha(TOOLCHAIN),
        "suite_sha256": suite_digest(),
        "matrix_sha256": file_sha(args.matrix),
        "pack": f"{sup['pack']}@{sup['version']}",
        "tool_versions": dict(sorted(versions.items())),
        "org_flags": ORG_FLAGS,
        "counts": counts,
        "requirements": [{k: r[k] for k in ("id", "tool", "guideline", "rule_id", "source", "tests", "runs",
                                            "status", "anomalies")} for r in reqs],
    }
    os.makedirs(args.out, exist_ok=True)
    out_record = os.path.join(args.out, "validation-record.json")
    with open(out_record, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
        fh.write("\n")
    trace = render_traceability(record, mapping, log)
    with open(os.path.join(args.out, "traceability.md"), "w", encoding="utf-8") as fh:
        fh.write(trace)
    with open(os.path.join(args.out, "validation-report.md"), "w", encoding="utf-8") as fh:
        fh.write(render_report(record, reqs, log, problems, results))
    if args.check:
        for path, new in ((RECORD, out_record), (TRACE_DOC, os.path.join(args.out, "traceability.md"))):
            old = open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
            if old != open(new, encoding="utf-8").read():
                problems.append(f"{rel(path)} does not match this validation run: the toolchain, the suite or a "
                                f"result changed. Re-validate and commit the regenerated file from the run's "
                                f"'tool-validation' artifact")
    if args.write:
        shutil.copyfile(out_record, RECORD)
        shutil.copyfile(os.path.join(args.out, "traceability.md"), TRACE_DOC)
    for p in problems:
        print(f"::error::{p}")
    for tool, c in sorted(counts.items()):
        print(f"{tool}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    print(f"{len(reqs)} requirement(s), {len(problems)} problem(s)")
    return 1 if problems else 0


def render_traceability(record: dict, mapping: list[dict], log: dict) -> str:
    lines = ["# Traceability: requirement, tests, result", "",
             "<!-- generated: traceability (tests/misra-validation/validate.py record --write); checked by the self-CI -->",
             "",
             "Every claim that a tool decides a guideline is a requirement. Its tests are the case directories under "
             "`tests/misra-validation/cases/` (and `codeql/*/validation/`), run on the targets listed; the result is "
             "that of the recorded validation run. The [plan](plan.md) defines the statuses.", "",
             f"Toolchain `{record['toolchain_sha256'][:16]}`, suite `{record['suite_sha256'][:16]}`, pack "
             f"`{record['pack']}`.", "", "## Summary", "", "| Tool | " + " | ".join(
                 ("pass", "anomaly", "fail", "no test")) + " |", "| --- | --- | --- | --- | --- |"]
    for tool, c in sorted(record["counts"].items()):
        lines.append(f"| {tool} | " + " | ".join(str(c.get(s, 0)) for s in ("pass", "anomaly", "fail", "no test"))
                     + " |")
    lines += ["", "## Guideline to tools", "",
              "The matrix's verification entries for each guideline, and the validation status of each tool the "
              "suite holds requirements for.", "", "| Guideline | Matrix | Validated |", "| --- | --- | --- |"]
    for m in mapping:
        v = ", ".join(f"{t}: {s}" for t, s in m["validated"].items()) or "-"
        lines.append(f"| {m['guideline']} | {', '.join(m['matrix'])} | {v} |")
    lines += ["", "## Requirements", "", "| Requirement | Guideline | Tool | Rule id | Tests | Result |",
              "| --- | --- | --- | --- | --- | --- |"]
    for r in record["requirements"]:
        tests = "<br>".join(f"`{t.split('/')[-1]}`" for t in r["tests"]) or "-"
        res = r["status"] + (f" ({', '.join(r['anomalies'])})" if r["anomalies"] else "")
        lines.append(f"| {r['id']} | {r['guideline']} | {r['tool']} | `{r['rule_id']}` | {tests} | {res} |")
    return "\n".join(lines) + "\n"


def render_report(record: dict, reqs: list[dict], log: dict, problems: list[str], results: list[dict]) -> str:
    lines = ["# Tool validation report: MISRA C++:2023 toolchain", "",
             "The record of one self-CI run of the tool-validation suite (`tests/misra-validation/validate.py record`), "
             "attached to each ci-tools release. The plan, acceptance criteria and statuses are in docs/tool-validation/plan.md.", "",
             f"**Result: {'ACCEPTED' if not problems else 'NOT ACCEPTED'}** "
             f"({len(problems)} open problem(s)).", "", "## Tools", "", "| Tool | Version |", "| --- | --- |"]
    lines += [f"| {k} | `{v}` |" for k, v in record["tool_versions"].items()]
    t = load_toolchain()
    lines += ["", "| Pinned artefact | SHA-256 |", "| --- | --- |"]
    for k in ("codeql_bundle", "misra_pack", "coding_standards_script", "arm_gnu_toolchain"):
        lines.append(f"| {k} {t[k].get('version', '')} | `{t[k]['sha256']}` |")
    lines += [f"| clang-tidy wheel | `{t['clang_tidy']['requirement'].split('sha256:')[1]}` |",
              f"| toolchain.json | `{record['toolchain_sha256']}` |", f"| suite | `{record['suite_sha256']}` |",
              f"| matrix | `{record['matrix_sha256']}` |", "", "Compile flags of every compliant file: "
              f"`{' '.join(record['org_flags'])}`.", "", "## Results by tool", "",
              "| Tool | Requirements | Pass | Anomaly | Fail | No test |", "| --- | --- | --- | --- | --- | --- |"]
    for tool, c in sorted(record["counts"].items()):
        lines.append(f"| {tool} | {sum(c.values())} | {c.get('pass', 0)} | {c.get('anomaly', 0)} | "
                     f"{c.get('fail', 0)} | {c.get('no test', 0)} |")
    if problems:
        lines += ["", "## Open problems", ""] + [f"- {p}" for p in problems]
    lines += ["", "## Anomalies (known false negatives and false positives)", "",
              "| Id | Tool | Rule id | Kind | Case | Description | Disposition |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for a in log.get("anomalies", []):
        lines.append(f"| {a['id']} | {a['tool']} | `{a['rule_id']}` | {a['kind']} | `{a['case'].split('/')[-1]}` | "
                     f"{' '.join(str(a.get('description', '')).split())} | {' '.join(str(a.get('disposition', '')).split())} |")
    lines += ["", "## Known limitations", ""] + [f"- {' '.join(str(x).split())}" for x in log.get("limitations", [])]
    lines += ["", "## Every test result", "", "| Requirement | Case | Target | Result |", "| --- | --- | --- | --- |"]
    for r in reqs:
        for x in results:
            if x["tool"] == r["tool"] and x["id"] == r["rule_id"] and x["guideline"] == r["guideline"]:
                res = "pass" if x.get("proven") else ("anomaly " + x["anomaly"]["kind"]) if x.get("anomaly") else "FAIL"
                lines.append(f"| {r['id']} | `{x['case'].split('/')[-1]}` | {x.get('target', 'host')} | {res} |")
    return "\n".join(lines) + "\n"


# --- local ---------------------------------------------------------------------------------------------------


def quick_queries(packs: list[str]) -> list[str]:
    """The .ql files of the queries the selected cases name, found by their @id."""
    wanted = {q for c in load_cases() if "codeql" in c for q in (c["codeql"] or {}).get("queries", [])}
    found = []
    for root in packs:
        for ql in glob.glob(os.path.join(root, "**", "*.ql"), recursive=True):
            if "/.codeql/" in ql:
                continue
            with open(ql, encoding="utf-8") as fh:
                m = re.search(r"@id (\S+)", fh.read(2000))
            if m and m.group(1) in wanted:
                found.append(ql)
    return sorted(found)


def cmd_local(args) -> int:
    """Everything the self-CI runs, on this machine (CodeQL's terms allow it on this repository: public, MIT)."""
    py, me = sys.executable, os.path.abspath(__file__)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    status = subprocess.run([py, me, "compilers", "--gcc", args.gcc, "--clang", args.clang,
                             *(["--arm", args.arm] if args.arm else []),
                             "--results", os.path.join(work, "results-compilers.json")]).returncode
    if shutil.which(args.clang_tidy):
        status |= subprocess.run([py, me, "tidy", "--clang-tidy", args.clang_tidy,
                                  "--results", os.path.join(work, "results-tidy.json")]).returncode
    else:
        print(f"::warning::{args.clang_tidy} not found: clang-tidy claims not checked")
    if not args.codeql:
        return status
    own = sorted(glob.glob(os.path.join(REPO, "codeql", "*", "qlpack.yml")))
    own_dirs = [os.path.dirname(p) for p in own]
    suites = [os.path.join(args.pack, "codeql-suites", "misra-cpp-default.qls")] + [
        os.path.join(d, "codeql-suites", os.path.basename(d) + "-default.qls") for d in own_dirs]
    if args.quick:
        suites = quick_queries([args.pack, *own_dirs])
    for target in args.target:
        cxx = args.codeql_cxx if target == "host" else args.arm
        if not cxx:
            continue
        for side in ("bad", "ok"):
            db = os.path.join(work, f"db-{target}-{side}")
            shutil.rmtree(db, ignore_errors=True)
            script = os.path.join(work, f"build-{target}-{side}.sh")
            with open(script, "w", encoding="utf-8") as fh:  # codeql splits --command on blanks, ignoring quotes
                fh.write("#!/bin/sh\nexec " + shlex.join([py, me, "build", "--side", side, "--target", target,
                                                          "--cxx", cxx, "--out", os.path.join(work, f"obj-{target}")])
                         + "\n")
            os.chmod(script, 0o755)
            env = {**os.environ, "VALIDATE_ONLY": ONLY}
            if subprocess.run([args.codeql, "database", "create", db, "--language=cpp", "--overwrite",
                               f"--source-root={REPO}", f"--command={script}"], env=env).returncode:
                return 1
            if subprocess.run([args.codeql, "database", "analyze", db, *suites, "--format=sarifv2.1.0",
                               f"--output={work}/{target}-{side}.sarif", f"--threads={args.threads}",
                               *([f"--ram={args.ram}"] if args.ram else []),
                               f"--additional-packs={os.pathsep.join([args.pack, *own_dirs])}"]).returncode:
                return 1
        status |= subprocess.run([py, me, "codeql", "--target", target, "--bad", f"{work}/{target}-bad.sarif",
                                  "--ok", f"{work}/{target}-ok.sarif",
                                  "--results", os.path.join(work, f"results-codeql-{target}.json"),
                                  *(["--no-others"] if args.quick else [])]).returncode
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", help="regex on the case directory name (same as VALIDATE_ONLY)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("compilers")
    p.add_argument("--gcc", default="g++-14")
    p.add_argument("--clang", default="clang++-18")
    p.add_argument("--arm", help="the cross GCC (arm-none-eabi-g++): the GCC claims and the cortex-m ok builds")
    p.add_argument("--results")
    p = sub.add_parser("tidy")
    p.add_argument("--clang-tidy", default="clang-tidy")
    p.add_argument("--results")
    p = sub.add_parser("handbook")
    p.add_argument("--matrix", required=True)
    p.add_argument("--handbook", help="a checkout of kokeb-labs/handbook at the matrix's commit")
    p.add_argument("--results")
    p = sub.add_parser("build")
    p.add_argument("--side", choices=["bad", "ok"], required=True)
    p.add_argument("--target", choices=TARGETS, default="host")
    p.add_argument("--cxx", default="g++")
    p.add_argument("--out", default="build-misra-validation")
    p = sub.add_parser("codeql")
    p.add_argument("--bad", required=True)
    p.add_argument("--ok", required=True)
    p.add_argument("--target", choices=TARGETS, default="host")
    p.add_argument("--results")
    p.add_argument("--no-others", action="store_true", help="skip the review of other queries' results on ok files")
    p = sub.add_parser("record")
    p.add_argument("--results-dir", required=True)
    p.add_argument("--matrix", required=True)
    p.add_argument("--out", default="build-misra-validation/record")
    p.add_argument("--check", action="store_true", help="fail unless the committed record and traceability match")
    p.add_argument("--write", action="store_true", help="copy the new record and traceability into the repository")
    p = sub.add_parser("local")
    p.add_argument("--gcc", default="g++-14")
    p.add_argument("--clang", default="clang++-18")
    p.add_argument("--arm", help="arm-none-eabi-g++: also validate the cortex-m target")
    p.add_argument("--clang-tidy", default="clang-tidy")
    p.add_argument("--codeql", help="the codeql binary; without it CodeQL is skipped")
    p.add_argument("--codeql-cxx", default="g++", help="the compiler of the host CodeQL databases")
    p.add_argument("--pack", help="the extracted misra-cpp-coding-standards pack")
    p.add_argument("--target", action="append", choices=TARGETS, help="CodeQL targets (default: host)")
    p.add_argument("--work", default="build-misra-validation")
    p.add_argument("--quick", action="store_true", help="only the queries the selected cases name; no other-findings review")
    p.add_argument("--threads", default="0")
    p.add_argument("--ram")
    args = ap.parse_args()
    if args.only:
        os.environ["VALIDATE_ONLY"] = args.only
        globals()["ONLY"] = args.only
    if args.cmd == "local" and not args.target:
        args.target = ["host"]
    try:
        return {"compilers": cmd_compilers, "tidy": cmd_tidy, "handbook": cmd_handbook, "build": cmd_build, "codeql": cmd_codeql,
                "record": cmd_record, "local": cmd_local}[args.cmd](args)
    except CaseError as e:
        print(f"::error::{e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
