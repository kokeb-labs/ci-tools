# ru-cmake-matrix

Configure, build and test a CMake project in many configurations at once: MCU x RTOS x preset, on the host, for Arm
cores and with ESP-IDF, with a bounded number of jobs.

`ru-cmake-matrix.yml` collects its configurations from three sources and runs each one in its own job:

1. `matrix`: a JSON list of entries.
2. `matrix_from`: a compatibility catalogue (`compat.yml`, as [`ru-catalog`](ru-catalog.md) writes it). Every
   distinct `mcu` and `rtos` of its drivers' `configs` becomes an entry named `<MCU>-<RTOS>`.
3. `mcus`, `rtoses` and `presets`: their cross product, named `<mcu>-<rtos>-<preset>`.

An entry's `mcu` and `rtos` reach CMake as `-D<mcu_variable>=<mcu>` and `-D<rtos_variable>=<rtos>`. An entry that
names no toolchain gets one from `mcu_toolchains` by its MCU (first matching pattern), else `toolchain`.

| Toolchain | Where it runs | Compilers | Tests |
| --- | --- | --- | --- |
| `host-gcc`, `host-clang` | the runner | the GCC and Clang of `tools/misra/toolchain.json` | ctest, JUnit report; install consumer |
| `arm-none-eabi` | the runner | the pinned, hash-checked Arm GNU toolchain of `toolchain.json`, flags of `core` | none (cross) |
| `esp-idf` | the ESP-IDF v5.5 container, pinned by digest (`esp_idf_image`) | ESP-IDF's toolchain file for `idf_target` | none (cross) |

Each job configures with Ninja and `CMAKE_EXPORT_COMPILE_COMMANDS`, builds `target` (or all) and, for host entries,
runs ctest. With `install_consumer`, a host entry is installed to a staging prefix and the consumer project is
configured against it (`CMAKE_PREFIX_PATH`, `-DMATRIX_ENTRY=<name>`), built and tested: the installed package works
through `find_package`.

## Entries

| Key | Meaning | Default |
| --- | --- | --- |
| `name` | Job name and artifact suffix; `A-Z a-z 0-9 . _ -`, unique | required |
| `toolchain` | `host-gcc`, `host-clang`, `arm-none-eabi`, `esp-idf` (`arm-none-eabi:<core>`, `esp-idf:<target>` also work) | from `mcu_toolchains`, else `toolchain` |
| `core` | `cortex-m0plus`, `cortex-m3`, `cortex-m4f`, `cortex-m7f`, `cortex-m33f` | `cortex-m4f` |
| `idf_target` | `esp32`, `esp32s3`, `esp32c3`, `esp32c6`, ... | `esp32` |
| `mcu`, `rtos` | Passed as the two CMake variables | none |
| `preset` | A configure preset of the project's `CMakePresets.json`; the build folder is the job's own | none |
| `cmake_args` | Configure arguments of this entry (the call's `cmake_args` follow them) | none |
| `source_dir`, `target`, `build_type` | Per entry | the call's `source_dir`, `build_target`, `build_type` |
| `test` | Run ctest; only for host toolchains | `run_tests` on the host, false otherwise |
| `consumer_args` | Configure arguments of the install consumer | none |

## Caller

```yaml
jobs:
  parts:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-cmake-matrix.yml@v1
    permissions:
      contents: read
    with:
      matrix: >-
        [{"name": "utils", "cmake_args": "-DMYLIB_PARTS=utils -DMYLIB_BUILD_TESTS=ON"},
         {"name": "rtos", "cmake_args": "-DMYLIB_PARTS=rtos -DMYLIB_BUILD_TESTS=ON"}]
      install_consumer: tests/install_consumer

  configurations:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-cmake-matrix.yml@v1
    permissions:
      contents: read
    with:
      matrix_from: catalog/compat.yml
      submodules: "true"
      artifact_prefix: cmake-matrix-catalogue
```

Add both jobs to the CI gate's `needs`. A call with no configuration (an empty catalogue, say) passes with a notice.
Two calls in one run need distinct `artifact_prefix` values only when they share entry names.

## Parallelism and caching

At most `max_parallel` configurations build at once (`strategy.max-parallel`), and each `cmake --build` and ctest
uses `build_parallel` jobs (default: the runner's processor count). Each configuration keeps its own ccache in the
Actions cache, keyed by toolchain and entry name; `ccache: false` turns it off. The Arm toolchain archive is cached
too and checked against its SHA-256 on every run, so a cache entry cannot change the compiler.

## Results

Compiler errors and warnings become annotations on the source line. The `matrix result` job writes one table to the
run summary and fails when a configuration failed or did not run. The `results` output (JSON: name, toolchain, mcu,
rtos, status, failed step, seconds, test counts) feeds [`ru-catalog`](ru-catalog.md)'s `results_json`. Each
configuration's artifact holds `result.json` and, when tests ran, `junit.xml`.

## Inputs

<!-- generated: inputs-ru-cmake-matrix -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | string | empty | JSON list of entries. Keys: name (required, unique), toolchain (host-gcc, host-clang, arm-none-eabi, esp-idf), core (arm-none-eabi), idf_target (esp-idf), mcu, rtos, preset, cmake_args, source_dir, target, build_type, test, consumer_args |
| `matrix_from` | string | empty | A compatibility catalogue (compat.yml, schema 1, as ru-catalog writes it): every distinct mcu and rtos of its drivers' configs becomes an entry, added to matrix |
| `mcus` | string | empty | Space-separated MCUs; with rtoses and presets their cross product is added to matrix |
| `rtoses` | string | empty | Space-separated RTOSes of the cross product |
| `presets` | string | empty | Space-separated CMake configure presets of the cross product (CMakePresets.json) |
| `mcu_toolchains` | string | `{"HOST": "host-gcc", "ESP32S3*": "esp-idf:esp32s3", "ESP32C3*": "esp-idf:esp32c3", "ESP32C6*": "esp-idf:esp32c6", "ESP32*": "esp-idf:esp32", "STM32F0*": "arm-none-eabi:cortex-m0plus", "STM32G0*": "arm-none-eabi:cortex-m0plus", "STM32F1*": "arm-none-eabi:cortex-m3", "STM32F7*": "arm-none-eabi:cortex-m7f", "STM32H7*": "arm-none-eabi:cortex-m7f", "STM32H5*": "arm-none-eabi:cortex-m33f", "STM32U5*": "arm-none-eabi:cortex-m33f", "STM32*": "arm-none-eabi:cortex-m4f"}` | JSON object: MCU name pattern (fnmatch, case-insensitive, first match wins) -> toolchain, toolchain:core or esp-idf:target, for entries that name an MCU but no toolchain |
| `mcu_variable` | string | `KB_MCU` | CMake cache variable an entry's mcu is passed as (-D<variable>=<mcu>); empty passes none |
| `rtos_variable` | string | `KB_RTOS` | CMake cache variable an entry's rtos is passed as; empty passes none |
| `toolchain` | string | `host-gcc` | Toolchain of an entry that names none and whose MCU matches no mcu_toolchains pattern |
| `source_dir` | string | `.` | CMake source directory of an entry that names none, relative to the repository root |
| `cmake_args` | string | empty | Configure arguments added to every entry, after the entry's own |
| `build_type` | string | `Debug` | CMAKE_BUILD_TYPE of an entry without a preset or build_type |
| `build_target` | string | empty | Target of an entry that names none; empty builds all |
| `run_tests` | boolean | `true` | Run ctest for host entries that do not set test |
| `no_tests` | string | `error` | What a tested entry with no tests is: error (default) or ignore |
| `ctest_args` | string | empty | Extra ctest arguments, e.g. -L unit |
| `install_consumer` | string | empty | A CMake project that uses the installed package through find_package: after each host entry's tests, the build is installed to a staging prefix and this project is configured (with CMAKE_PREFIX_PATH and -DMATRIX_ENTRY=<name>), built and tested. Skipped with a warning while it has no CMakeLists.txt. |
| `submodules` | string | `false` | actions/checkout submodules value: false, true or recursive |
| `max_parallel` | string | `4` | Most configurations built at the same time (strategy.max-parallel) |
| `build_parallel` | string | empty | Jobs of each cmake --build and ctest; empty uses the runner's processor count |
| `ccache` | boolean | `true` | Use ccache with a per-configuration Actions cache |
| `esp_idf_image` | string | `espressif/idf:v5.5.6@sha256:bf72fe7a15c22849a9a94147301165a545fb8905d97c176cf748e3e4614cac84` | Container image of esp-idf entries (pin it by digest) |
| `timeout_minutes` | string | `60` | Timeout of each configuration's job, in minutes |
| `artifact_prefix` | string | `cmake-matrix` | Prefix of the per-configuration artifacts (results, JUnit); distinct per call in one run |
<!-- /generated -->

## Jobs and permissions

<!-- generated: jobs-ru-cmake-matrix -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `plan` (configurations) | `contents: read` | `actions/checkout`; `actions/checkout`; Install PyYAML (pinned, hash-checked); Plan the configurations |
| `build` | `contents: read` | `actions/checkout`; `actions/checkout`; Restore the Arm GNU toolchain archive; Install the toolchain (toolchain.json); Restore the compiler cache; Configure, build and test ${{ matrix.entry.name }}; Upload the result and test report |
| `build-esp-idf` | `contents: read` | `actions/checkout`; `actions/checkout`; ESP-IDF version; Restore the compiler cache; Configure, build and test ${{ matrix.entry.name }}; Upload the result and test report |
| `report` (matrix result) | `contents: read` | `actions/checkout`; Download the results; Result of every configuration |
<!-- /generated -->

`contents: read` checks out the caller and this workflow's scripts and toolchain pins at the workflow's own commit.

## Self-test

[`ci-cmake-matrix.yml`](https://github.com/kokeb-labs/ci-tools/blob/main/.github/workflows/ci-cmake-matrix.yml)
builds `tests/fixtures/cmake-matrix` with host GCC (tests and the install consumer), host Clang through a preset,
an STM32F4 entry on the Arm toolchain and an ESP32/FreeRTOS entry in the ESP-IDF container, and the pairs of a
catalogue fixture; it checks the counts and the result of every entry.
