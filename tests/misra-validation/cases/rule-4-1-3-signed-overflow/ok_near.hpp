// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_SIGNED_OVERFLOW_OK_NEAR_HPP
#define KV_RULE_4_1_3_SIGNED_OVERFLOW_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_3_signed_overflow::near {

// Two 8-bit values widened to 32 bits cannot overflow when added.
inline std::int32_t add_small(std::int8_t a, std::int8_t b) { return static_cast<std::int32_t>(a) + static_cast<std::int32_t>(b); }

}  // namespace kv::rule_4_1_3_signed_overflow::near

#endif  // KV_RULE_4_1_3_SIGNED_OVERFLOW_OK_NEAR_HPP
