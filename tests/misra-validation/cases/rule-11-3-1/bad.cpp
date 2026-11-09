// Seeded violation: a built-in array object.
#include <cstdint>

namespace kv::rule_11_3_1::bad {

std::int32_t sum3(std::int32_t a, std::int32_t b, std::int32_t c) {
  std::int32_t values[3] = {a, b, c};  // seeded
  return values[0] + values[1] + values[2];
}

}  // namespace kv::rule_11_3_1::bad
