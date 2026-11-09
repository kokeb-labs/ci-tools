// Seeded violation: an unguarded signed addition, called with operands whose sum overflows std::int32_t.
#include <cstdint>
#include <limits>

namespace kv::rule_4_1_3_signed_overflow::bad {

std::int32_t add(std::int32_t a, std::int32_t b) { return a + b; }  // seeded

std::int32_t past_the_top() { return add(std::numeric_limits<std::int32_t>::max(), 1); }

}  // namespace kv::rule_4_1_3_signed_overflow::bad
