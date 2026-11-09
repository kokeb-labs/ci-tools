// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_8_1_AFTER_OK_NEAR_HPP
#define KV_RULE_6_8_1_AFTER_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_8_1_after::near {

// The pointer is only used inside the scope of the object it points to.
inline std::int32_t last_seen(std::int32_t n) {
  std::int32_t out = 0;
  for (std::int32_t i = 0; i < n; ++i) {
    const std::int32_t copy = i;
    const std::int32_t* const p = &copy;
    out = *p;
  }
  return out;
}

}  // namespace kv::rule_6_8_1_after::near

#endif  // KV_RULE_6_8_1_AFTER_OK_NEAR_HPP
