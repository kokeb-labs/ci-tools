// Seeded violation (loop): a function whose only return is inside a loop that may not run.
#include <cstdint>

namespace kv::rule_9_6_5::bad_loop {

std::int32_t first_above(const std::int32_t* values, std::int32_t n, std::int32_t limit) {
  for (std::int32_t i = 0; i < n; ++i) {
    if (values[i] > limit) {
      return i;
    }
  }
}

}  // namespace kv::rule_9_6_5::bad_loop
