// Seeded violation: the result of std::ranges::fill (an iterator past the last element written) dropped.
#include <array>
#include <algorithm>
#include <cstdint>

namespace kv::rule_0_1_2_niebloid::bad {

std::uint32_t clear(std::array<std::uint32_t, 4U>& buf) {
  std::ranges::fill(buf, 0U);  // seeded
  return buf[0];
}

}  // namespace kv::rule_0_1_2_niebloid::bad
