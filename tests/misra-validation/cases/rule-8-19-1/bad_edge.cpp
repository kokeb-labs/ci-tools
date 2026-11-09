// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_19_1::bad_edge {

std::uint32_t walk(std::uint32_t n) {
  std::uint32_t j = 0U;
  for (std::uint32_t i = 0U; i < n; ++i, ++j) {
  }
  return j;
}

bool tested(std::uint32_t& a, std::uint32_t b) {
  if ((a = b), a != 0U) {
    return true;
  }
  return false;
}

}  // namespace kv::rule_8_19_1::bad_edge
