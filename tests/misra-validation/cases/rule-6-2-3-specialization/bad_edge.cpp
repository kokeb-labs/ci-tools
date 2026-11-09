// Edge cases: a second explicit specialisation and a partial one, away from the primary template.
#include <cstdint>
#include "zz_primary.inc"

namespace kv::rule_6_2_3_specialization::bad {

template <>
struct Width<std::uint32_t> {  // seeded
  static constexpr std::int32_t kBits{32};
};
template <typename T>
struct Width<T*> {  // seeded
  static constexpr std::int32_t kBits{64};
};
std::int32_t wide() { return Width<std::uint32_t>::kBits + Width<char*>::kBits; }

}  // namespace kv::rule_6_2_3_specialization::bad
