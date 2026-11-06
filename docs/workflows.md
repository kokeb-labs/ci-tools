# Workflow catalogue

Every reusable workflow in this repository, what it is for and the permissions its caller grants.

Call a workflow from a job with `uses:` and pin the major tag, `@v1` ([Versioning](VERSIONING.md)). Grant the
permissions in the table on the calling job; a workflow that needs more than its caller grants fails before any
job starts ([Permissions contract](permissions.md)).

<!-- generated: workflow-catalogue -->
| Workflow | Purpose | Permissions |
| --- | --- | --- |
| [`dco.yml`](dco.md) | Fail a pull request when any of its commits lacks a `Signed-off-by:` line that matches the commit's author. | `contents: read`, `pull-requests: read` |
| [`org-standard-check.yml`](org-standard-check.md) | Check that a repository has the root files every Kokeb Labs repository must carry, and that its licence is MIT. | `contents: read` |
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
| [`ru-mkdocs-publish.yml`](ru-mkdocs-publish.md) | Build, check, audit and publish a Kokeb Labs documentation site with the shared theme, versioned or not. | `contents: write` |
| [`ru-release-with-artifacts.yml`](ru-release-with-artifacts.md) | Create a GitHub Release for a tag and attach the firmware that `ru-build` built and tested for the same commit. | `contents: write` |
| [`ru-release.yml`](ru-release.md) | Create a GitHub Release with generated notes for a tag. | `contents: write` |
| [`ru-yaml-lint.yml`](ru-yaml-lint.md) | Lint YAML files with yamllint against the repository's own rules. | `contents: read` |
<!-- /generated -->

## Which one to use

| A repository that | Calls |
| --- | --- |
| has any CI | [`ru-ci-gate`](ru-ci-gate.md) as the last job, the one required check |
| builds and tests C++ on the host with CMake | [`ru-host-ci`](ru-host-ci.md): build, ctest, clang-tidy and cppcheck on the same compile database |
| needs formatting and lint checks on C++ | [`ru-cpp-lint`](ru-cpp-lint.md), plus [`ru-cpp-analysis`](ru-cpp-analysis.md) when it has no host build |
| has documentation | [`ru-mkdocs-publish`](ru-mkdocs-publish.md) (the platform), [`ru-docs-linkcheck`](ru-docs-linkcheck.md) for links in Markdown outside the site |
| keeps Markdown or YAML | [`ru-markdown-lint`](ru-markdown-lint.md), [`ru-yaml-lint`](ru-yaml-lint.md) |
| tags releases | [`ru-release`](ru-release.md) |
| builds ESP32 firmware with ESP-IDF | [`ru-build`](ru-build.md), and [`ru-release-with-artifacts`](ru-release-with-artifacts.md) to ship the tested firmware ([ESP-IDF quickstart](esp-idf-quickstart.md)) |
| takes pull requests | [`dco`](dco.md): every commit signed off by its author |
| is a Kokeb Labs repository | [`org-standard-check`](org-standard-check.md): the required root files and the MIT licence |

Next: [Quickstart](quickstart.md).
