// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_0_0_1_hook::bad {

std::int32_t clamp(std::int32_t v) {
  if (v < 0) {
    return 0;
  }
  return v;
  v = 1;  // never runs  // seeded
}

}  // namespace kv::rule_0_0_1_hook::bad
