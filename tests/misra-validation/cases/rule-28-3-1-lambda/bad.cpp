// Seeded violation: a mutable lambda that counts its calls, used as an algorithm predicate.
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_28_3_1_lambda::bad {

std::ptrdiff_t count_positive(const std::array<std::int32_t, 4U>& values) {
  std::int32_t calls = 0;
  return std::count_if(values.begin(), values.end(), [calls](std::int32_t v) mutable {
    ++calls;
    return v > calls;
  });
}

}  // namespace kv::rule_28_3_1_lambda::bad
