// Seeded violation (bitwise): two untyped unscoped enumerators combined with a bitwise operator.
#include <cstdint>

namespace kv::rule_10_2_3::bad_bitwise {

enum Flag { kRead = 1, kWrite = 2 };

std::int32_t both() { return kRead | kWrite; }  // seeded

}  // namespace kv::rule_10_2_3::bad_bitwise
