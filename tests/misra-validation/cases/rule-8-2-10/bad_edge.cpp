// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_10::bad_edge {

struct Tree {
  std::uint32_t height(std::uint32_t n) const {
    if (n == 0U) {
      return 0U;
    }
    return height(n / 2U);  // seeded
  }
};

std::uint32_t c_step(std::uint32_t n);

std::uint32_t a_step(std::uint32_t n) {
  if (n == 0U) {
    return 0U;
  }
  return c_step(n / 2U);  // seeded
}

std::uint32_t b_step(std::uint32_t n) { return a_step(n / 2U); }  // seeded

std::uint32_t c_step(std::uint32_t n) { return b_step(n / 2U); }  // seeded

}  // namespace kv::rule_8_2_10::bad_edge
