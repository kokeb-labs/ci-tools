// Compliant: the loop leaves with break; no goto.
#ifndef KV_RULE_9_6_2_SIBLING_OK_HPP
#define KV_RULE_9_6_2_SIBLING_OK_HPP

#include <cstdint>

namespace kv::rule_9_6_2_sibling::ok {

inline std::uint32_t hop(std::uint32_t n) {
  std::uint32_t r = 0U;
  for (std::uint32_t i = 0U; i < n; ++i) {
    if (i == 2U) {
      r = i;
      break;
    }
  }
  return r;
}

}  // namespace kv::rule_9_6_2_sibling::ok

#endif  // KV_RULE_9_6_2_SIBLING_OK_HPP
