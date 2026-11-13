# Chip diagrams

One file describes a chip's hardware; the pinout, the block diagram, the application circuits, the pin table and a
KiCad netlist are all drawn from it, so they cannot disagree.

## What a repository gets

A driver repository writes `docs/hardware.yml`. With the theme package installed it then has, with no figure
module or generator of its own:

| Output | Made by | Checked by |
| --- | --- | --- |
| `chip-pinout`: the package from the top, pins on their datasheet sides, pin 1 marked, coloured by type, each pin's port hook | `kokeb-docs figures` | `kokeb-docs figures --check` |
| `chip-outline`: the package body from above, to scale, with its pads, dimension arrows (length, width, pitch), a side view with the height, and a size label; only when `package.outline` is given | `kokeb-docs figures` | `kokeb-docs figures --check` |
| `chip-blocks`: the function blocks, their links and the pins that reach each block | `kokeb-docs figures` | `kokeb-docs figures --check` |
| `chip-circuit-<id>`: each reference circuit as a schematic, MCU wires labelled with the hook that drives them | `kokeb-docs figures` | `kokeb-docs figures --check` |
| `<!-- generated: chip-pins -->`: one row per pin with type, domain, function, hook, "if unused" and citation | `kokeb-docs gen` | `kokeb-docs gen --check` |
| `<!-- generated: chip-parts -->`: the parts of each circuit with their values and nets | `kokeb-docs gen` | `kokeb-docs gen --check` |
| `<!-- generated: chip-card -->`: the chip at a glance for the README: package, pin count, body size, pin pitch, supply range, and a table of the other packages it is sold in, each with its citation; a row the file does not give is left out | `kokeb-docs gen` | `kokeb-docs gen --check` |
| A KiCad netlist of a circuit, for a schematic or PCB tool | `kokeb-docs hardware --kicad-netlist OUT --circuit ID` | `kokeb-docs hardware --check` |

`kokeb-docs check`, which CI runs before every build, validates the file first and stops there when it is wrong,
then checks the figures and the regions. The figures are figkit figures: light and dark from one layout, contrast
checked in both, embedded with `<!-- figure: chip-pinout -->` like any other.

## The file

```yaml title="docs/hardware.yml"
schema: 1
chip: XMPL100
refs:                                   # named citations; every fact cites one
  pinout: {doc: ds, section: "3 Pin configuration", page: 3}
  spi: {doc: ds, section: "6.2 SPI interface", page: 8}
  app: {doc: ds, section: "9 Application information", page: 20}
  outline: {doc: ds, section: "10.1 Package outline", page: 24}
  order: {doc: ds, section: "11 Ordering information", page: 26}
  electrical: {doc: ds, section: "5 Electrical characteristics", page: 5}
package:
  type: SOIC-8
  pins: 8
  ref: pinout
  outline: {length_mm: 4.9, width_mm: 3.9, height_mm: 1.75, pitch_mm: 1.27, ref: outline}   # optional
  variants:                             # optional: the other packages the chip is sold in
    - {id: dfn, type: DFN-8, pins: 8, size: "3.0 x 3.0 x 0.8 mm", ordering: "XMPL100D", ref: order}
supply:                                 # optional: feeds the README chip card
  - {name: VDD, min_v: 1.8, max_v: 3.6, ref: electrical}
hooks:
  - {id: transfer, call: "Transfer()", kind: spi, source: inc/xmpl100_spi_interface.hpp, symbol: Transfer}
  - {id: reset, call: "GpioSet(CtrlPin::Reset)", kind: gpio-out, source: inc/xmpl100_spi_interface.hpp,
     symbol: Reset}
pins:
  - {number: 1, name: CS_N, type: bus, domain: VDD, function: "SPI chip select, active low", hook: transfer,
     ref: spi}
  # ... one entry per pin
block_diagram:
  ref: pinout
  blocks:
    - {id: spi, label: SPI interface, detail: "mode 0 or 3", at: [0, 0], pins: [CS_N, SCLK, SDI, SDO]}
  links:
    - {from: spi, to: regs, label: frames, both: true}
circuits:
  - id: typical
    title: Typical application
    ref: app
    parts:
      - {id: U1, kind: chip}
      - {id: U2, kind: mcu, label: MCU, pins: [{name: SCK, label: SPI SCK}, VDD, GND]}
      - {id: C1, kind: capacitor, value: 100 nF}
    nets:
      - {name: "+3V3", kind: supply, nodes: [U1.VDD, U2.VDD, C1.1]}
      - {name: GND, kind: ground, nodes: [U1.GND, U2.GND, C1.2]}
      - {name: SCLK, nodes: [U1.SCLK, U2.SCK]}
```

The template site's [`docs/hardware.yml`](../templates/mkdocs-site/docs/hardware.yml) is a complete example.

### Keys

| Key | Required | What it holds |
| --- | --- | --- |
| `schema` | yes | `1` |
| `chip` | yes | The part, as the docs name it |
| `documents` | no | `{id, name, pdf, page_offset}` per document; leave it out when `docs/datasheets.yml` lists them |
| `refs` | no | Named citations `{doc, section, page}`; `section` is the datasheet's own heading, `page` its printed page |
| `package` | yes | `type` (`SOIC-8`, `TSSOP-24`, `QFN-24`), `pins` (the exposed pad not counted), `exposed_pad`, `ref`; `layout` (`dual`, `quad`) is guessed from the type, vendor forms included (`PG-DSO-36`, `HTSSOP-28`, `HVQFN-24`, `TQFN-38`); `sides` lists the pins of each side counter-clockwise (left top to bottom, bottom left to right, right bottom to top, top right to left) for a package the layout does not describe (`SOT-23-5`) |
| `package.outline` | no | The body from the datasheet's package outline drawing: `length_mm` (the body edge pin 1 lies along, drawn as the left edge), `width_mm` (the other edge), `height_mm`, `pitch_mm` (the last two optional), `ref`; `height_ref` and `pitch_ref` when a value is cited elsewhere than the drawing (a mechanical-data table). All numbers are positive; the pins of a side must fit on its edge at the pitch |
| `package.variants` | no | The other packages the chip is sold in, from the ordering information: `id` (unique), `type`, `pins`, `size` (text, `"3.0 x 3.0 x 0.8 mm"`), `ordering` (the part-number suffix or code), `note`, `ref`; only `id`, `type` and `ref` are required |
| `supply` | no | The supply range or ranges: `name` (`VDD`), `min_v`, `max_v` (positive, `min_v` not above `max_v`), `ref`; shown on the chip card |
| `hooks` | yes | The port hooks a pin can map to: `id`, `call` (as the reader writes it), `kind` (`spi`, `i2c`, `uart`, `gpio-out`, `gpio-in`, `irq`, `other`); with `source` and `symbol` the check fails when the symbol is no longer in that header |
| `pins` | yes | One entry per package pin: `number` (or `EP` for the exposed pad), `name`, `type`, `domain` (the supply that sets its levels), `function`, `hook`, `unused` (what to do with it when unused), `ref` |
| `block_diagram` | no | `ref`, `blocks` (`id`, `label`, `detail`, `at: [column, row]`, `pins`, `tone`, `side`), `links` (`from`, `to`, `label`, `both`) |
| `circuits` | no | `id` (names the figure), `title`, `description`, `ref`, `parts`, `nets` (`name`, `kind`, `label`, `nodes`, `ref`, `hook`), `unused` |

Pin `type` is one of `power`, `ground`, `bus`, `digital-in`, `digital-out`, `digital-io`, `open-drain`, `analog`,
`power-out` (a load output) and `nc`; each has its own colour in the pinout, told apart in both themes. A part
`kind` is `chip` (the documented chip, exactly one per circuit), `mcu`, `ic`, `connector` (these list their
`pins`), or a two-pin part: `resistor`, `capacitor`, `polarized-capacitor`, `inductor`, `solenoid`, `diode`,
`zener`, `led`, `crystal`, `fuse`, whose pins are `1` and `2` (`A`/`K` and `+`/`-` work too). A net `kind` is
`signal` (the default), `supply` or `ground`. A node is `PART.PIN`; pins of the chip that share a name (GND on
several package pins) are one node.

A net may carry an optional `hook`: the id of a hook under `hooks`, which replaces the chip pin's own `hook` in that
one circuit's drawing and alt text (the pin table and the pinout keep the pin's hook). `hook: null` (or `""`) shows
no hook on that wire. A net without the key is unchanged. Use it when a circuit drives a pin another way than
the pinout says, for example a chip's SPI pins wired as a UART:

```yaml
hooks:
  - {id: transfer, call: "Transfer()", kind: spi}
  - {id: exchange, call: "Exchange()", kind: uart}
circuits:
  - id: uart
    nets:
      - {name: SWP, nodes: [U1.SWP, U2.TX], hook: exchange}   # labelled Exchange() here, Transfer() elsewhere
      - {name: NAO, nodes: [U1.NAO, U2.GND], hook: null}      # no hook label on this wire
```

Every pin, block, link, part or net may carry `unverified: <why>`: a fact that could not be confirmed in the
datasheet. The table gives it a footnote and the figures an asterisk with the reason under the figure, so a guess
never reads as a fact.

### What the check refuses

- A key the schema does not know, a missing required key, a value of the wrong type (with the path, e.g.
  `pins[3].type`).
- An outline with a number that is not positive, missing `length_mm`, `width_mm` or `ref`, a pitch that does not fit
  the pins on a side; a variant id listed twice or a variant pin count that is not a number; a supply range
  with `min_v` above `max_v`; any of these citing an unknown `ref`.
- A pin number listed twice, missing, or outside the package; an `EP` pin without `exposed_pad`.
- A fact without a citation, a citation of an unknown document, a page that is not a number.
- A pin or net whose `hook` is not under `hooks` (a net `hook` also needs a chip pin on the net); a hook whose `symbol` is not in its `source`.
- A block that names an unknown pin, two blocks in one cell, a link to an unknown block.
- A circuit node whose part or pin does not exist; a pin on two nets; a net with fewer than two nodes; a pin on no
  net that is not listed under `unused` (pins of type `nc` excepted).
- A figure with figkit problems: text under 4.5:1 contrast in either theme, overlapping text, text on any stroke of
  a symbol (a part, a supply or ground, a pin stub, a no-connect cross), a wire through a part or a label, a link
  line through another link's label, a pin drawn on the wrong side of the package. A block title word too wide for
  its card first breaks after a `/` or `-` and then shrinks; only a word that still does not fit is a problem.

## How the figures are drawn

The renderers are pure Python in the theme package (`kokeb_mkdocs_theme/hardware/`), with no dependency beyond
PyYAML, no network and no browser; the same file always gives the same bytes.

- **Pinout.** Pins counter-clockwise from pin 1, the way datasheets number them: on a dual package down the left
  and up the right, on a quad package also along the bottom and the top (names read bottom to top there).
- **Outline.** The pinout's pads, colours, legend and pin-1 dot, on a body drawn at one scale (about 300 px across,
  larger when a fine pitch needs it): a leaded package (SOIC, TSSOP, SOT, QFP) shows its leads reaching out of the
  body, a leadless one (QFN, DFN, LGA) its pads inside the edge. Pads are centred on each side at the stated pitch,
  an indication of where the pins are and not the land pattern, which the datasheet gives. The exposed pad is
  dashed and not sized. Arrows give the length, width and pitch; with `height_mm` a side view at the same scale
  gives the height. No `outline`, no figure.
- **Block diagram.** Blocks sit in the grid cells their `at` names; pins stand on the chip outline, left or right of
  their block. Links and pin wires are routed like the circuit's wires. Links into one face of a block share it out,
  each on the side toward its other end; a link label sits on its own line, or beside it, never on another line.
- **Circuit.** Parts are placed by their role, the way reference designs are drawn: supply pins up with their
  decoupling and supply symbol, ground pins down, MCU-facing pins on the left with the MCU level with them, pull-ups
  above the wires, loads in lanes to the right (each lane as tall as its parts and their labels draw), connectors at
  the far right. A part no pattern places goes in a row
  under the circuit. Supplies and grounds are symbols where they are used.
- **Router.** Every other wire is routed by A* on an 8 px grid: orthogonal, never through a part body or a label,
  crossings only at right angles and never at a bend, junction dots where three wires meet and never four. Bends
  and crossings cost extra; ties are broken in a fixed order.

## Export a circuit

```bash
kokeb-docs hardware --check                                      # what CI runs
kokeb-docs hardware --kicad-netlist typical.net --circuit typical
kokeb-docs hardware --svg /tmp/chip                              # the figures, light and dark, anywhere
```

The netlist is KiCad's export format (version `E`): KiCad's PCB editor imports it directly and most schematic and
PCB tools read it. Passive parts map to KiCad's `Device` library (`R`, `C`, `LED` ...); the chip, the MCU and other
ICs to a `kokeb` library part whose pins come from `pins`. A chip pin on no net is written the way KiCad writes an
open pin. There are no dates or time stamps, so the same circuit always gives the same file.

## Adopt it in a driver

1. Write `docs/hardware.yml`: the package and every pin from the datasheet's pin table, citing section and page;
   the hooks from the port header (`inc/*_interface.hpp`) with `source` and `symbol`; the blocks from the
   datasheet's block diagram; one circuit from its application section. Mark anything you could not confirm with
   `unverified`.
   The outline and the variants come from the datasheet's package outline drawing (chapter "Package", "Package
   outline" or "Mechanical data": the body in millimetres, the pitch, the height) and its ordering information
   (the package options and their part-number suffixes). Leave out a number the text does not give.
2. In `docs/hardware.md`, replace the hand-written pin table with `<!-- generated: chip-pins -->` and embed
   `<!-- figure: chip-pinout -->`, `<!-- figure: chip-blocks -->` and `<!-- figure: chip-circuit-<id> -->`, each
   closed by its end marker.
   In the README, under "At a glance", embed `<!-- figure: chip-pinout -->`, `<!-- figure: chip-outline -->` (when
   the file has an outline) and `<!-- figure: chip-blocks -->`, then add `<!-- generated: chip-card -->` for the
   table: the chip's module view without opening the docs.
3. Run `kokeb-docs hardware --check`, then `kokeb-docs figures && kokeb-docs gen`, and commit the SVGs,
   `docs/diagrams/figures.json`, `docs/diagrams/index.md`, the README and the page.
4. `kokeb-docs check` and `mkdocs build --strict` pass locally; CI then keeps them current.

Next: [Style guide](DOCS-STYLE-GUIDE.md#chip-hardware).
