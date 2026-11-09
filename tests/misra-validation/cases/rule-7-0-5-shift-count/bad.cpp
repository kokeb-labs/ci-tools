// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_5_shift_count::bad {

std::uint32_t scaled(std::uint8_t v) { return v << 2U; }  // seeded

}  // namespace kv::rule_7_0_5_shift_count::bad
