// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_4_1_3_enum_fixed_wide::bad {

enum Mode { kOff, kOn };
Mode to_mode() { return static_cast<Mode>(7); }  // seeded

}  // namespace kv::rule_4_1_3_enum_fixed_wide::bad
