// Seeded violation (while): a while body and a switch body that are single statements.
#include <cstdint>

namespace kv::rule_9_3_1::bad_while {

std::int32_t drain(std::int32_t n, std::int32_t mode) {
  std::int32_t steps = 0;
  while (n > steps)
    ++steps;
  switch (mode)
    default:
      steps = 0;
  return steps;
}

}  // namespace kv::rule_9_3_1::bad_while
