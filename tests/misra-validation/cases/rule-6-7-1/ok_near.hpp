// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_7_1_OK_NEAR_HPP
#define KV_RULE_6_7_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_7_1::near {

// Function-local statics that are constants are allowed.
inline std::uint32_t low(std::uint32_t v) {
  static const std::uint32_t kMask = 0xFFU;
  static constexpr std::uint32_t kShift = 0U;
  return (v & kMask) >> kShift;
}

}  // namespace kv::rule_6_7_1::near

#endif  // KV_RULE_6_7_1_OK_NEAR_HPP
