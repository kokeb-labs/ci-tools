# Figures

<!-- Written by kokeb-docs figures from docs/diagrams/figures/*.py. Do not edit by hand. -->

Every figure on this site is drawn by a Python module from facts extracted from the code, so it is rebuilt,
not redrawn, when the code changes. CI runs `kokeb-docs figures --check` and fails when a
committed figure no longer matches the code. Each figure below lists the files it is drawn from.

## From push to release

<!-- figure: workflow-flow -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="workflow-flow.dark.svg">
  <img src="workflow-flow.svg"
    alt="Two-lane flow: on every push and pull request ru-build runs generate-matrix, build and size-report
    and uploads fw-* artifacts; on a version tag ru-release-firmware downloads those same artifacts and
    attaches them to a GitHub Release.">
</picture>
<!-- /figure -->

Figure module: [`docs/diagrams/figures/workflow-flow.py`](../../docs/diagrams/figures/workflow-flow.py)

Drawn from:

- `jobs` in [`.github/workflows/ru-build.yml`](../../.github/workflows/ru-build.yml)
- `jobs` in [`.github/workflows/ru-release-firmware.yml`](../../.github/workflows/ru-release-firmware.yml)
