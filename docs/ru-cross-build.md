# ru-cross-build

Compile a CMake target for microcontroller cores with the GNU Arm Embedded toolchain, so code that claims to run on
any MCU is shown to compile for one on every pull request.

`ru-cross-build.yml` runs one job per core in `cores`:

1. Installs `gcc-arm-none-eabi` with newlib and libstdc++ from Ubuntu's archive.
2. Writes a CMake toolchain file for the core (`-mcpu`, `-mthumb`, the float ABI and FPU) with
   `CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY`, so configuring needs no linker script.
3. Configures with that toolchain at `MinSizeRel` and builds **only** `build_target`. The project's own flags
   still apply: a Kokeb driver's test flags are `-fno-exceptions -fno-rtti -Werror` and the full warning set.
4. Writes the objects' `text`, `data` and `bss` sizes to the run summary.

| Core | Flags |
| --- | --- |
| `cortex-m0plus` | `-mcpu=cortex-m0plus -mthumb -mfloat-abi=soft` |
| `cortex-m3` | `-mcpu=cortex-m3 -mthumb -mfloat-abi=soft` |
| `cortex-m4f` | `-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16` |
| `cortex-m7f` | `-mcpu=cortex-m7 -mthumb -mfloat-abi=hard -mfpu=fpv5-d16` |
| `cortex-m33f` | `-mcpu=cortex-m33 -mthumb -mfloat-abi=hard -mfpu=fpv5-sp-d16` |

The default is `cortex-m0plus cortex-m4f cortex-m7f`: the smallest core without an FPU, and the two most common
cores with one.

## What to build

The target must compile code that instantiates the driver; a header-only `INTERFACE` library compiles nothing. A
Kokeb driver passes `<chip>_optimised_build`, the object library that compiles every test source, and with it every
operation of the driver against the mock port, at `-O2` with the strict flags. Nothing is linked, so no linker
script or startup code is needed.

## Caller

```yaml
jobs:
  cross:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-cross-build.yml@v1
    permissions:
      contents: read
    with:
      build_target: mychip_optimised_build
      cmake_args: "-DMYCHIP_BUILD_TESTS=ON"
```

Add the job to the CI gate's `needs`.
