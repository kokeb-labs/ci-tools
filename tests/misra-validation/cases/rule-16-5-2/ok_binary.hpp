// Near miss: a binary operator& is a bitwise and, not address-of.
#ifndef KV_RULE_16_5_2_OK_BINARY_HPP
#define KV_RULE_16_5_2_OK_BINARY_HPP

#include <cstdint>

namespace kv::rule_16_5_2::ok_binary {

enum class Mask : std::uint8_t { kNone = 0U, kLow = 1U, kHigh = 2U };

[[nodiscard]] constexpr Mask operator&(Mask a, Mask b) {
  return static_cast<Mask>(static_cast<std::uint8_t>(static_cast<std::uint32_t>(a) & static_cast<std::uint32_t>(b)));
}

}  // namespace kv::rule_16_5_2::ok_binary

#endif  // KV_RULE_16_5_2_OK_BINARY_HPP
