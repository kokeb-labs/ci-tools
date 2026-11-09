// Seeded violation: const_cast strips const from what a pointer points to.
#include <cstdint>

namespace kv::rule_8_2_3::bad {

void reset(const std::uint32_t* reg) {
  std::uint32_t* writable = const_cast<std::uint32_t*>(reg);  // seeded
  *writable = 0U;
}

}  // namespace kv::rule_8_2_3::bad
