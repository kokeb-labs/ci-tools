# Documentation platform

The pieces every Kokeb Labs documentation site is built from, where each one lives, and how a repository uses them.

## The pieces

| Piece | Where | What it gives a repository |
| --- | --- | --- |
| Theme package | [`packages/kokeb-mkdocs-theme`](../packages/kokeb-mkdocs-theme/README.md) | `theme: kokeb` (brand, layout, components, light and dark), `plugins: [kokeb]` (Markdown dialect, validation, repository links, figures, page checks), figkit, the `kokeb-docs` command and the pinned toolchain |
| Publish workflow | [`ru-mkdocs-publish.yml`](ru-mkdocs-publish.md) | Strict build, drift checks, Doxygen under `api/`, offline link check, Lighthouse budget, screenshots, publish with mike or at the branch root |
| Template | [`templates/mkdocs-site`](../templates/mkdocs-site/mkdocs.yml) | The skeleton of a driver site; the self-CI builds it |
| Migration tool | [`tools/docs-migrate.py`](../tools/docs-migrate.py) | The mechanical move from Jekyll, with a `--check` dry run |
| Guides | [Migrating to MkDocs](MIGRATING-TO-MKDOCS.md), [Style guide](DOCS-STYLE-GUIDE.md) | The procedure, and what the pages contain |
| Chip diagrams | [`kokeb_mkdocs_theme/hardware`](chip-diagrams.md) | Pinout, block diagram, application circuits, pin table and KiCad netlist from one `docs/hardware.yml` |

A repository carries no CSS, templates, hooks or requirements file for its site. The workflow installs the theme
package from its own commit, so a caller pinned to `@v1` builds with the theme released in `v1`.

## A site in three files

```yaml title="mkdocs.yml"
site_name: TMC9660 Driver
site_description: One sentence on what this is.
repo_url: https://github.com/kokeb-labs/driver-tmc9660

theme:
  name: kokeb

plugins:
  - kokeb
  - search
  - awesome-nav
```

`docs/.nav.yml` orders the pages; `.github/workflows/ci-docs-publish.yml` calls the workflow
([Quickstart](quickstart.md#documentation)). The plugin fills in the rest: `site_url`, `repo_name`, `edit_uri`, the
Markdown extensions, strict validation and the version selector.

## Versioned and unversioned sites

| | Versioned (every repository) | Unversioned (the portal, `kokeb-labs.github.io`) |
| --- | --- | --- |
| Addresses | `https://kokeb-labs.github.io/<repo>/<version>/`, root redirects to `latest/` | `https://kokeb-labs.github.io/` |
| Push to `main` | Publishes `dev` (also `latest` until the first release) | Replaces the site on `gh-pages` |
| Tag `vX.Y.Z` | Publishes `vX.Y.Z`, moves `latest` | Nothing |
| Selector | Version selector in the header, banner on old versions | None |
| Set by | Default | `versioning: false` on the workflow; the plugin knows `<org>.github.io` by itself |

## The `kokeb-docs` command

| Command | Does |
| --- | --- |
| `kokeb-docs figures [--check]` | Builds (or checks) the figkit figures under `docs/diagrams/figures/` |
| `kokeb-docs gen [--check]` | Fills (or checks) `<!-- generated: name -->` regions; repository generators live in `tools/docs/generators/` |
| `kokeb-docs hardware [--check]` | Validates `docs/hardware.yml`; `--kicad-netlist OUT --circuit ID` exports a circuit, `--svg DIR` writes the chip figures anywhere ([Chip diagrams](chip-diagrams.md)) |
| `kokeb-docs check` | All three checks, as CI runs them: the hardware file first, then the figures (the chip figures included) and the regions |
| `kokeb-docs screenshots SITE OUT` | Phone and desktop screenshots, light and dark (needs the `[screenshots]` extra) |
| `kokeb-docs publish-root SITE` | Commits a built site as the whole deployment branch (unversioned sites) |

This site uses a generator itself: [`tools/docs/generators/workflows.py`](../tools/docs/generators/workflows.py)
writes the catalogue, the permissions table and every inputs and jobs table from the workflow files.

## Preview a site locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install "git+https://github.com/kokeb-labs/ci-tools@v1#subdirectory=packages/kokeb-mkdocs-theme"
mkdocs serve                       # http://127.0.0.1:8000
mkdocs build --strict -d /tmp/site # what CI runs
lychee --offline --include-fragments --index-files index.html --root-dir /tmp/site '/tmp/site/**/*.html'
```

## Sites that carry their own copy of the theme

A site that copied `overrides/`, a stylesheet under `docs/stylesheets/`, `tools/docs/` and `tools/figkit/` into
the repository moves onto the package like this:

1. Set `theme: {name: kokeb}` and `plugins: [kokeb, search, awesome-nav]`.
2. Delete the copies and `requirements-docs.txt`.
3. Change figure modules to `from kokeb_mkdocs_theme.figkit import Fig`.
4. Move repository-specific generators to `tools/docs/generators/`; they run under `kokeb-docs gen`.

Next: [Migrating to MkDocs](MIGRATING-TO-MKDOCS.md).
