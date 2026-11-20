# ADR 0001: the figure toolchain

The decision on how every published figure of the organisation is drawn, stored and checked.

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-11-14 |
| Applies to | `kokeb-mkdocs-theme` (figkit), every repository that publishes figures |
| Version | introduced in ci-tools 1.22.0 |

## Context

Figures were drawn three ways: figkit (Python, code-drawn SVG, light and dark from one layout, contrast checked),
Mermaid fences rendered in the reader's browser from a public CDN, and hand-placed boxes in figure modules. The
Mermaid pages need the network at view time, have no CI step that parses them, carry no accessible text, and cannot be
printed or opened offline. figkit had cards, edges, pills and notes, so state machines, sequences, timelines,
matrices, byte layouts and graphs had no code-drawn form. Its contrast check covered text only: the card outline token
was 1.54:1 and one tone's stripe 2.17:1, below the 3:1 that WCAG 2.x asks of a shape that carries meaning.

The requirements: one source of truth per figure; deterministic bytes on every platform; light and dark from one
layout; accessible text; fits a printed page; no network at build or view time; pinned tools; permissive licences;
checks that fail CI when a figure drifts or is broken; a procedure an agent can follow without touching the renderer.

## Decision

### 1. Toolchain

- **figkit is the one renderer of every published figure.** The new kinds (`state`, `graph`, `seq`, `timeline`,
  `matrix`, `bytes`, `pipeline`) live in `kokeb_mkdocs_theme.figkit.kinds`, in this repository, and drivers, ports and
  the core library consume them by tag like the existing kinds.
- **A figure has one source**: a generated fact file or a small model file `docs/model/<id>.<kind>.yml`. Nobody edits
  a generated SVG.
- **Graphviz `dot` is a build-time layout oracle only.** It places the nodes of the `state` and `graph` kinds and
  never draws. The result is a committed layout lock; a normal render never runs `dot`, and a Graphviz upgrade changes
  a figure only when someone runs `kokeb-docs figkit layout` and commits the new lock. The CI container carries a
  pinned Graphviz for that command and for an advisory job that reports where the pinned version would change a lock.
- **Edges are routed by figkit**, not taken from Graphviz: orthogonal runs with rounded corners, a slot for every run in
  a gutter, a proper loop on the side of a card for a self transition.
- **Palette versions.** `palette=1` is the palette of every figure written before this decision and its bytes do not
  change. `palette=2` fixes the non-text colours (`line`, `rail`, `stone.strong`) and adds the `status` family (`ok`,
  `warn`, `fail`, `na`, `planned`) and a five step `heat` ramp. The model kinds use palette 2. An existing figure opts in
  with `Fig(..., palette=2)`. Making palette 2 the default is a separate, versioned decision (a major release).
- **Adaptive output.** A model figure also writes `<id>.adaptive.svg`: one file whose colours are classes over custom
  properties for both themes. It follows the page theme (`data-theme`, Material's colour scheme, then the reader's
  preference), switches to system colours in forced-colors mode, and has no script and no `style=` attribute. An
  inline form without a style block exists for pages whose CSP forbids inline style.
- **Fonts in standalone files.** Text names Inter with fallbacks and layout comes from font metrics, so a missing font
  changes nothing but the glyph shapes. A figure may say `font: embed`: the standalone SVGs then carry a subset of
  Inter (the glyphs of that figure, WOFF2, weight axis kept), at most 25 KB. The subset is a committed lock like the
  layout (`kokeb-docs figkit font`), so rendering needs no font tooling and its bytes do not depend on a tool version.
  Inter is under the SIL Open Font License 1.1, which allows embedding and subsetting; the file carries the notice.
- **Wording.** Figures of stack use or path cost say "estimate, not a worst-case claim". No figure makes a safety
  claim.

### 2. Directory contract

| Path | What | Written by |
| --- | --- | --- |
| `docs/model/<id>.<kind>.yml` | The model of a figure: the only thing a person edits | a person, or `kokeb-docs figkit new` |
| `docs/diagrams/figures/<id>.py` | A figure module, for figures that read facts from code | a person |
| `docs/diagrams/<id>.svg`, `.dark.svg` | Light and dark SVG, as before | `kokeb-docs figures` |
| `docs/diagrams/<id>.adaptive.svg` | One SVG for both themes (model figures) | `kokeb-docs figures` |
| `docs/diagrams/<id>.table.html` | Table form of a data-heavy figure (`matrix`, `bytes`) | `kokeb-docs figures` |
| `docs/diagrams/<id>.layout.json` | The layout lock of a `state` or `graph` figure | `kokeb-docs figkit layout` |
| `docs/diagrams/<id>.font.woff2`, `.font.json` | The font subset lock, for `font: embed` | `kokeb-docs figkit font` |
| `docs/diagrams/figures.json`, `index.md` | The index and the figure catalogue | `kokeb-docs figures` |

Generated figures stay in `docs/diagrams/`, where every existing site already embeds them; moving them would break
every caller and is a major-version change, not part of this decision. All paths come from one module
(`kokeb_mkdocs_theme.paths` and `figkit.build`), so a later rename changes one place. A lock is committed; `figures
--check` fails when a lock is missing or was made from different inputs ("layout stale, run `kokeb-docs figkit
layout <id>`"), and when a committed output differs from a fresh build.

### 3. Mermaid policy

Mermaid is **not used**, on published pages or in `README.md` files: it does not render on phones and in mobile apps.
Every repository of the organisation was migrated to figkit figures, which are committed SVG that GitHub shows too.
`kokeb-docs check` runs `figures --lint --ban-mermaid`, so a `mermaid` fence or a `.mmd` file is an error; a site can opt
out with `extra: {no_mermaid: false}` in its configuration. The theme no longer loads Mermaid, ships no styles for it and
no longer registers the fence, so a stray fence shows as a plain code block. (Until release 1.26.0 the policy allowed
Mermaid in README files and kept an on-demand loader in the theme.)

### 4. Budgets

| Budget | Limit | Checked by |
| --- | --- | --- |
| One SVG | 60 KB (85 KB with an embedded font) | SVG lint |
| Embedded font subset | 25 KB per figure | `kokeb-docs figkit font` |
| Text on a printed page | at least 7 pt on A4 (content width 510 pt portrait, 757 pt landscape) | print fit |
| Text contrast | 4.5:1, both themes | figure build |
| Shape contrast (outline, arrow, stripe, mark) | 3:1, both themes (palette 2) | figure build |
| Time to render one figure | under 1 s; all fixtures under 10 s | test suite |
| `kokeb-docs figures --check` of a site with 50 figures | under 30 s, no network, no Graphviz | design limit |
| Re-layout of one figure | under 5 s (Graphviz), run on demand only | `figkit layout` |

### 5. Gates (in `kokeb-docs figures`)

Render and golden bytes (a committed file equals a fresh build), well-formed XML, SVG lint (`viewBox`, `role="img"`,
`<title>`, `<desc>`, no script or handler or `style=`, no external reference, ids prefixed with the figure id), alt
lint (one sentence of 40 to 300 characters, not "diagram of", the long description names every state or lane),
text and non-text contrast, print fit. Palette 2 figures fail the build on any of them; older figures see the same
findings as warnings with `--lint`, so no existing site breaks.

### 6. Tests and tools around it

axe-core (MPL-2.0) may be added to the configurator tests of a repository, unmodified, vendored with its hash and never
shipped. This decision does not add it.

## Consequences

- A figure of any of the seven kinds is a 20 to 60 line YAML file and one command. State machines, sequences and
  timelines no longer need Mermaid.
- Output bytes depend on Python and figkit only; macOS and Linux give the same hashes (verified in the self-CI test
  suite). Graphviz is needed on the machine that changes a layout, nowhere else.
- Every consumer of a new figkit release gets new kinds without changing what it already builds: existing figures are
  byte for byte the same (a test rebuilds a figure drawn with the original calls and compares it with bytes made by 1.21.0).
- A lock file is a reviewed diff. A change of node sizes or edges needs `kokeb-docs figkit layout`.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Mermaid CLI at build time | A headless browser (hundreds of MB of modules) in the docs build; one theme per run; layout from browser text measurement; no contrast or overlap checks |
| D2 | Good tool, one binary, light and dark built in; no contrast, overlap or alt checks; class names from hashes and mass diffs on upgrade. Kept as the fallback if the kinds slip |
| Graphviz as the renderer | No themes, no accessible text, output tied to the Graphviz version |
| PlantUML | Java, mixed licences, needs Graphviz anyway |
| Structurizr | Java; its C4 vocabulary is borrowed, the tool is not used |
| A new package | The kinds are generic and figkit already owns tokens, metrics and checks; a second package would duplicate them |
