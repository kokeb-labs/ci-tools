// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_BINDER_TYPEDEF_OK_NEAR_HPP
#define KV_RULE_4_1_2_BINDER_TYPEDEF_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_2_binder_typedef::near {

// A user function object declaring its own result_type: not a standard binder typedef.
struct IsSet {
  using result_type = bool;
  [[nodiscard]] result_type operator()(std::uint32_t v) const { return v != 0U; }
};
inline bool set(std::uint32_t v) { return IsSet{}(v); }

}  // namespace kv::rule_4_1_2_binder_typedef::near

#endif  // KV_RULE_4_1_2_BINDER_TYPEDEF_OK_NEAR_HPP
