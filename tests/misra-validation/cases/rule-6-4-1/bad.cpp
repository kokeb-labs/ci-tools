// Seeded violation: an inner variable reuses the name of a variable in an enclosing block.
#include <cstdint>

namespace kv::rule_6_4_1::bad {

std::int32_t total(std::int32_t n) {
  std::int32_t sum = 0;
  for (std::int32_t i = 0; i < n; ++i) {
    std::int32_t sum = i;
    (void)sum;
  }
  return sum;
}

}  // namespace kv::rule_6_4_1::bad
