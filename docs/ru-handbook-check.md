# ru-handbook-check

Check a repository against the [Kokeb Labs handbook](https://kokeb-labs.github.io/handbook/) rules that a script can
decide, and report every finding by rule ID.

## The declaration

Each repository says what it is in `.kokeb/handbook.yml`:

```yaml
---
handbook: "1.0"        # the handbook release it follows
kind: driver           # driver, library, hal, firmware, tooling, docs or template
level: high            # standard, high or safety
waivers:               # optional
  - rule: KB-DOC-004
    reason: Doxygen comments for the v2 register API land with #41.
    approved_by: "@N3b3x"
    until: 2027-01-31
```

A rule applies when the repository's kind is in the rule's scope and its level is at or above the rule's lowest
level.

## What it checks

| Rule | Check |
| --- | --- |
| KB-REPO-002 | The declaration exists and names a handbook release, a kind and a level |
| KB-REPO-003 | Every waiver names a handbook rule, a reason, an approver and a date that has not passed |
| KB-REPO-005 | The root of a driver holds only the committed entries ADR-0011 allows |
| KB-REPO-018 | `driver.yml` has name, version, bus, mcus, peripheral and kb_core_min, matching `cmake/<chip>_build_settings.cmake` |
| KB-CPP-001 | The library requires C++20 and compiler extensions are not turned on |
| KB-BLD-002 | No `file(GLOB)` in CMake outside `tests/` and `examples/` |
| KB-CPP-002 | No `throw`, `try`, `catch`, `typeid` or `dynamic_cast` in `inc/` and `src/` |
| KB-CPP-003 | No `new`, `delete`, `malloc` and friends, or heap-owning smart pointers in `inc/` and `src/` |
| KB-ARCH-011 | No `virtual` in a driver (ADR-0016) |
| KB-CPP-012 | Driver headers include only the target library subset; other target code includes no allocating, throwing or OS header (ADR-0017) |
| KB-REPO-016 | No generated `sdkconfig` is committed (ADR-0018) |
| KB-DOC-035 | No PDF is committed under `docs/` (ADR-0019) |

Code checks read only committed files, with comments and string literals blanked out first, so a word in a
comment or a message never counts. `= delete` and placement `new` are not heap use.

## How a finding counts

- **Error** (fails the job): the rule is active, or its `enforce_from` date has passed.
- **Warning**: the rule is still proposed and its `enforce_from` date is ahead, or it is a *should* rule.
- **Notice**: a valid waiver covers the rule; the notice quotes the waiver.

Each finding is an annotation on its file and line with the rule's ID, title and a link to its page, and the run
summary has the full table.

## Where the rules come from

The checker and `rules.json`, a snapshot of the handbook's rules exported by the handbook's own tooling, live in
`tools/handbook_check/` in this repository. The workflow checks them out at its own commit, so a caller on `@v1`
always gets a checker and a rule set that belong together.

## Caller

```yaml
jobs:
  handbook:
    uses: kokeb-labs/ci-tools/.github/workflows/ru-handbook-check.yml@v1
    permissions:
      contents: read
```

Add the job to the CI gate's `needs`.
