// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_2_template::bad {

std::int32_t pick(std::int32_t flags) {
  if (flags) {  // seeded
    return 1;
  }
  return 0;
}

}  // namespace kv::rule_7_0_2_template::bad
