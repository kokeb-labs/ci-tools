#ifndef KV_RULE_6_2_3_INLINE_OK_HPP
#define KV_RULE_6_2_3_INLINE_OK_HPP

// Compliant: the inline function is written once, in a header.
#include <cstdint>

namespace kv::rule_6_2_3_inline::ok {

inline std::int32_t clamp(std::int32_t v) { return (v < 0) ? 0 : v; }

}  // namespace kv::rule_6_2_3_inline::ok

#endif  // KV_RULE_6_2_3_INLINE_OK_HPP
