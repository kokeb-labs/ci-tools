// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_DIV_ZERO_OK_NEAR_HPP
#define KV_RULE_4_1_3_DIV_ZERO_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_3_div_zero::near {

// A divisor that is a non-zero constant, and a divisor excluded by an early return.
inline std::uint32_t eighth(std::uint32_t v) { return v / 8U; }
inline std::uint32_t wrap(std::uint32_t v, std::uint32_t m) {
  if (m == 0U) {
    return 0U;
  }
  return v % m;
}

}  // namespace kv::rule_4_1_3_div_zero::near

#endif  // KV_RULE_4_1_3_DIV_ZERO_OK_NEAR_HPP
