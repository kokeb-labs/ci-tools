# Versioning and releases

Many repositories call these reusable workflows. When all of them used
`@main`, one bad commit here broke every one of them at once. Versioning
exists so that does not happen again.

## Scheme

- **Release tags** are immutable [semver](https://semver.org) tags:
  `v1.0.0`, `v1.1.0`, `v1.1.1`, and so on.
- **The moving major tag** (`v1`) always points at the newest `v1.x.y`
  release.
- **Callers pin the major tag**:

  ```yaml
  uses: kokeb-labs/ci-tools/.github/workflows/ru-cpp-lint.yml@v1
  ```

  They receive fixes and new optional inputs automatically, never a breaking
  change. A caller that needs to be fully reproducible can pin an exact tag
  (`@v1.2.0`) or a commit SHA.
- `@main` is the development line. Its first users are the self-tests in this
  repository.

## What is breaking

Anything that can make an existing, correct caller fail:

| Change | Why it breaks |
|--------|---------------|
| A reusable workflow removed or renamed | `uses:` no longer resolves |
| An input removed | Callers that pass it get `startup_failure` |
| An input's type changed | Callers that pass the old type get `startup_failure` |
| An input or secret made required, or a new required one added | Callers that do not pass it get `startup_failure` |
| An output removed | Callers that read it get empty values |
| A job needs a permission it did not need before | Callers that grant the old set get `startup_failure` |

A breaking change needs a **major** bump (`v1` → `v2`). It is listed under
`### Breaking` in [CHANGELOG.md](../CHANGELOG.md), under Unreleased or in the new version section.
On pull requests, the self-CI (`.github/scripts/check_contract.py`) compares
each `ru-*.yml` with the base branch. It fails if it finds one of these
changes and that heading is missing.

Everything else is a **minor** release (new workflow, new optional input,
new output) or a **patch** release (bug fix, action bump, documentation).

## Deprecating instead of removing

To retire an input within a major:

1. Keep declaring it, so callers that pass it keep starting.
2. Prefix its description with `Deprecated:` and say what replaces it.
3. Ignore it, or map it onto the replacement. When it is set, emit a
   `::warning::` that names the replacement.
4. List it under `### Deprecated` in the changelog.
5. Remove it in the next major, and list the removal under `### Breaking`.

## Releases come from the changelog

`CHANGELOG.md` decides what is released. Entries go under `## [Unreleased]` as usual. A pull request that should
reach callers also moves them to a new version section:

```bash
python .github/scripts/changelog.py bump patch   # or minor, or major
```

That writes `## [X.Y.Z] - YYYY-MM-DD` with the Unreleased entries under it. When the pull request merges,
`release.yml` tags `vX.Y.Z` on the merge commit, publishes the section as the GitHub Release notes and moves `vX`.
A pull request without a new section is merged without a release; its entries wait under Unreleased for the next
one. Callers pinned to `@v1` therefore get a fix as soon as a pull request asks for its release, and the changelog
and the releases never drift apart.

The self-CI (`changelog.py check`) fails a pull request whose new section is not the next patch, minor or major,
has no date or no entries, leaves entries under Unreleased, or has `### Breaking` without being a major. Two pull
requests that both add `1.0.6` cannot both merge: the second must be rebased and bumped again.

## Cutting a release by hand (maintainers)

A tag push still works, for a pre-release or to re-run a release:

1. Make sure `CHANGELOG.md` has the `## [X.Y.Z] - YYYY-MM-DD` section on `main`.
2. Tag the commit and push the tag:

   ```bash
   git tag -a v1.0.0 -m "v1.0.0"
   git push origin v1.0.0
   ```

3. `release.yml` then creates the GitHub Release, with the matching changelog section as notes (generated notes when
   there is none). If the
   tag is the highest `v1.*.*` release, it also force-updates `v1` to the
   same commit. A pre-release tag (`v1.1.0-rc.1`) gets a pre-release and
   leaves `v1` alone. A patch to an older minor does not move `v1` backwards.

The release workflow pushes `v1` with the workflow token. If a tag ruleset
protects `v*`, allow GitHub Actions to update it, or move the tag by hand.

## Re-runs use the old revision

**Re-run failed jobs** reruns the workflow at the revision the original run
resolved, including the revision of each reusable workflow. After a fix lands
here, or after `v1` moves, start a new run instead: push a commit, use
**Run workflow**, or close and reopen the pull request.

## Keeping callers current

Callers pinned to `@v1` need nothing more for minor and patch releases. For
majors, and for callers that pin exact tags or SHAs, Dependabot with
`package-ecosystem: github-actions` proposes the update, because it also
tracks `uses:` references to reusable workflows.

## Inside this repository

The workflows in this repository pin third-party actions to full commit SHAs
with a `# vX.Y.Z` comment. Dependabot (`.github/dependabot.yml`) keeps both
current.
