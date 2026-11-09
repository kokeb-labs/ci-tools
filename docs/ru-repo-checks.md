# ru-repo-checks

The small checks of a repository (sign-off, organisation standard, Markdown and YAML lint, handbook rules, template
drift and cppcheck) as steps of one job, with the same scripts and failure rules as their single workflows.

GitHub bills every job of a private repository rounded up to a whole minute. Each of these checks takes 5 to 15
seconds, so as seven jobs they cost seven minutes a run; as one job they cost one or two.

| Step | Same as | Fails the job when | Turn off |
| --- | --- | --- | --- |
| DCO | [`dco`](dco.md) | a commit of the pull request has no `Signed-off-by` matching its author | `run_dco: false` |
| Org standard | [`org-standard-check`](org-standard-check.md) | a required root file is missing or empty, or `LICENSE` is not MIT | `run_org_standard: false` |
| Markdown lint | [`ru-markdown-lint`](ru-markdown-lint.md) (the markdownlint-cli2 action) | markdownlint reports an issue | `run_markdown_lint: false` |
| Handbook rules | [`ru-handbook-check`](ru-handbook-check.md) | a handbook error (with `handbook_enforce: true`, the default) | `run_handbook: false` |
| Template drift | [`ru-template-drift`](ru-template-drift.md) | never by default; with `template_drift_enforce: true`, on drift | `run_template_drift: false` |
| cppcheck | [`ru-cpp-analysis`](ru-cpp-analysis.md) | cppcheck itself fails, or with `cppcheck_strict: true` it reports a finding | `run_cppcheck: false` |
| YAML lint | [`ru-yaml-lint`](ru-yaml-lint.md) | yamllint reports an error (with `yaml_strict_mode: true`, a warning too) | `run_yaml_lint: false` |

Every check runs whether or not an earlier one failed, and writes the summary its single workflow writes. The job
summary ends with one line per check, and the `failed` output lists the checks that failed. The self-CI
(`check_repo_checks.py`) fails when a step here differs from the step of the single workflow it copies, so a fix to
one reaches the other.

## Caller

```yaml
jobs:
  checks:
    name: Repository checks
    uses: kokeb-labs/ci-tools/.github/workflows/ru-repo-checks.yml@v1
    permissions:
      contents: read
      pull-requests: read
    with:
      markdown_globs: 'docs/** *.md **/*.md'
      cppcheck_paths: "inc src"
      cppcheck_strict: true
```

Add the job to the CI gate's `needs`. DCO passes with nothing to check on an event that is not a pull request (a
push to `main`, a tag), so the job always runs and needs no `allow_skipped` entry, unlike a `dco.yml` job that is
skipped outside pull requests.

## Order and trust

1. **DCO first**, before anything is checked out. It reads the commits through the API, so no code of the pull
   request has run in the job when the verdict is made.
2. The caller's checkout, then the organisation standard and the Markdown lint.
3. The handbook checker (this repository's `tools/handbook_check` at the workflow's own commit) and driver-template
   (for its `scaffold.py --check-drift`) are checked out into the workspace, after the Markdown lint so that they
   are never linted as the caller's files. They are removed again before the YAML lint.
4. cppcheck, then the YAML lint last: its install puts yamllint's virtual environment on `PATH`.

The job has `contents: read` and `pull-requests: read` only, no secrets and no cache, so nothing it runs can write
to the caller's repository, its pull requests, its caches or its releases.

## Jobs and permissions

<!-- generated: jobs-ru-repo-checks -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `checks` (repository checks) | `contents: read`, `pull-requests: read` | DCO: check the sign-off of every commit; `actions/checkout`; Org standard: required files and the MIT licence; Markdown lint: markdownlint-cli2; Markdown lint: result; Handbook: check out the checker; Handbook: install PyYAML (pinned, hash-checked); Handbook: check; Template drift: check out driver-template; Template drift: compare with the template; cppcheck: install; cppcheck: run; cppcheck: upload the report; cppcheck: fail on findings (strict); Remove the checked-out tools; YAML lint: install yamllint (pinned, hash-checked); YAML lint: yamllint; Summary |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-repo-checks -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `run_dco` | boolean | `true` | Run the DCO sign-off check (pull requests; on other events it passes with nothing to check) |
| `dco_allow_bots` | boolean | `true` | Accept commits whose GitHub author is a bot account (type Bot, or a login ending in [bot]), such as Dependabot or github-actions, without a sign-off. |
| `dco_skip_merge_commits` | boolean | `true` | Accept merge commits (more than one parent) without a sign-off; they add no authored change of their own. |
| `run_org_standard` | boolean | `true` | Run the organisation-standard check (required root files, MIT licence) |
| `org_standard_extra_files` | string | empty | More files that must exist, as paths relative to the repository root separated by spaces or newlines (for example `SECURITY.md docs/index.md`). The organisation's own list is always checked. |
| `run_markdown_lint` | boolean | `true` | Run markdownlint-cli2 |
| `markdown_globs` | string | `**/*.md` | Space-separated glob patterns of the Markdown files to check |
| `markdown_config_file` | string | `_config/.markdownlint.json` | Path of the markdownlint configuration file |
| `markdown_fix` | boolean | `false` | Fix fixable issues (markdownlint --fix); the runner's fix is not committed |
| `markdown_separator` | string | empty | Separator between the glob patterns. Empty: a space. |
| `run_handbook` | boolean | `true` | Run the handbook check |
| `handbook_path` | string | `.` | Directory of the repository the handbook check reads, relative to the checkout root |
| `handbook_enforce` | boolean | `true` | Fail on a handbook error. False reports only (the counts are in the outputs). |
| `run_template_drift` | boolean | `true` | Run the template drift check (a repository without .kokeb/template.yml gets a warning) |
| `template_drift_ref` | string | `main` | Branch, tag or commit of kokeb-labs/driver-template to compare against |
| `template_drift_enforce` | boolean | `false` | Fail on template drift. False reports only, as warnings on the drifted files. |
| `run_cppcheck` | boolean | `true` | Run cppcheck |
| `cppcheck_paths` | string | `src inc examples` | Directories cppcheck analyses (space-separated) |
| `cppcheck_std` | string | `c++20` | C++ standard |
| `cppcheck_strict` | boolean | `false` | Fail when cppcheck reports a finding (severity other than information) |
| `cppcheck_exclude` | string | empty | Paths cppcheck leaves out (space-separated) |
| `cppcheck_enable` | string | `warning,style,performance,portability,information` | Checks to enable (comma-separated: all,warning,style,performance, portability,information,unusedFunction,missingInclude) |
| `cppcheck_force` | boolean | `false` | Force checking even with incomplete analysis |
| `cppcheck_max_configs` | number | `0` | Maximum configs to check (for template-heavy code, 0=unlimited) |
| `cppcheck_artifact_name` | string | `cppcheck-report` | Name of the uploaded cppcheck report artifact (unique per call when a run calls this more than once) |
| `run_yaml_lint` | boolean | `true` | Run yamllint |
| `yaml_paths` | string | `**/*.yml,**/*.yaml` | Comma-separated paths or glob patterns of the YAML files to check |
| `yaml_config_file` | string | `_config/.yamllint` | Path of the yamllint configuration file |
| `yaml_strict_mode` | boolean | `false` | Fail on yamllint warnings too (--strict) |
| `yaml_exclude_patterns` | string | `.git/**,node_modules/**,venv/**,.venv/**,**/espidf-tools/**` | Comma-separated patterns of files the YAML lint leaves out |
<!-- /generated -->
