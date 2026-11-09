// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_2_3_SPECIALIZATION_OK_NEAR_HPP
#define KV_RULE_6_2_3_SPECIALIZATION_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_2_3_specialization::near {

// The primary template, an explicit and a partial specialisation, all in one header.
template <typename T>
struct Width {
  static constexpr std::int32_t kBits{0};
};
template <>
struct Width<std::uint32_t> {
  static constexpr std::int32_t kBits{32};
};
template <typename T>
struct Width<T*> {
  static constexpr std::int32_t kBits{64};
};
inline std::int32_t wide() { return Width<std::uint32_t>::kBits; }

}  // namespace kv::rule_6_2_3_specialization::near

#endif  // KV_RULE_6_2_3_SPECIALIZATION_OK_NEAR_HPP
