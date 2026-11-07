# ru-cpp-lint

Check C and C++ formatting with clang-format and lint with clang-tidy, with results as annotations on the pull
request.

`ru-cpp-lint.yml` runs clang-format 20.1.8 and clang-tidy 20.1.0 with the repository's own `.clang-format` and
`.clang-tidy`. Both come from LLVM's builds published on PyPI, pinned and checked against their SHA-256, so no
install script or third-party action runs. With `cmake_args`, it configures the project first and gives clang-tidy
the CMake compile database, so clang-tidy sees the include paths and defines the compiler sees; without it,
clang-tidy guesses and cannot find the project's own headers. Every finding fails the job unless
`fail_on_findings` is false.

## What it does

1. Checks out the repository.
2. Links `clang_format_config` and `clang_tidy_config` to `.clang-format` and `.clang-tidy` at the root when they
   live elsewhere (the Kokeb Labs layout keeps them in `_config/`). A missing file is a warning, not an error.
3. Installs the pinned clang-format and clang-tidy.
4. Selects the files: `git ls-files` with `extensions`, without `ignore`, and only the files a pull request changes
   when `files_changed_only` is true.
5. With `cmake_args`, configures CMake with `CMAKE_EXPORT_COMPILE_COMMANDS=ON` into `build-clang-tidy/`.
6. Runs clang-format (`--dry-run -Werror`) and clang-tidy on every selected file in parallel. Each finding is an
   annotation on its line; the run summary has a table and the clang-tidy findings. Compiler warnings that
   clang-tidy echoes as `clang-diagnostic-*` are left to the build, except hard errors.
7. Fails when any file has a finding (`fail_on_findings`, default true). `findings` is the number of such files.

`thread_comments` and `lines_changed_only` are still accepted but ignored: whole files are always checked.

## Caller

```yaml
jobs:
  lint:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-cpp-lint.yml@v1
    permissions:
      contents: read
    with:
      clang_format_config: _config/.clang-format
      clang_tidy_config: _config/.clang-tidy
      files_changed_only: true
```

## Jobs and permissions

<!-- generated: jobs-ru-cpp-lint -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `lint` | `contents: read` | `actions/checkout`; Prepare clang configuration; Install clang-format and clang-tidy (pinned, hash-checked); Select files; Configure for clang-tidy (compile_commands.json); clang-format and clang-tidy; Fail on findings |
<!-- /generated -->

The job needs only `contents: read`: annotations come from the log, and nothing is posted to the pull request.

## Inputs

<!-- generated: inputs-ru-cpp-lint -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `clang_version` | string | `20` | Clang major version of clang-format and clang-tidy (20 is the supported version) |
| `clang_format_config` | string | `_config/.clang-format` | Path to clang-format configuration file |
| `clang_tidy_config` | string | `_config/.clang-tidy` | Path to clang-tidy configuration file |
| `tidy_checks` | string | empty | clang-tidy checks (comma-separated glob patterns, use - prefix to disable) |
| `extensions` | string | `c,cpp,cc,cxx,h,hpp,ipp,tpp,inl` | File extensions to check (comma-separated) |
| `ignore` | string | `build\|.git` | Files or directories to exclude from linting (pipe-separated) |
| `files_changed_only` | boolean | `false` | Only lint files that have been changed in the pull request |
| `lines_changed_only` | boolean | `false` | Deprecated, ignored: whole files are always checked, which is stricter. Kept so existing callers do not break. |
| `step_summary` | boolean | `true` | Add a summary of linting results to the workflow step summary |
| `file_annotations` | boolean | `true` | Display linting errors and warnings as file annotations in the GitHub UI |
| `thread_comments` | boolean | `false` | Deprecated, ignored: findings are reported as annotations and in the run summary. Kept so existing callers do not break. |
| `cmake_args` | string | empty | Arguments for a CMake configure that exports compile_commands.json for clang-tidy (for example "-DMYCHIP_BUILD_TESTS=ON"). Without a compile database clang-tidy cannot see the project's include paths and reports "file not found" for its own headers. Empty: no configure, no database. |
| `cmake_source_dir` | string | `.` | Directory with the top-level CMakeLists.txt for the cmake_args configure |
| `fail_on_findings` | boolean | `true` | Fail the job when clang-format or clang-tidy reports a finding. Set false to only report (the count is in the findings output). |
<!-- /generated -->

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| clang-tidy reports `file not found` for the project's own headers | No compile database | Set `cmake_args` so CMake exports one |
| Every line of a file is reported by clang-format | The config was not found, so the default style was used | Check the `clang_format_config` path; the log says which file was linked |
| clang-tidy reports missing headers | No compile database: include paths are guessed | Use [`ru-host-ci`](ru-host-ci.md) for clang-tidy, keep this for formatting |
| Findings in vendored code | The folder is not in `ignore` | Add it, pipe-separated: `build\|.git\|third_party` |
