// Seeded violation: the range-for initializer calls two functions.
#include <array>
#include <cstdint>

namespace kv::rule_9_5_2::bad {

struct Table {
  std::array<std::int32_t, 4> data{};
  const std::array<std::int32_t, 4>& values() const { return data; }
};

const Table& table() {
  static const Table t{};
  return t;
}

std::int32_t total() {
  std::int32_t sum = 0;
  for (const std::int32_t v : table().values()) {
    sum += v;
  }
  return sum;
}

}  // namespace kv::rule_9_5_2::bad
