// Seeded violation: a mutable function-local static.
#include <cstdint>

namespace kv::rule_6_7_1::bad {

std::int32_t next_id() {
  static std::int32_t counter = 0;  // seeded
  ++counter;
  return counter;
}

}  // namespace kv::rule_6_7_1::bad
