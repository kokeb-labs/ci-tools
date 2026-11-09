// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_13_3_OK_NEAR_HPP
#define KV_RULE_5_13_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_13_3::near {

// Zero, a hex literal, a binary literal and a zero escape are not octal literals.
inline std::uint32_t masks() { return 0x10U | 0b10U; }
inline char nul() { return '\0'; }

}  // namespace kv::rule_5_13_3::near

#endif  // KV_RULE_5_13_3_OK_NEAR_HPP
