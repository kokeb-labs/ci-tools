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
| [`ci-host-quality.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-host-quality.yml), [`ci-cross-build.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-cross-build.yml) | | [`ru-host-quality`](ru-host-quality.md) and [`ru-cross-build`](ru-cross-build.md) on fixtures, in one job and with `separate_jobs` / `per_core_jobs`; the figures must agree |

## Scripts

| Script | Run by | Fails when |
| --- | --- | --- |
| `.github/scripts/check_run_tails.py` | `workflow-checks` | A `run:` block ends in a bare `cond && cmd` |
| `.github/scripts/check_permissions.py` | `workflow-checks` | The permissions of a workflow differ from the README table |
| `.github/scripts/gen_readme_inputs.py --check` | `workflow-checks` | A README inputs table differs from its workflow |
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
