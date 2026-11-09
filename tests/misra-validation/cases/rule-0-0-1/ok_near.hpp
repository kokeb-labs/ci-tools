// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_0_1_OK_NEAR_HPP
#define KV_RULE_0_0_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_0_1::near {

// A return inside a branch: the statements after the if still run on the other path.
inline std::uint32_t pick(std::uint32_t v) {
  if (v == 0U) {
    return 1U;
  }
  const std::uint32_t out = v | 2U;
  return out;
}

}  // namespace kv::rule_0_0_1::near

#endif  // KV_RULE_0_0_1_OK_NEAR_HPP
