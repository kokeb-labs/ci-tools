# Review checklist

What a reviewer checks in a pull request at the safety level, because the validated tools cannot prove it.

Each item names what the tests cannot show, why, and what the reviewer does about it. The anomaly log's
dispositions point here by item id.

## Every pull request

| Id | Check | Why no tool proves it |
| --- | --- | --- |
| R-UNDECIDABLE | Read each change against the undecidable guidelines the matrix keeps under review: lifetimes, data flow, side effects, recursion, floating point and preconditions | A query reports the forms it finds. No finding is not proof for an undecidable guideline (MISRA Compliance:2020 §3.5) |
| R-SYSTEM | For a change to a public header, consider the uses outside this repository (ODR, hiding, unused entities) | System-scope queries see only the translation units of the analysed build |
| R-CONFIG | Code under `#if` branches that neither host nor Cortex-M compiles (today ESP-IDF, `ESP_PLATFORM`) gets the full review and the commercial checker | Only the configurations ru-misra builds are analysed |
| R-FP | Each finding marked as a false diagnosis has an investigation record in the pull request: what the query reports, why the code complies, the anomaly id if it is known | MISRA Compliance:2020 §3.4: false diagnoses are recorded, not deviated |
| R-SCOPE | Each deviation marker is inside the scope its record states (for example, MD-CPP-003 only in `mcu/<family>/` and `bsp_bind/`) | The project-wide records state their scope in prose; ru-misra checks the guideline and the record id, not the scope |
| R-FLAGS | The build of the change uses the org flags (ru-misra's flags table says "yes" for every configuration) | ru-misra reports missing flags; at the high level it only warns |

## Known false negatives

| Id | Check | Disposition in the anomaly log |
| --- | --- | --- |
| R-4.1.2 | No deprecated standard library members (binder typedefs, `shared_ptr::unique`) in new code | AN entries for `use-of-deprecated-function-binder-typedef-member` and `use-of-deprecated-shared-ptr-unique` |
| R-5.13.6 | A literal meant as `long long` carries `LL`, never a single `L` | `long-long-literal-with-single-l-suffix` is not exercisable on the LP64 host |
| R-8.18.1 | No assignment between overlapping objects (union members of different sizes) | Unions are banned by Rule 12.3.1; review any deviation of it |
| R-12.2.3 | No one-bit signed bit-field through a fixed-width alias | Bit-fields are banned by Rule 12.2.1; review any deviation of it |
| R-21.6.4 | A replaced global `operator delete` has both the sized and the unsized form | Drivers never replace it (no heap) |
| R-22.4.1 | `errno` is only ever reset to zero | The query does not see glibc's `errno` macro |
| R-26.3.1 | No `std::vector<bool>`, also not `const` or by reference | Drivers use no `std::vector` (no heap) |

Next: [Tool validation plan](plan.md)
