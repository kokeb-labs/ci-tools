// Compliant: the range is computed first; the range-for initializer names it.
#ifndef KV_RULE_9_5_2_OK_HPP
#define KV_RULE_9_5_2_OK_HPP

#include <array>
#include <cstdint>

namespace kv::rule_9_5_2::ok {

inline std::uint32_t total(const std::array<std::uint32_t, 4>& data) {
  std::uint32_t sum = 0U;
  for (const std::uint32_t v : data) {
    sum = sum | v;
  }
  return sum;
}

}  // namespace kv::rule_9_5_2::ok

#endif  // KV_RULE_9_5_2_OK_HPP
