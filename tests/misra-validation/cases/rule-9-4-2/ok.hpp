// Compliant: every clause ends with break, and default comes last.
#ifndef KV_RULE_9_4_2_OK_HPP
#define KV_RULE_9_4_2_OK_HPP

#include <cstdint>

namespace kv::rule_9_4_2::ok {

inline std::uint32_t weight(std::uint32_t code) {
  std::uint32_t w = 0U;
  switch (code) {
    case 1U:
      w = 5U;
      break;
    case 2U:
      w = 7U;
      break;
    default:
      break;
  }
  return w;
}

}  // namespace kv::rule_9_4_2::ok

#endif  // KV_RULE_9_4_2_OK_HPP
