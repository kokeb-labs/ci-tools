// Seeded violation: the loop counter is also changed inside the body.
#include <cstdint>

namespace kv::rule_9_5_1::bad {

std::int32_t skip_sum(std::int32_t n) {
  std::int32_t total = 0;
  for (std::int32_t i = 0; i < n; ++i) {  // seeded
    total += i;
    i += 2;
  }
  return total;
}

}  // namespace kv::rule_9_5_1::bad
