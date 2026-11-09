// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_0_2_OK_NEAR_HPP
#define KV_RULE_0_0_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_0_2::near {

// The comparison of an 8-bit value with a bound inside its range can go both ways.
inline bool high(std::uint8_t b) { return b > 127U; }

}  // namespace kv::rule_0_0_2::near

#endif  // KV_RULE_0_0_2_OK_NEAR_HPP
