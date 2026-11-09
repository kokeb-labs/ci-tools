// Seeded violation: a union used to view a word as bytes.
#include <cstdint>

namespace kv::rule_12_3_1::bad {

union Word {  // seeded
  std::uint32_t value;
  std::uint8_t bytes[4];
};

std::uint8_t low_byte(std::uint32_t v) {
  Word w{};
  w.value = v;
  return w.bytes[0];
}

}  // namespace kv::rule_12_3_1::bad
