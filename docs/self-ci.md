# How this repository tests itself

The checks every pull request to this repository runs, and what each one proves.

## Workflows

| Workflow | Job | What it checks |
| --- | --- | --- |
| [`ci-self.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-self.yml) | `actionlint` | actionlint with shellcheck, both pinned and verified by SHA-256, and the same shellcheck on the composite action (`shellcheck_actions.py`); any finding fails |
| | `workflow-checks` | The [`&&` tail rule](permissions.md#the-no-bare--tail-rule), the [permissions contract](permissions.md), the README inputs tables, unit tests of these scripts and of the CI gate, DCO and organisation-standard scripts, `ru-build`'s copy of the [`ensure-tools-directory`](ensure-tools-directory.md) script, [`ru-repo-checks`](ru-repo-checks.md)' copies of the single checks' steps, and, on pull requests, breaking changes against the base branch |
| | `docs-platform` | Unit tests of the theme package; the template site builds strictly with current figures; the migration tool turns a Jekyll fixture into a site that builds strictly |
| | `dco`, `org-standard` | [`dco`](dco.md) and [`org-standard-check`](org-standard-check.md) on this repository |
| | `ci-gate` | This repository's own [CI gate](ru-ci-gate.md); the required check is `CI gate / gate` |
| [`ci-docs-publish.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-docs-publish.yml) | `docs` | This site, through [`ru-mkdocs-publish`](ru-mkdocs-publish.md) at the same commit, published on `main` |
| | `selftest-mkdocs-unversioned` | `ru-mkdocs-publish` with `versioning: false` on the organisation-site fixture |
| | `selftest-site-in-subdir` | The legacy [`ru-docs-publish`](ru-docs-publish.md) on a Jekyll site in a subdirectory |
| [`ci-host-ci.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-host-ci.yml) | | `ru-host-ci` on a fixture: the preset path on clean code passes; the `-S`/`-B` path with seeded defects reports findings |
| [`ci-docs-linkcheck.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-docs-linkcheck.yml) | `selftest-own-site` | `ru-docs-linkcheck` skips the repository's own unpublished Pages site |
| `ci-cpp-lint.yml`, `ci-cpp-analysis.yml`, `ci-markdown-lint.yml`, `ci-yaml-lint.yml` | | Each reusable lint workflow on this repository |
| [`ci-repo-checks.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-repo-checks.yml) | `this-repository`, `findings` | [`ru-repo-checks`](ru-repo-checks.md) on this repository (every check passes), then on the known-bad handbook and cppcheck fixtures (the findings are counted) |
| [`ci-misra.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-misra.yml) | `validate-compilers`, `validate-codeql` (host, cortex-m), `record`, `ru-misra-fixture`, `ru-misra-fixture-check` | The [tool validation](tool-validation/plan.md) of the MISRA toolchain, and [`ru-misra`](ru-misra.md) on a fixture with known findings, deviations and bad suppressions (the counts are checked) |
| [`ci-host-quality.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-host-quality.yml), [`ci-cross-build.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-cross-build.yml) | | [`ru-host-quality`](ru-host-quality.md) and [`ru-cross-build`](ru-cross-build.md) on fixtures, in one job and with `separate_jobs` / `per_core_jobs`; the figures must agree |
| [`ci-cmake-matrix.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-cmake-matrix.yml) | `fixture`, `catalogue`, `outputs-checked` | [`ru-cmake-matrix`](ru-cmake-matrix.md): host GCC with tests and the install consumer, host Clang through a preset, an Arm entry, an ESP-IDF container entry, and a catalogue's pairs; every result is checked |
| [`ci-mutation.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-mutation.yml) | `catalogue`, `generated`, `outputs-checked` | [`ru-mutation`](ru-mutation.md): a catalogue at level high with one equivalent mutant, generated operators in two shards; the counts are checked |
| [`ci-pin-hygiene.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-pin-hygiene.yml) | `empty`, `stale`, `live`, `outputs-checked` | [`ru-pin-hygiene`](ru-pin-hygiene.md): an empty lock, a pin without a submodule (exactly PIN-001), and the checker on a scratch repository pinning a real driver |
| [`ci-layering.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-layering.yml) | `fixture`, `seeded`, `outputs-checked` | [`ru-layering`](ru-layering.md): the fixture tree with its good and bad cases, the poison build, the target graph and the symbol lint; one seeded case (exactly LAY-012) |
| [`ci-catalog.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-catalog.yml) | `fixture`, `outputs-checked` | [`ru-catalog`](ru-catalog.md): a real pinned driver read through the API; the catalogue equals the committed one; SBOMs, scan and Pages artifact |

## Scripts

| Script | Run by | Fails when |
| --- | --- | --- |
| `.github/scripts/check_run_tails.py` | `workflow-checks` | A `run:` block ends in a bare `cond && cmd` |
| `.github/scripts/check_permissions.py` | `workflow-checks` | The permissions of a workflow differ from the README table |
| `.github/scripts/gen_readme_inputs.py --check` | `workflow-checks` | A README inputs table differs from its workflow |
| `tools/cmake_matrix/test_cmake_matrix.py`, `tools/mutation/test_mutation.py`, `tools/pins/test_pins.py`, `tools/layering/test_layering.py`, `tools/catalog/test_catalog.py` | `workflow-checks` | A unit test of the scripts behind `ru-cmake-matrix`, `ru-mutation`, `ru-pin-hygiene`, `ru-layering` or `ru-catalog` fails |
| `.github/scripts/check_contract.py` | `workflow-checks` (pull requests) | A breaking change has no `### Breaking` entry |
| `.github/scripts/check_repo_checks.py` | `workflow-checks` | A step of `ru-repo-checks.yml` differs from the step of the single workflow it copies |
| `.github/scripts/shellcheck_actions.py` | `actionlint` | shellcheck reports a finding in a composite action's `run:` step |
| `.github/scripts/test_checks.py` | `workflow-checks` | A unit test of the scripts above, the CI gate, the DCO script (in Node) or the organisation-standard script fails |
| `kokeb-docs check` | `docs` | A table on this site differs from the workflows it is read from |

## Actions and updates

Third-party actions are pinned to full commit SHAs with a `# vX.Y.Z` comment. Dependabot proposes updates to them
and to the theme package's pinned toolchain.

## Run the checks locally

```bash
python3 -m pip install ./packages/kokeb-mkdocs-theme   # brings PyYAML
python3 .github/scripts/check_run_tails.py .github/workflows/*.yml .github/actions/*/action.yml
python3 .github/scripts/shellcheck_actions.py .github/actions/*/action.yml
python3 .github/scripts/check_permissions.py
python3 .github/scripts/gen_readme_inputs.py --check
python3 .github/scripts/check_repo_checks.py
python3 .github/scripts/test_checks.py
(cd packages/kokeb-mkdocs-theme && python3 -m unittest discover -s tests)
kokeb-docs check && mkdocs build --strict
```
