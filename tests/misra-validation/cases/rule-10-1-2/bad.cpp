// Seeded violation: volatile on a local, a parameter and a return type, where it means nothing.
#include <cstdint>

namespace kv::rule_10_1_2::bad {

volatile std::int32_t twice(volatile std::int32_t v) {  // seeded
  volatile std::int32_t r = v * 2;  // seeded
  return r;
}

}  // namespace kv::rule_10_1_2::bad
