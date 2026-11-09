// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_0_0_2_hook::bad {

std::uint32_t limit(std::uint32_t v) {
  if (v >= 0U) {  // always true for an unsigned value  // seeded
    return v;
  }
  return 0U;
}

}  // namespace kv::rule_0_0_2_hook::bad
