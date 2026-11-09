#!/usr/bin/env python3
"""Install the validated MISRA toolchain from toolchain.json, and only from it. Standard library only.

  install.py codeql --cache DIR --dest DIR [--github-env FILE]
      The CodeQL bundle, the misra-cpp-coding-standards pack and the deviation script. Archives are kept in --cache
      (an Actions cache) and checked against their SHA-256 on every run, cached or not, before anything is
      extracted; exports CODEQL, MISRA_PACK and CS_SCRIPT.
  install.py python --venv DIR [--with-clang-tidy]
      PyYAML (and clang-tidy) into a venv, hash-checked by pip --require-hashes.
  install.py arm --cache DIR --dest DIR [--github-env FILE]
      The Arm GNU toolchain; exports ARM_BIN.
  install.py apt
      The runner's compilers and cppcheck from the signed Ubuntu archive (retried).
  install.py versions --out FILE [--codeql BIN] [--arm-bin DIR] [--clang-tidy BIN]
      The exact version of every tool, for the validation record and the report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def toolchain() -> dict:
    with open(os.path.join(HERE, "toolchain.json"), encoding="utf-8") as fh:
        return json.load(fh)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fetch(url: str, digest: str, cache: str) -> str:
    """The file at url, from the cache when it is there and intact; its hash is checked either way."""
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, url.rsplit("/", 1)[1])
    if os.path.isfile(path) and sha256(path) == digest:
        print(f"cached and verified: {os.path.basename(path)}")
        return path
    for attempt in range(1, 6):
        try:
            tmp = path + ".part"
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as fh:
                shutil.copyfileobj(r, fh, 1 << 20)
            os.replace(tmp, path)
            break
        except OSError as e:
            if attempt == 5:
                raise
            print(f"download failed ({e}); retry {attempt}")
            time.sleep(10 * attempt)
    got = sha256(path)
    if got != digest:
        os.remove(path)
        sys.exit(f"::error::{url}: SHA-256 {got} is not the pinned {digest}")
    print(f"downloaded and verified: {os.path.basename(path)} {digest}")
    return path


def export(env_file: str | None, **values: str) -> None:
    for k, v in values.items():
        print(f"{k}={v}")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as fh:
            fh.writelines(f"{k}={v}\n" for k, v in values.items())


def cmd_codeql(a) -> int:
    t = toolchain()
    os.makedirs(a.dest, exist_ok=True)
    b = t["codeql_bundle"]
    bundle = fetch(b["url"], b["sha256"], a.cache)
    if not os.path.isfile(os.path.join(a.dest, "codeql", "codeql")):
        subprocess.run(["tar", "--zstd", "-xf", bundle, "-C", a.dest], check=True)
    p = t["misra_pack"]
    packs = fetch(p["url"], p["sha256"], a.cache)
    pack_dir = os.path.join(a.dest, "misra-pack")
    if not os.path.isdir(pack_dir):
        member = os.path.join(a.dest, p["member"])
        with zipfile.ZipFile(packs) as z, z.open(p["member"]) as src, open(member, "wb") as dst:
            shutil.copyfileobj(src, dst)
        if sha256(member) != p["member_sha256"]:
            sys.exit(f"::error::{p['member']} in the pack archive does not match its pinned SHA-256")
        os.makedirs(pack_dir)
        with tarfile.open(member) as tf:
            tf.extractall(pack_dir, filter="data")
        os.remove(member)
    s = t["coding_standards_script"]
    script = fetch(s["url"], s["sha256"], a.cache)
    codeql = os.path.join(a.dest, "codeql", "codeql")
    out = subprocess.run([codeql, "version", "--format=terse"], capture_output=True, text=True, check=True).stdout
    if out.strip() != b["version"]:
        sys.exit(f"::error::the bundle reports CodeQL {out.strip()}, not the pinned {b['version']}")
    export(a.github_env, CODEQL=codeql, MISRA_PACK=pack_dir, CS_SCRIPT=script)
    return 0


def cmd_python(a) -> int:
    t = toolchain()
    reqs = [t["pyyaml"]["requirement"]] + ([t["clang_tidy"]["requirement"]] if a.with_clang_tidy else [])
    req = os.path.join(os.path.dirname(os.path.abspath(a.venv)), "ru-misra-requirements.txt")
    with open(req, "w", encoding="utf-8") as fh:
        fh.write("\n".join(reqs) + "\n")
    subprocess.run([sys.executable, "-m", "venv", a.venv], check=True)
    subprocess.run([os.path.join(a.venv, "bin", "pip"), "install", "--quiet", "--disable-pip-version-check",
                    "--require-hashes", "--no-deps", "-r", req], check=True)
    return 0


def cmd_arm(a) -> int:
    t = toolchain()["arm_gnu_toolchain"]
    archive = fetch(t["url"], t["sha256"], a.cache)
    dest = os.path.join(a.dest, "arm")
    if not os.path.isfile(os.path.join(dest, "bin", "arm-none-eabi-g++")):
        os.makedirs(dest, exist_ok=True)
        subprocess.run(["tar", "-xJf", archive, "-C", dest, "--strip-components=1"], check=True)
    export(a.github_env, ARM_BIN=os.path.join(dest, "bin"))
    return 0


def cmd_apt(_a) -> int:
    pkgs = toolchain()["host"]["apt"]
    opts = ["-o", "Acquire::Retries=3", "-o", "Acquire::http::Timeout=30"]
    for attempt in range(1, 4):
        if subprocess.run(["sudo", "apt-get", *opts, "update", "-q"]).returncode == 0 and subprocess.run(
                ["sudo", "apt-get", *opts, "install", "-y", "-q", "--no-install-recommends", *pkgs]).returncode == 0:
            return 0
        time.sleep(15 * attempt)
    print("::error::apt-get install failed after 3 attempts")
    return 1


def first_line(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip().splitlines()[0]
    except (OSError, IndexError, subprocess.TimeoutExpired):
        return "not installed"


def cmd_versions(a) -> int:
    t = toolchain()
    h = t["host"]
    v = {
        "codeql": first_line([a.codeql, "version", "--format=terse"]) if a.codeql else "not installed",
        "misra_pack": f"{t['misra_pack']['name']}@{t['misra_pack']['version']}",
        "gcc": first_line([h["gcc"], "-dumpfullversion"]),
        "clang": first_line([h["clang"], "--version"]),
        "codeql_build": first_line([h["codeql_build"], "-dumpfullversion"]),
        "clang_tidy": first_line([a.clang_tidy, "--version"]) if a.clang_tidy else "not installed",
        "cppcheck": first_line(["cppcheck", "--version"]),
        "arm_gcc": first_line([os.path.join(a.arm_bin, "arm-none-eabi-g++"), "-dumpfullversion"])
        if a.arm_bin else "not installed",
    }
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(v, fh, indent=1)
    for k, x in v.items():
        print(f"{k}: {x}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("codeql")
    p.add_argument("--cache", required=True)
    p.add_argument("--dest", required=True)
    p.add_argument("--github-env", default=os.environ.get("GITHUB_ENV"))
    p = sub.add_parser("python")
    p.add_argument("--venv", required=True)
    p.add_argument("--with-clang-tidy", action="store_true")
    p = sub.add_parser("arm")
    p.add_argument("--cache", required=True)
    p.add_argument("--dest", required=True)
    p.add_argument("--github-env", default=os.environ.get("GITHUB_ENV"))
    sub.add_parser("apt")
    p = sub.add_parser("versions")
    p.add_argument("--out", required=True)
    p.add_argument("--codeql")
    p.add_argument("--arm-bin")
    p.add_argument("--clang-tidy")
    a = ap.parse_args()
    return {"codeql": cmd_codeql, "python": cmd_python, "arm": cmd_arm, "apt": cmd_apt,
            "versions": cmd_versions}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
