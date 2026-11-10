# kokeb-mkdocs-theme

The Kokeb Labs documentation theme for MkDocs, as one package: the `kokeb` theme, the `kokeb` plugin, figkit, the
`kokeb-docs` command and the pinned toolchain (mkdocs, mkdocs-material, mkdocs-awesome-nav, pymdown-extensions,
mike). Every Kokeb Labs documentation site builds with it; no site carries CSS, templates or hooks of its own.

```bash
pip install "git+https://github.com/kokeb-labs/ci-tools@v1#subdirectory=packages/kokeb-mkdocs-theme"
```

`ru-mkdocs-publish.yml` installs it from the same commit as the workflow, so `@v1` callers get the matching theme.

## A site

```yaml
site_name: TMC9660 Driver
site_description: One sentence.
repo_url: https://github.com/kokeb-labs/driver-tmc9660

theme:
  name: kokeb

plugins:
  - kokeb
  - search
  - awesome-nav
```

The plugin fills in `site_url` (`https://kokeb-labs.github.io/<repo>/latest/`; the root for an unversioned site), `repo_name`, `edit_uri`, copyright,
mike versioning, the Markdown extensions (admonitions, tabs, snippets from the repository root, Mermaid,
GitHub-style anchors, ...) and strict validation.

A site is versioned with mike unless it is the organisation site (`kokeb-labs.github.io`), or sets
`plugins: [{kokeb: {versioned: false}}]`; `KOKEB_DOCS_VERSIONED=true|false` overrides both (the publish
workflow sets it from its `versioning` input). An unversioned site has no version selector and its `site_url` is
the Pages root.

### Configuration outside the root

A repository that keeps tool configuration in `_config/` puts the site there with `docs_dir: ../docs`
(and `site_dir: ../site`, so a local build lands where it would with a root `mkdocs.yml`):

```yaml
# _config/mkdocs.yml
site_name: TMC9660 Driver
repo_url: https://github.com/kokeb-labs/driver-tmc9660
docs_dir: ../docs
site_dir: ../site
theme:
  name: kokeb
plugins:
  - kokeb
  - search
  - awesome-nav
```

The repository root is then the folder that holds `docs_dir`, not the folder of the configuration, so snippets,
repository links, figures and generated regions resolve as they would with a root `mkdocs.yml`. Build with
`mkdocs build -f _config/mkdocs.yml`; `kokeb-docs` finds `_config/mkdocs.yml` from anywhere in the repository
(or takes `-f _config/mkdocs.yml`), and the publish workflow takes `mkdocs_config: _config/mkdocs.yml`.

## What is in it

| Path | What |
| --- | --- |
| `kokeb_mkdocs_theme/theme/` | Theme (`extends: material`): `main.html`, header with the org crumb, footer, inline mark, `assets/kokeb/kokeb.css` (tokens for light and dark, typography, admonitions, code, tables, hero, cards, chip card, figures, Mermaid, focus), the Doxygen stylesheet, the root `404.html` |
| `kokeb_mkdocs_theme/plugin.py` | Defaults, Markdown extensions, validation, build-input exclusion, page checks |
| `kokeb_mkdocs_theme/hooks.py` | Repository links to GitHub, API links, figure embeds, raw-HTML rebase, image and alt-text gate |
| `kokeb_mkdocs_theme/figkit/` | Code-sourced SVG figures, light and dark from one layout, contrast-checked |
| `kokeb_mkdocs_theme/hardware/` | Chip pinout, block diagram and application circuits from `docs/hardware.yml`, the grid router, the KiCad netlist export |
| `kokeb_mkdocs_theme/gen.py`, `generators/` | `<!-- generated: name -->` regions; built in: `examples` (from `examples/*/app_config.yml`) |
| `kokeb_mkdocs_theme/screenshots.py` | Phone / desktop, light / dark screenshots of a built site |
| `kokeb_mkdocs_theme/publish.py` | `publish-root`: an unversioned site as the whole deployment branch |
| `tests/` | Unit tests (`python -m unittest discover -s tests`), run by the self-CI |

## Commands

```text
kokeb-docs [-f CONFIG] COMMAND        CONFIG: the site configuration (default: nearest mkdocs.yml or _config/mkdocs.yml)
kokeb-docs figures [--check] [ids]   build (or check) docs/diagrams/figures/*.py
kokeb-docs gen [--check|--list]      fill (or check) generated regions (built-in + tools/docs/generators/)
kokeb-docs hardware [--check]        validate docs/hardware.yml; --kicad-netlist OUT exports a circuit
kokeb-docs check                     all checks, as CI runs them
kokeb-docs screenshots SITE OUT      needs the [screenshots] extra and `playwright install chromium`
kokeb-docs pages SITE                the pages CI audits
kokeb-docs publish-root SITE         commit SITE as the whole deployment branch (unversioned sites)
```

## Brand

Indigo `#0E1726` (primary), teal `#2BB3A3` / `#0B7A72` (accent), ink `#0E1726`; dark surface `#0A111D`. Inter for
text and JetBrains Mono for code, bundled with the theme (`theme/assets/kokeb/*.woff2`, SIL Open Font License in
`FONTS-LICENSE.txt`), so no page loads a font from a third party. The mark is a five-point
star (kokeb) on the brand tile (`theme/assets/kokeb/mark.svg`, `wordmark.svg`, `favicon.svg`).
Every text colour is at least 4.5:1 on its background in both schemes; the ratios are noted in `kokeb.css`.

The palette is one block, section 0 of `assets/kokeb/kokeb.css` (`--kb-palette-*`); every other token reads it. A
new palette drops in there; the comment above the block lists the few files that repeat the colours because they
cannot read CSS custom properties (logo SVGs, the root 404 page, the Doxygen stylesheet, figkit).
