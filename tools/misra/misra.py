#!/usr/bin/env python3
"""The steps of ru-misra that are not tool invocations: licence gate, deviation records, run-time assurance, report.

Commands:

  licence   --private true|false --advanced-security true|false [--repo .]
      May the CodeQL CLI run on this repository? (docs/tool-validation/plan.md, "CodeQL licence")
  prepare   --records <project-wide records> [--repo-records docs/deviations.yml] --paths "inc src"
            --coding-standards <out.yml> --markers <out.json> [--today YYYY-MM-DD]
      Validate the deviation records, turn them into the coding-standards deviation configuration (one record per
      code identifier, so a suppression must cite a record id), and scan the sources for suppression markers.
  flags     --compdb compile_commands.json --paths "inc src" --out flags.json [--canary FILE]
      Does every translation unit build with the flags the compiler-decided guidelines rely on?
  extraction --compdb compile_commands.json --compiled compiled.json --diagnostics diagnostics.json
            --paths "inc src" --out extraction.json [--canary FILE]
      Did CodeQL extract every translation unit of the build and every source file under the paths, without errors?
  tidy-configs --cases tests/misra-validation/cases --out configs.json
      The validated clang-tidy configurations (one per distinct check and options) and the guidelines each decides.
  report    --matrix misra-cpp-2023.yml --config <name>=<dir> ... --markers markers.json --level high|safety
            --out-dir DIR [--canary-expect cpp/misra/a,kokeb/...]
      Merge the configurations' results into one per-guideline summary (step summary, JSON keyed by guideline,
      CSV), apply the level's failure policy, and exit 1 when it fails.

Every command exits 0 on success, 1 on a failing check, 2 on bad input. PyYAML is the only dependency.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import shlex
import urllib.parse
import subprocess
import sys

import yaml

RECORD_ID = re.compile(r"\b(MD-CPP-\d{3}|DEV-\d{3})\b")
# The code-identifier marker forms of the coding-standards pack (user manual, "Deviation code identifier comments"),
# for any standard name, so a marker for another standard is reported instead of silently ignored.
CODEQL_MARKER = re.compile(r"codeql::(\w+?)_deviation(?:_next_line|_begin|_end)?\(\s*\"?([^)\"]*)\"?\s*\)")
CODEQL_ATTRIBUTE = re.compile(r"\[\[\s*codeql::(\w+?)_deviation\(([^\]]*)\)\s*\]\]")
TOOL_SUPPRESSION = re.compile(r"NOLINT(NEXTLINE|BEGIN|END)?\b(?:\(([^)]*)\))?|cppcheck-suppress\s+\S+")
SOURCE_EXT = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ipp", ".tpp", ".inl")
# The flags the compiler-decided guidelines of the matrix rely on (tests/misra-validation/validate.py ORG_FLAGS).
REQUIRED_FLAGS = ["-Wall", "-Wextra", "-Wpedantic", "-Wshadow", "-Wundef", "-Werror", "-fno-exceptions", "-fno-rtti"]
OSI_LICENCE = re.compile(r"MIT License|Permission is hereby granted, free of charge|Apache License|BSD|"
                         r"Mozilla Public License|GNU (Lesser |Affero )?General Public License|ISC License|"
                         r"Boost Software License", re.I)


def emit(kind: str, msg: str, file: str = "", line: int = 0) -> None:
    loc = f" file={file}" + (f",line={line}" if line else "") if file else ""
    print(f"::{kind}{loc}::{msg}")


def guideline_id(tag: str) -> str:
    """rule-8-2-5 -> Rule 8.2.5; dir-0-3-1 -> Dir 0.3.1; kb-cpp-046 -> KB-CPP-046."""
    m = re.fullmatch(r"(rule|dir)-(\d+(?:-\d+)+)", tag)
    if m:
        return f"{m.group(1).capitalize()} {m.group(2).replace('-', '.')}"
    return tag.upper()


def pack_rule_id(gid: str) -> str:
    """Rule 8.2.5 -> RULE-8-2-5 (the rule-id the coding-standards configuration uses)."""
    kind, num = gid.split(" ", 1)
    return f"{kind.upper()}-{num.replace('.', '-')}"


def split_paths(text: str) -> list[str]:
    return [p.strip().strip("/") for p in re.split(r"[\s,]+", text or "") if p.strip()]


def under(path: str, prefixes: list[str]) -> bool:
    path = path.replace(os.sep, "/").lstrip("./")
    return not prefixes or any(p in (".", "") or path == p or path.startswith(p + "/") for p in prefixes)


def git_files(repo: str) -> list[str]:
    try:
        out = subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True, text=True, check=True).stdout
        return out.split()
    except (OSError, subprocess.CalledProcessError):
        files = []
        for d, _dirs, names in os.walk(repo):
            if "/." in d.replace(os.sep, "/"):
                continue
            files += [os.path.relpath(os.path.join(d, n), repo) for n in names]
        return files


# --- licence -------------------------------------------------------------------------------------------------


def osi_licence(repo: str) -> tuple[str | None, str | None]:
    """The repository's licence file and an error, if it is missing or not an OSI-approved licence."""
    lic = next((os.path.join(repo, n) for n in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
                if os.path.isfile(os.path.join(repo, n))), None)
    if not lic:
        return None, "No LICENSE file: CodeQL may run only on code released under an OSI-approved licence."
    with open(lic, encoding="utf-8", errors="replace") as fh:
        if not OSI_LICENCE.search(fh.read(4000)):
            return lic, f"{lic} does not look like an OSI-approved licence; CodeQL may not run."
    return lic, None


def cmd_licence(a) -> int:
    """The CodeQL Terms allow analysis of an Open Source Codebase (released under an OSI-approved licence) and, when
    it is hosted on GitHub.com, CI use; any other codebase needs a paid Advanced Security licence. A private
    repository may run it only when the caller declares it an open-source pre-release: its code is under the OSI
    licence in its LICENSE file and is to be published. That declaration is the caller's, and is printed."""
    if a.advanced_security == "true":
        print("CodeQL may run: the caller states a paid GitHub Advanced Security / Code Security licence.")
        return 0
    if a.private == "true" and a.open_source_prerelease != "true":
        emit("error", "CodeQL may not run on a private repository without a paid GitHub Advanced Security / Code "
                      "Security licence (CodeQL Terms and Conditions, License Restrictions). Make the repository "
                      "public under its OSI licence; set open_source_prerelease: true if its code is released "
                      "under that licence and is to be published; or set advanced_security: true if the licence "
                      "is held.")
        return 1
    lic, err = osi_licence(a.repo)
    if err:
        emit("error", err)
        return 1
    name = os.path.basename(lic)
    if a.private == "true":
        emit("warning", f"CodeQL runs on a private repository declared an open-source pre-release ({name} is an "
                        "OSI-approved licence). The declaration is the caller's; results stay in the run's artifact.")
        return 0
    print(f"CodeQL may run: public repository on GitHub.com, {name} is an OSI-approved licence.")
    return 0


# --- deviation records and markers ---------------------------------------------------------------------------


def load_records(path: str, repo_path: str | None, today: dt.date) -> tuple[dict, list[str]]:
    errors, records = [], {}
    with open(path, encoding="utf-8") as fh:
        for r in (yaml.safe_load(fh) or {}).get("deviations", []):
            records[r["id"]] = {"id": r["id"], "guideline": r["guideline"], "scope": " ".join(str(r["scope"]).split()),
                                "justification": " ".join(str(r["justification"]).split()),
                                "approved_by": r.get("approved_by", ""), "date": str(r.get("date", "")),
                                "review_by": str(r.get("review_by", "")), "where": None, "kind": "project"}
    if repo_path and os.path.isfile(repo_path):
        with open(repo_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or []
        for r in data if isinstance(data, list) else data.get("deviations", []):
            m = re.fullmatch(r"(?:misra|codeql)/((?:Rule|Dir) \d+(?:\.\d+)+)", str(r.get("check", "")))
            if not m:
                continue  # a record for another check (clang-tidy, cppcheck): not a MISRA CodeQL deviation
            records[r["id"]] = {"id": r["id"], "guideline": m.group(1), "scope": str(r.get("where", "")),
                                "justification": " ".join(str(r.get("reason", "")).split()),
                                "approved_by": str(r.get("approved_by", "")), "date": str(r.get("date", "")),
                                "review_by": str(r.get("review_by", "")), "where": r.get("where"), "kind": "repo"}
    for r in records.values():
        if r["review_by"]:
            try:
                if dt.date.fromisoformat(r["review_by"]) < today:
                    errors.append(f"deviation record {r['id']} lapsed on {r['review_by']}: renew or withdraw it")
            except ValueError:
                errors.append(f"deviation record {r['id']}: review_by {r['review_by']!r} is not a date")
    return records, errors


def suppression_needs_record(m: re.Match, matrix_checks: set[str] | None) -> bool:
    """A tool suppression must cite a deviation record when it can silence a finding the matrix relies on: a
    cppcheck suppression, a bare NOLINT, or a NOLINT naming a validated clang-tidy check (globs included). The
    NOLINTEND that closes a region does not repeat the citation."""
    if not m.group(0).startswith("NOLINT"):
        return True
    if m.group(1) == "END":
        return False
    if not m.group(2) or matrix_checks is None:
        return True
    named = [c.strip() for c in m.group(2).split(",") if c.strip()]
    return any(fnmatch.fnmatchcase(v, c) for c in named for v in matrix_checks) or "*" in named


def scan_markers(repo: str, paths: list[str], known: dict,
                 matrix_checks: set[str] | None = None) -> tuple[list[dict], list[dict]]:
    """Every suppression marker in the sources, and the errors among them."""
    markers, errors = [], []
    for f in git_files(repo):
        if not f.endswith(SOURCE_EXT) or not under(f, paths) or f.startswith(".ru-misra/"):
            continue
        try:
            with open(os.path.join(repo, f), encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            comment = line.split("//", 1)[1].strip() if "//" in line else ""
            found = []
            for m in CODEQL_ATTRIBUTE.finditer(line):
                ids = [x.strip().strip('"') for x in m.group(2).split(",")]
                found += [(m.group(1), i, "attribute") for i in ids]
            for m in CODEQL_MARKER.finditer(comment):
                found.append((m.group(1), m.group(2).strip(), "comment"))
            if not found and comment:
                # The pack also accepts a bare code identifier at the start or end of a comment.
                for i in {comment.split()[0].rstrip(".,;:"), comment.split()[-1].rstrip(".,;:")}:
                    if RECORD_ID.fullmatch(i):
                        found.append(("misra", i, "bare"))
            for std, ident, form in found:
                mk = {"file": f, "line": n, "id": ident, "form": form, "standard": std}
                markers.append(mk)
                if std != "misra":
                    errors.append({**mk, "error": f"codeql::{std}_deviation is not a MISRA deviation"})
                elif ident not in known:
                    errors.append({**mk, "error": f"{ident} is not a deviation record"})
                elif known[ident]["where"] and not under(f, split_paths(str(known[ident]["where"]))):
                    errors.append({**mk, "error": f"{ident} applies only to {known[ident]['where']}"})
            # A tool suppression (NOLINT, cppcheck-suppress) silences a finding the matrix may rely on: it must cite
            # the record that allows it.
            sup = TOOL_SUPPRESSION.search(comment)
            if sup:
                ids = RECORD_ID.findall(comment)
                if not ids and suppression_needs_record(sup, matrix_checks):
                    errors.append({"file": f, "line": n, "id": "", "form": "tool", "standard": "",
                                   "error": "a NOLINT or cppcheck-suppress must cite its deviation record id"})
                for i in ids:
                    if i not in known:
                        errors.append({"file": f, "line": n, "id": i, "form": "tool", "standard": "",
                                       "error": f"{i} is not a deviation record"})
    return markers, errors


def cmd_prepare(a) -> int:
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    records, errors = load_records(a.records, a.repo_records, today)
    paths = split_paths(a.paths)
    for f in git_files(a.repo):
        if os.path.basename(f) in ("coding-standards.yml", "coding-standards.yaml"):
            errors.append(f"{f}: deviations come only from the deviation records; remove this file")
    matrix_checks = None
    if a.tidy_configs:
        with open(a.tidy_configs, encoding="utf-8") as fh:
            matrix_checks = {c["check"] for c in json.load(fh)}
    markers, marker_errors = scan_markers(a.repo, paths, records, matrix_checks)
    deviations = []
    for r in records.values():
        if not re.fullmatch(r"(Rule|Dir) \d+(\.\d+)+", r["guideline"]):
            continue
        d = {"rule-id": pack_rule_id(r["guideline"]), "code-identifier": r["id"],
             "justification": f"{r['id']}: {r['justification']}"[:2000], "scope": r["scope"][:2000]}
        if r["approved_by"] and r["date"]:
            d["raised-by"] = {"name": str(r["approved_by"]), "date": r["date"]}
            d["approved-by"] = {"name": str(r["approved_by"]), "date": r["date"]}
        deviations.append(d)
    with open(a.coding_standards, "w", encoding="utf-8") as fh:
        fh.write("# Generated by ru-misra from the deviation records; never committed.\n")
        yaml.safe_dump({"report-deviated-alerts": True, "deviations": deviations}, fh, sort_keys=False)
    with open(a.markers, "w", encoding="utf-8") as fh:
        json.dump({"records": records, "markers": markers, "marker_errors": marker_errors, "errors": errors}, fh,
                  indent=1)
    for e in errors:
        emit("error", e)
    for e in marker_errors:
        emit("error", e["error"], e["file"], e["line"])
    print(f"{len(records)} deviation record(s), {len(markers)} marker(s), "
          f"{len(errors) + len(marker_errors)} error(s)")
    return 1 if errors or marker_errors else 0


# --- build flags and extraction coverage ---------------------------------------------------------------------


def object_path(directory: str, output: str) -> str:
    """Where a compile database entry's object file is. CMake's Makefile generator writes `output` relative to the
    top of the build tree while `directory` is the target's subdirectory, so the nearest ancestor of `directory`
    that holds the file is taken; with none, the path relative to `directory` (the documented meaning)."""
    if os.path.isabs(output):
        return output
    d = os.path.abspath(directory)
    while True:
        cand = os.path.join(d, output)
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.join(os.path.abspath(directory), output)
        d = parent


def compdb_units(path: str, paths: list[str], canary: str | None) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        db = json.load(fh)
    units = []
    for e in db:
        f = os.path.normpath(os.path.join(e.get("directory", ""), e["file"]))
        args = e.get("arguments") or shlex.split(e.get("command", ""))
        out = object_path(e.get("directory", ""), e["output"]) if e.get("output") else None
        units.append({"file": f, "args": args, "output": out,
                      "canary": bool(canary) and os.path.normpath(f) == os.path.normpath(os.path.abspath(canary))})
    return units


def cmd_flags(a) -> int:
    units = compdb_units(a.compdb, [], None)
    root = os.path.abspath(a.repo)
    missing = {}
    for u in units:
        have = set(u["args"])
        for flag in REQUIRED_FLAGS:
            if flag not in have and not (flag == "-Werror" and any(x.startswith("-Werror") for x in have)):
                missing.setdefault(flag, []).append(os.path.relpath(u["file"], root))
    out = {"units": len(units), "required": REQUIRED_FLAGS, "missing": missing,
           "complete": not missing and bool(units)}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    for flag, files in missing.items():
        emit("warning", f"{len(files)}/{len(units)} translation unit(s) build without {flag}: the guidelines the "
                        f"matrix assigns to that compiler flag are not enforced by this build (e.g. {files[0]})")
    print(f"{len(units)} translation unit(s); flags missing: {sorted(missing) or 'none'}")
    return 0


def cmd_extraction(a) -> int:
    """Run-time assurance: the scan analysed what the build compiled, and every source file under the paths."""
    root = os.path.abspath(a.repo)
    paths = split_paths(a.paths)
    units = compdb_units(a.compdb, paths, None)
    # `codeql bqrs decode --format=json` of the own pack's diagnostics/CompiledFiles.ql and ExtractionDiagnostics.ql.
    with open(a.compiled, encoding="utf-8") as fh:
        rows = json.load(fh)["#select"]["tuples"]  # [absolute path, relative path, compiled as a unit]
    with open(a.diagnostics, encoding="utf-8") as fh:
        diags = [{"file": r[0], "line": r[1], "severity": r[2], "message": r[3]}
                 for r in json.load(fh)["#select"]["tuples"]]
    compiled_units = {os.path.normpath(r[0]) for r in rows if r[2] is True}
    db_files = {str(r[1]).replace(os.sep, "/") for r in rows}
    problems = []
    if not units:
        problems.append("the compile database is empty: nothing was built")
    # A unit the build defines but never compiles (a target excluded from `all`, such as a compile-fail test)
    # has no object file. It is not analysed, and says so; anything the build compiled must be in the database.
    # Only when the build left objects behind can their absence be told from a deleted build directory.
    built = [u for u in units if u["output"] and os.path.isfile(u["output"])]
    not_built = [u for u in units if built and u["output"] and not os.path.isfile(u["output"])]
    if not_built:
        print(f"{len(not_built)} unit(s) defined but not built by the traced build (not analysed): "
              + ", ".join(os.path.relpath(u["file"], root) for u in not_built[:20]))
    for u in units:
        if u in not_built:
            continue
        if os.path.normpath(u["file"]) not in compiled_units:
            problems.append(f"translation unit {os.path.relpath(u['file'], root)} is in the build but not in the "
                            "CodeQL database")
    sources = [f for f in git_files(root) if f.endswith(SOURCE_EXT) and under(f, paths)]
    not_analysed = [f for f in sources if f not in db_files]
    for f in not_analysed:
        problems.append(f"{f} is under the analysed paths but no translation unit of this configuration includes it")
    # Errors (4) and catastrophes (5) mean code the front end could not model: the scan is incomplete. A
    # discretionary error (3) is an error the front end may relax: reported, not failed.
    errors = [d for d in diags if d["severity"] >= 4 and (not d["file"] or under(d["file"], paths))]
    for d in errors:
        problems.append(f"extraction error in {d['file'] or '(no file)'}:{d['line']}: {d['message']}")
    for d in diags:
        if d["severity"] == 3 and under(d["file"], paths):
            emit("warning", f"extractor discretionary error: {d['message']}", d["file"], d["line"])
    if a.canary and os.path.normpath(os.path.abspath(a.canary)) not in compiled_units:
        problems.append("the canary translation unit is not in the database: the build was not traced")
    out = {"translation_units": len(units),
           "extracted_units": len(compiled_units), "source_files": len(sources),
           "analysed_source_files": len(sources) - len(not_analysed), "not_analysed": not_analysed,
           "extraction_errors": errors, "problems": problems, "complete": not problems}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    for p in problems:
        emit("error", p)
    print(f"{out['translation_units']} translation unit(s) built, {out['extracted_units']} extracted; "
          f"{out['analysed_source_files']}/{out['source_files']} source file(s) under the paths analysed; "
          f"{len(errors)} extraction error(s)")
    return 1 if problems else 0


# --- clang-tidy configurations from the validation suite ------------------------------------------------------


def cmd_tidy_configs(a) -> int:
    configs = {}
    for root in a.cases:
        for d in sorted(os.listdir(root)):
            p = os.path.join(root, d, "case.yml")
            if not os.path.isfile(p):
                continue
            with open(p, encoding="utf-8") as fh:
                spec = yaml.safe_load(fh) or {}
            t = spec.get("clang-tidy")
            if not t:
                continue
            key = json.dumps({"check": t["check"], "options": t.get("options") or {}, "config": t.get("config") or {},
                              "message": t.get("message", "")}, sort_keys=True)
            c = configs.setdefault(key, {**json.loads(key), "guidelines": [], "cases": []})
            if spec["guideline"] not in c["guidelines"]:
                c["guidelines"].append(spec["guideline"])
            c["cases"].append(d)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(list(configs.values()), fh, indent=1)
    print(f"{len(configs)} validated clang-tidy configuration(s)")
    return 0


def cmd_tidy(a) -> int:
    """Each validated clang-tidy configuration over the build's translation units (the same compile database the
    CodeQL scan traced), mapped to the guidelines that configuration is validated for."""
    import concurrent.futures as cf
    root = os.path.abspath(a.repo)
    paths = split_paths(a.paths)
    with open(a.configs, encoding="utf-8") as fh:
        configs = json.load(fh)
    units = [u["file"] for u in compdb_units(a.compdb, paths, None)]
    pattern = re.compile(r"^([^\n:]+):(\d+):\d+: (?:warning|error): (.*?) \[([^\]\n]+)\]$", re.M)
    header_filter = "^" + re.escape(root) + "/(" + "|".join(re.escape(p) for p in paths) + ")/" if paths else ".*"

    def run(job):
        cfg, unit = job
        conf = {"Checks": f"-*,{cfg['check']}", "WarningsAsErrors": "", "HeaderFilterRegex": header_filter,
                **cfg.get("config", {}), "CheckOptions": {k: (str(v).lower() if isinstance(v, bool) else str(v))
                                                         for k, v in (cfg.get("options") or {}).items()}}
        r = subprocess.run([a.clang_tidy, "--quiet", f"--config={json.dumps(conf)}", "-p", os.path.dirname(a.compdb),
                            unit], capture_output=True, text=True)
        return cfg, r.stdout + r.stderr

    jobs = [(c, u) for c in configs for u in units]
    findings = {}
    with cf.ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        for cfg, out in ex.map(run, jobs):
            for m in pattern.finditer(out):
                f = os.path.relpath(os.path.normpath(os.path.join(root, m.group(1))), root)
                if cfg["check"] not in [x.strip() for x in m.group(4).split(",")] or not under(f, paths):
                    continue
                if cfg.get("message") and not re.search(cfg["message"], m.group(3)):
                    continue  # the check reports more than the guideline; only these messages decide it
                for g in cfg["guidelines"]:
                    k = (g, cfg["check"], f, int(m.group(2)))
                    findings[k] = {"tool": "clang-tidy", "query": cfg["check"], "guideline": g, "file": f,
                                   "line": int(m.group(2)), "message": m.group(3), "deviated": False}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(sorted(findings.values(), key=lambda x: (x["guideline"], x["file"], x["line"])), fh, indent=1)
    print(f"clang-tidy: {len(configs)} validated configuration(s) over {len(units)} translation unit(s), "
          f"{len(findings)} finding(s)")
    return 0


def cmd_cppcheck(a) -> int:
    """cppcheck on the same compile database; its message ids map to guidelines through the matrix's cppcheck
    entries, all partial (they find violations, they never prove absence)."""
    import xml.etree.ElementTree as ET
    root = os.path.abspath(a.repo)
    paths = split_paths(a.paths)
    with open(a.matrix, encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)["guidelines"]
    ids = {}
    for g in matrix:
        for v in g["verification"]:
            if v["by"] == "cppcheck":
                for i in re.findall(r"[A-Za-z][A-Za-z0-9_]+", v["how"].split("(")[0]):
                    ids.setdefault(i, []).append(g["id"])
    xml = os.path.join(os.path.dirname(a.out), "cppcheck.xml")
    subprocess.run(["cppcheck", f"--project={a.compdb}", "--enable=warning,style,performance,portability",
                    "--inline-suppr", "--suppress=missingIncludeSystem", "--xml", f"--output-file={xml}",
                    "--quiet", f"-j{os.cpu_count() or 2}"], check=False)
    findings = []
    if os.path.isfile(xml):
        for err in ET.parse(xml).getroot().iter("error"):
            loc = err.find("location")
            if loc is None or err.get("id") not in ids:
                continue
            f = os.path.relpath(os.path.normpath(os.path.join(root, loc.get("file"))), root)
            if not under(f, paths):
                continue
            for g in ids[err.get("id")]:
                findings.append({"tool": "cppcheck", "query": err.get("id"), "guideline": g, "file": f,
                                 "line": int(loc.get("line", 0)), "message": err.get("msg", ""), "deviated": False})
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=1)
    print(f"cppcheck: {len(findings)} finding(s) for guidelines the matrix maps to cppcheck message ids")
    return 0


# --- report --------------------------------------------------------------------------------------------------


def sarif_results(path: str, root: str) -> list[dict]:
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
            uri = loc.get("artifactLocation", {}).get("uri", "")
            if uri.startswith("file://"):
                uri = os.path.relpath(uri[7:], root)
            out.append({"tool": "codeql", "query": rid, "guideline": guideline_id(rules.get(rid, "")) if rules.get(rid)
                        else "", "file": uri, "line": loc.get("region", {}).get("startLine", 0),
                        "message": (res.get("message") or {}).get("text", ""),
                        "deviated": bool(res.get("suppressions"))})
    return out


def load_suppression_scopes(path: str) -> list[dict]:
    """Rows of the pack's DeviationsSuppression query: the scope each marker covers, and the query it deviates."""
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    rows = (data.get("#select") or {}).get("tuples", [])
    scopes = []
    for row in rows:
        text, scope = row[1], row[3]
        url = scope.get("url", {}) if isinstance(scope, dict) else {}
        m = re.search(r"lgtm\[([^\]]+)\]", str(text))
        uri = urllib.parse.unquote(re.sub(r"^file:(//)?", "", url.get("uri", "")))
        scopes.append({"query": m.group(1) if m else "", "file": uri,
                       "start": url.get("startLine", 0), "end": url.get("endLine", 0),
                       "label": scope.get("label", "") if isinstance(scope, dict) else str(scope)})
    return scopes


def cmd_report(a) -> int:
    root = os.path.abspath(a.repo)
    paths = split_paths(a.paths)
    with open(a.matrix, encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)["guidelines"]
    with open(a.markers, encoding="utf-8") as fh:
        marks = json.load(fh)
    records = marks["records"]
    supported = {}
    if a.supported:
        with open(a.supported, encoding="utf-8") as fh:
            supported = {g: [q["id"] for q in qs if not q["audit"]] for g, qs in json.load(fh)["guidelines"].items()}
    # A rule the tool validation found reporting compliant code (a false positive in the anomaly log) does not
    # decide its guideline alone: at the high level its findings are listed for review with the anomaly ids, and
    # do not fail the job (MISRA Compliance:2020 §3.4: a false diagnosis is investigated, not deviated). The
    # safety level fails on them as on any other finding; the commercial checker and the review decide there.
    known_fp: dict[tuple[str, str], list[str]] = {}
    if a.anomalies:
        with open(a.anomalies, encoding="utf-8") as fh:
            for an in (yaml.safe_load(fh) or {}).get("anomalies", []):
                if an.get("kind") == "false-positive":
                    known_fp.setdefault((an.get("tool", "codeql"), an["rule_id"]), []).append(an["id"])
    canary_expect = [q for q in (a.canary_expect or "").split(",") if q]
    findings, configs, problems, warnings = [], [], [], []
    for spec in a.config:
        name, d = spec.split("=", 1)
        cfg = {"name": name, "dir": d}
        sarif = os.path.join(d, "results.sarif")
        if not os.path.isfile(sarif):
            problems.append(f"{name}: no CodeQL results (results.sarif missing): the scan did not run")
            configs.append(cfg)
            continue
        res = sarif_results(sarif, root)
        # Canary: the known-violating file analysed with every scan must be reported, query by query.
        canary = [r for r in res if os.path.basename(r["file"]).startswith("ru_misra_canary")]
        cfg["canary_found"] = sorted({r["query"] for r in canary})
        missing = [q for q in canary_expect if q not in cfg["canary_found"]]
        if missing:
            problems.append(f"{name}: the canary was not detected by {', '.join(missing)}: the scan is not working")
        res = [r for r in res if r not in canary and under(r["file"], paths)]
        for r in res:
            r["config"] = name
        # Suppression markers that deviate nothing are errors: a marker must cover a finding of its record.
        scopes = load_suppression_scopes(os.path.join(d, "suppressions.json"))
        cfg["scopes"] = len(scopes)
        for s in scopes:
            rel = os.path.relpath(s["file"], root) if os.path.isabs(s["file"]) else s["file"]
            s["file"] = rel
            s["used"] = any(r["deviated"] and r["query"] == s["query"] and r["file"] == rel
                            and s["start"] <= r["line"] <= max(s["end"], s["start"]) for r in res)
        cfg["unused_scopes"] = [s for s in scopes if not s["used"] and under(s["file"], paths)]
        for extra in ("tidy.json", "cppcheck.json"):
            p = os.path.join(d, extra)
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as fh:
                    for r in json.load(fh):
                        if under(r["file"], paths):
                            findings.append({**r, "config": name})
        for extra, key in (("extraction.json", "extraction"), ("flags.json", "flags")):
            p = os.path.join(d, extra)
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as fh:
                    cfg[key] = json.load(fh)
        if not (cfg.get("extraction") or {}).get("complete", False):
            problems.append(f"{name}: extraction coverage is incomplete (see extraction.json)")
        findings += res
        configs.append(cfg)

    # A marker is unused only if no configuration used it (a marker may cover code one configuration compiles).
    unused = {}
    for cfg in configs:
        for s in cfg.get("unused_scopes", []):
            unused.setdefault((s["file"], s["start"], s["query"]), set()).add(cfg["name"])
    marker_errors = list(marks["marker_errors"])
    for (f, line, q), cfgs in sorted(unused.items()):
        if len(cfgs) == len([c for c in configs if "scopes" in c]):
            marker_errors.append({"file": f, "line": line, "error": f"suppression marker deviates no finding of {q} "
                                  "in any configuration: remove it, or it cites the wrong record"})

    # Merge configurations: one finding per tool, rule, file and line.
    merged = {}
    for r in findings:
        k = (r["tool"], r["query"], r["file"], r["line"])
        m = merged.setdefault(k, {**r, "configs": []})
        m["configs"].append(r["config"])
        m["deviated"] = m["deviated"] and r["deviated"]
    findings = sorted(merged.values(), key=lambda r: (r["guideline"], r["file"], r["line"]))
    for f in findings:
        f["known_fp"] = sorted(known_fp.get((f["tool"], f["query"]), []))
        f["review"] = bool(f["known_fp"]) and a.level != "safety" and not f["deviated"]

    rows = {}
    for g in matrix:
        gid = g["id"]
        tools = sorted({v["by"] for v in g["verification"]})
        rows[gid] = {"guideline": gid, "category": g["category"], "our_category": g["our_category"],
                     "applies": g["applies"] is True, "verification": tools,
                     "codeql_queries": supported.get(gid, []), "violations": 0, "deviated": 0, "review": 0,
                     "status": "", "findings": []}
    for f in findings:
        row = rows.get(f["guideline"])
        if row is None:
            rows[f["guideline"]] = row = {"guideline": f["guideline"], "category": "profile", "our_category":
                                          "required", "applies": True, "verification": [], "codeql_queries": [],
                                          "violations": 0, "deviated": 0, "review": 0, "status": "", "findings": []}
        row["deviated" if f["deviated"] else "review" if f["review"] else "violations"] += 1
        row["findings"].append({k: f[k] for k in ("tool", "query", "file", "line", "message", "deviated", "configs",
                                                  "review", "known_fp")})
    flags_ok = all((c.get("flags") or {}).get("complete") for c in configs if "flags" in c)
    for row in rows.values():
        if row["violations"]:
            row["status"] = "violations"
        elif row["review"]:
            row["status"] = "review (rule with known false positives)"
        elif row["deviated"]:
            row["status"] = "deviated"
        elif row["codeql_queries"] or row["category"] == "profile" or "clang-tidy" in row["verification"]:
            row["status"] = "no findings"
        elif "compiler" in row["verification"]:
            row["status"] = "no findings (compiler flags)" if flags_ok else "not enforced (build flags missing)"
        elif not row["applies"]:
            row["status"] = "not applicable"
        else:
            row["status"] = "review"

    # Failure policy of the level.
    failing = []
    for row in rows.values():
        if not row["violations"]:
            continue
        hard = a.level == "safety" or row["our_category"] in ("mandatory", "required")
        (failing if hard else warnings).append(row["guideline"])
    if a.level == "safety" and not flags_ok:
        problems.append("level safety: some translation units build without the flags the compiler-decided "
                        "guidelines rely on (see flags.json)")
    problems += marks["errors"]
    status = 1 if failing or problems or marker_errors else 0

    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"level": a.level, "passed": status == 0, "configurations": [
        {k: c.get(k) for k in ("name", "canary_found", "scopes", "extraction", "flags")} for c in configs],
        "problems": problems, "suppression_errors": marker_errors, "failing_guidelines": failing,
        "warning_guidelines": warnings, "records": records,
        "totals": {"violations": sum(r["violations"] for r in rows.values()),
                   "deviated": sum(r["deviated"] for r in rows.values()),
                   "review": sum(r["review"] for r in rows.values()),
                   "guidelines_with_violations": sum(1 for r in rows.values() if r["violations"]),
                   "guidelines_deviated": sum(1 for r in rows.values() if r["deviated"] and not r["violations"]),
                   "guidelines_clean": sum(1 for r in rows.values() if r["status"].startswith("no findings"))},
        "guidelines": rows}
    with open(os.path.join(a.out_dir, "misra-summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(a.out_dir, "misra-findings.csv"), "w", encoding="utf-8") as fh:
        fh.write("guideline,tool,rule,file,line,deviated,review,configurations,message\n")
        for f in findings:
            msg = f["message"].replace('"', "'").replace("\n", " ")
            review = " ".join(f["known_fp"]) if f["review"] else ""
            fh.write(f"{f['guideline']},{f['tool']},{f['query']},{f['file']},{f['line']},{f['deviated']},{review},"
                     f"{' '.join(f['configs'])},\"{msg}\"\n")
    md = render_summary(summary, a.level)
    with open(os.path.join(a.out_dir, "misra-summary.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(md)
    for f in findings:
        if f["deviated"]:
            continue
        if f["review"]:
            # Listed in the report, not as annotations: hundreds of known false positives would drown the rest.
            continue
        kind = "error" if f["guideline"] in failing else "warning"
        emit(kind, f"{f['guideline']} [{f['query']}] {f['message']}", f["file"], f["line"])
    for e in marker_errors:
        emit("error", e["error"], e.get("file", ""), e.get("line", 0))
    for p in problems:
        emit("error", p)
    t = summary["totals"]
    print(f"level {a.level}: {t['violations']} violation(s) in {t['guidelines_with_violations']} guideline(s), "
          f"{t['deviated']} deviated, {len(marker_errors)} suppression error(s), {len(problems)} problem(s): "
          f"{'pass' if status == 0 else 'FAIL'}")
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"violations={t['violations']}\ndeviated={t['deviated']}\n"
                     f"suppression_errors={len(marker_errors)}\nproblems={len(problems)}\n"
                     f"failing_guidelines={len(failing)}\npassed={'true' if status == 0 else 'false'}\n")
    return status if a.enforce == "true" else 0


def render_summary(s: dict, level: str) -> str:
    t = s["totals"]
    out = [f"### MISRA C++:2023 ({level} level): {'pass' if s['passed'] else 'FAIL'}", "",
           f"{t['violations']} violation(s) in {t['guidelines_with_violations']} guideline(s), {t['deviated']} "
           f"deviated finding(s), {t.get('review', 0)} finding(s) of rules with known false positives to review, "
           f"{t['guidelines_clean']} guideline(s) without findings. No findings is not proof of "
           "compliance for an undecidable guideline (MISRA Compliance:2020 §3.5): those keep their review step.", ""]
    out += ["| Configuration | Translation units | Source files analysed | Canary | Flags complete |",
            "| --- | --- | --- | --- | --- |"]
    for c in s["configurations"]:
        e = c.get("extraction") or {}
        out.append(f"| {c['name']} | {e.get('translation_units', '-')} | {e.get('analysed_source_files', '-')}/"
                   f"{e.get('source_files', '-')} | {'detected' if c.get('canary_found') else '**missing**'} | "
                   f"{'yes' if (c.get('flags') or {}).get('complete') else 'no'} |")
    if s["problems"] or s["suppression_errors"]:
        out += ["", "**Problems**", ""]
        out += [f"- {p}" for p in s["problems"]]
        out += [f"- `{e.get('file', '')}:{e.get('line', '')}` {e['error']}" for e in s["suppression_errors"]]
    out += ["", "| Guideline | Category (ours) | Violations | To review | Deviated | Status |",
            "| --- | --- | --- | --- | --- | --- |"]
    for row in s["guidelines"].values():
        if row["violations"] or row["deviated"] or row.get("review"):
            out.append(f"| {row['guideline']} | {row['our_category']} | {row['violations']} | {row.get('review', 0)} | "
                       f"{row['deviated']} | {row['status']} |")
    if any(r.get("review") for r in s["guidelines"].values()):
        out += ["", "*To review*: findings of a rule the tool validation found reporting compliant code (the anomaly "
                "ids are in misra-findings.csv). Each is checked by the reviewer (review checklist R-FP); a real one "
                "is fixed, a false one needs no record beyond the anomaly. They do not fail the high level."]
    counts = {}
    for row in s["guidelines"].values():
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    out += ["", "Status of all guidelines: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())), ""]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("licence")
    p.add_argument("--private", required=True)
    p.add_argument("--advanced-security", default="false")
    p.add_argument("--open-source-prerelease", default="false")
    p.add_argument("--repo", default=".")
    p = sub.add_parser("prepare")
    p.add_argument("--records", required=True)
    p.add_argument("--repo-records")
    p.add_argument("--repo", default=".")
    p.add_argument("--paths", default="")
    p.add_argument("--coding-standards", required=True)
    p.add_argument("--markers", required=True)
    p.add_argument("--tidy-configs", help="the validated clang-tidy configurations (tidy-configs output)")
    p.add_argument("--today")
    p = sub.add_parser("flags")
    p.add_argument("--compdb", required=True)
    p.add_argument("--repo", default=".")
    p.add_argument("--canary")
    p.add_argument("--out", required=True)
    p = sub.add_parser("extraction")
    p.add_argument("--compdb", required=True)
    p.add_argument("--compiled", required=True)
    p.add_argument("--diagnostics", required=True)
    p.add_argument("--repo", default=".")
    p.add_argument("--paths", default="")
    p.add_argument("--canary")
    p.add_argument("--out", required=True)
    p = sub.add_parser("tidy-configs")
    p.add_argument("--cases", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("tidy")
    p.add_argument("--compdb", required=True)
    p.add_argument("--configs", required=True)
    p.add_argument("--clang-tidy", default="clang-tidy")
    p.add_argument("--repo", default=".")
    p.add_argument("--paths", default="")
    p.add_argument("--out", required=True)
    p = sub.add_parser("cppcheck")
    p.add_argument("--compdb", required=True)
    p.add_argument("--matrix", required=True)
    p.add_argument("--repo", default=".")
    p.add_argument("--paths", default="")
    p.add_argument("--out", required=True)
    p = sub.add_parser("report")
    p.add_argument("--matrix", required=True)
    p.add_argument("--supported")
    p.add_argument("--anomalies", help="the tool validation's anomaly log (tests/misra-validation/anomalies.yml)")
    p.add_argument("--markers", required=True)
    p.add_argument("--config", action="append", default=[], help="name=directory with that configuration's results")
    p.add_argument("--repo", default=".")
    p.add_argument("--paths", default="")
    p.add_argument("--level", choices=["high", "safety"], default="high")
    p.add_argument("--canary-expect", default="")
    p.add_argument("--enforce", default="true")
    p.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    p.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    try:
        return {"licence": cmd_licence, "prepare": cmd_prepare, "flags": cmd_flags, "extraction": cmd_extraction,
                "tidy-configs": cmd_tidy_configs, "tidy": cmd_tidy, "cppcheck": cmd_cppcheck,
                "report": cmd_report}[a.cmd](a)
    except (OSError, KeyError, ValueError, yaml.YAMLError) as e:
        emit("error", f"{a.cmd}: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
