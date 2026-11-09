// Seeded violation: a built-in array decays to a pointer when passed to a function.
#include <cstdint>

namespace kv::rule_7_11_2::bad {

std::int32_t first(std::int32_t const* values) { return values[0]; }

std::int32_t use() {
  std::int32_t const samples[3] = {1, 2, 3};
  return first(samples);
}

}  // namespace kv::rule_7_11_2::bad
