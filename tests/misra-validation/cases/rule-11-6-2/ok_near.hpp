// Near misses (near): a value written on every path before it is read.
#ifndef KV_RULE_11_6_2_OK_NEAR_HPP
#define KV_RULE_11_6_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_11_6_2::ok_near {

inline std::uint32_t choose(bool a, std::uint32_t x, std::uint32_t y) {
  std::uint32_t v = x;
  if (a) {
    v = y;
  }
  return v;
}

}  // namespace kv::rule_11_6_2::ok_near

#endif  // KV_RULE_11_6_2_OK_NEAR_HPP
