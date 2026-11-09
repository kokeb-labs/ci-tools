// Compliant: the same results with loops, so the call graph has no cycle.
#ifndef KV_RULE_8_2_10_OK_HPP
#define KV_RULE_8_2_10_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_10::ok {

inline std::uint32_t depth(std::uint32_t n) {
  std::uint32_t d = 0U;
  for (std::uint32_t i = n; i > 0U; --i) {
    ++d;
  }
  return d;
}

inline bool is_even(std::uint32_t n) { return (n % 2U) == 0U; }

}  // namespace kv::rule_8_2_10::ok

#endif  // KV_RULE_8_2_10_OK_HPP
