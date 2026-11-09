// Seeded violation: arithmetic on a plain enumerator whose type is not fixed.
#include <cstdint>

namespace kv::rule_10_2_3::bad {

enum Level { kLow, kHigh };

std::int32_t bump(Level l) { return l + 1; }  // seeded

}  // namespace kv::rule_10_2_3::bad
