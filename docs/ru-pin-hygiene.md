# ru-pin-hygiene

Prove that every pinned submodule is a release that passed its own CI, so a repository can trust its pins instead
of re-running their checks.

`ru-pin-hygiene.yml` reads the lock file, `.gitmodules` and the gitlinks of the checked-out commit, then asks the
GitHub API about each pin with the workflow's built-in token. That token is the only credential it uses: there is
no token input. A pin to a private repository is a finding unless `private_repos: true`, and is then read with the
same token, so the token must be able to read it.

| Id | Check |
| --- | --- |
| PIN-001 | The lock has exactly one entry per submodule, and none without a submodule |
| PIN-002 | The gitlink commit equals the lock entry's `commit` |
| PIN-003 | The entry's `tag` exists and points at that commit (annotated tags dereferenced): a moved tag fails |
| PIN-004 | The tag matches `tag_pattern` and `kind` agrees (`rc` for `-rc.N`, else `release`); an rc pin in a final release of this repository is a warning |
| PIN-005 | The `required_check` concluded success on that commit (the newest run of that name) |
| PIN-006 | `driver.yml` at the commit: `name` is the lock's, `version` is the tag's without `v` and `-rc.N` |
| PIN-007 | `mcus` and `peripheral` equal the MCU gate table (`gates_file`); no entry means `mcus: [any]`, `peripheral: null` |
| PIN-008 | `kb_core_min` is null or not above this revision's version (`version_file`) |
| PIN-009 | `.kokeb/handbook.yml` at the commit declares one of `handbook_levels` |
| PIN-010 | Every `.gitmodules` URL matches `url_pattern`; with `submodules`, each working tree is clean |
| PIN-011 | `.gitmodules` has no `branch =` entry (`forbid_branch_entries`) |
| PIN-012 | At a release, `release_lock` lists the same pins and records this tree's commit |
| PIN-013 | The pinned repository is readable, and public unless `private_repos` |

## Lock file

```yaml
drivers:
  - name: ws2812_rmt                                # driver.yml name
    repo: kokeb-labs-drivers/driver-ws2812-rmt
    tag: v0.1.0-rc.1                                # vX.Y.Z or vX.Y.Z-rc.N
    commit: 2790be043fce5c620281aafa5b2bc2e0880af829
    kind: rc                                        # release | rc
```

A lock entry is matched to its submodule by the `.gitmodules` URL. The gate table is any file holding
`"<driver>:<MCU>:<peripheral>"` strings, such as a CMake list; the version file holds `set(<X>_VERSION_MAJOR n)`,
`_MINOR` and `_PATCH`, or a line `X.Y.Z`.

## Caller

```yaml
jobs:
  pins:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-pin-hygiene.yml@v1
    permissions:
      contents: read
    with:
      lock_file: drivers/drivers.lock.yml
      gates_file: cmake/mcu_gates.cmake
      version_file: cmake/version.cmake
      handbook_levels: "high safety"
```

## Report

Each finding is an annotation on the lock file's entry. The run summary has a table of every pin (repository, tag,
commit, kind, gate, result) and of every finding. The artifact holds `pins.json` and `pins.sarif`. The outputs give
the pin and finding counts and the rule ids that fired.

## Inputs

<!-- generated: inputs-ru-pin-hygiene -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `lock_file` | string | `drivers/drivers.lock.yml` | Lock file of the pins (drivers: [{name, repo, tag, commit, kind}]) |
| `gates_file` | string | empty | MCU gate table: a file of "<driver>:<MCU>:<peripheral>" strings; empty skips PIN-007 |
| `version_file` | string | empty | File with this revision's version (set(<X>_VERSION_MAJOR n) ..., or X.Y.Z); empty skips PIN-008 |
| `required_check` | string | `CI gate / gate` | Check run that must have concluded success on each pinned commit; empty skips PIN-005 |
| `tag_pattern` | string | `^v[0-9]+\.[0-9]+\.[0-9]+(-rc\.[0-9]+)?$` | Regular expression a pin's tag must match |
| `forbid_branch_entries` | boolean | `true` | Fail on a branch = entry in .gitmodules |
| `url_pattern` | string | `^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?(\.git)?$` | Regular expression every .gitmodules URL must match |
| `handbook_levels` | string | empty | Space-separated levels a pin's .kokeb/handbook.yml may declare (e.g. high safety); empty skips PIN-009 |
| `private_repos` | boolean | `false` | Accept pins to private repositories. They are read with the workflow's built-in token only (no other credential is accepted), so the token must be able to read them. |
| `release_lock` | string | empty | Release lock to check at a release (PIN-012): its pins equal the lock's and it records HEAD |
| `submodules` | string | `false` | Check out the submodules too, so PIN-010 also checks that each working tree is clean |
| `enforce` | boolean | `true` | Fail the job on a finding; false reports only (the counts are in the outputs) |
| `artifact_name` | string | `pin-hygiene-report` | Name of the report artifact (JSON and SARIF) |
<!-- /generated -->

## Jobs and permissions

<!-- generated: jobs-ru-pin-hygiene -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `pins` (pins) | `contents: read` | `actions/checkout`; `actions/checkout`; Install PyYAML (pinned, hash-checked); Check every pin; `actions/upload-artifact` |
<!-- /generated -->

`contents: read` checks out the caller; the API calls read public repositories (and, with `private_repos`, the
private ones the token can read).

## Self-test

[`ci-pin-hygiene.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-pin-hygiene.yml) checks
an empty lock (no finding), a lock whose real pin has no submodule (exactly PIN-001), and runs the checker on a
scratch repository whose gitlink pins `driver-ws2812-rmt` at `v0.1.0-rc.1`: clean first, then PIN-004 after the
entry's kind is changed.
