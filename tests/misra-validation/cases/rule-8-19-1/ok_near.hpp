// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_19_1_OK_NEAR_HPP
#define KV_RULE_8_19_1_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_8_19_1::ok_near {

inline std::uint32_t pick(std::uint32_t a, std::uint32_t b) { return (a < b) ? a : b; }

inline std::uint32_t first() {
  std::array<std::uint32_t, 3> const values{1U, 2U, 3U};
  return pick(values[0], values[1]);
}

}  // namespace kv::rule_8_19_1::ok_near

#endif  // KV_RULE_8_19_1_OK_NEAR_HPP
