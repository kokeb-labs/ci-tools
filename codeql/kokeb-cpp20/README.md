# kokeb/cpp20-queries

CodeQL queries for the Kokeb Labs C++20 profile: the handbook's own C++ rules (KB-CPP-*) that a query can
decide, run by [`ru-misra`](../../docs/ru-misra.md) next to the MISRA C++:2023 pack.

| Folder | Contents |
| --- | --- |
| `rules/<RULE>/` | One query per rule aspect. `@id kokeb/cpp20/<name>`, tagged `external/kokeb/id/<rule>` |
| `validation/<rule>[-aspect]/` | The validation case: `case.yml`, seeded violations `bad*`, compliant code `ok*` |
| `diagnostics/` | Queries ru-misra runs for its run-time assurance (files extracted, extractor errors), not rules |
| `codeql-suites/` | The default suite: every query under `rules/` |

## Adding a rule

1. Write `rules/KB-CPP-NNN/<Name>.ql` with `@kind problem`, `@id kokeb/cpp20/<kebab-name>` and the tags
   `external/kokeb/id/kb-cpp-nnn` and `external/kokeb/obligation/required|advisory`.
2. Add `validation/kb-cpp-nnn/` with `case.yml` (`guideline: KB-CPP-NNN`, `codeql: {queries: [...]}`), at least
   one `bad*` file with the violations and edge cases, and at least one `ok*` file with compliant code and near
   misses.
3. Run the suite locally (`tests/misra-validation/validate.py local ... --extra-pack codeql/kokeb-cpp20`) and add
   a requirement row to the validation record (`validate.py record`); the self-CI fails until the record matches.
