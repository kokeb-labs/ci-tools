// Seeded violation (nested): the range initializer passes one call's result to another call.
#include <array>
#include <cstdint>

namespace kv::rule_9_5_2::bad_nested {

const std::array<std::int32_t, 3>& pick(const std::array<std::int32_t, 3>& a) { return a; }

const std::array<std::int32_t, 3>& source() {
  static const std::array<std::int32_t, 3> data{1, 2, 3};
  return data;
}

std::int32_t total() {
  std::int32_t sum = 0;
  for (const std::int32_t v : pick(source())) {
    sum += v;
  }
  return sum;
}

}  // namespace kv::rule_9_5_2::bad_nested
