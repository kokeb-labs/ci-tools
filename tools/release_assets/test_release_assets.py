#!/usr/bin/env python3
"""Unit tests for release_assets.py: run with `python tools/release_assets/test_release_assets.py`."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_assets  # noqa: E402


def run(*cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


class ReleaseAssets(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        env = {"GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
        os.environ.update(env)
        run("git", "init", "-q", "-b", "main", cwd=self.repo)
        run("git", "config", "user.email", "t@example.invalid", cwd=self.repo)
        run("git", "config", "user.name", "t", cwd=self.repo)
        (self.repo / "LICENSE").write_text("MIT License\n\nCopyright\n")
        (self.repo / "driver.yml").write_text("name: demo\nversion: 1.2.0\n")
        (self.repo / "src.cpp").write_text("int x;\n")
        run("git", "add", ".", cwd=self.repo)
        run("git", "commit", "-q", "-m", "init", cwd=self.repo)
        run("git", "tag", "v1.2.0", cwd=self.repo)
        self.fw = Path(self.tmp.name) / "artifacts" / "fw-a"
        self.fw.mkdir(parents=True)
        (self.fw / "demo.bin").write_bytes(b"\x01\x02")
        self.cwd = os.getcwd()
        os.chdir(self.repo)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def release(self, out):
        return release_assets.main(["--tag", "v1.2.0", "--out", str(out),
                                    "--files", str(self.fw.parent) + "/**/*"])

    def test_writes_archive_sbom_and_sums(self):
        out = Path(self.tmp.name) / "dist"
        self.assertEqual(self.release(out), 0)
        self.assertEqual(sorted(p.name for p in out.iterdir()),
                         ["SHA256SUMS", "demo-1.2.0.spdx.json", "demo-1.2.0.tar.gz"])
        sums = dict(reversed(line.split("  ")) for line in (out / "SHA256SUMS").read_text().splitlines())
        self.assertEqual(set(sums), {"demo-1.2.0.spdx.json", "demo-1.2.0.tar.gz", "demo.bin"})
        self.assertEqual(sums["demo.bin"], hashlib.sha256(b"\x01\x02").hexdigest())

    def test_sbom_names_the_package_licence_and_files(self):
        out = Path(self.tmp.name) / "dist"
        self.release(out)
        doc = json.loads((out / "demo-1.2.0.spdx.json").read_text())
        self.assertEqual(doc["spdxVersion"], "SPDX-2.3")
        main = doc["packages"][0]
        self.assertEqual((main["name"], main["versionInfo"], main["licenseDeclared"]), ("demo", "1.2.0", "MIT"))
        self.assertEqual(main["checksums"][0]["checksumValue"],
                         hashlib.sha256((out / "demo-1.2.0.tar.gz").read_bytes()).hexdigest())
        algos = {c["algorithm"] for c in doc["files"][0]["checksums"]}
        self.assertEqual(algos, {"SHA1", "SHA256"})

    def test_same_tag_gives_same_bytes(self):
        a, b = Path(self.tmp.name) / "a", Path(self.tmp.name) / "b"
        self.release(a)
        self.release(b)
        self.assertEqual((a / "SHA256SUMS").read_text(), (b / "SHA256SUMS").read_text())

    def test_duplicate_release_file_names_fail(self):
        other = self.fw.parent / "fw-b"
        other.mkdir()
        (other / "demo.bin").write_bytes(b"\x03")
        self.assertEqual(self.release(Path(self.tmp.name) / "dist"), 1)

    def test_firmware_zip_holds_the_flash_set_per_artifact(self):
        import zipfile
        fw = Path(self.tmp.name) / "fw"
        for kind in ("Debug", "Release"):
            b = fw / f"fw-demo-{kind}" / "builds" / "b"
            (b / "bootloader").mkdir(parents=True)
            (b / "bootloader" / "bootloader.bin").write_bytes(kind.encode())
            (b / "app.bin").write_bytes(b"app")
            (b / "app.elf").write_bytes(b"elf")
            (b / "main.o").write_bytes(b"not shipped")
            (b / "flasher_args.json").write_text(json.dumps({
                "flash_files": {"0x0": "bootloader/bootloader.bin", "0x10000": "app.bin"},
                "app": {"file": "app.bin"}}))
        out = Path(self.tmp.name) / "dist"
        self.assertEqual(release_assets.main(["--tag", "v1.2.0", "--out", str(out), "--firmware", str(fw)]), 0)
        for kind in ("Debug", "Release"):
            with zipfile.ZipFile(out / f"fw-demo-{kind}.zip") as z:
                self.assertEqual(sorted(z.namelist()), ["builds/b/app.bin", "builds/b/app.elf",
                                                        "builds/b/bootloader/bootloader.bin",
                                                        "builds/b/flasher_args.json"])
                self.assertEqual(z.read("builds/b/bootloader/bootloader.bin"), kind.encode())
        self.assertIn("fw-demo-Release.zip", (out / "SHA256SUMS").read_text())

    def test_firmware_missing_flash_file_fails(self):
        b = Path(self.tmp.name) / "fw" / "fw-x" / "b"
        b.mkdir(parents=True)
        (b / "flasher_args.json").write_text(json.dumps({"flash_files": {"0x0": "gone.bin"}}))
        with self.assertRaises(SystemExit):
            release_assets.main(["--tag", "v1.2.0", "--out", str(Path(self.tmp.name) / "d"),
                                 "--firmware", str(b.parent.parent)])

    def test_missing_tag_fails(self):
        self.assertEqual(release_assets.main(["--tag", "v9.9.9", "--out", str(Path(self.tmp.name) / "d")]), 1)

    def test_unknown_licence_is_noassertion(self):
        (self.repo / "LICENSE").write_text("Proprietary\n")
        self.assertEqual(release_assets.license_of(self.repo), "NOASSERTION")


if __name__ == "__main__":
    unittest.main(verbosity=2)
