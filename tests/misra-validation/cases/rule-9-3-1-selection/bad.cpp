// Seeded violation: if and else bodies that are single statements (no loop, no switch).
#include <cstdint>

namespace kv::rule_9_3_1_selection::bad {

std::int32_t clamp(std::int32_t v, std::int32_t hi) {
  std::int32_t r = v;
  if (v > hi)
    r = hi;
  else
    r = v;
  return r;
}

}  // namespace kv::rule_9_3_1_selection::bad
