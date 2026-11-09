// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_18_1_OK_NEAR_HPP
#define KV_RULE_8_18_1_OK_NEAR_HPP

#include <algorithm>
#include <array>
#include <cstdint>

namespace kv::rule_8_18_1::ok_near {

struct Pair {
  std::uint32_t a{0U};
  std::uint32_t b{0U};
};

inline void copy(std::array<std::uint8_t, 4> const& src, std::array<std::uint8_t, 4>& dst) {
  static_cast<void>(std::copy(src.begin(), src.end(), dst.begin()));
}

inline std::uint32_t members(Pair& p) {
  p.a = p.b;
  return p.a;
}

}  // namespace kv::rule_8_18_1::ok_near

#endif  // KV_RULE_8_18_1_OK_NEAR_HPP
