# Chip-first README

A driver README opens with the chip: what it is, what it does, where it is used, what is inside it and how it is
wired. Then come the shortest working code and how the driver covers each function. Readers already know how a
driver is layered, so the software architecture stays on the architecture page. Every part of the opening is
drawn or generated from `docs/hardware.yml`, so it is checked against the datasheet citations and the driver's
headers, and it is rebuilt rather than retyped when the facts change.

## The layout

| Order | Section | Content | Source |
| --- | --- | --- | --- |
| 1 | Title | `# <Chip> Driver` | hand-written |
| 2 | (under the title) | `<!-- generated: chip-summary -->`: "The **\<chip\>** is ..." with its citation | `overview.summary`, `overview.ref` |
| 3 | (under the title) | One line on the driver, the badges, the documentation link | hand-written |
| 4 | (under the title) | `<!-- figure: chip-hero -->`: the chip in its system and its headline numbers | `overview` |
| 5 | What it does | `<!-- figure: chip-capabilities -->`: one card per function, with an icon, a line, the driver's status and the registers behind it | `capabilities` |
| 6 | Where it is used | `<!-- generated: chip-uses -->`: the datasheet's applications | `overview.applications` |
| 7 | Inside the chip | `<!-- figure: chip-blocks -->` (the heading may say module, device, sensor or part; `overview.inside` fixes the word) | `block_diagram` |
| 8 | Pins and wiring | `chip-pinout`, `chip-wiring-<id>`, the wiring table, `chip-frame-<id>`, `chip-outline`, `chip-card` | `pins`, `circuits`, `frames`, `package` |
| 9 | Quick start | Wire, write the port, `<!-- generated: quickstart-code -->` (compiled by the host CI from `tests/docs/quickstart.cpp`) | the snippet file |
| 10 | Driver coverage | `<!-- generated: chip-coverage -->`, then the driver notes (paragraph, glance table, feature list) | `capabilities` |
| 11 | Documentation | The page table | hand-written |
| then | any order | Datasheet, Try it on your PC, Add it to your project, Tests and quality, License | as before |

`kokeb-docs readme --check` enforces rows 1, 2, 4 and 5 to 11 and refuses any figure in the README that is not a
chip figure (`chip-*`). `kokeb-docs check` runs it once `docs/hardware.yml` has an `overview`, so a repository opts
in by writing one. A repository without an `overview` gets no new figure and no new check. A chip with no wiring
figure (no MCU signal reaches it in any circuit) needs no `chip-wiring-<id>` under Pins and wiring.

## The site's home page

`docs/index.md` opens the same way, under the site's hero, so the README and the site home read alike:

| Order | Section | Content |
| --- | --- | --- |
| 1 | (hero) | `<div class="kb-hero" markdown>`: the kicker, `# <Chip> Driver`, one paragraph on the driver, the buttons |
| 2 | (under the hero) | `<!-- generated: chip-summary -->`, then any note (the template's scaffold note), then `<!-- figure: chip-hero -->` |
| 3 | What it does | `<!-- figure: chip-capabilities -->` |
| 4 | Where it is used | `<!-- generated: chip-uses -->` |
| 5 | Inside the chip | `<!-- figure: chip-blocks -->` (same word as the README) |
| 6 | Pins and wiring | `chip-pinout`, every `chip-wiring-<id>`, `chip-outline`, each `chip-frame-<id>`, the chip card (`kb-chip`), a pointer to the Hardware page |
| 7 | Quick start (optional) | "Wire the chip as above, write the port", `<!-- generated: quickstart-code -->`, a pointer to the Quickstart page |
| 8 | Driver coverage | `<!-- generated: chip-coverage -->`, then the driver paragraph ("The driver has no platform code ...") |
| then | any order | What you get, Datasheet, Where to go next (the navigation cards) |

`kokeb-docs readme --site --check` enforces rows 1 to 6 and 8, and refuses a figure other than a chip figure above
Driver coverage. `kokeb-docs check` runs it once `docs/index.md` has a `chip-summary` region, so a site opts in by
migrating its home page. `kokeb-docs readme --site --migrate` rewrites a template home page into this order: the
paragraph under the hero moves under Driver coverage, the chip card under Pins and wiring, a chip summary inside the
hero moves under it, and the other sections keep their order after Driver coverage. Quick start is added when the
README has the `quickstart-code` region.

## The figures

All four are figkit figures in the `overview` profile: read at README width (about 830 px) with no text under
11 px, light and dark from one layout, every text at 4.5:1 or better in both themes, every icon and pin stub at
3:1 against its fill, an SVG `<title>` and `<desc>` (the alt text), and the long description under `Reads:`. On top
of figkit's checks each runs the chip figures' geometry checks (no overlapping text, no wire through a body or a
text), and the wiring figure also refuses a label that runs onto a box.

| Figure | Shows | Drawn when |
| --- | --- | --- |
| `chip-hero` | The host and its bus, the chip drawn as its package (pin stubs on the package's sides, pin 1 marked), what it drives from left to right, what it reads back, and two to six headline numbers as tiles, each with its datasheet section and page | `overview` |
| `chip-capabilities` | A grid of cards: an icon, the function's name and one line, a filled pill for the driver's status and outlined pills for the registers behind it (the function-to-register map); a legend of the statuses used | `capabilities` |
| `chip-frame-<id>` | One bus transfer bit by bit: each frame row's fields with the first and last bit number, MSB first; optionally the SPI waveform (select, clock idling at CPOL with the sampling edge from CPHA, data lines carrying the fields) in the same bit grid, and a table naming each bit of one field | `frames` |
| `chip-wiring-<id>` | What a reader wires by hand: each MCU signal to its chip pin, coloured by pin type, with the net, the pin number, the driver hooks (one line each) and any part on the net or in series; a part between the MCU and the chip (a buffer, a transceiver, a level shifter, a load switch: any `ic` with an MCU wire on one side and a chip pin on the other, directly or through one series part; a load switch to a chip supply pin) as its own box with its wires in and out; the external blocks; then the supplies (a supply that reaches no chip pin names what it feeds), the support parts and the unwired pins in words. Long names are wrapped or ellipsised. The full schematic stays `chip-circuit-<id>` | each circuit in which an MCU signal reaches the chip, once there is an `overview`; `kokeb-docs figures` notes the others |

The icons (`kokeb_mkdocs_theme/hardware/icons.py`) are line drawings made here from simple strokes: `motion`,
`ramp`, `steps`, `home`, `load`, `stop`, `encoder`, `current`, `analog`, `chopper`, `power`, `coil`, `switch`,
`light`, `gate`, `gauge`, `temperature`, `axes`, `flow`, `alert`, `shield`, `check`, `clock`, `bus`, `chain`,
`memory`, `table`, `settings`, `key`, `lock`, `tag`, `sleep`. Pick the one that says what the function does for the
application.

## What a builder writes

Everything goes in `docs/hardware.yml`, after `supply` and before `hooks`. Each fact cites the datasheet with `ref`
(a key of `refs`); a fact you could not confirm carries `unverified: <why>` and is marked in the figure and the
table. Nothing is copied from the datasheet: write the facts in your own words and draw nothing by hand.

### `overview`

| Key | Required | What to write |
| --- | --- | --- |
| `summary` | yes | Completes "The \<chip\> is ...": what it is and what it does for a board, one sentence, no full stop |
| `category` | yes | The kind of part in a few words: the hero's kicker ("Stepper motor controller and driver") |
| `ref` | yes | Where the datasheet says it (its title page or features list) |
| `applications` | no | The datasheet's applications list, one short noun phrase each (a string, or `{label, detail, ref}`) |
| `applications_ref` | no | Where the list is, when that is not `ref` (an Applications section); the footer under the list cites it |
| `applications_inferred` | no | When the datasheet names no uses: what the list is inferred from ("the functions in the features list"); the footer then says "Uses inferred, not named by the datasheet" |
| `inside` | no | The word of the "Inside the ..." heading: `chip`, `module`, `device`, `sensor` or `part`; the README check then asks for it |
| `specs` | no | Two to six `{value, label, ref}`: the numbers a reader compares parts by (supply range, resolution, bus speed, current, package size); a `value` fits a tile, about 12 characters |
| `system.host` | no | What drives the chip, default `MCU` |
| `system.bus` | with `system` | The interface label on the host link ("SPI or UART", "I2C") |
| `system.drives` | no | Up to three `{label, detail, ref}`, chip to load ("MOSFET bridge", then "Stepper motor") |
| `system.senses` | no | `{label, detail, ref}` the chip reads back (a sensor element, an encoder, switches) |

### `driver` and `capabilities`

`driver.api` and `driver.registers` list the headers the names below must appear in (as whole words); give them
and the check fails when a call or a register named in the README no longer exists. `driver.kind: protocol` is for a
driver of a protocol rather than of one part (a CANopen client): the legend and the coverage table then speak of
the protocol ("the protocol defines it and the driver leaves it out", an Objects column), and every `supported`
capability names its host test under `tests`.

| Key | Required | What to write |
| --- | --- | --- |
| `id` | yes | A slug, unique |
| `title` | yes | The function's name as the datasheet names it |
| `icon` | yes | One of the icon names above |
| `what` | yes | What it does for the application, one line, 110 characters at most |
| `status` | yes | `supported`, `guarded` (covered behind an acknowledgement), `partial`, `read-only` or `not-covered` |
| `api` | unless `not-covered` | The driver calls that cover it, without parentheses (`MoveTo`, `Mode::StepDir`) |
| `registers` | no | The registers behind it, as the datasheet names them; the card shows three and a count, the table all. When the header spells one otherwise, write `{name: <datasheet name>, header: <constant>}`: the pill shows the name, the table both, and the check looks for the constant |
| `tests` | for a supported capability of a protocol driver | The host tests that check it: a file (`tests/test_sdo.cpp`) or a test case name, each checked to exist under `tests/`; the coverage table gains a Host test column |
| `docs` | no | The docs page that explains it (`motion.md`), linked from the coverage table |
| `ref` | yes | The datasheet section of the function |
| `note` | no | A short qualifier shown after `what` in the table |

Six to twelve capabilities read well: one per function a buyer looks for, including the ones the driver leaves
alone (`not-covered`), so the map is honest.

### `frames`

| Key | Required | What to write |
| --- | --- | --- |
| `id`, `title`, `bits`, `ref` | yes | `bits` is the frame length, 1 to 128 (a 72-bit TMCL datagram fits) |
| `bit_order` | no | `msb-first` (the default: SPI, the high bit sent first and drawn on the left) or `lsb-first` (a UART datagram: bit 0 sent first and drawn on the left, each byte least significant bit first; field `bits` are then `[first, last]`, listed from bit 0 up, as the datasheet numbers them; no waveform) |
| `description` | no | One sentence on what a transfer does |
| `rows` | yes | `{label, sub, fields}`; each field `{name, bits, tone, short}`, `bits` a bit (`39`) or `[high, low]`, listed from bit `bits - 1` down to 0 with no gap and no overlap; `short` when the name does not fit its bits |
| `decode` | no | `{row, field, ref, bits: [{bit, name}]}`, naming every bit of one field once |
| `waveform` | no | `{spi_mode, select, clock, lanes: [{name, row}]}`, a lane with no `row` drawn idle |

A frame is a fixed bit layout (SPI datagrams, a UART register frame); a variable-length protocol (I2C, Modbus)
draws one representative transfer, or none.

## Apply it to a driver

1. Write `overview`, `driver`, `capabilities` and `frames` in `docs/hardware.yml` from the datasheet
   (an hour or two per driver); `kokeb-docs hardware --check` lists every problem with its path.
2. `kokeb-docs readme --migrate` moves the README into the layout: the chip paragraph's driver half, the glance
   table (without its chip row) and the feature list land under Driver coverage, the wiring table under Pins and
   wiring, the layering figure leaves the README. A quick start under another heading ("In 30 seconds") is found by
   its wiring step or its `quickstart-code` region; a section the layout does not know keeps its place after
   Documentation. Nothing else is dropped.
3. `kokeb-docs readme --site --migrate` does the same for `docs/index.md`.
4. `kokeb-docs figures && kokeb-docs gen`, then read the README and the home page top to bottom and trim the driver
   notes.
5. Before the push: `kokeb-docs check`, `mkdocs build -f _config/mkdocs.yml --strict`, markdownlint with
   `_config/.markdownlint.json`, the offline link check, `python3 tools/check_standalone.py`.

## What CI checks

| Check | Where | What fails it |
| --- | --- | --- |
| `kokeb-docs check` | docs job, before the build | an invalid `hardware.yml` (unknown icon or status, an API or register missing from the headers, a frame with a gap), a stale figure or region, a README out of order |
| `mkdocs build --strict` | docs job | a broken page or link in the site |
| Link check (lychee, offline) | `ci-docs-linkcheck` | a README link or image path that does not resolve (the figures are committed under `docs/diagrams/`) |
| markdownlint | repository checks | a long paragraph line (the generated regions wrap at 120), a heading problem |
| Lighthouse budget | docs job, pull requests | the site pages below performance 0.8, accessibility 0.95, best practices 0.9, SEO 0.9 |
| Stand-alone check | repository checks | another project's name, a local path, a dated history line, a wrong copyright holder |

Next: [Chip diagrams](chip-diagrams.md) for the rest of `docs/hardware.yml`.
