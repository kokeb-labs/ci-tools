"""Chip hardware diagrams: one description of a chip's hardware (``docs/hardware.yml``), many outputs.

* ``model``   loads and validates the file (schema in its docstring and in ci-tools' ``docs/chip-diagrams.md``);
* ``render``  draws the package pinout and the block diagram as figkit figures;
* ``outline`` draws the to-scale package outline (``chip-outline``) from ``package.outline``;
* ``circuit`` places and routes a reference circuit as a schematic figure;
* ``router``  is the orthogonal grid router the figures use;
* ``symbols`` draws the schematic symbols;
* ``netlist`` exports a circuit as a KiCad netlist;
* ``cli``     is ``kokeb-docs hardware``.

The figures join the figkit build (``kokeb-docs figures``), the pin table the generated regions (``kokeb-docs gen``,
regions ``chip-pins``, ``chip-parts`` and ``chip-card``), and ``kokeb-docs check`` runs both plus ``kokeb-docs hardware --check``.
"""
