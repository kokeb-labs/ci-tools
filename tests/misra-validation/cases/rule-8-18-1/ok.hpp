// Compliant: overlapping ranges are moved with std::copy_backward; no unions.
#ifndef KV_RULE_8_18_1_OK_HPP
#define KV_RULE_8_18_1_OK_HPP

#include <algorithm>
#include <array>
#include <cstdint>

namespace kv::rule_8_18_1::ok {

inline void shift(std::array<std::uint8_t, 8>& data) {
  static_cast<void>(std::copy_backward(data.begin(), data.begin() + 4, data.begin() + 5));
}

}  // namespace kv::rule_8_18_1::ok

#endif  // KV_RULE_8_18_1_OK_HPP
