// Seeded violation: pointers into two different arrays are order-compared.
#include <cstdint>

namespace kv::rule_8_9_1::bad {

bool before() {
  std::uint8_t first[4] = {};
  std::uint8_t second[4] = {};
  std::uint8_t* a = &first[1];
  std::uint8_t* b = &second[2];
  return a < b;  // seeded
}

}  // namespace kv::rule_8_9_1::bad
