// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_2_3_INLINE_OK_NEAR_HPP
#define KV_RULE_6_2_3_INLINE_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_2_3_inline::near {

// One definition in one header, included by two translation units: the same definition everywhere.
inline std::int32_t clamp_twice(std::int32_t v) { return (v > 50) ? 50 : v; }
template <typename T>
inline T clamp_any(T v) { return v; }
std::int32_t use_twice(std::int32_t v);

}  // namespace kv::rule_6_2_3_inline::near

#endif  // KV_RULE_6_2_3_INLINE_OK_NEAR_HPP
