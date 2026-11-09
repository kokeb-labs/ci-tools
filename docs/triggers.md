# Trigger policy

Which events may start a workflow in this repository and in the repositories made from the templates, and why.

## The rule

A workflow starts only from:

| Trigger | Runs in the context of |
| --- | --- |
| `push` | The pushed branch or tag |
| `pull_request` | The pull request's merge ref, with a read-only token for forks |
| `merge_group` | The merge queue's temporary branch |
| `workflow_call` | The caller's event: one of the rows above |

`release.yml` is the one exception: it starts from `workflow_run` when the self-CI finishes on `main`, and checks out
only the commit that self-CI tested.

Not allowed: `workflow_dispatch`, `schedule`, `pull_request_target`, `issue_comment`, `workflow_run` (outside
`release.yml`) and the other events that run in the default branch's context. To run a workflow again, use
**Re-run jobs** on its run; to run it on a branch, push the branch or open a draft pull request.

The self-CI enforces the rule: `.github/scripts/check_triggers.py` fails on any other trigger in
`.github/workflows/` or in a template's workflows.

## Why

A run started by one of those events executes in the context of the default branch. It can write the Actions cache
entries that every later run on `main`, and every release built from `main`, restores. If such a run executes code
it checked out by a computed ref, that code could leave a poisoned cache entry behind
([CodeQL `actions/cache-poisoning/poisonable-step`](https://codeql.github.com/codeql-query-help/actions/actions-cache-poisoning-poisonable-step/)).

Several workflows here must run code checked out by a computed ref: the handbook checker and the template drift
check run ci-tools' own scripts at the commit of the workflow (`job.workflow_sha`), and template drift runs
driver-template's scaffold at the caller's recorded version. Those refs are trusted, but neither CodeQL nor a
reviewer can tell that from the expression alone. Removing the privileged triggers removes the risk instead of
explaining it away: no run of these workflows can write the default branch's cache from code that a pull request
chose.

A manual trigger bought nothing a re-run does not give: every check already runs on each push and pull request.

## For callers

Repositories made from driver-template follow the same rule: their workflow files have no `workflow_dispatch`
either. An ESP-IDF clean build needs no manual input: the caches are keyed by IDF commit and source, and
`gh cache delete --all` empties them when a clean build is wanted.

## Code scanning: untrusted checkout

Code scanning runs `security-and-quality`, which includes `actions/untrusted-checkout/medium`. That query reports
every `actions/checkout` whose `ref:` names a ref, SHA or head in a workflow a pull request can start; it cannot
tell a pinned ci-tools or handbook commit from a pull request's branch. Every reusable workflow here checks out that
way by design, and what the query warns about (a self-hosted runner, a cache or artifact that a privileged workflow
later trusts) is ruled out by this trigger policy, GitHub-hosted runners, read-only tokens and
`persist-credentials: false`. `.github/codeql/codeql-config.yml` therefore excludes the medium variant, with this
reasoning, and keeps `actions/untrusted-checkout/high` (privileged triggers), which reports any regression.
