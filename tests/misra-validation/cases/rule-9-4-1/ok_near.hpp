// Near misses (near): ifs that need no final else, and a final else with a nested if.
#ifndef KV_RULE_9_4_1_OK_NEAR_HPP
#define KV_RULE_9_4_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_9_4_1::ok_near {

inline std::uint32_t at_least(std::uint32_t v, std::uint32_t lo) {
  std::uint32_t r = v;
  if (v < lo) {
    r = lo;
  }
  return r;
}

inline std::uint32_t pick(bool a, std::uint32_t x, std::uint32_t y) {
  std::uint32_t r = y;
  if (a) {
    r = x;
  } else {
    r = r | 1U;
  }
  return r;
}

inline std::uint32_t band(std::uint32_t v) {
  std::uint32_t b = 0U;
  if (v < 10U) {
    b = 1U;
  } else if (v < 100U) {
    b = 2U;
  } else {
    if (v > 1000U) {
      b = 4U;
    }
  }
  return b;
}

}  // namespace kv::rule_9_4_1::ok_near

#endif  // KV_RULE_9_4_1_OK_NEAR_HPP
