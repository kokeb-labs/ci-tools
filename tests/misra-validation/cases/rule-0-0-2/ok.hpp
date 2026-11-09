// Compliant: the condition depends on the input.
#ifndef KV_RULE_0_0_2_OK_HPP
#define KV_RULE_0_0_2_OK_HPP

#include <cstdint>

namespace kv::rule_0_0_2::ok {

inline std::uint32_t limit(std::uint32_t v) {
  std::uint32_t out = v;
  if (v > 100U) {
    out = 100U;
  }
  return out;
}

}  // namespace kv::rule_0_0_2::ok

#endif  // KV_RULE_0_0_2_OK_HPP
