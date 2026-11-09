// Seeded violation: a division by a zero divisor.
#include <cstdint>

namespace kv::rule_4_1_3_div_zero::bad {

std::uint32_t share(std::uint32_t total) {
  const std::uint32_t parts = 0U;
  return total / parts;  // seeded
}

}  // namespace kv::rule_4_1_3_div_zero::bad
