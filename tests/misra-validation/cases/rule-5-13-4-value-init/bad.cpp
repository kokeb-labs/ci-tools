// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_5_13_4_value_init::bad {

std::uint32_t top_bit() { return 0x80000000; }  // seeded

}  // namespace kv::rule_5_13_4_value_init::bad
