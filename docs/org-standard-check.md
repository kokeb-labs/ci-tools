# org-standard-check

Check that a repository has the root files every Kokeb Labs repository must carry, and that its licence is MIT.

`org-standard-check.yml` checks out the repository and fails when a required file is missing or empty, or when
`LICENSE` is not the MIT licence.

## What it checks

| Check | Passes when |
| --- | --- |
| `README.md` | the file exists and is not empty |
| `LICENSE` | the file exists and is not empty |
| `CHANGELOG.md` | the file exists and is not empty |
| `.github/CODEOWNERS` | the file exists and is not empty |
| Each path in `extra_files` | the file exists and is not empty |
| MIT licence | `LICENSE` holds the MIT grant, notice and warranty text (line wrapping ignored) and a `Copyright (c) <year> <holder>` line |

The result is a table in the job summary and one error annotation per failed check.

## Caller

```yaml
jobs:
  org-standard:
    uses: kokeb-labs/ci-tools/.github/workflows/org-standard-check.yml@v1
    permissions:
      contents: read
```

## Jobs and permissions

<!-- generated: jobs-org-standard-check -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `check` (Organisation standard) | `contents: read` | `actions/checkout`; Required files and the MIT licence |
<!-- /generated -->

## Inputs

<!-- generated: inputs-org-standard-check -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `extra_files` | string | empty | More files that must exist, as paths relative to the repository root separated by spaces or newlines (for example `SECURITY.md docs/index.md`). The organisation's own list is always checked. |
<!-- /generated -->

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `required file ... is missing or empty` | The file is not at that path | Add it; CODEOWNERS belongs in `.github/` |
| `LICENSE is not the MIT licence` | Another licence, or edited MIT text | Use the MIT text with `Copyright (c) <year> The Kokeb Labs Authors` |
| `LICENSE has no 'Copyright (c) <year> <holder>' line` | The copyright line is missing | Add it above the grant |
