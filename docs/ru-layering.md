# ru-layering

Prove on every pull request that dependencies point down only and that SDK and RTOS code stays in its boundary files.

`ru-layering.yml` checks the tree against a rules file:

1. **Fixtures.** The checker runs on the caller's fixtures first: `good/` must give no finding, each `bad/<case>/`
   exactly the rule ids of its `expect.txt`. A case is a tree of its own; it uses its own `rules.yml` when it has
   one, else the caller's.
2. **Poison build.** The project is configured and built with a folder first on every system include path that holds
   a header that stops the build (`#error`) for every SDK and RTOS header named in `sdk_headers` (and common names
   under each pattern's folder), plus the caller's `poison_dir`. An SDK header reached by any path fails the build
   with LAY-002 on the including line.
3. **Check.** Every `#include` of every file in a zone, resolved through the poison build's compile database (or the
   tree's `inc/` and `include/` folders), the platform macros, the keywords, the CMake target graph
   (`cmake --graphviz`) and `nm` over every object of the build.

There is no suppression: a rule change is a change to the rules file, reviewed like code.

| Id | Finding |
| --- | --- |
| LAY-001 | An include the zone may not use (or the zone's `violation_id`); an include that resolves nowhere |
| LAY-002 | An SDK or RTOS header outside a listed boundary file, or in a boundary header |
| LAY-003 | A boundary file included by another file |
| LAY-006 | A CMake link against the layers, or a non-PRIVATE link to a `private_only` target |
| LAY-007 | A platform macro tested outside boundary files and zones that may use the SDK |
| LAY-008 | The boundary list and the tree disagree (a present file missing, a planned file present) |
| LAY-009 | A denylisted name (the list comes from the `denylist` secret and is never printed) |
| LAY-012 | A forbidden keyword in code (comments and strings excluded) |
| SYM-001 | A linked object of a platform-free zone references a forbidden symbol |
| own ids | `forbidden_patterns` of the rules file, such as a CMake file that adds `ports/` |

## Rules file

```yaml
zones:                       # first match wins; a zone may always include its own files
  core:
    paths: ["lib/core/inc/**", "lib/core/src/**"]
    may_include: [core, std_subset]
  backend:
    paths: ["lib/core/backends/**"]
    may_include: [core, std_subset, sdk]     # sdk: only in files of the boundary list
  app:
    paths: ["lib/app/**"]
    may_include: [app, core_public, std_subset]
public_headers:
  core_public: "lib/core/inc/core/**"
header_groups:
  unit_test: ["gtest/*", "gmock/*"]
boundary_files: deviations/boundary-files.yml
sdk_headers: ["freertos/*", "FreeRTOS.h", "esp_*"]
forbidden_keywords: [virtual]
platform_macros: [ESP_PLATFORM, "configUSE_*"]
external_zones: []           # zones whose files are include targets but not checked
forbidden_patterns:
  - {id: LAY-010, regex: 'add_subdirectory\(\s*"?ports', paths: ["**/CMakeLists.txt"], message: "adds ports/"}
targets:
  layers: [["mylib_core"], ["mylib_app"]]   # lowest first
  private_only: ["mylib_backend"]
symbols:
  forbidden: ['^x(Task|Queue|Semaphore)', '^esp_']
```

`may_include` names zones, `public_headers` groups, `header_groups`, `std_subset` (a freestanding subset of the
standard library unless the rules give one), `std_any`, `sdk` and `sdk_any` (an SDK header anywhere in the zone).
The boundary list is `boundary_files: [{path, sdk, status: present | planned}]`; a zone may name its own list.

## Caller

```yaml
jobs:
  layering:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-layering.yml@v1
    permissions:
      contents: read
    with:
      rules: tools/include_checker/rules.yml
      boundary_files: deviations/boundary-files.yml
      fixtures: tests/layering
      poison_cmake_args: "-DMYLIB_BUILD_TESTS=ON"
    secrets:
      denylist: ${{ secrets.LAYERING_DENYLIST }}   # optional
```

## Report

Each finding is an annotation with its rule id. The run summary has the counts per rule and the first 200
findings. The artifact holds `layering.sarif`, `layering.json`, the target graph and the poison build's logs.

## Inputs

<!-- generated: inputs-ru-layering -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `rules` | string | required | Rules file (zones, boundary files, SDK headers, keywords, targets, symbols), relative to root |
| `boundary_files` | string | empty | Boundary file list that replaces the rules file's boundary_files; empty uses the rules file's |
| `fixtures` | string | empty | Folder of the checker's fixtures, relative to root: good/ must give no finding, each bad/<case>/ exactly the rule ids of its expect.txt. Excluded from the check of the tree. Empty runs none. |
| `root` | string | `.` | Folder the rules' paths are relative to |
| `exclude` | string | empty | Space-separated globs, relative to root, that are not checked |
| `poison` | boolean | `true` | Run the poison build (needs a CMake project at source_dir) |
| `poison_cmake_args` | string | empty | Configure arguments of the poison build (build every platform-free translation unit) |
| `poison_dir` | string | `tests/poison` | Folder of extra poison headers, relative to root, copied over the generated ones (if present) |
| `source_dir` | string | `.` | CMake source folder of the poison build, relative to root |
| `build_target` | string | empty | Target of the poison build; empty builds all |
| `build_parallel` | string | `2` | Jobs of the poison build |
| `compiler` | string | `gcc` | gcc or clang, the version of tools/misra/toolchain.json |
| `symbol_lint` | boolean | `true` | Run nm over the poison build's objects (the rules' symbols, or the default SDK and RTOS symbols) |
| `submodules` | string | `false` | actions/checkout submodules value: false, true or recursive |
| `enforce` | boolean | `true` | Fail the job on a finding; false reports only (the count is in the outputs) |
| `artifact_name` | string | `layering-report` | Name of the report artifact (SARIF, JSON, build log) |
<!-- /generated -->

## Jobs and permissions

<!-- generated: jobs-ru-layering -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `check` (includes, links and poison build) | `contents: read` | `actions/checkout`; `actions/checkout`; Install PyYAML (pinned, hash-checked) and the compiler (toolchain.json); The checker's fixtures; Poison build; Layering check; `actions/upload-artifact` |
<!-- /generated -->

## Self-test

[`ci-layering.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-layering.yml) runs the
fixture tree `tests/fixtures/layering` (a good case and eight bad ones, then the tree itself with the poison build,
the target graph and the symbol lint: no finding) and one bad case as a tree (exactly LAY-012, not enforced).
