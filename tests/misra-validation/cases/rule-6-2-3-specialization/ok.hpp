#ifndef KV_RULE_6_2_3_SPECIALIZATION_OK_HPP
#define KV_RULE_6_2_3_SPECIALIZATION_OK_HPP

// Compliant: the specialisation sits in the same file as the primary template.
#include <cstdint>

namespace kv::rule_6_2_3_specialization::ok {

template <typename T>
struct Width {
  static constexpr std::int32_t kBits{0};
};

template <>
struct Width<std::uint16_t> {
  static constexpr std::int32_t kBits{16};
};

inline std::int32_t bits() { return Width<std::uint16_t>::kBits; }

}  // namespace kv::rule_6_2_3_specialization::ok

#endif  // KV_RULE_6_2_3_SPECIALIZATION_OK_HPP
