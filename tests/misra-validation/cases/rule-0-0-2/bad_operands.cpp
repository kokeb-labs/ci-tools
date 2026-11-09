// Seeded violations (operands): invariant first operand of ?: and invariant left operand of &&.
#include <cstdint>

namespace kv::rule_0_0_2::bad_operands {

std::uint32_t pick(std::uint16_t v) {
  return (v < 0U) ? 0U : 1U;  // seeded
}

bool small(std::uint8_t b, bool ready) {
  return (b <= 255U) && ready;  // seeded
}

}  // namespace kv::rule_0_0_2::bad_operands
