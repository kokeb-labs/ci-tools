// Compliant: every local is referenced.
#ifndef KV_RULE_0_2_1_OK_HPP
#define KV_RULE_0_2_1_OK_HPP

#include <cstdint>

namespace kv::rule_0_2_1::ok {

inline std::uint32_t mask(std::uint32_t v) {
  const std::uint32_t low = 0xFFU;
  return v & low;
}

}  // namespace kv::rule_0_2_1::ok

#endif  // KV_RULE_0_2_1_OK_HPP
