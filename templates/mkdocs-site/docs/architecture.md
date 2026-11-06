# Architecture

How the driver is built: hardware-agnostic core, communication interface, platform port.

<!-- Write this page to docs/DOCS-STYLE-GUIDE.md (page "Architecture"). -->

<!-- figure: driver-layers -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagrams/driver-layers.dark.svg">
  <img src="diagrams/driver-layers.svg"
    alt="Layer diagram: your application calls the hardware-agnostic driver, which sends transactions through
    the communication interface to the platform port you write, which drives the chip; only the port
    changes from one MCU to the next.">
</picture>
<!-- /figure -->
