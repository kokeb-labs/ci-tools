// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_4_6_1_sequenced::bad {

std::uint32_t combine(std::uint32_t a, std::uint32_t b) { return a ^ b; }
std::uint32_t both(std::uint32_t i) { return combine(i++, i++); }  // seeded

}  // namespace kv::rule_4_6_1_sequenced::bad
