// Seeded violation: functions hand back a reference and a pointer to their own locals.
#include <cstdint>

namespace kv::rule_6_8_2::bad {

std::int32_t& dangling_ref() {
  std::int32_t local = 1;
  return local;  // seeded
}

std::int32_t* dangling_ptr() {
  std::int32_t local = 2;
  return &local;  // seeded
}

// A parameter passed by value is a local of the function too.
std::int32_t const& dangling_param(std::int32_t value) {
  return value;  // seeded
}

}  // namespace kv::rule_6_8_2::bad
