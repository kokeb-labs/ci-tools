// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_2::bad_edge {

std::int32_t countdown(std::int32_t n) {
  std::int32_t steps = 0;
  while (n) {
    n = n - 1;
    steps = steps + 1;
  }
  return steps;
}

std::int32_t choose(std::int32_t sel, std::int32_t a, std::int32_t b) { return sel ? a : b; }

bool empty(std::int32_t count) { return !count; }

bool both(std::int32_t x, std::int32_t y) { return x && y; }

}  // namespace kv::rule_7_0_2::bad_edge
