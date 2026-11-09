// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_9_1_OK_NEAR_HPP
#define KV_RULE_8_9_1_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_8_9_1::ok_near {

inline bool same(std::array<std::uint8_t, 2>& one, std::array<std::uint8_t, 2>& two) {
  return one.data() == two.data();
}

inline bool ordered(std::array<std::uint8_t, 4>& data) { return data.data() < (data.data() + 2); }

}  // namespace kv::rule_8_9_1::ok_near

#endif  // KV_RULE_8_9_1_OK_NEAR_HPP
