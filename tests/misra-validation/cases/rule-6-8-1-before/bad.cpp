// Seeded violation: a pointer that was never initialised is dereferenced (no object behind it yet).
#include <cstdint>

namespace kv::rule_6_8_1_before::bad {

std::int32_t early() {
  std::int32_t const* p;
  return *p;
}

}  // namespace kv::rule_6_8_1_before::bad
