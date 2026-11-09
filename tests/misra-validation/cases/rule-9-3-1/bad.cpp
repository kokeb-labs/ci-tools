// Seeded violation: loop, if and switch bodies that are not braced blocks.
#include <cstdint>

namespace kv::rule_9_3_1::bad {

std::int32_t sum_to(std::int32_t n) {
  std::int32_t total = 0;
  for (std::int32_t i = 0; i < n; ++i)  // seeded
    total += i;
  if (total > 100)  // seeded: clang-tidy
    total = 100;
  return total;
}

std::int32_t pick(std::int32_t mode) {
  std::int32_t out = 0;
  switch (mode)  // seeded: codeql
    case 1:
      out = 10;
  return out;
}

}  // namespace kv::rule_9_3_1::bad
