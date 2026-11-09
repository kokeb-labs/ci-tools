// Compliant: std::fill returns void, so there is no result to use.
#ifndef KV_RULE_0_1_2_NIEBLOID_OK_HPP
#define KV_RULE_0_1_2_NIEBLOID_OK_HPP

#include <algorithm>
#include <array>
#include <cstdint>

namespace kv::rule_0_1_2_niebloid::ok {

inline std::uint32_t clear(std::array<std::uint32_t, 4U>& buf) {
  std::fill(buf.begin(), buf.end(), 0U);
  return buf[0];
}

}  // namespace kv::rule_0_1_2_niebloid::ok

#endif  // KV_RULE_0_1_2_NIEBLOID_OK_HPP
