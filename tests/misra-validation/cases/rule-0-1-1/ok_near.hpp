// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_1_1_OK_NEAR_HPP
#define KV_RULE_0_1_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_1_1::near {

// The value written is read by the compound assignment and by the return.
inline std::uint32_t mix(std::uint32_t a) {
  std::uint32_t r = a;
  r ^= 5U;
  return r;
}

// The value written is read through the reference by the callee.
inline void set_low(std::uint32_t& out, std::uint32_t v) { out = v & 0xFFU; }
inline std::uint32_t low_of(std::uint32_t v) {
  std::uint32_t r = 0U;
  set_low(r, v);
  return r;
}

}  // namespace kv::rule_0_1_1::near

#endif  // KV_RULE_0_1_1_OK_NEAR_HPP
