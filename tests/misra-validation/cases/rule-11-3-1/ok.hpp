// Compliant: std::array instead of a built-in array.
#ifndef KV_RULE_11_3_1_OK_HPP
#define KV_RULE_11_3_1_OK_HPP

#include <array>
#include <cstdint>

namespace kv::rule_11_3_1::ok {

inline std::uint32_t any3(std::uint32_t a, std::uint32_t b, std::uint32_t c) {
  const std::array<std::uint32_t, 3> values{a, b, c};
  return values[0] | values[1] | values[2];
}

}  // namespace kv::rule_11_3_1::ok

#endif  // KV_RULE_11_3_1_OK_HPP
