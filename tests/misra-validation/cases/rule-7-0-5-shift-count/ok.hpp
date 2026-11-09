// Compliant: the left operand of each shift is std::uint32_t; only the count is a narrow unsigned type.
#ifndef KV_RULE_7_0_5_SHIFT_COUNT_OK_HPP
#define KV_RULE_7_0_5_SHIFT_COUNT_OK_HPP

#include <cstdint>

namespace kv::rule_7_0_5_shift_count::ok {

inline constexpr std::uint16_t kFieldShift = 3U;

inline std::uint32_t field(std::uint32_t reg) { return (reg >> kFieldShift) & 0x7U; }

inline std::uint32_t bit(std::uint8_t n) { return (n < 32U) ? (1U << n) : 0U; }

}  // namespace kv::rule_7_0_5_shift_count::ok

#endif  // KV_RULE_7_0_5_SHIFT_COUNT_OK_HPP
