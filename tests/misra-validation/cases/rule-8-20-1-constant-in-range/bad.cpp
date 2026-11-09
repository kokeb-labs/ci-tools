// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_8_20_1_constant_in_range::bad {

std::uint32_t wrapped() { return 0xFFFFFFFFU + 2U; }  // seeded

}  // namespace kv::rule_8_20_1_constant_in_range::bad
