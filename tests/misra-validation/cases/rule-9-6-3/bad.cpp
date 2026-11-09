// Seeded violation: a backward goto that forms a loop.
#include <cstdint>

namespace kv::rule_9_6_3::bad {

std::int32_t count_down(std::int32_t n) {
  std::int32_t steps = 0;
again:
  if (n > 0) {
    --n;
    ++steps;
    goto again;  // seeded
  }
  return steps;
}

}  // namespace kv::rule_9_6_3::bad
