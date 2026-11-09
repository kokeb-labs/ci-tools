// Seeded violation: a goto to a label in a sibling block that does not enclose the goto.
#include <cstdint>

namespace kv::rule_9_6_2_sibling::bad {

std::int32_t hop(std::int32_t n) {
  std::int32_t r = 0;
  std::int32_t j = 0;
  for (std::int32_t i = 0; i < n; ++i) {
    if (i == 2) {
      goto inside;
    }
  }
  while (j < n) {
  inside:
    r = j;
    ++j;
  }
  return r;
}

}  // namespace kv::rule_9_6_2_sibling::bad
