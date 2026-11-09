// Seeded violation: an octal integer literal.
#include <cstdint>

namespace kv::rule_5_13_3::bad {

std::uint32_t mode() { return 0755U; }  // seeded

}  // namespace kv::rule_5_13_3::bad
