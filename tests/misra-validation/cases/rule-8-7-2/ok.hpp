// Compliant: both pointers point into the same array.
#ifndef KV_RULE_8_7_2_OK_HPP
#define KV_RULE_8_7_2_OK_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_8_7_2::ok {

inline std::ptrdiff_t gap(std::array<std::uint8_t, 4>& data) {
  std::uint8_t* a = &data[1];
  std::uint8_t* b = &data[3];
  return b - a;
}

}  // namespace kv::rule_8_7_2::ok

#endif  // KV_RULE_8_7_2_OK_HPP
