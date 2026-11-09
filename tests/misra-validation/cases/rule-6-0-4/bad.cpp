// Seeded violation: a function called main that is not the program entry point.
#include <cstdint>

namespace kv::rule_6_0_4::bad {

std::int32_t main() { return 0; }

}  // namespace kv::rule_6_0_4::bad
