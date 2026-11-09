// Seeded violation: a cast removes volatile from what a pointer points to.
#include <cstdint>

namespace kv::rule_8_2_3_adding::bad {

std::uint32_t read_once(volatile std::uint32_t* reg) {
  std::uint32_t* plain = const_cast<std::uint32_t*>(reg);  // seeded
  return *plain;
}

}  // namespace kv::rule_8_2_3_adding::bad
