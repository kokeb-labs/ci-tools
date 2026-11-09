// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_5_1_OK_NEAR_API_HPP
#define KV_RULE_6_5_1_OK_NEAR_API_HPP

#include <cstdint>

namespace kv::rule_6_5_1::near {

// The external object and function are declared in this header.
extern const std::int32_t kLimit;
std::int32_t twice_limit();
inline std::int32_t limit_or(std::int32_t v) { return (v < kLimit) ? v : kLimit; }

}  // namespace kv::rule_6_5_1::near

#endif  // KV_RULE_6_5_1_OK_NEAR_API_HPP
