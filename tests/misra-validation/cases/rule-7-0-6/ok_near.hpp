// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_0_6_OK_NEAR_HPP
#define KV_RULE_7_0_6_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_0_6::ok_near {

inline std::int32_t widen(std::int16_t small) {
  std::int32_t const wide = small;
  return wide;
}

inline std::uint32_t same(std::uint32_t a) {
  std::uint32_t const b = a;
  return b;
}

inline std::int16_t explicit_narrow(std::int32_t wide) {
  std::int32_t const bounded = (wide > 1000) ? 1000 : ((wide < -1000) ? -1000 : wide);
  return static_cast<std::int16_t>(bounded);
}

}  // namespace kv::rule_7_0_6::ok_near

#endif  // KV_RULE_7_0_6_OK_NEAR_HPP
