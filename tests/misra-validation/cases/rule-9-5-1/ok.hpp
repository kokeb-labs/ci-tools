// Compliant: one counter, changed only in the increment clause, compared with a plain bound.
#ifndef KV_RULE_9_5_1_OK_HPP
#define KV_RULE_9_5_1_OK_HPP

#include <cstdint>

namespace kv::rule_9_5_1::ok {

inline std::uint32_t mask_to(std::uint32_t n) {
  std::uint32_t mask = 0U;
  for (std::uint32_t i = 0U; i < n; ++i) {
    mask = mask | i;
  }
  return mask;
}

}  // namespace kv::rule_9_5_1::ok

#endif  // KV_RULE_9_5_1_OK_HPP
