# ru-template-drift

Find the files a driver or library has let drift from [driver-template](https://github.com/kokeb-labs/driver-template).

Every scaffolded repository keeps a copy of the template's shell: the CI workflows, the tool configuration in
`_config/`, the agent skills and the CMake helpers. A fix in the template does not reach those copies by itself.
`ru-template-drift.yml` scaffolds the template again with the arguments the repository was made with
(`.kokeb/template.yml`, written by the scaffold) and compares each file the template manages. Code, tests, docs,
the README, the changelog and `_config/Kconfig` are the repository's own and are never compared.

The comparison is the template's own `tools/scaffold.py --check-drift`, so it always knows what the template makes
today.

## Caller

```yaml
jobs:
  template-drift:
    name: Template drift
    uses: kokeb-labs/ci-tools/.github/workflows/ru-template-drift.yml@v1
    permissions:
      contents: read
```

By default it warns on each drifted file and passes. With `enforce: true` drift fails the job.

## Jobs and permissions

<!-- generated: jobs-ru-template-drift -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `drift` (template drift) | `contents: read` | `actions/checkout`; `actions/checkout`; Compare with the template |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-template-drift -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `template_ref` | string | `main` | Branch, tag or commit of kokeb-labs/driver-template to compare against |
| `enforce` | boolean | `false` | Fail the job on drift. False reports only, as warnings on the drifted files. |
<!-- /generated -->

## Fix drift

```bash
git clone https://github.com/kokeb-labs/driver-template /tmp/driver-template
python3 /tmp/driver-template/tools/scaffold.py --check-drift .         # show each difference
python3 /tmp/driver-template/tools/scaffold.py --check-drift . --fix   # take the template's version
```

`--fix` overwrites each drifted file and records the template commit in `.kokeb/template.yml`. Review the diff
before committing: a difference can be a fix the repository made first, which then belongs in the template.

A file that differs on purpose (a skill that names this chip's pins, for example) goes under `local` with the
reason:

```yaml
local:
  - path: .claude/skills/add-port/SKILL.md
    reason: "names the WP pin and its GpioSet() mapping"
```

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `.kokeb/template.yml: missing` | The repository was scaffolded before the record existed | Add the record with the arguments it was scaffolded with (name, bus, description, platforms) |
| `the scaffold failed with the recorded arguments` | An argument in the record is invalid for the current template | Correct the record; the scaffold's message says which argument |
| `listed under local but matches the template` | The file was brought back in line | Remove its `local` entry |
