// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_7_2_OK_NEAR_HPP
#define KV_RULE_6_7_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_7_2::near {

// Namespace-scope constants and a static constexpr member are not mutable.
inline constexpr std::int32_t kLimit{8};
const std::int32_t kFloor{0};
struct Range {
  static constexpr std::int32_t kTop{16};
};
inline std::int32_t span() { return Range::kTop - (kLimit + kFloor); }

}  // namespace kv::rule_6_7_2::near

#endif  // KV_RULE_6_7_2_OK_NEAR_HPP
