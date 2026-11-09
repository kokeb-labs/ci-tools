// Seeded violations: pointer arithmetic past the end of an array, and memcpy writing past one.
#include <cstdint>
#include <cstring>

namespace kv::rule_8_7_1::bad {

std::uint8_t* past_end() {
  std::uint8_t buffer[4];
  std::uint8_t* p = buffer;
  std::uint8_t* q = p + 6;  // seeded
  return q;
}

void copy_too_much() {
  std::uint8_t small[4];
  std::uint8_t large[8] = {};
  std::memcpy(small, large, 8U);  // seeded
}

}  // namespace kv::rule_8_7_1::bad
