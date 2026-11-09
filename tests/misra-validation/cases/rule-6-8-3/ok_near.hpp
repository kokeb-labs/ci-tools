// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_8_3_OK_NEAR_HPP
#define KV_RULE_6_8_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_8_3::near {

// A local's address stored in another local of the same scope does not outlive it.
inline std::int32_t same_scope() {
  std::int32_t value = 6;
  std::int32_t* const p = &value;
  *p = 7;
  return value;
}

}  // namespace kv::rule_6_8_3::near

#endif  // KV_RULE_6_8_3_OK_NEAR_HPP
