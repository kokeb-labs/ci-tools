#!/usr/bin/env python3
"""Mutation testing of a CMake project: one-edit mutants, each built and tested; a mutant the tests do not kill is a
finding. Standard library only (PyYAML for a YAML equivalents file).

  mutate.py list   --root DIR [--paths "a b"] [--catalogue GLOB ...] [--mode auto|catalogue|generated|both]
                   [--equivalents FILE] [--max N] --out MUTANTS_JSON
  mutate.py run    --root DIR --mutants MUTANTS_JSON [--shard I --shards N] [--workers N] [--build-parallel N]
                   [--cmake-args ARGS] [--source-dir DIR] [--build-target T] [--ctest-args ARGS] [--timeout-factor F]
                   --out RESULTS_JSON
  mutate.py report --mutants MUTANTS_JSON --results DIR_OR_FILE ... [--level standard|high] [--threshold PCT]
                   [--report-dir DIR] [--summary FILE] [--github-output FILE] [--enforce true|false]
  mutate.py selftest

Mutants come from two sources:

* A catalogue in the drivers' tools/mutants format: blocks of "id | file | what the edit removes", an optional
  "= reason" line (an equivalent mutant: listed, not run), then the old text ("- " lines) and the new text ("+ "
  lines); a bare "-" or "+" is an empty line. File paths are relative to --root. The first occurrence is edited.
* Generated operators over the C and C++ files under --paths: relational (< <= > >= == !=), logical (&& ||),
  negation (!x), arithmetic (+ -), boolean literals and integer constants (n -> n+1, 0 <-> 1). Comments, string and
  character literals and preprocessor lines are never edited. Binary operators are edited only when written with a
  space on each side, so template brackets, ->, << and >> are left alone. Each generated mutant's id is a hash of
  its file, operator and line text, stable across unrelated edits of the file.

--mode auto uses the catalogues when any exists and generates otherwise. The equivalents file (YAML or JSON:
{id: reason}, or a list of {id, reason}, under an optional `equivalent:` key) lists mutants that cannot change
behaviour; they are reported, not run. A listed id that matches no mutant is an error, so the file cannot rot.

run: the tree is copied once per worker (without .git and build folders), configured once and built; the unedited
tree must build and pass its tests (else exit 2, since a failing test would count as a kill). Then every mutant of
the shard: apply the edit, build incrementally, ctest with a timeout of --timeout-factor x the baseline time (at least
30 s), restore the file. Verdicts: killed (a test failed or timed out, or a static_assert fired), survived (every
test passed), compile_error (a generated edit that does not compile: excluded from the score), broken (a catalogue
edit whose old text is not in the file, or that does not compile: the catalogue drifted from the code).

report: kill rate = killed / (killed + survived). level high requires 100 % and no broken mutant; standard requires
80 %; --threshold overrides the percentage. Writes mutation-report.json (the mutation-testing-elements schema,
version 2), mutation-report.md and annotations for survivors, and exits 1 when the policy fails (with --enforce).
"""

from __future__ import annotations

import argparse
import fnmatch
import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time

SOURCE_EXT = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ipp", ".inl")
SKIP_DIRS = {".git", "build", "_build", ".ru-mutation", "node_modules", ".venv", "venv"}
LEVELS = {"standard": 80.0, "high": 100.0}

# (operator id, regex on the masked line, replacement text or callable)
BINARY = [
    ("ror-lt", r" < ", " <= "), ("ror-le", r" <= ", " < "), ("ror-gt", r" > ", " >= "), ("ror-ge", r" >= ", " > "),
    ("ror-eq", r" == ", " != "), ("ror-ne", r" != ", " == "),
    ("lcr-and", r" && ", " || "), ("lcr-or", r" \|\| ", " && "),
    ("aor-add", r" \+ ", " - "), ("aor-sub", r" - ", " + "),
]


# --------------------------------------------------------------------------------------------------------- catalogue

def load_catalogue(path: str) -> list[dict]:
    """The mutants of a catalogue file, equivalent ones marked with their reason."""
    items: list[dict] = []
    cur = None
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.startswith("#"):
            continue
        if line[0] in "-+" and cur is not None and (len(line) == 1 or line[1] == " "):
            cur["old" if line[0] == "-" else "new"].append(line[2:])
        elif line.startswith("= ") and cur is not None:
            cur["equivalent"] = line[2:]
        else:
            parts = [x.strip() for x in line.split("|", 2)]
            if len(parts) != 3 or not all(parts[:2]):
                raise SystemExit(f"::error file={path},line={n}::not 'id | file | what': {line[:80]}")
            cur = {"id": parts[0], "file": parts[1], "old": [], "new": [], "what": parts[2], "source": "catalogue",
                   "operator": "catalogue", "catalogue": path, "line": 0, "column": 0}
            items.append(cur)
    for m in items:
        m["old"], m["new"] = "\n".join(m["old"]), "\n".join(m["new"])
        if not m["old"]:
            raise SystemExit(f"::error file={path}::{m['id']}: no old text ('- ' lines)")
    return items


def locate(text: str, old: str) -> tuple[int, int]:
    i = text.find(old)
    if i < 0:
        return 0, 0
    line = text.count("\n", 0, i) + 1
    col = i - (text.rfind("\n", 0, i) + 1) + 1
    return line, col


# --------------------------------------------------------------------------------------------------------- generated

def mask(text: str) -> str:
    """text with comments, string and character literals and preprocessor lines replaced by spaces (same length)."""
    out = list(text)
    i, n = 0, len(text)
    line_start = True
    while i < n:
        c = text[i]
        if line_start and c == "#" or (line_start and c in " \t" and text[i:].lstrip(" \t").startswith("#")):
            j = text.find("#", i)
            k = j
            while True:  # a preprocessor line, with its continuations
                e = text.find("\n", k)
                e = n if e < 0 else e
                if e > 0 and text[e - 1] == "\\" and e < n:
                    k = e + 1
                    continue
                break
            for x in range(i, e):
                if out[x] != "\n":
                    out[x] = " "
            i = e
            continue
        if c == "\n":
            line_start = True
            i += 1
            continue
        if c not in " \t":
            line_start = False
        if text.startswith("//", i):
            e = text.find("\n", i)
            e = n if e < 0 else e
            for x in range(i, e):
                out[x] = " "
            i = e
        elif text.startswith("/*", i):
            e = text.find("*/", i + 2)
            e = n if e < 0 else e + 2
            for x in range(i, e):
                if out[x] != "\n":
                    out[x] = " "
            i = e
        elif c == 'R' and text.startswith('R"', i):
            m = re.match(r'R"([^(\s]{0,16})\(', text[i:])
            if not m:
                i += 1
                continue
            end = text.find(")" + m.group(1) + '"', i)
            e = n if end < 0 else end + len(m.group(1)) + 2
            for x in range(i, e):
                if out[x] != "\n":
                    out[x] = " "
            i = e
        elif c in "\"'":
            if c == "'" and i > 0 and (text[i - 1].isalnum()):  # digit separator 1'000
                i += 1
                continue
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            e = min(j + 1, n)
            for x in range(i, e):
                out[x] = " "
            i = e
        else:
            i += 1
    return "".join(out)


def generate(root: str, paths: list[str]) -> list[dict]:
    files = []
    for p in paths or ["."]:
        base = os.path.join(root, p)
        if os.path.isfile(base):
            files.append(base)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            files += [os.path.join(dirpath, f) for f in sorted(filenames) if f.endswith(SOURCE_EXT)]
    mutants = []
    seen: dict[str, int] = {}
    for path in sorted(set(files)):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        masked = mask(text)
        lines, mlines = text.split("\n"), masked.split("\n")
        for ln, (line, mline) in enumerate(zip(lines, mlines), 1):
            if not mline.strip():
                continue
            for op, rx, new, start, end in candidates(mline):
                key = f"{rel}|{op}|{line.strip()}"
                seen[key] = seen.get(key, 0) + 1
                mid = "m-" + hashlib.sha256(f"{key}|{seen[key]}".encode()).hexdigest()[:12]
                old_text = line[start:end]
                mutants.append({
                    "id": mid, "file": rel, "line": ln, "column": start + 1, "operator": op, "source": "generated",
                    "old": old_text, "new": new, "start": start, "end": end, "line_text": line,
                    "what": f"{op}: '{old_text.strip()}' -> '{new.strip()}'",
                })
    return mutants


def candidates(mline: str):
    for op, rx, new in BINARY:
        for m in re.finditer(rx, mline):
            yield op, rx, new, m.start(), m.end()
    for m in re.finditer(r"(?<![\w!=<>])!(?=[\w(])", mline):  # !x -> x
        yield "neg", "!", "", m.start(), m.end()
    for m in re.finditer(r"\btrue\b", mline):
        yield "bool-true", "true", "false", m.start(), m.end()
    for m in re.finditer(r"\bfalse\b", mline):
        yield "bool-false", "false", "true", m.start(), m.end()
    for m in re.finditer(r"(?<![\w.'])(\d+)([uUlL]*)\b(?![.'\w])", mline):
        value = int(m.group(1)) if not m.group(1).startswith("0") or m.group(1) == "0" else None
        if value is None or value > 1_000_000:
            continue
        new = ("1" if value == 0 else "0" if value == 1 else str(value + 1)) + m.group(2)
        yield "const", m.group(0), new, m.start(), m.end()


# ------------------------------------------------------------------------------------------------------- equivalents

def load_equivalents(path: str) -> dict[str, str]:
    if not path or not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    try:
        import yaml  # noqa: PLC0415
        doc = yaml.safe_load(text)
    except ImportError:
        doc = json.loads(text)
    if isinstance(doc, dict) and "equivalent" in doc:
        doc = doc["equivalent"]
    out: dict[str, str] = {}
    if isinstance(doc, dict):
        out = {str(k): str(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        for e in doc:
            if not isinstance(e, dict) or "id" not in e or not e.get("reason"):
                raise SystemExit(f"::error file={path}::every equivalent entry needs an id and a reason")
            out[str(e["id"])] = str(e["reason"])
    elif doc is not None:
        raise SystemExit(f"::error file={path}::expected a mapping id -> reason or a list of {{id, reason}}")
    for k, v in out.items():
        if not v.strip():
            raise SystemExit(f"::error file={path}::{k}: an equivalent mutant needs a reason")
    return out


# ------------------------------------------------------------------------------------------------------------- list

def cmd_list(a) -> int:
    root = os.path.abspath(a.root)
    paths = a.paths.split()
    for p in paths:
        if not os.path.exists(os.path.join(root, p)):
            print(f"::warning::mutate path {p} does not exist")
    cats = sorted({f for g in a.catalogue for f in glob.glob(os.path.join(root, g), recursive=True)})
    mode = a.mode
    if mode == "auto":
        mode = "catalogue" if cats else "generated"
    mutants: list[dict] = []
    if mode in ("catalogue", "both"):
        if not cats:
            print("::error::mode catalogue, but no catalogue file matches " + " ".join(a.catalogue))
            return 1
        for c in cats:
            for m in load_catalogue(c):
                m["catalogue"] = os.path.relpath(c, root)
                if paths and not any(fnmatch.fnmatch(m["file"], p.rstrip("/") + "/*") or m["file"] == p
                                     for p in paths):
                    print(f"::warning::{m['id']}: {m['file']} is outside mutate_paths; it is run anyway")
                full = os.path.join(root, m["file"])
                if os.path.isfile(full):
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        m["line"], m["column"] = locate(fh.read(), m["old"])
                mutants.append(m)
    if mode in ("generated", "both"):
        mutants += generate(root, paths)
    ids = [m["id"] for m in mutants]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        print(f"::error::duplicate mutant id(s): {', '.join(dups)}")
        return 1
    equivalent = load_equivalents(a.equivalents)
    known = set(ids)
    stale = sorted(set(equivalent) - known)
    for s in stale:
        print(f"::error file={a.equivalents}::{s} is listed as equivalent but is no mutant (remove it)")
    for m in mutants:
        if m.get("equivalent"):
            equivalent.setdefault(m["id"], m["equivalent"])
        m["equivalent"] = equivalent.get(m["id"], "")
    if a.max and a.max > 0:
        active = sorted((m for m in mutants if not m["equivalent"]), key=lambda m: m["id"])
        keep = {m["id"] for m in active[: a.max]}
        dropped = len(active) - len(keep)
        mutants = [m for m in mutants if m["equivalent"] or m["id"] in keep]
        if dropped:
            print(f"::notice::max_mutants {a.max}: {dropped} mutant(s) not run (a stable sample by id)")
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"mode": mode, "catalogues": [os.path.relpath(c, root) for c in cats], "mutants": mutants}, fh,
                  indent=1)
    eq = sum(1 for m in mutants if m["equivalent"])
    print(f"{len(mutants)} mutant(s) ({mode}): {len(mutants) - eq} to run, {eq} equivalent")
    return 1 if stale else 0


# -------------------------------------------------------------------------------------------------------------- run

def shard_of(mid: str, shards: int) -> int:
    return int(hashlib.sha256(mid.encode()).hexdigest()[:8], 16) % shards


def copy_tree(src: str, dst: str) -> None:
    def ignore(d, names):
        return [n for n in names if n in SKIP_DIRS or (n.startswith("build") and os.path.isdir(os.path.join(d, n)))]
    shutil.copytree(src, dst, ignore=ignore, symlinks=True)


class Worker:
    def __init__(self, root: str, work: str, a):
        self.src = os.path.join(work, "src")
        self.build = os.path.join(work, "build")
        self.a = a
        copy_tree(root, self.src)
        self.timeout = 600.0

    def sh(self, cmd: list[str], timeout: float | None = None) -> tuple[int, str]:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return p.returncode, p.stdout + p.stderr
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            return -999, out

    def configure(self) -> tuple[bool, str]:
        cmd = ["cmake", "-S", os.path.join(self.src, self.a.source_dir), "-B", self.build, "-G", "Ninja",
               "-DCMAKE_BUILD_TYPE=Debug"]
        if shutil.which("ccache"):
            cmd += ["-DCMAKE_CXX_COMPILER_LAUNCHER=ccache", "-DCMAKE_C_COMPILER_LAUNCHER=ccache"]
        rc, out = self.sh(cmd + shlex.split(self.a.cmake_args))
        return rc == 0, out

    def build_cmd(self) -> list[str]:
        cmd = ["cmake", "--build", self.build, "--parallel", str(self.a.build_parallel)]
        if self.a.build_target:
            cmd += ["--target", self.a.build_target]
        return cmd

    def test_cmd(self, timeout: float) -> list[str]:
        return ["ctest", "--test-dir", self.build, "--output-on-failure", "--no-tests=error", "--stop-on-failure",
                "--timeout", str(int(timeout)), "--parallel", str(self.a.build_parallel)] + shlex.split(
                    self.a.ctest_args)

    def baseline(self) -> tuple[bool, str]:
        ok, out = self.configure()
        if not ok:
            return False, "configure failed:\n" + out[-4000:]
        rc, out = self.sh(self.build_cmd())
        if rc != 0:
            return False, "build failed:\n" + out[-4000:]
        t0 = time.monotonic()
        rc, out = self.sh(self.test_cmd(3600))
        elapsed = time.monotonic() - t0
        if rc != 0:
            return False, "tests failed:\n" + out[-4000:]
        self.timeout = max(30.0, elapsed * self.a.timeout_factor)
        return True, f"baseline passed in {elapsed:.1f} s; mutant test timeout {self.timeout:.0f} s"

    def mutate(self, m: dict) -> dict:
        path = os.path.join(self.src, m["file"])
        res = {"id": m["id"], "status": "", "note": ""}
        if not os.path.isfile(path):
            res.update(status="broken", note=f"{m['file']} does not exist")
            return res
        with open(path, encoding="utf-8", errors="surrogateescape", newline="") as fh:
            original = fh.read()
        if m["source"] == "catalogue":
            i = original.find(m["old"])
            if i < 0:
                res.update(status="broken", note="old text not in the file: " + m["old"].splitlines()[0][:70])
                return res
            edited = original[:i] + m["new"] + original[i + len(m["old"]):]
        else:
            lines = original.split("\n")
            line = lines[m["line"] - 1] if m["line"] - 1 < len(lines) else ""
            if line[m["start"]:m["end"]] != m["old"]:
                res.update(status="broken", note="the line changed since the mutants were listed")
                return res
            lines[m["line"] - 1] = line[:m["start"]] + m["new"] + line[m["end"]:]
            edited = "\n".join(lines)
        stat = os.stat(path)
        try:
            with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
                fh.write(edited)
            rc, out = self.sh(self.build_cmd(), timeout=max(600.0, self.timeout * 4))
            if rc != 0:
                if "static_assert" in out or "static assertion" in out:
                    res.update(status="killed", note="a static_assert fired")
                elif m["source"] == "catalogue":
                    res.update(status="broken", note="does not compile: " + last_error(out))
                else:
                    res.update(status="compile_error", note=last_error(out))
                return res
            rc, out = self.sh(self.test_cmd(self.timeout), timeout=self.timeout + 60)
            if rc == -999:
                res.update(status="killed", note="timed out")
            elif rc != 0:
                failed = re.findall(r"\d+ - (\S+) \(", out)
                res.update(status="killed", note="failed: " + (", ".join(failed[:3]) or "a test"))
            else:
                res.update(status="survived", note=m["what"])
            return res
        finally:
            with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
                fh.write(original)
            # A restored file must look newer than the mutant's object, so the next build recompiles it.
            os.utime(path, ns=(stat.st_atime_ns, max(stat.st_mtime_ns, time.time_ns())))


def last_error(out: str) -> str:
    errs = [ln for ln in out.splitlines() if "error" in ln.lower()]
    return (errs[0] if errs else (out.strip().splitlines() or ["?"])[-1])[:160]


def cmd_run(a) -> int:
    root = os.path.abspath(a.root)
    with open(a.mutants, encoding="utf-8") as fh:
        doc = json.load(fh)
    todo = [m for m in doc["mutants"] if not m["equivalent"] and shard_of(m["id"], a.shards) == a.shard]
    print(f"shard {a.shard + 1}/{a.shards}: {len(todo)} mutant(s), {a.workers} worker(s)")
    results: list[dict] = []
    started = time.monotonic()
    if not todo:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"shard": a.shard, "results": [], "baseline": "no mutant in this shard"}, fh)
        return 0
    workers_n = max(1, min(a.workers, len(todo)))
    with tempfile.TemporaryDirectory(prefix="ru-mutation-", dir=a.work_dir or None) as work:
        workers = [Worker(root, os.path.join(work, f"w{i}"), a) for i in range(workers_n)]
        status: list = [None] * workers_n

        def setup(i):
            status[i] = workers[i].baseline()
        threads = [threading.Thread(target=setup, args=(i,)) for i in range(workers_n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        ok, note = status[0]
        print(note.splitlines()[0] if ok else note)
        if not all(s[0] for s in status):
            bad = next(s[1] for s in status if not s[0])
            print("::error::the unedited tree does not build and pass its tests, so no verdict can be read: "
                  + bad.splitlines()[0])
            print(bad)
            with open(a.out, "w", encoding="utf-8") as fh:
                json.dump({"shard": a.shard, "results": [], "baseline": "failed", "note": bad[-2000:]}, fh)
            return 2
        lock = threading.Lock()
        queue = list(todo)

        def loop(w: Worker):
            while True:
                with lock:
                    if not queue:
                        return
                    m = queue.pop(0)
                t0 = time.monotonic()
                r = w.mutate(m)
                r["seconds"] = round(time.monotonic() - t0, 1)
                with lock:
                    results.append(r)
                    print(f"[{len(results)}/{len(todo)}] {r['id']:24} {r['status']:13} {m['file']}:{m['line']} "
                          f"{r['note'][:90]}", flush=True)
        threads = [threading.Thread(target=loop, args=(w,)) for w in workers]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"shard": a.shard, "results": sorted(results, key=lambda r: r["id"]), "baseline": "passed",
                   "seconds": round(time.monotonic() - started, 1)}, fh, indent=1)
    return 0


# ----------------------------------------------------------------------------------------------------------- report

STATUS_MTE = {"killed": "Killed", "survived": "Survived", "compile_error": "CompileError", "broken": "RuntimeError",
              "equivalent": "Ignored", "missing": "Pending"}


def cmd_report(a) -> int:
    with open(a.mutants, encoding="utf-8") as fh:
        doc = json.load(fh)
    mutants = {m["id"]: m for m in doc["mutants"]}
    results: dict[str, dict] = {}
    baseline_failed = []
    files = []
    for r in a.results:
        files += glob.glob(os.path.join(r, "**", "*.json"), recursive=True) if os.path.isdir(r) else [r]
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if not isinstance(d, dict) or "results" not in d:
            continue
        if d.get("baseline") == "failed":
            baseline_failed.append(d.get("note", ""))
        for x in d["results"]:
            results[x["id"]] = x
    rows = []
    for mid, m in sorted(mutants.items(), key=lambda kv: (kv[1]["file"], kv[1]["line"], kv[0])):
        if m["equivalent"]:
            rows.append((m, {"status": "equivalent", "note": m["equivalent"]}))
        else:
            rows.append((m, results.get(mid, {"status": "missing", "note": "no result (shard failed or cancelled)"})))
    count = {s: 0 for s in ("killed", "survived", "compile_error", "broken", "equivalent", "missing")}
    for _, r in rows:
        count[r["status"]] = count.get(r["status"], 0) + 1
    scored = count["killed"] + count["survived"]
    rate = 100.0 if scored == 0 else 100.0 * count["killed"] / scored
    threshold = float(a.threshold) if a.threshold not in (None, "") else LEVELS[a.level]
    problems = []
    if baseline_failed:
        problems.append("the unedited tree did not pass its tests")
    if rate + 1e-9 < threshold:
        problems.append(f"kill rate {rate:.1f} % is below {threshold:g} %")
    if count["missing"]:
        problems.append(f"{count['missing']} mutant(s) have no result")
    if a.level == "high" and count["broken"]:
        problems.append(f"{count['broken']} catalogue mutant(s) are broken (the catalogue drifted from the code)")
    passed = not problems
    os.makedirs(a.report_dir, exist_ok=True)
    write_mte(rows, a.root, threshold, os.path.join(a.report_dir, "mutation-report.json"))
    lines = [f"### Mutation testing ({doc.get('mode', '?')}, level {a.level})", "",
             f"Kill rate **{rate:.1f} %** (threshold {threshold:g} %): {count['killed']} killed, "
             f"{count['survived']} survived, {count['compile_error']} did not compile (not scored), "
             f"{count['broken']} broken, {count['equivalent']} equivalent (not run), {count['missing']} missing.", ""]
    shown = [(m, r) for m, r in rows if r["status"] in ("survived", "broken", "missing")]
    if shown:
        lines += ["| Mutant | Where | Verdict | Edit or note |", "| --- | --- | --- | --- |"]
        for m, r in shown[:200]:
            edit = m["what"] if r["status"] == "survived" else r["note"]
            lines.append(f"| `{m['id']}` | `{m['file']}:{m['line']}` | {r['status']} | {cell(edit)} |")
        if len(shown) > 200:
            lines.append(f"| ... | {len(shown) - 200} more in the artifact | | |")
        lines.append("")
    lines.append("**Passed.**" if passed else "**Failed:** " + "; ".join(problems) + ".")
    lines.append("")
    lines.append("A survivor is fixed by a test that kills it, or recorded in the equivalents file with the reason "
                 "the edit cannot change behaviour; never by deleting the mutant.")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(a.report_dir, "mutation-report.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(os.path.join(a.report_dir, "mutation-results.json"), "w", encoding="utf-8") as fh:
        json.dump([dict(m, **{"status": r["status"], "note": r.get("note", "")}) for m, r in rows], fh, indent=1)
    print(text)
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(text)
    level = "error" if a.enforce == "true" else "warning"
    for m, r in shown[:50]:
        where = os.path.normpath(os.path.join(a.annotate_prefix, m["file"])) if a.annotate_prefix else m["file"]
        print(f"::{level} file={where},line={max(m['line'], 1)},col={max(m['column'], 1)},"
              f"title=mutant {r['status']}::{m['id']}: {m['what']}"
              + ("" if r["status"] == "survived" else f" ({r['note'][:120]})"))
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"kill_rate={rate:.1f}\nkilled={count['killed']}\nsurvived={count['survived']}\n"
                     f"broken={count['broken']}\ncompile_errors={count['compile_error']}\n"
                     f"equivalent={count['equivalent']}\ntotal={len(rows)}\npassed={'true' if passed else 'false'}\n")
    for p in problems:
        print(f"::{level}::{p}")
    return 1 if (problems and a.enforce == "true") else 0


def cell(s: str) -> str:
    return " ".join(str(s).split()).replace("|", "\\|")[:140]


def write_mte(rows, root: str, threshold: float, path: str) -> None:
    """The report in the mutation-testing-elements schema (https://github.com/stryker-mutator/mutation-testing-elements)."""
    files: dict[str, dict] = {}
    for m, r in rows:
        f = files.get(m["file"])
        if f is None:
            src = ""
            full = os.path.join(root, m["file"])
            if os.path.isfile(full):
                with open(full, encoding="utf-8", errors="replace") as fh:
                    src = fh.read()
            f = files[m["file"]] = {"language": "cpp", "source": src, "mutants": []}
        line, col = max(m["line"], 1), max(m["column"], 1)
        old = m["old"].split("\n")
        end_line = line + len(old) - 1
        end_col = (len(old[-1]) + (col if len(old) == 1 else 1))
        f["mutants"].append({
            "id": m["id"], "mutatorName": m["operator"], "replacement": m["new"],
            "location": {"start": {"line": line, "column": col}, "end": {"line": end_line, "column": end_col}},
            "status": STATUS_MTE.get(r["status"], "Pending"),
            "statusReason": r.get("note", ""), "description": m["what"],
        })
    doc = {"$schema": "https://git.io/mutation-testing-schema", "schemaVersion": "2",
           "thresholds": {"high": threshold, "low": max(0.0, threshold - 20.0)},
           "projectRoot": ".", "files": files}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)


# --------------------------------------------------------------------------------------------------------- selftest

def cmd_selftest(_a) -> int:
    bad = 0
    src = 'int f(int a, int b) { // a < b\n  const char* s = "x < y";\n  return (a < b) && !flag ? 1 : 0;\n}\n#if A < B\n'
    m = mask(src)
    if len(m) != len(src) or "x < y" in m or "// a" in m or "#if" in m:
        print("mask leaves a comment, a string or a preprocessor line")
        bad += 1
    ops = sorted(op for op, *_ in candidates(m.split("\n")[2]))
    if ops != ["const", "const", "lcr-and", "neg", "ror-lt"]:
        print(f"operators on the return line: {ops}")
        bad += 1
    if list(candidates("std::vector<int> v; p->x; a << 2;")) and any(
            op.startswith("ror") for op, *_ in candidates("std::vector<int> v; p->x; a << 2;")):
        print("template brackets, -> or << were mutated")
        bad += 1
    print(f"selftest: {bad} problem(s)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("--root", default=".")
    p.add_argument("--paths", default="")
    p.add_argument("--catalogue", action="append", default=[])
    p.add_argument("--mode", default="auto", choices=["auto", "catalogue", "generated", "both"])
    p.add_argument("--equivalents", default="")
    p.add_argument("--max", type=int, default=0)
    p.add_argument("--out", required=True)
    p = sub.add_parser("run")
    p.add_argument("--root", default=".")
    p.add_argument("--mutants", required=True)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--shards", type=int, default=1)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--build-parallel", type=int, default=2)
    p.add_argument("--cmake-args", default="")
    p.add_argument("--source-dir", default=".")
    p.add_argument("--build-target", default="")
    p.add_argument("--ctest-args", default="")
    p.add_argument("--timeout-factor", type=float, default=3.0)
    p.add_argument("--work-dir", default="")
    p.add_argument("--out", required=True)
    p = sub.add_parser("report")
    p.add_argument("--root", default=".")
    p.add_argument("--mutants", required=True)
    p.add_argument("--results", nargs="+", required=True)
    p.add_argument("--level", default="high", choices=sorted(LEVELS))
    p.add_argument("--threshold", default="")
    p.add_argument("--report-dir", default="mutation-report")
    p.add_argument("--summary")
    p.add_argument("--github-output")
    p.add_argument("--enforce", default="true", choices=["true", "false"])
    p.add_argument("--annotate-prefix", default="", help="path of --root from the repository root, for annotations")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "run" and not (0 <= a.shard < a.shards):
        ap.error("--shard must be in [0, --shards)")
    return {"list": cmd_list, "run": cmd_run, "report": cmd_report, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
