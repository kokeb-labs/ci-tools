// Seeded violation: a backslash at the end of a line comment splices the next line into it.
#include <cstdint>

namespace kv::rule_5_7_3::bad {

// a line comment that ends with a backslash \
std::uint32_t hidden() { return 1U; }
std::uint32_t two() { return 2U; }

}  // namespace kv::rule_5_7_3::bad
