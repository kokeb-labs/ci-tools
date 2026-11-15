# Language standards

Every Kokeb Labs driver declares the C++ standard it needs once, in the `language:` block of its `driver.yml`. The
organisation keeps the list of standards it accepts, and where each one stands, in
[`tools/standards/standards.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/tools/standards/standards.yml).
`tools/standards/check_standards.py` compares the two, and compares the declaration with the files that repeat it. A
driver that moves from one standard to the next changes the block, runs the checker and fixes what it lists.

## The registry

`standards.yml` lists profiles. A profile is a standard plus the handbook rules written for it (`KB-CPP20`:
handbook `rules/cpp20.yml`), the MISRA editions it may be analysed with, the CMake feature, the compiler flag and
the oldest compiler versions that support it.

| Status | Meaning | The check |
| --- | --- | --- |
| `current` | What a new driver is scaffolded with. Exactly one profile. | passes |
| `supported` | Older but accepted. A `supported_until` date is set when the end is planned. | note, with the profile to move to |
| `preview` | Being prepared; compiler floors and rules may still change. Never scaffolded. | warning |
| `retired` | Not accepted. A `supported_until` date that has passed counts as retired. | error |

`default` names the current profile and `next` the preview one. `python3 tools/standards/check_standards.py
--registry` checks the file itself (one current profile, ids match standards, every retired profile has a date,
compiler keys are known); the unit tests run it on every pull request.

## The declaration

```yaml
language:
  standard: 20               # the minimum ISO C++ standard: a consumer needs at least this
  profile: KB-CPP20          # a profile of standards.yml
  profile_version: "1.0"     # the handbook release that defines the profile
  misra: "MISRA C++:2023"    # the MISRA edition the driver is analysed against
  compilers:                 # the oldest versions the driver promises to build with, quoted
    gcc: "10"
    clang: "13"
  tested: [20]               # every standard CI compiles the headers under; includes `standard`
  effective_from: 2026-11-15 # the date this declaration took effect
```

## What the checker compares

```bash
python3 tools/standards/check_standards.py --repo path/to/driver [--today YYYY-MM-DD] [--require] [--base-ref origin/main]
```

| Code | Fails when |
| --- | --- |
| `LANG-001` | no `language:` block (a note, an error with `--require`; the registry default is assumed) |
| `LANG-002` | the block is malformed: a missing or unknown key, an unquoted compiler version, a bad date |
| `LANG-003` to `LANG-006` | the profile is unknown (error), retired (error), a preview (warning) or merely supported (note) |
| `LANG-007` to `LANG-009` | `standard`, `profile_version` or `misra` do not belong to the profile |
| `LANG-010` | a compiler key is unknown, or a promised version is below the profile's floor |
| `LANG-011` | `tested` is not a list of accepted standards that includes `standard` and none below it |
| `LANG-012` | `effective_from` is in the future or before the profile existed |
| `LANG-020` | `CMakeLists.txt` and `cmake/` never require the declared standard (`cxx_std_N`) |
| `LANG-021` | a file names another standard: `cxx_std_N`, `CMAKE_CXX_STANDARD`, clang-format `Standard`, a `__cplusplus ==` assertion, or a `-std=c++N` / `cppcheck_std` outside `tested` |
| `LANG-022` | a workflow's standard matrix differs from `tested` |
| `LANG-040` | with `--base-ref`: the minimum standard was raised, or a tested standard dropped, and `CHANGELOG.md` has no `### Breaking` entry |
| `LANG-030`, `LANG-031` | the README badge is missing (warning), or the badge, "a C++20 compiler" or "GCC 10+" (README and `docs/` pages) disagree with the block |

Build directories and `third_party/` are skipped; Markdown is read for badge, prose and compiler floors only, never for flags, and a line that names a `KB-CPP` rule is left alone. The checker needs
PyYAML. A repository whose `driver.yml` has no block still passes, with a note, so the check can be switched on before
every driver has the block.

The unit tests (`tools/standards/test_standards.py`) run in the `workflow-checks` job of the self-CI.
