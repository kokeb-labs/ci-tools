// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_5_same_type::bad {

bool mixed(std::uint8_t a, std::uint16_t b) { return a < b; }  // seeded

}  // namespace kv::rule_7_0_5_same_type::bad
