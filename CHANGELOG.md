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

### Fixed

- The bundled fonts' `@font-face` rules moved from `kokeb.css` to `assets/kokeb/fonts.css`, which loads without
  blocking the first paint (as Google Fonts did before). Referenced from the render-blocking stylesheet, the font
  files sat on Lighthouse's critical path and the portal's performance score fell from about 0.89 to 0.78.

### Changed

- The kokeb docs theme ships Inter and JetBrains Mono itself (variable woff2, SIL Open Font License) instead of
  loading them from Google Fonts, so no Kokeb page sends a reader's address to Google. `ru-mkdocs-publish` copies
  the fonts beside the Doxygen stylesheet for the API pages; the root 404 page uses system fonts.
- Mermaid, still loaded on demand from unpkg, is pinned to 11.17.2 and checked with Subresource Integrity, so a
  changed file on the CDN is refused instead of run.
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
