// Near misses (near): braced bodies in every form, else-if chains.
#ifndef KV_RULE_9_3_1_OK_NEAR_HPP
#define KV_RULE_9_3_1_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_9_3_1::ok_near {

inline std::uint32_t classify(std::uint32_t v) {
  std::uint32_t c = v;
  if (v < 10U) {
    c = 1U;
  } else if (v < 100U) {
    c = 2U;
  } else {
    c = c | 3U;
  }
  return c;
}

inline std::uint32_t count_up(std::uint32_t n) {
  std::uint32_t i = 0U;
  while (i < n) {
    i = i + 1U;
  }
  do {
    i = i | 1U;
  } while (i < n);
  for (std::uint32_t k = 0U; k < n; ++k) {
  }
  return i;
}

inline std::uint32_t any(const std::array<std::uint32_t, 3>& values) {
  std::uint32_t acc = 0U;
  for (const std::uint32_t v : values) {
    acc = acc | v;
  }
  return acc;
}

}  // namespace kv::rule_9_3_1::ok_near

#endif  // KV_RULE_9_3_1_OK_NEAR_HPP
