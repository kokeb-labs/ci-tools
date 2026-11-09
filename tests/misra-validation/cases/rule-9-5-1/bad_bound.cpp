// Seeded violation (bound): the loop bound is changed inside the body.
#include <cstdint>

namespace kv::rule_9_5_1::bad_bound {

std::int32_t shrink(std::int32_t n) {
  std::int32_t total = 0;
  for (std::int32_t i = 0; i < n; ++i) {  // seeded
    total += i;
    --n;
  }
  return total;
}

}  // namespace kv::rule_9_5_1::bad_bound
