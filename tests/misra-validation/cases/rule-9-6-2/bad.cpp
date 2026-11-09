// Seeded violation: a goto into a block that does not enclose the goto.
#include <cstdint>

namespace kv::rule_9_6_2::bad {

std::int32_t jump_in(std::int32_t v) {
  std::int32_t r = 0;
  if (v > 0) {
    goto inner;  // seeded
  }
  if (v < 10) {
  inner:
    r = 1;
  }
  return r;
}

}  // namespace kv::rule_9_6_2::bad
