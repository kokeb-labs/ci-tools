#!/usr/bin/env python3
"""Build the supply-chain files of a release: a source archive, an SPDX 2.3 SBOM and SHA256SUMS.

Run from the root of the repository being released, at the tagged commit:

    release_assets.py --tag v1.2.0 --out dist [--firmware artifacts] [--files 'other/**/*']

Writes into --out:

- <name>-<version>.tar.gz: the tagged tree (git archive), with a fixed mtime so the same tag gives the same bytes.
  GitHub's own "Source code" archives are not promised to be byte-stable, so checksums cannot name them.
- <name>-<version>.spdx.json: the repository as the main package, each git submodule as a package it contains
  (name, URL, pinned commit), and each release file as a file it generates, with its SHA-256.
- <artifact>.zip for each folder in --firmware (one downloaded CI artifact): the files needed to flash and debug
  each ESP-IDF build in it (flasher_args.json, every file it lists, the app .elf and .map), at their build-relative
  paths, so `esptool.py write_flash @flash_args` works after unzipping. A folder with no flasher_args.json is
  zipped whole. One zip per artifact keeps Debug and Release apart, where uploading the files one by one would let
  equal names overwrite each other and pass GitHub's limit of 1000 files per release.
- SHA256SUMS: one line per file in --out and in --files, in `sha256sum -c` format.

Standard library only. The licence is read from the first line of LICENSE (MIT, Apache-2.0, BSD-3-Clause; anything
else is NOASSERTION, never a guess).
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import gzip
import hashlib
import json
import re
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path

LICENSES = (
    (re.compile(r"^\s*MIT License", re.I), "MIT"),
    (re.compile(r"^\s*Apache License", re.I), "Apache-2.0"),
    (re.compile(r"^\s*BSD 3-Clause", re.I), "BSD-3-Clause"),
)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def digest(path: Path, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def spdx_id(text: str) -> str:
    return "SPDXRef-" + re.sub(r"[^A-Za-z0-9.-]", "-", text)


def license_of(root: Path) -> str:
    lic = root / "LICENSE"
    if not lic.is_file():
        return "NOASSERTION"
    first = lic.read_text(errors="replace").lstrip().splitlines()[0] if lic.stat().st_size else ""
    for pattern, spdx in LICENSES:
        if pattern.search(first):
            return spdx
    return "NOASSERTION"


def name_of(root: Path) -> str:
    """driver.yml `name:` when present, else the directory name."""
    meta = root / "driver.yml"
    if meta.is_file():
        m = re.search(r"^name:\s*([A-Za-z0-9_.-]+)", meta.read_text(), re.M)
        if m:
            return m.group(1)
    return root.name


def repo_url() -> str:
    url = git("config", "--get", "remote.origin.url") if git("remote") else ""
    return re.sub(r"^git@github\.com:", "https://github.com/", url).removesuffix(".git") or "NOASSERTION"


def submodules(commit: str) -> list[dict]:
    """Every submodule pinned at `commit`: path, url and the commit it records."""
    if not Path(".gitmodules").is_file():
        return []
    out = []
    config = git("config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$").splitlines()
    for line in config:
        key, path = line.split(" ", 1)
        section = key.removesuffix(".path")
        url = git("config", "--file", ".gitmodules", "--get", f"{section}.url")
        tree = git("ls-tree", commit, "--", path).split()
        if len(tree) >= 3 and tree[1] == "commit":
            out.append({"path": path, "url": url.removesuffix(".git"), "commit": tree[2]})
    return out


def build_archive(name: str, version: str, tag: str, out: Path) -> Path:
    archive = out / f"{name}-{version}.tar.gz"
    prefix = f"{name}-{version}/"
    tar = subprocess.run(["git", "archive", "--format=tar", f"--prefix={prefix}", tag], check=True,
                         capture_output=True).stdout
    # gzip with no name and mtime 0, so the bytes depend on the tree only.
    with archive.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(tar)
    return archive


ZIP_TIME = (1980, 1, 1, 0, 0, 0)  # zip's earliest date: fixed, so equal inputs give equal bytes


def add_to_zip(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, path.read_bytes())


def flash_set(build: Path) -> list[Path]:
    """flasher_args.json, every file it flashes, flash_args, and the app's .elf and .map, under `build`."""
    args = json.loads((build / "flasher_args.json").read_text())
    files = {build / "flasher_args.json"}
    files |= {build / f for f in args.get("flash_files", {}).values()}
    if (build / "flash_args").is_file():
        files.add(build / "flash_args")
    app = args.get("app", {}).get("file")
    if app:
        stem = (build / app).with_suffix("")
        files |= {p for p in (stem.with_suffix(".elf"), stem.with_suffix(".map")) if p.is_file()}
    missing = sorted(str(f) for f in files if not f.is_file())
    if missing:
        raise SystemExit(f"::error::{build}/flasher_args.json lists files the artifact lacks: {', '.join(missing)}")
    return sorted(files)


def package_firmware(firmware: Path, out: Path) -> list[Path]:
    """One zip per artifact folder in `firmware`; see the module docstring."""
    zips = []
    for art in sorted(p for p in firmware.iterdir() if p.is_dir()):
        builds = sorted(f.parent for f in art.rglob("flasher_args.json"))
        if builds:
            members = [(f, f.relative_to(art)) for b in builds for f in flash_set(b)]
        else:
            print(f"::warning::{art.name} has no flasher_args.json; zipping the whole folder", file=sys.stderr)
            members = [(f, f.relative_to(art)) for f in sorted(art.rglob("*")) if f.is_file()]
        if not members:
            continue
        target = out / f"{art.name}.zip"
        with zipfile.ZipFile(target, "w") as zf:
            for f, rel in members:
                add_to_zip(zf, f, rel.as_posix())
        zips.append(target)
    return zips


def build_sbom(root: Path, name: str, version: str, tag: str, commit: str, archive: Path,
               files: list[Path]) -> dict:
    url = repo_url()
    main_id = spdx_id(f"Package-{name}")
    created = dt.datetime.fromtimestamp(int(git("log", "-1", "--format=%ct", commit)), dt.timezone.utc)
    packages = [{
        "SPDXID": main_id,
        "name": name,
        "versionInfo": version,
        "downloadLocation": f"git+{url}@{tag}" if url != "NOASSERTION" else "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": license_of(root),
        "licenseDeclared": license_of(root),
        "copyrightText": "NOASSERTION",
        "checksums": [{"algorithm": "SHA256", "checksumValue": digest(archive)}],
        "packageFileName": archive.name,
        "externalRefs": [{"referenceCategory": "OTHER", "referenceType": "gitoid",
                          "referenceLocator": f"gitoid:commit:sha1:{commit}"}],
    }]
    relationships = [{"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES",
                      "relatedSpdxElement": main_id}]
    for sub in submodules(commit):
        sid = spdx_id(f"Package-{sub['path']}")
        packages.append({
            "SPDXID": sid,
            "name": sub["url"].rsplit("/", 1)[-1],
            "versionInfo": sub["commit"],
            "downloadLocation": f"git+{sub['url']}@{sub['commit']}",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
            "comment": f"git submodule at {sub['path']}",
        })
        relationships.append({"spdxElementId": main_id, "relationshipType": "CONTAINS", "relatedSpdxElement": sid})
    spdx_files = []
    for f in files:
        fid = spdx_id(f"File-{f.name}")
        spdx_files.append({"SPDXID": fid, "fileName": f"./{f.name}",
                           # SPDX 2.3 requires SHA1 on every file; SHA256 is the one to check against.
                           "checksums": [{"algorithm": "SHA1", "checksumValue": digest(f, "sha1")},
                                         {"algorithm": "SHA256", "checksumValue": digest(f)}],
                           "licenseConcluded": "NOASSERTION", "copyrightText": "NOASSERTION"})
        relationships.append({"spdxElementId": fid, "relationshipType": "GENERATED_FROM",
                              "relatedSpdxElement": main_id})
    doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{name}-{version}",
        # Stable for a given repository and tag, so re-running the release gives the same document.
        "documentNamespace": f"https://spdx.org/spdxdocs/{name}-{version}-"
                             f"{uuid.uuid5(uuid.NAMESPACE_URL, f'{url}@{commit}')}",
        "creationInfo": {"created": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "creators": ["Tool: kokeb-labs-ci-tools-release_assets"]},
        "packages": packages,
        "relationships": relationships,
    }
    if spdx_files:
        doc["files"] = spdx_files
    return doc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tag", required=True, help="the release tag, e.g. v1.2.0")
    ap.add_argument("--out", required=True, type=Path, help="directory to write the files into")
    ap.add_argument("--firmware", type=Path,
                    help="folder of downloaded CI artifacts, one subfolder each; each becomes one zip")
    ap.add_argument("--files", action="append", default=[],
                    help="glob of other release files, attached as they are; repeatable; recursive ** allowed")
    args = ap.parse_args(argv)

    root = Path.cwd()
    try:
        commit = git("rev-parse", "--verify", "--quiet", f"refs/tags/{args.tag}^{{commit}}")
    except subprocess.CalledProcessError:
        print(f"::error::tag {args.tag} does not exist here; push the tag before releasing", file=sys.stderr)
        return 1
    name = name_of(root)
    version = args.tag.removeprefix("v")
    args.out.mkdir(parents=True, exist_ok=True)

    extra = sorted({Path(p) for g in args.files for p in glob.glob(g, recursive=True) if Path(p).is_file()})
    if args.firmware and args.firmware.is_dir():
        extra += package_firmware(args.firmware, args.out)
    names = [p.name for p in extra]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        print(f"::error::release files share a name, so a checksum line would be ambiguous: {', '.join(dupes)}",
              file=sys.stderr)
        return 1

    archive = build_archive(name, version, args.tag, args.out)
    sbom = args.out / f"{name}-{version}.spdx.json"
    sbom.write_text(json.dumps(build_sbom(root, name, version, args.tag, commit, archive, extra), indent=2) + "\n")

    sums = sorted({p.name: p for p in [*extra, *args.out.glob("*")]}.values(), key=lambda p: p.name)
    lines = [f"{digest(p)}  {p.name}" for p in sums if p.name != "SHA256SUMS"]
    (args.out / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
