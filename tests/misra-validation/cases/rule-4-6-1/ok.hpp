// Compliant: each modification is its own full expression.
#ifndef KV_RULE_4_6_1_OK_HPP
#define KV_RULE_4_6_1_OK_HPP

#include <cstdint>

namespace kv::rule_4_6_1::ok {

inline std::uint32_t mark(std::uint32_t i) {
  std::uint32_t out = i;
  out |= 1U;
  out ^= 2U;
  return out;
}

}  // namespace kv::rule_4_6_1::ok

#endif  // KV_RULE_4_6_1_OK_HPP
