// Seeded violation: if and else bodies that are single statements (no unbraced loop, no switch).
#include <cstdint>

namespace kv::rule_9_3_1_selection::bad {

std::int32_t clamp(std::int32_t v, std::int32_t hi) {
  std::int32_t r = v;
  if (v > hi)  // seeded
    r = hi;
  else  // seeded
    r = v;
  return r;
}

std::int32_t count_big(std::int32_t n) {
  std::int32_t big = 0;
  for (std::int32_t i = 0; i < n; ++i) {
    if (i > 10)  // seeded
      big = big + 1;
  }
  return big;
}

}  // namespace kv::rule_9_3_1_selection::bad
