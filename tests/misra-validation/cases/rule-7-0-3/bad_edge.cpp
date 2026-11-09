// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_3::bad_edge {

char next(char c) { return static_cast<char>(c + 1); }

bool below_digits(char c) { return c < 48; }

std::int32_t doubled(char c) { return c * 2; }

}  // namespace kv::rule_7_0_3::bad_edge
