// Seeded violation: a literal of unsigned type written without the U suffix.
#include <cstdint>

namespace kv::rule_5_13_4::bad {

std::uint32_t top_bit() { return 0x80000000; }  // unsigned type, no U  // seeded

}  // namespace kv::rule_5_13_4::bad
