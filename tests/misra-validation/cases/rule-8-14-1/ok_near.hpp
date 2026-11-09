// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_14_1_OK_NEAR_HPP
#define KV_RULE_8_14_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_14_1::ok_near {

inline bool is_small(std::uint32_t v) { return v < 10U; }

inline bool check(bool on, std::uint32_t v) { return on && is_small(v); }

inline bool mark(std::uint32_t& count, std::uint32_t value) {
  count = value;
  return value != 0U;
}

inline bool left_side(std::uint32_t& count, std::uint32_t value, bool on) { return mark(count, value) && on; }

}  // namespace kv::rule_8_14_1::ok_near

#endif  // KV_RULE_8_14_1_OK_NEAR_HPP
