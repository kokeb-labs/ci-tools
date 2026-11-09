// Seeded violation: functions hand back a reference and a pointer to their own locals.
#include <cstdint>

namespace kv::rule_6_8_2::bad {

std::int32_t& dangling_ref() {
  std::int32_t local = 1;
  return local;
}

std::int32_t* dangling_ptr() {
  std::int32_t local = 2;
  return &local;
}

}  // namespace kv::rule_6_8_2::bad
