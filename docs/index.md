---
hide:
  - navigation
  - toc
---

<div class="kb-hero" markdown>
<span class="kb-kicker">Kokeb Labs CI and documentation platform</span>

# CI Tools

<p>Reusable GitHub Actions workflows that every Kokeb Labs repository calls: C/C++ lint and analysis, host builds and
tests, ESP-IDF firmware builds, the documentation platform, link and lint checks, the DCO sign-off and
organisation-standard checks, releases, and one required CI gate. Callers pin <code>@v1</code> and get fixes without
breaking changes.</p>

[Quickstart](quickstart.md){ .md-button .md-button--primary }
[Workflow catalogue](workflows.md){ .md-button }
[Source on GitHub](https://github.com/kokeb-labs/ci-tools){ .md-button }
</div>

A repository keeps a few short caller workflows; the jobs, the pinned tools and the checks live here. Every
third-party action is pinned to a commit SHA, so `@v1` pins everything a caller runs.

## What you get

- **One required check.** [`ru-ci-gate`](ru-ci-gate.md) turns every job of a workflow into `CI gate / gate`.
- **C++ checks that agree with the compiler.** [`ru-host-ci`](ru-host-ci.md) builds, runs ctest, then
  clang-tidy 18 and cppcheck over the same compile database.
- **The documentation platform.** [`ru-mkdocs-publish`](ru-mkdocs-publish.md) builds a site with the shared theme
  in [`packages/kokeb-mkdocs-theme`](https://github.com/kokeb-labs/ci-tools/tree/main/packages/kokeb-mkdocs-theme),
  checks it, audits it and publishes it, versioned or not ([platform guide](docs-platform.md)).
- **ESP-IDF firmware.** [`ru-build`](ru-build.md) builds every app of `app_config.yml` across ESP-IDF versions
  and build types with a size report; [`ru-release-with-artifacts`](ru-release-with-artifacts.md) ships the
  tested firmware ([ESP-IDF quickstart](esp-idf-quickstart.md)).
- **Organisation checks.** [`dco`](dco.md) fails a pull request with an unsigned commit;
  [`org-standard-check`](org-standard-check.md) checks the required root files and the MIT licence.
- **Releases without breaking callers.** Semver tags, a moving `v1`, a release for each changelog version a pull
  request adds, and a check that stops a breaking change from landing without a major ([Versioning](VERSIONING.md)).
- **A permissions contract.** Each workflow asks for the least it needs, per job, and the self-CI holds it to
  the [documented table](permissions.md).

## Workflows

<!-- generated: workflow-catalogue -->
| Workflow | Purpose | Permissions |
| --- | --- | --- |
| [`dco.yml`](dco.md) | Fail a pull request when any of its commits lacks a `Signed-off-by:` line that matches the commit's author. | `contents: read`, `pull-requests: read` |
| [`org-standard-check.yml`](org-standard-check.md) | Check that a repository has the root files every Kokeb Labs repository must carry, and that its licence is MIT. | `contents: read` |
| [`ru-attest-release.yml`](ru-attest-release.md) | Sign build provenance for every file of a published release. | `attestations: write`, `contents: read`, `id-token: write` |
| [`ru-build.yml`](ru-build.md) | Build every ESP32 example app of a repository across ESP-IDF versions and build types, upload the firmware and report its size on pull requests. | `contents: read`, `pull-requests: write` |
| [`ru-ci-gate.yml`](ru-ci-gate.md) | One required status check per repository: it passes only when every other CI job passed. | `contents: read` |
| [`ru-cpp-analysis.yml`](ru-cpp-analysis.md) | Run cppcheck over source folders, without a build, and keep the report as an artifact. | `contents: read` |
| [`ru-cpp-lint.yml`](ru-cpp-lint.md) | Check C and C++ formatting with clang-format and lint with clang-tidy, with results as annotations on the pull request. | `contents: read` |
| [`ru-cross-build.yml`](ru-cross-build.md) | Compile a CMake target for microcontroller cores with the GNU Arm Embedded toolchain, so code that claims to run on any MCU is shown to compile for one on every pull request. | `contents: read` |
| [`ru-docs-linkcheck.yml`](ru-docs-linkcheck.md) | Check every link in a repository's Markdown, external ones included, with lychee. | `contents: read` |
| [`ru-docs-publish.yml`](ru-docs-publish.md) | Build a Jekyll site with Doxygen and publish it to `gh-pages` in version folders: the documentation pipeline that [`ru-mkdocs-publish`](ru-mkdocs-publish.md) replaces. | `contents: write` |
| [`ru-handbook-check.yml`](ru-handbook-check.md) | Check a repository against the [Kokeb Labs handbook](https://kokeb-labs.github.io/handbook/) rules that a script can decide, and report every finding by rule ID. | `contents: read` |
| [`ru-host-ci.yml`](ru-host-ci.md) | Build, test and analyse a CMake project on the host, with clang-tidy 18 and cppcheck over the compiler's own compile database. | `contents: read` |
| [`ru-host-quality.yml`](ru-host-quality.md) | Complexity, coverage and sanitizer gates for a CMake C/C++ project, with the limits the Kokeb Labs handbook sets for each assurance level (ADR-0020). | `contents: read` |
| [`ru-markdown-lint.yml`](ru-markdown-lint.md) | Lint Markdown with markdownlint-cli2 against the repository's own rules. | `contents: read` |
| [`ru-misra.yml`](ru-misra.md) | Check C++ code against MISRA C++:2023 with the validated open-source toolchain, and get a per-guideline report. | `contents: read` |
| [`ru-mkdocs-publish.yml`](ru-mkdocs-publish.md) | Build, check, audit and publish a Kokeb Labs documentation site with the shared theme, versioned or not. | `contents: write` |
| [`ru-release-with-artifacts.yml`](ru-release-with-artifacts.md) | Create a GitHub Release for a tag and attach the firmware that `ru-build` built and tested for the same commit. | `contents: write` |
| [`ru-release.yml`](ru-release.md) | Create a GitHub Release with generated notes for a tag. | `contents: write` |
| [`ru-repo-checks.yml`](ru-repo-checks.md) | The small checks of a repository (sign-off, organisation standard, Markdown and YAML lint, handbook rules, template drift and cppcheck) as steps of one job, with the same scripts and failure rules as their single workflows. | `contents: read`, `pull-requests: read` |
| [`ru-template-drift.yml`](ru-template-drift.md) | Find the files a driver or library has let drift from [driver-template](https://github.com/kokeb-labs/driver-template). | `contents: read` |
| [`ru-yaml-lint.yml`](ru-yaml-lint.md) | Lint YAML files with yamllint against the repository's own rules. | `contents: read` |
<!-- /generated -->

<div class="grid cards" markdown>

-   **[Quickstart](quickstart.md)**

    The smallest CI for a repository: one workflow, the gate, pinned to `@v1`.

-   **[Versioning](VERSIONING.md)**

    Tags, the moving major, what counts as breaking, releases from the changelog.

-   **[Permissions contract](permissions.md)**

    What each workflow needs from its caller, and why a missing grant fails before any job runs.

-   **[Docs platform](docs-platform.md)**

    The theme package, the publish workflow, the migration tool and the style guide.

-   **[Workflow catalogue](workflows.md)**

    One page per workflow: what it does, jobs, permissions, inputs and failure modes.

-   **[How this repository tests itself](self-ci.md)**

    Self-CI, contract checks and the fixtures every change runs against.

</div>
