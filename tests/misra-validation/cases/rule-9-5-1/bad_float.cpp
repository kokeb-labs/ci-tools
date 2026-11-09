// Seeded violation (float): a floating-point loop counter.
#include <cstdint>

namespace kv::rule_9_5_1::bad_float {

std::int32_t steps(float limit) {
  std::int32_t n = 0;
  for (float x = 0.0F; x < limit; x += 0.5F) {  // seeded
    ++n;
  }
  return n;
}

}  // namespace kv::rule_9_5_1::bad_float
