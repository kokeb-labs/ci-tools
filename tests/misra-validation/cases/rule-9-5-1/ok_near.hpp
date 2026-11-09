// Near misses (near): counting down, constant steps, a const bound.
#ifndef KV_RULE_9_5_1_OK_NEAR_HPP
#define KV_RULE_9_5_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_9_5_1::ok_near {

inline std::uint32_t down(std::uint32_t n) {
  std::uint32_t acc = 0U;
  for (std::uint32_t i = n; i > 0U; --i) {
    acc = acc | i;
  }
  return acc;
}

inline std::uint32_t evens(std::uint32_t n) {
  std::uint32_t acc = 0U;
  for (std::uint32_t i = 0U; i < n; i += 2U) {
    acc = acc | i;
  }
  return acc;
}

inline std::uint32_t half(std::uint32_t n) {
  const std::uint32_t bound = n >> 1U;
  std::uint32_t acc = 0U;
  for (std::uint32_t i = 0U; i < bound; ++i) {
    acc = acc | i;
  }
  return acc;
}

}  // namespace kv::rule_9_5_1::ok_near

#endif  // KV_RULE_9_5_1_OK_NEAR_HPP
