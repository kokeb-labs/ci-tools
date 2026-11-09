// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_3_2_OK_NEAR_HPP
#define KV_RULE_8_3_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_3_2::ok_near {

inline std::int32_t sum(std::int8_t a, std::int8_t b) { return static_cast<std::int32_t>(a) + static_cast<std::int32_t>(b); }

inline std::int32_t bump(std::int8_t v) {
  std::int32_t w = static_cast<std::int32_t>(v);
  w += 1;
  return w;
}

}  // namespace kv::rule_8_3_2::ok_near

#endif  // KV_RULE_8_3_2_OK_NEAR_HPP
