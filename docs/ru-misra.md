# ru-misra

Check C++ code against MISRA C++:2023 with the validated open-source toolchain, and get a per-guideline report.

`ru-misra.yml` builds the caller twice, for the host and for a Cortex-M core, each time traced by CodeQL. It runs the
MISRA C++:2023 queries of the CodeQL coding-standards pack and the Kokeb C++20 profile pack on both databases. It
applies the handbook's deviation records, and runs clang-tidy's validated checks and cppcheck on the same compile
databases. Every tool comes from `tools/misra/toolchain.json` at the workflow's commit, pinned by version and
SHA-256. The [tool validation plan](tool-validation/plan.md) explains why each tool can be trusted for what it
decides.

!!! warning "Licence: open-source code only"
    The CodeQL Terms and Conditions license analysis of an *Open Source Codebase*, code released under an
    OSI-approved licence, and CI use when it is hosted on GitHub.com. Any other codebase needs a paid GitHub
    Advanced Security or Code Security licence. The first job passes a public repository with an OSI licence, a
    caller that states the paid licence (`advanced_security: true`), or a private repository that the caller
    declares an open-source pre-release (`open_source_prerelease: true`): its code is under the OSI licence in its
    LICENSE file and is to be published. That declaration is the caller's responsibility; the job prints it as a
    warning and the report stays in the run's artifact. Anything else fails before CodeQL is downloaded.

## Caller

```yaml
jobs:
  misra:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-misra.yml@v1
    permissions:
      contents: read
    with:
      level: safety
      cmake_args: "-DMYCHIP_BUILD_TESTS=ON"
      cross_build_target: mychip_optimised_build
```

`cmake_args` must build every translation unit that includes the code under `paths`. For a header-only driver, that
is the host tests. The scan fails if a header under `paths` is not included by any translation unit.

## What it does

1. **Licence and configurations.** The `plan` job checks the licence, then lists the configurations: `host`, and
   `cortex-m` unless `cross: false`.
2. **Deviation records.** It reads the project-wide records (`compliance/misra-cpp-2023-deviations.yml` of the
   handbook at `handbook_ref`) and the repository's own MISRA records (`docs/deviations.yml`, entries with
   `check: misra/<guideline>`). Each record becomes one entry of the pack's deviation configuration. Its code
   identifier is the record id and its `rule-id` is the record's guideline. A lapsed record (`review_by` passed)
   fails the scan.
3. **Traced build.** It configures from scratch with `compile_commands.json`. The host uses `g++` and the
   Cortex-M build uses `arm-none-eabi-g++` with `-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16`. It
   then builds under `codeql database create` and compiles the canary into the same database.
4. **Analysis.** It runs the pack's default suite, the profile pack and the pack's deviation suppression query,
   and writes the results as SARIF 2.1.0.
5. **Run-time assurance.** The scan fails when any of these holds:
    - a translation unit of the build is not in the database;
    - a source file under `paths` is in no translation unit;
    - the extractor reported an error;
    - the canary's known violations were not all reported.
6. **Other tools on the same compile database.**
    - **Build flags:** it checks that every translation unit builds with the flags the compiler-decided guidelines
      rely on.
    - **clang-tidy:** it runs each configuration the validation suite proved, mapped to its guidelines.
    - **cppcheck:** it maps the message ids the matrix lists to guidelines. These are partial tools.
7. **Report.** It merges the configurations into one report, with one row for each of the 179 guidelines. The
   report goes to the step summary, `misra-summary.json` (keyed by guideline), `misra-findings.csv` and one SARIF
   file per configuration, all in the `misra-report` artifact. The level's policy then decides whether the job
   fails.

## Deviations in the code

A finding is deviated only by a marker that cites a record. The pack's forms are accepted:

```cpp
// codeql::misra_deviation_next_line(MD-CPP-004)
return *reinterpret_cast<volatile std::uint32_t*>(address);  // codeql::misra_deviation(MD-CPP-003)
```

A bare record id at the start or end of a comment also counts, so the NOLINT that MD-CPP-003 already asks for
(`// NOLINT(cppcoreguidelines-pro-type-reinterpret-cast) MD-CPP-003`) deviates the CodeQL finding as well.
`codeql::misra_deviation_begin(...)` and `codeql::misra_deviation_end(...)` mark a range.

Any of these is a **suppression error**, and fails the scan at every level:

- a marker citing an id that is no record;
- a marker for another standard (`codeql::autosar_deviation`);
- a marker that deviates no finding of its record's guideline in any configuration (a stale or misdirected
  marker);
- a `NOLINT` or `cppcheck-suppress` comment that cites no record id;
- a committed `coding-standards.yml` (deviations come from the records only).

## Levels

| Level | Fails on |
| --- | --- |
| `high` | A finding of a mandatory or required guideline (our category) that no record deviates. Advisory findings are warnings |
| `safety` | Any finding no record deviates, and any translation unit built without the org flags (`-Wall -Wextra -Wpedantic -Wshadow -Wundef -Werror -fno-exceptions -fno-rtti`) |

Both levels fail on suppression errors, a lapsed record, a missing canary detection or incomplete extraction.

A rule the tool validation found reporting compliant code (a false positive in
`tests/misra-validation/anomalies.yml`, for example a query that misreads code in class templates) does not decide its
guideline alone. At the `high` level its findings are listed as **to review** in the summary and in
`misra-findings.csv` (with the anomaly ids), and do not fail the job; the reviewer checks each one (review checklist
R-FP), fixes a real one and needs no record for a false one. At the `safety` level they fail like any other finding.
A recorded false negative never weakens a rule's findings.
`enforce: false` reports only. The outputs carry the counts.

A guideline without findings is reported as `no findings`, which proves nothing for an undecidable guideline. Those
keep their review step (MISRA Compliance:2020 §3.5), as the [plan](tool-validation/plan.md) explains.

## Jobs and permissions

<!-- generated: jobs-ru-misra -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `plan` (licence and configurations) | `contents: read` | `actions/checkout`; `actions/checkout`; Install PyYAML (pinned, hash-checked); May CodeQL run on this repository?; Configurations |
| `scan` | `contents: read` | `actions/checkout`; `actions/checkout`; `actions/checkout`; `actions/cache`; Install the validated toolchain (toolchain.json, hash-checked); Tool versions; Scan; Upload the configuration's results |
| `report` (per-guideline report) | `contents: read` | `actions/checkout`; `actions/checkout`; `actions/download-artifact`; Install PyYAML (pinned, hash-checked); Report; Upload the report |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-misra -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `level` | string | `high` | Failure policy. high: a finding of a mandatory or required guideline (our category) that no record deviates fails, an advisory one warns. safety: any finding that no record deviates fails, and every translation unit must build with the flags the compiler-decided guidelines rely on. |
| `paths` | string | `inc src` | Folders whose code is checked, space-separated, relative to the repository root |
| `cmake_source_dir` | string | `.` | Directory with the top-level CMakeLists.txt |
| `cmake_args` | string | empty | Configure arguments that build every translation unit of the code under paths (for example -DMYCHIP_BUILD_TESTS=ON) |
| `build_target` | string | empty | Target of the host build; empty builds all |
| `cross` | boolean | `true` | Also analyse the Cortex-M build (cortex-m4f, the Arm GNU toolchain of toolchain.json), whose preprocessor paths differ from the host's |
| `cross_cmake_args` | string | empty | Configure arguments of the Cortex-M build; empty uses cmake_args |
| `cross_build_target` | string | empty | Target of the Cortex-M build (for example the driver's <chip>_optimised_build); empty builds all |
| `profile_pack` | boolean | `true` | Also run the Kokeb C++20 profile pack (codeql/kokeb-cpp20) of this workflow's commit |
| `repo_deviations` | string | `docs/deviations.yml` | The repository's own deviation records; entries with check: misra/<guideline> become code identifiers like the project-wide MD-CPP records |
| `handbook_ref` | string | `daec60fa62c5e418eb72a1bfb28c0937f536a751` | Commit of kokeb-labs/handbook whose compliance matrix and project-wide deviation records apply |
| `advanced_security` | boolean | `false` | Set true only if the organisation holds a paid GitHub Advanced Security or Code Security licence for this repository. Without it, CodeQL may run only on a public repository under an OSI-approved licence. |
| `open_source_prerelease` | boolean | `false` | Set true for a private repository whose code is released under the OSI-approved licence in its LICENSE file and is to be made public. CodeQL then runs and the job prints the declaration as a warning; the report stays in the run's artifact (nothing is uploaded to code scanning). |
| `enforce` | boolean | `true` | Fail the job by the level's policy. False reports only (the counts are in the outputs). |
| `artifact_name` | string | `misra-report` | Name of the report artifact (unique per call when a run calls this more than once) |
<!-- /generated -->

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| "CodeQL may not run on a private repository" | The repository is private, and neither `advanced_security` nor `open_source_prerelease` is set | Make the repository public under its OSI licence, declare it an open-source pre-release, or hold the licence and set `advanced_security: true` |
| "is under the analysed paths but no translation unit of this configuration includes it" | A header is not built by `cmake_args`, or not by the cross target | Build the host tests (`-D<CHIP>_BUILD_TESTS=ON`) and a cross target that includes every header |
| "the canary was not detected" | The build was not traced, or a pack did not run | Check the scan log; the build must run a real compiler, not a cache |
| "suppression marker deviates no finding" | The marker cites a record of another guideline, or the finding is gone | Remove the marker, or cite the record of the finding's guideline |
| "translation units build without -W..." (warning; error at `safety`) | The build does not use the org warning set | Add the flags to the targets (the driver template's `<CHIP>_ENABLE_WARNINGS`) |
| A scan takes more than 20 minutes | The CodeQL bundle and pack are downloaded | The archives are cached by toolchain hash; the second run restores them |

Next: [Tool validation plan](tool-validation/plan.md)
