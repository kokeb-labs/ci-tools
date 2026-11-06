# ru-cpp-analysis

Run cppcheck over source folders, without a build, and keep the report as an artifact.

`ru-cpp-analysis.yml` runs cppcheck in a container (`ghcr.io/facthunder/cppcheck`) over `paths`. It needs no
compile database, so it suits header-only drivers and repositories without a host build; with a CMake build,
[`ru-host-ci`](ru-host-ci.md) runs cppcheck on the compiler's own database instead.

## What it does

1. Checks out the repository.
2. Runs cppcheck with `--enable=<enable>`, `--std=<std>`, inline suppressions, `-i` for each `exclude` path, and
   `--force` / `--max-configs` when set. `missingIncludeSystem` and `unmatchedSuppression` are suppressed, because
   system headers are not mounted.
3. Uploads `cppcheck_report.xml` and the console output as the `cppcheck-report` artifact (14 days).
4. With `strict: true`, fails the job when the report is not empty.

## Caller

```yaml
jobs:
  cppcheck:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-cpp-analysis.yml@v1
    permissions:
      contents: read
    with:
      paths: "src inc"
      std: c++20
      strict: true
```

## Jobs and permissions

<!-- generated: jobs-ru-cpp-analysis -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `cppcheck` | `contents: read` | `actions/checkout`; Install cppcheck; Run cppcheck; Upload report; Fail on findings (strict) |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-cpp-analysis -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `paths` | string | `src inc examples` | Dirs to analyze (space-separated) |
| `std` | string | `c++20` | C++ standard |
| `strict` | boolean | `false` | Fail the job when cppcheck reports a finding (severity other than information) |
| `exclude` | string | empty | Paths to exclude (space-separated) |
| `enable` | string | `warning,style,performance,portability,information` | Checks to enable (comma-separated: all,warning,style,performance, portability,information,unusedFunction,missingInclude) |
| `force` | boolean | `false` | Force checking even with incomplete analysis |
| `max_configs` | number | `0` | Maximum configs to check (for template-heavy code, 0=unlimited) |
| `artifact_name` | string | `cppcheck-report` | Name of the uploaded report artifact (unique per call when a run calls this more than once) |
<!-- /generated -->

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| The job passes although cppcheck printed findings | `strict` is `false` (the default) | Set `strict: true` once the findings are fixed |
| "Too many #ifdef configurations" | Template- or macro-heavy code | Set `max_configs`, or `force: true` |
| A path is not found | `paths` and `exclude` are relative to the repository root, space-separated | Check each folder exists in the checkout |
