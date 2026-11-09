// Near misses (near): an inline (versioning) namespace, which is named.
#ifndef KV_RULE_10_3_1_OK_NEAR_HPP
#define KV_RULE_10_3_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_3_1::ok_near {

inline namespace v1 {

inline std::uint32_t twice(std::uint32_t v) { return v << 1U; }

}  // namespace v1

}  // namespace kv::rule_10_3_1::ok_near

#endif  // KV_RULE_10_3_1_OK_NEAR_HPP
