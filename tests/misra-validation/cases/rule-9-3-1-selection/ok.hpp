// Compliant: braced if and else bodies; an else directly followed by if.
#ifndef KV_RULE_9_3_1_SELECTION_OK_HPP
#define KV_RULE_9_3_1_SELECTION_OK_HPP

#include <cstdint>

namespace kv::rule_9_3_1_selection::ok {

inline std::uint32_t clamp(std::uint32_t v, std::uint32_t hi) {
  std::uint32_t r = v;
  if (v > hi) {
    r = hi;
  } else if (v == 0U) {
    r = 1U;
  } else {
    r = r | 1U;
  }
  return r;
}

}  // namespace kv::rule_9_3_1_selection::ok

#endif  // KV_RULE_9_3_1_SELECTION_OK_HPP
