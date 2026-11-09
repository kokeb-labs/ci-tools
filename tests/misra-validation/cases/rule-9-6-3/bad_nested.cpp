// Seeded violation (nested): a backward goto from a nested block to a label of the enclosing block.
#include <cstdint>

namespace kv::rule_9_6_3::bad_nested {

std::int32_t settle(std::int32_t v) {
  std::int32_t rounds = 0;
top:
  ++rounds;
  if (rounds < 3) {
    if (v > 0) {
      goto top;
    }
  }
  return rounds;
}

}  // namespace kv::rule_9_6_3::bad_nested
