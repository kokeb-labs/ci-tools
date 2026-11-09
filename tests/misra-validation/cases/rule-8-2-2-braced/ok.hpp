// Compliant: functional-notation conversions with braces, which Rule 8.2.2 does not cover.
#ifndef KV_RULE_8_2_2_BRACED_OK_HPP
#define KV_RULE_8_2_2_BRACED_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_2_braced::ok {

inline constexpr std::uint16_t kError = 0x4000U;
inline constexpr std::uint16_t kWarning = 0x8000U;

inline std::uint32_t flags() { return std::uint32_t{kError} | std::uint32_t{kWarning}; }

inline std::uint32_t bit(std::uint32_t n) { return (n < 32U) ? (std::uint32_t{1} << n) : 0U; }

}  // namespace kv::rule_8_2_2_braced::ok

#endif  // KV_RULE_8_2_2_BRACED_OK_HPP
