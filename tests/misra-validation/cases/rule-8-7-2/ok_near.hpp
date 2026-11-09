// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_7_2_OK_NEAR_HPP
#define KV_RULE_8_7_2_OK_NEAR_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_8_7_2::ok_near {

inline std::ptrdiff_t size_of(std::array<std::uint8_t, 4>& data) {
  std::uint8_t* first = data.data();
  std::uint8_t* last = data.data() + 4;
  return last - first;
}

}  // namespace kv::rule_8_7_2::ok_near

#endif  // KV_RULE_8_7_2_OK_NEAR_HPP
