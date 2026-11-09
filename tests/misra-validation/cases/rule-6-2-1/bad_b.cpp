// Seeded violation (with bad_a.cpp): limit_b is defined here and again in zz_dup_b.inc, in bad_a.cpp.
#include <cstdint>

namespace kv::rule_6_2_1::bad {

std::int32_t limit_b(std::int32_t v) { return (v > 20) ? 20 : v; }  // seeded

}  // namespace kv::rule_6_2_1::bad

#include "zz_dup_a.inc"
