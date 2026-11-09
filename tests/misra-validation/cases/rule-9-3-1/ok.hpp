// Compliant: every loop, branch and switch body is a braced block.
#ifndef KV_RULE_9_3_1_OK_HPP
#define KV_RULE_9_3_1_OK_HPP

#include <cstdint>

namespace kv::rule_9_3_1::ok {

inline std::uint32_t mask_to(std::uint32_t n) {
  std::uint32_t mask = 0U;
  for (std::uint32_t i = 0U; i < n; ++i) {
    mask = mask | i;
  }
  if (mask > 100U) {
    mask = 100U;
  }
  return mask;
}

inline std::uint32_t pick(std::uint32_t mode) {
  std::uint32_t out = 0U;
  switch (mode) {
    case 1U: {
      out = 10U;
      break;
    }
    default: {
      break;
    }
  }
  return out;
}

}  // namespace kv::rule_9_3_1::ok

#endif  // KV_RULE_9_3_1_OK_HPP
