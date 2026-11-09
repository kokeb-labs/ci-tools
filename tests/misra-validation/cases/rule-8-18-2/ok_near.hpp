// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_18_2_OK_NEAR_HPP
#define KV_RULE_8_18_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_18_2::ok_near {

inline std::uint32_t loop(std::uint32_t n) {
  std::uint32_t last = 0U;
  for (std::uint32_t i = 0U; i < n; i = i + 1U) {
    last = i;
  }
  return last;
}

inline bool equal(std::uint32_t a, std::uint32_t b) { return a == b; }

}  // namespace kv::rule_8_18_2::ok_near

#endif  // KV_RULE_8_18_2_OK_NEAR_HPP
