// Near miss: bitwise operators on a flag type keep their meaning.
#ifndef KV_RULE_16_5_1_OK_BITWISE_HPP
#define KV_RULE_16_5_1_OK_BITWISE_HPP

#include <cstdint>

namespace kv::rule_16_5_1::ok_bitwise {

enum class Flags : std::uint8_t { kNone = 0U, kReady = 1U, kError = 2U };

[[nodiscard]] constexpr Flags operator|(Flags a, Flags b) {
  return static_cast<Flags>(static_cast<std::uint8_t>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b)));
}

[[nodiscard]] constexpr Flags operator&(Flags a, Flags b) {
  return static_cast<Flags>(static_cast<std::uint8_t>(static_cast<std::uint32_t>(a) & static_cast<std::uint32_t>(b)));
}

}  // namespace kv::rule_16_5_1::ok_bitwise

#endif  // KV_RULE_16_5_1_OK_BITWISE_HPP
