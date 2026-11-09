// Seeded violation (loop): a local inside a loop body declared without an initializer.
#include <cstdint>

namespace kv::rule_11_6_1::bad_loop {

std::int32_t sum(std::int32_t n) {
  std::int32_t total = 0;
  for (std::int32_t i = 0; i < n; ++i) {
    std::int32_t step;  // seeded
    step = i;
    total += step;
  }
  return total;
}

}  // namespace kv::rule_11_6_1::bad_loop
