// Edge cases of the seeded violation.
#include <cstdint>
#include <cstring>

namespace kv::rule_8_7_1::bad_edge {

std::uint8_t* before_start() {
  std::uint8_t buffer[4] = {};
  std::uint8_t* p = buffer;
  return p - 1;  // seeded
}

void copy_text(char const* src) {
  char small[2] = {};
  std::strncpy(small, "abc", 3U);  // seeded
  static_cast<void>(src);
}

}  // namespace kv::rule_8_7_1::bad_edge
