// Seeded violation: a statement after an unconditional return.
#include <cstdint>

namespace kv::rule_0_0_1::bad {

std::int32_t clamp(std::int32_t v) {
  if (v < 0) {
    return 0;
  }
  return v;
  v = 1;  // never runs
}

}  // namespace kv::rule_0_0_1::bad
