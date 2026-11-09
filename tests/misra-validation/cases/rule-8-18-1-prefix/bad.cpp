// Seeded violation: a union member is assigned from a smaller sibling that shares its first bytes.
#include <cstdint>

namespace kv::rule_8_18_1_prefix::bad {

union Word {
  std::uint32_t whole;
  std::uint16_t half;
};

std::uint32_t fold() {
  Word w{};
  w.half = 3U;
  w.whole = w.half;  // seeded
  return w.whole;
}

}  // namespace kv::rule_8_18_1_prefix::bad
