// Near miss: the primary template is in another file, but the explicit specialisation sits in the file that
// defines the class named by its template argument, which the guideline also allows.
#ifndef KV_RULE_6_2_3_SPECIALIZATION_OK_ARG_HPP
#define KV_RULE_6_2_3_SPECIALIZATION_OK_ARG_HPP

#include <cstdint>

#include "zz_ok_primary.inc"

namespace kv::rule_6_2_3_specialization::ok_arg {

struct Sensor {
  std::int32_t raw{0};
};

template <>
struct Width<Sensor> {
  static constexpr std::int32_t kBits{12};
};

inline std::int32_t bits() { return Width<Sensor>::kBits; }

}  // namespace kv::rule_6_2_3_specialization::ok_arg

#endif  // KV_RULE_6_2_3_SPECIALIZATION_OK_ARG_HPP
