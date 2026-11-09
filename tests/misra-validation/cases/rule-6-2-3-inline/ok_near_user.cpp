// A second translation unit that includes the same header (with ok_near.hpp itself).
#include "ok_near.hpp"

namespace kv::rule_6_2_3_inline::near {

std::int32_t use_twice(std::int32_t v) { return clamp_twice(clamp_any(v)); }

}  // namespace kv::rule_6_2_3_inline::near
