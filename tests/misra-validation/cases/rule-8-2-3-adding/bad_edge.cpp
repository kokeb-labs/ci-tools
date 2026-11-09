// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_3_adding::bad_edge {

std::uint32_t strip(std::uint32_t const volatile* reg) {
  std::uint32_t* plain = const_cast<std::uint32_t*>(reg);
  return *plain;
}

}  // namespace kv::rule_8_2_3_adding::bad_edge
