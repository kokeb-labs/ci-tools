# Changelog

All notable changes to the reusable workflows in this repository are
documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and releases follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
as described in [docs/VERSIONING.md](docs/VERSIONING.md).

A change that breaks callers pinned to the current major goes under a
`### Breaking` heading in **Unreleased**, and the next release must then be a
major bump. Breaking means: a workflow or input removed, an input's type
changed, an input or secret made required, an output removed, or a job
needing a permission it did not need before. The self-CI
(`check_contract.py`) fails a pull request that makes such a change without
that heading.

## [Unreleased]

## [1.8.0] - 2026-11-07

### Added

- `ru-attest-release`: signed build provenance (GitHub artifact attestation, SLSA, Sigstore) for every file of a
  published release, after the files are checked against its `SHA256SUMS`. Callers add it as a job after
  `ru-release` or `ru-release-with-artifacts` and grant `id-token: write` and `attestations: write`. Public
  repositories, or GitHub Enterprise Cloud.

## [1.7.0] - 2026-11-07

### Added

- `ru-release` and `ru-release-with-artifacts` attach supply-chain files to every release: a source archive with a
  stable checksum (`<name>-<version>.tar.gz`), an SPDX 2.3 SBOM (`<name>-<version>.spdx.json`: the repository,
  its licence and tagged commit, each git submodule at its pinned commit, each firmware zip) and `SHA256SUMS`.
  Built by the new `tools/release_assets/release_assets.py` (standard library only, unit-tested in the self-CI);
  the checksums also go to the run summary. Signed provenance waits for public repositories
  (`docs/ru-release-with-artifacts.md#provenance`).

### Changed

- `ru-release-with-artifacts` attaches one zip per firmware artifact, holding what flashes and debugs each ESP-IDF
  build (`flasher_args.json`, `flash_args`, the files they flash, the app `.elf` and `.map`), instead of every file
  of the build folders. The old upload sent about 2,900 files for a driver with a Debug and a Release build, past
  GitHub's limit of 1,000 per release, and files of the same name in Debug and Release overwrote each other.

## [1.6.0] - 2026-11-07

### Added

- `ru-host-quality`: a `fuzz` job. With `fuzz_cmake_args` set (for example `-DMYCHIP_BUILD_FUZZERS=ON`), it builds
  with clang 18 and libFuzzer, ASan and UBSan, and fuzzes every `fuzz_<name>` executable for `fuzz_seconds` (by
  level: 60, 120, 600 s). Each target starts from its committed seeds in `tests/fuzz/corpus/fuzz_<name>/` plus a
  corpus cached between runs. The step summary has runs, coverage edges and corpus size per target, and a failing
  input is uploaded as `<artifact_name>-fuzz-crashes`. Without `fuzz_cmake_args` nothing changes.

## [1.5.3] - 2026-11-07

### Changed

- `ru-handbook-check`: the rules snapshot follows the handbook's ADR-0021 (`EnsureInitialized()` is the one start-up
  entry point: KB-CPP-043, KB-CPP-058, KB-CPP-059) and the new datasheet-trail rule KB-DOC-065.

## [1.5.2] - 2026-11-07

### Fixed

- `ru-host-quality`: coverage merges the instances of a template (`gcovr --merge-lines`), so a line, branch or
  condition counts as covered when any instance ran it. A header-only driver is compiled once per port type, and an
  example's instance that runs only the happy path counted every failure path again, as uncovered: the AS5047U
  driver measured 73.8 % of branches instead of 94.5 %.

## [1.5.1] - 2026-11-07

### Fixed

- `ru-host-quality`: the complexity job now measures header-only implementation files (`.ipp`, `.tpp`, `.inl`).
  lizard picks the files of a directory by extension and skipped them, so a driver whose code lives in
  `src/<chip>.ipp` had its implementation unmeasured. The job lists every C and C++ file under `library_paths`
  itself; the self-test fixture has a too-complex function in an `.ipp` file as well and must report both.
- `ru-cpp-lint`: `extensions` defaults to `c,cpp,cc,cxx,h,hpp,ipp,tpp,inl`, so clang-format checks header-only
  implementation files. clang-tidy skips those files as translation units and reports on them through the
  sources that include them, as before. Callers that set `extensions` add `ipp` themselves.

## [1.5.0] - 2026-11-06

### Added

- `ru-handbook-check`: checks a repository against the Kokeb Labs handbook rules a script can decide. It reads the
  `.kokeb/handbook.yml` declaration (handbook version, kind, assurance level, waivers) and checks the root layout,
  `driver.yml` against the build settings, C++20 and no `file(GLOB)` in CMake, no heap, exceptions, RTTI or virtual
  functions in driver code, the target library subset of headers, and no committed `sdkconfig` or datasheet. Each
  finding names its rule, quotes its title and links to it; a rule still in its warning period warns, a waived
  rule is a notice, and an expired waiver fails. The checker (`tools/handbook_check/`) and its snapshot of the
  rules are fetched at this workflow's own commit; 15 unit tests and good and bad fixture repositories run under
  the CI gate.

### Fixed

- `tools/docs-migrate.py`: a character range listed twice in the emoji pattern (CodeQL `py/overly-large-range`).

## [1.4.0] - 2026-11-06

### Added

- `ru-cross-build`: builds one CMake target for Cortex-M0+, M3, M4F, M7F and M33F cores with Arm's GNU toolchain
  14.3.rel1 (pinned, SHA-256 checked; an Ubuntu mirror hung one install for 20 minutes), one job per core, with the caller's own warning and language flags, and reports
  the objects' code and data size. A driver proves its code compiles for a microcontroller, not only on the host.

## [1.3.0] - 2026-11-06

### Added

- `ru-release-with-artifacts` takes a `commit` input: the commit whose CI artifacts are released, for callers that
  release from a finished CI run (`workflow_run`), where `github.sha` is the default branch's head. It also checks
  that the release tag points to that commit before releasing. The guide shows a caller that releases only after
  CI passed on the tag.

### Fixed

- `ru-build` no longer fails pull requests from forks: their token cannot comment, so the size comment is skipped
  for them (and never fails the job), and the size table is always written to the run summary. On same-repository
  pull requests the comment is updated on each push instead of added again.

### Security

- `ru-yaml-lint` installs yamllint 1.38.0 pinned with SHA-256 hashes on `ubuntu-24.04`, instead of the latest
  yamllint from an unpinned `pip install`.
- `ru-host-ci` passes `artifact_name` through the environment instead of expanding it inside a shell command.
- `ru-markdown-lint` with `use_docker: true` pulled `markdownlint/markdownlint-cli2:latest`, an image that does not
  exist; it now uses the author's image `davidanson/markdownlint-cli2`, pinned to v0.23.3 by digest.

## [1.2.1] - 2026-11-06

### Changed

- `ru-cpp-lint` runs clang-format 20.1.8 and clang-tidy 20.1.0 itself, from LLVM's builds on PyPI pinned with their
  SHA-256, instead of cpp-linter-action. That action installed clang from LLVM's apt server, fetching and running its
  install script as root without a pinned version or checksum, and the install hung for 20 minutes several times
  a day. The job now needs only `contents: read`; `thread_comments` and `lines_changed_only` are accepted but
  ignored (whole files are checked). Findings are annotations and a run-summary table, as before.

### Security

- The `cpp-linter/cpp-linter-action` and `hustcer/setup-nu` actions are no longer used, so they can leave the
  organisation's allow-list.

## [1.2.0] - 2026-11-06

### Added

- `ru-host-quality`: complexity (lizard, modified cyclomatic complexity, length, parameters), coverage (GCC 14 and
  gcovr: lines, branches and MC/DC from `-fcondition-coverage`) and AddressSanitizer/UndefinedBehaviorSanitizer
  jobs, with the limits the Kokeb Labs handbook sets per assurance level (`level: standard | high | safety`). Tools
  are pinned and hash-checked. Its self-test runs under the CI gate, including a fixture over every complexity
  limit that must be reported.

## [1.1.0] - 2026-11-06

### Changed

- A release waits for the whole self-CI on the merged commit (`release.yml` runs on `workflow_run` of
  "🧪 Workflow Self-CI"). The self-tests of the reusable workflows (`ci-*.yml`) are now called from `ci-self.yml`, so
  the required "CI gate" covers them: a red reusable workflow can neither merge nor reach `@v1`. The Markdown lint
  self-test reports issues instead of fixing them in the runner.
- `ru-cpp-lint` fails the job when clang-format or clang-tidy reports a finding (`fail_on_findings`, default true);
  before, findings were only annotated and the job always passed. A new `cmake_args` input configures CMake with
  `compile_commands.json`, so clang-tidy sees the project's include paths; without it clang-tidy could not find
  the project's own headers. A `findings` output gives the count.
- `ru-cpp-analysis` runs cppcheck from Ubuntu's archive instead of the unpinned `ghcr.io/facthunder/cppcheck:latest`
  image, no longer ignores cppcheck's own exit status, counts findings from the XML report (`strict` used to fail
  on every run, because the report always has a header), defaults `std` to `c++20`, takes an `artifact_name`, and
  has a `findings` output.

- Releases of this repository are cut from `CHANGELOG.md`: a pull request that should be released moves the
  Unreleased entries to a new `## [X.Y.Z] - YYYY-MM-DD` section (`python .github/scripts/changelog.py bump patch`),
  and merging it tags that version, publishes the section as the release notes and moves `v1`. Before, every merge
  was tagged and the changelog was left behind. The self-CI checks that a new section is the next version, is
  dated, and is a major when it has `### Breaking`.

## [1.0.5] - 2026-11-06

### Fixed

- The bundled fonts' `@font-face` rules moved from `kokeb.css` to `assets/kokeb/fonts.css`, which loads without
  blocking the first paint (as Google Fonts did before). Referenced from the render-blocking stylesheet, the font
  files sat on Lighthouse's critical path and the portal's performance score fell from about 0.89 to 0.78.

## [1.0.4] - 2026-11-06

### Changed

- Bundled fonts used `font-display: optional` without a preload. This did not restore the Lighthouse score and was
  replaced in 1.0.5.

## [1.0.3] - 2026-11-06

### Changed

- The kokeb docs theme ships Inter and JetBrains Mono itself (variable woff2, SIL Open Font License) instead of
  loading them from Google Fonts, so no Kokeb page sends a reader's address to Google. `ru-mkdocs-publish` copies
  the fonts beside the Doxygen stylesheet for the API pages; the root 404 page uses system fonts.

### Security

- Mermaid, still loaded on demand from unpkg, is pinned to 11.17.2 and checked with Subresource Integrity, so a
  changed file on the CDN is refused instead of run.

## [1.0.2] - 2026-11-05

### Security

- `ru-docs-publish` installs Doxygen from its own release, checked against a pinned SHA-256, and Graphviz with
  apt, instead of two small third-party actions (`ssciwr/doxygen-install`, `tlylt/install-graphviz`).

## [1.0.1] - 2026-11-06

### Changed

- figkit draws in the Kokeb palette (copper on light, star gold on dark), and its legend can explain solid and
  dashed arrows. A region can put its caption on a second line.
- The workflow figure shows the push lane and the tag lane apart, with labelled arrows.
- The style guide says how a figure reads: one direction, a verb on every arrow, colour for ownership.

## [1.0.0] - 2026-11-05

First release of `kokeb-labs/ci-tools`.

### Added

- Reusable workflows for C/C++ (`ru-host-ci`, `ru-cpp-lint`, `ru-cpp-analysis`), documentation
  (`ru-mkdocs-publish`, `ru-docs-publish`, `ru-docs-linkcheck`), Markdown and YAML lint (`ru-markdown-lint`,
  `ru-yaml-lint`), releases (`ru-release`) and the single required check (`ru-ci-gate`).
- ESP-IDF firmware workflows in the same repository: `ru-build` (matrix build from `app_config.yml`, size report
  and budget) and `ru-release-with-artifacts` (release with the tested firmware), plus the
  `ensure-tools-directory` composite action. The build finds or clones
  [espidf-tools](https://github.com/kokeb-labs/espidf-tools).
- `dco.yml`: fails a pull request when a commit lacks a `Signed-off-by:` line matching its author.
- `org-standard-check.yml`: fails when `README.md`, `LICENSE`, `CHANGELOG.md` or `.github/CODEOWNERS` is missing,
  or when `LICENSE` is not the MIT licence.
- `packages/kokeb-mkdocs-theme`: the documentation theme (`theme: kokeb`), plugin (`plugins: [kokeb]`), figkit and
  the `kokeb-docs` command, with the pinned MkDocs toolchain. The colours sit in one palette block
  (`--kb-palette-*` in `assets/kokeb/kokeb.css`).
- Self-CI: actionlint and shellcheck (pinned, SHA-256 verified), shellcheck of the composite action, the
  permissions contract, the README inputs tables, breaking-change detection, unit tests of the checks (the CI gate,
  the DCO script and the organisation-standard script included), the theme package's tests and the template site.

### Security

- Every reusable workflow sets `permissions: {}` at the top and the least each job needs; the self-CI enforces
  both. Every checkout sets `persist-credentials: false` except the two jobs that push (the release tag and the
  documentation branch).
