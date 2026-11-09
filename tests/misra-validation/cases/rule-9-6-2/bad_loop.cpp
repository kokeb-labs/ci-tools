// Seeded violation (loop): a goto from outside a loop to a label inside the loop body.
#include <cstdint>

namespace kv::rule_9_6_2::bad_loop {

std::int32_t enter(std::int32_t n) {
  std::int32_t r = 0;
  std::int32_t i = 0;
  if (n > 3) {
    goto body;  // seeded
  }
  while (i < n) {
  body:
    r += i;
    ++i;
  }
  return r;
}

}  // namespace kv::rule_9_6_2::bad_loop
