// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_2_1_OK_NEAR_HPP
#define KV_RULE_0_2_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_2_1::near {

// The local is only read inside the lambda that captures it, and by sizeof: both refer to it.
inline std::uint32_t masked(std::uint32_t v) {
  const std::uint32_t mask = v >> 28U;
  const auto apply = [mask](std::uint32_t x) -> std::uint32_t { return x & mask; };
  return apply(v) | static_cast<std::uint32_t>(sizeof(mask));
}

}  // namespace kv::rule_0_2_1::near

#endif  // KV_RULE_0_2_1_OK_NEAR_HPP
