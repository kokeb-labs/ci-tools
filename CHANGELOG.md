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

### Added

- `ru-misra`: MISRA C++:2023 analysis with the CodeQL coding-standards pack (2.62.0, CLI 2.21.4) and the Kokeb C++20
  profile pack on traced host and Cortex-M builds, the handbook's deviation records applied through the pack's
  deviation mechanism (a marker must cite a record and deviate a finding of its guideline), clang-tidy's validated
  checks and cppcheck on the same compile databases, and a per-guideline report (step summary, SARIF, JSON keyed by
  guideline, CSV). Levels `high` and `safety`. Every scan analyses a canary and fails on incomplete extraction. The
  first job refuses private repositories without an Advanced Security licence (CodeQL terms). Needs `contents: read`.
- Tool validation of the MISRA toolchain (`docs/tool-validation/plan.md`): requirements derived from the compliance
  matrix and the pack, a seeded-violation and compliant case per requirement (`tests/misra-validation/`), a
  traceability page, an anomaly log, and a validation report attached to each release. The self-CI fails when a
  tool-decided guideline has no passing test, or when the toolchain changes without re-validation.
- `codeql/kokeb-cpp20`: the own C++20 profile query pack, with KB-CPP-046 (Result types are `[[nodiscard]]`).
- `ru-misra`: `open_source_prerelease` lets a private repository whose code is under the OSI licence in its LICENSE
  file, and is to be published, run the analysis; the job prints the declaration as a warning.
- Code scanning of ci-tools moves to an advanced setup (`.github/workflows/codeql.yml`, `security-and-quality`) that
  leaves out the test fixtures, which break rules on purpose and whose findings the self-CI asserts.
- `ru-misra` passes `cmake_args` and `paths` to its scanner as `--option=value`, so a value that starts with `-D`
  is not read as an option; the fixture self-test now passes one.

## [1.12.1] - 2026-11-08

### Fixed

- `ru-build`: the native build no longer downloads ccache on every run. The pinned, hash-checked binary is kept in
  the Actions cache by version; a download retries on every error with a delay, and one that still fails falls back
  to the runner's ccache package with a warning. GitHub release downloads returning HTTP 504 had failed whole
  ESP32 jobs.
- Self-CI caches its pinned shellcheck and actionlint by version and hash and retries their download on any
  error; `ru-cross-build` and `ru-docs-publish` retry their release downloads on any error (HTTP 5xx included).
- `ru-docs-linkcheck` and `ru-mkdocs-publish` run lychee 0.24.2 installed by the job (pinned, SHA-256-checked,
  kept in the Actions cache) instead of `lycheeverse/lychee-action`, which downloaded it from GitHub releases on every
  run. Same arguments, same failure rule; the link report goes to the step summary.
- `ru-docs-publish` (legacy): Doxygen 1.10.0 is kept in the Actions cache by version (falling back to the runner's
  package with a warning when GitHub releases fail), and its link check runs the same cached lychee.

## [1.12.0] - 2026-11-08

### Added

- `ru-build`: input `idf_install` (default `native`). The job installs ESP-IDF for the matrix target only (a shallow
  clone and `install.sh <target>`, about 1.1 GB) and keeps it in the Actions cache keyed by the commit the IDF
  version names, with a pinned, hash-checked ccache. A warm restore takes about 20 s, against 70 to 160 s to pull
  the 9.4 GB `espressif/idf` image; a Debug and Release build of one app dropped from 175 s to 93 s.
  `idf_install: docker` keeps the image and `espressif/esp-idf-ci-action`.

## [1.11.0] - 2026-11-08

### Added

- `ru-repo-checks`: DCO, the organisation standard, Markdown lint, the handbook rules, template drift, cppcheck and
  YAML lint as steps of one job, with the same scripts, pinned actions, failure rules and summaries as `dco`,
  `org-standard-check`, `ru-markdown-lint`, `ru-handbook-check`, `ru-template-drift`, `ru-cpp-analysis` and
  `ru-yaml-lint`. DCO runs first, before any checkout, and passes with nothing to check outside a pull request, so
  the gate needs no `allow_skipped` for it. Needs `contents: read` and `pull-requests: read`. The self-CI
  (`check_repo_checks.py`) fails when a copied step differs from its single workflow. The single workflows stay.
- `ru-cross-build`: input `per_core_jobs` (default `false`) keeps one job per core.
- `ru-host-quality`: input `separate_jobs` (default `false`) keeps one job per check.

- Trigger policy (`docs/triggers.md`), enforced by the self-CI (`check_triggers.py`): workflows
  start only from `push`, `pull_request`, `merge_group` and `workflow_call`, with `release.yml`'s `workflow_run` as
  the one exception.

### Changed

- The self-test callers (`ci-*.yml`) and the mkdocs-site template no longer have a `workflow_dispatch` trigger: a
  manual run is a re-run. A dispatched run executes in the default branch's context and can write the cache that
  runs on `main` restore, which made every checkout of a pinned ci-tools or driver-template commit a CodeQL
  `actions/cache-poisoning/poisonable-step` finding. The examples in the docs drop it too.
- `ru-cross-build`: every core is built in one job, one after the other, each in its own build directory and log
  group; a core that fails does not stop the others. The toolchain is downloaded once, and a private repository
  is billed one rounded-up job instead of four (the plan job and one per core).
- `ru-host-quality`: complexity, coverage and sanitizers run as steps of one job, each still running when another
  failed, with the same limits, summaries, artifacts and outputs; the `limits` job is gone (each job resolves the
  limits itself). Fuzzing stays a job of its own and no longer waits for the limits job. A private repository is
  billed one rounded-up job instead of four.

## [1.10.0] - 2026-11-08

### Added

- `ru-build`: input `group_build_types` (default `true`) builds every build type of an app and IDF version in one
  job, so the runner is prepared and the ESP-IDF image pulled once per app instead of once per build type. The job
  name and artifact name list the build types together (`Debug Release`).

### Changed

- `ru-build`: ccache's directory is now kept between runs (`actions/cache`, skipped with `clean_build`). Before,
  `IDF_CCACHE_ENABLE` left it inside the container and every build started cold.
- `ru-build`: the runner's unused SDKs are removed in parallel, and only when less than 30 GB is free.
- `ru-mkdocs-publish`: the Lighthouse and screenshots job caches pip's wheels, the `@lhci/cli` download and
  Playwright's Chromium.

## [1.9.1] - 2026-11-08

### Fixed

- `ru-template-drift`: with `enforce: false` the job failed instead of warning when the scaffold printed only to
  stderr (an empty report made the summary's `grep` fail). The scaffold's errors now reach the log and the summary.

## [1.9.0] - 2026-11-08

### Added

- `ru-template-drift`: compares the files driver-template manages (workflows, `_config/`, skills, CMake helpers)
  with what the template makes today from the caller's `.kokeb/template.yml`, using the template's own
  `scaffold.py --check-drift`. It warns by default; `enforce: true` fails on drift. The signed-release job had
  already drifted: two drivers had it and the template did not.

## [1.8.1] - 2026-11-07

### Fixed

- `ru-mkdocs-publish`: a pre-release tag (`vX.Y.Z-rc.N`) no longer takes the `latest` alias, and with
  `release_version: minor` no longer overwrites the docs of its minor; it publishes under its own tag. The first
  release candidate of driver-pcal9555 moved `latest` off `dev`, against the release standard.

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
