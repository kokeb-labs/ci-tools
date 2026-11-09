// Seeded violation: a condition that can only be true.
#include <cstdint>

namespace kv::rule_0_0_2::bad {

std::uint32_t limit(std::uint32_t v) {
  if (v >= 0U) {  // always true for an unsigned value  // seeded
    return v;
  }
  return 0U;
}

}  // namespace kv::rule_0_0_2::bad
