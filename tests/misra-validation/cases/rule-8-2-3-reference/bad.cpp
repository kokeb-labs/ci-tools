// Seeded violation: a cast removes volatile from an object bound to a reference.
#include <cstdint>

namespace kv::rule_8_2_3_reference::bad {

std::uint32_t read_once(volatile std::uint32_t& reg) {
  std::uint32_t& plain = const_cast<std::uint32_t&>(reg);  // seeded
  return plain;
}

}  // namespace kv::rule_8_2_3_reference::bad
