// Seeded violation: a number and a pointer used directly as conditions.
#include <cstdint>

namespace kv::rule_7_0_2::bad {

std::int32_t pick(std::int32_t flags, std::int32_t const* p) {
  if (flags) {
    return 1;
  }
  if (p) {
    return *p;
  }
  return 0;
}

}  // namespace kv::rule_7_0_2::bad
