// Near misses (near): every path returns a value.
#ifndef KV_RULE_9_6_5_OK_NEAR_HPP
#define KV_RULE_9_6_5_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_9_6_5::ok_near {

inline std::uint32_t pick(bool a, std::uint32_t x, std::uint32_t y) {
  if (a) {
    return x;
  } else {
    return y;
  }
}

inline std::uint32_t code_of(std::uint32_t k) {
  switch (k) {
    case 0U:
      return 10U;
    case 1U:
      return 20U;
    default:
      return 0U;
  }
}

}  // namespace kv::rule_9_6_5::ok_near

#endif  // KV_RULE_9_6_5_OK_NEAR_HPP
