// Seeded violation: a bool used as a number.
#include <cstdint>

namespace kv::rule_7_0_1::bad {

std::int32_t count(bool a, bool b) {
  std::int32_t const total = a + b;  // seeded
  return total;
}

}  // namespace kv::rule_7_0_1::bad
