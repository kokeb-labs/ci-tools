// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_0_2_OK_NEAR_HPP
#define KV_RULE_7_0_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_7_0_2::ok_near {

inline std::int32_t choose(bool sel, std::int32_t a, std::int32_t b) { return sel ? a : b; }

inline bool empty(std::int32_t count) { return count == 0; }

inline std::uint32_t halve_until_zero(std::uint32_t n) {
  std::uint32_t remaining = n;
  while (remaining != 0U) {
    remaining = remaining / 2U;
  }
  return remaining;
}

}  // namespace kv::rule_7_0_2::ok_near

#endif  // KV_RULE_7_0_2_OK_NEAR_HPP
