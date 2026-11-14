# ru-catalog

Generate the compatibility catalogue of a revision from its pinned drivers, check it against the committed one, and
publish it with the revision's SBOMs and a known-vulnerability scan.

`ru-catalog.yml` does it in one job:

1. **Catalogue.** For each lock entry, `driver.yml` is read at the pinned commit: from the checked-out submodule
   (`submodules: true`), else through the GitHub API. The lock, every `driver.yml` and the result are validated
   against JSON schemas: the bundled ones (`tools/catalog/schemas/`), or the caller's in `schemas`. A driver whose
   `mcus` or `peripheral` disagree with the gate table is an error, not an entry. `configs` come from `results` and
   `results_json` (such as [`ru-cmake-matrix`](ru-cmake-matrix.md)'s `results` output). The output is
   deterministic: drivers by name, configurations by MCU and RTOS, no timestamp.
2. **Compare.** With `check: true` the job fails when `output` does not hold the same catalogue (compared as data,
   so its comments may differ); the generated file is in the artifact to commit.
3. **SBOM.** CycloneDX 1.6 and SPDX 2.3 JSON: the repository and every pinned driver with its version, tag, commit,
   repository, licence and package URL. The timestamps are the HEAD commit's, so the files are reproducible.
4. **Scan.** OSV-Scanner 2.7.0 (pinned, hash-checked) scans the tree (lock files, SBOMs, submodules) and the
   generated SBOMs. Each known vulnerability is an annotation; `fail_on_vulnerabilities` fails the job.
5. **Publish.** The catalogue (YAML and JSON), the SBOMs and the scan (JSON and SARIF) are one artifact. With
   `pages: true` a GitHub Pages artifact holds a static page of the catalogue and the same files.

## Catalogue (schema 1)

```yaml
schema: 1
kb_core: 0.2.0
drivers:
  - name: ws2812_rmt
    version: 0.1.0
    repo: kokeb-labs-drivers/driver-ws2812-rmt
    tag: v0.1.0-rc.1
    commit: 2790be043fce5c620281aafa5b2bc2e0880af829
    bus: [pio]
    mcus: [esp32]
    peripheral: rmt
    kb_core_min: null
    binding: null
    configs:
      - {mcu: ESP32, rtos: FREERTOS, result: pass}
```

The version is read from `version_file`, else from `project(VERSION)` in `CMakeLists.txt`, else from a
`cmake/*version*.cmake` file. `binding` is the include path of `binding_pattern` (with `{name}`) when that file
exists.

## Caller

```yaml
jobs:
  catalog:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-catalog.yml@v1
    permissions:
      contents: read
    with:
      lock_file: drivers/drivers.lock.yml
      gates_file: cmake/mcu_gates.cmake
      output: catalog/compat.yml
      submodules: true
```

## Publishing to GitHub Pages

The reusable workflow never asks for `pages: write` or `id-token: write`, so a caller that grants `contents: read`
keeps working. To publish, add a deploy job of your own on the default branch:

```yaml
  catalog:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-catalog.yml@v1
    permissions:
      contents: read
    with:
      pages: ${{ github.ref == 'refs/heads/main' }}

  catalog-pages:
    needs: catalog
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
    steps:
      - uses: actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346  # v5.0.1
```

## Inputs

<!-- generated: inputs-ru-catalog -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `lock_file` | string | `drivers/drivers.lock.yml` | Lock file of the pins (drivers: [{name, repo, tag, commit, kind}]), relative to root |
| `gates_file` | string | empty | MCU gate table: a file of "<driver>:<MCU>:<peripheral>" strings (a CMake list); empty: none |
| `version_file` | string | empty | File with this revision's version (set(<X>_VERSION_MAJOR n) ..., or X.Y.Z); empty looks in CMakeLists.txt's project(VERSION) and cmake/*version*.cmake |
| `output` | string | `catalog/compat.yml` | The committed catalogue, relative to root; the generated one is compared with it |
| `check` | boolean | `true` | Fail when the committed catalogue differs from the generated one |
| `results` | string | empty | Integration results file (JSON or YAML list of {driver?, mcu, rtos, result}), relative to root |
| `results_json` | string | empty | Integration results as JSON, e.g. ru-cmake-matrix's results output; added to results |
| `binding_pattern` | string | empty | Path of a driver's binding header with {name} for the driver name, relative to root; the catalogue records it from its include root (after inc/ or include/). Empty records binding: null. |
| `schemas` | string | empty | Folder of the caller's JSON schemas (lock.schema.json, driver.schema.json, compat.schema.json), relative to root; a file it lacks falls back to the bundled one |
| `root` | string | `.` | Folder the other paths are relative to |
| `submodules` | boolean | `false` | Check out the submodules; driver.yml is then read from them, else through the GitHub API |
| `sbom` | boolean | `true` | Write the CycloneDX 1.6 and SPDX 2.3 SBOMs |
| `sbom_name` | string | empty | Name of the SBOM's root component; empty uses the repository name |
| `osv` | boolean | `true` | Scan the tree (lock files, SBOMs, submodules) with OSV-Scanner for known vulnerabilities |
| `fail_on_vulnerabilities` | boolean | `true` | Fail the job when OSV-Scanner reports a known vulnerability |
| `pages` | boolean | `false` | Also upload a GitHub Pages artifact (index.html, compat.json, compat.yml, SBOMs, scan); deploy it from the caller with actions/deploy-pages (docs/ru-catalog.md) |
| `artifact_name` | string | `catalog` | Name of the artifact (catalogue, SBOMs, scan results) |
<!-- /generated -->

## Jobs and permissions

<!-- generated: jobs-ru-catalog -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `catalog` (compat.yml, SBOM and vulnerability scan) | `contents: read` | `actions/checkout`; `actions/checkout`; Install PyYAML and jsonschema (pinned, hash-checked); Generate, validate and compare the catalogue; SBOM (CycloneDX 1.6, SPDX 2.3); Restore OSV-Scanner; Known vulnerabilities (OSV-Scanner); `actions/upload-artifact`; Pages site; `actions/upload-pages-artifact` |
<!-- /generated -->

`contents: read` checks out the caller and this workflow's scripts; the API reads each pin's `driver.yml` and licence.

## Self-test

[`ci-catalog.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-catalog.yml) builds the
catalogue of `tests/fixtures/catalog` (a real driver pinned at its release-candidate tag, read through the API) and
checks it equals the committed file, then checks the SBOMs, the scan and the Pages artifact.
