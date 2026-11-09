// Seeded violations: direct recursion, and two functions that call each other.
#include <cstdint>

namespace kv::rule_8_2_10::bad {

std::uint32_t depth(std::uint32_t n) {
  if (n == 0U) {
    return 0U;
  }
  return 1U + depth(n - 1U);
}

bool is_odd(std::uint32_t n);

bool is_even(std::uint32_t n) {
  if (n == 0U) {
    return true;
  }
  return is_odd(n - 1U);
}

bool is_odd(std::uint32_t n) {
  if (n == 0U) {
    return false;
  }
  return is_even(n - 1U);
}

}  // namespace kv::rule_8_2_10::bad
