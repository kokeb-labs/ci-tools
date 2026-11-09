// Seeded violation: a value outside an enumeration's range converted to it.
#include <cstdint>

namespace kv::rule_4_1_3_enum_out_of_range::bad {

enum Mode { kOff, kOn };

Mode to_mode() { return static_cast<Mode>(7); }  // seeded

}  // namespace kv::rule_4_1_3_enum_out_of_range::bad
