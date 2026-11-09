// Compliant: a std::uint32_t converted to an enumeration with a fixed std::uint8_t underlying type is
// first converted to std::uint8_t, so every source value is defined; here it is also at most 3.
#ifndef KV_RULE_4_1_3_ENUM_FIXED_WIDE_OK_HPP
#define KV_RULE_4_1_3_ENUM_FIXED_WIDE_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_enum_fixed_wide::ok {

enum class Protect : std::uint8_t { kNone = 0U, kQuarter = 1U, kHalf = 2U, kAll = 3U };

constexpr std::uint32_t extract(std::uint8_t reg) noexcept {
  return (static_cast<std::uint32_t>(reg) >> 2U) & 0x3U;
}

constexpr Protect decode(std::uint8_t status) noexcept { return static_cast<Protect>(extract(status)); }

}  // namespace kv::rule_4_1_3_enum_fixed_wide::ok

#endif  // KV_RULE_4_1_3_ENUM_FIXED_WIDE_OK_HPP
