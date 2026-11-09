// Compliant: one plain integer with masks and shifts instead of bit-fields.
#ifndef KV_RULE_12_2_1_OK_HPP
#define KV_RULE_12_2_1_OK_HPP

#include <cstdint>

namespace kv::rule_12_2_1::ok {

inline constexpr std::uint32_t kModeShift = 1U;
inline constexpr std::uint32_t kModeMask = 0x7U;

inline std::uint32_t mode_of(std::uint32_t flags) { return (flags >> kModeShift) & kModeMask; }

}  // namespace kv::rule_12_2_1::ok

#endif  // KV_RULE_12_2_1_OK_HPP
