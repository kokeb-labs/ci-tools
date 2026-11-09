// Seeded violation (union): a union member is read before its lifetime has begun; another member is active.
#include <cstdint>

namespace kv::rule_6_8_1_before::bad_union {

union Word {
  std::uint32_t whole;
  std::uint16_t halves[2];
};

std::uint16_t low_half() {
  Word w{};
  w.whole = 0x12345678U;
  return w.halves[0];  // seeded
}

}  // namespace kv::rule_6_8_1_before::bad_union
