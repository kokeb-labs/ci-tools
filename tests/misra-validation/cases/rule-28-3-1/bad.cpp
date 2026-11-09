// Seeded violation: predicates that change state while the algorithm calls them.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iterator>

namespace kv::rule_28_3_1::bad {

struct CountingPositive {
  std::int32_t calls = 0;
  bool operator()(std::int32_t value) {
    ++calls;
    return value > 0;
  }
};

std::int32_t total_calls = 0;

bool positive_and_counted(std::int32_t value) {
  ++total_calls;
  return value > 0;
}

std::ptrdiff_t count_positive(const std::array<std::int32_t, 4U>& values) {
  return std::count_if(values.begin(), values.end(), CountingPositive{}) +  // seeded
         std::count_if(values.begin(), values.end(), positive_and_counted);  // seeded
}

}  // namespace kv::rule_28_3_1::bad
