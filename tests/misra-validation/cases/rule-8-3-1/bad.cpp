// Seeded violation: unary minus applied to an unsigned value.
#include <cstdint>

namespace kv::rule_8_3_1::bad {

std::uint32_t negate(std::uint32_t value) {
  return -value;  // seeded
}

}  // namespace kv::rule_8_3_1::bad
