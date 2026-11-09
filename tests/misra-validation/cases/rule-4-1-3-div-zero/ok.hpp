// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_DIV_ZERO_OK_HPP
#define KV_RULE_4_1_3_DIV_ZERO_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_div_zero::ok {

inline std::uint32_t share(std::uint32_t total, std::uint32_t parts) {
  std::uint32_t out = 0U;
  if (parts != 0U) {
    out = total / parts;
  }
  return out;
}

}  // namespace kv::rule_4_1_3_div_zero::ok

#endif  // KV_RULE_4_1_3_DIV_ZERO_OK_HPP
