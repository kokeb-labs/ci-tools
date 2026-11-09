// Seeded violation: assert used for a fact the compiler already knows.
#include <cassert>
#include <cstdint>

namespace kv::rule_22_3_1::bad {

std::int32_t widen(std::int16_t value) {
  assert(sizeof(std::int32_t) == 4U);  // seeded
  return value;
}

}  // namespace kv::rule_22_3_1::bad
