// Seeded violation (compound): an untyped unscoped enumerator in a compound assignment.
#include <cstdint>

namespace kv::rule_10_2_3::bad_compound {

enum Step { kOne = 1, kTwo = 2 };

std::int32_t advance(std::int32_t v) {
  std::int32_t r = v;
  r += kTwo;  // seeded
  return r;
}

}  // namespace kv::rule_10_2_3::bad_compound
