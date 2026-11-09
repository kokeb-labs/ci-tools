// Seeded violation: a specialisation for a standard type, away from the primary template's file.
#include <cstdint>

#include "zz_primary.inc"

namespace kv::rule_6_2_3_specialization::bad {

template <>
struct Width<std::uint16_t> {  // seeded
  static constexpr std::int32_t kBits{16};
};

std::int32_t bits() { return Width<std::uint16_t>::kBits; }

}  // namespace kv::rule_6_2_3_specialization::bad
