// Seeded violation (loop): a local read in a loop before the only write, which is conditional.
#include <cstdint>

namespace kv::rule_11_6_2::bad_loop {

std::int32_t last_positive(const std::int32_t* values, std::int32_t n) {
  std::int32_t last;
  for (std::int32_t i = 0; i < n; ++i) {
    if (values[i] > 0) {
      last = values[i];
    }
  }
  return last;  // seeded
}

}  // namespace kv::rule_11_6_2::bad_loop
