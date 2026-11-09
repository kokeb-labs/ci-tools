# Tool validation plan

How the static-analysis toolchain behind the MISRA C++:2023 compliance matrix is validated for use under the quality
management system of an IEC 62304 Class C product, and how the evidence stays current.

## Purpose and scope

The [compliance matrix](https://github.com/kokeb-labs/handbook/blob/main/compliance/misra-cpp-2023.yml) says,
guideline by guideline, which tool decides it. A tool that decides a guideline replaces a reviewer for that
guideline. If the tool misses a violation, nobody else is looking. Every such claim therefore needs evidence that
the tool, in our configuration, does what the matrix says. This plan defines that evidence: its requirements, test
cases, acceptance criteria, records and re-validation.

In scope are the tools whose output is verification evidence for C++ code in drivers, libraries, HALs and firmware:

- compiler warnings
- clang-tidy
- cppcheck
- the CodeQL MISRA C++:2023 pack and our own C++20 profile pack
- the handbook checks
- the scripts of [`ru-misra`](../ru-misra.md) that run them

Compilers as code generators, debuggers and the documentation tools are out of scope.

## Governing expectations

| Source | What it asks of us | How this plan meets it |
| --- | --- | --- |
| ISO 13485:2016 §4.1.6, §7.5.6 (and §7.6) | Documented procedures to validate software used in the QMS, before first use and after changes, with effort proportionate to the risk of its use, and records | This plan; the suite in the repository; the [record](#records) re-made on every change; [re-validation](#re-validation) enforced by the self-CI |
| ISO/TR 80002-2:2017 | Critical thinking, intended use first, risk-driven choice of confidence-building activities, a validation plan and report, maintenance and change control | [Intended use](#intended-use-and-confidence-classification) per tool; scripted tests chosen by classification; the [report](#records) per release; change control through the record check |
| FDA, Computer Software Assurance for Production and Quality Management System Software (final, 3 February 2026) | Risk-based assurance: scripted testing where process risk is high; records of intended use, risk, tests, issues and conclusion | Process risk is high (a missed violation in Class C code), so every claim is tested by script and recorded; anomalies are logged with dispositions |
| FDA, General Principles of Software Validation (2002), §5.2.4, §5.2.5 | The most rigorous compiler error checking for the final build, warnings documented; test tools of a quality no less than the product they test | `-Werror` with the org warning set is checked in every translation unit; this validation |
| IEC 62304:2006+A1:2015, 5.1.4, 5.1.10, 5.1.12, 8.1 | Plan development tools; control supporting items such as tools and their settings; identify the defect categories of the language and show they do not lead to unacceptable risk; identify configuration items and versions | The toolchain is a controlled supporting item (`tools/misra/toolchain.json`, versions and hashes in the record). The matrix plus this validation are the evidence for 5.1.12. IEC 62304 has no tool-qualification clause of its own, so tool validation follows from ISO 13485 §4.1.6 |
| ISO 26262-8:2018 clause 11 | Classify tools by tool impact (TI) and tool error detection (TD) into a tool confidence level (TCL); qualify TCL2/TCL3 tools, for example by validation of the software tool (11.4.9) | Used as a recognised method for the [classification](#intended-use-and-confidence-classification); qualification by validation (method 1c) |
| MISRA Compliance:2020 §2.6.2–§2.6.5, §3.3–§3.5 | Justify trust in analysers and compilers; a test suite of violations; validate with the product's options and libraries; keep a known-defects list; know which guidelines each tool checks; a guideline enforcement plan with tool versions and configuration; investigate every message; no finding is not proof for undecidable guidelines | The suite seeds violations per guideline; it is compiled with the product's flags and libraries; the [anomaly log](https://github.com/kokeb-labs/ci-tools/blob/main/tests/misra-validation/anomalies.yml) is the known-defects list; the matrix is the guideline enforcement plan; undecidable guidelines keep review |

Sources:
- [ISO 13485:2016, reading copy](https://law.resource.org/pub/us/cfr/ibr/inc/iso/iso.13485.2016.pdf)
- [ISO/TR 80002-2:2017, public sample](https://cdn.standards.iteh.ai/samples/60044/b47e65ef109549eab8fa2d728bb591b4/ISO-TR-80002-2-2017.pdf)
- [FDA CSA guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software)
- [FDA General Principles of Software Validation](https://www.fda.gov/media/73141/download); its section 6 is superseded by CSA
- [IEC 62304 AMD1, public sample](https://cdn.standards.iteh.ai/samples/21252/f7905e39d6514a4da0bb6592596afd44/IEC-62304-2006-AMD1-2015.pdf)
- [ISO 26262-8 clause 11, public summary](https://www.synopsys.com/content/dam/synopsys/solutions/documents/automotive-tool-confidence-iso-26262-wp.pdf)
- [MISRA Compliance:2020](https://misra.org.uk/app/uploads/2021/06/MISRA-Compliance-2020.pdf)

The table paraphrases these sources. The licensed standards themselves are held by the maintainer.

## Intended use and confidence classification

Tool impact is TI2 for every tool here: each can fail to report a violation it is relied on to find. The tool error
detection (TD) column says how likely a tool error is to be caught later in our process. The method is ISO 26262-8
Table 3: TI2 with TD1 gives TCL1, with TD2 gives TCL2, with TD3 gives TCL3.

| Tool | Intended use | TD and reasoning | TCL | Confidence from |
| --- | --- | --- | --- | --- |
| GCC and Clang warnings, `-Werror` | Decide the guidelines the matrix assigns to a warning option, or to a hard error (exceptions, RTTI, preprocessor). | TD2: the warnings are front-end checks on syntax, and the CodeQL queries cover most of the same guidelines independently. | TCL2 | Validation of the tool (suite, every claim, GCC 14, Clang 18, Arm GNU 14.3); confidence from use |
| clang-tidy 20.1.0 | Decide the guidelines the matrix assigns to a check, with the CheckOptions the suite records. | TD2: most of these guidelines also have a CodeQL query. | TCL2 | Validation of the tool (suite); confidence from use |
| CodeQL 2.21.4 with `codeql/misra-cpp-coding-standards` 2.62.0 | Report violations of 175 guidelines. This decides the decidable translation-unit guidelines whose queries the suite proves, and is partial for the undecidable and system-scope ones. | TD3 for guidelines where it would be the only tool. The pack's own validation covers C++14/17 with gcc 8.4, clang 10 and qcc 8.3 only, not our C++20 and compilers. | TCL3 | Validation of the tool (suite with true positives, true negatives and near misses, both configurations); the vendor's test suite and qualification material for their configurations; the anomaly log |
| Kokeb C++20 profile pack (`codeql/kokeb-cpp20`) | Decide the handbook rules its queries implement (today KB-CPP-046). | TD3: no other tool checks these rules. | TCL3 | Validation of the tool (suite); review of every query |
| cppcheck (Ubuntu 24.04 archive) | Partial findings for guidelines the matrix maps to cppcheck message ids. It never decides a guideline. | TD1: every guideline it touches keeps review or another tool. | TCL1 | None needed; `ru-cpp-analysis` self-tests on known-bad fixtures |
| Handbook checks (`tools/handbook_check`) | Decide the forbidden-pattern rules the matrix names (exceptions, RTTI). | TD1: the compilers make the same constructs hard errors. | TCL1 | Unit tests in the self-CI |
| `ru-misra` scripts (`tools/misra/*.py`) | Install the pinned tools, apply the deviation records, merge results and apply the policy. A defect could hide findings. | TD2: the canary, the extraction checks, the fixture self-test and the unit tests catch silent failure. | TCL2 | Unit tests (`test_misra.py`), the fixture self-test with exact counts, run-time assurance in every scan |

A TCL2 or TCL3 tool decides a guideline only for the requirements that pass. A requirement recorded as an anomaly
does not decide anything. That aspect of the guideline keeps review, or the tool named in the anomaly's
disposition.

## Operating environment

The validated configuration is exactly what `tools/misra/toolchain.json` pins:

| Item | Version | Integrity |
| --- | --- | --- |
| CodeQL bundle (CLI and standard library) | 2.21.4, the CLI the pack's release supports | SHA-256 of `codeql-bundle-linux64.tar.zst` |
| `codeql/misra-cpp-coding-standards` | 2.62.0 | SHA-256 of the release archive and of the pack inside it |
| Deviation script `process_coding_standards_config.py` | tag v2.62.0, commit `6ac4b1d` | SHA-256 |
| clang-tidy | 20.1.0 (LLVM's PyPI wheel) | pip `--require-hashes` |
| PyYAML | 6.0.3 | pip `--require-hashes` |
| Arm GNU toolchain | 14.3.rel1 | SHA-256 Arm publishes |
| GCC 14, Clang 18, GCC 13 (`g++`, the CodeQL build compiler), cppcheck | Ubuntu 24.04 archive (signed) | Exact versions recorded at every run |
| Runner | `ubuntu-24.04` | Recorded in the validation report |

The compile flags of the validated configuration are the org warning set:
`-std=c++20 -Wall -Wextra -Wpedantic -Wshadow -Wundef -Werror -fno-exceptions -fno-rtti`. The Cortex-M
configuration adds `-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16`.

### Analysing compiled code

CodeQL's C/C++ extractor builds its database from the compiler invocations it traces. `build-mode: none` exists
for C/C++, as a preview from June 2025 and generally available since October 2025 in CLI 2.23.3. It infers the
translation units and flags from the files instead. GitHub's documentation says this may give less accurate
results, especially with macros or defines that are not in headers. The pack's user manual requires a clean, full
build of the code. Both sources:
[build options for compiled languages](https://docs.github.com/en/code-security/reference/code-scanning/codeql/build-options-for-compiled-languages)
and the [pack's user manual](https://github.com/github/codeql-coding-standards/blob/main/docs/user_manual.md).

**Decision.**

- **Only traced builds.** `ru-misra` and the suite analyse traced builds only, from a fresh build directory, with
  the real compiler command lines CMake writes to `compile_commands.json`. Build-mode none is not used.
- **Two configurations.** The preprocessor takes different paths per target, so every configuration the drivers
  ship is a separate database:
  - `host` (`g++`);
  - `cortex-m`: the Arm GNU toolchain with the cortex-m4f flags of `ru-cross-build`.
- **ESP-IDF not yet.** An ESP-IDF (Xtensa) configuration is not analysed yet; see the
  [limitations](#what-the-tests-cannot-prove).
- **Same compile databases for the other tools.** clang-tidy and cppcheck run on the same compile databases as the
  CodeQL scan.
- **Run-time checks.** The extraction checks prove at every run that each translation unit of the build, and each
  source file under the analysed paths, is in the database.

## Requirements

Each claim "tool T decides guideline G with rule id R" is a requirement with a stable id
`TV-<TOOL>-<GUIDELINE>-<NN>`, for example `TV-CQL-RULE-8-2-5-01`:

| Source of the claim | Requirements |
| --- | --- |
| The matrix's non-partial `compiler` entries | One per compiler (`GCC`, `CLANG`) and diagnostic; the GCC claim also for the cross GCC (`GCCARM`) |
| The matrix's non-partial `clang-tidy` entries | One per check (`TIDY`) |
| The pack's default suite | One per query of each applicable guideline (`CQL`), 221 queries for 175 guidelines, minus the not-applicable guidelines |
| The own profile pack | One per query (`CQL`, guideline `KB-CPP-NNN`) |

`validate.py record` derives the requirements from the matrix at the pinned handbook commit, from the pack's
supported list (`tests/misra-validation/codeql-supported.json`, read from the pinned pack's query metadata) and from
the profile pack. A new matrix claim is a new requirement, and it fails until a test proves it.

## Test cases

A test case is a directory under `tests/misra-validation/cases/` (or `codeql/<pack>/validation/`) with:

- **Seeded violations** (`bad*`): true positives, including the edge cases the guideline targets. Each seeded
  violation ends its line with `// seeded`, and every claimed tool must report on that line: a file that seeds
  three forms proves three detections, not one. `// seeded: codeql` (or another list of tools) limits a marker to
  the tools that report the form on that line. A bad file without a marker is a malformed case.
- **Compliant code** (`ok*`): true negatives, including near misses that must not be flagged. Every compliant file
  must build without a warning with the org flags on GCC and Clang. For the Cortex-M target it must also build with
  the cross GCC.
- **The exact rule id** in `case.yml`. That is the warning option, or the clang-tidy check name, or the CodeQL
  query id. A query's result must also carry the guideline's tag (`external/misra/id/rule-x-y-z`).

The snippets are our own. None is copied from the MISRA documents, whose text and examples are licensed. Each case was reviewed
against the guideline by a reviewer who did not write it (bad files violate in every seeded form, ok files comply,
near misses sit at the boundary); the review findings were fixed before the suite's first release. A CodeQL
query is shown on two databases per target, one of all seeded violations and one of all compliant files. Each is
built by a traced compile of each file. Both are analysed with the full default suites, so every result of every
query on compliant code is seen. A result of another query on a compliant file must be listed in the case's
`other_findings` with a reason. A false positive of the pack is recorded there as `misfire: ...` and in the anomaly
log. The suite runs on every pull request and every push to `main` (the self-CI, `ci-misra.yml`). It runs locally
with `tests/misra-validation/validate.py local`.

## Acceptance criteria

| Status | Meaning | Accepted when |
| --- | --- | --- |
| `pass` | On every target of every case of the requirement, the tool reports the rule id on every marked line of every seeded file and nothing on every compliant file, except recorded false positives (listed with the requirement) | Always |
| `anomaly` | A recorded false negative of the rule id in any case (or only recorded anomalies), with a log entry and a disposition. The rule id is then partial for the guideline | Only for pack and profile queries; the guideline keeps the mitigation the disposition names |
| `fail` | A test does not hold, or did not run on a target | Never |
| `no test` | No case for the requirement | Never |

**The self-CI fails** (`record --check`) when any of these holds:

- a matrix claim (compiler, clang-tidy) is not `pass`;
- a pack or profile query is `fail` or `no test`;
- a compliant file draws an unreviewed result;
- the anomaly log and the cases disagree;
- the committed record does not match the run.

## Records

| Record | Where | Content |
| --- | --- | --- |
| Validation record | `tests/misra-validation/validation-record.json`, committed | Hashes of the toolchain, suite and matrix; exact tool versions; every requirement with its tests, runs and status |
| Traceability | [traceability.md](traceability.md), committed | Requirement → tests → result; guideline → tools of the matrix, with what is validated |
| Validation report | `validation-report.md`, artifact `tool-validation` of every self-CI run, attached to each ci-tools release | Tool versions and hashes, results by tool, open problems, anomalies with dispositions, limitations, every test result |
| Anomaly log | `tests/misra-validation/anomalies.yml` | Every known false negative and false positive, how it was found, its disposition |

The report is the record an auditor reads. The release attaches the report of the self-CI run that released it.

## Re-validation

A change to any of these changes a validated tool or its configuration:

- `toolchain.json`
- the runner's compiler versions
- the compile flags
- a clang-tidy option
- a case
- a profile query
- `validate.py`
- the pinned handbook commit (the matrix)

Each of these changes the record: its hashes, its versions or its results. The record check then fails the self-CI
until the validation has run again and the regenerated record and traceability are committed from that run's
`tool-validation` artifact. A version bump therefore cannot merge without its validation evidence. An update of the
runner image that changes a compiler fails the self-CI the same way.

## Run-time assurance

Validation shows the tools work. Run-time assurance shows they worked on this scan:

- **Canary.** A file with known violations (`tools/misra/canary/ru_misra_canary.cpp`) is compiled into every
  database. If any of its expected query results is missing, the scan fails.
- **Extraction coverage.** Every translation unit of `compile_commands.json` must be in the database. So must every
  source file under the analysed paths, through some translation unit. An extractor error (severity 4 or 5) fails
  the scan.
- **Flags.** Each translation unit is checked for the org flags. At the safety level, a missing flag fails, because
  the compiler-decided guidelines would not be enforced.
- **Suppressions.** Every marker must cite a record and deviate a finding of that record's guideline.

## What the tests cannot prove

The [review checklist](review-checklist.md) covers what remains:

- Absence of violations of an undecidable guideline. Passing tests show detection of the seeded forms, not
  completeness.
- System-scope guidelines across a whole program, beyond the translation units of the analysed build.
- Code paths no analysed configuration compiles, today ESP-IDF (Xtensa).
- The guidelines no tool covers (Dir 0.3.2, and the review-only parts of others).

## Licence of CodeQL

The CodeQL CLI is licensed per user, and only for these purposes:

- academic research;
- demonstrating the software;
- testing OSI-licensed queries;
- analysis of an *Open Source Codebase*: a codebase released under an OSI-approved licence;
- for an Open Source Codebase hosted on GitHub.com, creating databases in automated analysis, CI or CD.

The License Restrictions exclude "any codebase that is not an Open Source Codebase". Their own example of such a
codebase is a private repository. Those restrictions do not apply under a paid GitHub Advanced Security licence
([terms](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md)). This repository is public and MIT,
so the suite runs here and locally. A private driver may not be analysed, in CI or locally, until it is public under
its OSI licence, or the organisation buys the licence. `ru-misra` enforces this before it downloads anything.

Next: [Traceability](traceability.md) · [Review checklist](review-checklist.md)
