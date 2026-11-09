// Seeded violation: pointers into two different arrays are subtracted.
#include <cstddef>
#include <cstdint>

namespace kv::rule_8_7_2::bad {

std::ptrdiff_t gap() {
  std::uint8_t first[4] = {};
  std::uint8_t second[4] = {};
  std::uint8_t* a = &first[1];
  std::uint8_t* b = &second[2];
  return b - a;
}

}  // namespace kv::rule_8_7_2::bad
