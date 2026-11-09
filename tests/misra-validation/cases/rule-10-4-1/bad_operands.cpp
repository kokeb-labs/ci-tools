// Seeded violation (operands): an asm statement with an operand list.
#include <cstdint>

namespace kv::rule_10_4_1::bad_operands {

std::int32_t pass(std::int32_t v) {
  std::int32_t r = v;
  asm volatile("" : "+r"(r));
  return r;
}

}  // namespace kv::rule_10_4_1::bad_operands
