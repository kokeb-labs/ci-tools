// Seeded violation: an array with external linkage declared without its size.
#include <cstdint>

namespace kv::rule_6_0_2::bad {

extern std::int32_t const kTable[];  // seeded

std::int32_t first() { return kTable[0]; }

}  // namespace kv::rule_6_0_2::bad
