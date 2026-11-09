// Seeded violation (cast): a static_cast whose target is an unscoped enumeration with no fixed type.
#include <cstdint>

namespace kv::rule_10_2_3::bad_cast {

enum Level { kLow, kHigh };

Level from_raw(std::int32_t raw) { return static_cast<Level>(raw); }  // seeded

}  // namespace kv::rule_10_2_3::bad_cast
