# ru-mutation

Find the guards no test checks: change the code one edit at a time and require the tests to fail on every change.

`ru-mutation.yml` lists the mutants, builds and tests each one, and reports the kill rate:

1. **Mutants.** From catalogue files in the drivers' `tools/mutants` format, or generated over `mutate_paths`, or
   both (`mode`). `auto` uses the catalogues when one exists and generates otherwise.
2. **Run.** The mutants are split into `shards` parallel jobs. Each job copies the tree once per worker, configures
   and builds it, and runs the tests of the unedited tree first: when they fail, no verdict can be read and the job
   stops. Then each mutant is applied, built incrementally, tested with ctest under a timeout (`timeout_factor` times
   the unedited run, at least 30 s) and restored.
3. **Report.** Kill rate = killed / (killed + survived). `level: high` needs 100 % and no broken catalogue mutant;
   `standard` needs 80 %; `threshold` overrides the percentage.

| Verdict | Meaning | Scored |
| --- | --- | --- |
| killed | A test failed or timed out, or a `static_assert` fired | yes |
| survived | Every test passed: a guard no test checks | yes |
| compile_error | A generated edit that does not compile | no |
| broken | A catalogue edit whose old text is not in the file, or that does not compile: the catalogue drifted | fails `high` |
| equivalent | Listed in the equivalents file with its reason; not run | no |

A survivor is fixed by a test that kills it, or recorded as equivalent with the reason the edit cannot change
behaviour; never by deleting the mutant.

## Catalogue format

```text
# One block per mutant: "id | file | what the edit removes", an optional "= reason" line (equivalent), then
# the old text ("- " lines) and the new text ("+ " lines); a bare "-" or "+" is an empty line.
retry-cap | inc/mychip_types.hpp | the ten-retry limit
- kMaxRetries = 10;
+ kMaxRetries = 11;
```

The first occurrence of the old text is edited. File paths are relative to `root`.

## Generated operators

| Operator | Edit |
| --- | --- |
| `ror-*` | `<` `<=` `>` `>=` `==` `!=` to the neighbouring comparison |
| `lcr-and`, `lcr-or` | `&&` and `\|\|` swapped |
| `aor-add`, `aor-sub` | `+` and `-` swapped |
| `neg` | `!x` to `x` |
| `bool-true`, `bool-false` | `true` and `false` swapped |
| `const` | an integer literal `n` to `n + 1` (`1` to `0`) |

Comments, string and character literals and preprocessor lines are never edited, and binary operators only when
written with a space on each side, so template brackets, `->`, `<<` and `>>` stay as they are. A generated mutant's
id hashes its file, operator and line text, so it survives unrelated edits and can be listed as equivalent.

## Equivalents file

```yaml
equivalent:
  - id: clamp-low-equal
    reason: Clamp returns low for value == low on both paths, so < and <= cannot be told apart.
```

A plain mapping `id: reason` works too. An id that matches no mutant fails the listing, so the file cannot rot.

## Caller

```yaml
jobs:
  mutation:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-mutation.yml@v1
    permissions:
      contents: read
    with:
      level: high
      cmake_args: "-DMYLIB_BUILD_TESTS=ON"
      mutate_paths: "inc src"
      equivalents_file: docs/equivalent-mutants.yml
      shards: "2"
```

## Report

Survivors and broken mutants become annotations on their line. The run summary has the kill rate and a table of
every mutant that was not killed. The artifact holds `mutation-report.md`, `mutation-results.json` (every mutant with
its verdict) and `mutation-report.json` in the schema of
[mutation-testing-elements](https://github.com/stryker-mutator/mutation-testing-elements), whose HTML viewer opens it.
The outputs give the counts.

## Inputs

<!-- generated: inputs-ru-mutation -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `level` | string | `high` | Policy: high (100 % kill rate, no broken catalogue mutant) or standard (80 %) |
| `threshold` | string | empty | Kill-rate percentage that overrides the level's; empty uses the level's |
| `root` | string | `.` | Directory mutant file paths, mutate_paths, catalogues and the equivalents file are relative to |
| `mutate_paths` | string | `inc src include` | Space-separated folders or files whose C and C++ code generated mutants edit |
| `catalogue` | string | `tools/mutants/*.txt` | Space-separated globs of catalogue files (the drivers' tools/mutants format: "id \| file \| what", optional "= reason", "- old" and "+ new" lines) |
| `mode` | string | `auto` | auto (the catalogues when one exists, else generated), catalogue, generated or both |
| `equivalents_file` | string | empty | YAML or JSON of equivalent mutants (id -> reason, or a list of {id, reason}): reported, not run. A listed id that matches no mutant fails the run; a file that does not exist yet is a warning. |
| `source_dir` | string | `.` | CMake source directory, relative to root |
| `cmake_args` | string | empty | Configure arguments that build the tests (for example -DMYLIB_BUILD_TESTS=ON) |
| `build_target` | string | empty | Target built for each mutant; empty builds all |
| `ctest_args` | string | empty | Extra ctest arguments, e.g. -L unit to run only the fast tests |
| `compiler` | string | `gcc` | gcc or clang, the version of tools/misra/toolchain.json |
| `max_mutants` | string | `0` | Most mutants run (a stable sample by id); 0 runs every one |
| `shards` | string | `1` | Parallel jobs the mutants are split into |
| `workers` | string | `2` | Mutants built and tested at the same time in each shard (each in its own copy of the tree) |
| `build_parallel` | string | `2` | Jobs of each worker's cmake --build and ctest |
| `timeout_factor` | string | `3` | A mutant's tests time out after this many times the unedited tree's test time (at least 30 s) |
| `submodules` | string | `false` | actions/checkout submodules value: false, true or recursive |
| `enforce` | boolean | `true` | Fail the job by the level's policy; false reports only (the counts are in the outputs) |
| `timeout_minutes` | string | `120` | Timeout of each shard's job, in minutes |
| `artifact_name` | string | `mutation-report` | Name of the report artifact (unique per call when a run calls this more than once) |
<!-- /generated -->

## Jobs and permissions

<!-- generated: jobs-ru-mutation -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `plan` (mutants) | `contents: read` | `actions/checkout`; `actions/checkout`; Install PyYAML (pinned, hash-checked); List the mutants; `actions/upload-artifact` |
| `run` | `contents: read` | `actions/checkout`; `actions/checkout`; `actions/download-artifact`; Install the compiler (toolchain.json); Build and test every mutant of the shard; `actions/upload-artifact` |
| `report` (kill rate) | `contents: read` | `actions/checkout`; `actions/checkout`; `actions/download-artifact`; `actions/download-artifact`; Kill rate and report; `actions/upload-artifact` |
<!-- /generated -->

## Self-test

[`ci-mutation.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-mutation.yml) runs the
catalogue of `tests/fixtures/mutation` at level `high` (four killed, one equivalent) and its generated operators in
two shards with Clang (six killed, two survivors at the clamp bounds, reported with `enforce: false`), and checks
every count.
