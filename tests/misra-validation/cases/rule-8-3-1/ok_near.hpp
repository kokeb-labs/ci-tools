// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_3_1_OK_NEAR_HPP
#define KV_RULE_8_3_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_3_1::ok_near {

inline constexpr std::int32_t kOffset = -5;

inline std::int32_t offset() { return kOffset; }

}  // namespace kv::rule_8_3_1::ok_near

#endif  // KV_RULE_8_3_1_OK_NEAR_HPP
