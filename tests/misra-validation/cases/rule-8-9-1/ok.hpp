// Compliant: both pointers point into the same array.
#ifndef KV_RULE_8_9_1_OK_HPP
#define KV_RULE_8_9_1_OK_HPP

#include <array>
#include <cstdint>

namespace kv::rule_8_9_1::ok {

inline bool before(std::array<std::uint8_t, 4>& data) {
  std::uint8_t* a = &data[1];
  std::uint8_t* b = &data[3];
  return a < b;
}

}  // namespace kv::rule_8_9_1::ok

#endif  // KV_RULE_8_9_1_OK_HPP
