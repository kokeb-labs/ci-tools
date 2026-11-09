// Seeded violation: arithmetic on character codes.
#include <cstdint>

namespace kv::rule_7_0_3::bad {

std::int32_t digit(char c) { return c - '0'; }

char upper(char c) { return static_cast<char>(c - 32); }

}  // namespace kv::rule_7_0_3::bad
