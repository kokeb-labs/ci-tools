// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_NEGATE_ADAPTOR_OK_NEAR_HPP
#define KV_RULE_4_1_2_NEGATE_ADAPTOR_OK_NEAR_HPP

#include <cstdint>
#include <functional>

namespace kv::rule_4_1_2_negate_adaptor::near {

// std::not_fn is the replacement for the removed negators.
struct IsZero {
  [[nodiscard]] bool operator()(std::uint32_t v) const { return v == 0U; }
};
inline bool nonzero(std::uint32_t v) { return std::not_fn(IsZero{})(v); }

}  // namespace kv::rule_4_1_2_negate_adaptor::near

#endif  // KV_RULE_4_1_2_NEGATE_ADAPTOR_OK_NEAR_HPP
