// Seeded violation: unary plus used to force a promotion.
#include <cstdint>

namespace kv::rule_8_3_2::bad {

std::int32_t widen(std::uint8_t value) {
  return +value;  // seeded
}

}  // namespace kv::rule_8_3_2::bad
