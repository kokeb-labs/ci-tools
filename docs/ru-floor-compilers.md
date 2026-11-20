# ru-floor-compilers

Build and test a CMake project with the oldest compilers it promises to support (GCC 10 and Clang 13 by default),
each in a container pinned by digest.

The usual host job builds with the newest GCC and Clang on the runner, so a feature that only a newer compiler has
passes it. A driver declares the oldest compilers it supports in `language.compilers` of its `driver.yml`; this
workflow builds and tests the project with exactly those, so the promise is checked rather than assumed.

Each compiler runs in its own job and both always run. A job first checks that the image holds the compiler the
`driver.yml` promises (an image of another major version fails with a message that names both), then configures,
builds and runs `ctest`.

## Caller

```yaml
jobs:
  floor:
    name: Floor compilers
    uses: kokeb-labs/ci-tools/.github/workflows/ru-floor-compilers.yml@v1
    permissions:
      contents: read
    with:
      cmake_args: -DMYCHIP_BUILD_TESTS=ON
```

The project must configure with CMake 3.16 or newer as the images provide it (the Debian package). When
`language.compilers` names other majors, pass `gcc_image` and `clang_image` with matching images, each pinned by
digest.

## Jobs and permissions

<!-- generated: jobs-ru-floor-compilers -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `floor` | `contents: read` | Install the build tools; `actions/checkout`; The compiler is the declared floor; Configure; Build; Test |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-floor-compilers -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `source_dir` | string | `.` | CMake source directory, relative to the repository root |
| `cmake_args` | string | empty | Extra arguments for the configure step, space separated (for example -DMYCHIP_BUILD_TESTS=ON) |
| `build_type` | string | `Debug` | CMAKE_BUILD_TYPE |
| `gcc_image` | string | `gcc:10@sha256:19b31d0b2b263047b173e4e253d91f199d99c082973f13604d2913252c13309e` | Container image of the GCC floor, pinned by digest; its major version must equal language.compilers.gcc |
| `clang_image` | string | `silkeh/clang:13@sha256:1c2be5e37d8165ece17c18449f1a866633876c56cf286919d1c3e226e87a0449` | Container image of the Clang floor, pinned by digest; its major version must equal language.compilers.clang |
| `timeout_minutes` | number | `45` | Timeout of each compiler's job, in minutes |
<!-- /generated -->

## When to run it

Weekly, from the one scheduled workflow the [trigger policy](triggers.md) allows. A driver's
`weekly-floor-compilers.yml` is only this call:

```yaml
name: Weekly floor compilers
on:
  schedule:
    - cron: "17 4 * * 1"
  workflow_dispatch:
permissions: {}
jobs:
  floor:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-floor-compilers.yml@v1
    permissions:
      contents: read
    with:
      cmake_args: -DMYCHIP_BUILD_TESTS=ON
```

The file must keep this shape: the trigger lint fails a scheduled file with steps, secrets or more than
`contents: read`. A caller may also call the workflow from `push` or `pull_request` in a file of another name.
