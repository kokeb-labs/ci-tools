# Figures

<!-- Written by kokeb-docs figures from docs/diagrams/figures/*.py. Do not edit by hand. -->

Every figure on this site is drawn by a Python module from facts extracted from the code, so it is rebuilt,
not redrawn, when the code changes. CI runs `kokeb-docs figures --check` and fails when a
committed figure no longer matches the code. Each figure below lists the files it is drawn from.

## From description to generated code

<!-- figure: board-flow -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="board-flow.dark.svg">
  <img src="board-flow.svg"
    alt="Pipeline in three columns in which a board description is read by checks and then written out by
    emitters as generated files.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/board-flow.pipeline.yml`](../model/board-flow.pipeline.yml)

Drawn from:

- [`docs/model/board-flow.pipeline.yml`](../model/board-flow.pipeline.yml)

## A guarded bus access

<!-- figure: bus-access -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="bus-access.dark.svg">
  <img src="bus-access.svg"
    alt="Sequence of a guarded register read, in which the caller asks the handler, the handler takes the bus
    lock, calls the driver, and the driver returns the value through the port.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/bus-access.seq.yml`](../model/bus-access.seq.yml)

Drawn from:

- [`docs/model/bus-access.seq.yml`](../model/bus-access.seq.yml)

## Handler lifecycle and health

<!-- figure: handler-health -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="handler-health.dark.svg">
  <img src="handler-health.svg"
    alt="State machine of a handler with the states Unknown, Starting, Ready, Degraded, Faulted and
    Recovering, and the calls that move it between them.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/handler-health.state.yml`](../model/handler-health.state.yml)

Drawn from:

- [`docs/model/handler-health.state.yml`](../model/handler-health.state.yml)

## Channels per port

<!-- figure: heat-channels -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="heat-channels.dark.svg">
  <img src="heat-channels.svg"
    alt="Heat map of the number of channels each port offers for the ADC, PWM and timer peripherals, darker
    cells meaning more channels.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/heat-channels.matrix.yml`](../model/heat-channels.matrix.yml)

Drawn from:

- [`docs/model/heat-channels.matrix.yml`](../model/heat-channels.matrix.yml)

## Fault journal record and ring

<!-- figure: journal-layout -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="journal-layout.dark.svg">
  <img src="journal-layout.svg"
    alt="Layout of the 32-byte fault journal record in four rows of eight bytes, from the magic and version
    to the CRC-32, and a ring of eight slots in which the next append overwrites the oldest record.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/journal-layout.bytes.yml`](../model/journal-layout.bytes.yml)

Drawn from:

- [`docs/model/journal-layout.bytes.yml`](../model/journal-layout.bytes.yml)

## Include zones

<!-- figure: layers-zones -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="layers-zones.dark.svg">
  <img src="layers-zones.svg"
    alt="Zone graph of the include checker rules: handlers include interfaces, rtos, utils and drivers,
    interfaces include rtos and utils, and the MCU port and the RTOS backend may include SDK headers
    through boundary files only.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/layers-zones.graph.yml`](../model/layers-zones.graph.yml)

Drawn from:

- [`docs/model/layers-zones.graph.yml`](../model/layers-zones.graph.yml)

## Contract support by port

<!-- figure: port-capabilities -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="port-capabilities.dark.svg">
  <img src="port-capabilities.svg"
    alt="Matrix of which bus contracts each port supports, as native, adapted, planned or not applicable,
    with the published limit where there is one.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/port-capabilities.matrix.yml`](../model/port-capabilities.matrix.yml)

Drawn from:

- [`docs/model/port-capabilities.matrix.yml`](../model/port-capabilities.matrix.yml)

## A transfer against its deadline

<!-- figure: transfer-deadline -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="transfer-deadline.dark.svg">
  <img src="transfer-deadline.svg"
    alt="Timeline of one transfer in which the CPU prepares a buffer, the DMA engine moves it, the CPU
    completes it, and the whole transfer ends before its deadline.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/transfer-deadline.timeline.yml`](../model/transfer-deadline.timeline.yml)

Drawn from:

- [`docs/model/transfer-deadline.timeline.yml`](../model/transfer-deadline.timeline.yml)

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

## Which repositories call which workflows

<!-- figure: workflow-use -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="workflow-use.dark.svg">
  <img src="workflow-use.svg"
    alt="Matrix of the reusable workflow families of ci-tools against the calling repositories: every caller
    uses the gate and the organisation checks, kb-core and product repositories add host CI, and espidf-
    tools uses only the gate, docs and organisation checks.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/workflow-use.matrix.yml`](../model/workflow-use.matrix.yml)

Drawn from:

- [`docs/model/workflow-use.matrix.yml`](../model/workflow-use.matrix.yml)
