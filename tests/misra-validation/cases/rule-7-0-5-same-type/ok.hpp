// Compliant: both operands of each comparison have the same type (Rule 7.0.5, Exception 3).
#ifndef KV_RULE_7_0_5_SAME_TYPE_OK_HPP
#define KV_RULE_7_0_5_SAME_TYPE_OK_HPP

#include <cstdint>

namespace kv::rule_7_0_5_same_type::ok {

inline constexpr std::uint8_t kChannels = 8U;
inline constexpr std::uint16_t kMaxCode = 4095U;

inline bool valid(std::uint8_t channel) { return channel < kChannels; }

inline bool in_range(std::uint16_t code) { return code <= kMaxCode; }

inline bool same(std::uint8_t a, std::uint8_t b) { return a == b; }

}  // namespace kv::rule_7_0_5_same_type::ok

#endif  // KV_RULE_7_0_5_SAME_TYPE_OK_HPP
