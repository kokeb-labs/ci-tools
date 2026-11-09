# Traceability: requirement, tests, result

<!-- generated: traceability (tests/misra-validation/validate.py record --write); checked by the self-CI -->

Every claim that a tool decides a guideline is a requirement. Its tests are the case directories under `tests/misra-validation/cases/` (and `codeql/*/validation/`), run on the targets listed; the result is that of the recorded validation run. The [plan](plan.md) defines the statuses.

Toolchain `765756156ae0a2e6`, suite `afd51a2c4fde4b55`, pack `codeql/misra-cpp-coding-standards@2.62.0`.

## Summary

| Tool | pass | anomaly | fail | no test |
| --- | --- | --- | --- | --- |
| clang | 19 | 0 | 0 | 0 |
| clang-tidy | 34 | 0 | 0 | 0 |
| codeql | 149 | 63 | 0 | 0 |
| gcc | 20 | 0 | 0 | 0 |
| gcc-arm | 20 | 0 | 0 | 0 |
| handbook-check | 8 | 0 | 0 | 0 |

## Guideline to tools

The matrix's verification entries for each guideline, and the validation status of each tool the suite holds requirements for.

| Guideline | Matrix | Validated |
| --- | --- | --- |
| Rule 0.0.1 | codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 0.0.2 | codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 0.1.1 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: anomaly |
| Rule 0.1.2 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), handbook-check (partial), review | codeql: anomaly |
| Rule 0.2.1 | codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 0.2.2 | codeql, compiler, cppcheck (partial) | clang: pass, codeql: pass, gcc: pass, gcc-arm: pass |
| Rule 0.2.3 | codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 0.2.4 | codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Dir 0.3.1 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Dir 0.3.2 | commercial-checker, compiler (partial), review | - |
| Rule 4.1.1 | codeql (partial), commercial-checker, compiler (partial), handbook-check (partial), review | codeql: pass |
| Rule 4.1.2 | codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 4.1.3 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: anomaly |
| Rule 4.6.1 | codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 5.0.1 | codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 5.7.1 | codeql, compiler | clang: pass, codeql: pass, gcc: pass, gcc-arm: pass |
| Dir 5.7.2 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 5.7.3 | codeql, compiler | clang: pass, codeql: pass, gcc: pass, gcc-arm: pass |
| Rule 5.10.1 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 5.13.1 | codeql (partial), compiler | clang: pass, codeql: anomaly, gcc: pass, gcc-arm: pass |
| Rule 5.13.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 5.13.3 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 5.13.4 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 5.13.5 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 5.13.6 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 5.13.7 | commercial-checker, compiler (partial), review | - |
| Rule 6.0.1 | codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 6.0.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 6.0.3 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 6.0.4 | codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 6.2.1 | codeql (partial), commercial-checker, compiler (partial), handbook-check (partial), review | codeql: pass |
| Rule 6.2.2 | codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 6.2.3 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 6.2.4 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 6.4.1 | codeql (partial), compiler, cppcheck (partial) | codeql: anomaly, gcc: pass, gcc-arm: pass |
| Rule 6.4.2 | codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 6.4.3 | codeql, commercial-checker, review | codeql: pass |
| Rule 6.5.1 | codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 6.5.2 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 6.7.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 6.7.2 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: pass |
| Rule 6.8.1 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: anomaly |
| Rule 6.8.2 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: anomaly |
| Rule 6.8.3 | clang-tidy (partial), codeql, commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 6.8.4 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 6.9.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 6.9.2 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 7.0.1 | clang-tidy (partial), codeql (partial), commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 7.0.2 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: pass |
| Rule 7.0.3 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 7.0.4 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 7.0.5 | clang-tidy (partial), codeql (partial), commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 7.0.6 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 7.11.1 | clang-tidy, codeql, compiler (partial) | clang-tidy: pass, codeql: pass |
| Rule 7.11.2 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 7.11.3 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 8.0.1 | clang-tidy (partial), codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 8.1.1 | clang-tidy (partial), codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 8.1.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 8.2.1 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 8.2.2 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 8.2.3 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 8.2.4 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 8.2.5 | clang-tidy, codeql, review | clang-tidy: pass, codeql: pass |
| Rule 8.2.6 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 8.2.7 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: pass |
| Rule 8.2.8 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 8.2.9 | compiler, not-applicable | clang: pass, gcc: pass, gcc-arm: pass |
| Rule 8.2.10 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: pass |
| Rule 8.2.11 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: pass |
| Rule 8.3.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 8.3.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 8.7.1 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 8.7.2 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 8.9.1 | codeql (partial), commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 8.14.1 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 8.18.1 | codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: anomaly |
| Rule 8.18.2 | clang-tidy (partial), codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 8.19.1 | codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 8.20.1 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 9.2.1 | clang-tidy (partial), codeql, commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 9.3.1 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 9.4.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 9.4.2 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), handbook-check (partial), review | codeql: anomaly |
| Rule 9.5.1 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 9.5.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 9.6.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 9.6.2 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 9.6.3 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 9.6.4 | codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 9.6.5 | codeql, compiler, cppcheck (partial) | clang: pass, codeql: pass, gcc: pass, gcc-arm: pass |
| Rule 10.0.1 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 10.1.1 | clang-tidy (partial), codeql, commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 10.1.2 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 10.2.1 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 10.2.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 10.2.3 | codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 10.3.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 10.4.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 11.3.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 11.3.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 11.6.1 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 11.6.2 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 11.6.3 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 12.2.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 12.2.2 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 12.2.3 | codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 12.3.1 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 13.1.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 13.1.2 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 13.3.1 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: pass |
| Rule 13.3.2 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 13.3.3 | clang-tidy (partial), codeql (partial), commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 13.3.4 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 14.1.1 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 15.0.1 | clang-tidy (partial), codeql, commercial-checker, compiler (partial), cppcheck (partial), review | codeql: pass |
| Rule 15.0.2 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: pass |
| Rule 15.1.1 | clang-tidy (partial), codeql (partial), commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 15.1.2 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 15.1.3 | clang-tidy, codeql (partial), cppcheck (partial) | clang-tidy: pass, codeql: pass |
| Rule 15.1.4 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 15.1.5 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Dir 15.8.1 | clang-tidy (partial), codeql (partial), commercial-checker, cppcheck (partial), review | codeql: pass |
| Rule 16.5.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 16.5.2 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 16.6.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 17.8.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 18.1.1 | compiler, handbook-check, not-applicable | clang: pass, gcc: pass, gcc-arm: pass, handbook-check: pass |
| Rule 18.1.2 | compiler, handbook-check, not-applicable | clang: pass, gcc: pass, gcc-arm: pass, handbook-check: pass |
| Rule 18.3.1 | compiler, handbook-check, not-applicable | clang: pass, gcc: pass, gcc-arm: pass, handbook-check: pass |
| Rule 18.3.2 | compiler, handbook-check, not-applicable | clang: pass, gcc: pass, gcc-arm: pass, handbook-check: pass |
| Rule 18.3.3 | compiler, handbook-check, not-applicable | clang: pass, gcc: pass, gcc-arm: pass, handbook-check: pass |
| Rule 18.4.1 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 18.5.1 | compiler, handbook-check, not-applicable | clang: pass, gcc: pass, gcc-arm: pass, handbook-check: pass |
| Rule 18.5.2 | codeql, commercial-checker, review | codeql: pass |
| Rule 19.0.1 | commercial-checker, compiler (partial), review | - |
| Rule 19.0.2 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 19.0.3 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 19.0.4 | codeql, commercial-checker, review | codeql: pass |
| Rule 19.1.1 | codeql (partial), compiler | clang: pass, codeql: anomaly, gcc: pass, gcc-arm: pass |
| Rule 19.1.2 | compiler | clang: pass, gcc: pass, gcc-arm: pass |
| Rule 19.1.3 | codeql (partial), compiler | clang: pass, codeql: pass, gcc: pass, gcc-arm: pass |
| Rule 19.2.1 | codeql, commercial-checker, handbook-check | codeql: pass, handbook-check: pass |
| Rule 19.2.2 | codeql (partial), compiler | clang: pass, codeql: anomaly, gcc: pass, gcc-arm: pass |
| Rule 19.2.3 | codeql, commercial-checker, review | codeql: pass |
| Rule 19.3.1 | codeql, commercial-checker, review | codeql: pass |
| Rule 19.3.2 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 19.3.3 | codeql, commercial-checker, review | codeql: pass |
| Rule 19.3.4 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 19.3.5 | codeql, commercial-checker, compiler (partial), review | codeql: pass |
| Rule 19.6.1 | clang-tidy (partial), codeql (partial), commercial-checker, handbook-check | codeql: anomaly, handbook-check: pass |
| Rule 21.2.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 21.2.2 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 21.2.3 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 21.2.4 | codeql, commercial-checker, review | codeql: pass |
| Rule 21.6.1 | clang-tidy (partial), codeql (partial), commercial-checker, handbook-check (partial), review | codeql: anomaly |
| Rule 21.6.2 | clang-tidy (partial), codeql (partial), commercial-checker, handbook-check (partial), review | codeql: anomaly |
| Rule 21.6.3 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 21.6.4 | codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 21.6.5 | codeql, compiler | clang: pass, codeql: pass, gcc: pass, gcc-arm: pass |
| Rule 21.10.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 21.10.2 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 21.10.3 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 22.3.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 22.4.1 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 23.11.1 | clang-tidy (partial), codeql, commercial-checker, review | codeql: pass |
| Rule 24.5.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 24.5.2 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: anomaly |
| Rule 25.5.1 | clang-tidy, codeql | clang-tidy: pass, codeql: pass |
| Rule 25.5.2 | clang-tidy, codeql (partial), commercial-checker | clang-tidy: pass, codeql: anomaly |
| Rule 25.5.3 | clang-tidy, codeql (partial), commercial-checker | clang-tidy: pass, codeql: anomaly |
| Rule 26.3.1 | codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 28.3.1 | codeql (partial), commercial-checker, review | codeql: pass |
| Rule 28.6.1 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 28.6.2 | clang-tidy (partial), codeql (partial), commercial-checker, review | codeql: anomaly |
| Rule 28.6.3 | clang-tidy (partial), codeql (partial), commercial-checker, cppcheck (partial), review | codeql: anomaly |
| Rule 28.6.4 | clang-tidy (partial), codeql (partial), commercial-checker, compiler (partial), review | codeql: anomaly |
| Rule 30.0.1 | clang-tidy, codeql (partial) | clang-tidy: pass, codeql: pass |
| Rule 30.0.2 | codeql (partial), commercial-checker, cppcheck (partial), review | codeql: anomaly |

## Requirements

| Requirement | Guideline | Tool | Rule id | Tests | Result |
| --- | --- | --- | --- | --- | --- |
| TV-CQL-RULE-0-0-1-01 | Rule 0.0.1 | codeql | `cpp/misra/unreachable-statement` | `rule-0-0-1`<br>`rule-0-0-1-hook` | pass (AN-128) |
| TV-CQL-RULE-0-0-2-01 | Rule 0.0.2 | codeql | `cpp/misra/invariant-condition` | `rule-0-0-2`<br>`rule-0-0-2-hook` | pass (AN-129) |
| TV-CQL-RULE-0-1-1-01 | Rule 0.1.1 | codeql | `cpp/misra/unnecessary-write-to-local-object` | `rule-0-1-1`<br>`rule-0-1-1-member` | anomaly (AN-082, AN-135) |
| TV-CQL-RULE-0-1-2-01 | Rule 0.1.2 | codeql | `cpp/misra/unused-return-value-misra-cpp` | `rule-0-1-2`<br>`rule-0-1-2-niebloid` | anomaly (AN-083, AN-084) |
| TV-CQL-RULE-0-2-1-01 | Rule 0.2.1 | codeql | `cpp/misra/unused-limited-visibility-variable` | `rule-0-2-1`<br>`rule-0-2-1-member` | pass |
| TV-CLANG-RULE-0-2-2-01 | Rule 0.2.2 | clang | `-Wunused-parameter` | `rule-0-2-2` | pass |
| TV-GCC-RULE-0-2-2-01 | Rule 0.2.2 | gcc | `-Wunused-parameter` | `rule-0-2-2` | pass |
| TV-GCCARM-RULE-0-2-2-01 | Rule 0.2.2 | gcc-arm | `-Wunused-parameter` | `rule-0-2-2` | pass |
| TV-CQL-RULE-0-2-2-01 | Rule 0.2.2 | codeql | `cpp/misra/unused-parameter-misra-cpp` | `rule-0-2-2` | pass |
| TV-CQL-RULE-0-2-3-01 | Rule 0.2.3 | codeql | `cpp/misra/unused-type-with-limited-visibility` | `rule-0-2-3` | anomaly (AN-085) |
| TV-CQL-RULE-0-2-4-01 | Rule 0.2.4 | codeql | `cpp/misra/unused-limited-visibility-function` | `rule-0-2-4`<br>`rule-0-2-4-template` | pass (AN-138) |
| TV-CQL-DIR-0-3-1-01 | Dir 0.3.1 | codeql | `cpp/misra/possible-misuse-of-infinite-floating-point-value` | `dir-0-3-1-infinity` | anomaly (AN-081) |
| TV-CQL-DIR-0-3-1-02 | Dir 0.3.1 | codeql | `cpp/misra/possible-misuse-of-nan-floating-point-value` | `dir-0-3-1-nan` | pass |
| TV-CQL-RULE-4-1-1-01 | Rule 4.1.1 | codeql | `cpp/misra/compiler-language-extensions-used` | `rule-4-1-1`<br>`rule-4-1-1-has-include` | pass (AN-159) |
| TV-CQL-RULE-4-1-2-01 | Rule 4.1.2 | codeql | `cpp/misra/implicit-declaration-of-copy-constructor` | `rule-4-1-2-implicit-copy`<br>`rule-4-1-2-implicit-copy-defaulted` | pass (AN-055) |
| TV-CQL-RULE-4-1-2-02 | Rule 4.1.2 | codeql | `cpp/misra/noexcept-specifier-throw` | `rule-4-1-2-throw-spec` | pass |
| TV-CQL-RULE-4-1-2-03 | Rule 4.1.2 | codeql | `cpp/misra/redeclaration-of-static-constexpr-data-member` | `rule-4-1-2-constexpr-redecl` | pass |
| TV-CQL-RULE-4-1-2-04 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-allocator-void` | `rule-4-1-2-allocator-void` | pass |
| TV-CQL-RULE-4-1-2-05 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-c-headers` | `rule-4-1-2-c-headers` | pass |
| TV-CQL-RULE-4-1-2-06 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-function-binder-typedef-member` | `rule-4-1-2-binder-typedef` | anomaly (AN-011) |
| TV-CQL-RULE-4-1-2-07 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-is-literal-type-traits` | `rule-4-1-2-is-literal-type` | pass |
| TV-CQL-RULE-4-1-2-08 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-raw-storage-iterator` | `rule-4-1-2-raw-storage-iterator` | pass |
| TV-CQL-RULE-4-1-2-09 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-shared-ptr-unique` | `rule-4-1-2-shared-ptr-unique` | anomaly (AN-012) |
| TV-CQL-RULE-4-1-2-10 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-std-allocator-member` | `rule-4-1-2-allocator-member` | anomaly (AN-013) |
| TV-CQL-RULE-4-1-2-11 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-std-iterator-base-class` | `rule-4-1-2-iterator-base`<br>`rule-4-1-2-iterator-base-template` | anomaly (AN-045) |
| TV-CQL-RULE-4-1-2-12 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-str-stream-class` | `rule-4-1-2-strstream` | pass |
| TV-CQL-RULE-4-1-2-13 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-temporary-buffers` | `rule-4-1-2-temporary-buffer` | pass |
| TV-CQL-RULE-4-1-2-14 | Rule 4.1.2 | codeql | `cpp/misra/use-of-deprecated-unary-or-binary-negate` | `rule-4-1-2-negate-adaptor` | pass |
| TV-CQL-RULE-4-1-2-15 | Rule 4.1.2 | codeql | `cpp/misra/use-of-uncaught-exception` | `rule-4-1-2-uncaught-exception` | pass |
| TV-CQL-RULE-4-1-3-01 | Rule 4.1.3 | codeql | `cpp/misra/array-deleted-through-pointer-of-incorrect-type` | `rule-4-1-3-array-delete-type` | pass |
| TV-CQL-RULE-4-1-3-02 | Rule 4.1.3 | codeql | `cpp/misra/deallocation-type-mismatch` | `rule-4-1-3-dealloc-mismatch` | pass |
| TV-CQL-RULE-4-1-3-03 | Rule 4.1.3 | codeql | `cpp/misra/division-by-zero-undefined-behavior` | `rule-4-1-3-div-zero` | pass |
| TV-CQL-RULE-4-1-3-04 | Rule 4.1.3 | codeql | `cpp/misra/non-existent-member-access-undefined-behavior` | `rule-4-1-3-member-pointer-wrong-type` | pass |
| TV-CQL-RULE-4-1-3-05 | Rule 4.1.3 | codeql | `cpp/misra/null-pointer-to-member-access-undefined-behavior` | `rule-4-1-3-null-member-function-pointer`<br>`rule-4-1-3-null-member-pointer` | anomaly (AN-042) |
| TV-CQL-RULE-4-1-3-06 | Rule 4.1.3 | codeql | `cpp/misra/out-of-range-enum-cast-critical-unspecified-behavior` | `rule-4-1-3-enum-fixed-wide`<br>`rule-4-1-3-enum-out-of-range` | pass (AN-162) |
| TV-CQL-RULE-4-1-3-07 | Rule 4.1.3 | codeql | `cpp/misra/possible-data-race-between-threads` | `rule-4-1-3-data-race` | pass |
| TV-CQL-RULE-4-1-3-08 | Rule 4.1.3 | codeql | `cpp/misra/signed-integer-overflow` | `rule-4-1-3-signed-overflow` | pass |
| TV-CQL-RULE-4-1-3-09 | Rule 4.1.3 | codeql | `cpp/misra/uninitialized-static-pointer-to-member-undefined-behavior` | `rule-4-1-3-static-member-pointer` | pass |
| TV-CQL-RULE-4-6-1-01 | Rule 4.6.1 | codeql | `cpp/misra/memory-usage-not-sequenced` | `rule-4-6-1`<br>`rule-4-6-1-sequenced` | pass (AN-164) |
| TV-CQL-RULE-5-0-1-01 | Rule 5.0.1 | codeql | `cpp/misra/trigraph-like-sequences-should-not-be-used` | `rule-5-0-1`<br>`rule-5-0-1-escaped` | pass (AN-066) |
| TV-CLANG-RULE-5-7-1-01 | Rule 5.7.1 | clang | `-Wcomment` | `rule-5-7-1` | pass |
| TV-GCC-RULE-5-7-1-01 | Rule 5.7.1 | gcc | `-Wcomment` | `rule-5-7-1` | pass |
| TV-GCCARM-RULE-5-7-1-01 | Rule 5.7.1 | gcc-arm | `-Wcomment` | `rule-5-7-1` | pass |
| TV-CQL-RULE-5-7-1-01 | Rule 5.7.1 | codeql | `cpp/misra/character-sequence-used-within-ac-style-comment` | `rule-5-7-1` | pass |
| TV-CQL-DIR-5-7-2-01 | Dir 5.7.2 | codeql | `cpp/misra/sections-of-code-should-not-be-commented-out` | `dir-5-7-2` | pass |
| TV-CLANG-RULE-5-7-3-01 | Rule 5.7.3 | clang | `-Wcomment` | `rule-5-7-3` | pass |
| TV-GCC-RULE-5-7-3-01 | Rule 5.7.3 | gcc | `-Wcomment` | `rule-5-7-3` | pass |
| TV-GCCARM-RULE-5-7-3-01 | Rule 5.7.3 | gcc-arm | `-Wcomment` | `rule-5-7-3` | pass |
| TV-CQL-RULE-5-7-3-01 | Rule 5.7.3 | codeql | `cpp/misra/line-splicing-used-in-comments` | `rule-5-7-3` | pass |
| TV-CQL-RULE-5-10-1-01 | Rule 5.10.1 | codeql | `cpp/misra/poorly-formed-identifier` | `rule-5-10-1` | pass |
| TV-CLANG-RULE-5-13-1-01 | Rule 5.13.1 | clang | `-Wunknown-escape-sequence` | `rule-5-13-1` | pass |
| TV-GCC-RULE-5-13-1-01 | Rule 5.13.1 | gcc | `message /unknown escape sequence/` | `rule-5-13-1` | pass |
| TV-GCCARM-RULE-5-13-1-01 | Rule 5.13.1 | gcc-arm | `message /unknown escape sequence/` | `rule-5-13-1` | pass |
| TV-CQL-RULE-5-13-1-01 | Rule 5.13.1 | codeql | `cpp/misra/backslash-character-misuse` | `rule-5-13-1`<br>`rule-5-13-1-raw-string` | anomaly (AN-047, AN-106) |
| TV-CQL-RULE-5-13-2-01 | Rule 5.13.2 | codeql | `cpp/misra/non-terminated-escape-sequences` | `rule-5-13-2` | pass |
| TV-CQL-RULE-5-13-3-01 | Rule 5.13.3 | codeql | `cpp/misra/octal-constants-used` | `rule-5-13-3` | anomaly (AN-107) |
| TV-CQL-RULE-5-13-4-01 | Rule 5.13.4 | codeql | `cpp/misra/unsigned-integer-literals-not-appropriately-suffixed` | `rule-5-13-4`<br>`rule-5-13-4-value-init` | anomaly (AN-166, AN-207) |
| TV-TIDY-RULE-5-13-5-01 | Rule 5.13.5 | clang-tidy | `readability-uppercase-literal-suffix` | `rule-5-13-5` | pass |
| TV-CQL-RULE-5-13-5-01 | Rule 5.13.5 | codeql | `cpp/misra/lowercase-l-starts-in-literal-suffix` | `rule-5-13-5` | anomaly (AN-108) |
| TV-CQL-RULE-5-13-6-01 | Rule 5.13.6 | codeql | `cpp/misra/long-long-literal-with-single-l-suffix` | `rule-5-13-6` | anomaly (AN-006) |
| TV-CQL-RULE-6-0-1-01 | Rule 6.0.1 | codeql | `cpp/misra/block-scope-function-ambiguous` | `rule-6-0-1` | pass |
| TV-CQL-RULE-6-0-2-01 | Rule 6.0.2 | codeql | `cpp/misra/external-linkage-array-without-explicit-size-misra` | `rule-6-0-2` | pass |
| TV-CQL-RULE-6-0-3-01 | Rule 6.0.3 | codeql | `cpp/misra/global-namespace-declarations` | `rule-6-0-3` | pass |
| TV-CQL-RULE-6-0-4-01 | Rule 6.0.4 | codeql | `cpp/misra/non-global-function-main` | `rule-6-0-4` | pass |
| TV-CQL-RULE-6-2-1-01 | Rule 6.2.1 | codeql | `cpp/misra/one-definition-rule-violated` | `rule-6-2-1` | pass |
| TV-CQL-RULE-6-2-2-01 | Rule 6.2.2 | codeql | `cpp/misra/incompatible-function-declarations-cpp` | `rule-6-2-2-function` | pass |
| TV-CQL-RULE-6-2-2-02 | Rule 6.2.2 | codeql | `cpp/misra/incompatible-object-declarations-cpp` | `rule-6-2-2-object` | pass |
| TV-CQL-RULE-6-2-3-01 | Rule 6.2.3 | codeql | `cpp/misra/duplicate-inline-function-definitions` | `rule-6-2-3-inline` | pass |
| TV-CQL-RULE-6-2-3-02 | Rule 6.2.3 | codeql | `cpp/misra/duplicate-type-definitions` | `rule-6-2-3-type` | pass |
| TV-CQL-RULE-6-2-3-03 | Rule 6.2.3 | codeql | `cpp/misra/template-specialization-wrong-location` | `rule-6-2-3-specialization` | pass |
| TV-TIDY-RULE-6-2-4-01 | Rule 6.2.4 | clang-tidy | `misc-definitions-in-headers` | `rule-6-2-4` | pass |
| TV-CQL-RULE-6-2-4-01 | Rule 6.2.4 | codeql | `cpp/misra/violations-of-one-definition-rule-misra` | `rule-6-2-4` | anomaly (AN-109) |
| TV-GCC-RULE-6-4-1-01 | Rule 6.4.1 | gcc | `-Wshadow` | `rule-6-4-1` | pass |
| TV-GCCARM-RULE-6-4-1-01 | Rule 6.4.1 | gcc-arm | `-Wshadow` | `rule-6-4-1` | pass |
| TV-CQL-RULE-6-4-1-01 | Rule 6.4.1 | codeql | `cpp/misra/variable-declared-in-inner-scope-hides-outer-scope` | `rule-6-4-1` | anomaly (AN-110) |
| TV-CQL-RULE-6-4-2-01 | Rule 6.4.2 | codeql | `cpp/misra/definition-shall-be-considered-for-unqualified-lookup` | `rule-6-4-2-unqualified-lookup` | anomaly (AN-208) |
| TV-CQL-RULE-6-4-2-02 | Rule 6.4.2 | codeql | `cpp/misra/inherited-non-overridable-member-function` | `rule-6-4-2-nonvirtual`<br>`rule-6-4-2-using` | anomaly (AN-111, AN-170) |
| TV-CQL-RULE-6-4-2-03 | Rule 6.4.2 | codeql | `cpp/misra/inherited-overridable-member-function` | `rule-6-4-2-virtual` | pass |
| TV-CQL-RULE-6-4-3-01 | Rule 6.4.3 | codeql | `cpp/misra/name-shall-be-referred-using-a-qualified-id-or-this` | `rule-6-4-3` | pass |
| TV-CQL-RULE-6-4-3-02 | Rule 6.4.3 | codeql | `cpp/misra/name-shall-be-referred-using-a-qualified-id-or-this-audit` | `rule-6-4-3` | pass |
| TV-CQL-RULE-6-5-1-01 | Rule 6.5.1 | codeql | `cpp/misra/external-linkage-not-declared-in-header-file-misra` | `rule-6-5-1` | pass |
| TV-CQL-RULE-6-5-2-01 | Rule 6.5.2 | codeql | `cpp/misra/internal-linkage-specified-appropriately` | `rule-6-5-2` | pass |
| TV-CQL-RULE-6-7-1-01 | Rule 6.7.1 | codeql | `cpp/misra/local-variable-static-storage-duration` | `rule-6-7-1` | pass |
| TV-CQL-RULE-6-7-2-01 | Rule 6.7.2 | codeql | `cpp/misra/global-variable-used` | `rule-6-7-2`<br>`rule-6-7-2-variable-template` | pass (AN-173) |
| TV-CQL-RULE-6-8-1-01 | Rule 6.8.1 | codeql | `cpp/misra/object-accessed-after-lifetime-misra` | `rule-6-8-1-after` | pass |
| TV-CQL-RULE-6-8-1-02 | Rule 6.8.1 | codeql | `cpp/misra/object-accessed-before-lifetime-misra` | `rule-6-8-1-before` | anomaly (AN-112) |
| TV-CQL-RULE-6-8-2-01 | Rule 6.8.2 | codeql | `cpp/misra/return-reference-or-pointer-to-automatic-local-variable` | `rule-6-8-2`<br>`rule-6-8-2-indirect` | anomaly (AN-044) |
| TV-CQL-RULE-6-8-3-01 | Rule 6.8.3 | codeql | `cpp/misra/automatic-storage-assigned-to-object-greater-lifetime` | `rule-6-8-3` | pass |
| TV-CQL-RULE-6-8-4-01 | Rule 6.8.4 | codeql | `cpp/misra/member-functions-refqualified` | `rule-6-8-4`<br>`rule-6-8-4-template` | anomaly (AN-113, AN-175) |
| TV-CQL-RULE-6-9-1-01 | Rule 6.9.1 | codeql | `cpp/misra/type-aliases-declaration` | `rule-6-9-1` | pass |
| TV-CQL-RULE-6-9-2-01 | Rule 6.9.2 | codeql | `cpp/misra/avoid-standard-integer-type-names` | `rule-6-9-2` | pass |
| TV-CQL-RULE-7-0-1-01 | Rule 7.0.1 | codeql | `cpp/misra/no-conversion-from-bool` | `rule-7-0-1`<br>`rule-7-0-1-void` | pass (AN-177) |
| TV-CQL-RULE-7-0-2-01 | Rule 7.0.2 | codeql | `cpp/misra/no-implicit-bool-conversion` | `rule-7-0-2`<br>`rule-7-0-2-template` | pass (AN-181) |
| TV-CQL-RULE-7-0-3-01 | Rule 7.0.3 | codeql | `cpp/misra/no-character-numerical-value` | `rule-7-0-3` | pass |
| TV-CQL-RULE-7-0-4-01 | Rule 7.0.4 | codeql | `cpp/misra/inappropriate-bitwise-or-shift-operands` | `rule-7-0-4`<br>`rule-7-0-4-dependent-auto` | pass (AN-184) |
| TV-CQL-RULE-7-0-5-01 | Rule 7.0.5 | codeql | `cpp/misra/no-signedness-change-from-promotion` | `rule-7-0-5`<br>`rule-7-0-5-same-type`<br>`rule-7-0-5-shift-count` | pass (AN-186, AN-187) |
| TV-CQL-RULE-7-0-6-01 | Rule 7.0.6 | codeql | `cpp/misra/numeric-assignment-type-mismatch` | `rule-7-0-6`<br>`rule-7-0-6-implicit-this`<br>`rule-7-0-6-member-access` | pass (AN-188, AN-189) |
| TV-TIDY-RULE-7-11-1-01 | Rule 7.11.1 | clang-tidy | `modernize-use-nullptr` | `rule-7-11-1` | pass |
| TV-CQL-RULE-7-11-1-01 | Rule 7.11.1 | codeql | `cpp/misra/nullptr-not-the-only-form-of-the-null-pointer-constant` | `rule-7-11-1` | pass |
| TV-TIDY-RULE-7-11-2-01 | Rule 7.11.2 | clang-tidy | `cppcoreguidelines-pro-bounds-array-to-pointer-decay` | `rule-7-11-2` | pass |
| TV-CQL-RULE-7-11-2-01 | Rule 7.11.2 | codeql | `cpp/misra/array-passed-as-function-argument-decay-to-a-pointer` | `rule-7-11-2` | pass |
| TV-CQL-RULE-7-11-3-01 | Rule 7.11.3 | codeql | `cpp/misra/function-pointer-conversion-context` | `rule-7-11-3`<br>`rule-7-11-3-template` | anomaly (AN-191, AN-192) |
| TV-CQL-RULE-8-0-1-01 | Rule 8.0.1 | codeql | `cpp/misra/missing-precedence-clarifying-parenthesis` | `rule-8-0-1` | pass |
| TV-CQL-RULE-8-0-1-02 | Rule 8.0.1 | codeql | `cpp/misra/missing-sizeof-operator-parenthesis` | `rule-8-0-1` | pass |
| TV-CQL-RULE-8-1-1-01 | Rule 8.1.1 | codeql | `cpp/misra/non-transient-lambda-implicitly-captures-this` | `rule-8-1-1` | pass |
| TV-CQL-RULE-8-1-2-01 | Rule 8.1.2 | codeql | `cpp/misra/implicit-captures-disallowed-in-non-transient-lambda` | `rule-8-1-2` | pass |
| TV-TIDY-RULE-8-2-1-01 | Rule 8.2.1 | clang-tidy | `fuchsia-virtual-inheritance` | `rule-8-2-1` | pass |
| TV-CQL-RULE-8-2-1-01 | Rule 8.2.1 | codeql | `cpp/misra/virtual-base-class-cast-to-derived` | `rule-8-2-1` | anomaly (AN-115) |
| TV-CQL-RULE-8-2-2-01 | Rule 8.2.2 | codeql | `cpp/misra/no-c-style-or-functional-casts` | `rule-8-2-2`<br>`rule-8-2-2-braced` | pass (AN-200) |
| TV-CQL-RULE-8-2-3-01 | Rule 8.2.3 | codeql | `cpp/misra/cast-removes-const-or-volatile-from-pointer-or-reference` | `rule-8-2-3`<br>`rule-8-2-3-adding`<br>`rule-8-2-3-reference` | anomaly (AN-001) |
| TV-CQL-RULE-8-2-4-01 | Rule 8.2.4 | codeql | `cpp/misra/casts-between-a-pointer-to-function-and-any-other-type` | `rule-8-2-4` | anomaly (AN-117) |
| TV-TIDY-RULE-8-2-5-01 | Rule 8.2.5 | clang-tidy | `cppcoreguidelines-pro-type-reinterpret-cast` | `rule-8-2-5` | pass |
| TV-CQL-RULE-8-2-5-01 | Rule 8.2.5 | codeql | `cpp/misra/reinterpret-cast-shall-not-be-used` | `rule-8-2-5` | pass |
| TV-CQL-RULE-8-2-6-01 | Rule 8.2.6 | codeql | `cpp/misra/int-to-pointer-cast-prohibited` | `rule-8-2-6` | pass |
| TV-CQL-RULE-8-2-7-01 | Rule 8.2.7 | codeql | `cpp/misra/no-pointer-to-integral-cast` | `rule-8-2-7` | pass |
| TV-CQL-RULE-8-2-8-01 | Rule 8.2.8 | codeql | `cpp/misra/pointer-to-integral-cast` | `rule-8-2-8` | pass |
| TV-CLANG-RULE-8-2-9-01 | Rule 8.2.9 | clang | `error /use of typeid requires '?-frtti'?/` | `rule-8-2-9` | pass |
| TV-GCC-RULE-8-2-9-01 | Rule 8.2.9 | gcc | `error /cannot use 'typeid' with '-fno-rtti'/` | `rule-8-2-9` | pass |
| TV-GCCARM-RULE-8-2-9-01 | Rule 8.2.9 | gcc-arm | `error /cannot use 'typeid' with '-fno-rtti'/` | `rule-8-2-9` | pass |
| TV-CQL-RULE-8-2-10-01 | Rule 8.2.10 | codeql | `cpp/misra/functions-call-themselves-either-directly-or-indirectly` | `rule-8-2-10` | pass |
| TV-TIDY-RULE-8-2-11-01 | Rule 8.2.11 | clang-tidy | `cppcoreguidelines-pro-type-vararg` | `rule-8-2-11` | pass |
| TV-CQL-RULE-8-2-11-01 | Rule 8.2.11 | codeql | `cpp/misra/inappropriate-argument-type-passed-via-ellipsis` | `rule-8-2-11`<br>`rule-8-2-11-trivial` | pass (AN-197) |
| TV-CQL-RULE-8-3-1-01 | Rule 8.3.1 | codeql | `cpp/misra/built-in-unary-operator-applied-to-unsigned-expression` | `rule-8-3-1` | pass |
| TV-CQL-RULE-8-3-2-01 | Rule 8.3.2 | codeql | `cpp/misra/built-in-unary-plus-operator-should-not-be-used` | `rule-8-3-2` | pass |
| TV-CQL-RULE-8-7-1-01 | Rule 8.7.1 | codeql | `cpp/misra/pointer-argument-to-cstring-function-is-invalid` | `rule-8-7-1` | pass |
| TV-CQL-RULE-8-7-1-02 | Rule 8.7.1 | codeql | `cpp/misra/pointer-arithmetic-forms-an-invalid-pointer` | `rule-8-7-1` | pass |
| TV-CQL-RULE-8-7-2-01 | Rule 8.7.2 | codeql | `cpp/misra/pointer-difference-taken-between-different-arrays` | `rule-8-7-2` | pass |
| TV-CQL-RULE-8-9-1-01 | Rule 8.9.1 | codeql | `cpp/misra/pointer-compared-between-different-arrays` | `rule-8-9-1` | pass |
| TV-CQL-RULE-8-14-1-01 | Rule 8.14.1 | codeql | `cpp/misra/short-circuited-persistent-side-effect` | `rule-8-14-1` | anomaly (AN-114) |
| TV-CQL-RULE-8-18-1-01 | Rule 8.18.1 | codeql | `cpp/misra/object-assigned-to-an-overlapping-object-misra-cpp` | `rule-8-18-1`<br>`rule-8-18-1-prefix` | anomaly (AN-007) |
| TV-CQL-RULE-8-18-1-02 | Rule 8.18.1 | codeql | `cpp/misra/object-copied-to-an-overlapping-object-misra-cpp` | `rule-8-18-1` | pass |
| TV-CQL-RULE-8-18-2-01 | Rule 8.18.2 | codeql | `cpp/misra/result-of-an-assignment-operator-should-not-be-used` | `rule-8-18-2` | pass |
| TV-CQL-RULE-8-19-1-01 | Rule 8.19.1 | codeql | `cpp/misra/comma-operator-should-not-be-used` | `rule-8-19-1` | pass |
| TV-CQL-RULE-8-20-1-01 | Rule 8.20.1 | codeql | `cpp/misra/unsigned-operation-with-constant-operands-wraps` | `rule-8-20-1`<br>`rule-8-20-1-constant-in-range` | pass (AN-202) |
| TV-CQL-RULE-9-2-1-01 | Rule 9.2.1 | codeql | `cpp/misra/no-standalone-type-cast-expression` | `rule-9-2-1` | pass |
| TV-TIDY-RULE-9-3-1-01 | Rule 9.3.1 | clang-tidy | `readability-braces-around-statements` | `rule-9-3-1`<br>`rule-9-3-1-selection` | pass |
| TV-CQL-RULE-9-3-1-01 | Rule 9.3.1 | codeql | `cpp/misra/loop-body-compound-condition` | `rule-9-3-1`<br>`rule-9-3-1-selection` | anomaly (AN-041) |
| TV-CQL-RULE-9-3-1-02 | Rule 9.3.1 | codeql | `cpp/misra/switch-body-compound-condition` | `rule-9-3-1` | pass |
| TV-TIDY-RULE-9-4-1-01 | Rule 9.4.1 | clang-tidy | `hicpp-multiway-paths-covered` | `rule-9-4-1` | pass |
| TV-CQL-RULE-9-4-1-01 | Rule 9.4.1 | codeql | `cpp/misra/if-else-if-end-condition` | `rule-9-4-1` | pass |
| TV-CQL-RULE-9-4-2-01 | Rule 9.4.2 | codeql | `cpp/misra/appropriate-structure-of-switch-statement` | `rule-9-4-2`<br>`rule-9-4-2-scoped-enum`<br>`rule-9-4-2-template-default` | anomaly (AN-118, AN-203) |
| TV-CQL-RULE-9-5-1-01 | Rule 9.5.1 | codeql | `cpp/misra/legacy-for-statements-should-be-simple` | `rule-9-5-1`<br>`rule-9-5-1-size-t` | pass (AN-204) |
| TV-CQL-RULE-9-5-2-01 | Rule 9.5.2 | codeql | `cpp/misra/for-range-initializer-at-most-one-function-call` | `rule-9-5-2` | pass |
| TV-TIDY-RULE-9-6-1-01 | Rule 9.6.1 | clang-tidy | `cppcoreguidelines-avoid-goto` | `rule-9-6-1` | pass |
| TV-CQL-RULE-9-6-1-01 | Rule 9.6.1 | codeql | `cpp/misra/goto-statement-should-not-be-used` | `rule-9-6-1` | pass |
| TV-TIDY-RULE-9-6-2-01 | Rule 9.6.2 | clang-tidy | `cppcoreguidelines-avoid-goto` | `rule-9-6-2`<br>`rule-9-6-2-sibling` | pass |
| TV-CQL-RULE-9-6-2-01 | Rule 9.6.2 | codeql | `cpp/misra/goto-reference-a-label-in-surrounding-block` | `rule-9-6-2`<br>`rule-9-6-2-sibling` | anomaly (AN-039) |
| TV-TIDY-RULE-9-6-3-01 | Rule 9.6.3 | clang-tidy | `cppcoreguidelines-avoid-goto` | `rule-9-6-3` | pass |
| TV-CQL-RULE-9-6-3-01 | Rule 9.6.3 | codeql | `cpp/misra/goto-shall-jump-to-label-declared-later-in-the-function` | `rule-9-6-3` | pass |
| TV-CQL-RULE-9-6-4-01 | Rule 9.6.4 | codeql | `cpp/misra/function-declared-with-the-noreturn-attribute-return` | `rule-9-6-4` | pass |
| TV-CLANG-RULE-9-6-5-01 | Rule 9.6.5 | clang | `-Wreturn-type` | `rule-9-6-5` | pass |
| TV-GCC-RULE-9-6-5-01 | Rule 9.6.5 | gcc | `-Wreturn-type` | `rule-9-6-5` | pass |
| TV-GCCARM-RULE-9-6-5-01 | Rule 9.6.5 | gcc-arm | `-Wreturn-type` | `rule-9-6-5` | pass |
| TV-CQL-RULE-9-6-5-01 | Rule 9.6.5 | codeql | `cpp/misra/non-void-function-shall-return-a-value-on-all-paths` | `rule-9-6-5` | pass |
| TV-CQL-RULE-10-0-1-01 | Rule 10.0.1 | codeql | `cpp/misra/use-single-global-or-member-declarators` | `rule-10-0-1`<br>`rule-10-0-1-initialised` | anomaly (AN-046) |
| TV-CQL-RULE-10-0-1-02 | Rule 10.0.1 | codeql | `cpp/misra/use-single-local-declarators` | `rule-10-0-1` | pass |
| TV-CQL-RULE-10-1-1-01 | Rule 10.1.1 | codeql | `cpp/misra/pointer-or-ref-param-not-const` | `rule-10-1-1` | pass |
| TV-CQL-RULE-10-1-2-01 | Rule 10.1.2 | codeql | `cpp/misra/volatile-qualifier-not-used-appropriately` | `rule-10-1-2` | anomaly (AN-086) |
| TV-CQL-RULE-10-2-1-01 | Rule 10.2.1 | codeql | `cpp/misra/enumeration-not-defined-with-an-explicit-underlying-type` | `rule-10-2-1` | anomaly (AN-139) |
| TV-CQL-RULE-10-2-2-01 | Rule 10.2.2 | codeql | `cpp/misra/unscoped-enumerations-should-not-be-declared` | `rule-10-2-2` | pass |
| TV-CQL-RULE-10-2-3-01 | Rule 10.2.3 | codeql | `cpp/misra/unscoped-enum-without-fixed-underlying-type-used` | `rule-10-2-3` | pass |
| TV-TIDY-RULE-10-3-1-01 | Rule 10.3.1 | clang-tidy | `google-build-namespaces` | `rule-10-3-1` | pass |
| TV-CQL-RULE-10-3-1-01 | Rule 10.3.1 | codeql | `cpp/misra/unnamed-namespaces-in-header-files` | `rule-10-3-1` | pass |
| TV-TIDY-RULE-10-4-1-01 | Rule 10.4.1 | clang-tidy | `hicpp-no-assembler` | `rule-10-4-1` | pass |
| TV-CQL-RULE-10-4-1-01 | Rule 10.4.1 | codeql | `cpp/misra/asm-declaration-shall-not-be-used` | `rule-10-4-1` | pass |
| TV-TIDY-RULE-11-3-1-01 | Rule 11.3.1 | clang-tidy | `cppcoreguidelines-avoid-c-arrays` | `rule-11-3-1` | pass |
| TV-CQL-RULE-11-3-1-01 | Rule 11.3.1 | codeql | `cpp/misra/variable-declared-array-type` | `rule-11-3-1` | pass |
| TV-CQL-RULE-11-3-2-01 | Rule 11.3.2 | codeql | `cpp/misra/declaration-of-an-object-indirections-level` | `rule-11-3-2` | pass |
| TV-CQL-RULE-11-6-1-01 | Rule 11.6.1 | codeql | `cpp/misra/uninitialized-variable` | `rule-11-6-1` | pass |
| TV-CQL-RULE-11-6-2-01 | Rule 11.6.2 | codeql | `cpp/misra/value-of-an-object-must-not-be-read-before-it-has-been-set` | `rule-11-6-2` | pass |
| TV-CQL-RULE-11-6-3-01 | Rule 11.6.3 | codeql | `cpp/misra/non-unique-enumeration-constant` | `rule-11-6-3` | anomaly (AN-142) |
| TV-CQL-RULE-12-2-1-01 | Rule 12.2.1 | codeql | `cpp/misra/bit-fields-should-not-be-declared-misra-cpp` | `rule-12-2-1` | pass |
| TV-CQL-RULE-12-2-2-01 | Rule 12.2.2 | codeql | `cpp/misra/bit-field-shall-have-an-appropriate-type` | `rule-12-2-2` | anomaly (AN-048) |
| TV-CQL-RULE-12-2-3-01 | Rule 12.2.3 | codeql | `cpp/misra/signed-integer-named-bit-field-have-a-length-of-one-bit` | `rule-12-2-3`<br>`rule-12-2-3-alias` | anomaly (AN-010) |
| TV-CQL-RULE-12-3-1-01 | Rule 12.3.1 | codeql | `cpp/misra/union-keyword-used` | `rule-12-3-1` | pass |
| TV-TIDY-RULE-13-1-1-01 | Rule 13.1.1 | clang-tidy | `fuchsia-virtual-inheritance` | `rule-13-1-1` | pass |
| TV-CQL-RULE-13-1-1-01 | Rule 13.1.1 | codeql | `cpp/misra/virtual-inheritance-not-allowed` | `rule-13-1-1` | pass |
| TV-TIDY-RULE-13-1-2-01 | Rule 13.1.2 | clang-tidy | `fuchsia-virtual-inheritance` | `rule-13-1-2` | pass |
| TV-CQL-RULE-13-1-2-01 | Rule 13.1.2 | codeql | `cpp/misra/virtual-and-non-virtual-class-in-the-hierarchy` | `rule-13-1-2` | pass |
| TV-CQL-RULE-13-3-1-01 | Rule 13.3.1 | codeql | `cpp/misra/member-specifiers-not-used-appropriately` | `rule-13-3-1` | pass |
| TV-TIDY-RULE-13-3-2-01 | Rule 13.3.2 | clang-tidy | `google-default-arguments` | `rule-13-3-2` | pass |
| TV-CQL-RULE-13-3-2-01 | Rule 13.3.2 | codeql | `cpp/misra/overriding-shall-specify-different-default-arguments` | `rule-13-3-2` | pass |
| TV-CQL-RULE-13-3-3-01 | Rule 13.3.3 | codeql | `cpp/misra/declarations-of-a-function-same-parameter-name` | `rule-13-3-3` | pass |
| TV-CQL-RULE-13-3-4-01 | Rule 13.3.4 | codeql | `cpp/misra/potentially-virtual-pointer-only-compares-to-nullptr` | `rule-13-3-4`<br>`rule-13-3-4-variables` | anomaly (AN-043) |
| TV-CQL-RULE-14-1-1-01 | Rule 14.1.1 | codeql | `cpp/misra/private-and-public-data-members-mixed` | `rule-14-1-1` | pass |
| TV-CQL-RULE-15-0-1-01 | Rule 15.0.1 | codeql | `cpp/misra/improperly-provided-special-member-functions` | `rule-15-0-1` | pass |
| TV-CQL-RULE-15-0-2-01 | Rule 15.0.2 | codeql | `cpp/misra/invalid-signature-for-special-member-function` | `rule-15-0-2` | pass |
| TV-CQL-RULE-15-1-1-01 | Rule 15.1.1 | codeql | `cpp/misra/objects-dynamic-type-used-from-constructor-or-destructor` | `rule-15-1-1` | pass |
| TV-CQL-RULE-15-1-2-01 | Rule 15.1.2 | codeql | `cpp/misra/initialize-all-virtual-base-classes` | `rule-15-1-2`<br>`rule-15-1-2-delegating` | anomaly (AN-057, AN-145) |
| TV-TIDY-RULE-15-1-3-01 | Rule 15.1.3 | clang-tidy | `google-explicit-constructor` | `rule-15-1-3` | pass |
| TV-CQL-RULE-15-1-3-01 | Rule 15.1.3 | codeql | `cpp/misra/non-explicit-conversion-member` | `rule-15-1-3` | pass |
| TV-CQL-RULE-15-1-4-01 | Rule 15.1.4 | codeql | `cpp/misra/non-static-member-not-init-before-use` | `rule-15-1-4` | pass |
| TV-CQL-RULE-15-1-5-01 | Rule 15.1.5 | codeql | `cpp/misra/initializer-list-constructor-is-the-only-constructor` | `rule-15-1-5` | anomaly (AN-087) |
| TV-CQL-DIR-15-8-1-01 | Dir 15.8.1 | codeql | `cpp/misra/copy-and-move-assignments-shall-handle-self-assignment` | `dir-15-8-1`<br>`dir-15-8-1-swap` | pass (AN-050) |
| TV-CQL-RULE-16-5-1-01 | Rule 16.5.1 | codeql | `cpp/misra/logical-and-and-logical-or-operators-overloaded` | `rule-16-5-1` | pass |
| TV-TIDY-RULE-16-5-2-01 | Rule 16.5.2 | clang-tidy | `google-runtime-operator` | `rule-16-5-2` | pass |
| TV-CQL-RULE-16-5-2-01 | Rule 16.5.2 | codeql | `cpp/misra/address-of-operator-overloaded` | `rule-16-5-2` | pass |
| TV-CQL-RULE-16-6-1-01 | Rule 16.6.1 | codeql | `cpp/misra/invalid-operator-overloaded-as-member-function` | `rule-16-6-1` | pass |
| TV-CQL-RULE-17-8-1-01 | Rule 17.8.1 | codeql | `cpp/misra/function-templates-explicitly-specialized` | `rule-17-8-1` | pass |
| TV-CLANG-RULE-18-1-1-01 | Rule 18.1.1 | clang | `error /cannot use 'throw' with exceptions disabled/` | `rule-18-1-1` | pass |
| TV-GCC-RULE-18-1-1-01 | Rule 18.1.1 | gcc | `error /exception handling disabled/` | `rule-18-1-1` | pass |
| TV-GCCARM-RULE-18-1-1-01 | Rule 18.1.1 | gcc-arm | `error /exception handling disabled/` | `rule-18-1-1` | pass |
| TV-HBC-RULE-18-1-1-01 | Rule 18.1.1 | handbook-check | `forbidden-patterns/exceptions-rtti` | `test_handbook_check.py::test_heap_exceptions_rtti_virtual_in_code` | pass |
| TV-CLANG-RULE-18-1-2-01 | Rule 18.1.2 | clang | `error /cannot use '(throw|try)' with exceptions disabled/` | `rule-18-1-2` | pass |
| TV-GCC-RULE-18-1-2-01 | Rule 18.1.2 | gcc | `error /exception handling disabled/` | `rule-18-1-2` | pass |
| TV-GCCARM-RULE-18-1-2-01 | Rule 18.1.2 | gcc-arm | `error /exception handling disabled/` | `rule-18-1-2` | pass |
| TV-HBC-RULE-18-1-2-01 | Rule 18.1.2 | handbook-check | `forbidden-patterns/exceptions-rtti` | `test_handbook_check.py::test_heap_exceptions_rtti_virtual_in_code` | pass |
| TV-CLANG-RULE-18-3-1-01 | Rule 18.3.1 | clang | `error /cannot use '(throw|try)' with exceptions disabled/` | `rule-18-3-1` | pass |
| TV-GCC-RULE-18-3-1-01 | Rule 18.3.1 | gcc | `error /exception handling disabled/` | `rule-18-3-1` | pass |
| TV-GCCARM-RULE-18-3-1-01 | Rule 18.3.1 | gcc-arm | `error /exception handling disabled/` | `rule-18-3-1` | pass |
| TV-HBC-RULE-18-3-1-01 | Rule 18.3.1 | handbook-check | `forbidden-patterns/exceptions-rtti` | `test_handbook_check.py::test_heap_exceptions_rtti_virtual_in_code` | pass |
| TV-CLANG-RULE-18-3-2-01 | Rule 18.3.2 | clang | `error /cannot use '(throw|try)' with exceptions disabled/` | `rule-18-3-2` | pass |
| TV-GCC-RULE-18-3-2-01 | Rule 18.3.2 | gcc | `error /exception handling disabled/` | `rule-18-3-2` | pass |
| TV-GCCARM-RULE-18-3-2-01 | Rule 18.3.2 | gcc-arm | `error /exception handling disabled/` | `rule-18-3-2` | pass |
| TV-HBC-RULE-18-3-2-01 | Rule 18.3.2 | handbook-check | `forbidden-patterns/exceptions-rtti` | `test_handbook_check.py::test_heap_exceptions_rtti_virtual_in_code` | pass |
| TV-CLANG-RULE-18-3-3-01 | Rule 18.3.3 | clang | `error /cannot use '(throw|try)' with exceptions disabled/` | `rule-18-3-3` | pass |
| TV-GCC-RULE-18-3-3-01 | Rule 18.3.3 | gcc | `error /exception handling disabled/` | `rule-18-3-3` | pass |
| TV-GCCARM-RULE-18-3-3-01 | Rule 18.3.3 | gcc-arm | `error /exception handling disabled/` | `rule-18-3-3` | pass |
| TV-HBC-RULE-18-3-3-01 | Rule 18.3.3 | handbook-check | `forbidden-patterns/exceptions-rtti` | `test_handbook_check.py::test_heap_exceptions_rtti_virtual_in_code` | pass |
| TV-CQL-RULE-18-4-1-01 | Rule 18.4.1 | codeql | `cpp/misra/exception-unfriendly-function-must-be-noexcept` | `rule-18-4-1`<br>`rule-18-4-1-no-exceptions` | anomaly (AN-148, AN-150) |
| TV-CLANG-RULE-18-5-1-01 | Rule 18.5.1 | clang | `error /cannot use '(throw|try)' with exceptions disabled/` | `rule-18-5-1` | pass |
| TV-GCC-RULE-18-5-1-01 | Rule 18.5.1 | gcc | `error /exception handling disabled/` | `rule-18-5-1` | pass |
| TV-GCCARM-RULE-18-5-1-01 | Rule 18.5.1 | gcc-arm | `error /exception handling disabled/` | `rule-18-5-1` | pass |
| TV-HBC-RULE-18-5-1-01 | Rule 18.5.1 | handbook-check | `forbidden-patterns/exceptions-rtti` | `test_handbook_check.py::test_heap_exceptions_rtti_virtual_in_code` | pass |
| TV-CQL-RULE-18-5-2-01 | Rule 18.5.2 | codeql | `cpp/misra/avoid-program-terminating-functions` | `rule-18-5-2`<br>`rule-18-5-2-quick-exit` | pass |
| TV-TIDY-RULE-19-0-2-01 | Rule 19.0.2 | clang-tidy | `cppcoreguidelines-macro-usage` | `rule-19-0-2` | pass |
| TV-CQL-RULE-19-0-2-01 | Rule 19.0.2 | codeql | `cpp/misra/function-like-macros-defined` | `rule-19-0-2` | pass |
| TV-CQL-RULE-19-0-3-01 | Rule 19.0.3 | codeql | `cpp/misra/include-directives-preceded-by-preprocessor-directives` | `rule-19-0-3`<br>`rule-19-0-3-using` | anomaly (AN-040) |
| TV-CQL-RULE-19-0-4-01 | Rule 19.0.4 | codeql | `cpp/misra/undef-of-macro-not-defined-in-file` | `rule-19-0-4` | pass |
| TV-CLANG-RULE-19-1-1-01 | Rule 19.1.1 | clang | `-Wexpansion-to-defined` | `rule-19-1-1`<br>`rule-19-1-1-elif` | pass |
| TV-CLANG-RULE-19-1-1-02 | Rule 19.1.1 | clang | `error /macro name (missing|must be an identifier)/` | `rule-19-1-1-malformed` | pass |
| TV-GCC-RULE-19-1-1-01 | Rule 19.1.1 | gcc | `-Wexpansion-to-defined` | `rule-19-1-1`<br>`rule-19-1-1-elif` | pass |
| TV-GCCARM-RULE-19-1-1-01 | Rule 19.1.1 | gcc-arm | `-Wexpansion-to-defined` | `rule-19-1-1`<br>`rule-19-1-1-elif` | pass |
| TV-GCC-RULE-19-1-1-02 | Rule 19.1.1 | gcc | `error /operator .defined. requires an identifier/` | `rule-19-1-1-malformed` | pass |
| TV-GCCARM-RULE-19-1-1-02 | Rule 19.1.1 | gcc-arm | `error /operator .defined. requires an identifier/` | `rule-19-1-1-malformed` | pass |
| TV-CQL-RULE-19-1-1-01 | Rule 19.1.1 | codeql | `cpp/misra/defined-operator-expanded-in-if-directive` | `rule-19-1-1`<br>`rule-19-1-1-elif` | anomaly (AN-036) |
| TV-CQL-RULE-19-1-1-02 | Rule 19.1.1 | codeql | `cpp/misra/invalid-token-in-defined-operator` | `rule-19-1-1-malformed` | anomaly (AN-005) |
| TV-CLANG-RULE-19-1-2-01 | Rule 19.1.2 | clang | `error /unterminated conditional directive/` | `rule-19-1-2` | pass |
| TV-GCC-RULE-19-1-2-01 | Rule 19.1.2 | gcc | `error /unterminated #if/` | `rule-19-1-2` | pass |
| TV-GCCARM-RULE-19-1-2-01 | Rule 19.1.2 | gcc-arm | `error /unterminated #if/` | `rule-19-1-2` | pass |
| TV-CLANG-RULE-19-1-3-01 | Rule 19.1.3 | clang | `-Wundef` | `rule-19-1-3` | pass |
| TV-GCC-RULE-19-1-3-01 | Rule 19.1.3 | gcc | `-Wundef` | `rule-19-1-3` | pass |
| TV-GCCARM-RULE-19-1-3-01 | Rule 19.1.3 | gcc-arm | `-Wundef` | `rule-19-1-3` | pass |
| TV-CQL-RULE-19-1-3-01 | Rule 19.1.3 | codeql | `cpp/misra/identifiers-used-in-the-controlling-expression-of` | `rule-19-1-3`<br>`rule-19-1-3-has-include` | pass (AN-153) |
| TV-HBC-RULE-19-2-1-01 | Rule 19.2.1 | handbook-check | `include-guards` | `source_checks.py selftest` | pass |
| TV-CQL-RULE-19-2-1-01 | Rule 19.2.1 | codeql | `cpp/misra/include-outside-guard` | `rule-19-2-1-include-outside` | pass |
| TV-CQL-RULE-19-2-1-02 | Rule 19.2.1 | codeql | `cpp/misra/no-valid-ifdef-guard-in-header` | `rule-19-2-1-no-guard` | pass |
| TV-CLANG-RULE-19-2-2-01 | Rule 19.2.2 | clang | `-Wextra-tokens` | `rule-19-2-2-extra-tokens` | pass |
| TV-CLANG-RULE-19-2-2-02 | Rule 19.2.2 | clang | `error /expected "FILENAME" or <FILENAME>/` | `rule-19-2-2` | pass |
| TV-GCC-RULE-19-2-2-01 | Rule 19.2.2 | gcc | `error /#include'? expects/` | `rule-19-2-2` | pass |
| TV-GCCARM-RULE-19-2-2-01 | Rule 19.2.2 | gcc-arm | `error /#include'? expects/` | `rule-19-2-2` | pass |
| TV-GCC-RULE-19-2-2-02 | Rule 19.2.2 | gcc | `message /extra tokens at end of '?#include'? directive \[-Werror\]/` | `rule-19-2-2-extra-tokens` | pass |
| TV-GCCARM-RULE-19-2-2-02 | Rule 19.2.2 | gcc-arm | `message /extra tokens at end of '?#include'? directive \[-Werror\]/` | `rule-19-2-2-extra-tokens` | pass |
| TV-CQL-RULE-19-2-2-01 | Rule 19.2.2 | codeql | `cpp/misra/invalid-include-directive` | `rule-19-2-2-extra-tokens` | anomaly (AN-004) |
| TV-CQL-RULE-19-2-3-01 | Rule 19.2.3 | codeql | `cpp/misra/chars-that-should-not-occur-in-header-file-name` | `rule-19-2-3` | pass |
| TV-CQL-RULE-19-3-1-01 | Rule 19.3.1 | codeql | `cpp/misra/and-preprocessor-operators-should-not-be-used` | `rule-19-3-1` | pass |
| TV-CQL-RULE-19-3-2-01 | Rule 19.3.2 | codeql | `cpp/misra/macro-parameter-following-hash` | `rule-19-3-2`<br>`rule-19-3-2-split` | pass (AN-058) |
| TV-CQL-RULE-19-3-3-01 | Rule 19.3.3 | codeql | `cpp/misra/a-mixed-use-macro-argument-subject-to-expansion` | `rule-19-3-3` | pass |
| TV-CQL-RULE-19-3-4-01 | Rule 19.3.4 | codeql | `cpp/misra/unparenthesized-macro-argument` | `rule-19-3-4` | pass |
| TV-CQL-RULE-19-3-5-01 | Rule 19.3.5 | codeql | `cpp/misra/tokens-that-look-like-directives-in-a-macro-argument` | `rule-19-3-5` | pass |
| TV-HBC-RULE-19-6-1-01 | Rule 19.6.1 | handbook-check | `include-guards` | `source_checks.py selftest` | pass |
| TV-CQL-RULE-19-6-1-01 | Rule 19.6.1 | codeql | `cpp/misra/disallowed-use-of-pragma` | `rule-19-6-1` | anomaly (AN-088) |
| TV-TIDY-RULE-21-2-1-01 | Rule 21.2.1 | clang-tidy | `cert-err34-c` | `rule-21-2-1` | pass |
| TV-CQL-RULE-21-2-1-01 | Rule 21.2.1 | codeql | `cpp/misra/atof-atoi-atol-and-atoll-used` | `rule-21-2-1` | pass |
| TV-TIDY-RULE-21-2-2-01 | Rule 21.2.2 | clang-tidy | `bugprone-unsafe-functions` | `rule-21-2-2` | pass |
| TV-CQL-RULE-21-2-2-01 | Rule 21.2.2 | codeql | `cpp/misra/unsafe-string-handling-functions` | `rule-21-2-2` | anomaly (AN-089) |
| TV-TIDY-RULE-21-2-3-01 | Rule 21.2.3 | clang-tidy | `cert-env33-c` | `rule-21-2-3` | pass |
| TV-CQL-RULE-21-2-3-01 | Rule 21.2.3 | codeql | `cpp/misra/banned-system-function` | `rule-21-2-3` | pass |
| TV-CQL-RULE-21-2-4-01 | Rule 21.2.4 | codeql | `cpp/misra/macro-offsetof-shall-not-be-used` | `rule-21-2-4` | pass |
| TV-CQL-RULE-21-6-1-01 | Rule 21.6.1 | codeql | `cpp/misra/dynamic-memory-should-not-be-used` | `rule-21-6-1` | anomaly (AN-090) |
| TV-CQL-RULE-21-6-2-01 | Rule 21.6.2 | codeql | `cpp/misra/dynamic-memory-managed-manually` | `rule-21-6-2`<br>`rule-21-6-2-array` | anomaly (AN-037, AN-091) |
| TV-CQL-RULE-21-6-3-01 | Rule 21.6.3 | codeql | `cpp/misra/advanced-memory-management-used` | `rule-21-6-3`<br>`rule-21-6-3-uninitialized` | anomaly (AN-035) |
| TV-CQL-RULE-21-6-4-01 | Rule 21.6.4 | codeql | `cpp/misra/global-sized-operator-delete-shall-be-defined` | `rule-21-6-4` | anomaly (AN-092) |
| TV-CQL-RULE-21-6-4-02 | Rule 21.6.4 | codeql | `cpp/misra/global-unsized-operator-delete-shall-be-defined` | `rule-21-6-4-sized-only` | anomaly (AN-002) |
| TV-CLANG-RULE-21-6-5-01 | Rule 21.6.5 | clang | `-Wdelete-incomplete` | `rule-21-6-5` | pass |
| TV-GCC-RULE-21-6-5-01 | Rule 21.6.5 | gcc | `-Wdelete-incomplete` | `rule-21-6-5` | pass |
| TV-GCCARM-RULE-21-6-5-01 | Rule 21.6.5 | gcc-arm | `-Wdelete-incomplete` | `rule-21-6-5` | pass |
| TV-CQL-RULE-21-6-5-01 | Rule 21.6.5 | codeql | `cpp/misra/pointer-to-an-incomplete-class-type-deleted` | `rule-21-6-5` | pass |
| TV-TIDY-RULE-21-10-1-01 | Rule 21.10.1 | clang-tidy | `cppcoreguidelines-pro-type-vararg` | `rule-21-10-1` | pass |
| TV-CQL-RULE-21-10-1-01 | Rule 21.10.1 | codeql | `cpp/misra/no-variadic-function-macros` | `rule-21-10-1` | pass |
| TV-TIDY-RULE-21-10-2-01 | Rule 21.10.2 | clang-tidy | `cert-err52-cpp` | `rule-21-10-2` | pass |
| TV-CQL-RULE-21-10-2-01 | Rule 21.10.2 | codeql | `cpp/misra/no-csetjmp-header` | `rule-21-10-2` | anomaly (AN-206) |
| TV-TIDY-RULE-21-10-3-01 | Rule 21.10.3 | clang-tidy | `bugprone-unsafe-functions` | `rule-21-10-3` | pass |
| TV-CQL-RULE-21-10-3-01 | Rule 21.10.3 | codeql | `cpp/misra/csignal-facilities-used` | `rule-21-10-3` | pass |
| TV-CQL-RULE-21-10-3-02 | Rule 21.10.3 | codeql | `cpp/misra/csignal-types-shall-not-be-used` | `rule-21-10-3` | pass |
| TV-TIDY-RULE-22-3-1-01 | Rule 22.3.1 | clang-tidy | `misc-static-assert` | `rule-22-3-1` | pass |
| TV-CQL-RULE-22-3-1-01 | Rule 22.3.1 | codeql | `cpp/misra/assert-macro-used-with-a-constant-expression` | `rule-22-3-1` | pass |
| TV-CQL-RULE-22-4-1-01 | Rule 22.4.1 | codeql | `cpp/misra/invalid-assignment-to-errno` | `rule-22-4-1` | anomaly (AN-003) |
| TV-CQL-RULE-23-11-1-01 | Rule 23.11.1 | codeql | `cpp/misra/use-smart-ptr-factory-functions` | `rule-23-11-1` | pass |
| TV-TIDY-RULE-24-5-1-01 | Rule 24.5.1 | clang-tidy | `bugprone-unsafe-functions` | `rule-24-5-1` | pass |
| TV-CQL-RULE-24-5-1-01 | Rule 24.5.1 | codeql | `cpp/misra/character-handling-function-restrictions` | `rule-24-5-1` | pass |
| TV-TIDY-RULE-24-5-2-01 | Rule 24.5.2 | clang-tidy | `bugprone-unsafe-functions` | `rule-24-5-2` | pass |
| TV-CQL-RULE-24-5-2-01 | Rule 24.5.2 | codeql | `cpp/misra/no-memory-functions-from-c-string` | `rule-24-5-2` | anomaly (AN-093) |
| TV-TIDY-RULE-25-5-1-01 | Rule 25.5.1 | clang-tidy | `bugprone-unsafe-functions` | `rule-25-5-1` | pass |
| TV-CQL-RULE-25-5-1-01 | Rule 25.5.1 | codeql | `cpp/misra/locale-global-function-not-allowed` | `rule-25-5-1` | pass |
| TV-TIDY-RULE-25-5-2-01 | Rule 25.5.2 | clang-tidy | `bugprone-unsafe-functions` | `rule-25-5-2` | pass |
| TV-CQL-RULE-25-5-2-01 | Rule 25.5.2 | codeql | `cpp/misra/pointers-returned-by-locale-functions-must-be-used-as-const` | `rule-25-5-2`<br>`rule-25-5-2-const-use`<br>`rule-25-5-2-subscript-write` | anomaly (AN-008, AN-094) |
| TV-TIDY-RULE-25-5-3-01 | Rule 25.5.3 | clang-tidy | `bugprone-unsafe-functions` | `rule-25-5-3` | pass |
| TV-CQL-RULE-25-5-3-01 | Rule 25.5.3 | codeql | `cpp/misra/call-to-setlocale-invalidates-old-pointers-misra` | `rule-25-5-3`<br>`rule-25-5-3-ordered-use`<br>`rule-25-5-3-strerror` | anomaly (AN-095, AN-097, AN-099) |
| TV-CQL-RULE-25-5-3-02 | Rule 25.5.3 | codeql | `cpp/misra/call-to-setlocale-invalidates-old-pointers-warn-misra` | `rule-25-5-3`<br>`rule-25-5-3-ordered-use`<br>`rule-25-5-3-strerror` | anomaly (AN-096, AN-098, AN-100) |
| TV-CQL-RULE-26-3-1-01 | Rule 26.3.1 | codeql | `cpp/misra/vector-should-not-be-specialized-with-bool` | `rule-26-3-1`<br>`rule-26-3-1-const` | anomaly (AN-014) |
| TV-CQL-RULE-28-3-1-01 | Rule 28.3.1 | codeql | `cpp/misra/non-const-predicate-function-object` | `rule-28-3-1`<br>`rule-28-3-1-lambda` | pass |
| TV-CQL-RULE-28-3-1-02 | Rule 28.3.1 | codeql | `cpp/misra/predicate-with-persistent-side-effects` | `rule-28-3-1` | pass |
| TV-CQL-RULE-28-6-1-01 | Rule 28.6.1 | codeql | `cpp/misra/std-move-with-non-const-lvalue` | `rule-28-6-1` | anomaly (AN-101) |
| TV-CQL-RULE-28-6-2-01 | Rule 28.6.2 | codeql | `cpp/misra/forwarding-references-and-forward-not-used-together` | `rule-28-6-2`<br>`rule-28-6-2-generic-lambda` | anomaly (AN-038, AN-102) |
| TV-CQL-RULE-28-6-3-01 | Rule 28.6.3 | codeql | `cpp/misra/object-used-while-in-potentially-moved-from-state` | `rule-28-6-3`<br>`rule-28-6-3-reassigned` | anomaly (AN-024, AN-103) |
| TV-CQL-RULE-28-6-4-01 | Rule 28.6.4 | codeql | `cpp/misra/potentially-erroneous-container-usage` | `rule-28-6-4` | anomaly (AN-104) |
| TV-TIDY-RULE-30-0-1-01 | Rule 30.0.1 | clang-tidy | `bugprone-unsafe-functions` | `rule-30-0-1` | pass |
| TV-CQL-RULE-30-0-1-01 | Rule 30.0.1 | codeql | `cpp/misra/cstdio-functions-shall-not-be-used` | `rule-30-0-1`<br>`rule-30-0-1-algorithm-remove` | pass (AN-051) |
| TV-CQL-RULE-30-0-1-02 | Rule 30.0.1 | codeql | `cpp/misra/cstdio-macros-shall-not-be-used` | `rule-30-0-1` | pass |
| TV-CQL-RULE-30-0-1-03 | Rule 30.0.1 | codeql | `cpp/misra/cstdio-types-shall-not-be-used` | `rule-30-0-1` | pass |
| TV-CQL-RULE-30-0-2-01 | Rule 30.0.2 | codeql | `cpp/misra/reads-and-writes-on-stream-not-separated-by-positioning` | `rule-30-0-2`<br>`rule-30-0-2-member` | anomaly (AN-077, AN-105) |
| TV-CQL-KB-CPP-046-01 | KB-CPP-046 | codeql | `kokeb/cpp20/result-type-not-nodiscard` | `kb-cpp-046` | pass |
