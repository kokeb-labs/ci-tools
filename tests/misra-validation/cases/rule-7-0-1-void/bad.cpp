// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_1_void::bad {

std::int32_t count(bool a, bool b) {
  std::int32_t const total = a + b;  // seeded
  return total;
}

}  // namespace kv::rule_7_0_1_void::bad
