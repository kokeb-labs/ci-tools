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
