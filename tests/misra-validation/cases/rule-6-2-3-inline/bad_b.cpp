// Seeded violation: an inline function written out in two source files instead of one header.
#include <cstdint>

namespace kv::rule_6_2_3_inline::bad {

inline std::int32_t clamp_b(std::int32_t v) { return (v < 1) ? 1 : v; }

std::int32_t use_b(std::int32_t v) { return clamp_b(v); }

}  // namespace kv::rule_6_2_3_inline::bad

#include "zz_copy_a.inc"
