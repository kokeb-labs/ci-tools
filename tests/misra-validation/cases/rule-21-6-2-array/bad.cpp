// Seeded violation: an array new-expression released with delete[] by hand.
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_6_2_array::bad {

std::int32_t first_of(std::size_t n) {
  std::int32_t* values = new std::int32_t[n]{};  // seeded
  const std::int32_t first = values[0];
  delete[] values;  // seeded
  return first;
}

}  // namespace kv::rule_21_6_2_array::bad
