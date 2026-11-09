// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_6_1_OK_NEAR_HPP
#define KV_RULE_4_6_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_6_1::near {

// Increments of different objects in one expression, and a read then write in separate statements.
inline std::uint32_t pair(std::uint32_t x, std::uint32_t y) { return x ^ y; }
inline std::uint32_t args(std::uint32_t i, std::uint32_t j) {
  const std::uint32_t first = i;
  const std::uint32_t second = j | 1U;
  return pair(first, second);
}

}  // namespace kv::rule_4_6_1::near

#endif  // KV_RULE_4_6_1_OK_NEAR_HPP
