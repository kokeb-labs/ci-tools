// Seeded violation (with bad_b.cpp): limit_a is defined here and again in zz_dup_a.inc, in bad_b.cpp.
#include <cstdint>

namespace kv::rule_6_2_1::bad {

std::int32_t limit_a(std::int32_t v) { return (v > 10) ? 10 : v; }

}  // namespace kv::rule_6_2_1::bad

#include "zz_dup_b.inc"
