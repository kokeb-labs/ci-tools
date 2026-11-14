#!/usr/bin/env python3
"""The configurations of one ru-cmake-matrix call, checked and split by where they run. Standard library only.

  plan.py --out FILE [--github-output FILE]

Reads its inputs from the environment (the workflow passes them through env:, never through the command line):

  MATRIX          JSON list of entries (keys below); may be empty
  MATRIX_FROM     a catalogue file (compat.yml, schema 1): every distinct {mcu, rtos} of its drivers' configs (and of a
                  top-level `configurations` list) becomes an entry; YAML is read with PyYAML when it is installed,
                  else the file must be JSON
  MCUS, RTOSES, PRESETS
                  space-separated; their cross product becomes entries (an empty list is one empty value)
  MCU_TOOLCHAINS  JSON object: MCU name (fnmatch pattern, case-insensitive) -> toolchain, or toolchain:core /
                  toolchain:idf_target, for entries that name an MCU but no toolchain
  MCU_VARIABLE, RTOS_VARIABLE
                  the CMake cache variables an entry's mcu and rtos are passed as (-D<var>=<value>)
  DEFAULT_TOOLCHAIN, BUILD_TYPE, SOURCE_DIR, BUILD_TARGET, RUN_TESTS
                  defaults of an entry that does not set them

Entry keys: name (required, unique; [A-Za-z0-9._-]), toolchain (host-gcc, host-clang, arm-none-eabi, esp-idf), core
(arm-none-eabi: cortex-m0plus, cortex-m3, cortex-m4f, cortex-m7f, cortex-m33f), idf_target (esp-idf: esp32, esp32s3,
esp32c3, esp32c6, esp32h2, esp32p4, ...), mcu, rtos, preset, cmake_args, source_dir, target, build_type, test
(default true on the host, false for a cross toolchain), consumer_args.

Writes the plan: {"call_id", "count", "runner": [...], "container": [...]} where every entry is complete (all keys
set, cmake_args with the -D of mcu and rtos), and the same as step outputs. Exit 1 with ::error:: lines on a bad entry.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import itertools
import json
import os
import re
import sys

TOOLCHAINS = {"host-gcc", "host-clang", "arm-none-eabi", "esp-idf"}
CORES = {"cortex-m0plus", "cortex-m3", "cortex-m4f", "cortex-m7f", "cortex-m33f"}
KEYS = {"name", "toolchain", "core", "idf_target", "mcu", "rtos", "preset", "cmake_args", "source_dir", "target",
        "build_type", "test", "consumer_args"}
NAME = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
VALUE = re.compile(r"^[A-Za-z0-9._+-]*$")


def load_structured(path: str):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    try:
        import yaml  # noqa: PLC0415 (optional)
        return yaml.safe_load(text)
    except ImportError:
        return json.loads(text)


def from_catalogue(path: str) -> list[dict]:
    """The distinct {mcu, rtos} pairs of a compatibility catalogue, in a stable order."""
    doc = load_structured(path) or {}
    pairs = []
    sources = [c for d in (doc.get("drivers") or []) for c in ((d or {}).get("configs") or [])]
    sources += list(doc.get("configurations") or [])
    for cfg in sources:
        cfg = cfg or {}
        mcu, rtos = str(cfg.get("mcu") or ""), str(cfg.get("rtos") or "")
        if mcu and (mcu, rtos) not in pairs:
            pairs.append((mcu, rtos))
    return [{"name": "-".join(p for p in (mcu, rtos) if p), "mcu": mcu, "rtos": rtos} for mcu, rtos in sorted(pairs)]


def cross_product(mcus: str, rtoses: str, presets: str) -> list[dict]:
    m, r, p = mcus.split(), rtoses.split(), presets.split()
    if not (m or r or p):
        return []
    out = []
    for mcu, rtos, preset in itertools.product(m or [""], r or [""], p or [""]):
        name = "-".join(x for x in (mcu, rtos, preset) if x)
        out.append({"name": name, "mcu": mcu, "rtos": rtos, "preset": preset})
    return out


def toolchain_for(mcu: str, table: dict) -> str | None:
    for pattern, tc in table.items():
        if fnmatch.fnmatch(mcu.lower(), str(pattern).lower()):
            return str(tc)
    return None


def complete(entry: dict, env: dict, table: dict, errors: list[str]) -> dict | None:
    name = str(entry.get("name", ""))
    where = f"entry {name or '(unnamed)'}"
    unknown = sorted(set(entry) - KEYS)
    if unknown:
        errors.append(f"{where}: unknown key(s) {', '.join(unknown)}; known: {', '.join(sorted(KEYS))}")
    if not NAME.match(name):
        errors.append(f"{where}: name must be 1-64 characters of A-Z a-z 0-9 . _ -")
        return None
    mcu, rtos = str(entry.get("mcu") or ""), str(entry.get("rtos") or "")
    tc = str(entry.get("toolchain") or "")
    if not tc and mcu:
        tc = toolchain_for(mcu, table) or ""
    tc = tc or env["DEFAULT_TOOLCHAIN"]
    core = str(entry.get("core") or "")
    idf_target = str(entry.get("idf_target") or "")
    if ":" in tc:
        tc, extra = tc.split(":", 1)
        if tc == "arm-none-eabi":
            core = core or extra
        elif tc == "esp-idf":
            idf_target = idf_target or extra
    if tc not in TOOLCHAINS:
        errors.append(f"{where}: toolchain '{tc}' is not one of {', '.join(sorted(TOOLCHAINS))}")
        return None
    if tc == "arm-none-eabi":
        core = core or "cortex-m4f"
        if core not in CORES:
            errors.append(f"{where}: core '{core}' is not one of {', '.join(sorted(CORES))}")
    elif core:
        errors.append(f"{where}: core is only for the arm-none-eabi toolchain")
    if tc == "esp-idf":
        idf_target = idf_target or "esp32"
        if not re.match(r"^esp32[a-z0-9]*$", idf_target):
            errors.append(f"{where}: idf_target '{idf_target}' is not an ESP-IDF target (esp32, esp32s3, ...)")
    elif idf_target:
        errors.append(f"{where}: idf_target is only for the esp-idf toolchain")
    for key, value in (("mcu", mcu), ("rtos", rtos), ("preset", str(entry.get("preset") or ""))):
        if not VALUE.match(value):
            errors.append(f"{where}: {key} '{value}' may hold only A-Z a-z 0-9 . _ + -")
    args = []
    if mcu and env["MCU_VARIABLE"]:
        args.append(f"-D{env['MCU_VARIABLE']}={mcu}")
    if rtos and env["RTOS_VARIABLE"]:
        args.append(f"-D{env['RTOS_VARIABLE']}={rtos}")
    extra_args = str(entry.get("cmake_args") or "")
    host = tc.startswith("host-")
    test = entry.get("test", env["RUN_TESTS"] == "true" and host)
    if isinstance(test, str):
        test = test.lower() == "true"
    if test and not host:
        errors.append(f"{where}: test: true needs a host toolchain (a {tc} build does not run on the runner)")
    return {
        "name": name,
        "toolchain": tc,
        "core": core,
        "idf_target": idf_target,
        "mcu": mcu,
        "rtos": rtos,
        "preset": str(entry.get("preset") or ""),
        "cmake_args": " ".join(args + ([extra_args] if extra_args else [])),
        "source_dir": str(entry.get("source_dir") or env["SOURCE_DIR"]),
        "target": str(entry.get("target") or env["BUILD_TARGET"]),
        "build_type": str(entry.get("build_type") or env["BUILD_TYPE"]),
        "test": bool(test),
        "consumer_args": str(entry.get("consumer_args") or ""),
    }


def plan(env: dict) -> tuple[dict, list[str]]:
    errors: list[str] = []
    entries: list[dict] = []
    raw = env.get("MATRIX", "").strip()
    if raw:
        try:
            given = json.loads(raw)
        except json.JSONDecodeError as e:
            return {}, [f"matrix is not JSON: {e}"]
        if not isinstance(given, list) or not all(isinstance(x, dict) for x in given):
            return {}, ["matrix must be a JSON list of objects"]
        entries += given
    if env.get("MATRIX_FROM"):
        path = env["MATRIX_FROM"]
        if not os.path.isfile(path):
            return {}, [f"matrix_from: {path} does not exist"]
        entries += from_catalogue(path)
    entries += cross_product(env.get("MCUS", ""), env.get("RTOSES", ""), env.get("PRESETS", ""))
    try:
        table = json.loads(env.get("MCU_TOOLCHAINS") or "{}")
        if not isinstance(table, dict):
            raise ValueError
    except ValueError:
        return {}, ["mcu_toolchains must be a JSON object (MCU pattern -> toolchain)"]
    done = [e for e in (complete(x, env, table, errors) for x in entries) if e]
    names = [e["name"] for e in done]
    for dup in sorted({n for n in names if names.count(n) > 1}):
        errors.append(f"entry {dup}: the name is used more than once")
    call_id = hashlib.sha256(json.dumps(done, sort_keys=True).encode()).hexdigest()[:8]
    out = {
        "call_id": call_id,
        "count": len(done),
        "runner": [e for e in done if e["toolchain"] != "esp-idf"],
        "container": [e for e in done if e["toolchain"] == "esp-idf"],
    }
    return out, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--github-output")
    a = ap.parse_args()
    env = {k: os.environ.get(k, "") for k in ("MATRIX", "MATRIX_FROM", "MCUS", "RTOSES", "PRESETS", "MCU_TOOLCHAINS",
                                              "MCU_VARIABLE", "RTOS_VARIABLE", "DEFAULT_TOOLCHAIN", "BUILD_TYPE",
                                              "SOURCE_DIR", "BUILD_TARGET", "RUN_TESTS")}
    env["DEFAULT_TOOLCHAIN"] = env["DEFAULT_TOOLCHAIN"] or "host-gcc"
    env["BUILD_TYPE"] = env["BUILD_TYPE"] or "Debug"
    env["SOURCE_DIR"] = env["SOURCE_DIR"] or "."
    env["RUN_TESTS"] = env["RUN_TESTS"] or "true"
    result, errors = plan(env)
    for e in errors:
        print(f"::error::{e}")
    if errors:
        return 1
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    for e in result["runner"] + result["container"]:
        print(f"{e['name']:32} {e['toolchain']:14} {e['core'] or e['idf_target']:14} {e['cmake_args']}")
    print(f"{result['count']} configuration(s): {len(result['runner'])} on the runner, "
          f"{len(result['container'])} in the ESP-IDF container")
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"call_id={result['call_id']}\n")
            fh.write(f"count={result['count']}\n")
            fh.write(f"runner={json.dumps(result['runner'])}\n")
            fh.write(f"runner_count={len(result['runner'])}\n")
            fh.write(f"container={json.dumps(result['container'])}\n")
            fh.write(f"container_count={len(result['container'])}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
