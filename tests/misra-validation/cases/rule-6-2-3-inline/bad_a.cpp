// Seeded violation: an inline function written out in two source files instead of one header.
#include <cstdint>

namespace kv::rule_6_2_3_inline::bad {

inline std::int32_t clamp_a(std::int32_t v) { return (v < 0) ? 0 : v; }

std::int32_t use_a(std::int32_t v) { return clamp_a(v); }

}  // namespace kv::rule_6_2_3_inline::bad

#include "zz_copy_b.inc"
