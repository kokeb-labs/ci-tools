# ru-attest-release

Sign build provenance for every file of a published release.

`ru-attest-release.yml` runs after [`ru-release`](ru-release.md) or
[`ru-release-with-artifacts`](ru-release-with-artifacts.md). It downloads the release's files, checks each against
the release's `SHA256SUMS`, and creates a
[GitHub artifact attestation](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations)
for every file that `SHA256SUMS` lists: an [SLSA](https://slsa.dev/) build-provenance statement, signed through
Sigstore and stored on the repository. Anyone can then check that a file they downloaded came from this
repository's release workflow at a given commit.

It is a separate workflow because it needs `id-token: write` and `attestations: write`. GitHub refuses to start a
called workflow when any of its jobs asks for more than its caller grants, so adding the job to the release
workflows would break their existing callers.

Attestations need a public repository, or GitHub Enterprise Cloud for a private one.

## Caller

Add a job after the release job, in the same workflow:

```yaml
jobs:
  release:
    # ... ru-release or ru-release-with-artifacts ...

  attest:
    needs: release
    uses: kokeb-labs/ci-tools/.github/workflows/ru-attest-release.yml@v1
    permissions:
      contents: read
      id-token: write
      attestations: write
    with:
      tag_name: ${{ github.ref_name }}  # or the tag the release job used
```

## Jobs and permissions

<!-- generated: jobs-ru-attest-release -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `attest` (Attest release files) | `attestations: write`, `contents: read`, `id-token: write` | Download the release files and check them against SHA256SUMS; Attest every file in SHA256SUMS |
<!-- /generated -->

## Inputs

<!-- generated: inputs-ru-attest-release -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `tag_name` | string | empty | Tag of the published release to attest (defaults to github.ref_name) |
<!-- /generated -->

## Check a download

```bash
gh release download v1.2.0 -R kokeb-labs/driver-as5047u -D v1.2.0 && cd v1.2.0
sha256sum -c SHA256SUMS
gh attestation verify as5047u-1.2.0.tar.gz -R kokeb-labs/driver-as5047u \
  --signer-workflow kokeb-labs/ci-tools/.github/workflows/ru-attest-release.yml
```

`gh attestation verify` checks that the file's digest was signed by this workflow, running for that repository,
and prints the commit and the workflow run. Repeat it for each file you use.

What it proves: the release workflow of the repository published these exact files at the tagged commit. The
firmware zips are built by `ru-build` in CI and released by `ru-release-with-artifacts` only after that CI run
passed on the tagged commit. The attestation is signed in the release job, not in the build job.

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `startup_failure` | The calling job does not grant `id-token: write` and `attestations: write` | Grant all three permissions on the `attest` job |
| `release ... has no SHA256SUMS` | The release was made by an older ci-tools, or by hand | Release with ci-tools 1.7.0 or later |
| `sha256sum: WARNING ... did NOT match` | A release file was replaced after it was published | Find out who changed it; publish a new release rather than attesting a changed one |
| `Feature not available` from the attest step | The repository is private on a plan without attestations | Make it public, or skip this job |
