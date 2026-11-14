#!/usr/bin/env python3
"""One configuration of an ru-misra scan, end to end (the workflow's scan job runs exactly this).

  scan.py --config host|cortex-m --out DIR --codeql BIN --misra-pack DIR --cs-script FILE --records FILE
          --matrix FILE [--repo-records FILE] [--source-dir .] [--cmake-args "..."] [--build-target T]
          [--paths "inc src"] [--build-command "..."] [--own-pack DIR ...] [--clang-tidy BIN] [--arm-bin DIR]

Stages, each failing the scan when it fails:
  1. deviation records and suppression markers (misra.py prepare), coding-standards.yml at the source root
  2. a clean CMake configure with compile_commands.json (host: g++; cortex-m: the Arm GNU toolchain)
  3. the CodeQL database, by tracing the build, with the deviation configuration indexed and the canary compiled
  4. the MISRA pack's default suite, the own profile packs and the deviation suppression query: results.sarif
  5. run-time assurance: extracted translation units and files against the build, extractor errors, the canary
  6. the build flags the compiler-decided guidelines rely on, clang-tidy's validated configurations and cppcheck
     on the same compile database
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_TOOLS = os.path.abspath(os.path.join(HERE, "..", ".."))
CANARY = os.path.join(HERE, "canary", "ru_misra_canary.cpp")


def run(cmd: list[str], **kw) -> int:
    print("+ " + shlex.join(cmd), flush=True)
    return subprocess.run(cmd, **kw).returncode


def group(title: str) -> None:
    print(f"::endgroup::\n::group::{title}", flush=True)


DEFAULT_BUILD_PARALLEL = 2


def build_parallel(value: str = "", environ: dict | None = None) -> int:
    """Job count of the traced build: --parallel, else CMAKE_BUILD_PARALLEL_LEVEL, else 2 (never unbounded)."""
    env = os.environ if environ is None else environ
    for raw in (value, env.get("CMAKE_BUILD_PARALLEL_LEVEL", "")):
        raw = (raw or "").strip()
        if raw:
            try:
                n = int(raw)
            except ValueError:
                raise SystemExit(f"::error::build parallelism must be a positive integer, got {raw!r}")
            if n < 1:
                raise SystemExit(f"::error::build parallelism must be a positive integer, got {raw!r}")
            return n
    return DEFAULT_BUILD_PARALLEL


def ram_option() -> list[str]:
    """CodeQL's heap: the machine's memory less 2 GiB for the OS and the evaluator's native memory."""
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") // (1024 * 1024)
    except (ValueError, OSError, AttributeError):
        return []
    return [f"--ram={max(2048, total - 2048)}"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", choices=["host", "cortex-m"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--codeql", required=True)
    ap.add_argument("--misra-pack", required=True)
    ap.add_argument("--cs-script", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--repo-records")
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--source-dir", default=".")
    ap.add_argument("--cmake-args", default="")
    ap.add_argument("--build-target", default="")
    ap.add_argument("--build-command", default="", help="instead of CMake: a command that builds every TU cleanly "
                    "and writes compile_commands.json to --out")
    ap.add_argument("--paths", default="")
    ap.add_argument("--own-pack", action="append", default=[])
    ap.add_argument("--clang-tidy", default="clang-tidy")
    ap.add_argument("--tidy-configs")
    ap.add_argument("--arm-bin", default="")
    ap.add_argument("--cxx", default="g++")
    ap.add_argument("--threads", default="0")
    ap.add_argument("--parallel", default="", help="jobs of the traced CMake build (default: "
                    "$CMAKE_BUILD_PARALLEL_LEVEL, else 2)")
    a = ap.parse_args()

    py = sys.executable
    misra = [py, os.path.join(HERE, "misra.py")]
    with open(os.path.join(HERE, "toolchain.json"), encoding="utf-8") as fh:
        tc = json.load(fh)
    root = os.getcwd()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    build = os.path.join(root, ".ru-misra", f"build-{a.config}")
    db = os.path.join(out, "db")
    shutil.rmtree(build, ignore_errors=True)
    shutil.rmtree(db, ignore_errors=True)
    paths = a.paths

    print(f"::group::{a.config}: deviation records and suppression markers", flush=True)
    # Record and marker errors are reported by the report job (which applies the level); not fatal here.
    status = 0
    run([*misra, "prepare", "--records", a.records, *(["--repo-records", a.repo_records]
                  if a.repo_records else []), "--paths", paths, "--coding-standards",
                  os.path.join(root, "coding-standards.yml"), "--markers", os.path.join(out, "markers.json"),
                  *(["--tidy-configs", a.tidy_configs] if a.tidy_configs else [])])
    shutil.copyfile(os.path.join(root, "coding-standards.yml"), os.path.join(out, "coding-standards.yml"))

    group(f"{a.config}: configure (compile_commands.json)")
    if a.config == "cortex-m":
        cxx = os.path.join(a.arm_bin, "arm-none-eabi-g++")
        flags = tc["cortex_m"]["flags"]
        toolchain = os.path.join(out, "toolchain-cortex-m.cmake")
        with open(toolchain, "w", encoding="utf-8") as fh:
            fh.write("set(CMAKE_SYSTEM_NAME Generic)\nset(CMAKE_SYSTEM_PROCESSOR arm)\n"
                     f"set(CMAKE_C_COMPILER {os.path.join(a.arm_bin, 'arm-none-eabi-gcc')})\n"
                     f"set(CMAKE_CXX_COMPILER {cxx})\nset(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)\n"
                     f'set(CMAKE_C_FLAGS_INIT "{flags}")\nset(CMAKE_CXX_FLAGS_INIT "{flags}")\n')
        cmake_extra = [f"-DCMAKE_TOOLCHAIN_FILE={toolchain}", "-DCMAKE_BUILD_TYPE=MinSizeRel"]
        canary_cmd = [cxx, *flags.split(), "-std=c++20", "-c", CANARY, "-o", os.path.join(out, "canary.o")]
    else:
        cxx = shutil.which(a.cxx) or a.cxx
        cmake_extra = [f"-DCMAKE_CXX_COMPILER={cxx}", "-DCMAKE_BUILD_TYPE=Debug"]
        canary_cmd = [cxx, "-std=c++20", "-c", CANARY, "-o", os.path.join(out, "canary.o")]
    compdb = os.path.join(out, "compile_commands.json")
    if a.build_command:
        build_cmd = a.build_command
    else:
        if run(["cmake", "-S", a.source_dir, "-B", build, "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON", *cmake_extra,
                *shlex.split(a.cmake_args)]):
            print("::error::CMake configure failed")
            return 1
        shutil.copyfile(os.path.join(build, "compile_commands.json"), compdb)
        build_cmd = shlex.join(["cmake", "--build", build, "--parallel", str(build_parallel(a.parallel)),
                                *(["--target", a.build_target] if a.build_target else [])])

    group(f"{a.config}: CodeQL database (traced build, deviation configuration, canary)")
    # codeql splits each --command on blanks and ignores quotes: hand it scripts instead.
    scripts = []
    for name, cmd in (("deviations", shlex.join([py, a.cs_script])), ("build", build_cmd),
                      ("canary", shlex.join(canary_cmd))):
        p = os.path.join(out, f"step-{name}.sh")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(f"#!/bin/sh\nset -e\ncd {shlex.quote(root)}\n{cmd}\n")
        os.chmod(p, 0o700)  # owner only: run by the CodeQL tracer as this user
        scripts.append(f"--command={p}")
    if run([a.codeql, "database", "create", db, "--language=cpp", f"--source-root={root}", *scripts]):
        print("::error::the CodeQL database could not be built: the build failed under the tracer")
        return 1
    if a.build_command and not os.path.isfile(compdb):
        print("::error::--build-command did not write compile_commands.json to the output folder")
        return 1

    group(f"{a.config}: analysis")
    lib = os.path.join(a.misra_pack, ".codeql", "libraries")
    common = next(os.path.join(dp, "DeviationsSuppression.ql") for dp, _d, fs in os.walk(lib)
                  if "DeviationsSuppression.ql" in fs)
    suites = [os.path.join(a.misra_pack, "codeql-suites", "misra-cpp-default.qls")]
    suites += [os.path.join(p, "codeql-suites", os.path.basename(os.path.normpath(p)) + "-default.qls")
               for p in a.own_pack]
    search = os.pathsep.join([a.misra_pack, lib, *[os.path.dirname(os.path.normpath(p)) for p in a.own_pack]])
    if run([a.codeql, "database", "analyze", db, *suites, common, "--format=sarifv2.1.0",
            f"--output={os.path.join(out, 'results.sarif')}", f"--threads={a.threads}", *ram_option(),
            f"--additional-packs={search}", "--sarif-add-snippets"]):
        print("::error::CodeQL analysis failed")
        return 1
    queries = [("suppressions", common)]
    for p in a.own_pack:
        for name, q in (("compiled", "CompiledFiles.ql"), ("diagnostics", "ExtractionDiagnostics.ql")):
            if os.path.isfile(os.path.join(p, "diagnostics", q)):
                queries.append((name, os.path.join(p, "diagnostics", q)))
    for name, q in queries:
        bqrs = os.path.join(out, f"{name}.bqrs")
        if run([a.codeql, "query", "run", f"--database={db}", f"--output={bqrs}", f"--additional-packs={search}",
                f"--threads={a.threads}", q]) or run(
                [a.codeql, "bqrs", "decode", "--format=json", "--entities=url,string", f"--output="
                 f"{os.path.join(out, name + '.json')}", bqrs]):
            print(f"::error::the {name} query failed")
            return 1

    group(f"{a.config}: run-time assurance (extraction coverage, canary)")
    run([*misra, "extraction", "--compdb", compdb, "--compiled", os.path.join(out, "compiled.json"),
                   "--diagnostics", os.path.join(out, "diagnostics.json"), "--paths", paths, "--canary", CANARY,
                   "--out", os.path.join(out, "extraction.json")])

    group(f"{a.config}: build flags, clang-tidy and cppcheck on the same compile database")
    run([*misra, "flags", "--compdb", compdb, "--out", os.path.join(out, "flags.json")])
    if a.tidy_configs:
        run([*misra, "tidy", "--compdb", compdb, "--configs", a.tidy_configs, "--clang-tidy", a.clang_tidy,
             "--paths", paths, "--out", os.path.join(out, "tidy.json")])
    if shutil.which("cppcheck"):
        run([*misra, "cppcheck", "--compdb", compdb, "--matrix", a.matrix, "--paths", paths,
             "--out", os.path.join(out, "cppcheck.json")])
    print("::endgroup::", flush=True)
    shutil.rmtree(db, ignore_errors=True)  # large; the results are kept
    os.remove(os.path.join(root, "coding-standards.yml"))
    return status


if __name__ == "__main__":
    sys.exit(main())
