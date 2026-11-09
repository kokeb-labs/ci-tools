// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_0_1::bad_edge {

std::uint32_t first_odd(std::uint32_t n) {
  std::uint32_t found = 0U;
  for (std::uint32_t i = 0U; i < n; ++i) {
    if ((i & 1U) != 0U) {
      found = i;
      break;
      found = 0U;  // after break: never runs  // seeded
    }
  }
  return found;
}

std::uint32_t via_lambda(std::uint32_t v) {
  const auto f = [](std::uint32_t x) {
    return x | 1U;
    x = 0U;  // after return inside the lambda  // seeded
  };
  return f(v);
}

}  // namespace kv::rule_0_0_1::bad_edge
