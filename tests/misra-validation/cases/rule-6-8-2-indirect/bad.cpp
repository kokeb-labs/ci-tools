// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_8_2_indirect::bad {

const std::int32_t& pick(bool c) {
  const std::int32_t a = 1;
  const std::int32_t b = 2;
  return c ? a : b;  // reference to a local through a conditional
}
std::int32_t* first_slot() {
  std::int32_t buf[2] = {0, 0};
  return &buf[0];  // pointer into a local array
}

}  // namespace kv::rule_6_8_2_indirect::bad
