// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_CONSTEXPR_REDECL_OK_NEAR_HPP
#define KV_RULE_4_1_2_CONSTEXPR_REDECL_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_constexpr_redecl::near {

// A static constexpr member used without an out-of-class redeclaration.
struct Range {
  static constexpr std::uint32_t kHigh = 9U;
};
// A static const (not constexpr) member defined out of class: that definition is required, not redundant.
struct Limit {
  static const std::uint32_t kMax;
};
inline const std::uint32_t Limit::kMax = 4U;
inline std::uint32_t both() { return Range::kHigh & Limit::kMax; }

}  // namespace kv::rule_4_1_2_constexpr_redecl::near

#endif  // KV_RULE_4_1_2_CONSTEXPR_REDECL_OK_NEAR_HPP
