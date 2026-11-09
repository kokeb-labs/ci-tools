// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_0_2_1_member::bad {

std::uint32_t mask(std::uint32_t v) {
  std::uint32_t spare = 3U;  // never referenced  // seeded
  return v & 0xFFU;
}

}  // namespace kv::rule_0_2_1_member::bad
