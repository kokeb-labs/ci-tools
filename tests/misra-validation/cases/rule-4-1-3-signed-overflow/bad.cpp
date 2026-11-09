// Seeded violation: a signed addition that may overflow.
#include <cstdint>

namespace kv::rule_4_1_3_signed_overflow::bad {

std::int32_t add(std::int32_t a, std::int32_t b) { return a + b; }

}  // namespace kv::rule_4_1_3_signed_overflow::bad
