// Seeded violation (untyped): an unscoped enumeration with no fixed type.
#include <cstdint>

namespace kv::rule_10_2_2::bad_untyped {

enum Speed { kSlow, kFast };

bool fast(Speed s) { return s == kFast; }

}  // namespace kv::rule_10_2_2::bad_untyped
