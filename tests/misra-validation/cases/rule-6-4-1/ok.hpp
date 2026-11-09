#ifndef KV_RULE_6_4_1_OK_HPP
#define KV_RULE_6_4_1_OK_HPP

// Compliant: every variable in a nested block has its own name.
#include <cstdint>

namespace kv::rule_6_4_1::ok {

inline bool any_odd(std::uint32_t n) {
  bool odd = false;
  for (std::uint32_t i = 0U; i < n; ++i) {
    std::uint32_t const rest = i % 2U;
    if (rest != 0U) {
      odd = true;
    }
  }
  return odd;
}

}  // namespace kv::rule_6_4_1::ok

#endif  // KV_RULE_6_4_1_OK_HPP
