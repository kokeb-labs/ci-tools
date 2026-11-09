// Seeded violations: memcpy between overlapping ranges, and a union member assigned from its sibling.
#include <cstdint>
#include <cstring>

namespace kv::rule_8_18_1::bad {

void shift(std::uint8_t (&data)[8]) {
  std::memcpy(&data[1], &data[0], 4U);  // seeded
}

union Word {
  std::uint32_t whole;
  std::int32_t value;
};

std::uint32_t fold() {
  Word w{};
  w.value = 3;
  w.whole = w.value;  // seeded
  return w.whole;
}

}  // namespace kv::rule_8_18_1::bad
