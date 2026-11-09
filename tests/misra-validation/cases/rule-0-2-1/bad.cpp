// Seeded violation: a local variable that nothing refers to.
#include <cstdint>

namespace kv::rule_0_2_1::bad {

std::uint32_t mask(std::uint32_t v) {
  std::uint32_t spare = 3U;  // never referenced
  return v & 0xFFU;
}

}  // namespace kv::rule_0_2_1::bad
