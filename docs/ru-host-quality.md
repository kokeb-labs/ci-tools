# ru-host-quality

Complexity, coverage and sanitizer gates for a CMake C/C++ project, with the limits the Kokeb Labs handbook sets
for each assurance level (ADR-0020).

`ru-host-quality.yml` runs three independent jobs:

| Job | Tool | Measures | Fails when |
| --- | --- | --- | --- |
| **complexity** | lizard 1.24.1 | Modified cyclomatic complexity (a whole `switch` counts once), lines of code and parameters of every function in `library_paths` | a function is over a limit |
| **coverage** | GCC 14 `--coverage`, gcovr 8.7 | Line, branch and, when the level asks for it, MC/DC coverage (`-fcondition-coverage`) of `library_paths` by the tests | a figure is below its floor |
| **sanitizers** | clang, AddressSanitizer and UndefinedBehaviorSanitizer | The tests built with `-fsanitize=address,undefined -fno-sanitize-recover=all` | any report, or a failing test |

Python tools are installed from pinned versions checked against their SHA-256 hashes, and each version was at
least three weeks old when it was pinned.

## Limits by level

| Limit | `standard` | `high` | `safety` |
| --- | --- | --- | --- |
| Cyclomatic complexity (modified) | 15 | 15 | 10 |
| Function length (lines of code) | 80 | 60 | 60 |
| Parameters | 7 | 6 | 6 |
| Line coverage | reported | 85% | 100% |
| Branch coverage | reported | 75% | 100% |
| MC/DC coverage | not measured | reported | 100% |

Every limit can be overridden with an input (`max_ccn`, `max_length`, `max_params`, `min_line`, `min_branch`,
`min_condition`); an override should match a waiver or deviation recorded in the repository.

## What is counted

- **Library code only.** `library_paths` (default `inc src`) names it. Tests, examples and tools are not measured
  for complexity and do not count towards coverage.
- **Every C and C++ file, header-only implementations included.** The complexity job lists `.c`, `.cc`, `.cpp`,
  `.cxx`, `.h`, `.hh`, `.hpp`, `.hxx`, `.ipp`, `.tpp` and `.inl` files under `library_paths` itself: lizard alone
  skips `.ipp`, `.tpp` and `.inl` files in a directory, which is where a header-only driver keeps its code.
- **Per source line, all template instances together.** A header-only driver is a class template, compiled once
  for every port type a test or example uses. gcovr's `--merge-lines` counts a line, branch or condition as covered
  when any instance ran it: coverage measures the source, as a structural-coverage objective does, not how many
  copies the compiler made. Without it, an example that instantiates the driver with its own port and runs only the
  happy path would count every failure path a second time, as uncovered.
- **Only code that ran.** Coverage reads the data of test binaries that executed. A compile-only target (for
  example an optimised build that exists to prove the code compiles at `-O2`) has no data and would otherwise count
  every line as missed.
- **No exception branches.** The compiler's exception-handling branches and unreachable branches are excluded:
  Kokeb code builds without exceptions.

## Minimal caller

```yaml
jobs:
  quality:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-host-quality.yml@v1
    permissions:
      contents: read
    with:
      level: high
      cmake_args: "-DMYCHIP_BUILD_TESTS=ON"
```

Add the job to the CI gate's `needs`. The reports (lizard's full table, gcovr's HTML, Cobertura XML and JSON
summary) are uploaded as artifacts, and the figures appear in the run summary.

## Outputs

`complexity_findings`, `line_coverage`, `branch_coverage` and `condition_coverage` let a later job record the
figures, for example in a release's evidence package.
