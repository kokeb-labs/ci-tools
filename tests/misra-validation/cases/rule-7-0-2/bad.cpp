// Seeded violation: a number used directly as a condition, and a pointer converted to a bool object.
#include <cstdint>

namespace kv::rule_7_0_2::bad {

std::int32_t pick(std::int32_t flags) {
  if (flags) {  // seeded
    return 1;
  }
  return 0;
}

bool present(std::int32_t const* p) {
  bool const has = p;  // seeded
  return has;
}

}  // namespace kv::rule_7_0_2::bad
