# dco

Fail a pull request when any of its commits lacks a `Signed-off-by:` line that matches the commit's author.

`dco.yml` enforces the [Developer Certificate of Origin](https://developercertificate.org/) that every Kokeb Labs
repository asks of its contributors. It reads the pull request's commits through the GitHub API with
`actions/github-script`; it checks out nothing, so no code of the pull request runs.

## What it does

1. Lists the commits of the pull request (up to 250, the API's limit; a longer pull request fails with a message).
2. Skips merge commits (`skip_merge_commits`) and commits whose GitHub author is a bot (`allow_bots`).
3. Accepts a commit when one of its `Signed-off-by: Name <email>` trailers has the author's name and email,
   compared without case and with runs of spaces collapsed.
4. Fails with one error per commit and a table in the job summary: the commit, its subject, and the sign-off it
   has (or that it has none).

On an event without a pull request (a push, `merge_group`) it passes with a notice.

## Caller

```yaml
on:
  pull_request:

jobs:
  dco:
    uses: kokeb-labs/ci-tools/.github/workflows/dco.yml@v1
    permissions:
      contents: read
      pull-requests: read
```

Put it in the same workflow as the [CI gate](ru-ci-gate.md) and list it in the gate's `needs`, so the sign-off is
part of the one required check.

## Jobs and permissions

<!-- generated: jobs-dco -->
| Job | Permissions | Steps |
| --- | --- | --- |
| `dco` (DCO) | `contents: read`, `pull-requests: read` | Check the sign-off of every commit |
<!-- /generated -->

## Inputs

<!-- generated: inputs-dco -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `allow_bots` | boolean | `true` | Accept commits whose GitHub author is a bot account (type Bot, or a login ending in [bot]), such as Dependabot or github-actions, without a sign-off. |
| `skip_merge_commits` | boolean | `true` | Accept merge commits (more than one parent) without a sign-off; they add no authored change of their own. |
<!-- /generated -->

## When it fails

| Symptom | Cause | Fix |
| --- | --- | --- |
| `no Signed-off-by line` | The commit was made without `-s` | `git commit --amend -s` (last commit) or `git rebase --signoff <base>`, then force-push |
| `sign-off is ..., author is ...` | The trailer names someone else, or another email | Set `user.name` and `user.email` to the values in the trailer, or sign off again |
| `the API listed N of M commits` | More than 250 commits in one pull request | Split the pull request |
| `startup_failure` | The caller does not grant `contents: read` and `pull-requests: read` | Grant both on the calling job |
