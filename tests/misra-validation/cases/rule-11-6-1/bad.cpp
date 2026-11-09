// Seeded violation: a local declared without an initializer and assigned later.
#include <cstdint>

namespace kv::rule_11_6_1::bad {

std::int32_t pick(bool high) {
  std::int32_t v;  // seeded
  if (high) {
    v = 10;
  } else {
    v = 1;
  }
  return v;
}

}  // namespace kv::rule_11_6_1::bad
