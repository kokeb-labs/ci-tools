# ru-release

Create a GitHub Release with generated notes for a tag.

`ru-release.yml` creates the release with
[action-gh-release](https://github.com/softprops/action-gh-release) and `generate_release_notes: true`, so the
notes list the pull requests merged since the previous tag. It attaches a source archive with a stable checksum,
an SPDX 2.3 SBOM and `SHA256SUMS`, built by `tools/release_assets/release_assets.py`
([what each holds and how to check a download](ru-release-firmware.md#what-the-release-holds)). It attaches
no build artifacts; firmware repositories use [`ru-release-firmware`](ru-release-firmware.md).

## Caller

```yaml
on:
  push:
    tags: ["v*"]

jobs:
  release:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-release.yml@v1
    permissions:
      contents: write
```

## Jobs and permissions

<!-- generated: jobs-ru-release -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `release` (Create Release) | `contents: write` | Checkout code; Checkout the release asset script; Build source archive, SBOM and checksums; Create Release |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-release -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `draft` | boolean | `false` | Create as draft release |
| `prerelease` | boolean | `false` | Mark as pre-release |
| `tag_name` | string | empty | Tag name for release (defaults to github.ref_name) |
<!-- /generated -->

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| "Resource not accessible by integration" | The caller grants `contents: read` | Grant `contents: write` |
| `tag ... does not exist here` | The tag was not pushed, or `tag_name` names one that does not exist | Push the tag first; this workflow does not create tags |
| The release has the branch name as its tag | It ran on a branch push without `tag_name` | Trigger it on tags, or pass `tag_name` |
| Empty release notes | No pull requests since the previous tag | Expected; edit the release by hand if needed |
