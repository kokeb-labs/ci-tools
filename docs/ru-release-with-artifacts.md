# ru-release-with-artifacts

Create a GitHub Release for a tag and attach the firmware that `ru-build` built and tested for the same commit.

**File:** [`.github/workflows/ru-release-with-artifacts.yml`](../.github/workflows/ru-release-with-artifacts.yml)

## Caller

```yaml
---
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  release:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-release-with-artifacts.yml@v1
    permissions:
      contents: write
    with:
      build_workflow: esp32-examples-build-ci.yml
      fail_on_no_artifacts: true
```

## Release only after CI passed on the tag

Triggered by the tag push itself, the release runs at the same time as CI on that tag and can publish before (or
without) a green build. Trigger it from the finished CI run instead, and pass the tag and the commit:

```yaml
on:
  workflow_run:
    workflows: [CI]
    types: [completed]

permissions:
  contents: write

jobs:
  release:
    if: >-
      github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.event == 'push' &&
      startsWith(github.event.workflow_run.head_branch, 'v')
    uses: kokeb-labs/ci-tools/.github/workflows/ru-release-with-artifacts.yml@v1
    with:
      build_workflow: ci.yml
      tag_name: ${{ github.event.workflow_run.head_branch }}
      commit: ${{ github.event.workflow_run.head_sha }}
      fail_on_no_artifacts: true
```

The workflow checks that the tag points to `commit` before it releases anything.

## Inputs

<!-- generated: inputs-ru-release-with-artifacts -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `build_workflow` | string | `esp32-examples-build-ci.yml` | Name of the ESP32 build workflow |
| `artifact_pattern` | string | `fw-.*` | Pattern for firmware artifacts |
| `draft` | boolean | `false` | Create as draft release |
| `prerelease` | boolean | `false` | Mark as pre-release |
| `tag_name` | string | empty | Tag name for release (defaults to github.ref_name) |
| `fail_on_no_artifacts` | boolean | `false` | Fail if no firmware artifacts found |
| `commit` | string | empty | Commit whose CI artifacts are released, and that the release tag must point to. Empty: github.sha. A caller triggered by workflow_run passes github.event.workflow_run.head_sha, because github.sha is then the default branch's head, not the tagged commit. |
<!-- /generated -->

## Jobs and permissions

One job, `release`, with `contents: write`. It checks out with full history, downloads every artifact whose
name matches `artifact_pattern` from the run of `build_workflow` on `github.sha`
(`dawidd6/action-download-artifact`), builds the [release files](#what-the-release-holds) with
`tools/release_assets/release_assets.py` from ci-tools at the same commit as this workflow, and creates the release
for `tag_name` (default: the pushed tag) with generated notes and those files attached
(`softprops/action-gh-release`). The checksums also go to the run's summary.

The workflow does not ask for `actions: read`: existing callers grant only `contents: write`, and the token can
read artifacts of its own repository without it.

## What the release holds

For tag `v1.2.0` of a repository whose `driver.yml` names it `as5047u`:

| File | What it is |
| --- | --- |
| `as5047u-1.2.0.tar.gz` | The tagged tree (`git archive`), compressed with a fixed date: the same tag always gives the same bytes. GitHub's own "Source code" archives are not promised to be byte-stable, so checksums name this one. Submodules are not inside; the SBOM names each at its pinned commit. |
| `as5047u-1.2.0.spdx.json` | SBOM, [SPDX 2.3](https://spdx.github.io/spdx-spec/v2.3/) JSON: the repository as the main package (licence from `LICENSE`, the archive's SHA-256, the tagged commit), each git submodule as a package it contains (URL and pinned commit), and each firmware zip as a file generated from it. |
| `fw-<app>-<idf>-<type>.zip` | One per firmware artifact: for each ESP-IDF build in it, `flasher_args.json`, `flash_args`, every file they flash (bootloader, partition table, app) and the app's `.elf` and `.map`, at their build paths. An artifact with no `flasher_args.json` is zipped whole, with a warning. |
| `SHA256SUMS` | SHA-256 of every other file, in `sha256sum -c` format. |

One zip per artifact keeps Debug and Release apart. Uploading the build folders file by file, as versions before
1.7.0 did, attached thousands of files (an ESP-IDF build folder holds about 1,500), let files with the same name
in Debug and Release overwrite each other, and could pass GitHub's limit of 1,000 files per release.

### Check a download

```bash
gh release download v1.2.0 -R kokeb-labs/driver-as5047u -D v1.2.0
cd v1.2.0 && sha256sum -c SHA256SUMS        # macOS: shasum -a 256 -c SHA256SUMS
```

Every line must say `OK`. To flash a firmware zip: unzip it, go to the build folder inside and run
`esptool.py --chip <chip> write_flash @flash_args` (the chip is in `flasher_args.json`).

### Provenance

For a public repository, add [`ru-attest-release`](ru-attest-release.md) as a job after this one. It signs build
provenance for every file in `SHA256SUMS`, and `gh attestation verify` checks a download against it. It is a
separate workflow because it needs `id-token: write` and `attestations: write`, which callers of this workflow do
not grant.

## When it finds no firmware

The release only reuses artifacts; it never builds. It finds none when:

- the build workflow has not run on the tagged commit (tag a commit that was pushed to a branch the build runs on,
  and wait for that build to finish);
- the artifacts expired (`ru-build` keeps them 7 days);
- `build_workflow` names a different file than the caller of `ru-build`;
- `artifact_pattern` (a regular expression, default `fw-.*`) does not match.

With `fail_on_no_artifacts: false` (the default) the release is still created, without firmware, and the step
logs a warning. Set it to `true` to fail instead.

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `startup_failure` | The calling job does not grant `contents: write` | Grant it in the calling job |
| `Resource not accessible by integration` when creating the release | The repository restricts the workflow token to read | Grant `contents: write` in the caller; check **Settings > Actions > Workflow permissions** |
| Release has no firmware zips | See [above](#when-it-finds-no-firmware) | Set `fail_on_no_artifacts: true` to catch it |
| `release files share a name` | Two artifacts would give zips with the same name | Give the artifacts distinct names (`ru-build` names them by app, IDF version and build type) |
| `flasher_args.json lists files the artifact lacks` | The build artifact was uploaded without part of the build | Upload the whole build folder in `ru-build` |
| `tag ... does not exist here` | The release ran for a tag that was not pushed | Push the tag first |

Next: [ensure-tools-directory](ensure-tools-directory.md), for your own jobs that need the project tools.
