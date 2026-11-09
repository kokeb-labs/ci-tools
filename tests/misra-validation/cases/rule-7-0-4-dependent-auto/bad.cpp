// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_4_dependent_auto::bad {

std::int32_t low(std::int32_t v) { return v & 0x0F; }  // seeded

}  // namespace kv::rule_7_0_4_dependent_auto::bad
