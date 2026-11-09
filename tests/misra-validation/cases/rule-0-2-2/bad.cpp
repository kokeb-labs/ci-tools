// Seeded violation: a named parameter that the body never reads.
#include <cstdint>

namespace kv::rule_0_2_2::bad {

std::uint32_t select(std::uint32_t value, std::uint32_t mask) {  // seeded
  return value | 1U;
}

}  // namespace kv::rule_0_2_2::bad
