// Seeded violation: a standard container that allocates as it grows.
#include <cstddef>
#include <cstdint>
#include <vector>

namespace kv::rule_21_6_1::bad_container {

std::size_t collect(std::int32_t count) {
  std::vector<std::int32_t> values;  // seeded
  for (std::int32_t i = 0; i < count; ++i) {
    values.push_back(i);
  }
  return values.size();
}

}  // namespace kv::rule_21_6_1::bad_container
