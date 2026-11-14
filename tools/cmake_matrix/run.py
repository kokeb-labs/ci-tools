#!/usr/bin/env python3
"""Configure, build and test one ru-cmake-matrix entry. Standard library only; runs on the runner and in the ESP-IDF
container alike.

  run.py --entry-json JSON --out-dir DIR [--parallel N] [--install-consumer DIR] [--ctest-args ARGS]
         [--configure-args ARGS] [--no-tests error|ignore] [--no-ccache] [--dry-run]

Steps, each in its own log group: (cross toolchains) write the CMake toolchain file; configure (`cmake -S <source_dir>
-B <build> -G Ninja`, or `--preset <preset>` with the build directory forced to <build>); build (`--target` when the
entry names one) with --parallel N; test (`ctest --output-junit`, host entries with test: true); install and build the
consumer project against the installed package (host entries, when --install-consumer is given and has a
CMakeLists.txt; the consumer gets -DMATRIX_ENTRY=<name> and the entry's consumer_args) and run its tests.

Writes <out-dir>/result.json ({name, toolchain, status, failed_step, seconds, tests}) and <out-dir>/junit.xml when
tests ran. ccache is used as the compiler launcher when it is on PATH. Exit 1 when a step failed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

FLAGS = {
    "cortex-m0plus": "-mcpu=cortex-m0plus -mthumb -mfloat-abi=soft",
    "cortex-m3": "-mcpu=cortex-m3 -mthumb -mfloat-abi=soft",
    "cortex-m4f": "-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16",
    "cortex-m7f": "-mcpu=cortex-m7 -mthumb -mfloat-abi=hard -mfpu=fpv5-d16",
    "cortex-m33f": "-mcpu=cortex-m33 -mthumb -mfloat-abi=hard -mfpu=fpv5-sp-d16",
}
COMPILERS = {"host-gcc": ("gcc", "g++"), "host-clang": ("clang", "clang++")}


def arm_toolchain_file(core: str, path: str) -> str:
    flags = FLAGS[core]
    text = "\n".join([
        "set(CMAKE_SYSTEM_NAME Generic)",
        "set(CMAKE_SYSTEM_PROCESSOR arm)",
        "set(CMAKE_C_COMPILER arm-none-eabi-gcc)",
        "set(CMAKE_CXX_COMPILER arm-none-eabi-g++)",
        "set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)",
        "set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)",
        f'set(CMAKE_C_FLAGS_INIT "{flags} -ffunction-sections -fdata-sections")',
        f'set(CMAKE_CXX_FLAGS_INIT "{flags} -ffunction-sections -fdata-sections")',
        "",
    ])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def host_compilers(toolchain: str) -> tuple[str, str]:
    """The C and C++ compilers of a host toolchain: CMAKE_MATRIX_GCC / CMAKE_MATRIX_CLANG (the C++ driver named in
    toolchain.json, e.g. g++-14) when set, else the newest versioned compiler on PATH, else the unversioned one."""
    c, cxx = COMPILERS[toolchain]
    pinned = os.environ.get("CMAKE_MATRIX_GCC" if toolchain == "host-gcc" else "CMAKE_MATRIX_CLANG", "")
    if pinned:
        return pinned.replace(cxx, c, 1), pinned
    for v in range(30, 9, -1):
        if shutil.which(f"{cxx}-{v}") and shutil.which(f"{c}-{v}"):
            return f"{c}-{v}", f"{cxx}-{v}"
    return c, cxx


def configure_command(e: dict, build: str, toolchain_file: str | None, extra: str, ccache: bool = True) -> list[str]:
    cmd = ["cmake", "-S", e["source_dir"], "-B", build]
    if e["preset"]:
        cmd += ["--preset", e["preset"]]
    else:
        cmd += ["-G", "Ninja", f"-DCMAKE_BUILD_TYPE={e['build_type']}"]
    if toolchain_file:
        cmd.append(f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}")
    if e["toolchain"] == "esp-idf":
        # ESP-IDF's toolchain file links with -nostartfiles; the compiler check builds a library instead.
        cmd.append("-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY")
    if e["toolchain"] in COMPILERS:
        c, cxx = host_compilers(e["toolchain"])
        cmd += [f"-DCMAKE_C_COMPILER={c}", f"-DCMAKE_CXX_COMPILER={cxx}"]
    if ccache and shutil.which("ccache"):
        cmd += ["-DCMAKE_C_COMPILER_LAUNCHER=ccache", "-DCMAKE_CXX_COMPILER_LAUNCHER=ccache"]
    cmd += ["-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"]
    cmd += shlex.split(e["cmake_args"]) + shlex.split(extra)
    return cmd


def run(step: str, cmd: list[str], dry: bool, cwd: str | None = None) -> bool:
    print(f"::group::{step}")
    print("+ " + shlex.join(cmd), flush=True)
    ok = True
    if not dry:
        ok = subprocess.run(cmd, cwd=cwd).returncode == 0
    print("::endgroup::", flush=True)
    if not ok:
        print(f"::error::{step} failed (see the log group above)")
    return ok


def junit_counts(path: str) -> dict:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return {}
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    out = {"tests": 0, "failures": 0, "skipped": 0}
    for s in suites:
        for k in out:
            out[k] += int(s.get(k, "0") or 0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry-json", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--parallel", default="")
    ap.add_argument("--install-consumer", default="")
    ap.add_argument("--ctest-args", default="")
    ap.add_argument("--configure-args", default="")
    ap.add_argument("--no-tests", default="error", choices=["error", "ignore"])
    ap.add_argument("--no-ccache", action="store_true", help="do not use ccache even when it is on PATH")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    e = json.loads(a.entry_json)
    os.makedirs(a.out_dir, exist_ok=True)
    work = os.path.abspath(os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "cmake-matrix", e["name"]))
    build = os.path.join(work, "build")
    parallel = a.parallel if re.fullmatch(r"[1-9][0-9]*", a.parallel or "") else str(os.cpu_count() or 2)
    started = time.monotonic()
    result = {"name": e["name"], "toolchain": e["toolchain"], "status": "passed", "failed_step": "", "tests": {}}

    def finish(status: str, step: str = "") -> int:
        result["status"], result["failed_step"] = status, step
        result["seconds"] = round(time.monotonic() - started, 1)
        with open(os.path.join(a.out_dir, "result.json"), "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        return 0 if status == "passed" else 1

    toolchain_file = None
    if e["toolchain"] == "arm-none-eabi":
        os.makedirs(work, exist_ok=True)
        toolchain_file = arm_toolchain_file(e["core"], os.path.join(work, f"toolchain-{e['core']}.cmake"))
    elif e["toolchain"] == "esp-idf":
        idf = os.environ.get("IDF_PATH", "")
        toolchain_file = os.path.join(idf, "tools", "cmake", f"toolchain-{e['idf_target']}.cmake")
        if not a.dry_run and not os.path.isfile(toolchain_file):
            print(f"::error::{toolchain_file} not found: is IDF_PATH set (the ESP-IDF container) and "
                  f"{e['idf_target']} a target of this ESP-IDF version?")
            return finish("failed", "toolchain")
    if not run(f"{e['name']}: configure", configure_command(e, build, toolchain_file, a.configure_args,
                                                                     not a.no_ccache), a.dry_run):
        return finish("failed", "configure")
    cmd = ["cmake", "--build", build, "--parallel", parallel]
    if e["target"]:
        cmd += ["--target", e["target"]]
    if not run(f"{e['name']}: build {e['target'] or 'all'}", cmd, a.dry_run):
        return finish("failed", "build")
    if e["test"]:
        junit = os.path.join(os.path.abspath(a.out_dir), "junit.xml")
        cmd = ["ctest", "--test-dir", build, "--output-on-failure", f"--no-tests={a.no_tests}",
               "--parallel", parallel,
               "--output-junit", junit] + shlex.split(a.ctest_args)
        ok = run(f"{e['name']}: test", cmd, a.dry_run)
        result["tests"] = junit_counts(junit)
        if not ok:
            return finish("failed", "test")
    if a.install_consumer and not os.path.isfile(os.path.join(a.install_consumer, "CMakeLists.txt")):
        print(f"::warning::{a.install_consumer}/CMakeLists.txt does not exist; the install consumer is skipped")
        result["consumer"] = "skipped"
    elif a.install_consumer and e["toolchain"] in COMPILERS:
        prefix = os.path.join(work, "stage")
        if not run(f"{e['name']}: install", ["cmake", "--install", build, "--prefix", prefix], a.dry_run):
            return finish("failed", "install")
        cbuild = os.path.join(work, "consumer")
        c, cxx = host_compilers(e["toolchain"])
        cmd = ["cmake", "-S", a.install_consumer, "-B", cbuild, "-G", "Ninja", f"-DCMAKE_BUILD_TYPE={e['build_type']}",
               f"-DCMAKE_PREFIX_PATH={prefix}", f"-DCMAKE_C_COMPILER={c}", f"-DCMAKE_CXX_COMPILER={cxx}",
               f"-DMATRIX_ENTRY={e['name']}"] + shlex.split(e["consumer_args"])
        if not run(f"{e['name']}: configure the install consumer", cmd, a.dry_run):
            return finish("failed", "consumer-configure")
        if not run(f"{e['name']}: build the install consumer", ["cmake", "--build", cbuild, "--parallel", parallel],
                   a.dry_run):
            return finish("failed", "consumer-build")
        cmd = ["ctest", "--test-dir", cbuild, "--output-on-failure", "--no-tests=ignore"]
        if not run(f"{e['name']}: test the install consumer", cmd, a.dry_run):
            return finish("failed", "consumer-test")
    return finish("passed")


if __name__ == "__main__":
    sys.exit(main())
