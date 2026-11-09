// Seeded violation (pointer): a pointer local declared without an initializer.
#include <cstdint>

namespace kv::rule_11_6_1::bad_pointer {

std::int32_t deref(std::int32_t& v) {
  std::int32_t* p;  // seeded
  p = &v;
  return *p;
}

}  // namespace kv::rule_11_6_1::bad_pointer
